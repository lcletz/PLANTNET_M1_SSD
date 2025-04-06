# Calcul des scores des données non expertes 
#%%
import json

# Charger les données JSON
with open("samples_user_answers.json", "r") as file:
    data = json.load(file)

# Calculer les scores de non-conformité et les associer aux observations
scores_dict = {}

for plant_id, predictions in data.items():
    scores_dict[plant_id] = []
    for entry in predictions:
        non_conformity_score = 1 - entry["proba"]  # Calcul du score
        scores_dict[plant_id].append({
            "obs": entry["obs"], 
            "non_conformity_score": round(non_conformity_score, 4)  # Arrondi à 4 décimales
        })

# Sauvegarder les scores dans un fichier JSON
with open("5_score_non_expertes.json", "w") as outfile:
    json.dump(scores_dict, outfile, indent=4)

print("Fichier '5_scores_non_expertes.json' créé avec succès !")
