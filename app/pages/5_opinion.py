import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="UTM Genie — Feedback", page_icon="🧙", layout="centered", initial_sidebar_state="expanded")
apply_style()

st.markdown("""
<div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1.5px solid #E4E4E7">
  <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
              letter-spacing:0.2em;text-transform:uppercase;color:#71717A;margin-bottom:8px">
    UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:600;
              letter-spacing:-0.04em;color:#1A1A1A;line-height:1.1;margin-bottom:10px">
    Feedback
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#71717A;letter-spacing:0.01em">
    Tu opinión nos ayuda a mejorar la herramienta
  </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Conexión Google Sheets
# ------------------------------------------------------------------

def get_gsheet_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        # Streamlit Cloud: credenciales en st.secrets
        # Local: credenciales en .streamlit/secrets.toml
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        return None

def get_or_create_sheet(client, sheet_name="UTM Genie NPS"):
    try:
        sh = client.open(sheet_name)
    except Exception:
        # Crear sheet nuevo
        sh = client.create(sheet_name)
        # Sheet privado — acceso solo via Service Account
    ws = sh.sheet1
    # Añadir cabeceras si está vacío
    if ws.row_count == 0 or not ws.get_all_values():
        ws.append_row(["timestamp", "nombre", "nps_score", "categoria", "comentario"])
    return ws

def save_response(ws, nombre, score, comentario):
    if score <= 4:
        cat = "Detractor"
    elif score <= 6:
        cat = "Pasivo"
    else:
        cat = "Promotor"
    ws.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        nombre or "Anónimo",
        score,
        cat,
        comentario or ""
    ])

def load_responses(ws):
    try:
        data = ws.get_all_records(expected_headers=["timestamp","nombre","nps_score","categoria","comentario"])
        df = pd.DataFrame(data) if data else pd.DataFrame(
            columns=["timestamp","nombre","nps_score","categoria","comentario"]
        )
        # Filtrar filas completamente vacías
        df = df[df["timestamp"].astype(str).str.strip() != ""]
        return df
    except Exception:
        # Fallback: leer como valores raw
        rows = ws.get_all_values()
        if len(rows) <= 1:
            return pd.DataFrame(columns=["timestamp","nombre","nps_score","categoria","comentario"])
        headers = rows[0]
        data    = rows[1:]
        df = pd.DataFrame(data, columns=headers)
        df = df[df["timestamp"].astype(str).str.strip() != ""]
        return df

# ------------------------------------------------------------------
# Datos de ejemplo (cuando no hay Google Sheets configurado)
# ------------------------------------------------------------------

SAMPLE_DATA = pd.DataFrame([
    {"timestamp":"2024-11-03 08:47","nombre":"Marta S.","nps_score":9,"categoria":"Promotor","comentario":"Llevaba meses buscando algo así. Lo hemos adoptado en todo el equipo de paid."},
    {"timestamp":"2024-11-08 10:12","nombre":"Anónimo","nps_score":7,"categoria":"Promotor","comentario":"El generador masivo me ahorra fácil 2 horas a la semana."},
    {"timestamp":"2024-11-14 16:33","nombre":"Rafa M.","nps_score":10,"categoria":"Promotor","comentario":"Herramienta imprescindible. El validador con corrección automática es lo mejor."},
    {"timestamp":"2024-11-19 09:05","nombre":"Claudia B.","nps_score":4,"categoria":"Detractor","comentario":"Me costó entender el Naming Convention al principio, faltaría un tutorial en vídeo."},
    {"timestamp":"2024-11-25 14:20","nombre":"Anónimo","nps_score":8,"categoria":"Promotor","comentario":"Muy bueno. Le añadiría la opción de guardar plantillas de campañas recurrentes."},
    {"timestamp":"2024-12-02 11:45","nombre":"Iñigo R.","nps_score":10,"categoria":"Promotor","comentario":"Lo recomendé a tres compañeros la semana pasada. Facilísimo de usar."},
    {"timestamp":"2024-12-09 17:02","nombre":"Anónimo","nps_score":5,"categoria":"Pasivo","comentario":"Cumple lo que promete pero esperaba más integraciones con herramientas de analytics."},
    {"timestamp":"2024-12-15 10:38","nombre":"Laura P.","nps_score":9,"categoria":"Promotor","comentario":"El Excel de auditoría que genera el validador es perfecto para reportar a clientes."},
    {"timestamp":"2024-12-20 09:14","nombre":"Tomàs V.","nps_score":7,"categoria":"Promotor","comentario":"Bien diseñado y rápido. El naming convention tarda un poco en entenderse pero vale la pena."},
    {"timestamp":"2024-12-28 15:50","nombre":"Anónimo","nps_score":10,"categoria":"Promotor","comentario":"Lo uso cada lunes para preparar las campañas de la semana. Un 10."},
    {"timestamp":"2025-01-06 08:30","nombre":"Silvia G.","nps_score":3,"categoria":"Detractor","comentario":"Tuve problemas al importar un Excel con más de 500 URLs. Se quedaba cargando."},
    {"timestamp":"2025-01-10 12:17","nombre":"Anónimo","nps_score":9,"categoria":"Promotor","comentario":"Mucho mejor que las hojas de cálculo que usábamos antes. Y gratis."},
    {"timestamp":"2025-01-16 16:44","nombre":"Jordi F.","nps_score":8,"categoria":"Promotor","comentario":"Muy completo. Agradecería poder exportar también a Google Sheets directamente."},
    {"timestamp":"2025-01-21 09:58","nombre":"Anónimo","nps_score":10,"categoria":"Promotor","comentario":"El equipo entero lo ha adoptado en menos de una semana. Súper intuitivo."},
    {"timestamp":"2025-01-27 14:05","nombre":"Neus A.","nps_score":6,"categoria":"Pasivo","comentario":"Está bien para lo básico. Le falta pulir algunos detalles en móvil."},
    {"timestamp":"2025-02-03 10:22","nombre":"Anónimo","nps_score":9,"categoria":"Promotor","comentario":"Lo que más me gusta es el producto cartesiano automático en el generador masivo."},
    {"timestamp":"2025-02-07 11:35","nombre":"Diego C.","nps_score":10,"categoria":"Promotor","comentario":"Diseño limpio, flujo claro, resultado perfecto. No le cambiaría nada."},
    {"timestamp":"2025-02-12 08:48","nombre":"Anónimo","nps_score":8,"categoria":"Promotor","comentario":"Muy útil. Ojalá tuviera historial de URLs generadas para no repetir trabajo."},
    {"timestamp":"2025-02-17 15:30","nombre":"Carla M.","nps_score":9,"categoria":"Promotor","comentario":"El validador detectó errores en campañas antiguas que teníamos sin saber. Genial."},
    {"timestamp":"2025-02-21 09:10","nombre":"Anónimo","nps_score":10,"categoria":"Promotor","comentario":"Sencillo, rápido y profesional. Exactamente lo que necesitaba."},
])

# ------------------------------------------------------------------
# Detectar modo: Google Sheets o demo
# ------------------------------------------------------------------

client    = get_gsheet_client()
use_sheets = client is not None
gsheet_ws  = None

if use_sheets:
    try:
        sheet_name = st.secrets.get("sheet_name", "UTM Genie NPS")
        gsheet_ws  = get_or_create_sheet(client, sheet_name)
    except Exception as e:
        use_sheets = False



# ------------------------------------------------------------------
# Tabs: Formulario / Dashboard / Configuración
# ------------------------------------------------------------------

tab_form, tab_dash = st.tabs(["Enviar feedback", "Dashboard NPS"])

# ══════════════════════════════════════════════════════════
# TAB 1 — Formulario
# ══════════════════════════════════════════════════════════
with tab_form:
    st.markdown("### Tu opinión")
    st.markdown('<p style="font-size:0.82rem;color:#71717A;margin-bottom:20px">No pedimos datos personales. Puedes usar un pseudónimo.</p>', unsafe_allow_html=True)

    nombre = st.text_input("Nombre o pseudónimo (opcional)", placeholder="Patricia")

    st.markdown("### ¿Con qué probabilidad recomendarías UTM Genie?")
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px">
      <div style="background:#FFE4E6;border:1.5px solid #FECDD3;border-radius:6px;padding:10px 14px">
        <div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:600;letter-spacing:0.1em;
                    text-transform:uppercase;color:#E11D48;margin-bottom:4px">Detractor · 0-4</div>
        <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#9F1239;line-height:1.5">
          No lo recomendarías. Hay aspectos importantes que mejorar.
        </div>
      </div>
      <div style="background:#FFFBEB;border:1.5px solid #FDE68A;border-radius:6px;padding:10px 14px">
        <div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:600;letter-spacing:0.1em;
                    text-transform:uppercase;color:#92400E;margin-bottom:4px">Pasivo · 5-6</div>
        <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#92400E;line-height:1.5">
          Neutral. La herramienta cumple pero no entusiasma.
        </div>
      </div>
      <div style="background:#DCFCE7;border:1.5px solid #86EFAC;border-radius:6px;padding:10px 14px">
        <div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:600;letter-spacing:0.1em;
                    text-transform:uppercase;color:#16a34a;margin-bottom:4px">Promotor · 7-10</div>
        <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#166534;line-height:1.5">
          La recomendarías. Aporta valor real a tu trabajo.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Selector visual de puntuación
    score_cols = st.columns(11)
    selected_score = st.session_state.get("nps_selected", 8)
    for i, col in enumerate(score_cols):
        with col:
            is_sel = (i == selected_score)
            bg = "#3D5A80" if is_sel else "#EEF2F7"
            tc = "white"  if is_sel else "#3D5A80"
            st.markdown(
                f'<div style="background:{bg};color:{tc};text-align:center;padding:8px 4px;'
                f'border-radius:6px;font-family:\'Sora\',sans-serif;font-weight:600;'
                f'font-size:0.85rem;cursor:pointer;border:1.5px solid #C5D3E8">{i}</div>',
                unsafe_allow_html=True
            )

    nps_val = st.slider("", 0, 10, 8, label_visibility="collapsed")

    if nps_val <= 4:
        cat_color, cat_label = "#E11D48", "Detractor"
    elif nps_val <= 6:
        cat_color, cat_label = "#92400E", "Pasivo"
    else:
        cat_color, cat_label = "#16a34a", "Promotor"

    st.markdown(f"""
    <div style="margin:8px 0 16px">
      <span style="background:{cat_color}18;color:{cat_color};padding:3px 12px;
                   border-radius:20px;font-size:0.72rem;font-weight:600;
                   font-family:'Sora',sans-serif">{cat_label}</span>
    </div>
    """, unsafe_allow_html=True)

    comentario = st.text_area("¿Por qué esa puntuación? (opcional)",
                              placeholder="Cualquier comentario es bienvenido...",
                              height=100)

    if st.button("Enviar feedback", type="primary", use_container_width=True):
        respuesta = {
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nombre":     nombre or "Anónimo",
            "nps_score":  nps_val,
            "categoria":  cat_label,
            "comentario": comentario or ""
        }

        if use_sheets and gsheet_ws:
            try:
                save_response(gsheet_ws, nombre, nps_val, comentario)
                st.success("Gracias, tu respuesta se ha guardado.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")
                st.info("Descarga tu respuesta manualmente:")
                df_r = pd.DataFrame([respuesta])
                st.download_button("Descargar respuesta CSV", df_r.to_csv(index=False).encode(),
                                   file_name="respuesta_nps.csv", mime="text/csv")
        else:
            st.success("Gracias por tu feedback.")
            df_r = pd.DataFrame([respuesta])
            st.download_button("Descargar respuesta CSV", df_r.to_csv(index=False).encode(),
                               file_name="respuesta_nps.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════
# TAB 2 — Dashboard NPS
# ══════════════════════════════════════════════════════════
with tab_dash:

    # Cargar datos reales o demo
    if use_sheets and gsheet_ws:
        df = load_responses(gsheet_ws)
        st.caption(f"Datos en tiempo real desde Google Sheets · {len(df)} respuestas")
    else:
        df = SAMPLE_DATA.copy()
        st.caption("Datos de ejemplo — configura Google Sheets para ver datos reales")

    # Opción de subir CSV acumulado (modo sin Sheets)
    if not use_sheets:
        with st.expander("Subir CSV de respuestas acumuladas"):
            uploaded = st.file_uploader("CSV con columnas: timestamp, nombre, nps_score, categoria, comentario",
                                        type=["csv"], label_visibility="collapsed")
            if uploaded:
                df = pd.read_csv(uploaded)
                st.success(f"{len(df)} respuestas cargadas.")

    if df.empty:
        st.info("Sin respuestas todavía.")
    else:
        df["nps_score"] = pd.to_numeric(df["nps_score"], errors="coerce").fillna(0).astype(int)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # Calcular NPS
        promotores  = (df["nps_score"] >= 7).sum()
        detractores = (df["nps_score"] <= 4).sum()
        pasivos     = len(df) - promotores - detractores
        nps_score   = round(((promotores - detractores) / len(df)) * 100)
        nps_color   = "#16a34a" if nps_score >= 50 else ("#92400E" if nps_score >= 0 else "#E11D48")

        # ── KPIs ──────────────────────────────────────────
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:12px;margin-bottom:24px">
          <div style="background:#FFFFFF;border:1.5px solid #E4E4E7;border-radius:8px;padding:16px 20px">
            <div style="font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#71717A;margin-bottom:6px">Score NPS</div>
            <div style="font-size:2.4rem;font-weight:700;color:{nps_color};font-family:'Sora',sans-serif;line-height:1">{nps_score}</div>
            <div style="font-size:0.7rem;color:#A1A1AA;margin-top:4px">de -100 a +100</div>
          </div>
          <div style="background:#DCFCE7;border:1.5px solid #86EFAC;border-radius:8px;padding:16px 20px">
            <div style="font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#166534;margin-bottom:6px">Promotores</div>
            <div style="font-size:2rem;font-weight:700;color:#16a34a;font-family:'Sora',sans-serif;line-height:1">{promotores}</div>
            <div style="font-size:0.7rem;color:#16a34a;margin-top:4px">{round(promotores/len(df)*100)}% · score 7-10</div>
          </div>
          <div style="background:#FFFBEB;border:1.5px solid #FDE68A;border-radius:8px;padding:16px 20px">
            <div style="font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#92400E;margin-bottom:6px">Pasivos</div>
            <div style="font-size:2rem;font-weight:700;color:#92400E;font-family:'Sora',sans-serif;line-height:1">{pasivos}</div>
            <div style="font-size:0.7rem;color:#92400E;margin-top:4px">{round(pasivos/len(df)*100)}% · score 5-6</div>
          </div>
          <div style="background:#FFE4E6;border:1.5px solid #FECDD3;border-radius:8px;padding:16px 20px">
            <div style="font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#9F1239;margin-bottom:6px">Detractores</div>
            <div style="font-size:2rem;font-weight:700;color:#E11D48;font-family:'Sora',sans-serif;line-height:1">{detractores}</div>
            <div style="font-size:0.7rem;color:#E11D48;margin-top:4px">{round(detractores/len(df)*100)}% · score 0-4</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Barra de distribución ─────────────────────────
        pct_p = round(promotores/len(df)*100)
        pct_n = round(pasivos/len(df)*100)
        pct_d = round(detractores/len(df)*100)
        st.markdown(f"""
        <div style="margin-bottom:24px">
          <div style="font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase;color:#71717A;margin-bottom:8px">Distribución</div>
          <div style="display:flex;height:10px;border-radius:6px;overflow:hidden;gap:2px">
            <div style="background:#16a34a;width:{pct_p}%;border-radius:4px 0 0 4px"></div>
            <div style="background:#FBBF24;width:{pct_n}%"></div>
            <div style="background:#E11D48;width:{pct_d}%;border-radius:0 4px 4px 0"></div>
          </div>
          <div style="display:flex;gap:16px;margin-top:6px">
            <span style="font-size:0.7rem;color:#16a34a">Promotores {pct_p}%</span>
            <span style="font-size:0.7rem;color:#92400E">Pasivos {pct_n}%</span>
            <span style="font-size:0.7rem;color:#E11D48">Detractores {pct_d}%</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Histograma de puntuaciones ────────────────────
        st.markdown("### Distribución de puntuaciones")
        dist = df["nps_score"].value_counts().sort_index()
        max_val = dist.max() if not dist.empty else 1

        bars_html = ""
        for score_v in range(11):
            count    = dist.get(score_v, 0)
            height   = int((count / max_val) * 80) if max_val > 0 else 0
            color    = "#16a34a" if score_v >= 7 else ("#FBBF24" if score_v >= 5 else "#E11D48")
            count_lbl = str(count) if count > 0 else ""
            min_h    = "4px" if count > 0 else "0"
            bars_html += (
                f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px;flex:1">'
                f'<div style="font-size:0.68rem;color:#52525B;font-weight:600">{count_lbl}</div>'
                f'<div style="width:100%;background:{color};border-radius:4px 4px 0 0;height:{height}px;min-height:{min_h}"></div>'
                f'<div style="font-size:0.68rem;color:#71717A;font-family:DM Mono,monospace">{score_v}</div>'
                f'</div>'
            )

        st.markdown(f"""
        <div style="background:#FAFAFA;border:1.5px solid #E4E4E7;border-radius:8px;padding:20px;margin-bottom:24px">
          <div style="display:flex;align-items:flex-end;gap:4px;height:110px">
            {bars_html}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Comentarios recientes ─────────────────────────
        st.markdown("### Comentarios recientes")
        comentarios = df[df["comentario"].notna() & (df["comentario"] != "")].copy()
        comentarios = comentarios.sort_values("timestamp", ascending=False).head(8)

        for _, row in comentarios.iterrows():
            cat = row.get("categoria", "")
            score_v = int(row["nps_score"])
            color = "#16a34a" if score_v >= 7 else ("#92400E" if score_v >= 5 else "#E11D48")
            bg    = "#F0FDF4" if score_v >= 7 else ("#FFFBEB" if score_v >= 5 else "#FFF1F2")
            fecha = row["timestamp"].strftime("%d/%m/%Y") if pd.notna(row["timestamp"]) else ""
            st.markdown(f"""
            <div style="background:{bg};border-radius:6px;padding:12px 16px;margin-bottom:8px;
                        border-left:3px solid {color}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <span style="font-family:'Sora',sans-serif;font-size:0.75rem;font-weight:600;color:#1A1A1A">{row.get("nombre","Anónimo")}</span>
                <div style="display:flex;gap:8px;align-items:center">
                  <span style="font-family:'DM Mono',monospace;font-size:0.75rem;font-weight:700;color:{color}">{score_v}</span>
                  <span style="font-size:0.65rem;color:#A1A1AA">{fecha}</span>
                </div>
              </div>
              <div style="font-family:'Sora',sans-serif;font-size:0.78rem;color:#52525B;line-height:1.55">{row["comentario"]}</div>
            </div>
            """, unsafe_allow_html=True)
