import os

# Prometheus
import time
from typing import Any

import pandas as pd  # pyright: ignore[reportMissingModuleSource, reportMissingImports]
import requests  # pyright: ignore[reportMissingModuleSource, reportMissingImports]
import streamlit as st  # pyright: ignore[reportMissingImports]
from prometheus_client import Counter, Histogram, start_http_server

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
    la declaración de métricas se ejecuten una sola vez en la memoria del sistema.

    Args:
        port (int, optional): Puerto TCP para exponer las métricas. Por defecto 9101.
        addr (str, optional): Dirección IP a vincular. Por defecto '0.0.0.0'.

    Returns:
        tuple: Tupla con las instancias en caché de (PAGE_VIEWS_TOTAL, API_REQUEST_LATENCY, API_ERRORS_TOTAL).
    """
    start_http_server(port=port, addr=addr)

    page_views = Counter(
        "streamlit_page_views_total",
        "Número total de ejecuciones o interacciones en la aplicación",
    )
    api_latency = Histogram(
        "frontend_api_request_duration_seconds",
        "Latencia de las peticiones HTTP enviadas hacia el backend",
        ["endpoint"],
    )
    api_errors = Counter(
        "frontend_api_errors_total",
        "Cantidad total de errores al intentar consultar la API",
        ["endpoint"],
    )

    return page_views, api_latency, api_errors


# Recuperar las instancias únicas guardadas en la caché de Streamlit
PAGE_VIEWS_TOTAL, API_REQUEST_LATENCY, API_ERRORS_TOTAL = init_prometheus()

# Incrementar la métrica de visitas en cada ciclo de la interfaz
PAGE_VIEWS_TOTAL.inc()

# ---------------------------------


def get_api_url() -> str:
    """Obtiene la URL de la API desde las variables de entorno del contenedor.

    Args:
        Ninguno.

    Returns:
        str: La URL base de la API de backend (por defecto "http://localhost:8000").
    """
    return os.getenv("API_URL", "http://localhost:8000")


API_URL = get_api_url()


def fetch_data(endpoint: str) -> list[dict[str, Any]]:
    """Consulta un endpoint específico de la API para obtener un listado de registros.

    Args:
        endpoint (str): El nombre del recurso a consultar (ej. 'devices', 'locations').

    Raises:
        requests.exceptions.RequestException: Si ocurre un error de red o HTTP.

    Returns:
        list[dict[str, Any]]: Una lista de diccionarios con los datos devueltos por la API.
    """
    start_time = time.time()
    try:
        response = requests.get(f"{API_URL}/{endpoint}/")
        response.raise_for_status()

        duration = time.time() - start_time
        API_REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

        return response.json()

    except requests.exceptions.RequestException:
        API_ERRORS_TOTAL.labels(endpoint=endpoint).inc()
        raise


def get_mapped_dataframe(
    devices: list[dict[str, Any]],
    locations: list[dict[str, Any]],
    manufacturers: list[dict[str, Any]],
) -> pd.DataFrame:
    """Procesa los datos en crudo para cruzar IDs y renombrar las columnas para la interfaz web.

    Args:
        devices (list[dict[str, Any]]): Lista de dispositivos obtenidos de la API.
        locations (list[dict[str, Any]]): Lista de ubicaciones obtenidas de la API.
        manufacturers (list[dict[str, Any]]): Lista de fabricantes obtenidos de la API.

    Returns:
        pd.DataFrame: Un DataFrame de Pandas con los cruces resueltos y columnas amigables.
    """

    # 1. Crear diccionarios de mapeo para búsquedas rápidas (O(1))
    loc_map = {loc["id"]: loc["name"] for loc in locations}
    mfg_map = {mfg["id"]: mfg["name"] for mfg in manufacturers}

    # 2. Enriquecer los datos de los dispositivos con los nombres legibles
    for device in devices:
        # Se usa .get() doble para evitar errores si la llave no existe o si el valor es None
        device["location_name"] = loc_map.get(device.get("location_id"), "Sin Asignar")
        device["manufacturer_name"] = mfg_map.get(
            device.get("manufacturer_id"), "Sin Asignar"
        )

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
        "location_name": "Sitio / Ubicación",
    }

    if not df.empty:
        # Filtrar solo las columnas que nos interesan mostrar y ordenarlas según el diccionario
        existing_columns = [col for col in COLUMN_MAPPING if col in df.columns]
        df = df[existing_columns]

        # Aplicar el renombramiento de columnas para la visualización
        df = df.rename(columns=COLUMN_MAPPING)

    return df


def render_devices() -> None:
    """Renderiza la vista principal de Gestión de Dispositivos.

    Obtiene dispositivos, ubicaciones y fabricantes, cruza los datos con
    la función get_mapped_dataframe y los muestra en una tabla interactiva.

    Args:
        Ninguno.

    Returns:
        None: Renderiza componentes visuales en Streamlit.
    """
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
        st.error(
            "Error de comunicación con la base de datos: Verifica que el backend esté ejecutándose."
        )
        st.code(str(e))


def render_locations() -> None:
    """Renderiza la vista de Gestión de Ubicaciones.

    Obtiene el listado de sitios desde el endpoint de ubicaciones y los expone.

    Args:
        Ninguno.

    Returns:
        None: Renderiza componentes visuales en Streamlit.
    """
    st.title("Gestión de Ubicaciones")
    st.markdown("Directorio de sitios y sucursales operativas.")

    try:
        with st.spinner("Cargando ubicaciones..."):
            locations_data = fetch_data("locations")

        if locations_data:
            df = pd.DataFrame(locations_data)

            # Mapeo específico para las columnas de las ubicaciones
            COLUMN_MAPPING = {
                "id": "ID",
                "name": "Nombre de la Ubicación",
                "site_code": "Codigo de Sitio",
            }

            existing_columns = [col for col in COLUMN_MAPPING if col in df.columns]
            if existing_columns:
                df = df[existing_columns].rename(columns=COLUMN_MAPPING)

            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay ubicaciones registradas actualmente en la base de datos.")

    except requests.exceptions.RequestException as e:
        st.error("Error al cargar el directorio de ubicaciones.")
        st.code(str(e))


def render_manufacturers() -> None:
    """Renderiza la vista de Gestión de Fabricantes.

    Obtiene el listado de fabricantes desde el endpoint de fabricantes y los expone.

    Args:
        Ninguno.

    Returns:
        None: Renderiza componentes visuales en Streamlit.
    """
    st.title("Gestión de Fabricantes")
    st.markdown("Directorio de fabricantes y proveedores.")

    try:
        with st.spinner("Cargando fabricantes..."):
            manufacturers_data = fetch_data("manufacturers")

        if manufacturers_data:
            df = pd.DataFrame(manufacturers_data)

            # Mapeo específico para las columnas de los fabricantes
            COLUMN_MAPPING = {
                "id": "ID",
                "name": "Fabricante",
            }

            existing_columns = [col for col in COLUMN_MAPPING if col in df.columns]
            if existing_columns:
                df = df[existing_columns].rename(columns=COLUMN_MAPPING)

            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay fabricantes registrados actualmente en la base de datos.")

    except requests.exceptions.RequestException as e:
        st.error("Error al cargar el directorio de fabricantes.")
        st.code(str(e))


def main() -> None:
    """Función principal que renderiza la interfaz web del MVP en Streamlit.

    Construye la barra lateral de navegación con estado de sesión para el
    enrutamiento de las diferentes pantallas.

    Args:
        Ninguno.

    Returns:
        None: La función se dedica a pintar componentes en la pantalla.
    """
    if "current_view" not in st.session_state:
        st.session_state.current_view = "Dispositivos"

    st.sidebar.title("Navegación")

    if st.sidebar.button("🏢 Ubicaciones", use_container_width=True):
        st.session_state.current_view = "Ubicaciones"
    if st.sidebar.button("🔌 Dispositivos", use_container_width=True):
        st.session_state.current_view = "Dispositivos"
    if st.sidebar.button("🏷️ Fabricantes", use_container_width=True):
        st.session_state.current_view = "Fabricantes"
    if st.sidebar.button("💻 Tipos de Dispositivos", use_container_width=True):
        st.session_state.current_view = "Tipos de Dispositivos"

    # Enrutamiento principal
    if st.session_state.current_view == "Dispositivos":
        render_devices()
    elif st.session_state.current_view == "Ubicaciones":
        render_locations()
    elif st.session_state.current_view == "Fabricantes":
        render_manufacturers()
    elif st.session_state.current_view == "Tipos de Dispositivos":
        st.title("Tipos de Dispositivos")
        st.info("Vista en construcción...")


if __name__ == "__main__":
    main()
