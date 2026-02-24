import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="UTM Genie — Naming Convention", page_icon="🧙", layout="centered")
apply_style()

st.markdown("""
<div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1.5px solid #E4E4E7">
  <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
              letter-spacing:0.2em;text-transform:uppercase;color:#71717A;margin-bottom:8px">
    UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:600;
              letter-spacing:-0.04em;color:#1A1A1A;line-height:1.1;margin-bottom:10px">
    Naming Convention
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#71717A;letter-spacing:0.01em">
    Define la estructura y valores de cada parámetro UTM
  </div>
</div>
""", unsafe_allow_html=True)

# Instrucciones + sticky CTA
st.markdown("""
<style>
.sticky-cta {
    position: fixed;
    bottom: 32px;
    right: 36px;
    z-index: 99999;
}
.sticky-cta a {
    font-family: 'Sora', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    background: #3D5A80;
    color: #FFFFFF !important;
    text-decoration: none !important;
    border-radius: 8px;
    padding: 14px 26px;
    display: inline-block;
    box-shadow: 0 4px 20px rgba(61,90,128,0.45), 0 1px 4px rgba(0,0,0,0.15);
    transition: background 0.15s, box-shadow 0.15s, transform 0.1s;
}
.sticky-cta a:hover {
    background: #2e4460;
    box-shadow: 0 8px 28px rgba(61,90,128,0.55);
    transform: translateY(-1px);
}
</style>
<div class="sticky-cta">
  <a href="/1_generator_UTM" target="_self">Ir al Generador &rarr;</a>
</div>
<div style="background:#EEF2F7;border:1.5px solid #C5D3E8;border-radius:6px;padding:18px 22px;margin-bottom:4px">
  <div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:#3D5A80;margin-bottom:10px">Cómo funciona</div>
  <div style="font-family:'Sora',sans-serif;font-size:0.83rem;color:#1A1A1A;line-height:1.75;margin-bottom:14px">
    Define los <strong>bloques</strong> de cada parámetro UTM y añade <strong>valores</strong> a cada uno.
    Todo lo que configures aquí se cargará automáticamente en el <strong>Generador Masivo</strong>
    para que puedas generar todas las combinaciones sin escribir nada manualmente.
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 24px">
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_campaign</strong> &rarr; combinaciones de bloques</div>
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_source</strong> &rarr; fuentes de tráfico</div>
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_medium</strong> &rarr; canales o medios</div>
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_content</strong> &rarr; variantes del anuncio</div>
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_term</strong> &rarr; palabras clave</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Estado inicial
# ------------------------------------------------------------------

SECTIONS = {
    "campaign": ["producto", "pais", "fecha", "audiencia", "region"],
    "source":   ["google", "facebook", "instagram", "newsletter", "linkedin"],
    "medium":   ["cpc", "organic", "email", "referral", "social"],
    "content":  ["color", "version", "posicion"],
    "term":     ["keyword", "matchtype"],
}

for key, defaults in SECTIONS.items():
    if key not in st.session_state:
        st.session_state[key] = defaults.copy()
    if f"vals_{key}" not in st.session_state:
        st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    if f"reset_count_{key}" not in st.session_state:
        st.session_state[f"reset_count_{key}"] = 0

# ------------------------------------------------------------------
# Callbacks — toda la mutación de estado aquí, nunca en el render
# ------------------------------------------------------------------

def reset_sec(key):
    defaults = SECTIONS[key]
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    st.session_state[f"reset_count_{key}"] += 1
    # Limpiar también los inputs del generador para forzar resync
    for k in ["bulk_source","bulk_medium","bulk_campaign","bulk_content","bulk_term"]:
        if k in st.session_state:
            del st.session_state[k]

def add_block_cb(key):
    name = st.session_state[f"newblk_input_{key}"].strip()
    if name and name not in st.session_state[key]:
        st.session_state[key].append(name)
        st.session_state[f"vals_{key}"][name] = []
        st.session_state[f"reset_count_{key}"] += 1
    st.session_state[f"newblk_input_{key}"] = ""

def delete_block_cb(key, blk):
    if blk in st.session_state[key]:
        st.session_state[key].remove(blk)
    st.session_state[f"vals_{key}"].pop(blk, None)
    st.session_state[f"reset_count_{key}"] += 1

def add_values_cb(key):
    blk = st.session_state[f"sel_input_{key}"]
    txt = st.session_state[f"txt_input_{key}"].strip()
    if txt:
        new_vals = [v.strip() for v in txt.split(",") if v.strip()]
        existing = st.session_state[f"vals_{key}"].get(blk, [])
        for v in new_vals:
            if v not in existing:
                existing.append(v)
        st.session_state[f"vals_{key}"][blk] = existing
        # Invalidar cache del generador para forzar resync
        for k in ["bulk_source","bulk_medium","bulk_campaign","bulk_content","bulk_term"]:
            if k in st.session_state:
                del st.session_state[k]
    st.session_state[f"txt_input_{key}"] = ""

def delete_val_cb(key, blk, val):
    if val in st.session_state[f"vals_{key}"].get(blk, []):
        st.session_state[f"vals_{key}"][blk].remove(val)
    for k in ["bulk_source","bulk_medium","bulk_campaign","bulk_content","bulk_term"]:
        if k in st.session_state:
            del st.session_state[k]

def get_all_values(key):
    all_vals = []
    for blk in st.session_state.get(key, []):
        all_vals.extend(st.session_state.get(f"vals_{key}", {}).get(blk, []))
    return list(dict.fromkeys(all_vals))

# ------------------------------------------------------------------
# Render de sección
# ------------------------------------------------------------------

def section(title: str, key: str):
    st.markdown(f"## {title}")

    # FIX: sort_items puede devolver None si no hay interacción — proteger siempre
    rc     = st.session_state[f"reset_count_{key}"]
    result = sort_items(st.session_state[key], direction="horizontal", key=f"sort_{key}_{rc}")
    if result and len(result) == len(st.session_state[key]):
        st.session_state[key] = result

    st.caption("Arrastra los bloques para cambiar el orden")

    # Bloques con sus valores como pastillas y botón de borrado
    for blk in list(st.session_state[key]):  # list() para evitar mutation durante iteración
        vals = st.session_state[f"vals_{key}"].get(blk, [])
        c1, c2 = st.columns([9, 1])
        with c1:
            pastillas = " ".join([
                f'<span style="background:#EEF2F7;color:#3D5A80;padding:2px 10px;'
                f'border-radius:20px;font-size:11px;border:1.5px solid #C5D3E8;'
                f'font-family:\'Sora\',sans-serif;letter-spacing:0.03em;margin:2px;display:inline-block">{v}</span>'
                for v in vals
            ])
            sin_vals = '<em style="color:#A1A1AA;font-size:11px">sin valores</em>' if not vals else ""
            st.markdown(
                f'<div style="margin:6px 0;font-size:0.82rem;line-height:2">'
                f'<strong style="font-family:\'Sora\',sans-serif">{blk}</strong>'
                f'&nbsp;&nbsp;{pastillas}{sin_vals}</div>',
                unsafe_allow_html=True
            )
        with c2:
            # FIX: usar on_click para que el callback se ejecute antes del re-render
            st.button("—", key=f"del_blk_{key}_{blk}",
                      help=f"Eliminar bloque '{blk}'",
                      on_click=delete_block_cb,
                      kwargs={"key": key, "blk": blk})

        # FIX: mostrar TODOS los valores, no solo los primeros 6
        if vals:
            for i in range(0, len(vals), 4):
                chunk = vals[i:i+4]
                val_cols = st.columns(len(chunk))
                for j, val in enumerate(chunk):
                    with val_cols[j]:
                        st.button(f"x {val}", key=f"del_val_{key}_{blk}_{val}",
                                  on_click=delete_val_cb,
                                  kwargs={"key": key, "blk": blk, "val": val})

    st.markdown("")

    # Añadir nuevo bloque
    st.markdown("### Nuevo bloque")
    nc1, nc2 = st.columns([4, 1])
    with nc1:
        st.text_input("", key=f"newblk_input_{key}", placeholder="ej. promocion", label_visibility="collapsed")
    with nc2:
        st.button("Agregar", key=f"btn_addblk_{key}", on_click=add_block_cb, kwargs={"key": key})

    # Reset
    st.button("Resetear sección", key=f"reset_btn_{key}", on_click=reset_sec, kwargs={"key": key})

    # Añadir valores
    st.markdown("### Añadir valores")
    if st.session_state[key]:
        st.selectbox("", st.session_state[key], key=f"sel_input_{key}", label_visibility="collapsed")
        st.text_input("", key=f"txt_input_{key}", placeholder="valor1, valor2, valor3", label_visibility="collapsed")
        st.button("Agregar valores", key=f"btn_addvals_{key}", on_click=add_values_cb, kwargs={"key": key})
    else:
        st.caption("Añade al menos un bloque primero.")

    # Debug / preview
    with st.expander("Ver valores guardados"):
        st.json(st.session_state[f"vals_{key}"])

    preview = get_all_values(key)
    if preview:
        st.caption(f"El generador usará: {', '.join(preview)}")

    st.markdown("---")

# ------------------------------------------------------------------
# Secciones
# ------------------------------------------------------------------

section("utm_campaign", "campaign")
section("utm_source",   "source")
section("utm_medium",   "medium")
section("utm_content",  "content")
section("utm_term",     "term")

# ------------------------------------------------------------------
# Exportar a Excel
# ------------------------------------------------------------------

st.markdown("## Exportar a Excel")

def build_val_sheet():
    cols = {}
    for sec in SECTIONS:
        col = []
        for blk in st.session_state[sec]:
            col += [blk] + st.session_state[f"vals_{sec}"].get(blk, []) + [""]
        cols[sec] = col
    max_len = max(len(v) for v in cols.values())
    for v in cols.values():
        v.extend([""] * (max_len - len(v)))
    return pd.DataFrame(cols)

if st.button("Descargar Excel"):
    df_struct = pd.DataFrame([{f"utm_{sec}": "_".join(st.session_state[sec]) for sec in SECTIONS}])
    df_vals   = build_val_sheet()
    buffer    = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_struct.to_excel(writer, index=False, sheet_name="estructura")
        df_vals.to_excel(writer,   index=False, sheet_name="valores")
    buffer.seek(0)
    st.download_button("naming_config.xlsx", data=buffer, file_name="naming_config.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")
st.caption("Los valores configurados se cargarán automáticamente en el Generador Masivo.")
