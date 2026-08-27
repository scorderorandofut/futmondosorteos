from datetime import datetime
import json
import random
import requests
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Sorteo Champions Mandinguera", page_icon="⚽", layout="wide"
)

# 🌐 PEGA AQUÍ TU URL DE NPOINT.IO (o guárdala en st.secrets)
NPOINT_URL = st.secrets.get(
    "NPOINT_URL", "https://api.npoint.io/8bb91db2ed41d4d64582"
)  # <--- Cambia esto por tu enlace de npoint.io


# Funciones para leer y escribir en la nube
def cargar_datos_nube():
  try:
    response = requests.get(NPOINT_URL)
    if response.status_code == 200:
      return response.json()
  except:
    pass
  return {"target_time": "", "equipos": [], "resultado": None}


def guardar_datos_nube(datos):
  try:
    headers = {"Content-Type": "application/json"}
    requests.post(NPOINT_URL, json=datos, headers=headers)
  except Exception as e:
    st.error(f"Error al guardar en la nube: {e}")


st.title("⚽ Sorteo Champions Mandinguera - Futmondo 2026/27 (Cloud)")
st.write(
    "Sorteo en directo sincronizado en la nube. Configura la fecha y hora; el"
    " resultado se generará automáticamente y en secreto al expirar la cuenta"
    " atrás."
)

# Equipos oficiales de la Champions Mandinguera
equipos_default_texto = """AC PONIENTE, Nando, 1
AL-LARIK-APAPA, Ale, 1
APOEL BARCELÓ C.F., Juanma, 1
BASS-T-NATION UNITED, Noya, 2
CSKA LAROPA, Gonzalo, 2
EMERITA DISGUSTA!, Miguel, 2
ESTRELLA GALICIA CF, Francis, 3
LA CASA DE LA JUVENTUS, Sergio, 3
LA MÉRIDA GUSTO FC, Javi, 3
MACCABI DE LEVANTÁ, Alfon, 4
OLYMPIQUE DE MARMÀSELLA, Salva, 4
RAYO MALAYO, Victor, 4
WINE & HORSE, Jose, 4"""

# --- PANEL DE CONFIGURACIÓN (ADMIN) ---
with st.sidebar:
  st.header("⚙️ Configuración Cloud")
  fecha_sorteo = st.date_input("Fecha del Sorteo")
  hora_sorteo = st.time_input("Hora del Sorteo")
  target_datetime = datetime.combine(fecha_sorteo, hora_sorteo)

  st.divider()
  st.subheader("👥 Equipos y Bombos")
  equipos_texto = st.text_area(
      "Lista de participantes:", value=equipos_default_texto, height=280
  )

  if st.button("💾 Sincronizar y Programar en la Nube", type="primary"):
    lista_equipos = []
    for linea in equipos_texto.strip().split("\n"):
      partes = [p.strip() for p in linea.split(",")]
      if len(partes) >= 3:
        lista_equipos.append({
            "nombre": partes[0],
            "manager": partes[1],
            "bombo": int(partes[2]),
        })

    datos_nuevos = {
        "target_time": target_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "equipos": lista_equipos,
        "resultado": None,  # Mantiene el secreto en la nube
    }
    guardar_datos_nube(datos_nuevos)
    st.success("¡Configuración guardada en la nube con éxito!")
    st.rerun()

  st.markdown("---")
  if st.button("🔄 Reiniciar Sorteo en la Nube"):
    datos_vaciados = {"target_time": "", "equipos": [], "resultado": None}
    guardar_datos_nube(datos_vaciados)
    st.success("Sorteo reiniciado.")
    st.rerun()

# --- LÓGICA PRINCIPAL DE LA VISTA ---
datos_actuales = cargar_datos_nube()

if not datos_actuales or not datos_actuales.get("target_time"):
  st.warning(
      "⚠️ Aún no hay ningún sorteo programado en la nube. Configúralo en el"
      " panel lateral."
  )
else:
  target_time = datetime.strptime(
      datos_actuales["target_time"], "%Y-%m-%d %H:%M:%S"
  )
  ahora = datetime.now()

  if ahora < target_time:
    st.info(
        "⏳ El sorteo en directo está programado para el:"
        f" **{datos_actuales['target_time']}**"
    )

    # Cuenta atrás
    tiempo_restante = target_time - ahora
    horas, resto = divmod(int(tiempo_restante.total_seconds()), 3600)
    minutos, segundos = divmod(resto, 60)
    dias, horas = divmod(horas, 24)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Días", dias)
    col2.metric("Horas", horas)
    col3.metric("Minutos", minutos)
    col4.metric("Segundos", segundos)

    st.write("---")
    st.subheader(
        "📋 Equipos apuntados para la Champions Mandinguera (Ocultos hasta el"
        " sorteo):"
    )
    for eq in datos_actuales["equipos"]:
      st.text(
          f"• {eq['nombre']} (Manager: {eq['manager']}) - Bombo {eq['bombo']}"
      )

    if st.button("🔄 Actualizar cuenta atrás"):
      st.rerun()

  else:
    # EL TIEMPO HA LLEGADO: SORTEO EN DIRECTO EN LA NUBE
    st.success(
        "🎉 ¡Llegó la hora! Sorteo en directo de la Champions Mandinguera"
    )

    # Si el resultado es Nulo en la nube, el primer usuario que llegue ejecuta el sorteo y lo sube
    if datos_actuales.get("resultado") is None:
      equipos = datos_actuales["equipos"]

      def ejecutar_sorteo_champions(eqs):
        for _ in range(2000):
          grupos = {"Grupo A": [], "Grupo B": [], "Grupo C": []}
          limites = {"Grupo A": 4, "Grupo B": 4, "Grupo C": 5}

          bombos = {}
          for e in eqs:
            b = e["bombo"]
            if b not in bombos:
              bombos[b] = []
            bombos[b].append(e)

          for b in bombos:
            random.shuffle(bombos[b])

          exito = True
          bombo_keys = sorted(bombos.keys())
          for b in bombo_keys:
            for eq in bombos[b]:
              grupos_disponibles = [
                  g for g in grupos.keys() if len(grupos[g]) < limites[g]
              ]
              if not grupos_disponibles:
                exito = False
                break
              g_elegido = random.choice(grupos_disponibles)
              grupos[g_elegido].append(eq)
            if not exito:
              break

          if exito:
            return grupos
        return None

      resultado_final = ejecutar_sorteo_champions(equipos)
      if resultado_final:
        datos_actuales["resultado"] = resultado_final
        guardar_datos_nube(
            datos_actuales
        )  # Se guarda el resultado en la nube para todos
      else:
        st.error(
            "Error al repartir los equipos. Revisa la distribución de los"
            " bombos."
        )

    # Mostrar resultados definitivos sincronizados de la nube
    if datos_actuales.get("resultado"):
      st.balloons()
      cols = st.columns(3)
      for i, (grupo, miembros) in enumerate(
          datos_actuales["resultado"].items()
      ):
        with cols[i]:
          st.markdown(f"### 🏆 {grupo} ({len(miembros)} equipos)")
          st.divider()
          for m in miembros:
            st.markdown(
                f"⚪ **{m['nombre']}**  \n<sub>👤 {m['manager']} | 🏛️ Bombo"
                f" {m['bombo']}</sub>",
                unsafe_allow_html=True,
            )