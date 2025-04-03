import requests
from bs4 import BeautifulSoup
import yaml
import os
import json
from datetime import datetime
import argparse

class CinesaScraper:
    def __init__(self):
        # Cargar configuración
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.base_url = f"https://{self.config['scrape_website']}"
        self.user_agent = self.config['scraper']['user_agent']
        self.headers = {
            'User-Agent': self.user_agent
        }
    
    def obtener_peliculas(self):
        """Obtiene la lista de películas de la página principal"""
        url = f"{self.base_url}/peliculas/"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar el contenedor de la lista de películas
            pelicula_items = soup.select('.v-film-list-film')
            
            peliculas = []
            for item in pelicula_items:
                try:
                    # Extraer información básica
                    link_element = item.select_one('.v-film-list-film__link')
                    titulo_element = item.select_one('.v-film-title__text')
                    imagen_element = item.select_one('.v-film-image__img img')
                    clasificacion_element = item.select_one('.v-censor-rating-icon__img img')
                    
                    # Verificar si es "Próximos" o tiene alguna etiqueta especial
                    etiqueta_element = item.select_one('.v-promoted-tag__label')
                    
                    if link_element and titulo_element:
                        pelicula = {
                            'titulo': titulo_element.text.strip(),
                            'url': self.base_url + link_element.get('href', ''),
                            'id': link_element.get('href', '').split('/')[-2] if link_element.get('href') else None,
                            'imagen': imagen_element.get('src') if imagen_element else None,
                            'clasificacion': clasificacion_element.get('alt') if clasificacion_element else 'No especificada',
                            'etiqueta': etiqueta_element.text.strip() if etiqueta_element else None
                        }
                        peliculas.append(pelicula)
                except Exception as e:
                    print(f"Error al procesar película: {e}")
            
            return peliculas
            
        except Exception as e:
            print(f"Error al obtener películas: {e}")
            return []
    
    def obtener_detalles_pelicula(self, url):
        """Obtiene los detalles de una película específica"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Aquí puedes extraer más detalles como sinopsis, duración, director, etc.
            # Esto dependerá de la estructura específica de la página de detalles
            
            detalles = {
                'url': url,
                'sinopsis': self._extraer_sinopsis(soup),
                'duracion': self._extraer_duracion(soup),
                'director': self._extraer_director(soup),
                'genero': self._extraer_genero(soup),
            }
            
            return detalles
            
        except Exception as e:
            print(f"Error al obtener detalles de la película: {e}")
            return {}
    
    def _extraer_sinopsis(self, soup):
        # Implementar extracción de sinopsis
        sinopsis_element = soup.select_one('.v-film-synopsis')
        return sinopsis_element.text.strip() if sinopsis_element else "No disponible"
    
    def _extraer_duracion(self, soup):
        # Implementar extracción de duración
        duracion_element = soup.select_one('.v-film-info-list__item--duration .v-film-info-list__text')
        return duracion_element.text.strip() if duracion_element else "No disponible"
    
    def _extraer_director(self, soup):
        # Implementar extracción de director
        director_element = soup.select_one('.v-film-credits__persons--directors .v-film-credits__name')
        return director_element.text.strip() if director_element else "No disponible"
    
    def _extraer_genero(self, soup):
        # Implementar extracción de género
        genero_element = soup.select_one('.v-film-info-list__item--genre .v-film-info-list__text')
        return genero_element.text.strip() if genero_element else "No disponible"
    
    def guardar_datos(self, peliculas, ruta_archivo=None):
        """Guarda los datos de películas en un archivo JSON"""
        if ruta_archivo is None:
            # Crear directorio data si no existe
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Generar nombre de archivo con timestamp
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_archivo = os.path.join(data_dir, f"cinesa_peliculas_{fecha}.json")
        
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
    if not args.solo_lista:
        print("Obteniendo detalles de películas...")
        for i, pelicula in enumerate(peliculas):
            print(f"Procesando película {i+1}/{len(peliculas)}: {pelicula['titulo']}")
            detalles = scraper.obtener_detalles_pelicula(pelicula['url'])
            peliculas[i].update(detalles)
    
    # Guardar los datos
    scraper.guardar_datos(peliculas, args.guardar)

if __name__ == "__main__":
    main()