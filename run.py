import time
import sys
import requests
from bs4 import BeautifulSoup
import json
import os
import re
import signal
from colorama import init, Fore, Back, Style

def signal_handler(signum, frame):
    print(f"\n{Colors.YELLOW}Received interrupt signal. Stopping...{Colors.RESET}")
    exit()

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

def display_progress_bar(total=1007, bar_length=30):
    """
    Muestra una barra de progreso en la consola.

    Parámetros:
    total (int): El número total que se quiere alcanzar.
    bar_length (int): La longitud de la barra de progreso.
    """
    for i in range(total + 1):
        percent = 100.0 * i / total
        sys.stdout.write('\r')
        sys.stdout.write("Completed: [{:{}}] {:>3}%"
                         .format('=' * int(percent / (100.0 / bar_length)),
                                 bar_length, int(percent)))
        sys.stdout.flush()
        time.sleep(0.002)

# Llamar a la función para mostrar la barra de progreso
print_logo();
#display_progress_bar()
