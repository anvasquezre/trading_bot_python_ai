ALTER SYSTEM SET max_connections = 2000;

CREATE TABLE IF NOT EXISTS stock (
    stock_id TEXT NOT NULL UNIQUE PRIMARY KEY, 
    name TEXT NOT NULL,
    exchange TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ohlc_data 
(
  id SERIAL PRIMARY KEY,
  dt TIMESTAMP WITH TIME ZONE NOT NULL,
  stock_id TEXT NOT NULL,
  open NUMERIC NOT NULL,
  high NUMERIC NOT NULL,
  low NUMERIC NOT NULL,
  close NUMERIC NOT NULL,
  volume NUMERIC NOT NULL,
  FOREIGN KEY(stock_id) REFERENCES stock(stock_id),
  UNIQUE (dt, stock_id)
);

CREATE TABLE IF NOT EXISTS tick_data  
(
  id SERIAL PRIMARY KEY,
  dt TIMESTAMP WITH TIME ZONE NOT NULL,
  stock_id TEXT NOT NULL,
  bid NUMERIC NOT NULL,
  ask NUMERIC NOT NULL,
  bid_vol NUMERIC,
  ask_vol NUMERIC,
  FOREIGN KEY(stock_id) REFERENCES stock(stock_id)
);

CREATE TABLE IF NOT EXISTS transaction_types 
(
  transaction_type_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signal_data 
(
  id SERIAL PRIMARY KEY,
  dt TIMESTAMP WITH TIME ZONE NOT NULL,
  stock_id TEXT NOT NULL,
  transaction_type_id INTEGER NOT NULL,
  FOREIGN KEY(stock_id) REFERENCES stock(stock_id),
  FOREIGN KEY(transaction_type_id) REFERENCES transaction_types(transaction_type_id)
);

CREATE TABLE IF NOT EXISTS news_data 
(
  dt TIMESTAMP WITH TIME ZONE NOT NULL,
  news_url TEXT NOT NULL,
  stock_id TEXT NOT NULL,
  sentiment_score NUMERIC NOT NULL,
  FOREIGN KEY(stock_id) REFERENCES stock(stock_id),
  UNIQUE (dt, news_url, stock_id)
);

CREATE TABLE IF NOT EXISTS stocks_real_time
(
  dt TIMESTAMP WITH TIME ZONE NOT NULL,
  stock_id TEXT NOT NULL,
  value NUMERIC NOT NULL,
  volume NUMERIC NOT NULL,
  FOREIGN KEY(stock_id) REFERENCES stock(stock_id),
  UNIQUE (dt, stock_id)
);

SELECT create_hypertable('stocks_real_time','dt');
CREATE INDEX ix_stock_id_time ON stocks_real_time (stock_id, dt DESC);

CREATE MATERIALIZED VIEW quotes_1h WITH
(timescaledb.continuous)
AS
SELECT stock_id, time_bucket('1h', dt) as bucket,
min(value) as low,
max(value) as high,
first(value, dt) as open,
last(value, dt) as close,
last(volume, dt) as volume
FROM stocks_real_time
GROUP BY bucket, stock_id
WITH NO DATA;

CREATE MATERIALIZED VIEW quotes_1m WITH
(timescaledb.continuous)
AS
SELECT stock_id, time_bucket('1m', dt) as bucket,
min(value) as low,
max(value) as high,
first(value, dt) as open,
last(value, dt) as close,
last(volume, dt) as volume
FROM stocks_real_time
GROUP BY bucket, stock_id
WITH NO DATA;

CREATE MATERIALIZED VIEW quotes_1d WITH
(timescaledb.continuous)
AS
SELECT stock_id, time_bucket('1d', dt) as bucket,
min(value) as low,
max(value) as high,
first(value, dt) as open,
last(value, dt) as close,
last(volume, dt) as volume
FROM stocks_real_time
GROUP BY bucket, stock_id
WITH NO DATA;

CREATE MATERIALIZED VIEW quotes_1w WITH
(timescaledb.continuous)
AS
SELECT stock_id, time_bucket('1w', dt) as bucket,
min(value) as low,
max(value) as high,
first(value, dt) as open,
last(value, dt) as close,
last(volume, dt) as volume
FROM stocks_real_time
GROUP BY bucket, stock_id
WITH NO DATA;

CREATE MATERIALIZED VIEW quotes_1mo WITH
(timescaledb.continuous)
AS
SELECT stock_id, time_bucket('1 month', dt) as bucket,
min(value) as low,
max(value) as high,
first(value, dt) as open,
last(value, dt) as close,
last(volume, dt) as volume
FROM stocks_real_time
GROUP BY bucket, stock_id
WITH NO DATA;

CREATE MATERIALIZED VIEW quotes_1y WITH
(timescaledb.continuous)
AS
SELECT stock_id, time_bucket('1y', dt) as bucket,
min(value) as low,
max(value) as high,
first(value, dt) as open,
last(value, dt) as close,
last(volume, dt) as volume
FROM stocks_real_time
GROUP BY bucket, stock_id
WITH NO DATA;


INSERT INTO transaction_types (name, description) VALUES 
('BUY', 'Buy'),
('SELL', 'Sell');
