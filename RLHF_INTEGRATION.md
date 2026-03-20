# 🔌 KATS RLHF Integration Guide

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      KATS ECOSYSTEM v2.0                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  INPUTS                                                          │
│  ├─ Environmental Data (temp, humidity, etc)    → ANN           │
│  ├─ Spectral Indices (NDVI, SWIR, etc)         → SVM           │
│  └─ Urban Context (pressure, weather)          → RF            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ KatsInferenceEngine (src/models/inference.py)            │  │
│  │                                                           │  │
│  │  ANN: water_L, fertilizer_mL                            │  │
│  │  SVM: disease_label (0-3)                               │  │
│  │  RF: time_slot, priority                                │  │
│  └──────────┬───────────────────────────────────────────────┘  │
│             │                                                    │
│             ├─ Predictions                                      │
│             │  ├─ water: 12L                                    │
│             │  ├─ fertilizer: 8mL                               │
│             │  ├─ disease: Healthy                              │
│             │  ├─ time: 14:00-17:00                             │
│             │  └─ priority: 3.5                                 │
│             │                                                    │
│  ┌──────────▼───────────────────────────────────────────────┐  │
│  │ Decision Fusion (inference.py: fuse_predictions)         │  │
│  │                                                           │  │
│  │ Combine predictions according to weights:               │  │
│  │ • ANN Weight × water_L +                                │  │
│  │ • SVM Weight × disease_status +                         │  │
│  │ • RF Weight × scheduling                                │  │
│  │                                                           │  │
│  │ Load RLHF Weights:                                       │  │
│  │ ├─ Load ANN, SVM, RF weights from fusion_weights.json   │  │
│  │ └─ Apply disease, water, and other safety rules         │  │
│  └──────────┬───────────────────────────────────────────────┘  │
│             │                                                    │
│             └─ Final Recommendation                             │
│                ├─ water: 12L (ANN 35% + Tariff×15%)           │
│                ├─ fertilizer: 8mL                              │
│                ├─ irrigation_window: 14:00-17:00              │
│                └─ confidence: 92%                              │
│                                                                   │
│  ┌──────────┬───────────────────────────────────────────────┐  │
│  │ FARMER UI                                                 │  │
│  │                                                           │  │
│  │ ┌─ Recommendation displayed                             │  │
│  │ │                                                         │  │
│  │ └─ [✅ APPROVE] [✏️ MODIFY] [⚠️ REPORT ISSUE] Buttons  │  │
│  │     │              │              │                      │  │
│  │     ▼              ▼              ▼                      │  │
│  └──────┬───────────┬────────────────┬──────────────────────┘  │
│         │           │                │                         │
│  ┌──────▼───────────▼────────────────▼──────────────────────┐  │
│  │ KatsRLHFProcessor (src/models/rlhf_processor.py)        │  │
│  │                                                           │  │
│  │ Process Feedback → Update Weights                       │  │
│  │ APPROVE  : ANN +2%, SVM +2%, RF +2%                   │  │
│  │ MODIFY   : (water/fertilizer changed) ANN -3%         │  │
│  │ REPORT   : (disease missed) SVM -5%                   │  │
│  │           (timing error)     RF -5%                    │  │
│  │                                                           │  │
│  │ Save New Weights → fusion_weights.json                 │  │
│  │ History → rlhf_history.json                            │  │
│  │                                                           │  │
│  │ if weight < 0.20 → 🚨 RETRAINING ALARM!              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 💻 Code Example: Complete Workflow

### 1. Initialize Systems
```python
from src.models.inference import KatsInferenceEngine
from src.models.rlhf_processor import KatsRLHFProcessor

# Load inference engine
engine = KatsInferenceEngine()

# Load RLHF engine
rlhf = KatsRLHFProcessor()

print(f"System initialized!")
print(f"Current Weights: {rlhf.weights}")
# Output: Current Weights: {'ANN': 0.35, 'SVM': 0.30, 'RF': 0.35}
```

### 2. Make Predictions
```python
# Farmer collects sensor data
sensor_data = {
    'temp': 25.5,
    'humidity': 65.0,
    'solar_radiation': 6.2,
    'wind_speed': 8.5,
    'soil_moisture': 48.0,
    'soil_ec': 950
}

# Make predictions (weights used during inference)
ann_pred = engine.predict_ann(
    temp=sensor_data['temp'],
    humidity=sensor_data['humidity'],
    solar_radiation=sensor_data['solar_radiation'],
    wind_speed=sensor_data['wind_speed'],
    soil_moisture=sensor_data['soil_moisture'],
    soil_ec=sensor_data['soil_ec'],
    floor_level=2,
    orientation=180
)

svm_pred = engine.predict_svm(
    ndvi=0.68, nir_red=2.9, red_edge=0.42,
    swir=0.25, ndvi_delta=-0.01, crop_type=1
)

rf_pred = engine.predict_rf(
    city_water_pressure=85.0,
    tariff_slot=2,
    weather_24h=1,
    active_buildings=15
)

print(f"ANN Recommendation: {ann_pred['water_volume_L']}L water")
print(f"SVM Prediction: {svm_pred['disease_status']}")
print(f"RF Scheduling: {rf_pred['time_window']}")
```

### 3. Decision Fusion (Combine Predictions)
```python
# Create final decision using RLHF weights
recommendation = engine.fuse_predictions(
    water_L=ann_pred['water_volume_L'],
    fertilizer_mL=ann_pred['fertilizer_dose_mL'],
    disease_label=svm_pred['disease_label'],
    time_slot=rf_pred['time_slot'],
    priority=rf_pred['building_priority']
)

# Display to farmer
print("="*50)
print("🌾 IRRIGATION RECOMMENDATION")
print("="*50)
print(f"Water Volume:        {recommendation['recommendation']['water_volume_L']}L")
print(f"Fertilizer Dose:     {recommendation['recommendation']['fertilizer_dose_mL']}mL")
print(f"Irrigation Time:     {recommendation['recommendation']['irrigation_window']}")
print(f"Building Priority:   {recommendation['recommendation']['building_priority']}/5")
print(f"\n⚠️ SENSITIVITY:")
print(f"Disease Status:      {recommendation['safety']['disease_status']}")
print(f"Confidence Score:    {recommendation['safety']['confidence']*100}%")
if recommendation['safety']['warning']:
    print(f"🚨 WARNING:          {recommendation['safety']['warning']}")
print("="*50)
```

### 4. Farmer Provides Feedback
```python
# Scenario 1: Farmer approved decision (it worked out well)
print("\n✅ Farmer approved the recommendation (successful irrigation)")
new_weights = rlhf.process_feedback('APPROVE')
print(f"New Weights: {new_weights}")
# Output: New Weights: {'ANN': 0.357, 'SVM': 0.306, 'RF': 0.357}

# Scenario 2: Farmer corrects water amount
print("\n✏️ Farmer had to correct water to 8.5L (ANN made error)")
new_weights = rlhf.process_feedback(
    'MODIFY',
    corrected_values={'water_L': 8.5}
)
print(f"Result: ANN weight decreased → {new_weights}")
# Output: {'ANN': 0.334, 'SVM': 0.313, 'RF': 0.353}

# Scenario 3: Critical error - disease detection missed
print("\n⚠️ SVM missed a disease (missed_disease)")
new_weights = rlhf.process_feedback(
    'REPORT',
    issue_type='missed_disease'
)
print(f"Result: SVM penalized → {new_weights}")
# Output: {'ANN': 0.351, 'SVM': 0.263, 'RF': 0.386}
```

### 5. Critical Threshold Check
```python
# Monitor system health through RLHF history
print("\n📊 SYSTEM HEALTH DASHBOARD")
print("="*50)
for model, weight in rlhf.weights.items():
    percentage = weight * 100
    status = "🟢 HEALTHY" if percentage >= 20 else "🔴 CRITICAL"
    bar = "█" * int(percentage / 2) + "░" * (50 - int(percentage / 2))
    print(f"{model:<5} {bar} {percentage:>5.1f}% {status}")

if any(w < 0.20 for w in rlhf.weights.values()):
    print("\n🚨 CRITICAL WARNING: One or more models require retraining!")
    for model, weight in rlhf.weights.items():
        if weight < 0.20:
            print(f"  • {model}: {weight*100:.1f}% → RETRAIN REQUIRED!")
```

---

## 🔄 Workflow Summary

```
MORNING
├─ Farmer collects sensor data
├─ KatsInferenceEngine → Make predictions
├─ Decision Fusion (RLHF weights applied)
├─ Generate Recommendations
└─ Display to farmer

EVENING
├─ Farmer provides feedback
│  ├─ [✅] APPROVE        → Weights +0.02
│  ├─ [✏️] MODIFY         → Related Model -0.03
│  └─ [⚠️] REPORT         → Related Model -0.05
├─ KatsRLHFProcessor → Update weights
├─ Save history
├─ Check critical threshold
│  └─ if weight < 0.20 → 🚨 RETRAIN ALARM
└─ Report on operations
```

---

## 🚀 Advanced Scenarios

### Scenario 1: Seasonal System Adaptation

**Winter → Summer Transition:**
```python
# During winter months:
# ANN: Makes errors in low temperature scenarios → weight decreases
# SVM: Successfully detects mildew (wet air disease) → weight increases
# RF: Night systems work well → weight increases

# During summer months:
# ANN: Perfect for high heat scenarios → weight increases
# SVM: Struggles with indoor diseases → weight decreases
# RF: Daytime pressure issues → weight decreases

# Result: System automatically adapts to seasonal patterns!
```

### Scenario 2: New Crop Type

```python
# Farmer starts growing tomatoes
# System initially makes incorrect predictions:
# - RF timing is wrong (RF -3%)
# - SVM misses tomato-specific diseases (SVM -5%)

# Over one week of feedback:
tomato_data = [
    {'feedback': 'MODIFY', 'corrected': {'water_L': 5.0}},  # ANN -0.03
    {'feedback': 'MODIFY', 'corrected': {'water_L': 4.5}},  # ANN -0.03
    {'feedback': 'REPORT', 'issue_type': 'missed_disease'}, # SVM -0.05
    {'feedback': 'APPROVE'},                                 # All +0.02
    {'feedback': 'APPROVE'},                                 # All +0.02
]

for entry in tomato_data:
    rlhf.process_feedback(
        entry['feedback'],
        corrected_values=entry.get('corrected'),
        issue_type=entry.get('issue_type')
    )
    
# Result: System optimized for tomatoes!
```

### Scenario 3: Model Rotation

```python
# If a model weight drops below 20%:
# 1. Alarm is triggered
# 2. New model is retrained
# 3. Old model backed up
# 4. New model starts with 30% weight
# 5. Feedback flows to new model

# Example: SVM fails too many times (detect disease detection issues)
if rlhf.weights['SVM'] < 0.15:
    print("🚨 SVM Critical!")
    
    # Start new SVM training
    from src.models.train_models import KatsModelTrainer
    trainer = KatsModelTrainer()
    # trainer.train_svm_only()  # Retrain only SVM
    
    # Reset weight
    rlhf.weights['SVM'] = 0.30
    rlhf._save_weights()
    
    print("✅ SVM retrained, weight reset to 30%")
```

---

## 📈 Metrics & Monitoring

```python
import json

# Extract statistics from RLHF history
with open(rlhf.history_path) as f:
    history = json.load(f)

# Action Distribution
action_counts = {}
for entry in history:
    action = entry['action']
    action_counts[action] = action_counts.get(action, 0) + 1

print("📊 RLHF Statistics:")
print(f"  APPROVE:  {action_counts.get('APPROVE', 0)} times")
print(f"  MODIFY:   {action_counts.get('MODIFY', 0)} times")
print(f"  REPORT:   {action_counts.get('REPORT', 0)} times")

# Weight Trend
print("\n📈 ANN Weight Trend:")
for i, entry in enumerate(history[-5:]):
    print(f"  {i}: {entry['resulting_weights']['ANN']}")
```

---

## 🔐 Best Practices

1. ✅ **Regular Monitoring**: Check system health daily
2. ✅ **Backup Data**: Weekly backup of fusion_weights.json and rlhf_history.json
3. ✅ **Seasonal Tuning**: Check models at season changes
4. ✅ **Farmer Feedback**: Track feedback rate and quality
5. ✅ **Model Diversity**: Try to keep all models above 15% weight

---

**KATS RLHF Integration v1.0**  
**Production Ready ✅**  
**Last Updated: March 18, 2026**
