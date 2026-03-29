# utils/nav.py

import streamlit as st
from PIL import Image

def render_sidebar():

    try:
        logo_ifast = Image.open("img/logo_ifast.png")
        st.sidebar.image(logo_ifast, width=160)
    except:
        pass

    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Go to",
        [
            "Home",
            "About Us",
            "SP",
            "RJ"
        ]
    )

    if page == "SP":
        subpage = st.sidebar.radio(
            "São Paulo",
            [
                "Previsão tempo real",
                "Previsões passadas"
            ]
        )
        return page, subpage

    if page == "RJ":
        subpage = st.sidebar.radio(
            "Rio de Janeiro",
            [
                "Previsão tempo real",
                "Previsões passadas"
            ]
        )
        return page, subpage

    return page, None