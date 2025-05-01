# Compare AI answers (ai answers.json) with correct answers (answers.json).
# Calculate AI prediction rate and make a graph.
#%%
import os
import pandas as pd
import matplotlib.pyplot as plt

# Gets the absolute path of the folder containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Building absolute paths for JSON files
ai_answers_path = os.path.join(script_dir, '../extracted_data/aggregation/ai_answers.json')
answers_path = os.path.join(script_dir, '../extracted_data/answers/answers.json')

# Load JSON files as dictionaries
import json
with open(ai_answers_path, 'r') as file:
    ai_answers_data = json.load(file)
with open(answers_path, 'r') as file:
    answers_data = json.load(file)

# Convert Dictionaries to DataFrames
ai_answers = pd.DataFrame(list(ai_answers_data.items()), columns=['index', 'ai_answer'])
answers = pd.DataFrame(list(answers_data.items()), columns=['index', 'correct_answer'])

# Merge DataFrames to compare responses
comparison_df = pd.merge(ai_answers, answers, on='index')

# Calculate the accuracy rate
correct_predictions = (comparison_df['ai_answer'] == comparison_df['correct_answer']).mean()
print(f"Taux de précision de l'IA : {correct_predictions * 100:.2f}%")

# Show comparison as graph
plt.figure(figsize=(10, 6))
comparison_df['ai_answer'].value_counts().plot(kind='bar', color='skyblue', alpha=0.7, label='Réponses IA')
comparison_df['correct_answer'].value_counts().plot(kind='bar', color='lightcoral', alpha=0.7, label='Réponses correctes')
plt.title("Comparaison des réponses de l'IA et des réponses correctes")
plt.xlabel("Classes")
plt.ylabel("Fréquence")
plt.legend()
plt.show()

# I get an Accuracy Rate of 0.00% this means that all the AI ​​predictions differ from the correct answers.
###################################################################################################################################################################################
###################################################################################################################################################################################

# Examine the AI's confidence scores (in ai_scores.json) to see how confident the AI ​​is in its answers.
#%%
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Gets the absolute path of the folder containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build the absolute path for the ai_scores.json file
ai_scores_path = os.path.join(script_dir, '../extracted_data/aggregation/ai_scores.json')

# Load AI confidence scores
import json
with open(ai_scores_path, 'r') as file:
    ai_scores_data = json.load(file)

# Convert to DataFrame if necessary
if isinstance(ai_scores_data, dict):
    ai_scores = pd.DataFrame(list(ai_scores_data.values()), columns=['score'])
elif isinstance(ai_scores_data, list):
    ai_scores = pd.DataFrame(ai_scores_data, columns=['score'])
else:
    ai_scores = pd.Series(ai_scores_data, name='score')

# Show distribution of confidence scores
plt.figure(figsize=(10, 6))
sns.histplot(ai_scores['score'], kde=True, color='green')  # Note the 'score' column
plt.title("Distribution des Scores de Confiance de l'IA")
plt.xlabel("Score de Confiance")
plt.ylabel("Fréquence")
plt.show()

# We have a histogram of the distribution of confidence scores. We can see an increasing trend the higher the confidence score.
###################################################################################################################################################################################
###################################################################################################################################################################################

# We will analyze the distribution of classes predicted by AI (ai_classes.json) and compare with the real classes (answers.json).
#%%
import os
import pandas as pd
import matplotlib.pyplot as plt

# Gets the absolute path of the folder containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Building absolute paths for JSON files
ai_classes_path = os.path.join(script_dir, '../extracted_data/aggregation/ai_classes.json')
classes_path = os.path.join(script_dir, '../extracted_data/converters/classes.json')

# Load predicted classes and actual classes
import json
with open(ai_classes_path, 'r') as file:
    ai_classes_data = json.load(file)
with open(classes_path, 'r') as file:
    classes_data = json.load(file)

# Convert to DataFrame if necessary
if isinstance(ai_classes_data, dict):
    ai_classes = pd.DataFrame(list(ai_classes_data.values()), columns=['predicted_class'])
elif isinstance(ai_classes_data, list):
    ai_classes = pd.DataFrame(ai_classes_data, columns=['predicted_class'])
else:
    ai_classes = pd.Series(ai_classes_data, name='predicted_class')

if isinstance(classes_data, dict):
    classes = pd.DataFrame(list(classes_data.values()), columns=['actual_class'])
elif isinstance(classes_data, list):
    classes = pd.DataFrame(classes_data, columns=['actual_class'])
else:
    classes = pd.Series(classes_data, name='actual_class')

# Compare the distribution of predicted and actual classes
predicted_class_counts = ai_classes['predicted_class'].value_counts()
actual_class_counts = classes['actual_class'].value_counts()

# Show bar charts for class distribution
plt.figure(figsize=(12, 6))

# Distribution of predicted classes
plt.subplot(1, 2, 1)
predicted_class_counts.plot(kind='bar', color='lightgreen')
plt.title("Distribution des Classes Prédites par l'IA")
plt.xlabel("Classe")
plt.ylabel("Fréquence")

# Distribution of real classes
plt.subplot(1, 2, 2)
actual_class_counts.plot(kind='bar', color='salmon')
plt.title("Distribution des Classes Réelles")
plt.xlabel("Classe")
plt.ylabel("Fréquence")

plt.tight_layout()
plt.show()

# Here are bar charts to visualize the class distribution in predictions and correct answers.
###################################################################################################################################################################################
###################################################################################################################################################################################

# We will examine the k-southwestern-europe.json file to analyze plant taxonomy, for example by counting the number of synonyms for each species.
#%%
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# Gets the absolute path of the folder containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build the absolute path for the k-southwestern-europe.json file
plant_data_path = os.path.join(script_dir, '../extracted_data/aggregation/k-southwestern-europe.json')

# Load data from k-southwestern-europe.json file
with open(plant_data_path, 'r') as file:
    plant_data = json.load(file)

# Extract synonyms for each species
# Check that each entry has the necessary keys to avoid errors
synonyms_count = {
    entry['species']: len(entry['synonyms'])
    for entry in plant_data if 'species' in entry and 'synonyms' in entry
}

# Create a DataFrame to visualize the frequency of synonyms by species
synonyms_df = pd.DataFrame(list(synonyms_count.items()), columns=['Species', 'Number of Synonyms'])

# Show a graph of synonym frequency by species
plt.figure(figsize=(12, 8))
synonyms_df.sort_values('Number of Synonyms', ascending=False).head(20).plot(
    kind='bar', x='Species', y='Number of Synonyms', color='purple'
)
plt.title("Top 20 des Espèces avec le Plus de Synonymes")
plt.xlabel("Espèce")
plt.ylabel("Nombre de Synonymes")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# We have a synonym frequency graph for each species.
###################################################################################################################################################################################
###################################################################################################################################################################################


# I want to make a graph for the easy to meet and difficult to meet species for the plantnet interface for the average score (average the score over the whole class) 
# Also make a cross table to see if there is a link between nb observation.

#%% 
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# Absolute path to the working directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Building paths for JSON files
ai_answers_path = os.path.join(script_dir, '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_answers.json')
ai_scores_path = os.path.join(script_dir, '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_scores.json')
answer_path = '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/answers/answers.json'
classes_path = os.path.join(script_dir, '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/classes.json')
tasks_path = os.path.join(script_dir, '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json')

# Load JSON files
with open(ai_answers_path, 'r') as file:
    ai_answers = json.load(file)

with open(ai_scores_path, 'r') as file:
    ai_scores = json.load(file)

with open(answer_path, 'r') as file:
    correct_answers = json.load(file)

with open(classes_path, 'r') as file:
    species_classes = json.load(file)

# Load observation data if available
if os.path.exists(tasks_path):
    with open(tasks_path, 'r') as file:
        tasks_data = json.load(file)
else:
    tasks_data = {}

# Convert data to DataFrames
ai_answers_df = pd.DataFrame(list(ai_answers.items()), columns=['id', 'predicted_class'])
ai_scores_df = pd.DataFrame(list(ai_scores.items()), columns=['id', 'score'])
correct_answers_df = pd.DataFrame(list(correct_answers.items()), columns=['id', 'correct_class'])

# Convert 'species_classes' to DataFrame
species_classes_df = pd.DataFrame(list(species_classes.items()), columns=['class_id', 'species_name'])

# Create a dictionary to map class_id to species_name
class_to_species = dict(species_classes_df[['class_id', 'species_name']].values)

# Replace numeric IDs in 'predicted_class' with species names
ai_answers_df['predicted_class'] = ai_answers_df['predicted_class'].map(class_to_species)

# Merge DataFrames to have all information on one line
df = ai_answers_df.merge(ai_scores_df, on='id').merge(correct_answers_df, on='id')

# Merge with species data
df = df.merge(species_classes_df, left_on='predicted_class', right_on='species_name', how='left')

# Calculate the average score per species
species_scores = df.groupby('species_name')['score'].mean().reset_index()

# Identify easy and difficult species to encounter
species_scores['difficulty'] = species_scores['score'].apply(lambda x: 'Facile' if x > 0.75 else 'Difficile')

# Show a graph of average scores by species
plt.figure(figsize=(12, 8))
species_scores.sort_values('score', ascending=False).plot(kind='bar', x='species_name', y='score', color='skyblue')
plt.title("Scores Moyens de Confiance de l'IA par Espèce")
plt.xlabel("Espèce")
plt.ylabel("Score Moyen de Confiance")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# Show a graph for easy vs hard species
plt.figure(figsize=(8, 6))
species_scores.groupby('difficulty')['score'].mean().plot(kind='bar', color=['green', 'red'])
plt.title("Comparaison des Scores Moyens : Espèces Faciles vs Difficiles")
plt.ylabel("Score Moyen de Confiance")
plt.show()

# If observation data is available in tasks.json
if tasks_data:
    tasks_df = pd.DataFrame(list(tasks_data.items()), columns=['id', 'task_info'])  
    df = df.merge(tasks_df, on='id', how='left')
    
    # Calculate the number of observations for each species
    observation_counts = df.groupby('species_name')['id'].nunique().reset_index()
    observation_counts.rename(columns={'id': 'observation_count'}, inplace=True)
    
    # Merge observation data with mean scores per species
    species_scores = species_scores.merge(observation_counts, on='species_name', how='left')
    
    # Display a cross-tabulation to analyze the correlation between the number of observations and the average score
    correlation_df = species_scores[['species_name', 'observation_count', 'score']]
    print(correlation_df.corr())

    # Display a graph of the relationship between the number of observations and the average score
    plt.figure(figsize=(10, 6))
    plt.scatter(correlation_df['observation_count'], correlation_df['score'], color='purple')
    plt.title("Relation entre le Nombre d'Observations et le Score Moyen")
    plt.xlabel("Nombre d'Observations")
    plt.ylabel("Score Moyen de Confiance")
    plt.show()


## It gives me an empty graph.
## I'll try to fix that.

#%%
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# Absolute path to the working directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct paths to the JSON files
ai_answers_path = os.path.join(script_dir, '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_answers.json')
ai_scores_path = os.path.join(script_dir, '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/aggregation/ai_scores.json')
answer_path = '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/answers/answers.json'
classes_path = os.path.join(script_dir, '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/classes.json')
tasks_path = os.path.join(script_dir, '/home/anne-laure/projet/PLANTNET_M1_SSD/extracted_data/converters/tasks.json')

# Load the JSON files into variables
with open(ai_answers_path, 'r') as file:
    ai_answers = json.load(file)

with open(ai_scores_path, 'r') as file:
    ai_scores = json.load(file)

with open(answer_path, 'r') as file:
    correct_answers = json.load(file)

with open(classes_path, 'r') as file:
    species_classes = json.load(file)

# Load task data if available
if os.path.exists(tasks_path):
    with open(tasks_path, 'r') as file:
        tasks_data = json.load(file)
else:
    tasks_data = {}

# Convert the JSON data into DataFrames for easier manipulation
ai_answers_df = pd.DataFrame(list(ai_answers.items()), columns=['id', 'predicted_class'])
ai_scores_df = pd.DataFrame(list(ai_scores.items()), columns=['id', 'score'])
correct_answers_df = pd.DataFrame(list(correct_answers.items()), columns=['id', 'correct_class'])

# Convert 'species_classes' into a DataFrame and reverse the columns for proper mapping
species_classes_df = pd.DataFrame(list(species_classes.items()), columns=['species_name', 'class_id'])

# Display the first few rows to verify the data
print("Species Classes DataFrame (after reversing columns) :")
print(species_classes_df.head())

# Ensure that 'predicted_class' is of type int (or str) and corresponds to 'class_id' in species_classes
ai_answers_df['predicted_class'] = ai_answers_df['predicted_class'].apply(pd.to_numeric, errors='coerce')

# Check if the 'predicted_class' column has been converted correctly
print("AI Answers DataFrame after converting the identifiers :")
print(ai_answers_df.head())

# Create a dictionary to map 'class_id' to 'species_name'
class_to_species = dict(species_classes_df[['class_id', 'species_name']].values)

# Check the unique values in 'predicted_class' to be mapped
print("Unique values of 'predicted_class' to map :")
print(ai_answers_df['predicted_class'].unique())

# Replace the numeric identifiers in 'predicted_class' with species names using the created dictionary
ai_answers_df['predicted_class'] = ai_answers_df['predicted_class'].map(class_to_species)

# Verify the first few rows after the mapping
print("AI Answers DataFrame after replacing the identifiers :")
print(ai_answers_df.head())

# Merge the DataFrames to consolidate all the information into a single DataFrame
df = ai_answers_df.merge(ai_scores_df, on='id', how='left')
df = df.merge(correct_answers_df, on='id', how='left')

# Verify the merged DataFrame
print("DataFrame after merging with ai_scores and correct_answers :")
print(df.head())

# Merge with species data
df = df.merge(species_classes_df, left_on='predicted_class', right_on='species_name', how='left')

# Verify the merged DataFrame with species_classes_df
print("DataFrame after merging with species_classes_df :")
print(df.head())

# Calculate the average score per species
species_scores = df.groupby('species_name')['score'].mean().reset_index()

# Check the average scores per species
print("Average scores per species :")
print(species_scores.head())

# Identify which species are easy or difficult based on the average score
species_scores['difficulty'] = species_scores['score'].apply(lambda x: 'Easy' if x > 0.75 else 'Difficult')

# Plot a bar chart of average scores per species
plt.figure(figsize=(12, 8))
species_scores.sort_values('score', ascending=False).plot(kind='bar', x='species_name', y='score', color='skyblue')
plt.title("Average Confidence Scores of AI by Species")
plt.xlabel("Species")
plt.ylabel("Average Confidence Score")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# Plot a comparison of easy vs difficult species based on their average scores
plt.figure(figsize=(8, 6))
species_scores.groupby('difficulty')['score'].mean().plot(kind='bar', color=['green', 'red'])
plt.title("Comparison of Average Scores: Easy vs Difficult Species")
plt.ylabel("Average Confidence Score")
plt.show()

# %%
