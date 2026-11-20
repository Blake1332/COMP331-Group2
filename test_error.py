
import copy
from error import inject, FIELDS

original = {
    "symbol": "test",
    "open": 150.0,
    "dayHigh": 155.0,
    "dayLow": 147.0,
    "currentPrice": 153.0,
    "volume": 1200000,
}

for i in range( 20 ):
    row = copy.deepcopy( original )

    error = inject( row )

    if error:
        print( f"\nError: {error}" )
        for field in FIELDS:
            print( f"{field}: {original[field]} -> {row[field]}" )