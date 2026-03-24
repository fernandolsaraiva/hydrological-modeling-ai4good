import os
from datetime import datetime
from utils.menu import render_menu
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

# Timezone
sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

# --- Render menu sidebar existente ---
render_menu()

# Language selection
lang = st.sidebar.selectbox("Language", ["Portuguese", "English"])

translations = {
   "Portuguese": {"title": "Painel de Previsão de Alagamentos", 
                  "page_title": "Sistema de Alerta de Alagamentos",
                  "select_station": "Selecione a Estação",
                  "prediction_option": "Opção de Previsão",
                  "current_moment": "Instante atual",
                  "past_moment": "Data/Hora Passada",
                  "horizon": "Horizonte (minutos)",
                  "select_station": "Selecione a Estação",
                  "select_date": "Selecione a Data",
                  "select_time": "Selecione a Hora",
                  "forecast": "Previsão",
                  "explainability": "Explicabilidade",
                  "explainability_analysis": "Análise de Explicabilidade",
                  "plot": "Plotar Gráfico",  
                  "loading":"Carregando dados e gerando gráficos...",
                  "river_level": "Nível do Rio",
                  "current_time": "Hora Atual",
                  "observed": "Observado",
                  "forecast": "Previsão",
                  "uncertainty": "Incerteza"
   },
    "English": {"title": "Flood Forecasting Dashboard", 
               "page_title": "Flood Alert System",
               "select_station": "Select Station",
               "prediction_option": "Prediction Option",
               "current_moment": "Current moment",
               "past_moment": "Past Date/Time",
               "horizon": "Horizon (minutes)",
               "select_station": "Select Station",
               "select_date": "Select Date",
               "select_time": "Select Time",
               "forecast": "Forecast",
               "explainability": "Explainability",
               "explainability_analysis": "Explainability Analysis",
               "plot": "Plot Graph",
               "loading":"Loading data and generating plots...",
               "river_level": "River Level",
               "current_time": "Current Time",
               "observed": "Observed",
               "forecast": "Forecast",
               "uncertainty": "Uncertainty"
    }
}

st.set_page_config(
    page_title=translations[lang]["page_title"],
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title(translations[lang]["title"])

# --- Função de plotagem ---
def plot_river_level(data, station_name, last_available_date, critical_levels, prediction_data=None, option="current"):
    data['value'] = data['value'] / 100
    fig = px.line(data, x='timestamp', y='value')
    fig.add_scatter(x=data['timestamp'], y=data['value'], mode='lines+markers', marker=dict(color='blue', size=5), name=translations[lang]["observed"])
    
    if prediction_data is not None:
        prediction_data['prediction'] = prediction_data['prediction'] / 100
        prediction_data['upper_bound'] = prediction_data['upper_bound'] / 100
        prediction_data['lower_bound'] = prediction_data['lower_bound'] / 100

        fig.add_scatter(x=prediction_data['timestamp'], y=prediction_data['prediction'], mode='lines+markers', marker=dict(color='orange', size=5), name=translations[lang]["forecast"])

        fig.add_scatter(
            x=prediction_data['timestamp'].tolist() + prediction_data['timestamp'].tolist()[::-1],
            y=prediction_data['upper_bound'].tolist() + prediction_data['lower_bound'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(255,165,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name=translations[lang]["uncertainty"]
        )
    
    river_level_title = translations[lang]["river_level"] + f' - {station_name}'

    fig.update_layout(title={'text': river_level_title , 'x': 0.5, 'xanchor': 'center','font': {'size': 20}}, height=600)
    
    current_time = datetime.now(sao_paulo_tz) if option == "current" else last_available_date.astimezone(sao_paulo_tz)
    fig.add_vline(x=current_time, line_width=3, line_dash="dash", line_color="red")
    fig.add_annotation(x=current_time, y=max(data['value']), text=translations[lang]["current_time"], showarrow=True, arrowhead=1)

    all_timestamps = data['timestamp']
    if prediction_data is not None:
        all_timestamps = pd.concat([all_timestamps, prediction_data['timestamp']])
    min_timestamp = all_timestamps.min()
    max_timestamp = all_timestamps.max()

    critical_colors = {"ALERT": "green", "WARNING": "orange", "EMERGENCY": "purple", "OVERFLOW": "pink"}
    color_translations = {"ALERTA": "ALERT", "ATENÇÃO": "WARNING", "EMERGENCIA": "EMERGENCY", "EXTRAVAZAMENTO": "OVERFLOW"}
    
    for level, value in critical_levels.items():
        translated_level = color_translations[level]
        fig.add_scatter(x=[min_timestamp, max_timestamp], y=[value, value], mode='lines', line=dict(color=critical_colors[translated_level], dash='dash'), name=translated_level)

    fig.update_yaxes(title_text=translations[lang]["river_level"] + ' (m)')
    return fig


# --- Inputs organizados em colunas ---
station_names, critical_levels_list = get_station_names_and_critical_levels()
default_station = 'Rio Tamanduateí - Mercado Municipal'
col1, col2, col3 = st.columns([2, 1, 1])    

options = {
    "current": translations[lang]["current_moment"],
    "past": translations[lang]["past_moment"]
}

with col1:
    station_name = st.selectbox(translations[lang]["select_station"], station_names, index=station_names.index(default_station) if default_station in station_names else 0)
with col2:
    option = st.radio(
        translations[lang]["prediction_option"],
        options.keys(),
        format_func=lambda x: options[x]
    )
with col3:
    model_options = [10,20,30,40,50,60,70,80,90,100,110,120]
    selected_horizon = st.selectbox(translations[lang]["horizon"], model_options, index=0)/10

selected_index = station_names.index(station_name)
selected_critical_level = critical_levels_list[selected_index]

# Campos adicionais se "Past Date/Time" for selecionado
if option == "past":
    col4, col5 = st.columns(2)
    with col4:
        selected_date = st.date_input(translations[lang]["select_date"], value=pd.to_datetime('today').date())
    with col5:
        selected_time = st.time_input(translations[lang]["select_time"], value=pd.to_datetime('now').time())
    selected_datetime = datetime.combine(selected_date, selected_time)
    localized_datetime = sao_paulo_tz.localize(selected_datetime)
    utc_datetime = localized_datetime.astimezone(pytz.utc)
    formatted_datetime = utc_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' +0000'


# --- Botão de Plot ---
if st.button(translations[lang]["plot"]):
    with st.spinner(translations[lang]["loading"]):
        station_code = get_station_code_flu(station_name)
        last_available_date = get_last_available_date(station_code) if option=="current" else pd.to_datetime(formatted_datetime)
        end_time = last_available_date
        start_time = end_time - pd.Timedelta(hours=2)
        start_time_visualization = end_time - pd.Timedelta(hours=12)
        
        df = load_data(start_time, end_time)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('America/Sao_Paulo')
        df = df.sort_values(by='timestamp', ascending=False).head(7)
        df.set_index('timestamp', inplace=True)
        
        n_lags = 6
        horizon = 0
        station_target = station_code
        embedded_df = time_delay_embedding_df(df, n_lags, horizon, station_target=station_target)
        embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)
        embedded_df = fill_missing_values_horizontal(embedded_df, 'flu_', n_lags)
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        models_data = load_all_models_from_db(station_code, DATABASE_URL)
        
        # Predictions
        predictions, upper_bounds, lower_bounds = [], [], []
        for horizon_i, model, parameters, period, rmse in models_data:
            dmatrix = xgb.DMatrix(embedded_df)
            prediction = model.predict(dmatrix)
            predictions.append(prediction[0])
            upper_bounds.append(prediction[0] + 1.96*rmse['test'])
            lower_bounds.append(prediction[0] - 1.96*rmse['test'])
            if horizon_i == selected_horizon:
                selected_model = model
        
        prediction_timestamps = [end_time + pd.Timedelta(minutes=10*i) for i in range(1,13)]
        prediction_df = pd.DataFrame({
            'timestamp': prediction_timestamps,
            'prediction': predictions,
            'upper_bound': upper_bounds,
            'lower_bound': lower_bounds
        })
        prediction_df['timestamp'] = prediction_df['timestamp'].dt.tz_convert('America/Sao_Paulo')
        
        data = get_station_data_flu(station_name, start_time_visualization, end_time, aggregation='10-minute')
        data['timestamp'] = data['timestamp'].dt.tz_convert('America/Sao_Paulo')
        
        fig1 = plot_river_level(
            data, station_name,
            last_available_date=last_available_date,
            critical_levels=selected_critical_level,
            prediction_data=prediction_df,
            option=option
        )
        
        # Tabs
        tab1, tab2 = st.tabs([translations[lang]["forecast"], translations[lang]["explainability"]])
        
        with tab1:
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            st.header(translations[lang]["explainability_analysis"])
            explainer = shap.TreeExplainer(selected_model)
            shap_values = explainer.shap_values(dmatrix)
            shap.initjs()
            shap.waterfall_plot(
                shap.Explanation(
                    values=shap_values[0],
                    base_values=explainer.expected_value,
                    data=embedded_df.iloc[0]
                ),
                show=False, max_display=10
            )
            st.pyplot(plt.gcf())