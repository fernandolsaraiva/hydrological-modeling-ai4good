
# utils/nav.py
import streamlit as st
from PIL import Image

HIDE_NATIVE_PAGES_MENU = True  # pode deixar True/False para testar rapidamente

def hide_native_sidebar_nav():
    """
    Esconde o menu nativo de páginas do Streamlit, SEM .streamlit/config.
    Combina CSS imediato + MutationObserver para lidar com carregamento tardio
    e mudanças de seletor entre versões do Streamlit.
    """
    st.markdown(
        """
        <style>
        /* Esconde a navegação nativa se ela já estiver no DOM */
        [data-testid="stSidebar"] nav,
        [data-testid="stSidebar"] section[data-testid="stSidebarNav"],
        [data-testid="stSidebar"] section[data-testid="stSidebarNavItems"],
        section[data-testid="stSidebarNav"],
        section[data-testid="stSidebarNavItems"] {
            display: none !important;
        }

        /* Se por acaso existir uma UL/OL dentro do bloco de navegação nativa */
        [data-testid="stSidebar"] nav ul,
        [data-testid="stSidebar"] nav ol {
            display: none !important;
        }
        </style>
        <script>
        // Esconde qualquer nav nativa na sidebar assim que aparecer
        (function() {
          const attemptHide = () => {
            const sidebar = parent.document.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;

            const selectors = [
              'nav',
              'section[data-testid="stSidebarNav"]',
              'section[data-testid="stSidebarNavItems"]',
              'div[data-testid="stSidebarNav"]',
              'div[data-testid="stSidebarNavItems"]'
            ];

            const hideAll = () => {
              selectors.forEach(sel => {
                sidebar.querySelectorAll(sel).forEach(el => { el.style.display = 'none'; });
              });
            };

            hideAll();
            // Observa alterações futuras (ex.: quando o Streamlit remonta a sidebar)
            const obs = new MutationObserver(() => hideAll());
            obs.observe(sidebar, { childList: true, subtree: true });
          };

          // Tenta algumas vezes para cobrir diferentes tempos de render
          const start = () => { try { attemptHide(); } catch (e) {} };
          setTimeout(start, 0);
          setTimeout(start, 120);
          setTimeout(start, 300);
          setTimeout(start, 600);
          setTimeout(start, 1000);
        })();
        </script>
        """,
        unsafe_allow_html=True
    )

def render_sidebar(active_area: str | None = None):
    """
    Desenha o submenu customizado com expansores por área.
    active_area: "RMSP", "RSRJ", "PA", "UY" ou None
    """
    # 🔴 NÃO envolver hide_native_sidebar_nav() em st.sidebar.*; precisa estar no "corpo" (já foi chamado no arquivo da página)
    # Aqui, por segurança, aplicamos novamente caso a página chame só render_sidebar().
    if HIDE_NATIVE_PAGES_MENU:
        hide_native_sidebar_nav()

    # Logos (opcional)
    try:
        logo_ifast = Image.open("img/logo_ifast.png")
        st.sidebar.image(logo_ifast, width=160)
    except Exception:
        pass
    try:
        logo_ai4g = Image.open("img/logo_ai4good.png")
        st.sidebar.image(logo_ai4g, width=120)
    except Exception:
        pass

    st.sidebar.markdown("### Navegação")

    # Link global (ajuste para o arquivo real)
    st.sidebar.page_link("pages/7_About_Us.py", label="ℹ️ Sobre o projeto")

    # Estrutura das áreas
    AREAS = {
        "RMSP": {
            "emoji": "🟦",
            "tempo_real": "pages/1_RMSP__1_Previsao_a_tempo_real.py",
            "passadas":   "pages/1_RMSP__2_PrevISOES_passadas.py",
        },
        "RSRJ": {
            "emoji": "🟩",
            "tempo_real": "pages/2_RSRJ__1_Previsao_a_tempo_real.py",
            "passadas":   "pages/2_RSRJ__2_PrevISOES_passadas.py",
        },
        # Ative quando quiser
        # "PA": {
        #     "emoji": "🟨",
        #     "tempo_real": "pages/3_PA__1_Previsao_a_tempo_real.py",
        #     "passadas":   "pages/3_PA__2_PrevISOES_passadas.py",
        # },
        # "UY": {
        #     "emoji": "🟧",
        #     "tempo_real": "pages/4_UY__1_Previsao_a_tempo_real.py",
        #     "passadas":   "pages/4_UY__2_PrevISOES_passadas.py",
        # },
    }

    for area, info in AREAS.items():
        marker = " 🔹" if active_area == area else ""
        with st.sidebar.expander(f"{info['emoji']} {area}{marker}", expanded=(active_area == area)):
            st.page_link(info["tempo_real"], label="Previsão a tempo real", icon="🌧️")
            st.page_link(info["passadas"],   label="Previsões passadas",   icon="🕒")

    st.sidebar.markdown("---")
    # Ajuste para o entrypoint real do seu app (Home.py ou app.py)
    st.sidebar.page_link("Home.py", label="🏠 Página inicial")
