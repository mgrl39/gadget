#!/bin/bash

# Habilitar modo estricto para manejar errores
set -e

# Obtener el directorio donde se encuentra este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cambiar al directorio del script para asegurar rutas relativas
cd "$SCRIPT_DIR/.."

echo "🔄 Actualizando paquetes..."
sudo apt update && sudo apt upgrade -y

echo "📦 Instalando dependencias del sistema..."
sudo apt install -y python3 python3-pip python3-venv unzip wget

# Verificar si el entorno virtual ya existe
if [ ! -d "venv" ]; then
  echo "🚀 Creando entorno virtual..."
  python3 -m venv venv
else
  echo "✅ El entorno virtual ya existe, omitiendo creación."
fi

echo "🔗 Activando entorno virtual..."
source venv/bin/activate

echo "📥 Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar si Selenium y WebDriver Manager ya están instalados
if ! pip list | grep -q selenium; then
  echo "🌐 Instalando Selenium y WebDriver Manager..."
  pip install selenium webdriver-manager
else
  echo "✅ Selenium ya está instalado."
fi

# Verificar si Google Chrome está instalado
if ! command -v google-chrome &>/dev/null; then
  echo "🌍 Instalando Google Chrome..."
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt --fix-broken install -y
  rm google-chrome-stable_current_amd64.deb
else
  echo "✅ Google Chrome ya está instalado."
fi

echo "✅ Instalación completada. Para ejecutar el scraper, usa:"
echo "   source venv/bin/activate && python run.py"
