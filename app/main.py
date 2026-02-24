import streamlit as st

st.set_page_config(
    page_title="UTM Genie",
    page_icon="🧙",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.switch_page("pages/1_generator_UTM.py")
