from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from src.ollama_testlog_analysis import TestFailures, call_ai, build_prompt, template_check

app = FastAPI()

class ClassifyRequest(BaseModel):
    log: str
    sources: dict[str, str] | None = None

@app.get("/")
def read_root():
    return {"Hello" : "World"}

@app.post("/classify")
def classify(request: ClassifyRequest) -> TestFailures:
    prompt, _ = template_check()
    prompt = build_prompt(prompt, request.log)
    try:
        return call_ai(prompt)
    except ValidationError:
        raise HTTPException(status_code=502, detail="Model returned invalid output")
    except Exception as err:
        raise HTTPException(status_code=503, detail=f"Classification backend unavailable: {err}")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}