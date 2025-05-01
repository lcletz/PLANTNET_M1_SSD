# Couper en deux le fichiers 5_scores.json
#%%
import json
import random # Pour mélanger

# Charger les scores d'origine
with open("5_scores.json", "r") as f:
    scores = json.load(f)

# Séparer en deux groupes : ceux avec score 0 et ceux avec score > 0
scores_0 = {k: v for k, v in scores.items() if v["sum_until_correct"][0] == 0}
scores_non0 = {k: v for k, v in scores.items() if v["sum_until_correct"][0] != 0}

# Mélanger les clés
keys_0 = list(scores_0.keys())
keys_non0 = list(scores_non0.keys())
random.shuffle(keys_0)
random.shuffle(keys_non0)

# Diviser chaque groupe en deux
mid_0 = len(keys_0) // 2
mid_non0 = len(keys_non0) // 2

part1_keys = keys_0[:mid_0] + keys_non0[:mid_non0]
part2_keys = keys_0[mid_0:] + keys_non0[mid_non0:]

# Créer les deux nouveaux fichiers
scores_part1 = {k: scores[k] for k in part1_keys}
scores_part2 = {k: scores[k] for k in part2_keys}

# Sauvegarde
with open("5_scores_part1.json", "w") as f:
    json.dump(scores_part1, f, indent=2)

with open("5_scores_part2.json", "w") as f:
    json.dump(scores_part2, f, indent=2)

print("Découpage équilibré terminé.")

# SCENARIO 1
# %%
# pip install scikit-learn

import json
import argparse
#  Pour le modèle, la calibration, l’évaluation
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
# pour gérer les tableaux de données
import numpy as np

# Fonction pour charger les scores
def load_scores(path):
    with open(path, "r") as f:
        data = json.load(f)
    X = []
    y = []
    for _, d in data.items():
        X.append([1 - d["one_minus_prob"][0]])                  # Probabilité brute
        y.append(1 if d["sum_until_correct"][0] == 0 else 0)    # 1 = correct direct, 0 sinon
    return np.array(X), np.array(y)

# Chargement des données pour le scénario 1
def scenario_loader():
    X_cal, y_cal = load_scores("5_scores_non_experts.json")     # pour entraîner le modèle de calibration
    X_test, y_test = load_scores("5_scores_part2.json")               # pour tester les prédictions calibrées
    return X_cal, y_cal, X_test, y_test

# Main qui est la fonction pour exécuter le scénario
def main():
    print(">> Chargement du scénario 1 (Non-experts pour calibration, Experts2 pour test)")
    X_cal, y_cal, X_test, y_test = scenario_loader()

    print(f"  Calibrage sur {len(X_cal)} exemples, Test sur {len(X_test)} exemples")

    # Calibration (Platt scaling)
    base_clf = LogisticRegression()                             # modèle de régression logistique
    calibrated_clf = CalibratedClassifierCV(base_clf, method='sigmoid', cv='prefit')

    # Fit sur données de calibration
    base_clf.fit(X_cal, y_cal)
    calibrated_clf.fit(X_cal, y_cal)

    # Prédictions calibrées
    proba_preds = calibrated_clf.predict_proba(X_test)[:, 1]

    # Évaluation (ex: Brier score)
    brier = brier_score_loss(y_test, proba_preds)
    print(f"Brier Score sur le set de test : {brier:.4f}")

if __name__ == "__main__":
    main()


### VISUALISATION SCENARIO 1 ###############################
#%%
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve

# Charger les données 
with open("5_scores.json", "r") as f:
    data = json.load(f)

y_true = []
y_prob = []

for _, entry in data.items():
    # Probabilité brute
    prob = 1 - entry["one_minus_prob"][0]
    y_prob.append(prob)

    # Étiquette binaire : 1 si correct direct, sinon 0
    label = 1 if entry["sum_until_correct"][0] == 0 else 0
    y_true.append(label)

# Conversion en tableaux numpy
y_true = np.array(y_true)
y_prob = np.array(y_prob)

# Courbe de calibration 
prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy='uniform')

# Affichage 
plt.figure(figsize=(6, 6))
plt.plot(prob_pred, prob_true, marker='o', label='Modèle calibré')
plt.plot([0, 1], [0, 1], linestyle='--', label='Calibration parfaite')
plt.xlabel("Probabilité prédite")
plt.ylabel("Probabilité observée")
plt.title("Courbe de calibration (Scénario 1)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# SCENARIO 2
#%%
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss

# Chargement des données 
with open("5_scores_part1.json", "r") as f:
    data_calib = json.load(f)

with open("5_scores_part2.json", "r") as f:
    data_test = json.load(f)

# Fonction d'extraction des features et labels
def extract_X_y(data):
    X = []
    y = []
    for entry in data.values():
        X.append([entry["one_minus_prob"][0]])
        y.append(int(entry["sum_until_correct"][0]))  # On s'assure que y est bien un entier
    return np.array(X), np.array(y)

# Préparation des données 
X_calib, y_calib = extract_X_y(data_calib)
X_test, y_test = extract_X_y(data_test)

# Entraînement de la régression logistique (Platt Scaling)
base_clf = LogisticRegression()
base_clf.fit(X_calib, y_calib)

# Calibration du classifieur avec Platt scaling
calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method='sigmoid', cv='prefit')

# Pas besoin de refit : cv='prefit' => on a déjà entraîné base_clf
calibrated_clf.fit(X_calib, y_calib)

# Prédictions sur le set de test
y_prob = calibrated_clf.predict_proba(X_test)[:, 1]  # Probabilité de classe 1

# Calcul du Brier Score
brier = brier_score_loss(y_test, y_prob)
print(f"Brier Score sur le set de test : {brier:.4f}")

### VISUALISATION SCENARIO 2 ###############################
#%%
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve

# Calcul des courbes de calibration 
prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)

# Tracé de la courbe 
plt.figure(figsize=(6, 6))
plt.plot(prob_pred, prob_true, marker='o', label="Modèle calibré")
plt.plot([0, 1], [0, 1], linestyle='--', color='orange', label="Calibration parfaite")

# Labels & Style
plt.xlabel("Probabilité prédite")
plt.ylabel("Probabilité observée")
plt.title("Courbe de Calibration (Scénario 2)")
plt.legend()
plt.grid()

plt.show()

############### Visualisation ##############################

#%%
import matplotlib.pyplot as plt
import seaborn as sns

brier_score_scenario_1 = 0.0292  # Brier Score du scénario 1
brier_score_scenario_2 = 0.0006  # Brier Score du scénario 2

# Liste des scores et des scénarios
brier_scores = [brier_score_scenario_1, brier_score_scenario_2]
scenarios = ['Scénario 1', 'Scénario 2']

# Création du graphique
plt.figure(figsize=(6, 4))
sns.barplot(x=scenarios, y=brier_scores, palette="Blues_d")

# Ajouter un titre et une étiquette à l'axe Y
plt.title("Comparaison des Brier Scores")
plt.ylabel('Brier Score')

# Affichage du graphique
plt.show()

## Code 1

########################################## Données expertes ##########################################################################################


#%%
import json

# Charger les données
with open("5_scores.json", "r") as file:
    data = json.load(file)

# Extraire les scores de non-conformité
non_conformity_scores = [v["one_minus_prob"][0] for v in data.values()]

# Trier les données
non_conformity_scores.sort()

# Calculer l'indice du quantile
confidence = 0.95
index = confidence * (len(non_conformity_scores) - 1)
lower_idx = int(index)
upper_idx = min(lower_idx + 1, len(non_conformity_scores) - 1)
weight = index - lower_idx

# Interpolation linéaire
quantile = (1 - weight) * non_conformity_scores[lower_idx] + weight * non_conformity_scores[upper_idx]

# Afficher
print(f"Scores de non-conformité : {non_conformity_scores}")
print(f"Quantile à {confidence * 100:.0f}% : {quantile}")


# Graphique avec quantile
#%%
import matplotlib.pyplot as plt
import numpy as np

# Trier les données
non_conformity_scores.sort()

# Calculer l'indice du quantile
confidence = 0.95
index = confidence * (len(non_conformity_scores) - 1)
lower_idx = int(index)
upper_idx = min(lower_idx + 1, len(non_conformity_scores) - 1)
weight = index - lower_idx
quantile = (1 - weight) * non_conformity_scores[lower_idx] + weight * non_conformity_scores[upper_idx]

# Tracer la distribution
plt.figure(figsize=(8, 5))
plt.hist(non_conformity_scores, bins=30, edgecolor="black", alpha=0.7)
plt.axvline(quantile, color="red", linestyle="dashed", linewidth=2, label=f"Quantile {confidence*100:.0f}%")
plt.xlabel("Scores de non-conformité")
plt.ylabel("Fréquence")
plt.title("Distribution des scores et position du quantile")
plt.legend()
plt.show()


# Nuage de point pour scores non conformité et rang cuulatif
#%%
import plotly.express as px
import pandas as pd
import json

# Charger les données JSON
with open("5_scores.json", "r") as file:
    data = json.load(file)

# Extraire les numéros des plantes et les scores de non-conformité
plant_ids = list(data.keys())  # Récupère les identifiants des plantes
non_conformity_scores = [v["one_minus_prob"][0] for v in data.values()]

# Créer un DataFrame avec les numéros et les scores
df = pd.DataFrame({"Score": non_conformity_scores, "Plante_ID": plant_ids})

# Calculer le quantile
confidence = 0.95
quantile = np.percentile(non_conformity_scores, confidence * 100)

# Tracer la CDF interactive avec les numéros de plantes
fig = px.scatter(df, x="Score", y=df.index / len(df), hover_data=["Plante_ID"], title="Score de non-conformité et son rang cumulatif.")

# Ajouter la ligne rouge du quantile
fig.add_vline(x=quantile, line_dash="dash", line_color="red", annotation_text=f"Quantile {confidence*100:.0f}%")

fig.update_layout(xaxis_title="Scores de non-conformité", yaxis_title="Proportion cumulée")

fig.show()



# Test pour voir si avoir une valeur Lamdba sa fonctionne 
 # %%
# Nouvelle prédiction (par exemple, une probabilité 1 - probabilité prédite)
nouvelle_prédiction = 0.3  # Remplacer par la probabilité réelle de la nouvelle prédiction

# Calculer le score de non-conformité pour la nouvelle prédiction
nouveau_score = nouvelle_prédiction

# Vérifier si cette prédiction est conforme
if nouveau_score <= quantile:
    print("La prédiction est conforme à 95% de confiance.")
else:
    print("La prédiction est peu conforme et est considérée comme une anomalie.")

########################################## Données non expertes ##########################################################################################

#%%
import json

# Charger les scores non experts
with open("5_scores_non_expertes.json", "r") as file:
    non_expert_data = json.load(file)

# Extraire et trier les scores
non_expert_scores = sorted([entry["non_conformity_score"] for entries in non_expert_data.values() for entry in entries])

# Calcul de l'indice du quantile
confidence = 0.95
index = confidence * (len(non_expert_scores) - 1)
lower_idx = int(index)
upper_idx = min(lower_idx + 1, len(non_expert_scores) - 1)
weight = index - lower_idx

# Interpolation linéaire si nécessaire
quantile_non_expert = (1 - weight) * non_expert_scores[lower_idx] + weight * non_expert_scores[upper_idx]

# Affichage des scores
print("Scores de non-conformité des données non expertes :")
for score in non_expert_scores:
    print(f"{score:.4f}")

# Affichage du quantile à 95 %
print(f"\nQuantile à {confidence * 100:.0f}%  : {quantile_non_expert: }")


############################################# Comparer les expertes et non-expertes #################################################################################
# %%
import json
import numpy as np
import pandas as pd
import plotly.express as px

# Charger les scores des experts
with open("5_scores.json", "r") as file:
    expert_data = json.load(file)
expert_scores = [v["one_minus_prob"][0] for v in expert_data.values()]

# Charger les scores des non experts
with open("5_scores_non_expertes.json", "r") as file:
    non_expert_data = json.load(file)
non_expert_scores = [entry["non_conformity_score"] for entries in non_expert_data.values() for entry in entries]

# Créer un DataFrame pour la visualisation
df_expert = pd.DataFrame({"Score": expert_scores, "Type": "Expert"})
df_non_expert = pd.DataFrame({"Score": non_expert_scores, "Type": "Non-expert"})
df = pd.concat([df_expert, df_non_expert], ignore_index=True)

# Trier et calculer la CDF pour chaque type
df.sort_values(["Type", "Score"], inplace=True)
df["CDF"] = df.groupby("Type").cumcount() / df.groupby("Type")["Score"].transform("count")

# Calculer les quantiles à 95 %
quantile_expert = np.percentile(expert_scores, 95)
quantile_non_expert = np.percentile(non_expert_scores, 95)

# Tracer la courbe cumulative interactive
fig = px.line(df, x="Score", y="CDF", color="Type", title="Comparaison des distributions - Experts vs Non-experts")

# Ajouter les lignes de quantile
fig.add_vline(x=quantile_expert, line_dash="dash", line_color="blue", annotation_text="Quantile 95% Expert")
fig.add_vline(x=quantile_non_expert, line_dash="dash", line_color="red", annotation_text="Quantile 95% Non-expert")

fig.update_layout(xaxis_title="Scores de non-conformité", yaxis_title="Proportion cumulée")

fig.show()
# %%
