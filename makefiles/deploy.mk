# 🚀 DESPLIEGUE
.PHONY: deploy
deploy: setup-db  # 🚀 Despliega la aplicación
	@echo "🌍 Desplegando aplicación..."
	@bash scripts/deploy.sh 