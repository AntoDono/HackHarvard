# Deepfake Detection Module

A simplified interface for detecting AI-generated/deepfake images using multiple detection models.

## Status: ⚠️ Models Not Included

**Important:** This module requires trained model weights that are NOT included in this directory. The `models/` folder is missing and must be obtained separately.

## Structure

```
ai_detection/
├── deepfake_detector.py     # Main interface - USE THIS
├── packaged_models/          # Core model runner
│   ├── model_runner.py
│   └── server.py             # Optional FastAPI server
├── requirements.txt          # Python dependencies
└── models/                   # ⚠️ MISSING - Required for functionality
    ├── cnndetection_image/
    ├── ganimagedetection_image/
    ├── faceforensics_image/
    └── photoshop_fal_image/
```

## Usage

Once you have the models folder in place:

```python
from ai_detection.deepfake_detector import detect_deepfake_from_path

# Simple usage
result = detect_deepfake_from_path("path/to/image.jpg")

print(f"Is deepfake: {result['is_deepfake']}")
print(f"Confidence: {result['probability']:.2%}")
print(f"Per-model results: {result['per_model']}")
```

Or use the class interface:

```python
from ai_detection.deepfake_detector import DeepfakeDetector

detector = DeepfakeDetector()
result = detector.detect_deepfake("path/to/image.jpg")
```

## Models Used

The detection ensemble includes 4 image detection models:
- `cnndetection_image` - CNN-based detection
- `ganimagedetection_image` - GAN-generated image detection  
- `faceforensics_image` - Face manipulation detection
- `photoshop_fal_image` - Photoshop manipulation detection

Each model returns a probability (0-1) and the final result is averaged across all models.

## Next Steps

To make this functional, you need to:
1. Obtain the trained model weights (models folder)
2. Install dependencies: `pip install -r requirements.txt`
3. Test with: `python -c "from deepfake_detector import detect_deepfake_from_path; print(detect_deepfake_from_path('test_image.jpg'))"`
