import os
from datetime import datetime

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import pytz
import shap
import streamlit as st
import xgboost as xgb
from PIL import Image

from src.scripts.database import load_all_models_from_db
from src.scripts.preprocess import fill_missing_values_horizontal
from src.scripts.time_delay_embedding import time_delay_embedding_df
from src.scripts.utils import load_data
from util import (get_last_available_date, get_station_code_flu,
                  get_station_data_flu, get_station_names_and_critical_levels)

sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

def plot_river_level(data, station_name, last_available_date,critical_levels, prediction_data=None, option = "Prediction for the current moment"):
    data['value'] = data['value'] / 100
    fig = px.line(data, x='timestamp', y='value', title=f'River Level - {station_name}')
    fig.add_scatter(x=data['timestamp'], y=data['value'], mode='lines+markers', marker=dict(color='blue', size=5), name='Observed')
    
    if prediction_data is not None:
        prediction_data['prediction'] = prediction_data['prediction'] / 100
        prediction_data['upper_bound'] = prediction_data['upper_bound'] / 100
        prediction_data['lower_bound'] = prediction_data['lower_bound'] / 100

        fig.add_scatter(x=prediction_data['timestamp'], y=prediction_data['prediction'], mode='lines+markers', marker=dict(color='orange', size=5), name='Predicted')

        # Adicionar região de incerteza
        fig.add_scatter(
            x=prediction_data['timestamp'].tolist() + prediction_data['timestamp'].tolist()[::-1],
            y=prediction_data['upper_bound'].tolist() + prediction_data['lower_bound'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name='Uncertainty'
        )
    
    fig.update_layout(title={'text': f'River Level - {station_name}', 'x': 0.5, 'xanchor': 'center','font': {'size': 20}},height=600)
    if option == "Prediction for the current moment":
        current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
    else:
        current_time = last_available_date.astimezone(pytz.timezone('America/Sao_Paulo'))
    fig.add_vline(x=current_time, line_width=3, line_dash="dash", line_color="red")
    fig.add_annotation(x=current_time, y=max(data['value']), text="Current Time", showarrow=True, arrowhead=1)

    # Calcular o mínimo e máximo dos timestamps combinados
    all_timestamps = data['timestamp']
    if prediction_data is not None:
        all_timestamps = pd.concat([all_timestamps, prediction_data['timestamp']])
    
    min_timestamp = all_timestamps.min()
    max_timestamp = all_timestamps.max()

    # Adicionar linhas horizontais para os níveis críticos com legendas
    critical_colors = {
        "ALERT": "green",
        "WARNING": "orange",
        "EMERGENCY": "purple",
        "OVERFLOW": "pink"
    }
    
    translations = {
        "ALERTA": "ALERT",
        "ATENÇÃO": "WARNING",
        "EMERGENCIA": "EMERGENCY",
        "EXTRAVAZAMENTO": "OVERFLOW"
    }
    
    for level, value in critical_levels.items():
        translated_level = translations[level]
        fig.add_scatter(x=[min_timestamp, max_timestamp], y=[value, value], mode='lines', line=dict(color=critical_colors[translated_level], dash='dash'), name=translated_level)


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

    station_names, critical_levels = get_station_names_and_critical_levels()
    default_station = 'Rio Tamanduateí - Mercado Municipal'
    if default_station in station_names:
        station_name = st.selectbox('Select the station', station_names, index=station_names.index(default_station))
    else:
        station_name = st.selectbox('Select the station', station_names)
    selected_index = station_names.index(station_name)
    selected_critical_level = critical_levels[selected_index]


    # Add options for the user
    option = st.selectbox("Choose the prediction option:", ("Prediction for the current moment", "Choose date/time in the past"))
    # Adicionar um seletor para o usuário escolher o modelo
    model_options = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    selected_horizon = st.selectbox("Select a horizon (minutes) for Explainability analysis", model_options, index=3)
    selected_horizon = selected_horizon/10

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
        start_time_visualization = end_time - pd.Timedelta(hours=12)
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
        upper_bounds = []
        lower_bounds = []
        for horizon, model, parameters, period, rmse in models_data:
            dmatrix = xgb.DMatrix(embedded_df)
            prediction = model.predict(dmatrix)
            predictions.append(prediction[0])
            upper_bounds.append(prediction[0] + 1.96 * rmse['test'])
            lower_bounds.append(prediction[0] - 1.96 * rmse['test'])
            if horizon == selected_horizon:
                selected_model = model
                

        # Adicionar as predições ao dataframe original
        prediction_timestamps = [end_time + pd.Timedelta(minutes=10 * i) for i in range(1, 13)]
        prediction_df = pd.DataFrame({'timestamp': prediction_timestamps, 'prediction': predictions,'upper_bound': upper_bounds,
        'lower_bound': lower_bounds})
        prediction_df['timestamp'] = prediction_df['timestamp'].dt.tz_convert('America/Sao_Paulo')
        # Plotar
        data = get_station_data_flu(station_name, start_time_visualization, end_time, aggregation='10-minute')
        data['timestamp'] = data['timestamp'].dt.tz_convert('America/Sao_Paulo')

        fig1 = plot_river_level(data, station_name,last_available_date=last_available_date, critical_levels=selected_critical_level,prediction_data=prediction_df, option = option)
        st.plotly_chart(fig1)

        st.header("Explainability Analysis")

        # Shap value analysis
        explainer = shap.TreeExplainer(selected_model)
        shap_values = explainer.shap_values(dmatrix)
        shap.initjs()
        shap.waterfall_plot(
            shap.Explanation(
                values=shap_values[0], 
                base_values=explainer.expected_value, 
                data=embedded_df.iloc[0]
            ),
            show = False, max_display=10
        )
        st.pyplot(plt.gcf())

        