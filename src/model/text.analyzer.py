import os
import re
import json
import rispy
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter, defaultdict
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Descargar recursos de NLTK necesarios
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class TextAnalyzer:
    def __init__(self, ris_file_path):
        """
        Inicializa el analizador de texto con la ruta al archivo RIS.
        
        Args:
            ris_file_path (str): Ruta al archivo RIS unificado.
        """
        self.ris_file_path = ris_file_path
        self.articles = self._load_articles()
        self.abstracts = self._extract_abstracts()
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        
        # Carga las categorías y variables
        self.categories = self._load_categories()
        # Diccionario para mapear sinónimos a términos principales
        self.synonyms_map = self._create_synonyms_map()
        
        # Resultados del análisis
        self.category_frequencies = {}
        self.word_co_occurrences = defaultdict(lambda: defaultdict(int))

    def _load_articles(self):
        """Carga los artículos desde el archivo RIS."""
        with open(self.ris_file_path, "r", encoding="utf-8") as bibliography_file:
            return rispy.load(bibliography_file)

    def _extract_abstracts(self):
        """Extrae los abstracts de los artículos."""
        abstracts = []
        for article in self.articles:
            # El campo para el abstract puede variar según el formato RIS
            abstract = article.get('abstract', article.get('AB', ''))
            if abstract:
                abstracts.append(abstract)
        return abstracts

    def _load_categories(self):
        """
        Carga las categorías y sus variables desde un archivo JSON.
        Si el archivo no existe, crea un diccionario con las categorías definidas.
        """
        # Verificar si existe un archivo de categorías
        categories_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'categories.json')
        
        if os.path.exists(categories_file):
            with open(categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Definir categorías y variables según el requerimiento
            return {
                "Habilidades": [
                    "Abstraction", "Algorithm", "Algorithmic thinking", "Coding", "Collaboration", 
                    "Cooperation", "Creativity", "Critical thinking", "Debug", "Decomposition", 
                    "Evaluation", "Generalization", "Logic", "Logical thinking", "Modularity", 
                    "Patterns recognition", "Problem solving", "Programming"
                ],
                "Conceptos Computacionales": [
                    "Conditionals", "Control structures", "Directions", "Events", "Funtions", 
                    "Loops", "Modular structure", "Parallelism", "Sequences", "Software/hardware", 
                    "Variables"
                ],
                "Actitudes": [
                    "Emotional", "Engagement", "Motivation", "Perceptions", "Persistence", 
                    "Self-efficacy", "Self-perceived"
                ],
                "Propiedades psicométricas": [
                    "Classical Test Theory - CTT", "Confirmatory Factor Analysis - CFA", 
                    "Exploratory Factor Analysis - EFA", "Item Response Theory (IRT) - IRT", 
                    "Reliability", "Structural Equation Model - SEM", "Validity"
                ],
                "Herramienta de evaluación": [
                    "Beginners Computational Thinking test - BCTt", "Coding Attitudes Survey - ESCAS", 
                    "Collaborative Computing Observation Instrument", "Competent Computational Thinking test - cCTt", 
                    "Computational thinking skills test - CTST", "Computational concepts", 
                    "Computational Thinking Assessment for Chinese Elementary Students - CTA-CES", 
                    "Computational Thinking Challenge - CTC", "Computational Thinking Levels Scale - CTLS", 
                    "Computational Thinking Scale - CTS", "Computational Thinking Skill Levels Scale - CTS", 
                    "Computational Thinking Test - CTt", "Computational Thinking Test", 
                    "Computational Thinking Test for Elementary School Students", 
                    "Computational Thinking Test for Lower Primary - CTtLP", 
                    "Computational thinking-skill tasks on numbers and arithmetic", 
                    "Computerized Adaptive Programming Concepts Test - CAPCT", "CT Scale - CTS", 
                    "Elementary Student Coding Attitudes Survey - ESCAS", "General self-efficacy scale", 
                    "ICT competency test", "Instrument of computational identity", "KBIT fluid intelligence subtest", 
                    "Mastery of computational concepts Test and an Algorithmic Test", 
                    "Multidimensional 21st Century Skills Scale", "Self-efficacy scale", 
                    "STEM learning attitude scale", "The computational thinking scale"
                ],
                "Diseño de investigación": [
                    "No experimental", "Experimental", "Longitudinal research", "Mixed methods", 
                    "Post-test", "Pre-test", "Quasi-experiments"
                ],
                "Nivel de escolaridad": [
                    "Upper elementary education - Upper elementary school", 
                    "Primary school - Primary education - Elementary school", 
                    "Early childhood education – Kindergarten -Preschool", 
                    "Secondary school - Secondary education", "high school - higher education", 
                    "University – College"
                ],
                "Medio": [
                    "Block programming", "Mobile application", "Pair programming", "Plugged activities", 
                    "Programming", "Robotics", "Spreadsheet", "STEM", "Unplugged activities"
                ],
                "Estrategia": [
                    "Construct-by-self mind mapping", "Construct-on-scaffold mind mapping", 
                    "Design-based learning", "Evidence-centred design approach", "Gamification", 
                    "Reverse engineering pedagogy", "Technology-enhanced learning", 
                    "Collaborative learning", "Cooperative learning", "Flipped classroom", 
                    "Game-based learning", "Inquiry-based learning", "Personalized learning", 
                    "Problem-based learning", "Project-based learning", "Universal design for learning"
                ],
                "Herramienta": [
                    "Alice", "Arduino", "Scratch", "ScratchJr", "Blockly Games", "Code.org", 
                    "Codecombat", "CSUnplugged", "Robot Turtles", "Hello Ruby", "Kodable", 
                    "LightbotJr", "KIBO robots", "BEE BOT", "CUBETTO", "Minecraft", "Agent Sheets", 
                    "Mimo", "Py– Learn", "SpaceChem"
                ]
            }

    def _create_synonyms_map(self):
        """
        Crea un diccionario que mapea sinónimos a términos principales.
        Por ejemplo, "Primary school", "Primary education", y "Elementary school" 
        se mapean todos a "Primary school".
        """
        synonyms_map = {}
        
        for category, terms in self.categories.items():
            for term in terms:
                # Si el término contiene guiones, podría tener sinónimos
                if " - " in term:
                    # Conservar el primer término como el principal
                    main_term = term.split(" - ")[0].strip()
                    # Agregar el término principal al mapa
                    synonyms_map[main_term.lower()] = main_term
                    continue
                
                # Tratar los casos con guiones como sinónimos
                if " – " in term:
                    parts = term.split(" – ")
                    main_term = parts[0].strip()
                    for part in parts:
                        part = part.strip()
                        synonyms_map[part.lower()] = main_term
                    continue
                
                # Manejar términos separados por guiones
                if " - " in term:
                    parts = term.split(" - ")
                    main_term = parts[0].strip()
                    for part in parts:
                        part = part.strip()
                        synonyms_map[part.lower()] = main_term
                    continue
                
                # Agregar el término normal
                synonyms_map[term.lower()] = term
        
        return synonyms_map

    def _preprocess_text(self, text):
        """
        Preprocesa el texto: tokeniza, convierte a minúsculas,
        elimina stopwords y aplica stemming/lemmatization.
        """
        # Convertir a minúsculas y tokenizar
        tokens = word_tokenize(text.lower())
        
        # Eliminar stopwords y tokens no alfabéticos
        tokens = [token for token in tokens if token.isalpha() and token not in self.stop_words]
        
        # Aplicar lemmatization para normalizar términos
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens

    def _count_term_frequency(self, category, terms, preprocessed_abstracts):
        """
        Cuenta la frecuencia de términos específicos en los abstracts.
        
        Args:
            category (str): Nombre de la categoría.
            terms (list): Lista de términos a buscar.
            preprocessed_abstracts (list): Lista de abstracts preprocesados.
            
        Returns:
            dict: Diccionario con las frecuencias de los términos.
        """
        term_freq = {term: 0 for term in terms}
        
        # Crear patrones regex para cada término (coincidencia exacta de palabra)
        term_patterns = {}
        for term in terms:
            # Escapar caracteres especiales y crear un patrón que busque la palabra completa
            escaped_term = re.escape(term.lower())
            term_patterns[term] = re.compile(r'\b' + escaped_term + r'\b')
        
        # Buscar términos en cada abstract
        for abstract in self.abstracts:
            abstract_lower = abstract.lower()
            
            for term, pattern in term_patterns.items():
                if pattern.search(abstract_lower):
                    term_freq[term] += 1
        
        return term_freq

    def analyze_frequency(self):
        """
        Analiza la frecuencia de términos en los abstracts por categoría.
        
        Returns:
            dict: Diccionario con las frecuencias por categoría.
        """
        # Preprocesar todos los abstracts
        preprocessed_abstracts = [self._preprocess_text(abstract) for abstract in self.abstracts]
        
        # Analizar frecuencias por categoría
        for category, terms in self.categories.items():
            self.category_frequencies[category] = self._count_term_frequency(
                category, terms, preprocessed_abstracts
            )
        
        return self.category_frequencies

    def analyze_co_occurrence(self):
        """
        Analiza la co-ocurrencia de términos en los abstracts.
        
        Returns:
            dict: Matriz de co-ocurrencia entre términos.
        """
        # Aplanar todas las categorías en una lista única de términos
        all_terms = []
        for terms in self.categories.values():
            all_terms.extend(terms)
        
        # Crear patrones regex para cada término
        term_patterns = {}
        for term in all_terms:
            # Escapar caracteres especiales y crear un patrón
            escaped_term = re.escape(term.lower())
            term_patterns[term] = re.compile(r'\b' + escaped_term + r'\b')
        
        # Analizar co-ocurrencia en cada abstract
        for abstract in self.abstracts:
            abstract_lower = abstract.lower()
            
            # Encontrar todos los términos presentes en este abstract
            present_terms = []
            for term, pattern in term_patterns.items():
                if pattern.search(abstract_lower):
                    present_terms.append(term)
            
            # Registrar co-ocurrencias
            for i, term1 in enumerate(present_terms):
                for term2 in present_terms[i+1:]:
                    self.word_co_occurrences[term1][term2] += 1
                    self.word_co_occurrences[term2][term1] += 1
        
        return self.word_co_occurrences

    def get_results_dataframe(self):
        """
        Convierte los resultados del análisis de frecuencia a un DataFrame de pandas.
        
        Returns:
            pandas.DataFrame: DataFrame con los resultados.
        """
        results = []
        
        for category, term_freq in self.category_frequencies.items():
            for term, freq in term_freq.items():
                results.append({
                    'Categoría': category,
                    'Término': term,
                    'Frecuencia': freq
                })
        
        return pd.DataFrame(results)

    def get_co_occurrence_dataframe(self):
        """
        Convierte la matriz de co-ocurrencia a un DataFrame de pandas.
        
        Returns:
            pandas.DataFrame: DataFrame con la matriz de co-ocurrencia.
        """
        results = []
        
        for term1, co_occurs in self.word_co_occurrences.items():
            for term2, freq in co_occurs.items():
                results.append({
                    'Término1': term1,
                    'Término2': term2,
                    'Co-ocurrencias': freq
                })
        
        return pd.DataFrame(results)

    def save_results(self, output_dir):
        """
        Guarda los resultados del análisis en archivos CSV.
        
        Args:
            output_dir (str): Directorio donde se guardarán los resultados.
        """
        # Crear directorio si no existe
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Guardar frecuencias por categoría
        freq_df = self.get_results_dataframe()
        freq_df.to_csv(os.path.join(output_dir, 'term_frequencies.csv'), index=False)
        
        # Guardar co-ocurrencias
        co_occur_df = self.get_co_occurrence_dataframe()
        co_occur_df.to_csv(os.path.join(output_dir, 'term_co_occurrences.csv'), index=False)
        
        # Guardar como JSON para posible uso en visualizaciones
        with open(os.path.join(output_dir, 'frequencies.json'), 'w', encoding='utf-8') as f:
            json.dump(self.category_frequencies, f, ensure_ascii=False, indent=2)
        
        # Convertir defaultdict a dict normal para JSON
        co_occurrences_dict = {
            k: dict(v) for k, v in self.word_co_occurrences.items()
        }
        
        with open(os.path.join(output_dir, 'co_occurrences.json'), 'w', encoding='utf-8') as f:
            json.dump(co_occurrences_dict, f, ensure_ascii=False, indent=2)