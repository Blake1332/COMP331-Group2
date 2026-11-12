import pandas as pd
from pathlib import Path
from datetime import date, timedelta
from xfinance import info

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

def detect_threshold( row, currentDate, history, today ) -> list:
    # Check if stock has had very large returns from previous
    flags = []

    if True:
        flags.append( "threshold test")

    return flags

def detect_other( row, currentDate, history, today ) -> list:
    # Check if stock has had very large returns from previous
    flags = []

    if False:
        flags.append( "other test")

    return flags

DETECTORS = {
    "threshold": detect_threshold,
    "other": detect_other,
}

def flush( rows: list, path: Path ):
    if not rows:
        return

    df = pd.DataFrame( rows ).reindex( columns=COLUMNS )

    path.parent.mkdir( parents=True, exist_ok=True )
    df.to_parquet( path, index=False )

def main():
    currentDate = START

    results = { name: [] for name in DETECTORS }
    history = { symbol: [] for symbol in SYMBOLS }

    rows = []

    for i in range( LENGTH ):
        today = {}

        # Get current day record from xfinance for each stock
        for symbol in SYMBOLS:
            # Get record
            baseline = info( symbol, currentDate )    # Returns dict

            # Skip if nothing returned
            if not baseline:
                continue

            # Add recieved date
            baseline["date"] = currentDate
            today[symbol] = baseline

        # Loop through all stocks
        for symbol, base in today.items():
            # Loop through all detection techniques
            for name, detector in DETECTORS.items():
                row = dict( baseline )

                flags = detector( row, currentDate, history, today )
                row["flags"] = ",".join( flags ) or "None"
                row["detected"] = True

                print( name, row )
                results[name].append( row )

        # Update history only after detectors have run
        for symbol, baseline in today.items():
            history[symbol].append( base )

        # Save to parquet
        for name, rows in results.items():
            flush( rows, f"data/detect/{name}.parquet" )

        currentDate += timedelta( days=1 )

if __name__ == "__main__":
    main()