import time
import datetime
import traceback
import pandas as pd
from binance.client import Client
from dateutil.relativedelta import relativedelta


class BinanceAPI:

    def __init__(self):
        self.client = Client()

    def get_spot_info(self):
        return self.client.get_exchange_info()

    def get_spot_symbols(self):
        info = self.get_spot_info()
        is_spot = lambda d: 'USDT' in d['symbol'] and 'SPOT' in d['permissions']
        symbols = [d['symbol'] for d in info['symbols'] if is_spot(d)]
        return symbols

    def _get_spot_data(self,
                       symbol: str,
                       interval: str,
                       start_time: int = None,
                       end_time: int = None):
        """
        :param symbol: BTCUSDT
        :param interval: 1m, 3m, 5m, 10m, 15m, 1h, 4h, 1d
        :param start_time: timestamp
        :param end_time: timestamp
        :return: pd.DataFrame
        """
        if not end_time:
            end_time = int(datetime.datetime.now().timestamp() * 1000)

        columns = [
            'Open time',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'Close time',
            'Quote asset volume',
            'Number of trades',
            'Taker buy base asset volume',
            'Taker buy quote asset volume',
            'Ignore'
        ]
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time,
            'limit': 1000
        }
        data = self.client._get('klines', data=params, version='v3')
        df = pd.DataFrame(data)
        df.columns = columns
        df['Open time'] = df['Open time'].apply(lambda t: datetime.datetime.fromtimestamp(t // 1000))
        df['Close time'] = df['Close time'].apply(lambda t: datetime.datetime.fromtimestamp(t // 1000))
        return df

    def get_spot_data(self,
                      symbol: str,
                      interval: str,
                      count: int):
        """
        :param symbol: BTCUSDT, ETHUSDT, ...
        :param interval: 1m, 5m, 15m, 60m, 120m, 240m, ...
        :param count: integer
        :return: pd.DataFrame
        """
        return_columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']
        mins = int(interval.replace('m', ''))
        if mins >= 60:
            interval = f'{mins // 60}h'
        data = self._get_spot_data(symbol, interval)
        if len(data) >= count:
            return data.iloc[-count:].reset_index(drop=True)[return_columns]
        else:
            result = data
            result_len = len(result)
            while len(result) < count:
                time.sleep(0.1)
                end_time = int(result.iloc[0]['Open time'].timestamp() * 1000)
                data = self._get_spot_data(symbol, interval, end_time=end_time)
                data = data[~data['Open time'].isin(result['Open time'])]
                result = pd.concat([data, result], axis=0)
                if result_len != len(result):
                    result_len = len(result)
                else:
                    break
            return result[-count:].reset_index(drop=True)[return_columns]

    def get_spot_data_by_month(self, symbol: str, year: int, month: int):
        start_time = datetime.datetime(year, month, 1)
        end_time = start_time + relativedelta(months=1) - pd.Timedelta(minutes=1)

        get_func = self._get_spot_data

        try:
            data = get_func(symbol=symbol,
                            interval='1m',
                            start_time=int(start_time.timestamp() * 1000),
                            end_time=int(end_time.timestamp() * 1000))
            start_time = data.iloc[-1]['Open time'] - pd.Timedelta(hours=10)

            if end_time <= start_time:
                done = True
            else:
                done = False

            result = data
            prev_start_time = None

            while not done:
                time.sleep(0.1)
                data = get_func(symbol=symbol,
                                interval='1m',
                                start_time=int(start_time.timestamp() * 1000),
                                end_time=int(end_time.timestamp() * 1000))
                start_time = data.iloc[-1]['Open time'] - pd.Timedelta(hours=10)
                data = data[~data['Open time'].isin(result['Open time'])]
                result = pd.concat([result, data], axis=0)

                if prev_start_time == start_time:
                    done = True
                else:
                    prev_start_time = start_time

        except:
            traceback.print_exc()
            print(f'BinanceAPI.get_data_by_month({symbol}, {year}, {month}) -> API error')
            result = None

        return result[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']]


if __name__ == '__main__':
    api = BinanceAPI()

    info = api.get_spot_info()
    print(info)

    # 1. Spot Symbols
    symbols = api.get_spot_symbols()
    print(symbols)

    # 2. Low level request of spot OHLCV data
    btcusdt = api._get_spot_data(symbol='BTCUSDT', interval='1h')
    print(btcusdt)

    # 3. Spot OHLCV API request
    btcusdt = api.get_spot_data(symbol='BTCUSDT', interval='1m', count=100)
    print(btcusdt)

    # 4. Request OHLCV data by month
    data = api.get_spot_data_by_month(symbol='BTCUSDT', year=2021, month=1)
    print(data)
