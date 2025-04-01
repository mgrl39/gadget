#!/bin/bash

# Colores
BLUE="\033[1;34m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

# Definir versiones mínimas requeridas
PYTHON_MIN="3.8"
PHP_MIN="7.4"
MYSQL_MIN="5.7"

# Función para comparar versiones
version_greater_equal() {
  awk -v ver1="$1" -v ver2="$2" 'BEGIN {
        split(ver1, a, ".");
        split(ver2, b, ".");
        for (i = 1; i <= 3; i++) {
            if (a[i] + 0 > b[i] + 0) { exit 0 }
            if (a[i] + 0 < b[i] + 0) { exit 1 }
        }
        exit 0
    }'
}

echo -e "${BLUE}🔍 Verificando entorno...${RESET}"

# Verificar Python
if command -v python3 &>/dev/null; then
  PYTHON_VER=$(python3 --version 2>&1 | awk '{print $2}')
  if version_greater_equal "$PYTHON_VER" "$PYTHON_MIN"; then
    echo -e "✅ ${GREEN}Python $PYTHON_VER encontrado (mínimo requerido: $PYTHON_MIN)${RESET}"
  else
    echo -e "⚠️ ${YELLOW}Python $PYTHON_VER encontrado, pero se requiere al menos $PYTHON_MIN${RESET}"
  fi
else
  echo -e "❌ ${RED}Python no encontrado${RESET}"
fi

# Verificar PHP
if command -v php &>/dev/null; then
  PHP_VER=$(php -v | head -n 1 | awk '{print $2}')
  if version_greater_equal "$PHP_VER" "$PHP_MIN"; then
    echo -e "✅ ${GREEN}PHP $PHP_VER encontrado (mínimo requerido: $PHP_MIN)${RESET}"
  else
    echo -e "⚠️ ${YELLOW}PHP $PHP_VER encontrado, pero se requiere al menos $PHP_MIN${RESET}"
  fi
else
  echo -e "❌ ${RED}PHP no encontrado${RESET}"
fi

# Verificar MySQL
if command -v mysql &>/dev/null; then
  MYSQL_VER=$(mysql --version | grep -oP '[0-9]+\.[0-9]+\.[0-9]+')
  if version_greater_equal "$MYSQL_VER" "$MYSQL_MIN"; then
    echo -e "✅ ${GREEN}MySQL $MYSQL_VER encontrado (mínimo requerido: $MYSQL_MIN)${RESET}"
  else
    echo -e "⚠️ ${YELLOW}MySQL $MYSQL_VER encontrado, pero se requiere al menos $MYSQL_MIN${RESET}"
  fi
else
  echo -e "❌ ${RED}MySQL no encontrado${RESET}"
fi

# Verificar yq
if command -v yq &>/dev/null; then
  YQ_VER=$(yq --version | awk '{print $NF}')
  echo -e "✅ ${GREEN}yq $YQ_VER encontrado${RESET}"
else
  echo -e "❌ ${RED}yq no encontrado. Instálalo con: sudo snap install yq (Debian/Ubuntu)${RESET}"
fi
