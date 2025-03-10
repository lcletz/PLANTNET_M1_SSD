#%%
import os
import json
from tqdm import tqdm  # Pour afficher une barre de progression

# Chemins des fichiers
input_dir = "/home/anne-laure/projet/PLANTNET_M1_SSD/multiple_data_python/kswe_20250117_00"
tasks_file = "/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json"
output_file = "output_final.json"

# Charger tasks.json
with open(tasks_file, "r", encoding="utf-8") as f:
    tasks = json.load(f)

# Récupérer les IDs d'observations valides
valid_obs_ids = set(tasks.keys())

# Dictionnaire pour stocker les résultats finaux
result_dict = {}

# Parcourir les fichiers en respectant la structure "/79/56/1000460000.json"
for root, _, files in tqdm(os.walk(input_dir), desc="Traitement des fichiers JSON"):
    for file in files:
        if file.endswith(".json"):
            file_path = os.path.join(root, file)
            obs_id = os.path.splitext(file)[0]  # Récupère l'ID de l'observation
            
            # Vérifier si l'observation est valide
            if obs_id not in valid_obs_ids:
                continue
            
            # Charger le contenu du fichier JSON
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extraire les scores des espèces
            species_scores = {entry["id"]: entry["score"] for entry in data.get("results", [])}
            
            # Ajouter au dictionnaire final
            if species_scores:
                result_dict[obs_id] = species_scores

# Écriture du fichier final en .json
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result_dict, f, indent=4)

print(f"Traitement terminé ! Résultat enregistré dans {output_file}")
# Sa me sort un fichier output_final.json qui contient les observations et les scores associés aux espèces.

# Je fais des vérifications du fichiers que m'a donner le code, j'essaye de voir si le nombre d'observations dans outpul_final.json = nb d'observation dans tasks.json
# %%
import json

# Charger les deux fichiers
with open("output_final.json", "r", encoding="utf-8") as f:
    output_data = json.load(f)

with open("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

# Vérification
print(f"Nombre d'observations dans output_final1.json : {len(output_data)}")
print(f"Nombre d'observations attendues dans tasks.json : {len(tasks)}")

# On obtient :
# Nombre d'observations dans output_final1.json : 1199
# Nombre d'observations attendues dans tasks.json : 999999
#On remarque qu'il manque énormément d'observaition
# Ece que mon dossier kwse contient assez de fichier JSON ?
# %%
import os

input_dir = "/home/anne-laure/projet/PLANTNET_M1_SSD/multiple_data_python/kswe_20250117_00"

# Vérification des fichiers trouvés
json_files = []
for root, _, files in os.walk(input_dir):
    for file in files:
        if file.endswith(".json"):
            json_files.append(os.path.join(root, file))

print(f"Nombre total de fichiers JSON trouvés : {len(json_files)}")
print(f"Exemples de chemins : {json_files[:5]}")

# On obtient un nombre total de fichiers JSON trouvés : 8183.

# Verifions maintenant si les IDs dans tasks.json correspondent bien à ceux présents dans les noms des fichiers JSON.
# %%
# Affiche quelques IDs pour comparer leur format
print(f"Exemples d'IDs dans tasks.json : {list(valid_obs_ids)[:5]}")
print(f"Exemples d'IDs de fichiers JSON détectés : {[os.path.splitext(os.path.basename(file))[0] for file in json_files[:5]]}")

# Les IDs dans tasks.json semblent être à 10 chiffres, tandis que les fichiers JSON sont également à 10 chiffres mais semblent différer légèrement.
# Il faut que les deux soient au même format, donc nous devons comparer les IDs correctement.



#%%
# Nettoyage des IDs dans tasks.json
valid_obs_ids = {str(obs_id).strip() for obs_id in tasks.keys()}

# Nettoyage des IDs de fichiers JSON
json_file_ids = {os.path.splitext(os.path.basename(file))[0].strip() for file in json_files}

# Afficher les nouveaux ensembles
print(f"IDs dans tasks.json après nettoyage : {list(valid_obs_ids)[:5]}")
print(f"IDs des fichiers JSON après nettoyage : {list(json_file_ids)[:5]}")

# %%
