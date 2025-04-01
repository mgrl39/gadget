import os
import sys
import subprocess

# Añadir el directorio raíz del proyecto a sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora podemos importar módulos desde la raíz del proyecto
from utils.config_loader import load_config

def purge_database():
    # Cargar configuración (solo desde .env para seguridad)
    config = load_config(only_env=True)
    db_config = config["database"]
    
    db_host = db_config["host"]
    db_user = db_config["user"]
    db_password = db_config["password"]
    db_name = db_config["name"]

    print(f"🔴 Intentando eliminar la base de datos: {db_name} en {db_host}")

    # Usar directamente el cliente MySQL
    mysql_cmd = f"mysql -h {db_host} -u {db_user}"
    
    if db_password:
        mysql_cmd += f" -p{db_password}"
    
    drop_cmd = f"DROP DATABASE IF EXISTS {db_name};"
    
    # Ejecutar comando
    try:
        result = subprocess.run(
            f"{mysql_cmd} -e '{drop_cmd}'",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"💀 Base de datos '{db_name}' eliminada correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error al eliminar la base de datos: {e}")
        print(f"Mensaje: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}")
        return False

if __name__ == "__main__":
    purge_database() 