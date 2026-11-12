# COMP331 Data Quality - Group 2

## Setup

Instructions for setup and running here.

## Data Flow

detect.py causes xfiance to cache any needed historical data, this is stored in `cache/download.parquet` and `cahce/info.parquet`.

Final output for detect.py is stored in `/data/detect/"detect type".parquet`.

Final output for impute.py is stored in `data/impute/"detect type"-"impute type".parquet`.

## DataFrame Structure

| Column | Description | Stage added | Type |
| symbol | The ticker symbol for  the stock | xfinance | string |

| shortname |  | xfinance |  |
| longname |  | xfinance |  |
| quoteType |  | xfinance |  |
| currency |  | xfinance |  |
| exchange |  | xfinance |  |
| country |  | xfinance |  |
| sector |  | xfinance |  |
| industry |  | xfinance |  |
| open |  | xfinance |  |
| dayHigh |  | xfinance |  |
| dayLow |  | xfinance |  |
| currentPrice |  | xfinance |  |
| volume |  | xfinance |  |
| date | Date record was recieved | detect |  |
| errors | Denotes any errors created by xfinance | xfinance | string (comma seperated list) |
| flags | Denotes any errors found by detector | detect | string (comma seperated list) |
| detected | Confirms detector has been run on record | detect | boolean |
