# KATS API REFERENCE

Complete API documentation for all KATS components.

## Table of Contents
1. [Data Processor API](#data-processor-api)
2. [Model Trainer API](#model-trainer-api)
3. [Inference Engine API](#inference-engine-api)

---

## Data Processor API

### Module: `src.utils.data_processor`

#### Class: `KATSPreprocessingPipeline`

Main orchestrator for the preprocessing pipeline.

**Constructor**:
```python
pipeline = KATSPreprocessingPipeline(
    base_dir: Path = BASE_DIR  # Project root directory
)
```

**Methods**:

##### `run() → None`
Executes full preprocessing pipeline for all three models.

```python
pipeline = KATSPreprocessingPipeline()
pipeline.run()
```

**Output**:
- `data/processed/train_ann_processed.csv`
- `data/processed/train_svm_processed.csv`
- `data/processed/train_rf_processed.csv`

---

#### Class: `ANNDataProcessor`

Processes environmental data for water/fertilizer prediction.

**Constructor**:
```python
processor = ANNDataProcessor()
```

**Methods**:

##### `process(path: Path) → pd.DataFrame`

Processes raw crop data for ANN training.

**Input Features**:
- temp: Temperature (°C)
- humidity: Relative humidity (%)
- solar_rad: Solar radiation (kWh/m²)
- wind: Wind speed (m/s)
- soil_moisture: Soil moisture (%)

**Output Features** (10 columns):
- temp, humidity, solar_rad, wind, soil_moisture (inputs)
- soil_ec (generated: electrical conductivity)
- floor_level (generated: 1-5 for rooftop height)
- orientation (generated: 0-360° compass direction)
- water_volume_L (target: liters)
- fertilizer_dose_mL (target: milliliters)

```python
ann_proc = ANNDataProcessor()
df = ann_proc.process(path="ANN/Crop_recommendationV2.csv")
# Returns: DataFrame with 2,200 rows × 10 columns
```

---

#### Class: `SVMDataProcessor`

Processes spectral vegetation data for disease classification.

**Constructor**:
```python
processor = SVMDataProcessor()
```

**Methods**:

##### `process(path: Path) → pd.DataFrame`

Processes crop yield data with spectral indices for SVM training.

**Input Features**:
- Any column that could be NDVI (typically "NDVI_index" or "NDV Index")
- crop_disease_status (target, encoded as 0-3)

**Output Features** (7 columns):
- NDVI: Normalized Difference Vegetation Index
- NIR_red: NIR/Red band ratio
- red_edge: Red edge reflectance
- SWIR: Shortwave infrared
- 3day_NDVI_delta: 3-day change in NDVI
- crop_type (generated: 0-4 types)
- disease_label (target: 0=Healthy, 1=Mild, 2=Moderate, 3=Severe)

```python
svm_proc = SVMDataProcessor()
df = svm_proc.process(path="ANN/Smart_Farming_Crop_Yield_2024.csv")
# Returns: DataFrame with 500 rows × 7 columns
```

---

#### Class: `RFDataProcessor`

Processes scheduling data for irrigation timing and priority.

**Constructor**:
```python
processor = RFDataProcessor()
```

**Methods**:

##### `process(path: Path) → pd.DataFrame`

Generates urban scheduling features for Random Forest training.

**Output Features** (4 columns):
- city_water_pressure: Water system pressure (PSI), generated 50-100
- tariff_slot: Electricity tariff period (1=Peak, 2=Off-peak, 3=Super off-peak)
- weather_24h: 24-hour weather forecast (0=clear, 1=cloudy, 2=rainy)
- active_buildings: Number of active buildings in network (5-20)

**Output Targets** (2 columns):
- time_slot: Optimal irrigation time (0-7 representing 3-hour windows)
- building_priority: Urgency for this building (1-5 scale)

```python
rf_proc = RFDataProcessor()
df = rf_proc.process(path="RF/crop_yield.csv")
# Returns: DataFrame with 1,000,000 rows × 6 columns
```

---

#### Utility Functions

##### `load_csv_safe(path: Path) → pd.DataFrame`

Safely loads CSV with robust error handling.

```python
from src.utils.data_processor import load_csv_safe

df = load_csv_safe("ANN/Crop_recommendationV2.csv")
```

**Handles**:
- Missing files
- Encoding errors
- Malformed CSV
- Empty files

---

##### `safe_column_rename(df: pd.DataFrame, mapping: dict) → pd.DataFrame`

Safely renames columns with flexible matching.

```python
df_renamed = safe_column_rename(df, {
    "NDVI_index": "NDVI",
    "crop_disease_status": "disease_label"
})
```

---

##### `get_or_generate_column(df: pd.DataFrame, column: str, generator_func) → np.ndarray`

Gets column if exists, otherwise generates values.

```python
soil_ec = get_or_generate_column(
    df, 
    "soil_EC", 
    lambda n: np.random.uniform(900, 1100, n)
)
```

---

## Model Trainer API

### Module: `src.models.train_models`

#### Class: `KatsModelTrainer`

Orchestrates training for all KATS models.

**Constructor**:
```python
trainer = KatsModelTrainer(
    data_dir: Path = DATA_DIR,      # Preprocessed data directory
    models_dir: Path = MODELS_DIR,  # Model save directory
    reports_dir: Path = REPORTS_DIR # Reports save directory
)
```

**Methods**:

##### `run() → None`

Trains all models, evaluates, and saves results.

```python
trainer = KatsModelTrainer()
trainer.run()
```

**Outputs**:
- Models: `models/ann_model.pkl`, `svm_model.pkl`, `rf_*.pkl`
- Metrics: `reports/metrics_*.json`
- Report: `reports/report_svm_classification.txt`

---

#### Training Details

##### ANN Training (`_train_ann()`)

**Algorithm**: MLPRegressor
- **Hidden layers**: (128, 64, 32)
- **Activation**: ReLU
- **Optimizer**: Adam
- **Max iterations**: 500
- **Early stopping**: Yes (patience=10)
- **Scaling**: StandardScaler

**Input**: 8 features (temp, humidity, solar_rad, wind, soil_moisture, soil_ec, floor_level, orientation)

**Output**: 2 targets (water_volume_L, fertilizer_dose_mL)

**Train/Test Split**: 80/20, random_state=42

---

##### SVM Training (`_train_svm()`)

**Algorithm**: SVC (Support Vector Classification)
- **Kernel**: RBF (Radial Basis Function)
- **C parameter**: 1.0
- **Probability**: Enabled
- **Scaling**: StandardScaler

**Input**: 6 features (NDVI, NIR_red, red_edge, SWIR, 3day_NDVI_delta, crop_type)

**Output**: 1 target (disease_label: 0-3)

**Train/Test Split**: Stratified 80/20 to preserve class balance

---

##### Random Forest Training (`_train_rf()`)

**Time Slot Model**:
- **Algorithm**: RandomForestClassifier
- **N estimators**: 100
- **Max depth**: 20
- **Input**: 4 features (water_pressure, tariff_slot, weather_24h, active_buildings)
- **Output**: time_slot (0-7)

**Priority Model**:
- **Algorithm**: RandomForestRegressor
- **N estimators**: 100
- **Max depth**: 20
- **Input**: 4 features (water_pressure, tariff_slot, weather_24h, active_buildings)
- **Output**: building_priority (1-5)

**Train/Test Split**: 80/20, random_state=42

---

#### Evaluation Metrics

##### ANN Evaluation

```json
{
  "R2_water": 0.0055,
  "MAE_water_L": 15.95,
  "RMSE_water_L": 28.42,
  "R2_fertilizer": -0.0012,
  "MAE_fertilizer_mL": 5.87,
  "RMSE_fertilizer_mL": 9.84
}
```

*Note: Low R² is expected with synthetic features. Real field data would improve accuracy significantly.*

---

##### SVM Evaluation

```json
{
  "accuracy": 0.51,
  "precision_macro": 0.42,
  "recall_macro": 0.35,
  "f1_macro": 0.345,
  "confusion_matrix": [...],
  "class_distribution": {
    "0_Healthy": 0.45,
    "1_Mild": 0.30,
    "2_Moderate": 0.18,
    "3_Severe": 0.07
  }
}
```

Plus detailed classification report per class.

---

##### RF Evaluation

```json
{
  "time_slot_accuracy": 0.123,
  "priority_R2": 0.166,
  "priority_MAE": 1.45,
  "priority_RMSE": 1.92
}
```

---

## Inference Engine API

### Module: `src.models.inference`

#### Class: `KatsInferenceEngine`

Production-grade inference engine with decision fusion.

**Constructor**:
```python
engine = KatsInferenceEngine(
    models_dir: Path = MODELS_DIR  # Directory containing trained models
)
```

**Raises**: `FileNotFoundError` if any required model is missing.

---

#### Single Prediction Methods

##### `predict_ann(...) → dict`

Predict water and fertilizer needs.

**Parameters**:
- `temp` (float): Temperature in °C
- `humidity` (float): Relative humidity (0-100%)
- `solar_radiation` (float): Solar radiation (kWh/m²)
- `wind_speed` (float): Wind speed (m/s)
- `soil_moisture` (float): Soil moisture (0-100%)
- `soil_ec` (float): Electrical conductivity (µS/cm)
- `floor_level` (int): Building floor (1-5)
- `orientation` (float): Rooftop orientation (0-360°)

**Returns**:
```python
{
  "water_volume_L": 45.32,
  "fertilizer_dose_mL": 12.15
}
```

**Example**:
```python
engine = KatsInferenceEngine()
pred = engine.predict_ann(
    temp=22.5, humidity=65.0, solar_radiation=5.5,
    wind_speed=8.2, soil_moisture=50.0, soil_ec=950,
    floor_level=2, orientation=180
)
```

---

##### `predict_svm(...) → dict`

Predict disease status.

**Parameters**:
- `ndvi` (float): NDVI index (0-1)
- `nir_red` (float): NIR/Red ratio (typically 1-4)
- `red_edge` (float): Red edge reflectance (0-1)
- `swir` (float): Shortwave infrared (0-1)
- `ndvi_delta` (float): 3-day NDVI change (-0.2 to +0.2)
- `crop_type` (int): Encoded crop type (0-4)

**Returns**:
```python
{
  "disease_label": 2,
  "disease_status": "Moderate"  # Healthy | Mild | Moderate | Severe
}
```

**Example**:
```python
pred = engine.predict_svm(
    ndvi=0.65, nir_red=2.8, red_edge=0.5,
    swir=0.3, ndvi_delta=-0.02, crop_type=2
)
```

---

##### `predict_rf(...) → dict`

Predict irrigation scheduling.

**Parameters**:
- `city_water_pressure` (float): Water system pressure (PSI)
- `tariff_slot` (int): Tariff period (1=Peak, 2=Off-peak, 3=Super off-peak)
- `weather_24h` (int): Weather forecast (0=Clear, 1=Cloudy, 2=Rainy)
- `active_buildings` (int): Number of active buildings (5-20)

**Returns**:
```python
{
  "time_slot": 4,
  "time_window": "12:00-15:00",
  "building_priority": 3.2
}
```

**Time Slots**:
- 0: 00:00-03:00
- 1: 03:00-06:00
- 2: 06:00-09:00
- 3: 09:00-12:00
- 4: 12:00-15:00
- 5: 15:00-18:00
- 6: 18:00-21:00
- 7: 21:00-24:00

**Example**:
```python
pred = engine.predict_rf(
    city_water_pressure=85.0,
    tariff_slot=2,
    weather_24h=1,
    active_buildings=12
)
```

---

#### Batch Prediction Methods

##### `predict_ann_batch(X_ann: pd.DataFrame) → pd.DataFrame`

Batch predict water and fertilizer for multiple samples.

**Input**: DataFrame with 8 columns (temp, humidity, solar_radiation, wind_speed, soil_moisture, soil_ec, floor_level, orientation)

**Returns**: DataFrame with water_volume_L and fertilizer_dose_mL columns

```python
X = pd.DataFrame({
    "temp": [20.0, 22.0, 21.5],
    "humidity": [70.0, 65.0, 68.0],
    "solar_radiation": [5.0, 6.0, 5.5],
    "wind_speed": [7.0, 8.0, 7.5],
    "soil_moisture": [45.0, 50.0, 48.0],
    "soil_ec": [900, 950, 925],
    "floor_level": [1, 2, 3],
    "orientation": [180, 180, 180]
})
results = engine.predict_ann_batch(X)
#    water_volume_L  fertilizer_dose_mL
# 0           43.12                10.45
# 1           45.87                12.23
# 2           44.50                11.34
```

---

##### `predict_svm_batch(X_svm: pd.DataFrame) → pd.DataFrame`

Batch predict disease labels.

**Input**: DataFrame with 6 columns (NDVI, NIR_red, red_edge, SWIR, 3day_NDVI_delta, crop_type)

**Returns**: DataFrame with disease_label and disease_status columns

---

##### `predict_rf_batch(X_rf: pd.DataFrame) → pd.DataFrame`

Batch predict scheduling.

**Input**: DataFrame with 4 columns (city_water_pressure, tariff_slot, weather_24h, active_buildings)

**Returns**: DataFrame with time_slot, time_window, and building_priority columns

---

#### Unified Prediction

##### `predict(X_ann=None, X_svm=None, X_rf=None) → dict`

Unified interface for all models in one call.

**Parameters** (all optional):
- `X_ann`: DataFrame for ANN (8 columns)
- `X_svm`: DataFrame for SVM (6 columns)
- `X_rf`: DataFrame for RF (4 columns)

**Returns**: Dict with keys for each provided model

```python
results = engine.predict(
    X_ann=df_ann,
    X_svm=df_svm,
    X_rf=df_rf
)
# {
#   "ann": DataFrame(water, fertilizer),
#   "svm": DataFrame(disease_label, disease_status),
#   "rf": DataFrame(time_slot, building_priority)
# }
```

---

#### Decision Fusion

##### `fuse_predictions(water_L, fertilizer_mL, disease_label, time_slot, priority) → dict`

Safety-aware fusion of all model outputs.

**Parameters**:
- `water_L` (float): Predicted water from ANN
- `fertilizer_mL` (float): Predicted fertilizer from ANN
- `disease_label` (int): 0=Healthy, 1=Mild, 2=Moderate, 3=Severe
- `time_slot` (int): Predicted time slot from RF (0-7)
- `priority` (float): Predicted priority from RF

**Returns**:
```python
{
  "recommendation": {
    "water_volume_L": 49.5,        # Adjusted
    "fertilizer_dose_mL": 13.2,    # Adjusted
    "irrigation_window": "12:00-15:00",
    "building_priority": 3.2
  },
  "safety": {
    "disease_status": "Moderate",
    "confidence": 0.75,           # Decreases with disease
    "warning": "Moderate disease detected - Monitor closely"  # or None
  },
  "raw_predictions": {
    "water_volume_L": 45.0,       # Original
    "fertilizer_dose_mL": 12.0,   # Original
    "disease_label": 2,
    "time_slot": 4,
    "building_priority": 3.2
  }
}
```

**Fusion Rules**:
1. **Disease Adjustment**:
   - Severe (3): 1.2× multiplier, confidence 0.70, warning enabled
   - Moderate (2): 1.1× multiplier, confidence 0.75, warning enabled
   - Mild (1): 1.0× multiplier, confidence 0.85, no warning
   - Healthy (0): 1.0× multiplier, confidence 0.95, no warning

2. **Tariff Adjustment**:
   - Evening/Night (slots 6, 7, 0): 0.85× water multiplier
   - Other times: 1.0× multiplier

**Example**:
```python
fused = engine.fuse_predictions(
    water_L=45.0,
    fertilizer_mL=12.0,
    disease_label=2,
    time_slot=4,
    priority=3.2
)

print(fused["recommendation"]["water_volume_L"])  # 49.5 (45 × 1.1 × 1.0)
print(fused["safety"]["confidence"])               # 0.75
print(fused["safety"]["warning"])                  # "Moderate disease..."
```

---

## Complete Usage Example

```python
from src.models.inference import KatsInferenceEngine
import pandas as pd

# Initialize engine
engine = KatsInferenceEngine()

# Single prediction
ann_result = engine.predict_ann(
    temp=22.5, humidity=65.0, solar_radiation=5.5,
    wind_speed=8.2, soil_moisture=50.0, soil_ec=950,
    floor_level=2, orientation=180
)

svm_result = engine.predict_svm(
    ndvi=0.65, nir_red=2.8, red_edge=0.5,
    swir=0.3, ndvi_delta=-0.02, crop_type=2
)

rf_result = engine.predict_rf(
    city_water_pressure=85.0,
    tariff_slot=2,
    weather_24h=1,
    active_buildings=12
)

# Fuse predictions for recommendation
recommendation = engine.fuse_predictions(
    water_L=ann_result["water_volume_L"],
    fertilizer_mL=ann_result["fertilizer_dose_mL"],
    disease_label=svm_result["disease_label"],
    time_slot=rf_result["time_slot"],
    priority=rf_result["building_priority"]
)

print(recommendation)
# {
#   "recommendation": {
#     "water_volume_L": 49.5,
#     "fertilizer_dose_mL": 13.2,
#     "irrigation_window": "12:00-15:00",
#     "building_priority": 3.2
#   },
#   ...
# }
```

---

## Error Handling

All methods include validation and logging:

```python
try:
    engine = KatsInferenceEngine()
except FileNotFoundError as e:
    print(f"Model loading failed: {e}")
    # Ensure models/ directory exists with all 4 .pkl files

try:
    pred = engine.predict_ann(
        temp=22.5, humidity=65.0, solar_radiation=5.5,
        wind_speed=8.2, soil_moisture=50.0, soil_ec=950,
        floor_level=2, orientation=180
    )
except Exception as e:
    print(f"Prediction failed: {e}")
    # Check input types and ranges
```

---

## Performance Characteristics

| Operation | Time | Memory |
|-----------|------|--------|
| Engine initialization | ~100ms | ~500MB |
| Single ANN prediction | <1ms | N/A |
| Single SVM prediction | <1ms | N/A |
| Single RF prediction | <1ms | N/A |
| Batch prediction (1K) | ~50ms | N/A |
| Decision fusion | <1ms | N/A |

---

## See Also

- **README.md**: System architecture and overview
- **SETUP_AND_RUN.md**: Installation and execution instructions
- **src/models/inference.py**: Source code with docstrings
- **reports/metrics_*.json**: Model performance metrics

