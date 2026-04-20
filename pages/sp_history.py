import streamlit as st
from utils.menu import render_menu
import plotly.graph_objects as go
from datetime import datetime
import pytz

# st.title("São Paulo — Previsão em tempo real")

import os
from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
import shap
import streamlit as st
import xgboost as xgb
from PIL import Image
from sklearn.metrics import mean_squared_error

from src.scripts.database import load_model_from_db
from src.scripts.preprocess import fill_missing_values_horizontal
from src.scripts.time_delay_embedding import time_delay_embedding_df
from src.scripts.utils import load_data
from util import get_station_code_flu, get_station_names_and_critical_levels
from utils.translations import translations

render_menu()

PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
DANGER_COLOR = "#d62728"
BACKGROUND_COLOR = "#ffffff"
GRID_COLOR = "#e5e5e5"
FONT_FAMILY = "Arial"

lang = st.session_state.get("lang", "Português")  # Default to Portuguese if not set

translations2 = {
   "Português": {"title": "Dados Históricos e Previsões", 
                  "page_title": "Sistema de Alerta de Inundações",
                  "explicability_chart_title": "Impacto das Características na Predição"
                  
   },
    "English": {"title": "Historical Data and Predictions",
                "page_title": "Flood Alert System",
                "explicability_chart_title": "Impact of Features on Prediction"
    },
    "Español": {"title": "Datos Históricos y Predicciones",
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

# def plot_predictions(y_test, y_pred, timestamps, critical_levels):
#     y_test_m = [value / 100 for value in y_test]
#     y_pred_m = [value / 100 for value in y_pred]

#     fig = go.Figure()

#     # Add actual values line
#     fig.add_trace(go.Scatter(x=timestamps, y=y_test_m, mode='lines+markers', name='Actual Values', line=dict(color='blue')))

#     fig.add_trace(go.Scatter(x=timestamps, y=y_pred_m, mode='lines+markers', name='Predicted Values', line=dict(color='orange')))
    
#     # Add horizontal lines for critical levels with labels
#     critical_colors = {
#         "ALERT": "green",
#         "WARNING": "orange",
#         "EMERGENCY": "purple",
#         "OVERFLOW": "pink"
#     }
    
#     critical_colors_translations = {
#         "ALERTA": "ALERT",
#         "ATENÇÃO": "WARNING",
#         "EMERGENCIA": "EMERGENCY",
#         "EXTRAVAZAMENTO": "OVERFLOW"
#     }
    
#     min_timestamp = min(timestamps)
#     max_timestamp = max(timestamps)
    
#     for level, value in critical_levels.items():
#         translated_level = critical_colors_translations[level]
#         fig.add_scatter(x=[min_timestamp, max_timestamp], y=[value, value], mode='lines', line=dict(color=critical_colors[translated_level], dash='dash'), name=translated_level)
    

#     fig.update_layout(
#         title='Comparison between Actual and Predicted Values',
#         xaxis_title='Timestamp',
#         yaxis_title='River level (m)',
#         legend=dict(x=0, y=1),
#         margin=dict(l=0, r=0, t=30, b=0), 
#         height=600
#     )
#     return fig

def plot_predictions(y_test, y_pred, timestamps, critical_levels, station_name, option="current", last_available_date=None):
    y_test_m = [value / 100 for value in y_test]
    y_pred_m = [value / 100 for value in y_pred]

    fig = go.Figure()

    # 🔵 Observed (igual gráfico 1)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=y_test_m,
        mode='lines+markers',
        name=translations[lang]["observed"],
        line=dict(color='blue'),
        marker=dict(size=5)
    ))

    # 🟠 Forecast (igual gráfico 1)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=y_pred_m,
        mode='lines+markers',
        name=translations[lang]["forecast"],
        line=dict(color='orange'),
        marker=dict(size=5)
    ))

    # 📌 Critical levels (igual gráfico 1)
    critical_colors = {
        "ALERT": "#2ca02c",
        "WARNING": "#ff7f0e",
        "EMERGENCY": "#d62728",
        "OVERFLOW": "#9467bd"
    }

    critical_colors_translations = {
        "ALERTA": "ALERT",
        "ATENÇÃO": "WARNING",
        "EMERGENCIA": "EMERGENCY",
        "EXTRAVAZAMENTO": "OVERFLOW"
    }

    min_timestamp = min(timestamps)
    max_timestamp = max(timestamps)

    for level, value in critical_levels.items():
        translated_level = critical_colors_translations[level]

        fig.add_trace(go.Scatter(
            x=[min_timestamp, max_timestamp],
            y=[value, value],
            mode='lines',
            line=dict(color=critical_colors[translated_level], dash='dash'),
            name=translated_level
        ))

    river_level_title = translations[lang]["river_level"] + f' - {station_name}'

    fig.update_layout(title={'text': river_level_title , 'x': 0.5, 'xanchor': 'center','font': {'size': 20}}, height=600)

    # 🧠 Layout igual gráfico 1
    fig.update_layout(
        template="simple_white",
        font=dict(family="Arial", size=14),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=600,
        title=dict(
            # text="Comparison between Actual and Predicted Values",

            x=0.5,
            xanchor="center",
            font=dict(size=20)
        ),
        xaxis=dict(
            title=translations[lang]["timestamp"],
            showgrid=True,
            gridcolor="#e5e5e5"
        ),
        yaxis=dict(
            title=translations[lang]["river_level"],
            showgrid=True,
            gridcolor="#e5e5e5"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # ⏱️ Linha vertical (igual gráfico 1)
    if option == "current" and last_available_date is not None:
        current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
    else:
        current_time = last_available_date

    if current_time is not None:
        fig.add_vline(
            x=current_time,
            line_width=3,
            line_dash="dash",
            line_color="red"
        )

    return fig

if __name__ == "__main__":
  
    # st.title(translations[lang]["title"])

    station_names, critical_levels = get_station_names_and_critical_levels()
    default_station = 'Rio Tamanduateí - Mercado Municipal'
    if default_station in station_names:
        station_name = st.selectbox(translations[lang]["select_station"], station_names, index=station_names.index(default_station))
    else:
        station_name = st.selectbox(translations[lang]["select_station"], station_names)
    selected_index = station_names.index(station_name)
    selected_critical_level = critical_levels[selected_index]

    col1, col2, col3 = st.columns([2, 2, 1])  

    with col1:
        start_time = st.date_input(translations[lang]["select_start_date"], value=pd.to_datetime('today').date() - timedelta(days=7))

    with col2:
        end_time = st.date_input(translations[lang]["select_end_date"], value=pd.to_datetime('today').date())

    with col3:
        horizon = st.selectbox(translations[lang]["select_horizon"], list(range(5, 30)), index=5)

    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)+timedelta(days=1)

    if st.button(translations[lang]["plot"]):
        station_code = get_station_code_flu(station_name)

        df = load_data(start_time, end_time)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('America/Sao_Paulo')
        df= df.sort_values(by='timestamp', ascending=False)
        df.set_index('timestamp', inplace=True)

        # Carregar modelo do banco
        DATABASE_URL = os.getenv("DATABASE_URL")
        model, parameters, period, rmse = load_model_from_db(station_code, horizon, DATABASE_URL)

        # Aplicar Time Delay Embedding
        n_lags = 6
        horizon = horizon
        station_target = station_code
        target_variable = f'flu_{station_target}(t+{horizon})'
        max_nans = 3
        embedded_df = time_delay_embedding_df(df, n_lags, horizon, station_target=station_target)
        embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)
        embedded_df = fill_missing_values_horizontal(embedded_df, 'flu_', n_lags)
        X_test = embedded_df.drop(columns=[target_variable])
        y_test = embedded_df[target_variable]
        d_test = xgb.DMatrix(X_test)
        y_pred = model.predict(d_test)
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        adjusted_timestamps = (X_test.index + pd.to_timedelta(horizon * 10, unit='m')).tz_convert(sao_paulo_tz)
        mask = ~np.isnan(y_test) & ~np.isnan(y_pred)
        y_test_filtered = y_test[mask]
        y_pred_filtered = y_pred[mask]
        adjusted_timestamps_filtered = adjusted_timestamps[mask]
        rmse = np.sqrt(mean_squared_error(y_test_filtered, y_pred_filtered))
        st.write(f'RMSE: {rmse}')

        fig_pred = plot_predictions(y_test_filtered, y_pred_filtered, adjusted_timestamps_filtered, critical_levels=selected_critical_level, station_name=station_name, option="historical")

        # Tabs
        tab1, tab2 = st.tabs([translations[lang]["forecast"], translations[lang]["explainability"]])
        
        with tab1:
            st.plotly_chart(fig_pred, use_container_width=True)
        
        with tab2:

            plt.close("all")

            # 🎨 Estilo global (igual ao dashboard principal)
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

            # ⚙️ SHAP
            explainer = shap.TreeExplainer(model)

            # Agora sim: dataset inteiro
            d_all = xgb.DMatrix(X_test)
            shap_values = explainer.shap_values(d_all)

            # 📊 Summary bar plot (global)
            shap.summary_plot(
                shap_values,
                X_test,
                plot_type="bar",
                show=False
            )

            fig = plt.gcf()
            ax = plt.gca()

            # 🎨 Cores
            for bar in ax.patches:
                bar.set_color(SECONDARY_COLOR)

            # ➕ Adiciona valor em cada barra
            for bar in ax.patches:
                width = bar.get_width()
                ax.text(
                    width,                          # posição x (final da barra)
                    bar.get_y() + bar.get_height()/2,  # posição y (centro da barra)
                    f"{width:.3f}",                 # valor formatado
                    va="center",
                    ha="left",
                    fontsize=10
                )

            # 🎯 Layout
            fig.set_size_inches(12, 6)
            ax.grid(True)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            plt.title(translations2[lang]["explicability_chart_title"], fontsize=16)
            plt.tight_layout()

            st.pyplot(fig)
        