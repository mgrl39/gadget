# 🤖 Gadget

Este proyecto está diseñado para 🕵️‍♂️ extraer información de películas de Cinesa y almacenarla en una base de datos PostgreSQL.

## 🚀 Características

- 🔍 Scraping avanzado del sitio web de Cinesa
- 🗄️ Almacenamiento de datos en PostgreSQL
- 🖼️ Descarga y optimización automática de imágenes
- 🧵 Procesamiento multihilo para mayor velocidad

## 📋 Requisitos

- 🐍 Python 3.8+
- 🛠️ Entorno virtual (`venv`)
- 📦 Dependencias en `requirements.txt`
- 🏛️ PostgreSQL instalado

## 🛠️ Instalación

```bash
python gadget.py setup   # 🔧 Configurar entorno y base de datos
```

## ⚙️ Configuración

Edita `config/config.yaml` para configurar la conexión a la base de datos y opciones del scraper.

## 🎯 Uso

```bash
# Ejecutar scraper completo
python gadget.py scrape

# Solo obtener lista de películas
python gadget.py scrape --solo-lista

# Limitar a un número máximo de películas
python gadget.py scrape --max 10

# Usar múltiples hilos
python gadget.py scrape --hilos 3

# Crear backup de la base de datos
python gadget.py backup

# Purgar la base de datos
python gadget.py purge

# Limpiar archivos temporales
python gadget.py clean
```

## 📄 Estructura del Proyecto

```

```
