# Inventario TI - Frontend MVP

Interfaz de usuario web construida con **Streamlit** en Python para la visualización y gestión del inventario de activos TI. Esta aplicación actúa como un cliente ligero que consume la API REST del backend.

## 🚀 Características

- **Diseño funcional estilo dashboard:** Tablas interactivas con capacidad de filtrado, ordenamiento y búsqueda.
- **Cruce de datos automático:** Consulta los endpoints de la API (`/devices/`, `/locations/`, `/manufacturers/`) para presentar nombres legibles en lugar de IDs de base de datos.
- **Mapeo de columnas dinámico:** Los títulos de la tabla son personalizables sin alterar la estructura del backend.
- **Manejo de errores:** Resiliencia ante fallas de conexión o registros incompletos (`Sin Asignar`).

## 📁 Estructura del Módulo

```text
frontend/
├── app.py              # Aplicación principal de Streamlit
├── Dockerfile          # Construcción en dos etapas (Multi-stage)
└── requirements.txt    # Dependencias de Python (streamlit, requests, pandas)
```

## ⚙️ Variables de Entorno

|**Variable**|**Descripción**|**Valor por defecto**|
|---|---|---|
|`API_URL`|URL base para la comunicación con la API de FastAPI|`http://localhost:8000`|
## 🐳 Construcción con Docker

Para construir y probar el contenedor de forma independiente:

```Bash
docker build -t inventario_ti_frontend:latest .
docker run -d -p 8501:8501 -e API_URL="[http://host.docker.internal:8000](http://host.dock
```
