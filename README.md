# 🤖 Gadget

Este proyecto está diseñado para 🕵️‍♂️ extraer información de diversas páginas web y almacenarla en una base de datos.

<p align="center">
  <img src="gadget.jpeg" width="500" alt="Gadget Logo">
</p>

## 🚀 Características

- 🔍 Scraping de diferentes sitios web
- 🗄️ Inserción de datos en MySQL
- ⚙️ Automatización con `Makefile`

## 📋 Requisitos

- 🐍 Python 3.x
- 🛠️ Entorno virtual (`venv`)
- 📦 Dependencias en `requirements.txt`
- 🏛️ MySQL instalado

```
## 🛠️ Instalación

```bash
make venv   # 🔗 Configurar entorno virtual
make install   # 📥 Instalar dependencias
```

## ⚙️ Configuración

Edita `config/config.yaml` con las credenciales de tu base de datos:

```yaml
maintainer: mgrl39
version: 1.0
scrape_website: www.cinesa.es
github_repo: gadget

database:
  host: "localhost"
  port: 3306
  user: "gadget_user"
  password: "supersegura"
  name: "gadget_db"
```

## 🎯 Uso

```bash
make run   # 🤖 Ejecutar el scraper
make test   # ✅ Ejecutar pruebas
make clean   # 🧹 Limpiar archivos temporales
```

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.
