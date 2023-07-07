import pandas as pd
from ta import add_all_ta_features
from datetime import datetime
from sqlalchemy import create_engine,text
import config
from typing import Optional
import ta
import warnings
warnings.filterwarnings("ignore")

# engine = create_engine('postgresql+psycopg2://dev:dev\
# @172.17.0.1:5432/dev')


def get_candles(stock_id:int=None, 
                start = pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London') - pd.Timedelta(days=7),
                end:pd.Timestamp=pd.to_datetime(datetime.now().astimezone()).tz_convert('Europe/London'), 
                interval:str='1m',
                time_delta:Optional[pd.Timedelta] = None,
                engine = create_engine(config.DB)) -> pd.DataFrame:
    """ Get candles from database

    Args:
        stock_id (_type_, optional): Stock id Defaults to None.
        start (_type_, optional): pd.Datetime Defaults to Now.
        end (_type_, optional): pd.Datetime Defaults to Now - 7 days.
        interval (str, optional):  candles intervals. Defaults to '1m'. Possible values: 1m, 1h,  1d, 1w, 1mo, 1y

    Returns:
        _type_: _description_
    """
    if time_delta:
        start = end - time_delta
    try:
        if stock_id:
            query = f"SELECT * FROM quotes_{interval} WHERE stock_id = '{stock_id}' AND bucket BETWEEN '{start}' AND '{end}' ORDER BY bucket DESC"
            df = pd.read_sql_query(query,con=engine)
        else:
            return print("Please provide stock_id, start and end dates")
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


def add_trends(df:pd.DataFrame) -> pd.DataFrame:
    try:
        if df.empty:
            print("No df provided")
        else:
            df.sort_values(by="bucket", ascending=True, inplace=True)
            windows = [10,20,30,50,100,200]

            for window in windows:
                df[f"ema_{window}"] = ta.trend.EMAIndicator(close=df["close"], window=window, fillna=True).ema_indicator()
                df[f"sma_{window}"] = ta.trend.SMAIndicator(close=df["close"], window=window, fillna=True).sma_indicator()
            
            ichimoku = ta.trend.IchimokuIndicator(df['high'], df['low'], window1=9, window2=26, window3=52, visual=False)
            df['tenkan_sen'] = ichimoku.ichimoku_conversion_line()
            df['kijun_sen'] = ichimoku.ichimoku_base_line()
            df['senkou_span_a'] = ichimoku.ichimoku_a()
            df['senkou_span_b'] = ichimoku.ichimoku_b()
            df['chikou_span'] = df['close'].shift(-26)
            df["vwap"] = ta.volume.VolumeWeightedAveragePrice(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"], window=20, fillna=True).volume_weighted_average_price()
            df["hull"] = ta.trend.WMAIndicator(close=df["close"], window=20, fillna=True).wma()
            return df
    except Exception as e:
        return print(e)
    
def add_oscilators(df:pd.DataFrame=None) -> pd.DataFrame:
    try:
        if df.empty:
            print("No df provided")
        else:
            df.sort_values(by="bucket", ascending=True, inplace=True)
            df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14, fillna=False).rsi()
            
            stoch = ta.momentum.StochRSIIndicator(close=df["close"], window=14, smooth1=3, smooth2=3, fillna=False)
        
            df["stoch_k"] = stoch.stochrsi_k()
            df["stoch_d"] = stoch.stochrsi_d()
            
            df["cci"] = ta.trend.CCIIndicator(high=df["high"], low=df["low"], close=df["close"], window=20, constant=0.015, fillna=False).cci()
            adx = ta.trend.ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=14, fillna=False)
            df["adx"] = adx.adx()
            df["adx_plus_di"] = adx.adx_pos()
            df["adx_minus_di"] = adx.adx_neg()
            
            df["aws_os"] = ta.momentum.AwesomeOscillatorIndicator(high=df["high"], low=df["low"], window1=5, window2=34, fillna=False).awesome_oscillator()
            df["roc"] = ta.momentum.ROCIndicator(close=df["close"], window=10, fillna=False).roc()
            
            macd = ta.trend.MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9, fillna=False)
            df["macd"] = macd.macd()
            df["macd_signal"] = macd.macd_signal()
            
            stoch_os = ta.momentum.StochasticOscillator(
    close=df['close'], high=df['high'], low=df['low'], window=14, smooth_window=3
)
            df["sto_fast"] = stoch_os.stoch()
            df["sto_signal"] = stoch_os.stoch_signal()
            

            df["williams_r"] = ta.momentum.WilliamsRIndicator(high=df["high"], low=df["low"], close=df["close"], lbp=14, fillna=False).williams_r()
            df["ultimate_os"] = ta.momentum.UltimateOscillator(high=df["high"], low=df["low"], close=df["close"], window1=7, window2=14, window3=28, weight1=4.0, weight2=2.0, weight3=1.0, fillna=False).ultimate_oscillator()
            return df
    except Exception as e:
        return print(e)
    
    
def add_tradingview_metrics(df:pd.DataFrame=None, tail:Optional[bool]=False)-> pd.DataFrame:
    try:
        if df.empty:
            print("No df provided")
        else:
            data = df.copy()
            data = add_trends(data)
            data = add_oscilators(data)
            
            if tail:
                return data.tail()
            return data
    except Exception as e:
        return print(e)
    
    
def get_latest_value(stock_id:str, engine = create_engine(config.DB)) -> float:
    try:
        query = f"SELECT value FROM stocks_real_time WHERE stock_id = '{stock_id}' ORDER BY dt DESC LIMIT 1"
        with engine.connect() as con:
            value = con.execute(text(query)).fetchone()
            value = float(value[0])
        return value
    except Exception as e:
        return print(e)
    
def get_available_tickers():
    engine = create_engine(config.DB)
    query = """
    SELECT stock_id, name FROM stock
    """
    available_tickers = pd.read_sql(query,engine)
    return available_tickers.to_dict()