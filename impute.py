def impute_locf( row, currentDate, history, today ) -> float | None:
    # Iterate back to last non-error value
    for past in reversed( history[ row["symbol"] ] ):
        if not past["flags"]:
            return float( past["currentPrice"] )

def impute_other( row, currentDate, history, today ) -> float | None:
    return float( 50.0 )

IMPUTORS = {
    "locf": impute_locf,
    "other": impute_other,
}