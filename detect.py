import pandas as pd
from pathlib import Path
from datetime import date, timedelta
from xfinance import info

SAVE_PATH = Path( "data/detector.parquet" )

START = date(2020,1,1)
LENGTH = 10            # Increase to 5 years (365 * 5)

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

def check( row, currentDate ):
    error = True

    flags = []

    if error:
        flags.append( "test flag")

    row["flags"] = ",".join( flags ) or "None"

def flush( rows: list ):
    if not rows:
        return

    df = pd.DataFrame( rows ).reindex( columns=COLUMNS )

    SAVE_PATH.parent.mkdir( parents=True, exist_ok=True )
    df.to_parquet( SAVE_PATH, index=False )

def main():
    currentDate = START

    rows = []

    for i in range( LENGTH ):
        for symbol in SYMBOLS:
            # Get record
            row = info( symbol, currentDate )    # Returns dict

            if not row:
                continue

            row["date"] = currentDate

            check( row, currentDate )

            print( row )
            rows.append( row )

        # Save to parquet
        flush( rows )

        currentDate += timedelta( days=1 )

if __name__ == "__main__":
    main()