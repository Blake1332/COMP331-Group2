from datetime import date
from xfinance import info

result = info( "AAPL", date(2021,6,15) )

print( result )