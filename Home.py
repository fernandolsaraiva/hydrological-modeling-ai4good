import streamlit as st
from utils.menu import render_menu
from PIL import Image
from dotenv import load_dotenv
from streamlit_card import card
from streamlit_folium import st_folium
import folium
import psycopg2
import os
from utils.translations import translations

st.set_page_config(
    page_title="Floodcasting XAI Alert System",
    layout="wide",
    initial_sidebar_state="expanded"
)
render_menu()

translations2 = {
   "Português": {"title": "Bem-vindo ao ", 
                    "body": "Use as abas à esquerda ou os cards abaixo para selecionar a região de interesse e visualizar as previsões correspondentes.",
                    "subtitle1":"Selecione a Região de interesse"
   },
    "English": {"title": "Welcome to the ", 
                "body": "Use the tabs on the left or the cards below to select the region of interest and view the corresponding forecasts.",
                "subtitle1": "Select the Region of Interest"
    },
    "Español": {"title": "Bienvenido al ", 
                "body": "Use las pestañas de la izquierda o las tarjetas de abajo para seleccionar la región de interés y ver las predicciones correspondientes.",
                "subtitle1": "Seleccione la Región de interés"
    }
}

lang = st.session_state.get("lang", "Português")  # Default to Portuguese if not set

# Display text based on selection
st.title(translations2[lang]["title"] + "Floodcasting XAI Alert System")
st.write(translations2[lang]["body"])

st.divider()
st.subheader(translations2[lang]["subtitle1"])

cards_data = [
    {
        "title": "São Paulo",
        "page": "pages/sp_realtime.py",
        "img": "https://drive.google.com/thumbnail?id=1l7MHwN6cAea-SiCy-L92xYFWViav6adE&sz=w2000"
    },
    {
        "title": "Nova Friburgo",
        "page": "pages/nf_realtime.py",
        "img": "https://drive.google.com/thumbnail?id=1w03b1YyuguwZGAvyGsLcvgiObR0pKxyi&sz=w2000"
    },
    {
        "title": "Paraguai",
        "page": "pages/py_realtime.py",
        "img": "https://drive.google.com/thumbnail?id=1XWgu1gLrmTHKL7TLLrhZtkcBl4_ZUWWe&sz=w2000"
    },
    {
        "title": "Uruguai",
        "page": "pages/uy_realtime.py",
        "img": "https://drive.google.com/thumbnail?id=14Z3deszPh7YhRZib5P-zllCHNLpM02Ae&sz=w2000"
    },
]

cols = st.columns(2, gap="xsmall")

for i, data in enumerate(cards_data):
    col = cols[i % 2]
    with col:
        # streamlit-card precisa de URL, então usamos o caminho da pasta 'static'
        # no navegador, fica tipo http://localhost:8501/static/sp.jpg
        # img_url = data["img"]
        clicked = card(
            title=data["title"],
            text="",
            image=data["img"],
            styles={
                "card": {
                    "width": "100%",
                    "height": "220px",
                    "border-radius": "15px",
                    "box-shadow": "0 4px 8px rgba(0,0,0,0.3)",
                    "margin": "0px",
                    "padding": "0px",
                    "background-size": "cover",
                    "background-position": "center"
                },
                "title": {
                    "color": "white",
                    "font-size": "28px",
                    "font-weight": "bold",
                    "text-align": "center"
                }
            }
        )
        if clicked:
            st.switch_page(data["page"])

    if i % 2 == 1:
        st.markdown("<br>", unsafe_allow_html=True)

if __name__ == "__main__":
    load_dotenv()

    # station_type = st.selectbox("Select the type of station:", ["Rain", "Level"])

    # if station_type:
    #     DATABASE_URL = os.getenv("DATABASE_URL")
    #     # print("DATABASE_URL:", DATABASE_URL)
    #     stations = fetch_stations(station_type, DATABASE_URL)
    #     map_sp = create_map(stations, station_type)
    #     st_folium(map_sp, width=700, height=500)
