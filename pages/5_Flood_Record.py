#%% import
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import timedelta
from PIL import Image

#%% Conexão
if __name__ == "__main__":

    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=200)
    logo = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo, width=150)
    st.title('Flood Record')

    def get_stations_record(start_date, end_date): #Retirar daqui e colocar em util depois
        
        file = "stations_record.xlsx" #Substituir pela conexão ao banco posteriormente
        file_dict = pd.read_excel(file,sheet_name=None)
        compiled = {sheet:pd.DataFrame(data) for sheet,data in file_dict.items()}

        df = pd.concat(compiled,ignore_index=True)

        df["CONDICAO"] = df["CONDICAO"].astype(str)
        df["DATA"] = pd.to_datetime(df["DATA"]).dt.date

        def text_cleaning(condicao):  #Tratamento de texto para Transitável ou Intransitável, qnd tiver o banco fazer em sql
            if "INTRA" in condicao.upper():
                return "Intransitável"
            elif "TRAN" in condicao.upper():
                return "Transitável"
            else:
                return "Condicao Desconhecida"
            
        df["CONDICAO"] = df["CONDICAO"].apply(text_cleaning)

        df_plot = df[(df["DATA"]>=start_date) & (df["DATA"]<=end_date)]
        return df_plot

    #%% Streamlit
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('Start Date',value=pd.to_datetime('today').date() - timedelta(days=7))
    with col2:
        end_date = st.date_input('End Date',value=pd.to_datetime('today').date())
        end_date = end_date + timedelta(days=1)

    # %% Mapa
    if st.button('Plot'):
        df = get_stations_record(start_date, end_date)

        fig = px.scatter_map(
            df,
            lat = "lat",
            lon = "long",
            text = "CONDICAO",
            color = "CONDICAO",
            color_discrete_map = {"Intransitável":"red","Transitável":"blue","Condicao Desconhecida":"grey"},
            title = f"Flood Record from {start_date} to {end_date}"
        )

        st.plotly_chart(fig)

