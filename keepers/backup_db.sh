#!/bin/bash

# Verificar si yq está instalado
if ! command -v yq &>/dev/null; then
  echo "❌ Error: 'yq' no encontrado. Instálalo con:"
  echo "    sudo apt install yq  # (Debian/Ubuntu)"
  exit 1
fi

# Configuración
DB_HOST=$(yq '.database.host' config/config.yaml)
DB_USER=$(yq '.database.user' config/config.yaml)
DB_PASS=$(yq '.database.password' config/config.yaml)
DB_NAME=$(yq '.database.name' config/config.yaml)
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${TIMESTAMP}.sql"

# Crear directorio si no existe
mkdir -p "$BACKUP_DIR"

# Realizar el backup
echo "📂 Creando backup de la base de datos: $DB_NAME"
mysqldump -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" >"$BACKUP_FILE"

# Comprimir el backup
gzip "$BACKUP_FILE"
echo "✅ Backup guardado en: ${BACKUP_FILE}.gz"
