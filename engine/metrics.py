import pandas as pd
import numpy as np

# calculates performance metrics
def calculate_metrics(equity_curve: pd.DataFrame, trade_log: pd.DataFrame, initial_capital: float = 10_000.0) -> dict:
    portfolio = equity_curve["Portfolio_Value"]

    # how much did you make or lose in %
    total_return_pct = (portfolio.iloc[-1] - initial_capital) / initial_capital * 100

    # highest portfolio value to date
    running_max = portfolio.cummax()

    # for each day how far below the all time high you were 
    drawdowns = (portfolio - running_max) / running_max * 100
    
    # worst drop from peak before recovering
    max_drawdown_pct = drawdowns.min()

    # how much did the portfolio make or lose everyday 
    daily_returns = portfolio.pct_change().dropna()
    
    # sharpe ratio calculation
    # if 0 variation then for that day sharpe ratio is 0
    if daily_returns.std() == 0:
        sharpe_ratio = 0.0
    else:
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)

    # how many trades were made
    num_trades = len(trade_log)

    return {
        "total_return_pct": round(total_return_pct, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "num_trades": num_trades,
    }

# benchmark to compare 
# checks how we would have performed if we bought on day 1 and held until the end
def buy_and_hold(df: pd.DataFrame, initial_capital: float = 10_000.0) -> pd.Series:
    first_price = df["Open"].iloc[0]
    shares = initial_capital / first_price
    bah = df["Close"] * shares
    bah.name = "Buy_and_Hold_Value"
    return bah

