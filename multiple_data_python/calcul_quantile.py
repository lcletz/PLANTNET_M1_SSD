# Couper en deux le fichiers 5_scores.json
#%%
import json
import random

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
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
import numpy as np

# Fonction pour charger les scores
def load_scores(path):
    with open(path, "r") as f:
        data = json.load(f)
    X = []
    y = []
    for _, d in data.items():
        X.append([1 - d["one_minus_prob"][0]])  # Probabilité brute
        y.append(1 if d["sum_until_correct"][0] == 0 else 0)  # 1 = correct direct, 0 sinon
    return np.array(X), np.array(y)

# Chargement des données pour le scénario 1
def scenario_loader():
    X_cal, y_cal = load_scores("5_scores_non_experts.json")
    X_test, y_test = load_scores("5_scores.json")
    return X_cal, y_cal, X_test, y_test

# Main function pour exécuter le scénario
def main():
    print(">> Chargement du scénario 1 (Non-experts pour calibration, Experts pour test)")
    X_cal, y_cal, X_test, y_test = scenario_loader()

    print(f"  Calibrage sur {len(X_cal)} exemples, Test sur {len(X_test)} exemples")

    # Calibration (Platt scaling)
    base_clf = LogisticRegression()
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

# SCENARIO 2
#%%
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss

# === Chargement des données ===
with open("5_scores_part1.json", "r") as f:
    data_calib = json.load(f)

with open("5_scores_part2.json", "r") as f:
    data_test = json.load(f)

# === Fonction d'extraction des features et labels ===
def extract_X_y(data):
    X = []
    y = []
    for entry in data.values():
        X.append([entry["one_minus_prob"][0]])
        y.append(int(entry["sum_until_correct"][0]))  # On s'assure que y est bien un entier
    return np.array(X), np.array(y)

# === Préparation des données ===
X_calib, y_calib = extract_X_y(data_calib)
X_test, y_test = extract_X_y(data_test)

# === Entraînement de la régression logistique (Platt Scaling) ===
base_clf = LogisticRegression()
base_clf.fit(X_calib, y_calib)

# Calibration du classifieur avec Platt scaling
calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method='sigmoid', cv='prefit')

# Pas besoin de refit : cv='prefit' => on a déjà entraîné base_clf
calibrated_clf.fit(X_calib, y_calib)

# === Prédictions sur le set de test ===
y_prob = calibrated_clf.predict_proba(X_test)[:, 1]  # Probabilité de classe 1

# === Calcul du Brier Score ===
brier = brier_score_loss(y_test, y_prob)
print(f"Brier Score sur le set de test : {brier:.4f}")

############### Visualisation ##############################

#%%
import matplotlib.pyplot as plt
import seaborn as sns

# Hypothèses : tu as déjà calculé les Brier Scores pour les deux scénarios.
# Par exemple :
brier_score_scenario_1 = 0.0308  # Exemple de Brier Score du scénario 1
brier_score_scenario_2 = 0.0006  # Exemple de Brier Score du scénario 2

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

# %%
