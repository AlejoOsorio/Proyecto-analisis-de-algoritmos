from collections import defaultdict
import json
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from src.util.ris_utils import read_ris_file, merge_ris_file
from src.model.web_scraper_sage import WebScraperSage
from src.model.web_scraper_ieee import WebScraperIeee
from src.model.web_scraper_science_direct import WebScraperScienceDirect
from src.model.text_analyzer import TextAnalyzer

def configure_environment():
    """Configura las variables de entorno y estructura de directorios"""
    # Configurar paths
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    
    # Crear estructura de directorios
    data_dir.mkdir(exist_ok=True)
    (data_dir / "ieee").mkdir(exist_ok=True)
    (data_dir / "sage").mkdir(exist_ok=True)
    (data_dir / "science").mkdir(exist_ok=True)
    
    # Configurar variables de entorno que los scrapers esperan
    os.environ["DOWNLOAD_PATH"] = str(data_dir)
    os.environ["UNIQUE_FILE_PATH"] = str(data_dir / "sample.ris")

def run_scrapers():
    """Ejecuta todos los scrapers con manejo de errores"""
    try:
        print("⚙️ Configurando entorno...")
        configure_environment()
        
        print("🚀 Iniciando scrapers...")
        scraper_sage = WebScraperSage()
        scraper_sage.run()

        scraper_ieee = WebScraperIeee()
        scraper_ieee.run()

        scraper_science = WebScraperScienceDirect()
        scraper_science.run()
        
        print("✅ Todos los scrapers finalizados con éxito")
    except Exception as e:
        print(f"❌ Error en los scrapers: {e}")
        raise

def unify_ris_files():
    """Une los archivos RIS descargados en un solo archivo"""
    ris_files = [
        Path("data/sage/sage.ris"),
        Path("data/ieee/ieee.ris"),
        Path("data/science/science.ris")
    ]
    
    output_file = Path("data/sample.ris")
    
    # Filtrar solo archivos que existen
    existing_files = [str(f) for f in ris_files if f.exists()]
    
    if not existing_files:
        print("⚠️ No se encontraron archivos RIS para unificar")
        return None
    
    print("🔗 Unificando archivos RIS...")
    merge_ris_file(existing_files, str(output_file))
    return output_file

# Funciones de análisis (se mantienen igual que en tu versión original)
def top_fifteen_authors(file):
    elements = read_ris_file(file)
    authors_count = defaultdict(int)
    for e in elements:
        authors = e.get("authors")
        if authors:
            authors_count[authors[0]] += 1
    return dict(sorted(authors_count.items(), key=lambda item: item[1], reverse=True)[:15])

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
    return dict(sorted(journals.items(), key=lambda item: item[1], reverse=True)[:15])

def top_fifteen_publishers(file):
    elements = read_ris_file(file)
    publishers = defaultdict(int)
    for e in elements:
        publisher = e.get("publisher")
        if publisher:
            publishers[publisher] += 1
    return dict(sorted(publishers.items(), key=lambda item: item[1], reverse=True)[:15])

# Funciones de visualización (se mantienen igual)
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
    plt.xticks(x + bar_width * (len(subcategories) - 1) / 2, categories, rotation=90)
    plt.legend(title='Tipo de producto')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def main():
    # 1. Ejecutar scrapers
    run_scrapers()
    
    # 2. Unificar archivos RIS
    unified_file = unify_ris_files()
    if not unified_file or not unified_file.exists():
        print("❌ No se pudo crear el archivo unificado. Verifica que los scrapers funcionaron correctamente.")
        return
    
    # 3. Análisis y visualización
    print("📊 Generando visualizaciones...")
    plot_bar_chart_from_dict(
        top_fifteen_authors(str(unified_file)), 
        title='15 autores con más publicaciones', 
        xlabel='Autores', 
        ylabel='Cantidad'
    )
    plot_grouped_bar_chart(
        publication_years_per_product_type(str(unified_file)), 
        title='Publicaciones por Año y Tipo', 
        xlabel='Año', 
        ylabel='Cantidad'
    )
    plot_bar_chart_from_dict(
        count_products_by_type(str(unified_file)), 
        title='Productos por tipo', 
        xlabel='Producto', 
        ylabel='Cantidad'
    )
    plot_bar_chart_from_dict(
        top_fifteen_journals(str(unified_file)), 
        title='15 journals con más apariciones', 
        xlabel='Journal', 
        ylabel='Cantidad', 
        rotation=90
    )
    plot_bar_chart_from_dict(
        top_fifteen_publishers(str(unified_file)), 
        title='15 publishers con más artículos', 
        xlabel='Publisher', 
        ylabel='Cantidad'
    )

    # 4. Análisis de texto
    print("🔍 Iniciando análisis de texto...")
    output_dir = Path('src') / 'results'
    output_dir.mkdir(exist_ok=True)
    
    try:
        analyzer = TextAnalyzer(str(unified_file))
        analyzer.analyze_frequency()
        analyzer.analyze_co_occurrence()
        analyzer.save_results(str(output_dir))
        print("✅ Análisis de texto completado con éxito.")
    except Exception as e:
        print(f"❌ Error durante el análisis de texto: {e}")

if __name__ == '__main__':
    main()