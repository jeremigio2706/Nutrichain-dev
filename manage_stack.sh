#!/bin/bash

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuración
PROJECT_NAME="nutrichain"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}NUTRICHAIN STACK MANAGER${NC}"
    echo -e "${BLUE}========================${NC}"
    echo ""
    echo "Uso: $0 [COMANDO] [OPCIONES]"
    echo ""
    echo -e "${YELLOW}Comandos principales:${NC}"
    echo "  setup     - Configurar entorno inicial"
    echo "  build     - Construir todas las imágenes"
    echo "  up        - Levantar todos los servicios"
    echo "  down      - Detener todos los servicios"
    echo "  restart   - Reiniciar todos los servicios"
    echo "  logs      - Mostrar logs de servicios"
    echo "  status    - Mostrar estado de servicios"
    echo "  test      - Ejecutar pruebas de conectividad"
    echo "  clean     - Limpiar recursos Docker"
    echo "  backup    - Crear backup de datos"
    echo "  restore   - Restaurar backup de datos"
    echo ""
    echo -e "${YELLOW}Comandos de servicio específico:${NC}"
    echo "  service [SERVICIO] [ACCION] - Gestionar servicio específico"
    echo "    Servicios: catalogo, almacen, tienda, reportes, postgres, redis"
    echo "    Acciones: start, stop, restart, logs, shell"
    echo ""
    echo -e "${YELLOW}Comandos de desarrollo:${NC}"
    echo "  migrate   - Ejecutar migraciones de BD"
    echo "  seed      - Cargar datos de prueba"
    echo "  reset     - Resetear base de datos"
    echo "  monitor   - Abrir dashboard de monitoreo"
    echo ""
    echo -e "${YELLOW}Opciones:${NC}"
    echo "  -d, --detach    - Ejecutar en background"
    echo "  -f, --force     - Forzar operación"
    echo "  -v, --verbose   - Output detallado"
    echo "  -h, --help      - Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  $0 up -d                    # Levantar en background"
    echo "  $0 service tienda logs      # Ver logs de tienda"
    echo "  $0 service postgres shell   # Acceder a PostgreSQL"
    echo "  $0 test --verbose           # Pruebas detalladas"
}

# Función para logging
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} ${timestamp} - $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} ${timestamp} - $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${timestamp} - $message"
            ;;
        "DEBUG")
            if [ "$VERBOSE" = "true" ]; then
                echo -e "${CYAN}[DEBUG]${NC} ${timestamp} - $message"
            fi
            ;;
    esac
}

# Función para verificar prerrequisitos
check_prerequisites() {
    log "INFO" "Verificando prerrequisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker no está instalado"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log "ERROR" "Docker Compose no está instalado"
        exit 1
    fi
    
    # Verificar que Docker esté corriendo
    if ! docker info &> /dev/null; then
        log "ERROR" "Docker daemon no está ejecutándose"
        exit 1
    fi
    
    # Verificar archivo compose
    if [ ! -f "$COMPOSE_FILE" ]; then
        log "ERROR" "Archivo $COMPOSE_FILE no encontrado"
        exit 1
    fi
    
    log "INFO" "Prerrequisitos verificados ✅"
}

# Función para configurar entorno
setup_environment() {
    log "INFO" "Configurando entorno..."
    
    if [ -f "./setup_environment.sh" ]; then
        ./setup_environment.sh
    else
        log "WARN" "Script setup_environment.sh no encontrado"
    fi
}

# Función para construir imágenes
build_images() {
    log "INFO" "Construyendo imágenes Docker..."
    
    local force_flag=""
    if [ "$FORCE" = "true" ]; then
        force_flag="--no-cache"
    fi
    
    docker-compose build $force_flag
    
    log "INFO" "Imágenes construidas exitosamente ✅"
}

# Función para levantar servicios
start_services() {
    log "INFO" "Iniciando servicios..."
    
    local detach_flag=""
    if [ "$DETACH" = "true" ]; then
        detach_flag="-d"
    fi
    
    # Verificar si ya están corriendo
    if docker-compose ps -q | grep -q .; then
        log "WARN" "Algunos servicios ya están ejecutándose"
        if [ "$FORCE" != "true" ]; then
            read -p "¿Desea continuar? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log "INFO" "Operación cancelada"
                exit 0
            fi
        fi
    fi
    
    # Levantar servicios en orden
    log "INFO" "Iniciando base de datos..."
    docker-compose up $detach_flag postgres redis
    
    if [ "$DETACH" = "true" ]; then
        # Esperar a que la BD esté lista
        log "INFO" "Esperando a que PostgreSQL esté listo..."
        timeout 60 bash -c 'until docker-compose exec -T postgres pg_isready -U user; do sleep 2; done'
        
        log "INFO" "Iniciando servicios de aplicación..."
        docker-compose up $detach_flag
    else
        log "INFO" "Iniciando todos los servicios..."
        docker-compose up $detach_flag
    fi
    
    if [ "$DETACH" = "true" ]; then
        log "INFO" "Servicios iniciados en background ✅"
        show_status
    fi
}

# Función para detener servicios
stop_services() {
    log "INFO" "Deteniendo servicios..."
    
    docker-compose down
    
    if [ "$FORCE" = "true" ]; then
        log "INFO" "Removiendo volúmenes..."
        docker-compose down -v
    fi
    
    log "INFO" "Servicios detenidos ✅"
}

# Función para reiniciar servicios
restart_services() {
    log "INFO" "Reiniciando servicios..."
    
    stop_services
    sleep 2
    start_services
    
    log "INFO" "Servicios reiniciados ✅"
}

# Función para mostrar logs
show_logs() {
    local service=${1:-""}
    local lines=${2:-"100"}
    
    if [ -n "$service" ]; then
        log "INFO" "Mostrando logs de $service..."
        docker-compose logs --tail=$lines -f "$service"
    else
        log "INFO" "Mostrando logs de todos los servicios..."
        docker-compose logs --tail=$lines -f
    fi
}

# Función para mostrar estado
show_status() {
    log "INFO" "Estado de servicios:"
    echo ""
    
    # Estado de contenedores
    docker-compose ps
    echo ""
    
    # Estado de puertos
    log "INFO" "Puertos expuestos:"
    echo "  • PostgreSQL:    5432"
    echo "  • Redis:         6379"
    echo "  • Catálogo:      8000"
    echo "  • Almacén:       8001"
    echo "  • Reportes:      8002"
    echo "  • Tienda:        8003"
    echo "  • Grafana:       3000"
    echo "  • Loki:          3100"
    echo ""
    
    # Verificar conectividad básica
    log "INFO" "Verificando conectividad básica..."
    
    services=("postgres:5432" "redis:6379")
    
    for service in "${services[@]}"; do
        service_name=${service%:*}
        port=${service#*:}
        
        if docker-compose exec -T "$service_name" echo "ok" &>/dev/null; then
            echo -e "  ✅ $service_name: Activo"
        else
            echo -e "  ❌ $service_name: Inactivo"
        fi
    done
}

# Función para pruebas de conectividad
run_tests() {
    log "INFO" "Ejecutando pruebas de conectividad..."
    
    # Verificar que los servicios estén corriendo
    if ! docker-compose ps | grep -q "Up"; then
        log "ERROR" "Los servicios no están ejecutándose. Use '$0 up' primero."
        exit 1
    fi
    
    # Función auxiliar para testing HTTP
    test_http_endpoint() {
        local name=$1
        local url=$2
        local expected_status=${3:-200}
        
        log "DEBUG" "Probando $name en $url"
        
        local status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        
        if [ "$status" = "$expected_status" ]; then
            echo -e "  ✅ $name: HTTP $status"
            return 0
        else
            echo -e "  ❌ $name: HTTP $status (esperado $expected_status)"
            return 1
        fi
    }
    
    # Esperar a que los servicios estén completamente listos
    log "INFO" "Esperando a que los servicios estén listos..."
    sleep 10
    
    # Probar endpoints
    echo ""
    log "INFO" "Probando endpoints de servicios:"
    
    failed_tests=0
    
    # Test PostgreSQL
    if docker-compose exec -T postgres pg_isready -U user &>/dev/null; then
        echo -e "  ✅ PostgreSQL: Conectividad OK"
    else
        echo -e "  ❌ PostgreSQL: Sin conectividad"
        ((failed_tests++))
    fi
    
    # Test Redis
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        echo -e "  ✅ Redis: Conectividad OK"
    else
        echo -e "  ❌ Redis: Sin conectividad"
        ((failed_tests++))
    fi
    
    # Test servicios web (con retry)
    web_services=(
        "Catálogo:http://localhost:8000"
        "Almacén:http://localhost:8001/health"
        "Reportes:http://localhost:8002/health"
        "Tienda:http://localhost:8003/health"
    )
    
    for service in "${web_services[@]}"; do
        name=${service%:*}
        url=${service#*:}
        
        # Retry logic
        success=false
        for i in {1..3}; do
            if test_http_endpoint "$name" "$url"; then
                success=true
                break
            fi
            if [ $i -lt 3 ]; then
                log "DEBUG" "Reintentando $name en 5 segundos..."
                sleep 5
            fi
        done
        
        if [ "$success" = false ]; then
            ((failed_tests++))
        fi
    done
    
    echo ""
    if [ $failed_tests -eq 0 ]; then
        log "INFO" "Todas las pruebas pasaron ✅"
        return 0
    else
        log "WARN" "$failed_tests prueba(s) fallaron ⚠️"
        return 1
    fi
}

# Función para gestionar servicios específicos
manage_service() {
    local service=$1
    local action=$2
    
    if [ -z "$service" ] || [ -z "$action" ]; then
        log "ERROR" "Uso: $0 service <servicio> <accion>"
        echo "Servicios: catalogo, almacen, tienda, reportes, postgres, redis"
        echo "Acciones: start, stop, restart, logs, shell, exec"
        exit 1
    fi
    
    case $action in
        "start")
            log "INFO" "Iniciando servicio $service..."
            docker-compose up -d "$service"
            ;;
        "stop")
            log "INFO" "Deteniendo servicio $service..."
            docker-compose stop "$service"
            ;;
        "restart")
            log "INFO" "Reiniciando servicio $service..."
            docker-compose restart "$service"
            ;;
        "logs")
            show_logs "$service"
            ;;
        "shell")
            log "INFO" "Accediendo a shell de $service..."
            case $service in
                "postgres")
                    docker-compose exec postgres psql -U user -d catalogo_db
                    ;;
                "redis")
                    docker-compose exec redis redis-cli
                    ;;
                *)
                    docker-compose exec "$service" /bin/bash
                    ;;
            esac
            ;;
        "exec")
            shift 2  # Remove service and action from args
            log "INFO" "Ejecutando comando en $service: $*"
            docker-compose exec "$service" "$@"
            ;;
        *)
            log "ERROR" "Acción no reconocida: $action"
            exit 1
            ;;
    esac
}

# Función para migraciones
run_migrations() {
    log "INFO" "Ejecutando migraciones de base de datos..."
    
    # Verificar que PostgreSQL esté corriendo
    if ! docker-compose exec -T postgres pg_isready -U user &>/dev/null; then
        log "ERROR" "PostgreSQL no está disponible"
        exit 1
    fi
    
    # Ejecutar scripts SQL
    if [ -d "database/migrations" ]; then
        for migration in database/migrations/*.sql; do
            if [ -f "$migration" ]; then
                local db_name=$(basename "$migration" | cut -d'_' -f1)
                log "INFO" "Aplicando migración: $(basename $migration)"
                docker-compose exec -T postgres psql -U user -d "${db_name}_db" -f "/docker-entrypoint-initdb.d/migrations/$(basename $migration)"
            fi
        done
    fi
    
    log "INFO" "Migraciones completadas ✅"
}

# Función para cargar datos de prueba
load_seed_data() {
    log "INFO" "Cargando datos de prueba..."
    
    if [ -d "database/seeds" ]; then
        for seed in database/seeds/*.sql; do
            if [ -f "$seed" ]; then
                local db_name=$(basename "$seed" | cut -d'_' -f1)
                log "INFO" "Cargando seed: $(basename $seed)"
                docker-compose exec -T postgres psql -U user -d "${db_name}_db" -f "/docker-entrypoint-initdb.d/seeds/$(basename $seed)"
            fi
        done
    fi
    
    log "INFO" "Datos de prueba cargados ✅"
}

# Función para limpiar recursos
clean_resources() {
    log "INFO" "Limpiando recursos Docker..."
    
    if [ "$FORCE" = "true" ]; then
        log "WARN" "Limpieza forzada - esto eliminará TODOS los datos"
        docker-compose down -v --remove-orphans
        docker system prune -af --volumes
    else
        log "INFO" "Limpieza estándar"
        docker-compose down --remove-orphans
        docker system prune -f
    fi
    
    log "INFO" "Limpieza completada ✅"
}

# Función para backup
create_backup() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    log "INFO" "Creando backup en $backup_dir..."
    
    # Backup de base de datos
    if docker-compose exec -T postgres pg_isready -U user &>/dev/null; then
        databases=("catalogo_db" "almacen_db" "tienda_db" "reportes_db")
        
        for db in "${databases[@]}"; do
            log "INFO" "Backup de $db..."
            docker-compose exec -T postgres pg_dump -U user "$db" > "$backup_dir/${db}.sql"
        done
    fi
    
    # Backup de configuración
    cp -r .env docker-compose.yml "$backup_dir/" 2>/dev/null || true
    
    log "INFO" "Backup completado en $backup_dir ✅"
}

# Función para abrir monitoreo
open_monitoring() {
    log "INFO" "Abriendo dashboard de monitoreo..."
    
    local urls=(
        "Grafana:http://localhost:3000"
        "Tienda API:http://localhost:8003/docs"
        "Almacén API:http://localhost:8001/docs"
        "Reportes API:http://localhost:8002/docs"
    )
    
    for url_info in "${urls[@]}"; do
        name=${url_info%:*}
        url=${url_info#*:}
        echo "  🌐 $name: $url"
    done
    
    # Intentar abrir Grafana automáticamente
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:3000" &>/dev/null &
    elif command -v open &> /dev/null; then
        open "http://localhost:3000" &>/dev/null &
    fi
}

# Función principal
main() {
    local command=${1:-"help"}
    shift || true
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--detach)
                DETACH="true"
                shift
                ;;
            -f|--force)
                FORCE="true"
                shift
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                # Argumentos adicionales específicos del comando
                break
                ;;
        esac
    done
    
    # Verificar prerrequisitos para la mayoría de comandos
    case $command in
        "help"|"--help"|"-h")
            show_help
            exit 0
            ;;
        "setup")
            setup_environment
            exit 0
            ;;
        *)
            check_prerequisites
            ;;
    esac
    
    # Ejecutar comando
    case $command in
        "build")
            build_images
            ;;
        "up"|"start")
            start_services
            ;;
        "down"|"stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            show_logs "$@"
            ;;
        "status"|"ps")
            show_status
            ;;
        "test")
            run_tests
            ;;
        "service")
            manage_service "$@"
            ;;
        "migrate")
            run_migrations
            ;;
        "seed")
            load_seed_data
            ;;
        "reset")
            log "WARN" "Esto eliminará todos los datos de la base de datos"
            if [ "$FORCE" != "true" ]; then
                read -p "¿Está seguro? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    log "INFO" "Operación cancelada"
                    exit 0
                fi
            fi
            stop_services
            clean_resources
            start_services
            run_migrations
            load_seed_data
            ;;
        "clean")
            clean_resources
            ;;
        "backup")
            create_backup
            ;;
        "monitor")
            open_monitoring
            ;;
        *)
            log "ERROR" "Comando no reconocido: $command"
            echo "Use '$0 help' para ver los comandos disponibles"
            exit 1
            ;;
    esac
}

# Manejo de señales
trap 'log "INFO" "Operación interrumpida por el usuario"; exit 130' INT TERM

# Ejecutar función principal
main "$@"
