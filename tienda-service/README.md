# 🛒 NutriChain - Servicio de Tienda

**Microservicio de gestión comercial para clientes, pedidos, envíos y devoluciones en el ecosistema NutriChain.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Descripción

El **Servicio de Tienda** es el corazón comercial del ecosistema NutriChain, encargado de gestionar todo el ciclo de vida comercial desde el cliente hasta la entrega del producto. Orquesta las operaciones de ventas, logística y atención al cliente proporcionando APIs robustas para la gestión integral del negocio.

### 🎯 Funcionalidades Principales

- **👥 Gestión de Clientes**: CRUD completo con validaciones y búsquedas avanzadas
- **📦 Gestión de Pedidos**: Ciclo completo desde creación hasta entrega
- **🚚 Control de Envíos**: Seguimiento logístico y estados de entrega
- **↩️ Gestión de Devoluciones**: Procesamiento de retornos y reembolsos
- **📊 Integración Transversal**: Comunicación con servicios de Almacén y Catálogo
- **🔄 Estados y Flujos**: Control de estados del negocio con validaciones

---

## 🏗️ Arquitectura del Negocio

### 🔄 Flujo de Operaciones

```
    👤 CLIENTE
       │
       ▼
┌─────────────────┐
│   📝 PEDIDO     │ ─── Validación Stock ──► 📦 Almacén Service
│                 │
│ • Productos     │ ─── Info Productos ──► 📚 Catálogo Service
│ • Cantidades    │
│ • Precios       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   🚚 ENVÍO      │
│                 │
│ • Preparación   │
│ • Despacho      │
│ • Entrega       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  ✅ ENTREGADO   │ ◄─── Posible ──► 🔙 DEVOLUCIÓN
└─────────────────┘
```

### 📊 Modelo de Datos Principal

| Entidad | Descripción | Estados |
|---------|-------------|---------|
| **Cliente** | Datos del comprador | `activo`, `inactivo`, `suspendido` |
| **Pedido** | Orden de compra | `pendiente`, `confirmado`, `preparando`, `enviado`, `entregado`, `cancelado` |
| **Envío** | Logística de entrega | `preparando`, `despachado`, `en_transito`, `entregado`, `devuelto` |
| **Devolución** | Retorno de productos | `solicitada`, `aprobada`, `en_proceso`, `completada`, `rechazada` |

---

## 🚀 Inicio Rápido

### 📋 Prerrequisitos

- **Docker** y **Docker Compose**
- **Python 3.11+** (para desarrollo local)
- **PostgreSQL 15+** (incluido en Docker Compose)
- **Redis** (para colas y caché)

### 🐳 Ejecución con Docker

1. **Clonar el repositorio**:

```bash
git clone <repository-url>
cd nutrichain_dev
```

2. **Levantar todos los servicios**:

```bash
docker-compose up -d
```

3. **Verificar que el servicio está corriendo**:

```bash
curl http://localhost:8003/health
```

### 💻 Ejecución Local (Desarrollo)

1. **Crear entorno virtual**:

```bash
cd tienda-service
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:

```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/tienda_db
export ALMACEN_SERVICE_URL=http://localhost:8001
export CATALOGO_SERVICE_URL=http://localhost:8000
export REDIS_URL=redis://localhost:6379
export DEBUG=true
```

4. **Ejecutar migraciones**:

```bash
alembic upgrade head
```

5. **Ejecutar el servicio**:

```bash
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

---

## 📡 API Reference

### 🔍 Endpoints Principales

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `GET` | `/` | Información del servicio | No |
| `GET` | `/health` | Health check | No |
| `GET` | `/docs` | Documentación Swagger | No |

### 👥 Gestión de Clientes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/clientes/` | Crear nuevo cliente |
| `GET` | `/clientes/{id}` | Obtener cliente por ID |
| `GET` | `/clientes/codigo/{codigo}` | Obtener cliente por código |
| `PUT` | `/clientes/{id}` | Actualizar cliente |
| `GET` | `/clientes/` | Listar clientes con filtros |

#### 👤 Crear Cliente

**Endpoint**: `POST /clientes/`

**Body de ejemplo**:

```json
{
  "codigo": "CLI001",
  "nombre": "Juan Pérez",
  "email": "juan.perez@email.com",
  "telefono": "555-0123",
  "direccion": "Av. Principal 123",
  "ciudad": "Bogotá",
  "pais": "Colombia",
  "tipo_documento": "cedula",
  "numero_documento": "12345678",
  "es_empresa": false
}
```

**Respuesta**:

```json
{
  "id": 1,
  "codigo": "CLI001",
  "nombre": "Juan Pérez",
  "email": "juan.perez@email.com",
  "telefono": "555-0123",
  "direccion": "Av. Principal 123",
  "ciudad": "Bogotá",
  "pais": "Colombia",
  "tipo_documento": "cedula",
  "numero_documento": "12345678",
  "es_empresa": false,
  "estado": "activo",
  "fecha_creacion": "2025-08-06T10:30:00",
  "fecha_actualizacion": "2025-08-06T10:30:00"
}
```

### 📦 Gestión de Pedidos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/pedidos/` | Crear nuevo pedido |
| `GET` | `/pedidos/{id}` | Obtener pedido por ID |
| `GET` | `/pedidos/numero/{numero}` | Obtener pedido por número |
| `PUT` | `/pedidos/{id}` | Actualizar pedido |
| `POST` | `/pedidos/{id}/confirmar` | Confirmar pedido |
| `POST` | `/pedidos/{id}/cancelar` | Cancelar pedido |
| `GET` | `/pedidos/cliente/{cliente_id}` | Pedidos de un cliente |
| `GET` | `/pedidos/estado/{estado}` | Pedidos por estado |

#### 📋 Crear Pedido

**Endpoint**: `POST /pedidos/`

**Headers requeridos**:

- `X-Usuario`: Usuario que crea el pedido

**Body de ejemplo**:

```json
{
  "cliente_id": 1,
  "observaciones": "Entrega en horario de oficina",
  "items": [
    {
      "producto_id": 1,
      "cantidad": 2,
      "precio_unitario": 12.50
    },
    {
      "producto_id": 2,
      "cantidad": 1,
      "precio_unitario": 25.00
    }
  ]
}
```

**Respuesta**:

```json
{
  "id": 1,
  "numero_pedido": "PED-2025-001",
  "cliente_id": 1,
  "estado": "pendiente",
  "subtotal": 50.00,
  "impuestos": 9.50,
  "descuentos": 0.00,
  "total": 59.50,
  "observaciones": "Entrega en horario de oficina",
  "fecha_pedido": "2025-08-06T10:30:00",
  "usuario_creacion": "admin",
  "items": [
    {
      "id": 1,
      "producto_id": 1,
      "cantidad": 2,
      "precio_unitario": 12.50,
      "subtotal": 25.00
    },
    {
      "id": 2,
      "producto_id": 2,
      "cantidad": 1,
      "precio_unitario": 25.00,
      "subtotal": 25.00
    }
  ]
}
```

### 🚚 Gestión de Envíos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/envios/` | Crear nuevo envío |
| `GET` | `/envios/{id}` | Obtener envío por ID |
| `GET` | `/envios/numero/{numero}` | Obtener envío por número |
| `GET` | `/envios/pedido/{pedido_id}` | Envíos de un pedido |
| `PUT` | `/envios/{id}` | Actualizar envío |
| `POST` | `/envios/{id}/despachar` | Marcar como despachado |
| `POST` | `/envios/{id}/entregar` | Marcar como entregado |
| `GET` | `/envios/estado/{estado}` | Envíos por estado |

#### 🚛 Estados de Envío

| Estado | Descripción | Siguiente Estado |
|--------|-------------|------------------|
| `preparando` | Preparando productos para envío | `despachado` |
| `despachado` | Envío salió del almacén | `en_transito` |
| `en_transito` | En camino al cliente | `entregado` |
| `entregado` | Recibido por el cliente | - |
| `devuelto` | Retornado al almacén | - |

### ↩️ Gestión de Devoluciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/devoluciones/` | Crear nueva devolución |
| `GET` | `/devoluciones/{id}` | Obtener devolución por ID |
| `GET` | `/devoluciones/numero/{numero}` | Obtener devolución por número |
| `GET` | `/devoluciones/pedido/{pedido_id}` | Devoluciones de un pedido |
| `PUT` | `/devoluciones/{id}` | Actualizar devolución |
| `POST` | `/devoluciones/{id}/aprobar` | Aprobar devolución |
| `POST` | `/devoluciones/{id}/rechazar` | Rechazar devolución |
| `POST` | `/devoluciones/{id}/completar` | Completar devolución |
| `GET` | `/devoluciones/estado/{estado}` | Devoluciones por estado |

#### 🔄 Motivos de Devolución

- `producto_defectuoso`: Producto con defectos de fábrica
- `producto_incorrecto`: Se envió producto diferente
- `producto_danado`: Producto dañado durante el transporte
- `no_satisfecho`: Cliente no satisfecho con el producto
- `talla_incorrecta`: Talla o medida incorrecta
- `cambio_opinion`: Cliente cambió de opinión
- `entrega_tardia`: Entrega fuera del tiempo acordado

---

## ⚙️ Configuración

### 🔧 Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql://user:pass@localhost:5432/tienda_db` |
| `ALMACEN_SERVICE_URL` | URL del servicio de almacén | `http://localhost:8001` |
| `CATALOGO_SERVICE_URL` | URL del servicio de catálogo | `http://localhost:8000` |
| `REDIS_URL` | URL de conexión a Redis | `redis://localhost:6379` |
| `DEBUG` | Modo debug | `false` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `SECRET_KEY` | Clave secreta para JWT | (generada automáticamente) |
| `CORS_ORIGINS` | Orígenes permitidos para CORS | `["*"]` |

### 🐳 Docker Compose

```yaml
tienda-service:
  build:
    context: ./tienda-service
    dockerfile: Dockerfile
  container_name: tienda_service
  ports:
    - "8003:8001"
  volumes:
    - ./tienda-service:/app
  depends_on:
    - postgres
    - redis
    - almacen-service
    - catalogo-service
  environment:
    DATABASE_URL: "postgresql://nutrichain:nutrichain123@postgres:5432/tienda_db"
    ALMACEN_SERVICE_URL: "http://almacen-service:8000"
    CATALOGO_SERVICE_URL: "http://catalogo-service:80"
    REDIS_URL: "redis://redis:6379"
    ENVIRONMENT: "development"
    DEBUG: "true"
    LOG_LEVEL: "INFO"
  networks:
    - nutrichain-net
```

---

## 🛠️ Desarrollo

### 📁 Estructura del Proyecto

```
tienda-service/
├── 📄 main.py                    # Punto de entrada de la aplicación
├── 📄 requirements.txt           # Dependencias de Python
├── 📄 Dockerfile                 # Configuración de Docker
├── 📄 README.md                  # Este archivo
├── 📁 alembic/                   # Migraciones de base de datos
│   ├── 📄 alembic.ini
│   ├── 📄 env.py
│   └── 📁 versions/
└── app/
    ├── 📄 __init__.py
    ├── 📄 config.py               # Configuración de la aplicación
    ├── 📄 database.py             # Configuración de SQLAlchemy
    ├── 📁 api/                    # Endpoints de la API
    │   ├── 📄 __init__.py
    │   ├── 📄 clientes.py         # API de clientes
    │   ├── 📄 pedidos.py          # API de pedidos
    │   ├── 📄 envios.py           # API de envíos
    │   └── 📄 devoluciones.py     # API de devoluciones
    ├── 📁 models/                 # Modelos de SQLAlchemy
    │   ├── 📄 __init__.py
    │   ├── 📄 cliente.py          # Modelo Cliente
    │   ├── 📄 pedido.py           # Modelo Pedido
    │   ├── 📄 envio.py            # Modelo Envío
    │   └── 📄 devolucion.py       # Modelo Devolución
    ├── 📁 dtos/                   # Modelos de datos (DTOs)
    │   ├── 📄 __init__.py
    │   ├── 📄 cliente_dto.py      # DTOs de Cliente
    │   ├── 📄 pedido_dto.py       # DTOs de Pedido
    │   ├── 📄 envio_dto.py        # DTOs de Envío
    │   └── 📄 devolucion_dto.py   # DTOs de Devolución
    ├── 📁 services/               # Lógica de negocio
    │   ├── 📄 __init__.py
    │   ├── 📄 cliente_service.py  # Servicio de Clientes
    │   ├── 📄 pedido_service.py   # Servicio de Pedidos
    │   ├── 📄 envio_service.py    # Servicio de Envíos
    │   └── 📄 devolucion_service.py # Servicio de Devoluciones
    ├── 📁 repositories/           # Acceso a datos
    │   ├── 📄 __init__.py
    │   ├── 📄 cliente_repository.py
    │   ├── 📄 pedido_repository.py
    │   ├── 📄 envio_repository.py
    │   └── 📄 devolucion_repository.py
    ├── 📁 exceptions/             # Excepciones personalizadas
    │   ├── 📄 __init__.py
    │   └── 📄 api_exceptions.py
    └── 📁 middleware/             # Middleware personalizado
        ├── 📄 __init__.py
        └── 📄 exception_handlers.py
```

### 🗄️ Base de Datos

#### 📊 Esquema Principal

```sql
-- Tabla de clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    direccion TEXT,
    ciudad VARCHAR(100),
    pais VARCHAR(100),
    tipo_documento VARCHAR(20),
    numero_documento VARCHAR(50),
    es_empresa BOOLEAN DEFAULT FALSE,
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de pedidos
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    numero_pedido VARCHAR(50) UNIQUE NOT NULL,
    cliente_id INTEGER REFERENCES clientes(id),
    estado VARCHAR(20) DEFAULT 'pendiente',
    subtotal DECIMAL(12,2) NOT NULL,
    impuestos DECIMAL(12,2) DEFAULT 0,
    descuentos DECIMAL(12,2) DEFAULT 0,
    total DECIMAL(12,2) NOT NULL,
    observaciones TEXT,
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_confirmacion TIMESTAMP,
    usuario_creacion VARCHAR(100),
    usuario_actualizacion VARCHAR(100)
);
```

#### 🔄 Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial de migraciones
alembic history
```

### 🧪 Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio pytest-cov

# Ejecutar tests
pytest

# Ejecutar tests con cobertura
pytest --cov=app --cov-report=html

# Ejecutar tests específicos
pytest tests/test_clientes.py::test_crear_cliente
```

### 📝 Logging

El servicio utiliza **structlog** para logging estructurado:

```python
import structlog

logger = structlog.get_logger()

# Log con contexto
logger.info("Cliente creado", cliente_id=cliente.id, codigo=cliente.codigo)

# Log de error con contexto
logger.error("Error al procesar pedido", 
             pedido_id=pedido_id, 
             error=str(e), 
             exc_info=True)
```

---

## 🔧 Integración con Otros Servicios

### 📦 Servicio de Almacén

```python
# Verificar stock antes de confirmar pedido
stock_response = await httpx.get(
    f"{ALMACEN_SERVICE_URL}/api/v1/stock/producto/{producto_id}"
)

# Reservar stock para pedido
reserva_response = await httpx.post(
    f"{ALMACEN_SERVICE_URL}/api/v1/movimientos/reserva",
    json={
        "producto_id": producto_id,
        "cantidad": cantidad,
        "referencia": f"PED-{pedido.numero_pedido}"
    }
)
```

### 📚 Servicio de Catálogo

```python
# Obtener información de producto
producto_response = await httpx.get(
    f"{CATALOGO_SERVICE_URL}/api/productos/{producto_id}"
)

# Validar existencia de productos en pedido
productos_ids = [item.producto_id for item in pedido.items]
validacion_response = await httpx.post(
    f"{CATALOGO_SERVICE_URL}/api/productos/validar",
    json={"productos_ids": productos_ids}
)
```

---

## 🔧 Troubleshooting

### ❗ Problemas Comunes

1. **Error de conexión a base de datos**:

```bash
# Verificar conexión
docker exec -it postgres_container psql -U nutrichain -d tienda_db

# Ver logs de PostgreSQL
docker logs postgres_container
```

2. **Servicio no responde**:

```bash
# Verificar estado del contenedor
docker ps | grep tienda

# Ver logs del servicio
docker logs tienda_service

# Reiniciar servicio
docker-compose restart tienda-service
```

3. **Error en migraciones**:

```bash
# Verificar estado de migraciones
alembic current

# Forzar migración
alembic stamp head

# Recrear base de datos
docker-compose down
docker volume rm nutrichain_dev_postgres_data
docker-compose up -d
```

4. **Errores de integración**:

```bash
# Verificar servicios dependientes
curl http://localhost:8001/health  # Almacén
curl http://localhost:8000/api/status  # Catálogo

# Ver logs de integración
docker logs tienda_service | grep -E "(almacen|catalogo)"
```

### 📊 Monitoreo y Métricas

```bash
# Health check completo
curl http://localhost:8003/health

# Métricas de base de datos
curl http://localhost:8003/metrics/database

# Estado de colas (si se usa Celery)
celery -A app.celery status

# Flower para monitoreo de colas
open http://localhost:5555
```

---

## 🚀 Despliegue

### 🐳 Producción con Docker

```bash
# Build de imagen de producción
docker build -t nutrichain/tienda-service:latest .

# Ejecutar en producción
docker run -d \
  --name tienda-service \
  -p 8003:8001 \
  -e DATABASE_URL=postgresql://user:pass@prod-db:5432/tienda_db \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  nutrichain/tienda-service:latest
```

### ☁️ Consideraciones de Producción

- **🔒 Secretos**: Usar gestores de secretos (AWS Secrets Manager, Azure Key Vault)
- **📊 Monitoreo**: Implementar Prometheus + Grafana
- **🔍 Logging**: Centralizar logs con ELK Stack o similar
- **🚦 Load Balancer**: Nginx o AWS ALB para múltiples instancias
- **🗄️ Base de Datos**: PostgreSQL con réplicas de lectura
- **📦 Backup**: Estrategia de respaldo automático

---

## 🤝 Contribución

1. **Fork** el repositorio
2. **Crear** una rama de feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** los cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abrir** un Pull Request

### 📋 Coding Standards

- **🐍 PEP 8**: Seguir estándares de Python
- **📝 Type Hints**: Usar anotaciones de tipo
- **📚 Docstrings**: Documentar todas las funciones
- **🧪 Tests**: Mantener cobertura > 80%
- **🔍 Linting**: Validar con flake8, black, isort

### 🧪 Pre-commit Hooks

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Ejecutar en todos los archivos
pre-commit run --all-files
```

---

## 📄 Licencia

Este software está licenciado bajo la **Licencia MIT**.

```
MIT License

Copyright (c) 2025 Jorge Ernesto Remigio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👨‍💻 Autor

**Jorge Ernesto Remigio**  
📧 Email: <jetradercu@yahoo.com>  
🐙 GitHub: [@jeremigio2706](https://github.com/jeremigio2706)

---

## 📚 Documentación Adicional

- 📖 [Documentación API (Swagger)](http://localhost:8003/docs)
- 📋 [Documentación API (ReDoc)](http://localhost:8003/redoc)
- 🏗️ [Arquitectura del Sistema](../DOCUMENTACION.md)
- 🔧 [Guía de Configuración](../README.md)
- 📊 [Dashboard de Monitoreo](http://localhost:3000)

---

## 🔄 Changelog

### v1.0.0 (2025-08-06)

- ✨ **Inicial**: Implementación completa del servicio de tienda
- 👥 **Clientes**: CRUD completo con validaciones
- 📦 **Pedidos**: Gestión de ciclo completo de pedidos
- 🚚 **Envíos**: Control logístico y seguimiento
- ↩️ **Devoluciones**: Procesamiento de retornos
- 🔗 **Integración**: Comunicación con servicios de almacén y catálogo
- 🐳 **Docker**: Containerización completa
- 📊 **Monitoreo**: Health checks y logging estructurado

---

*Última actualización: Agosto 2025*
