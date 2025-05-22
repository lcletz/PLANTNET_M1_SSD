# %%
import zipfile
import json
import numpy as np

zip_path = "15464436.zip"
confidence = 0.95
scores_s2 = []

# 1. Charger les scores non experts depuis le zip
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    for i in range(1, 35):
        filename = f"scores_nonexp_{i:02d}.json"
        if filename in zip_ref.namelist():
            with zip_ref.open(filename) as f:
                data = json.load(f)
                for valeurs in data.values():
                    if "sum_until_correct" in valeurs and isinstance(valeurs["sum_until_correct"], list):
                        scores_s2.append(valeurs["sum_until_correct"][0])
        else:
            print(f"[Info] Fichier manquant : {filename}")

# %% 2. Calculer le quantile
quantile3 = np.quantile(scores_s2, confidence)
print(f"\nQuantile à {confidence*100:.0f}% basé sur les non-experts : {quantile3:.4f}")

# %% 3. Charger les données de la moitié des scores des EXPERTS pour test
with open("expert_scores2.json", "r") as f:
    expert_data_full = json.load(f).values()

test_scores2 = [
    v["sum_until_correct"][0]
    for v in expert_data_full
    if v.get("sum_until_correct") and isinstance(v["sum_until_correct"], list)
]

# %% 4. Tester la conformité
results = [
    ("conforme" if score < quantile3 else "non conforme", score)
    for score in test_scores2
]

print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results, 1):
    print(f"Plante {i:02d} - Score : {score:.4f} → {status}")

# %% 5. Identifier les plantes non conformes
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

non_conformes = {
    plante: valeurs["sum_until_correct"][0]
    for plante, valeurs in data.items()
    if valeurs["sum_until_correct"][0] >= quantile3
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

# %% 7. Visualisation

import pandas as pd
import plotly.express as px

with open("expert_scores2.json", "r", encoding="utf-8") as f:
    expert_test_data = json.load(f)

plante_ids = list(expert_test_data.keys())
scores_s2 = [
    v["sum_until_correct"][0]
    for v in expert_test_data.values()
    if "sum_until_correct" in v
]

df3 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score s2": scores_s2
})

df3["Index"] = range(len(df3))
df3["Conforme"] = df3["Score s2"].apply(lambda x: "Vrai" if x < quantile3 else "Faux")

fig = px.scatter(
    df3,
    x="Score s2",
    y="Index",
    color="Conforme",
    color_discrete_map={"Vrai": "#B08FC7", "Faux": "#FF69B4"},
    title="Méthode 3 : s2 + non expert",
    labels={"Score s2": "Score s2", "Index": "Observations testées", "Conforme": "Conformité"},
    opacity=0.4
)

fig.add_vline(
    x=quantile3,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile 95% = {quantile3:.4f}",
    annotation_position="top left",
    annotation_font_size=6
)

fig.update_layout(
    width=400,
    height=250,
    title_font_size=8,
    margin=dict(l=5, r=5, t=15, b=20),
    showlegend=True,
    legend=dict(
        font=dict(size=6),
        x=1,
        y=0.5,
        xanchor='left',
        yanchor='middle',
        borderwidth=0
    ),
    yaxis=dict(
        tickformat="",
        showticklabels=False,
        title_font=dict(size=8),
        tickfont=dict(size=8)
    ),
    xaxis=dict(
        range=[0, 1],
        dtick=0.1,
        tickfont=dict(size=8),
        title_font=dict(size=8)
    ),
)

fig.show()
#fig.write_image("graphique_methode3.svg", width=400, height=250, scale=2)

# %% 8. Statistiques conformes à la calibration

# Couverture correcte : sur les données de calibration (non-experts)
scores_s2_array = np.array(scores_s2)
nb_conformes_calib = np.sum(scores_s2_array < quantile3)
taux_couverture_calib = (nb_conformes_calib / len(scores_s2_array)) * 100

print(f"\n Taux de couverture (méthode 3, s2 - calibration non-experts) : {taux_couverture_calib:.2f}% ({nb_conformes_calib} sur {len(scores_s2_array)})")

# Statistiques descriptives sur les scores test (experts)
scores_sous_quantile3 = [s for s in df3["Score s2"] if s < quantile3]
moyenne3 = np.mean(scores_sous_quantile3)
mediane3 = np.median(scores_sous_quantile3)

print(f"Taille des données test inférieures au quantile : {len(scores_sous_quantile3)}")
print(f"Score moyen test inférieur quantile : {moyenne3:.4f}")
print(f"Score médian test inférieur quantile : {mediane3:.4f}")
