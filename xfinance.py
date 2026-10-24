import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import date

downloadPath = Path( "cache/download.parquet" )
infoPath = Path( "cache/info.parquet" )

# Things to not track with
keepInfo = {
    "symbol",
    "shortName",
    "longName",
    "quoteType",
    "currency",
    "exchange",
    "country",
    "sector",
    "industry",
}

# Load cache, or create blank DataFrames
cacheInfo = pd.read_parquet( infoPath ) if infoPath.is_file() else pd.DataFrame()
cacheDownload = pd.read_parquet( downloadPath ) if downloadPath.is_file() else pd.DataFrame()

def info( ticker: str, date: date ) -> dict | None:
    # Check for cached
    if cacheInfo.empty or "ticker" not in cacheInfo.column or ticker not in cacheInfo["ticker"].values:
        addCache( ticker )
    elif cacheDownload.empty or "ticker" not in cacheDownload.column or ticker not in cacheDownload["ticker"].values:
        addCache( ticker )

    output = cacheInfo[ cacheInfo["ticker"] == ticker ]

    if output.empty:
        return None

    output = output.iloc[0].drop( "ticker" ).to_dict()

    date = pd.Timestamp( date ).date()

    prices = cacheDownload[
        ( cacheDownload["ticker"] == ticker ) &
        ( pd.to_datetime( cacheDownload["Date"] ).dt.date == date )
    ]

    if not prices.empty:
        row = prices.iloc[0]

        output.update( {
            "open": float(row["Open"]),
            "dayHigh": float(row["High"]),
            "dayLow": float(row["Low"]),
            "currentPrice": float(row["Close"]),
            "volume": int(row["Volume"]),
        } )

    return output

def addCache( ticker ):
    global cacheInfo, cacheDownload

    # yFiance Download last 5 years
    newDownload = yf.download(
        ticker,
        start="2020-01-01",
        end="2025-01-01",
        auto_adjust=False,
        multi_level_index=False
    )

    if not newDownload.empty:
        newDownload = newDownload.reset_index()
        newDownload["ticker"] = ticker
        cacheDownload = pd.concat([cacheDownload, newDownload], ignore_index=True)

    # yFinance current Info
    newInfo = yf.Ticker( ticker ).info

    if newInfo:
        newInfo = { key: value for key, value in newInfo.items() if key in keepInfo }
        newInfo["ticker"] = ticker
        newInfo = pd.DataFrame( [newInfo] )
        cacheInfo = pd.concat( [cacheInfo, newInfo], ignore_index=True )
    
    # Create folder if needed (both, incase they move)
    infoPath.parent.mkdir( parents=True, exist_ok=True )
    downloadPath.parent.mkdir( parents=True, exist_ok=True )

    # Save parquets
    cacheDownload.to_parquet( downloadPath )
    cacheInfo.to_parquet ( infoPath )