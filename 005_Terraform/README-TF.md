# Instructivo de Laboratorio Terraform con MiniStack
### 1. Configuración de AWS CLI

Instala y configura la interfaz de línea de comandos de AWS con credenciales de prueba para interactuar con el entorno local:


```bash
# Instalar AWS CLI
sudo apt update && sudo apt install awscli -y

# Configurar credenciales (utilizar valores de prueba)
aws configure
```

- **AWS Access Key ID:** `test`

- **AWS Secret Access Key:** `test`

- **Default region name:** `us-east-1`

- **Default output format:** `json`


### 2. Despliegue de MiniStack

Clona el repositorio oficial de MiniStack y levanta el entorno de contenedorización:


```bash
# Clonar el repositorio
git clone https://github.com/ministackorg/ministack 06_MiniStack
cd 06_MiniStack

# Iniciar los servicios en segundo plano
docker compose up -d
```

#### Validaciones del entorno

Verifica que el contenedor esté corriendo correctamente y que el servicio responda:

```bash
# Validar contenedor activo
docker ps

# Validar salud del servicio MiniStack
curl http://localhost:4566/_ministack/health
```

### 3. Ejecución de Comandos Básicos de Terraform

Utiliza los comandos estándar de Terraform dentro de tu directorio de configuración para gestionar la infraestructura:


```bash
# 1. Inicializar Terraform (descarga los proveedores necesarios)
terraform init

# 2. Revisar el plan de ejecución antes de aplicar cambios
terraform plan

# 3. Aplicar y crear la infraestructura (escribe "yes" para confirmar)
terraform apply
```

### 4. Limpieza del Entorno

Una vez finalizado el laboratorio, puedes detener y eliminar los contenedores junto con sus volúmenes asociados:

``` bash
docker compose down -v
```