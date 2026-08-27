from datetime import datetime
import base64
import os
from pathlib import Path
import random
import time
import requests
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Sorteo Champions Mandinguera", page_icon="⚽", layout="wide"
)

# ==========================================
# 🎨 ESTILOS CSS - ESTÉTICA CHAMPIONS LEAGUE
# ==========================================
CHAMPIONS_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');

    /* Fondo principal y tipografía general */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #00287a, #000418 80%);
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }

    /* Títulos principales */
    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #ffffff !important;
        text-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    }

    /* Estilo para la cuenta atrás (Metrics) */
    [data-testid="stMetricValue"] {
        color: #00e5ff !important;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        text-shadow: 0px 0px 15px rgba(0, 229, 255, 0.6);
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        color: #b0c4de !important;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 1.1rem;
        letter-spacing: 1px;
        text-align: center;
    }

    /* Contenedor general de columnas */
    [data-testid="column"] {
        padding: 5px;
    }

    /* Separadores */
    hr {
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Alertas de Info/Success */
    div.stAlert {
        background-color: rgba(0, 229, 255, 0.1);
        border: 1px solid #00e5ff;
        color: white;
    }

    /* Animación de la lluvia de balones */
    @keyframes drop {
        0% { transform: translateY(-50px) rotate(0deg); opacity: 1; }
        100% { transform: translateY(300px) rotate(360deg); opacity: 0; }
    }
    .falling-ball {
        position: absolute;
        top: -50px;
        animation: drop 2.5s linear infinite;
        z-index: 999;
    }
</style>
"""
st.markdown(CHAMPIONS_CSS, unsafe_allow_html=True)

# Enlace de tu base de datos remota en npoint.io
NPOINT_URL = "https://api.npoint.io/8bb91db2ed41d4d64582"

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
ESCUDOS_DIR = ASSETS_DIR / "escudos"
BALON_PATH = ASSETS_DIR / "balon.png"

# ==========================================
# ⚙️ CONFIGURACIÓN DE EQUIPOS
# ==========================================

EQUIPOS = [
    {
        "nombre": "AL-LARIK-APAPA",
        "manager": "Ale",
        "bombo": 1,
        "teamid": "5b699f437f9f7e021a9f71b4",
    },
    {
        "nombre": "APOEL BARCELÓ C.F.",
        "manager": "Juanma",
        "bombo": 1,
        "teamid": "66aff83db42d2f289215c3a0",
    },
    {
        "nombre": "BASS-T-NATION UNITED",
        "manager": "Noya",
        "bombo": 1,
        "teamid": "5f5612b297bff0563e446c9f",
    },
    {
        "nombre": "AC PONIENTE",
        "manager": "Nando",
        "bombo": 2,
        "teamid": "5b61c6e32bfc27e41987c9b1",
    },
    {
        "nombre": "LA CASA DE LA JUVENTUS",
        "manager": "Sergio",
        "bombo": 2,
        "teamid": "5b5f0e425077cd3775d96f66",
    },
    {
        "nombre": "OLYMPIQUE DE MARMÀSELLA",
        "manager": "Salva",
        "bombo": 2,
        "teamid": "6a6c777d9ca13a2cab53c9dd",
    },
    {
        "nombre": "CSKA LAROPA",
        "manager": "Gonzalo",
        "bombo": 3,
        "teamid": "68975fc2ca08f61db236301b",
    },
    {
        "nombre": "LA MÉRIDA GUSTO FC",
        "manager": "Javi",
        "bombo": 3,
        "teamid": "62e7c9fd594e39337f8f5243",
    },
    {
        "nombre": "RAYO MALAYO",
        "manager": "Victor",
        "bombo": 3,
        "teamid": "5b617d622bfc27e4198654de",
    },
    {
        "nombre": "EMERITA DISGUSTA!",
        "manager": "Miguel",
        "bombo": 4,
        "teamid": "6a6c8a3d3214f32ca53c27d5",
    },
    {
        "nombre": "ESTRELLA GALICIA CF",
        "manager": "Francis",
        "bombo": 4,
        "teamid": "689653326d85ec6bdab02609",
    },
    {
        "nombre": "MACCABI DE LEVANTÁ",
        "manager": "Alfon",
        "bombo": 4,
        "teamid": "6898cb62c4de884fb3611bd7",
    },
    {
        "nombre": "WINE & HORSE",
        "manager": "Jose",
        "bombo": 4,
        "teamid": "5b757e0520eda94909ef8326",
    },
]


def obtener_ruta_escudo(team_id):
  if ESCUDOS_DIR.exists():
    for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
      escudo_local = ESCUDOS_DIR / f"{team_id}{ext}"
      if escudo_local.exists():
        return str(escudo_local)
  return None


def obtener_balon_base64(path_balon):
  if os.path.exists(path_balon):
    with open(path_balon, "rb") as f:
      encoded = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded}"
  return None


# ==========================================
# ☁️ FUNCIONES DE NUBE (NPOINT.IO)
# ==========================================
def obtener_datos_nube():
  try:
    response = requests.get(NPOINT_URL)
    if response.status_code == 200:
      return response.json()
  except:
    pass
  return None


datos_nube = obtener_datos_nube()

DEFAULT_TARGET_TIME = datetime(2026, 6, 1, 20, 0, 0)
if datos_nube and "target_time" in datos_nube:
  try:
    TARGET_TIME = datetime.strptime(datos_nube["target_time"], "%Y-%m-%d %H:%M:%S")
  except:
    TARGET_TIME = DEFAULT_TARGET_TIME
else:
  TARGET_TIME = DEFAULT_TARGET_TIME


def guardar_resultado_nube(resultado):
  try:
    payload = {
        "target_time": TARGET_TIME.strftime("%Y-%m-%d %H:%M:%S"),
        "equipos": EQUIPOS,
        "resultado": resultado,
    }
    headers = {"Content-Type": "application/json"}
    requests.post(NPOINT_URL, json=payload, headers=headers)
  except Exception as e:
    st.error(f"Error al sincronizar con la nube: {e}")


def ejecutar_sorteo_champions(eqs):
  bombos = {1: [], 2: [], 3: [], 4: []}
  for e in eqs:
    bombos[e["bombo"]].append(e)

  for b in bombos:
    random.shuffle(bombos[b])

  grupos = {"Grupo A": [], "Grupo B": [], "Grupo C": []}

  try:
    for b in [1, 2, 3]:
      grupos["Grupo A"].append(bombos[b][0])
      grupos["Grupo B"].append(bombos[b][1])
      grupos["Grupo C"].append(bombos[b][2])

    grupos["Grupo A"].append(bombos[4][0])
    grupos["Grupo B"].append(bombos[4][1])
    grupos["Grupo C"].append(bombos[4][2])
    grupos["Grupo C"].append(bombos[4][3])

    return grupos
  except IndexError:
    return None


# --- CARGAR BALÓN EN BASE64 PARA TÍTULO Y ANIMACIÓN ---
balon_b64 = obtener_balon_base64(BALON_PATH)
if balon_b64:
  img_title = f'<img src="{balon_b64}" style="width: 38px; height: 38px; vertical-align: middle; margin: 0 10px;" />'
  img_anim = f'<img src="{balon_b64}" style="width: 35px; height: 35px;" />'
else:
  img_title = "⚽"
  img_anim = "⚽"

# --- VISTA DE LA APLICACIÓN ---
st.markdown(
    f"<h1>{img_title} CHAMPIONS MANDINGUERA 26/27 {img_title}</h1>",
    unsafe_allow_html=True,
)
st.write("")

ahora = datetime.now()

if ahora < TARGET_TIME:
  st.info(
      "⏳ El sorteo oficial está programado para el:"
      f" **{TARGET_TIME.strftime('%Y-%m-%d %H:%M:%S')}**"
  )
  st.write("---")

  # Cuenta atrás en tiempo real (en vivo)
  tiempo_restante = TARGET_TIME - ahora
  horas, resto = divmod(int(tiempo_restante.total_seconds()), 3600)
  minutos, segundos = divmod(resto, 60)
  dias, horas = divmod(horas, 24)

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Días", dias)
  col2.metric("Horas", horas)
  col3.metric("Minutos", minutos)
  col4.metric("Segundos", segundos)

  st.write("---")
  st.markdown("<h2>📋 Composición de los Bombos</h2>", unsafe_allow_html=True)
  st.write("")

  # Organizar equipos por bombo
  bombos = {1: [], 2: [], 3: [], 4: []}
  for eq in EQUIPOS:
    bombos[eq["bombo"]].append(eq)


  # Función auxiliar para pintar cada tarjeta de bombo de forma limpia
  def render_bombo(b_num, lista_equipos):
    st.markdown(
        f"""
        <div style="background: rgba(0, 15, 40, 0.85); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 10px; overflow: hidden; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
            <div style="background: linear-gradient(90deg, #00287a, #0045bc); padding: 10px; text-align: center; font-weight: 900; font-size: 1.1rem; letter-spacing: 1px; color: #ffffff; border-bottom: 2px solid #00e5ff;">
                BOMBO {b_num}
            </div>
            <div style="padding: 10px;">
    """,
        unsafe_allow_html=True,
    )

    for m in lista_equipos:
      ruta_img = obtener_ruta_escudo(m["teamid"])
      if ruta_img:
        with open(ruta_img, "rb") as f:
          img_b64 = base64.b64encode(f.read()).decode()
        # Escudo más grande (30px)
        escudo_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 30px; height: 30px; object-fit: contain; margin-right: 12px;">'
      else:
        escudo_html = (
            '<span style="font-size: 20px; margin-right: 12px;">🛡️</span>'
        )

      st.markdown(
          f"""
          <div style="display: flex; align-items: center; padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 1rem;">
              {escudo_html}
              <span style="color: #ffffff; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{m['nombre']}">{m['nombre']}</span>
          </div>
          """,
          unsafe_allow_html=True,
      )

    st.markdown("</div></div>", unsafe_allow_html=True)


  # Fila 1: Bombo 1 y Bombo 2
  row1_col1, row1_col2 = st.columns(2)
  with row1_col1:
    render_bombo(1, bombos[1])
  with row1_col2:
    render_bombo(2, bombos[2])

  # Fila 2: Bombo 3 y Bombo 4
  row2_col1, row2_col2 = st.columns(2)
  with row2_col1:
    render_bombo(3, bombos[3])
  with row2_col2:
    render_bombo(4, bombos[4])

  time.sleep(1)
  st.rerun()

else:
  st.success("🎉 ¡El Sorteo ha finalizado! Estos son los grupos oficiales.")

  resultado_actual = datos_nube.get("resultado") if datos_nube else None

  if not resultado_actual:
    resultado_actual = ejecutar_sorteo_champions(EQUIPOS)
    if resultado_actual:
      guardar_resultado_nube(resultado_actual)
    else:
      st.error("Error al repartir los equipos.")

  if resultado_actual:
    st.markdown(
        f"""
        <div style="text-align: center; position: relative; height: 60px; overflow: hidden; margin-bottom: 20px;">
            <span class="falling-ball" style="left: 15%; animation-delay: 0s;">{img_anim}</span>
            <span class="falling-ball" style="left: 30%; animation-delay: 0.8s;">{img_anim}</span>
            <span class="falling-ball" style="left: 50%; animation-delay: 0.3s;">{img_anim}</span>
            <span class="falling-ball" style="left: 70%; animation-delay: 1.2s;">{img_anim}</span>
            <span class="falling-ball" style="left: 85%; animation-delay: 0.5s;">{img_anim}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for i, (grupo, miembros) in enumerate(resultado_actual.items()):
      with cols[i]:
        st.markdown(
            f"""
            <div style="background: rgba(0, 15, 40, 0.85); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 10px; overflow: hidden; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                <div style="background: linear-gradient(90deg, #00287a, #0045bc); padding: 10px; text-align: center; font-weight: 900; font-size: 1.1rem; letter-spacing: 1px; color: #ffffff; border-bottom: 2px solid #00e5ff;">
                    🏆 {grupo}
                </div>
                <div style="padding: 8px;">
        """,
            unsafe_allow_html=True,
        )

        for idx, m in enumerate(miembros, 1):
          ruta_img = obtener_ruta_escudo(m["teamid"])
          if ruta_img:
            with open(ruta_img, "rb") as f:
              img_b64 = base64.b64encode(f.read()).decode()
            escudo_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 26px; height: 26px; object-fit: contain; margin-right: 10px;">'
          else:
            escudo_html = (
                '<span style="font-size: 18px; margin-right: 10px;">🛡️</span>'
            )

          st.markdown(
              f"""
              <div style="display: flex; align-items: center; padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.9rem;">
                  <span style="color: #00e5ff; font-weight: bold; width: 18px; text-align: center; margin-right: 5px;">{idx}</span>
                  {escudo_html}
                  <span style="color: #ffffff; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{m['nombre']}</span>
              </div>
              """,
              unsafe_allow_html=True,
          )

        st.markdown("</div></div>", unsafe_allow_html=True)
