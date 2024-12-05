import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from datetime import timedelta

from util import get_station_data_flu, get_station_names

if __name__ == "__main__":
    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=200)
    logo = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo, width=150)
    st.title('Hydrological Monitoring')

    station_names = get_station_names()
    default_station = 'Rio Tamanduateí - Mercado Municipal'
    if default_station in station_names:
        station_name = st.selectbox('Select the station', station_names, index=station_names.index(default_station))
    else:
        station_name = st.selectbox('Select the station', station_names)        

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('Start Date',value=pd.to_datetime('today').date() - timedelta(days=7))
    with col2:
        end_date = st.date_input('End Date',value=pd.to_datetime('today').date())
        end_date = end_date + timedelta(days=1)

    # Aggregation selector
    aggregation = st.selectbox('Select Aggregation', ['10-minute','Hourly' ,'Daily'])

    # Button to plot the data
    if st.button('Plot'):
        data = get_station_data_flu(station_name, start_date, end_date, aggregation)
        data['value'] = data['value'] / 100  # Convertendo de cm para m
        fig = px.line(data, x='timestamp', y='value', title=f'River Level - {station_name}')
        fig.update_layout(
            yaxis_title='River level (m)',
            title={
                'text': f'River Level - {station_name}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20} 
            }
        )
        st.plotly_chart(fig)