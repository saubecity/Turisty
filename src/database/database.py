from pathlib import Path
import shutil


BASE_DIR = Path(__file__).resolve().parent
STORAGE_PATH = BASE_DIR / ".turisty"

def remove():
    shutil.rmtree(path=STORAGE_PATH)
