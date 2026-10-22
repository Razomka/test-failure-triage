import datetime as dt
import hashlib
import json
from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Literal

prompt_text = "Analyse these pytest failure logs and classify them. Use the source and test code to help. Use the confidence levels to gauge how accurate you think you are, either Low, Medium or High." 
PROMPT_VERSION = "v1"
PROMPT_HASH = hashlib.sha256(prompt_text.encode()).hexdigest()[:8]
AI_MODEL = "gemma4:e2b"
new_prompt_version = PROMPT_VERSION

rubric = "------------RUBRIC------------" \
         "Real Defect: An issue with the code, something like an operator going wrong in the calculator or a result being incorrect as a value returned is wrong." \
         "Environmental Issue: Missing imports, missing files, something with the users environment is wrong and stopped the tests from working." \
         "Flaky/Timing Issue: Sometimes the tests pass, other times they fail - look for similar tests passing where one fails - timing issues." \
         "False Positive Issue: Nothing wrong in the code, so it is adding together without issue, instead the test is incorrectly written or experienced a bug" \
         "Ordering Issue: A test that works stand-alone but fails when conducted with other tests, look for variables that are carried across tests." \
         "No Coverage: Pytest silently passing without issues, without realising that it is wrong, something like no tests were ran, or less tests cause one was mislabelled'\n"



class TestFailures(BaseModel):
    category: Literal['Real Defect', 'Environmental Issue', 'Flaky/Timing Issue', 'False Positive Issue', 'Ordering Issue', 'No Coverage']
    reasoning: str
    confidence: Literal['Low', 'Medium', 'High']


hash_path = Path("version_hash.json")
try:
    with open(hash_path) as hash_file:
        json_file = json.load(hash_file)
except FileNotFoundError, json.JSONDecodeError:
    json_file = {}
   
if PROMPT_HASH not in json_file:
    new_prompt_version = PROMPT_VERSION[:1] + str(len(json_file) + 1)
    json_file[PROMPT_HASH] = new_prompt_version
    with open(hash_path, "w") as hash_file: 
        json.dump(json_file, hash_file)


fail_path = Path("failures/")
case_files = list(fail_path.glob('case*.txt'))

ai_result_log = Path(f"ai_results/ai_results_{AI_MODEL}_{new_prompt_version}_{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
try:
    with open(ai_result_log) as ai_file:
        ai_json_result_file = json.load(ai_file)
except FileNotFoundError, json.JSONDecodeError:
    ai_json_result_file = {}

results = []
for source_dir in sorted(Path("source_of_broken_code").iterdir()):
    log_path = Path("failures") / f"{source_dir.name}.txt"
    with open(log_path) as case_logs:
        log = case_logs.read()

        blocks = []
        for source_code in sorted(source_dir.glob("*.py")):
            blocks.append(f"--- Source: {source_code.name} ---\n {source_code.read_text()}")
        source_text = "\n\n".join(blocks)

        response: ChatResponse = chat(
        model='gemma4:e2b',
        messages=[
            {
            'role': 'user',
            'content': f'{prompt_text} Please use the following rubric to understand the catergories, choose only one, here is the rubric: {rubric}, here is source and test code: {source_text} and here is the log file: {log} ',
            },
        ],
        options = {"temperature": 0},
        format=TestFailures.model_json_schema()
        )
        ai_results = json.loads(response['message']['content'])
        ai_results["filename"] = str(log_path.name)
        results.append(ai_results)

with open(ai_result_log, "w") as ai_file:
    ai_json_result_file["model"] = AI_MODEL
    ai_json_result_file["prompt_version"] = new_prompt_version
    ai_json_result_file["timestamp"] = dt.datetime.now().isoformat()
    ai_json_result_file["Temperate"] = "0"
    ai_json_result_file["results"] = results

    json.dump(ai_json_result_file, ai_file)