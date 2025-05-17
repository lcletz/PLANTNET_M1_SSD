# %%
import json
import numpy as np

# 1. Charger la moitiée des scores expertes pour calibration
with open("expert_scores1.json", "r") as f:
    non_expert_data2 = json.load(f)

# Score s1 = "one_minus_prob"
calibration_scores = [
    values["one_minus_prob"][0]  # Prendre la première valeur de la liste
    for values in non_expert_data2.values()
    if "one_minus_prob" in values  # Vérifier que la clé existe
]

# 2. Calcul du quantile à 95%
confidence = 0.95
quantile2 = np.quantile(calibration_scores, confidence)

print(f"Quantile à {confidence*100:.0f}% basé sur la moitié des experts (score s1) : {quantile2:.4f}")

# 3. Charger les données de la moitié des scores des EXPERTS pour test
with open("expert_scores2.json", "r") as f:
    expert_data_full = json.load(f).values()  

# Score S1 = "one_minus_prob"[0]
test_scores = [v["one_minus_prob"][0] for v in expert_data_full 
               if v.get("one_minus_prob") and isinstance(v["one_minus_prob"], list)]

# 4. Tester la conformité
results = [
    ("conforme" if score < quantile2 else "non conforme", score)
    for score in test_scores
]

# Affichage
print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results):
    print(f"Plante {i+1:02d} - Score : {score:.4f} → {status}")

# Est-ce qu'il y a des plantes avec des scores non conformes ?
# %%
import json

# Charger les données JSON
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Définir le seuil de conformité
quantile2

# Extraire les scores correctement
non_conformes = {plante: valeurs["one_minus_prob"][0] for plante, valeurs in data.items() if valeurs["one_minus_prob"][0] >= quantile2}

# Afficher les résultats
print("Plantes non conformes :", non_conformes)
print("Nombre total de plantes non conformes :", len(non_conformes))  

# %% # Visualisation
import json
import pandas as pd
import plotly.express as px
import kaleido

# Recharger les données expertes testées
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    expert_test_data = json.load(f)

# Extraire les IDs et les scores
plante_ids = list(expert_test_data.keys())
scores = [v["one_minus_prob"][0] for v in expert_test_data.values() if "one_minus_prob" in v]

# Recréer le DataFrame
df2 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s1": scores
})

# Déterminer la conformité par rapport au quantile
df2["Conforme"] = df2["Score_s1"] < quantile2

# Histogramme
fig = px.histogram(
    df2,
    x="Score_s1",
    color="Conforme",
    nbins=30,
    color_discrete_sequence=["#B08FC7", "#FF69B4"],
    title="s1 + expert",
    labels={"Score_s1"}
)

fig.add_vline(
    x=quantile2,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile 95% = {quantile2:.3f}",
    annotation_position="top left",
    annotation_font_size=12
)

fig.update_layout(
    width=800,
    height=500,
    bargap=0.1,
    xaxis=dict(
        title="Score de non-conformité s1",
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
fig.write_image("histogramme_method2.png")
fig.write_image("histogramme_method2.svg")

# %% Calcul du pourcentage de plantes conformes
nb_total2 = len(df2)
nb_conformes2 = df2["Conforme"].sum()
taux_couverture2 = (nb_conformes2 / nb_total2) * 100
print(f"\nTaux de couverture (méthode 2, s1) : {taux_couverture2:.2f}% ({nb_conformes2} sur {nb_total2})")

# Filtrer les scores en dessous ou égaux au quantile
scores_sous_quantile2 = [s for s in df2["Score_s1"] if s < quantile2]

# Calcul de la moyenne et de la médiane
moyenne2 = np.mean(scores_sous_quantile2)
mediane2 = np.median(scores_sous_quantile2)

print(f"Taille des données inférieures au quantile : {len(scores_sous_quantile2)}")
print(f"Score moyen des données inférieures au quantile : {moyenne2:.4f}")
print(f"Score médian des données inférieures au quantile : {mediane2:.4f}")

# %%
