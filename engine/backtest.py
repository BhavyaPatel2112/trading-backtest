import pandas as pd

# simulates trading with fake money 
def run_backtest(df: pd.DataFrame, initial_capital: float = 10_000.0):
   
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
        signal = row["Signal"]
        price = row["Open"]
        date = df.index[i]

        # if singal == 1 and shares == 0 it means it is a buy day you dont have any shares
        # buy as many whole shares as you can afford 
        # subtract what you spent 
        # log the trade
        if signal == 1 and shares == 0:
            shares = int(cash // price)
            cash -= shares * price
            trade_log.append({
                "Date": date,
                "Action": "BUY",
                "Price": price,
                "Shares": shares,
                "Cash": cash,
            })

        # if singal == -1 and shares > 0 it means it is a sell day and you have shares to sell 
        # sell all shares and add the money to cash 
        # log the trade
        elif signal == -1 and shares > 0:
            cash += shares * price
            trade_log.append({
                "Date": date,
                "Action": "SELL",
                "Price": price,
                "Shares": shares,
                "Cash": cash,
            })
            shares = 0

        # calculate total portfolio value which is cash + value of shares you own 
        portfolio_value = cash + shares * row["Close"]

        # add that to the list
        equity_curve.append({"Date": date, "Portfolio_Value": portfolio_value})

    equity_curve = pd.DataFrame(equity_curve).set_index("Date")
    trade_log = pd.DataFrame(trade_log)

    # return 2 tables one showing portolio value every day and one showing every trade you make
    return equity_curve, trade_log
