import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Naming Builder", layout="wide")
st.title("🧱 Naming Convention UTM")

# ------- helpers -------
def init_sec(key, defaults):
    if key not in st.session_state:
        st.session_state[key] = defaults.copy()
    if f"vals_{key}" not in st.session_state:
        st.session_state[f"vals_{key}"] = {b: [] for b in defaults}

def reset_sec(key, defaults):
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}

def section(title, key, defaults):
    init_sec(key, defaults)

    st.subheader(title)
    st.session_state[key] = sort_items(
        st.session_state[key],
        direction="horizontal",
        key=f"sortable_{key}"
    ) or st.session_state[key]

    if st.button("Reset", key=f"reset_{key}"):
        reset_sec(key, defaults)

    st.write("Orden actual:", st.session_state[key])

    # ---- formulario externo estable ----
    st.markdown("**Añadir valores**")
    blk = st.selectbox("Bloque", st.session_state[key], key=f"sel_{key}")
    txt = st.text_input("Valores (coma separada)", key=f"txt_{key}")
    if st.button("Agregar", key=f"add_{key}") and txt.strip():
        nuevos = [v.strip() for v in txt.split(",") if v.strip()]
        st.session_state[f"vals_{key}"][blk].extend(nuevos)
        st.session_state[f"txt_{key}"] = ""   # limpia
        st.success(f"Añadidos a {blk}: {', '.join(nuevos)}")

    with st.expander("Ver valores guardados"):
        st.json(st.session_state[f"vals_{key}"])

# ------- secciones -------
section("utm_campaign", "campaign",
        ["producto","pais","fecha","audiencia"])
section("utm_source", "source",
        ["google","facebook","instagram","newsletter"])
section("utm_medium", "medium",
        ["organic","cpc","email","social"])
section("utm_content", "content",
        ["color","version","posicion"])
section("utm_term", "term",
        ["keyword","matchtype"])

# ------- export -------
st.markdown("---")
if st.button("Exportar Excel"):
    df1 = pd.DataFrame([{
        "utm_campaign": "_".join(st.session_state["campaign"]),
        "utm_source"  : "_".join(st.session_state["source"]),
        "utm_medium"  : "_".join(st.session_state["medium"]),
        "utm_content" : "_".join(st.session_state["content"]),
        "utm_term"    : "_".join(st.session_state["term"]),
    }])

    # hoja 2 vertical
    def col(sec):
        out=[]
        for b in st.session_state[sec]:
            out += [b]+st.session_state[f"vals_{sec}"][b]+[""]
        return out
    cols = {
        "campaign": col("campaign"),
        "source"  : col("source"),
        "medium"  : col("medium"),
        "content" : col("content"),
        "term"    : col("term")
    }
    m = max(len(v) for v in cols.values())
    for k,v in cols.items():
        v.extend([""]*(m-len(v)))
    df2 = pd.DataFrame(cols)

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        df1.to_excel(w, sheet_name="estructura", index=False)
        df2.to_excel(w, sheet_name="valores",     index=False)
    buf.seek(0)
    st.download_button("Descargar naming.xlsx", buf,
                       "naming_config.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
