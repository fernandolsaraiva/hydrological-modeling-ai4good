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
    station_code = get_station_code_flu(station_name)
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
    station_code = get_station_code_plu(station_name)
    df = df.drop(columns=['station'])
    if aggregation == '10-minute':
        df = df.resample('10min').mean().reset_index()
    elif aggregation == 'Hourly':
        df = df.resample('H').mean().reset_index()
    elif aggregation == 'Daily':
        df = df.resample('D').mean().reset_index()
    df['station'] = station_code
    return df

def get_multiple_station_data_plu(station_names, start_date, end_date, aggregation='10-minute'):
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    
    # Construir a consulta SQL para buscar dados de todas as estações
    station_names_str = "', '".join(station_names)
    query = f"""
    SELECT ts.*, st.name
    FROM timeseries.data_station_plu ts
    JOIN station.station_plu st ON ts.station = st.original_id
    WHERE st.name IN ('{station_names_str}')
    AND ts.timestamp >= '{start_date}'
    AND ts.timestamp <= '{end_date}'
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Processar os dados
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    
    # Criar um DataFrame vazio para armazenar os dados mesclados
    merged_df = pd.DataFrame()
    
    station_codes = get_station_codes_plu(station_names)

    for station_name in station_names:
        print(f"Processando estação: {station_name}")
        station_code = station_codes[station_name]
        print(f"Código da estação: {station_code}")
        station_data = df[df['name'] == station_name][['value']].rename(columns={'value': f'plu_{station_code}'})
        
        if aggregation == '10-minute':
            station_data = station_data.resample('10min').mean()
        elif aggregation == 'Hourly':
            station_data = station_data.resample('H').mean()
        elif aggregation == 'Daily':
            station_data = station_data.resample('D').mean()
        
        if merged_df.empty:
            merged_df = station_data
        else:
            merged_df = pd.merge(merged_df, station_data, left_index=True, right_index=True, how='outer')
    
    merged_df = merged_df.reset_index()
    return merged_df

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

def get_station_code_flu(station_name):
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
    
def get_station_code_plu(station_name):
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    query = f"""
    SELECT st.original_id
    FROM station.station_plu st
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
    
def get_station_codes_plu(station_names):
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    station_names_str = "', '".join(station_names)
    query = f"""
    SELECT st.name, st.original_id
    FROM station.station_plu st
    WHERE st.name IN ('{station_names_str}')
    """
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    station_codes = {name: code for name, code in results}
    
    for station_name in station_names:
        if station_name not in station_codes:
            station_codes[station_name] = f"unknown_{station_name.replace(' ', '_')}"
    
    return station_codes

def get_last_available_date(station_code):
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT MAX(timestamp) FROM timeseries.data_station_flu where station = '{station_code}'""")
        last_data_date = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return last_data_date