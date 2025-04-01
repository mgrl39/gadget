# 🔧 CONFIGURACIÓN Y LIMPIEZA
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

.PHONY: venv
venv:  # 🔧 Configura entorno virtual
	@echo "🔧 Configurando entorno virtual..."
	@bash installers/virtual_env.sh

.PHONY: install
install: venv  # 📦 Instala todas las dependencias
	@echo "📦 Instalando dependencias..."
	@bash -c "source venv/bin/activate && pip install -r requirements.txt"
	@echo "✅ Dependencias instaladas correctamente."

.PHONY: tutorial
tutorial:  # 📚 Muestra guía paso a paso y verifica estado de instalación
	@bash scripts/setup_checker.sh

.PHONY: check
check:  # ✅ Verifica el estado del entorno
	@bash checkers/environment_check.sh 