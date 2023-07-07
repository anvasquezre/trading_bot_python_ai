ALTER SYSTEM SET max_connections = 2000;

CREATE TABLE IF NOT EXISTS stock (
    stock_id TEXT NOT NULL UNIQUE PRIMARY KEY, 
    name TEXT NOT NULL,
    exchange TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tick_data_vals
(
  bucket TIMESTAMP WITH TIME ZONE NOT NULL,
  stock_id TEXT NOT NULL,
  interval TEXT NOT NULL,
  ema_10 NUMERIC ,
  ema_20 NUMERIC ,
  ema_30 NUMERIC ,
  ema_50 NUMERIC ,
  ema_100 NUMERIC ,
  ema_200 NUMERIC ,
  sma_10 NUMERIC ,
  sma_20 NUMERIC ,
  sma_30 NUMERIC ,
  sma_50 NUMERIC ,
  sma_100 NUMERIC ,
  sma_200 NUMERIC ,
  tenkan_sen NUMERIC ,
  kijun_sen NUMERIC ,
  senkou_span_a NUMERIC ,
  senkou_span_b NUMERIC ,
  chikou_span NUMERIC ,
  vwap NUMERIC ,
  hull NUMERIC ,
  rsi NUMERIC ,
  stoch_k NUMERIC ,
  stoch_d NUMERIC ,
  cci NUMERIC ,
  adx NUMERIC ,
  adx_plus_di NUMERIC ,
  adx_minus_di NUMERIC ,
  aws_os NUMERIC ,
  roc NUMERIC ,
  macd NUMERIC ,
  macd_signal NUMERIC ,
  sto_fast NUMERIC ,
  sto_signal NUMERIC ,
  williams_r NUMERIC ,
  ultimate_os NUMERIC ,
  FOREIGN KEY(stock_id) REFERENCES stock(stock_id),
  UNIQUE (bucket, stock_id)
);

SELECT create_hypertable('tick_data_vals','bucket');

CREATE TABLE IF NOT EXISTS tick_data_signals 
(
  bucket TIMESTAMP WITH TIME ZONE NOT NULL,
  stock_id TEXT NOT NULL,
  interval TEXT NOT NULL,
  ema_10 TEXT ,
  ema_20 TEXT ,
  ema_30 TEXT ,
  ema_50 TEXT ,
  ema_100 TEXT ,
  ema_200 TEXT ,
  sma_10 TEXT ,
  sma_20 TEXT ,
  sma_30 TEXT ,
  sma_50 TEXT ,
  sma_100 TEXT ,
  sma_200 TEXT ,
  ichimoku TEXT ,
  vwap TEXT ,
  hull TEXT ,
  rsi TEXT ,
  stoch_k TEXT ,
  cci TEXT ,
  adx TEXT ,
  aws_os TEXT ,
  roc TEXT ,
  macd TEXT ,
  sto_fast TEXT ,
  williams_r TEXT ,
  ultimate_os TEXT ,
  FOREIGN KEY(stock_id) REFERENCES stock(stock_id),
  UNIQUE (bucket, stock_id)
);

SELECT create_hypertable('tick_data_signals','bucket');

CREATE TABLE IF NOT EXISTS signal_scores
(
  bucket TIMESTAMP WITH TIME ZONE NOT NULL,
  stock_id TEXT NOT NULL,
  interval TEXT NOT NULL,
  os_sell NUMERIC NOT NULL,
  os_buy NUMERIC NOT NULL,
  os_hold NUMERIC NOT NULL,
  os_score NUMERIC NOT NULL,
  os_recommendation TEXT NOT NULL,
  ma_sell NUMERIC NOT NULL,
  ma_buy NUMERIC NOT NULL,
  ma_hold NUMERIC NOT NULL,
  ma_score NUMERIC NOT NULL,
  ma_recommendation TEXT NOT NULL,
  total_sell NUMERIC NOT NULL,
  total_buy NUMERIC NOT NULL,
  total_hold NUMERIC NOT NULL,
  total_score NUMERIC NOT NULL,
  total_recommendation TEXT NOT NULL,
  FOREIGN KEY(stock_id) REFERENCES stock(stock_id),
  UNIQUE (bucket, stock_id)
);


SELECT create_hypertable('signal_scores','bucket');

CREATE TABLE IF NOT EXISTS transaction_types 
(
  transaction_type_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL
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

CREATE TABLE IF NOT EXISTS stocks_real_time (
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
(first(volume,dt)-last(volume, dt)) as volume
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
(first(volume,dt)-last(volume, dt)) as volume
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
(first(volume,dt)-last(volume, dt)) as volume
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
(first(volume,dt)-last(volume, dt)) as volume
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
(first(volume,dt)-last(volume, dt)) as volume
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
(first(volume,dt)-last(volume, dt)) as volume
FROM stocks_real_time
GROUP BY bucket, stock_id
WITH NO DATA;


INSERT INTO transaction_types (name, description) VALUES 
('BUY', 'BUY'),
('SELL', 'SELL'),
('NEUTRAL', 'HOLD');
