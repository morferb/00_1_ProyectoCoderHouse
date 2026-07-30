import os
import streamlit as st # pyright: ignore[reportMissingImports]
import requests # pyright: ignore[reportMissingModuleSource, reportMissingImports]
import pandas as pd # pyright: ignore[reportMissingModuleSource, reportMissingImports]
from typing import List, Dict, Any

def get_api_url() -> str:
    """Obtiene la URL de la API desde las variables de entorno del contenedor.

    Returns:
        str: La URL base de la API de backend (por defecto "http://localhost:8000" si no se encuentra).
    """
    return os.getenv("API_URL", "http://localhost:8000")

API_URL = get_api_url()

# El resto de tus funciones fetch_devices() y main() irían a partir de aquí...

def fetch_devices() -> List[Dict[str, Any]]:
    """Obtiene la lista de dispositivos desde la API de Inventario TI.

    Realiza una petición GET al endpoint /devices/ y formatea la respuesta
    para ser consumida por la interfaz web.

    Returns:
        List[Dict[str, Any]]: Una lista de diccionarios, donde cada diccionario 
        representa los datos operativos de un dispositivo (hostname, IP, serial, etc.).

    Raises:
        requests.exceptions.RequestException: Si ocurre un error de conexión, 
        timeout o la API devuelve un código de error HTTP.
    """
    response = requests.get(f"{API_URL}/devices/")
    response.raise_for_status()
    return response.json()

def main() -> None:
    """Ejecuta y renderiza la interfaz web del MVP utilizando Streamlit.

    Configura el diseño de la página, construye un panel lateral de navegación
    inspirado en el estilo de NetBox y despliega una tabla de datos interactiva 
    con los dispositivos registrados en el sistema.

    Returns:
        None: La función no retorna datos, se encarga de pintar la UI.
    """
    st.set_page_config(page_title="Inventario TI", layout="wide")

    # Panel lateral de navegación
    st.sidebar.title("Navegación")
    st.sidebar.button("🏢 Ubicaciones")
    st.sidebar.button("🏷️ Fabricantes")
    st.sidebar.button("💻 Tipos de Dispositivos")
    st.sidebar.button("🔌 Dispositivos", type="primary")

    st.title("Gestión de Dispositivos")
    st.markdown("Vista general del inventario operativo consultando el backend de FastAPI.")

    try:
        devices = fetch_devices()
        if devices:
            # Pandas permite que Streamlit renderice una tabla rica en funcionalidades (ordenar, buscar)
            df = pd.DataFrame(devices)
            
            # Reordenamos columnas para dar prioridad visual al hostname e IP
            column_order = ["id", "hostname", "ip_address", "status", "serial_number", "model", "manufacturer_id", "location_id"]
            
            # Filtramos para mostrar solo las columnas que existan en el DataFrame
            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay dispositivos registrados actualmente en la base de datos.")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error de comunicación con la API: {e}")

if __name__ == "__main__":
    main()