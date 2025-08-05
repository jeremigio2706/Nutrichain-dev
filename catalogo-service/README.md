# 📦 NutriChain - Microservicio de Catálogo

[![PHP](https://img.shields.io/badge/PHP-7.2+-777BB4.svg)](https://php.net)
[![Symfony](https://img.shields.io/badge/Symfony-2.8-000000.svg)](https://symfony.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![Apache](https://img.shields.io/badge/Apache-2.4+-D22128.svg)](https://httpd.apache.org)

Microservicio especializado para la gestión integral del catálogo de productos en la plataforma NutriChain. Implementa una arquitectura robusta con Symfony 2.8, proporcionando una API REST completa para la administración de productos alimentarios con validaciones avanzadas y categorización inteligente.

## 🏗️ Arquitectura del Sistema

```mermaid
graph TB
    subgraph "Catálogo Service (PHP/Symfony)"
        WEB[Apache Web Server]
        API[REST API Controllers]
        SVC[Business Services]
        VAL[Validation Layer]
        ORM[Doctrine ORM]
        DB[(PostgreSQL)]
        
        WEB --> API
        API --> SVC
        SVC --> VAL
        SVC --> ORM
        ORM --> DB
    end
    
    subgraph "Servicios Consumidores"
        ALM[Almacén Service]
        TIE[Tienda Service]
        REP[Reportes Service]
    end
    
    ALM -.->|Validar productos| API
    TIE -.->|Consultar productos| API
    REP -.->|Datos de catálogo| API
    
    subgraph "Componentes Técnicos"
        CORS[CORS Bundle]
        API_DOC[API Documentation]
        SER[JMS Serializer]
        CACHE[Doctrine Cache]
    end
    
    API --> CORS
    API --> API_DOC
    API --> SER
    ORM --> CACHE
```

### 🎯 Principios de Diseño

- **Domain-Driven Design**: Entidades y servicios orientados al dominio alimentario
- **RESTful Architecture**: API REST siguiendo estándares HTTP
- **Separation of Concerns**: Controladores, servicios y repositorios separados
- **Data Validation**: Validación robusta en múltiples capas
- **Response Standardization**: Respuestas consistentes y documentadas
- **Legacy Compatibility**: Soporte para Symfony 2.8 con PHP 7.2

## 📋 Funcionalidades Principales

### 🛒 Gestión de Productos

- **CRUD Completo**: Crear, leer, actualizar y eliminar productos
- **Validación Avanzada**: SKU únicos, pesos positivos, categorías válidas
- **Categorización**: Clasificación por tipo alimentario (refrigerados, secos, congelados)
- **Gestión de Estado**: Activación/desactivación de productos
- **Metadatos**: Información completa con imágenes y descripciones

### 🔍 Búsqueda y Filtrado

- **Búsqueda por texto**: Nombre y descripción de productos
- **Filtros por categoría**: Organización por tipos alimentarios
- **Búsqueda por SKU**: Consultas directas por código único
- **Estado de activación**: Filtrar productos activos/inactivos
- **Ordenamiento**: Por nombre, fecha, categoría

### 📊 Validaciones de Negocio

- **SKU Único**: Garantía de códigos únicos en el sistema
- **Peso Positivo**: Validación de pesos mayor a cero
- **Categorías Válidas**: Solo categorías alimentarias permitidas
- **Formato de Imágenes**: Validación de URLs de imágenes
- **Campos Obligatorios**: Validación de datos esenciales

### 🔗 Integración de Servicios

- **API Documentada**: Documentación automática con Nelmio API Doc
- **Formato JSON**: Respuestas estandarizadas en JSON
- **CORS Configurado**: Acceso desde múltiples dominios
- **Versionado**: Preparado para múltiples versiones de API

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Framework** | Symfony | 2.8.x | Framework web robusto |
| **Lenguaje** | PHP | 7.2+ | Lenguaje de programación |
| **Servidor Web** | Apache | 2.4+ | Servidor HTTP con mod_rewrite |
| **Base de Datos** | PostgreSQL | 13+ | Base de datos relacional |
| **ORM** | Doctrine | 2.5+ | Mapeo objeto-relacional |
| **API REST** | FOSRestBundle | 2.1+ | Construcción de APIs REST |
| **Documentación** | NelmioApiDocBundle | 2.13+ | Documentación automática |
| **Serialización** | JMSSerializerBundle | 1.1+ | Serialización JSON/XML |
| **CORS** | NelimioCorsBundle | 1.5+ | Cross-Origin Resource Sharing |
| **Testing** | PHPUnit | 6.5+ | Framework de testing |

## 🚀 Configuración y Despliegue

### Prerrequisitos

```bash
# Software requerido
- PHP 7.2+
- Composer 2.0+
- PostgreSQL 13+
- Apache 2.4+ (o Docker)
- Git
```

### 🐳 Despliegue con Docker (Recomendado)

#### 1. Configuración de variables de entorno

```bash
# Crear archivo .env en el directorio del servicio
cat > .env << EOF
# Configuración de Base de Datos
DATABASE_URL=pgsql://user:password@localhost:5432/catalogo_db

# Configuración de Symfony
SYMFONY_ENV=dev
DEBUG=true

# Configuración de Apache
APACHE_DOCUMENT_ROOT=/var/www/html/web
APACHE_LOG_DIR=/var/log/apache2

# Configuración de API
API_VERSION=v1
CORS_ALLOW_ORIGIN=*
EOF
```

#### 2. Construcción y ejecución

```bash
# Construir la imagen
docker build -t nutrichain-catalogo:latest .

# Ejecutar con PostgreSQL
docker run -d \
  --name catalogo-service \
  -p 8000:80 \
  -e DATABASE_URL="pgsql://user:password@host.docker.internal:5432/catalogo_db" \
  nutrichain-catalogo:latest

# Verificar estado
curl http://localhost:8000/api/productos
```

#### 3. Con Docker Compose (Stack completo)

```bash
# Desde el directorio raíz del proyecto
docker-compose up -d db  # Base de datos
docker-compose up -d catalogo-service  # Servicio de catálogo

# Ver logs
docker-compose logs -f catalogo-service
```

### 💻 Desarrollo Local

#### 1. Configuración del entorno

```bash
# Clonar repositorio
git clone <repository-url>
cd nutrichain_dev/catalogo-service

# Instalar dependencias
composer install

# Configurar parámetros
cp app/config/parameters.yml.dist app/config/parameters.yml
# Editar app/config/parameters.yml con tu configuración
```

#### 2. Configuración de base de datos

```bash
# Crear base de datos
createdb catalogo_db

# Ejecutar migraciones
php app/console doctrine:migrations:migrate

# Cargar datos de prueba (opcional)
php app/console doctrine:fixtures:load
```

#### 3. Ejecución del servicio

```bash
# Servidor de desarrollo Symfony
php app/console server:run 0.0.0.0:8000

# Con Apache (configurar virtual host)
sudo a2ensite catalogo-service
sudo systemctl reload apache2
```

## 📡 Documentación de API

### Endpoints Principales

| Método | Endpoint | Descripción | Content-Type |
|--------|----------|-------------|--------------|
| `GET` | `/api/productos` | Listar todos los productos | `application/json` |
| `GET` | `/api/productos?categoria={cat}` | Filtrar por categoría | `application/json` |
| `GET` | `/api/productos?nombre={name}` | Buscar por nombre | `application/json` |
| `GET` | `/api/productos/{id}` | Obtener producto específico | `application/json` |
| `POST` | `/api/productos` | Crear nuevo producto | `application/json` |
| `PUT` | `/api/productos/{id}` | Actualizar producto completo | `application/json` |
| `PATCH` | `/api/productos/{id}` | Actualización parcial | `application/json` |
| `DELETE` | `/api/productos/{id}` | Eliminar producto | `application/json` |
| `GET` | `/api/doc` | Documentación Swagger | `text/html` |

### Ejemplos de Uso

#### Listar Productos

```bash
# Todos los productos
curl -X GET "http://localhost:8000/api/productos" \
  -H "Accept: application/json"

# Filtrar por categoría
curl -X GET "http://localhost:8000/api/productos?categoria=refrigerados" \
  -H "Accept: application/json"

# Buscar por nombre
curl -X GET "http://localhost:8000/api/productos?nombre=pollo" \
  -H "Accept: application/json"
```

#### Crear Producto

```bash
curl -X POST "http://localhost:8000/api/productos" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "nombre": "Pollo Entero Premium",
    "sku": "POL001-PREM",
    "unidad_medida": "kg",
    "peso": 1.8,
    "categoria": "refrigerados",
    "imagen": "https://cdn.nutrichain.com/productos/pollo-entero-premium.jpg",
    "descripcion": "Pollo entero fresco de granja, alimentado con granos naturales. Ideal para asados y guisos familiares.",
    "activo": true
  }'
```

#### Obtener Producto Específico

```bash
curl -X GET "http://localhost:8000/api/productos/1" \
  -H "Accept: application/json"
```

#### Actualizar Producto

```bash
# Actualización completa (PUT)
curl -X PUT "http://localhost:8000/api/productos/1" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "nombre": "Pollo Entero Premium Plus",
    "sku": "POL001-PREM-PLUS",
    "unidad_medida": "kg",
    "peso": 2.0,
    "categoria": "refrigerados",
    "imagen": "https://cdn.nutrichain.com/productos/pollo-entero-premium-plus.jpg",
    "descripcion": "Pollo entero premium de granja orgánica",
    "activo": true
  }'

# Actualización parcial (PATCH)
curl -X PATCH "http://localhost:8000/api/productos/1" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "peso": 2.2,
    "descripcion": "Peso actualizado por nueva clasificación"
  }'
```

#### Eliminar Producto

```bash
curl -X DELETE "http://localhost:8000/api/productos/1" \
  -H "Accept: application/json"
```

### Estructura de Respuestas

#### Respuesta Exitosa (200/201)

```json
{
  "success": true,
  "data": {
    "id": 1,
    "nombre": "Pollo Entero Premium",
    "sku": "POL001-PREM",
    "unidad_medida": "kg",
    "peso": 1.8,
    "categoria": "refrigerados",
    "imagen": "https://cdn.nutrichain.com/productos/pollo-entero-premium.jpg",
    "descripcion": "Pollo entero fresco de granja",
    "activo": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "Producto obtenido exitosamente",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Lista de Productos

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Pollo Entero Premium",
      "sku": "POL001-PREM",
      "categoria": "refrigerados",
      "peso": 1.8,
      "activo": true
    },
    {
      "id": 2,
      "nombre": "Arroz Integral",
      "sku": "ARR001-INT",
      "categoria": "secos",
      "peso": 1.0,
      "activo": true
    }
  ],
  "meta": {
    "total": 2,
    "page": 1,
    "per_page": 20,
    "total_pages": 1
  },
  "message": "Productos obtenidos exitosamente",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Respuesta de Error (400/404/422)

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Los datos proporcionados no son válidos",
    "details": {
      "sku": ["El SKU ya existe en el sistema"],
      "peso": ["El peso debe ser mayor a 0"],
      "categoria": ["La categoría debe ser: refrigerados, secos o congelados"]
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🗄️ Estructura de Base de Datos

### Esquema Principal

```sql
-- Tabla principal de productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    unidad_medida VARCHAR(50) NOT NULL DEFAULT 'unidad',
    peso DECIMAL(10,2) NOT NULL CHECK (peso > 0),
    categoria VARCHAR(50) NOT NULL CHECK (categoria IN ('refrigerados', 'secos', 'congelados')),
    imagen VARCHAR(500),
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de categorías (para escalabilidad futura)
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    activa BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de atributos adicionales (extensible)
CREATE TABLE producto_atributos (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER REFERENCES productos(id) ON DELETE CASCADE,
    atributo VARCHAR(100) NOT NULL,
    valor TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Índices de Rendimiento

```sql
-- Índices principales para optimización
CREATE INDEX idx_productos_sku ON productos(sku);
CREATE INDEX idx_productos_categoria ON productos(categoria);
CREATE INDEX idx_productos_activo ON productos(activo);
CREATE INDEX idx_productos_nombre ON productos USING gin(to_tsvector('spanish', nombre));
CREATE INDEX idx_productos_created_at ON productos(created_at DESC);

-- Índices compuestos
CREATE INDEX idx_productos_categoria_activo ON productos(categoria, activo);
CREATE INDEX idx_producto_atributos_producto_id ON producto_atributos(producto_id);

-- Constraint de unicidad
ALTER TABLE productos ADD CONSTRAINT uk_productos_sku UNIQUE (sku);
```

### Datos de Prueba (Seeds)

```sql
-- Insertar categorías base
INSERT INTO categorias (nombre, descripcion) VALUES 
('refrigerados', 'Productos que requieren refrigeración'),
('secos', 'Productos de almacenamiento en seco'),
('congelados', 'Productos que requieren congelación');

-- Insertar productos de ejemplo
INSERT INTO productos (nombre, sku, unidad_medida, peso, categoria, descripcion, activo) VALUES 
('Pollo Entero', 'POL001', 'kg', 1.5, 'refrigerados', 'Pollo entero fresco de granja', true),
('Arroz Blanco', 'ARR001', 'kg', 1.0, 'secos', 'Arroz blanco grano largo', true),
('Helado Vainilla', 'HEL001', 'l', 1.0, 'congelados', 'Helado artesanal de vainilla', true),
('Pescado Salmón', 'PES001', 'kg', 0.8, 'refrigerados', 'Filete de salmón fresco', true),
('Pasta Espagueti', 'PAS001', 'kg', 0.5, 'secos', 'Pasta de trigo durum', true);
```

## 🧪 Testing y Validación

### Configuración de Testing

```bash
# Configurar base de datos de test
createdb catalogo_db_test

# Configurar archivo de test
cp app/config/parameters.yml app/config/parameters_test.yml
# Editar parameters_test.yml con la BD de test
```

### Ejecutar Tests

```bash
# Tests unitarios
./bin/phpunit -c app/

# Tests específicos
./bin/phpunit -c app/ src/CatalogoBundle/Tests/Entity/
./bin/phpunit -c app/ src/CatalogoBundle/Tests/Controller/

# Tests con coverage
./bin/phpunit -c app/ --coverage-html web/coverage

# Tests de API (funcionales)
./bin/phpunit -c app/ src/CatalogoBundle/Tests/Controller/ProductoControllerTest.php
```

### Validación Manual de Endpoints

```bash
# Script de validación automática
curl -s http://localhost:8000/api/productos | jq .
curl -s http://localhost:8000/api/productos/1 | jq .

# Crear producto de test
curl -X POST "http://localhost:8000/api/productos" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test Product","sku":"TEST001","peso":1.0,"categoria":"secos"}' | jq .
```

## 📊 Monitoreo y Observabilidad

### Health Checks

```bash
# Verificar estado del servicio
curl http://localhost:8000/api/health

# Respuesta esperada:
{
  "status": "ok",
  "service": "catalogo-service",
  "version": "1.0.0",
  "database": "connected",
  "symfony_env": "dev",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Logs de Apache

```bash
# Ver logs en tiempo real
docker exec -it catalogo-service tail -f /var/log/apache2/access.log
docker exec -it catalogo-service tail -f /var/log/apache2/error.log

# Logs de Symfony
docker exec -it catalogo-service tail -f /var/www/html/app/logs/dev.log
```

### Métricas de Rendimiento

```bash
# Estadísticas de Apache
curl http://localhost:8000/server-status

# Información de PHP
curl http://localhost:8000/info.php  # Solo en desarrollo
```

## 🔧 Configuración Avanzada

### Variables de Entorno Symfony

| Variable | Descripción | Valor por Defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `DATABASE_URL` | Conexión a PostgreSQL | `pgsql://user:pass@localhost/catalogo_db` | ✅ |
| `SYMFONY_ENV` | Entorno de Symfony | `prod` | ❌ |
| `SYMFONY_DEBUG` | Modo debug | `false` | ❌ |
| `MAILER_URL` | Configuración de correo | `null://localhost` | ❌ |
| `SECRET` | Clave secreta de Symfony | `auto-generated` | ✅ |

### Configuración de Producción

```yaml
# app/config/parameters.yml (producción)
parameters:
    database_driver: pdo_pgsql
    database_host: '%env(DATABASE_HOST)%'
    database_port: '%env(DATABASE_PORT)%'
    database_name: '%env(DATABASE_NAME)%'
    database_user: '%env(DATABASE_USER)%'
    database_password: '%env(DATABASE_PASSWORD)%'
    
    mailer_transport: smtp
    mailer_host: '%env(MAILER_HOST)%'
    mailer_user: '%env(MAILER_USER)%'
    mailer_password: '%env(MAILER_PASSWORD)%'
    
    secret: '%env(SYMFONY_SECRET)%'
    
    # Cache de producción
    doctrine_cache_driver: redis
    doctrine_cache_host: '%env(REDIS_HOST)%'
    doctrine_cache_port: '%env(REDIS_PORT)%'
```

### Optimizaciones de Apache

```apache
# 000-default.conf optimizado
<VirtualHost *:80>
    DocumentRoot /var/www/html/web
    
    # Compresión gzip
    LoadModule deflate_module modules/mod_deflate.so
    <Location />
        SetOutputFilter DEFLATE
        SetEnvIfNoCase Request_URI \
            \.(?:gif|jpe?g|png)$ no-gzip dont-vary
        SetEnvIfNoCase Request_URI \
            \.(?:exe|t?gz|zip|bz2|sit|rar)$ no-gzip dont-vary
    </Location>
    
    # Cache de archivos estáticos
    <FilesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg)$">
        ExpiresActive On
        ExpiresDefault "access plus 1 month"
    </FilesMatch>
    
    # Seguridad
    <Directory /var/www/html/web>
        AllowOverride All
        Require all granted
        
        # Ocultar archivos sensibles
        <FilesMatch "^\.">
            Require all denied
        </FilesMatch>
    </Directory>
    
    ErrorLog /var/log/apache2/error.log
    CustomLog /var/log/apache2/access.log combined
</VirtualHost>
```

## 📚 Estructura del Proyecto

### Organización del Código

```
catalogo-service/
├── app/                          # Configuración de Symfony
│   ├── config/
│   │   ├── parameters.yml        # Parámetros de configuración
│   │   ├── config.yml           # Configuración principal
│   │   ├── routing.yml          # Rutas principales
│   │   └── security.yml         # Configuración de seguridad
│   ├── Resources/
│   │   └── views/               # Plantillas Twig
│   └── AppKernel.php            # Kernel de la aplicación
├── src/
│   └── CatalogoBundle/          # Bundle principal
│       ├── Controller/          # Controladores REST
│       │   ├── ProductoController.php
│       │   └── HealthController.php
│       ├── Entity/              # Entidades Doctrine
│       │   ├── Producto.php
│       │   └── Categoria.php
│       ├── Repository/          # Repositorios
│       │   └── ProductoRepository.php
│       ├── Service/             # Servicios de negocio
│       │   ├── ProductoService.php
│       │   └── ValidationService.php
│       ├── DTO/                 # Data Transfer Objects
│       │   ├── ProductoDTO.php
│       │   └── ResponseDTO.php
│       ├── Exception/           # Excepciones personalizadas
│       │   └── ProductoException.php
│       ├── Validator/           # Validadores customizados
│       │   └── SkuValidator.php
│       └── Tests/               # Tests unitarios
│           ├── Controller/
│           ├── Service/
│           └── Entity/
├── web/                         # Directorio público
│   ├── app.php                  # Punto de entrada producción
│   ├── app_dev.php              # Punto de entrada desarrollo
│   ├── .htaccess                # Configuración Apache
│   └── assets/                  # Recursos estáticos
├── vendor/                      # Dependencias Composer
├── bin/                         # Ejecutables
├── var/                         # Cache y logs
├── Dockerfile                   # Imagen Docker
├── 000-default.conf             # Configuración Apache
├── composer.json                # Dependencias PHP
├── phpunit.xml                  # Configuración testing
└── README.md                    # Esta documentación
```

### Patrones Implementados

#### Controller Pattern

```php
<?php
/**
 * Controlador REST para gestión de productos
 */
class ProductoController extends Controller
{
    /**
     * @Route("/api/productos", methods={"GET"})
     * @Rest\View()
     */
    public function listAction(Request $request)
    {
        $productos = $this->get('catalogo.producto_service')
            ->findByFilters($request->query->all());
            
        return new Response($productos, Response::HTTP_OK);
    }
}
```

#### Service Layer Pattern

```php
<?php
/**
 * Servicio de negocio para productos
 */
class ProductoService
{
    private $em;
    private $validator;
    
    public function create(ProductoDTO $dto)
    {
        $this->validateSku($dto->getSku());
        
        $producto = new Producto();
        $producto->fromDTO($dto);
        
        $this->em->persist($producto);
        $this->em->flush();
        
        return $producto;
    }
}
```

#### Repository Pattern

```php
<?php
/**
 * Repositorio para consultas de productos
 */
class ProductoRepository extends EntityRepository
{
    public function findByFilters(array $filters)
    {
        $qb = $this->createQueryBuilder('p');
        
        if (isset($filters['categoria'])) {
            $qb->andWhere('p.categoria = :categoria')
               ->setParameter('categoria', $filters['categoria']);
        }
        
        return $qb->getQuery()->getResult();
    }
}
```

## ⚠️ Solución de Problemas

### Problemas Comunes

#### Error 500 - Internal Server Error

```bash
# Verificar logs de Apache
docker exec -it catalogo-service tail -f /var/log/apache2/error.log

# Verificar logs de Symfony
docker exec -it catalogo-service tail -f /var/www/html/app/logs/prod.log

# Verificar permisos
docker exec -it catalogo-service ls -la /var/www/html/app/cache
docker exec -it catalogo-service ls -la /var/www/html/app/logs
```

#### Error de Base de Datos

```bash
# Verificar conexión
docker exec -it catalogo-service php app/console doctrine:schema:validate

# Verificar parámetros
docker exec -it catalogo-service cat app/config/parameters.yml

# Probar conexión manual
docker exec -it db psql -U user -d catalogo_db -c "SELECT version();"
```

#### Problemas de Composer

```bash
# Limpiar cache de Composer
docker exec -it catalogo-service composer clear-cache

# Reinstalar dependencias
docker exec -it catalogo-service composer install --no-dev --optimize-autoloader

# Verificar autoloader
docker exec -it catalogo-service composer dump-autoload --optimize
```

#### Errores de Cache

```bash
# Limpiar cache de Symfony
docker exec -it catalogo-service php app/console cache:clear --env=prod --no-debug

# Verificar permisos de cache
docker exec -it catalogo-service chmod -R 777 app/cache app/logs

# Calentar cache
docker exec -it catalogo-service php app/console cache:warmup --env=prod
```

### Debugging Avanzado

```bash
# Modo debug en producción (temporal)
docker exec -it catalogo-service sed -i 's/debug: false/debug: true/' app/config/config_prod.yml

# Profiler de Symfony (solo desarrollo)
curl http://localhost:8000/app_dev.php/_profiler/

# Debug de rutas
docker exec -it catalogo-service php app/console debug:router

# Debug de servicios
docker exec -it catalogo-service php app/console debug:container | grep catalogo
```

## 🚀 Optimizaciones de Rendimiento

### Cache de Doctrine

```yaml
# app/config/config_prod.yml
doctrine:
    orm:
        metadata_cache_driver: redis
        result_cache_driver: redis
        query_cache_driver: redis
        
        result_cache_lifetime: 3600
        query_cache_lifetime: 3600
```

### OPcache para PHP

```ini
; php.ini optimizado
opcache.enable=1
opcache.memory_consumption=256
opcache.interned_strings_buffer=16
opcache.max_accelerated_files=20000
opcache.revalidate_freq=0
opcache.validate_timestamps=0
opcache.fast_shutdown=1
```

### Índices de Base de Datos

```sql
-- Análisis de performance
EXPLAIN ANALYZE SELECT * FROM productos WHERE categoria = 'refrigerados';

-- Estadísticas de tablas
ANALYZE productos;

-- Mantenimiento de índices
REINDEX TABLE productos;
```

## 🤝 Contribución y Desarrollo

### Estándares de Código

- **PSR-4**: Autoloading de clases
- **PSR-2**: Estilo de código
- **Symfony Best Practices**: Convenciones del framework
- **PHPDoc**: Documentación de código
- **Testing**: Cobertura mínima del 80%

### Flujo de Desarrollo

1. **Fork** del repositorio
2. **Branch de feature**: `git checkout -b feature/nueva-funcionalidad`
3. **Desarrollo** con tests
4. **Commit** descriptivo siguiendo [Conventional Commits](https://conventionalcommits.org/)
5. **Push**: `git push origin feature/nueva-funcionalidad`
6. **Pull Request** con descripción detallada

### Comandos de Desarrollo

```bash
# Crear nueva entidad
php app/console generate:entity

# Crear nuevo controlador
php app/console generate:controller

# Generar getters/setters
php app/console generate:doctrine:entities CatalogoBundle

# Crear migración
php app/console doctrine:migrations:generate

# Ejecutar migración
php app/console doctrine:migrations:migrate
```

## 📞 Soporte y Recursos

### Enlaces Útiles

- **Documentación API**: [http://localhost:8000/api/doc](http://localhost:8000/api/doc)
- **Symfony 2.8 Docs**: [https://symfony.com/legacy/doc/2.8/](https://symfony.com/legacy/doc/2.8/)
- **Doctrine ORM**: [https://www.doctrine-project.org/projects/orm.html](https://www.doctrine-project.org/projects/orm.html)
- **FOSRestBundle**: [https://symfony.com/bundles/FOSRestBundle/2.x/index.html](https://symfony.com/bundles/FOSRestBundle/2.x/index.html)

### Contacto

- **Issues**: [GitHub Issues](https://github.com/jeremigio2706/Nutrichain-dev/issues)
- **Email**: <jetradercu@yahoo.com>

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](../LICENSE) para más detalles.

---

**NutriChain Catálogo Service v1.0.0** - Gestión de productos alimentarios de nueva generación 🚀
