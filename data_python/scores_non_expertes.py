# Calcul des scores des données non expertes 
#%%
import json

# Charger les données JSON
with open("samples_user_answers.json", "r") as file:
    data = json.load(file)

# Fonction pour calculer les scores comme pour les experts
def calculate_non_expert_scores(data):
    scores = {}

    for plant_id, predictions in data.items():
        cumulative_prob = 0
        score_du_vrai = 0
        score_somme = 0
        found_correct = False

        for pred in predictions:
            if pred.get('correct') == 1:
                found_correct = True
                score_du_vrai = round(1 - pred.get('proba', 0), 4)
                score_somme = round(cumulative_prob, 4)
                break
            else:
                cumulative_prob += pred.get('proba', 0)

        if found_correct:
            scores[plant_id] = {
                "one_minus_prob": [score_du_vrai],
                "sum_until_correct": [score_somme]
            }
        else:
            scores[plant_id] = {
                "one_minus_prob": [0.999],
                "sum_until_correct": [0.001]
            }

    return scores

# Calculer les scores
scores_non_experts = calculate_non_expert_scores(data)

# Sauvegarder dans un fichier JSON
with open("5_scores_non_experts.json", "w") as outfile:
    json.dump(scores_non_experts, outfile, indent=4)

print("Fichier '5_scores_non_experts.json' créé avec succès !")

# %%
