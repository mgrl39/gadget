import os
from dotenv import load_dotenv

def load_config(only_env=False):
    """
    Carga la configuración desde .env y opcionalmente config.yaml
    
    Args:
        only_env (bool): Si es True, solo carga variables desde .env
                         Si es False, también carga desde config.yaml
    
    Returns:
        dict: Configuración completa
    """
    # Cargar variables de entorno
    load_dotenv()
    
    # Configuración base
    config = {
        "database": {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": int(os.environ.get("DB_PORT", "3306")),
            "user": os.environ.get("DB_USER", "root"),
            "password": os.environ.get("DB_PASSWORD", ""),
            "name": os.environ.get("DB_NAME", "cinedb")
        },
        "logging": {
            "level": os.environ.get("LOG_LEVEL", "INFO"),
            "log_file": "logs/gadget.log"
        },
        "api": {
            "key": os.environ.get("API_KEY", ""),
            "url": os.environ.get("API_URL", "")
        }
    }
    
    # Si se permite usar config.yaml, intentar cargarlo
    if not only_env:
        try:
            import yaml
            with open("config/config.yaml", "r") as f:
                yaml_config = yaml.safe_load(f)
                
            # Combinar, dando prioridad a variables de entorno
            if yaml_config:
                # Solo usar valores de yaml que no estén en variables de entorno
                if "database" in yaml_config:
                    for key, value in yaml_config["database"].items():
                        env_var = f"DB_{key.upper()}"
                        if env_var not in os.environ:
                            config["database"][key] = value
                
                # Copiar otras secciones que no sean database
                for section, values in yaml_config.items():
                    if section != "database":
                        if section not in config:
                            config[section] = {}
                        config[section].update(values)
        except Exception as e:
            print(f"⚠️ Error al cargar config.yaml: {e}. Usando solo variables de entorno.")
    
    return config 