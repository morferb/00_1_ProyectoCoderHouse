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

Luego hay que editar el archivo `~/.aws/config` para que incluya el parámetro `endpoint_url`:
```bash
[default]
region = us-east-1
endpoint_url = http://localhost:4566
output = json
```
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

---
# Arquitectura Multi-cuenta AWS
Para un entorno productivo y multi-cuenta, la clave en Terraform es separar responsabilidades. Dado que interactúan dos cuentas de AWS (Networking y Servicios), el código debe reflejar esta frontera utilizando múltiples proveedores (providers con alias) y una estructura de módulos que aisle la lógica de cada componente.

A continuación, presento la estructura recomendada y el instructivo de configuración para organizar los artefactos de networking.
### 1. Estructura de Directorios Recomendada
Para mantener el orden y facilitar la documentación, el árbol de directorios debe expandirse dividiendo los recursos lógicos.

```bash
005_Terraform/
├── providers.tf             # Configuración de los providers (Cuenta 1 y Cuenta 2)
├── main.tf                  # Orquestador principal que llama a los módulos
├── variables.tf             # Variables globales (ej. CIDRs, IDs de cuentas)
└── modules/
    ├── vpc/                 # (Cuenta 2) VPC, Subnets y Route Tables locales
    │   ├── vpc.tf           
    │   ├── variables.tf
    │   └── outputs.tf
    ├── tgw/                 # (Cuenta 1) Transit Gateway, TGW RTs, Asociaciones
    │   ├── tgw.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── tgw_attachment/      # (Cross-Account) RAM Share, VPC Attachments
        ├── attachment.tf
        ├── variables.tf
        └── outputs.tf
```

### 2. Configuración de Providers (`providers.tf`)

Al tener recursos en dos cuentas distintas, Terraform necesita saber con qué credenciales ejecutar cada bloque. Esto se logra definiendo un provider por defecto y otro con un `alias`.

```terraform
# providers.tf

# Provider para la Cuenta 1 (Networking / TGW / DX)
provider "aws" {
  alias   = "networking"
  region  = "us-east-1"
  profile = "aws-profile-networking" # O rol asumido correspondiente
}

# Provider para la Cuenta 2 (Servicios / App)
provider "aws" {
  alias   = "app"
  region  = "us-east-1"
  profile = "aws-profile-app"
}
```

### 3. Diseño de los Módulos (Artefactos a declarar)

#### Módulo VPC (`modules/vpc/vpc.tf`) - _Se ejecuta en Cuenta 2_

Este módulo es responsable de la red local donde vive la EC2 y de dirigir el tráfico saliente hacia el On-Premise.

- **VPC:** CIDR `172.200.0.0/24`.
- **Subnet Privada:** Donde se alojará la EC2.
- **Route Table (`aws_route_table`):** La tabla de la subred.
- **Ruta Estática (`aws_route`):** Debe inyectar la ruta hacia On-Premise (`10.0.1.0/24`) apuntando al ID del Attachment del TGW (que será inyectado como variable desde el orquestador).


### 4. Orquestación (`main.tf`)

El archivo principal unirá los módulos pasando las dependencias mediante variables (Outputs de un módulo se vuelven Inputs del siguiente) y pasará explícitamente los providers.

  


```

```

### Siguientes pasos para la implementación
