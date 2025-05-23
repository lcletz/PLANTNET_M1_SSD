# %%
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
            prob_vector.append(0.999)
            true_class = len(prob_vector) - 1

        all_obs_data[obs_id] = {
            "probs": prob_vector,
            "true_class": true_class
        }

print(f"Total observations processed: {len(all_obs_data)}")

with open(output_file, "w") as f_out:
    json.dump(all_obs_data, f_out, indent=2)

# %%
import json
import numpy as np
from mapie.conformity_scores import APSConformityScore

with open("PlantNet_M1_SSD/data/all_probs.json", "r") as f:
    all_obs_data = json.load(f)

conformity_scores = []
for obs_id, data in all_obs_data.items():
    probs = data["probs"]
    true_class = data["true_class"]
    conformity_score = 1 - probs[true_class]
    conformity_scores.append(conformity_score)

conformity_scores = np.array(conformity_scores)

alpha_np = [0.05]

class DummyEstimator:
    cv = "prefit"

dummy_estimator = DummyEstimator()
conformity = APSConformityScore()
quantile = conformity.get_conformity_score_quantiles(
    conformity_scores, alpha_np, estimator=dummy_estimator
)

print(f"Quantile at {1 - alpha_np[0]:.0%} = {quantile}")
# 0.97

# %%
import json
import os

input_file = "PlantNet_M1_SSD/data/processed/expert_processed.json"
output_file = "PlantNet_M1_SSD/data/all_probs_experts.json"

all_obs_data = {}

with open(input_file, "r") as f:
    data = json.load(f)

for obs_id, preds in data.items():
    prob_vector = [pred.get("proba", 0) for pred in preds]
    true_class = next((i for i, pred in enumerate(preds) if pred.get("correct") == 1), None)

    if true_class is None:
        prob_vector.append(0.999)
        true_class = len(prob_vector) - 1

    all_obs_data[obs_id] = {
        "probs": prob_vector,
        "true_class": true_class
    }

print(f"Total observations processed: {len(all_obs_data)}")

with open(output_file, "w") as f_out:
    json.dump(all_obs_data, f_out, indent=2)

# %%
import json
import os
import random

input_file = "PlantNet_M1_SSD/data/all_probs_experts.json"

with open(input_file, "r") as f:
    data = json.load(f)

random.seed(42)

keys = list(data.keys())
random.shuffle(keys)

mid = len(keys) // 2
expert_half1 = {k: data[k] for k in keys[:mid]}
expert_half2 = {k: data[k] for k in keys[mid:]}

with open("PlantNet_M1_SSD/data/expert_probs1.json", "w", encoding="utf-8") as f:
    json.dump(expert_half1, f, indent=4, ensure_ascii=False)

with open("PlantNet_M1_SSD/data/expert_probs2.json", "w", encoding="utf-8") as f:
    json.dump(expert_half2, f, indent=4, ensure_ascii=False)

# %%
import json
import numpy as np
from mapie.conformity_scores import APSConformityScore

with open("PlantNet_M1_SSD/data/expert_probs1.json", "r") as f:
    all_obs_data = json.load(f)

conformity_scores = []
for obs_id, data in all_obs_data.items():
    probs = data["probs"]
    true_class = data["true_class"]
    conformity_score = 1 - probs[true_class]
    conformity_scores.append(conformity_score)

conformity_scores = np.array(conformity_scores)

alpha_np = [0.05]

class DummyEstimator:
    cv = "prefit"

dummy_estimator = DummyEstimator()
conformity = APSConformityScore()
quantile = conformity.get_conformity_score_quantiles(
    conformity_scores, alpha_np, estimator=dummy_estimator
)

print(f"Quantile at {1 - alpha_np[0]:.0%} = {quantile}")
# 0.8498
# %%
