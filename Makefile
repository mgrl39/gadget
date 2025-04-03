# Makefile principal para el proyecto Gadget
# mgrl39
.DEFAULT_GOAL := help
# Incluir módulos específicos
include makefiles/setup.mk
include makefiles/database.mk
include makefiles/development.mk
include makefiles/deploy.mk

.PHONY: help
help:  # 📖 Muestra los comandos disponibles
	@echo "\033[1;34m🔹 Comandos disponibles:\033[0m"
	@for file in $(MAKEFILE_LIST); do \
		grep -E '^[a-zA-Z0-9_-]+:.*?#' $$file | sort | \
		awk '{gsub(/:.*/,"",$$1); printf "  \033[1;36m%-20s\033[0m %s\n", $$1, substr($$0, index($$0,"#")+1)}'; \
	done | sort

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

.PHONY: panel
panel: venv install  # 🖥️ Inicia el panel web de control
	@echo "🌐 Iniciando panel web en http://localhost:5000..."
	@bash -c "source venv/bin/activate && pip install flask && python panels/gadget_panel.py"

