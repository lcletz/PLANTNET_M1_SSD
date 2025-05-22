# %% 1. Extraction des scores non experts pour la calibration
import zipfile
import json
import numpy as np

zip_path = "15464436.zip"
confidence = 0.95
scores_s2 = []

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    for i in range(1, 35):
        filename = f"scores_nonexp_{i:02d}.json"
        if filename in zip_ref.namelist():
            with zip_ref.open(filename) as f:
                data = json.load(f)
                for valeurs in data.values():
                    if "sum_until_correct" in valeurs and isinstance(valeurs["sum_until_correct"], list):
                        scores_s2.extend(valeurs["sum_until_correct"])  # On ajoute tous les éléments à plat
        else:
            print(f"[Info] Fichier manquant : {filename}")

# %% 2.Calcul du quantile sur tous les éléments non experts
quantile3 = np.quantile(scores_s2, confidence)
print(f"\nQuantile à {confidence*100:.0f}% basé sur les non-experts : {quantile3:.4f}")

# %% 3. Chargement des données expertes 
with open("expert_scores2.json", "r") as f:
    expert_data_full = json.load(f).values()

test_scores2 = [
    v["sum_until_correct"]
    for v in expert_data_full
    if v.get("sum_until_correct") and isinstance(v["sum_until_correct"], list)
]

# %% 4. Test de conformité par élément : non conforme si au moins un score >= quantile
results = []
for score_list in test_scores2:
    if any(score >= quantile3 for score in score_list):
        results.append(("non conforme", score_list))
    else:
        results.append(("conforme", score_list))

print("\nRésultats du test sur moitié des données expertes :")
for i, (status, scores) in enumerate(results, 1):
    print(f"Plante {i:02d} - Scores : {scores} → {status}")

# %% 5. Identifier les plantes non conformes dans set test
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

non_conformes = {
    plante: valeurs["sum_until_correct"]
    for plante, valeurs in data.items()
    if any(s >= quantile3 for s in valeurs.get("sum_until_correct", []))
}

print("Plantes non conformes dans le set test :", non_conformes)
print("Nombre total de plantes non conformes dans le set test :", len(non_conformes))

# %% 6. Vérification de cas spécifiques
plante_ids = ["1004046780", "1014153815", "1011331452", "1013910015"]

for pid in plante_ids:
    if pid in non_conformes:
        print(f"La plante {pid} est non conforme avec un score de {non_conformes[pid]}")
    else:
        print(f"La plante {pid} est conforme.")

# %% 7. Visualisation avec Plotly en prenant le max de chaque liste (plus représentatif)
import pandas as pd
import plotly.express as px

with open("expert_scores2.json", "r", encoding="utf-8") as f:
    expert_test_data = json.load(f)

plante_ids = list(expert_test_data.keys())
scores_expert = [
    max(v["sum_until_correct"])  
    for v in expert_test_data.values()
    if "sum_until_correct" in v and len(v["sum_until_correct"]) > 0
]

df3 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score s2": scores_expert
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
fig.write_image("graphique_methode3.svg", width=400, height=250, scale=2)

# %% 8. Statistiques conformes à la théorie de la calibration

from scipy.stats import chisquare

calibration_array_m3 = np.array(scores_s2)  # tous les éléments non experts
quantile_m3 = quantile3
confidence_m3 = confidence

nb_conformes_m3 = np.sum(calibration_array_m3 < quantile_m3)
nb_non_conformes_m3 = len(calibration_array_m3) - nb_conformes_m3
taux_couverture_m3 = (nb_conformes_m3 / len(calibration_array_m3)) * 100

print(f"Taux de couverture observé : {taux_couverture_m3:.2f}%")
print(f"Taille du set de calibration : {len(calibration_array_m3)}")
print(f"Nombre de conformes : {nb_conformes_m3}")
print(f"Nombre de non conformes : {nb_non_conformes_m3}")

# %% 9. Test du Chi² : conformité au taux attendu

expected_m3 = [
    len(calibration_array_m3) * confidence_m3,
    len(calibration_array_m3) * (1 - confidence_m3)
]

observed_m3 = [nb_conformes_m3, nb_non_conformes_m3]

print(f"Observés : conformes = {observed_m3[0]}, non conformes = {observed_m3[1]}")
print(f"Attendus : conformes = {int(expected_m3[0])}, non conformes = {int(expected_m3[1])}")

chi2_stat_m3, p_value_m3 = chisquare(f_obs=observed_m3, f_exp=expected_m3)

print(f"Chi² = {chi2_stat_m3:.2f}, p = {p_value_m3:.4e}")

alpha = 0.05
if p_value_m3 < alpha:
    interpretation = (
        "Le test du Chi² indique que le taux de couverture observé "
        "diffère significativement du taux attendu (95%).\n"
        "L'hypothèse nulle est rejetée."
    )
else:
    interpretation = (
        "Le test du Chi² n'indique pas de différence significative entre "
        "le taux de couverture observé et celui attendu (95%).\n"
        "L'hypothèse nulle est conservée."
    )

print(interpretation)
# %%
