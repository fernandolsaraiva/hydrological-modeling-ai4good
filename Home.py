import folium
import streamlit as st
from PIL import Image
from streamlit_folium import st_folium
import psycopg2
import os 

st.set_page_config(page_title="Flood Alert System - Map", layout="wide")

st.title("Welcome to the Floodcasting XAI Alert System")
st.write("Use the tabs on the left to navigate through the different sections of the dashboard.")

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
    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=200)
    logo = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo, width=150)

    station_type = st.selectbox("Select the type of station:", ["Rain", "Level"])

    if station_type:
        DATABASE_URL = os.getenv("DATABASE_URL")
        stations = fetch_stations(station_type, DATABASE_URL)
        map_sp = create_map(stations, station_type)
        st_folium(map_sp, width=700, height=500)