import datetime as dt
import hashlib
import json
from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Literal

PROMPT_VERSION = "v1"
AI_MODEL = "gemma4:e2b"
FAILURES_DIR = Path("failures")
SOURCES_DIR = Path("src")


class TestFailures(BaseModel):
    category: Literal['Real Defect', 'Environmental Issue', 'Flaky/Timing Issue', 'False Positive Issue', 'Ordering Issue', 'No Coverage']
    reasoning: str
    confidence: Literal['Low', 'Medium', 'High']

def build_prompt(source_dir: str = None):
    '''Builds the prompt, first it takes a standard prompt and hashes it, then it adds the requires paths.
       It has two prompts, one where source code is given, one where it is not.'''
    rubric = "------------ RUBRIC ------------" \
         "Real Defect: An issue with the code, something like an operator going wrong in the calculator or a result being incorrect as a value returned is wrong." \
         "Environmental Issue: Missing imports, missing files, something with the users environment is wrong and stopped the tests from working." \
         "Flaky/Timing Issue: Sometimes the tests pass, other times they fail - look for similar tests passing where one fails - timing issues." \
         "False Positive Issue: Nothing wrong in the code, so it is adding together without issue, instead the test is incorrectly written or experienced a bug" \
         "Ordering Issue: A test that works stand-alone but fails when conducted with other tests, look for variables that are carried across tests." \
         "No Coverage: Pytest silently passing without issues, without realising that it is wrong, something like no tests were ran, or less tests cause one was mislabelled." \
         "----------------- Confidence -----------------" \
         "High: Logs contain direct evidence for this category" \
         "Medium: Logs contain some evidence for category but could also easily apply another category" \
         "Low: Logs contain very little evidence for any category"

    if source_dir:
        given_prompt = f'Analyse these pytest failure logs and classify them. Use the source and test code to help.\n' \
                       f'Use the confidence levels to gauge how accurate you think you are, either Low, Medium or High.\n' \
                       f'Use the following rubric to understand the catergories, choose only one, here is the rubric: {rubric}\n' \
                       f'Here is the source code: {source_dir}' \
                       f'and here is the log file: \n'
    else:
        given_prompt = f'Analyse these pytest failure logs and classify them. Use the source and test code to help.\n' \
                       f'Use the confidence levels to gauge how accurate you think you are, either Low, Medium or High.\n' \
                       f'Use the following rubric to understand the catergories, choose only one, here is the rubric: {rubric}\n' \
                       f'and here is the log file: \n'

    prompt_hash = hashlib.sha256(given_prompt.encode()).hexdigest()[:8]

    hash_path = Path("version_hash.json")
    try:
        with open(hash_path) as hash_file:
            json_file = json.load(hash_file)
    except FileNotFoundError, json.JSONDecodeError:
        json_file = {}

    if prompt_hash not in json_file:
        prompt_version = PROMPT_VERSION[:1] + str(len(json_file) + 1)
        if source_dir:
            json_file[prompt_hash] = prompt_version + "_source"
        else:
            json_file[prompt_hash] = prompt_version
        with open(hash_path, "w") as hash_file: 
            json.dump(json_file, hash_file)
    else:
        prompt_version = json_file[prompt_hash]

    return given_prompt, prompt_version

def generate_list_of_files(directory_to_analyse: Path, source_dir: str = None):
    '''Takes a path, gathers all cases and places them into a list.
       Currently set for cases but can be changed to be name agnostic'''
    list_of_files = []  
    for case in sorted(directory_to_analyse.iterdir()):
        if "case_" in case.name:
            case_path = case
            list_of_files.append(case_path)
    return list_of_files


def ollama_analysis(directory_to_analyse: Path, source_dir: str = None):
    '''The main place where the AI runs over the cases and analyses them.
       Returns back a json which is appended to a list to be written to a file'''
    results = []
    list_of_files = generate_list_of_files(directory_to_analyse)
    given_prompt, prompt_version = build_prompt()
    if source_dir:
        pass
    for case_path in list_of_files:
        file_path = case_path
        with open(file_path) as f:
            log = f.read()

            response: ChatResponse = chat(
            model='gemma4:e2b',
            messages=[
                {
                'role': 'user',
                'content': f"{given_prompt} {log}",
                },
            ],
            options = {"temperature": 0},
            format=TestFailures.model_json_schema()
            )
            ai_results = json.loads(response['message']['content'])
            ai_results["filename"] = str(file_path.name)
            results.append(ai_results)

    return results, prompt_version

def write_results(results: list, prompt_version: str = PROMPT_VERSION):
    '''Write AI analysis results to JSON file contain metadata in the name.'''
    prompt_version = prompt_version
    metadata_json_plus_results = {}
    results_files = Path(f"ai_results/ai_results_{AI_MODEL}_{prompt_version}_{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    with open(results_files, "w") as ai_file:
        metadata_json_plus_results["model"] = AI_MODEL
        metadata_json_plus_results["prompt_version"] = prompt_version
        metadata_json_plus_results["timestamp"] = dt.datetime.now().isoformat()
        metadata_json_plus_results["Temperate"] = "0"
        metadata_json_plus_results["results"] = results

        json.dump(metadata_json_plus_results, ai_file)

def main():
    results, prompt_version = ollama_analysis(FAILURES_DIR)
    write_results(results, prompt_version)


if __name__ == "__main__":
    main()
