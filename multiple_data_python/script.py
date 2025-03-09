#%%
import os # allows you to manage files and directories
import json # used to read and use .json files
from tqdm import tqdm # displays a progress bar to track processing progress

def process_json_files(input_dir, output_file):
    #1. Check if the folder exists
    if not os.path.exists(input_dir):
        print(f"Le dossier {input_dir} n'existe pas !")
        return
    
    # Create a dictionary to store the results
    # Initialize an empty dictionary result_dict which will contain the data extracted from the JSON files
    result_dict = {}
    # Traversing JSON files in the folder
    for root, _, files in tqdm(os.walk(input_dir), desc="Processing JSON files"):
        for file in files: # Processing JSON files
            if file.endswith(".json"): # For each file in files, check if it has the .json extension (to avoid unnecessary files)
                file_path = os.path.join(root, file) # file_path : builds the full path to the file
                obs_id = os.path.splitext(file)[0]  # Get the file name without the .json extension (which corresponds to the observation ID)
                
                with open(file_path, "r", encoding="utf-8") as f: #Opens the JSON file for reading ("r") with UTF-8 encoding
                    data = json.load(f)  # json.load(f): Loads the contents of the file as a Python dictionary
                    species_scores = {entry["id"]: entry["score"] for entry in data.get("results", [])}
                    #data.get("results", []) : Searches for the key "results" in the JSON. If it does not exist, returns an empty list [] (avoids errors)
                    # entry["id"] and entry["score"] : Extracts the species ID and its score for each entry in "results"
                    result_dict[obs_id] = species_scores # Un dictionnaire {id_espece: score}
    
    #3. Save the final dictionary to a JSON file
    with open(output_file, "w", encoding="utf-8") as out_f:
        json.dump(result_dict, out_f, indent=4)
    
    print(f"Processing terminé ! Résultat sauvegardé dans {output_file}")

# Example of use
process_json_files("kswe_20250117_00", "output.json")

# %%
