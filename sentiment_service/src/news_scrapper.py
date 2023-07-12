import time

import config
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from text_normalizer import normalize_corpus
from thinc import config


def get_urls_daily_fx(ticker):
    pair1, pair2 = ticker[0:3], ticker[3:6]
    url = f"https://www.dailyfx.com/{pair1.lower()}-{pair2.lower()}/news-and-analysis"
    div_class = "dfx-newsAnalysis jsdfx-newsAnalysis pt-2"
    class_ = "dfx-articleListItem jsdfx-articleListItem d-flex mb-3"
    response = requests.get(url)

    # Create a BeautifulSoup object from the response content
    soup = BeautifulSoup(response.content, "html.parser")
    # Find the element with the class "z4rs2b"
    # Find all <a> elements with rel="noopener noreferrer"
    div_elements = soup.find_all("div", class_=div_class)

    divs = soup.find_all("div", class_=div_class)
    links = []
    headers = []
    dates = []

    for div in divs:
        anchor_elements = div.find_all("a", class_=class_)
        for anchor in anchor_elements:
            date_class = "jsdfx-articleListItem__date text-nowrap"
            date_anchor = anchor.find_all("span", class_=date_class)
            date = date_anchor[0].get("data-time")
            dates.append(date)
            href = anchor.get("href")
            links.append(href)
            text = anchor.get_text()
            headers.append(text)
            headers_norm = normalize_corpus(headers)

    return links, headers_norm, dates


def get_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    article_tag = soup.find("article")
    paragraphs = article_tag.find_all("p")
    concatenated_text = " ".join([p.get_text() for p in paragraphs])
    normalized_text = normalize_corpus([concatenated_text])
    return normalized_text


def get_available_tickers(engine):
    query = """
    SELECT stock_id, name FROM stock
    """
    available_tickers = pd.read_sql(query, engine)
    return available_tickers.to_dict()


def check_url_in_db(url, stock_id, engine):
    with engine.connect() as con:
        query = f"""
        SELECT news_url FROM news_data WHERE news_url = '{url}' AND stock_id = '{stock_id}'
        """
        url_in_db = con.execute(text(query)).fetchone()
    return url_in_db is not None


def save_record_to_db(url, stock_id, sentiment_score, date, engine):
    if check_url_in_db(url):
        print(f"URL {url} already exists in the database. Skipping...")
        return
    with engine.connect() as con:
        query = f"""
        INSERT INTO news_data (dt, news_url, stock_id, sentiment_score)
        VALUES ('{date}','{url}', {stock_id}, {sentiment_score})
        """
        con.execute(text(query))


def get_ticker_id(ticker, engine):
    with engine.connect() as con:
        query = f"""
        SELECT stock_id FROM stock WHERE name = '{ticker}'
        """
        id = con.execute(text(query)).fetchone()
    return id


def fetch_news_process(ticker):
    engine = create_engine(config.DB)
    stock_id = get_ticker_id(ticker, engine)[0]
    while True:
        news_url, headers, dt = get_urls_daily_fx(ticker)
        df = pd.DataFrame({"news_url": news_url, "headers": headers, "dt": dt})
        df["in_db"] = df["news_url"].apply(
            lambda x: check_url_in_db(x, stock_id, engine)
        )
        mask = df["in_db"] == False
        news_to_save = df[mask].copy()

        if len(news_to_save) == 0:
            print(
                f"No new news articles found for {ticker}. Sleeping for {config.SLEEP_TIME} seconds..."
            )
        else:
            print(
                f"Found {len(news_to_save)} new news articles for {ticker}. Saving to the database..."
            )
            news_to_save["dt"] = pd.to_datetime(news_to_save["dt"])
            news_to_save["text"] = news_to_save["news_url"].apply(
                lambda x: get_text(x)[0]
            )

            ### Testing with random numbers
            news_to_save["sentiment_score"] = news_to_save["text"].apply(
                lambda x: np.random.uniform(-10, 10)
            )
            news_to_save["stock_id"] = stock_id
            cols_to_save = ["news_url", "dt", "sentiment_score", "stock_id"]
            news_to_save = news_to_save[cols_to_save]
            news_to_save.drop_duplicates(
                subset=["news_url", "dt", "stock_id"], inplace=True
            )
            rows = news_to_save.to_sql(
                "news_data", engine, if_exists="append", index=False
            )
            print(f"Saved {rows} rows to the database")

        time.sleep(config.SLEEP_TIME)
