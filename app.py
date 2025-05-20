from flask import Flask, render_template
import os
from export_images import exportar_imagenes  # Importa tu método desde el otro archivo

# Copiar imágenes al iniciar
ORIGEN = 'resources/results/visualizations'
DESTINO = 'static/visualizations'
exportar_imagenes(ORIGEN, DESTINO)

app = Flask(__name__)

@app.route('/')
def index():
    base_path = DESTINO  # usamos la misma ruta
    categories = {}

    for category in os.listdir(base_path):
        category_path = os.path.join(base_path, category)
        if os.path.isdir(category_path):
            images = [f'{category}/{img}' for img in os.listdir(category_path) if img.endswith('.png')]
            categories[category] = images
        elif category.endswith('.png'):
            categories.setdefault('others', []).append(category)

    return render_template('index.html', categories=categories)

if __name__ == '__main__':
    app.run(debug=True)
