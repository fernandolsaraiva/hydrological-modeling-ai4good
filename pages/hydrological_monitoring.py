import os

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st


# Função para conectar ao banco de dados e buscar os nomes das estações
def get_station_names():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    query = "SELECT * FROM station.station_flu"
    df = pd.read_sql(query, conn)
    conn.close()
    return df['name'].tolist()

# Função para buscar os dados da estação selecionada
def get_station_data(station_name, start_date, end_date, aggregation):
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

    df = df[['timestamp', 'value']]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    if aggregation == '10-minute':
        df = df.resample('10T').mean().reset_index()
    elif aggregation == 'Hourly':
        df = df.resample('H').mean().reset_index()
    elif aggregation == 'Daily':
        df = df.resample('D').mean().reset_index()
    return df

if __name__ == "__main__":
    st.title('Hydrological Monitoring')

    station_names = get_station_names()
    station_name = st.selectbox('Select the station', station_names)        

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('Start Date')
    with col2:
        end_date = st.date_input('End Date')

    # Aggregation selector
    aggregation = st.selectbox('Select Aggregation', ['10-minute','Hourly' ,'Daily'])

    # Button to plot the data
    if st.button('Plot'):
        data = get_station_data(station_name, start_date, end_date, aggregation)
        fig = px.line(data, x='timestamp', y='value', title=f'River Level - {station_name}')
        st.plotly_chart(fig)