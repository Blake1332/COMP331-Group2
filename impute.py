from utils import parse_flags

"""
Notes:
- Create a cheater method that just uses the original values?

"""

def impute_locf( row, currentDate, history, today ) -> float | None:
    affected = set()

    for fields in parse_flags( row["flags"]).values():
        affected.update( fields )

    result = {}

    # Iterate back to last non-error value
    for field in affected:
        for past in reversed( history[ row["symbol"] ] ):
            if past[field] is not None:
                result[field] = float( past[field] )
                break
        else:
                result[field] = None
                
    return result

def impute_other( row, currentDate, history, today ) -> float | None:
    affected = set()

    for fields in parse_flags( row["flags"] ).values():
        affected.update( fields )

    return {field: 50.0 for field in affected}

IMPUTORS = {
    "locf": impute_locf,
    "other": impute_other,
}