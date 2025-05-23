# %% Méthode 1 : Analyse des scores non experts et comparaison avec les experts
import zipfile
import json
import numpy as np
import pandas as pd
import plotly.express as px

# Paramètres
zip_path = "15464436.zip"
confidence = 0.95
prefix_nonexp = "scores_nonexp_"
expert_file = "expert_scores2.json"

# %% 1. Extraction des scores non experts
scores_nonexp = []

with zipfile.ZipFile(zip_path, 'r') as archive:
    for i in range(1, 35):
        filename = f"{prefix_nonexp}{i:02d}.json"
        if filename in archive.namelist():
            with archive.open(filename) as f:
                data = json.load(f)
                for val in data.values():
                    if "one_minus_prob" in val and isinstance(val["one_minus_prob"], list):
                        scores_nonexp.append(val["one_minus_prob"][0])
        else:
            print(f"[Info] Fichier manquant : {filename}")

if not scores_nonexp:
    raise ValueError("Aucun score non expert trouvé. Veuillez vérifier les fichiers dans le zip.")

# %% 2. Calcul du quantile basé sur les non-experts
quantile1 = np.quantile(scores_nonexp, confidence)
print(f"\nQuantile à {confidence*100:.0f}% basé sur les non-experts : {quantile1:.4f}")

# %% 3. Chargement et test sur les scores experts
with open(expert_file, "r", encoding="utf-8") as f:
    expert_data = json.load(f)

expert_scores_s1 = [v["one_minus_prob"][0] for v in expert_data.values()
                    if "one_minus_prob" in v and isinstance(v["one_minus_prob"], list)]

# Conformité
results = [("conforme" if s < quantile1 else "non conforme", s) for s in expert_scores_s1]

print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results):
    print(f"Plante {i+1:02d} - Score : {score:.4f} → {status}")

# %% 4. Identifier les plantes non conformes (set de test "expert_scores2.json")
non_conformes = {
    pid: valeurs["one_minus_prob"][0]
    for pid, valeurs in expert_data.items()
    if "one_minus_prob" in valeurs and valeurs["one_minus_prob"][0] >= quantile1
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
plante_ids = list(expert_data.keys())
scores_s1 = [v["one_minus_prob"][0] for v in expert_data.values() if "one_minus_prob" in v]

# Création du DataFrame
df = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s1": scores_s1
})

df["Index"] = range(len(df))
df["Conforme"] = df["Score_s1"].apply(lambda x: "Vrai" if x < quantile1 else "Faux")

fig = px.scatter(
    df,
    x="Score_s1",
    y="Index",
    color="Conforme",
    color_discrete_map={"Vrai": "#B08FC7", "Faux": "#FF69B4"},
    title="Méthode 1 : s1 + non expert",
    labels={"Score_s1": "Score s1", "Index": "Observations testées", "Conforme": "Conformité"},
    opacity=0.4
)

fig.add_vline(
    x=quantile1,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile {confidence*100:.0f}% = {quantile1:.4f}",
    annotation_position="top left",
    annotation_font_size=6
)

fig.update_layout(
    width=600,
    height=300,
    title_font_size=14,
    margin=dict(l=10, r=10, t=40, b=10),
    showlegend=True,
    legend=dict(font=dict(size=10), x=1, y=0.5, xanchor='left', yanchor='middle', borderwidth=0),
    yaxis=dict(showticklabels=False, title_font=dict(size=12), tickfont=dict(size=12)),
    xaxis=dict(range=[0, 1], dtick=0.1, tickfont=dict(size=12), title_font=dict(size=12))
)

fig.show()
fig.write_image("graphique_methode1.svg")

# %% 7. Calcul du taux de couverture sur notre set test
nb_total_experts = len(df)
nb_conformes_experts = df["Conforme"].value_counts().get("Vrai", 0)
nb_non_conformes_experts = nb_total_experts - nb_conformes_experts
taux_couverture_experts = (nb_conformes_experts / nb_total_experts) * 100

print(f"Taux de couverture observé : {taux_couverture_experts:.2f}%")
print(f"Taille totale du set test : {nb_total_experts}")
print(f"Nombre d'observations conformes : {nb_conformes_experts}")
print(f"Nombre d'observations non conformes : {nb_non_conformes_experts}")

# %% 8. Test du Chi² 

from scipy.stats import chisquare

obs_exp = [nb_conformes_experts, nb_non_conformes_experts]
exp_exp = [nb_total_experts * confidence, nb_total_experts * (1 - confidence)]

print(f"Observés : conformes = {obs_exp[0]}, non conformes = {obs_exp[1]}")
print(f"Attendus : conformes = {int(exp_exp[0])}, non conformes = {int(exp_exp[1])}")

chi2_stat_exp, p_value = chisquare(f_obs=obs_exp, f_exp=exp_exp)

print(f"Chi² = {chi2_stat_exp:.2f}, p = {p_value:.4e}")

# Interprétation
alpha = 0.05
if p_value < alpha:
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
import json
import numpy as np

# Fonction pour créer l'ensemble de prédiction selon le score
def create_prediction_set(predictions, threshold, score_type):
    prediction_set = []

    if score_type == "one_minus_prob":
        for pred in predictions:
            score = 1 - pred['proba']
            if score < threshold:
                prediction_set.append(pred['name'])

    elif score_type == "sum_until_correct":
        sorted_preds = sorted(predictions, key=lambda x: -x['proba'])
        cumulative = 0
        for pred in sorted_preds:
            if cumulative < threshold:
                prediction_set.append(pred['name'])
            cumulative += pred['proba']

    return prediction_set

# Fonction pour calculer la taille moyenne et médiane
def compute_avg_median_set_size(raw_data, threshold, score_type):
    set_sizes = []

    for obs_id, predictions in raw_data.items():
        pred_set = create_prediction_set(predictions, threshold, score_type)
        set_sizes.append(len(pred_set))

    avg_size = np.mean(set_sizes)
    median_size = np.median(set_sizes)
    return avg_size, median_size

# Charger les fichiers
with open("expert_scores2.json", "r") as f:
    expert_scores = json.load(f)

with open("expert_processed.json", "r") as f:
    expert_processed = json.load(f)

# Filtrer les observations communes
common_ids = set(expert_scores.keys()) & set(expert_processed.keys())
filtered_processed = {k: expert_processed[k] for k in common_ids}

# Définir le type de score et le seuil
score_type = "one_minus_prob"  
threshold = quantile1

# Calcul des tailles
avg, median = compute_avg_median_set_size(filtered_processed, threshold, score_type)

print(f"Taille moyenne : {avg:.2f}")
print(f"Taille médiane : {median}")
