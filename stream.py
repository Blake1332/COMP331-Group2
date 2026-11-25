import argparse
import pandas as pd
from vars import START, LENGTH, SYMBOLS, COLUMNS, FIELDS
from pathlib import Path
from datetime import timedelta
from xfinance import info
from detect import DETECTORS
from impute import IMPUTORS
from error import reset

def flush( rows: list, path: Path ):
    if not rows:
        return

    df = pd.DataFrame( rows ).reindex(
        columns=COLUMNS +
        list( IMPUTORS ) + 
        [ f"{name}_{field}" for name in IMPUTORS for field in FIELDS ]
    )

    path.parent.mkdir( parents=True, exist_ok=True )
    df.to_parquet( path, index=False )

def main( seed: int | None = None ):
    if seed:
        reset( seed )
    else:
        reset()
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
            flags = {}
            for name, detector in DETECTORS.items():
                detected = detector( row, currentDate, history, today )

                if detected:
                    flags[name] = detected

            # Detectors seperated by ;
            # Fields seperated by ,
            row["flags"] = ";".join(
                f"{name}:{','.join( fields )}" for name, fields in flags.items()
            ) or None

            # Loop through all imputation techniques
            for name, imputor in IMPUTORS.items():
                if flags:
                    imputed = imputor( row, currentDate, history, today )

                    for field, value in imputed.items():
                        row[f"{name}_{field}"] = value
                else:
                    for field in FIELDS:
                        row[f"{name}_{field}"] = row[field]

            rows.append( row )

        # Update history only after detectors have run
        for symbol, row in today.items():
            history[symbol].append( row )

    # Save to parquet
    flush( rows, Path( "data/imported.parquet" ) )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Sets a seed for reproducible errors across runs.",
    )
    main(seed=parser.parse_args().seed)