Para unificar **Prometheus**, **Blackbox Exporter** y **Grafana** en un solo contenedor optimizado, la mejor estrategia es construir un **Dockerfile Multistage** que extraiga los binarios y dependencias esenciales de las imágenes oficiales y utilice **Supervisor** como gestor de procesos en un runtime ligero de Linux.

---

## 📁 Estructura del Proyecto

```text
observability-stack/
├── Dockerfile
├── docker-compose.yml
└── config/
    ├── supervisord.conf
    ├── prometheus/
    │   └── prometheus.yml
    ├── blackbox/
    │   └── blackbox.yml
    └── grafana/
        └── provisioning/
            └── datasources/
                └── datasource.yml

```

---
# Pasos para la instalación
## 1. Multi-Stage Dockerfile (`Dockerfile`)
En las primeras etapas se obtienen los binarios de las imágenes oficiales de Prometheus, Blackbox Exporter y Grafana. La etapa final integra todo sobre una base Debian Slim con `supervisord`.

---
## 2. Archivos de Configuración (`config/`)

### A. Supervisor (`config/supervisord.conf`)
Controla la ejecución simultánea de los tres servicios en primer plano.

---
### B. Prometheus (`config/prometheus/prometheus.yml`)
Configura el scraping interno y el monitoreo mediante Blackbox Exporter.

---
### C. Blackbox Exporter (`config/blackbox/blackbox.yml`)
Define los módulos de sondeo HTTP/HTTPS.

---
### D. Auto-provisioning Grafana Datasource (`config/grafana/provisioning/datasources/datasource.yml`)
Conecta Grafana automáticamente a Prometheus al iniciar el contenedor.

---
## 3. Orchestración (`docker-compose.yml`)

---
## 🚀 Despliegue

Para construir la imagen multistage e iniciar el servicio en segundo plano:

```bash
docker compose up --build -d

```

* **Grafana:** `http://localhost:3000` (User/Pass por defecto: `admin` / `admin`)
* **Prometheus:** `http://localhost:9090`
* **Blackbox Exporter:** `http://localhost:9115`

# Importación de dashboard
en la ruta '03_Observabilidad/config/Dashboard/MonitoreoServicios.json' se encuentra un dashboard acorde al proyecto.
Los pasos para importarlo son:
- Copiar el contenido de 'MonitoreoServicios.json' 
- Abrir Grafana y dirigirse a: Home ->Dashboards ->Import dashboard
	- Copiar el contenido en 'Import via dashboard JSON model'
- Guardar cambios
---
# Troubleshooting

Reiniciar servicio prometheus luego de realizar cambios:
```bash
docker exec -it observability_all_in_one supervisorctl restart prometheus

```
