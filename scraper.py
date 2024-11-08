import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import os
import psycopg2
from io import StringIO


def getJson(url):
    s = requests.Session()
    s.get(url)
    json_value = s.get(url).content.decode("utf-8")
    return json_value

def getDate():
    date = datetime.utcnow() # current date and time
    return date

def getNivel(date):
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    date_yesterday = date-timedelta(days=1)
    year_yesterday = date_yesterday.strftime("%Y")
    month_yesterday = date_yesterday.strftime("%m")
    day_yesterday = date_yesterday.strftime("%d")
    station=33767
    url_new = f"https://cth.daee.sp.gov.br/sibh/api/v1/measurements/grouped?format=csv&start_date={year_yesterday}-{month_yesterday}-{day_yesterday}%2003%3A00&end_date={year}-{month}-{day}%2002%3A59&group_type=none&transmission_type_ids%5B%5D=1&transmission_type_ids%5B%5D=2&transmission_type_ids%5B%5D=3&transmission_type_ids%5B%5D=4&transmission_type_ids%5B%5D=5&transmission_type_ids%5B%5D=6&station_prefix_ids%5B%5D={station}"
    json_value = getJson(url_new)
    print(json_value)
    json_value_transformed = StringIO(json_value)
    df = pd.read_csv(json_value_transformed, delimiter=";")
    df.to_csv('teste.csv', index=False)
    return df

def upsertData(df):
    column_mapping = {
    'prefix': 'station',
    'date': 'timestamp',
    'value': 'value'
    }
    db_columns = [column_mapping[col] for col in df.columns if col in column_mapping]
    data_tuples = [tuple(row[col] for col in column_mapping.keys() if col in df.columns) for _, row in df.iterrows()]
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    upsert_query = f"""
        INSERT INTO timeseries.data_station ({', '.join(db_columns)}, created_at, updated_at) 
        VALUES ({', '.join(['%s'] * len(db_columns))}, NOW(), NOW())
        ON CONFLICT (station, timestamp)
        DO UPDATE SET 
            value = EXCLUDED.value,
            updated_at = NOW();
        """
    cursor.executemany(upsert_query, data_tuples)
    conn.commit()
    print("Dados inseridos/atualizados com sucesso na tabela timeseries.data_station!")
    cursor.close()
    conn.close()



if __name__ == '__main__':
    date = getDate()    
    df = getNivel(date)
    print(df)
    upsertData(df)
    print('Concluído')