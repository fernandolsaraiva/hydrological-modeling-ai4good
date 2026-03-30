import streamlit as st
from utils.menu import render_menu
from PIL import Image
from utils.translations import translations

render_menu()


translations = {
   "Português": {"title": "Plataforma de Previsão Hidrológica com IA eXplicável", 
                    "body1": "Uma plataforma operacional voltada à previsão hidrológica, utilizando técnicas de Inteligência Artificial eXplicável (XAI) para apoiar a tomada de decisão em cenários críticos.",
                    "body2": "Este projeto é fruto do trabalho direto e indireto de diversas pessoas — desde alunos de graduação até pesquisadores de pós-doutorado, professores e especialistas da área.",
                    "Fernando":"Fernando Saraiva é engenheiro pelo ITA e mestrando em Ciência da Computação (Unifesp), com foco em Machine Learning. Liderou o projeto na iniciativa AI4GOOD da Brazil Conference 2025.",
                    "Luan":"Luan Baraúna é doutor em Computação Aplicada pelo INPE, com formação em Física pela UFBA. Especialista em Inteligência Artificial, desenvolveu modelos baseados em redes neurais para detecção de padrões no espaço de Fourier.",
                    "Leonardo":"Leonardo Santos é Pesquisador Titular em Modelagem Computacional no CEMADEN-MCTI e professor em programas de pós-graduação do INPE e da UNIFESP. Doutor pelo INPE, com formação em Física pela UFBA, atuou também como professor visitante na Universidade Humboldt (Berlim).",
                    "Elton":"Elton Escobar é doutor em Sensoriamento Remoto pelo INPE, com formação em Ciências Ambientais pela UNIFESP e UFSCar. Atua em geoinformática, modelagem hidrodinâmica e sistemas de alerta para alagamentos urbanos, sendo atualmente pesquisador de pós-doutorado no Cemaden.",
                    "Catia":"Cátia Sepetauskas é doutora em Computação Aplicada pelo INPE, com graduação em Ciência da Computação pela UFBA e mestrado na mesma área pela UFRGS.",
                    "leo_role":"Coordenador",
                    "fernando_role":"Idealizador e líder do projeto AI4GOOD",
                    "elton_role":"Especialista em Hidrologia",
                    "luan_role":"Especialista em IA",
                    "catia_role":"Programadora",
                    "equipe_title":"Equipe Principal",
                    "colaboradores_title":"Principais Colaboradores",
                    "financiamento_title":"Financiamento",
                    "financiamento_body":"Agradecemos o financiamento do CNPq (446053/2023-6) e da FAPESP (24/02748-7), no âmbito do projeto iFAST - Ferramentas Inteligentes para Alertas de Enxurradas.",
                    "apresentacao":"Apresentação do projeto na Brazil Conference 2025"
                    },
    "English": {"title": "Operational Platform for Hydrological Forecasting using Explainable AI", 
                "body1": "An operational platform focused on hydrological forecasting, utilizing Explainable Artificial Intelligence (XAI) techniques to support decision-making in critical scenarios.",
                "body2": "This project is the result of direct and indirect work from many people — from undergraduate students to postdoctoral researchers, professors, and experts in the field.",
                "Fernando": "Fernando Saraiva is an engineer from ITA and a master's student in Computer Science (Unifesp), focusing on Machine Learning. He led the project in the AI4GOOD initiative of the Brazil Conference 2025.",
                "Luan": "Luan Baraúna holds a Ph.D. in Applied Computing from INPE, with a background in Physics from UFBA. An expert in Artificial Intelligence, he developed models based on neural networks for pattern detection in Fourier space.",
                "Leonardo": "Leonardo Santos is a Titular Researcher in Computational Modeling at CEMADEN-MCTI and a professor in graduate programs at INPE and UNIFESP. He holds a Ph.D. from INPE, with a background in Physics from UFBA, and also served as a visiting professor at Humboldt University (Berlin).",
                "Elton": "Elton Escobar holds a Ph.D. in Remote Sensing from INPE, with a background in Environmental Sciences from UNIFESP and UFSCar. He works in geoinformatics, hydrodynamic modeling, and alert systems for urban flooding, currently serving as a postdoctoral researcher at Cemaden.",
                "Catia": "Cátia Sepetauskas holds a Ph.D. in Applied Computing from INPE, with a bachelor's degree in Computer Science from UFBA and a master's degree in the same field from UFRGS.",
                "leo_role": "Coordinator",
                "fernando_role": "Project Idealizer and Leader for AI4GOOD",
                "elton_role": "Hydrology Specialist",
                "luan_role": "AI Specialist",
                "catia_role": "Programmer",
                "equipe_title": "Main Team",
                "colaboradores_title": "Main Collaborators",
                "financiamento_title": "Funding",
                "financiamento_body": "We thank the funding from CNPq (446053/2023-6) and FAPESP (24/02748-7), within the scope of the iFAST project - Intelligent Tools for Flash Flood Alerts.",
                "apresentacao": "Project presentation at Brazil Conference 2025"},
    "Español": {"title": "Plataforma Operacional para Previsión Hidrológica usando IA Explicable",
                "body1": "Una plataforma operacional centrada en la previsión hidrológica, utilizando técnicas de Inteligencia Artificial Explicable (XAI) para apoyar la toma de decisiones en escenarios críticos.",
                "body2": "Este proyecto es el resultado del trabajo directo e indirecto de muchas personas — desde estudiantes de pregrado hasta investigadores postdoctorales, profesores y expertos en el campo.",
                "Fernando": "Fernando Saraiva es ingeniero por el ITA y estudiante de maestría en Ciencias de la Computación (Unifesp), con enfoque en Machine Learning. Lideró el proyecto en la iniciativa AI4GOOD de la Brazil Conference 2025.",
                "Luan": "Luan Baraúna tiene un doctorado en Computación Aplicada por INPE, con formación en Física por UFBA. Experto en Inteligencia Artificial, desarrolló modelos basados en redes neuronales para detección de patrones en el espacio de Fourier.",
                "Leonardo": "Leonardo Santos es Investigador Titular en Modelado Computacional en CEMADEN-MCTI y profesor en programas de posgrado en INPE y UNIFESP. Tiene un doctorado por INPE, con formación en Física por UFBA, y también se desempeñó como profesor visitante en la Universidad Humboldt (Berlín).",
                "Elton": "Elton Escobar tiene un doctorado en Sensoriamento Remoto por INPE, con formación en Ciencias Ambientales por UNIFESP y UFSCar. Trabaja en geoinformática, modelado hidrodinámico y sistemas de alerta para inundaciones urbanas, actualmente como investigador postdoctoral en Cemaden.",
                "Catia": "Cátia Sepetauskas tiene un doctorado en Computación Aplicada por INPE, con una licenciatura en Ciencias de la Computación por UFBA y una maestría en la misma área por UFRGS.",
                "leo_role": "Coordinador",
                "fernando_role": "Idealizador y Líder del Proyecto para AI4GOOD",
                "elton_role": "Especialista en Hidrología",
                "luan_role": "Especialista en IA",
                "catia_role": "Programadora",
                "equipe_title": "Equipo Principal",
                "colaboradores_title": "Colaboradores Principales",
                "financiamento_title": "Financiamiento",
                "financiamento_body": "Agradecemos el financiamiento de CNPq (446053/2023-6) y FAPESP (24/02748-7), dentro del ámbito del proyecto iFAST - Herramientas Inteligentes para Alertas de Inundaciones Torrenciales."
    }

}

lang = st.session_state.get("lang", "Português")  # Default to Portuguese if not set

st.set_page_config(
    page_title="Floodcasting XAI Alert System",
    layout="wide",
    initial_sidebar_state="expanded"
)

def member_card(image, name, role, description=None, links=None):
    st.image(image, width=150)
    st.subheader(name)
    st.caption(role)

    if description:
        st.markdown(description)

    if links:
        st.markdown(links)


def main():
    st.set_page_config(layout="wide")

    # =========================
    # HEADER
    # =========================
    st.title("🌊" + translations[lang]["title"])

    st.markdown(translations[lang]["body1"])
    st.markdown(translations[lang]["body2"])

    st.divider()
    
    # =========================
    # EQUIPE PRINCIPAL
    # =========================
    st.header("👥 " + translations[lang]["equipe_title"])

    col1, col2 = st.columns(2, gap="large")

    with col1:
        member_card(
            "img/leonardo_santos.jpeg",
            "Dr. Leonardo B. L. Santos",
            translations[lang]["leo_role"],
            description=translations[lang]["Leonardo"]
        )

    with col2:
        member_card(
            "img/fernando_saraiva.jpeg",
            "Me. Fernando Saraiva Filho",
            translations[lang]["fernando_role"],
            description=translations[lang]["Fernando"],
            links="""
            🔗 [Pré-print](https://eartharxiv.org/repository/view/12016/)  
            🎥 [Apresentação](https://www.youtube.com/watch?v=YpaqKJVqGd8&t=14s)
            """
            )

    # st.markdown("---")

    col3, col4 = st.columns(2, gap="large")

    with col3:
        member_card(
            "img/elton_escobar.jpeg",
            "Dr. Elton Escobar",
            translations[lang]["elton_role"],
            description=translations[lang]["Elton"]
        )

    with col4:
        member_card(
            "img/luan_barauna.jpeg",
            "Dr. Luan Orion Barauna",
            translations[lang]["luan_role"],
            description=translations[lang]["Luan"]
        )

    # st.markdown("---")

    col5, _ = st.columns(2, gap="large")

    with col5:
        member_card(
            "img/catia.jpg",
            "Dra. Cátia S. do N. Sepetauskas",
            translations[lang]["catia_role"],
            description=translations[lang]["Catia"]
        )

    st.divider()
    
    # =========================
    # COLABORADORES
    # =========================
    st.header("🤝 " + translations[lang]["colaboradores_title"])

    st.markdown("""
    - (Voluntários da Brazil Conference)
    """)

    st.divider()

    # =========================
    # FINANCIAMENTO
    # =========================
    st.header("💰 " + translations[lang]["financiamento_title"])

    st.info(translations[lang]["financiamento_body"])

if __name__ == "__main__":
    main()