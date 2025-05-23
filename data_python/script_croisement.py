# ETAPE 0 : Creation de plusieurs fichiers sample.json (car trop lourd)
#%%
import json
import os
import math

# Fonction pour sauvegarder en plusieurs fichiers
def save_in_n_chunks(data, base_path, num_chunks=7):
    os.makedirs(os.path.dirname(base_path), exist_ok=True)  # S'assurer que le dossier existe
    chunk_size = math.ceil(len(data) / num_chunks)  # Taille de chaque chunk

    for i in range(num_chunks):
        start_index = i * chunk_size
        end_index = min((i + 1) * chunk_size, len(data))  # Évite d'aller trop loin

        chunk = data[start_index:end_index]
        chunk_file = f"{base_path}_part_{i + 1}.json"
        with open(chunk_file, 'w', encoding='utf-8') as output_file:
            json.dump(chunk, output_file, indent=4)
        
        print(f"Fichier {chunk_file} généré avec succès ({len(chunk)} éléments).")

# Sauvegarder en 7 fichiers
output_base_path = '/home/anne-laure/projet/PLANTNET_M1_SSD/multiple_data_python/sample'
save_in_n_chunks(sample_data, output_base_path, num_chunks=7)

#################################################################################################################################

# VERIFIE SI DOSSIER 00 EXISTE BIEN DANS LE DOSSIER .tar
# %%
import tarfile
import os

# Chemin du fichier TAR
chemin_tar = os.path.join(os.getcwd(), 'kswe_20250117.tar')

# Vérifier si le fichier TAR existe
if not os.path.isfile(chemin_tar):
    print(f"Le fichier '{chemin_tar}' n'existe pas.")
    raise Exception(f"Le fichier '{chemin_tar}' est introuvable. Veuillez vérifier le chemin.")

# Ouvrir le fichier TAR et lister son contenu
with tarfile.open(chemin_tar, 'r') as archive:
    fichiers_dans_tar = archive.getnames()  # Liste des fichiers/dossiers dans le .tar
    
    # Vérifier si le dossier "00" est présent dans le TAR
    dossier_00_present = any(nom.startswith("kswe_20250117_00") for nom in fichiers_dans_tar)

    if dossier_00_present:
        print("Le dossier '00' est bien présent dans le fichier TAR.")
    else:
        print("Le dossier '00' est introuvable dans le fichier TAR.")


#################################################################################################################################


# ETAPE 1 : Création du fichier 1_predictions.json
#%%
import os
import json
import tarfile
import math

def process_plant_data_advanced(chemin_tar, output_base='1_predictions_part', files_per_chunk=50000):
    """Traite les fichiers JSON dans un fichier .tar contenant des archives .tgz et découpe les résultats en plusieurs fichiers."""

    # Ouvrir le fichier tar principal
    with tarfile.open(chemin_tar, 'r') as archive:
        # Lister tous les fichiers dans l'archive .tar
        fichiers_dans_tar = archive.getnames()
        print(f"Fichiers présents dans l'archive : {fichiers_dans_tar[:10]}...")  # Afficher les 10 premiers fichiers

        # Filtrer pour ne récupérer que les fichiers .tgz
        tgz_files = [f for f in fichiers_dans_tar if f.endswith('.tgz')]
        print(f"Fichiers .tgz trouvés : {len(tgz_files)}")

        # Initialiser un compteur pour les fichiers JSON traités
        processed_count = 0
        chunk_count = 1
        all_results = []

        # Parcourir chaque fichier .tgz
        for tgz_file in tgz_files:
            try:
                # Extraire l'archive .tgz contenue dans le fichier .tar
                with archive.extractfile(tgz_file) as tgz_f:
                    with tarfile.open(fileobj=tgz_f, mode='r:gz') as tgz_archive:
                        # Lister tous les fichiers JSON dans l'archive .tgz
                        json_files = [f for f in tgz_archive.getnames() if f.endswith('.json')]
                        print(f"Fichiers JSON trouvés dans {tgz_file}: {len(json_files)}")

                        # Parcourir chaque fichier JSON dans l'archive .tgz
                        for json_file in json_files:
                            try:
                                # Extraire et ouvrir le fichier JSON à partir de l'archive .tgz
                                with tgz_archive.extractfile(json_file) as f:
                                    # Lire le fichier JSON par morceaux pour éviter un surchargement mémoire
                                    json_data = ''
                                    for line in f:
                                        json_data += line.decode('utf-8')

                                    # Charger le JSON une fois qu'il a été entièrement lu
                                    try:
                                        json_data = json.loads(json_data)

                                        # Vérifier si le fichier JSON est vide ou mal formaté
                                        if not json_data or 'results' not in json_data or not isinstance(json_data['results'], list) or len(json_data['results']) == 0:
                                            print(f"Le fichier {json_file} est vide ou mal formaté, il sera ignoré.")
                                            continue  # Passer au fichier suivant si c'est le cas

                                        # Extraire l'ID d'observation à partir du nom du fichier (sans extension)
                                        obs_id = os.path.splitext(os.path.basename(json_file))[0]

                                        # Créer une liste d'entrées avec 'name', 'obs' et 'proba'
                                        result = []
                                        for entry in json_data['results']:
                                            if 'name' in entry and 'id' in entry and 'score' in entry:
                                                result.append({
                                                    'name': entry['name'],
                                                    'obs': entry['id'],
                                                    'proba': entry['score']
                                                })

                                        # Ajouter les résultats dans la liste globale
                                        all_results.append({obs_id: result})

                                        # Écrire dans un fichier si nous avons atteint la limite de chunk
                                        processed_count += 1
                                        if processed_count >= files_per_chunk:
                                            output_path = f"{output_base}_{chunk_count}.json"
                                            with open(output_path, 'w') as f:
                                                json.dump(all_results, f, indent=4)
                                            print(f"Fichier {output_path} créé avec {len(all_results)} observations.")
                                            chunk_count += 1
                                            all_results = []  # Réinitialiser les résultats pour le prochain chunk
                                            processed_count = 0  # Réinitialiser le compteur

                                    except json.JSONDecodeError:
                                        print(f"Erreur de décodage JSON dans le fichier {json_file}, il sera ignoré.")
                                        continue

                            except Exception as e:
                                print(f"Erreur lors de la lecture du fichier {json_file}: {e}")

            except Exception as e:
                print(f"Erreur lors de l'extraction de l'archive {tgz_file}: {e}")

        # Si des résultats restent après le dernier fichier, les enregistrer
        if all_results:
            output_path = f"{output_base}_{chunk_count}.json"
            with open(output_path, 'w') as f:
                json.dump(all_results, f, indent=4)
            print(f"Fichier {output_path} créé avec {len(all_results)} observations.")

        print(f"Traitement terminé pour {processed_count} fichiers JSON.")

# Exemple d'utilisation
chemin_tar = '/home/anne-laure/projet/PLANTNET_M1_SSD/multiple_data_python/kswe_20250117.tar'
process_plant_data_advanced(chemin_tar)


#################################################################################################################################


# ETAPE 2 : Answers avec la création de 3_trues.json
# %%
import os
import json
import pandas as pd

# Définition des chemins corrects
chemin_base = "/home/anne-laure/projet/PLANTNET_M1_SSD"
chemin_extracted = os.path.join(chemin_base, "extracted_data")
chemin_output = os.path.join(chemin_base, "multiple_data_python", "3_true_classes.json")

tasks_path = os.path.join(chemin_extracted, "converters", "tasks.json")
ground_truth_path = os.path.join(chemin_extracted, "answers", "ground_truth.txt")

# Vérification de l'existence des fichiers
if not os.path.exists(tasks_path):
    raise FileNotFoundError(f"Erreur : le fichier {tasks_path} est introuvable.")

if not os.path.exists(ground_truth_path):
    raise FileNotFoundError(f"Erreur : le fichier {ground_truth_path} est introuvable.")

# Chargement du fichier ground_truth.txt
expert_df = pd.read_csv(ground_truth_path, header=None, delimiter="\t", names=["V1"])

# Supprimer la première ligne (inutile)
expert_df = expert_df.iloc[1:].reset_index(drop=True)

# Ajouter un numéro de ligne
expert_df["ligne"] = expert_df.index + 1

# Filtrer les lignes où V1 n'est pas -1
expert_filtre = expert_df[expert_df["V1"] != -1]

# Lecture du fichier tasks.json
with open(tasks_path, 'r') as f:
    tasks = json.load(f)

# Conversion en DataFrame
tasks_df = pd.DataFrame({
    "id": tasks.keys(),
    "numero": [int(value) for value in tasks.values()]
})

# Fusion des données sur la colonne "ligne" (équivalent d'une jointure)
resultats = expert_filtre.merge(tasks_df, left_on="ligne", right_on="numero", how="inner")

# Création de la structure JSON
json_output = {
    str(row["id"]): {
        "obs_SWE": str(row["ligne"]),
        "id_SWE": int(row["V1"])
    }
    for _, row in resultats.iterrows()
}

# Sauvegarde en JSON dans multiple_data_python
with open(chemin_output, 'w') as f:
    json.dump(json_output, f, indent=4)

print(f"Fichier {chemin_output} créé avec {len(json_output)} entrées.")


#################################################################################################################################

# Etape 3 : Création de 2_predictions
#%%
import os
import json
import glob

# Définition du chemin de travail
chemin_base = "/home/anne-laure/projet/PLANTNET_M1_SSD/multiple_data_python"

# Chemin correct du fichier de classes
chemin_classes = '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_classes.json'

# Vérifier si le fichier existe
if not os.path.exists(chemin_classes):
    raise FileNotFoundError(f"ERREUR : Le fichier {chemin_classes} est introuvable ! Vérifiez son emplacement.")

# Charger les fichiers de classes
with open(chemin_classes, 'r') as f:
    classes = json.load(f)

# Fonction pour ajouter les identifiants Pl@ntNet aux observations
def ajout_classes(observation):
    """Ajoute les identifiants Pl@ntNet aux observations"""
    for item in observation:
        nom_espece = item.get("name")  # Nom de l'espèce
        if nom_espece in classes:
            item["id_SWE"] = classes[nom_espece]  # Ajouter l'identifiant de l'espèce
        else:
            item["id_SWE"] = None  # Si l'espèce n'est pas trouvée, id_SWE est None
    return observation

# Fonction pour traiter les fichiers de prédictions en plusieurs parties
def traiter_predictions_partielles(chemin_predictions_folder):
    # Initialisation d'une liste vide pour stocker les résultats
    resultat_complet = []
    
    # Rechercher tous les fichiers de prédictions (parties)
    fichiers_predictions = glob.glob(os.path.join(chemin_predictions_folder, '1_predictions_part_*.json'))

    # Traiter chaque fichier de prédictions
    total_obs = 0
    for fichier in fichiers_predictions:
        with open(fichier, 'r') as f:
            predictions = json.load(f)

        # Appliquer la fonction d'enrichissement
        for id_obs, obs in predictions[0].items():  # Maintenant, on itère sur les prédictions
            resultat_complet.append({id_obs: ajout_classes(obs)})  # Enrichir les prédictions
            total_obs += 1

        print(f"Traitement du fichier {fichier} terminé, nombre d'observations : {total_obs}.")

    # Sauvegarder le résultat complet
    output_path = os.path.join(chemin_base, "2_predictions_classes.json")
    with open(output_path, 'w') as f:
        json.dump(resultat_complet, f, indent=4, ensure_ascii=False)

    print(f"Fichier final généré avec succès : {output_path}")

# Exemple d'utilisation
chemin_predictions_folder = "/home/anne-laure/projet/PLANTNET_M1_SSD/multiple_data_python"
traiter_predictions_partielles(chemin_predictions_folder)


#################################################################################################################################

# Etape 4 : Croisement
#%%import json

import json
import os

chemin = "/home/anne-laure/projet/PLANTNET_M1_SSD/multiple_data_python"

# Changer le répertoire actuel vers ce dossier
os.chdir(chemin)

# Afficher le répertoire de travail pour confirmation
print("Répertoire de travail actuel:", os.getcwd())

# Fonction de croisement avec filtrage
def croisement_avec_filtrage(chemin_predictions, chemin_reference, chemin_sortie):
    """Effectue un croisement entre les prédictions et la référence et les filtre selon la correspondance."""
    
    # Charger les fichiers JSON
    with open(chemin_predictions, 'r') as f:
        predictions = json.load(f)
    
    with open(chemin_reference, 'r') as f:
        reference = json.load(f)
    
    # Créer une nouvelle liste pour stocker les résultats filtrés
    resultats_filtres = {}

    # Vérification si predictions et reference sont des listes
    if isinstance(predictions, list) and isinstance(reference, list):
        # Pour chaque élément dans les prédictions (en supposant que chaque élément a un identifiant unique)
        for idx, pred_item in enumerate(predictions):
            # Récupérer l'id de prédiction (assumé ici comme étant une clé dans les éléments de la liste)
            id = pred_item.get('id', None)
            
            if id and any(ref.get('id') == id for ref in reference):
                # Si l'id existe dans la référence
                reference_item = next(ref for ref in reference if ref.get('id') == id)
                expected_value = reference_item.get('id_SWE')
                obs_SWE_value = reference_item.get('obs_SWE')
                
                # Ajouter les éléments filtrés et évalués
                pred_item['obs_SWE'] = obs_SWE_value
                
                # Vérification de la correspondance
                if expected_value and 'id_SWE' in pred_item and pred_item['id_SWE'] == expected_value:
                    pred_item['correct'] = 1
                else:
                    pred_item['correct'] = 0
                
                # Ajouter l'élément filtré aux résultats
                resultats_filtres[id] = pred_item
    
    # Écrire le résultat
    with open(chemin_sortie, 'w') as f:
        json.dump(resultats_filtres, f, indent=4)
    
    print(f"Terminé. Résultat enregistré dans: {chemin_sortie}")
    return resultats_filtres


# Si on veut vérifier le nombre d'ID communs
def verifier_ids_communs(chemin_predictions, chemin_reference):
    """Compter les IDs communs dans les prédictions et la référence"""
    
    with open(chemin_predictions, 'r') as f:
        predictions = json.load(f)
    
    with open(chemin_reference, 'r') as f:
        reference = json.load(f)
    
    # Compter les identifiants dans chaque fichier
    nb_ids_predictions = len(predictions)
    nb_ids_reference = len(reference)
    
    # Compter les identifiants communs
    ids_communs = {pred['id'] for pred in predictions} & {ref['id'] for ref in reference}
    nb_ids_communs = len(ids_communs)
    
    print(f"Nombre d'identifiants dans le fichier de prédictions: {nb_ids_predictions}")
    print(f"Nombre d'identifiants dans le fichier de référence: {nb_ids_reference}")
    print(f"Nombre d'identifiants communs: {nb_ids_communs}")
    
    return nb_ids_predictions, nb_ids_reference, nb_ids_communs


# Utilisation de la fonction croisement_avec_filtrage
resultats = croisement_avec_filtrage(
    os.path.join(chemin, "2_predictions_classes.json"),  # fichier de prédictions
    os.path.join(chemin, "3_true_classes.json"),         # fichier de référence
    os.path.join(chemin, "4_croisements_experts.json")   # fichier de sortie
)

# Pour visualiser quelques statistiques sur les résultats
print(f"Nombre d'observations après filtrage: {len(resultats)}")

# Compter le nombre total d'items corrects
nb_correct = 0
nb_total = 0

for id, item in resultats.items():
    nb_total += 1
    if item.get('correct') == 1:
        nb_correct += 1

print(f"Nombre total de prédictions: {nb_total}")
print(f"Nombre de prédictions correctes: {nb_correct}")

#################################################################################################################################

# ETAPE 5 : Calcul des scores 
# %%
import json
import os

# Afficher le répertoire de travail pour confirmation
print("Répertoire de travail actuel:", os.getcwd())

# Importer les données
with open(os.path.join(chemin, "4_croisements_experts.json"), 'r') as f:
    data = json.load(f)

# Fonction pour calculer les scores de prédiction
def calculate_scores(data):
    """Calcule les scores de prédiction basés sur les résultats filtrés."""
    
    # Initialisation d'un dictionnaire vide pour stocker les résultats
    scores = {}
    
    # Parcourir chaque observation
    for id, predictions in data.items():
        # Initialisation du compteur de score à 0
        cumulative_prob = 0
        score_du_vrai = 0
        score_somme = 0
        
        # Savoir si une prédiction correcte a été trouvée
        found_correct = False
        
        # Parcourir les prédictions dans l'ordre
        for pred in predictions:
            if pred.get('correct') == 1:
                # Si la prédiction est correcte
                found_correct = True
                
                # Premier score: 1 - probabilité de la vraie valeur
                score_du_vrai = 1 - pred.get('proba', 0)
                
                # Deuxième score: somme des probabilités jusqu'à la vraie valeur exclue
                score_somme = cumulative_prob
                
                break
            else:
                # Si la prédiction est incorrecte : ajouter sa probabilité au cumul
                cumulative_prob += pred.get('proba', 0)
        
        # Si une prédiction correcte a été trouvée : on enregistre les scores
        if found_correct:
            scores[id] = {
                'one_minus_prob': score_du_vrai,
                'sum_until_correct': score_somme
            }
        else:
            # Si aucune prédiction correcte n'a été trouvée : attribuer 0 aux deux scores
            scores[id] = {
                'one_minus_prob': 0.999,
                'sum_until_correct': 0.001
            }
    
    return scores


# Utilisation de la fonction à nos données
scores = calculate_scores(data)

# Sauvegarder les résultats
with open(os.path.join(chemin, "5_scores.json"), 'w') as f:
    json.dump(scores, f, indent=4)

print("Les scores ont été calculés et enregistrés dans '5_scores.json'.")

# %%
