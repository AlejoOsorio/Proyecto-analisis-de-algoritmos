# util/visualization.py

import os
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from wordcloud import WordCloud
from collections import Counter
import seaborn as sns


class Visualization:
    """
    Clase para la visualización de datos bibliométricos, incluyendo
    nubes de palabras y gráficos de co-ocurrencia de palabras clave.
    """
    
    def __init__(self, output_dir='output'):
        """
        Inicializa la clase de visualización.
        
        Args:
            output_dir (str): Directorio donde se guardarán las visualizaciones.
        """
        self.output_dir = output_dir
        
        # Creamos el directorio si no existe
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Configuramos el estilo de matplotlib
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def generate_wordcloud(self, word_frequencies, title, filename, width=800, height=400, 
                           background_color='white', colormap='viridis', max_words=200):
        """
        Genera una nube de palabras a partir de frecuencias de palabras.
        
        Args:
            word_frequencies (dict): Diccionario con palabras y sus frecuencias.
            title (str): Título para la visualización.
            filename (str): Nombre del archivo para guardar la imagen.
            width (int): Ancho de la imagen.
            height (int): Alto de la imagen.
            background_color (str): Color de fondo.
            colormap (str): Mapa de colores para las palabras.
            max_words (int): Número máximo de palabras a mostrar.
            
        Returns:
            str: Ruta completa al archivo guardado.
        """
        # Validamos que haya palabras para visualizar
        if not word_frequencies:
            print(f"No hay palabras para generar la nube de palabras para: {title}")
            return None
        
        # Creamos la nube de palabras
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color=background_color,
            colormap=colormap,
            max_words=max_words,
            collocations=False,
            min_font_size=10
        ).generate_from_frequencies(word_frequencies)
        
        # Configuramos y mostramos la figura
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title(title, fontsize=16)
        plt.tight_layout(pad=0)
        
        # Guardamos la imagen
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Nube de palabras guardada en: {output_path}")
        return output_path
    
    def generate_category_wordclouds(self, category_frequencies, combined_frequencies=None):
        """
        Genera nubes de palabras para cada categoría y una combinada si se proporciona.
        
        Args:
            category_frequencies (dict): Diccionario con categorías y diccionarios de frecuencias.
            combined_frequencies (dict, optional): Diccionario con frecuencias combinadas.
            
        Returns:
            dict: Diccionario con rutas a las imágenes generadas.
        """
        generated_paths = {}
        
        # Generamos nube de palabras para cada categoría
        for category, frequencies in category_frequencies.items():
            if frequencies:
                title = f"Frecuencia de términos - Categoría: {category}"
                filename = f"wordcloud_{category.lower().replace(' ', '_')}"
                path = self.generate_wordcloud(
                    frequencies, 
                    title, 
                    filename,
                    colormap='plasma'
                )
                generated_paths[category] = path
        
        # Si se proporcionan frecuencias combinadas, generamos una nube global
        if combined_frequencies:
            title = "Frecuencia global de términos - Todas las categorías"
            filename = "wordcloud_all_categories"
            path = self.generate_wordcloud(
                combined_frequencies, 
                title, 
                filename,
                width=1000,
                height=600,
                colormap='viridis',
                max_words=300
            )
            generated_paths['all'] = path
            
        return generated_paths
    
    def generate_co_word_network(self, co_occurrence_matrix, word_labels, 
                                title="Red de co-ocurrencia de palabras clave", 
                                filename="co_word_network", 
                                min_edge_weight=2,
                                node_size_factor=500,
                                category_labels=None):
        """
        Genera una visualización de red de co-ocurrencia de palabras clave.
        
        Args:
            co_occurrence_matrix (numpy.ndarray): Matriz de co-ocurrencia de palabras.
            word_labels (list): Lista de etiquetas de palabras correspondientes a la matriz.
            title (str): Título de la visualización.
            filename (str): Nombre del archivo para guardar la imagen.
            min_edge_weight (int): Peso mínimo de arista para mostrar.
            node_size_factor (int): Factor para el tamaño de los nodos.
            category_labels (dict, optional): Mapeo de palabras a categorías para colorear nodos.
            
        Returns:
            str: Ruta completa al archivo guardado.
        """
        # Validamos que haya datos para visualizar
        if len(word_labels) == 0 or co_occurrence_matrix.size == 0:
            print("No hay datos suficientes para generar la red de co-ocurrencia")
            return None
        
        # Creamos un grafo no dirigido
        G = nx.Graph()
        
        # Añadimos los nodos con sus pesos y categorías
        for i, word in enumerate(word_labels):
            # Contamos ocurrencias totales para determinar tamaño del nodo
            node_weight = sum(co_occurrence_matrix[i]) 
            
            # Si tenemos información de categoría, la incluimos
            if category_labels and word in category_labels:
                G.add_node(word, weight=node_weight, category=category_labels[word])
            else:
                G.add_node(word, weight=node_weight)
        
        # Añadimos las aristas (co-ocurrencias)
        rows, cols = co_occurrence_matrix.shape
        for i in range(rows):
            for j in range(i+1, cols):  # Solo la mitad superior para evitar duplicados
                weight = co_occurrence_matrix[i, j]
                if weight >= min_edge_weight:
                    G.add_edge(word_labels[i], word_labels[j], weight=weight)
        
        # Solo visualizamos si hay nodos y conexiones
        if len(G.nodes) == 0 or len(G.edges) == 0:
            print("No hay suficientes conexiones para visualizar la red")
            return None
        
        # Configuramos la figura
        plt.figure(figsize=(16, 12))
        
        # Calculamos el layout usando el algoritmo spring
        pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)
        
        # Obtenemos pesos de nodos y aristas para visualización
        node_sizes = [G.nodes[node].get('weight', 1) * node_size_factor for node in G.nodes()]
        edge_weights = [G.edges[edge].get('weight', 1) * 0.5 for edge in G.edges()]
        
        # Definimos colores para categorías si están disponibles
        if category_labels:
            # Obtenemos todas las categorías únicas
            categories = set(nx.get_node_attributes(G, 'category').values())
            
            # Creamos un mapa de colores
            colormap = plt.cm.get_cmap('tab20', len(categories))
            color_dict = {category: colormap(i) for i, category in enumerate(categories)}
            
            # Asignamos colores a nodos
            node_colors = [color_dict.get(G.nodes[node].get('category', 'Unknown'), 'gray') for node in G.nodes()]
            
            # Dibujamos el grafo
            nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8)
            
            # Añadimos leyenda para categorías
            handles = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=color_dict[cat], markersize=10, 
                                 label=cat) for cat in categories]
            plt.legend(handles=handles, title="Categorías", loc='upper left', 
                      bbox_to_anchor=(1, 1), fontsize=10)
        else:
            # Sin categorías, usamos un solo color
            nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.8)
        
        # Dibujamos aristas con escala de color según peso
        edges = nx.draw_networkx_edges(G, pos, width=edge_weights, 
                                      edge_color=[G.edges[edge].get('weight', 1) for edge in G.edges()],
                                      edge_cmap=plt.cm.Blues, alpha=0.7)
        
        # Dibujamos etiquetas solo para nodos con peso alto
        node_threshold = np.percentile([G.nodes[node].get('weight', 1) for node in G.nodes()], 75)
        node_labels = {node: node for node in G.nodes() if G.nodes[node].get('weight', 1) >= node_threshold}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_weight='bold')
        
        # Configuración final de la figura
        plt.title(title, fontsize=16)
        plt.axis('off')  # Oculta los ejes
        plt.tight_layout()
        
        # Guardamos la imagen
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Red de co-ocurrencia guardada en: {output_path}")
        return output_path
    
    def plot_category_frequencies(self, category_frequencies, 
                                 title="Frecuencia de términos por categoría", 
                                 filename="category_frequencies", 
                                 top_n=15):
        """
        Genera un gráfico de barras para mostrar las frecuencias de palabras por categoría.
        
        Args:
            category_frequencies (dict): Diccionario con categorías y frecuencias.
            title (str): Título del gráfico.
            filename (str): Nombre del archivo para guardar la imagen.
            top_n (int): Número máximo de términos a mostrar por categoría.
            
        Returns:
            str: Ruta completa al archivo guardado.
        """
        # Determinamos el número de categorías
        num_categories = len(category_frequencies)
        
        if num_categories == 0:
            print("No hay categorías para visualizar")
            return None
        
        # Configuramos el tamaño de la figura según el número de categorías
        fig, axes = plt.subplots(num_categories, 1, figsize=(12, 5 * num_categories))
        
        # Si solo hay una categoría, axes no será un array
        if num_categories == 1:
            axes = [axes]
        
        # Generamos un gráfico por categoría
        for i, (category, frequencies) in enumerate(category_frequencies.items()):
            # Tomamos las top_n palabras con más frecuencia
            top_words = Counter(frequencies).most_common(top_n)
            
            if not top_words:
                axes[i].text(0.5, 0.5, f"No hay datos para la categoría: {category}", 
                           horizontalalignment='center', verticalalignment='center',
                           fontsize=14)
                axes[i].set_title(f"Categoría: {category}")
                continue
            
            # Preparamos datos para el gráfico
            words, counts = zip(*top_words)
            
            # Creamos un colormap personalizado
            colors = plt.cm.viridis(np.linspace(0, 0.8, len(words)))
            
            # Invertimos para que la palabra más frecuente esté arriba
            axes[i].barh(words[::-1], counts[::-1], color=colors[::-1], alpha=0.7)
            axes[i].set_title(f"Categoría: {category}", fontsize=14)
            axes[i].set_xlabel("Frecuencia", fontsize=12)
            
            # Ajustamos etiquetas y márgenes
            axes[i].tick_params(axis='y', labelsize=10)
            
            # Añadimos etiquetas con los valores
            for j, value in enumerate(counts[::-1]):
                axes[i].text(value + 0.5, j, str(value), va='center')
            
            # Ajustamos límites para mejorar visualización
            max_value = max(counts)
            axes[i].set_xlim(0, max_value * 1.15)
            
        plt.tight_layout(pad=3.0)
        plt.suptitle(title, fontsize=16, y=1.02)
        
        # Guardamos la imagen
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Gráfico de frecuencias por categoría guardado en: {output_path}")
        return output_path
    
    def heatmap_word_frequency(self, word_freq_by_year, title="Evolución de términos por año", 
                              filename="word_freq_heatmap", top_n=20):
        """
        Genera un mapa de calor para visualizar la evolución de frecuencias de palabras por año.
        
        Args:
            word_freq_by_year (dict): Diccionario con años como claves y frecuencias de palabras como valores.
            title (str): Título del gráfico.
            filename (str): Nombre del archivo para guardar la imagen.
            top_n (int): Número máximo de palabras a mostrar.
            
        Returns:
            str: Ruta completa al archivo guardado.
        """
        if not word_freq_by_year:
            print("No hay datos para generar el mapa de calor")
            return None
        
        # Obtenemos las palabras más frecuentes en total
        all_words = Counter()
        for year_freq in word_freq_by_year.values():
            all_words.update(year_freq)
        
        top_words = [word for word, _ in all_words.most_common(top_n)]
        years = sorted(word_freq_by_year.keys())
        
        # Creamos la matriz de datos
        data = np.zeros((len(top_words), len(years)))
        
        for i, word in enumerate(top_words):
            for j, year in enumerate(years):
                data[i, j] = word_freq_by_year[year].get(word, 0)
        
        # Creamos la figura
        plt.figure(figsize=(14, 10))
        
        # Generamos el mapa de calor
        sns.heatmap(data, annot=True, fmt="d", cmap="YlGnBu", 
                   xticklabels=years, yticklabels=top_words)
        
        plt.title(title, fontsize=16)
        plt.xlabel("Año", fontsize=14)
        plt.ylabel("Término", fontsize=14)
        plt.tight_layout()
        
        # Guardamos la imagen
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Mapa de calor guardado en: {output_path}")
        return output_path