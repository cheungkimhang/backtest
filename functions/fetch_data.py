from datetime import datetime
import pandas as pd
import requests
import json
import os

class fetch_data:
    
    def __init__(self):
        self.api_key_glassnode = os.getenv('api_key_glassnode')
        self.api_key_coinalyze = os.getenv('api_key_coinalyze')
        self.api_key_coinglass = os.getenv('api_key_coinglass')
        self.api_key_cryptoquant = os.getenv('api_key_cryptoquant')
        self.api_key_santiment = os.getenv('api_key_santiment')
        self.api_key_nodechart = os.getenv('api_key_nodechart')

    def get_price(self, symbol: str, endpoint: str, interval: str, 
                  startTime: datetime, endTime: datetime, limit: int = 1000) -> pd.DataFrame:
        url = "https://fapi.binance.com/fapi/v1/klines"
        df = pd.DataFrame()
        start_timestamp = int(startTime.timestamp()*1000)
        end_timestamp = int(endTime.timestamp()*1000)
        current_timestamp = start_timestamp
        mapping = {
            "1m": 12,
            "5m": 72,
            "15m": 240,
            "30m": 480,
            "1h": 960
        }
        time_interval = mapping.get(interval, 1)
        while current_timestamp <= end_timestamp:
            startTime = current_timestamp
            current_timestamp += (time_interval * 60 * 60 * 1000)
            endTime = current_timestamp - 10
            url = "https://fapi.binance.com/fapi/v1/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit
            }
            response = requests.get(url, params=params)
            data = response.json()
            df_temp = pd.DataFrame(data)
            df = pd.concat([df, df_temp], ignore_index=True)
        df = df.rename(columns = {0: "open time", 1:"open", 2:"high", 3:"low", 4:"close", 5:"volume", 6:"close time", 7:"quote asset volume", 8:"number of trades", 9:"taker buy base asset volume", 10:"taker buy quote asset volume"})    
        df = df.iloc[:, :-1]
        df['open time'] = pd.to_datetime(df['open time'], unit='ms')
        df['open time'] = df['open time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['close time'] = pd.to_datetime(df['close time'], unit='ms')
        df['close time'] = df['close time'].dt.strftime('%Y-%m-%d %H:%M:%S')

        df = df.drop_duplicates(subset='open time', keep='first')

        return df

    def get_data_from_glassnode(self, symbol: str, endpoint: str, interval: str, 
                                startTime: datetime, endTime: datetime, 
                                exchange: str = "binance") -> pd.DataFrame:
        try:
            startTimestamp = int(startTime.timestamp())
            endTimestamp = int(endTime.timestamp())

            params = {
                "a": symbol,
                "f": "JSON",
                "i": interval,
                "e": exchange,
                's': startTimestamp,
                'u': endTimestamp,
                "api_key": self.api_key_glassnode
            }

            response = requests.get(endpoint, params=params)
            print(response) # Raise an exception for non-2xx status codes
            data = response.json()

            if not isinstance(data, list):
                print(f"Unexpected response format from {endpoint}: {data}")
                return None

            data = pd.DataFrame(data)

            data.rename(
                columns={"t": "time", "v": "value"},
                inplace=True,
            )
            data["time"] = pd.to_datetime(data["time"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")

            return data
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {endpoint}: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Unexpected error while fetching data from {endpoint}: {e}")
            return pd.DataFrame()

    def get_data_from_coinglass(self, symbol: str, endpoint: str, interval: str, 
                                startTime: datetime, endTime: datetime, 
                                exchange: str = "binance", limit: int = 500) -> pd.DataFrame:
        startTimestamp = int(startTime.timestamp()*1000)
        endTimestamp = int(endTime.timestamp()*1000)
        url = f"{endpoint}?symbol={symbol}&interval={interval}&limit={limit}&start_time={startTimestamp}&end_time={endTimestamp}"
        try:
            headers = {"coinglassSecret": self.api_key_coinglass, "accept": "application/json"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            json_data = json.loads(response.text)   
            data = json_data['data']

            data = pd.DataFrame(data)
            try:
                data["time"] = pd.to_datetime(data["time"], unit="ms").dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                data["time"] = pd.to_datetime(data["t"], unit="ms").dt.strftime("%Y-%m-%d %H:%M:%S")
            return pd.DataFrame()
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error while fetching data from {url}: {e}")
            return pd.DataFrame()
