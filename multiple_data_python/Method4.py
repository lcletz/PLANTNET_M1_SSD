# %%
import json
import numpy as np

# 1. Charger la moitiée des scores expertes pour calibration
with open("expert_scores1.json", "r") as f:
    non_expert_data4 = json.load(f)

# Score s2 = "sum_until_correct"
calibration_scores2 = [
    values["sum_until_correct"][0]  # Prendre la première valeur de la liste
    for values in non_expert_data4.values()
    if "sum_until_correct" in values  # Vérifier que la clé existe
]

# 2. Calcul du quantile à 95%
confidence = 0.95
quantile4 = np.quantile(calibration_scores2, confidence)

print(f"Quantile à {confidence*100:.0f}% basé sur la moitié des experts (score s2) : {quantile4:.4f}")

# 3. Charger les données de la moitié des scores des EXPERTS pour test
with open("expert_scores2.json", "r") as f:
    expert_data_full = json.load(f).values()  

test_scores2 = [v["sum_until_correct"][0] for v in expert_data_full 
               if v.get("sum_until_correct") and isinstance(v["sum_until_correct"], list)]

# 4. Tester la conformité
results = [
    ("conforme" if score < quantile4 else "non conforme", score)
    for score in test_scores2
]

# Affichage
print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results):
    print(f"Plante {i+1:02d} - Score : {score:.4f} → {status}")

# Est-ce qu'il y a des plantes avec des scores non conformes ?
# %%
import json

# Charger les données JSON
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Définir le seuil de conformité
quantile4

# Extraire les scores correctement
non_conformes = {plante: valeurs["sum_until_correct"][0] for plante, valeurs in data.items() if valeurs["sum_until_correct"][0] >= quantile4}

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
df4 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s2": scores
})

# Déterminer la conformité par rapport au quantile
df4["Conforme"] = df4["Score_s2"] < quantile4

# Histogramme
fig = px.histogram(
    df4,
    x="Score_s2",
    color="Conforme",
    nbins=30,
    color_discrete_sequence=["#B08FC7", "#FF69B4"],
    title="s2 + expert",
    labels={"Score_s2"}
)

fig.add_vline(
    x=quantile4,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile 95% = {quantile4:.3f}",
    annotation_position="top left",
    annotation_font_size=12
)

fig.update_layout(
    width=800,
    height=500,
    bargap=0.1,
    xaxis=dict(
        title="Score_s2 : Score cumulatif s2",
        tickformat=".2f",
        range=[0, 1],
        tick0=0,
        dtick=0.2
    ),
    yaxis=dict(
        title="Nombre de plantes",
        tickmode="auto"  
    ),
    showlegend=True
)

fig.update_layout(margin=dict(l=60, r=30, t=50, b=60))

fig.show()

# Sauvegarde
fig.write_image("histogramme_method4.png")
fig.write_image("histogramme_method4.svg")

# %% Calculs :

# Calcul du pourcentage de plantes conformes
nb_total4 = len(df4)
nb_conformes4 = df4["Conforme"].sum()
taux_couverture4 = (nb_conformes4 / nb_total4) * 100
print(f"\nTaux de couverture (méthode 4, s2) : {taux_couverture4:.2f}% ({nb_conformes4} sur {nb_total4})")

# Filtrer les scores en dessous ou égaux au quantile
scores_sous_quantile4 = [s for s in df4["Score_s2"] if s < quantile4]

# Calcul de la moyenne et de la médiane
moyenne4 = np.mean(scores_sous_quantile4)
mediane4 = np.median(scores_sous_quantile4)

# Affichage des résultats
print(f"Taille des données inférieures au quantile : {len(scores_sous_quantile4)}")
print(f"Score moyen des données inférieures au quantile : {moyenne4:.4f}")
print(f"Score médian des données inférieures au quantile : {mediane4:.4f}")
# %%
