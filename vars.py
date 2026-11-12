from datetime import date

START = date(2020,1,1)
LENGTH = 10

SYMBOLS = [
    "AAPL",
    "AMZN",
    "GOOGL",
    "COST",
    "KO",
    "NVDA",
    "TSLA",
]

COLUMNS = [ "symbol", "date", "errors", "flags", "shortName",
            "longName", "quoteType", "currency", "exchange",
            "country", "sector", "industry","open", "dayHigh",
            "dayLow", "currentPrice", "volume"
]