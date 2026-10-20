from pathlib import Path


ai_result_log = Path("ai_results/ai_run.txt")
labels = Path("failures/labels.json")

with open(ai_result_log) as ai_file:
    with open(labels) as lab_file:
        ai_read = ai_file.read()
        labels_read = lab_file.read()
        for 