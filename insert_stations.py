import os

import pandas as pd
import psycopg2


def insert_stations_flu():
    stations_flu = pd.read_csv('stations_flu.csv')    
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    for index, row in stations_flu.iterrows():
        cursor.execute(
            f"""
            INSERT INTO station.station_flu (original_id, long, lat, name, minDate, api_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """,
            (row['posto'], row['lon'], row['lat'], row['nome'], row['minDate'], row['Código API - FLU'])
        )
    conn.commit()
    cursor.close()
    conn.close()

# faça uma função semelhante a de cima mas para inserir os dados do arquivo stations_plu.csv na tabela station.station_plu:)
def insert_stations_plu():
    stations_plu = pd.read_csv('stations_plu.csv')    
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    for index, row in stations_plu.iterrows():
        cursor.execute(
            f"""
            INSERT INTO station.station_plu (original_id, long, lat, name, minDate, api_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """,
            (row['posto'], row['lon'], row['lat'], row['nome'], row['minDate'], row['Código API - PLU'])
        )
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    insert_stations_flu()
    insert_stations_plu()
    print('Stations inserted successfully')