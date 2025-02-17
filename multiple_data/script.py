#%%
import os # permet de gérer les fichiers et les répertoires
import json # utilisé pour lire et utiliser les fichier .json
from tqdm import tqdm # affiche une barre de progression pour suivre l'avancement du traitement

def process_json_files(input_dir, output_file):
    # 1. Vérifier si le dossier existe
    if not os.path.exists(input_dir):
        print(f"Le dossier {input_dir} n'existe pas !")
        return
    
    # Création d'un dictionnaire pour stocker les résultat ; Initialise un dictionnaire vide result_dict qui va contenir les données extraites des fichiers JSON
    result_dict = {}
    # Parcours des fichiers JSON dans le dossier
    for root, _, files in tqdm(os.walk(input_dir), desc="Processing JSON files"):
        for file in files: # Traitement des fichiers JSON
            if file.endswith(".json"): # Pour chaque fichier dans files, vérifie s'il a l'extension .json (pour éviter les fichiers inutiles)
                file_path = os.path.join(root, file) # file_path : construit le chemin complet vers le fichie
                obs_id = os.path.splitext(file)[0]  # Récupère le nom du fichier sans l'extension .json (qui correspond à l’ID de l’observation)
                
                with open(file_path, "r", encoding="utf-8") as f: #Ouvre le fichier JSON en lecture ("r") avec l’encodage UTF-8
                    data = json.load(f)  # json.load(f) : Charge le contenu du fichier sous forme de dictionnaire Python
                    species_scores = {entry["id"]: entry["score"] for entry in data.get("results", [])}
                    #data.get("results", []) : Cherche la clé "results" dans le JSON. Si elle n'existe pas, retourne une liste vide [] (évite les erreurs)
                    # entry["id"] et entry["score"] : Extrait l’ID de l’espèce et son score pour chaque entrée dans "results"
                    result_dict[obs_id] = species_scores # Un dictionnaire {id_espece: score}
    
    # 3. Sauvegarder le dictionnaire final dans un fichier JSON
    with open(output_file, "w", encoding="utf-8") as out_f:
        json.dump(result_dict, out_f, indent=4)
    
    print(f"Processing terminé ! Résultat sauvegardé dans {output_file}")

# Exemple d'utilisation
process_json_files("kswe_20250117_00", "output.json")

# %%
