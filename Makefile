# Makefile para el proyecto Gadget
# mgrl39

.PHONY: help
help:  # 📖 Muestra los comandos disponibles
	@echo "\033[1;34m🔹 Comandos disponibles:\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?#' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?#"}; {printf "  \033[1;36m%-20s\033[0m %s\n", $$1, $$2}'

# 🔥 1️⃣ LIMPIEZA Y CONFIGURACIÓN
.PHONY: clean
clean:  # 🧹 Limpia archivos temporales y elimina el entorno virtual
	@echo "🔥 Eliminando archivos temporales y el entorno virtual..."
	rm -rf build venv __pycache__ *.log *.db
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

.PHONY: build
build:  # 🏗️ Crea la estructura de carpetas necesarias
	mkdir -p build logs output

# 📦 2️⃣ ENTORNO VIRTUAL Y DEPENDENCIAS
.PHONY: venv
venv:  # 🐍 Crea y activa el entorno virtual
	@if [ ! -d "venv" ]; then python3 -m venv venv; fi
	@echo "🔗 Activando entorno virtual..."
	. venv/bin/activate

.PHONY: install
install:  # 📥 Instala dependencias de Python
	@echo "📦 Instalando dependencias..."
	source venv/bin/activate && pip install --upgrade pip
	source venv/bin/activate && pip install -r requirements.txt

# 🌍 3️⃣ WEB SCRAPING
.PHONY: scrape
scrape:  # 🌐 Ejecuta el scraper
	source venv/bin/activate && python scraper.py

###############################################################################$
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
	bash keepers/backup_db.sh

.PHONY: db-purge
db-purge:  # 💀 Elimina la base de datos y el entorno virtual
	@echo "⚠️  Eliminando la base de datos y el entorno virtual..."
	rm -rf *.db venv
	@echo "✅ Base de datos y entorno virtual eliminados."
###############################################################################$

# ✅ 6️⃣ PRUEBAS Y DESPLIEGUE
.PHONY: test
test:  # 🧪 Ejecuta los tests
	@echo "✅ Ejecutando tests..."
	source venv/bin/activate && pytest tests/

.PHONY: deploy
deploy:  # 🚀 Despliega la aplicación
	@echo "🌍 Desplegando aplicación..."
	bash scripts/deploy.sh

.PHONY: check
check:  # ✅ Verifica el estado del entorno
	bash checkers/environment_check.sh

.PHONY: show-rule
show-rule: # 📙 Muestra la regla que le indiques en RULE=
	@if [ -z "$(RULE)" ]; then \
		echo "❌ Debes especificar una regla con RULE=<nombre>"; \
	elif ! grep -qE "^$(RULE):" $(MAKEFILE_LIST); then \
		echo "❌ La regla '$(RULE)' no existe."; \
	else \
		echo "🔍 Mostrando la regla '$(RULE)'\n"; \
		if command -v bat >/dev/null 2>&1; then \
			grep -A 10 -E "^$(RULE):" $(MAKEFILE_LIST) | bat --style=plain --language=makefile; \
		elif command -v batcat >/dev/null 2>&1; then \
			grep -A 10 -E "^$(RULE):" $(MAKEFILE_LIST) | batcat --style=plain --language=makefile; \
		else \
			grep -A 10 -E "^$(RULE):" $(MAKEFILE_LIST) | cat; \
		fi; \
	fi

