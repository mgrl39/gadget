import os
import argparse
import mysql.connector
from mysql.connector import Error
import re
import yaml

def get_db_config():
    with open("config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config["database"]

def connect_to_database():
    db_config = get_db_config()
    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["name"]
        )
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def insert_data(table, data):
    connection = connect_to_database()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, list(data.values()))
        connection.commit()
        print(f"✅ Datos insertados correctamente en {table}")
        return True
    except Error as e:
        print(f"❌ Error al insertar datos: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def main():
    parser = argparse.ArgumentParser(description='Inserta datos en la base de datos')
    parser.add_argument('--table', required=True, help='Tabla donde insertar los datos')
    parser.add_argument('--data', required=True, help='Datos en formato clave1=valor1,clave2=valor2')
    
    args = parser.parse_args()
    
    # Parsear los datos
    data_dict = {}
    for pair in args.data.split(','):
        key, value = pair.split('=')
        data_dict[key.strip()] = value.strip()
    
    # Insertar en la base de datos
    insert_data(args.table, data_dict)

if __name__ == "__main__":
    main()
