# %%
# Méthode 4 : Calibration et test avec score s2 des experts
import json
import numpy as np
import pandas as pd
import plotly.express as px

# Paramètres
confidence = 0.95
calibration_file = "expert_scores1.json"
test_file = "expert_scores2.json"

# %% 1. Charger la moitié des scores experts pour calibration
with open(calibration_file, "r", encoding="utf-8") as f:
    calib_data = json.load(f)

calibration_scores2 = [
    v["sum_until_correct"][0]
    for v in calib_data.values()
    if "sum_until_correct" in v and isinstance(v["sum_until_correct"], list)
]

# %% 2. Calcul du quantile à 95% sur les données calibrées
quantile4 = np.quantile(calibration_scores2, confidence)
print(f"Quantile à {confidence*100:.0f}% basé sur la moitié des experts (score s2) : {quantile4:.4f}")

# %% 3. Charger les données test (autre moitié des experts)
with open(test_file, "r", encoding="utf-8") as f:
    test_data = json.load(f)

test_scores2 = [
    v["sum_until_correct"][0]
    for v in test_data.values()
    if "sum_until_correct" in v and isinstance(v["sum_until_correct"], list)
]

# %% 4. Tester la conformité des scores test
results = [("conforme" if s < quantile4 else "non conforme", s) for s in test_scores2]

print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results, 1):
    print(f"Plante {i:02d} - Score : {score:.4f} → {status}")

# %% 5. Identifier les plantes non conformes dans les données test
non_conformes = {
    pid: v["sum_until_correct"][0]
    for pid, v in test_data.items()
    if "sum_until_correct" in v and v["sum_until_correct"][0] >= quantile4
}

print("Plantes non conformes :", non_conformes)
print("Nombre total de plantes non conformes :", len(non_conformes))

# %% 6. Vérification de cas spécifiques
plante_ids = ["1004046780", "1014153815", "1011331452", "1013910015"]

for pid in plante_ids:
    if pid in non_conformes:
        print(f"La plante {pid} est non conforme avec un score de {non_conformes[pid]:.4f}")
    else:
        print(f"La plante {pid} est conforme.")

# %% 7. Visualisation interactive des résultats
plante_ids = list(test_data.keys())
scores_s2 = [
    v["sum_until_correct"][0]
    for v in test_data.values()
    if "sum_until_correct" in v
]

df4 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s2": scores_s2
})

df4["Index"] = range(len(df4))
df4["Conforme"] = df4["Score_s2"].apply(lambda x: "Vrai" if x < quantile4 else "Faux")

fig = px.scatter(
    df4,
    x="Score_s2",
    y="Index",
    color="Conforme",
    color_discrete_map={"Vrai": "#B08FC7", "Faux": "#FF69B4"},
    title="Méthode 4 : s2 + expert",
    labels={"Score_s2": "Score s2", "Index": "Observations testées", "Conforme": "Conformité"},
    opacity=0.4
)

fig.add_vline(
    x=quantile4,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile {confidence*100:.0f}% = {quantile4:.4f}",
    annotation_position="top left",
    annotation_font_size=6
)

fig.update_layout(
    width=400,
    height=250,
    title_font_size=8,
    margin=dict(l=5, r=5, t=15, b=5),
    showlegend=True,
    legend=dict(font=dict(size=6), x=1, y=0.5, xanchor='left', yanchor='middle', borderwidth=0),
    yaxis=dict(showticklabels=False, title_font=dict(size=8), tickfont=dict(size=8)),
    xaxis=dict(range=[0, 1], dtick=0.1, tickfont=dict(size=8), title_font=dict(size=8))
)

fig.show()
#fig.write_image("graphique_methode4.svg", width=400, height=250, scale=2)

# %% 8. Taux de couverture sur le jeu de calibration (expert_scores1.json)

calibration_scores2_array = np.array(calibration_scores2)
nb_conformes_calibration = np.sum(calibration_scores2_array < quantile4)
taux_couverture_calibration = (nb_conformes_calibration / len(calibration_scores2_array)) * 100

print(f"\nTaux de couverture (méthode 4, calibration sur experts, score s2) : {taux_couverture_calibration:.2f}% "
      f"({nb_conformes_calibration} sur {len(calibration_scores2_array)})")

# Statistiques descriptives sur les scores test (non utilisés pour la calibration)
scores_sous_q4 = df4[df4["Score_s2"] < quantile4]["Score_s2"]
print(f"Taille des données test inférieures au quantile : {len(scores_sous_q4)}")
print(f"Score moyen test inférieur quantile : {scores_sous_q4.mean():.4f}")
print(f"Score médian test inférieur quantile : {scores_sous_q4.median():.4f}")

# %%
