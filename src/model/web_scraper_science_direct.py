import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from src.util.selenium_utils import get_driver_undected
from src.util.ris_utils import merge_ris_file
from src.util.utils import validate_path


class WebScraperScienceDirect:
    def __init__(self):
        self.download_path = os.getenv("DOWNLOAD_PATH") + "\\science"
        validate_path(self.download_path)
        self.driver = get_driver_undected(self.download_path)
        self.search_term = os.getenv("SEARCH_TERM")

    def run(self):
        crai = os.getenv("BILBIOTECA_CRAI")
        wait = WebDriverWait(self.driver, 60)

        self.driver.get(crai)

        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".onload-background")))

        ingenieria = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="block-stacks-content-listing-results-block"]/div/details[7]/summary')))
        ingenieria.click()

        sicne_direct = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="facingenierasciencedirectconsorciocolombiadescubridor"]/div/div/h3/a')))
        sicne_direct.click()

        btn_google = self.driver.find_element(By.ID, "btn-google")
        btn_google.click()

        input_email = wait.until(EC.element_to_be_clickable((By.ID, "identifierId")))
        input_email.send_keys(os.getenv("EMAIL"))
        input_email.send_keys(Keys.ENTER)

        input_password = wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))
        input_password.send_keys(os.getenv("PASSWORD"))
        input_password.send_keys(Keys.ENTER)

        input_search = wait.until(EC.element_to_be_clickable((By.ID, "qs")))
        input_search.send_keys(self.search_term)
        input_search.send_keys(Keys.ENTER)

        select_hundred = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[span[text()='100']]")))
        select_hundred.click()

        time.sleep(2)

        for _ in range(10):
            print("Seleccionar chek")

            select_all_check = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="srp-toolbar"]/div[1]/span/span[1]/span[1]/div/div/label/span[1]')))
            select_all_check.click()

            time.sleep(1)

            print("boton export")
            btn_export = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="srp-toolbar"]/div[1]/span/span[1]/span[2]/div[2]/button')))
            btn_export.click()

            time.sleep(1)

            print("export to ris")
            export_to_ris = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div/p/div/div/button[2]')))
            export_to_ris.click()

            select_all_check = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="srp-toolbar"]/div[1]/span/span[1]/span[1]/div/div/label/span[1]')))
            select_all_check.click()

            time.sleep(4)

            self.driver.execute_script("""
                var feedback_button = document.getElementById("_pendo-badge_9BcFvkCLLiElWp6hocDK3ZG6Z4E");
                if (feedback_button) {
                    feedback_button.style.display = 'none';
                }
            """)

            next_button = WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.pagination-link.next-link a"))
            )

            if "disabled" not in next_button.get_attribute("class") and next_button.is_displayed():
                ActionChains(self.driver).move_to_element(next_button).click().perform()
                print("Cargando siguiente página...")

                WebDriverWait(self.driver, 2000).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.result-item-content"))
                )
                print("Página siguiente cargada.")
                time.sleep(5)

        self.driver.quit()
        merge_ris_file(self.download_path)
