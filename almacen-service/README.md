# 📦 NutriChain - Microservicio de Almacén

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)

Microservicio especializado para la gestión integral de almacenes, inventarios y movimientos de stock en la plataforma NutriChain. Implementa patrones de arquitectura senior con manejo centralizado de estado y trazabilidad completa.

## 🏗️ Arquitectura del Sistema

```mermaid
graph TB
    subgraph "Almacén Service"
        API[FastAPI Router Layer]
        BL[Business Logic Services]
        REPO[Repository Pattern]
        DB[(PostgreSQL)]
        
        API --> BL
        BL --> REPO
        REPO --> DB
    end
    
    subgraph "Integraciones Externas"
        CAT[Catálogo Service]
        TIE[Tienda Service]
        REP[Reportes Service]
    end
    
    API -.->|Consulta productos| CAT
    TIE -.->|Reservas de stock| API
    REP -.->|Datos inventario| API
    
    subgraph "Componentes Internos"
        EXC[Exception Handlers]
        MID[Middleware]
        DTO[DTOs/Schemas]
        MOD[SQLAlchemy Models]
    end
    
    API --> EXC
    API --> MID
    API --> DTO
    REPO --> MOD
```

### 🎯 Principios de Diseño

- **Single Responsibility**: Cada componente tiene una responsabilidad específica
- **Dependency Injection**: Gestión de dependencias a través de FastAPI
- **Repository Pattern**: Abstracción de acceso a datos
- **DTO Pattern**: Separación entre modelos de dominio y transferencia
- **Exception Handling**: Manejo centralizado sin try/catch repetitivo
- **Immutable Operations**: Operaciones de stock como eventos inmutables

## 📋 Funcionalidades Principales

### 🏪 Gestión de Almacenes

- **CRUD completo** de almacenes con validaciones
- **Geolocalización** y datos de contacto
- **Estado operacional** (activo/inactivo/mantenimiento)
- **Capacidad y métricas** de utilización

### 📊 Control de Inventario

- **Stock en tiempo real** por producto y almacén
- **Niveles mínimos** configurables con alertas
- **Reservas temporales** para procesos de venta
- **Histórico completo** de movimientos

### 🔄 Movimientos de Stock

- **Entradas**: Compras, devoluciones, ajustes positivos
- **Salidas**: Ventas, mermas, ajustes negativos  
- **Transferencias**: Entre almacenes con trazabilidad
- **Auditoría**: Registro inmutable de todas las operaciones

### 🚨 Sistema de Alertas

- **Stock bajo**: Notificaciones automáticas
- **Productos vencidos**: Control de fechas de caducidad
- **Discrepancias**: Detección de inconsistencias
- **Métricas operacionales**: Rendimiento de almacenes

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Framework** | FastAPI | 0.104+ | API REST de alto rendimiento |
| **Base de Datos** | PostgreSQL | 13+ | Persistencia ACID-compliant |
| **ORM** | SQLAlchemy | 2.0+ | Mapeo objeto-relacional |
| **Validación** | Pydantic | 2.5+ | Validación de datos y serialización |
| **Contenedor** | Docker | 20+ | Containerización y despliegue |
| **Servidor ASGI** | Uvicorn | 0.24+ | Servidor de aplicaciones async |

## 🚀 Configuración y Despliegue

### Prerrequisitos

```bash
# Software requerido
- Python 3.9+
- PostgreSQL 13+
- Docker & Docker Compose (opcional)
- Git
```

### 🐳 Despliegue con Docker (Recomendado)

#### 1. Configuración de variables de entorno

```bash
# Crear archivo .env en el directorio del servicio
cat > .env << EOF
# Configuración de Base de Datos
DATABASE_URL=postgresql://user:password@localhost:5432/almacen_db

# Configuración del Servidor
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development

# Configuración de Stock
STOCK_MINIMO_DEFAULT=10.0

# URLs de Servicios Externos
CATALOGO_SERVICE_URL=http://localhost:8000
EOF
```

#### 2. Construcción y ejecución

```bash
# Construir la imagen
docker build -t nutrichain-almacen:latest .

# Ejecutar con PostgreSQL
docker run -d \\
  --name almacen-service \\
  -p 8001:8000 \\
  -e DATABASE_URL="postgresql://user:password@host.docker.internal:5432/almacen_db" \\
  nutrichain-almacen:latest

# Verificar estado
curl http://localhost:8001/health
```

#### 3. Con Docker Compose (Stack completo)

```bash
# Desde el directorio raíz del proyecto
docker-compose up -d db redis  # Infraestructura base
docker-compose up -d almacen-service  # Solo el servicio de almacén

# Ver logs
docker-compose logs -f almacen-service
```

### 💻 Desarrollo Local

#### 1. Configuración del entorno

```bash
# Clonar repositorio
git clone <repository-url>
cd nutrichain_dev/almacen-service

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. Configuración de base de datos

```bash
# Crear base de datos PostgreSQL
createdb almacen_db

# Configurar variable de entorno
export DATABASE_URL="postgresql://user:password@localhost:5432/almacen_db"
```

#### 3. Ejecución del servicio

```bash
# Modo desarrollo con hot-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Modo producción
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

## 📡 Documentación de API

### Endpoints Principales

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `GET` | `/health` | Estado del servicio | No |
| `GET` | `/docs` | Documentación Swagger | No |
| `GET` | `/almacenes` | Listar almacenes | No |
| `POST` | `/almacenes` | Crear almacén | No |
| `GET` | `/almacenes/{id}` | Obtener almacén | No |
| `PUT` | `/almacenes/{id}` | Actualizar almacén | No |
| `DELETE` | `/almacenes/{id}` | Eliminar almacén | No |
| `GET` | `/stock` | Consultar stock | No |
| `POST` | `/stock/reservar` | Reservar stock | No |
| `POST` | `/stock/liberar` | Liberar reserva | No |
| `GET` | `/movimientos` | Historial movimientos | No |
| `POST` | `/movimientos` | Registrar movimiento | No |

### Ejemplos de Uso

#### Crear Almacén

```bash
curl -X POST "http://localhost:8001/almacenes" \\
  -H "Content-Type: application/json" \\
  -d '{
    "nombre": "Almacén Central Madrid",
    "direccion": "Calle Mayor 123, Madrid",
    "telefono": "+34 91 234 5678",
    "email": "madrid@nutrichain.com",
    "capacidad_maxima": 10000.0,
    "estado": "activo"
  }'
```

#### Consultar Stock

```bash
curl "http://localhost:8001/stock?producto_id=123&almacen_id=1"
```

#### Reservar Stock

```bash
curl -X POST "http://localhost:8001/stock/reservar" \\
  -H "Content-Type: application/json" \\
  -d '{
    "producto_id": 123,
    "almacen_id": 1,
    "cantidad": 5.0,
    "referencia_externa": "pedido-456"
  }'
```

#### Registrar Movimiento

```bash
curl -X POST "http://localhost:8001/movimientos" \\
  -H "Content-Type: application/json" \\
  -d '{
    "tipo": "entrada",
    "producto_id": 123,
    "almacen_id": 1,
    "cantidad": 100.0,
    "motivo": "Compra a proveedor",
    "referencia": "COMPRA-2024-001"
  }'
```

### Respuestas de la API

#### Estructura Estándar de Respuesta

```json
{
  "success": true,
  "data": {
    // Contenido específico del endpoint
  },
  "message": "Operación completada exitosamente",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Manejo de Errores

```json
{
  "success": false,
  "error": {
    "code": "STOCK_INSUFICIENTE",
    "message": "No hay suficiente stock disponible",
    "details": {
      "disponible": 5.0,
      "solicitado": 10.0,
      "producto_id": 123,
      "almacen_id": 1
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🗄️ Estructura de Base de Datos

### Esquema Principal

```sql
-- Tabla de Almacenes
CREATE TABLE almacenes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    capacidad_maxima DECIMAL(10,2),
    estado VARCHAR(20) DEFAULT 'activo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Stock
CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    almacen_id INTEGER REFERENCES almacenes(id),
    cantidad DECIMAL(10,2) NOT NULL DEFAULT 0,
    cantidad_reservada DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock_minimo DECIMAL(10,2) DEFAULT 10.0,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Movimientos
CREATE TABLE movimientos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL, -- 'entrada', 'salida', 'transferencia'
    producto_id INTEGER NOT NULL,
    almacen_origen_id INTEGER REFERENCES almacenes(id),
    almacen_destino_id INTEGER REFERENCES almacenes(id),
    cantidad DECIMAL(10,2) NOT NULL,
    motivo TEXT,
    referencia VARCHAR(100),
    usuario_id INTEGER,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Reservas
CREATE TABLE reservas_stock (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    almacen_id INTEGER REFERENCES almacenes(id),
    cantidad DECIMAL(10,2) NOT NULL,
    referencia_externa VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'activa', -- 'activa', 'confirmada', 'liberada'
    fecha_expiracion TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Índices de Rendimiento

```sql
-- Índices para optimizar consultas frecuentes
CREATE INDEX idx_stock_producto_almacen ON stock(producto_id, almacen_id);
CREATE INDEX idx_movimientos_fecha ON movimientos(fecha_movimiento DESC);
CREATE INDEX idx_movimientos_producto ON movimientos(producto_id);
CREATE INDEX idx_reservas_estado ON reservas_stock(estado, fecha_expiracion);
```

## 🧪 Testing y Validación

### Ejecutar Tests

```bash
# Tests unitarios
pytest tests/unit/ -v

# Tests de integración
pytest tests/integration/ -v

# Coverage report
pytest --cov=app --cov-report=html tests/

# Validación de endpoints
python validate_all_endpoints_senior.py
```

### Validación de Arquitectura

```bash
# Verificar cumplimiento de patrones senior
python validate_senior_architecture.py

# Verificar endpoints activos
curl http://localhost:8001/health
curl http://localhost:8001/almacenes
curl http://localhost:8001/stock
```

## 📊 Monitoreo y Observabilidad

### Health Checks

```bash
# Estado general del servicio
GET /health

# Respuesta esperada:
{
  "status": "healthy",
  "database": "connected",
  "service": "almacen-service-refactored",
  "architecture": "clean",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime": "2h 15m 30s"
}
```

### Métricas Disponibles

- **Rendimiento**: Tiempo de respuesta de endpoints
- **Base de Datos**: Estado de conexiones y queries
- **Negocio**: Stock bajo, movimientos por hora, utilización de almacenes
- **Sistema**: Memoria, CPU, espacio en disco

### Logs Estructurados

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "almacen-service",
  "operation": "stock.reservar",
  "data": {
    "producto_id": 123,
    "almacen_id": 1,
    "cantidad": 5.0,
    "usuario_id": "admin"
  },
  "duration_ms": 45,
  "success": true
}
```

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por Defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `DATABASE_URL` | Conexión a PostgreSQL | `postgresql://user:password@localhost:5432/almacen_db` | ✅ |
| `DEBUG` | Modo debug | `false` | ❌ |
| `LOG_LEVEL` | Nivel de logging | `INFO` | ❌ |
| `CATALOGO_SERVICE_URL` | URL del servicio de catálogo | `http://localhost:8000` | ❌ |
| `STOCK_MINIMO_DEFAULT` | Stock mínimo por defecto | `10.0` | ❌ |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `["*"]` | ❌ |

### Configuración de Producción

```bash
# Optimizaciones para producción
export DEBUG=false
export LOG_LEVEL=WARNING
export WORKERS=4
export TIMEOUT=120

# Configuración de base de datos optimizada
export DATABASE_URL="postgresql://user:password@db:5432/almacen_db?pool_size=20&max_overflow=30"
```

## 📚 Guía de Desarrollo

### Estructura del Código

```
almacen-service/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuración centralizada
│   ├── database.py            # Setup de SQLAlchemy
│   ├── main.py               # Punto de entrada FastAPI
│   ├── api/                  # Routers y endpoints
│   │   ├── almacenes.py
│   │   ├── stock.py
│   │   └── movimientos.py
│   ├── services/             # Lógica de negocio
│   │   ├── almacen_service.py
│   │   ├── stock_service.py
│   │   └── movimiento_service.py
│   ├── repositories/         # Acceso a datos
│   │   ├── almacen_repository.py
│   │   ├── stock_repository.py
│   │   └── movimiento_repository.py
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── almacen.py
│   │   ├── stock.py
│   │   └── movimiento.py
│   ├── dtos/                # Schemas Pydantic
│   │   ├── almacen_dto.py
│   │   ├── stock_dto.py
│   │   └── movimiento_dto.py
│   ├── exceptions/          # Excepciones personalizadas
│   │   └── api_exceptions.py
│   └── middleware/          # Middleware personalizado
│       └── exception_handlers.py
├── tests/                   # Tests organizados
├── Dockerfile              # Imagen Docker
├── requirements.txt        # Dependencias Python
└── README.md               # Esta documentación
```

### Patrones Implementados

#### Repository Pattern

```python
class StockRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_producto_almacen(self, producto_id: int, almacen_id: int):
        return self.db.query(Stock).filter_by(
            producto_id=producto_id,
            almacen_id=almacen_id
        ).first()
```

#### Service Layer

```python
class StockService:
    def __init__(self, stock_repo: StockRepository):
        self.stock_repo = stock_repo
    
    def reservar_stock(self, request: ReservaStockDTO):
        # Lógica de negocio centralizada
        stock = self.stock_repo.get_by_producto_almacen(
            request.producto_id, 
            request.almacen_id
        )
        # ... validaciones y operaciones
```

## ⚠️ Solución de Problemas

### Problemas Comunes

#### Error de Conexión a Base de Datos

```bash
# Verificar conectividad
pg_isready -h localhost -p 5432

# Verificar credenciales
psql -h localhost -p 5432 -U user -d almacen_db
```

#### Puerto Ocupado

```bash
# Verificar qué proceso usa el puerto
lsof -i :8001

# Matar proceso si es necesario
kill -9 <PID>
```

#### Problemas de Migración

```bash
# Recrear tablas en desarrollo
python -c "from app.database import engine, Base; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"
```

### Debugging

```bash
# Logs en tiempo real
docker logs -f almacen-service

# Conectar al contenedor
docker exec -it almacen-service bash

# Verificar variables de entorno
docker exec almacen-service env | grep DATABASE_URL
```

## 🤝 Contribución

### Estándares de Código

- **PEP 8**: Formato de código Python
- **Type Hints**: Tipado estático obligatorio
- **Docstrings**: Documentación de funciones y clases
- **Tests**: Cobertura mínima del 80%

### Flujo de Trabajo

1. Fork del repositorio
2. Crear branch de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commits descriptivos siguiendo [Conventional Commits](https://conventionalcommits.org/)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request con descripción detallada

## 📞 Soporte

Para dudas, problemas o sugerencias:

- **Issues**: [GitHub Issues](https://github.com/jeremigio2706/Nutrichain-dev/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/jeremigio2706/Nutrichain-dev/wiki)
- **Email**: <soporte@nutrichain.com>

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](../LICENSE) para más detalles.

---

**NutriChain Almacén Service v1.0.0** - Gestión de inventarios de próxima generación 🚀
