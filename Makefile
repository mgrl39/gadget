# Gadget's Makefile
# mgrl39
.DEFAULT_GOAL := help
# Incluir módulos específicos
include makefiles/setup.mk
include makefiles/database.mk
include makefiles/development.mk
include makefiles/deploy.mk

.PHONY: help
help:  # 📚 Muestra esta ayuda
	@echo "🚀 SCRAPER CINESA"
	@echo ""
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Comando para mostrar reglas específicas
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

.PHONY: check
check:  # 🔍 Verifica el estado de la configuración
	@echo "Verificando estado de la configuración..."
	@bash checkers/setup_checker.sh

.PHONY: purge-db
purge-db:  # 🗑️ Elimina la base de datos
	@echo "Eliminando base de datos..."
	@python3 purgers/purge_db.py

.PHONY: scrape-cinesa
scrape-cinesa: venv install  # 🎬 Ejecuta el scraper de películas de Cinesa
	@echo "🎬 Ejecutando scraper de Cinesa..."
	@bash -c "source venv/bin/activate && python scrapers/cinesa_scraper.py"

# 🚀 SCRAPER CINESA

.PHONY: install
install:  # 🔧 Instala el entorno virtual y dependencias
	@echo "🚀 Instalando entorno virtual y dependencias..."
	@bash installers/virtual_env.sh

.PHONY: clean
clean:  # 🧹 Limpia archivos temporales y elimina el entorno virtual
	@echo "🔥 Eliminando archivos temporales y el entorno virtual..."
	rm -rf build venv __pycache__ *.log
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "✅ Limpieza completada."

.PHONY: scrape
scrape:  # 🕸️ Ejecuta el scraper de Cinesa
	@echo "🕸️ Ejecutando scraper de Cinesa..."
	@bash -c "source venv/bin/activate && python scrapers/cinesa_detalles_scraper.py"

.PHONY: scrape-list
scrape-list:  # 📋 Obtiene solo la lista de películas sin detalles
	@echo "📋 Obteniendo lista de películas..."
	@bash -c "source venv/bin/activate && python scrapers/cinesa_detalles_scraper.py --solo-lista"

