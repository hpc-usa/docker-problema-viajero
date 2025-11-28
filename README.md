# Taller Práctico 4: Optimización de Rutas TSP con Docker Compose

## 📋 Estructura del Proyecto

```
tsp-distributed/
├── app.py              # API Flask
├── client.py           # Cliente de fuerza bruta
├── Dockerfile          # Definición del contenedor
├── docker-compose.yml  # Orquestación de servicios
├── nginx.conf         # Configuración del load balancer
├── requirements.txt    # Dependencias Python
├── deploy.sh          # Script de despliegue
└── README.md          # Este archivo
```

## 🚀 Instalación en Ubuntu

### Prerequisitos

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker

# Instalar Docker Compose
sudo apt install docker-compose -y

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Instalar Python y dependencias
sudo apt install python3 python3-pip -y
pip3 install requests

# Instalar jq para tests (opcional)
sudo apt install jq -y
```

## 📦 Despliegue con Docker Compose

### Opción 1: Usando el script automático

```bash
# Dar permisos de ejecución
chmod +x deploy.sh

# Levantar servicios
./deploy.sh up

# Ver estado
./deploy.sh status

# Ver logs
./deploy.sh logs

# Probar API
./deploy.sh test

# Detener servicios
./deploy.sh down
```

### Opción 2: Comandos manuales

```bash
# Construir y levantar servicios
docker-compose up -d --build

# Ver estado de los contenedores
docker-compose ps

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f calculator1

# Detener servicios
docker-compose down

# Reconstruir y reiniciar
docker-compose up -d --build --force-recreate
```

## 🏗️ Arquitectura

```
┌─────────────┐
│   Cliente   │
│  (client.py)│
└──────┬──────┘
       │ HTTP Requests
       ↓
┌─────────────────────┐
│   Nginx (Port 5000) │  ← Load Balancer
│   Round Robin       │
└──────┬──────────────┘
       │
       ├→ calculator1:5000 (Réplica 1)
       ├→ calculator2:5000 (Réplica 2)
       ├→ calculator3:5000 (Réplica 3)
       └→ calculator4:5000 (Réplica 4)
```

## 🧪 Ejecutar el Cliente

```bash
# Ejecutar el cliente de fuerza bruta
python3 client.py
```

El cliente realizará:
1. ✓ Verificación de conectividad
2. ✓ Búsqueda secuencial (una petición a la vez)
3. ✓ Búsqueda paralela (múltiples peticiones simultáneas)
4. ✓ Comparación de rendimiento entre ambos métodos

## 📊 Comandos Útiles

### Docker Compose

```bash
# Ver todos los contenedores
docker-compose ps

# Ver uso de recursos
docker stats

# Entrar a un contenedor
docker exec -it tsp-calculator-1 /bin/sh

# Ver logs de todos los servicios
docker-compose logs

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar un servicio específico
docker-compose restart calculator1

# Eliminar todo (contenedores, redes, volúmenes)
docker-compose down -v
```

### Nginx

```bash
# Ver configuración de Nginx
docker exec tsp-nginx cat /etc/nginx/nginx.conf

# Ver logs de Nginx
docker-compose logs nginx

# Stats de Nginx
curl http://localhost:5000/nginx_status
```

## 🔧 Pruebas Manuales de la API

### Con curl

```bash
# Health check
curl http://localhost:5000/health

# Info del servicio
curl http://localhost:5000/info

# Calcular distancia
curl -X POST http://localhost:5000/calculate_distance \
  -H "Content-Type: application/json" \
  -d '{
    "cities": [
      {"name": "A", "x": 0, "y": 0},
      {"name": "B", "x": 10, "y": 5},
      {"name": "C", "x": 15, "y": 15}
    ]
  }'

# Verificar balanceo de carga (ejecutar varias veces)
for i in {1..10}; do
  curl -s http://localhost:5000/health | grep replica_id
done
```

### Con Python

```python
import requests

# Test básico
response = requests.post('http://localhost:5000/calculate_distance', json={
    "cities": [
        {"name": "A", "x": 0, "y": 0},
        {"name": "B", "x": 10, "y": 5},
        {"name": "C", "x": 15, "y": 15}
    ]
})

print(response.json())
# Output: {"total_distance": 22.3607, "processed_by": "Replica-1", "hostname": "..."}
```

## 🎯 Escalar el Servicio

### Opción 1: Editar docker-compose.yml

Agrega más réplicas copiando el patrón:

```yaml
  calculator5:
    build: .
    container_name: tsp-calculator-5
    environment:
      - FLASK_ENV=production
      - REPLICA_ID=5
    networks:
      - tsp-network
    restart: unless-stopped
```

Y actualiza nginx.conf:

```nginx
upstream calculator_backend {
    least_conn;
    server calculator1:5000;
    server calculator2:5000;
    server calculator3:5000;
    server calculator4:5000;
    server calculator5:5000;  # Nueva réplica
}
```

Luego:

```bash
docker-compose up -d --build
```

### Opción 2: Docker Compose Scale (limitado)

```bash
# Nota: esto solo funciona con servicios sin nombre de contenedor específico
docker-compose up -d --scale calculator=8
```

## 📈 Experimentación para el Informe

### 1. Rendimiento con diferentes réplicas

```bash
# 2 réplicas (comentar calculator3 y calculator4)
docker-compose up -d --build
python3 client.py > resultados_2_replicas.txt

# 4 réplicas (todas activas)
docker-compose up -d --build
python3 client.py > resultados_4_replicas.txt

# 6 réplicas (agregar calculator5 y calculator6)
docker-compose up -d --build
python3 client.py > resultados_6_replicas.txt
```

### 2. Diferentes tamaños de problema

Edita `client.py`:

```python
# 4 ciudades = 24 permutaciones
CITIES = CITIES[:4]

# 5 ciudades = 120 permutaciones
CITIES = CITIES[:5]

# 6 ciudades = 720 permutaciones
CITIES = CITIES[:6]

# 7 ciudades = 5040 permutaciones
CITIES = CITIES[:7]
```

### 3. Paralelismo del cliente

Modifica en `client.py` la función main:

```python
# Probar con diferentes números de workers
for workers in [5, 10, 20, 50]:
    print(f"\n=== Probando con {workers} workers ===")
    route, dist, time = brute_force_parallel(max_workers=workers)
```

### 4. Algoritmos de balanceo

Edita `nginx.conf` y prueba diferentes estrategias:

```nginx
upstream calculator_backend {
    # Opción 1: Round Robin (por defecto)
    server calculator1:5000;
    
    # Opción 2: Least Connections
    least_conn;
    
    # Opción 3: IP Hash (mismo cliente → mismo servidor)
    ip_hash;
    
    # Opción 4: Pesos diferentes
    server calculator1:5000 weight=3;
    server calculator2:5000 weight=1;
}
```

## 🐛 Solución de Problemas

### Los contenedores no inician

```bash
# Ver logs detallados
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs calculator1

# Verificar errores de sintaxis
docker-compose config
```

### Puerto 5000 ocupado

```bash
# Ver qué está usando el puerto
sudo netstat -tlnp | grep 5000

# Cambiar el puerto en docker-compose.yml
nginx:
  ports:
    - "5001:80"  # Usar puerto 5001 en lugar de 5000
```

### Problemas de permisos

```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar permisos
docker ps
```

### Reconstruir desde cero

```bash
# Eliminar todo
docker-compose down -v
docker system prune -a

# Reconstruir
docker-compose up -d --build
```

- [ ] Ejecutar cliente paralelo
- [ ] Recolectar métricas
- [ ] Crear gráficas
- [ ] Escribir informe
- [ ] Entregar proyecto  
