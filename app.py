import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import date

from data.fetcher import get_ohlcv
from data.stocks import CATEGORIES, filter_stocks
from strategies.registry import STRATEGIES
from engine.backtest import run_backtest
from engine.metrics import calculate_metrics, buy_and_hold

st.set_page_config(page_title="BacktestLab", page_icon="📈", layout="wide")

st.title("📈 BacktestLab")
st.caption("Backtest trading strategies against historical stock data.")


# Looks up the FULL history of a ticker once, just to learn the first and
# last day data is available for. We use this to bound the date pickers so
# the user can't pick a future date or a date the stock has no data for.
# Cached so it only downloads once per ticker.
@st.cache_data(show_spinner=False)
def get_available_range(ticker: str):
    if not ticker:
        return None
    try:
        hist = yf.download(ticker, period="max", auto_adjust=True, progress=False)
        if hist.empty:
            return None
        return hist.index.min().date(), hist.index.max().date()
    except Exception:
        return None

with st.sidebar:
    st.header("Strategy Settings")

    # 1) pick a category to narrow the list (Most Popular, a sector, or All)
    category = st.selectbox("Category", CATEGORIES, index=0)

    # 2) pick a stock from that filtered, alphabetically-sorted list.
    # the dropdown is searchable — start typing a name to jump to it.
    choices = filter_stocks(category)
    labels = [f"{s['name']} — {s['symbol']}" for s in choices]
    picked = st.selectbox("Stock", labels)
    picked_symbol = choices[labels.index(picked)]["symbol"]

    # 3) optional: type any ticker by hand. if filled, it overrides the dropdown.
    custom = st.text_input("Or enter a custom ticker", value="").upper().strip()

    ticker = custom if custom else picked_symbol

    # Find out which dates this ticker actually has data for.
    available = get_available_range(ticker)
    if available:
        min_date, max_date = available
        st.caption(f"Data available: {min_date} → {max_date}")
    else:
        # fallback bounds if we couldn't look the ticker up (bad symbol, no network, etc.)
        min_date, max_date = date(1990, 1, 1), date.today()
        if ticker:
            st.warning("Couldn't look up this ticker's date range — check the symbol.")

    # sensible defaults, clamped to stay inside the available range
    default_start = min(max(date(2020, 1, 1), min_date), max_date)
    default_end = max_date

    col1, col2 = st.columns(2)
    with col1:
        # key includes the ticker so the calendar resets cleanly when the ticker changes
        start_date = st.date_input(
            "Start Date", value=default_start,
            min_value=min_date, max_value=max_date, key=f"start_{ticker}",
        )
    with col2:
        end_date = st.date_input(
            "End Date", value=default_end,
            min_value=min_date, max_value=max_date, key=f"end_{ticker}",
        )

    st.divider()

    # pick a strategy from the menu, then build that strategy's sliders automatically
    strategy_name = st.selectbox("Strategy", list(STRATEGIES.keys()))
    spec = STRATEGIES[strategy_name]

    # collect each slider's value into a params dict, e.g. {"fast_window": 20, "slow_window": 50}
    params = {}
    for p in spec["params"]:
        params[p["name"]] = st.slider(
            p["label"],
            min_value=p["min"], max_value=p["max"], value=p["default"], step=p["step"],
        )

    st.divider()

    initial_capital = st.number_input("Initial Capital ($)", min_value=1000, max_value=1_000_000, value=10_000, step=1000)

    # trading cost per trade, as a percentage. default 0.1%.
    cost_pct = st.slider(
        "Trading Cost per Trade (%)",
        min_value=0.0, max_value=1.0, value=0.1, step=0.05,
        help="Cost charged on every buy and sell (commission + slippage). 0.1% is a sensible default.",
    ) / 100.0

    run = st.button("Run Backtest", type="primary", use_container_width=True)

if not run:
    st.info("Configure your strategy in the sidebar and click **Run Backtest** to get started.")
    st.stop()

# run this strategy's own validation check, if it has one
validate = spec.get("validate")
if validate:
    error = validate(params)
    if error:
        st.error(error)
        st.stop()

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

with st.spinner(f"Fetching data and running backtest for {ticker}..."):
    try:
        df = get_ohlcv(ticker, str(start_date), str(end_date))
    except Exception as e:
        st.error(f"Could not fetch data for **{ticker}**: {e}")
        st.stop()

    df = spec["func"](df, **params)
    equity_curve, trade_log = run_backtest(df, initial_capital=initial_capital, cost_pct=cost_pct)
    metrics = calculate_metrics(equity_curve, trade_log, initial_capital=initial_capital)
    bah = buy_and_hold(df, initial_capital=initial_capital)

st.subheader(f"Results — {ticker}  |  {start_date} to {end_date}")

m1, m2, m3, m4 = st.columns(4)

total_return = metrics["total_return_pct"]
m1.metric(
    "Total Return",
    f"{total_return:+.2f}%",
    delta=f"{total_return:+.2f}%",
    delta_color="normal"
)

bah_return = (bah.iloc[-1] - initial_capital) / initial_capital * 100
m2.metric(
    "Buy & Hold Return",
    f"{bah_return:+.2f}%",
    delta=f"{bah_return:+.2f}%",
    delta_color="normal"
)

m3.metric("Max Drawdown", f"{metrics['max_drawdown_pct']:.2f}%")
m4.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")

st.divider()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=equity_curve.index,
    y=equity_curve["Portfolio_Value"],
    name="Strategy",
    line=dict(color="#00C4FF", width=2),
))

fig.add_trace(go.Scatter(
    x=bah.index,
    y=bah.values,
    name="Buy & Hold",
    line=dict(color="#FF6B6B", width=2, dash="dash"),
))

if not trade_log.empty:
    buys = trade_log[trade_log["Action"] == "BUY"]
    sells = trade_log[trade_log["Action"] == "SELL"]

    fig.add_trace(go.Scatter(
        x=buys["Date"],
        y=equity_curve.loc[buys["Date"], "Portfolio_Value"].values,
        mode="markers",
        name="Buy",
        marker=dict(color="#00FF99", size=10, symbol="triangle-up"),
    ))

    fig.add_trace(go.Scatter(
        x=sells["Date"],
        y=equity_curve.loc[sells["Date"], "Portfolio_Value"].values,
        mode="markers",
        name="Sell",
        marker=dict(color="#FF4444", size=10, symbol="triangle-down"),
    ))

fig.update_layout(
    title="Equity Curve: Strategy vs Buy & Hold",
    xaxis_title="Date",
    yaxis_title="Portfolio Value ($)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=500,
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Summary")
    # build one table row per slider this strategy used (uses each slider's label)
    param_rows = "".join(
        f"| **{p['label']}** | {params[p['name']]} |\n" for p in spec["params"]
    )
    st.markdown(f"""
| | |
|---|---|
| **Ticker** | {ticker} |
| **Period** | {start_date} → {end_date} |
| **Strategy** | {strategy_name} |
{param_rows}| **Trading Cost** | {cost_pct * 100:.2f}% |
| **Initial Capital** | ${initial_capital:,.0f} |
| **Final Value** | ${equity_curve['Portfolio_Value'].iloc[-1]:,.2f} |
| **Total Trades** | {metrics['num_trades']} |
""")

with col_right:
    st.subheader("Trade Log")
    if trade_log.empty:
        st.info("No trades were executed in this period.")
    else:
        display_log = trade_log.copy()
        display_log["Date"] = display_log["Date"].dt.strftime("%Y-%m-%d")
        display_log["Price"] = display_log["Price"].map("${:,.2f}".format)
        display_log["Cost"] = display_log["Cost"].map("${:,.2f}".format)
        display_log["Cash"] = display_log["Cash"].map("${:,.2f}".format)
        st.dataframe(display_log, use_container_width=True, hide_index=True)
