import pandas as pd
import numpy as np

from detect import DETECTORS
from impute import IMPUTORS
from vars import FIELDS
from utils import parse_flags

def divide( a, b ):
    return round( a / b, 4 ) if b else np.nan

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

    actual = []
    predicted = []

    for field in FIELDS:
        original = pd.to_numeric( sub[f"og_{field}"], errors="coerce" )
        imputed = pd.to_numeric( sub[f"{name}_{field}"], errors="coerce" )

        valid = original.notna() & imputed.notna()

        actual = original[valid]
        predicted = imputed[valid]

    actual = pd.Series( actual )
    predicted = pd.Series( predicted )

    errors = ( predicted - actual ).abs()
    pct = errors / actual.abs().replace( 0, np.nan ) * 100

    attempted = len( sub ) * len( FIELDS )

    return {
        "imputor": name,
        "attempted": attempted,
        "missing": attempted - len( actual ),
        "coverage": divide( len( actual ), attempted ),
        "MAE": errors.mean(),
        "RMSE": np.sqrt( ( errors ** 2 ).mean() ),
        "mean error %": round( pct.mean(), 2 ),
        "median error %": round( pct.median(), 2 ),
        "max error %": round( pct.max(), 2 ),
    }

def main():

    df = pd.read_parquet( "data/imported.parquet" )

    error = df["errors"].notna() & ( df["errors"] != "None" )
    names = df["flags"].apply( parse_flags )

    any_flagged = df["flags"].fillna("").str.strip().ne("")

    # Detectors
    detectors = [ summarize_detector( "ANY", df["flags"].notna(), error ) ]

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