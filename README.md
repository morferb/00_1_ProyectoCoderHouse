# 🖥️ Sistema de Inventario TI MVP con Observabilidad Completa

Este proyecto consiste en un **MVP de Inventario de Infraestructura TI** diseñado con una arquitectura basada en microservicios desacoplados. Incluye una interfaz de usuario interactiva estilo NetBox (Streamlit), una API RESTful (FastAPI + SQLModel), persistencia relacional (PostgreSQL) y un **stack dedicado de observabilidad** (Prometheus, Grafana, Exporters) interconectados a través de una red externa de gestión en Docker.

## 🏗️ Arquitectura del Sistema

La solución está dividida en dos planos conceptuales operados mediante instancias independientes de `docker-compose`:

Plaintext

```
====================================================================================
                        RED DOCKER: MGMT - LAB TYMA (External)
====================================================================================
  │
  ├─► [ STACK DE APLICACIÓN ]
  │    │
  │    ├─► FRONTEND (Streamlit)
  │    │    ├── TCP 8501 : UI Web
  │    │    └── TCP 9101 : Métricas Prometheus (/metrics)
  │    │
  │    ├─► BACKEND (FastAPI + SQLModel)
  │    │    └── TCP 8000 : API REST & Métricas Prometheus
  │    │
  │    └─► DATABASE (PostgreSQL)
  │         ├── TCP 5432 : Servicio Base de Datos
  │         └── Volume   : inventario_postgres_data
  │
  └─► [ STACK DE OBSERVABILIDAD ]
       │
       ├─► OBSERVABILITY ALL-IN-ONE
       │    ├── TCP 3000 : Grafana Dashboards
       │    ├── TCP 9090 : Prometheus Server
       │    ├── TCP 9115 : Blackbox Exporter (Sondas ICMP/HTTP)
       │    └── Volumes  : Obs_grafana_data, Obs_prometheus_data
       │
       └─► POSTGRES EXPORTER
            └── TCP 9187 : Métricas de rendimiento de la BD
====================================================================================
```

## 🛠️ Tech Stack

|**Componente**|**Tecnología**|**Descripción / Rol**|
|---|---|---|
|**Frontend**|Python 3.11 / Streamlit|Dashboard interactivo para la gestión y visualización del inventario.|
|**Backend**|Python 3.11 / FastAPI / SQLModel|API RESTful con validación de tipos y ORM relacional.|
|**Base de Datos**|PostgreSQL 15+|Motor de base de datos relacional para almacenamiento permanente.|
|**Monitoreo**|Prometheus|Servidor de scraping y almacenamiento de series temporales (TSDB).|
|**Visualización**|Grafana|Consola unificada de dashboards para métricas del sistema y frontend.|
|**Exporters**|Postgres Exporter / Blackbox|Agentes para métricas internas de BD y monitoreo de disponibilidad de red.|
|**Contenedores**|Docker / Docker Compose|Orquestación en contenedores con _Multi-stage builds_.|

## 📊 Matriz de Puertos y Servicios

|**Servicio**|**Puerto Interno/Host**|**Protocolo**|**Endpoint / Función**|
|---|---|---|---|
|**Frontend UI**|`8501`|TCP|Interfaz gráfica del usuario (Streamlit)|
|**Frontend Metrics**|`9101`|TCP|Servidor de métricas en caché (`/metrics`)|
|**Backend API**|`8000`|TCP|Endpoints REST + Métricas API|
|**PostgreSQL**|`5432`|TCP|Acceso al motor de base de datos|
|**Grafana**|`3000`|TCP|Paneles de control y dashboards|
|**Prometheus**|`9090`|TCP|Consola web y motor de métricas PromQL|
|**Blackbox Exporter**|`9115`|TCP|Sondas de conectividad (Probe ICMP/HTTP)|
|**Postgres Exporter**|`9187`|TCP|Extracción de métricas operativas de PostgreSQL|

## 📁 Estructura del Proyecto

```Plaintext
├── 001-Inventario-MVP
│   ├── backend
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── Mejorar Main.py.md
│   │   └── requirements.txt
│   ├── data
│   │   ├── devices.json.example
│   │   ├── device-types.json.example
│   │   ├── locations.json.exameple
│   │   ├── manufacturers.json.example
│   │   └── Validación de datos en API.md
│   ├── docker-compose.yml
│   ├── frontend
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   └── requirements.txt
│   └── README.md
├── 002_Observabilidad
│   ├── config
│   │   ├── blackbox
│   │   │   └── blackbox.yml
│   │   ├── Dashboard
│   │   │   └── MonitoreoServicios.json
│   │   ├── grafana
│   │   │   └── provisioning
│   │   │       └── datasources
│   │   │           └── datasource.yml
│   │   ├── prometheus
│   │   │   └── prometheus.yml
│   │   └── supervisord.conf
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── README.md
│   └── tree.txt
├── 003_Arquitectura
│   ├── Arquitectura_DevOps.drawio
│   └── Arquitectura_DevOps_v1.png
└── README.md
```

## 🚀 Despliegue e Instalación

### 1. Prerrequisitos

- Docker Engine `v20.10+` y Docker Compose `v2.0+` instalados.
- Creación de la red externa de gestión `MGMT - LAB TYMA`:

```bash
docker network create \
--driver bridge \
--subnet 172.200.0/24 \
--gateway 172.200.0.1 \
LAB_TYMA
```

### 2. Levantar el Stack de Aplicación

1. Navegar al directorio de la aplicación:

    ```bash
    cd 001-Inventario-MVP
    ```
    
2. Desplegar los contenedores en segundo plano:
   
    ```bash
    docker compose up -d --build
    ```
    
3. Verificar que los contenedores estén en estado `Up`:

    ```
    docker compose ps
    ```
    
### 3. Levantar el Stack de Observabilidad

1. Navegar al directorio de monitoreo:

    ```
    cd ../002_Observabilidad/
    ```
    
2. Desplegar la infraestructura de monitoreo:

    ```
    docker compose up -d --build
    ```
    

## 📈 Verificación de Métricas y Estado

Una vez inicializados ambos stacks, puedes validar los puntos finales de observabilidad mediante `curl` o desde el navegador web:

- **Métricas Frontend:** `curl http://localhost:9101/metrics`
- **Métricas Backend:** `curl http://localhost:8000/metrics`
- **Métricas Postgres Exporter:** `curl http://localhost:9187/metrics`
- **Prometheus Targets:** Acceder a `http://localhost:9090/targets` y verificar que todos los _jobs_ (`backend`, `frontend`, `postgres`) reporten estado **UP**.
    

## 💾 Persistencia de Datos

El proyecto implementa volúmenes nombrados administrados por Docker para garantizar la persistencia de información ante reinicios o recreación de contenedores:

- **`inventario_postgres_data`:** Datos relacionales del inventario TI.
    
- **`Obs_prometheus_data`:** Base de datos de series temporales de métricas.
    
- **`Obs_grafana_data`:** Configuraciones, usuarios y dashboards de Grafana.
---
## 📌 Próximos Pasos y Roadmap

### 🔄 Fase 1: Integración y Despliegue Continuo (CI/CD)
- [ ] Crear pipeline en GitHub Actions / GitLab CI para linters y ejecuciones de test automáticas.
- [ ] Automatizar la construcción (*build*) y etiquetado (*tagging*) de imágenes Docker en cada `git push`.
- [ ] Configurar la publicación automática de imágenes en un Container Registry (GHCR / Docker Hub).
- [ ] Implementar despliegue automático (*CD*) sobre la red de gestión `LAB_TYMA` ante fusiones a la rama principal.

### 🏗️ Fase 2: Infraestructura como Código (Terraform)
- [ ] Crear scripts de Terraform para aprovisionar las instancias y redes virtuales en el entorno destino.
- [ ] Modularizar la infraestructura para soportar fácilmente entornos de *Staging* y *Producción*.
- [ ] Integrar la gestión de estado de Terraform (*backend remoto*).

### ☸️ Fase 3: Orquestación y Alta Disponibilidad (Kubernetes)
- [ ] Traducir los servicios de `docker-compose` a manifiestos de Kubernetes (`Deployments`, `Services`, `PVCs`).
- [ ] Empaquetar la aplicación en un **Helm Chart** modular.
- [ ] Configurar un **Ingress Controller** (Nginx / Traefik) para exponer las interfaces de Streamlit, Grafana y la API.
- [ ] Implementar la estrategia GitOps utilizando **ArgoCD** para la sincronización del cluster.

### 💡 Fase 4: Mejoras Funcionales del Inventario
- [ ] Implementar vistas de detalle y filtros avanzados en el frontend de Streamlit.
- [x] Agregar soporte para importación y exportación masiva de activos (Excel / JSON).
- [ ] Configurar alertas en Grafana / Alertmanager para notificaciones en tiempo real (Slack / Teams / Email).

### 🧪 Fase 5: Calidad de Código y Seguridad Básica
- [ ] Implementar pruebas unitarias e integración en el Backend con `pytest`.
- [ ] Configurar linters y formateadores automáticos (`ruff`, `black`) reforzando el estándar de Docstrings.
- [ ] Agregar autenticación y autorización mediante JWT en los endpoints de FastAPI.
- [ ] Implementar gestión de secretos mediante variables de entorno en lugar de credenciales estáticas.