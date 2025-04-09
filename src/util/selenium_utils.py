import os

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver(download_path):
    """Retorna el driver del navegador brave"""
    # se obtine la ruta del ejecutable de brave
    BRAVE_PATH = os.getenv("BRAVE_PATH")

    options = Options()
    options.binary_location = BRAVE_PATH
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('prefs', {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    })
    driver = webdriver.Chrome(options=options)
    return driver


def get_driver_undected(download_path):
    """Retorna el driver del navegador brave"""
    # se obtine la ruta del ejecutable de brave
    BRAVE_PATH = os.getenv("BRAVE_PATH")

    options = Options()
    options.add_argument('--disable-gpu')  # Opcional, para mejorar el rendimiento
    options.add_argument('--no-sandbox')  # Opcional, para entornos limitados

    options.binary_location = BRAVE_PATH

    driver = uc.Chrome(options=options)
    driver.maximize_window()
    params = {
        "behavior": "allow",
        "downloadPath": download_path
    }
    driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
    return driver
