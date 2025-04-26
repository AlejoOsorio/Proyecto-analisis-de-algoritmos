# util/categories.py

class Categories:
    """
    Clase para manejar las categorías y sus variables (términos) para el análisis bibliométrico.
    """
    
    def __init__(self):
        """
        Inicializa la clase de categorías con la estructura predefinida
        y el mapeo de sinónimos.
        """
        self.categories = {
            "Habilidades": [
                "Abstraction",
                "Algorithm",
                "Algorithmic thinking",
                "Coding",
                "Collaboration",
                "Cooperation",
                "Creativity",
                "Critical thinking",
                "Debug",
                "Decomposition",
                "Evaluation",
                "Generalization",
                "Logic",
                "Logical thinking",
                "Modularity",
                "Patterns recognition",
                "Problem solving",
                "Programming",
            ],
            "Conceptos Computacionales": [
                "Conditionals",
                "Control structures",
                "Directions",
                "Events",
                "Functions",
                "Loops",
                "Modular structure",
                "Parallelism",
                "Sequences",
                "Software/hardware",
                "Variables",
            ],
            "Actitudes": [
                "Emotional",
                "Engagement",
                "Motivation",
                "Perceptions",
                "Persistence",
                "Self-efficacy",
                "Self-perceived",
            ],
            "Propiedades psicométricas": [
                "Classical Test Theory - CTT",
                "Confirmatory Factor Analysis - CFA",
                "Exploratory Factor Analysis - EFA",
                "Item Response Theory (IRT) - IRT",
                "Reliability",
                "Structural Equation Model - SEM",
                "Validity",
            ],
            "Herramienta de evaluación": [
                "Beginners Computational Thinking test - BCTt",
                "Coding Attitudes Survey - ESCAS",
                "Collaborative Computing Observation Instrument",
                "Competent Computational Thinking test - cCTt",
                "Computational thinking skills test - CTST",
                "Computational concepts",
                "Computational Thinking Assessment for Chinese Elementary Students - CTA-CES",
                "Computational Thinking Challenge - CTC",
                "Computational Thinking Levels Scale - CTLS",
                "Computational Thinking Scale - CTS",
                "Computational Thinking Skill Levels Scale - CTS",
                "Computational Thinking Test - CTt",
                "Computational Thinking Test",
                "Computational Thinking Test for Elementary School Students",
                "Computational Thinking Test for Lower Primary - CTtLP",
                "Computational thinking-skill tasks on numbers and arithmetic",
                "Computerized Adaptive Programming Concepts Test - CAPCT",
                "CT Scale - CTS",
                "Elementary Student Coding Attitudes Survey - ESCAS",
                "General self-efficacy scale",
                "ICT competency test",
                "Instrument of computational identity",
                "KBIT fluid intelligence subtest",
                "Mastery of computational concepts Test and an Algorithmic Test",
                "Multidimensional 21st Century Skills Scale",
                "Self-efficacy scale",
                "STEM learning attitude scale",
                "The computational thinking scale",
            ],
            "Diseño de investigación": [
                "No experimental",
                "Experimental",
                "Longitudinal research",
                "Mixed methods",
                "Post-test",
                "Pre-test",
                "Quasi-experiments",
            ],
            "Nivel de escolaridad": [
                "Upper elementary education - Upper elementary school",
                "Primary school - Primary education - Elementary school",
                "Early childhood education – Kindergarten - Preschool",
                "Secondary school - Secondary education",
                "high school - higher education",
                "University – College",
            ],
            "Medio": [
                "Block programming",
                "Mobile application",
                "Pair programming",
                "Plugged activities",
                "Programming",
                "Robotics",
                "Spreadsheet",
                "STEM",
                "Unplugged activities",
            ],
            "Estrategia": [
                "Construct-by-self mind mapping",
                "Construct-on-scaffold mind mapping",
                "Design-based learning",
                "Evidence-centred design approach",
                "Gamification",
                "Reverse engineering pedagogy",
                "Technology-enhanced learning",
                "Collaborative learning",
                "Cooperative learning",
                "Flipped classroom",
                "Game-based learning",
                "Inquiry-based learning",
                "Personalized learning",
                "Problem-based learning",
                "Project-based learning",
                "Universal design for learning",
            ],
            "Herramienta": [
                "Alice",
                "Arduino",
                "Scratch",
                "ScratchJr",
                "Blockly Games",
                "Code.org",
                "Codecombat",
                "CSUnplugged",
                "Robot Turtles",
                "Hello Ruby",
                "Kodable",
                "LightbotJr",
                "KIBO robots",
                "BEE BOT",
                "CUBETTO",
                "Minecraft",
                "Agent Sheets",
                "Mimo",
                "Py– Learn",
                "SpaceChem",
            ]
        }
        
        # Creamos un mapa de sinónimos para normalizar términos
        self.synonyms_map = self._build_synonyms_map()
        
        # Creamos un mapa de términos en minúsculas para búsqueda insensible a mayúsculas/minúsculas
        self.lowercase_terms = self._build_lowercase_terms_map()
    
    def _build_synonyms_map(self):
        """
        Construye un mapa de sinónimos a partir de los términos que contienen guiones.
        Cada parte separada por guión se considera un sinónimo del término principal.
        
        Returns:
            dict: Mapa de sinónimos.
        """
        synonyms = {}
        
        for category, terms in self.categories.items():
            for term in terms:
                # Si el término contiene un guión, consideramos sinónimos
                if " - " in term:
                    parts = [part.strip() for part in term.split(" - ")]
                    main_term = parts[0]  # El primero es el término principal
                    
                    # Registramos cada sinónimo
                    for synonym in parts[1:]:
                        synonyms[synonym.lower()] = main_term
                        
                # Casos especiales de sinónimos
                if "thinking" in term.lower():
                    base = term.lower().replace("thinking", "").strip()
                    if base:
                        synonyms[base] = term
                
        # Agregamos algunos sinónimos comunes adicionales
        additional_synonyms = {
            "abstraction": "Abstraction",
            "algorithm": "Algorithm",
            "algorithms": "Algorithm",
            "coding": "Coding",
            "code": "Coding",
            "programming": "Programming",
            "program": "Programming",
            "decompose": "Decomposition",
            "debug": "Debug",
            "debugging": "Debug",
            "problem-solving": "Problem solving",
            "pattern recognition": "Patterns recognition",
            "patterns": "Patterns recognition",
            "elementary school": "Primary school - Primary education - Elementary school",
            "primary education": "Primary school - Primary education - Elementary school",
            "kindergarten": "Early childhood education – Kindergarten - Preschool",
            "preschool": "Early childhood education – Kindergarten - Preschool",
            "secondary education": "Secondary school - Secondary education",
            "high school": "high school - higher education",
            "higher education": "high school - higher education",
            "university": "University – College",
            "college": "University – College",
            "robot": "Robotics",
            "unplugged": "Unplugged activities",
            "stem": "STEM"
        }
        
        synonyms.update(additional_synonyms)
        return synonyms
    
    def _build_lowercase_terms_map(self):
        """
        Construye un mapa de términos en minúsculas para hacer búsquedas 
        insensibles a mayúsculas/minúsculas.
        
        Returns:
            dict: Mapa de términos en minúsculas a términos originales.
        """
        lowercase_map = {}
        
        for category, terms in self.categories.items():
            for term in terms:
                lowercase_map[term.lower()] = term
                
                # Si el término contiene guiones, también mapeamos las partes
                if " - " in term:
                    parts = [part.strip() for part in term.split(" - ")]
                    for part in parts:
                        lowercase_map[part.lower()] = term
        
        return lowercase_map
    
    def get_all_categories(self):
        """
        Devuelve todas las categorías y sus términos.
        
        Returns:
            dict: Diccionario con categorías y términos.
        """
        return self.categories
    
    def get_category_terms(self, category):
        """
        Devuelve los términos de una categoría específica.
        
        Args:
            category (str): Nombre de la categoría.
            
        Returns:
            list: Lista de términos de la categoría o lista vacía si no existe.
        """
        return self.categories.get(category, [])
    
    def get_all_terms(self):
        """
        Devuelve todos los términos de todas las categorías.
        
        Returns:
            list: Lista con todos los términos.
        """
        all_terms = []
        for terms in self.categories.values():
            all_terms.extend(terms)
        return all_terms
    
    def normalize_term(self, term):
        """
        Normaliza un término según el mapa de sinónimos.
        
        Args:
            term (str): Término a normalizar.
            
        Returns:
            str: Término normalizado o el original si no hay sinónimo.
        """
        term_lower = term.lower().strip()
        
        # Primero buscamos en el mapa de sinónimos
        if term_lower in self.synonyms_map:
            return self.synonyms_map[term_lower]
        
        # Luego en el mapa de términos en minúsculas
        if term_lower in self.lowercase_terms:
            return self.lowercase_terms[term_lower]
        
        return term
    
    def get_term_category(self, term):
        """
        Devuelve la categoría a la que pertenece un término.
        
        Args:
            term (str): Término a buscar.
            
        Returns:
            str: Nombre de la categoría o None si no se encuentra.
        """
        normalized_term = self.normalize_term(term)
        
        for category, terms in self.categories.items():
            if normalized_term in terms:
                return category
            
            # Comprobamos también en minúsculas
            terms_lower = [t.lower() for t in terms]
            if normalized_term.lower() in terms_lower:
                return category
        
        return None