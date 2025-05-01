# %%
import json
import numpy as np

# 1. Charger les données NON-EXPERTES pour calibration
with open("5_scores_non_experts.json", "r") as f:
    non_expert_data3 = json.load(f)

# Score s2 = "sum_until_correct"
calibration_scores2 = [
    values["sum_until_correct"][0]  # Prendre la première valeur de la liste
    for values in non_expert_data3.values()
    if "sum_until_correct" in values  # Vérifier que la clé existe
]

# 2. Calcul du quantile à 95%
confidence = 0.95
quantile3 = np.quantile(calibration_scores2, confidence)

print(f"Quantile à {confidence*100:.0f}% basé sur les non-experts (score s2) : {quantile3:.4f}")

# 3. Charger les données de la moitié des scores des EXPERTS pour test
with open("expert_scores2.json", "r") as f:
    expert_data_full = json.load(f).values()  

test_scores2 = [v["sum_until_correct"][0] for v in expert_data_full 
               if v.get("sum_until_correct") and isinstance(v["sum_until_correct"], list)]

# 4. Tester la conformité
results = [
    ("conforme" if score <= quantile3 else "non conforme", score)
    for score in test_scores2
]

# Affichage
print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results):
    print(f"Plante {i+1:02d} - Score : {score:.4f} → {status}")

# Esse que il y a des plantes avec des scores non conforme ?
# %%
import json

# Charger les données JSON
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Définir le seuil de conformité
threshold = 0.7618

# Extraire les scores correctement
non_conformes = {plante: valeurs["sum_until_correct"][0] for plante, valeurs in data.items() if valeurs["sum_until_correct"][0] > threshold}

# Afficher les résultats
print("Plantes non conformes :", non_conformes)
print("Nombre total de plantes non conformes :", len(non_conformes))  

# Visualisation
# %%
import json
import pandas as pd
import plotly.express as px
import kaleido

# Recharger les données expertes testées
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    expert_test_data = json.load(f)

# Extraire les IDs et les scores
plante_ids = list(expert_test_data.keys())
scores = [v["sum_until_correct"][0] for v in expert_test_data.values() if "sum_until_correct" in v]

# Recréer le DataFrame
df3 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s2": scores
})

# Déterminer la conformité par rapport au quantile
df3["Conforme"] = df3["Score_s2"] <= quantile3

# Créer le scatter plot avec les couleurs demandées
fig = px.scatter(
    df3,
    x="Score_s2",
    y=df3.index,
    color="Conforme",
    color_discrete_map={True: "#B08FC7", False: "#FF69B4"},  
    hover_data=["Plante_ID"],
    title="s2 scores of the tested plants and 95% quantile threshold",
    labels={"Score_s2": "Score cumulatif s2", "index": "Index plante"}
)

# Ajouter la ligne rouge du quantile
fig.add_vline(
    x=quantile3,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile 95% = {quantile3:.4f}",
    annotation_position="top right"
)

fig.update_layout(
    yaxis_title="Plants tested",
    xaxis_title="Score s2",
    showlegend=True
)

fig.show()

# Enregistrement PNG statique
fig.write_image("graphique_method3.png")

# %% Calculs :
# 1. Taux de couverture
nb_total = len(df3)
nb_conformes = df3["Conforme"].sum()
taux_couverture = (nb_conformes / nb_total) * 100
print(f"\nTaux de couverture (méthode 3, s2) : {taux_couverture:.2f}% ({nb_conformes} sur {nb_total})")

# 2. Taille moyenne des ensembles de prédiction
ensemble_sizes = [
    v["sum_until_correct"][0]
    for v in data.values()
    if "sum_until_correct" in v
]

taille_moyenne = np.mean(ensemble_sizes)
print(f"Taille moyenne des ensembles de prédiction (méthode 3 - s2) : {taille_moyenne:.2f}")

# %%
