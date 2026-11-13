import pandas as pd
from vars import START, LENGTH, SYMBOLS, COLUMNS
from pathlib import Path
from datetime import date, timedelta
from detect import DETECTORS
from impute import IMPUTORS

def summarize_detector( name: str, flagged: pd.Series, error: pd.Series ) -> dict:
    return {
        "detector": name,
        "errors": int( error.sum() ),
        "detected": int( flagged.sum() ),
        "caught": int( ( error & flagged ).sum() ),
        "missed": int( (error & ~flagged ).sum() ),
        "false_pos": int( ( ~error & flagged ).sum() ),
    }

def summarize_imputor( name: str, df: pd.DataFrame, flagged: pd.Series ) -> dict:
    sub = df[flagged]
    pct = ( sub[name] - sub["originalPrice"] ).abs() / sub["originalPrice"] * 100

    return {
        "imputor": name,
        "no value": int( sub[name].isna().sum() ),
        "mean error pct ": float( pct.mean() ),
        "max error pct": float( pct.max() ),
    }

def main():

    df = pd.read_parquet( "data/imported.parquet" )

    error = df["errors"].notna() & ( df["errors"] != "None" )
    names = df["flags"].fillna( "" ).str.split( "," )

    # Detectors
    detectors = [ summarize_detector( "ANY", df[ "flags" ].notna(), error ) ]

    for name in DETECTORS:
        flagged = names.apply( lambda f: name in f )
        detectors.append( summarize_detector( name, flagged, error ) )

    # Imputors
    caught = error & df["flags"].notna()
    imputors = [ summarize_imputor( name, df, caught ) for name in IMPUTORS ]

    print( "Detectors" )
    print( pd.DataFrame( detectors ).to_string( index=False ) )
    print( "\nImputors" )
    print( pd.DataFrame( imputors ).to_string( index=False ) )

if __name__ == "__main__":
    main()