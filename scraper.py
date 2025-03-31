from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

from config import BASE_URL, MOVIES_URL

def get_movies():
    options = Options()
    options.add_argument("--headless")  # Modo sin interfaz gráfica
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(MOVIES_URL)
    time.sleep(5)  # Esperar a que se cargue la página

    movie_elements = driver.find_elements(By.CSS_SELECTOR, ".v-film-list-film a.v-link")

    movie_list = []
    for movie in movie_elements:
        title = movie.get_attribute("href").split("/")[-2].replace("-", " ").title()
        link = movie.get_attribute("href")
        movie_list.append({"title": title, "link": link})

    driver.quit()
    return movie_list

