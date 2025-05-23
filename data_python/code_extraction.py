# %%
import requests
import zipfile
import io
import os

def fetch_data(url):
    """Télécharge les données depuis l'URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement des données : {e}")
        return None

def extract_and_save_data(zip_content, output_dir="extracted_data", num_lines=5000):
    """Extrait un nombre limité de lignes (par défaut 5000) depuis le fichier ZIP et les enregistre."""
    os.makedirs(output_dir, exist_ok=True)  # Crée le dossier si nécessaire
    
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        for file_name in z.namelist():
            if file_name.endswith('/'):  # Ignore les répertoires
                continue
            
            # Chemin relatif pour le fichier extrait
            relative_path = os.path.join(output_dir, *file_name.split('/')[1:])
            os.makedirs(os.path.dirname(relative_path), exist_ok=True)
            
            # Ouvre le fichier et lit les lignes
            with z.open(file_name) as f:
                with open(relative_path, 'wb') as out_file:
                    for _ in range(num_lines):
                        line = f.readline()
                        if not line:  # Arrête si la ligne est vide
                            break
                        out_file.write(line)
            
            print(f"Enregistré les {num_lines} premières lignes de {file_name} dans {relative_path}")

def extract_and_save_all_data(zip_content, output_dir="data"):
    """Extrait et enregistre tout le contenu d'un fichier ZIP."""
    os.makedirs(output_dir, exist_ok=True)
    
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        for file_name in z.namelist():
            if file_name.endswith('/'):  # Ignore les répertoires
                continue
            
            relative_path = os.path.join(output_dir, *file_name.split('/')[1:])
            os.makedirs(os.path.dirname(relative_path), exist_ok=True)
            
            with z.open(file_name) as f:
                with open(relative_path, 'wb') as out_file:
                    for line in f:
                        out_file.write(line)
            print(f"{file_name} enregistré dans {relative_path}")

if __name__ == "__main__":
    url = "https://zenodo.org/record/10782465/files/plantnet_swe.zip"
    zip_content = fetch_data(url)
    
    if zip_content:
        print("Données téléchargées avec succès.")
        
        # Limite le nombre de lignes à extraire (par exemple 100000)
        num_lines = 100000  # Modifier ce nombre pour ajuster la quantité de lignes extraites
        extract_and_save_data(zip_content, num_lines=num_lines)
        
        # Pour tout extraire sans limite de lignes, utiliser la fonction suivante :
        # extract_and_save_all_data(zip_content)

# %%
