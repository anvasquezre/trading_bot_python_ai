import time
from multiprocessing import Process

import config
from news_scrapper import fetch_news_process, get_available_tickers
from sqlalchemy import create_engine

engine = create_engine(config.DB)


def main_process(ticker):
    print(f"News fethching process started for {ticker}")
    fetch_news_process(ticker)
    return


if __name__ == "__main__":
    process_list = []
    ticker_dict = get_available_tickers(engine)
    ticker_list = list(ticker_dict["name"].values())

    print(f"Currencies found {ticker_list}")
    for ticker in ticker_list:
        # create process
        process = Process(target=main_process, args=(ticker,))
        process_list.append(process)
        time.sleep(config.SLEEP_TIME)
        process.start()
