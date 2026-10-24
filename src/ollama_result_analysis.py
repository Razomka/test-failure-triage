import json
from pathlib import Path


ai_result_path = list(Path("ai_results").glob('**/ai_results*.json'))
number_of_ai_runs = len(ai_result_path)
labels = Path("failures/labels.json")
new_json_label_file = {}
entries_dict = {}

for ai_result in ai_result_path:
    count = 0
    no_of_files = 0
    confusion_dict = {}
    confidence_dict = {}
    with open(ai_result) as ai_file:
        json_result_file = json.load(ai_file)

        with open(labels) as lab_file:
            json_label_file = json.load(lab_file)
            new_json_label_file = {dic["filename"]: dic for dic in json_label_file}

            for result in json_result_file["results"]:
                no_of_files += 1
                label_entry = new_json_label_file[result["filename"]]
                # print(f"Label: {label_entry['filename']} {label_entry['label']} AI: {result['filename']} {result['category']} AI Reasoning: {result["reasoning"]}\n")
                confidence_key = result["confidence"]
                confidence_dict[confidence_key] = confidence_dict.get(confidence_key, 0) + 1
                confusion_key = (label_entry['label'], result['category'])
                confusion_dict[confusion_key] = confusion_dict.get(confusion_key, 0) + 1
                if result["category"] == label_entry["label"]:
                    count += 1

    print(f"{'prompt version':<15}{'AI model':<14}{'Number of Cases':>17}{'Number of Correct labels':>26}{'Percent Accuracy':>18}")
    print("-" * 100)
    print(f"{json_result_file['prompt_version']:<15}{json_result_file['model']:<14}{no_of_files:>17}{count:>26}{(count/no_of_files)*100:>17.0f}%")
    print("\n")