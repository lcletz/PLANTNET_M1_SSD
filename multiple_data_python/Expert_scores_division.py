# Division des données expertes 
# %%
import json
import random

# Charger les données
with open("expert_processed_scores.json", "r") as f:
    expert_data = json.load(f)

# Rendre le tirage reproductible
random.seed(42)

# Mélanger les clés
keys = list(expert_data.keys())
random.shuffle(keys)

# Diviser en deux moitiés
mid = len(keys) // 2
expert_half1 = {k: expert_data[k] for k in keys[:mid]}
expert_half2 = {k: expert_data[k] for k in keys[mid:]}

# Sauvegarder les moitiés
with open("expert_scores1.json", "w") as f:
    json.dump(expert_half1, f, indent=4)

with open("expert_scores2.json", "w") as f:
    json.dump(expert_half2, f, indent=4)

# %%
