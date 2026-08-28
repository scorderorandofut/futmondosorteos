from datetime import datetime
from zoneinfo import ZoneInfo
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

    .stApp {
        background: radial-gradient(circle at 50% -20%, #00287a, #000418 80%);
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }

    h2, h3 {
        font-family: 'Montserrat', sans-serif;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #ffffff !important;
        text-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    }

    .champions-header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin: 10px 0 20px 0;
        text-align: center;
    }

    .title-texts-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .app-title-line {
        font-family: 'Montserrat', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #ffffff !important;
        text-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
        line-height: 1.2;
    }

    .title-ball {
        width: 38px;
        height: 38px;
        object-fit: contain;
    }

    .countdown-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin: 20px 0;
    }
    .countdown-box {
        background: rgba(0, 15, 40, 0.85);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 10px;
        padding: 12px 18px;
        text-align: center;
        min-width: 90px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .countdown-value {
        color: #00e5ff !important;
        font-size: 3.2rem;
        font-weight: 900;
        text-shadow: 0px 0px 15px rgba(0, 229, 255, 0.6);
        line-height: 1.1;
    }
    .countdown-label {
        color: #b0c4de !important;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 1px;
        margin-top: 5px;
    }
    .countdown-separator {
        color: #00e5ff;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 0px 0px 10px rgba(0, 229, 255, 0.6);
        margin-top: -15px;
    }

    @media (max-width: 480px) {
        .champions-header-container { gap: 8px; }
        .app-title-line { font-size: 1.25rem !important; letter-spacing: 1px !important; }
        .title-ball { width: 24px; height: 24px; }
        .countdown-container { gap: 6px; }
        .countdown-box { padding: 8px 10px; min-width: 65px; border-radius: 8px; }
        .countdown-value { font-size: 1.8rem; }
        .countdown-label { font-size: 0.6rem; letter-spacing: 0.5px; }
        .countdown-separator { font-size: 1.5rem; margin-top: -10px; }
    }

    [data-testid="column"] { padding: 5px; }
    hr { border-top: 1px solid rgba(255, 255, 255, 0.2); }
    div.stAlert { background-color: rgba(0, 229, 255, 0.1); border: 1px solid #00e5ff; color: white; }

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

# ==========================================
# ⚙️ CONFIGURACIÓN DE JSONBIN.IO
# ==========================================
JSONBIN_BIN_ID = "6a9155e5f5f4af5e294d311b"
JSONBIN_API_KEY = "$2a$10$6I7nVD3OyqopEu07qX3opevvL7qmSu8n3xqC1acoVVrCidjJBIHoK"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
ESCUDOS_DIR = ASSETS_DIR / "escudos"
BALON_PATH = ASSETS_DIR / "balon.png"
CHAMPIONS_LOGO_PATH = ASSETS_DIR / "Champions.png"

# ==========================================
# ⚙️ CONFIGURACIÓN DE EQUIPOS
# ==========================================
EQUIPOS = [
    {
        "nombre": "BASS-T-NATION UNITED",
        "manager": "Noya",
        "bombo": 1,
        "teamid": "5f5612b297bff0563e446c9f",
    },
    {
        "nombre": "APOEL BARCELÓ C.F.",
        "manager": "Juanma",
        "bombo": 1,
        "teamid": "66aff83db42d2f289215c3a0",
    },
    {
        "nombre": "AL-LARIK-APAPA",
        "manager": "Ale",
        "bombo": 1,
        "teamid": "5b699f437f9f7e021a9f71b4",
    },
    {
        "nombre": "OLYMPIQUE DE MARMÀSELLA",
        "manager": "Salva",
        "bombo": 2,
        "teamid": "6a6c777d9ca13a2cab53c9dd",
    },
    {
        "nombre": "LA CASA DE LA JUVENTUS",
        "manager": "Sergio",
        "bombo": 2,
        "teamid": "5b5f0e425077cd3775d96f66",
    },
    {
        "nombre": "AC PONIENTE",
        "manager": "Nando",
        "bombo": 2,
        "teamid": "5b61c6e32bfc27e41987c9b1",
    },
    {
        "nombre": "RAYO MALAYO",
        "manager": "Victor",
        "bombo": 3,
        "teamid": "5b617d622bfc27e4198654de",
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
        "nombre": "ESTRELLA GALICIA CF",
        "manager": "Francis",
        "bombo": 4,
        "teamid": "689653326d85ec6bdab02609",
    },
    {
        "nombre": "WINE & HORSES",
        "manager": "Jose",
        "bombo": 4,
        "teamid": "5b757e0520eda94909ef8326",
    },
    {
        "nombre": "MACCABI DE LEVANTÁ",
        "manager": "Alfon",
        "bombo": 4,
        "teamid": "6898cb62c4de884fb3611bd7",
    },
    {
        "nombre": "EMERITA DISGUSTA!",
        "manager": "Miguel",
        "bombo": 4,
        "teamid": "6a6c8a3d3214f32ca53c27d5",
    },
]


def obtener_ruta_escudo(team_id):
    if ESCUDOS_DIR.exists():
        for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
            escudo_local = ESCUDOS_DIR / f"{team_id}{ext}"
            if escudo_local.exists():
                return str(escudo_local)
    return None


def obtener_imagen_base64(path_img):
    if os.path.exists(path_img):
        with open(path_img, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return None


SPANISH_TZ = ZoneInfo("Europe/Madrid")


def obtener_datos_nube():
    try:
        headers = {"X-Master-Key": JSONBIN_API_KEY}
        response = requests.get(JSONBIN_URL, headers=headers)
        if response.status_code == 200:
            return response.json().get("record", {})
    except Exception as e:
        print(f"Error al leer de JSONBin: {e}")
    return {}


datos_nube = obtener_datos_nube()

DEFAULT_TARGET_TIME = datetime(2026, 8, 27, 20, 0, 0, tzinfo=SPANISH_TZ)
if datos_nube and "target_time" in datos_nube:
    try:
        TARGET_TIME = datetime.strptime(
            datos_nube["target_time"], "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=SPANISH_TZ)
    except:
        TARGET_TIME = DEFAULT_TARGET_TIME
else:
    TARGET_TIME = DEFAULT_TARGET_TIME


def guardar_seed_nube(seed_val):
    try:
        payload = {
            "target_time": TARGET_TIME.strftime("%Y-%m-%d %H:%M:%S"),
            "seed": seed_val,
            "drawed": 1,
        }
        headers = {
            "Content-Type": "application/json",
            "X-Master-Key": JSONBIN_API_KEY,
        }
        requests.put(JSONBIN_URL, json=payload, headers=headers)
    except Exception as e:
        print(f"Excepción al guardar semilla: {e}")


def ejecutar_sorteo_champions(eqs):
    bombos = {1: [], 2: [], 3: [], 4: []}
    for e in eqs:
        bombos[e["bombo"]].append(e)
    for b in bombos:
        random.shuffle(bombos[b])
    grupos = {"GRUPO A": [], "GRUPO B": [], "GRUPO C": []}
    try:
        for b in [1, 2, 3]:
            grupos["GRUPO A"].append(bombos[b][0])
            grupos["GRUPO B"].append(bombos[b][1])
            grupos["GRUPO C"].append(bombos[b][2])
        grupos["GRUPO A"].append(bombos[4][0])
        grupos["GRUPO B"].append(bombos[4][1])
        grupos["GRUPO C"].append(bombos[4][2])
        grupos["GRUPO C"].append(bombos[4][3])
        return grupos
    except IndexError:
        return None


def generar_jornadas_grupo_ab(equipos):
    l = list(equipos)
    n = len(l)
    jornadas = []
    teams = l[:]
    for r in range(n - 1):
        jornada_partidos = []
        for i in range(n // 2):
            t1 = teams[i]
            t2 = teams[n - 1 - i]
            jornada_partidos.append((t1, t2))
        jornadas.append(jornada_partidos)
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    jornadas_vuelta = [[(t2, t1) for (t1, t2) in j] for j in reversed(jornadas)]
    return jornadas + jornadas_vuelta


def generar_jornadas_grupo_c(equipos):
    l = list(equipos)
    l_dummy = l + [None]
    n = len(l_dummy)
    jornadas = []
    teams = l_dummy[:]
    for r in range(n - 1):
        jornada_partidos = []
        for i in range(n // 2):
            t1 = teams[i]
            t2 = teams[n - 1 - i]
            if t1 is not None and t2 is not None:
                jornada_partidos.append((t1, t2))
        jornadas.append(jornada_partidos)
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    jornada_6 = [
        ({"nombre": "1º GRUPO C"}, {"nombre": "4º GRUPO C"}),
        ({"nombre": "2º GRUPO C"}, {"nombre": "3º GRUPO C"}),
    ]
    jornadas.append(jornada_6)
    return jornadas


# --- RECURSOS EN BASE64 ---
balon_b64 = obtener_imagen_base64(BALON_PATH)
if balon_b64:
    ball_tag = f'<img src="{balon_b64}" class="title-ball" />'
    img_anim = f'<img src="{balon_b64}" style="width: 35px; height: 35px;" />'
else:
    ball_tag = '<span style="font-size: 30px;">⚽</span>'
    img_anim = "⚽"

logo_b64 = obtener_imagen_base64(CHAMPIONS_LOGO_PATH)
if logo_b64:
    logo_tag = f'<div style="text-align: center; margin-bottom: 10px;"><img src="{logo_b64}" style="max-height: 100px; object-fit: contain;" /></div>'
else:
    logo_tag = ""

if logo_tag:
    st.markdown(logo_tag, unsafe_allow_html=True)

header_html = f'<div class="champions-header-container">{ball_tag}<div class="title-texts-wrapper"><div class="app-title-line">SORTEO CHAMPIONS</div><div class="app-title-line">MANDINGUERA 26/27</div></div>{ball_tag}</div>'
st.markdown(header_html, unsafe_allow_html=True)
st.write("")

ahora = datetime.now(SPANISH_TZ)

if ahora < TARGET_TIME:
    tiempo_restante = TARGET_TIME - ahora
    total_segundos = max(0, int(tiempo_restante.total_seconds()))
    horas, resto = divmod(total_segundos, 3600)
    minutos, segundos = divmod(resto, 60)

    countdown_html = f'<div class="countdown-container"><div class="countdown-box"><div class="countdown-value">{horas:02d}</div><div class="countdown-label">Horas</div></div><div class="countdown-separator">:</div><div class="countdown-box"><div class="countdown-value">{minutos:02d}</div><div class="countdown-label">Minutos</div></div><div class="countdown-separator">:</div><div class="countdown-box"><div class="countdown-value">{segundos:02d}</div><div class="countdown-label">Segundos</div></div></div>'
    st.markdown(countdown_html, unsafe_allow_html=True)

    st.write("---")
    st.markdown("<h2>📋 Composición de los Bombos</h2>", unsafe_allow_html=True)
    st.write("")

    bombos = {1: [], 2: [], 3: [], 4: []}
    for eq in EQUIPOS:
        bombos[eq["bombo"]].append(eq)


    def render_bombo(b_num, lista_equipos):
        equipos_html = ""
        for m in lista_equipos:
            ruta_img = obtener_ruta_escudo(m["teamid"])
            if ruta_img:
                with open(ruta_img, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                escudo_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 30px; height: 30px; object-fit: contain; margin-right: 12px;">'
            else:
                escudo_html = (
                    '<span style="font-size: 20px; margin-right: 12px;">🛡️</span>'
                )

            equipos_html += f'<div style="display: flex; align-items: center; padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 1rem;">{escudo_html}<span style="color: #ffffff; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{m["nombre"]}">{m["nombre"]}</span></div>'

        bombo_html = f'<div style="background: rgba(0, 15, 40, 0.85); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 10px; overflow: hidden; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);"><div style="background: linear-gradient(90deg, #00287a, #0045bc); padding: 10px; text-align: center; font-weight: 900; font-size: 1.1rem; letter-spacing: 1px; color: #ffffff; border-bottom: 2px solid #00e5ff;">BOMBO {b_num}</div><div style="padding: 10px;">{equipos_html}</div></div>'
        st.markdown(bombo_html, unsafe_allow_html=True)


    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        render_bombo(1, bombos[1])
    with row1_col2:
        render_bombo(2, bombos[2])

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        render_bombo(3, bombos[3])
    with row2_col2:
        render_bombo(4, bombos[4])

    time.sleep(1)
    st.rerun()

else:
    st.success("🎉 ¡El Sorteo ha finalizado! Estos son los grupos oficiales.")

    datos_nube_fresco = obtener_datos_nube()
    drawed_flag = (
        datos_nube_fresco.get("drawed", 0) if datos_nube_fresco else 0
    )
    cloud_seed = (
        datos_nube_fresco.get("seed", None) if datos_nube_fresco else None
    )

    if drawed_flag == 1 and cloud_seed is not None:
        random.seed(int(cloud_seed))
    else:
        nueva_seed = random.randint(1, 999999)
        random.seed(nueva_seed)
        guardar_seed_nube(nueva_seed)

    resultado_actual = ejecutar_sorteo_champions(EQUIPOS)

    if resultado_actual:
        anim_html = f'<div style="text-align: center; position: relative; height: 60px; overflow: hidden; margin-bottom: 20px;"><span class="falling-ball" style="left: 15%; animation-delay: 0s;">{img_anim}</span><span class="falling-ball" style="left: 30%; animation-delay: 0.8s;">{img_anim}</span><span class="falling-ball" style="left: 50%; animation-delay: 0.3s;">{img_anim}</span><span class="falling-ball" style="left: 70%; animation-delay: 1.2s;">{img_anim}</span><span class="falling-ball" style="left: 85%; animation-delay: 0.5s;">{img_anim}</span></div>'
        st.markdown(anim_html, unsafe_allow_html=True)

        cols = st.columns(3)
        for i, (grupo, miembros) in enumerate(resultado_actual.items()):
            with cols[i]:
                equipos_html = ""
                for idx, m in enumerate(miembros, 1):
                    ruta_img = obtener_ruta_escudo(m["teamid"])
                    if ruta_img:
                        with open(ruta_img, "rb") as f:
                            img_b64 = base64.b64encode(f.read()).decode()
                        escudo_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 26px; height: 26px; object-fit: contain; margin-right: 10px;">'
                    else:
                        escudo_html = '<span style="font-size: 18px; margin-right: 10px;">🛡️</span>'

                    equipos_html += f'<div style="display: flex; align-items: center; padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.9rem;"><span style="color: #00e5ff; font-weight: bold; width: 18px; text-align: center; margin-right: 5px;">{idx}</span>{escudo_html}<span style="color: #ffffff; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{m["nombre"]}</span></div>'

                grupo_html = f'<div style="background: rgba(0, 15, 40, 0.85); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 10px; overflow: hidden; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);"><div style="background: linear-gradient(90deg, #00287a, #0045bc); padding: 10px; text-align: center; font-weight: 900; font-size: 1.1rem; letter-spacing: 1px; color: #ffffff; border-bottom: 2px solid #00e5ff;">🏆 {grupo}</div><div style="padding: 4px 8px 8px 8px;">{equipos_html}</div></div>'
                st.markdown(grupo_html, unsafe_allow_html=True)

        st.write("---")
        st.markdown(
            "<h2>📅 Calendario de Enfrentamientos</h2>", unsafe_allow_html=True
        )
        st.write("")

        jornadas_por_grupo = {}
        for nombre, miembros in resultado_actual.items():
            if nombre in ["GRUPO A", "GRUPO B"]:
                jornadas_por_grupo[nombre] = generar_jornadas_grupo_ab(miembros)
            elif nombre == "GRUPO C":
                jornadas_por_grupo[nombre] = generar_jornadas_grupo_c(miembros)

        max_jornadas = max(len(j) for j in jornadas_por_grupo.values())

        for j_idx in range(max_jornadas):
            groups_html_content = ""
            for nombre_grupo, miembros in resultado_actual.items():
                jornadas_g = jornadas_por_grupo[nombre_grupo]
                if j_idx < len(jornadas_g):
                    partidos = jornadas_g[j_idx]
                    partidos_html = ""
                    for t1, t2 in partidos:
                        t1_id = t1.get("teamid")
                        if t1_id:
                            ruta_img1 = obtener_ruta_escudo(t1_id)
                            if ruta_img1:
                                with open(ruta_img1, "rb") as f:
                                    t1_b64 = base64.b64encode(f.read()).decode()
                                t1_escudo = f'<img src="data:image/png;base64,{t1_b64}" style="width: 20px; height: 20px; object-fit: contain; margin-right: 6px; vertical-align: middle;">'
                            else:
                                t1_escudo = '<span style="font-size: 14px; margin-right: 6px;">🛡️</span>'
                        else:
                            t1_escudo = '<span style="font-size: 14px; margin-right: 6px;">⭐</span>'

                        t2_id = t2.get("teamid")
                        if t2_id:
                            ruta_img2 = obtener_ruta_escudo(t2_id)
                            if ruta_img2:
                                with open(ruta_img2, "rb") as f:
                                    t2_b64 = base64.b64encode(f.read()).decode()
                                t2_escudo = f'<img src="data:image/png;base64,{t2_b64}" style="width: 20px; height: 20px; object-fit: contain; margin-left: 6px; vertical-align: middle;">'
                            else:
                                t2_escudo = '<span style="font-size: 14px; margin-left: 6px;">🛡️</span>'
                        else:
                            t2_escudo = '<span style="font-size: 14px; margin-left: 6px;">⭐</span>'

                        partidos_html += f'<div style="font-size: 0.85rem; padding: 6px 8px; margin-bottom: 6px; background: rgba(0,0,0,0.35); border-radius: 6px; display: flex; justify-content: space-between; align-items: center; border-left: 2px solid #00e5ff;"><div style="display: flex; align-items: center; width: 44%; overflow: hidden;">{t1_escudo}<span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #ffffff;" title="{t1["nombre"]}">{t1["nombre"]}</span></div><span style="color: #00e5ff; font-weight: bold; width: 12%; text-align: center;">VS</span><div style="display: flex; align-items: center; justify-content: flex-end; width: 44%; overflow: hidden;"><span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #ffffff; text-align: right;" title="{t2["nombre"]}">{t2["nombre"]}</span>{t2_escudo}</div></div>'

                    descansa_html = ""
                    if nombre_grupo == "GRUPO C" and j_idx < 5:
                        equipos_jugando = set()
                        for t1, t2 in partidos:
                            equipos_jugando.add(t1["nombre"])
                            equipos_jugando.add(t2["nombre"])
                        equipo_descansa = [
                            m
                            for m in miembros
                            if m["nombre"] not in equipos_jugando
                        ]
                        if equipo_descansa:
                            desc = equipo_descansa[0]
                            desc_id = desc.get("teamid")
                            desc_escudo = "💤"
                            if desc_id:
                                ruta_desc = obtener_ruta_escudo(desc_id)
                                if ruta_desc:
                                    with open(ruta_desc, "rb") as f:
                                        desc_b64 = base64.b64encode(
                                            f.read()
                                        ).decode()
                                    desc_escudo = f'<img src="data:image/png;base64,{desc_b64}" style="width: 16px; height: 16px; object-fit: contain; vertical-align: middle; margin-right: 4px;">'

                            descansa_html = f'<div style="font-size: 0.8rem; color: #b0c4de; background: rgba(0,229,255,0.06); border: 1px dashed rgba(0,229,255,0.25); border-radius: 6px; padding: 4px 6px; margin-top: 6px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="Descansa: {desc["nombre"]}">{desc_escudo} <b>Descansa:</b> {desc["nombre"]}</div>'

                    group_content = f"{partidos_html}{descansa_html}"
                else:
                    group_content = '<div style="font-size: 0.85rem; color: #888; text-align: center; font-style: italic; padding: 6px;">Sin partido</div>'

                # Sin caja individual de grupo, manteniendo solo el texto del grupo y su contenido limpio
                groups_html_content += f'<div style="flex: 1; min-width: 280px; padding: 5px;"><div style="color: #00e5ff; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; text-align: center; text-transform: uppercase; letter-spacing: 1px;">{nombre_grupo}</div>{group_content}</div>'

            jornada_master_html = f'<div style="background: rgba(0, 15, 40, 0.85); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 10px; overflow: hidden; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);"><div style="background: linear-gradient(90deg, #00287a, #0045bc); padding: 12px; text-align: center; font-weight: 900; font-size: 1.15rem; letter-spacing: 1px; color: #ffffff; border-bottom: 2px solid #00e5ff; text-transform: uppercase;">Jornada {j_idx + 1}</div><div style="padding: 15px; display: flex; gap: 15px; flex-wrap: wrap; justify-content: center;">{groups_html_content}</div></div>'
            st.markdown(jornada_master_html, unsafe_allow_html=True)
