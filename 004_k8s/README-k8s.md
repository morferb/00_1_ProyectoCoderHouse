Esta guía rápida de comandos está estructurada y optimizada para tu flujo de trabajo en **Minikube**, asegurando que las imágenes locales se utilicen correctamente y se eviten errores de acceso a los servicios.

---

## 🛠️ 1. Preparación del Entorno y Docker

Apunta la terminal al motor Docker interno de Minikube para que las imágenes compiladas queden disponibles directamente en el clúster sin necesidad de un registro externo:

```bash
minikube start
minikube status

# Activar el entorno de Docker de Minikube
eval $(minikube -p minikube docker-env)

# Verificar que la sesión de Docker apunta a Minikube
echo $DOCKER_HOST

```

---

## 📦 2. Construcción de Imágenes Locales

Construye las imágenes del sistema de inventario (Backend y Frontend) asegurando los tags correctos:

```bash
# Ir al directorio del proyecto
cd 001-Inventario-MVP

# Opción A: Mediante Docker Compose (asigna nombres según tu configuración)
docker compose build

# Opción B: Mediante Docker Build manual con tags explícitos
docker build -t inventario-backend:v1 ./backend
docker build -t inventario-frontend:v1 ./frontend

```

---

## 🚀 3. Despliegue en Kubernetes (`kubectl`)

Verifica la conectividad con el clúster y aplica todos tus manifiestos YAML de una sola vez:

```bash
# Confirmar que kubectl apunta al clúster local
kubectl cluster-info

# Ir al directorio del proyecto
cd ..

# Aplicar todos los manifiestos de la carpeta de Kubernetes
kubectl apply -f ./004_k8s

# Validar el estado de los recursos desplegados
kubectl get pods
kubectl get all

```

---

## 🔗 4. Acceso a los Servicios

Para que Minikube pueda exponer los servicios mediante túneles locales, recuerda que el servicio debe tener configurado `type: NodePort` (tal como se revisó en los pasos anteriores para evitar el error de *No node port*):

```bash
minikube service frontend-service
minikube service api-host

```