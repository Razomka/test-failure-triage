import sys, httpx

log = open(sys.argv[1]).read()
r = httpx.post("http://127.0.0.1:8000/classify", json={"log": log}, timeout=300)
print(r.json())