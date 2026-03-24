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
render_menu()

# Define translations
translations = {
   "Portuguese": {"title": "Bem-vindo ao ", 
                    "body": "Use as abas à esquerda ou os cards abaixo para selecionar a região de interesse e visualizar as previsões correspondentes.",
                    "subtitle1":"Selecione a Região de interesse"},
   "English": {"title": "Welcome to the ", 
                "body": "Use the tabs on the left or the cards below to select the region of interest and view the corresponding forecasts.",
                "subtitle1": "Selecione a Região de interesse"},
}
# Language selection
lang = st.sidebar.selectbox("Language", ["Portuguese", "English"])

# Display text based on selection
st.title(translations[lang]["title"] + "Floodcasting XAI Alert System")
st.write(translations[lang]["body"])

st.divider()
st.subheader(translations[lang]["subtitle1"])

cards_data = [
    {"title": "São Paulo", "page": "pages/sp_realtime.py", "img": "https://img.freepik.com/fotos-premium/ponte-de-cabo-em-uma-paisagem-urbana-em-sao-paulo-brasil_1153727-876.jpg?semt=ais_hybrid&w=740&q=80"},
    {"title": "Rio de Janeiro", "page": "pages/rj_realtime.py", "img": "https://media.istockphoto.com/id/608540602/photo/aerial-panorama-of-botafogo-bay-rio-de-janeiro.jpg?s=612x612&w=0&k=20&c=9vsK_9r4ldoLyfS6oLnUbvpQOgYCfzr4xCZ1-YFNJZo="},
    {"title": "Paraguai", "page": "pages/py_realtime.py", "img": "https://media.istockphoto.com/id/525336822/photo/presidential-palace-in-asuncion-paraguay.jpg?s=612x612&w=0&k=20&c=lZ80xPsCwmBdfRB_iG_U4kSiyhK-BY7Lji_YzfsupOA="},
    {"title": "Uruguai", "page": "pages/uy_realtime.py", "img": "https://media.istockphoto.com/id/1295557985/photo/artigas-mausoleum-and-salvo-palace-in-montevideo-uruguay.jpg?s=612x612&w=0&k=20&c=LyPOLUtgtY-cvT29TL2DErrf5Vvhp8W0IrGHvo6pVu4="},
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