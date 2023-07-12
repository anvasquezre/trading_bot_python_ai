#### /////////////////////////////////////// [INIT] From Mario ///////////////////////////////////////////////

# Importing libraries

from typing import Dict, List, Optional, Union

import config
import pandas as pd
import yfinance as yf
from pymongo import MongoClient
from sqlalchemy import MetaData, create_engine

engine = create_engine(config.DB)
metadata = MetaData()
metadata.reflect(bind=engine)
prices = metadata.tables["stocks_real_time"]
client = MongoClient("localhost", 27017)
db = client["dev"]
db.create_collection(
    "stock",
    {"timeField": "timestamp", "metaField": "metadata", "granularity": "seconds"},
)


def get_data(tickers: List[str], kwargs: Optional[Dict] = {}) -> pd.DataFrame:
    """This function gets the data from yahoo finance and returns a dataframe to initialise the database

    Args:
        tickers (str): tickers, e.g. "AAPL MSFT"
        kwargs (dict, optional): kwargs for yfinance. Defaults to {}.

    Returns:
        pd.DataFrame: dataframe with the data
    """

    data = yf.download(tickers=tickers, period="7d", interval="1m", **kwargs)
    data = data.stack().reset_index()
    cols = ["Datetime", "level_1", "Close", "Volume"]
    data = data[cols].copy()
    data.columns = ["dt", "stock_id", "value", "volume"]
    return data


def save_data(data: pd.DataFrame, table_name: str) -> None:
    data.to_sql(table_name, engine, if_exists="append", index=False)
    return print("Data saved to database")


def main():
    # Get data
    tickers_dict = config.TICKERS

    ticks = pd.DataFrame().from_dict(tickers_dict, orient="index")
    ticks.reset_index(inplace=True, drop=False)
    ticks.columns = ["name", "stock_id"]
    ticks["exchange"] = "FOREX"

    save_data(ticks, "stock")

    tickers = list(tickers_dict.values())
    data = get_data(tickers)
    save_data(data, "stocks_real_time")

    return print("Data Initialized and saved to database")


if __name__ == "__main__":
    main()


#### /////////////////////////////////////// [END] From Mario ///////////////////////////////////////////////
