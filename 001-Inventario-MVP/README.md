# Sistema de Inventario de Activos TI (MVP)

Plataforma integral para la gestión de infraestructura y activos de Red/TI. El sistema está diseñado en una arquitectura de microservicios con backend asíncrono, persistencia relacional, interfaz web interactiva y métricas de observabilidad integradas.

## 🏗️ Arquitectura y Tecnologías

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) + [SQLModel](https://sqlmodel.tiangolo.com/) (ORMs con type hinting estricto).
- **Frontend:** [Streamlit](https://streamlit.io/) (Dashboard web en Python).
- **Base de Datos:** [PostgreSQL 15](https://www.postgresql.org/) sobre imagen Alpine Linux.
- **Métricas:** Instrumentation con `prometheus-fastapi-instrumentator` (Endpoint `/metrics`).
- **Orquestación:** Docker Compose con compilación multi-etapa (*multi-stage builds*).

---

## 📂 Estructura del Proyecto

```text
.
├── backend/
│   ├── main.py             # Aplicación FastAPI, modelos SQLModel y endpoints REST
│   └── Dockerfile          # Configuración del contenedor del backend
├── frontend/
│   ├── app.py              # Interfaz web de Streamlit
│   ├── Dockerfile          # Dockerfile multi-stage para el frontend
│   └── requirements.txt    # Librerías del cliente web
├── docker-compose.yml      # Configuración y orquestación de servicios
├── .env.example            # Plantilla de variables de entorno
└── README.md               # Documentación general
````

## ⚙️ Configuración del Entorno (`.env`)

Copia y edita el `.env.example` o cree un archivo `.env` en la raíz del proyecto con la siguiente configuración:
```bash
# Configuración de Conexión a PostgreSQL
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=  # Ej: inventario_db_prod o 192.168.1.50
POSTGRES_PORT=5432
POSTGRES_DB=

# Referencia a las variables definidas arriba:
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
```

## 🚀 Despliegue Rápido con Docker Compose

### Prerrequisitos

- [ ] Docker Engine y Docker Compose instalados.
- [ ] Red externa de Docker previa creada (`LAB_TYMA`).
- [ ]  
1. **Crear la red docker (si no existe):**
	```Bash
	docker network create \
  --driver bridge \
  --subnet 172.200.0/24 \
  --gateway 172.200.0.1 \
  LAB_TYMA
	```
2. **Levantar todos los servicios:**
    ```Bash
    docker compose up -d --build
    ```
    
3. **Verificar el estado de los contenedores:**
    ```Bash
    docker compose ps
    ```
    
## 🔗 Puertos y Servicios Expuestos

|**Servicio**|**Puerto Host**|**Descripción**|**Acceso Directo**|
|---|---|---|---|
|**Frontend Web**|`8501`|Panel interactivo de administración|[http://localhost:8501](http://localhost:8501/)|
|**API Backend**|`8000`|Documentación Swagger de la API REST|[http://localhost:8000/docs](http://localhost:8000/docs)|
|**Métricas**|`8000`|Endpoint para Prometheus|[http://localhost:8000/metrics](http://localhost:8000/metrics)|
|**PostgreSQL**|`5432`|Base de datos relacional|`localhost:5432`|

## 📌 Endpoints de la API Backend

- `GET /` — Healthcheck de la API.
    
- `GET /metrics` — Exposición de métricas de rendimiento para Prometheus.
    
- `GET /POST /PUT /DELETE /devices/` — CRUD completo de Equipos TI.
    
- `GET /POST /PUT /DELETE /locations/` — CRUD de Ubicaciones Físicas / Sites.
    
- `GET /POST /PUT /DELETE /manufacturers/` — CRUD de Fabricantes (Cisco, Fortinet, etc.).
    
- `GET /POST /DELETE /device-types/` — Categorías de equipamiento.