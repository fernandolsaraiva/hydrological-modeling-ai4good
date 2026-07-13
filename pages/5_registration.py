import streamlit as st
import pandas as pd
import os

# Nome do arquivo CSV
csv_file = "inscritos.csv"

# Carregar dados existentes ou criar um novo DataFrame
if os.path.exists(csv_file):
    inscritos_df = pd.read_csv(csv_file)
else:
    inscritos_df = pd.DataFrame(columns=["Email", "Nome", "Telefone", "Endereço", "Estações"])

# Lista de estações
stations = [
    {"code": "1000370", "name": "Ribeirão dos Couros - Piraporinha Casa Grande", "lat": -23.69609, "lon": -46.586149},
    {"code": "1000410", "name": "Ribeirão dos Couros - Mercedes Paulicéia", "lat": -23.669418, "lon": -46.577271},
    {"code": "1000430", "name": "Ribeirão dos Couros - Ford", "lat": -23.652025, "lon": -46.585491},
    {"code": "1000490", "name": "Rio Tamanduateí - Vila Santa Cecilia", "lat": -23.656435, "lon": -46.47238},
    {"code": "1000580", "name": "Ribeirão dos Meninos - Volks Demarch", "lat": -23.733222, "lon": -46.552189},
    {"code": "1000610", "name": "Ribeirão dos Couros - Ford", "lat": -23.652025, "lon": -46.585491},
    {"code": "1000817", "name": "Ribeirão Vermelho - Anhanguera", "lat": -23.49195, "lon": -46.755819},
    {"code": "1000958", "name": "Rio Tamanduateí - Montante AT -09 Guamiranga", "lat": -23.589799, "lon": -46.588237},
    {"code": "1000959", "name": "Rio Tamanduateí - Jusante AT -09 Guamiranga", "lat": -23.587659, "lon": -46.592951},
    {"code": "143", "name": "Rio Tamanduateí - Prosperidade", "lat": -23.61085, "lon": -46.544628},
    {"code": "157", "name": "Rio Aricanduva - Foz", "lat": -23.537221, "lon": -46.547165},
    {"code": "279", "name": "Ribeirão dos Couros - Jd Taboão", "lat": -23.64777694, "lon": -46.58624978},
    {"code": "280", "name": "Córrego Oratório - Vila Prudente", "lat": -23.608315, "lon": -46.544318},
    {"code": "283", "name": "Rio Tamanduateí - Vd. Pacheco Chaves", "lat": -23.58216937, "lon": -46.59946381},
    {"code": "413", "name": "Rio Tamanduateí - Mercado Municipal", "lat": -23.541539, "lon": -46.628423},
    {"code": "528", "name": "Córrego Água Espraiada - Cabeceira", "lat": -23.654099, "lon": -46.648478},
    {"code": "563", "name": "Córrego Ipiranga - Pç. Leonor Kaupa", "lat": -23.619963, "lon": -46.627853},
    {"code": "629", "name": "Córrego Moinho Velho - R. Dois de Julho", "lat": -23.595544, "lon": -46.597368}
]

# Extraindo apenas os nomes das estações
station_names = [station["name"] for station in stations]

# Interface do usuário no Streamlit
st.title("Cadastro para Alerta de Enchentes 🌊🚨")

# Campos para informações do usuário
email = st.text_input("Digite seu email (obrigatório):", "")
nome = st.text_input("Digite seu nome (opcional):", "")
telefone = st.text_input("Digite seu telefone (opcional):", "")
endereco = st.text_area("Digite seu endereço (opcional):", "")
selected_stations = st.multiselect(
    "Selecione as estações para receber alertas (opcional):",
    station_names
)

# Botão de cadastro
if st.button("Cadastrar"):
    if not email:
        st.error("O email é obrigatório!")
    else:
        # Verificar se o email já está cadastrado
        if email in inscritos_df["Email"].values:
            st.error("O email já foi cadastrado.")
        else:
            # Adicionar nova entrada ao DataFrame
            new_entry = {
                "Email": email,
                "Nome": nome,
                "Telefone": telefone,
                "Endereço": endereco,
                "Estações": ", ".join(selected_stations)
            }
            inscritos_df = inscritos_df.append(new_entry, ignore_index=True)
            # Salvar no arquivo CSV
            inscritos_df.to_csv(csv_file, index=False)
            st.success("Cadastro realizado com sucesso!")
