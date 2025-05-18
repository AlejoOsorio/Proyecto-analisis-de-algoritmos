import os
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from dotenv import load_dotenv

load_dotenv()  # Cargar variables desde el archivo .env

def get_edge_driver(download_path):
    """Retorna el driver del navegador Microsoft Edge."""
    EDGE_DRIVER_PATH = os.getenv("EDGE_DRIVER_PATH")

    options = EdgeOptions()
    options.use_chromium = True
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('prefs', {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    })

    service = EdgeService(executable_path=EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)
    return driver
