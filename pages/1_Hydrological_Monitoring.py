import os

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from util import get_station_data_flu


# Função para conectar ao banco de dados e buscar os nomes das estações
def get_station_names():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    query = "SELECT * FROM station.station_flu"
    df = pd.read_sql(query, conn)
    conn.close()
    return df['name'].tolist()

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
        data = get_station_data_flu(station_name, start_date, end_date, aggregation)
        fig = px.line(data, x='timestamp', y='value', title=f'River Level - {station_name}')
        st.plotly_chart(fig)