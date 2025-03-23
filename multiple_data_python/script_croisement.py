# ETAPE 0 : Creation du fichier sample.json
#%%
import json

# Fonction de lecture du fichier JSON
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Fonction de lecture du fichier texte ground_truth.txt
def load_ground_truth(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Lire chaque ligne, retirer les espaces et les nouvelles lignes, puis les convertir en entier
        return [int(line.strip()) for line in file.readlines()]

# Charger les fichiers nécessaires
ai_answers = load_json("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_answers.json")  # ID des espèces
ai_classes = load_json("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_classes.json")  # Noms des classes
ai_scores = load_json("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_scores.json")  # Scores de prédictions
tasks = load_json("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json")  # Tâches (task_id -> observation)
ground_truth = load_ground_truth("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/answers/ground_truth.txt")  # Vérités terrain

# Créer la structure de données unifiée
sample_data = []

# Parcourir les tâches pour organiser les données
for task_id, obs_id in tasks.items():
    species_id = ai_answers.get(str(obs_id), -1)  # Récupérer l'ID de l'espèce, ou -1 si non trouvé
    class_name = next((name for name, class_id in ai_classes.items() if class_id == species_id), None)
    score = ai_scores.get(str(obs_id), 0)  # Récupérer le score, ou 0 si non trouvé

    # Gérer les cas où la vérité terrain est -1 (invalide ou non définie)
    if obs_id < len(ground_truth):
        correct = 1 if ground_truth[obs_id] == species_id and ground_truth[obs_id] != -1 else 0
    else:
        correct = 0

    # Créer un dictionnaire pour chaque entrée
    sample_data.append({
        "task_id": task_id,
        "obs_SWE": str(obs_id),
        "id_SWE": species_id,
        "class_name": class_name,
        "score": score,
        "prediction": species_id,
        "correct": correct
    })

# Sauvegarder le fichier sample.json
output_file_path = '/home/anne-laure/projet/PLANTNET_M1_SSD/multiple_data_python/sample.json'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(sample_data, output_file, indent=4)

print(f"Fichier {output_file_path} généré avec succès.")

#################################################################################################################################

# VERIFIE SI DOSSIER 00 EXISTE
# %%
import os

# Chemin relatif vers le dossier 00
chemin = os.path.join(os.getcwd(), 'kswe_20250117_00', '00')

if not os.path.isdir(chemin):
    print(f"Le dossier '{chemin}' n'existe pas.")
    raise Exception(f"Le dossier '{chemin}' est introuvable. Veuillez vérifier le chemin.")
else:
    print(f"Le dossier '{chemin}' existe.")


#################################################################################################################################


# ETAPE 1 : Création du fichier 1_predictions.json
# %%
import os
import json

def process_plant_data_advanced():
    # Utiliser le chemin correct du dossier "00"
    chemin = os.path.join(os.getcwd(), 'kswe_20250117_00', '00')
    
    # Lister les sous-dossiers dans "00"
    subdirs = [subdir for subdir in os.listdir(chemin) if os.path.isdir(os.path.join(chemin, subdir))]
    print(f"Sous-dossiers trouvés : {len(subdirs)}")
    
    # Initialiser une liste vide pour stocker les résultats
    all_results = {}
    
    # Pour chaque sous-répertoire
    for subdir in subdirs:
        # Lister tous les fichiers JSON dans le sous-répertoire
        json_files = [f for f in os.listdir(os.path.join(chemin, subdir)) if f.endswith('.json')]
        
        for file in json_files:
            file_path = os.path.join(chemin, subdir, file)
            
            # Lire le fichier JSON
            try:
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
                continue
            
            # Vérifier si la clé 'results' existe et est une liste
            if 'results' not in json_data or not isinstance(json_data['results'], list) or len(json_data['results']) == 0:
                print(f"Le fichier {file_path} ne contient pas de données valides dans 'results'.")
                continue
            
            # Extraire l'ID d'observation du nom du fichier
            obs_id = os.path.splitext(file)[0]
            
            # Créer une liste de noms et probabilités
            result = []
            for entry in json_data['results']:
                if 'name' in entry and 'id' in entry and 'score' in entry:
                    entry_data = {
                        'name': entry['name'],
                        'obs': entry['id'],
                        'proba': entry['score']
                    }
                    result.append(entry_data)
            
            # Ajouter cette observation aux résultats
            all_results[obs_id] = result
        
        print(f"Traitement du dossier {subdir} terminé ({len(json_files)} fichiers traités)")
    
    # Vérifier si des résultats ont été collectés
    if len(all_results) == 0:
        print("Aucun fichier JSON valide n'a été traité.")
        return None
    
    # Sauvegarder les résultats finaux sous forme de fichier JSON
    output_path = '1_predictions.json'
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=4)
    
    print(f"\nSUCCÈS: Fichier créé avec succès à: {os.path.abspath(output_path)}")
    
    return all_results

# Exécuter la fonction
process_plant_data_advanced()


#################################################################################################################################

# ETAPE 2 : Croiser les prédictions avec les classes réelles (ai_classes.json) et création du fichier 2_predictions_classes.json
# %%
import json

# Charger un fichier JSON
def load_json(file_path):
    """Charger un fichier JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Fusionner les prédictions avec les classes réelles
def merge_predictions_with_classes(predictions_file, classes_file, output_file):
    # Charger les fichiers JSON
    predictions = load_json(predictions_file)  # Prédictions au format {'id': [{'name': '...', 'obs': ..., 'proba': ...}]}
    ai_classes = load_json(classes_file)  # Classes réelles au format {'Nom de plante': classe_id}

    # Créer un dictionnaire pour accéder rapidement aux classes réelles par nom de plante
    # Ici, ai_classes est déjà un dictionnaire clé=nom_plante, valeur=classe_id

    # Liste pour stocker les résultats combinés
    merged_results = {}

    # Parcourir chaque identifiant dans les prédictions
    for plant_id, predictions_list in predictions.items():
        # Initialiser une liste pour stocker les résultats fusionnés pour cette plante
        merged_results[plant_id] = []
        
        for prediction in predictions_list:
            plant_name = prediction['name']
            # Trouver la classe réelle à partir du nom de la plante
            if plant_name in ai_classes:
                actual_class = ai_classes[plant_name]
                # Ajouter la classe réelle aux données de prédiction
                merged_entry = {
                    'name': plant_name,
                    'obs': prediction['obs'],
                    'proba': prediction['proba'],
                    'class': actual_class  # Ajout de la classe réelle
                }
                merged_results[plant_id].append(merged_entry)

    # Sauvegarder les résultats dans un nouveau fichier JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_results, f, ensure_ascii=False, indent=4)
    print(f"Résultats fusionnés sauvegardés dans {output_file}")

# Chemins des fichiers
predictions_file = '/home/anne-laure/projet/PLANTNET_M1_SSD/multiple_data_python/1_predictions.json'
classes_file = '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_classes.json'
output_file = '2_predictions_classes.json'

# Exécuter la fonction
merge_predictions_with_classes(predictions_file, classes_file, output_file)


#################################################################################################################################


# ETAPE 2bis : Découper en plusieurs sous-fichiers 2_prediction_classes.json
# %%
import json
import os

# Récupérer le répertoire où se trouve le script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Charger le fichier 2_predictions_classes.json
with open('2_predictions_classes.json', 'r') as f:
    data = json.load(f)

# Diviser les données en 7 parties égales
num_parts = 7
part_size = len(data) // num_parts
remainder = len(data) % num_parts

# Découper les données en 7 sous-fichiers
for i in range(num_parts):
    start_idx = i * part_size
    end_idx = (i + 1) * part_size
    if i == num_parts - 1:  # Pour le dernier fichier, ajouter le reste
        end_idx += remainder
    
    # Extraire la partie des données
    split_data = dict(list(data.items())[start_idx:end_idx])

    # Nom du fichier découpé avec le chemin complet
    output_file = os.path.join(script_dir, f"2.{i+1}_prediction_sample_{i+1}.json")

    # Sauvegarder le fichier découpé
    with open(output_file, 'w') as f_out:
        json.dump(split_data, f_out, indent=4)

    print(f"Fichier découpé sauvegardé : {output_file}")

print("Découpage terminé.")


#################################################################################################################################


# ETAPE 3 : Création de 3_trues_classes.json
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


#################################################################################################################################

### PROBLEMMMMEEEEE


# ETAPE 4 : Croiser les prédictions avec les classes réelles et marquer les prédictions correctes
# %%
import json
import os

# Fonction pour croiser les prédictions avec les classes réelles
def cross_check_predictions(predictions_file, true_classes_file, output_file):
    # Charger les fichiers JSON
    with open(predictions_file, 'r') as f:
        predictions_data = json.load(f)
    
    with open(true_classes_file, 'r') as f:
        true_classes_data = json.load(f)

    # Créer un dictionnaire pour accéder rapidement aux classes réelles par observation ID
    true_classes_dict = {}
    for item in true_classes_data:
        for obs_id, values in item.items():
            true_classes_dict[str(obs_id)] = values['id_SWE']

    # Croiser les prédictions avec les classes réelles
    for obs_id, predictions in predictions_data.items():
        for prediction in predictions:
            # Vérification : si une classe réelle existe pour cette observation
            if str(prediction['obs']) in true_classes_dict:
                # Comparer la classe prédite avec la classe réelle
                if prediction['class'] == true_classes_dict[str(prediction['obs'])]:
                    prediction['correct'] = 1  # Prédiction correcte
                else:
                    prediction['correct'] = 0  # Prédiction incorrecte
            else:
                prediction['correct'] = 0  # Pas de classe réelle pour cette observation

    # Sauvegarder les résultats croisés dans un fichier
    with open(output_file, 'w') as f_out:
        json.dump(predictions_data, f_out, indent=4)

    print(f"Fichier croisé sauvegardé : {output_file}")

# Exemple d'utilisation pour chaque sous-fichier découpé
script_dir = os.getcwd()

for i in range(1, 8):
    predictions_file = os.path.join(script_dir, f"2.{i}_prediction_sample_{i}.json")
    output_file = os.path.join(script_dir, f"4.{i}_results_{i}.json")
    cross_check_predictions(predictions_file, '3_trues_classes.json', output_file)

print("Croisement des prédictions terminé.")

# SOLUTION ?
#%%
import json
import os

# Fonction pour croiser les prédictions avec les classes réelles
def cross_check_predictions(predictions_file, true_classes_file, output_file):
    # Charger les fichiers JSON
    with open(predictions_file, 'r') as f:
        predictions_data = json.load(f)
    
    with open(true_classes_file, 'r') as f:
        true_classes_data = json.load(f)

    # Créer un dictionnaire pour accéder rapidement aux classes réelles par observation ID
    true_classes_dict = {}
    for item in true_classes_data:
        for obs_id, values in item.items():
            true_classes_dict[str(values['obs_SWE'])] = int(values['id_SWE'])  # Assurez-vous que id_SWE est un entier

    # Débogage : vérifier le contenu du dictionnaire des classes réelles
    print("Dictionnaire des classes réelles : ", true_classes_dict)

    # Croiser les prédictions avec les classes réelles
    for obs_id, predictions in predictions_data.items():
        for prediction in predictions:
            # Débogage : vérifier l'ID de l'observation et sa classe prédite
            print(f"Vérification pour obs_id = {obs_id}, classe prédite = {prediction['class']}")
            
            # Vérification : si une classe réelle existe pour cette observation
            if str(prediction['obs']) in true_classes_dict:
                # Comparer la classe prédite avec la classe réelle
                real_class = true_classes_dict[str(prediction['obs'])]
                if prediction['class'] == real_class:
                    prediction['correct'] = 1  # Prédiction correcte
                    print(f"Prédiction correcte pour {obs_id}")
                else:
                    prediction['correct'] = 0  # Prédiction incorrecte
                    print(f"Prédiction incorrecte pour {obs_id}")
            else:
                prediction['correct'] = 0  # Pas de classe réelle pour cette observation
                print(f"Pas de classe réelle pour obs_id = {obs_id}")

    # Sauvegarder les résultats croisés dans un fichier
    with open(output_file, 'w') as f_out:
        json.dump(predictions_data, f_out, indent=4)

    print(f"Fichier croisé sauvegardé : {output_file}")

# Exemple d'utilisation pour chaque sous-fichier découpé
script_dir = os.getcwd()

for i in range(1, 8):
    predictions_file = os.path.join(script_dir, f"2.{i}_prediction_sample_{i}.json")
    output_file = os.path.join(script_dir, f"4.{i}_results_{i}.json")
    cross_check_predictions(predictions_file, '3_trues_classes.json', output_file)

print("Croisement des prédictions terminé.")

#################################################################################################################################

# ETAPE 5 : Calcul des scores 
# %%
import json
import os

def calculate_scores(data):
    scores = {}

    # Parcourir chaque observation
    for obs_id, predictions in data.items():
        cumulative_prob = 0
        found_correct = False

        # Parcourir les prédictions dans l'ordre
        for prediction in predictions:
            if prediction.get('correct') == 1:
                # Si la prédiction est correcte : on arrête sans ajouter sa proba
                found_correct = True
                break
            else:
                # Si la prédiction est incorrecte : ajouter sa probabilité
                cumulative_prob += prediction.get('proba', 0)

        # Si une prédiction correcte a été trouvée : on calcule le score
        if found_correct:
            scores[obs_id] = 1 - cumulative_prob
        else:
            # Si aucune prédiction correcte n'a été trouvée : attribuer 0
            scores[obs_id] = 0

    return scores

def save_scores(scores, output_file):
    with open(output_file, 'w') as f_out:
        json.dump(scores, f_out, indent=4)

    print(f"Scores sauvegardés dans {output_file}")

# Exemple d'utilisation pour chaque fichier de résultats
script_dir = os.getcwd()

for i in range(1, 8):
    results_file = os.path.join(script_dir, f"4.{i}_results_{i}.json")
    output_file = os.path.join(script_dir, f"5_scores_{i}.json")
    
    # Charger les données
    with open(results_file, 'r') as f:
        data = json.load(f)

    # Calculer les scores
    scores = calculate_scores(data)

    # Sauvegarder les scores
    save_scores(scores, output_file)

# Sauvegarder les scores dans un fichier global "5_scores.json"
with open(os.path.join(script_dir, "5_scores.json"), 'w') as f_out:
    json.dump(scores, f_out, indent=4)

print("Calcul des scores terminé et sauvegardé dans '5_scores.json'.")
