import numpy as np
from utils import parse_flags
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


def detect_zero( row, currentDate, history, today ) -> list[str]:
    # Check fields so to see if they are within threshold
    flagged = []

    for field in FIELDS:
        if row[field] == 0:
            flagged.append( field )

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

def detect_missing( row, currentDate, history, today ) -> list[str]:
    # Flag a field that is missing. A missing value IS NOT ZERO!!!!
    flagged = []

    for field in FIELDS:
        value = row.get( field )

        if value is None or value != value:
            flagged.append( field )

    return flagged

def detect_bar( row, currentDate, history, today ) -> list[str]:
    # Flag prices that are outside the expected range.
    flagged = []
    prices = []

    # Collect all available prices.
    for field in FIELDS:
        value = row.get( field )

        if value is None or value != value:
            continue

        prices.append( ( field, float( value ) ) )

    # Check each price against the other prices.
    for field, value in prices:
        others = []

        for name, other in prices:
            if name != field:
                others.append( other )

        if len( others ) == 0:
            continue

        # The dayHigh should be the highest price.
        if field == "dayHigh" and value < max( others ):
            flagged.append( field )

        # The dayLow should be the lowest price.
        elif field == "dayLow" and value > min( others ):
            flagged.append( field )

        # Other prices should be between the high and low.
        elif value > max( others ) or value < min( others ):
            flagged.append( field )

    return flagged


def detect_peer( row, currentDate, history, today ) -> list[str]:
    # Flag stocks that move 20% away from other stocks. this can be usefull as the stock market tends to be correlated or move together.
    flagged = []

    for field in FIELDS:
        base = None

        # last non-error price for this stock.
        for past in reversed( history.get( row["symbol"], [] ) ):
            value = past.get( field )

            if value is None:
                continue
            elif np.isnan(value):
                continue
            elif value <= 0:
                continue

            alreadyflagged = False

            for names in parse_flags( past.get( "flags" ) ).values():
                if field in names:
                    alreadyflagged = True
                    break

            if alreadyflagged:
                continue

            base = float( value ) # last non-error price for this stock named as base price
            break

        current = row.get( field )

        if base is None:
            continue
        elif current is None:
            continue
        elif np.isnan(current):
            continue
        elif current <= 0:
            continue


        #stock's percentage change.
        change = float( current ) / base - 1
        peers = []

        # Compare against the other stocks from today.
        for other in today.values():
            if other is row:
                continue

            other_base = None

            # last non-error price for other stock.
            for past in reversed( history.get( other["symbol"], [] ) ):
                other_value = past.get( field )

                if other_value is None:
                    continue
                elif np.isnan(other_value):
                    continue
                elif other_value <= 0:
                    continue

                alreadyflagged = False

                for names in parse_flags( past.get( "flags" ) ).values():
                    if field in names:
                        alreadyflagged = True
                        break

                if alreadyflagged:
                    continue

                other_base = float( other_value )
                break

            other_value = other.get( field )

            if other_base is None:
                continue
            elif other_value is None:
                continue
            elif np.isnan(other_value):
                continue
            elif other_value <= 0:
                continue

            # other stock's percentage change.
            other_change = float( other_value ) / other_base - 1

            # ignore other stocks not following the trend.
            if abs( other_change ) > 0.5: #50% change in stock price is to much
                continue
            peers.append( other_change )

        # at least three other stocks for comparison.
        if len( peers ) < 3:
            continue

        # Flag the stock as not following peer trend if it differs from the median by at least 20%.
        if abs( change - float( np.median( peers ) ) ) >= 0.20:
            flagged.append( field )

    return flagged


def detect_multi( row, currentDate, history, today ) -> list[str]:
    flagged = set()

    flagged.update( detect_threshold( row, currentDate, history, today ) )
    flagged.update( detect_outlier( row, currentDate, history, today ) )

    return flagged

DETECTORS = {
    "zero": detect_zero,
    "missing": detect_missing,
    "bar": detect_bar,
    "outlier": detect_outlier,
    "peer": detect_peer,
    "multi": detect_multi,
}