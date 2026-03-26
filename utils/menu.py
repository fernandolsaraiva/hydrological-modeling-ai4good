import streamlit as st
from PIL import Image
from utils.translations import translations

def render_menu():
    # ==========================
    # Inicializa idioma
    # ==========================
    if "lang" not in st.session_state:
        st.session_state.lang = "Português"

    t = translations[st.session_state.lang]

    # ==========================
    # LOGO NO TOPO
    # ==========================
    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=250)
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)  # pequeno espaçamento

    # ==========================
    # SELECTBOX DE IDIOMA
    # ==========================
    lang = st.sidebar.selectbox(
        "🌐 " + t.get("language_label", "Idioma(Language)"),
        ["Português", "English", "Español"],
        index=["Português", "English", "Español"].index(st.session_state.lang),
        key="language_select"
    )

    if st.session_state.lang != lang:
        st.session_state.lang = lang
        t = translations[lang]  # atualiza traduções imediatamente

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)  # linha separadora

    # ==========================
    # MENU PRINCIPAL
    # ==========================
    st.sidebar.page_link("Home.py", label=t["home"], icon="🏠")

    # Expander por cidade
    for city_key in ["sp", "rj", "py", "uy"]:
        with st.sidebar.expander(t[city_key]):
            st.page_link(f"pages/{city_key}_realtime.py", label=t["realtime"])
            st.page_link(f"pages/{city_key}_history.py", label=t["history"])
            st.page_link(f"pages/{city_key}_about.py", label=t["about_project"])

    st.sidebar.page_link("pages/about.py", label=t["about"], icon="ℹ️")

    # ==========================
    # CSS PARA ESTILIZAÇÃO
    # ==========================
    st.sidebar.markdown(
        """
        <style>
        /* Expander com fundo leve, borda arredondada e padding */
        div[data-testid="stSidebar"] .st-expander {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 5px;
        }
        /* Hover suave */
        div[data-testid="stSidebar"] .st-expander:hover {
            background-color: #e6e8ed;
        }
        /* Linha divisória */
        div[data-testid="stSidebar"] hr {
            border-top: 1px solid #c0c0c0;
            margin: 10px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )