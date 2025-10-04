Packaged Models
===============

This folder contains a small wrapper to make it easy to use the DeepSafe
detectors from another application.

Two integration options are provided:

1) Python import: use the ModelRunner class to run a model and get the
   probability result.

   Example:

   ```python
   from packaged_models import ModelRunner

   runner = ModelRunner(models_root="./models", python_exe="python3")
   prob = runner.run_model("cnndetection_image")
   print(prob)
   ```

2) REST API (cross-language): run the included FastAPI server and call
   POST /predict with JSON {"model": "cnndetection_image"}.

   Install dependencies: fastapi, uvicorn

   Start server:

   ```bash
   uvicorn packaged_models.server:app --reload
   ```

Notes
-----
- This wrapper intentionally executes the existing `demo.py` scripts so you
  don't need to refactor model code. The model demo scripts are expected to
  write a single numeric probability to `models/<model>/result.txt`.
- If you plan to call models at high throughput or from multiple processes,
  consider converting model weights to a standard format (ONNX) and writing a
  dedicated inference service.
