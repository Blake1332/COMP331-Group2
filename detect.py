import numpy as np
from vars import FIELDS

"""
Notes:
- Ignore weekend/holiday rows? They will have no data
- Create cheater method that just checks the error column?

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
        list[str]: Name of each field that was flagged by the detector

"""


def detect_threshold( row, currentDate, history, today ) -> list[str]:
    # Check fields so to see if they are within threshold
    flagged = []

    for field in FIELDS:
        if row[field] == 0:
            flagged.append(field)

    return flagged


def detect_outlier( row, currentDate, history, today ) -> list[str]:
    flagged = []

    past = history.get( row["symbol"], [] )[-20:]

    for field in FIELDS:
        values = [ float(r[field]) for r in past if r.get(field) is not None ]

        if len(values) < 5:
            continue

        q1, q3 = np.percentile( values, [25, 75] )
        iqr = q3 - q1

        val = row.get(field)
   
        if val is not None and not (q1 - 3 * iqr <= val <= q3 + 3 * iqr):
            flagged.append(field)

    return flagged

def detect_other( row, currentDate, history, today ) -> list[str]:
    flagged = []

    return flagged

def detect_multi( row, currentDate, history, today ) -> list[str]:
    flagged = set()

    flagged.update( detect_threshold( row, currentDate, history, today ) )
    flagged.update( detect_outlier( row, currentDate, history, today ) )

    return flagged

DETECTORS = {
    "threshold": detect_threshold,
    "outlier": detect_outlier,
    "other": detect_other,
}