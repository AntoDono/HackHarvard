"""Tiny FastAPI server to serve packaged models.

This is optional — useful if your web app is not Python-based. Start with
`uvicorn packaged_models.server:app --reload` and POST to `/predict` with JSON
{"model": "cnndetection_image"}.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .model_runner import ModelRunner

app = FastAPI()
runner = ModelRunner()


class PredictRequest(BaseModel):
    model: str


@app.post("/predict")
def predict(req: PredictRequest):
    try:
        prob = runner.run_model(req.model)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))

    if prob is None:
        raise HTTPException(status_code=500, detail="Model did not produce a result")
    return {"model": req.model, "probability": prob}
