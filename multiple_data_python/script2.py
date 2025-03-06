#%%
import os
import json
from tqdm import tqdm

def load_tasks(tasks_file):
    """Charge le fichier tasks.json contenant la correspondance des espèces."""
    if not os.path.exists(tasks_file):
        print(f"Erreur : le fichier {tasks_file} n'existe pas !")
        return None
    
    with open(tasks_file, "r", encoding="utf-8") as f:
        try:
            tasks = json.load(f)
            if not tasks:  # Vérifie si le JSON est vide
                print("tasks.json est vide ou mal formaté !")
                return None
            print(f"Chargé {len(tasks)} correspondances d'espèces")
            print(f"Exemple de correspondance : {list(tasks.items())[:5]}")
            return tasks
        except json.JSONDecodeError:
            print(f"Erreur : Impossible de lire {tasks_file}, format JSON invalide.")
            return None

def process_json_files(input_dir, output_file, tasks_file):
    """Parcourt les fichiers JSON et convertit les IDs des espèces."""
    
    tasks = load_tasks(tasks_file)
    if tasks is None:
        print("Impossible de charger la correspondance des espèces. Abandon.")
        return
    
    if not os.path.exists(input_dir):
        print(f"Erreur : le dossier {input_dir} n'existe pas !")
        return
    
    result_dict = {}
    
    json_files = [os.path.join(root, file) for root, _, files in os.walk(input_dir) for file in files if file.endswith(".json")]
    
    for file_path in tqdm(json_files, desc="Processing JSON files"):
        obs_id = os.path.splitext(os.path.basename(file_path))[0]
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Erreur de lecture JSON dans {file_path}, fichier ignoré.")
            continue
        
        results = data.get("results", [])
        if not results:
            continue
        
        species_scores = {}
        for entry in results:
            plantnet_id = str(entry.get("id"))
            score = entry.get("score", 0.0)
            if plantnet_id in tasks:
                crowdse_id = str(tasks[plantnet_id])
                species_scores[crowdse_id] = score
        
        if species_scores:
            result_dict[obs_id] = species_scores
    
    with open(output_file, "w", encoding="utf-8") as out_f:
        json.dump(result_dict, out_f, indent=4)
    
    print(f"Processing terminé ! Résultat sauvegardé dans {output_file}")

# Exemple d'utilisation
process_json_files("kswe_20250117_00", "output_converted.json", "/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json")

######################################################################################################################################################################################################################
#Ca me donne un fichier vide "{}". Je vais donc cherché d'ou ça vient.
######################################################################################################################################################################################################################
# %%
import json

# Chemins des fichiers
output_file = "output.json"
tasks_file = "/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json"

filtered_output_file = "filtered_output.json"

# Charger tasks.json
with open(tasks_file, "r", encoding="utf-8") as f:
    tasks = json.load(f)

# Récupérer les clés de tasks.json (IDs d'observations à 10 chiffres)
valid_obs_ids = set(tasks.keys())

# Charger output.json
with open(output_file, "r", encoding="utf-8") as f:
    output_data = json.load(f)

# Filtrer uniquement les observations qui existent dans tasks.json
filtered_data = {obs_id: output_data[obs_id] for obs_id in output_data if obs_id in valid_obs_ids}

# Sauvegarder le résultat
with open(filtered_output_file, "w", encoding="utf-8") as f:
    json.dump(filtered_data, f, indent=4)

print(f"Filtrage terminé ! Résultat enregistré dans {filtered_output_file}")

### Ca me donne un fichier final "output_final.jsonl" avec les observations et leurs espèces prédictes. Mon fichier contient : Chaque ligne est un dictionnaire {obs_id: {species_id: score}}
#Les identifiants d'observation (10 chiffres) sont bien pris en compte.
#Les scores des espèces sont conservés.
# %%
import os
import json
import jsonlines
from tqdm import tqdm

# Chemins des fichiers
input_dir = "kswe_20250117_00"  # Dossier principal contenant les sous-dossiers "00", "01", etc.
tasks_file = "/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json"
output_file = "output_final.jsonl"  # Utilisation de JSONL pour éviter la surcharge mémoire

# Charger tasks.json
with open(tasks_file, "r", encoding="utf-8") as f:
    tasks = json.load(f)

# Récupérer les IDs d'observations valides (10 chiffres)
valid_obs_ids = set(tasks.keys())

# Lister tous les fichiers JSON dans les sous-dossiers
json_files = []
for root, _, files in os.walk(input_dir):
    for file in files:
        if file.endswith(".json"):
            json_files.append(os.path.join(root, file))

# Vérifier que des fichiers ont été trouvés
print(f"Nombre total de fichiers JSON trouvés : {len(json_files)}")

# Traitement avec écriture progressive
with jsonlines.open(output_file, mode='w') as writer:
    for file_path in tqdm(json_files, desc="Traitement des fichiers JSON"):
        obs_id = os.path.splitext(os.path.basename(file_path))[0]
        
        # Vérifier si l'observation est valide
        if obs_id not in valid_obs_ids:
            continue
        
        # Charger le JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Extraire les scores des espèces
        species_scores = {entry["id"]: entry["score"] for entry in data.get("results", [])}
        
        # Vérifier qu'il y a des données valides
        if species_scores:
            writer.write({obs_id: species_scores})  # Écriture progressive
        
print(f"Traitement terminé ! Résultat enregistré dans {output_file}")

#### Convertir le fichier .jsol on .json car plus facile à lire
# %%
import json

input_file = "output_final.jsonl"
output_json = "output_final.json"

data = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        data.append(json.loads(line))

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print(f"Conversion terminée ! Fichier enregistré sous {output_json}")
