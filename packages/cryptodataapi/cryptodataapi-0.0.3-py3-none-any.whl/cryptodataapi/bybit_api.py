import pytz
import datetime
import pandas as pd
from pybit import spot, usdt_perpetual


class BybitAPI:

    def __init__(self):
        self.spot_api = spot.HTTP('https://api.bybit.com')
        self.api = usdt_perpetual.HTTP('https://api.bybit.com')

    def get_spot_symbols(self):
        symbols = self.spot_api.query_symbol()['result']
        return [d['name'] for d in symbols]

    def get_usdt_symbols(self):
        symbols = self.api.query_symbol()['result']
        return [d['name'] for d in symbols if 'USDT' in d['name']]

    def get_spot_data(self,
                      symbol: str,
                      interval: str,
                      count: int = None):

        mins = int(interval.replace('m', ''))

        if mins not in [1, 5, 15, 60, 240]:
            raise Exception('Data request can only take intervals of: 1m, 5m, 15m, 60m, 240m')

        if mins >= 60:
            interval = f'{mins // 60}h'
            date_fmt = '%Y-%m-%d %H:00:00'
        else:
            date_fmt = '%Y-%m-%d %H:%M:00'

        data = self.spot_api.query_kline(symbol=symbol, interval=interval)
        df = pd.DataFrame(data['result'])
        df.columns = ['Open time', 'Open', 'High', 'Low', 'Close',
                      'Volume', 'endTime', 'quoteAssetVolume', 'trades',
                      'takerBaseVolume', 'takerQuoteVolume']
        df = df[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']]
        tz = pytz.timezone('Asia/Seoul')
        df['Open time'] = df['Open time'].apply(lambda t: datetime.datetime.fromtimestamp(t / 1000, tz))

        result = df[df['Open time'] < datetime.datetime.now(tz=tz).strftime(date_fmt)]
        if count is None:
            result = result.reset_index(drop=True)
        else:
            result = result.iloc[-count:].reset_index(drop=True)
        return result


if __name__ == '__main__':
    api = BybitAPI()

    spot = api.get_spot_symbols()
    print(spot)

    btcusdt = api.get_spot_data(symbol='BTCUSDT', interval='60m', count=1000)
    print(btcusdt)
