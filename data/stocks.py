# stock options to choose from
STOCKS = [
    # Technology
    {"symbol": "AAPL", "name": "Apple", "category": "Technology", "popular": True},
    {"symbol": "MSFT", "name": "Microsoft", "category": "Technology", "popular": True},
    {"symbol": "GOOGL", "name": "Alphabet (Google)", "category": "Technology", "popular": True},
    {"symbol": "NVDA", "name": "Nvidia", "category": "Technology", "popular": True},
    {"symbol": "META", "name": "Meta Platforms", "category": "Technology", "popular": True},
    {"symbol": "AMD", "name": "Advanced Micro Devices", "category": "Technology", "popular": True},
    {"symbol": "INTC", "name": "Intel", "category": "Technology", "popular": False},
    {"symbol": "CRM", "name": "Salesforce", "category": "Technology", "popular": False},
    {"symbol": "ORCL", "name": "Oracle", "category": "Technology", "popular": False},
    {"symbol": "ADBE", "name": "Adobe", "category": "Technology", "popular": False},
    {"symbol": "CSCO", "name": "Cisco Systems", "category": "Technology", "popular": False},

    # Consumer
    {"symbol": "AMZN", "name": "Amazon", "category": "Consumer", "popular": True},
    {"symbol": "TSLA", "name": "Tesla", "category": "Consumer", "popular": True},
    {"symbol": "WMT", "name": "Walmart", "category": "Consumer", "popular": False},
    {"symbol": "MCD", "name": "McDonald's", "category": "Consumer", "popular": False},
    {"symbol": "NKE", "name": "Nike", "category": "Consumer", "popular": False},
    {"symbol": "SBUX", "name": "Starbucks", "category": "Consumer", "popular": False},
    {"symbol": "KO", "name": "Coca-Cola", "category": "Consumer", "popular": False},
    {"symbol": "PEP", "name": "PepsiCo", "category": "Consumer", "popular": False},
    {"symbol": "PG", "name": "Procter & Gamble", "category": "Consumer", "popular": False},
    {"symbol": "DIS", "name": "Walt Disney", "category": "Consumer", "popular": False},
    {"symbol": "NFLX", "name": "Netflix", "category": "Consumer", "popular": True},

    # Financials
    {"symbol": "JPM", "name": "JPMorgan Chase", "category": "Financials", "popular": False},
    {"symbol": "BAC", "name": "Bank of America", "category": "Financials", "popular": False},
    {"symbol": "WFC", "name": "Wells Fargo", "category": "Financials", "popular": False},
    {"symbol": "GS", "name": "Goldman Sachs", "category": "Financials", "popular": False},
    {"symbol": "V", "name": "Visa", "category": "Financials", "popular": False},
    {"symbol": "MA", "name": "Mastercard", "category": "Financials", "popular": False},
    {"symbol": "BRK-B", "name": "Berkshire Hathaway", "category": "Financials", "popular": False},

    # Healthcare
    {"symbol": "JNJ", "name": "Johnson & Johnson", "category": "Healthcare", "popular": False},
    {"symbol": "PFE", "name": "Pfizer", "category": "Healthcare", "popular": False},
    {"symbol": "UNH", "name": "UnitedHealth Group", "category": "Healthcare", "popular": False},
    {"symbol": "LLY", "name": "Eli Lilly", "category": "Healthcare", "popular": False},
    {"symbol": "MRK", "name": "Merck", "category": "Healthcare", "popular": False},

    # Energy & Industrial
    {"symbol": "XOM", "name": "ExxonMobil", "category": "Energy & Industrial", "popular": False},
    {"symbol": "CVX", "name": "Chevron", "category": "Energy & Industrial", "popular": False},
    {"symbol": "BA", "name": "Boeing", "category": "Energy & Industrial", "popular": False},
    {"symbol": "CAT", "name": "Caterpillar", "category": "Energy & Industrial", "popular": False},

    # ETFs (baskets of many stocks)
    {"symbol": "SPY", "name": "S&P 500 ETF", "category": "ETFs", "popular": True},
    {"symbol": "QQQ", "name": "Nasdaq 100 ETF", "category": "ETFs", "popular": True},
    {"symbol": "VOO", "name": "Vanguard S&P 500 ETF", "category": "ETFs", "popular": False},
    {"symbol": "VTI", "name": "Vanguard Total Market ETF", "category": "ETFs", "popular": False},
    {"symbol": "DIA", "name": "Dow Jones ETF", "category": "ETFs", "popular": False},
    {"symbol": "IWM", "name": "Russell 2000 ETF", "category": "ETFs", "popular": False},
]

# the filter options shown in the dropdown, in order
CATEGORIES = [
    "⭐ Most Popular",
    "Technology",
    "Consumer",
    "Financials",
    "Healthcare",
    "Energy & Industrial",
    "ETFs",
    "All",
]


# returns the stocks that match a chosen filter, sorted alphabetically by name
def filter_stocks(category: str) -> list:
    if category == "All":
        matches = STOCKS
    elif category == "⭐ Most Popular":
        matches = [s for s in STOCKS if s["popular"]]
    else:
        matches = [s for s in STOCKS if s["category"] == category]
    return sorted(matches, key=lambda s: s["name"].lower())
