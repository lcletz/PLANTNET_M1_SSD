# Division des données expertes 
#%%
import json

# Charger le JSON
with open("expert_processed_scores.json", "r") as file:
    expert_data = json.load(file)

# Obtenir les clés et diviser en deux
keys = list(expert_data.keys())
mid = len(keys) // 2

expert_half1 = {key: expert_data[key] for key in keys[:mid]}
expert_half2 = {key: expert_data[key] for key in keys[mid:]}

# Sauvegarder les fichiers
with open("expert_scores1.json", "w") as file:
    json.dump(expert_half1, file, indent=4)

with open("expert_scores2.json", "w") as file:
    json.dump(expert_half2, file, indent=4)


# %%
