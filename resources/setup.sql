CREATE CATALOG IF NOT EXISTS mnb_catalog;
USE CATALOG mnb_catalog;

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Opcionálisan a táblák előre definiálása (ha nem a Spark hozza létre őket)
CREATE TABLE IF NOT EXISTS silver.exchange_rates_cleaned (
  date DATE,
  currency STRING,
  unit INT,
  exchange_rate DOUBLE,
  processing_timestamp TIMESTAMP
) USING DELTA;