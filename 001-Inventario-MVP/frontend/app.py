import os
import streamlit as st # pyright: ignore[reportMissingImports]
import requests # pyright: ignore[reportMissingModuleSource, reportMissingImports]
import pandas as pd # pyright: ignore[reportMissingModuleSource, reportMissingImports]
from typing import List, Dict, Any
#Prometheus
import time
from prometheus_client import start_http_server, Counter, Histogram

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA (ESTRICTAMENTE PRIMERO)
# ==========================================
st.set_page_config(page_title="Inventario TI", page_icon="🖥️", layout="wide")

# ==========================================
# MÉTRICAS DE PROMETHEUS
# ==========================================

@st.cache_resource
def init_prometheus(port: int = 9101, addr: str = "0.0.0.0") -> tuple:
    """Inicializa el servidor HTTP y define las métricas de Prometheus.

    Utiliza el decorador @st.cache_resource para garantizar que el servidor y 
    la declaración de métricas se ejecuten una sola vez en la memoria del sistema,
    evitando colisiones de registro en las re-ejecuciones de Streamlit.

    Args:
        port (int, optional): Puerto TCP para exponer las métricas. Por defecto 9101.
        addr (str, optional): Dirección IP a vincular. Por defecto '0.0.0.0'.

    Returns:
        tuple: Tupla con las instancias en caché de (PAGE_VIEWS_TOTAL, API_REQUEST_LATENCY, API_ERRORS_TOTAL).
    """
    start_http_server(port=port, addr=addr)

    page_views = Counter(
        "streamlit_page_views_total", 
        "Número total de ejecuciones o interacciones en la aplicación"
    )
    api_latency = Histogram(
        "frontend_api_request_duration_seconds",
        "Latencia de las peticiones HTTP enviadas hacia el backend",
        ["endpoint"]
    )
    api_errors = Counter(
        "frontend_api_errors_total",
        "Cantidad total de errores al intentar consultar la API",
        ["endpoint"]
    )

    return page_views, api_latency, api_errors


# Recuperar las instancias únicas guardadas en la caché de Streamlit
PAGE_VIEWS_TOTAL, API_REQUEST_LATENCY, API_ERRORS_TOTAL = init_prometheus()

# Incrementar la métrica de visitas en cada ciclo de la interfaz
PAGE_VIEWS_TOTAL.inc()

#---------------------------------

def get_api_url() -> str:
    """Obtiene la URL de la API desde las variables de entorno del contenedor.

    Returns:
        str: La URL base de la API de backend (por defecto "http://localhost:8000" si no se encuentra).
    """
    return os.getenv("API_URL", "http://localhost:8000")

API_URL = get_api_url()

def fetch_data(endpoint: str) -> List[Dict[str, Any]]:
    """Consulta un endpoint específico de la API para obtener un listado de registros.

    Args:
        endpoint (str): El nombre del recurso a consultar (ej. 'devices', 'locations').

    Returns:
        List[Dict[str, Any]]: Una lista de diccionarios con los datos devueltos por la API.

    Raises:
        requests.exceptions.RequestException: Si ocurre un error de red, timeout o
            la API devuelve un código de error HTTP (ej. 404, 500).
    """
    start_time = time.time()
    try:
        response = requests.get(f"{API_URL}/{endpoint}/")
        response.raise_for_status()
        
        duration = time.time() - start_time
        API_REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
        
        return response.json()
    except requests.exceptions.RequestException as e:
        API_ERRORS_TOTAL.labels(endpoint=endpoint).inc()
        raise e

def get_mapped_dataframe(devices: List[Dict[str, Any]], locations: List[Dict[str, Any]], manufacturers: List[Dict[str, Any]]) -> pd.DataFrame:
    """Procesa los datos en crudo para cruzar IDs y renombrar las columnas para la interfaz web.

    Args:
        devices (List[Dict[str, Any]]): Lista de dispositivos obtenidos de la API.
        locations (List[Dict[str, Any]]): Lista de ubicaciones obtenidas de la API.
        manufacturers (List[Dict[str, Any]]): Lista de fabricantes obtenidos de la API.

    Returns:
        pd.DataFrame: Un DataFrame de Pandas con los cruces resueltos y columnas amigables
        listo para ser renderizado en Streamlit.
    """

# 1. Crear diccionarios de mapeo para búsquedas rápidas (O(1))
    loc_map = {loc["id"]: loc["name"] for loc in locations}
    mfg_map = {mfg["id"]: mfg["name"] for mfg in manufacturers}

    # 2. Enriquecer los datos de los dispositivos con los nombres legibles
    for device in devices:
        # Se usa .get() doble para evitar errores si la llave no existe o si el valor es None
        device["location_name"] = loc_map.get(device.get("location_id"), "Sin Asignar")
        device["manufacturer_name"] = mfg_map.get(device.get("manufacturer_id"), "Sin Asignar")

    df = pd.DataFrame(devices)

    # 3. DICCIONARIO DE CONFIGURACIÓN DE COLUMNAS
    # Puedes editar los valores (derecha) sin romper la lógica del sistema (izquierda)
    COLUMN_MAPPING = {
        "hostname": "Nombre del Host",
        "ip_address": "Dirección IP",
        "status": "Estado Operativo",
        "manufacturer_name": "Fabricante",
        "model": "Modelo de Equipo",
        "serial_number": "Número de Serie",
        "location_name": "Sitio / Ubicación"
    }

    if not df.empty:
        # Filtrar solo las columnas que nos interesan mostrar y ordenarlas según el diccionario
        existing_columns = [col for col in COLUMN_MAPPING.keys() if col in df.columns]
        df = df[existing_columns]
        
        # Aplicar el renombramiento de columnas para la visualización
        df = df.rename(columns=COLUMN_MAPPING)

    return df

def main() -> None:
    """Función principal que renderiza la interfaz web del MVP en Streamlit.

    Construye la barra lateral de navegación y la tabla principal interactiva.
    Se encarga de orquestar la obtención de datos y el manejo de errores visuales.

    Returns:
        None: La función se dedica a pintar componentes en la pantalla.
    """

    # --- Barra Lateral ---
    st.sidebar.title("Navegación")
    st.sidebar.button("🏢 Ubicaciones")
    st.sidebar.button("🔌 Dispositivos", type="primary")
    st.sidebar.button("🏷️ Fabricantes")
    st.sidebar.button("💻 Tipos de Dispositivos")

    # --- Área Principal ---
    st.title("Gestión de Dispositivos")
    st.markdown("Visualización cruzada del inventario operativo actual.")

    try:
        # Ejecutar peticiones a los distintos endpoints
        with st.spinner("Cargando datos desde la API..."):
            devices_data = fetch_data("devices") 
            locations_data = fetch_data("locations") 
            manufacturers_data = fetch_data("manufacturers") 

        if devices_data:
            # Procesar el dataframe cruzado
            df = get_mapped_dataframe(devices_data, locations_data, manufacturers_data)
            
            # Renderizar tabla interactiva
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay dispositivos registrados actualmente en la base de datos.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error de comunicación con la base de datos: Verifica que el backend esté ejecutándose.")
        st.code(str(e))


if __name__ == "__main__":
    main()