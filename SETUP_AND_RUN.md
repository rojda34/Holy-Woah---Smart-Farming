# SETUP AND RUN GUIDE

Complete step-by-step instructions for setting up and running the KATS preprocessing, training, and inference pipelines.

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- pandas (data manipulation)
- numpy (numerical computing)
- scikit-learn (machine learning)
- joblib (model persistence)
- openpyxl (optional, for Excel support)

### 2. Verify Installation

```bash
python -c "import pandas, numpy, sklearn, joblib; print('✓ All packages installed')"
```

## Running the Pipelines

### Option 1: Run Complete Pipeline (Preprocess + Train)

```bash
python examples.py
```

**What it does:**
1. Preprocesses raw CSV data (~/datasets/ANN/, ~/datasets/RF/)
2. Generates 3 processed datasets in `data/processed/`
3. Trains 4 models using processed data
4. Evaluates all models with metrics
5. Saves models to `models/`
6. Saves metrics to `reports/`

**Expected time**: ~10-15 minutes (depending on system)

**Expected output**:
```
INFO - Starting KATS Preprocessing Pipeline...
INFO - Loading Crop_recommendationV2.csv...
INFO - ✓ ANNDataProcessor: 2200 samples processed
INFO - ✓ SVMDataProcessor: 500 samples processed
INFO - ✓ RFDataProcessor: 1000000 samples processed
INFO - ✓ All datasets saved to data/processed/

INFO - Starting KATS Model Training...
INFO - Loading preprocessed data...
INFO - Training ANN model...
INFO - ✓ ANN trained. R²=0.0055, MAE(water)=15.95L
INFO - Training SVM model...
INFO - ✓ SVM trained. Accuracy=0.51
INFO - Training RF models...
INFO - ✓ RF Time Slot trained. Accuracy=0.123
INFO - ✓ RF Priority trained. R²=0.166
```

### Option 2: Run Only Preprocessing

```python
from src.utils.data_processor import KATSPreprocessingPipeline

pipeline = KATSPreprocessingPipeline()
pipeline.run()
```

**Output files**:
- `data/processed/train_ann_processed.csv` (2,200 × 10)
- `data/processed/train_svm_processed.csv` (500 × 6)
- `data/processed/train_rf_processed.csv` (1,000,000 × 4)

### Option 3: Run Only Training

(Requires preprocessed data from Option 2)

```python
from src.models.train_models import KatsModelTrainer

trainer = KatsModelTrainer()
trainer.run()
```

**Output files**:
- Models: `models/ann_model.pkl`, `svm_model.pkl`, `rf_time_slot_model.pkl`, `rf_priority_model.pkl`
- Metrics: `reports/metrics_*.json`
- SVM Report: `reports/report_svm_classification.txt`

### Option 4: Run Inference Only

(Requires trained models from Option 3)

```bash
python src/models/inference.py
```

Or programmatically:

```python
from src.models.inference import KatsInferenceEngine

engine = KatsInferenceEngine()

# Single prediction
pred = engine.predict_ann(
    temp=22.5, humidity=65.0, solar_radiation=5.5,
    wind_speed=8.2, soil_moisture=50.0, soil_ec=950,
    floor_level=2, orientation=180
)
print(pred)
```

## Manual Step-by-Step (Advanced)

If you need to run components separately:

### Step 1: Preprocess Data

```python
from src.utils.data_processor import ANNDataProcessor, SVMDataProcessor, RFDataProcessor
from pathlib import Path

base_dir = Path(".")

# ANN Preprocessing
ann = ANNDataProcessor()
df_ann = ann.process(path=base_dir / "ANN" / "Crop_recommendationV2.csv")
df_ann.to_csv("data/processed/train_ann_processed.csv", index=False)

# SVM Preprocessing  
svm = SVMDataProcessor()
df_svm = svm.process(path=base_dir / "ANN" / "Smart_Farming_Crop_Yield_2024.csv")
df_svm.to_csv("data/processed/train_svm_processed.csv", index=False)

# RF Preprocessing
rf = RFDataProcessor()
df_rf = rf.process(path=base_dir / "RF" / "crop_yield.csv")
df_rf.to_csv("data/processed/train_rf_processed.csv", index=False)
```

### Step 2: Train Models

```python
from src.models.train_models import KatsModelTrainer
import logging

logging.basicConfig(level=logging.INFO)

trainer = KatsModelTrainer()
trainer.run()
```

### Step 3: Load and Use Inference

```python
from src.models.inference import KatsInferenceEngine
import pandas as pd

engine = KatsInferenceEngine()

# Single prediction
result = engine.predict_ann(
    temp=20.0, humidity=70.0, solar_radiation=5.0,
    wind_speed=7.0, soil_moisture=45.0, soil_ec=900,
    floor_level=1, orientation=180
)

# Batch prediction
X_ann = pd.read_csv("data/processed/train_ann_processed.csv").iloc[:, :8]
results = engine.predict_ann_batch(X_ann)

# Decision fusion
fused = engine.fuse_predictions(
    water_L=result['water_volume_L'],
    fertilizer_mL=result['fertilizer_dose_mL'],
    disease_label=0,
    time_slot=4,
    priority=3.0
)
print(fused)
```

## Troubleshooting

### Issue: "FileNotFoundError: models/ann_model.pkl not found"
**Solution**: Run training first with `examples.py` or `KatsModelTrainer().run()`

### Issue: "ModuleNotFoundError: No module named 'sklearn'"
**Solution**: Run `pip install scikit-learn`

### Issue: "Memory error processing RF dataset"
**Solution**: The RF processor handles 1M rows efficiently. If memory constrained, reduce sample size in data_processor.py line 450.

### Issue: "Models directory doesn't exist"
**Solution**: Run `mkdir models reports data/processed` or let the pipeline create them automatically.

## Verifying Success

After running `examples.py`, check:

1. **Preprocessed data exists**:
   ```bash
   ls -la data/processed/
   ```
   Should show 3 CSV files with sizes >1MB

2. **Models are trained**:
   ```bash
   ls -la models/
   ```
   Should show 4 .pkl files totaling ~115MB

3. **Metrics are saved**:
   ```bash
   ls -la reports/
   ```
   Should show 4 JSON/text files

4. **Inference works**:
   ```bash
   python src/models/inference.py
   ```
   Should output predictions without errors

## Performance Expectations

| Task | Time | Output Size |
|------|------|------------|
| Preprocess Data | ~5 min | 20.5 MB |
| Train ANN | ~1 min | 5.2 MB |
| Train SVM | ~30 sec | 0.8 MB |
| Train RF (2 models) | ~3 min | 108 MB |
| Single Prediction | <1 ms | N/A |
| Batch Prediction (1K) | ~50 ms | N/A |

## Environment Variables (Optional)

```bash
# Set logging level
export LOGLEVEL=INFO

# Set model directory
export MODELS_DIR=/path/to/models

# Set data directory  
export DATA_DIR=/path/to/data
```

## Next Steps

After successful setup:
1. Review KATS_API_REFERENCE.md for detailed API documentation
2. Examine examples.py for implementation patterns
3. Check metrics in reports/metrics_*.json
4. Deploy inference engine to production

See README.md for architecture overview.
