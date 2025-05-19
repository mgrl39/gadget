"""
Cargador de configuración para el proyecto Gadget
"""

import os
import yaml
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ConfigLoader")

def load_config(only_env=False):
    """
    Carga la configuración del proyecto desde config.yaml y/o variables de entorno
    
    Args:
        only_env (bool): Si es True, solo carga desde variables de entorno
        
    Returns:
        dict: Configuración cargada
    """
    config = {}
    
    # Cargar desde archivo YAML si no se especifica only_env
    if not only_env:
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Configuración cargada desde {config_path}")
            else:
                logger.warning(f"Archivo de configuración no encontrado: {config_path}")
        except Exception as e:
            logger.error(f"Error al cargar configuración desde {config_path}: {e}")
    
    # Cargar o sobrescribir con variables de entorno
    # Base de datos
    db_config = config.get("database", {})
    db_config["host"] = os.environ.get("DB_HOST", db_config.get("host", "localhost"))
    db_config["port"] = int(os.environ.get("DB_PORT", db_config.get("port", 5432)))
    db_config["user"] = os.environ.get("DB_USER", db_config.get("user", "postgres"))
    db_config["password"] = os.environ.get("DB_PASSWORD", db_config.get("password", "postgres"))
    db_config["name"] = os.environ.get("DB_NAME", db_config.get("name", "cinedb"))
    config["database"] = db_config
    
    # Scraper
    scraper_config = config.get("scraper", {})
    scraper_config["user_agent"] = os.environ.get("SCRAPER_USER_AGENT", scraper_config.get("user_agent", "Mozilla/5.0"))
    scraper_config["headless"] = os.environ.get("SCRAPER_HEADLESS", scraper_config.get("headless", "true")).lower() == "true"
    scraper_config["max_retries"] = int(os.environ.get("SCRAPER_MAX_RETRIES", scraper_config.get("max_retries", 3)))
    scraper_config["timeout"] = int(os.environ.get("SCRAPER_TIMEOUT", scraper_config.get("timeout", 10)))
    config["scraper"] = scraper_config
    
    return config 