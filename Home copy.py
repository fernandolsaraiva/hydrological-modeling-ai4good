import streamlit as st
from utils.menu import render_menu
from PIL import Image
from dotenv import load_dotenv
from streamlit_card import card
from streamlit_folium import st_folium
import folium
import psycopg2
import os

st.set_page_config(
    page_title="Floodcasting XAI Alert System",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.card-container {
    background-color: #ffffff;
    border-radius: 18px;
    overflow: hidden;
    transition: all 0.25s ease-in-out;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    cursor: pointer;
}

.card-container:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.card-image {
    width: 100%;
    height: 140px;
    object-fit: cover;
}

.card-content {
    padding: 14px;
}

.card-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 6px;
}

.card-subtitle {
    font-size: 13px;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

def city_card(nome, imagem, key):
    st.markdown(f"""
    <div class="card">
        <img src="{imagem}">
        <div class="card-body">
            <div class="card-title">{nome}</div>
            <div class="card-sub">Clique abaixo</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return st.button("Selecionar", key=key, use_container_width=True)

render_menu()

# Define translations
translations = {
   "Portuguese": {"title": "Bem-vindo ao ", 
                    "body": "Utilize as abas à esquerda para navegar pelas diferentes seções do painel de controle.",
                    "subtitle1":"Selecione a Região de interesse"},
   "English": {"title": "Welcome to the ", 
                "body": "Use the tabs on the left to navigate through the different sections of the dashboard.",
                "subtitle1": "Selecione a Região de interesse"},
}
# Language selection
lang = st.sidebar.selectbox("Language", ["Portuguese", "English"])

# Display text based on selection
st.title(translations[lang]["title"] + "Floodcasting XAI Alert System")
st.write(translations[lang]["body"])

st.divider()
st.subheader(translations[lang]["subtitle1"])

col1, col2, col3, col4 = st.columns(4, gap="large")

with col1:
    if city_card(
        "São Paulo - Brasil",
        "https://upload.wikimedia.org/wikipedia/commons/9/93/Mapa_sp.png",
        "sp"
    ):
        st.session_state["cidade_selecionada"] = "São Paulo"
        st.toast("São Paulo selecionada!")

with col2:
    if city_card(
        "Rio de Janeiro - Brasil",
        "https://tvprefeito.com/wp-content/uploads/2023/03/mapa-rj.jpeg",
        "rj"
    ):
        st.session_state["cidade_selecionada"] = "Rio de Janeiro"
        st.toast("Rio de Janeiro selecionado!")

with col3:
    if city_card(
        "Paraguai",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Mapa_do_Paraguai.gif",
        "py"
    ):
        st.session_state["cidade_selecionada"] = "Paraguai"
        st.toast("Paraguai selecionado!")

with col4:
    if city_card(
        "Uruguai",
        "https://upload.wikimedia.org/wikipedia/commons/1/1a/Uruguay_location_map.svg",
        "uy"
    ):
        st.session_state["cidade_selecionada"] = "Uruguai"
        st.toast("Uruguai selecionado!")

st.divider()
if "cidade_selecionada" in st.session_state:
    st.success(f"Você selecionou: {st.session_state['cidade_selecionada']}")

def fetch_stations(station_type, db_url):
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    if station_type == "Rain":
        query = "SELECT name, lat, long FROM station.station_plu;"
    else:
        query = "SELECT name, lat, long FROM station.station_flu;"
    
    cursor.execute(query)
    stations = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return stations

def create_map(stations, station_type):
    map_sp = folium.Map(location=[-23.55052, -46.633308], zoom_start=10)
    
    icon_color = "blue" if station_type == "Rain" else "green"
    
    for station in stations:
        folium.Marker(
            location=[station[1], station[2]],
            popup=station[0],
            tooltip=station[0],
            icon=folium.Icon(icon="tint", prefix="fa", color=icon_color)
        ).add_to(map_sp)
    
    return map_sp

if __name__ == "__main__":
    load_dotenv()

    station_type = st.selectbox("Select the type of station:", ["Rain", "Level"])

    if station_type:
        DATABASE_URL = os.getenv("DATABASE_URL")
        # print("DATABASE_URL:", DATABASE_URL)
        stations = fetch_stations(station_type, DATABASE_URL)
        map_sp = create_map(stations, station_type)
        st_folium(map_sp, width=700, height=500)

