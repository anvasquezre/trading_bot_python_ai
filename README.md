# Synapse-Data Engineering
**Overall description**

Tradingview socket api for fetching real time prices and news and creating buy and sell signals based on live candle data. All data is stored them in mongodb as timeseries data or simple collections.

**Features**

- Fetches real time stock data and stores it in monogodb
- Fetches real time news data, estimate its sentiment score and associated sentiments, and stores them in mongodb

**Backlog**
- Once uploaded to repo, create links to each service
- Check implementation of new APIs for fetching data
- Create docstring and comment code
- Implement data_fetcher for crypto
- Implement environment variables to avoid config.py files
- Create system architecture diagram
- Check API endpoints if needed 
- Create unitests and integration tests
- **Migrate from postgres to monogodb**


**Finished**

- Backlog task (date) - commit


## How to run

Complete standalone application
```
docker compose up --build
```

## How to use

Let's take a quick overview of each module:

- **api**: [TO DO] It has all the needed code to implement the communication interface between the endpoints and our service. It uses FastAPI and Redis to queue tasks to be processed by our machine learning model.
    - `api/app.py`: Setup and launch our FastAPI api.
    - `api/views.py`: Contains the API endpoints. 
        - *predict*: POST method which receives a set of OHCL data and returns the predicted data for the following 30 minutes.
    - `api/middleware.py`: Implements some extra functions used internally by our api to communicate to redis.
    - `api/settings.py`: It has all the API settings.
    - `api/tests`: [TO DO]Test suite.

- **data_fetcher**: Websocket api for fetching real time stock prices.
    - `data_fetcher/src/config.py`: contains the service variables for configuration.
    - `data_fetcher/src/main.py`: Entrypoint for the service. Main thread in which it connects to tradingview websocket, fetches latest tick values and stores it in a database
    - `data_fetcher/src/tradingView.py`: Implements all the functions realted to connecting to tradingview websocket

- **data_preloader**: Service for initialization of database with previous historical data using yfinance
    - `data_preloader/src/config.py`: contains the service variables for configuration.
    - `data_preloader/src/main.py`: Entrypoint for the service. Main thread in which it connects to yfinance, dowloads the latest 7 days of historical candle data by minute and stores it to a database.
    - `data_preloader/src/health_check.py`: Waiting time for timescale to build. **WARNING**: To be deprecated once migrated to monogodb

- **db**: Service for initialization of database structure in postgreSQL
    - `db.sql`: SQL script for database structure initializacion.**WARNING**: To be deprecated once migrated to monogodb

- **model**: Implements the logic to get buy and sell signals from historical OHLC data stored in mongodb.
    - `model/src/config.py`: Contains the service variables for configuration.
    - `model/src/main.py`: Entrypoint for the service. Main thread in which it estimates indicators, processes them with a specific logic according to the indicator and returns buy and sell signals storing them in a database
    - `model/src/signals.py`: Implementes the logic behind estimating buy and sell signals.
    - `model/src/signals.py`: Implementes the logic behing estimating key indicators from candle data.

- **sentiment_service**: Implements the logic to get all the previous news for the ticks and fetches new news each 30 seconds. Processes each new , estimates its sentiments using OpenAI 3.5 turbo and stores it in a database.
    - `sentiment_service/src/config.py`: Contains the service variables for configuration.
    - `sentiment_service/src/main.py`: Entrypoint for the service. Main thread in which it fetches the latest news, processes them and stores them in a database.
    - `sentiment_service/src/news_scrapper.py`: Implementes the logic behind beautifulsoup and news scrapping.
    - `sentiment_service/src/sentiment_analysis_test.py`: Implementes the logic behing the sentiment analysis with openai.
    - `sentiment_service/src/text_normalizer.py`: Basic text normalizing functions for text preprocessing.

- **tests**: [TO DO ]This module contains integration tests so we can properly check our system's end-to-end behavior is expected.


[TO DO] You can also take a look at the file `System_architecture_diagram.png` to have a graphical description of the microservices and how the communication is performed.

## Folders architecture

```

├── api
│   ├── app.py
│   ├── Dockerfile
│   ├── middleware.py
│   ├── requirements.txt
│   └── settings.py
├── data_fetcher
│   ├── Dockerfile
│   ├── __init__.py
│   ├── requirements.txt
│   └── src
│       ├── config.py
│       ├── __init__.py
│       ├── main.py
│       └── tradingView.py
├── data_preloader
│   ├── Dockerfile
│   ├── __init__.py
│   ├── requirements.txt
│   └── src
│       ├── config.py
│       ├── health_check.py
│       ├── __init__.py
│       ├── main.py
├── db
│   └── init.sql
├── docker-compose.yml
├── EDA.ipynb
├── model
│   ├── Dockerfile
│   ├── __init__.py
│   ├── requirements.txt
│   └── src
│       ├── config.py
│       ├── __init__.py
│       ├── main.py
│       ├── signals.py
│       └── trading_monitor.py
├── README.md
├── requirements.txt
├── sentiment_service
    ├── Dockerfile
    ├── __init__.py
    ├── requirements.txt
    └── src
        ├── config.py
        ├── __init__.py
        ├── main.py
        ├── news_scrapper.py
        ├── sentiment_analysis_test.py
        └── text_normalizer.py


16 directories


```


## Technical aspects

To develop this solution you will need to have a proper working environment setup in your machine consisting of:
- Docker
- docker-compose
- VS Code or any other IDE of your preference
- Optional: Linux subsystem for Windows (WSL2)

Please make sure to carefully read the `README.md` file which contains detailed instructions about the code you have to complete to make the project run correctly.

The technologies involved are:
- Python is the main programming language
- FastAPI framework for the API
- OpenAI for NLP tasks
- bs4 for scrapping of news
- yfinance for historical data
- Tradingview for live data
- MongoDB as database


## Example for getting data

### Getting latest data.
```python
from pymongo import MongoClient

DB_URI = 'mongodb://user:password@ip:27017'
client = MongoClient(DB_URI)

# Default
DB_URI = 'mongodb://localhost:27017'
client = MongoClient(DB_URI)

with client.start_session(causal_consistency=True) as session:
    collection = db["tick_data"]
    
    # A secondary read waits for replication of the write.
    cursor = collection.find({"metadata.stock_id": "EURUSD=X"}, 
                             {"timestamp": -1, "value": 1, "_id" : 0}, session=session)
    docs = list(cursor)
    df = pd.DataFrame(docs)

print(df)
```

if any results found it will be shown.

### Turning data into tick data

```py
df['close'] = df['value'].astype(float)
df['volume'] = df['volume'].astype(float)
df['open'] = df['close']
df['high'] = df['close']
df['low'] = df['close']
df.drop(columns = ["value", "_id"], inplace = True)

# Resampliing the candles

candles = df.resample("30min",
            on = "timestamp",
            closed='left',
            axis=0,
            kind="timestamp").agg({"open": "first", 
                                            "high": "max", 
                                            "low": "min",
                                            "close": "last", 
                                            "volume": "sum"})
# Ploting the candles

import plotly.graph_objects as go


fig = go.Figure()

fig.add_trace(go.Candlestick(x=candles.index,
                open=candles['open'],
                high=candles['high'],
                low=candles['low'],
                close=candles['close']))
```


## Code Style

Following a style guide keeps the code's aesthetics clean and improves readability, making contributions and code reviews easier. Automated Python code formatters make sure your codebase stays in a consistent style without any manual work on your end. If adhering to a specific style of coding is important to you, employing an automated to do that job is the obvious thing to do. This avoids bike-shedding on nitpicks during code reviews, saving you an enormous amount of time overall.

We use [Black](https://black.readthedocs.io/) and [isort](https://pycqa.github.io/isort/) for automated code formatting in this project, you can run it with:

```console
$ isort --profile=black . && black --line-length 88 .
```

