import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from src.util.selenium_utils import get_driver
from src.util.ris_utils import merge_ris_file
from src.util.utils import validate_path


class WebScraperTaylorAndFrancis:
    def __init__(self):
        self.download_path = os.getenv("DOWNLOAD_PATH") + "\\taylor"
        validate_path(self.download_path)
        self.driver = get_driver(self.download_path)
        self.search_term = os.getenv("SEARCH_TERM")

    def run(self):
        crai = os.getenv("BILBIOTECA_CRAI")
        wait = WebDriverWait(self.driver, 60)

        self.driver.get(crai)

        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".onload-background")))

        ingenieria = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="block-stacks-content-listing-results-block"]/div/details[7]/summary')))
        ingenieria.click()

        taylor = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="facingenierataylorfrancisconsorciocolombiadescubridor"]/div/div/h3/a/span')))
        taylor.click()

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
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookies_continue.click()
        except TimeoutException:
            print("El banner de cookies no apareció o fue bloqueado por el navegador.")

        input_search = wait.until(EC.element_to_be_clickable((By.ID, "searchText-1d85a42e-ad57-4c0d-a477-c847718bcb5d")))
        time.sleep(2)
        input_search.send_keys(self.search_term)
        input_search.send_keys(Keys.ENTER)

        combo_box_options = wait.until(EC.element_to_be_clickable((By.ID, "perPage-button")))
        combo_box_options.click()

        current_url = self.driver.current_url

        # Analiza y modifica pageSize
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)
        query_params['pageSize'] = ['200']
        nueva_query = urlencode(query_params, doseq=True)
        nueva_url = urlunparse(parsed_url._replace(query=nueva_query))

        self.driver.get(nueva_url)

        for idx in range(3):
            time.sleep(2)

            select_all_checkbox = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "checkbox-container")))
            select_all_checkbox.click()

            download_citations = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="allTabsContainer"]/div/div/div[1]/a[1]')))
            download_citations.click()

            time.sleep(1)

            btn_dowunload_citations = wait.until(EC.element_to_be_clickable((By.ID, "btn-download-citations")))
            btn_dowunload_citations.click()

            time_wait = 0
            while len(os.listdir(self.download_path)) <= 0 and time_wait < 60:
                print("--> esperando que inicie la descarga")
                time.sleep(2)
                time_wait += 2

            if (self.is_download_complete(self.download_path)):
                print("--> Esperando que el archivo descargue completamente")
                time.sleep(1)

            time.sleep(5)
            self.rename_file()
            print("Finalizo la descarga")

            time.sleep(2)

            btn_next_page = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "nextPage")))
            btn_next_page.click()

            while (not self.wait_for_display_none()):
                print("--> Esperando siguiente pagina...")
                time.sleep(2)

        self.driver.quit()
        merge_ris_file(self.download_path)

    def wait_for_display_none(self):
        # Espera hasta que desaparesca determinado item pop up
        element = self.driver.find_element(By.CSS_SELECTOR, ".ajax-overlay")
        display_value = element.value_of_css_property("display")
        return display_value == "none"

    def rename_file(self):
        """Renombra los archivos con nombre acm.bib, para evitar que se sobre escriban"""
        downloaded_files = os.listdir(self.download_path)
        for idx, file_name in enumerate(downloaded_files):
            # Verifica si el archivo ya existe y cambia su nombre
            if file_name == "tandf_citations.ris":
                new_name = f"tandf_citations-{idx}.ris"
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
