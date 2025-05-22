# %% 1. Charger la moitié des scores experts pour calibration
import json
import numpy as np
import pandas as pd
import plotly.express as px

# Paramètres
calibration_file = "expert_scores1.json"
expert_file = "expert_scores2.json"
confidence = 0.95

with open(calibration_file, "r", encoding="utf-8") as f:
    expert_calib_data = json.load(f)

calibration_scores = [
    v["one_minus_prob"][0]
    for v in expert_calib_data.values()
    if "one_minus_prob" in v and isinstance(v["one_minus_prob"], list)
]

if not calibration_scores:
    raise ValueError("Aucun score de calibration trouvé dans expert_scores1.json")

# %% 2. Calcul du quantile basé sur les experts en calibration
quantile2 = np.quantile(calibration_scores, confidence)
print(f"\nQuantile à {confidence*100:.0f}% basé sur la moitié des experts (score s1) : {quantile2:.4f}")

# %% 3. Chargement des scores experts pour test
with open(expert_file, "r", encoding="utf-8") as f:
    expert_test_data = json.load(f)

test_scores = [
    v["one_minus_prob"][0]
    for v in expert_test_data.values()
    if "one_minus_prob" in v and isinstance(v["one_minus_prob"], list)
]

# Conformité
results = [("conforme" if s < quantile2 else "non conforme", s) for s in test_scores]

print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results, 1):
    print(f"Plante {i:02d} - Score : {score:.4f} → {status}")

# %% 4. Identifier les plantes non conformes pour le set test
non_conformes = {
    pid: valeurs["one_minus_prob"][0]
    for pid, valeurs in expert_test_data.items()
    if "one_minus_prob" in valeurs and valeurs["one_minus_prob"][0] >= quantile2
}

print("Plantes non conformes :", non_conformes)
print("Nombre total de plantes non conformes :", len(non_conformes))

# %% 5. Vérification de cas spécifiques
plante_ids = ["1004046780", "1014153815", "1011331452", "1013910015"]
for pid in plante_ids:
    if pid in non_conformes:
        print(f"La plante {pid} est non conforme avec un score de {non_conformes[pid]:.4f}")
    else:
        print(f"La plante {pid} est conforme.")

# %% 6. Visualisation interactive
plante_ids = list(expert_test_data.keys())
scores_s1 = [v["one_minus_prob"][0] for v in expert_test_data.values() if "one_minus_prob" in v]

df2 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s1": scores_s1
})

df2["Index"] = range(len(df2))
df2["Conforme"] = df2["Score_s1"].apply(lambda x: "Vrai" if x < quantile2 else "Faux")

fig = px.scatter(
    df2,
    x="Score_s1",
    y="Index",
    color="Conforme",
    color_discrete_map={"Vrai": "#B08FC7", "Faux": "#FF69B4"},
    title="Méthode 2 : s1 + expert",
    labels={"Score_s1": "Score s1", "Index": "Observations testées", "Conforme": "Conformité"},
    opacity=0.4
)

fig.add_vline(
    x=quantile2,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile {confidence*100:.0f}% = {quantile2:.4f}",
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
fig.write_image("graphique_methode2.svg", width=400, height=250, scale=2)

# %% 7. Statistiques conformes à la théorie de la calibration (Méthode 2)

# Calcul du taux de couverture sur les données de calibration (experts calibration)
calibration_array = np.array(calibration_scores)
nb_conformes_calib = np.sum(calibration_array < quantile2)
nb_non_conformes_calib = len(calibration_array) - nb_conformes_calib
taux_couverture_calib = (nb_conformes_calib / len(calibration_array)) * 100

print(f"Taux de couverture observé : {taux_couverture_calib:.2f}%")
print(f"Taille totale du set de calibration : {len(calibration_array)}")
print(f"Nombre d'observations conformes : {nb_conformes_calib}")
print(f"Nombre d'observations non conformes : {nb_non_conformes_calib}")

# %% 8. Test du Chi² : conformité au taux attendu (Méthode 2)

from scipy.stats import chisquare

# Données observées et attendues
n_total = len(calibration_array)
obs = [nb_conformes_calib, nb_non_conformes_calib]
exp = [n_total * confidence, n_total * (1 - confidence)]

print(f"Observés : conformes = {obs[0]}, non conformes = {obs[1]}")
print(f"Attendus : conformes = {int(exp[0])}, non conformes = {int(exp[1])}")

# Test statistique
chi2_stat, p_value_m2 = chisquare(f_obs=obs, f_exp=exp)

# Résultats du test
print(f"Chi² = {chi2_stat:.2f}, p = {p_value_m2:.4e}")

# Interprétation automatique
alpha = 0.05
if p_value_m2 < alpha:
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
