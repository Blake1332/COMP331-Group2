import pandas as pd
from vars import START, LENGTH, SYMBOLS, COLUMNS
from pathlib import Path
from datetime import timedelta
from xfinance import info
from detect import DETECTORS
from impute import IMPUTORS

def flush( rows: list, path: Path ):
    if not rows:
        return

    df = pd.DataFrame( rows ).reindex( columns=COLUMNS + list( IMPUTORS ) )

    path.parent.mkdir( parents=True, exist_ok=True )
    df.to_parquet( path, index=False )

def main():
    
    history = { symbol: [] for symbol in SYMBOLS }

    rows = []

    for i in range( LENGTH ):
        currentDate = START + timedelta( days=i )

        today = {}

        # Get current day record from xfinance for each stock
        for symbol in SYMBOLS:
            # Get record
            row = info( symbol, currentDate )    # Returns dict

            # Skip if nothing returned
            if not row:
                continue

            # Add recieved date
            row["date"] = currentDate
            today[symbol] = row

        # Loop through all stocks
        for symbol, row in today.items():

            # Loop through all detection techniques
            flags = []
            for name, detector in DETECTORS.items():
                if detector( row, currentDate, history, today ):
                    flags.append( name )

            row["flags"] = ",".join( flags ) or None

            # Loop through all imputation techniques
            for name, imputor in IMPUTORS.items():
                if flags:
                    imputed = imputor( row, currentDate, history, today )
                    row[name] = imputed
                else:
                    row[name] = row["currentPrice"]

            rows.append( row )

        # Update history only after detectors have run
        for symbol, row in today.items():
            history[symbol].append( row )

    # Save to parquet
    flush( rows, Path( "data/imported.parquet" ) )

if __name__ == "__main__":
    main()