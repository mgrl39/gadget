# Makefile para el proyecto Gadget

.PHONY: help
help:  # 📖 Muestra los comandos disponibles
	@echo "\033[1;34m🔹 Comandos disponibles:\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?#' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?#"}; {printf "  \033[1;36m%-20s\033[0m %s\n", $$1, $$2}'

# 🔥 1️⃣ LIMPIEZA Y CONFIGURACIÓN
.PHONY: clean
clean:  # 🧹 Limpia archivos temporales
	rm -rf build venv __pycache__ *.log *.db

.PHONY: build
build:  # 🏗️ Crea la estructura de carpetas necesarias
	mkdir -p build logs output

# 📦 2️⃣ ENTORNO VIRTUAL Y DEPENDENCIAS
.PHONY: venv
venv:  # 🐍 Crea y activa el entorno virtual
	@if [ ! -d "venv" ]; then python3 -m venv venv; fi
	@echo "🔗 Activando entorno virtual..."
	source venv/bin/activate

.PHONY: install
install:  # 📥 Instala dependencias de Python
	@echo "📦 Instalando dependencias..."
	source venv/bin/activate && pip install --upgrade pip
	source venv/bin/activate && pip install -r requirements.txt

# 🌍 3️⃣ WEB SCRAPING
.PHONY: scrape
scrape:  # 🌐 Ejecuta el scraper
	source venv/bin/activate && python scraper.py

# 🗄️ 4️⃣ BASE DE DATOS
.PHONY: db-setup
db-setup:  # 🛠️ Configura la base de datos
	@echo "⚙️ Configurando base de datos..."
	source venv/bin/activate && python db/setup.py

.PHONY: db-reset
db-reset:  # 🔄 Reinicia la base de datos
	@echo "🔥 Eliminando y recreando base de datos..."
	source venv/bin/activate && python db/reset.py

.PHONY: db-backup
db-backup:  # 💾 Realiza un backup de la base de datos
	@echo "📂 Creando backup..."
	source venv/bin/activate && python db/backup.py

# 🐳 5️⃣ CONTENEDORES (LXC/Docker)
.PHONY: lxc-setup
lxc-setup:  # 🚀 Crea un contenedor LXC
	@echo "🛠️ Creando contenedor LXC..."
	bash scripts/lxc_setup.sh

.PHONY: docker-build
docker-build:  # 🏗️ Construye la imagen de Docker
	docker build -t gadget-app .

.PHONY: docker-run
docker-run:  # ▶️ Ejecuta el contenedor de Docker
	docker run --rm -p 8080:8080 gadget-app

# ✅ 6️⃣ PRUEBAS Y DESPLIEGUE
.PHONY: test
test:  # 🧪 Ejecuta los tests
	@echo "✅ Ejecutando tests..."
	source venv/bin/activate && pytest tests/

.PHONY: deploy
deploy:  # 🚀 Despliega la aplicación
	@echo "🌍 Desplegando aplicación..."
	bash scripts/deploy.sh

