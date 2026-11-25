import pandas as pd
from utils import parse_flags

"""
Notes:
- Create a cheater method that just uses the original values?

Data Info:
    Row
        Description: A single stock's data for the day.
        Type: dict
        Structure: Key is the column name, value is the column value.
        Fields: COLUMNS from vars.py

    currentDate
        Description: Date currently being processed.
        Type: datetime.date

    history
        Description: Past data for for all symbols.
        Type: dict[str, list[dict]]
        Structure: Key is the ticker symbol, and the value is all the row dicts collected.
        Fields: COLUMNS from vars.py

    today
        Description: A record for each symbol downloaded on the day.
        Type: dict[str, dict]
        Structure: Key is the stock ticker, value is the row (for "today") for that stock.
        Fields: COLUMNS from vars.py

    Return
        Description: Dict 
        Type: dict[str, float | None]
        Structure: Key is the field name, value is the imputed value.

"""

def impute_locf( row, currentDate, history, today ) -> dict:
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

def impute_other( row, currentDate, history, today ) -> dict:
    affected = set()

    for fields in parse_flags( row["flags"] ).values():
        affected.update( fields )

    return {field: 50.0 for field in affected}

def impute_mean(row, currentDate, history, today) -> dict:
    # Find all fields that need to be replaced.
    affected = set()

    for fields in parse_flags(row["flags"]).values():
        affected.update(fields)

    result = {}

    #last 10 previous records for the stock.
    previous = history[row["symbol"]][-10:]

    # mean
    for field in affected:
        values = []

        # if missing dont use
        for past in previous:
            value = past[field]

            if pd.notna(value):
                values.append(float(value))
            else:
                continue

        # Use the average, if no previous values exist use none
        if len(values) > 0:
            result[field] = sum(values) / len(values)
        else:
            result[field] = None

    return result


def impute_median( row, currentDate, history, today ) -> dict:
    affected = set()

    for fields in parse_flags( row["flags"] ).values():
        affected.update( fields )

    result = {}
    previous = history[ row["symbol"] ][-10:]

    # last 10 previous records.
    for field in affected:
        values = []

        # if missing dont use
        for past in previous:
            value = past[field]

            if pd.notna( value ):
                values.append( float( value ) )

        if len( values ) > 0:
            result[field] = float( pd.Series( values ).median() )
        else:
            result[field] = None

    return result


def impute_interpolate( row, currentDate, history, today ) -> dict:
    affected = set()

    for fields in parse_flags( row["flags"] ).values():
        affected.update( fields )

    result = {}

    # estimate
    for field in affected:
        previous = None
        next_value = None

        # last non-error value
        for past in reversed( history[ row["symbol"] ] ):
            if pd.notna( past[field] ):
                previous = float( past[field] )
                break

        #today's value if one is available. 
        if field in today and pd.notna( today[field] ):
            next_value = float( today[field] )

        # try our best to average values if we can
        if previous is not None and next_value is not None:
            result[field] = ( previous + next_value ) / 2
        elif previous is not None:
            result[field] = previous
        elif next_value is not None:
            result[field] = next_value
        else:
            result[field] = None

    return result


IMPUTORS = {
    "locf": impute_locf,
    "mean": impute_mean,
    "median": impute_median,
    "interpolate": impute_interpolate,
    "other": impute_other,
}