# Usar una imagen base con PHP 7.2 y Apache (requerimiento específico)
FROM php:7.2-apache

# --- PASO 1: Configurar repositorios de Debian para compatibilidad ---
RUN echo "deb http://archive.debian.org/debian buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list && \
    echo "Acquire::Check-Valid-Until false;" > /etc/apt/apt.conf.d/99no-check-valid-until

# --- PASO 2: Instalar dependencias del sistema ---
RUN apt-get update && apt-get install -y \
    libzip-dev \
    zip \
    unzip \
    libpq-dev \
    git \
    curl \
    && docker-php-ext-install pdo pdo_pgsql zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- PASO 3: Instalar Composer ---
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# --- PASO 4: Configuración de Apache ---
RUN a2enmod rewrite

# --- PASO 4.1: CONFIGURACIÓN DE LOGS PARA DOCKER ---
RUN sed -i 's#ErrorLog /proc/self/fd/2#ErrorLog /var/log/apache2/error.log#g' /etc/apache2/apache2.conf && \
    sed -i 's#CustomLog /proc/self/fd/1 combined#CustomLog /var/log/apache2/access.log combined#g' /etc/apache2/apache2.conf

# --- PASO 5: Configurar el entorno de la aplicación ---
WORKDIR /var/www/html

# Copiar TODO el código de la aplicación
COPY . .

# --- PASO 6: Instalar dependencias ---
RUN composer install --optimize-autoloader --no-dev --no-interaction

# --- PASO 7: CORRECCIÓN CRÍTICA DE PERMISOS ---
# Crear los directorios necesarios si no existen
RUN mkdir -p var/cache var/logs var/sessions && \
    # Cambiar propietario de toda la aplicación a www-data
    chown -R www-data:www-data /var/www/html && \
    # Dar permisos de escritura específicos a los directorios que Symfony necesita
    chmod -R 775 var/cache var/logs var/sessions && \
    # Asegurar que los archivos PHP sean ejecutables
    find /var/www/html -name "*.php" -type f -exec chmod 644 {} \; && \
    # Permisos especiales para el directorio web
    chmod -R 755 web/

# --- PASO 8: Limpiar cache existente ---
RUN rm -rf var/cache/* var/logs/* 2>/dev/null || true

# --- PASO 9: Copiar configuración de Apache ---
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf

# --- PASO 10: Variables de entorno ---
ENV SYMFONY_ENV=prod
ENV SYMFONY_DEBUG=0

# --- PASO 11: Verificación final de permisos ---
RUN echo "=== VERIFICACIÓN DE PERMISOS ===" && \
    ls -la var/ && \
    echo "=== PROPIETARIO DE ARCHIVOS ===" && \
    ls -la /var/www/html/ | head -10

EXPOSE 80