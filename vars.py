from datetime import date

START = date(2020,1,1)
LENGTH = 100

SYMBOLS = [
    "AAPL",
    "AMZN",
    "GOOGL",
    "COST",
    "KO",
    "NVDA",
    "TSLA",
]

COLUMNS = [
        # xfinance
        "symbol", "date", "errors", "shortName", "longName",
        "quoteType", "currency", "exchange", "country",
        "sector", "industry","open", "dayHigh", "dayLow",
        "currentPrice", "originalPrice", "volume",

        # Detect
        "flags", "detected",

]