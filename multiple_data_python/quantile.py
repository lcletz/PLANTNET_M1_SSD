#%%
import json
import numpy as np

# Charger les données depuis le fichier .json
with open("5_scores.json", "r") as file:
    data = json.load(file)

# Extraire les valeurs de 'one_minus_prob' pour calculer les scores de non-conformité
non_conformity_scores = []

for key, value in data.items():
    non_conformity_scores.append(value["one_minus_prob"][0])

# Calculer un quantile de ces scores de non-conformité (par exemple, le 95e percentile)
quantile = np.percentile(non_conformity_scores, 95)

# Afficher les scores de non-conformité et le quantile calculé
print(f"Scores de non-conformité : {non_conformity_scores}")
print(f"Quantile à 95% : {quantile}")

# %%
