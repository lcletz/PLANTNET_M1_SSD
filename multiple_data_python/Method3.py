# %%
# 1. Charger les scores non experts depuis le zip
import zipfile
import json
import numpy as np

zip_path = "15353081.zip"
confidence = 0.95
scores = []

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    for i in range(1, 35):
        filename = f"scores_nonexp_{i:02d}.json"
        if filename in zip_ref.namelist():
            with zip_ref.open(filename) as f:
                data = json.load(f)
                for valeurs in data.values():
                    if "sum_until_correct" in valeurs and isinstance(valeurs["sum_until_correct"], list):
                        scores.append(valeurs["sum_until_correct"][0])
        else:
            print(f"[Info] Fichier manquant : {filename}")

# 2. Calculer le quantile
quantile3 = np.quantile(scores, confidence)
print(f"\nQuantile à {confidence*100:.0f}% basé sur les non-experts : {quantile3:.4f}")

# 3. Charger les données de la moitié des scores des EXPERTS pour test
with open("expert_scores2.json", "r") as f:
    expert_data_full = json.load(f).values()  

test_scores2 = [v["sum_until_correct"][0] for v in expert_data_full 
               if v.get("sum_until_correct") and isinstance(v["sum_until_correct"], list)]

# 4. Tester la conformité
results = [
    ("conforme" if score < quantile3 else "non conforme", score)
    for score in test_scores2
]

# Affichage
print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results):
    print(f"Plante {i+1:02d} - Score : {score:.4f} → {status}")

# %% Est-ce qu'il y a des plantes avec des scores non conformes ?
import json

# Charger les données JSON
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Définir le seuil de conformité
quantile3

# Extraire les scores correctement
non_conformes = {plante: valeurs["sum_until_correct"][0] for plante, valeurs in data.items() if valeurs["sum_until_correct"][0] >= quantile3}

# Afficher les résultats
print("Plantes non conformes :", non_conformes)
print("Nombre total de plantes non conformes :", len(non_conformes))  

#%% Plante : Daphne Striata Tratt.

# Liste des IDs de plantes à vérifier
plante_ids = ["1004046780", "1014153815", "1011331452", "1013910015"]

# Vérification
for pid in plante_ids:
    if pid in non_conformes:
        print(f"La plante {pid} est non conforme avec un score de {non_conformes[pid]:.4f}")
    else:
        print(f"La plante {pid} est conforme.")
        
# %% Visualisation
import json
import pandas as pd
import numpy as np
import plotly.express as px
import kaleido

# Charger les données expertes
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    expert_test_data = json.load(f)

# Extraire les IDs et les scores s2 (sum_until_correct)
plante_ids = list(expert_test_data.keys())
scores_s2 = [v["sum_until_correct"][0] for v in expert_test_data.values() if "sum_until_correct" in v]

# Construire le DataFrame
df_method3 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s2": scores_s2
})

# Ajouter un index pour l’axe Y
df_method3["Index"] = range(len(df_method3))

# Déterminer la conformité
df_method3["Conforme"] = df_method3["Score_s2"].apply(lambda x: "Vrai" if x < quantile3 else "Faux")

# Création du nuage de points
fig = px.scatter(
    df_method3,
    x="Score_s2",
    y="Index",
    color="Conforme",
    color_discrete_map={"Vrai": "#B08FC7", "Faux": "#FF69B4"},
    title="Méthode 3 : s2 + non expert",
    labels={"Score_s2": "Score s2", "Index": "Observations testées", "Conforme": "Conformité"},
    opacity=0.4
)

# Ligne de seuil (quantile)
fig.add_vline(
    x=quantile3,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile 95% = {quantile3:.4f}",
    annotation_position="top left",
    annotation_font_size=12
)

# Mise à jour des axes
fig.update_layout(
    width=800,
    height=500,
    showlegend=True,
    margin=dict(l=60, r=30, t=50, b=60),
    yaxis=dict(
        tickformat="",
        showticklabels=False  
    ),
    xaxis=dict(
        range=[0, 1],
        dtick=0.1
    )
)

fig.show()

# Sauvegarde
fig.write_image("graphique_methode3.svg")

# %% Calcul du pourcentage de plantes conformes
nb_total3 = len(df_method3)
nb_conformes3 = (df_method3["Conforme"] == "Vrai").sum()
taux_couverture3 = (nb_conformes3 / nb_total3) * 100
print(f"\nTaux de couverture (méthode 3, s2) : {taux_couverture3:.2f}% ({nb_conformes3} sur {nb_total3})")

# Filtrer les scores en dessous du quantile
scores_sous_quantile3 = [s for s in df_method3["Score_s2"] if s < quantile3]

# Calcul de la moyenne et de la médiane
moyenne3 = np.mean(scores_sous_quantile3)
mediane3 = np.median(scores_sous_quantile3)

# Affichage des résultats
print(f"Taille des données inférieures au quantile : {len(scores_sous_quantile3)}")
print(f"Score moyen des données inférieures au quantile : {moyenne3:.4f}")
print(f"Score médian des données inférieures au quantile : {mediane3:.4f}")

# %%
