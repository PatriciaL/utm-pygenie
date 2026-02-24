import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="UTM Genie — Feedback", page_icon="🧙", layout="centered")
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
    if score <= 6:
        cat = "Detractor"
    elif score <= 8:
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
    data = ws.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(
        columns=["timestamp","nombre","nps_score","categoria","comentario"]
    )

# ------------------------------------------------------------------
# Datos de ejemplo (cuando no hay Google Sheets configurado)
# ------------------------------------------------------------------

SAMPLE_DATA = pd.DataFrame([
    {"timestamp":"2025-01-10 09:12","nombre":"Ana M.","nps_score":9,"categoria":"Promotor","comentario":"Muy útil para el equipo, ahorra mucho tiempo"},
    {"timestamp":"2025-01-12 11:34","nombre":"Carlos R.","nps_score":8,"categoria":"Pasivo","comentario":"Funciona bien, le faltaría integración con GA4"},
    {"timestamp":"2025-01-15 16:20","nombre":"Lucía P.","nps_score":10,"categoria":"Promotor","comentario":"Perfecto, lo recomendaré a mi equipo de marketing"},
    {"timestamp":"2025-01-18 10:05","nombre":"Anónimo","nps_score":5,"categoria":"Detractor","comentario":"A veces falla al importar el Excel"},
    {"timestamp":"2025-01-20 14:45","nombre":"Marc T.","nps_score":9,"categoria":"Promotor","comentario":"El generador masivo es una pasada"},
    {"timestamp":"2025-01-22 09:30","nombre":"Sara L.","nps_score":7,"categoria":"Pasivo","comentario":"Está bien pero le falta el modo oscuro"},
    {"timestamp":"2025-01-25 17:10","nombre":"Anónimo","nps_score":10,"categoria":"Promotor","comentario":"Lo uso cada semana para mis campañas"},
    {"timestamp":"2025-02-01 11:00","nombre":"Jordi V.","nps_score":6,"categoria":"Detractor","comentario":"Esperaba más opciones de personalización"},
    {"timestamp":"2025-02-05 13:22","nombre":"Elena S.","nps_score":9,"categoria":"Promotor","comentario":"Muy intuitivo y bien diseñado"},
    {"timestamp":"2025-02-10 10:15","nombre":"David F.","nps_score":8,"categoria":"Pasivo","comentario":"Bien, pero echo de menos un historial de URLs generadas"},
    {"timestamp":"2025-02-14 16:40","nombre":"Anónimo","nps_score":10,"categoria":"Promotor","comentario":"El validador con corrección automática es brillante"},
    {"timestamp":"2025-02-18 09:55","nombre":"Nuria G.","nps_score":9,"categoria":"Promotor","comentario":"Muy completo, gracias"},
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

if not use_sheets:
    st.markdown("""
    <div style="background:#FFFBEB;border:1.5px solid #FDE68A;border-radius:6px;
                padding:12px 16px;margin-bottom:20px;font-family:'Sora',sans-serif;font-size:0.78rem;color:#92400E">
      <strong>Modo demo</strong> — Google Sheets no configurado. El dashboard muestra datos de ejemplo.
      Las respuestas se pueden descargar como CSV pero no se guardan automáticamente.
      <a href="#configuracion" style="color:#3D5A80;text-decoration:none;margin-left:8px">Ver instrucciones de configuración →</a>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Tabs: Formulario / Dashboard / Configuración
# ------------------------------------------------------------------

tab_form, tab_dash, tab_config = st.tabs(["Enviar feedback", "Dashboard NPS", "Configuración"])

# ══════════════════════════════════════════════════════════
# TAB 1 — Formulario
# ══════════════════════════════════════════════════════════
with tab_form:
    st.markdown("### Tu opinión")
    st.markdown('<p style="font-size:0.82rem;color:#71717A;margin-bottom:20px">No pedimos datos personales. Puedes usar un pseudónimo.</p>', unsafe_allow_html=True)

    nombre = st.text_input("Nombre o pseudónimo (opcional)", placeholder="Patricia")

    st.markdown("### ¿Con qué probabilidad recomendarías UTM Genie?")
    st.caption("0 = Nada probable · 10 = Totalmente probable")

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

    if nps_val <= 6:
        cat_color, cat_label = "#E11D48", "Detractor"
    elif nps_val <= 8:
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
        promotores  = (df["nps_score"] >= 9).sum()
        detractores = (df["nps_score"] <= 6).sum()
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
            <div style="font-size:0.7rem;color:#16a34a;margin-top:4px">{round(promotores/len(df)*100)}% · score 9-10</div>
          </div>
          <div style="background:#FFFBEB;border:1.5px solid #FDE68A;border-radius:8px;padding:16px 20px">
            <div style="font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#92400E;margin-bottom:6px">Pasivos</div>
            <div style="font-size:2rem;font-weight:700;color:#92400E;font-family:'Sora',sans-serif;line-height:1">{pasivos}</div>
            <div style="font-size:0.7rem;color:#92400E;margin-top:4px">{round(pasivos/len(df)*100)}% · score 7-8</div>
          </div>
          <div style="background:#FFE4E6;border:1.5px solid #FECDD3;border-radius:8px;padding:16px 20px">
            <div style="font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#9F1239;margin-bottom:6px">Detractores</div>
            <div style="font-size:2rem;font-weight:700;color:#E11D48;font-family:'Sora',sans-serif;line-height:1">{detractores}</div>
            <div style="font-size:0.7rem;color:#E11D48;margin-top:4px">{round(detractores/len(df)*100)}% · score 0-6</div>
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
            count   = dist.get(score_v, 0)
            height  = int((count / max_val) * 80) if max_val > 0 else 0
            color   = "#16a34a" if score_v >= 9 else ("#FBBF24" if score_v >= 7 else "#E11D48")
            bars_html += f"""
            <div style="display:flex;flex-direction:column;align-items:center;gap:4px;flex:1">
              <div style="font-size:0.68rem;color:#52525B;font-weight:600">{count if count > 0 else ""}</div>
              <div style="width:100%;background:{color};border-radius:4px 4px 0 0;height:{height}px;min-height:{"4px" if count > 0 else "0"}"></div>
              <div style="font-size:0.68rem;color:#71717A;font-family:'DM Mono',monospace">{score_v}</div>
            </div>"""

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
            color = "#16a34a" if score_v >= 9 else ("#92400E" if score_v >= 7 else "#E11D48")
            bg    = "#F0FDF4" if score_v >= 9 else ("#FFFBEB" if score_v >= 7 else "#FFF1F2")
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



# ══════════════════════════════════════════════════════════
# TAB 3 — Configuración Google Sheets
# ══════════════════════════════════════════════════════════
with tab_config:
    st.markdown("### Conectar con Google Sheets")
    st.markdown("""
    <div style="background:#EEF2F7;border:1.5px solid #C5D3E8;border-radius:6px;padding:18px 22px;margin-bottom:20px">
      <div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:500;letter-spacing:0.14em;
                  text-transform:uppercase;color:#3D5A80;margin-bottom:12px">Pasos de configuración</div>
      <ol style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#52525B;line-height:2;padding-left:18px;margin:0">
        <li>En Google Cloud Console, activa las APIs <strong>Google Sheets</strong> y <strong>Google Drive</strong></li>
        <li>Crea una <strong>Service Account</strong> y descarga el JSON de credenciales</li>
        <li>Crea un Google Sheet nuevo y compártelo con el email de la Service Account (editor)</li>
        <li>En Streamlit Cloud, ve a <strong>Settings → Secrets</strong> y añade lo siguiente:</li>
      </ol>
    </div>
    """, unsafe_allow_html=True)

    st.code("""
# .streamlit/secrets.toml

sheet_name = "UTM Genie NPS"

[gcp_service_account]
type = "service_account"
project_id = "tu-proyecto-id"
private_key_id = "abc123..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "utm-genie-nps@tu-proyecto.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
    """, language="toml")

    st.markdown("""
    <div style="background:#F0FDF4;border:1.5px solid #86EFAC;border-radius:6px;padding:14px 18px;
                font-family:'Sora',sans-serif;font-size:0.78rem;color:#166534;margin-top:12px">
      Una vez configurado, el dashboard mostrará datos en tiempo real y cada respuesta
      del formulario se guardará automáticamente en el Sheet.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Dependencias requeridas")
    st.code("gspread\ngoogle-auth", language="text")
    st.caption("Añade estas líneas al requirements.txt")
