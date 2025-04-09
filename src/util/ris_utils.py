import os
import rispy


def read_ris_file(filepath):
    with open(filepath, "r", encoding="utf-8") as bibliography_file:
        entries = rispy.load(bibliography_file)
        return entries


def merge_ris_file(path_folder):
    unique_file_path = os.getenv("UNIQUE_FILE_PATH")
    duplicate_file_path = os.getenv("DUPLICATE_FILE_PATH")

    uniques = {}
    duplicates = {}

    files = [file for file in os.listdir(path_folder) if file.endswith(".ris")]
    for file in files:
        articles = read_ris_file(os.path.join(path_folder, file))

        for article in articles:
            identifier = article.get("doi", None) or article.get("UR", None)

            if identifier:
                if identifier in uniques:
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
