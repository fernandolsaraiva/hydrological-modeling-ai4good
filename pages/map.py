import streamlit as st
from streamlit_folium import st_folium
import folium

# Configuração da página
st.set_page_config(page_title="Flood Alert System - Map", layout="wide")

# Coordenadas das estações hidrológicas
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
from PIL import Image
# logo = Image.open("cemaden_logo.png")
# st.sidebar.image(logo, use_column_width=True)

st.header('AI Flood Alert System')

# Criação do mapa centralizado em São Paulo
mapa_sp = folium.Map(location=[-23.5505, -46.6333], zoom_start=11)

# Adiciona marcadores das estações hidrológicas com ícones personalizados
for station in stations:
    folium.Marker(
        location=[station["lat"], station["lon"]],
        popup=station["name"],
        tooltip=station["name"],
        icon=folium.Icon(icon="tint", prefix="fa", color="blue")
    ).add_to(mapa_sp)

# Exibe o mapa e captura eventos de clique
map_click = st_folium(mapa_sp, width=700, height=500)

# Verifica se uma estação foi clicada
if map_click and "last_object_clicked" in map_click:
    lat_clicked = map_click["last_object_clicked"]["lat"]
    lon_clicked = map_click["last_object_clicked"]["lng"]
    
    # Identifica a estação correspondente ao clique e salva no session_state
    for station in stations:
        if station["lat"] == lat_clicked and station["lon"] == lon_clicked:
            st.session_state["selected_station"] = station
            st.success(f"Selected station: {station['name']}")
            st.info("Go to the 'Station Graph' tab to view the time series.")
            break
