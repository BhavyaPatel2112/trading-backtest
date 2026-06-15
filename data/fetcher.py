import os # lets code interact with computer operating system directly
import pandas as pd
import yfinance as yf # importing y finance library

# builds a path to a cache directory that saves downloaded files 
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

# builds a filename for a cached file in the form STOCK_START_END
def _cache_path(ticker: str, start: str, end: str) -> str:
    filename = f"{ticker.upper()}_{start}_{end}.csv"
    return os.path.join(CACHE_DIR, filename)

# checks if CSV file exists in cache. If so then returns it as a table, if not then returns NONE
def _load_from_cache(path: str) -> pd.DataFrame | None:
    if os.path.exists(path):
        print(f"[fetcher] Loading from cache: {path}")
        df = pd.read_csv(path, index_col="Date", parse_dates=True)
        return df
    return None

# 
def _download_from_yfinance(ticker: str, start: str, end: str) -> pd.DataFrame:
    print(f"[fetcher] Downloading {ticker} from {start} to {end} via yfinance...")
    raw = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)

    if raw.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'. Check the ticker symbol and date range.")

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()

    df.dropna(how="all", inplace=True)

    df.index.name = "Date"
    return df



def _save_to_cache(df: pd.DataFrame, path: str) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    df.to_csv(path)
    print(f"[fetcher] Saved to cache: {path}")


def get_ohlcv(ticker: str, start: str, end: str) -> pd.DataFrame:
    path = _cache_path(ticker, start, end)

    df = _load_from_cache(path)

    if df is None:
        df = _download_from_yfinance(ticker, start, end)
        _save_to_cache(df, path)

    return df
