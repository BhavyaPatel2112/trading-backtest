import pandas as pd
from indicators.moving_averages import sma # pulls the SMA function 

# takes the stock price table and decides when to buy or sell 
def generate_signals(df: pd.DataFrame, fast_window: int = 20, slow_window: int = 50) -> pd.DataFrame:
    df = df.copy()

    # calculates the fast and slow moving averages of the number of days needed
    df["fast_ma"] = sma(df["Close"], fast_window)
    df["slow_ma"] = sma(df["Close"], slow_window)

    # generates trading signals based on the crossover
    df["Signal"] = 0
    df.loc[df["fast_ma"] > df["slow_ma"], "Signal"] = 1 # Buy since fast > slow 
    df.loc[df["fast_ma"] < df["slow_ma"], "Signal"] = -1 # Sell since fast < slow 

    # subtracts consecutive pairs. If anything other than 0 then buy or sell 
    # else do not do anything 
    # row 2 - row 1 | row 4 - row 3 | row 6 - row 5 and so on
    df["Signal"] = df["Signal"].diff().clip(-1, 1).fillna(0).astype(int)

    # returns OHLCV table along with fast MA, slow MA and signal
    return df
