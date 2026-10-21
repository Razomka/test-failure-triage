import json
from pathlib import Path


ai_result_log = Path("ai_results/ai_run.json")
labels = Path("failures/labels.json")
new_json_label_file = {}
count = 0
no_of_files = 0

with open(ai_result_log) as ai_file:
    json_result_file = json.load(ai_file)

    with open(labels) as lab_file:
        json_label_file = json.load(lab_file)
        new_json_label_file = {dic["filename"]: dic for dic in json_label_file}

        for result in json_result_file["results"]:
            no_of_files += 1
            label_entry = new_json_label_file[result["filename"]]
            print(f"AI: {result['filename']} {result['category']} Label: {label_entry['filename']} {label_entry['label']} ")
            if result["category"] == label_entry["label"]:
                count += 1

print(f"The number of matches is: {count}")
print(f"The accuracy is only: {count} of {no_of_files} ({(count/no_of_files)*100:.2f}%)")