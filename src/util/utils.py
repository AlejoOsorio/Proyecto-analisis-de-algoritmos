import os


def validate_path(path):
    "Revisa si la ruta no existe, de ser así la crea"
    if not os.path.exists(path):
        os.makedirs(path)
        print(f'La ruta {path} ha sido creada.')