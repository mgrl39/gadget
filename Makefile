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
venv:  # 🔧 Configura entorno virtual
	@echo "🔧 Configurando entorno virtual..."
	@bash installers/virtual_env.sh

.PHONY: install
install: venv  # 📦 Instala todas las dependencias
	@echo "📦 Instalando dependencias..."
	@bash -c "source venv/bin/activate && pip install -r requirements.txt"
	@echo "✅ Dependencias instaladas correctamente."

# 🌍 3️⃣ WEB SCRAPING
.PHONY: scrape
scrape:  # 🌐 Ejecuta el scraper
	source venv/bin/activate && python scraper.py

###############################################################################$
# 🗄️ 4️⃣ BASE DE DATOS
.PHONY: setup-db
setup-db: install  # 🗄️ Configura la base de datos (requiere entorno virtual e instalación)
	@echo "🗄️ Configurando base de datos..."
	@bash -c "source venv/bin/activate && python installers/setup_db.py"
	@echo "✅ Base de datos configurada correctamente."

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
	@echo "⚠️ Eliminando la base de datos y el entorno virtual..."
	@if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then \
		bash -c "source venv/bin/activate && python scripts/purge_db.py"; \
	else \
		python3 scripts/purge_db.py; \
	fi
	@echo "🧹 Eliminando entorno virtual..."
	@rm -rf venv
	@echo "✅ Base de datos y entorno virtual eliminados."

# ✅ 0️⃣ TUTORIAL Y ASISTENTE DE CONFIGURACIÓN
.PHONY: tutorial
tutorial:  # 📚 Muestra guía paso a paso y verifica estado de instalación
	@bash scripts/setup_checker.sh

.PHONY: run
run: setup-db  # 🚀 Ejecuta el programa principal (requiere todos los pasos anteriores)
	@echo "🚀 Iniciando Gadget..."
	@bash -c "source venv/bin/activate && python run.py"

# ✅ 6️⃣ PRUEBAS Y DESPLIEGUE
.PHONY: test
test: install  # 🧪 Ejecuta los tests (requiere entorno virtual e instalación)
	@echo "✅ Ejecutando tests..."
	@bash -c "source venv/bin/activate && pytest tests/"

.PHONY: deploy
deploy: setup-db  # 🚀 Despliega la aplicación (requiere configuración completa)
	@echo "🌍 Desplegando aplicación..."
	@bash scripts/deploy.sh

.PHONY: check
check:  # ✅ Verifica el estado del entorno
	@bash checkers/environment_check.sh

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

