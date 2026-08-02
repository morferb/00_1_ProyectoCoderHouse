# ==========================================
# ETAPA 1: Construcción (Builder)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Configurar variables de entorno para optimizar Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear y activar entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# ETAPA 2: Producción (Runner)
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Copiar entorno virtual de la etapa de construcción
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar el código de la aplicación
COPY . /app

## Puerto 8501: Interfaz de Streamlit / Puerto 9101: Métricas Prometheus
EXPOSE 8501 9101

# Comando para ejecutar la aplicación web
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]