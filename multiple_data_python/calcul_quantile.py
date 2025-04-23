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

# %%
