import streamlit as st
from utils.menu import render_menu

render_menu()

translations = {
    "Português": {
        "title": "Plataforma de Monitoramento e Visualização dos Rios MORIS",
        "body1": (
            "A Aplicação de Monitoramento e Alerta de Inundações constitui uma plataforma web "
            "concebida para a visualização de dados hidrológicos provenientes de sensores "
            "localizados no rio Yí."
        ),
        "body2": (
            "Esta ferramenta permite a realização de previsões do nível do rio e a gestão dos "
            "dados coletados pelos sensores em tempo real. As funcionalidades chave da plataforma "
            "compreendem: 1. Monitoramento em Tempo Real, 2. Modelagem e Previsão, "
            "3. Gestão de Dados Históricos, 4. Sistema de Alertas. Finalmente, a plataforma "
            "contribui significativamente para a melhoria da gestão do recurso hídrico, permitindo "
            "não só a mitigação de riscos, mas também um planejamento superior do uso da água."
        ),
        "link_label": "Link para plataforma original",
        "link": "Link para configuração da plataforma original"
    },
    "English": {
        "title": "MORIS River Monitoring and Visualization Platform",
        "body1": (
            "The Flood Monitoring and Alert Application is a web platform designed for visualizing "
            "hydrological data from sensors located in the Yí River."
        ),
        "body2": (
            "This tool enables river level forecasting and real-time management of sensor data. "
            "The key features include: 1. Real-time monitoring, 2. Modeling and forecasting, "
            "3. Historical data management, 4. Alert system. Overall, the platform significantly "
            "improves water resource management, enabling both risk mitigation and better planning "
            "of water use under normal conditions."
        ),
        "link_label": "Original platform link",
        "link": "Link to the original platform setup"
    },
    "Español": {
        "title": "Plataforma de Monitoreo y Visualización de los Ríos MORIS",
        "body1": (
            "La Aplicación de Monitoreo y Alerta de Inundaciones es una plataforma web diseñada "
            "para visualizar datos hidrológicos provenientes de sensores ubicados en el río Yí."
        ),
        "body2": (
            "Esta herramienta permite realizar pronósticos del nivel del río y gestionar los datos "
            "recopilados por los sensores en tiempo real. Las características clave incluyen: 1. "
            "Monitoreo en tiempo real, 2. Modelado y pronóstico, 3. Gestión de datos históricos, "
            "4. Sistema de alertas. En general, la plataforma mejora significativamente la gestión "
            "de los recursos hídricos, permitiendo tanto la mitigación de riesgos como una mejor "
            "planificación del uso del agua en condiciones normales."
        ),
        "link_label": "Enlace a la plataforma original",
        "link": "Link para la configuración de la plataforma original"
    }
}

lang = st.session_state.get("lang", "Português")  # Default to Portuguese if not set
t = translations[lang]

st.title(t["title"])
st.write(t["body1"])
st.write(t["body2"])

st.markdown("---")

# if t["link"]:
#     st.markdown(f"🔗 [{t['link_label']}]({t['link']})")
# else:
    # st.markdown("🔗 **Link para plataforma original:** https://drive.google.com/drive/folders/1ooidwueE6fabWDCi7B_V52saJSesMMmK?usp=drive_link")

# link externo (Streamlit + URL correta)

st.markdown(
    f"🔗 [{translations[lang]['link']}]({ 'https://drive.google.com/drive/folders/1ooidwueE6fabWDCi7B_V52saJSesMMmK?usp=drive_link' })"
)