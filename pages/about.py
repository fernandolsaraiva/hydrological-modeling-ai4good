import streamlit as st
from utils.menu import render_menu
from PIL import Image

render_menu()

# Language selection
lang = st.sidebar.selectbox("Language", ["Portuguese", "English"])

translations = {
   "Portuguese": {"title": "Sobre Nós", 
                    "body1": "Nosso projeto apresenta a primeira ferramenta operacional para previsão de alagamentos urbanos utilizando Inteligência Artificial explicável. Utilizamos exclusivamente ferramentas open source, com execução em tempo real, uma interface amigável e uma abordagem escalável.",
                    "body2": "Contamos com o apoio da Conferência AI4Good Brasil para impulsionar nossa plataforma e ampliar cada vez mais o nosso impacto.",
                    "teamtext": "Conheça nossa equipe",
                    "Fernando":"Fernando Saraiva possui graduação em Engenharia Eletrônica pelo Instituto Tecnológico de Aeronáutica (ITA) e está cursando mestrado em Ciência da Computação com foco em Aprendizado de Máquina na Universidade Federal de São Paulo (Unifesp). Ele atua como cientista de dados, especializado em aplicações de inteligência artificial em energia renovável.",
                    "Luan":"Luan Baraúna possui graduação e mestrado em Física pela Universidade Federal da Bahia (UFBA) e doutorado em Computação Aplicada pelo Instituto Nacional de Pesquisas Espaciais (INPE), onde se especializou em Inteligência Artificial (IA), desenvolvendo uma rede neural para detecção de padrões no espaço de Fourier.",
                    "Leonardo":"Leonardo Santos é Pesquisador Titular em Modelagem Computacional no CEMADEN-MCTI, professor permanente do Programa de Pós-Graduação em Computação Aplicada do INPE e professor colaborador do Programa de Pós-Graduação em Ciência da Computação da UNIFESP. Santos possui graduação em Física pela UFBA, mestrado e doutorado pelo INPE, e foi Professor Visitante no Departamento de Física da Universidade Humboldt (Berlim).",
                    "Elton":"Elton Escobar holds a Bachelor’s degree in Environmental Science from the Federal University of São Paulo (UNIFESP), a Master’s degree in Environmental Science from the Federal University of São Carlos (UFSCar), and a Ph.D. in Remote Sensing from the National Institute for Space Research (INPE). He works in the fields of geoinformatics, remote sensing, urban planning, hydrodynamic modeling, urban flooding, flood early warning systems (FEWS), and climate change and water security. Currently, he is a postdoctoral researcher at Cemaden."},
    "English": {"title": "About Us", 
                "body1": "Our project presents the first operational tool for predicting urban floods using explainable Artificial Intelligence. We exclusively use open-source tools, with real-time execution, a user-friendly interface, and a scalable approach.",
                "body2": "We count on the support of the AI4Good Brazil Conference to boost our platform and help us helping more and more people.",
                "teamtext": "Meet Our Team",
                "Fernando": "Fernando Saraiva holds a Bachelor's degree in Electronic Engineering from the Aeronautics Institute of Technology (ITA) and is pursuing a Master's degree in Computer Science with a focus on Machine Learning at the Federal University of São Paulo (Unifesp). He works as a data scientist specializing in artificial intelligence applications in renewable energy.",
                "Luan": "Luan Baraúna holds a Bachelor's and Master's in Physics from the Federal University of Bahia (UFBA), and a Ph.D. in Applied Computing from the National Institute for Space Research (INPE), where he specialized in Artificial Intelligence (AI), developing a neural network for detecting patterns in the Fourier space.",
                "Leonardo": "Leonardo Santos is a Titular Researcher in Computational Modeling at CEMADEN-MCTI, a permanent professor in INPE's Applied Computing Graduate Program, and a collaborating professor in UNIFESP's Computer Science Graduate Program. Santos has a bachelor's in Physics from UFBA, a master's and PhD from INPE, and was a Visiting Professor at the Physics department at Humboldt University (Berlin).",
                "Elton": "Elton Escobar possui graduação em Ciências Ambientais pela Universidade Federal de São Paulo (UNIFESP), mestrado em Ciências Ambientais pela Universidade Federal de São Carlos (UFSCar) e doutorado em Sensoriamento Remoto pelo Instituto Nacional de Pesquisas Espaciais (INPE). Atua nas áreas de geoinformática, sensoriamento remoto, planejamento urbano, modelagem hidrodinâmica, alagamentos urbanos, sistemas de alerta precoce de cheias (FEWS) e mudanças climáticas e segurança hídrica. Atualmente, é pesquisador de pós-doutorado no Cemaden."}
}

st.set_page_config(
    page_title="Floodcasting XAI Alert System",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title(translations[lang]["title"])
    st.write(translations[lang]["body1"])
    st.write(translations[lang]["body2"])

    st.write("### " + translations[lang]["teamtext"])
    
    col1, col2, col3 = st.columns(3)
    
    def resize_image(image_path, size):
        img = Image.open(image_path)
        resized_img = img.resize(size)
        return resized_img
    
    size = (200, 200)  # Define the size (width, height)
    
    with col1:
        img1 = "img/fernando_saraiva.png"
        st.image(img1, caption=translations[lang]["Fernando"],width=240)

        img4 = "img/elton_escobar.jpeg"
        st.image(img4, caption=translations[lang]["Elton"],width=240)
    
    with col2:
        img2 = "img/luan_barauna.jpeg"
        st.image(img2, caption=translations[lang]["Luan"],width=280)
    
    with col3:
        img3 = "img/leonardo_santos.jpeg"
        st.image(img3, caption=translations[lang]["Leonardo"],width=250)



if __name__ == "__main__":
    main()