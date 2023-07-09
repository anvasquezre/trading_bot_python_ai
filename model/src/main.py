#### /////////////////////////////////////// [INIT] From Mario ///////////////////////////////////////////////

import pandas as pd
from sqlalchemy import create_engine
from trading_monitor import get_candles,add_tradingview_metrics, get_available_tickers
from signals import check_all_signals, save_signals, check_scores
import time
import config
from datetime import datetime
import warnings
from multiprocessing import Process
warnings.filterwarnings("ignore")

def main(stock_id:str=None,interval='1m',
         ):
    while True: 
        """ Main function

        Args:
            now (pd.Timestamp, optional): Actual time. Defaults to pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London').
            stock_id (str, optional): Stock. Defaults to None.

        Returns:
            
        """
        now = pd.Timestamp=pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London')
        engine = create_engine(config.DB)
        end = now
        start = now - pd.Timedelta(days=7)
        cols_to_drop = ['open', 'high', 'low', 'close', 'volume']
        
        
        
        candles = get_candles(stock_id=stock_id, start=start, end=end, interval=interval, engine=engine)
        candles.sort_values(by=['bucket'], inplace=True, ascending=True)   
        data = add_tradingview_metrics(candles)
        last_row = data.tail(1).copy()
        last_row_save = last_row.copy()
        
        last_row_save.drop(cols_to_drop, axis=1, inplace=True)
        last_row_save['stock_id'] = stock_id
        last_row_save['interval'] = interval
        last_row_save['bucket'] = now
        save_signals(last_row_save,'tick_data_vals',stock_id ,engine=engine)
        signals = check_all_signals(last_row)

        signals.drop(cols_to_drop, axis=1, inplace=True)
        signals['stock_id'] = stock_id
        signals['interval'] = interval
        signals['bucket'] = now
        save_signals(signals,'tick_data_signals',stock_id ,engine=engine)
        
        scores = check_scores(signals)
        scores['stock_id'] = stock_id
        scores['interval'] = interval
        scores['bucket'] = now
        save_signals(scores,'signal_scores',stock_id ,engine=engine)
        time.sleep(config.SLEEP_INTERVAL)
    return print("procees finished")
    

if __name__ == "__main__":
    
    ticker_dict = get_available_tickers()
    ticker_list = list(ticker_dict['stock_id'].values())
    interval='1m'
    process_list = []
    for stock_id in ticker_list:
            #create process
            process = Process(target=main, args=(stock_id,interval))
            process_list.append(process)
            time.sleep(config.SLEEP_INTERVAL)
            process.start()
            
            
#### /////////////////////////////////////// [END] From Mario ///////////////////////////////////////////////