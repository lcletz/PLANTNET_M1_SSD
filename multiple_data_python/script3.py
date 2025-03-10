#%%
import json
import os

# Chargement des fichiers
def load_json(file_path):
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier {file_path} est introuvable.")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Mise à jour des chemins d'accès vers les bons dossiers
tasks = load_json("extracted_data/converters/tasks.json")
ai_answers = load_json("extracted_data/aggregation/ai_answers.json")
ai_classes = load_json("extracted_data/aggregation/ai_classes.json")
answers = load_json("extracted_data/answers/answers.json")
output = load_json("multiple_data_python/output.json")

def get_swe_ids_from_output(output):
    result = {}
    for obs_id, scores in output.items():
        plant_ids = list(scores.keys())  # Les plant_ids sont déjà des SWE_ids
        result[obs_id] = [int(plant_id) for plant_id in plant_ids if plant_id.isdigit()]
    return result

def get_swe_ids_from_tasks(tasks, ai_answers):
    result = {}
    for obs_id, class_id in tasks.items():
        if str(class_id) in ai_answers:
            result[obs_id] = ai_answers[str(class_id)]
    return result

# Étape 1 : Associer IDs SWE aux observations via output 
output_with_swe = get_swe_ids_from_output(output)

# Étape 2 : Associer IDs SWE aux observations via tasks et ai_answers
tasks_with_swe = get_swe_ids_from_tasks(tasks, ai_answers)

# Étape 3 : Fusionner les résultats
final_result = {obs_id: {"output_swe_ids": output_with_swe.get(obs_id, []),
                         "task_swe_id": tasks_with_swe.get(obs_id)}
                for obs_id in set(output_with_swe) | set(tasks_with_swe)}

# Enregistrement du résultat
with open("final_result.json", "w", encoding="utf-8") as f:
    json.dump(final_result, f, indent=4)

print("Fusion des données terminée. Résultat enregistré dans 'final_result.json'")



# %%
