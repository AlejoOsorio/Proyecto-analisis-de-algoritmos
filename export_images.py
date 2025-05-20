import os
import shutil

def exportar_imagenes(origen, destino):
    os.makedirs(destino, exist_ok=True)

    for root, dirs, files in os.walk(origen):
        for file in files:
            if file.endswith('.png'):
                ruta_origen = os.path.join(root, file)
                subcarpeta = os.path.relpath(root, origen)
                destino_final = os.path.join(destino, subcarpeta)

                os.makedirs(destino_final, exist_ok=True)
                shutil.copy2(ruta_origen, os.path.join(destino_final, file))
                print(f"Imagen copiada: {file} -> {destino_final}")
