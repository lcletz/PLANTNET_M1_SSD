#%%
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
        print(f"Error fetching data: {e}")
        return None

def extract_and_save_data(zip_content, output_dir="/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data", num_lines=5000):
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
                        if not line:  # Si la ligne est vide, arrête de lire
                            break
                        out_file.write(line)
            
            print(f"Saved first {num_lines} lines of {file_name} to {relative_path}")

def extract_and_save_all_data(zip_content, output_dir="/home/anne-laure/projet/PLANTNET_M1_SSD/data"):
    """Extrait et sauvegarde tout le contenu d'un fichier ZIP."""
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
            print(f"Saved {file_name} to {relative_path}")

if __name__ == "__main__":
    url = "https://zenodo.org/record/10782465/files/plantnet_swe.zip"
    zip_content = fetch_data(url)
    
    if zip_content:
        print("Data fetched successfully:")
        
        # Limite le nombre de lignes à extraire (par exemple 5000)
        num_lines = 5000  # Change ce nombre si tu veux plus ou moins de lignes extraites
        extract_and_save_data(zip_content, num_lines=num_lines)
        
        # Si tu veux tout extraire sans limite de lignes, tu peux utiliser cette fonction :
        # extract_and_save_all_data(zip_content)

# %%
