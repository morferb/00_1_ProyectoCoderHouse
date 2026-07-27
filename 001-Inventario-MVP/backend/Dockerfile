# ==========================================
# ETAPA 1: Constructor (Builder Stage)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear un entorno virtual para aislar las librerías instaladas
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar las dependencias de Python dentro del entorno virtual
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ==========================================
# ETAPA 2: Producción (Runtime Stage)
# ==========================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Instalar únicamente la librería cliente runtime de PostgreSQL (libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual ya compilado desde la etapa anterior
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar el código fuente de la aplicación
COPY . /app

# Exponer el puerto de la aplicación
EXPOSE 8000