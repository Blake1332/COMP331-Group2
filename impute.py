import pandas as pd
from vars import START, LENGTH, SYMBOLS, COLUMNS
from pathlib import Path
from datetime import date, timedelta

def impute_locf():
    return

def impute_other():
    return

IMPUTORS = {
    "locf": impute_locf,
    "other": impute_other,
}

def flush( rows: list, path: Path ):
    if not rows:
        return

    df = pd.DataFrame( rows ).reindex( columns=COLUMNS )

    path.parent.mkdir( parents=True, exist_ok=True )
    df.to_parquet( path, index=False )

def main():

    # Gather all the parquet files
    folder = Path( "data/detect" )

    files = folder.glob( "*.parquet" )

    dataframes = []

    for file in files:
        df = df.read_parquet( file )
        dataframes.append( ( file.stem, df ) )

    for detector, df in dataframes:
        currentDate = START
        
        results = { name: [] for name in IMPUTORS }
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
                for name, detector in IMPUTORS.items():
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
            for imputor, rows in results.items():
                flush( rows, f"data/impute/{detector}-{imputor}.parquet" )

            currentDate += timedelta( days=1 )

if __name__ == "__main__":
    main()