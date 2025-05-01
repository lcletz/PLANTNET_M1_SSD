# %%
import requests
import zipfile
import io

def fetch_data(url):
    """Télécharge les données depuis l'URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def list_zip_contents(zip_content):
    """Liste le contenu de l'archive ZIP pour vérifier le chemin exact des fichiers."""
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        # Affiche tous les fichiers dans l'archive
        print("Contenu de l'archive ZIP :")
        for file_name in z.namelist():
            print(file_name)

def extract_tasks_json(zip_content, output_path="/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json"):
    """Extrait uniquement le fichier tasks.json du ZIP."""
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        # Liste les fichiers dans le ZIP
        for file_name in z.namelist():
            if file_name == "converters/tasks.json":  # Cherche uniquement tasks.json
                with z.open(file_name) as f:
                    with open(output_path, "wb") as out_f:
                        out_f.write(f.read())  # Extrait et sauvegarde tasks.json
                print(f"Le fichier tasks.json a été extrait avec succès vers {output_path}")
                return
        print("tasks.json n'a pas été trouvé dans l'archive.")

if __name__ == "__main__":
    url = "https://zenodo.org/record/10782465/files/plantnet_swe.zip"
    zip_content = fetch_data(url)
    
    if zip_content:
        # Liste le contenu de l'archive pour vérifier le chemin
        list_zip_contents(zip_content)









# %%
import requests
import zipfile
import io

def fetch_data(url):
    """Télécharge les données depuis l'URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def extract_tasks_json(zip_content, output_path="/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json"):
    """Extrait uniquement le fichier tasks.json du ZIP."""
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        # Cherche le fichier `zenodo/converters/tasks.json` dans l'archive
        for file_name in z.namelist():
            if file_name == "zenodo/converters/tasks.json":  # Cherche uniquement tasks.json
                with z.open(file_name) as f:
                    with open(output_path, "wb") as out_f:
                        out_f.write(f.read())  # Extrait et sauvegarde tasks.json
                print(f"Le fichier tasks.json a été extrait avec succès vers {output_path}")
                return
        print("tasks.json n'a pas été trouvé dans l'archive.")

if __name__ == "__main__":
    url = "https://zenodo.org/record/10782465/files/plantnet_swe.zip"
    zip_content = fetch_data(url)
    
    if zip_content:
        extract_tasks_json(zip_content)
