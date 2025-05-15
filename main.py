from src.model.web_scraper_ieee import WebScraperIeee
from src.model.web_scraper_science_direct import WebScraperScienceDirect
from src.model.web_scraper_sage import WebScraperSage
from src.model.content_analyzer import ContentAnalyzer
from src.util.categories import Categories # Asumido que esta clase existe para manejar categorías

def main():
    try:
        # Inicialización de los scrapers
        scraper_sage = WebScraperSage()
        scraper_sage.run()

        scraper_ieee = WebScraperIeee()
        scraper_ieee.run()

        scraper_science = WebScraperScienceDirect()
        scraper_science.run()
        
        # Asumimos que los scrapers devuelven una lista de entradas RIS
        entries = scraper_sage.get_entries() + scraper_ieee.get_entries() + scraper_science.get_entries()
        
        # Inicialización del analizador de contenido con las categorías
        categories_handler = Categories()  # Inicializa el manejador de categorías
        content_analyzer = ContentAnalyzer(categories_handler)
        
        # Carga y analiza las entradas obtenidas de los scrapers
        category_term_frequencies, combined_term_frequencies = content_analyzer.load_and_analyze_entries(entries)
        
        # Muestra los resultados del análisis
        print("Frecuencia de términos por categoría:")
        print(category_term_frequencies)
        
        print("Frecuencia combinada de términos:")
        print(combined_term_frequencies)

    except Exception as e:
        print(f"Ocurrió un error: {e}")

    print("Programa finalizado")

if __name__ == '__main__':
    main()
