#!/bin/bash
set -e

# Función para crear una base de datos si no existe
function create_database() {
    local database=$1
    echo "  Creating database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        SELECT 'CREATE DATABASE $database'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$database')\gexec
EOSQL
}

# Crear las bases de datos si se proporcionan en la variable de entorno
if [ -n "$POSTGRES_MULTIPLE_DBS" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DBS"
    for db in $(echo $POSTGRES_MULTIPLE_DBS | tr ',' ' '); do
        create_database $db
        # Crear también la base de datos de test
        create_database "${db}_test"
    done
    echo "Multiple databases created"
fi
