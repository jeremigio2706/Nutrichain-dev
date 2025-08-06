# 📊 NutriChain - Servicio de Reportes

**Microservicio de consolidación de datos y generación de reportes empresariales para el ecosistema NutriChain.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Descripción

El **Servicio de Reportes** es un microservicio especializado en la consolidación de datos de múltiples servicios del ecosistema NutriChain para generar reportes analíticos y de negocio. Opera sin mantener estado propio, actuando como un orquestador que consulta información de los servicios de **Almacén**, **Tienda** y **Catálogo** para proporcionar insights valiosos.

### 🎯 Funcionalidades Principales

- **📈 Reporte de Stock Valorizado**: Análisis financiero del inventario
- **👥 Reporte de Pedidos por Cliente**: Historial de compras y análisis de comportamiento
- **🔍 Trazabilidad de Productos**: Seguimiento completo del ciclo de vida de productos
- **⚡ Health Checks**: Monitoreo del estado de servicios dependientes
- **🔄 Consolidación en Tiempo Real**: Datos actualizados desde múltiples fuentes

---

## 🏗️ Arquitectura

### 📊 Diagrama de Integración

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   📦 Almacén    │    │   🛒 Tienda     │    │  📚 Catálogo    │
│   Puerto: 8001  │    │   Puerto: 8003  │    │   Puerto: 8000  │
│                 │    │                 │    │                 │
│ • Stock         │    │ • Pedidos       │    │ • Productos     │
│ • Movimientos   │    │ • Clientes      │    │ • Categorías    │
│ • Costos        │    │ • Ventas        │    │ • SKUs          │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────┐
                    │    📊 REPORTES         │
                    │    Puerto: 8002        │
                    │                        │
                    │ • Consolidación        │
                    │ • Análisis             │
                    │ • Reportes             │
                    └────────────────────────┘
```

### 🔗 Integraciones

| Servicio | URL Base | Endpoints Utilizados | Datos Obtenidos |
|----------|----------|---------------------|-----------------|
| **Almacén** | `http://almacen-service:8000/api/v1` | `/stock/`, `/movimientos/` | Stock, costos, movimientos |
| **Tienda** | `http://tienda-service:8003` | `/clientes/`, `/pedidos/` | Clientes, pedidos, ventas |
| **Catálogo** | `http://catalogo-service:80/api` | `/productos/{id}`, `/status` | Productos, SKUs, categorías |

---

## 🚀 Inicio Rápido

### 📋 Prerrequisitos

- **Docker** y **Docker Compose**
- **Python 3.11+** (para desarrollo local)
- Servicios dependientes ejecutándose:
  - Almacén Service (puerto 8001)
  - Tienda Service (puerto 8003)
  - Catálogo Service (puerto 8000)

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
curl http://localhost:8002/health
```

### 💻 Ejecución Local (Desarrollo)

1. **Crear entorno virtual**:

```bash
cd reportes-service
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:

```bash
export ALMACEN_SERVICE_URL=http://localhost:8001
export TIENDA_SERVICE_URL=http://localhost:8003
export CATALOGO_SERVICE_URL=http://localhost:8000
export DEBUG=true
```

4. **Ejecutar el servicio**:

```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

---

## 📡 API Reference

### 🔍 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información del servicio |
| `GET` | `/health` | Health check básico |
| `GET` | `/docs` | Documentación interactiva (Swagger) |
| `GET` | `/api/v1/reportes/health` | Health check con servicios dependientes |
| `GET` | `/api/v1/reportes/stock-valorizado` | Reporte de stock valorizado |
| `GET` | `/api/v1/reportes/pedidos-cliente/{cliente_id}` | Reporte de pedidos por cliente |
| `GET` | `/api/v1/reportes/trazabilidad-producto/{producto_id}` | Trazabilidad de producto |

### 📊 Reporte de Stock Valorizado

**Endpoint**: `GET /api/v1/reportes/stock-valorizado`

**Descripción**: Genera un reporte consolidado del valor del inventario combinando datos de stock (almacén) con información de productos (catálogo).

**Parámetros**:

- `almacen_id` (opcional): Filtrar por almacén específico
- `incluir_sin_stock` (boolean): Incluir productos sin stock (default: false)
- `categoria_id` (opcional): Filtrar por categoría de producto

**Ejemplo de uso**:

```bash
curl "http://localhost:8002/api/v1/reportes/stock-valorizado?incluir_sin_stock=true"
```

**Respuesta**:

```json
{
  "items": [
    {
      "producto_id": 1,
      "sku": "POL001",
      "nombre_producto": "Pollo Entero Fresco Premium",
      "categoria": "refrigerados",
      "almacen_id": 1,
      "almacen_nombre": "Almacén Principal",
      "cantidad_actual": "33.00",
      "costo_unitario": "12.50",
      "valor_total": "412.50",
      "estado_stock": "disponible",
      "ultima_actualizacion": "2025-08-06T02:35:14.208115"
    }
  ],
  "resumen": {
    "total_productos_diferentes": 4,
    "cantidad_total_items": 90,
    "valor_promedio_por_producto": 125.75
  },
  "fecha_reporte": "2025-08-06T02:35:14.660594",
  "total_productos": 4,
  "valor_total_inventario": "1547.50"
}
```

**🎯 Casos de Uso**:

- 💰 **Análisis Financiero**: Valoración total del inventario
- 📊 **Control de Stock**: Identificación de productos con bajo stock
- 📋 **Auditorías**: Verificación de inventarios físicos vs. sistema
- 📈 **Toma de Decisiones**: Planificación de compras y presupuestos

### 👥 Reporte de Pedidos por Cliente

**Endpoint**: `GET /api/v1/reportes/pedidos-cliente/{cliente_id}`

**Descripción**: Genera un historial completo de pedidos de un cliente específico, enriquecido con información de productos.

**Parámetros**:

- `cliente_id` (requerido): ID del cliente
- `fecha_desde` (opcional): Fecha inicio del período (ISO format)
- `fecha_hasta` (opcional): Fecha fin del período (ISO format)
- `estado` (opcional): Filtrar por estado del pedido
- `incluir_detalles` (boolean): Incluir detalles de productos (default: true)

**Ejemplo de uso**:

```bash
curl "http://localhost:8002/api/v1/reportes/pedidos-cliente/1?fecha_desde=2025-01-01T00:00:00&incluir_detalles=true"
```

**🎯 Casos de Uso**:

- 👤 **Análisis de Cliente**: Comportamiento de compra y preferencias
- 🛒 **Historial de Pedidos**: Seguimiento completo de transacciones
- 📊 **Segmentación**: Identificación de clientes VIP y patrones de compra
- 💼 **Customer Service**: Soporte al cliente con historial completo

### 🔍 Trazabilidad de Producto

**Endpoint**: `GET /api/v1/reportes/trazabilidad-producto/{producto_id}`

**Descripción**: Proporciona trazabilidad completa de un producto incluyendo movimientos de stock y historial de ventas.

**Parámetros**:

- `producto_id` (requerido): ID del producto
- `fecha_desde` (opcional): Fecha inicio del período
- `fecha_hasta` (opcional): Fecha fin del período
- `incluir_movimientos` (boolean): Incluir movimientos de stock (default: true)
- `incluir_ventas` (boolean): Incluir historial de ventas (default: true)
- `almacen_id` (opcional): Filtrar por almacén específico

**Ejemplo de uso**:

```bash
curl "http://localhost:8002/api/v1/reportes/trazabilidad-producto/1?incluir_movimientos=true&incluir_ventas=true"
```

**🎯 Casos de Uso**:

- 🔍 **Trazabilidad Completa**: Seguimiento desde entrada hasta venta
- 📦 **Control de Calidad**: Rastreo de lotes y fechas de vencimiento
- 📊 **Análisis de Rotación**: Tiempo de permanencia en inventario
- 🚨 **Recalls**: Localización rápida de productos defectuosos

---

## ⚙️ Configuración

### 🔧 Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `ALMACEN_SERVICE_URL` | URL del servicio de almacén | `http://localhost:8001` |
| `TIENDA_SERVICE_URL` | URL del servicio de tienda | `http://localhost:8003` |
| `CATALOGO_SERVICE_URL` | URL del servicio de catálogo | `http://localhost:8000` |
| `DEBUG` | Modo debug | `false` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

### 🐳 Docker Compose

```yaml
reportes-service:
  build:
    context: ./reportes-service
    dockerfile: Dockerfile
  container_name: reportes_service
  ports:
    - "8002:8002"
  volumes:
    - ./reportes-service:/app
  depends_on:
    - almacen-service
    - catalogo-service
    - tienda-service
  environment:
    ALMACEN_SERVICE_URL: "http://almacen-service:8000"
    CATALOGO_SERVICE_URL: "http://catalogo-service:80"
    TIENDA_SERVICE_URL: "http://tienda-service:8003"
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
reportes-service/
├── 📄 main.py                    # Punto de entrada de la aplicación
├── 📄 requirements.txt           # Dependencias de Python
├── 📄 Dockerfile                 # Configuración de Docker
├── 📄 README.md                  # Este archivo
└── app/
    ├── 📁 api/
    │   ├── 📄 __init__.py
    │   └── 📄 reportes.py         # Endpoints de la API
    ├── 📁 dtos/
    │   ├── 📄 __init__.py
    │   └── 📄 reporte_dto.py      # Modelos de datos (DTOs)
    ├── 📁 services/
    │   ├── 📄 __init__.py
    │   └── 📄 reporte_service.py  # Lógica de negocio
    ├── 📁 exceptions/
    │   ├── 📄 __init__.py
    │   └── 📄 api_exceptions.py   # Excepciones personalizadas
    ├── 📁 middleware/
    │   ├── 📄 __init__.py
    │   └── 📄 exception_handlers.py # Manejadores de errores
    └── 📄 config.py               # Configuración de la aplicación
```

### 🧪 Testing

```bash
# Ejecutar tests (cuando estén implementados)
pytest

# Health check completo
curl http://localhost:8002/api/v1/reportes/health

# Test de integración
curl http://localhost:8002/api/v1/reportes/stock-valorizado
```

### 📝 Logging

El servicio utiliza logging estructurado con diferentes niveles:

```python
import logging

logger = logging.getLogger(__name__)

# Configuración en main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 🔧 Troubleshooting

### ❗ Problemas Comunes

1. **Servicio no responde**:

   ```bash
   # Verificar estado del contenedor
   docker ps | grep reportes
   
   # Ver logs
   docker logs reportes_service
   ```

2. **Error de conexión con servicios dependientes**:

   ```bash
   # Verificar health check
   curl http://localhost:8002/api/v1/reportes/health
   
   # Verificar servicios dependientes
   curl http://localhost:8001/health  # Almacén
   curl http://localhost:8003/health  # Tienda
   curl http://localhost:8000/api/status  # Catálogo
   ```

3. **Datos incompletos en reportes**:
   - Verificar que todos los servicios tengan datos
   - Revisar logs para errores de integración
   - Validar URLs de servicios en configuración

### 📊 Monitoreo

```bash
# Verificar métricas básicas
curl http://localhost:8002/health

# Ver documentación de API
open http://localhost:8002/docs

# Monitorear logs en tiempo real
docker logs -f reportes_service
```

---

## 🤝 Contribución

1. **Fork** el repositorio
2. **Crear** una rama de feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** los cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abrir** un Pull Request

### 📋 Coding Standards

- Seguir **PEP 8** para Python
- Usar **type hints** en todas las funciones
- Documentar funciones con **docstrings**
- Mantener cobertura de tests > 80%
- Validar con **flake8** y **black**

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

- 📖 [Documentación API (Swagger)](http://localhost:8002/docs)
- 📋 [Documentación API (ReDoc)](http://localhost:8002/redoc)
- 🏗️ [Arquitectura del Sistema](../DOCUMENTACION.md)
- 🔧 [Guía de Configuración](../README.md)

---

*Último actualización: Agosto 2025*
