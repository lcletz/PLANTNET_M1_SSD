# Code pour crée le fichier "3_trues_classes.json"
#%%

import os
import json
import pandas as pd

# Chargement des données
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

# Utilisation des chemins relatifs
tasks = load_json("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json")
ai_answers = load_json("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_answers.json")

# Conversion en DataFrame
print("Conversion des données...")
tasks_df = pd.DataFrame({
    'task_id': list(tasks.keys()),
    'task_value': list(map(str, tasks.values()))
})
ai_answers_df = pd.DataFrame({
    'task_value': list(ai_answers.keys()),
    'answer_value': list(ai_answers.values())
})
print("Conversion des données terminée")

# Croisement des données par lots
print("Traitement des données par lots...")
batch_size = 500000
resultats_list = []

# Traitement par lot
for i in range(0, len(tasks_df), batch_size):
    print(f"Traitement du lot {i//batch_size + 1} sur {len(tasks_df) // batch_size + 1}...")
    batch = tasks_df.iloc[i:i + batch_size]
    result_batch = pd.merge(batch, ai_answers_df, on='task_value', how='left')

    # Format de sortie
    for _, row in result_batch.iterrows():
        resultats_list.append({
            row['task_id']: {
                'obs_SWE': row['task_value'],
                'id_SWE': None if pd.isna(row['answer_value']) else int(row['answer_value'])
            }
        })

print("Traitements terminés")

# Écriture du résultat final en JSON
print("Écriture du fichier JSON final...")
with open(os.path.join(".", "3_trues_classes.json"), 'w', encoding='utf-8') as file:
    json.dump(resultats_list, file, indent=4, ensure_ascii=False)

print("Traitement terminé avec succès !")


# Code pour crée 1_prediction et 2_prediction

#%%
import json
import os

# Charger le fichier 3_trues_classes.json
with open("3_trues_classes.json", 'r', encoding='utf-8') as file:
    data = json.load(file)

# Création de 1_predictions.json
predictions = {str(k): v['id_SWE'] for item in data for k, v in item.items()}
with open("1_predictions.json", 'w', encoding='utf-8') as file:
    json.dump(predictions, file, indent=4, ensure_ascii=False)

# Création de 2_predictions_classes.json
predictions_classes = [
    {
        "task_id": str(k),
        "obs_SWE": v['obs_SWE'],
        "id_SWE": v['id_SWE']
    }
    for item in data for k, v in item.items()
]

with open("2_predictions_classes.json", 'w', encoding='utf-8') as file:
    json.dump(predictions_classes, file, indent=4, ensure_ascii=False)

print("Fichiers créés avec succès : 1_predictions.json et 2_predictions_classes.json")

# Découpage du fichier en sous-fichiers

# %%
import math

def split_json_file(input_path, num_parts):
    # Charger le fichier JSON
    with open(input_path) as f:
        data = json.load(f)

    # Calculer la taille de chaque sous-fichier
    chunk_size = math.ceil(len(data) / num_parts)

    # Diviser les données en sous-ensembles
    for i in range(num_parts):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(data))

        sub_data = data[start_idx:end_idx]

        output_file = f"{input_path.rsplit('.', 1)[0]}_part_{i+1}.json"
        with open(output_file, 'w') as f:
            json.dump(sub_data, f, indent=4)

        print(f"Sous-fichier {output_file} créé.")

# Découper le fichier "2_predictions_classes.json" en 7 sous-fichiers
split_json_file(os.path.join("2_predictions_classes.json"), 7)


# %%
