#!/bin/bash

# Script para aplicar migraciones a múltiples bases de datos
# Versión: 2.0.0 - Soporte para bases de datos separadas

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuración
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-user}"
DB_PASSWORD="${DB_PASSWORD:-password}"

# Bases de datos por servicio
CATALOGO_DB="catalogo_db"
ALMACEN_DB="almacen_db"
TIENDA_DB="tienda_db"
REPORTES_DB="reportes_db"

# Directorio actual del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info "Configurando bases de datos separadas para NutriChain Logistics..."

# Cambiar al directorio del proyecto
cd "$PROJECT_ROOT"

log_info "Iniciando contenedor de base de datos..."
docker-compose up -d db

# Esperar a que la base de datos esté lista
log_info "Esperando a que la base de datos esté lista..."
sleep 15

# Función para ejecutar SQL en una base de datos específica
execute_sql_on_db() {
    local database="$1"
    local sql_file="$2"
    local description="$3"
    
    log_info "$description en base de datos: $database"
    
    if [ ! -f "$sql_file" ]; then
        log_error "Archivo no encontrado: $sql_file"
        return 1
    fi
    
    # Copiar archivo al contenedor
    docker cp "$sql_file" "$(docker-compose ps -q db)":/tmp/$(basename "$sql_file")
    
    # Ejecutar SQL
    docker-compose exec -T db psql -U "$DB_USER" -d "$database" -f "/tmp/$(basename "$sql_file")" 2>&1 | while read line; do
        if [[ $line == *"ERROR"* ]]; then
            log_error "$line"
        elif [[ $line == *"mensaje"* ]] || [[ $line == *"completada"* ]] || [[ $line == *"cargados"* ]]; then
            log_success "$line"
        else
            echo "  $line"
        fi
    done
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "$description completado en $database"
        return 0
    else
        log_error "$description falló en $database"
        return 1
    fi
}

# Aplicar esquema del catálogo
log_info "=== Configurando Base de Datos del Servicio de Catálogo ==="
execute_sql_on_db "$CATALOGO_DB" "database/migrations/catalogo_schema.sql" "Aplicando esquema de catálogo"
execute_sql_on_db "$CATALOGO_DB" "database/seeds/catalogo_seed.sql" "Cargando datos de productos"

# Aplicar esquema del almacén
log_info "=== Configurando Base de Datos del Servicio de Almacén ==="
execute_sql_on_db "$ALMACEN_DB" "database/migrations/almacen_schema.sql" "Aplicando esquema de almacén"
execute_sql_on_db "$ALMACEN_DB" "database/seeds/almacen_seed.sql" "Cargando datos de almacenes y stock"

# Aplicar esquema de tienda (preparado para futuro)
log_info "=== Configurando Base de Datos del Servicio de Tienda ==="
execute_sql_on_db "$TIENDA_DB" "database/migrations/tienda_schema.sql" "Aplicando esquema de tienda"
execute_sql_on_db "$TIENDA_DB" "database/seeds/tienda_seed.sql" "Cargando datos de pedidos"

# Verificar que todo esté configurado
log_info "=== Verificación de Configuración ==="

for db in $CATALOGO_DB $ALMACEN_DB $TIENDA_DB; do
    log_info "Verificando base de datos: $db"
    docker-compose exec -T db psql -U "$DB_USER" -d "$db" -c "
        SELECT 
            current_database() as database,
            count(*) as total_tables
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    " | while read line; do
        echo "  $line"
    done
done

log_success "¡Configuración de bases de datos separadas completada!"
echo ""
log_info "Bases de datos configuradas:"
echo "  - Catálogo: $CATALOGO_DB (productos)"
echo "  - Almacén: $ALMACEN_DB (inventarios y stock)"
echo "  - Tienda: $TIENDA_DB (pedidos y clientes)"
echo "  - Reportes: $REPORTES_DB (consolidación)"
echo ""
log_info "Stack de observabilidad:"
echo "  - Loki (logs): http://localhost:3100"
echo "  - Grafana (visualización): http://localhost:3000"
echo "  - Promtail (recolección): Ejecutándose en background"
echo ""
log_info "Servicios de aplicación:"
echo "  - Catálogo: http://localhost:8000"
echo "  - Almacén: http://localhost:8001"
