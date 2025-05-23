# %%
import requests
import zipfile
import io
from pathlib import Path

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement : {e}")
        return None

def list_zip_contents(zip_content):
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        print("Contenu de l'archive ZIP :")
        for file_name in z.namelist():
            print(file_name)

def extract_tasks_json(zip_content):
    possible_paths = [
        "converters/tasks.json",
        "zenodo/converters/tasks.json"
    ]

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "extracted_data/converters/tasks.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        for path in possible_paths:
            if path in z.namelist():
                with z.open(path) as f:
                    with open(output_path, "wb") as out_f:
                        out_f.write(f.read())
                print(f"Le fichier {path} a été extrait vers {output_path}")
                return
        print("Aucun fichier tasks.json trouvé aux emplacements attendus.")

if __name__ == "__main__":
    url = "https://zenodo.org/record/10782465/files/plantnet_swe.zip"
    zip_content = fetch_data(url)

    if zip_content:
        list_zip_contents(zip_content)  
        extract_tasks_json(zip_content)

# %%
