import streamlit as st
import requests
import os

# La URL apunta al servicio de FastAPI en la red de Docker
API_URL = os.getenv("API_URL", "http://web:8000")

st.set_page_config(page_title="Inventario TI", layout="wide")
st.title("🖥️ Gestión de Inventario TI")

# Crear pestañas para organizar la interfaz
tab_devices, tab_manufacturers = st.tabs(["Dispositivos", "Fabricantes"])

# ==========================================
# PESTAÑA 1: DISPOSITIVOS
# ==========================================
with tab_devices:
    st.header("Dispositivos Registrados")
    
    # 1. GET: Consultar los dispositivos a la API
    response = requests.get(f"{API_URL}/devices/")
    if response.status_code == 200:
        devices = response.json()
        st.dataframe(devices, use_container_width=True)
    else:
        st.error("No se pudieron cargar los dispositivos.")

    st.subheader("Registrar Nuevo Dispositivo")
    
    # Formulario para enviar datos (POST)
    with st.form("new_device_form"):
        hostname = st.text_input("Hostname (ej. SW-CORE-01)")
        ip_address = st.text_input("Dirección IP (ej. 192.168.1.1)")
        serial_number = st.text_input("Número de Serie")
        model = st.text_input("Modelo (ej. Catalyst 9300)")
        
        submitted = st.form_submit_button("Guardar Dispositivo")
        
        if submitted:
            payload = {
                "hostname": hostname,
                "ip_address": ip_address,
                "serial_number": serial_number,
                "model": model,
                "status": "Active"
            }
            # 2. POST: Enviar el nuevo dispositivo a FastAPI
            res = requests.post(f"{API_URL}/devices/", json=payload)
            if res.status_code == 200:
                st.success("¡Dispositivo creado con éxito!")
                st.rerun()  # Recarga la página para mostrar el nuevo item
            else:
                st.error(f"Error al guardar: {res.json().get('detail')}")