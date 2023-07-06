import pandas as pd
from ta import add_all_ta_features
from datetime import datetime
from sqlalchemy import create_engine
import config
import time
import config

# engine = create_engine('postgresql+psycopg2://dev:dev\
# @172.17.0.1:5432/dev')

engine = create_engine(config.DB)

def get_candles(stock_id:int=None, 
                start:pd.Timestamp=pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London') - pd.Timedelta(days=7), 
                end:pd.Timestamp=pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London'), 
                interval:str='1m') -> pd.DataFrame:
    """ Get candles from database

    Args:
        stock_id (_type_, optional): Stock id Defaults to None.
        start (_type_, optional): pd.Datetime Defaults to Now.
        end (_type_, optional): pd.Datetime Defaults to Now - 7 days.
        interval (str, optional):  candles intervals. Defaults to '1m'. Possible values: 1m, 1h,  1d, 1w, 1mo, 1y

    Returns:
        _type_: _description_
    """
    try:
        if stock_id:
            query = f"SELECT * FROM quotes_{interval} WHERE stock_id = '{stock_id}' AND bucket BETWEEN '{start}' AND '{end}' ORDER BY bucket DESC"
            df = pd.read_sql_query(query,con=engine)
        else:
            return print("Please provide stock_id")
        return df
    except Exception as e:
        print(e)

def add_indicators(data:pd.DataFrame) -> pd.DataFrame:
    """ Add indicators to dataframe using ta library

    Args:
        data (pd.DataFrame): ohlcv data

    Returns:
        pd.DataFrame: dataframe with indicators
    """    
    df = data.copy()
    df = add_all_ta_features(data, open="open", high="high", low="low", close="close", volume="volume", fillna=True)
    return df


def main(now:pd.Timestamp=None, stock_id:str=None,
         ):
    """ Main function

    Args:
        now (pd.Timestamp, optional): Actual time. Defaults to pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London').
        stock_id (str, optional): Stock. Defaults to None.

    Returns:
        
    """   
    end = now
    start = now - pd.Timedelta(days=7)
    candles = get_candles(stock_id=stock_id, start=start, end=end, interval='1m')    
    data = add_indicators(candles)
    print(data.head(5)) 
    return data
    

if __name__ == "__main__":
    
    
    while True:
        now = pd.Timestamp=pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London')
        main(now, stock_id='EURUSD=X')
        
        time.sleep(config.SLEEP_INTERVAL)