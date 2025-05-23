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
                        scores_s2.extend(valeurs["sum_until_correct"]) 
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

# %% 7. Visualisation avec Plotly 
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
    width=600,
    height=300,
    title_font_size=14,
    margin=dict(l=10, r=10, t=40, b=10),
    showlegend=True,
    legend=dict(
        font=dict(size=10),
        x=1,
        y=0.5,
        xanchor='left',
        yanchor='middle',
        borderwidth=0
    ),
    yaxis=dict(
        tickformat="",
        showticklabels=False,
        title_font=dict(size=12),
        tickfont=dict(size=12)
    ),
    xaxis=dict(
        range=[0, 1],
        dtick=0.1,
        tickfont=dict(size=12),
        title_font=dict(size=12)
    ),
)

fig.show()
fig.write_image("graphique_methode3.svg")

# %% 8. Calcul du taux de couverture sur notre set test
nb_total_experts3 = len(df3)
nb_conformes_experts3 = df3["Conforme"].value_counts().get("Vrai", 0)
nb_non_conformes_experts3 = nb_total_experts3 - nb_conformes_experts3
taux_couverture_experts3 = (nb_conformes_experts3 / nb_total_experts3) * 100

print(f"Taux de couverture observé : {taux_couverture_experts3:.2f}%")
print(f"Taille totale du set test : {nb_total_experts3}")
print(f"Nombre d'observations conformes : {nb_conformes_experts3}")
print(f"Nombre d'observations non conformes : {nb_non_conformes_experts3}")

# %% 8. Test du Chi² 

from scipy.stats import chisquare

obs_exp3 = [nb_conformes_experts3, nb_non_conformes_experts3]
exp_exp3 = [nb_total_experts3 * confidence, nb_total_experts3 * (1 - confidence)]

print(f"Observés : conformes = {obs_exp3[0]}, non conformes = {obs_exp3[1]}")
print(f"Attendus : conformes = {int(exp_exp3[0])}, non conformes = {int(exp_exp3[1])}")

chi2_stat_exp3, p_value3 = chisquare(f_obs=obs_exp3, f_exp=exp_exp3)

print(f"Chi² = {chi2_stat_exp3:.2f}, p = {p_value3:.4e}")

# Interprétation automatique
alpha = 0.05
if p_value3 < alpha:
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

threshold = quantile3

# Choix du mode
score_type = "sum_until_correct"

# Calcul
avg, median = compute_avg_median_set_size(expert_processed, threshold, score_type)

print(f"Taille moyenne : {avg:.2f}")
print(f"Taille médiane : {median}")

# %%
