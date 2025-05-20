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
import requests
from bs4 import BeautifulSoup
import re
import logging
import threading
import concurrent.futures
import urllib.parse
from PIL import Image
from io import BytesIO
import base64

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cinesa_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CinesaScraper")

class CinesaScraper:
    def __init__(self):
        # Cargar configuración
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.config = {}
            logger.warning(f"Archivo de configuración no encontrado en {config_path}, usando valores predeterminados")
        
        # Configurar opciones de Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        
        # Lista de User-Agents para rotar
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]
        
        # Seleccionar un User-Agent aleatorio
        user_agent = random.choice(self.user_agents)
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Inicializar navegador
        logger.info("Inicializando navegador Chrome...")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        
        self.base_url = "https://www.cinesa.es"
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        
        # Crear directorio para guardar películas individuales e imágenes
        self.directorio_peliculas = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'peliculas')
        self.directorio_imagenes = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'imagenes')
        os.makedirs(self.directorio_peliculas, exist_ok=True)
        os.makedirs(self.directorio_imagenes, exist_ok=True)
        
        # Mantener una sesión para las solicitudes
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Semáforo para controlar acceso concurrente al WebDriver
        self.driver_lock = threading.Lock()
    
    def __del__(self):
        # Cerrar el navegador al finalizar
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("Navegador cerrado")
    
    def rotar_user_agent(self):
        """Cambiar el User-Agent para evitar bloqueos"""
        new_user_agent = random.choice(self.user_agents)
        self.headers["User-Agent"] = new_user_agent
        self.session.headers.update({"User-Agent": new_user_agent})
        logger.info(f"User-Agent rotado: {new_user_agent}")
        return new_user_agent

    def esperar_aleatoriamente(self, min_segundos=3, max_segundos=10):
        """Esperar un tiempo aleatorio para simular comportamiento humano"""
        tiempo_espera = random.uniform(min_segundos, max_segundos)
        logger.info(f"Esperando {tiempo_espera:.2f} segundos...")
        time.sleep(tiempo_espera)
    
    def descargar_imagen(self, imagen_url, titulo):
        """Descarga y guarda una imagen localmente"""
        if not imagen_url:
            logger.warning(f"URL de imagen no proporcionada para {titulo}")
            return None
            
        try:
            # Crear nombre de archivo seguro
            titulo_seguro = re.sub(r'[^\w\s-]', '', titulo).strip().replace(' ', '_')
            if not titulo_seguro:
                titulo_seguro = 'imagen_sin_titulo'
                
            # Extraer extensión de archivo o usar .jpg por defecto
            extension = os.path.splitext(urllib.parse.urlparse(imagen_url).path)[1]
            if not extension:
                extension = '.jpg'
                
            nombre_archivo = f"{titulo_seguro}{extension}"
            ruta_imagen = os.path.join(self.directorio_imagenes, nombre_archivo)
            
            # Verificar si la imagen ya existe
            if os.path.exists(ruta_imagen):
                logger.info(f"La imagen para '{titulo}' ya existe, omitiendo descarga")
                return ruta_imagen
                
            # Rotar User-Agent para evitar bloqueos
            user_agent = self.rotar_user_agent()
            headers = self.headers.copy()
            
            # Descargar la imagen
            response = requests.get(imagen_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Guardar la imagen
            with open(ruta_imagen, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"Imagen para '{titulo}' descargada correctamente: {ruta_imagen}")
            
            # Optimizar imagen para reducir tamaño
            try:
                img = Image.open(ruta_imagen)
                img.save(ruta_imagen, optimize=True, quality=85)
            except Exception as e:
                logger.warning(f"No se pudo optimizar la imagen: {e}")
                
            return ruta_imagen
            
        except Exception as e:
            logger.error(f"Error al descargar imagen para '{titulo}': {e}")
            return None
    
    def descargar_imagen_selenium(self, selector, titulo):
        """Descarga imagen directamente desde Selenium"""
        try:
            # Buscar elemento de imagen
            img_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            if not img_elem:
                logger.warning(f"No se encontró imagen para '{titulo}' con selector {selector}")
                return None
                
            # Crear nombre de archivo seguro
            titulo_seguro = re.sub(r'[^\w\s-]', '', titulo).strip().replace(' ', '_')
            if not titulo_seguro:
                titulo_seguro = 'imagen_sin_titulo'
                
            # Usar .jpg como formato por defecto
            extension = '.jpg'
            nombre_archivo = f"{titulo_seguro}{extension}"
            ruta_imagen = os.path.join(self.directorio_imagenes, nombre_archivo)
            
            # Verificar si la imagen ya existe
            if os.path.exists(ruta_imagen):
                logger.info(f"La imagen para '{titulo}' ya existe, omitiendo descarga")
                return ruta_imagen
                
            # Capturar la imagen directamente desde el navegador
            logger.info(f"Capturando imagen para '{titulo}' directamente desde el navegador")
            img_elem.screenshot(ruta_imagen)
            
            # Optimizar imagen
            try:
                img = Image.open(ruta_imagen)
                img.save(ruta_imagen, optimize=True, quality=85)
            except Exception as e:
                logger.warning(f"No se pudo optimizar la imagen: {e}")
                
            return ruta_imagen
            
        except Exception as e:
            logger.error(f"Error al capturar imagen para '{titulo}': {e}")
            return None
    
    def descargar_imagen_base64(self, img_element, titulo):
        """Descarga imagen desde un elemento <img> obteniendo su base64 o src"""
        try:
            # Modificar el src para obtener mejor calidad si es posible
            img_src = img_element.get_attribute("src")
            if img_src and "moviexchange.com" in img_src and "width=" in img_src:
                # Modificar el atributo src para obtener mejor calidad
                self.driver.execute_script(
                    "arguments[0].setAttribute('src', arguments[1])",
                    img_element,
                    re.sub(r'width=\d+', 'width=900', img_src)
                )
                logger.info(f"URL de imagen modificada para mejor calidad")
                
                # Dar tiempo para que cargue la nueva imagen
                time.sleep(1)
            
            # Crear nombre de archivo seguro
            titulo_seguro = re.sub(r'[^\w\s-]', '', titulo).strip().replace(' ', '_')
            if not titulo_seguro:
                titulo_seguro = 'imagen_sin_titulo'
                
            # Usar .jpg como formato por defecto
            extension = '.jpg'
            nombre_archivo = f"{titulo_seguro}{extension}"
            ruta_imagen = os.path.join(self.directorio_imagenes, nombre_archivo)
            
            # Verificar si la imagen ya existe
            if os.path.exists(ruta_imagen):
                logger.info(f"La imagen para '{titulo}' ya existe, omitiendo descarga")
                return ruta_imagen
            
            # Intentar obtener la imagen como base64 o desde su src
            script = """
            var img = arguments[0];
            var canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            var ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/jpeg');
            """
            
            try:
                # Asegurarse de que la imagen esté cargada
                self.driver.execute_script("arguments[0].scrollIntoView();", img_element)
                time.sleep(1)
                
                # Intentar obtener la imagen como base64
                img_data = self.driver.execute_script(script, img_element)
                
                if img_data and img_data.startswith('data:image'):
                    # Extraer la parte base64 y guardarla
                    img_data = img_data.split(',')[1]
                    with open(ruta_imagen, 'wb') as f:
                        f.write(base64.b64decode(img_data))
                    logger.info(f"Imagen para '{titulo}' guardada desde base64")
                    return ruta_imagen
            except Exception as e:
                logger.warning(f"No se pudo obtener imagen como base64: {e}")
            
            # Si no funciona el base64, intentar con captura de pantalla
            img_element.screenshot(ruta_imagen)
            logger.info(f"Imagen para '{titulo}' guardada con screenshot")
            
            # Optimizar imagen
            try:
                img = Image.open(ruta_imagen)
                logger.info(f"Resolución de imagen: {img.width}x{img.height}")
                img.save(ruta_imagen, optimize=True, quality=95)
            except Exception as e:
                logger.warning(f"No se pudo optimizar la imagen: {e}")
                
            return ruta_imagen
            
        except Exception as e:
            logger.error(f"Error al capturar imagen para '{titulo}': {e}")
            return None
    
    def obtener_peliculas(self):
        """Obtiene la lista de películas usando Selenium"""
        url = "https://www.cinesa.es/peliculas/"
        peliculas = []
        
        try:
            logger.info(f"Navegando a: {url}")
            self.driver.get(url)
            
            # Esperar más tiempo para que cargue la página
            self.esperar_aleatoriamente(8, 12)
            
            # Manejar posibles ventanas de cookies
            try:
                boton_cookies = self.driver.find_element(By.ID, "onetrust-accept-btn-handler")
                boton_cookies.click()
                logger.info("Aceptadas las cookies")
                time.sleep(2)
            except Exception:
                logger.info("No se encontró el botón de cookies o ya estaban aceptadas")
            
            # Guardar HTML para depuración
            with open('debug_cinesa_page.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info("Guardado HTML para depuración en debug_cinesa_page.html")
            
            # Intentar con diferentes selectores para películas
            logger.info("Buscando elementos de película...")
            selectores = [
                "li.v-film-list-film", 
                ".v-film-list-film", 
                ".film-list-item",
                ".v-film-grid__item",
                ".movie-container"
            ]
            
            for selector in selectores:
                try:
                    logger.info(f"Probando selector: {selector}")
                    pelicula_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if pelicula_items:
                        logger.info(f"Se encontraron {len(pelicula_items)} elementos con selector {selector}")
                        break
                except Exception as e:
                    logger.warning(f"Error con selector {selector}: {e}")
            
            if not pelicula_items:
                logger.error("No se encontraron elementos de película con ningún selector")
                # Plan B: Usar BeautifulSoup para analizar el HTML guardado
                with open('debug_cinesa_page.html', 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    
                # Buscar elementos que parezcan películas (tarjetas, contenedores, etc.)
                posibles_peliculas = soup.find_all('div', class_=lambda c: c and ('film' in c.lower() or 'movie' in c.lower()))
                logger.info(f"Se encontraron {len(posibles_peliculas)} posibles películas con BeautifulSoup")
                
                for item in posibles_peliculas:
                    try:
                        # Intentar extraer información básica
                        link = item.find('a')
                        if link and 'href' in link.attrs:
                            url_pelicula = link['href']
                            if not url_pelicula.startswith('http'):
                                url_pelicula = f"{self.base_url}{url_pelicula}"
                            
                            titulo_elem = item.find(['h3', 'h2', 'div'], class_=lambda c: c and ('title' in c.lower() or 'nombre' in c.lower()))
                            titulo = titulo_elem.text.strip() if titulo_elem else url_pelicula.split('/')[-1].replace('-', ' ').title()
                            
                            imagen = item.find('img')
                            imagen_url = imagen['src'] if imagen and 'src' in imagen.attrs else None
                            
                            peliculas.append({
                                'titulo': titulo,
                                'url': url_pelicula,
                                'imagen_url': imagen_url
                            })
                    except Exception as e:
                        logger.error(f"Error al procesar posible película: {e}")
                
                return peliculas
            
            # Procesar elementos de películas encontrados con Selenium
            for item in pelicula_items:
                try:
                    # Intentar encontrar el enlace y título con varios selectores
                    enlace_selectores = [
                        '.v-film-list-film__info a', 
                        'a', 
                        '.film-title a', 
                        '.movie-title a'
                    ]
                    
                    enlace = None
                    for selector in enlace_selectores:
                        try:
                            enlace = item.find_element(By.CSS_SELECTOR, selector)
                            if enlace:
                                break
                        except NoSuchElementException:
                            continue
                    
                    if not enlace:
                        raise Exception("No se pudo encontrar el enlace de la película")
                    
                    url_pelicula = enlace.get_attribute('href')
                    
                    # Intentar extraer el título
                    titulo_selectores = [
                        '.v-film-list-film__info h3', 
                        'h3', 
                        '.film-title', 
                        '.movie-title'
                    ]
                    
                    titulo_elem = None
                    for selector in titulo_selectores:
                        try:
                            titulo_elem = item.find_element(By.CSS_SELECTOR, selector)
                            if titulo_elem:
                                break
                        except NoSuchElementException:
                            continue
                    
                    titulo = titulo_elem.text.strip() if titulo_elem else url_pelicula.split('/')[-1].replace('-', ' ').title()
                    
                    # Intentar extraer la imagen
                    imagen_selectores = [
                        '.v-film-list-film__thumbnail img',
                        'img',
                        '.film-poster img',
                        '.movie-poster img'
                    ]
                    
                    imagen = None
                    for selector in imagen_selectores:
                        try:
                            imagen = item.find_element(By.CSS_SELECTOR, selector)
                            if imagen:
                                break
                        except NoSuchElementException:
                            continue
                    
                    # Capturar y guardar la imagen inmediatamente si la encontramos
                    imagen_local = None
                    if imagen:
                        imagen_local = self.descargar_imagen_base64(imagen, titulo)
                    
                    # Otras informaciones que pudieran estar disponibles
                    info_adicional = {}
                    try:
                        # Estado (próximo estreno, en cartelera, etc.)
                        estado_elem = item.find_element(By.CSS_SELECTOR, '.v-film-status, .film-status, .status')
                        if estado_elem:
                            info_adicional['estado'] = estado_elem.text.strip()
                    except NoSuchElementException:
                        pass
                    
                    peliculas.append({
                        'titulo': titulo,
                        'url': url_pelicula,
                        'imagen_local': imagen_local,  # Solo guardamos la ruta local
                        **info_adicional
                    })
                    
                except Exception as e:
                    logger.error(f"Error al procesar una película: {e}")
            
            return peliculas
            
        except Exception as e:
            logger.error(f"Error al obtener lista de películas: {e}")
            return []
    
    def obtener_detalles_pelicula(self, url_pelicula):
        """Obtiene los detalles de una película específica usando Selenium"""
        logger.info(f"Obteniendo detalles para: {url_pelicula}")
        
        try:
            with self.driver_lock:  # Bloqueo para acceso seguro en multithreading
                # Rotar User-Agent
                self.rotar_user_agent()
                
                # Usar Selenium en lugar de requests para evitar el bloqueo 403
                self.driver.get(url_pelicula)
                self.esperar_aleatoriamente(3, 5)  # Reducido el tiempo de espera
                
                # Guardar HTML para depuración
                html_content = self.driver.page_source
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extraer título
                titulo_selectores = [
                    '.v-film-title__text',
                    '.film-title',
                    'h1'
                ]
                
                titulo = "Título no disponible"
                for selector in titulo_selectores:
                    elem = soup.select_one(selector)
                    if elem:
                        titulo = elem.text.strip()
                        break
                
                # Duración
                duracion_selectores = [
                    '.v-film-runtime .v-display-text-part',
                    '.film-runtime',
                    '.duration'
                ]
                
                duracion = None
                for selector in duracion_selectores:
                    elem = soup.select_one(selector)
                    if elem:
                        duracion = elem.text.strip()
                        break
                
                # Fecha de estreno
                fecha_estreno_selectores = [
                    '.v-film-release-date .v-display-text-part',
                    '.release-date',
                    '.film-release-date'
                ]
                
                fecha_estreno = None
                for selector in fecha_estreno_selectores:
                    elem = soup.select_one(selector)
                    if elem:
                        fecha_estreno = elem.text.strip()
                        break
                
                # Géneros
                generos_selectores = [
                    '.v-film-genres__list .v-description-list-item__description',
                    '.film-genres span',
                    '.genres'
                ]
                
                generos = []
                for selector in generos_selectores:
                    elems = soup.select(selector)
                    if elems:
                        generos = [elem.text.strip() for elem in elems]
                        break
                
                # Clasificación
                clasificacion_selectores = [
                    '.v-film-classification-description .v-description-list-item__description',
                    '.film-classification',
                    '.rating'
                ]
                
                clasificacion = None
                for selector in clasificacion_selectores:
                    elem = soup.select_one(selector)
                    if elem:
                        clasificacion = elem.text.strip()
                        break
                
                # Directores
                directores_selectores = [
                    '.v-film-directors .v-display-text-part',
                    '.film-directors',
                    '.directors'
                ]
                
                directores = None
                for selector in directores_selectores:
                    elem = soup.select_one(selector)
                    if elem:
                        directores = elem.text.strip()
                        break
                
                # Actores
                actores_selectores = [
                    '.v-film-actors .v-display-text-part',
                    '.film-actors',
                    '.actors'
                ]
                
                actores = []
                for selector in actores_selectores:
                    elem = soup.select_one(selector)
                    if elem:
                        actores_text = elem.text.strip()
                        actores = [a.strip() for a in actores_text.split(',')]
                        break
                
                # Sinopsis
                sinopsis_selectores = [
                    '.v-film-synopsis .v-display-text-part',
                    '.film-synopsis',
                    '.synopsis'
                ]
                
                sinopsis = "Sinopsis no disponible"
                for selector in sinopsis_selectores:
                    elem = soup.select_one(selector)
                    if elem:
                        sinopsis = elem.text.strip()
                        break
                
                # Poster
                poster_selectores = [
                    '.v-film-image__img img',
                    '.film-poster img',
                    '.movie-poster img'
                ]
                
                # Buscar y guardar el póster inmediatamente
                poster_ruta_local = None
                poster_elem = None
                for selector in poster_selectores:
                    try:
                        poster_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if poster_elem:
                            break
                    except NoSuchElementException:
                        continue
                
                if poster_elem:
                    poster_ruta_local = self.descargar_imagen_base64(poster_elem, titulo)
                
                # Extraer sesiones (usando Selenium para esto también)
                sesiones = self.obtener_sesiones_pelicula_selenium(url_pelicula)
            
            return {
                'titulo': titulo,
                'duracion': duracion,
                'fecha_estreno': fecha_estreno,
                'generos': generos,
                'clasificacion': clasificacion,
                'directores': directores,
                'actores': actores,
                'sinopsis': sinopsis,
                'poster_local': poster_ruta_local,  # Solo guardamos la ruta local
                'sesiones': sesiones,
                'fecha_scraping': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error al obtener detalles de película {url_pelicula}: {e}")
            return {
                'titulo': url_pelicula.split('/')[-1].replace('-', ' ').title(),
                'error': str(e),
                'fecha_scraping': datetime.now().isoformat()
            }

    def obtener_sesiones_pelicula_selenium(self, url_pelicula):
        """Obtiene sesiones usando Selenium para evitar bloqueos"""
        try:
            # Ya estamos en la página de la película, no necesitamos navegar de nuevo
            # Intentar encontrar el ID de la película
            id_pelicula = None
            script_tags = self.driver.find_elements(By.TAG_NAME, 'script')
            
            for script in script_tags:
                try:
                    contenido = script.get_attribute('innerHTML')
                    if 'filmId' in contenido or 'movieId' in contenido:
                        # Buscar patrones como "filmId": "HO00002126" o similar
                        match = re.search(r'"filmId"[:\s]+"([^"]+)"', contenido)
                        if match:
                            id_pelicula = match.group(1)
                            break
                        
                        match = re.search(r'"movieId"[:\s]+"([^"]+)"', contenido)
                        if match:
                            id_pelicula = match.group(1)
                            break
                except:
                    continue
            
            # Si no encontramos el ID, intentar extraerlo de la URL
            if not id_pelicula and '/peliculas/' in url_pelicula:
                match = re.search(r'/peliculas/[^/]+/([^/]+)', url_pelicula)
                if match:
                    id_pelicula = match.group(1)
            
            resultado_sesiones = []
            
            # Si tenemos el ID, pero no queremos arriesgarnos con la API,
            # buscar las sesiones directamente en el HTML
            sesiones_containers = self.driver.find_elements(By.CSS_SELECTOR, '.v-cinema-showtime-list__item, .cinema-container')
            
            if sesiones_containers:
                for container in sesiones_containers:
                    try:
                        nombre_cine_elem = container.find_element(By.CSS_SELECTOR, '.v-cinema-showtime-list__cinema-name, .cinema-name')
                        nombre_cine = nombre_cine_elem.text.strip()
                        
                        sesiones_cine = []
                        fecha_elems = container.find_elements(By.CSS_SELECTOR, '.v-showtime-list__date, .date')
                        
                        for fecha_elem in fecha_elems:
                            fecha = fecha_elem.text.strip()
                            try:
                                sesiones_elem = fecha_elem.find_element(By.XPATH, 'following-sibling::*[1]')
                                sesion_botones = sesiones_elem.find_elements(By.CSS_SELECTOR, '.v-showtime-button, .showtime')
                                
                                for boton in sesion_botones:
                                    hora_elem = boton.find_element(By.CSS_SELECTOR, '.v-showtime-button__time, .time')
                                    hora = hora_elem.text.strip()
                                    
                                    formato = ""
                                    try:
                                        formato_elem = boton.find_element(By.CSS_SELECTOR, '.v-showtime-button__attributes, .format')
                                        formato = formato_elem.text.strip()
                                    except:
                                        pass
                                    
                                    url_compra = boton.get_attribute('href') or ""
                                    
                                    sesiones_cine.append({
                                        'fecha': fecha,
                                        'hora': hora,
                                        'formato': formato,
                                        'url_compra': url_compra
                                    })
                            except:
                                continue
                        
                        if sesiones_cine:
                            resultado_sesiones.append({
                                'nombre_cine': nombre_cine,
                                'sesiones': sesiones_cine
                            })
                    except Exception as e:
                        logger.warning(f"Error al procesar sesiones para un cine: {e}")
            
            return resultado_sesiones
            
        except Exception as e:
            logger.error(f"Error al obtener sesiones de película: {e}")
            return []
    
    def guardar_pelicula(self, pelicula):
        """Guarda una película individual en un archivo JSON"""
        # Generar nombre de archivo seguro a partir del título
        titulo_seguro = re.sub(r'[^\w\s-]', '', pelicula.get('titulo', '')).strip().replace(' ', '_')
        if not titulo_seguro:
            titulo_seguro = 'pelicula_sin_titulo'
            
        fecha_actual = datetime.now().strftime("%Y%m%d")
        
        ruta_archivo = os.path.join(self.directorio_peliculas, f"{titulo_seguro}_{fecha_actual}.json")
        
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(pelicula, f, ensure_ascii=False, indent=4)
            logger.info(f"Película '{pelicula.get('titulo', 'Sin título')}' guardada en {ruta_archivo}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar película '{pelicula.get('titulo', 'Sin título')}': {e}")
            return False
    
    def guardar_indice_peliculas(self, peliculas):
        """Guarda un índice con información básica de todas las películas"""
        indice = []
        for pelicula in peliculas:
            # Solo guardar información básica en el índice
            indice.append({
                'titulo': pelicula.get('titulo', 'Sin título'),
                'url': pelicula.get('url', ''),
                'imagen_url': pelicula.get('imagen_url')
            })
        
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_archivo = os.path.join(os.path.dirname(self.directorio_peliculas), f"cinesa_indice_{fecha_actual}.json")
        
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(indice, f, ensure_ascii=False, indent=4)
            logger.info(f"Índice de películas guardado en {ruta_archivo}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar índice de películas: {e}")
            return False

    def procesar_pelicula_completa(self, pelicula):
        """Procesa una película completa: obtiene detalles y guarda"""
        try:
            logger.info(f"Procesando película: {pelicula.get('titulo', 'Sin título')}")
            detalles = self.obtener_detalles_pelicula(pelicula['url'])
            pelicula.update(detalles)
            self.guardar_pelicula(pelicula)
            return pelicula
        except Exception as e:
            logger.error(f"Error al procesar película {pelicula.get('titulo', 'Sin título')}: {e}")
            return None

# Función principal para ejecutar el scraper
def main():
    parser = argparse.ArgumentParser(description='Scraper de películas de Cinesa')
    parser.add_argument('--solo-lista', '-l', action='store_true', help='Obtener solo la lista de películas sin detalles')
    parser.add_argument('--pelicula', '-p', type=str, help='URL o ID de una película específica para scrapear')
    parser.add_argument('--max', '-m', type=int, default=0, help='Número máximo de películas a procesar (0 = todas)')
    parser.add_argument('--demora', '-d', type=int, default=2, help='Demora mínima entre películas en segundos (default: 2)')
    parser.add_argument('--hilos', '-t', type=int, default=3, help='Número de hilos para procesar películas (default: 3)')
    args = parser.parse_args()
    
    scraper = CinesaScraper()
    
    # Caso de película individual
    if args.pelicula:
        url_pelicula = args.pelicula
        if not url_pelicula.startswith('http'):
            url_pelicula = f"{scraper.base_url}/peliculas/{url_pelicula}"
        
        logger.info(f"Obteniendo detalles para: {url_pelicula}")
        pelicula = scraper.obtener_detalles_pelicula(url_pelicula)
        pelicula['url'] = url_pelicula
        scraper.guardar_pelicula(pelicula)
        return
    
    # Caso de lista de películas
    logger.info("Obteniendo lista de películas...")
    peliculas = scraper.obtener_peliculas()
    logger.info(f"Se encontraron {len(peliculas)} películas")
    
    # Limitar número de películas si se especificó
    if args.max > 0 and args.max < len(peliculas):
        logger.info(f"Limitando a {args.max} películas")
        peliculas = peliculas[:args.max]
    
    # Guardar índice de películas
    scraper.guardar_indice_peliculas(peliculas)
    
    # Si no se solicita solo la lista, obtener detalles de películas con multithreading
    if not args.solo_lista and peliculas:
        logger.info(f"Obteniendo detalles de películas usando {args.hilos} hilos...")
        
        # Configurar el número de trabajadores (hilos)
        num_workers = min(args.hilos, len(peliculas))
        
        # Crear un pool de trabajadores
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Enviar trabajos al pool
            futures = []
            for pelicula in peliculas:
                # Añadir un pequeño retraso entre envíos para evitar sobrecarga
                time.sleep(0.5)
                futures.append(executor.submit(scraper.procesar_pelicula_completa, pelicula))
            
            # Procesar resultados a medida que se completan
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        logger.info(f"Completado procesamiento de: {result.get('titulo', 'Sin título')}")
                except Exception as e:
                    logger.error(f"Error en ejecución de hilo: {e}")

if __name__ == "__main__":
    main()