import time
import sys
import requests
from bs4 import BeautifulSoup
import json
import os
import yaml
import re
import signal
from colorama import init, Fore, Back, Style
from utils.config_loader import load_config
import logging

# Configurar logging
def setup_logging():
    config = load_config()
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_file = log_config.get("log_file", "logs/gadget.log")
    
    # Crear directorio de logs si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Inicializar logger
logger = setup_logging()

def initializer():
    """Inicializa la configuración y dependencias del proyecto"""
    logger.info("Inicializando la aplicación")
    config = load_config()
    return config

def signal_handler(signum, frame):
    """Maneja señales de interrupción"""
    logger.warning("Recibida señal de interrupción. Deteniendo...")
    sys.exit(0)

# Registrar manejador de señales
signal.signal(signal.SIGINT, signal_handler)

# Initialize colorama
init(autoreset=True)

# Enhanced color class
class Colors:
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    YELLOW = Fore.YELLOW
    GREEN = Fore.GREEN
    RED = Fore.RED
    BLUE = Fore.BLUE
    WHITE = Fore.WHITE
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL
    BG_BLACK = Back.BLACK

def print_logo():
    """Muestra el logo de la aplicación"""
    logo = """
                                    ████   ████████   ████████
                                   ░░███  ███░░░░███ ███░░░░███
 █████████████    ███████ ████████  ░███ ░░░    ░███░███   ░███
░░███░░███░░███  ███░░███░░███░░███ ░███    ██████░ ░░█████████
 ░███ ░███ ░███ ░███ ░███ ░███ ░░░  ░███   ░░░░░░███ ░░░░░░░███
 ░███ ░███ ░███ ░███ ░███ ░███      ░███  ███   ░███ ███   ░███
 █████░███ █████░░███████ █████     █████░░████████ ░░████████
░░░░░ ░░░ ░░░░░  ░░░░░███░░░░░     ░░░░░  ░░░░░░░░   ░░░░░░░░
                 ███ ░███
                ░░██████
                 ░░░░░░
"""
    print(f"{Colors.MAGENTA}{Colors.BOLD}{logo}{Colors.RESET}")

def display_progress_bar(current, total=100, bar_length=30, description="Procesando"):
    """
    Muestra una barra de progreso en la consola.

    Parámetros:
    current (int): Valor actual del progreso
    total (int): El número total que se quiere alcanzar.
    bar_length (int): La longitud de la barra de progreso.
    description (str): Descripción de la tarea en progreso
    """
    percent = 100.0 * current / total
    filled_length = int(percent / (100.0 / bar_length))
    bar = '=' * filled_length + ' ' * (bar_length - filled_length)
    
    sys.stdout.write(f'\r{description}: [{bar}] {percent:.1f}%')
    sys.stdout.flush()
    
    # Salto de línea cuando se completa
    if current == total:
        print()

def main():
    """Función principal del programa"""
    print_logo()
    config = initializer()
    
    # Obtener configuración del scraper
    scraper_config = config.get("scraper", {})
    website = config.get("scrape_website", "")
    
    logger.info(f"Iniciando scraping de: {website}")
    
    # Simulación de scraping para demostración
    total_items = 100
    for i in range(total_items + 1):
        display_progress_bar(i, total_items, description="Extrayendo datos")
        time.sleep(0.02)  # Simular trabajo
    
    print(f"{Colors.GREEN}✅ Scraping completado con éxito!{Colors.RESET}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
