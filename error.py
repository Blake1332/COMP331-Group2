import random

from vars import FIELDS

MAX_ERRORS = 3

ERROR_CHANCE = 5

# Burst errors (same error for multiple days)
BURST_CHANCE = 2

BURST_MIN = 3
BURST_MAX = 10

ACTIVE_BURSTS = {}

seededRandom = random.Random()

def reset( seed: int | None = None ):
    ACTIVE_BURSTS.clear()

    if seed is not None:
        seededRandom.seed( seed )

def error_zero( row, fields ):
    for field in fields:
        row[field] = 0

def error_missing( row, fields ):
    for field in fields:
        row[field] = None

def error_outlier( row, fields ):
    for field in fields:
        row[field] = row[field] * seededRandom.uniform( 10, 50 )

def error_noise( row, fields ):
    for field in fields:
        row[field] = row[field] * seededRandom.uniform( 0.5, 1.2 )

def error_scaling( row, fields ):
    factor = seededRandom.choice( [0.01, 100] )

    for field in fields:
        row[field] = row[field] * factor

ERRORS = {
    "zero": error_zero,
    "missing": error_missing,
    "outlier": error_outlier,
    "noise": error_noise,
    "scaling": error_scaling,
}

def apply_error( row, error, fields ):
    ERRORS[error]( row, fields )

    # Ensure volume is integer
    if "volume" in fields and row["volume"] is not None:
        row["volume"] = int( row["volume"] )

    return f"{error}:{','.join( fields )}"

def inject( row ):
    errors = []
    affected = set()

    symbol = row["symbol"]

    # Active bursts
    if symbol in ACTIVE_BURSTS:
        burst = ACTIVE_BURSTS[symbol]

        fields = burst["fields"]

        apply_error( row, burst["error"], fields )

        errors.append( f"burst:{burst['error']}:{','.join( fields )}")

        burst["remaining"] -= 1

        if burst["remaining"] <= 0:
            del ACTIVE_BURSTS[symbol]

    # New burst
    elif seededRandom.randint( 1, 100 ) <= BURST_CHANCE:
        scope = seededRandom.choice( ["field", "record"] )
        error = seededRandom.choice( list( ERRORS ) )

        fields = (
            [ seededRandom.choice( FIELDS ) ]
            if scope == "field" else FIELDS
        )

        length = seededRandom.randint( BURST_MIN, BURST_MAX )

        apply_error( row, error, fields )
        affected.update( fields )

        errors.append( f"burst:{error}:{','.join( fields )}")

        if length > 1:
            ACTIVE_BURSTS[symbol] = {
                "error": error,
                "fields": fields,
                "remaining": length - 1,
            }
    
    # Standard errors
    if seededRandom.randint( 1, 100 ) <= ERROR_CHANCE:
        possible = [
            field for field in FIELDS
            if field not in affected
            and isinstance( row.get( field ), ( int, float ) )
            and not isinstance( row[field], bool )
            ]

        if not possible:
            return []

        count = seededRandom.randint( 1, min( MAX_ERRORS, len( possible ) ) )

        for _ in range( count ):
            if not possible:
                break

            scope = seededRandom.choice( ["field", "record"] )
            error = seededRandom.choice( list( ERRORS ) )

            fields = (
                [ seededRandom.choice( possible ) ]
                if scope == "field" else possible.copy()
            )

            apply_error( row, error, fields )

            affected.update( fields )
            errors.append( f"{error}:{scope}:{','.join( fields )}" )

            for field in fields:
                possible.remove( field )

            # Don't attempt more errors if already changing whole record
            if scope == "record":
                break

    # No errors
    return ",".join( errors ) if errors else None

