
# Home.py
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from streamlit_card import card
from streamlit_folium import st_folium
import folium
import psycopg2
import os

from utils.nav import render_sidebar

st.set_page_config(page_title="iFAST – Sistema de Alertas", layout="wide")

# hide_native_sidebar_nav()          # 1) Oculta menu nativo
render_sidebar()   # 2) Desenha seu submenu

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

# # Submenu lateral (na home não há área ativa)
# render_sidebar(active_area=None)

# st.set_page_config(page_title="Flood Alert System - Map", layout="wide")

# hide_native_sidebar_nav()  # Opção 3 é a mais garantida

# Em seguida, renderize seu submenu customizado
# render_sidebar(active_area="RMSP")

# Display text based on selection
st.title(translations[lang]["title"] + "Floodcasting XAI Alert System")
st.write(translations[lang]["body"])

st.divider()
st.subheader(translations[lang]["subtitle1"])
cols = st.columns(4)
with cols[0]:
    st.page_link("pages/sp_realtime.py", label="RMSP – entrar", icon="🟦")
with cols[1]:
    st.page_link("pages/2_RSRJ__1_Previsao_a_tempo_real.py", label="RSRJ – entrar", icon="🟩")
# with cols[2]:
#     st.page_link("pages/3_PA__1_Previsao_a_tempo_real.py", label="PA – entrar", icon="🟨")
# with cols[3]:
#     st.page_link("pages/4_UY__1_Previsao_a_tempo_real.py", label="UY – entrar", icon="🟧")


col1, col2, col3 = st.columns(3, vertical_alignment="top", border=True)

with col1:
    st.header("São Paulo - Brasil")
    clicked_sp = card(
        title="São Paulo",
        text="Clique para ver detalhes",
        styles={
            "card": {"width": "100%", "height": "260px", "border-radius": "10px"},
            "title": {"font-size": "24px", "font-weight": "700"},
            "text": {"font-size": "14px"}
        }
    )
    if clicked_sp:
        st.session_state["cidade_selecionada"] = "São Paulo"
        st.toast("São Paulo selecionada!")

with col2:
    st.header("Rio de Janeiro - Brasil")
    clicked_rj = card(
        title="Rio de Janeiro",
        text="Clique para ver detalhes",
        styles={
            "card": {"width": "100%", "height": "260px", "border-radius": "10px"},
        }
    )
    if clicked_rj:
        st.session_state["cidade_selecionada"] = "Rio de Janeiro"
        st.toast("Rio de Janeiro selecionado!")

with col3:
    st.header("Paraguai")
    clicked_py = card(
        title="Paraguai\n",
        text="Clique para ver detalhes",
        styles={
            "card": {"width": "100%", "height": "260px", "border-radius": "10px"},
        }
    )
    if clicked_py:
        st.session_state["cidade_selecionada"] = "Paraguai"
        st.toast("Paraguai selecionado!")

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

    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=200)
    logo = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo, width=150)

    station_type = st.selectbox("Select the type of station:", ["Rain", "Level"])

    if station_type:
        DATABASE_URL = os.getenv("DATABASE_URL")
        # print("DATABASE_URL:", DATABASE_URL)
        stations = fetch_stations(station_type, DATABASE_URL)
        map_sp = create_map(stations, station_type)
        st_folium(map_sp, width=700, height=500)