import os
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import psycopg2
import pytz


def get_historical_data(station, lookback_hours=24):
    """
    Obtém dados históricos do banco para uma estação específica
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    
    query = """
        SELECT timestamp, value 
        FROM timeseries.data_station_flu
        WHERE station = %s
        AND timestamp >= NOW() - INTERVAL '%s hours'
        ORDER BY timestamp DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(station, lookback_hours))
    conn.close()
    
    return df

def make_prediction(historical_data, lead_time):
    """
    Função placeholder para fazer a predição
    Aqui você deve implementar seu modelo de predição real
    """
    # Exemplo simples usando média móvel
    if len(historical_data) == 0:
        return None
        
    return historical_data['value'].mean()

def upsert_predictions(predictions_data, table="prediction.timeseries"):
    """
    Insere ou atualiza predições no banco de dados
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    upsert_query = """
        INSERT INTO prediction.timeseries 
        (timestamp, station, lead_time, value, created_at, updated_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (timestamp, station, lead_time)
        DO UPDATE SET 
            value = EXCLUDED.value,
            updated_at = NOW();
    """
    
    cursor.executemany(upsert_query, predictions_data)
    conn.commit()
    cursor.close()
    conn.close()

def generate_and_save_predictions(stations, lead_times):
    """
    Gera e salva predições para todas as estações e horizontes de tempo
    """
    predictions_data = []
    current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
    
    for station in stations:
        # Obtém dados históricos
        historical_data = get_historical_data(station)
        
        # Gera predições para cada lead time
        for lead_time in lead_times:
            prediction_timestamp = current_time + timedelta(hours=lead_time)
            predicted_value = make_prediction(historical_data, lead_time)
            
            if predicted_value is not None:
                predictions_data.append((
                    prediction_timestamp,
                    station,
                    lead_time,
                    predicted_value
                ))
    
    if predictions_data:
        upsert_predictions(predictions_data)
        print(f"Predições geradas e salvas com sucesso em {current_time}")

def run_continuous_predictions(stations, lead_times):
    """
    Executa o processo de predição continuamente
    """
    while True:
        try:
            generate_and_save_predictions(stations, lead_times)
            print('Aguardando 10 segundos...')
            time.sleep(10)
        except Exception as e:
            print(f"Erro durante a execução: {str(e)}")
            time.sleep(10)  # Aguarda mesmo em caso de erro


if __name__ == "__main__":
    # Lista de estações (mesmas do scraper.py)
    stations_flu = [33737,33751,33752,33755,33767,33846,33850,33678,33681,33682,
                   33711,33684,33690,796,33715,33182,33183,33181,33185,33705,797,33736]
    
    # Define os horizontes de predição (em horas)
    lead_times = [1, 3, 6, 12, 24]  # exemplo: predições para 1h, 3h, 6h, 12h e 24h à frente
    
    # Executa as predições continuamente
    run_continuous_predictions(stations_flu, lead_times) 