# 🤖 Gadget

Este proyecto está diseñado para 🕵️‍♂️ extraer información de diversas páginas web y almacenarla en una base de datos.

<p align="center">
  <img src="gadget.jpeg" width="500" alt="Gadget Logo">
</p>

## 🚀 Características

- 🔍 Scraping de diferentes sitios web
- 🗄️ Inserción de datos en MySQL
- ⚙️ Automatización con `Makefile`
- 🖥️ Panel de control web interactivo

## 📋 Requisitos

- 🐍 Python 3.x
- 🛠️ Entorno virtual (`venv`)
- 📦 Dependencias en `requirements.txt`
- 🏛️ MySQL instalado

## 🛠️ Instalación

```bash
make venv      # 🔗 Configurar entorno virtual
make install   # 📥 Instalar dependencias
```

## ⚙️ Configuración

Edita `config/config.yaml` con las credenciales de tu base de datos:

```yaml
maintainer: mgrl39
version: 1.0
scrape_website: www.cinesa.es
github_repo: gadget
```

## 🎯 Uso

```bash
make run      # 🤖 Ejecutar el scraper
make test     # ✅ Ejecutar pruebas
make clean    # 🧹 Limpiar archivos temporales
```

## 🖥️ Panel de Control

Gadget incluye un panel web interactivo para gestionar todas las operaciones:

```bash
python gadget_panel.py   # 🌐 Iniciar el panel web
```

Características del panel:
- 🌙 Modo oscuro/claro
- 📋 Historial de comandos
- 🔍 Búsqueda de acciones
- 📊 Visualización mejorada de resultados
- 📱 Diseño responsive

El panel estará disponible en: http://localhost:5000

## 📄 Estructura del Proyecto

```
gadget/
├── config/               # Configuración
├── makefiles/            # Submódulos de Makefile
├── scripts/              # Scripts de utilidad
├── templates/            # Plantillas HTML para el panel
├── static/               # Recursos estáticos (CSS, JS)
│   └── css/
│       └── styles.css    # Estilos del panel
├── utils/                # Utilidades de Python
├── checkers/             # Verificadores de configuración
├── purgers/              # Herramientas de limpieza
├── Makefile              # Automatización principal
└── gadget_panel.py       # Panel de control web
```

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.
