import pandas as pd
import numpy as np

from detect import DETECTORS
from impute import IMPUTORS

def divide( a, b ):
    return a / b if b else np.nan

def summarize_detector( name: str, flagged: pd.Series, error: pd.Series ) -> dict:
    tp = int((error & flagged).sum())
    tn = int((~error & ~flagged).sum())
    fp = int((~error & flagged).sum())
    fn = int((error & ~flagged).sum())

    return {
        "detector": name,
        "errors": int( error.sum() ),
        "detected": int( flagged.sum() ),
        "caught": tp,
        "missed": fn,
        "false pos": fp,
        "true neg": tn,
        "accuracy": divide( tp + tn, len( error ) ),
        "precision": divide( tp, tp + fp ),
        "recall": divide( tp, tp + fn ),
        "f-score": divide( 2 * tp, 2 * tp + fp + fn ),
    }

def summarize_imputor( name: str, df: pd.DataFrame, flagged: pd.Series ) -> dict:
    sub = df.loc[flagged]

    original = pd.to_numeric( sub["originalPrice"], errors="coerce" )
    imputed = pd.to_numeric( sub[name], errors="coerce" )

    valid = original.notna() & imputed.notna()

    actual = original[valid]
    predicted = imputed[valid]

    errors = ( predicted - actual ).abs()
    pct = errors/actual.abs().replace( 0, np.nan ) * 100

    return {
        "imputor": name,
        "attempted": len( sub ),
        "missing": int( imputed.isna().sum() ),
        "coverage": divide( valid.sum(), len( sub ) ),
        "MAE": errors.mean(),
        "RMSE": np.sqrt( ( errors ** 2 ).mean() ),
        "mean error %": pct.mean(),
        "median error %": pct.median(),
        "max error %": pct.max(),
    }

def main():

    df = pd.read_parquet( "data/imported.parquet" )

    error = df["errors"].notna() & ( df["errors"] != "None" )
    names = df["flags"].fillna( "" ).str.split( "," )

    any_flagged = df["flags"].fillna("").str.strip().ne("")

    # Detectors
    detectors = [ summarize_detector( "ANY", df[ "flags" ].notna(), error ) ]

    for name in DETECTORS:
        flagged = names.apply( lambda f: name in f )
        detectors.append( summarize_detector( name, flagged, error ) )

    # Imputors
    caught = error & any_flagged
    imputors = [ summarize_imputor( name, df, caught ) for name in IMPUTORS ]

    print( "Detectors" )
    print( pd.DataFrame( detectors ).to_string( index=False ) )
    
    print( "\nImputors" )
    print( pd.DataFrame( imputors ).to_string( index=False ) )

if __name__ == "__main__":
    main()