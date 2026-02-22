import requests
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, regexp_replace, to_date
from delta.tables import DeltaTable

# IMPORTÁLÁS: Itt hívjuk be a különválasztott logikát
from transformations import get_inner_xml, parse_mnb_rows

spark = SparkSession.builder.getOrCreate()

catalog = dbutils.widgets.get("p_catalog")
schema = dbutils.widgets.get("p_schema")
spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA {schema}")


def fetch_mnb_xml(start_date, end_date):
    """SOAP hívás dinamikus dátumokkal."""
    url = "http://www.mnb.hu/arfolyamok.asmx"
    payload = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetExchangeRates xmlns="http://www.mnb.hu/arfolyamok.asmx">
          <startDate>{start_date}</startDate>
          <endDate>{end_date}</endDate>
          <currencyNames></currencyNames>
        </GetExchangeRates>
      </soap:Body>
    </soap:Envelope>"""
    
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    resp = requests.post(url, data=payload, headers=headers)
    resp.raise_for_status()
    return resp.text

def get_start_date(table_name):
    """Meghatározza a kezdődátumot az utolsó sikeres betöltés alapján."""
    full_table_path = f"{catalog}.{schema}.{table_name}"
    try:
        if spark.catalog.tableExists(full_table_path):
            last_date = spark.table(full_table_path).select(spark_max("date")).collect()[0][0]
            if last_date:
                # A rögzített utolsó nap utáni nappal kezdünk
                return (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Info: Tábla olvasási hiba vagy üres tábla ({e}). Alapértelmezett dátum használata.")
    
    return "2024-01-01" # Alapértelmezett kezdődátum az első futáshoz

def run_etl():
    start_dt = get_start_date("exchange_rates_silver")
    end_dt = datetime.now().strftime("%Y-%m-%d")
    
    if start_dt > end_dt:
        dbutils.notebook.exit(f"Adatok már naprakészek: {end_dt}")

    print(f"Lekérdezési időszak: {start_dt} -> {end_dt}")

    # 2. BRONZE: Csak az új XML mentése
    soap_xml = fetch_mnb_xml(start_dt, end_dt)

    inner_xml = get_inner_xml(soap_xml)
    parsed_rows = parse_mnb_rows(inner_xml)

    if not parsed_rows:
        return "No new data"

    # 3. SPARK MŰVELETEK
    df = spark.createDataFrame(parsed_rows) \
        .withColumn("date", to_date(col("date"))) \
        .withColumn("exchange_rate", regexp_replace(col("rate_str"), ",", ".").cast("double")) \
        .withColumn("processing_timestamp", current_timestamp())

    # 4. MERGE (Inkrementális mentés)
    if spark.catalog.tableExists("exchange_rates_silver"):
        target = DeltaTable.forName(spark, "exchange_rates_silver")
        target.alias("t").merge(
            df.alias("s"), "t.date = s.date AND t.currency = s.currency"
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
    else:
        df.write.format("delta").saveAsTable("exchange_rates_silver")

if __name__ == "__main__":
    run_etl()