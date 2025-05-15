import os
import json
from src.model.text_analyzer import TextAnalyzer
from src.util.visualization_utils import (
    create_category_wordclouds,
    create_combined_wordcloud,
    create_co_occurrence_network,
    create_frequency_bar_charts
)

def main():
    # Configuración de rutas
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Cargar y procesar los datos
    ris_file_path = os.path.join(current_dir, "data", "sample.ris")  # Ajusta esta ruta
    output_dir = os.path.join(current_dir, "results")
    visualizations_dir = os.path.join(output_dir, "visualizations")
    
    # Crear directorios si no existen
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(visualizations_dir, exist_ok=True)
    
    # 2. Inicializar y ejecutar el analizador de texto
    print("Inicializando TextAnalyzer...")
    analyzer = TextAnalyzer(ris_file_path)
    
    print("Analizando frecuencias...")
    freq_results = analyzer.analyze_frequency()
    
    print("Analizando co-ocurrencias...")
    co_occur_results = analyzer.analyze_co_occurrence()
    
    print("Guardando resultados...")
    analyzer.save_results(output_dir)
    
    # 3. Generar visualizaciones
    print("Generando visualizaciones...")
    
    # Nubes de palabras por categoría
    print(" - Creando nubes de palabras por categoría...")
    create_category_wordclouds(
        freq_results, 
        os.path.join(visualizations_dir, "wordclouds")
    )
    
    # Nube de palabras combinada
    print(" - Creando nube de palabras combinada...")
    create_combined_wordcloud(
        freq_results,
        os.path.join(visualizations_dir, "wordclouds")
    )
    
    # Gráfico de red de co-ocurrencias
    print(" - Creando gráfico de red de co-ocurrencias...")
    create_co_occurrence_network(
        co_occur_results,
        os.path.join(visualizations_dir, "co_occurrence_network.png"),
        min_weight=2,  # Ajusta este valor según tus necesidades
        max_nodes=30   # Ajusta este valor según tus necesidades
    )
    
    # Gráficos de barras de frecuencia
    print(" - Creando gráficos de barras de frecuencia...")
    create_frequency_bar_charts(
        freq_results,
        os.path.join(visualizations_dir, "bar_charts"),
        top_n=15  # Ajusta este valor según tus necesidades
    )
    
    print("¡Proceso completado con éxito!")
    print(f"Resultados guardados en: {output_dir}")

if __name__ == "__main__":
    main()