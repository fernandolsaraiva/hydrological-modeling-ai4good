import os

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from PIL import Image

from util import get_station_data_plu, get_station_names_plu

if __name__ == "__main__":
    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=200)
    logo = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo, width=150)
    st.title('Rain Monitoring')

    station_names = get_station_names_plu()
    default_station = 'Rio Tamanduateí - Mercado Municipal'
    if default_station in station_names:
        station_name = st.selectbox('Select the station', station_names, index=station_names.index(default_station))
    else:
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
        data = get_station_data_plu(station_name, start_date, end_date, aggregation)
        fig = px.line(data, x='timestamp', y='value', title=f'River Level - {station_name}')
        st.plotly_chart(fig)