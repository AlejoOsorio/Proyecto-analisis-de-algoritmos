import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from src.util.selenium_utils import get_driver_undected
from src.util.ris_utils import clean_ris_file, merge_ris_file
from src.util.utils import validate_path


class WebScraperSage:
    def __init__(self):
        self.download_path = os.getenv("DOWNLOAD_PATH") + "\\sage"
        validate_path(self.download_path)
        self.driver = get_driver_undected(self.download_path)
        self.search_term = os.getenv("SEARCH_TERM")

    def is_not_disabled(self):
        element = self.driver.find_element(By.CSS_SELECTOR, "a.download__btn")
        return "disabled" not in element.get_attribute("class")

    def run(self):
        crai = os.getenv("BIBLIOTECA_CRAI")
        wait = WebDriverWait(self.driver, 60)

        self.driver.get(crai)

        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".onload-background")))

        ingenieria = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="block-stacks-content-listing-results-block"]/div/details[7]/summary')))
        ingenieria.click()

        sage = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="facingenierasagerevistasconsorciocolombiadescubridor"]/div/div/h3/a/span')))
        sage.click()

        btn_google = self.driver.find_element(By.ID, "btn-google")
        btn_google.click()

        input_email = wait.until(EC.element_to_be_clickable((By.ID, "identifierId")))
        input_email.send_keys(os.getenv("EMAIL"))
        input_email.send_keys(Keys.ENTER)

        input_password = wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))
        input_password.send_keys(os.getenv("PASSWORD"))
        input_password.send_keys(Keys.ENTER)

        # Esperar hasta que el banner de cookies sea visible (si aparece)
        try:
            cookies_continue = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
            )
            cookies_continue.click()
        except TimeoutException:
            print("El banner de cookies no apareció o fue bloqueado por el navegador.")

        input_search = wait.until(EC.element_to_be_clickable((By.ID, "AllField35ea26a9-ec16-4bde-9652-17b798d5b6750")))
        time.sleep(2)
        input_search.send_keys(self.search_term)
        input_search.send_keys(Keys.ENTER)

        # Obtiene la URL actual (en caso de que haya redirecciones o cambios por JS)
        url_actual = self.driver.current_url

        # Analiza y modifica pageSize
        parsed_url = urlparse(url_actual)
        query_params = parse_qs(parsed_url.query)
        query_params['pageSize'] = ['100']
        nueva_query = urlencode(query_params, doseq=True)
        nueva_url = urlunparse(parsed_url._replace(query=nueva_query))

        self.driver.get(nueva_url)

        for _ in range(10):
            time.sleep(4)
            interval_articles = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pb-page-content"]/div/div/main/div[1]/div/div/div/div[2]/div[3]/div/span[1]/span')))

            select_all_checkbox = wait.until(EC.element_to_be_clickable((By.ID, "action-bar-select-all")))
            select_all_checkbox.click()

            print("--> exportar citas")
            exported_selected_citations = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pb-page-content"]/div/div/main/div[1]/div/div/div/div[2]/div[4]/div[2]/div/div[2]/a')))
            exported_selected_citations.click()

            while (not self.is_not_disabled()):
                print("Esperando disponibilidad del boton descargar")
                time.sleep(2)

            print("--> Iniciando descarga")
            btn_dowunload_citations = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-secondary.download__btn")))
            btn_dowunload_citations.click()
            print("--> Descarga iniciada")

            if (self.is_download_complete(self.download_path)):
                print("--> Esperando que el archivo descargue completamente")
                time.sleep(1)

            time.sleep(5)
            self.rename_file()
            print("Finalizo la descarga")

            time.sleep(3)

            close_pop_up = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="exportCitation"]/div/div/div[1]/button')))
            close_pop_up.click()

            btn_next_page = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "next")))
            btn_next_page.click()

            time.sleep(2)

            while (not self.next_page_ready(interval_articles)):
                print("--> Esperando siguiente pagina...")
                time.sleep(2)

        self.driver.quit()

        files = [file for file in os.listdir(self.download_path) if file.endswith(".ris")]
        for file in files:
            clean_ris_file(os.path.join(self.download_path, file))

        merge_ris_file(self.download_path)

    def next_page_ready(self, interval_articles):
        # Espera hasta que desaparesca determinado item pop up
        element = self.driver.find_element(By.XPATH, '//*[@id="pb-page-content"]/div/div/main/div[1]/div/div/div/div[2]/div[3]/div/span[1]/span')
        time.sleep(2)
        return element != interval_articles

    def rename_file(self):
        """Renombra los archivos con nombre acm.bib, para evitar que se sobre escriban"""
        downloaded_files = os.listdir(self.download_path)
        for idx, file_name in enumerate(downloaded_files):
            # Verifica si el archivo ya existe y cambia su nombre
            if file_name == "sage.ris":
                new_name = f"sage-{idx}.ris"
                old_path = os.path.join(self.download_path, file_name)
                new_path = os.path.join(self.download_path, new_name)
                os.rename(old_path, new_path)
                print(f"--> Archivo renombrado: {new_name}")

    def is_download_complete(self, directory):
        # Verifica si la descarga ya esta finalizada
        files = os.listdir(directory)
        for f in files:
            if f.endswith('.crdownload'):
                return False
        return True