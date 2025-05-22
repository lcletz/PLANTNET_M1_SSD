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

# %% 4. Identifier les plantes non conformes
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
#fig.write_image("graphique_methode1.svg", width=400, height=250, scale=2)

# %% 
# 7. Statistiques conformes à la théorie de la calibration

# Calcul du taux de couverture uniquement sur les non-experts (set de calibration)
scores_nonexp_array = np.array(scores_nonexp)
nb_conformes_calibration = np.sum(scores_nonexp_array < quantile1)
taux_couverture_calibration = (nb_conformes_calibration / len(scores_nonexp_array)) * 100

print(f"\n Taux de couverture (méthode 1, s1 - calibration) : {taux_couverture_calibration:.2f}% ({nb_conformes_calibration} sur {len(scores_nonexp_array)})")

# Statistiques sur les scores experts (set de test) – informatif seulement
scores_sous_q1 = df[df["Score_s1"] < quantile1]["Score_s1"]
print(f"Taille des données test inférieures au quantile : {len(scores_sous_q1)}")
print(f"Score moyen test inférieur quantile : {scores_sous_q1.mean():.4f}")
print(f"Score médian test inférieur quantile : {scores_sous_q1.median():.4f}")

# %%
