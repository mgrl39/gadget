# Gadget

Este proyecto está diseñado para extraer información de la página web de Cinesa y almacenarla en una base de datos.

<p align="center">
  <img src="gadget.jpeg" width="500" alt="Gadget Logo">
</p>

## Características
- **Scraping**: Extrae la lista de películas disponibles en [Cinesa](https://www.cinesa.es/peliculas/).
- **Base de Datos**: Inserta los datos extraídos en una base de datos MySQL.
- **Automatización**: Usa un `Makefile` para simplificar tareas comunes.

## Requisitos
- Python 3.x
- Entorno virtual (`venv`)
- Dependencias listadas en `requirements.txt`

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/mgrl39/gadget.git
   cd gadget
   ```

2. **Configurar el entorno virtual**:
   ```bash
   make venv
   ```

3. **Instalar dependencias**:
   ```bash
   make install
   ```

4. **Configurar la base de datos**:
   - Edita el archivo `config/config.yaml` con las credenciales de tu base de datos MySQL.

5. **Ejecutar el scraper**:
   ```bash
   make run
   ```

## Licencia
Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.
