import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import os
import json
import folium
from streamlit_folium import st_folium
import psycopg2

def fetch_stations_as_json(db_url):
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    query = "SELECT name, lat, long FROM station.station_plu;"
    cursor.execute(query)
    stations = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Format stations data with labeled properties
    formatted_stations = [
        {
            "name": station[0],
            "latitude": float(station[1]),
            "longitude": float(station[2])
        }
        for station in stations
    ]
    
    return formatted_stations

def main():
    # Set page title and logos
    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=200)
    logo = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo, width=150)
    
    st.title('3D Map Visualization')
    
    # Description of the 3D map functionality
    st.write("""
    This 3D map visualization allows you to explore the monitoring stations and waterways in a three-dimensional environment. 
    You can navigate between stations, view elevation profiles, and analyze the terrain around monitoring points.
    
    Features:
    - 3D terrain visualization with elevation data
    - Interactive navigation between monitoring stations
    - Elevation profile analysis along waterways
    - Station information and details
    """)
    
    # Create a container for the map
    map_container = st.container()
    
    # Database URL for station data
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Get station data from database
    json_stations = fetch_stations_as_json(DATABASE_URL)    
    
    with map_container:
        # Get the absolute path to the arcgis_map directory
        arcgis_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'arcgis_map')
        
        # Load and inject the required CSS
        with open(os.path.join(arcgis_path, 'style.css'), 'r') as css_file:
            css = f'<style>{css_file.read()}</style>'
        
        # Load and inject the HTML content
        html_content = f"""
        <script type="module" src="https://js.arcgis.com/calcite-components/1.9.2/calcite.esm.js"></script>
        <script nomodule="" src="https://js.arcgis.com/calcite-components/1.9.2/calcite.js"></script>
        <link rel="stylesheet" type="text/css" href="https://js.arcgis.com/calcite-components/1.9.2/calcite.css" />
        <link rel="stylesheet" href="https://js.arcgis.com/4.29/esri/themes/light/main.css">
        <script src="https://js.arcgis.com/4.29/"></script>
        {css}
        <script>
            window.stations_data = {json_stations};
        </script>
        <div id="viewDiv"></div>
        """
        
        # Load and inject the JavaScript
        with open(os.path.join(arcgis_path, 'main.js'), 'r') as js_file:
            js = f'<script>{js_file.read()}</script>'
        
        # Combine all components and display
        components.html(
            f"{html_content}{js}",
            height=800,  # Adjust height as needed
            scrolling=False
        )
        
        # Add usage instructions
        st.write("""
        ### How to Use the 3D Map
        
        1. Use mouse controls to navigate:
           - Left click and drag to rotate
           - Right click and drag to pan
           - Scroll wheel to zoom
        
        2. Use the station list (bottom right) to:
           - View all monitoring stations
           - Click on a station to navigate to it
           - See station details and elevation
        
        3. Use the navigation buttons (bottom left) to:
           - Move between stations
           - Return to overview
        
        4. View elevation profiles of waterways near stations
        """)

if __name__ == "__main__":
    main()