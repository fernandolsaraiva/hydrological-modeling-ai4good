import streamlit as st
from utils.menu import render_menu

render_menu()

translations = {
    "Português": {
        "title": "Plataforma de Monitoramento e Visualização do Córrego Mburicaó",
        "body1": (
            "A equipe paraguaia, liderada pela Universidad Nacional de Asunción (UNA), "
            "concentra seus esforços na Bacia do Córrego Mburicaó, em Assunção, uma área "
            "densamente urbanizada e suscetível a enxurradas de rápida resposta."
        ),
        "body2": (
            "Atualmente, o monitoramento operacional na bacia conta com um sensor de nível "
            "tipo radar de 80 GHz (modelo SZY-801-80G-ABS), que fornece medições de altíssima "
            "precisão (±1mm) em tempo real via rede GSM, servindo como base para os modelos de "
            "previsão baseados em Inteligência Artificial. Como próximo passo, ampliaremos a rede "
            "observacional com a instalação de novos sensores de chuva distribuídos estrategicamente."
        ),
        "link_label": "Link para plataforma original"
    },
    "English": {
        "title": "Mburicaó Stream Monitoring and Visualization Platform",
        "body1": (
            "The Paraguayan team, led by the National University of Asunción (UNA), focuses "
            "its efforts on the Mburicaó Stream Basin in Asunción, a densely urbanized area "
            "susceptible to flash floods."
        ),
        "body2": (
            "Currently, the basin monitoring system includes an 80 GHz radar water level sensor "
            "(model SZY-801-80G-ABS), providing high-precision (±1mm) real-time measurements via GSM "
            "network, serving as the basis for AI-based forecasting models. Next, the observational "
            "network will be expanded with additional high-precision rain gauges."
        ),
        "link_label": "Original platform link"
    },
    "Español": {
        "title": "Plataforma de Monitoramiento y Visualización del Arroyo Mburicaó",
        "body1": (
            "El equipo paraguayo, liderado por la Universidad Nacional de Asunción (UNA), se enfoca "
            "en la Cuenca del Arroyo Mburicaó en Asunción, una área densamente urbanizada "
            "suscrita a inundaciones repentinas."
        ),
        "body2": (
            "Actualmente, el sistema de monitoreo de la cuenca incluye un sensor de nivel de agua "
            "de radar de 80 GHz (modelo SZY-801-80G-ABS), que proporciona mediciones de alta "
            "precisión (±1mm) en tiempo real a través de la red GSM, sirviendo como base para "
            "modelos de pronóstico basados en inteligencia artificial. En el futuro, se expandirá "
            "la red observacional con la instalación de nuevos pluviómetros de alta precisión."
        ),
        "link_label": "Enlace a la plataforma original"
    }
}

lang = st.session_state.get("lang", "Português")  # Default to Portuguese if not set

# conteúdo
st.title(translations[lang]["title"])
st.write(translations[lang]["body1"])
st.write(translations[lang]["body2"])

st.markdown("---")

# link externo (Streamlit + URL correta)
st.markdown(
    f"🔗 [{translations[lang]['link_label']}]({ 'http://mburicaocastai.github.io/v1' })"
)