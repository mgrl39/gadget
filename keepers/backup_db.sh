#!/bin/bash

# Verificar si yq está instalado
if ! command -v yq &> /dev/null; then
    echo "❌ Error: 'yq' no encontrado. Instálalo con:"
    echo "    sudo apt install yq  # (Debian/Ubuntu)"
    echo "    brew install yq       # (MacOS con Homebrew)"
    echo "    sudo dnf install yq   # (Fedora)"
    exit 1
fi

# Configuración
DB_NAME=$(yq '.database.name' config/config.yaml)
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${TIMESTAMP}.sql"

# Crear directorio si no existe
mkdir -p "$BACKUP_DIR"

# Realizar el backup
echo "📂 Creando backup de la base de datos: $DB_NAME"
pg_dump -U postgres -d "$DB_NAME" -F c -f "$BACKUP_FILE"

echo "✅ Backup guardado en: $BACKUP_FILE"

