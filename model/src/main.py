import pandas as pd
from trading_monitor import get_candles,add_tradingview_metrics
import time
import config
from datetime import datetime

def main(now:pd.Timestamp=None, stock_id:str=None,interal='1m',
         ):
    """ Main function

    Args:
        now (pd.Timestamp, optional): Actual time. Defaults to pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London').
        stock_id (str, optional): Stock. Defaults to None.

    Returns:
        
    """   
    end = now
    start = now - pd.Timedelta(days=7)
    candles = get_candles(stock_id=stock_id, start=start, end=end, interval=interal)    
    data = add_tradingview_metrics(candles)
    data
    return data
    

if __name__ == "__main__":
    
    
    while True:
        now = pd.Timestamp=pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London')
        main(now, stock_id='EURUSD=X')
        
        time.sleep(config.SLEEP_INTERVAL)