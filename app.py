import streamlit as st
import plotly.graph_objects as go
from datetime import date

from data.fetcher import get_ohlcv
from strategies.ma_crossover import generate_signals
from engine.backtest import run_backtest
from engine.metrics import calculate_metrics, buy_and_hold

st.set_page_config(page_title="BacktestLab", page_icon="📈", layout="wide")

st.title("📈 BacktestLab")
st.caption("Backtest moving average crossover strategies against historical stock data.")

with st.sidebar:
    st.header("Strategy Settings")

    ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date(2020, 1, 1))
    with col2:
        end_date = st.date_input("End Date", value=date(2024, 1, 1))

    st.divider()

    fast_window = st.slider("Fast MA (days)", min_value=5, max_value=100, value=20, step=1)
    slow_window = st.slider("Slow MA (days)", min_value=10, max_value=300, value=50, step=1)

    st.divider()

    initial_capital = st.number_input("Initial Capital ($)", min_value=1000, max_value=1_000_000, value=10_000, step=1000)

    run = st.button("Run Backtest", type="primary", use_container_width=True)

if not run:
    st.info("Configure your strategy in the sidebar and click **Run Backtest** to get started.")
    st.stop()

if fast_window >= slow_window:
    st.error("Fast MA must be smaller than Slow MA.")
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

    df = generate_signals(df, fast_window=fast_window, slow_window=slow_window)
    equity_curve, trade_log = run_backtest(df, initial_capital=initial_capital)
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
    st.markdown(f"""
| | |
|---|---|
| **Ticker** | {ticker} |
| **Period** | {start_date} → {end_date} |
| **Fast MA** | {fast_window} days |
| **Slow MA** | {slow_window} days |
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
        display_log["Cash"] = display_log["Cash"].map("${:,.2f}".format)
        st.dataframe(display_log, use_container_width=True, hide_index=True)
