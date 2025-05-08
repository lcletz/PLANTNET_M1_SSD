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
                    if "one_minus_prob" in valeurs and isinstance(valeurs["one_minus_prob"], list):
                        scores.append(valeurs["one_minus_prob"][0])
        else:
            print(f"[Info] Fichier manquant : {filename}")

# 2. Calculer le quantile
quantile1 = np.quantile(scores, confidence)
print(f"\nQuantile à {confidence*100:.0f}% basé sur les non-experts : {quantile1:.4f}")

# 3. Charger les données de la moitié des scores des EXPERTS pour test
with open("expert_scores2.json", "r") as f:
    expert_data_full = json.load(f).values()  

# Score S1 = "one_minus_prob"[0]
test_scores = [v["one_minus_prob"][0] for v in expert_data_full 
               if v.get("one_minus_prob") and isinstance(v["one_minus_prob"], list)]

# 4. Tester la conformité
results = [
    ("conforme" if score <= quantile1 else "non conforme", score)
    for score in test_scores
]

# Affichage
print("\nRésultats du test sur moitié des données expertes :")
for i, (status, score) in enumerate(results):
    print(f"Plante {i+1:02d} - Score : {score:.4f} → {status}")

# Est-ce qu'il y a des plantes avec des scores non conformes ?
# %%
import json

# Charger les données JSON
with open("expert_scores2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Définir le seuil de conformité
quantile1

# Extraire les scores correctement (en prenant le premier élément de la liste)
non_conformes = {plante: valeurs["one_minus_prob"][0] for plante, valeurs in data.items() if valeurs["one_minus_prob"][0] > quantile1}

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
scores = [v["one_minus_prob"][0] for v in expert_test_data.values() if "one_minus_prob" in v]

# Recréer le DataFrame
df = pd.DataFrame({
    "Plante_ID": plante_ids,
    "Score_s1": scores
})

# Déterminer la conformité par rapport au quantile (déjà défini plus tôt)
df["Conforme"] = df["Score_s1"] <= quantile1

# Créer le scatter plot
fig = px.scatter(
    df,
    x="Score_s1",
    y=df.index,
    color="Conforme",
    color_discrete_sequence=["#B08FC7"],
    hover_data=["Plante_ID"],
    title="Method1 : s1 + non expert",
    labels={"Score_s1": "Score de non-conformité s1", "index": "Index plante"}
)

# Ajouter la ligne rouge du quantile
fig.add_vline(
    x=quantile1,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Quantile 95% = {quantile1:.3f}",
    annotation_position="top left",  
    annotation_font_size=12
)

fig.update_layout(
    xaxis=dict(range=[0, 1.1]),  
    yaxis_title="Plants tested",
    xaxis_title="Score s1",
    showlegend=True
)

fig.show()

# Enregistrement PNG statique
fig.write_image("graphique_method1.png")

# %% 
# Calcul du pourcentage de plantes conformes
nb_total = len(df)
nb_conformes = df["Conforme"].sum()
taux_couverture = (nb_conformes / nb_total) * 100
print(f"\nTaux de couverture (méthode 1, s1) : {taux_couverture:.2f}% ({nb_conformes} sur {nb_total})")

# Filtrer les scores en dessous ou égaux au quantile
scores_sous_quantile1 = [s for s in df["Score_s1"] if s <= quantile1]

# Calcul de la moyenne et de la médiane
moyenne1 = np.mean(scores_sous_quantile1)
mediane1 = np.median(scores_sous_quantile1)

# Affichage des résultats
print(f"Taille des données ≤ quantile : {len(scores_sous_quantile1)}")
print(f"Taille moyenne des scores ≤ quantile : {moyenne1:.4f}")
print(f"Taille médiane des scores ≤ quantile : {mediane1:.4f}")

# %%
