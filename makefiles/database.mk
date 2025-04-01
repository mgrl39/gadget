# 🗄️ GESTIÓN DE BASE DE DATOS
.PHONY: setup-db
setup-db: install  # 🗄️ Configura la base de datos
	@echo "🗄️ Configurando base de datos..."
	@bash -c "source venv/bin/activate && python installers/setup_db.py"
	@echo "✅ Base de datos configurada correctamente."

.PHONY: db-reset
db-reset:  # 🔄 Reinicia la base de datos
	@echo "🔥 Eliminando y recreando base de datos..."
	@bash -c "source venv/bin/activate && python db/reset.py"

.PHONY: db-backup
db-backup:  # 💾 Realiza un backup de la base de datos
	@echo "📂 Creando backup..."
	@bash keepers/backup_db.sh

.PHONY: db-purge
db-purge:  # 💀 Elimina la base de datos y el entorno virtual
	@echo "⚠️ Eliminando la base de datos y el entorno virtual..."
	@if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then \
		bash -c "source venv/bin/activate && python purgers/purge_db.py"; \
	else \
		python3 purgers/purge_db.py; \
	fi
	@echo "🧹 Eliminando entorno virtual..."
	@rm -rf venv
	@echo "✅ Base de datos y entorno virtual eliminados." 