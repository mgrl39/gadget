#!/bin/bash

# Colores para mensajes
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
BLUE="\033[1;34m"
CYAN="\033[1;36m"
RESET="\033[0m"
BOLD="\033[1m"

# Emojis
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
STAR="🌟"
ROCKET="🚀"
WRENCH="🔧"
BOOK="📚"
DISK="💾"
GEAR="⚙️"

# Función para mostrar encabezado
show_header() {
    clear
    echo -e "${CYAN}${BOLD}"
    echo "===================================================="
    echo "         TUTORIAL DE INSTALACIÓN DE GADGET          "
    echo "===================================================="
    echo -e "${RESET}"
    echo -e "${YELLOW}${BOLD}Este asistente te guiará paso a paso en la configuración.${RESET}\n"
}

# Verificar dependencias del sistema
check_system_dependencies() {
    echo -e "${BLUE}${BOLD}${GEAR} Verificando dependencias del sistema...${RESET}"
    
    local missing=0
    
    # Verificar Python
    if command -v python3 &>/dev/null; then
        echo -e "  ${GREEN}${CHECK} Python3 instalado${RESET}"
    else
        echo -e "  ${RED}${CROSS} Python3 no encontrado${RESET}"
        echo -e "      ${YELLOW}Instala Python3: sudo apt install python3 python3-pip${RESET}"
        missing=1
    fi
    
    # Verificar MySQL
    if command -v mysql &>/dev/null; then
        echo -e "  ${GREEN}${CHECK} MySQL instalado${RESET}"
    else
        echo -e "  ${RED}${CROSS} MySQL no encontrado${RESET}"
        echo -e "      ${YELLOW}Instala MySQL: sudo apt install mysql-server${RESET}"
        missing=1
    fi
    
    # Verificar yq (para procesamiento YAML)
    if command -v yq &>/dev/null; then
        echo -e "  ${GREEN}${CHECK} yq instalado${RESET}"
    else
        echo -e "  ${RED}${CROSS} yq no encontrado${RESET}"
        echo -e "      ${YELLOW}Instala yq: sudo apt install yq${RESET}"
        missing=1
    fi
    
    echo ""
    return $missing
}

# Verificar entorno virtual
check_venv() {
    echo -e "${BLUE}${BOLD}${BOOK} Verificando entorno virtual...${RESET}"
    
    if [ -d "venv" ]; then
        echo -e "  ${GREEN}${CHECK} Entorno virtual creado${RESET}"
        if [ -f "venv/bin/activate" ]; then
            echo -e "  ${GREEN}${CHECK} Entorno virtual configurado correctamente${RESET}"
            return 0
        else
            echo -e "  ${RED}${CROSS} Entorno virtual dañado${RESET}"
            return 1
        fi
    else
        echo -e "  ${RED}${CROSS} Entorno virtual no encontrado${RESET}"
        echo -e "      ${YELLOW}Crea el entorno: make venv${RESET}"
        return 1
    fi
    
    echo ""
}

# Verificar dependencias de Python
check_python_dependencies() {
    echo -e "${BLUE}${BOLD}${WRENCH} Verificando dependencias de Python...${RESET}"
    
    if [ ! -f "requirements.txt" ]; then
        echo -e "  ${RED}${CROSS} Archivo requirements.txt no encontrado${RESET}"
        return 1
    fi
    
    # Verificar si pip está instalado dentro del entorno virtual
    if [ -f "venv/bin/pip" ]; then
        local is_mysql_installed=$(venv/bin/pip list | grep -i "mysql-connector-python" | wc -l)
        
        if [ "$is_mysql_installed" -gt 0 ]; then
            echo -e "  ${GREEN}${CHECK} Dependencias de Python instaladas${RESET}"
            return 0
        else
            echo -e "  ${RED}${CROSS} Dependencias faltantes${RESET}"
            echo -e "      ${YELLOW}Instala dependencias: make install${RESET}"
            return 1
        fi
    else
        echo -e "  ${YELLOW}${WARNING} No se puede verificar dependencias (entorno virtual no activado)${RESET}"
        return 1
    fi
    
    echo ""
}

# Verificar configuración de base de datos
check_database_config() {
    echo -e "${BLUE}${BOLD}${DISK} Verificando configuración de base de datos...${RESET}"
    
    local db_ok=0
    
    if [ -f "config/config.yaml" ]; then
        echo -e "  ${GREEN}${CHECK} Archivo de configuración encontrado${RESET}"
        
        # Verificar existencia de archivo .env
        if [ -f ".env" ]; then
            echo -e "  ${GREEN}${CHECK} Archivo .env para variables de entorno encontrado${RESET}"
            
            # Obtener credenciales del archivo .env
            DB_USER=$(grep DB_USER .env | cut -d '=' -f2)
            DB_PASSWORD=$(grep DB_PASSWORD .env | cut -d '=' -f2)
            DB_NAME=$(grep DB_NAME .env | cut -d '=' -f2)
            
            echo -e "  ${GREEN}${CHECK} Credenciales de base de datos encontradas${RESET}"
        else
            if [ -f ".env.example" ]; then
                echo -e "  ${YELLOW}${WARNING} Archivo .env no encontrado pero existe .env.example${RESET}"
                echo -e "      ${YELLOW}Copia y configura: cp .env.example .env${RESET}"
                db_ok=1
            else
                echo -e "  ${RED}${CROSS} Archivos de configuración de entorno no encontrados${RESET}"
                db_ok=1
            fi
        fi
        
        if command -v mysql &>/dev/null && [ ! -z "$DB_NAME" ] && [ ! -z "$DB_USER" ]; then
            echo -e "  ${GREEN}${CHECK} Nombre de base de datos configurado: ${CYAN}${DB_NAME}${RESET}"
            
            # Verificar si la base de datos existe con contraseña
            if [ ! -z "$DB_PASSWORD" ]; then
                if mysql -u${DB_USER} -p${DB_PASSWORD} -e "USE ${DB_NAME}" 2>/dev/null; then
                    echo -e "  ${GREEN}${CHECK} Base de datos creada y accesible${RESET}"
                else
                    echo -e "  ${RED}${CROSS} Base de datos no encontrada o no accesible${RESET}"
                    echo -e "      ${YELLOW}Crea la base de datos: make setup-db${RESET}"
                    db_ok=1
                fi
            else
                # Sin contraseña
                if mysql -u${DB_USER} -e "USE ${DB_NAME}" 2>/dev/null; then
                    echo -e "  ${GREEN}${CHECK} Base de datos creada y accesible${RESET}"
                else
                    echo -e "  ${RED}${CROSS} Base de datos no encontrada o no accesible${RESET}"
                    echo -e "      ${YELLOW}Crea la base de datos: make setup-db${RESET}"
                    db_ok=1
                fi
            fi
        else
            echo -e "  ${YELLOW}${WARNING} No se puede verificar la base de datos (MySQL no disponible o configuración incompleta)${RESET}"
            db_ok=1
        fi
    else
        echo -e "  ${RED}${CROSS} Archivo config.yaml no encontrado${RESET}"
        db_ok=1
    fi
    
    echo ""
    return $db_ok
}

# Mostrar resumen de estado
show_status_summary() {
    local dep_ok=$1
    local venv_ok=$2
    local req_ok=$3
    local db_ok=$4
    
    echo -e "${CYAN}${BOLD}${STAR} Resumen de estado de instalación:${RESET}"
    
    if [ $dep_ok -eq 0 ] && [ $venv_ok -eq 0 ] && [ $req_ok -eq 0 ] && [ $db_ok -eq 0 ]; then
        echo -e "${GREEN}${BOLD}${ROCKET} ¡Todo configurado correctamente! El sistema está listo.${RESET}"
        echo -e "\nPuedes ejecutar el programa con:"
        echo -e "${CYAN}  make run${RESET}"
    else
        echo -e "${YELLOW}${BOLD}Pasos pendientes:${RESET}"
        
        if [ $dep_ok -ne 0 ]; then
            echo -e "${YELLOW}1. Instala las dependencias del sistema${RESET}"
        fi
        
        if [ $venv_ok -ne 0 ]; then
            echo -e "${YELLOW}2. Crea el entorno virtual: ${CYAN}make venv${RESET}"
        fi
        
        if [ $req_ok -ne 0 ]; then
            echo -e "${YELLOW}3. Instala dependencias de Python: ${CYAN}make install${RESET}"
        fi
        
        if [ $db_ok -ne 0 ]; then
            echo -e "${YELLOW}4. Configura la base de datos: ${CYAN}make setup-db${RESET}"
        fi
    fi
}

# Secuencia principal
main() {
    show_header
    
    # Verificar cada paso
    check_system_dependencies
    local dep_status=$?
    echo ""
    
    check_venv
    local venv_status=$?
    echo ""
    
    check_python_dependencies
    local req_status=$?
    echo ""
    
    check_database_config
    local db_status=$?
    echo ""
    
    # Mostrar resumen
    show_status_summary $dep_status $venv_status $req_status $db_status
}

# Ejecutar secuencia principal
main 