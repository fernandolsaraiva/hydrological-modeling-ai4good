import os

import pandas as pd
import psycopg2
import streamlit as st


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

    #for station_name in station_names:
    for station_name in df['name'].unique():
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
    
    # Verificar se há nomes de estações faltando
    for station_name in station_names:
        station_code = station_codes[station_name]
        column_name = f'plu_{station_code}'
        if column_name not in merged_df.columns:
            merged_df[column_name] = 0

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

def get_station_names_and_critical_levels():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    query = "SELECT name, critical_levels FROM station.station_flu"
    df = pd.read_sql(query, conn)
    conn.close()
    station_names = df['name'].tolist()
    critical_levels = df['critical_levels'].tolist()
    return station_names, critical_levels

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

def load_model_from_db(horizon):
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Query to get the model for the given horizon
    cursor.execute("SELECT model_data FROM prediction_model WHERE horizon = %s", (horizon,))
    model_data = cursor.fetchone()
    
    # Close the connection
    conn.close()
    
    if model_data is None:
        raise ValueError(f"No model found for horizon {horizon}")
    
    # Load the model from binary data
    model = pickle.loads(model_data[0])
    
    return model

def email_exists(email):
    """
    Checks whether the provided email is already registered in the users.info table. 

    Args:
        email (str): The email address to check.

    Returns:
        bool: True if the email exists, False otherwise.
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    query = 'SELECT COUNT(*) FROM users.info WHERE email = %s'
    cur.execute(query, (email,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] > 0

def insert_user_info(name, number, email, station):
    """
    Inserts a new user's information into the users.info table.
    It assumes that the email has not been registered yet.

    Args:
        name (str): The user's name.
        number (str): The user's phone number (will be converted to a numeric type).
        email (str): The user's email address.
        station (str): The selected station.

    Returns:
        tuple: A tuple (success, message) where success is a boolean indicating if the insertion was successful,
               and message is a string describing the result.
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Convert the phone number to numeric type.
    try:
        numeric_number = float(number)
    except ValueError:
        return False, "The phone number must be numeric."
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    query = 'INSERT INTO users.info (name, number, email, station) VALUES (%s, %s, %s, %s)'
    try:
        cur.execute(query, (name, numeric_number, email, station))
        conn.commit()
        success = True
        message = "Registration successful!"
    except Exception as e:
        success = False
        message = f"An error occurred: {e}"
    finally:
        cur.close()
        conn.close()
    
    return success, message