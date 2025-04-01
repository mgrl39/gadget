import yaml
import mysql.connector

# Cargar configuración desde el YAML
with open("config/config.yaml", "r") as file:
    config = yaml.safe_load(file)

db_config = config["database"]

# Conectar con MySQL
conn = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"]
)
cursor = conn.cursor()

# Leer y ejecutar el esquema de la base de datos
with open("config/schema.sql", "r") as file:
    schema_sql = file.read()

for statement in schema_sql.split(";"):
    if statement.strip():
        cursor.execute(statement)

conn.commit()
cursor.close()
conn.close()

print("✅ Base de datos configurada correctamente.")

