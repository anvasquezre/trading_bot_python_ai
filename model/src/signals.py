import re
from typing import Any, List, Optional
from numpy import sign
import pandas as pd
from trading_monitor import get_latest_value
from sqlalchemy import create_engine
import config

def check_ma(value:float, ma:float) -> str:
    """_This function checks the moving average signals 

    Args:
        value (float): _description_
        ma (float): _description_

    Returns:
        str: _description_
    """    
    if ma > value:
        return "SELL"
    elif ma < value:
        return "BUY"
    else:
        return "HOLD"
    
    
def check_ichimoku_signals(df:pd.DataFrame, columns:Optional[List[str]]=None)-> pd.DataFrame:
    signals = df.copy()
    
    signals['ichimoku'] = "HOLD"
    signals.loc[(signals['tenkan_sen'] > signals['kijun_sen']) & (signals['close'] > signals['senkou_span_a']) &
        (signals['close'] > signals['senkou_span_b']) & (signals['close'] > signals['chikou_span']), 'ichimoku'] = "BUY"
    signals.loc[(signals['tenkan_sen'] < signals['kijun_sen']) & (signals['close'] < signals['senkou_span_a']) &
        (signals['close'] < signals['senkou_span_b']) & (signals['close'] < signals['chikou_span']), 'ichimoku'] = "SELL"
    
    return signals.drop(columns=['tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b', 'chikou_span'])


def check_ma_signals(df:pd.DataFrame, columns:Optional[List[str]]=None)-> pd.DataFrame:
    """_This function checks the moving average signals 

    Args:
        df (pd.DataFrame, optional): _description_. Defaults to None.
        columns (List[str], optional): _description_. Defaults to [].

    Returns:
        pd.DataFrame: _description_
    """ 
    signals = df.copy()
    windows = [10,20,30,50,100,200]
    windows_str = ['hull', 'vwap']
    try:
        if columns:
            col_names = columns
        else:
            col_names = [f"ema_{window}" for window in windows] + [f"sma_{window}" for window in windows] + windows_str
        for col in col_names:
            signals[col] = signals.apply(lambda row: check_ma(row.close, row[col]), axis=1)
        
        return signals
    except Exception as e:
        print(e)
        return pd.DataFrame()

##

def check_rsi_signals(df:pd.DataFrame, column:Optional[str]=None)-> pd.DataFrame:
    signals = df.copy()
    default_col = "rsi"
    try:
        if column:
            col_name = column
        else:
            col_name = default_col
            
        signals['signal'] = 'HOLD'
        
        for i in range(1, len(signals)):
            if signals[col_name][i] < 30 and signals[col_name][i] > signals[col_name][i - 1]:
                signals['signal'][i] = 'BUY'
            elif signals[col_name][i] > 70 and signals[col_name][i] < signals[col_name][i - 1]:
                signals['signal'][i] = 'SELL'
            else:
                signals['signal'][i] = 'HOLD'
            
        signals[col_name] = signals['signal'].copy()
        signals.drop(columns=['signal'], inplace=True)
        return signals
    except Exception as e:
        print(e)
        return pd.DataFrame()

def check_stoch_kd_signals(df:pd.DataFrame, columns:Optional[List[str]]=None)-> pd.DataFrame:
    signals = df.copy()
    cols_str = ['stoch_k', 'stoch_d'] ## 1 stoch_k , 2 stoch_d

    try:
        if columns:
            col_names = columns
        else:
            col_names = cols_str
            
        signals['signal'] = 'HOLD'
        
        for i in range(1, len(signals)):
            if signals[col_names[0]][i] < 20 and signals[col_names[0]][i] > signals[col_names[1]][i] and signals[col_names[0]][i - 1] < signals[col_names[1]][i - 1]:
                signals.loc[i, 'signal'] = 'BUY'
            elif signals[col_names[0]][i] > 80 and signals[col_names[0]][i] < signals[col_names[1]][i] and signals[col_names[0]][i - 1] > signals[col_names[1]][i - 1]:
                signals.loc[i, 'signal'] = 'SELL'
        
        signals[col_names[0]] = signals['signal']
        signals.drop(columns=['signal',col_names[1]], inplace=True)
        return signals
    except Exception as e:
        print(e)
        return pd.DataFrame()

def check_cci_signals(df:pd.DataFrame, column:Optional[str]=None)-> pd.DataFrame:
    signals = df.copy()
    # Inicializar la columna de señales
    signals['signal'] = 'HOLD'


    default_col = "cci"
    try:
        if column:
            col_name = column
        else:
            col_name = default_col

        # Calcular las señales de compra y venta
        for i in range(1, len(signals)):
            if signals[col_name][i] < -100 and signals[col_name][i] > signals[col_name][i - 1]:
                signals.loc[i, 'signal'] = 'BUY'
            elif signals[col_name][i] > 100 and signals[col_name][i] < signals[col_name][i - 1]:
                signals.loc[i, 'signal'] = 'SELL'
            else:
                signals.loc[i, 'signal'] = 'HOLD'
                
        signals[col_name] = signals['signal'].copy()
        
        signals.drop(columns=['signal'], inplace=True)
        return signals

    except Exception as e:
        print(e)
        return pd.DataFrame()
    
    
def check_adx_signals(df:pd.DataFrame, columns:Optional[List[str]]=None)-> pd.DataFrame:
    signals = df.copy()
    cols_str = ["adx", "adx_plus_di", "adx_minus_di"] ## 1 stoch_k , 2 stoch_d

    try:
        if columns:
            col_names = columns
        else:
            col_names = cols_str
            
        signals['signal'] = 'HOLD'
        
        # Calculate the buy and sell signals
        for i in range(1, len(signals)):
            if signals[col_names[0]][i] > 20 and signals[col_names[1]][i] > signals[col_names[1]][i] and signals[col_names[1]][i - 1] < signals[col_names[2]][i - 1]:
                signals['signal'][i] = 'BUY'
            elif signals[col_names[0]][i] > 20 and signals[col_names[1]][i] < signals[col_names[1]][i] and signals[col_names[1]][i - 1] > signals[col_names[2]][i - 1]:
                signals['signal'][i] = 'SELL'
        
        signals[col_names[0]] = signals['signal']
        signals.drop(columns=['signal',col_names[1],col_names[2]], inplace=True)
        return signals
    except Exception as e:
        print(e)
        return pd.DataFrame()
    
def check_aws_ao_signals(df:pd.DataFrame, column:Optional[str]=None)-> pd.DataFrame:
    signals = df.copy()
    # Inicializar la columna de señales
    signals['signal'] = 'HOLD'

    default_col = "aws_os"
    try:
        if column:
            col_name = column
        else:
            col_name = default_col

        # Calculate the buy and sell signals
        for i in range(1, len(signals)):
            if signals[col_name][i] > 0 and signals[col_name][i-1] < 0:
                signals.loc[i, 'signal'] = 'BUY'
            elif signals[col_name][i] < 0 and signals[col_name][i-1] > 0:
                signals.loc[i, 'signal'] = 'SELL'
            elif signals[col_name][i] > 0 and signals[col_name][i-1] > 0:
                signals.loc[i, 'signal'] = 'BUY'
            elif signals[col_name][i] < 0 and signals[col_name][i-1] < 0:
                signals.loc[i, 'signal'] = 'SELL'
                
        signals[col_name] = signals['signal'].copy()
        signals.drop(columns=['signal'], inplace=True)
        return signals

    except Exception as e:
        print(e)
        return pd.DataFrame()   

def check_roc_signals(df:pd.DataFrame, column:Optional[str]=None)-> pd.DataFrame:
    signals = df.copy()
    # Inicializar la columna de señales
    signals['signal'] = 'HOLD'

    default_col = "roc"
    try:
        if column:
            col_name = column
        else:
            col_name = default_col

        # Calculate the buy and sell signals
        for i in range(1, len(signals)):
            if signals[col_name][i] > signals[col_name][i - 1]:
                signals.loc[i, 'signal'] = 'BUY'
            elif signals[col_name][i] < signals[col_name][i - 1]:
                signals.loc[i, 'signal'] = 'SELL'
            
            
        signals[col_name] = signals['signal'].copy()
        signals.drop(columns=['signal'], inplace=True)
        return signals
    
    except Exception as e:
        print(e)
        return pd.DataFrame() 

def check_macd_signals(df:pd.DataFrame, columns:Optional[List[str]]=None)-> pd.DataFrame:
    signals = df.copy()
    cols_str = ["macd","macd_signal"] ## 1 macd, 2 macd_signal
    try:
        if columns:
            col_names = columns
        else:
            col_names = cols_str
            
        signals['signal'] = 'HOLD'
        
        # Calculate the buy and sell signals
        for i in range(1, len(signals)):
            if signals[col_names[0]][i] > signals[col_names[1]][i]:
                signals.loc[i, 'signal'] = 'BUY'
            elif signals[col_names[0]][i] < signals[col_names[1]][i]:
                signals.loc[i, 'signal'] = 'SELL'
        
        signals[col_names[0]] = signals['signal']
        signals.drop(columns=['signal',col_names[1]], inplace=True)
        return signals
    
    except Exception as e:
        print(e)
        return pd.DataFrame()


def check_sto_fast_signals(df:pd.DataFrame, columns:Optional[List[str]]=None)-> pd.DataFrame:
    signals = df.copy()
    cols_str = ["sto_fast","sto_signal"] ## 1 macd, 2 macd_signal
    try:
        if columns:
            col_names = columns
        else:
            col_names = cols_str
            
        signals['signal'] = 'HOLD'

        # Calculate the buy and sell signals
        for i in range(1, len(signals)):
            if signals[col_names[0]][i] < 20 and signals[col_names[1]][i] < 20 and signals[col_names[0]][i] > signals[col_names[1]][i] and signals[col_names[0]][i - 1] < signals[col_names[1]][i - 1]:
                signals.loc[i, 'signal'] = 'BUY'
            elif signals[col_names[0]][i] > 80 and signals[col_names[1]][i] > 80 and signals[col_names[0]][i] < signals[col_names[1]][i] and signals[col_names[0]][i - 1] > signals[col_names[1]][i - 1]:
                signals.loc[i, 'signal'] = 'SELL'
        
        signals[col_names[0]] = signals['signal']
        signals.drop(columns=['signal',col_names[1]], inplace=True)
        return signals
    
    except Exception as e:
        print(e)
        return pd.DataFrame()

def check_williann_r_signals(df:pd.DataFrame, column:Optional[str]=None)-> pd.DataFrame:
    signals = df.copy()
    # Inicializar la columna de señales
    signals['signal'] = 'HOLD'

    default_col = "williams_r"
    try:
        if column:
            col_name = column
        else:
            col_name = default_col

        # Define the buy and sell thresholds
        lower_band = -80
        upper_band = -20

        # Calculate the buy and sell signals
        for i in range(1, len(signals)):
            if signals[col_name][i] < lower_band and signals[col_name][i] > signals[col_name][i - 1]:
                signals.loc[i, 'signal'] = 'BUY'
            elif signals[col_name][i] > upper_band and signals[col_name][i] < signals[col_name][i - 1]:
                signals.loc[i, 'signal'] = 'SELL'
                    
            
        signals[col_name] = signals['signal'].copy()
        signals.drop(columns=['signal'], inplace=True)
        return signals
    
    except Exception as e:
        print(e)
        return pd.DataFrame() 
    
def check_ultimate_os_signals(df:pd.DataFrame, column:Optional[str]=None)-> pd.DataFrame:
    signals = df.copy()
    # Inicializar la columna de señales
    signals['signal'] = 'HOLD'

    default_col = "ultimate_os"
    try:
        if column:
            col_name = column
        else:
            col_name = default_col

        # Define the buy and sell thresholds
        lower_band = 30
        upper_band = 70
        
        # Calculate the buy and sell signals
        for i in range(1, len(signals)):
            if signals[col_name][i] > upper_band:
                signals.loc[i, 'signal'] = 'BUY'
            elif signals[col_name][i] < lower_band:
                signals.loc[i, 'signal'] = 'SELL'
                    
            
        signals[col_name] = signals['signal'].copy()
        signals.drop(columns=['signal'], inplace=True)
        return signals
    
    except Exception as e:
        print(e)
        return pd.DataFrame()   

def check_all_signals(df:pd.DataFrame) -> pd.DataFrame:
    result = check_ma_signals(df)
    result = check_ichimoku_signals(result)
    result = check_rsi_signals(result)
    result = check_stoch_kd_signals(result)
    result = check_cci_signals(result)
    result = check_adx_signals(result)
    result = check_aws_ao_signals(result)
    result = check_roc_signals(result)
    result = check_macd_signals(result)
    result = check_sto_fast_signals(result)
    result = check_williann_r_signals(result)
    result = check_ultimate_os_signals(result)
    
    return result


def save_signals(df:pd.DataFrame,table:str , ticker:Optional[str]='currency', engine = create_engine(config.DB))-> None:
    try:
        table_name = table
        df.to_sql(table_name, engine, if_exists="append", index=False)
        return print(f"Data saved to {table} for {ticker}")
            
    except Exception as e:
        print(e)
        
        
def type_of_signal(value:float)-> str:
    if value >= -1.0 and value < -0.5:
        return "Strong Sell"
    elif value >= -0.5 and value < -0.1:
        return "Sell"
    elif value >= -0.1 and value <= 0.1:
        return "Hold"
    elif value > 0.1 and value <= 0.5:
        return "Buy"
    elif value > 0.5 and value <= 1.0:
        return "Strong Buy"
    else:
        return "Invalid Value"


def sum_scores(df:pd.DataFrame, type:Optional[str]="total")-> pd.DataFrame:
    signal = df.copy()
    index_set = set(signal.T.iloc[:,:].value_counts().index)
    if ('BUY',) in index_set:
        buy = signal.T.iloc[:,:].value_counts().loc['BUY'].values[0]
    else:
        buy = 0
        
    if ('SELL',) in index_set:
        sell = signal.T.iloc[:,:].value_counts().loc['SELL'].values[0]
    else:
        sell = 0
        
    if ('HOLD',) in index_set:
        hold = signal.T.iloc[:,:].value_counts().loc['HOLD'].values[0]
    else:
        hold = 0
    
    score = (buy*1 + sell*-1 + hold*0)/(buy+sell+hold)
    type = type_of_signal(score) 
    
    return float(buy), float(sell), float(hold), float(score), type

def check_scores(df:pd.DataFrame, columns:Optional[List[str]]=None)-> pd.DataFrame:
    signal = df.copy()
    windows = [10,20,30,50,100,200]
    windows_str = ['hull', 'vwap']
    df_result = {}
    
    try:
        if columns:
            col_names = columns
        else:
            col_names = [f"ema_{window}" for window in windows] + [f"sma_{window}" for window in windows] + windows_str
        
        buy, sell, hold, score, type = sum_scores(signal)
        df_result["total_sell"] = sell
        df_result["total_buy"] = buy
        df_result["total_hold"] = hold
        df_result["total_score"] = score
        df_result["total_recommendation"] = type

        buy, sell, hold, score, type = sum_scores(signal[col_names])
        df_result["ma_sell"] = sell
        df_result["ma_buy"] = buy
        df_result["ma_hold"] = hold
        df_result["ma_score"] = score
        df_result["ma_recommendation"] = type
    
        buy, sell, hold, score, type = sum_scores(signal.drop(columns=col_names).copy())
    
        df_result["os_sell"] = sell
        df_result["os_buy"] = buy
        df_result["os_hold"] = hold
        df_result["os_score"] = score
        df_result["os_recommendation"] = type
        
        return pd.DataFrame().from_dict(df_result, orient='index').T
    except Exception as e:
        print(e)
        return pd.DataFrame()