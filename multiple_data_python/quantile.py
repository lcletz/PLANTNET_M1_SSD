
########################################## Données expertes ##########################################################################################


#%%
import json

# Charger les données
with open("5_scores.json", "r") as file:
    data = json.load(file)

# Extraire les scores de non-conformité
non_conformity_scores = [v["one_minus_prob"][0] for v in data.values()]

# Trier les données
non_conformity_scores.sort()

# Calculer l'indice du quantile
confidence = 0.95
index = confidence * (len(non_conformity_scores) - 1)
lower_idx = int(index)
upper_idx = min(lower_idx + 1, len(non_conformity_scores) - 1)
weight = index - lower_idx

# Interpolation linéaire
quantile = (1 - weight) * non_conformity_scores[lower_idx] + weight * non_conformity_scores[upper_idx]

# Afficher
print(f"Scores de non-conformité : {non_conformity_scores}")
print(f"Quantile à {confidence * 100:.0f}% : {quantile}")


# Graphique avec quantile
#%%
import matplotlib.pyplot as plt
import numpy as np

# Trier les données
non_conformity_scores.sort()

# Calculer l'indice du quantile
confidence = 0.95
index = confidence * (len(non_conformity_scores) - 1)
lower_idx = int(index)
upper_idx = min(lower_idx + 1, len(non_conformity_scores) - 1)
weight = index - lower_idx
quantile = (1 - weight) * non_conformity_scores[lower_idx] + weight * non_conformity_scores[upper_idx]

# Tracer la distribution
plt.figure(figsize=(8, 5))
plt.hist(non_conformity_scores, bins=30, edgecolor="black", alpha=0.7)
plt.axvline(quantile, color="red", linestyle="dashed", linewidth=2, label=f"Quantile {confidence*100:.0f}%")
plt.xlabel("Scores de non-conformité")
plt.ylabel("Fréquence")
plt.title("Distribution des scores et position du quantile")
plt.legend()
plt.show()


# Nuage de point pour scores non conformité et rang cuulatif
#%%
import plotly.express as px
import pandas as pd
import json

# Charger les données JSON
with open("5_scores.json", "r") as file:
    data = json.load(file)

# Extraire les numéros des plantes et les scores de non-conformité
plant_ids = list(data.keys())  # Récupère les identifiants des plantes
non_conformity_scores = [v["one_minus_prob"][0] for v in data.values()]

# Créer un DataFrame avec les numéros et les scores
df = pd.DataFrame({"Score": non_conformity_scores, "Plante_ID": plant_ids})

# Calculer le quantile
confidence = 0.95
quantile = np.percentile(non_conformity_scores, confidence * 100)

# Tracer la CDF interactive avec les numéros de plantes
fig = px.scatter(df, x="Score", y=df.index / len(df), hover_data=["Plante_ID"], title="Score de non-conformité et son rang cumulatif.")

# Ajouter la ligne rouge du quantile
fig.add_vline(x=quantile, line_dash="dash", line_color="red", annotation_text=f"Quantile {confidence*100:.0f}%")

fig.update_layout(xaxis_title="Scores de non-conformité", yaxis_title="Proportion cumulée")

fig.show()



# Test pour voir si avoir une valeur Lamdba sa fonctionne 
 # %%
# Nouvelle prédiction (par exemple, une probabilité 1 - probabilité prédite)
nouvelle_prédiction = 0.3  # Remplacer par la probabilité réelle de la nouvelle prédiction

# Calculer le score de non-conformité pour la nouvelle prédiction
nouveau_score = nouvelle_prédiction

# Vérifier si cette prédiction est conforme
if nouveau_score <= quantile:
    print("La prédiction est conforme à 95% de confiance.")
else:
    print("La prédiction est peu conforme et est considérée comme une anomalie.")

########################################## Données non expertes ##########################################################################################

#%%
import json

# Charger les scores non experts
with open("5_scores_non_expertes.json", "r") as file:
    non_expert_data = json.load(file)

# Extraire et trier les scores
non_expert_scores = sorted([entry["non_conformity_score"] for entries in non_expert_data.values() for entry in entries])

# Calcul de l'indice du quantile
confidence = 0.95
index = confidence * (len(non_expert_scores) - 1)
lower_idx = int(index)
upper_idx = min(lower_idx + 1, len(non_expert_scores) - 1)
weight = index - lower_idx

# Interpolation linéaire si nécessaire
quantile_non_expert = (1 - weight) * non_expert_scores[lower_idx] + weight * non_expert_scores[upper_idx]

# Affichage des scores
print("Scores de non-conformité des données non expertes :")
for score in non_expert_scores:
    print(f"{score:.4f}")

# Affichage du quantile à 95 %
print(f"\nQuantile à {confidence * 100:.0f}%  : {quantile_non_expert: }")


############################################# Comparer les expertes et non-expertes #################################################################################
# %%
import json
import numpy as np
import pandas as pd
import plotly.express as px

# Charger les scores des experts
with open("5_scores.json", "r") as file:
    expert_data = json.load(file)
expert_scores = [v["one_minus_prob"][0] for v in expert_data.values()]

# Charger les scores des non experts
with open("5_scores_non_expertes.json", "r") as file:
    non_expert_data = json.load(file)
non_expert_scores = [entry["non_conformity_score"] for entries in non_expert_data.values() for entry in entries]

# Créer un DataFrame pour la visualisation
df_expert = pd.DataFrame({"Score": expert_scores, "Type": "Expert"})
df_non_expert = pd.DataFrame({"Score": non_expert_scores, "Type": "Non-expert"})
df = pd.concat([df_expert, df_non_expert], ignore_index=True)

# Trier et calculer la CDF pour chaque type
df.sort_values(["Type", "Score"], inplace=True)
df["CDF"] = df.groupby("Type").cumcount() / df.groupby("Type")["Score"].transform("count")

# Calculer les quantiles à 95 %
quantile_expert = np.percentile(expert_scores, 95)
quantile_non_expert = np.percentile(non_expert_scores, 95)

# Tracer la courbe cumulative interactive
fig = px.line(df, x="Score", y="CDF", color="Type", title="Comparaison des distributions - Experts vs Non-experts")

# Ajouter les lignes de quantile
fig.add_vline(x=quantile_expert, line_dash="dash", line_color="blue", annotation_text="Quantile 95% Expert")
fig.add_vline(x=quantile_non_expert, line_dash="dash", line_color="red", annotation_text="Quantile 95% Non-expert")

fig.update_layout(xaxis_title="Scores de non-conformité", yaxis_title="Proportion cumulée")

fig.show()
# %%
