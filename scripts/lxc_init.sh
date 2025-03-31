#!/bin/bash

# Verificar si LXC está instalado
echo "🔍 Verificando instalación de LXC..."
if ! command -v lxc &> /dev/null; then
    echo "⚠️ LXC no está instalado. Instalándolo..."
    sudo apt update && sudo apt install -y lxc lxc-utils git
fi

echo "🚀 Creando contenedor LXC..."
CONTAINER_NAME="mi-contenedor"
IMAGE="ubuntu"
RELEASE="22.04"

# Crear el contenedor
lxc-create -n $CONTAINER_NAME -t download -- -d $IMAGE -r $RELEASE -a amd64

# Configurar red y actualizar
lxc-start -n $CONTAINER_NAME
sleep 5  # Esperar a que arranque
lxc-attach -n $CONTAINER_NAME -- bash -c "apt update && apt install -y iproute2 git"

# Clonar el repositorio en el contenedor
echo "📥 Clonando repositorio en el contenedor..."
lxc-attach -n $CONTAINER_NAME -- bash -c "git clone https://github.com/mgrl39/rsv_sys_datafeed /root/rsv_sys_datafeed"

echo "✅ Contenedor $CONTAINER_NAME creado, repositorio clonado y en ejecución."
echo "Para acceder: sudo lxc-attach -n $CONTAINER_NAME"
