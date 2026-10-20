import datetime
import hashlib
import json
from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Literal

prompt_text = "Analyse this pytest failure log and classify it: This is the log here" 
PROMPT_VERSION = "v1"
PROMPT_HASH = hashlib.sha256(prompt_text.encode()).hexdigest()[:8]
AI_MODEL = "gemma4:e2b"
new_prompt_version = PROMPT_VERSION

class TestFailures(BaseModel):
    category: Literal['Code Bug Issue', 'Environmental Issue', 'Flaky/Timing Issue', 'False Positive Issue', 'Ordering Issue']
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


fail_path = Path("failures")
case_files = list(fail_path.glob('**/case*.txt'))

ai_result_log = Path("ai_results/ai_run.txt")
with open(ai_result_log, 'a') as ai_file:
    for testlog in case_files:
        with open(testlog) as case_logs:
            log = case_logs.read()

            response: ChatResponse = chat(
            model='gemma4:e2b',
            messages=[
                {
                'role': 'user',
                'content': f'{prompt_text} {log}',
                },
            ],
            format=TestFailures.model_json_schema()
            )
            ai_file.write(f"{testlog} {datetime.datetime.now()} {new_prompt_version} {AI_MODEL}\n" + response['message']['content']+"\n\n")