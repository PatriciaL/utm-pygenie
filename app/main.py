import streamlit as st

st.set_page_config(
    page_title="UTM Genie",
    page_icon="🧙",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── Navegación explícita ──────────────────────────────────
# Para ocultar una página sin borrarla, coméntala o elimínala de esta lista

pages = st.navigation([
    st.Page("pages/1_generator_UTM.py",                    title="Generar",   icon=":material/link:"),
    st.Page("pages/2_validator_utm.py",                    title="Validar",   icon=":material/check_circle:"),
    st.Page("pages/3_final_naming_convention_constructor.py", title="Naming", icon=":material/tune:"),
    # st.Page("pages/4_Chatbot.py",                        title="Asistente", icon=":material/smart_toy:"),  # oculto
    st.Page("pages/5_opinion.py",                          title="Feedback",  icon=":material/rate_review:"),
    st.Page("pages/6_About.py",                            title="Acerca de", icon=":material/info:"),
])

pages.run()
