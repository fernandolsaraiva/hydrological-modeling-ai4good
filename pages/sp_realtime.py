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
from utils.translations import translations

from src.scripts.database import load_all_models_from_db
from src.scripts.preprocess import fill_missing_values_horizontal
from src.scripts.time_delay_embedding import time_delay_embedding_df
from src.scripts.utils import load_data
from util import (get_last_available_date, get_station_code_flu,
                  get_station_data_flu, get_station_names_and_critical_levels)

# Timezone
sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

render_menu()

lang = st.session_state.get("lang", "Português")  # Default to Portuguese if not set

translations2 = {
   "Português": {"title": "Painel de Previsão Hidrológica", 
                  "page_title": "Sistema de Alerta de Alagamentos",
                  "explicability_chart_title": "Impacto das Características na Previsão"
   },
    "English": {"title": "Hydrological Forecasting Dashboard", 
               "page_title": "Flood Alert System",
               "explicability_chart_title": "Feature Impact on Prediction"
    },
    "Español": {"title": "Panel de Pronóstico Hidrológico",
                "page_title": "Sistema de Alerta de Inundaciones",
                "explicability_chart_title": "Impacto de las Características en la Predicción"
}
}

st.set_page_config(
    page_title=translations2[lang]["page_title"],
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title(translations2[lang]["title"])

st.divider()

PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
DANGER_COLOR = "#d62728"
BACKGROUND_COLOR = "#ffffff"
GRID_COLOR = "#e5e5e5"
FONT_FAMILY = "Arial"

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

    # critical_colors = {"ALERT": "green", "WARNING": "orange", "EMERGENCY": "purple", "OVERFLOW": "pink"}
    critical_colors = {
        "ALERT": "#2ca02c",     # verde
        "WARNING": "#ff7f0e",   # laranja
        "EMERGENCY": "#d62728", # vermelho
        "OVERFLOW": "#9467bd"   # roxo (ok manter)
    }

    color_translations = {"ALERTA": "ALERT", "ATENÇÃO": "WARNING", "EMERGENCIA": "EMERGENCY", "EXTRAVAZAMENTO": "OVERFLOW"}
    
    for level, value in critical_levels.items():
        translated_level = color_translations[level]
        fig.add_scatter(x=[min_timestamp, max_timestamp], y=[value, value], mode='lines', line=dict(color=critical_colors[translated_level], dash='dash'), name=translated_level)

    fig.update_yaxes(title_text=translations[lang]["river_level"] + ' (m)')

    fig.update_layout(
        template="simple_white",
        font=dict(family=FONT_FAMILY, size=14),
        plot_bgcolor=BACKGROUND_COLOR,
        paper_bgcolor=BACKGROUND_COLOR,
        xaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )   

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

@st.cache_resource
def load_models(station_code):
    DATABASE_URL = os.getenv("DATABASE_URL")
    return load_all_models_from_db(station_code, DATABASE_URL)

@st.cache_data
def load_base_data(start_time, end_time):
    return load_data(start_time, end_time)

@st.cache_data
def compute_embedding(df, station_target):
    n_lags = 6
    horizon = 0
    embedded_df = time_delay_embedding_df(df, n_lags, horizon, station_target=station_target)
    embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)
    embedded_df = fill_missing_values_horizontal(embedded_df, 'flu_', n_lags)
    return embedded_df

# --- Botão de Plot ---
if st.button(translations[lang]["plot"]):
    with st.spinner(translations[lang]["loading"]):
        station_code = get_station_code_flu(station_name)
        last_available_date = get_last_available_date(station_code) if option=="current" else pd.to_datetime(formatted_datetime)
        end_time = last_available_date
        start_time = end_time - pd.Timedelta(hours=2)
        start_time_visualization = end_time - pd.Timedelta(hours=12)
        
        # df = load_data(start_time, end_time)
        df = load_base_data(start_time, end_time)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('America/Sao_Paulo')
        df = df.sort_values(by='timestamp', ascending=False).head(7)
        df.set_index('timestamp', inplace=True)
        
        station_target = station_code
        embedded_df = compute_embedding(df, station_target)
        
        # DATABASE_URL = os.getenv("DATABASE_URL")
        # models_data = load_all_models_from_db(station_code, DATABASE_URL)
        models_data = load_models(station_code)
        
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
            # st.header(translations[lang]["explainability_analysis"])

            plt.close('all')  # importante pra evitar sobreposição

            # 🎨 Estilo global (antes do plot)
            plt.style.use("default")
            plt.rcParams.update({
                "figure.facecolor": BACKGROUND_COLOR,
                "axes.facecolor": BACKGROUND_COLOR,
                "axes.edgecolor": GRID_COLOR,
                "axes.labelcolor": "#333",
                "xtick.color": "#333",
                "ytick.color": "#333",
                "font.family": FONT_FAMILY,
                "font.size": 12,
                "axes.titlesize": 16,
                "axes.labelsize": 12,
                "xtick.labelsize": 11,
                "ytick.labelsize": 11,
                "grid.color": GRID_COLOR,
                "grid.linestyle": "--",
                "grid.alpha": 0.4
            })

            explainer = shap.TreeExplainer(selected_model)
            dmatrix_single = xgb.DMatrix(embedded_df.iloc[:1])
            shap_values = explainer.shap_values(dmatrix_single)

            shap.waterfall_plot(
                shap.Explanation(
                    values=shap_values[0],
                    base_values=explainer.expected_value,
                    data=embedded_df.iloc[0]
                ),
                show=False,
                max_display=10
            )

            # 🎯 Ajustes finos pós-plot (SHAP ignora parte do rcParams)
            fig = plt.gcf()
            fig.set_size_inches(12, 6)  # mais próximo do plotly

            ax = plt.gca()

            # Grid mais parecido com Plotly
            ax.grid(True)

            # Remove bordas superiores/direita (clean style)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Ajuste de cores das barras (opcional mas melhora muito)
            for bar in ax.patches:
                if bar.get_width() > 0:
                    bar.set_color(SECONDARY_COLOR)  # positivo
                else:
                    bar.set_color(PRIMARY_COLOR)    # negativo

            plt.title(translations2[lang]["explicability_chart_title"], fontsize=16)
            plt.tight_layout()

            st.pyplot(fig)