import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import pytz
import shap
import streamlit as st
import xgboost as xgb
from PIL import Image
from streamlit_shap import st_shap

from src.scripts.database import load_all_models_from_db
from src.scripts.preprocess import fill_missing_values_horizontal
from src.scripts.time_delay_embedding import time_delay_embedding_df
from src.scripts.utils import load_data
from util import (get_last_available_date, get_station_code_flu,
                  get_station_data_flu, get_station_names)

sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

def plot_river_level(data, station_name, last_available_date, prediction_data=None, option = "Prediction for the current moment"):
    data['value'] = data['value'] / 100
    fig = px.line(data, x='timestamp', y='value', title=f'River Level - {station_name}')
    fig.add_scatter(x=data['timestamp'], y=data['value'], mode='lines+markers', marker=dict(color='blue', size=5), name='Observed')
    
    if prediction_data is not None:
        prediction_data['prediction'] = prediction_data['prediction'] / 100
        fig.add_scatter(x=prediction_data['timestamp'], y=prediction_data['prediction'], mode='lines+markers', marker=dict(color='orange', size=5), name='Predicted')
    
    fig.update_layout(title={'text': f'River Level - {station_name}', 'x': 0.5, 'xanchor': 'center'})
    if option == "Prediction for the current moment":
        current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
    else:
        current_time = last_available_date.astimezone(pytz.timezone('America/Sao_Paulo'))
    fig.add_vline(x=current_time, line_width=3, line_dash="dash", line_color="red")
    fig.add_annotation(x=current_time, y=max(data['value']), text="Current Time", showarrow=True, arrowhead=1)
    fig.update_yaxes(title_text='River Level (m)')
    return fig

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
    
    # Add options for the user
    option = st.selectbox("Choose the prediction option:", ("Prediction for the current moment", "Choose date/time in the past"))
    # Adicionar um seletor para o usuário escolher o modelo
    model_options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    selected_horizon = st.selectbox("Select a model for Explainability analysis", model_options, index=5)

    if option == "Choose date/time in the past":
        selected_date = st.date_input("Choose the date", value=pd.to_datetime('today').date())
        
        if 'selected_time' not in st.session_state:
            st.session_state.selected_time = pd.to_datetime('now').time()
        
        selected_time = st.time_input("Choose the time", value=st.session_state.selected_time)
        st.session_state.selected_time = selected_time

        selected_datetime = datetime.combine(selected_date, selected_time)
        localized_datetime = sao_paulo_tz.localize(selected_datetime)
        utc_datetime = localized_datetime.astimezone(pytz.utc)
        # Formate o datetime em UTC
        formatted_datetime = utc_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' +0000'
        st.write("Formatted datetime:", formatted_datetime)

    if st.button('Plot'):
        plot_container = st.empty()
        # Load data for prediction
        station_code = get_station_code_flu(station_name)
        if option == "Prediction for the current moment":
            last_available_date = get_last_available_date(station_code)
        else:
            last_available_date = formatted_datetime
            last_available_date = pd.to_datetime(last_available_date)
        end_time = last_available_date
        start_time = end_time - pd.Timedelta(2, 'h')
        start_time_visualization = end_time - pd.Timedelta(1, 'D')
        df = load_data(start_time, end_time)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('America/Sao_Paulo')
        df= df.sort_values(by='timestamp', ascending=False).head(7)
        df.set_index('timestamp', inplace=True)
        # Aplicar Time Delay Embedding
        n_lags = 6
        horizon = 0
        station_target = station_code
        target_variable = f'flu_{station_target}(t+{horizon})'
        max_nans = 3
        embedded_df = time_delay_embedding_df(df, n_lags, horizon, station_target=station_target)
        embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)
        embedded_df = fill_missing_values_horizontal(embedded_df, 'flu_', n_lags)
        # Carregar todos os modelos do banco de dados de uma vez
        DATABASE_URL = os.getenv("DATABASE_URL")
        models_data = load_all_models_from_db(station_code, DATABASE_URL)
        
        # Fazer as predições
        predictions = []
        for horizon, model, parameters, period, rmse in models_data:
            dmatrix = xgb.DMatrix(embedded_df)
            prediction = model.predict(dmatrix)
            predictions.append(prediction[0])
            if horizon == selected_horizon:
                selected_model = model
                

        # Adicionar as predições ao dataframe original
        prediction_timestamps = [end_time + pd.Timedelta(minutes=10 * i) for i in range(1, 13)]
        prediction_df = pd.DataFrame({'timestamp': prediction_timestamps, 'prediction': predictions})
        prediction_df['timestamp'] = prediction_df['timestamp'].dt.tz_convert('America/Sao_Paulo')
        # Plotar
        data = get_station_data_flu(station_name, start_time_visualization, end_time, aggregation='10-minute')
        data['timestamp'] = data['timestamp'].dt.tz_convert('America/Sao_Paulo')

        fig1 = plot_river_level(data, station_name,last_available_date=last_available_date, prediction_data=prediction_df, option = option)
        st.plotly_chart(fig1)

        # Shap value analysis
        explainer = shap.TreeExplainer(selected_model)
        shap_values = explainer.shap_values(dmatrix)
        shap.initjs()
        # Criar uma figura e um eixo
        fig, ax = plt.subplots(figsize=(8, 6))
        shap.waterfall_plot(shap.Explanation(values=shap_values[0], base_values=explainer.expected_value, data=embedded_df.iloc[0]))
        plt.tight_layout()
        st.pyplot(fig, bbox_inches='tight')
        plt.clf()

        