import os

import pandas as pd
import psycopg2


# Função para buscar os dados da estação selecionada
def get_station_data_flu(station_name, start_date, end_date, aggregation):
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    query = f"""
    SELECT ts.*
    FROM timeseries.data_station_flu ts
    JOIN station.station_flu st ON ts.station = st.original_id
    WHERE st.name = '{station_name}'
    AND ts.timestamp >= '{start_date}'
    AND ts.timestamp <= '{end_date}'
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df = df[['timestamp', 'value','station']]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    station_code = get_station_code(station_name)
    df = df.drop(columns=['station'])
    if aggregation == '10-minute':
        df = df.resample('10T').mean().reset_index()
    elif aggregation == 'Hourly':
        df = df.resample('H').mean().reset_index()
    elif aggregation == 'Daily':
        df = df.resample('D').mean().reset_index()
    df['station'] = station_code
    return df

# Função para buscar os dados da estação selecionada
def get_station_data_plu(station_name, start_date, end_date, aggregation = '10-minute'):
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    query = f"""
    SELECT ts.*
    FROM timeseries.data_station_plu ts
    JOIN station.station_plu st ON ts.station = st.original_id
    WHERE st.name = '{station_name}'
    AND ts.timestamp >= '{start_date}'
    AND ts.timestamp <= '{end_date}'
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df = df[['timestamp', 'value','station']]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    station_code = get_station_code(station_name)
    df = df.drop(columns=['station'])
    if aggregation == '10-minute':
        df = df.resample('10min').mean().reset_index()
    elif aggregation == 'Hourly':
        df = df.resample('H').mean().reset_index()
    elif aggregation == 'Daily':
        df = df.resample('D').mean().reset_index()
    df['station'] = station_code
    return df

# Função para buscar os nomes de todas as estações na tabela station.stations_plu e retornar uma lista
def get_station_names_plu():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    query = "SELECT * FROM station.station_plu"
    df = pd.read_sql(query, conn)
    conn.close()
    return df['name'].tolist()

# Função para conectar ao banco de dados e buscar os nomes das estações
def get_station_names():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    query = "SELECT * FROM station.station_flu"
    df = pd.read_sql(query, conn)
    conn.close()
    return df['name'].tolist()

def get_station_code(station_name):
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    query = f"""
    SELECT st.original_id
    FROM station.station_flu st
    WHERE st.name = '{station_name}'
    """
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return None

def get_last_available_date(station_code):
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT MAX(timestamp) FROM timeseries.data_station_flu where station = '{station_code}'""")
        last_data_date = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return last_data_date