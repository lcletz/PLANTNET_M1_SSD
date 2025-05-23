import json
import glob
import os

input_folder = "PlantNet_M1_SSD/data/processed"
output_file = "PlantNet_M1_SSD/data/all_probs.json"

all_obs_data = {}

json_files = sorted(glob.glob(os.path.join(input_folder, "kswe_*.json")))

for file_path in json_files:
    print(f"Processing {file_path}...")
    with open(file_path, "r") as f:
        data = json.load(f)

    for obs_id, preds in data.items():
        prob_vector = [pred.get("proba", 0) for pred in preds]
        true_class = next((i for i, pred in enumerate(preds) if pred.get("correct") == 1), None)

        if true_class is None:
            # Add an imaginary label if none marked correct (score close to 1)
            prob_vector.append(0.999)
            true_class = len(prob_vector) - 1

        all_obs_data[obs_id] = {
            "probs": prob_vector,
            "true_class": true_class
        }

print(f"Total observations processed: {len(all_obs_data)}")

# Write pretty-printed JSON
with open(output_file, "w") as f_out:
    json.dump(all_obs_data, f_out, indent=2)

print(f"Saved structured and indented JSON to {output_file}")
