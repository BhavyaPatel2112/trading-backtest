import pandas as pd

# calculates simple moving average
# takes a column of prices and a window (20 days) and each day it averages the closing price of the last 20 days 
def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window).mean()

# calculates exponential moving average
# more weight to recent prices so better reactions to price changes
def ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()
