from functions.fetch_data import fetch_data
from datetime import datetime
import pytz
import pandas as pd

fd = fetch_data()

# Information
coin = "BTC"
pair = f"{coin}USDT"
endpoint = "https://api.glassnode.com/v1/metrics/distribution/balance_exchanges"
data_name = endpoint.split('/')[-1]
interval = "1h"
utc_tz = pytz.timezone('UTC')
startTime = datetime(2021, 1, 1, tzinfo=utc_tz)
endTime = datetime.now(utc_tz)
exchange = "binance"

# Fetch exchange balance data from Glassnode API
exchange_balance_df = fd.get_data_from_glassnode(coin, endpoint, interval, startTime, endTime, exchange)
exchange_balance_df = exchange_balance_df.rename(columns={"value": data_name})
exchange_balance_df.to_csv(f"raw_data/{coin}_{data_name}_{interval}.csv", index = False)

# Fetch pair price data from Binance API
price_df = fd.get_price(pair, endpoint, interval, startTime, endTime)
price_df.to_csv(f"raw_data/{pair}_price_{interval}.csv", index = False)

# Prepare cleaned dataset
price_df = price_df.rename(columns={"open time": "time", "open": "price"})
merged_df = pd.merge(price_df, exchange_balance_df, on="time", how="inner")
final_df = merged_df[['time', 'price', data_name]]

# Save the cleaned dataset
final_df.to_csv(f"cleaned_data/{pair}_{data_name}_price_{interval}.csv", index = False)
