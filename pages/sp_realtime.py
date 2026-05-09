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

# Detect language change
if "last_lang" not in st.session_state:
    st.session_state["last_lang"] = lang

if st.session_state["last_lang"] != lang:
    # limpa o gráfico e qualquer coisa dependente de idioma
    if "fig1" in st.session_state:
        del st.session_state["fig1"]

    st.session_state["last_lang"] = lang

    st.rerun()

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

def plot_river_level(data, station_name, last_available_date,critical_levels, prediction_data=None, option = translations[lang]["current_time"]):
    data['value'] = data['value'] / 100
    fig = px.line(data, x='timestamp', y='value')
    fig.add_scatter(x=data['timestamp'], y=data['value'], mode='lines+markers', marker=dict(color='blue', size=5), name=translations[lang]["observed"])
    
    if prediction_data is not None:
        prediction_data['prediction'] = prediction_data['prediction'] / 100
        prediction_data['upper_bound'] = prediction_data['upper_bound'] / 100
        prediction_data['lower_bound'] = prediction_data['lower_bound'] / 100

        fig.add_scatter(x=prediction_data['timestamp'], y=prediction_data['prediction'], mode='lines+markers', marker=dict(color='orange', size=5), name=translations[lang]["forecast"])

        # Adicionar região de incerteza
        fig.add_scatter(
            x=prediction_data['timestamp'].tolist() + prediction_data['timestamp'].tolist()[::-1],
            y=prediction_data['upper_bound'].tolist() + prediction_data['lower_bound'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name=translations[lang]["uncertainty"]
        )
    
    river_level_title = translations[lang]["river_level"] + f' - {station_name}'
    fig.update_layout(title={'text': river_level_title , 'x': 0.5, 'xanchor': 'center','font': {'size': 20}}, height=600)
    
    if option == translations[lang]["current_time"]:
        current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
    else:
        current_time = last_available_date.astimezone(pytz.timezone('America/Sao_Paulo'))
    fig.add_vline(x=current_time, line_width=3, line_dash="dash", line_color="red")
    fig.add_annotation(x=current_time, y=max(data['value']), text=translations[lang]["current_time"], showarrow=True, arrowhead=1)

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
    
    color_translations = {"ALERTA": "ALERT", "ATENÇÃO": "WARNING", "EMERGENCIA": "EMERGENCY", "EXTRAVAZAMENTO": "OVERFLOW"}
    
    for level, value in critical_levels.items():
        translated_level = color_translations[level]
        fig.add_scatter(x=[min_timestamp, max_timestamp], y=[value, value], mode='lines', line=dict(color=critical_colors[translated_level], dash='dash'), name=translated_level)


    fig.update_yaxes(title_text=translations[lang]["river_level"] + ' (m)')
    return fig

# Configuração da página
# Configuração da página
st.set_page_config(page_title="Flood Alert System", layout="wide")

if __name__ == "__main__":

    station_names, critical_levels = get_station_names_and_critical_levels()

    default_station = 'Rio Tamanduateí - Mercado Municipal'

    col1, col2 = st.columns([2, 1])

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

    selected_index = station_names.index(station_name)
    selected_critical_level = critical_levels[selected_index]

    if option == "past":

        col3, col4 = st.columns(2)

        with col3:
            selected_date = st.date_input(translations[lang]["select_date"], value=pd.to_datetime('today').date())

        if 'selected_time' not in st.session_state:
            st.session_state.selected_time = pd.to_datetime('now').time()

        with col4:
            selected_time = st.time_input(
                translations[lang]["select_time"],
                value=st.session_state.selected_time
            )

        st.session_state.selected_time = selected_time

        selected_datetime = datetime.combine(
            selected_date,
            selected_time
        )

        localized_datetime = sao_paulo_tz.localize(selected_datetime)

        utc_datetime = localized_datetime.astimezone(pytz.utc)

        formatted_datetime = utc_datetime.strftime(
            '%Y-%m-%d %H:%M:%S.%f'
        )[:-3] + ' +0000'

    # =========================
    # BUTTON
    # =========================
    if st.button(translations[lang]["plot"]):
        with st.spinner(translations[lang]["loading"]):

            station_code = get_station_code_flu(station_name)

            if option == "current":
                last_available_date = get_last_available_date(station_code)
            else:
                last_available_date = formatted_datetime
                last_available_date = pd.to_datetime(last_available_date)

            end_time = last_available_date

            start_time = end_time - pd.Timedelta(2, 'h')

            start_time_visualization = end_time - pd.Timedelta(hours=12)

            df = load_data(start_time, end_time)

            df['timestamp'] = pd.to_datetime(
                df['timestamp']
            ).dt.tz_convert('America/Sao_Paulo')

            df = df.sort_values(
                by='timestamp',
                ascending=False
            ).head(7)

            df.set_index('timestamp', inplace=True)

            # =========================
            # EMBEDDING
            # =========================
            n_lags = 6
            horizon = 0

            station_target = station_code

            target_variable = f'flu_{station_target}(t+{horizon})'

            max_nans = 3

            embedded_df = time_delay_embedding_df(
                df,
                n_lags,
                horizon,
                station_target=station_target
            )

            embedded_df = fill_missing_values_horizontal(
                embedded_df,
                'plu_',
                n_lags
            )

            embedded_df = fill_missing_values_horizontal(
                embedded_df,
                'flu_',
                n_lags
            )

            # =========================
            # MODELS
            # =========================
            DATABASE_URL = os.getenv("DATABASE_URL")

            models_data = load_all_models_from_db(
                station_code,
                DATABASE_URL
            )

            # =========================
            # PREDICTIONS
            # =========================
            predictions = []
            upper_bounds = []
            lower_bounds = []

            for horizon, model, parameters, period, rmse in models_data:

                dmatrix = xgb.DMatrix(embedded_df)

                prediction = model.predict(dmatrix)

                predictions.append(prediction[0])

                upper_bounds.append(
                    prediction[0] + 1.96 * rmse['test']
                )

                lower_bounds.append(
                    prediction[0] - 1.96 * rmse['test']
                )

            prediction_timestamps = [
                end_time + pd.Timedelta(minutes=10 * i)
                for i in range(1, 13)
            ]

            prediction_df = pd.DataFrame({
                'timestamp': prediction_timestamps,
                'prediction': predictions,
                'upper_bound': upper_bounds,
                'lower_bound': lower_bounds
            })

            prediction_df['timestamp'] = prediction_df[
                'timestamp'
            ].dt.tz_convert('America/Sao_Paulo')

            # =========================
            # OBSERVED DATA
            # =========================
            data = get_station_data_flu(
                station_name,
                start_time_visualization,
                end_time,
                aggregation='10-minute'
            )

            data['timestamp'] = pd.to_datetime(
                data['timestamp']
            ).dt.tz_convert('America/Sao_Paulo')

            # =========================
            # FIGURE 1
            # =========================
            fig1 = plot_river_level(
                data,
                station_name,
                last_available_date=last_available_date,
                critical_levels=selected_critical_level,
                prediction_data=prediction_df,
                option=option
            )

            # =========================
            # SESSION STATE
            # =========================
            st.session_state["fig1"] = fig1
            st.session_state["embedded_df"] = embedded_df
            st.session_state["models_data"] = models_data
            

    # =========================
    # TABS
    # =========================
    tab1, tab2  = st.tabs([translations[lang]["forecast"], translations[lang]["explainability"]])

    # =========================
    # TAB 1
    # =========================
    with tab1:

        if "fig1" in st.session_state:

            st.plotly_chart(
                st.session_state["fig1"],
                use_container_width=True
            )

    # =========================
    # TAB 2
    # =========================
    with tab2:

        if (
            "models_data" in st.session_state
            and
            "embedded_df" in st.session_state
        ):

            model_options = [
                10, 20, 30, 40,
                50, 60, 70, 80,
                90, 100, 110, 120
            ]

            selected_horizon = st.selectbox(
                translations[lang]["select_horizon"],
                model_options,
                index=3,
                key="selected_horizon_exp"
            )

            selected_horizon = selected_horizon / 10

            embedded_df = st.session_state["embedded_df"]

            models_data = st.session_state["models_data"]

            for horizon, model, parameters, period, rmse in models_data:

                if horizon == selected_horizon:
                    selected_model = model

            dmatrix = xgb.DMatrix(embedded_df)

            # =========================
            # SHAP
            # =========================
            explainer = shap.TreeExplainer(selected_model)

            shap_values = explainer.shap_values(dmatrix)

            shap.initjs()

            plt.close('all')

            # =========================
            # STYLE
            # =========================
            plt.style.use("default")

            shap.waterfall_plot(
                shap.Explanation(
                    values=shap_values[0],
                    base_values=explainer.expected_value,
                    data=embedded_df.iloc[0]
                ),
                show=False,
                max_display=10
            )

            fig = plt.gcf()
            ax = plt.gca()

            # =========================
            # FIGURE CONFIG
            # =========================
            fig.set_size_inches(12, 7)

            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")

            # Grid
            ax.grid(
                True,
                linestyle="--",
                linewidth=0.7,
                alpha=0.35
            )

            # Remove bordas superiores/direita
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Bordas restantes
            ax.spines['left'].set_color("#cccccc")
            ax.spines['bottom'].set_color("#cccccc")

            # =========================
            # TITLE
            # =========================
            ax.set_title(
                translations2[lang]["explicability_chart_title"],
                fontsize=18,
                fontweight='bold',
                pad=20
            )

            # =========================
            # LABELS
            # =========================
            ax.set_xlabel(
                translations[lang]["shap_value_impact"],
                fontsize=12
            )

            ax.set_ylabel(
                translations[lang]["features"],
                fontsize=12
            )

            # =========================
            # TICKS
            # =========================
            ax.tick_params(
                axis='x',
                labelsize=11
            )

            ax.tick_params(
                axis='y',
                labelsize=11
            )

            # =========================
            # WATERFALL COLORS
            # =========================
            for patch in ax.patches:

                width = patch.get_width()

                if width >= 0:
                    patch.set_facecolor("#ff7f0e")  # laranja
                else:
                    patch.set_facecolor("#1f77b4")  # azul

            # =========================
            # VALUE LABELS
            # =========================
            x_min, x_max = ax.get_xlim()

            offset = (x_max - x_min) * 0.015

            for patch in ax.patches:

                width = patch.get_width()

                y = patch.get_y() + patch.get_height() / 2

                if width >= 0:
                    x = patch.get_x() + width + offset
                    ha = 'left'
                else:
                    x = patch.get_x() + width - offset
                    ha = 'right'

                ax.text(
                    x,
                    y,
                    f"{width:.3f}",
                    va='center',
                    ha=ha,
                    fontsize=9
                )

            # =========================
            # LAYOUT
            # =========================
            plt.tight_layout()

            st.pyplot(
                fig,
                use_container_width=True
            )   
