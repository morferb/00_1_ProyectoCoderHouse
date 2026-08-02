# ==========================================
# Stage 1: Prometheus Assets
# ==========================================
FROM prom/prometheus:v2.51.0 AS stage-prometheus

# ==========================================
# Stage 2: Blackbox Exporter Assets
# ==========================================
FROM prom/blackbox-exporter:v0.25.0 AS stage-blackbox

# ==========================================
# Stage 3: Grafana Assets
# ==========================================
FROM grafana/grafana:10.4.0 AS stage-grafana

# ==========================================
# Final Stage: Unified Runtime
# ==========================================
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    GF_PATHS_DATA=/var/lib/grafana \
    GF_PATHS_LOGS=/var/log/grafana \
    GF_PATHS_PLUGINS=/var/lib/grafana/plugins \
    GF_PATHS_PROVISIONING=/etc/grafana/provisioning

# Instalación de utilidades mínimas y gestor de procesos Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    ca-certificates \
    curl \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Copia de binarios de Prometheus
COPY --from=stage-prometheus /bin/prometheus /usr/local/bin/prometheus
COPY --from=stage-prometheus /bin/promtool /usr/local/bin/promtool

# Copia de binarios de Blackbox Exporter
COPY --from=stage-blackbox /bin/blackbox_exporter /usr/local/bin/blackbox_exporter

# Copia de archivos y binarios de Grafana
COPY --from=stage-grafana /usr/share/grafana /usr/share/grafana

# Estructura de directorios necesaria
RUN mkdir -p /etc/prometheus \
             /etc/blackbox \
             /etc/supervisor/conf.d \
             /var/lib/grafana \
             /var/log/grafana \
             /etc/grafana/provisioning/datasources \
             /etc/grafana/provisioning/dashboards

WORKDIR /usr/share/grafana

# Puertos: 9090 (Prometheus), 9115 (Blackbox), 3000 (Grafana)
EXPOSE 9090 9115 3000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]