import io
import json
import os
import time
from datetime import datetime, timedelta
from io import StringIO

import numpy as np
import pandas as pd
import psycopg2
import pytz
import requests


def getJson(url):
    s = requests.Session()
    s.get(url)
    json_value = s.get(url).content.decode("utf-8")
    return json_value


def getDate():
    date = datetime.utcnow()  # current date and time
    return date

def getDataStation(date, station=33767, interval=1):
    date_start = date-timedelta(days=interval-1)
    year_start = date_start.strftime("%Y")
    month_start = date_start.strftime("%m")
    day_start = date_start.strftime("%d")
    date_end = date + timedelta(days=1)
    year_end = date_end.strftime("%Y")
    month_end = date_end.strftime("%m")
    day_end = date_end.strftime("%d")
    url_newest = f"https://cth.daee.sp.gov.br/sibh/api/v1/measurements/grouped?format=csv&start_date={year_start}-{month_start}-{day_start}%2003%3A00&end_date={year_end}-{month_end}-{day_end}%2002%3A59&group_type=none&transmission_type_ids%5B%5D=1&transmission_type_ids%5B%5D=2&transmission_type_ids%5B%5D=3&transmission_type_ids%5B%5D=4&transmission_type_ids%5B%5D=5&transmission_type_ids%5B%5D=6&station_prefix_ids%5B%5D={station}"
    json_value = getJson(url_newest)
    json_value_transformed = StringIO(json_value)
    df = pd.read_csv(json_value_transformed, delimiter=";")
    df.to_csv("teste.csv", index=False)
    return df


def upsertData(df, table="timeseries.data_station_flu"):
    column_mapping = {"prefix": "station", "date": "timestamp", "value": "value"}
    db_columns = [column_mapping[col] for col in df.columns if col in column_mapping]
    data_tuples = [
        tuple(row[col] for col in column_mapping.keys() if col in df.columns)
        for _, row in df.iterrows()
    ]
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    upsert_query = f"""
        INSERT INTO {table} ({', '.join(db_columns)}, created_at, updated_at) 
        VALUES ({', '.join(['%s'] * len(db_columns))}, NOW(), NOW())
        ON CONFLICT (station, timestamp)
        DO UPDATE SET 
            value = EXCLUDED.value,
            updated_at = NOW();
        """
    cursor.executemany(upsert_query, data_tuples)
    conn.commit()
    cursor.close()
    conn.close()

def downloadDataAndUpsertMultipleStations(stations_flu, stations_plu):
    # Get the date of the last data in the database
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(timestamp) FROM timeseries.data_station_flu")
    last_data_date = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    if last_data_date is None:
        last_data_date = datetime(2024, 11, 9, tzinfo=pytz.UTC)
        print('entrou aqui')
        print(last_data_date)

    last_data_date = last_data_date.astimezone(pytz.timezone('America/Sao_Paulo'))
    print('depois da mudança de timezone',last_data_date)
    today = datetime.now(pytz.timezone('America/Sao_Paulo'))
    
    print('last_data_date',last_data_date)
    print('today',today)
    
    while last_data_date.date() < today.date():
        for station in stations_flu:
            df = getDataStation(last_data_date, station=station)
            upsertData(df,table="timeseries.data_station_flu")
            print(
                f"Dados da estação {station} inseridos/atualizados com sucesso na tabela timeseries.data_station_flu para o dia {last_data_date}"
            )
        for station in stations_plu:
            df = getDataStation(last_data_date, station=station)
            upsertData(df,table="timeseries.data_station_plu")
            print(
                f"Dados da estação {station} inseridos/atualizados com sucesso na tabela timeseries.data_station_plu para o dia {last_data_date}"
            )
        last_data_date = last_data_date + timedelta(days=1)

    if last_data_date.date() == today.date():
        while True:
            for station in stations_flu:
                df = getDataStation(last_data_date, station=station, interval=2) # interval=2 para pegar os dados do dia anterior e evitar perda de dado em alguma estação por atraso na atualização
                upsertData(df, table="timeseries.data_station_flu")
                print(
                    f"Dados da estação {station} inseridos/atualizados com sucesso na tabela timeseries.data_station_flu para o dia {last_data_date}"
                )
            for station in stations_plu:
                df = getDataStation(last_data_date, station=station, interval=2)
                upsertData(df,table="timeseries.data_station_plu")
                print(
                    f"Dados da estação {station} inseridos/atualizados com sucesso na tabela timeseries.data_station_plu para o dia {last_data_date}"
                )
            print('Waiting 10 seconds...')
            time.sleep(10)
            last_data_date = datetime.utcnow()
            last_data_date = last_data_date.astimezone(pytz.timezone('America/Sao_Paulo'))

if __name__ == "__main__":
    stations_flu = [33737,33751,33752,33755,33767,33846,33850,33678,33681,33682,33711,33684,33690,796,33715,33182,33183,33181,33185,33705,797,33736]

    stations_plu = [33738,33750,33753,33754,33768,33848,33847,33851,33184,33709,33710,33683,33712,33685,33691,33692,33694,33716,33223,33703,33706,33725,33734]
    
    while True:
        downloadDataAndUpsertMultipleStations(stations_flu, stations_plu) 
