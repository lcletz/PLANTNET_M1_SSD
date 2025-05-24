# %% 1. Charger la moitié des scores experts pour calibration

import json
import numpy as np
import pandas as pd
import plotly.express as px

# Paramètres
confidence = 0.95
calibration_file = "expert_scores1.json"
test_file = "expert_scores2.json"

with open(calibration_file, "r", encoding="utf-8") as f:
    calib_data = json.load(f)

calibration_scores2 = []
for v in calib_data.values():
    if "sum_until_correct" in v and isinstance(v["sum_until_correct"], list):
        calibration_scores2.extend(v["sum_until_correct"])

# %% 2. Calcul du quantile à 95% sur les données calibrées
quantile4 = np.quantile(calibration_scores2, confidence)
print(f"Quantile à {confidence*100:.0f}% basé sur la moitié des experts (score s2) : {quantile4:.4f}")

# %% 3. Charger les données test (autre moitié des experts)
with open(test_file, "r", encoding="utf-8") as f:
    test_data = json.load(f)

# Extraire les listes sum_until_correct
test_scores2 = [
    v["sum_until_correct"]
    for v in test_data.values()
    if "sum_until_correct" in v and isinstance(v["sum_until_correct"], list)
]

# %% 4. Tester la conformité des scores test
# Si au moins un score >= quantile alors non conforme
results = []
for scores in test_scores2:
    if any(s >= quantile4 for s in scores):
        results.append(("non conforme", scores))
    else:
        results.append(("conforme", scores))

print("\nRésultats du test sur moitié des données expertes :")
for i, (status, scores) in enumerate(results, 1):
    print(f"Plante {i:02d} - Scores : {scores} → {status}")

# %% 5. Identifier les plantes non conformes dans les données test
non_conformes = {
    pid: v["sum_until_correct"]
    for pid, v in test_data.items()
    if "sum_until_correct" in v and any(s >= quantile4 for s in v["sum_until_correct"])
}

print("Plantes non conformes :", non_conformes)
print("Nombre total de plantes non conformes :", len(non_conformes))

# %% 6. Vérification de cas spécifiques
plante_ids = ["1004046780", "1014153815", "1011331452", "1013910015"]

for pid in plante_ids:
    if pid in non_conformes:
        print(f"La plante {pid} est non conforme avec un score de {non_conformes[pid]}")
    else:
        print(f"La plante {pid} est conforme.")

# %% 7. Visualisation interactive des résultats
plante_ids = list(test_data.keys())
# Pour la visualisation, on prend le max des scores par plante (représente le pire cas)
scores_max = [
    max(v["sum_until_correct"]) if "sum_until_correct" in v and v["sum_until_correct"] else np.nan
    for v in test_data.values()
]

df4 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s2": scores_max
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
fig.write_image("graphique_methode4.svg", width=400, height=250, scale=2)


# %% 8. Calcul du taux de couverture sur notre set test
nb_total_experts4 = len(df4)
nb_conformes_experts4 = df4["Conforme"].value_counts().get("Vrai", 0)
nb_non_conformes_experts4 = nb_total_experts4 - nb_conformes_experts4
taux_couverture_experts4 = (nb_conformes_experts4 / nb_total_experts4) * 100

print(f"Taux de couverture observé : {taux_couverture_experts4:.2f}%")
print(f"Taille totale du set test : {nb_total_experts4}")
print(f"Nombre d'observations conformes : {nb_conformes_experts4}")
print(f"Nombre d'observations non conformes : {nb_non_conformes_experts4}")

# %% 8. Test du Chi² 

from scipy.stats import chisquare

obs_exp4 = [nb_conformes_experts4, nb_non_conformes_experts4]
exp_exp4 = [nb_total_experts4 * confidence, nb_total_experts4 * (1 - confidence)]

print(f"Observés : conformes = {obs_exp4[0]}, non conformes = {obs_exp4[1]}")
print(f"Attendus : conformes = {int(exp_exp4[0])}, non conformes = {int(exp_exp4[1])}")

chi2_stat_exp4, p_value4 = chisquare(f_obs=obs_exp4, f_exp=exp_exp4)

print(f"Chi² = {chi2_stat_exp4:.2f}, p = {p_value4:.4e}")

# Interprétation automatique
alpha = 0.05
if p_value4 < alpha:
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

#%%
import json
import numpy as np

def create_prediction_set_one_minus_prob(predictions, threshold):
    prediction_set = []
    for pred in predictions:
        score = 1 - pred['proba']
        if score < threshold:
            prediction_set.append(pred['name'])
    return prediction_set

def create_prediction_set_sum_until_correct_simulation(predictions, threshold):
    sorted_preds = sorted(predictions, key=lambda x: -x['proba'])
    
    # On va tester toutes les positions possibles comme si elles étaient correctes
    set_sizes = []
    
    for correct_name in [p['name'] for p in sorted_preds]:
        cumulative = 0
        prediction_set = []
        for pred in sorted_preds:
            prediction_set.append(pred['name'])
            cumulative += pred['proba']
            # On s'arrête si on a inclus la bonne prédiction ET que la somme cumulative dépasse le quantile
            if pred['name'] == correct_name and cumulative >= threshold:
                break
        set_sizes.append(len(prediction_set))
    
    # On prend la taille minimale du set 
    return min(set_sizes) if set_sizes else 0

def compute_avg_median_set_size(raw_data, threshold, score_type):
    set_sizes = []

    for obs_id, predictions in raw_data.items():
        if score_type == "one_minus_prob":
            pred_set = create_prediction_set_one_minus_prob(predictions, threshold)
            set_sizes.append(len(pred_set))

        elif score_type == "sum_until_correct":
            
            size = create_prediction_set_sum_until_correct_simulation(predictions, threshold)
            set_sizes.append(size)

    avg_size = np.mean(set_sizes)
    median_size = np.median(set_sizes)
    return avg_size, median_size

# Chargement des données
with open("expert_processed.json", "r") as f:
    expert_processed = json.load(f)

threshold = quantile4

# Choix du mode
score_type = "sum_until_correct"

# Calcul
avg, median = compute_avg_median_set_size(expert_processed, threshold, score_type)

print(f"Taille moyenne : {avg:.2f}")
print(f"Taille médiane : {median}")

# %%
