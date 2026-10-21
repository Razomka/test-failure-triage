from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel
from pathlib import Path

class TestFailures(BaseModel):
    name_of_file: str
    test_name: str
    category: str
    label: str
    reasoning: str
    confidence: str

p = Path("failures")
q = list(p.glob('**/*.txt'))

for testlog in q:
    with open(testlog) as f:
        log = f.read()

        response: ChatResponse = chat(
        model='gemma4:e2b',
        messages=[
            {
            'role': 'user',
            'content': f'Analyse this pytest failure log and classify it: This is the log here ----- {log}',
            },
        ],
        format=TestFailures.model_json_schema()
        )
        print(response['message']['content'])