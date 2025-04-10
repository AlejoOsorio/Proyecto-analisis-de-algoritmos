from src.model.web_scraper_ieee import WebScraperIeee
from src.model.web_scraper_science_direct import WebScraperScienceDirect
from src.model.web_scraper_sage import WebScraperSage


def main():

    try:
        scraper_sage = WebScraperSage()
        scraper_sage.run()

        scraper_ieee = WebScraperIeee()
        scraper_ieee.run()

        scraper_science = WebScraperScienceDirect()
        scraper_science.run()
        print("Web scrapers finalizados con exito")
    except Exception as e:
        print(f"Ocurrio un error: {e}")

    print("Programa finalizado")


if __name__ == '__main__':
    main()
