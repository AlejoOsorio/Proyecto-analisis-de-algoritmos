import os
import rispy


def __ris_to_dict(filepath):
    dict = {}
    if not os.path.exists(filepath):
        return dict

    articles = read_ris_file(filepath)
    for article in articles:
        identifier = article.get("doi", None) or article.get("urls", None)
        dict[identifier] = article

    return dict


def read_ris_file(filepath):
    with open(filepath, "r", encoding="utf-8") as bibliography_file:
        entries = rispy.load(bibliography_file)
        return entries


def clean_ris_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar espacios no separables por espacios normales
    content = content.replace('\xa0', ' ')

    # Guardar el archivo limpio
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def merge_ris_file(path_folder):
    unique_file_path = os.getenv("UNIQUE_FILE_PATH")
    duplicate_file_path = os.getenv("DUPLICATE_FILE_PATH")

    uniques = __ris_to_dict(unique_file_path)
    duplicates = __ris_to_dict(duplicate_file_path)

    files = [file for file in os.listdir(path_folder) if file.endswith(".ris")]
    for file in files:
        articles = read_ris_file(os.path.join(path_folder, file))

        for article in articles:
            identifier = article.get("doi", None) or article.get("UR", None)

            if identifier:
                if identifier in uniques:
                    if identifier not in duplicates:
                        duplicates[identifier] = article
                else:
                    uniques[identifier] = article
            else:
                uniques[f"no_identifier_{len(uniques)}"] = article

        if uniques:
            with open(unique_file_path, 'w', encoding="utf-8") as unique_file:
                rispy.dump(list(uniques.values()), unique_file)
            print("Se agregaron los elementos unicos")
        else:
            print("No se encontraron elementos repetidos")

        if duplicates:
            with open(duplicate_file_path, 'w', encoding="utf-8") as duplicate_file:
                rispy.dump(list(duplicates.values()), duplicate_file)
            print("Se agregaron los elementos reptidos")
        else:
            print("No se encontraron elementos repetidos")

        # Se elimina el archivo despues de unificarlo
        # os.remove(os.path.join(path_folder, file))
