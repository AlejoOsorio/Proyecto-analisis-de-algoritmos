import os

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.util.selenium_utils import get_driver
from src.util.ris_utils import merge_ris_file
from src.util.utils import validate_path


class WebScraperIeee:
    def __init__(self):
        self.download_path = os.getenv("DOWNLOAD_PATH") + "\\ieee"
        validate_path(self.download_path)
        self.driver = get_driver(self.download_path)
        self.search_term = os.getenv("SEARCH_TERM")

    def run(self):
        crai = os.getenv("BIBLIOTECA_CRAI")
        wait = WebDriverWait(self.driver, 60)

        self.driver.get(crai)

        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".onload-background")))

        ingenieria = self.driver.find_element(By.XPATH, '//*[@id="block-stacks-content-listing-results-block"]/div/details[7]/summary')
        ingenieria.click()

        ieee = self.driver.find_element(By.XPATH, '//*[@id="facingenieraieeeinstituteofelectricalandelectronicsengineersdescubridor"]/div/div/h3')
        ieee.click()

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
            deny_all = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="9475265f-50e2-41d2-89e8-8f3216186899"]/div[2]/button[3]'))
            )
            deny_all.click()
        except TimeoutException:
            print("El banner de cookies no apareció o fue bloqueado por el navegador.")

        input_search = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/header/xpl-header/div/div[2]/div[2]/xpl-search-bar-migr/div/form/div[2]/div/div[1]/xpl-typeahead-migr/div/input')))
        input_search.send_keys(self.search_term)
        input_search.send_keys(Keys.ENTER)

        button_item_per_page = wait.until(EC.element_to_be_clickable((By.ID, "dropdownPerPageLabel")))
        button_item_per_page.click()

        hundred_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xplMainContent"]/div[1]/div[1]/ul/li[2]/xpl-rows-per-page-drop-down/div/div/button[5]')))
        hundred_option.click()

        for _ in range(10):
            checkbox_select_all = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xplMainContent"]/div[2]/div[2]/xpl-results-list/div[2]/label/input')))
            checkbox_select_all.click()

            btn_export = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xplMainContent"]/div[1]/div[1]/ul/li[3]/xpl-export-search-results/button')))
            btn_export.click()

            selected_citations = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/ngb-modal-window/div/div/div[1]/ul/li[2]/a')))
            selected_citations.click()

            selected_ris = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/ngb-modal-window/div/div/div[2]/div/xpl-citation-download/form/div[1]/section[1]/div/label[3]/input')))
            selected_ris.click()

            selected_abstract = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/ngb-modal-window/div/div/div[2]/div/xpl-citation-download/form/div[1]/section[2]/div/label[2]/input')))
            selected_abstract.click()

            download_selection = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/ngb-modal-window/div/div/div[2]/div/xpl-citation-download/form/div[2]/button[2]')))
            download_selection.click()

            wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/ngb-modal-window/div/div/div[2]/div/xpl-citation-download/form/div[2]/button[2]')))

            close_meu_download = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/ngb-modal-window/div/div/div[1]/div')))
            close_meu_download.click()

            next_page = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'next-btn')))
            next_page.click()

        self.driver.quit()

        merge_ris_file(self.download_path)