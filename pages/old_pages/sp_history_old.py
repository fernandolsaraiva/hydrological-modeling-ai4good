import streamlit as st
from utils.menu import render_menu

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

@st.cache_data
def compute_embedding(df, station_target, horizon):
    n_lags = 6
    embedded_df = time_delay_embedding_df(
        df,
        n_lags,
        horizon,
        station_target=station_target
    )
    embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)
    embedded_df = fill_missing_values_horizontal(embedded_df, 'flu_', n_lags)
    return embedded_df


lang = st.session_state.get("lang", "Português")  # Default to Portuguese if not set

translations2 = {
   "Português": {"title": "Dados Históricos e Previsões", 
                  "page_title": "Sistema de Alerta de Inundações",
   },
    "English": {"title": "Historical Data and Predictions",
                "page_title": "Flood Alert System",
    },
    "Español": {"title": "Datos Históricos y Predicciones",
                "page_title": "Sistema de Alerta de Inundaciones"
    }
}

PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
DANGER_COLOR = "#d62728"
BACKGROUND_COLOR = "#ffffff"
GRID_COLOR = "#e5e5e5"
FONT_FAMILY = "Arial"

st.set_page_config(
    page_title=translations2[lang]["page_title"],
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title(translations2[lang]["title"])

st.divider()

def plot_predictions(
    y_test,
    y_pred,
    timestamps,
    station_name,
    critical_levels
):
    # Conversão para metros
    y_test_m = y_test / 100
    y_pred_m = y_pred / 100

    fig = go.Figure()

    # Observado
    fig.add_scatter(
        x=timestamps,
        y=y_test_m,
        mode='lines+markers',
        name=translations[lang]["observed"],
        marker=dict(color=PRIMARY_COLOR, size=5),
        line=dict(color=PRIMARY_COLOR)
    )

    # Previsto
    fig.add_scatter(
        x=timestamps,
        y=y_pred_m,
        mode='lines+markers',
        name=translations[lang]["forecast"],
        marker=dict(color=SECONDARY_COLOR, size=5),
        line=dict(color=SECONDARY_COLOR)
    )

    # Intervalo de tempo
    min_timestamp = timestamps.min()
    max_timestamp = timestamps.max()

    # Cores padronizadas de níveis críticos
    critical_colors = {
        "ALERT": "#2ca02c",     # verde
        "WARNING": "#ff7f0e",   # laranja
        "EMERGENCY": "#d62728", # vermelho
        "OVERFLOW": "#9467bd"
    }

    translate_level = {
        "ALERTA": "ALERT",
        "ATENÇÃO": "WARNING",
        "EMERGENCIA": "EMERGENCY",
        "EXTRAVAZAMENTO": "OVERFLOW"
    }

    for level, value in critical_levels.items():
        lvl = translate_level[level]
        fig.add_scatter(
            x=[min_timestamp, max_timestamp],
            y=[value / 100, value / 100],
            mode="lines",
            line=dict(color=critical_colors[lvl], dash="dash"),
            name=lvl
        )

    # Layout padronizado
    fig.update_layout(
        title={
            "text": f"{translations[lang]['river_level']} – {station_name}",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20}
        },
        template="simple_white",
        font=dict(family=FONT_FAMILY, size=14),
        plot_bgcolor=BACKGROUND_COLOR,
        paper_bgcolor=BACKGROUND_COLOR,
        height=600,
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR),
        yaxis=dict(
            title=translations[lang]["river_level"] + " (m)",
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
        # horizon = st.selectbox(translations[lang]["select_horizon"], list(range(5, 30)), index=5)
        model_options = [10,20,30,40,50,60,70,80,90,100,110,120]
        
        horizon_raw = st.selectbox(
            translations[lang]["select_horizon"],
            model_options,
            index=0,
            key="select_horizon_minutes"
        )

        horizon = int(horizon_raw / 10)

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
        station_target = station_code
        target_variable = f'flu_{station_target}(t+{horizon})'
        max_nans = 3
        # embedded_df = compute_embedding(df, station_target)
        embedded_df = compute_embedding(df, station_target, horizon)
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

        # plot_predictions(y_test_filtered, y_pred_filtered, adjusted_timestamps_filtered, critical_levels=selected_critical_level)

        fig_pred = plot_predictions(
            y_test_filtered,
            y_pred_filtered,
            adjusted_timestamps_filtered,
            station_name=station_name,
            critical_levels=selected_critical_level
        )

        # Tabs
        tab1, tab2 = st.tabs([translations[lang]["forecast"], translations[lang]["explainability"]])
        
        with tab1:
            st.plotly_chart(fig_pred, use_container_width=True)

        with tab2:
            # Shap value analysis
            
            # =========================
            # SHAP – Explainability
            # =========================

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

            # Usa apenas uma observação (mesmo padrão do outro código)
            d_single = xgb.DMatrix(X_test.iloc[:1])
            shap_values = explainer.shap_values(d_single)

            # 📊 Waterfall plot
            shap.waterfall_plot(
                shap.Explanation(
                    values=shap_values[0],
                    base_values=explainer.expected_value,
                    data=X_test.iloc[0]
                ),
                show=False,
                max_display=10
            )

            # 🎯 Ajustes finais de layout
            fig = plt.gcf()
            fig.set_size_inches(12, 6)

            ax = plt.gca()
            ax.grid(True)

            # Remove bordas superiores/direita (clean style)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            # 🎨 Cores consistentes com o dashboard
            for bar in ax.patches:
                if bar.get_width() > 0:
                    bar.set_color(SECONDARY_COLOR)  # impacto positivo
                else:
                    bar.set_color(PRIMARY_COLOR)    # impacto negativo

            plt.title(translations[lang]["explainability"], fontsize=16)
            plt.tight_layout()

            st.pyplot(fig)
            # explainer = shap.TreeExplainer(model)
            # shap_values = explainer.shap_values(d_test)

            # shap.initjs()
            # fig, ax = plt.subplots()
            # shap.summary_plot(shap_values, X_test, plot_type="bar")
            # plt.tight_layout()
            # fig.savefig("shap_summary_plot.png", bbox_inches='tight')
            # st.image("shap_summary_plot.png")
            # plt.clf()
            # os.remove("shap_summary_plot.png")