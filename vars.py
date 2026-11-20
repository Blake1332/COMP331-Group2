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
        "flags",

        # Original
        "og_open", "og_dayHigh", "og_dayLow", "og_currentPrice",
        "og_originalPrice", "og_volume",
]

FIELDS = [
    "open",
    "dayHigh",
    "dayLow",
    "currentPrice",
    "volume",
]