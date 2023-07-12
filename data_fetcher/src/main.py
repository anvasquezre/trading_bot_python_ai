import time
from multiprocessing import Process, current_process

from tradingView import get_available_tickers, get_quotes


def get_single_quotes(ticker, exchange):
    # Your implementation of the get_quotes function goes here
    print(f"Data fethching process started for {ticker}")
    get_quotes(ticker, exchange)
    return


if __name__ == "__main__":
    ticker_dict = get_available_tickers()
    ticker_list = list(ticker_dict["name"].values())

    process_list = []
    for ticker in ticker_list:
        # create process
        process = Process(target=get_single_quotes, args=(ticker, "forex"))
        process_list.append(process)
        time.sleep(2)
        process.start()
