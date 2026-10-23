from fastapi import FastAPI
from pydantic import BaseModel
from ollama_testlog_analysis import TestFailures

app = FastAPI()

class ClassifyRequest(BaseModel):
    log: str

@app.get("/")
def read_root():
    return {"Hello" : "World"}

@app.post("/classify")
def classify(request: ClassifyRequest) -> TestFailures:
    return classify_log(request.log)
