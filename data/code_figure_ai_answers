#%%
import json
import matplotlib.pyplot as plt

# Charger les données
with open("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_answers.json", "r", encoding="utf-8") as f:
    classes = json.load(f)  # 'classes' contient maintenant le dictionnaire JSON

# Extraire les clés et valeurs
keys = list(map(int, classes.keys()))  # Convertir les clés en entiers
values = list(classes.values())  # Récupérer les valeurs

# Création de l'histogramme
plt.figure(figsize=(12, 6))
plt.bar(keys, values, color="skyblue", edgecolor="black")

# Ajouter des labels
plt.xlabel("Identifiants (Classes)")
plt.ylabel("Valeurs (Fréquences)")
plt.title("Distribution des valeurs dans ai_answers.json")
plt.xticks(keys, rotation=45)  # Incliner les étiquettes

# Afficher la figure
plt.show()

#################################################################################################################################
#%%
import json
import matplotlib.pyplot as plt

# Charger les fichiers JSON
with open("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_answers.json", "r", encoding="utf-8") as f:
    ai_answers = json.load(f)

# Afficher un Nuages de points pour voir les tendances

plt.figure(figsize=(10, 5))
plt.scatter(ai_answers.keys(), ai_answers.values(), color="red", alpha=0.6)
plt.xlabel("Identifiant de plante")
plt.ylabel("Valeur associée")
plt.title("Nuage de points des valeurs dans ai_answers.json")
plt.xticks(rotation=90)
plt.show()

#########################################################################################################################################

#%%
import json
import matplotlib.pyplot as plt

# Charger les scores
with open("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_scores.json", "r", encoding="utf-8") as f:
    ai_scores = json.load(f)

# Afficher un histogramme des scores
#plt.figure(figsize=(10, 5))
#plt.bar(ai_scores.keys(), ai_scores.values(), color="lightcoral")
#plt.xlabel("Identifiant de plante")
#plt.ylabel("Score")
#plt.title("Distribution des scores dans ai_scores.json")
#plt.xticks(rotation=90)
#plt.show()

#Afficher un nuage de point 
plt.figure(figsize=(10, 5))
plt.scatter(ai_scores.keys(), ai_scores.values(), color="blue", alpha=0.6)
plt.xlabel("Identifiant de plante")
plt.ylabel("Score")
plt.title("Nuage de points des scores")
plt.xticks(rotation=90)
plt.show()

################################################################################################################################################################
#%%
#Le fichier classes.json contient les noms des plantes associés à des identifiants. On va faire des graphiques pour mieux visualiser ces données.

import json
import matplotlib.pyplot as plt

# Charger les données
with open("/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

# Extraire les noms des plantes et les identifiants
plant_names = list(classes.keys())
plant_ids = list(classes.values())

# Afficher le nuage de point
plt.figure(figsize=(12, 6))
plt.scatter(plant_ids, range(len(plant_ids)), color="green", alpha=0.6)
plt.xlabel("Identifiant de plante")
plt.ylabel("Index")
plt.title("Nuage de points des identifiants de plantes")
plt.yticks(range(len(plant_ids)), plant_names, fontsize=8)
plt.grid()
plt.show()

#############################################################################################################################################################
# %%
import json
import matplotlib.pyplot as plt

# Charger les données
file_path = "/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json"
with open(file_path, "r", encoding="utf-8") as f:
    tasks = json.load(f)

# Compter le nombre de tâches par indice
from collections import Counter
task_counts = Counter(tasks.values())

# Extraire les labels et les valeurs
labels = list(task_counts.keys())
sizes = list(task_counts.values())

# Créer un diagramme circulaire
plt.figure(figsize=(10, 7))
plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, cmap="tab20")

# Ajouter un titre
plt.title("Répartition des tâches par indice")
plt.show()

########################################################################################################################################
# %%import json
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Charger les données depuis le fichier JSON
with open('/home/anne-laure/projet/PLANTNET_M1_SSD/aggregation/k-southwestern-europe.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extraire les espèces et le nombre de synonymes
species = [entry['species'] for entry in data]
synonym_counts = [len(entry['synonyms']) for entry in data]

# Compter les occurrences de synonymes
synonym_distribution = Counter(synonym_counts)

# Création des graphiques
plt.figure(figsize=(12, 6))

# Graphique 1 : Nombre de synonymes par espèce
plt.subplot(1, 2, 1)
sns.histplot(synonym_counts, bins=range(0, max(synonym_counts)+2), kde=False)
plt.xlabel("Nombre de synonymes")
plt.ylabel("Nombre d'espèces")
plt.title("Distribution du nombre de synonymes par espèce")

# Graphique 2 : Top 10 des espèces avec le plus de synonymes
top_species = sorted(zip(species, synonym_counts), key=lambda x: x[1], reverse=True)[:10]
top_species_names = [s[0] for s in top_species]
top_species_synonyms = [s[1] for s in top_species]
plt.subplot(1, 2, 2)
sns.barplot(y=top_species_names, x=top_species_synonyms, palette='viridis')
plt.xlabel("Nombre de synonymes")
plt.ylabel("Espèces")
plt.title("Top 10 des espèces avec le plus de synonymes")

plt.tight_layout()
plt.show()

# %%
