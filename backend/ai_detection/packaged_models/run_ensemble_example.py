"""Example: run the four image detectors and print the average DeepFake probability.

This script adjusts sys.path so you can run it directly from the repo without
installing the `packaged_models` package.
"""
import os
import sys

# Ensure repo root is on sys.path so `packaged_models` can be imported when run
# directly (python packaged_models/run_ensemble_example.py)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from packaged_models import ModelRunner


def main():
    runner = ModelRunner(models_root="./models", python_exe="python3")
    print("Image ensemble:")
    res_img = runner.run_image_ensemble()
    for k, v in res_img["per_model"].items():
        print(f"  {k}: {v}")
    print(f"Average image probability: {res_img['average']}")

    print("\nVideo ensemble:")
    res_vid = runner.run_video_ensemble()
    for k, v in res_vid["per_model"].items():
        print(f"  {k}: {v}")
    print(f"Average video probability: {res_vid['average']}")


if __name__ == "__main__":
    main()
