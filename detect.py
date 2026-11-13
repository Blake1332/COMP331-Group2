def detect_threshold( row, currentDate, history, today ) -> bool:
    # Check if stock has had very large returns from previous
    if row["currentPrice"] == 0:
        return True


def detect_other( row, currentDate, history, today ) -> bool:
    # ?
    return False

DETECTORS = {
    "threshold": detect_threshold,
    "other": detect_other,
}