# %% Division des données expertes depuis le zip
import json
import random
import zipfile

# Chemin du fichier ZIP
zip_path = "15464436.zip"
expert_filename = "expert_processed_scores.json"

# Charger le fichier expert depuis le zip
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    if expert_filename in zip_ref.namelist():
        with zip_ref.open(expert_filename) as f:
            expert_data = json.load(f)
    else:
        raise FileNotFoundError(f"Fichier {expert_filename} non trouvé dans {zip_path}")

# Rendre le tirage reproductible
random.seed(42)

# Mélanger les clés
keys = list(expert_data.keys())
random.shuffle(keys)

# Diviser en deux moitiés
mid = len(keys) // 2
expert_half1 = {k: expert_data[k] for k in keys[:mid]}
expert_half2 = {k: expert_data[k] for k in keys[mid:]}

# Sauvegarder les moitiés localement
with open("expert_scores1.json", "w", encoding="utf-8") as f:
    json.dump(expert_half1, f, indent=4, ensure_ascii=False)

with open("expert_scores2.json", "w", encoding="utf-8") as f:
    json.dump(expert_half2, f, indent=4, ensure_ascii=False)

print("Division réussie : expert_scores1.json et expert_scores2.json sauvegardés.")
# %%
