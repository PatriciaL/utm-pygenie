import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Naming Builder", layout="wide")
st.title("🧱 Naming Convention UTM")

# ---------- helpers ----------
def init_sec(key, defaults):
    if key not in st.session_state:
        st.session_state[key] = defaults.copy()
    if f"vals_{key}" not in st.session_state:
        st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    if f"txt_{key}" not in st.session_state:
        st.session_state[f"txt_{key}"] = ""          # input persistente
    if f"sel_{key}" not in st.session_state:
        st.session_state[f"sel_{key}"] = defaults[0]

def reset_sec(key, defaults):
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    st.session_state[f"sel_{key}"]  = defaults[0]
    st.session_state[f"txt_{key}"]  = ""

def add_callback(sec_key):
    blk = st.session_state[f"sel_{sec_key}"]
    txt = st.session_state[f"txt_{sec_key}"]
    if txt.strip():
        nuevos = [v.strip() for v in txt.split(",") if v.strip()]
        st.session_state[f"vals_{sec_key}"][blk].extend(nuevos)
    st.session_state[f"txt_{sec_key}"] = ""  # limpia input

def section(title, sec_key, defaults):
    init_sec(sec_key, defaults)

    st.subheader(title)
    st.session_state[sec_key] = sort_items(
        st.session_state[sec_key],
        direction="horizontal",
        key=f"sortable_{sec_key}"
    ) or st.session_state[sec_key]

    if st.button("Reset", key=f"reset_{sec_key}"):
        reset_sec(sec_key, defaults)

    st.write("Orden:", st.session_state[sec_key])

    # ---------- Formulario estable ----------
    st.selectbox(
        "Bloque destino",
        st.session_state[sec_key],
        key=f"sel_{sec_key}")
    st.text_input(
        "Valores (coma separada)",
        key=f"txt_{sec_key}",
        placeholder="rojo, azul, verde")
    st.button(
        "➕ Agregar",
        key=f"add_{sec_key}",
        on_click=add_callback,
        kwargs=dict(sec_key=sec_key)
    )

    with st.expander("Ver valores guardados"):
        st.json(st.session_state[f"vals_{sec_key}"])

# ---------- secciones ----------
section("utm_campaign", "campaign",
        ["producto","pais","fecha","audiencia"])
section("utm_source", "source",
        ["google","facebook","instagram","newsletter","linkedin"])
section("utm_medium", "medium",
        ["organic","cpc","email","referral","social"])
section("utm_content", "content",
        ["color","version","posicion"])
section("utm_term", "term",
        ["keyword","matchtype"])

# ---------- export ----------
def build_sheet():
    cols={}
    for sec in ["campaign","source","medium","content","term"]:
        col=[]
        for blk in st.session_state[sec]:
            col += [blk]+st.session_state[f"vals_{sec}"][blk]+[""]
        cols[sec]=col
    m=max(len(v) for v in cols.values())
    for k,v in cols.items(): v.extend([""]*(m-len(v)))
    return pd.DataFrame(cols)

if st.button("Exportar Excel"):
    df1 = pd.DataFrame([{
        "utm_campaign": "_".join(st.session_state["campaign"]),
        "utm_source"  : "_".join(st.session_state["source"]),
        "utm_medium"  : "_".join(st.session_state["medium"]),
        "utm_content" : "_".join(st.session_state["content"]),
        "utm_term"    : "_".join(st.session_state["term"]),
    }])
    df2 = build_sheet()
    buf=BytesIO()
    with pd.ExcelWriter(buf,engine="xlsxwriter") as w:
        df1.to_excel(w, index=False, sheet_name="estructura")
        df2.to_excel(w, index=False, sheet_name="valores")
    buf.seek(0)
    st.download_button("⬇️ naming.xlsx", buf,
                       "naming_config.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
