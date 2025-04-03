import time
import random
import os
import json
import yaml
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class CinesaScraper:
    def __init__(self):
        # Cargar configuración
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Configurar opciones de Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ejecutar en modo sin interfaz gráfica
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        
        # Establecer un User-Agent convincente
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Inicializar navegador
        print("Inicializando navegador Chrome...")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def __del__(self):
        # Cerrar el navegador al finalizar
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("Navegador cerrado")
    
    def obtener_peliculas(self):
        """Obtiene la lista de películas usando Selenium"""
        url = "https://www.cinesa.es/peliculas/"
        peliculas = []
        
        try:
            print(f"Navegando a: {url}")
            self.driver.get(url)
            
            # Esperar a que cargue la página
            time.sleep(5)  # Dar tiempo para que cargue completamente
            
            # Esperar a que aparezcan los elementos de película
            print("Esperando a que carguen las películas...")
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.v-film-list-film")))
            
            # Guardar HTML para depuración
            with open('debug_cinesa_selenium.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("HTML guardado para depuración")
            
            # Extraer la lista de películas
            pelicula_items = self.driver.find_elements(By.CSS_SELECTOR, "li.v-film-list-film")
            print(f"Se encontraron {len(pelicula_items)} elementos de películas")
            
            for i, peli in enumerate(pelicula_items):
                try:
                    # Extraer datos de la película
                    try:
                        titulo = peli.find_element(By.CSS_SELECTOR, "span.v-film-title__text").text
                    except NoSuchElementException:
                        titulo = "Desconocido"
                    
                    # Verificar si es próximo estreno
                    try:
                        es_proximo = peli.find_element(By.CSS_SELECTOR, "div.v-film-promoted-tag--type-coming-soon").is_displayed()
                        estado = "Próximos" if es_proximo else "En cartelera"
                    except NoSuchElementException:
                        estado = "En cartelera"
                    
                    # Obtener URL
                    try:
                        link = peli.find_element(By.CSS_SELECTOR, "a.v-film-list-film__link")
                        url_pelicula = link.get_attribute("href")
                    except NoSuchElementException:
                        url_pelicula = ""
                    
                    # Obtener URL del póster
                    try:
                        img = peli.find_element(By.CSS_SELECTOR, "div.v-film-image__img img")
                        poster_url = img.get_attribute("src")
                    except NoSuchElementException:
                        poster_url = ""
                    
                    # Obtener clasificación de edad
                    try:
                        rating_img = peli.find_element(By.CSS_SELECTOR, "span.v-censor-rating-icon img")
                        clasificacion = rating_img.get_attribute("alt")
                    except NoSuchElementException:
                        clasificacion = "Desconocida"
                    
                    # Crear objeto película
                    pelicula = {
                        "titulo": titulo,
                        "estado": estado,
                        "url": url_pelicula,
                        "poster_url": poster_url,
                        "clasificacion": clasificacion
                    }
                    
                    peliculas.append(pelicula)
                    print(f"Procesada película: {titulo}")
                    
                except Exception as e:
                    print(f"Error procesando película {i+1}: {e}")
            
            return peliculas
            
        except Exception as e:
            print(f"Error al obtener películas: {e}")
            return []
        
    def obtener_detalles_pelicula(self, url):
        """Obtiene detalles de una película específica"""
        try:
            print(f"Navegando a: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))  # Esperar que cargue la página
            
            # Extraer detalles
            detalles = {}
            
            # Sinopsis
            try:
                sinopsis_elem = self.driver.find_element(By.CSS_SELECTOR, "div.v-film-detail-synopsis__content")
                detalles['sinopsis'] = sinopsis_elem.text.strip()
            except NoSuchElementException:
                print("No se encontró la sinopsis")
            
            # Aquí podrías extraer más detalles como director, reparto, duración, etc.
            
            return detalles
            
        except Exception as e:
            print(f"Error al obtener detalles de {url}: {e}")
            return {}
    
    def guardar_datos(self, peliculas, ruta_personalizada=None):
        """Guarda los datos de películas en un archivo JSON"""
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if ruta_personalizada:
            ruta_archivo = ruta_personalizada
        else:
            directorio_datos = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            os.makedirs(directorio_datos, exist_ok=True)
            ruta_archivo = os.path.join(directorio_datos, f"cinesa_peliculas_{fecha_actual}.json")
        
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(peliculas, f, ensure_ascii=False, indent=4)
            print(f"Datos guardados en {ruta_archivo}")
            return True
        except Exception as e:
            print(f"Error al guardar datos: {e}")
            return False

# Función principal para ejecutar el scraper
def main():
    parser = argparse.ArgumentParser(description='Scraper de películas de Cinesa')
    parser.add_argument('--guardar', '-g', type=str, help='Ruta donde guardar el archivo JSON resultante')
    parser.add_argument('--solo-lista', '-l', action='store_true', help='Solo obtener lista de películas sin detalles')
    args = parser.parse_args()
    
    scraper = CinesaScraper()
    print("Obteniendo lista de películas...")
    peliculas = scraper.obtener_peliculas()
    print(f"Se encontraron {len(peliculas)} películas")
    
    # Si no se solicita solo la lista, obtener detalles
    if not args.solo_lista and peliculas:
        print("Obteniendo detalles de películas...")
        for i, pelicula in enumerate(peliculas):
            print(f"Procesando película {i+1}/{len(peliculas)}: {pelicula['titulo']}")
            detalles = scraper.obtener_detalles_pelicula(pelicula['url'])
            peliculas[i].update(detalles)
    
    # Guardar los datos
    scraper.guardar_datos(peliculas, args.guardar)

if __name__ == "__main__":
    main()