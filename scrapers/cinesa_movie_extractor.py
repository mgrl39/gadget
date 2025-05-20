"""
Extractor específico para detalles de películas de Cinesa
"""

import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image
from io import BytesIO
from datetime import datetime
import time
import random

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CinesaExtractor")

class CinesaMovieExtractor:
    """Clase para extraer información detallada de películas de Cinesa"""
    
    def __init__(self, driver=None, base_url="https://www.cinesa.es", data_dir="data"):
        """
        Inicializar el extractor
        
        Args:
            driver: WebDriver de Selenium (opcional)
            base_url: URL base de Cinesa
            data_dir: Directorio para guardar datos
        """
        self.driver = driver
        self.base_url = base_url
        
        # Directorios para guardar datos
        self.data_dir = data_dir
        self.movies_dir = os.path.join(data_dir, "peliculas")
        self.images_dir = os.path.join(data_dir, "imagenes")
        
        # Crear directorios si no existen
        os.makedirs(self.movies_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Headers para requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        }
    
    def extract_movie_details(self, url):
        """
        Extrae detalles completos de una película desde su URL
        
        Args:
            url: URL de la película en Cinesa
            
        Returns:
            dict: Detalles de la película
        """
        logger.info(f"Extrayendo detalles de: {url}")
        
        try:
            # Verificar si tenemos un driver de Selenium
            if self.driver is None:
                logger.error("No se proporcionó un WebDriver. No se pueden extraer detalles.")
                return None
            
            # Navegar a la URL
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))  # Esperar carga
            
            # Manejar cookies si aparecen
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                cookie_button.click()
                time.sleep(1)
            except (TimeoutException, NoSuchElementException):
                logger.info("No se encontró el botón de cookies o ya estaban aceptadas")
            
            # Extraer título
            titulo = self._extract_element_text(
                [".v-film-title__text", "h1.film-title", ".movie-title h1"]
            )
            
            # Extraer imagen/póster
            poster_url = self._extract_image_url(
                [".v-film-image__img img", ".film-poster img", ".movie-poster img"]
            )
            
            # Descargar y guardar la imagen
            poster_path = None
            if poster_url:
                poster_path = self._download_image(poster_url, titulo)
            
            # Extraer duración
            duracion = self._extract_element_text(
                [".v-film-runtime .v-display-text-part", ".film-runtime", ".duration"]
            )
            
            # Extraer fecha de estreno
            fecha_estreno = self._extract_element_text(
                [".v-film-release-date .v-display-text-part", ".release-date", ".film-release-date"]
            )
            
            # Extraer géneros
            generos = self._extract_multiple_elements_text(
                [".v-film-genres__list .v-description-list-item__description", ".film-genres span", ".genres"]
            )
            
            # Extraer clasificación
            clasificacion = self._extract_element_text(
                [".v-film-classification-description .v-description-list-item__description", ".film-classification", ".rating"]
            )
            
            # Extraer directores
            directores = self._extract_element_text(
                [".v-film-directors .v-display-text-part", ".film-directors", ".directors"]
            )
            
            # Extraer actores
            actores_text = self._extract_element_text(
                [".v-film-actors .v-display-text-part", ".film-actors", ".actors"]
            )
            actores = [actor.strip() for actor in actores_text.split(",")] if actores_text else []
            
            # Extraer sinopsis
            sinopsis = self._extract_element_text(
                [".v-film-synopsis .v-display-text-part", ".film-synopsis", ".synopsis"]
            )
            
            # Extraer ID de la película
            movie_id = None
            url_parts = url.rstrip('/').split('/')
            if url_parts and len(url_parts) >= 2:
                movie_id = url_parts[-1]
            
            # Construir el objeto de película
            movie_data = {
                "id": movie_id,
                "titulo": titulo,
                "url": url,
                "poster_url": poster_url,
                "poster_local": poster_path,
                "duracion": duracion,
                "fecha_estreno": fecha_estreno,
                "generos": generos,
                "clasificacion": clasificacion,
                "directores": directores,
                "actores": actores,
                "sinopsis": sinopsis,
                "fecha_scraping": datetime.now().isoformat()
            }
            
            # Guardar los datos
            self._save_movie_data(movie_data)
            
            return movie_data
            
        except Exception as e:
            logger.error(f"Error al extraer detalles de {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "fecha_scraping": datetime.now().isoformat()
            }
    
    def _extract_element_text(self, selectors):
        """Extrae texto de un elemento usando múltiples selectores posibles"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    return element.text.strip()
            except NoSuchElementException:
                continue
        return ""
    
    def _extract_multiple_elements_text(self, selectors):
        """Extrae texto de múltiples elementos usando múltiples selectores posibles"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return [element.text.strip() for element in elements]
            except NoSuchElementException:
                continue
        return []
    
    def _extract_image_url(self, selectors):
        """Extrae URL de una imagen usando múltiples selectores posibles"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    return element.get_attribute("src")
            except NoSuchElementException:
                continue
        return None
    
    def _download_image(self, image_url, title):
        """Descarga y guarda una imagen"""
        if not image_url:
            return None
            
        try:
            # Crear nombre de archivo seguro
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            if not safe_title:
                safe_title = 'imagen_sin_titulo'
                
            # Extraer extensión o usar .jpg
            extension = os.path.splitext(image_url.split('?')[0])[1]
            if not extension:
                extension = '.jpg'
                
            image_path = os.path.join(self.images_dir, f"{safe_title}{extension}")
            
            # Verificar si ya existe
            if os.path.exists(image_path):
                logger.info(f"La imagen para '{title}' ya existe: {image_path}")
                return image_path
                
            # Descargar la imagen
            response = requests.get(image_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Guardar la imagen
            with open(image_path, 'wb') as f:
                f.write(response.content)
                
            # Optimizar la imagen
            try:
                img = Image.open(image_path)
                img.save(image_path, optimize=True, quality=85)
            except Exception as e:
                logger.warning(f"No se pudo optimizar la imagen: {e}")
                
            logger.info(f"Imagen guardada para '{title}': {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Error al descargar imagen para '{title}': {e}")
            return None
    
    def _save_movie_data(self, movie_data):
        """Guarda los datos de la película en un archivo JSON"""
        import json
        
        # Crear nombre de archivo seguro
        title = movie_data.get("titulo", "pelicula_sin_titulo")
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        if not safe_title:
            safe_title = 'pelicula_sin_titulo'
            
        # Añadir fecha al nombre del archivo
        date_str = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(self.movies_dir, f"{safe_title}_{date_str}.json")
        
        # Guardar como JSON
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(movie_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Datos guardados para '{title}': {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error al guardar datos para '{title}': {e}")
            return None 