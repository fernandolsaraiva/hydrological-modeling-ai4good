import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configuração da página
st.set_page_config(page_title="Station Graph and SHAP Waterfall Plot", layout="wide")

st.title("Station Graph and SHAP Waterfall Plot")

# Definições de parâmetros fixos
MARGIN_PERCENT = 0.1  # Percentual para as margens no eixo Y
SEED = 55  # Semente para controle de aleatoriedade (ou None para aleatório)
np.random.seed(SEED)

#####################################################################################
# REGIÃO RESPONSÁVEL POR GERAR OS DADOS DE MEDIÇÕES E PREDIÇÕES
#####################################################################################

# Função para gerar séries temporais com dois picos controlados por semente
def generate_mock_data(alert_value, overflow_value):
    now = datetime.now()
    times_past = pd.date_range(now - timedelta(hours=29), now, freq='H')  # 30 pontos de medida
    times_future = pd.date_range(now + timedelta(hours=1), now + timedelta(hours=12), freq='H')  # 12 pontos de previsão

    # Calcular o limite inferior baseado na diferença entre ALERTA e EXTRAVAZAMENTO
    limit_diff = overflow_value - alert_value
    lower_limit = alert_value - (limit_diff * 0.3)

    # Séries levemente ruidosas
    measured_levels = np.random.normal(loc=alert_value, scale=0.5, size=len(times_past))

    # Adiciona dois picos controlados pela semente
    if SEED is not None:
        np.random.seed(SEED)
    peak_indices = np.random.choice(len(times_past), size=2, replace=False)
    measured_levels[peak_indices] = np.random.uniform(overflow_value - 2, overflow_value, size=2)  # Picos até 2 acima do limite máximo

    # Garante que os dados não ultrapassem o valor de EXTRAVAZAMENTO
    measured_levels = np.clip(measured_levels, lower_limit, overflow_value)

    data_past = pd.DataFrame({"datetime": times_past, "measured": measured_levels})

    # Dados futuros como extensão ruidosa do último valor medido
    predicted_levels = measured_levels[-1] + np.random.normal(0, 0.5, len(times_future)).cumsum()

    # Banda de confiança de 97%
    base_error = 0.5
    time_deltas = np.arange(len(times_future))  # Número de horas desde o início da previsão
    ci_97_error = base_error * 2 * (1 + time_deltas / 5)  # Erro cresce mais rapidamente

    data_future = pd.DataFrame({
        "datetime": times_future,
        "predicted": predicted_levels,
        "ci_97_upper": predicted_levels + ci_97_error,
        "ci_97_lower": predicted_levels - ci_97_error,
    })

    return data_past, data_future, lower_limit

#####################################################################################
# REGIÃO RESPONSÁVEL POR PLOTAR O GRÁFICO APENAS SE UMA ESTAÇÃO FOR SELECIONADA
#####################################################################################

# Verifica se uma estação foi selecionada
if "selected_station" in st.session_state:
    station = st.session_state["selected_station"]
    st.subheader(f"River Level Time Series - {station['name']}")

    # Carregar o arquivo JSON com os níveis de alerta
    try:
        with open("levels.json", "r") as f:
            levels = json.load(f)
    except FileNotFoundError:
        st.error("File 'levels.json' not found.")
        st.stop()

    # Obtém os valores para a estação selecionada
    station_name = station['name']
    if station_name in levels:
        station_levels = levels[station_name]
    else:
        st.error(f"############### Station {station_name} not found in the levels.json file. ###############")
        st.stop()

    # Gera dados fictícios
    data_past, data_future, lower_limit = generate_mock_data(
        station_levels['ALERTA'], station_levels['EXTRAVAZAMENTO']
    )

    # Configuração do gráfico principal com Plotly
    fig = go.Figure()

    # Adiciona as linhas de risco usando os valores do arquivo JSON
    fig.add_trace(go.Scatter(
        x=[data_past["datetime"].min(), data_future["datetime"].max()],
        y=[station_levels['ATENÇÃO'], station_levels['ATENÇÃO']],
        mode="lines",
        line=dict(color="yellow", dash="dot"),
        name="Attention"
    ))

    fig.add_trace(go.Scatter(
        x=[data_past["datetime"].min(), data_future["datetime"].max()],
        y=[station_levels['ALERTA'], station_levels['ALERTA']],
        mode="lines",
        line=dict(color="orange", dash="dot"),
        name="Alert"
    ))

    fig.add_trace(go.Scatter(
        x=[data_past["datetime"].min(), data_future["datetime"].max()],
        y=[station_levels['EMERGENCIA'], station_levels['EMERGENCIA']],
        mode="lines",
        line=dict(color="magenta", dash="dot"),
        name="Emergency"
    ))

    fig.add_trace(go.Scatter(
        x=[data_past["datetime"].min(), data_future["datetime"].max()],
        y=[station_levels['EXTRAVAZAMENTO'], station_levels['EXTRAVAZAMENTO']],
        mode="lines",
        line=dict(color="red", dash="dot"),
        name="Overflow"
    ))

    # Adiciona a banda de confiança de 97%
    fig.add_trace(go.Scatter(
        x=pd.concat([data_future["datetime"], data_future["datetime"][::-1]]),
        y=pd.concat([data_future["ci_97_upper"], data_future["ci_97_lower"][::-1]]),
        fill='toself', fillcolor='rgba(0, 0, 255, 0.1)', line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip", name='Confidence 97%'
    ))

    # Linha de previsão com marcadores em "x"
    fig.add_trace(go.Scatter(
        x=data_future["datetime"], y=data_future["predicted"], mode='lines+markers',
        name='Predicted', line=dict(dash='dash', color='blue'),
        marker=dict(symbol='x', size=10, color='blue')  # Alteração do marcador para "x"
    ))

    # Linha de medições com marcadores
    fig.add_trace(go.Scatter(
        x=data_past["datetime"], y=data_past["measured"], mode='lines+markers',
        name='Measured', line=dict(color='green'), marker=dict(size=8, color='green')
    ))

    # Ajusta os limites do eixo Y dinamicamente com margem
    # Garantir que o limite mínimo e máximo seja ajustado corretamente aos valores de risco
    y_min = min(data_past["measured"].min(), data_future["ci_97_lower"].min(), station_levels['ATENÇÃO'])
    y_max = max(data_past["measured"].max(), data_future["ci_97_upper"].max(), station_levels['EXTRAVAZAMENTO'])

    # Coloca uma margem de 10% em relação ao intervalo entre os valores de risco
    y_margin = (y_max - y_min) * MARGIN_PERCENT
    fig.update_layout(
        yaxis=dict(range=[y_min - y_margin, y_max + y_margin]),
        xaxis_title="Time",
        yaxis_title="River Level (m)",
        legend_title="Data Type",
    )

    # Exibe o gráfico principal
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No station selected. Please select a station from the map to view the data.")
