import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items
from io import BytesIO

st.set_page_config(page_title="Naming Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

# ---------- helpers ----------
def init_sec(k, defaults):
    if k not in st.session_state:
        st.session_state[k] = defaults.copy()
    if f"vals_{k}" not in st.session_state:
        st.session_state[f"vals_{k}"] = {b: [] for b in defaults}
    st.session_state.setdefault(f"new_{k}", "")
    st.session_state.setdefault(f"sel_{k}", defaults[0])
    st.session_state.setdefault(f"txt_{k}", "")

def add_block(k, name):
    if name and name not in st.session_state[k]:
        st.session_state[k].append(name)
        st.session_state[f"vals_{k}"][name] = []

def add_values(k):
    blk = st.session_state[f"sel_{k}"]
    txt = st.session_state[f"txt_{k}"]
    if txt.strip():
        vals = [v.strip() for v in txt.split(",") if v.strip()]
        st.session_state[f"vals_{k}"][blk] += vals
        st.session_state[f"vals_{k}"][blk] = list(dict.fromkeys(st.session_state[f"vals_{k}"][blk]))
    st.session_state[f"txt_{k}"] = ""

def section(title, k, defaults):
    init_sec(k, defaults)
    st.markdown(f"### {title}")

    # ---- Drag & drop (lista actual) ----
    order_before = st.session_state[k]
    order_after  = sort_items(order_before, direction="horizontal", key=f"drag_{k}") or order_before
    st.session_state[k] = order_after
    st.caption("Orden:", order_after)

    # ---- Añadir bloque ----
    st.text_input("Nuevo bloque", key=f"new_{k}", placeholder="ej.: promocion")
    if st.button("Agregar bloque", key=f"btn_blk_{k}"):
        add_block(k, st.session_state[f"new_{k}"].strip())
        st.session_state[f"new_{k}"] = ""   # limpia box

    # ---- Añadir valores ----
    st.selectbox("Bloque destino", st.session_state[k], key=f"sel_{k}")
    st.text_input("Valores (coma separada)", key=f"txt_{k}")
    st.button("Agregar valores", key=f"btn_val_{k}", on_click=add_values, kwargs=dict(k=k))

    with st.expander("Ver valores guardados"):
        st.json(st.session_state[f"vals_{k}"])

# ---------- secciones ----------
section("utm_campaign", "campaign", ["producto","pais","fecha","audiencia","region"])
section("utm_source",   "source",   ["google","facebook","instagram","newsletter","linkedin"])
section("utm_medium",   "medium",   ["cpc","organic","email","referral","social"])
section("utm_content",  "content",  ["color","version","posicion"])
section("utm_term",     "term",     ["keyword","matchtype"])

# ---------- export ----------
def build_val_df():
    cols={}
    for k in ["campaign","source","medium","content","term"]:
        col=[]
        for blk in st.session_state[k]:
            col += [blk] + st.session_state[f"vals_{k}"][blk] + [""]
        cols[k]=col
    mx=max(len(v) for v in cols.values())
    for v in cols.values(): v.extend([""]*(mx-len(v)))
    return pd.DataFrame(cols)

st.markdown("---")
if st.button("📥 Descargar Excel"):
    df1 = pd.DataFrame([{
        "utm_campaign":"_".join(st.session_state["campaign"]),
        "utm_source"  :"_".join(st.session_state["source"]),
        "utm_medium"  :"_".join(st.session_state["medium"]),
        "utm_content" :"_".join(st.session_state["content"]),
        "utm_term"    :"_".join(st.session_state["term"]),
    }])
    df2 = build_val_df()

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        df1.to_excel(w, index=False, sheet_name="estructura")
        df2.to_excel(w, index=False, sheet_name="valores")
    buf.seek(0)
    st.download_button("⬇️ naming_config.xlsx", buf,
                       file_name="naming_config.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
