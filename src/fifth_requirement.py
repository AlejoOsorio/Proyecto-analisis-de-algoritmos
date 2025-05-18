import matplotlib.pyplot as plt
import re

import rispy
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet
from scipy.spatial.distance import pdist

nltk.download('stopwords')

class HierarchicalClustering:
    def __init__(self):
        self.abstracts = []
        self.X = None
        self.categories = []
        self.true_labels = []
        self.labels=[]

    def load_data(self, ris_path):
        with open(ris_path, 'r', encoding='utf-8') as f:
            entries = rispy.load(f)

        abstracts = []
        keywords = []

        for entry in entries:
            if 'abstract' in entry and 'keywords' in entry:
                abstracts.append(entry['abstract'])
                keywords.append(', '.join(entry['keywords']) if isinstance(entry['keywords'], list) else entry['keywords'])

        self.abstracts = [self.clean_text(abs) for abs in abstracts][:50]
        self.categories = keywords[:50]

        self.labels = [' '.join(cat.split()[:3]) for cat in self.categories]
        unique_categories = list(set(self.categories))
        self.true_labels = [unique_categories.index(cat) for cat in self.categories]
        print(f"[INFO] {len(self.abstracts)} abstracts y categorías cargadas desde .ris")


    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()
        clean_words = [word for word in words if word not in stopwords.words('english')]
        return ' '.join(clean_words)

    def vectorize_texts(self):
        vectorizer = TfidfVectorizer()
        self.X = vectorizer.fit_transform(self.abstracts).toarray()
        print("[INFO] Vectorización TF-IDF completada.")

    def apply_clustering(self, method):
        if self.X is None:
            raise ValueError("Debes vectorizar los textos antes de aplicar clustering.")
        linkage_matrix = linkage(self.X, method=method)
        return linkage_matrix

    def compare_methods(self):
        methods = ['ward', 'average']
        results = {}

        for method in methods:
            print(f"\n[INFO] Aplicando clustering con método: {method}")
            linkage_matrix = self.apply_clustering(method)
            self.plot_dendrogram(linkage_matrix, method)
            c = self.evaluate_quality(linkage_matrix)
            print(f"[RESULTADO] Coeficiente cophenético para '{method}': {c:.4f}")
            results[method] = c

            self.evaluate_clusterings_categories(method)

        best = max(results, key=results.get)
        print(f"\nEl método con mejor coeficiente cophenético es: '{best}' con {results[best]:.4f}")

    def plot_dendrogram(self, linkage_matrix, title):
        plt.figure(figsize=(10, 7))
        dendrogram(linkage_matrix, labels=self.labels)
        plt.title(f'Dendrograma - Método {title}')
        plt.xlabel('Abstracts')
        plt.ylabel('Distancia')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

    def evaluate_quality(self, linkage_matrix):
        c, _ = cophenet(linkage_matrix, pdist(self.X))
        return c

    def evaluate_clusterings_categories(self, method):
        clustering = AgglomerativeClustering(n_clusters=len(set(self.true_labels)), linkage=method)
        labels_pred = clustering.fit_predict(self.X)

        ari = adjusted_rand_score(self.true_labels, labels_pred)
        nmi = normalized_mutual_info_score(self.true_labels, labels_pred)

        print(f"[EVALUACIÓN CATEGORÍAS] ARI: {ari:.4f}, NMI: {nmi:.4f} usando método '{method}'")

