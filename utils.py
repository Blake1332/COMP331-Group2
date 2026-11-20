import pandas as pd

def parse_flags( value ):
    if pd.isna( value ):
        return {}

    result = {}

    for item in value.split( ";" ):
        name, fields = item.split( ":", 1 )
        result[name] = fields.split( "," )

    return result