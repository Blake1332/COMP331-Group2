from vars import FIELDS

"""
Notes:
- Ignore weekend/holiday rows? They will have no data
- Create cheater method that just checks the error column?

"""


def detect_threshold( row, currentDate, history, today ) -> bool:
    # Check fields so to see if they are within threshold
    flagged = []

    for field in FIELDS:
        if row[field] == 0:
            flagged.append(field)

    return flagged


def detect_other( row, currentDate, history, today ) -> bool:
    # Check fields so to see if...
    flagged = []

    return flagged

DETECTORS = {
    "threshold": detect_threshold,
    "other": detect_other,
}