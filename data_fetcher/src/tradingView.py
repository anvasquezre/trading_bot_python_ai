import json
import random
import re
import string

import config
import pandas as pd
import requests
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import query
from websocket import create_connection


def search(query, type):
    # type = 'stock' | 'futures' | 'forex' | 'cfd' | 'crypto' | 'index' | 'economic'
    # query = what you want to search!
    # it returns first matching item
    res = requests.get(
        f"https://symbol-search.tradingview.com/symbol_search/?text={query}&type={type}"
    )
    if res.status_code == 200:
        res = res.json()
        assert len(res) != 0, "Nothing Found."
        return res[0]
    else:
        print("Network Error!")
        exit(1)


def generateSession():
    stringLength = 12
    letters = string.ascii_lowercase
    random_string = "".join(random.choice(letters) for i in range(stringLength))
    return "qs_" + random_string


def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st


def constructMessage(func, paramList):
    return json.dumps({"m": func, "p": paramList}, separators=(",", ":"))


def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))


def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))


def sendPingPacket(ws, result):
    pingStr = re.findall(".......(.*)", result)
    if len(pingStr) != 0:
        pingStr = pingStr[0]
        ws.send("~m~" + str(len(pingStr)) + "~m~" + pingStr)


def socketJob(ws, pair, engine):
    while True:
        try:
            result = ws.recv()
            if "quote_completed" in result or "session_id" in result:
                continue
            Res = re.findall("^.*?({.*)$", result)
            if len(Res) != 0:
                jsonRes = json.loads(Res[0])
                if jsonRes["m"] == "qsd":
                    symbol = jsonRes["p"][1]["n"]
                    price = jsonRes["p"][1]["v"]["lp"]
                    volume = jsonRes["p"][1]["v"]["volume"]

                    if price and volume:
                        print(f"{symbol} -> {price} -> {volume}")

                        with engine.connect() as conn:
                            try:
                                stock_id = conn.execute(
                                    text(
                                        f"SELECT stock_id FROM stock WHERE stock_id LIKE '%{pair}%'"
                                    )
                                ).fetchone()
                                stock_id = stock_id[0]
                                id = conn.execute(
                                    text(
                                        f"INSERT INTO stocks_real_time (dt, stock_id, value, volume) VALUES (now(), '{stock_id}', {price}, {volume})"
                                    )
                                )
                                conn.commit()
                            except SQLAlchemyError as e:
                                error = str(e)
            else:
                # ping packet
                sendPingPacket(ws, result)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit(0)
        except Exception as e:
            # print(f"ERROR: {e}\nTradingView message: {result}")
            continue


def getSymbolId(pair, market):
    data = search(pair, market)
    symbol_name = data["symbol"]
    try:
        broker = data["prefix"]
    except KeyError:
        broker = data["exchange"]
    symbol_id = f"{broker.upper()}:{symbol_name.upper()}"
    print(symbol_id, end="\n\n")
    return symbol_id


def get_quotes(pair, market):
    # serach btcusdt from crypto category

    engine = create_engine(config.DB)

    print("Connected to database")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    prices = metadata.tables["stocks_real_time"]
    print("Getting symbols IDs...\n")
    symbol_id = getSymbolId(pair, market)
    print("Starting WebSocket Connection!\n")
    # create tunnel
    tradingViewSocket = "wss://data.tradingview.com/socket.io/websocket"
    headers = json.dumps({"Origin": "https://data.tradingview.com"})
    ws = create_connection(tradingViewSocket, headers=headers)
    session = generateSession()
    print("Session succesfully generated\n")

    # Send messages
    sendMessage(ws, "quote_create_session", [session])
    sendMessage(ws, "quote_set_fields", [session, "lp", "volume"])
    sendMessage(ws, "quote_add_symbols", [session, symbol_id])

    # Start job
    print(f"Starting data retrieval for {symbol_id}\n")
    socketJob(ws, pair, engine)


def get_available_tickers():
    engine = create_engine(config.DB)
    query = """
    SELECT stock_id, name FROM stock
    """
    available_tickers = pd.read_sql(query, engine)
    return available_tickers.to_dict()


if __name__ == "__main__":
    get_quotes("EURUSD", "forex")
