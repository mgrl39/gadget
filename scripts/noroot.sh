#!/bin/bash

# Habilitar modo estricto para manejar errores
set -e

# Obtener el directorio donde se encuentra este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cambiar al directorio del script para asegurar rutas relativas
cd "$SCRIPT_DIR/.."

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

echo "✅ Instalación completada. Para ejecutar el scraper, usa:"
echo "   source venv/bin/activate && python run.py"
