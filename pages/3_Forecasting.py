import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import pytz
import streamlit as st
from PIL import Image

from util import (get_last_available_date, get_station_code,
                  get_station_data_flu, get_station_names)

# Configuração da página
st.set_page_config(page_title="Flood Alert System", layout="wide")


if __name__ == "__main__":
    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=200)
    logo = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo, width=150)
    st.title('Forecasting')

    station_names = get_station_names()
    default_station = 'Rio Tamanduateí - Mercado Municipal'
    if default_station in station_names:
        station_name = st.selectbox('Select the station', station_names, index=station_names.index(default_station))
    else:
        station_name = st.selectbox('Select the station', station_names)
        

    station_code = get_station_code(station_name)
    
    last_available_date = get_last_available_date(station_code)

    end_time = last_available_date
    # write start_time as end_time minus 2 days
    start_time = end_time - pd.Timedelta(2, 'D')

    # Button to plot the data
    if st.button('Plot'):
        data = get_station_data_flu(station_name, start_time, end_time, aggregation='10-minute')
        data['timestamp'] = data['timestamp'].dt.tz_convert('America/Sao_Paulo')
        fig = px.line(data, x='timestamp', y='value', title=f'River Level - {station_name}')
        current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
        fig.add_vline(x=current_time, line_width=3, line_dash="dash", line_color="red")
        fig.add_annotation(x=current_time, y=max(data['value']), text="Current Time", showarrow=True, arrowhead=1)
        st.plotly_chart(fig)