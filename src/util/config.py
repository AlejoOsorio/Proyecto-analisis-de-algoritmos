import os
from pathlib import Path

# Configuración base de paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Configuración de descargas por scraper
DOWNLOAD_PATHS = {
    "ieee": DATA_DIR / "ieee",
    "sage": DATA_DIR / "sage", 
    "science": DATA_DIR / "science",
    "unified": DATA_DIR / "sample.ris"
}

# Asegurar que los directorios existen
for path in DOWNLOAD_PATHS.values():
    if not path.suffix:  # Es un directorio
        path.mkdir(parents=True, exist_ok=True)