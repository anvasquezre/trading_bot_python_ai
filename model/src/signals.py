import re
from typing import Any, List, Optional
from numpy import sign
import pandas as pd
from trading_monitor import get_latest_value


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
    
    signals['ichimoku'] = "NEUTRAL"
    signals.loc[(signals['tenkan_sen'] > signals['kijun_sen']) & (signals['close'] > signals['senkou_span_a']) &
        (signals['close'] > signals['senkou_span_b']) & (signals['close'] > signals['chikou_span']), 'signal'] = "BUY"
    signals.loc[(signals['tenkan_sen'] < signals['kijun_sen']) & (signals['close'] < signals['senkou_span_a']) &
        (signals['close'] < signals['senkou_span_b']) & (signals['close'] < signals['chikou_span']), 'signal'] = "SELL"
    
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