import importlib
import os
import subprocess
import time
from typing import Optional


class ModelRunner:
    """Run an existing DeepSafe model and return its prediction.

    Usage:
        runner = ModelRunner(models_root="./models")
        prob = runner.run_model("cnndetection_image")

    The DeepSafe models are expected to provide a `demo.py` that when run
    writes a single float probability to `models/<model>/result.txt`.
    """

    def __init__(self, models_root: str = "./models", python_exe: str = "python3"):
        self.models_root = models_root
        self.python_exe = python_exe
        # project root is the parent of the models folder
        self.project_root = os.path.abspath(os.path.join(self.models_root, os.pardir))

    def _demo_path(self, model_name: str) -> str:
        return os.path.join(self.models_root, model_name, "demo.py")

    def _result_path(self, model_name: str) -> str:
        return os.path.join(self.models_root, model_name, "result.txt")

    def run_model(self, model_name: str, timeout: Optional[int] = 60) -> Optional[float]:
        """Run the model's demo script and return the float result or None.

        model_name should be the folder name inside `models/`, e.g. "cnndetection_image".
        """
        demo = self._demo_path(model_name)
        if not os.path.exists(demo):
            raise FileNotFoundError(f"demo.py not found for model {model_name} at {demo}")

        # Run the demo script as a subprocess. Many demo scripts call `subprocess` or
        # run shell scripts themselves; invoking them as a subprocess keeps behaviour
        # identical to the original app.
        start = time.time()
        proc = subprocess.Popen([self.python_exe, demo], cwd=self.project_root)
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise TimeoutError(f"Model demo for {model_name} timed out after {timeout}s")

        # Read result
        result_file = self._result_path(model_name)
        if not os.path.exists(result_file):
            return None
        try:
            with open(result_file, "r") as f:
                text = f.readline().strip()
                return float(text)
        except Exception:
            return None

    def run_image_ensemble(self, timeout: Optional[int] = 90) -> dict:
        """Run the four image detectors and return per-model probabilities + average.

        The four models are: `cnndetection_image`, `ganimagedetection_image`,
        `faceforensics_image`, and `photoshop_fal_image`.

        Returns a dict: { 'per_model': {model: prob or None}, 'average': avg_or_None }
        """
        models = [
            "cnndetection_image",
            "ganimagedetection_image",
            "faceforensics_image",
            "photoshop_fal_image",
        ]
        results = {}
        probs = []
        for m in models:
            try:
                p = self.run_model(m, timeout=timeout)
            except Exception as e:
                p = None
            results[m] = p
            if p is not None:
                probs.append(float(p))

        avg = None
        if len(probs) > 0:
            avg = round(sum(probs) / len(probs), 6)

        return {"per_model": results, "average": avg}

    def run_video_ensemble(self, timeout: Optional[int] = 120) -> dict:
        """Run the three video detectors and return per-model probabilities + average.

        The three models are: `cvit_video`, `deepware_video`, and `selim_video`.

        Returns a dict: { 'per_model': {model: prob or None}, 'average': avg_or_None }
        """
        models = [
            "cvit_video",
            "deepware_video",
            "selim_video",
        ]
        results = {}
        probs = []
        for m in models:
            try:
                p = self.run_model(m, timeout=timeout)
            except Exception:
                p = None
            results[m] = p
            if p is not None:
                probs.append(float(p))

        avg = None
        if len(probs) > 0:
            avg = round(sum(probs) / len(probs), 6)

        return {"per_model": results, "average": avg}
