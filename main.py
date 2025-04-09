from src.model.web_scraper_ieee import WebScraperIeee
from src.model.web_scraper_science_direct import WebScraperScienceDirect
from src.model.web_scraper_taylor_and_francis import WebScraperTaylorAndFrancis


def main():
    scraper_taylor = WebScraperTaylorAndFrancis()
    scraper_taylor.run()

    scraper_ieee = WebScraperIeee()
    scraper_ieee.run()

    scraper_science = WebScraperScienceDirect()
    scraper_science.run()


if __name__ == '__main__':
    main()
