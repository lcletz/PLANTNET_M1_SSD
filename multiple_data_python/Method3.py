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
    ("conforme" if score <= quantile3 else "non conforme", score)
    for score in test_scores2
]

# Affichage
print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results):
    print(f"Plante {i+1:02d} - Score : {score:.4f} → {status}")

# Est-ce qu'il y a des plantes avec des scores non conformes ?
# %%
import json

# Charger les données JSON
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Définir le seuil de conformité
quantile3

# Extraire les scores correctement
non_conformes = {plante: valeurs["sum_until_correct"][0] for plante, valeurs in data.items() if valeurs["sum_until_correct"][0] > quantile3}

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
scores = [v["sum_until_correct"][0] for v in expert_test_data.values() if "sum_until_correct" in v]

# Recréer le DataFrame
df3 = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s2": scores
})

# Déterminer la conformité par rapport au quantile
df3["Conforme"] = df3["Score_s2"] <= quantile3

# Créer le scatter plot avec les couleurs demandées
fig = px.scatter(
    df3,
    x="Score_s2",
    y=df3.index,
    color="Conforme",
    color_discrete_map={True: "#B08FC7", False: "#FF69B4"},  
    hover_data=["Plante_ID"],
    title="Method3 : s2 + non expert",
    labels={"Score_s2": "Score cumulatif s2", "index": "Index plante"}
)

# Ajouter la ligne rouge du quantile
fig.add_vline(
    x=quantile3,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile 95% = {quantile3:.4f}",
    annotation_position="top right"
)

fig.update_layout(
    yaxis_title="Plants tested",
    xaxis_title="Score s2",
    showlegend=True
)

fig.show()

# Enregistrement PNG statique
fig.write_image("graphique_method3.png")

# %%
# Calcul du pourcentage de plantes conformes
nb_total3 = len(df3)
nb_conformes3 = df3["Conforme"].sum()
taux_couverture3 = (nb_conformes3 / nb_total3) * 100
print(f"\nTaux de couverture (méthode 3, s2) : {taux_couverture3:.2f}% ({nb_conformes3} sur {nb_total3})")

# Filtrer les scores en dessous ou égaux au quantile
scores_sous_quantile3 = [s for s in df3["Score_s2"] if s <= quantile3]

# Calcul de la moyenne et de la médiane
moyenne3 = np.mean(scores_sous_quantile3)
mediane3 = np.median(scores_sous_quantile3)

# Affichage des résultats
print(f"Taille des données ≤ quantile : {len(scores_sous_quantile3)}")
print(f"Taille moyenne des scores ≤ quantile : {moyenne3:.4f}")
print(f"Taille médiane des scores ≤ quantile : {mediane3:.4f}")
# %%
