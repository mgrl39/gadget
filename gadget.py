#!/usr/bin/env python3
"""
Gadget - Herramienta de scraping de Cinesa con gestión de base de datos
Todo en Python para máxima simplicidad y mantenibilidad.
"""

import argparse
import os
import sys
import subprocess
import shutil
import datetime
import gzip
import psycopg2
from pathlib import Path
import importlib.util

# Importar el cargador de configuración desde utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.config_loader import load_config

class GadgetCLI:
    """CLI principal para gestionar el scraper y la base de datos"""
    
    def __init__(self):
        self.config = load_config()
        self.db_config = self.config.get("database", {})
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def setup_venv(self):
        """Configura el entorno virtual e instala dependencias"""
        print("🚀 Configurando entorno virtual...")
        
        venv_path = Path("venv")
        if not venv_path.exists():
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Entorno virtual creado")
        else:
            print("✅ El entorno virtual ya existe")
        
        # Determinar la ruta al pip del entorno virtual
        if sys.platform == "win32":
            pip_path = "venv\\Scripts\\pip"
        else:
            pip_path = "venv/bin/pip"
        
        # Instalar dependencias
        print("📦 Instalando dependencias...")
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencias instaladas correctamente")
        
        return True
    
    def setup_db(self):
        """Configura la base de datos PostgreSQL"""
        print("🗄️ Configurando base de datos PostgreSQL...")
        
        try:
            # Conectar a PostgreSQL
            conn = psycopg2.connect(
                host=self.db_config.get("host", "localhost"),
                port=self.db_config.get("port", 5432),
                user=self.db_config.get("user", "postgres"),
                password=self.db_config.get("password", "postgres"),
                # Conectar a 'postgres' por defecto para crear nuestra base de datos
                database="postgres"
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Crear la base de datos si no existe
            db_name = self.db_config.get("name", "cinedb")
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"✅ Base de datos '{db_name}' creada")
            else:
                print(f"✅ Base de datos '{db_name}' ya existe")
            
            # Cerrar conexión a 'postgres'
            cursor.close()
            conn.close()
            
            # Reconectar a nuestra base de datos
            conn = psycopg2.connect(
                host=self.db_config.get("host", "localhost"),
                port=self.db_config.get("port", 5432),
                user=self.db_config.get("user", "postgres"),
                password=self.db_config.get("password", "postgres"),
                database=db_name
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Aplicar esquema si existe
            schema_path = Path("config/schema.sql")
            if schema_path.exists():
                print("📊 Aplicando esquema de base de datos...")
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                cursor.execute(schema_sql)
                print("✅ Esquema aplicado correctamente")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando la base de datos: {e}")
            return False
    
    def backup_db(self):
        """Realiza backup de la base de datos PostgreSQL"""
        print("💾 Creando backup de la base de datos...")
        
        try:
            # Configuración de la base de datos
            db_host = self.db_config.get("host", "localhost")
            db_port = self.db_config.get("port", 5432)
            db_user = self.db_config.get("user", "postgres")
            db_password = self.db_config.get("password", "postgres")
            db_name = self.db_config.get("name", "cinedb")
            
            # Nombre del archivo de backup
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"backup_{db_name}_{timestamp}.sql"
            
            # Configurar entorno para pg_dump
            env = os.environ.copy()
            env["PGPASSWORD"] = db_password
            
            # Ejecutar pg_dump
            result = subprocess.run(
                [
                    "pg_dump",
                    "-h", str(db_host),
                    "-p", str(db_port),
                    "-U", db_user,
                    "-d", db_name,
                    "-f", str(backup_file)
                ],
                env=env,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Comprimir el backup
            with open(backup_file, 'rb') as f_in:
                with gzip.open(f"{backup_file}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Eliminar el archivo sin comprimir
            backup_file.unlink()
            
            print(f"✅ Backup guardado en: {backup_file}.gz")
            return True
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False
    
    def purge_db(self):
        """Purga la base de datos PostgreSQL"""
        print("🔥 Purgando la base de datos...")
        
        try:
            # Configuración de la base de datos
            db_host = self.db_config.get("host", "localhost")
            db_port = self.db_config.get("port", 5432)
            db_user = self.db_config.get("user", "postgres")
            db_password = self.db_config.get("password", "postgres")
            db_name = self.db_config.get("name", "cinedb")
            
            # Conectar a PostgreSQL (base de datos postgres)
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database="postgres"
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Eliminar conexiones activas
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid()
            """)
            
            # Eliminar la base de datos
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            print(f"💀 Base de datos '{db_name}' eliminada")
            
            # Recrear la base de datos
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Base de datos '{db_name}' recreada")
            
            cursor.close()
            conn.close()
            
            # Aplicar esquema si existe
            schema_path = Path("config/schema.sql")
            if schema_path.exists():
                conn = psycopg2.connect(
                    host=db_host,
                    port=db_port,
                    user=db_user,
                    password=db_password,
                    database=db_name
                )
                conn.autocommit = True
                cursor = conn.cursor()
                
                print("📊 Aplicando esquema de base de datos...")
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                cursor.execute(schema_sql)
                
                cursor.close()
                conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error purgando la base de datos: {e}")
            return False
    
    def clean(self):
        """Limpia archivos temporales y caché"""
        print("🧹 Limpiando archivos temporales...")
        
        # Eliminar directorios de caché
        for path in Path(".").rglob("__pycache__"):
            if path.is_dir():
                shutil.rmtree(path)
        
        # Eliminar archivos temporales
        for ext in ["*.pyc", "*.pyo", "*.log"]:
            for path in Path(".").rglob(ext):
                path.unlink()
        
        print("✅ Limpieza completada")
        return True
    
    def run_scraper(self, args):
        """Ejecuta el scraper con los argumentos proporcionados"""
        print("🕸️ Ejecutando scraper de Cinesa...")
        
        # Importar el scraper dinámicamente
        scraper_path = Path("scrapers/cinesa_detalles_scraper.py")
        if not scraper_path.exists():
            print(f"❌ Scraper no encontrado en {scraper_path}")
            return False
        
        try:
            # Construir comando para ejecutar el scraper
            cmd = [sys.executable, str(scraper_path)]
            
            if args.solo_lista:
                cmd.append("--solo-lista")
            if args.max:
                cmd.extend(["--max", str(args.max)])
            if args.hilos:
                cmd.extend(["--hilos", str(args.hilos)])
            if args.demora:
                cmd.extend(["--demora", str(args.demora)])
            if args.pelicula:
                cmd.extend(["--pelicula", args.pelicula])
            
            # Ejecutar el scraper
            subprocess.run(cmd, check=True)
            print("✅ Scraper ejecutado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error ejecutando scraper: {e}")
            return False

def main():
    """Función principal que maneja la interfaz de línea de comandos"""
    parser = argparse.ArgumentParser(description="Gadget - Herramienta de scraping de Cinesa")
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")
    
    # Comando: setup
    setup_parser = subparsers.add_parser("setup", help="Configurar entorno y base de datos")
    
    # Comando: scrape
    scrape_parser = subparsers.add_parser("scrape", help="Ejecutar scraper")
    scrape_parser.add_argument("--solo-lista", "-l", action="store_true", help="Obtener solo lista de películas")
    scrape_parser.add_argument("--max", "-m", type=int, help="Número máximo de películas")
    scrape_parser.add_argument("--hilos", "-t", type=int, help="Número de hilos para procesamiento")
    scrape_parser.add_argument("--demora", "-d", type=int, help="Demora entre peticiones en segundos")
    scrape_parser.add_argument("--pelicula", "-p", type=str, help="URL o ID de una película específica")
    
    # Comando: backup
    backup_parser = subparsers.add_parser("backup", help="Crear backup de la base de datos")
    
    # Comando: purge
    purge_parser = subparsers.add_parser("purge", help="Purgar la base de datos")
    
    # Comando: clean
    clean_parser = subparsers.add_parser("clean", help="Limpiar archivos temporales")
    
    args = parser.parse_args()
    
    # Crear instancia de la CLI
    cli = GadgetCLI()
    
    # Ejecutar el comando seleccionado
    if args.command == "setup":
        success = cli.setup_venv() and cli.setup_db()
    elif args.command == "scrape":
        success = cli.run_scraper(args)
    elif args.command == "backup":
        success = cli.backup_db()
    elif args.command == "purge":
        success = cli.purge_db()
    elif args.command == "clean":
        success = cli.clean()
    else:
        parser.print_help()
        return 0
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 