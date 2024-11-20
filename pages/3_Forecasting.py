import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import pytz
import streamlit as st
from PIL import Image

from scr.scripts.utils import load_data
from util import (get_last_available_date, get_station_code,
                  get_station_data_flu, get_station_names)


def plot_river_level(data, station_name):
    data['value'] = data['value'] / 100
    fig = px.line(data, x='timestamp', y='value', title=f'River Level - {station_name}')
    fig.add_scatter(x=data['timestamp'], y=data['value'], mode='markers', marker=dict(color='blue', size=5))
    fig.update_layout(title={'text': f'River Level - {station_name}', 'x': 0.5, 'xanchor': 'center'})
    current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
    fig.add_vline(x=current_time, line_width=3, line_dash="dash", line_color="red")
    fig.add_annotation(x=current_time, y=max(data['value']), text="Current Time", showarrow=True, arrowhead=1)
    fig.update_yaxes(title_text='River Level (m)')
    st.plotly_chart(fig)

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
    # the start time is the end time minus 1 hour
    start_time = end_time - pd.Timedelta(1, 'h')
    start_time_visualization = end_time - pd.Timedelta(2, 'D')

    df = load_data(start_time, end_time)
    st.write(df)


    # Button to plot the data
    if st.button('Plot'):
        data = get_station_data_flu(station_name, start_time_visualization, end_time, aggregation='10-minute')
        data['timestamp'] = data['timestamp'].dt.tz_convert('America/Sao_Paulo')
        
        plot_river_level(data, station_name)