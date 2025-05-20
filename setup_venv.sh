#!/bin/bash

# Colores para la salida en terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con formato
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Función para imprimir encabezados
print_header() {
    local message=$1
    echo ""
    print_message "${BOLD}${PURPLE}" "=== $message ==="
    echo ""
}

# Función para verificar si un comando está disponible
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar la versión de Python
check_python_version() {
    print_message "${BLUE}" "🔍 Verificando versión de Python..."
    
    if ! command_exists python3; then
        print_message "${RED}" "❌ Python 3 no está instalado. Por favor instálalo e intenta de nuevo."
        exit 1
    fi
    
    # Obtener versión de Python
    python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    major_version=$(echo $python_version | cut -d. -f1)
    minor_version=$(echo $python_version | cut -d. -f2)
    
    if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 8 ]); then
        print_message "${RED}" "❌ Se requiere Python 3.8 o superior. Versión actual: $python_version"
        exit 1
    fi
    
    print_message "${GREEN}" "✅ Versión de Python compatible: $python_version"
}

# Verificar si PostgreSQL está instalado
check_postgres() {
    print_message "${BLUE}" "🔍 Verificando instalación de PostgreSQL..."
    
    if command_exists psql; then
        pg_version=$(psql --version | head -n 1)
        print_message "${GREEN}" "✅ PostgreSQL instalado: $pg_version"
    else
        print_message "${YELLOW}" "⚠️ PostgreSQL no parece estar instalado o no está en el PATH"
        print_message "${BLUE}" "ℹ️ Esto no impedirá la configuración del entorno, pero será necesario para usar la base de datos"
    fi
}

# Verificar si Chrome/Chromium está instalado
check_chrome() {
    print_message "${BLUE}" "🔍 Verificando instalación de Chrome/Chromium..."
    
    if command_exists google-chrome || command_exists google-chrome-stable || command_exists chromium || command_exists chromium-browser; then
        chrome_path=$(which google-chrome google-chrome-stable chromium chromium-browser 2>/dev/null | head -n 1)
        print_message "${GREEN}" "✅ Chrome/Chromium encontrado en: $chrome_path"
    else
        print_message "${YELLOW}" "⚠️ Chrome/Chromium no parece estar instalado"
        print_message "${BLUE}" "ℹ️ Es necesario para el funcionamiento del scraper con Selenium"
    fi
}

# Crear entorno virtual
create_venv() {
    print_message "${BLUE}" "🔧 Creando entorno virtual..."
    
    if [ -d "venv" ]; then
        print_message "${YELLOW}" "ℹ️ Ya existe un entorno virtual"
        read -p "¿Deseas eliminar y recrear el entorno virtual? (s/N): " response
        
        if [[ "$response" =~ ^[Ss]$ ]]; then
            print_message "${YELLOW}" "🗑️ Eliminando entorno virtual existente..."
            rm -rf venv
        else
            print_message "${GREEN}" "✅ Se usará el entorno virtual existente"
            return 0
        fi
    fi
    
    # Crear el entorno virtual
    python3 -m venv venv
    
    if [ $? -eq 0 ]; then
        print_message "${GREEN}" "✅ Entorno virtual creado correctamente"
    else
        print_message "${RED}" "❌ Error al crear el entorno virtual"
        exit 1
    fi
}

# Instalar dependencias
install_dependencies() {
    print_message "${BLUE}" "📦 Instalando dependencias..."
    
    # Activar el entorno virtual
    source venv/bin/activate
    
    # Actualizar pip
    pip install --upgrade pip
    
    if [ $? -ne 0 ]; then
        print_message "${RED}" "❌ Error al actualizar pip"
        exit 1
    fi
    
    print_message "${GREEN}" "✅ pip actualizado correctamente"
    
    # Verificar si existe requirements.txt
    if [ ! -f "requirements.txt" ]; then
        print_message "${YELLOW}" "⚠️ No se encontró el archivo requirements.txt"
        print_message "${BLUE}" "📝 Creando archivo requirements.txt con dependencias básicas..."
        
        # Crear requirements.txt básico
        cat > requirements.txt << EOF
# Cliente HTTP y Scraping
requests==2.31.0
beautifulsoup4==4.12.2
selenium>=4.5.0
webdriver-manager>=3.8.4

# Procesamiento de imágenes
Pillow>=9.4.0

# Formateo y CLI
colorama>=0.4.5
argparse>=1.4.0
pyyaml==6.0.1

# Base de datos
psycopg2-binary>=2.9.5  # Adaptador PostgreSQL (versión binaria para facilitar instalación)

# Multithreading y procesamiento paralelo
futures>=3.0.5

# Utilidades
pytest>=7.2.0
python-dotenv>=0.21.0
EOF
    fi
    
    # Instalar dependencias
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        print_message "${RED}" "❌ Error al instalar dependencias"
        exit 1
    fi
    
    print_message "${GREEN}" "✅ Dependencias instaladas correctamente"
    
    # Desactivar el entorno virtual
    deactivate
}

# Crear estructura básica de directorios
create_structure() {
    print_message "${BLUE}" "📂 Verificando estructura de directorios..."
    
    # Lista de directorios a crear
    directories=(
        "config"
        "scrapers"
        "utils"
        "data/peliculas"
        "data/imagenes"
        "backups"
        "logs"
    )
    
    # Crear directorios si no existen
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_message "${GREEN}" "✅ Directorio creado: $dir"
        else
            print_message "${GREEN}" "✅ Directorio existente: $dir"
        fi
    done
    
    # Crear archivo config.yaml básico si no existe
    if [ ! -f "config/config.yaml" ]; then
        print_message "${BLUE}" "📝 Creando archivo de configuración básico..."
        
        cat > config/config.yaml << EOF
maintainer: mgrl39
github_repo: gadget
version: 1.0

# Scraper
scrape_website: www.cinesa.es

# 📦 Dependencias del sistema
dependencies:
  - python3
  - python3-pip
  - python3-venv
  - postgresql

# 🔑 Credenciales 
# IMPORTANTE: En producción, usar .env
database:
  host: "localhost"
  port: 5432
  user: "postgres"
  password: "postgres"
  name: "cinedb"

# 🔍 Configuración del Web Scraper
scraper:
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
  headless: true
  max_retries: 3
  timeout: 10  # segundos

# 📜 Logging y Debug
logging:
  level: "INFO"  # Opciones: DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_file: "logs/gadget.log"
EOF
        
        print_message "${GREEN}" "✅ Archivo de configuración creado"
    fi
}

# Función principal
main() {
    print_header "🚀 CONFIGURACIÓN DEL ENTORNO PARA GADGET SCRAPER 🚀"
    
    # Verificar requisitos
    check_python_version
    check_postgres
    check_chrome
    
    # Crear entorno virtual
    create_venv
    
    # Instalar dependencias
    install_dependencies
    
    # Crear estructura básica
    create_structure
    
    print_header "✅ CONFIGURACIÓN COMPLETADA CON ÉXITO ✅"
    
    print_message "${CYAN}" "Para activar el entorno virtual:"
    print_message "${BOLD}${CYAN}" "    source venv/bin/activate"
    
    print_message "${CYAN}" "\nPara ejecutar el scraper:"
    print_message "${BOLD}${CYAN}" "    python gadget.py scrape"
    
    print_message "${BOLD}${BLUE}" "\n¡Feliz scraping! 🕷️\n"
}

# Ejecutar la función principal
main 