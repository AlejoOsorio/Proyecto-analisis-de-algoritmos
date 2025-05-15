# model/content_analyzer.py
import os
import re
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
import rispy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.util import ngrams
import math
# Descargar recursos de NLTK si no están disponibles
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
class ContentAnalyzer:
    """
    Clase para analizar el contenido de los archivos RIS y extraer información
    bibliométrica, especialmente centrada en el análisis de abstracts para el
    requerimiento 3.
    """
    
    def __init__(self, categories_handler):
        """
        Inicializa el analizador de contenido.
        
        Args:
            categories_handler: Instancia de la clase Categories para manejar categorías y sinónimos.
        """
        self.categories = categories_handler
        
        # Configuramos el preprocesamiento de texto
        self.setup_text_preprocessing()
        
        # Variables para almacenar resultados
        self.all_abstracts = []
        self.entries_with_abstracts = []
        self.category_term_frequencies = defaultdict(Counter)
        self.combined_term_frequencies = Counter()
        self.co_occurrence_matrix = None
        self.co_occurrence_terms = []
        self.term_by_category = {}  # Mapeo de términos a categorías
        
    def setup_text_preprocessing(self):
        """Configura herramientas y recursos para el preprocesamiento de texto."""
        # Stopwords en inglés y español
        self.stopwords = set(stopwords.words('english') + stopwords.words('spanish'))
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        
        # Añadimos stopwords específicas para el dominio
        additional_stopwords = {
            'computational', 'thinking', 'study', 'research', 'paper', 'article',
            'results', 'method', 'approach', 'analysis', 'using', 'based',
            'we', 'our', 'us', 'they', 'their', 'them', 'he', 'she', 'it',
            'this', 'that', 'these', 'those', 'et', 'al', 'doi', 'isbn',
            'vol', 'volume', 'issue', 'journal', 'conference', 'proceeding',
            'university', 'author', 'authors', 'abstract', 'introduction',
            'conclusion', 'discussion', 'figure', 'table', 'section', 'pp',
            'page', 'pages', 'year', 'publisher', 'published', 'publication',
            'review', 'education', 'educational', 'student', 'students', 'used',
            'also', 'can', 'may', 'one', 'two', 'three', 'first', 'second', 'third'
        }
        self.stopwords.update(additional_stopwords)
    
    def preprocess_text(self, text):
        """
        Preprocesa el texto para el análisis:
        - Convierte a minúsculas
        - Tokeniza
        - Elimina stopwords y caracteres no alfanuméricos
        - Lematiza
        
        Args:
            text: Texto a preprocesar
            
        Returns:
            Lista de tokens procesados
        """
        if not text or not isinstance(text, str):
            return []
        
        # Convertir a minúsculas y tokenizar
        tokens = word_tokenize(text.lower())
        
        # Filtrar tokens: solo alfanuméricos y no stopwords
        tokens = [token for token in tokens if token.isalpha() and token not in self.stopwords and len(token) > 2]
        
        # Lematizar
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens
    
    def extract_ngrams(self, tokens, n=2):
        """
        Extrae n-gramas de una lista de tokens.
        
        Args:
            tokens: Lista de tokens
            n: Tamaño de n-gramas a extraer
            
        Returns:
            Lista de n-gramas
        """
        return list(ngrams(tokens, n))
    
    def load_and_analyze_entries(self, entries):
        """
        Carga y analiza las entradas bibliográficas, extrayendo los abstracts
        y calculando frecuencias de términos por categoría.
        
        Args:
            entries: Lista de entradas bibliográficas
            
        Returns:
            tuple: (category_term_frequencies, combined_term_frequencies)
        """
        print(f"Analizando {len(entries)} entradas bibliográficas...")
        
        # Reiniciamos variables de resultados
        self.all_abstracts = []
        self.entries_with_abstracts = []
        self.category_term_frequencies = defaultdict(Counter)
        self.combined_term_frequencies = Counter()
        self.term_by_category = {}
        
        # Iteramos por cada entrada
        for entry in entries:
            # Extraemos el abstract
            abstract = entry.get('abstract', '')
            
            if abstract:
                self.all_abstracts.append(abstract)
                self.entries_with_abstracts.append(entry)
                
                # Preprocesamos el texto
                tokens = self.preprocess_text(abstract)
                
                # Analizamos los tokens por categoría
                self.analyze_tokens_by_category(tokens)
        
        print(f"Análisis completado. Se encontraron {len(self.entries_with_abstracts)} entradas con abstract.")
        return self.category_term_frequencies, self.combined_term_frequencies
    
    def analyze_tokens_by_category(self, tokens):
        """
        Analiza los tokens buscando términos específicos de cada categoría.
        
        Args:
            tokens: Lista de tokens preprocesados del abstract
        """
        # Convertimos los tokens a un texto para buscar frases completas
        text = ' '.join(tokens)
        
        # Extraemos n-gramas para detectar términos compuestos
        bigrams = [' '.join(bg) for bg in self.extract_ngrams(tokens, 2)]
        trigrams = [' '.join(tg) for tg in self.extract_ngrams(tokens, 3)]
        fourgrams = [' '.join(fg) for fg in self.extract_ngrams(tokens, 4)]
        
        # Todos los n-gramas para buscar
        all_ngrams = tokens + bigrams + trigrams + fourgrams
        
        # Obtenemos todas las categorías y sus términos
        categories = self.categories.get_all_categories()
        
        # Para cada categoría, buscamos sus términos en el texto
        for category, terms in categories.items():
            # Contador para esta categoría
            category_counter = Counter()
            
            # Buscamos términos individuales
            for term in terms:
                # Normalizamos el término según el mapeo de sinónimos
                normalized_term = self.categories.normalize_term(term)
                term_lower = term.lower()
                
                # Buscamos el término en n-gramas
                if any(term_lower in ngram for ngram in all_ngrams):
                    category_counter[normalized_term] += 1
                    self.combined_term_frequencies[normalized_term] += 1
                    self.term_by_category[normalized_term] = category
                
                # También buscamos el término directamente en el texto (para capturar variantes)
                elif re.search(r'\b' + re.escape(term_lower) + r'\b', text, re.IGNORECASE):
                    category_counter[normalized_term] += 1
                    self.combined_term_frequencies[normalized_term] += 1
                    self.term_by_category[normalized_term] = category
            
            # Actualizamos las frecuencias de esta categoría
            if category_counter:
                self.category_term_frequencies[category].update(category_counter)
    
    def build_co_occurrence_matrix(self, min_frequency=2):
        """
        Construye una matriz de co-ocurrencia de términos.
        
        Args:
            min_frequency: Frecuencia mínima para incluir un término en la matriz
            
        Returns:
            tuple: (matriz de co-ocurrencia, lista de términos)
        """
        print("Construyendo matriz de co-ocurrencia de términos...")
        
        # Filtramos términos que aparecen con suficiente frecuencia
        frequent_terms = [term for term, freq in self.combined_term_frequencies.items() 
                         if freq >= min_frequency]
        
        # Ordenamos términos alfabéticamente para consistencia
        frequent_terms.sort()
        
        # Creamos la matriz de co-ocurrencia
        n = len(frequent_terms)
        co_matrix = np.zeros((n, n), dtype=int)
        
        # Iteramos sobre cada abstract
        for abstract in self.all_abstracts:
            # Preprocesamos el texto
            tokens = self.preprocess_text(abstract)
            text = ' '.join(tokens)
            
            # Verificamos qué términos aparecen en este abstract
            present_terms = []
            for term in frequent_terms:
                if re.search(r'\b' + re.escape(term.lower()) + r'\b', text, re.IGNORECASE):
                    present_terms.append(term)
            
            # Actualizamos la matriz para los términos presentes
            for i, term1 in enumerate(present_terms):
                idx1 = frequent_terms.index(term1)
                # La diagonal representa la frecuencia total
                co_matrix[idx1, idx1] += 1
                
                # Las co-ocurrencias
                for j, term2 in enumerate(present_terms[i+1:], i+1):
                    idx2 = frequent_terms.index(term2)
                    co_matrix[idx1, idx2] += 1
                    co_matrix[idx2, idx1] += 1  # Matriz simétrica
        
        self.co_occurrence_matrix = co_matrix
        self.co_occurrence_terms = frequent_terms
        
        print(f"Matriz de co-ocurrencia construida con {len(frequent_terms)} términos.")
        return co_matrix, frequent_terms
    
    def get_term_category_mapping(self):
        """
        Devuelve un mapeo de términos a categorías.
        
        Returns:
            dict: Mapeo de términos a sus categorías
        """
        return self.term_by_category
    
    def calculate_tf_idf(self):
        """
        Calcula los valores TF-IDF para cada término en los abstracts.
        
        Returns:
            dict: Términos con sus valores TF-IDF
        """
        print("Calculando valores TF-IDF...")
        
        # Número total de documentos
        num_docs = len(self.all_abstracts)
        
        if num_docs == 0:
            print("No hay abstracts para calcular TF-IDF")
            return {}
        
        # Contador de documentos por término
        doc_freq = Counter()
        
        # Procesamos cada abstract
        for abstract in self.all_abstracts:
            # Preprocesamos y obtenemos términos únicos
            tokens = self.preprocess_text(abstract)
            unique_terms = set(tokens)
            
            # Aumentamos contador de documentos por cada término presente
            for term in unique_terms:
                doc_freq[term] += 1
        
        # Calculamos TF-IDF para cada término
        tf_idf = {}
        for term, freq in self.combined_term_frequencies.items():
            # Si el término no aparece en doc_freq, asignamos un valor pequeño
            df = doc_freq.get(term, 1)
            # Calculamos el TF-IDF
            idf = math.log(num_docs / df)
            tf_idf[term] = freq * idf
        
        print(f"TF-IDF calculado para {len(tf_idf)} términos.")
        return tf_idf
    
    def analyze_trends_by_year(self):
        """
        Analiza las tendencias de términos por año.
        
        Returns:
            dict: Frecuencia de términos por año
        """
        print("Analizando tendencias por año...")
        
        # Agrupamos abstracts por año
        abstracts_by_year = defaultdict(list)
        
        for entry in self.entries_with_abstracts:
            # Obtenemos el año de publicación
            year = entry.get('year')
            if year and entry.get('abstract'):
                abstracts_by_year[year].append(entry.get('abstract'))
        
        # Calculamos frecuencias por año
        term_freq_by_year = {}
        
        for year, year_abstracts in abstracts_by_year.items():
            # Combinamos todos los abstracts del año
            combined_text = ' '.join(year_abstracts)
            tokens = self.preprocess_text(combined_text)
            
            # Contamos frecuencias para este año
            year_counter = Counter()
            
            # Buscamos términos de todas las categorías
            for category, terms in self.categories.get_all_categories().items():
                for term in terms:
                    # Normalizamos el término
                    normalized_term = self.categories.normalize_term(term)
                    term_lower = term.lower()
                    
                    # Contamos ocurrencias en el texto
                    count = sum(1 for token in tokens if token == term_lower)
                    if count > 0:
                        year_counter[normalized_term] += count
            
            term_freq_by_year[year] = year_counter
        
        print(f"Análisis de tendencias completado para {len(term_freq_by_year)} años.")
        return term_freq_by_year
    
    def get_entries_with_term(self, target_term):
        """
        Obtiene las entradas bibliográficas que contienen un término específico.
        
        Args:
            target_term: Término a buscar
            
        Returns:
            list: Entradas que contienen el término
        """
        # Normalizamos el término objetivo
        normalized_term = self.categories.normalize_term(target_term)
        term_lower = target_term.lower()
        
        # Lista para almacenar entradas coincidentes
        matching_entries = []
        
        # Buscamos en cada entrada
        for entry in self.entries_with_abstracts:
            abstract = entry.get('abstract', '')
            if abstract:
                # Preprocesamos el texto
                tokens = self.preprocess_text(abstract)
                text = ' '.join(tokens)
                
                # Verificamos si el término está presente
                if term_lower in tokens or re.search(r'\b' + re.escape(term_lower) + r'\b', text, re.IGNORECASE):
                    matching_entries.append(entry)
        
        return matching_entries
    
    def get_frequent_terms(self, top_n=30, min_freq=2):
        """
        Obtiene los términos más frecuentes en todas las categorías.
        
        Args:
            top_n: Número máximo de términos a devolver
            min_freq: Frecuencia mínima para incluir un término
            
        Returns:
            list: Lista de tuplas (término, frecuencia)
        """
        # Filtramos términos que aparecen con suficiente frecuencia
        frequent_terms = [(term, freq) for term, freq in self.combined_term_frequencies.items() 
                         if freq >= min_freq]
        
        # Ordenamos por frecuencia (descendente)
        frequent_terms.sort(key=lambda x: x[1], reverse=True)
        
        # Devolvemos los top_n términos
        return frequent_terms[:top_n]
    
    def get_category_frequencies(self):
        """
        Devuelve las frecuencias de términos por categoría.
        
        Returns:
            dict: Diccionario con categorías y sus frecuencias de términos
        """
        return dict(self.category_term_frequencies)
    
    def get_combined_frequencies(self):
        """
        Devuelve las frecuencias combinadas de todos los términos.
        
        Returns:
            Counter: Contador con las frecuencias combinadas
        """
        return self.combined_term_frequencies
    
    def get_co_occurrence_matrix(self):
        """
        Devuelve la matriz de co-ocurrencia y los términos asociados.
        
        Returns:
            tuple: (matriz de co-ocurrencia, lista de términos)
        """
        return self.co_occurrence_matrix, self.co_occurrence_terms
    
    def generate_summary_report(self):
        """
        Genera un informe resumido del análisis de contenido.
        
        Returns:
            dict: Resumen del análisis
        """
        # Total de entradas y abstracts
        total_entries = len(self.entries_with_abstracts)
        total_abstracts = len(self.all_abstracts)
        
        # Términos por categoría
        terms_by_category = {category: len(freqs) for category, freqs in self.category_term_frequencies.items()}
        
        # Términos más frecuentes (top 10)
        top_terms = self.get_frequent_terms(top_n=10)
        
        # Calculamos totales por categoría
        category_totals = {}
        for category, freqs in self.category_term_frequencies.items():
            category_totals[category] = sum(freqs.values())
        
        # Construimos el resumen
        summary = {
            "total_entries": total_entries,
            "total_abstracts": total_abstracts,
            "unique_terms": len(self.combined_term_frequencies),
            "terms_by_category": terms_by_category,
            "category_totals": category_totals,
            "top_terms": top_terms
        }
        
        return summary