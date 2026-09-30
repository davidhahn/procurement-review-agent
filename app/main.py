from fastapi import FastAPI

app = FastAPI(title="Procurement Review Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
