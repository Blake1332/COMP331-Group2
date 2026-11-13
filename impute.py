import pandas as pd
from vars import START, LENGTH, SYMBOLS, COLUMNS
from pathlib import Path
from datetime import timedelta

def impute_locf( row, currentDate, history, today ):
    # Iterate back to last non-error value
    for past in reversed( history[ row["symbol"] ] ):
        if not past["detected"]:
            row["currentPrice"] = past["currentPrice"]
            break
    return row

def impute_other( row, currentDate, history, today ):
    row["currentPrice"] = 1
    return row

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

    files = sorted( folder.glob( "*.parquet" ) )

    # TODO: Switch to loading each file, one at a time
    for file in files:
        df = pd.read_parquet( file )
        detectorName = file.stem

        dataByDate = { d: f for d, f in df.groupby( "date" ) }
        
        results = { name: [] for name in IMPUTORS }
        history = { symbol: [] for symbol in SYMBOLS }

        for i in range( LENGTH ):
            currentDate = START + timedelta( days=i )

            dataForDay = dataByDate.get( currentDate )

            if dataForDay is None:
                continue

            today = { record["symbol"]: record for record in dataForDay.to_dict( "records" ) }

            # Loop through all stocks
            for symbol, baseline in today.items():
                # Loop through all detection techniques
                for imputorName, imputor in IMPUTORS.items():

                    row = dict( baseline )

                    if row["detected"]:
                        row = imputor( row, currentDate, history, today )

                    print( detectorName, imputorName, row )
                    results[imputorName].append( row )

            # Update history only after detectors have run
            for symbol, baseline in today.items():
                history[symbol].append( baseline )

            # Save to parquet
            for imputorName, rows in results.items():
                flush( rows, Path( "data/impute" ) / f"{detectorName}-{imputorName}.parquet" )

if __name__ == "__main__":
    main()