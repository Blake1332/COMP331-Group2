import pandas as pd
from vars import START, LENGTH, SYMBOLS, COLUMNS
from pathlib import Path
from datetime import date, timedelta


def summarize( detectName: str, imputeName: str, df: pd.DataFrame ) -> dict:
    error = df["errors"].notna() & ~df["errors"].isin( [ "None" ] )
    detected = df["detected"].fillna( False ).astype( bool )
    # diff = ( df["currentPrice"] - df["originalPrice"] ).abs()[detected].dropna()
    diff_pct = ( ( df["currentPrice"] - df["originalPrice"] ).abs() / df["originalPrice"] * 100 )[detected].dropna()

    return {
        "detector": detectName,
        "imputor": imputeName,
        "rows": len( df ),
        "errors": int( error.sum() ),
        "detected": int( detected.sum() ),
        "caught": int( ( error & detected ).sum() ),
        "missed": int( (error & ~detected ).sum() ),
        "false_pos": int( ( ~error & detected ).sum() ),
        "mean error": float( diff_pct.mean() ),
        "max error": float( diff_pct.max() ),
    }

def main():
    # Gather all the parquet files
    folder = Path( "data/impute" )
    files = sorted( folder.glob( "*.parquet" ) )

    summaries = []

    for file in files:
        df = pd.read_parquet( file )
        
        filename = file.stem
        detectorName, imputorName = filename.split( "-" )

        summaries.append( summarize( detectorName, imputorName, df ) )

    report = pd.DataFrame( summaries )

    print( report.to_string( index=False ) )




if __name__ == "__main__":
    main()