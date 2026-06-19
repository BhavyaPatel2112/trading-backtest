import pandas as pd

# simulates trading with fake money
# cost_pct is the trading cost as a fraction of each trade (0.001 = 0.1%)
def run_backtest(df: pd.DataFrame, initial_capital: float = 10_000.0, cost_pct: float = 0.001):

    # fake amount you start with default at $10k
    cash = initial_capital

    # shares you own
    shares = 0

    # tracks portfolio value over time
    equity_curve = []

    # tracks trade log over time
    trade_log = []

    # loops through every single day one by one
    # checks what to do on that day
    for i in range(len(df)):
        row = df.iloc[i]
        date = df.index[i]

        # NO LOOK-AHEAD:
        # a signal is generated from a day's CLOSE, so the earliest we could
        # actually act on it is the NEXT morning's OPEN.
        # so on day i we trade on YESTERDAY's signal, at TODAY's open price.
        signal = df.iloc[i - 1]["Signal"] if i > 0 else 0
        price = row["Open"]

        # if signal == 1 and shares == 0 it means it is a buy day and you have no shares
        # buy as many whole shares as you can afford, AFTER leaving room for the trading cost
        # subtract what you spent plus the cost
        # log the trade
        if signal == 1 and shares == 0:
            # each share effectively costs price * (1 + cost_pct) once the fee is included,
            # so divide cash by that to know how many whole shares you can really afford
            shares = int(cash // (price * (1 + cost_pct)))
            if shares > 0:
                gross = shares * price          # value of the shares
                cost = gross * cost_pct         # the trading cost
                cash -= gross + cost            # pay for shares AND the cost
                trade_log.append({
                    "Date": date,
                    "Action": "BUY",
                    "Price": price,
                    "Shares": shares,
                    "Cost": cost,
                    "Cash": cash,
                })

        # if signal == -1 and shares > 0 it means it is a sell day and you have shares to sell
        # sell all shares, then pay the trading cost out of the proceeds
        # log the trade
        elif signal == -1 and shares > 0:
            gross = shares * price              # money you get from selling
            cost = gross * cost_pct             # the trading cost
            cash += gross - cost                # keep proceeds minus the cost
            trade_log.append({
                "Date": date,
                "Action": "SELL",
                "Price": price,
                "Shares": shares,
                "Cost": cost,
                "Cash": cash,
            })
            shares = 0

        # calculate total portfolio value which is cash + value of shares you own
        portfolio_value = cash + shares * row["Close"]

        # add that to the list
        equity_curve.append({"Date": date, "Portfolio_Value": portfolio_value})

    equity_curve = pd.DataFrame(equity_curve).set_index("Date")
    trade_log = pd.DataFrame(trade_log)

    # return 2 tables one showing portfolio value every day and one showing every trade you make
    return equity_curve, trade_log
