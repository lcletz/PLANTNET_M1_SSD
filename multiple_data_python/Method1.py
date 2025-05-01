# %%
import json
import numpy as np

# 1. Charger les données NON-EXPERTES pour calibration
with open("5_scores_non_experts.json", "r") as f:
    non_expert_data = json.load(f)

# Score s1 = "non_conformity_score"
calibration_scores = [
    values["one_minus_prob"][0]  # Prendre la première valeur de la liste
    for values in non_expert_data.values()
    if "one_minus_prob" in values  # Vérifier que la clé existe
]

# 2. Calcul du quantile à 95%
confidence = 0.95
quantile1 = np.quantile(calibration_scores, confidence)

print(f"Quantile à {confidence*100:.0f}% basé sur les non-experts (score s1) : {quantile1:.4f}")

# 3. Charger les données de la moitié des scores des EXPERTS pour test
with open("expert_scores2.json", "r") as f:
    expert_data_full = json.load(f).values()  

# Score S1 = "one_minus_prob"[0]
test_scores = [v["one_minus_prob"][0] for v in expert_data_full 
               if v.get("one_minus_prob") and isinstance(v["one_minus_prob"], list)]

# 4. Tester la conformité
results = [
    ("conforme" if score <= quantile1 else "non conforme", score)
    for score in test_scores
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
threshold = 0.9990

# Extraire les scores correctement (en prenant le premier élément de la liste)
non_conformes = {plante: valeurs["one_minus_prob"][0] for plante, valeurs in data.items() if valeurs["one_minus_prob"][0] > threshold}

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
scores = [v["one_minus_prob"][0] for v in expert_test_data.values() if "one_minus_prob" in v]

# Recréer le DataFrame
df = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s1": scores
})

# Déterminer la conformité par rapport au quantile (déjà défini plus tôt)
df["Conforme"] = df["Score_s1"] <= quantile1

# Créer le scatter plot
fig = px.scatter(
    df,
    x="Score_s1",
    y=df.index,
    color="Conforme",
    color_discrete_sequence=["#B08FC7"],
    hover_data=["Plante_ID"],
    title="s1 scores of the tested plants and 95% quantile threshold",
    labels={"Score_s1": "Score de non-conformité s1", "index": "Index plante"}
)

# Ajouter la ligne rouge du quantile
fig.add_vline(
    x=quantile1,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile 95% = {quantile1:.3f}",
    annotation_position="top right"
)

fig.update_layout(
    yaxis_title="Plants tested",
    xaxis_title="Score s1",
    showlegend=True
)

fig.show()

# Enregistrement PNG statique
fig.write_image("graphique_method1.png")

# %%
