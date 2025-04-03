# 🛠️ DESARROLLO Y PRUEBAS
.PHONY: scrape
scrape:  # 🌐 Ejecuta el scraper
	@bash -c "source venv/bin/activate && python scraper.py"

.PHONY: run
run: setup-db  # 🚀 Ejecuta el programa principal
	@echo "🚀 Iniciando Gadget..."
	@bash -c "source venv/bin/activate && python run.py"

.PHONY: test
test: install  # 🧪 Ejecuta los tests
	@echo "✅ Ejecutando tests..."
	@bash -c "source venv/bin/activate && pytest tests/"

.PHONY: panel
panel:  # 🖥️ Inicia el panel web de control
	@echo "🌐 Preparando panel web..."
	@bash -c "source venv/bin/activate && pip install flask && python panels/gadget_panel.py" 