import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from wordcloud import WordCloud
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors

def create_wordcloud(frequencies, output_path, title="Nube de Palabras", max_words=100):
    """
    Crea una nube de palabras a partir de un diccionario de frecuencias.
    
    Args:
        frequencies (dict): Diccionario con palabras y sus frecuencias.
        output_path (str): Ruta donde se guardará la imagen.
        title (str): Título para la nube de palabras.
        max_words (int): Número máximo de palabras a mostrar.
    """
    # Crear carpeta si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Crear un mapa de colores personalizado
    colors = ['#5E4FA2', '#3288BD', '#66C2A5', '#ABDDA4', '#E6F598', 
              '#FFFFBF', '#FEE08B', '#FDAE61', '#F46D43', '#D53E4F', '#9E0142']
    
    custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', colors, N=256)
    
    # Crear nube de palabras
    wordcloud = WordCloud(
        width=1200, 
        height=800,
        max_words=max_words,
        background_color='white',
        colormap=custom_cmap,
        collocations=False,  # No incluir bigramas automáticamente
        contour_width=1,
        contour_color='steelblue',
        prefer_horizontal=0.9,  # Tolerancia para palabras verticales
        random_state=42
    ).generate_from_frequencies(frequencies)
    
    # Mostrar la nube de palabras
    plt.figure(figsize=(16, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=20)
    plt.tight_layout(pad=0)
    
    # Guardar la imagen
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def create_category_wordclouds(category_frequencies, output_dir):
    """
    Crea nubes de palabras para cada categoría.
    
    Args:
        category_frequencies (dict): Diccionario con categorías y sus frecuencias de términos.
        output_dir (str): Directorio donde se guardarán las imágenes.
    
    Returns:
        list: Lista de rutas a los archivos generados.
    """
    output_files = []
    
    for category, term_freq in category_frequencies.items():
        # Filtrar términos con frecuencia > 0
        filtered_freq = {term: freq for term, freq in term_freq.items() if freq > 0}
        
        if filtered_freq:  # Solo crear wordcloud si hay términos con frecuencia
            filename = f"wordcloud_{category.replace(' ', '_').lower()}.png"
            output_path = os.path.join(output_dir, filename)
            
            create_wordcloud(
                filtered_freq, 
                output_path, 
                title=f"Nube de Palabras - {category}"
            )
            
            output_files.append(output_path)
    
    return output_files

def create_combined_wordcloud(category_frequencies, output_dir):
    """
    Crea una nube de palabras combinada de todas las categorías.
    
    Args:
        category_frequencies (dict): Diccionario con categorías y sus frecuencias de términos.
        output_dir (str): Directorio donde se guardará la imagen.
    
    Returns:
        str: Ruta al archivo generado.
    """
    # Combinar todas las frecuencias
    combined_freq = {}
    
    for term_freq in category_frequencies.values():
        for term, freq in term_freq.items():
            if freq > 0:  # Solo incluir términos que aparecen
                if term in combined_freq:
                    combined_freq[term] += freq
                else:
                    combined_freq[term] = freq
    
    # Crear nube de palabras combinada
    output_path = os.path.join(output_dir, "wordcloud_combined.png")
    create_wordcloud(
        combined_freq, 
        output_path, 
        title="Nube de Palabras - Todos los Términos",
        max_words=150  # Permitir más palabras en la nube combinada
    )
    
    return output_path

def create_co_occurrence_network(co_occurrences, output_path, min_weight=1, max_nodes=50):
    """
    Crea un gráfico de red para visualizar co-ocurrencias entre términos.
    
    Args:
        co_occurrences (dict): Diccionario anidado con co-ocurrencias entre términos.
        output_path (str): Ruta donde se guardará la imagen.
        min_weight (int): Peso mínimo de co-ocurrencia para incluir en el gráfico.
        max_nodes (int): Número máximo de nodos a mostrar.
    """
    # Crear grafo no dirigido
    G = nx.Graph()
    
    # Agregar aristas con pesos
    edges = []
    
    for term1, co_terms in co_occurrences.items():
        for term2, weight in co_terms.items():
            if weight >= min_weight:
                edges.append((term1, term2, weight))
    
    # Ordenar bordes por peso (de mayor a menor)
    edges.sort(key=lambda x: x[2], reverse=True)
    
    # Limitar el número de nodos a mostrar
    if len(edges) > max_nodes*2:
        edges = edges[:max_nodes*2]
    
    # Crear conjunto de nodos y añadir aristas al grafo
    nodes = set()
    for u, v, w in edges:
        nodes.add(u)
        nodes.add(v)
        G.add_edge(u, v, weight=w)
    
    # Limitar número de nodos si es necesario
    if len(nodes) > max_nodes:
        # Calcular centralidad de grado
        degree_centrality = nx.degree_centrality(G)
        # Ordenar nodos por centralidad
        sorted_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
        # Mantener solo los nodos más centrales
        nodes_to_keep = [node for node, _ in sorted_nodes[:max_nodes]]
        # Crear subgrafo
        G = G.subgraph(nodes_to_keep)
    
    # Calcular posiciones de nodos usando layout de resorte (spring layout)
    pos = nx.spring_layout(G, k=0.3, seed=42)
    
    # Extraer pesos para el grosor de las aristas
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    
    # Normalizar pesos para el grosor de las aristas
    normalized_weights = [weight/max_weight * 5 for weight in edge_weights]
    
    # Configurar tamaño de nodos basado en la centralidad
    degree_centrality = nx.degree_centrality(G)
    node_sizes = [degree_centrality[node] * 5000 + 100 for node in G.nodes()]
    
    # Crear figura
    plt.figure(figsize=(20, 16))
    
    # Dibujar nodos
    nx.draw_networkx_nodes(
        G, pos, 
        node_size=node_sizes, 
        node_color='skyblue', 
        alpha=0.8, 
        linewidths=1.0,
        edgecolors='navy'
    )
    
    # Dibujar aristas con grosor según peso
    nx.draw_networkx_edges(
        G, pos, 
        width=normalized_weights, 
        alpha=0.5, 
        edge_color='navy',
        style='solid'
    )
    
    # Dibujar etiquetas de los nodos
    nx.draw_networkx_labels(
        G, pos, 
        font_size=10, 
        font_family='sans-serif', 
        font_weight='bold'
    )
    
    plt.title('Red de Co-ocurrencia de Términos', fontsize=20)
    plt.axis('off')
    
    # Guardar imagen
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def create_frequency_bar_charts(category_frequencies, output_dir, top_n=10):
    """
    Crea gráficos de barras para mostrar la frecuencia de términos por categoría.
    
    Args:
        category_frequencies (dict): Diccionario con categorías y sus frecuencias de términos.
        output_dir (str): Directorio donde se guardarán las imágenes.
        top_n (int): Número de términos principales a mostrar.
    
    Returns:
        list: Lista de rutas a los archivos generados.
    """
    output_files = []
    
    # Colores para los gráficos
    colors = plt.cm.viridis(np.linspace(0, 1, len(category_frequencies)))
    
    for idx, (category, term_freq) in enumerate(category_frequencies.items()):
        # Filtrar términos con frecuencia > 0
        filtered_freq = {term: freq for term, freq in term_freq.items() if freq > 0}
        
        if filtered_freq:  # Solo crear gráfico si hay términos con frecuencia
            # Ordenar por frecuencia y tomar los top_n
            sorted_terms = sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
            
            terms = [item[0] for item in sorted_terms]
            freqs = [item[1] for item in sorted_terms]
            
            # Crear gráfico de barras
            plt.figure(figsize=(12, 8))
            
            # Dibujar barras horizontales
            bars = plt.barh(terms, freqs, color=colors[idx % len(colors)], alpha=0.8)
            
            # Añadir valores en las barras
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 0.3, bar.get_y() + bar.get_height()/2, 
                         f'{int(width)}', 
                         ha='left', va='center', fontweight='bold')
            
            plt.title(f'Top {len(terms)} Términos en {category}', fontsize=16)
            plt.xlabel('Frecuencia', fontsize=12)
            plt.tight_layout()
            
            # Guardar imagen
            filename = f"barchart_{category.replace(' ', '_').lower()}.png"
            output_path = os.path.join(output_dir, filename)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            output_files.append(output_path)
    
    return output_files