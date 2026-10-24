# Ollama pytest analysis with fastAPI interface
Calls Ollama Gemma model to analyse pytest failure output

# Overview
Takes a pytest failure output file, analyses it and gives back a category label, reasoning and confidence. This can be ran from cli or using FastAPI.

# Why
Allows for quick analysis of pytest failures, allowing identification of the failure via a easy to understand label.

Additionally, it develop my own skill and understanding of AI, pytest, pydantic and fastAPI.  

# How it works
4 main python files, client.py, main.py, ollama_result_analysis.py and ollama_testlog_analysis.py.

When ollama_testlog_analysis.py is called, it will generate a prompt, read a pytest casefile and run the ollama AI model over it locally. This will return a results which are validated by pydantic then parsed into a file, whose title contains the model used, the prompt version, timestamp and the results from the analysis.

These results can be checked with ollama_result_analysis.py given back a small table containing how accurate the AI was. 

The prompt and rubric are pre-written and stored in ollama_testlog_analysis, when the prompt is changed, then the hash is created and added to version_hash.json, so it can be tracked how often the prompt has been changed. 

A Pydantic BaseModel was created called TestFailures, this contains: category, reasoning and confidence. This allows us to drive the AI to ensure that the data it produces matches the data type we want. 

There are a few methods around the prompt such as: check_template() - Where the static prompt is created and hashed and build_prompt() - where the log, source files(optional) and rubric are added. When the AI is called, the log changes, so hashing has to be taken earlier with the static prompt. 

There also some helper functions such as taking a path and creating a list of files, allowing the main function ollama_analysis() loop over the files and use call_ai() on each log file. These results are checked with pydantics model_validate method and then returned to be written to a file. 

ollama_result_analysis.py simply reads the file and the labels file to match up where the AI guesses matches the actual given label (given by myself) and presents this a small table. 

For the fastAPI side. A small main.py was created, this contains a method called classify() - It simply called template_check() to get the prompt and then calls build_prompt() to get the complete prompt to pass into call_ai() as a return. 

So, after some processing, it will display the given results when tests in the fastAPI <IP_address>/docs. This can also be called via client.py - This was made to call the classify method after parsing the pytest failure log to be suitable as a json. This is the preferred method and after some thinking, it will give a result. 

# Taxonomy

# Dataset

# Results

# Error Analysis

# Limitations

# Methodology

# Running it
first edit a test to fail e.g. change an assertion.
run pytest > failures/case_01.txt 2>&1

then two options:

Option 1 - cli python command:
python src/ollama_testlog_analysis.py 
This will find the case_01.txt automatically, analyse it and place it into a file located in ai_results/

Then:
python src/ollama_result_analysis.py
This will automatically find the ai_results*.json
Create a small table with some detail

Option 2 - fastAPI:
fastapi dev src/main.py
Start the fastAPI locally

python src/client.py <path to case>
Example:
python src/client.py failures/case_01.txt

This will run the Ollama AI on that specific case log and will print to the terminal as a json with category : <label>, reasoning : <text> and confidence: <label>

# Repo Layout
project directory = test-failure-triage

test-failure-triage/ai-results - location where the ai_results are kept when ran from the cli command. 

test-failure-triage/failures - location of the labels.json and all the pytest failure output e.g. case_01.txt

test-failure-triage/isolated - contains passes of certain tests like false positive and ordering issues - was considered to be used to improve AI accuracy

test-failure-triage/manual_categorisation - My manual opinion on how the AI failed and placing them into 3 categories: Rubric issue, good reasoning but needs more evidance and nonsense reasoning.

test-failure-triage/source_of_broken_code - This contains where the src or test code has been broken and will be the information for the optional source code varible in future

test-failure-triage/src/ - contains: __init__.py, client.py, main.py, ollama_result_analysis.py, ollama_testlog_analysis.py and pycalc.py

test-failure-triage/tests - contains: test_calc.py and test_tmp_files - an empty directory which was used for a failing test

test-failure-triage/conftest.py - enable test_calc.py to find src/pycalc.py

test-failure-triage/README.md - this read me

test-failure-triage/requirements.txt - a pip freeze output e.g. pip freeze > requirements.txt

test-failure-triage/version_hash.json - contains the prompt versions and their hashes.

# Future Work
Need to enable the optional source code input - While some logic is in place such as different prompts and prompt versions having "_source" added. The key logic of where to find the files and passing them between methods is not there yet. 