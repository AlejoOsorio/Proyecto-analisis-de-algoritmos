from collections import defaultdict
import json
import os

import numpy as np
import matplotlib.pyplot as plt

from src.util.ris_utils import read_ris_file
from src.model.web_scraper_sage import WebScraperSage
from src.model.web_scraper_ieee import WebScraperIeee
from src.model.web_scraper_science_direct import WebScraperScienceDirect
from dotenv import load_dotenv

load_dotenv()

def top_fifteen_authors(file):
    elements = read_ris_file(file)
    authors_count = defaultdict()

    for e in elements:
        authors = e.get("authors")

        if authors:
            aut = authors[0]
            if aut in authors_count:
                authors_count[aut] += 1
            else:
                authors_count[aut] = 1
    
    sorted_dict =  {k: v for k, v in sorted(authors_count.items(), key=lambda item: item[1], reverse=True)}
    
    return dict(list(sorted_dict.items())[:15])


def publication_years_per_product_type(file):
    elements = read_ris_file(file)
    year_pub = defaultdict(lambda: defaultdict(int))

    for e in elements:
        year = e.get("year") or e.get("publication_year")
        pub_type = e.get("type_of_reference")

        if year:
            if year in year_pub and pub_type in year_pub[year]:
                year_pub[year][pub_type] += 1
            else:
                year_pub[year][pub_type] = 1
    
    return year_pub


def count_products_by_type(file):
    elements = read_ris_file(file)
    type_prod = defaultdict()

    for e in elements:
        pub_type = e.get("type_of_reference")

        if pub_type:
            if pub_type in type_prod:
                type_prod[pub_type] += 1
            else:
                type_prod[pub_type] = 1
    
    return type_prod


def top_fifteen_journals(file):
    elements = read_ris_file(file)
    journals = defaultdict()

    for e in elements:
        journal = e.get("journal_name")
        pub_type = e.get("type_of_reference")

        if journal and pub_type and pub_type == "JOUR":
            if journal in journals:
                journals[journal] += 1
            else:
                journals[journal] = 1
    
    sorted_dict =  {k: v for k, v in sorted(journals.items(), key=lambda item: item[1], reverse=True)}
    
    return dict(list(sorted_dict.items())[:15])

def top_fifteen_publishers(file):
    elements = read_ris_file(file)
    publishers = defaultdict()

    for e in elements:
        publisher = e.get("publisher")
        
        if publisher:
            if publisher in publishers:
                publishers[publisher] += 1
            else:
                publishers[publisher] = 1

    sorted_dict =  {k: v for k, v in sorted(publishers.items(), key=lambda item: item[1], reverse=True)}
    
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
    categories = list(nested_dict.keys())  # e.g., años
    subcategories = sorted({sub for v in nested_dict.values() for sub in v.keys()})  # e.g., tipos de producto

    x = np.arange(len(categories))  # posiciones en el eje X
    bar_width = 0.8 / len(subcategories)  # espacio para cada barra

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


def main():

    # Web scrappers
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

    print("Scrapers finalizados")

    # Estadisticas
    unified_file  = os.getenv("UNIQUE_FILE_PATH")
    
    a = top_fifteen_authors(unified_file)
    b = publication_years_per_product_type(unified_file)
    c = count_products_by_type(unified_file)
    d = top_fifteen_journals(unified_file)
    e = top_fifteen_publishers(unified_file)

    plot_bar_chart_from_dict(a, title='15 autores con más publicaciones', xlabel='Autores', ylabel='Cantidad')
    plot_grouped_bar_chart(b, title='Publicaciones por Año y Tipo', xlabel='Año', ylabel='Cantidad')
    plot_bar_chart_from_dict(c, title='Productos por tipo', xlabel='Producto', ylabel='Cantidad')
    plot_bar_chart_from_dict(d, title='15 journals con más apariciones', xlabel='Journal', ylabel='Cantidad', rotation=90)
    plot_bar_chart_from_dict(e, title='15 publishers con más articulos', xlabel='Publisher', ylabel='Cantidad')


if __name__ == '__main__':
    main()