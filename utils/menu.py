import streamlit as st
from PIL import Image

def render_menu():

    st.sidebar.page_link("Home.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/about.py", label="About us", icon="ℹ️")

    with st.sidebar.expander("São Paulo"):
        st.page_link("pages/sp_realtime.py", label="Previsão tempo real")
        st.page_link("pages/sp_history.py", label="Previsões passadas")
        st.page_link("pages/sp_about.py", label="Sobre o Projeto")

    with st.sidebar.expander("Rio de Janeiro"):
        st.page_link("pages/rj_realtime.py", label="Previsão tempo real")
        st.page_link("pages/rj_history.py", label="Previsões passadas")
        st.page_link("pages/rj_about.py", label="Sobre o Projeto")

    with st.sidebar.expander("Paraguai"):
        st.page_link("pages/py_realtime.py", label="Previsão tempo real")
        st.page_link("pages/py_history.py", label="Previsões passadas")
        st.page_link("pages/py_about.py", label="Sobre o Projeto")

    with st.sidebar.expander("Uruguai"):
        st.page_link("pages/uy_realtime.py", label="Previsão tempo real")
        st.page_link("pages/uy_history.py", label="Previsões passadas")
        st.page_link("pages/uy_about.py", label="Sobre o Projeto")

    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=300)
    # logo = Image.open("img/logo_ai4good.png")
    # st.sidebar.image(logo, width=250)


