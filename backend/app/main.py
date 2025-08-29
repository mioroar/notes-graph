from fastapi import FastAPI

app = FastAPI(title="Notes Graph API")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
