import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener configuración de base de datos desde variables de entorno
db_host = os.environ.get("DB_HOST", "localhost")
db_port = int(os.environ.get("DB_PORT", "3306"))
db_user = os.environ.get("DB_USER", "root")
db_password = os.environ.get("DB_PASSWORD", "")
db_name = os.environ.get("DB_NAME", "cinedb")

print(f"📊 Conectando a MySQL en {db_host}:{db_port}")

# Conectar con MySQL
try:
    conn = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password
    )
    cursor = conn.cursor()

    # Crear base de datos si no existe
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"✅ Base de datos '{db_name}' creada correctamente")

    # Seleccionar la base de datos
    cursor.execute(f"USE {db_name}")

    # Leer y ejecutar el esquema de la base de datos
    try:
        with open("config/schema.sql", "r") as file:
            schema_sql = file.read()

        # Dividir por punto y coma y ejecutar cada sentencia
        for statement in schema_sql.split(";"):
            if statement.strip():
                cursor.execute(statement)
                
        print("✅ Esquema de la base de datos aplicado correctamente")
    except FileNotFoundError:
        print("⚠️ Archivo schema.sql no encontrado. Solo se ha creado la base de datos sin tablas.")

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Base de datos configurada correctamente.")
    
except mysql.connector.Error as err:
    print(f"❌ Error de MySQL: {err}")
    print("⚠️ Verifica que el servidor MySQL esté en ejecución y las credenciales sean correctas.")
    exit(1)

