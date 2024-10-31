import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(page_title="Flood Alert System - Station Graph", layout="wide")

st.title("Station Graph")

# Função para gerar dados fictícios de nível do rio
def generate_mock_data():
    now = datetime.now()
    times_past = pd.date_range(now - timedelta(hours=10), now, freq='H')
    times_future = pd.date_range(now, now + timedelta(hours=2), freq='H')
    
    # Dados passados (medidos)
    measured_levels = np.sin(np.linspace(0, 3 * np.pi, len(times_past))) * 5 + 10
    data_past = pd.DataFrame({"datetime": times_past, "measured": measured_levels})
    
    # Dados futuros (previsões)
    predicted_levels = measured_levels[-1] + np.random.normal(0, 0.5, len(times_future)).cumsum()
    data_future = pd.DataFrame({"datetime": times_future, "predicted": predicted_levels})
    
    return data_past, data_future

# Verifica se uma estação foi selecionada
if "selected_station" in st.session_state:
    station = st.session_state["selected_station"]
    st.subheader(f"River Level Time Series - {station['name']}")

    # Gera dados fictícios
    data_past, data_future = generate_mock_data()

    # Gráfico de série temporal para o nível do rio
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_past["datetime"], y=data_past["measured"], mode='lines', name='Measured'))
    fig.add_trace(go.Scatter(x=data_future["datetime"], y=data_future["predicted"], mode='lines', name='Predicted', line=dict(dash='dash')))
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="River Level (m)",
        legend_title="Data Type",
    )
    
    # Exibe o gráfico
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No station selected. Go to the 'Map' tab and click on a station.")
