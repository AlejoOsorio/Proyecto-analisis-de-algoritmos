from collections import defaultdict
import os


import numpy as np
import matplotlib.pyplot as plt


from src.model.text_analyzer import TextAnalyzer
from src.fifth_requirement import HierarchicalClustering
from src.util.ris_utils import read_ris_file
from src.model.web_scraper_sage import WebScraperSage
from src.model.web_scraper_ieee import WebScraperIeee
from src.model.web_scraper_science_direct import WebScraperScienceDirect

from dotenv import load_dotenv

from src.util.visualization_utils import create_category_wordclouds, create_co_occurrence_network, create_combined_wordcloud, create_frequency_bar_charts
load_dotenv()

def top_fifteen_authors(file):
    elements = read_ris_file(file)
    authors_count = defaultdict(int)
    for e in elements:
        authors = e.get("authors")
        if authors:
            authors_count[authors[0]] += 1
    sorted_dict = dict(sorted(authors_count.items(), key=lambda item: item[1], reverse=True))
    return dict(list(sorted_dict.items())[:15])

def publication_years_per_product_type(file):
    elements = read_ris_file(file)
    year_pub = defaultdict(lambda: defaultdict(int))
    for e in elements:
        year = e.get("year") or e.get("publication_year")
        pub_type = e.get("type_of_reference")
        if year and pub_type:
            year_pub[year][pub_type] += 1
    return year_pub

def count_products_by_type(file):
    elements = read_ris_file(file)
    type_prod = defaultdict(int)
    for e in elements:
        pub_type = e.get("type_of_reference")
        if pub_type:
            type_prod[pub_type] += 1
    return type_prod

def top_fifteen_journals(file):
    elements = read_ris_file(file)
    journals = defaultdict(int)
    for e in elements:
        journal = e.get("journal_name")
        pub_type = e.get("type_of_reference")
        if journal and pub_type == "JOUR":
            journals[journal] += 1
    sorted_dict = dict(sorted(journals.items(), key=lambda item: item[1], reverse=True))
    return dict(list(sorted_dict.items())[:15])

def top_fifteen_publishers(file):
    elements = read_ris_file(file)
    publishers = defaultdict(int)
    for e in elements:
        publisher = e.get("publisher")
        if publisher:
            publishers[publisher] += 1
    sorted_dict = dict(sorted(publishers.items(), key=lambda item: item[1], reverse=True))
    return dict(list(sorted_dict.items())[:15])

def plot_bar_chart_from_dict(data_dict, title='Bar Chart', xlabel='Categories', ylabel='Values', rotation=45):
    keys = list(data_dict.keys())
    values = list(data_dict.values())
    plt.figure(figsize=(10, 6))
    plt.bar(keys, values, color='skyblue', edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation)
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def plot_grouped_bar_chart(nested_dict, title='Grouped Bar Chart', xlabel='Main Category', ylabel='Values'):
    categories = list(nested_dict.keys())
    subcategories = sorted({sub for v in nested_dict.values() for sub in v.keys()})
    x = np.arange(len(categories))
    bar_width = 0.8 / len(subcategories)
    plt.figure(figsize=(12, 7))
    for i, sub in enumerate(subcategories):
        values = [nested_dict[cat].get(sub, 0) for cat in categories]
        plt.bar(x + i * bar_width, values, width=bar_width, label=sub)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(x + bar_width * (len(subcategories)-1) / 2, categories, rotation=90)
    plt.legend(title='Tipo de producto')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def fivth_requirement():
    a = HierarchicalClustering()
    a.load_data(os.getenv("UNIQUE_FILE_PATH"))
    a.vectorize_texts()
    a.compare_methods()

def run_text_analysis_pipeline():
    ris_file_path = os.getenv("UNIQUE_FILE_PATH")
    base_dir = os.path.dirname(ris_file_path)
    output_dir = os.path.join(base_dir, "results")
    visualizations_dir = os.path.join(output_dir, "visualizations")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(visualizations_dir, exist_ok=True)

    print("Inicializando TextAnalyzer...")
    analyzer = TextAnalyzer(ris_file_path)

    print("Analizando frecuencias...")
    freq_results = analyzer.analyze_frequency()

    print("Analizando co-ocurrencias...")
    co_occur_results = analyzer.analyze_co_occurrence()

    print("Guardando resultados...")
    analyzer.save_results(output_dir)

    print("Generando visualizaciones...")
    print(" - Creando nubes de palabras por categoría...")
    create_category_wordclouds(freq_results, os.path.join(visualizations_dir, "wordclouds"))

    print(" - Creando nube de palabras combinada...")
    create_combined_wordcloud(freq_results, os.path.join(visualizations_dir, "wordclouds"))

    print(" - Creando gráfico de red de co-ocurrencias...")
    create_co_occurrence_network(
        co_occur_results,
        os.path.join(visualizations_dir, "co_occurrence_network.png"),
        min_weight=2,
        max_nodes=30
    )

    print(" - Creando gráficos de barras de frecuencia...")
    create_frequency_bar_charts(freq_results, os.path.join(visualizations_dir, "bar_charts"), top_n=15)

    print("¡Proceso completado con éxito!")
    print(f"Resultados guardados en: {output_dir}")

    
def main():
    try:
        scraper_sage = WebScraperSage()
        scraper_sage.run()

        scraper_ieee = WebScraperIeee()
        scraper_ieee.run()

        scraper_science = WebScraperScienceDirect()
        scraper_science.run()

        print("Web scrapers finalizados con éxito")
    except Exception as e:
        print(f"Ocurrió un error con los scrapers: {e}")

    print("Iniciando análisis estadístico...")

    unified_file = os.getenv("UNIQUE_FILE_PATH")

    a = top_fifteen_authors(unified_file)
    b = publication_years_per_product_type(unified_file)
    c = count_products_by_type(unified_file)
    d = top_fifteen_journals(unified_file)
    e = top_fifteen_publishers(unified_file)

    plot_bar_chart_from_dict(a, title='15 autores con más publicaciones', xlabel='Autores', ylabel='Cantidad')
    plot_grouped_bar_chart(b, title='Publicaciones por Año y Tipo', xlabel='Año', ylabel='Cantidad')
    plot_bar_chart_from_dict(c, title='Productos por tipo', xlabel='Producto', ylabel='Cantidad')
    plot_bar_chart_from_dict(d, title='15 journals con más apariciones', xlabel='Journal', ylabel='Cantidad', rotation=90)
    plot_bar_chart_from_dict(e, title='15 publishers con más artículos', xlabel='Publisher', ylabel='Cantidad')

    fivth_requirement()

    print("Ejecutando análisis de texto y visualizaciones adicionales...")
    run_text_analysis_pipeline()

    print("Iniciando servidor Flask...")

    # Importa app justo antes de iniciar Flask para evitar recarga doble
    from app import app

    # Desactiva el reloader para que no se reinicie el servidor automáticamente
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    main()
