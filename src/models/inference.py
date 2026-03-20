"""
KATS Inference Engine
Provides a unified interface to load and use all trained KATS models.

Combines predictions from:
1. ANN Regressor (The Biologist) - water and fertilizer predictions
2. SVM Classifier (The Guard) - disease classification
3. Random Forest (The Strategist) - scheduling predictions (time slot, priority)

With optional decision fusion for safety-critical recommendations.

Author: KATS ML Engineering Team
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"


# ============================================================================
# KATS INFERENCE ENGINE
# ============================================================================

class KatsInferenceEngine:
    """
    Production inference engine for KATS models.
    Loads trained models and provides predictions with optional fusion.
    """

    def __init__(self, models_dir: Path = MODELS_DIR):
        """
        Initialize inference engine and load all trained models.
        
        Args:
            models_dir: Directory containing trained model files
            
        Raises:
            FileNotFoundError: If any model file is missing
        """
        self.models_dir = models_dir
        
        # Models (lazy loaded)
        self._ann_model = None
        self._svm_model = None
        self._rf_time_slot_model = None
        self._rf_priority_model = None
        
        logger.info("KatsInferenceEngine initialized")
        logger.info(f"  Models directory: {self.models_dir}")
        
        # Validate models exist
        self._validate_models()
    
    def _validate_models(self):
        """Validate that all required model files exist."""
        required_models = [
            "ann_model.pkl",
            "svm_model.pkl",
            "rf_time_slot_model.pkl",
            "rf_priority_model.pkl",
        ]
        
        missing = []
        for model_file in required_models:
            path = self.models_dir / model_file
            if not path.exists():
                missing.append(model_file)
        
        if missing:
            raise FileNotFoundError(
                f"Missing required models: {missing}\n"
                f"Expected location: {self.models_dir}"
            )
        
        logger.info(f"✓ All required models found in {self.models_dir}")
    
    # ========================================================================
    # LAZY MODEL LOADING
    # ========================================================================
    
    @property
    def ann_model(self):
        """Load ANN model on first access."""
        if self._ann_model is None:
            logger.info("Loading ANN model...")
            self._ann_model = joblib.load(self.models_dir / "ann_model.pkl")
            logger.info("  ✓ ANN model loaded")
        return self._ann_model
    
    @property
    def svm_model(self):
        """Load SVM model on first access."""
        if self._svm_model is None:
            logger.info("Loading SVM model...")
            self._svm_model = joblib.load(self.models_dir / "svm_model.pkl")
            logger.info("  ✓ SVM model loaded")
        return self._svm_model
    
    @property
    def rf_time_slot_model(self):
        """Load RF time slot model on first access."""
        if self._rf_time_slot_model is None:
            logger.info("Loading RF time slot model...")
            self._rf_time_slot_model = joblib.load(
                self.models_dir / "rf_time_slot_model.pkl"
            )
            logger.info("  ✓ RF time slot model loaded")
        return self._rf_time_slot_model
    
    @property
    def rf_priority_model(self):
        """Load RF priority model on first access."""
        if self._rf_priority_model is None:
            logger.info("Loading RF priority model...")
            self._rf_priority_model = joblib.load(
                self.models_dir / "rf_priority_model.pkl"
            )
            logger.info("  ✓ RF priority model loaded")
        return self._rf_priority_model
    
    # ========================================================================
    # SINGLE SAMPLE PREDICTION
    # ========================================================================
    
    def predict_ann(
        self,
        temp: float,
        humidity: float,
        solar_radiation: float,
        wind_speed: float,
        soil_moisture: float,
        soil_ec: float,
        floor_level: int,
        orientation: float,
    ) -> Dict[str, float]:
        """
        Predict water volume and fertilizer dose using ANN.
        
        Args:
            temp: Temperature (°C)
            humidity: Humidity (%)
            solar_radiation: Solar radiation (kWh/m²)
            wind_speed: Wind speed (m/s)
            soil_moisture: Soil moisture (%)
            soil_ec: Soil electrical conductivity (µS/cm)
            floor_level: Building floor level (1-5)
            orientation: Rooftop orientation (degrees, 0-360)
        
        Returns:
            Dict with water_volume_L and fertilizer_dose_mL
        """
        X = np.array([[
            temp, humidity, solar_radiation, wind_speed,
            soil_moisture, soil_ec, floor_level, orientation
        ]])
        
        water, fertilizer = self.ann_model.predict(X)[0]
        
        return {
            "water_volume_L": float(water),
            "fertilizer_dose_mL": float(fertilizer),
        }
    
    def predict_svm(
        self,
        ndvi: float,
        nir_red: float,
        red_edge: float,
        swir: float,
        ndvi_delta: float,
        crop_type: int,
    ) -> Dict[str, object]:
        """
        Predict disease classification using SVM.
        
        Args:
            ndvi: NDVI index
            nir_red: NIR/Red ratio
            red_edge: Red edge index
            swir: Shortwave infrared
            ndvi_delta: 3-day NDVI change
            crop_type: Crop type (encoded)
        
        Returns:
            Dict with disease_label and interpretation
        """
        X = np.array([[ndvi, nir_red, red_edge, swir, ndvi_delta, crop_type]])
        
        disease_label = int(self.svm_model.predict(X)[0])
        
        disease_map = {
            0: "Healthy",
            1: "Mild",
            2: "Moderate",
            3: "Severe",
        }
        
        return {
            "disease_label": disease_label,
            "disease_status": disease_map.get(disease_label, "Unknown"),
        }
    
    def predict_rf(
        self,
        city_water_pressure: float,
        tariff_slot: int,
        weather_24h: int,
        active_buildings: int,
    ) -> Dict[str, object]:
        """
        Predict urban scheduling using Random Forest.
        
        UPDATED: Re-introduced tariff_slot with noise-injection strategy.
        
        The model uses tariff slot as a strong signal, but the model was
        trained with 25% artificial noise injected into tariff_slot to
        simulate real-world human behavior that doesn't follow tariffs perfectly.
        This breaks the synthetic data's deterministic leakage (99% accuracy)
        and produces realistic predictions (74-77% accuracy).
        
        Features used:
        - City water pressure (network load)
        - Tariff slot (time-of-day pricing tier, with noise adjustment)
        - Weather (operational constraints)
        - Active buildings (demand)
        
        Args:
            city_water_pressure: City water pressure (PSI)
            tariff_slot: Electricity tariff slot (1=Peak, 2=Off-peak, 3=Super off-peak)
            weather_24h: Weather condition (encoded 0-5)
            active_buildings: Number of active buildings (50-200)
        
        Returns:
            Dict with time_slot and building_priority
        """
        # Feature array: [city_water_pressure, tariff_slot, weather_24h, active_buildings]
        X = np.array([[city_water_pressure, tariff_slot, weather_24h, active_buildings]])
        
        time_slot = int(self.rf_time_slot_model.predict(X)[0])
        priority = float(self.rf_priority_model.predict(X)[0])
        
        time_slot_map = {
            0: "00:00-03:00",
            1: "03:00-06:00",
            2: "06:00-09:00",
            3: "09:00-12:00",
            4: "12:00-15:00",
            5: "15:00-18:00",
            6: "18:00-21:00",
            7: "21:00-24:00",
        }
        
        return {
            "time_slot": time_slot,
            "time_window": time_slot_map.get(time_slot, "Unknown"),
            "building_priority": float(priority),
        }
    
    # ========================================================================
    # BATCH PREDICTION
    # ========================================================================
    
    def predict_ann_batch(self, X_ann: pd.DataFrame) -> pd.DataFrame:
        """
        Batch predict water and fertilizer for multiple samples.
        
        Args:
            X_ann: DataFrame with 8 ANN features
        
        Returns:
            DataFrame with water_volume_L and fertilizer_dose_mL
        """
        predictions = self.ann_model.predict(X_ann)
        return pd.DataFrame(
            predictions,
            columns=["water_volume_L", "fertilizer_dose_mL"],
        )
    
    def predict_svm_batch(self, X_svm: pd.DataFrame) -> pd.DataFrame:
        """
        Batch predict disease labels.
        
        Args:
            X_svm: DataFrame with 6 SVM features
        
        Returns:
            DataFrame with disease_label and disease_status
        """
        labels = self.svm_model.predict(X_svm)
        
        disease_map = {
            0: "Healthy",
            1: "Mild",
            2: "Moderate",
            3: "Severe",
        }
        
        return pd.DataFrame({
            "disease_label": labels,
            "disease_status": [disease_map.get(int(l), "Unknown") for l in labels],
        })
    
    def predict_rf_batch(self, X_rf: pd.DataFrame) -> pd.DataFrame:
        """
        Batch predict scheduling.
        
        Args:
            X_rf: DataFrame with 4 RF features
        
        Returns:
            DataFrame with time_slot and building_priority
        """
        time_slots = self.rf_time_slot_model.predict(X_rf)
        priorities = self.rf_priority_model.predict(X_rf)
        
        time_slot_map = {
            0: "00:00-03:00",
            1: "03:00-06:00",
            2: "06:00-09:00",
            3: "09:00-12:00",
            4: "12:00-15:00",
            5: "15:00-18:00",
            6: "18:00-21:00",
            7: "21:00-24:00",
        }
        
        return pd.DataFrame({
            "time_slot": time_slots,
            "time_window": [time_slot_map.get(int(t), "Unknown") for t in time_slots],
            "building_priority": priorities,
        })
    
    # ========================================================================
    # UNIFIED PREDICTION (All Models)
    # ========================================================================
    
    def predict(
        self,
        X_ann: Optional[pd.DataFrame] = None,
        X_svm: Optional[pd.DataFrame] = None,
        X_rf: Optional[pd.DataFrame] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Unified prediction interface for all three models.
        
        Args:
            X_ann: DataFrame with ANN features (8 columns)
            X_svm: DataFrame with SVM features (6 columns)
            X_rf: DataFrame with RF features (4 columns)
        
        Returns:
            Dict with predictions from each model
        """
        results = {}
        
        if X_ann is not None:
            logger.info(f"Predicting ANN for {len(X_ann)} samples...")
            results["ann"] = self.predict_ann_batch(X_ann)
        
        if X_svm is not None:
            logger.info(f"Predicting SVM for {len(X_svm)} samples...")
            results["svm"] = self.predict_svm_batch(X_svm)
        
        if X_rf is not None:
            logger.info(f"Predicting RF for {len(X_rf)} samples...")
            results["rf"] = self.predict_rf_batch(X_rf)
        
        return results
    
    # ========================================================================
    # DECISION FUSION (Optional Safety Layer)
    # ========================================================================
    
    def fuse_predictions(
        self,
        water_L: float,
        fertilizer_mL: float,
        disease_label: int,
        time_slot: int,
        priority: float,
    ) -> Dict[str, object]:
        """
        Fuse predictions from all models into safety-aware recommendations.
        
        Args:
            water_L: Predicted water volume
            fertilizer_mL: Predicted fertilizer dose
            disease_label: Predicted disease (0-3)
            time_slot: Predicted time slot (0-7)
            priority: Predicted priority (1-5)
        
        Returns:
            Dict with fused recommendations and confidence
        """
        logger.info("Applying decision fusion...")
        
        # Disease severity adjustment
        if disease_label == 3:  # Severe
            adjustment = 1.2  # Increase water/fertilizer for disease management
            confidence = 0.7
            warning = "SEVERE DISEASE DETECTED - Increase intervention"
        elif disease_label == 2:  # Moderate
            adjustment = 1.1
            confidence = 0.75
            warning = "Moderate disease detected - Monitor closely"
        elif disease_label == 1:  # Mild
            adjustment = 1.0
            confidence = 0.85
            warning = None
        else:  # Healthy
            adjustment = 1.0
            confidence = 0.95
            warning = None
        
        # Water pressure constraints
        if time_slot in [6, 7, 0]:  # Evening/night (peak demand)
            tariff_adjustment = 0.85  # Reduce water during peak
        else:
            tariff_adjustment = 1.0
        
        # Final recommendations
        adjusted_water = water_L * adjustment * tariff_adjustment
        adjusted_fertilizer = fertilizer_mL * adjustment
        
        # Build schedule window
        time_slot_map = {
            0: "00:00-03:00", 1: "03:00-06:00", 2: "06:00-09:00",
            3: "09:00-12:00", 4: "12:00-15:00", 5: "15:00-18:00",
            6: "18:00-21:00", 7: "21:00-24:00",
        }
        
        return {
            "recommendation": {
                "water_volume_L": round(adjusted_water, 2),
                "fertilizer_dose_mL": round(adjusted_fertilizer, 2),
                "irrigation_window": time_slot_map.get(time_slot, "Unknown"),
                "building_priority": round(priority, 1),
            },
            "safety": {
                "disease_status": ["Healthy", "Mild", "Moderate", "Severe"][disease_label],
                "confidence": round(confidence, 2),
                "warning": warning,
            },
            "raw_predictions": {
                "water_volume_L": round(water_L, 2),
                "fertilizer_dose_mL": round(fertilizer_mL, 2),
                "disease_label": disease_label,
                "time_slot": time_slot,
                "building_priority": round(priority, 1),
            },
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_single_prediction():
    """Example: Single sample prediction with all models."""
    logger.info("\n=== SINGLE SAMPLE PREDICTION ===\n")
    
    engine = KatsInferenceEngine()
    
    # ANN prediction
    ann_pred = engine.predict_ann(
        temp=22.5,
        humidity=65.0,
        solar_radiation=5.5,
        wind_speed=8.2,
        soil_moisture=50.0,
        soil_ec=950,
        floor_level=2,
        orientation=180,
    )
    logger.info(f"ANN Prediction: {ann_pred}")
    
    # SVM prediction
    svm_pred = engine.predict_svm(
        ndvi=0.65,
        nir_red=2.8,
        red_edge=0.5,
        swir=0.3,
        ndvi_delta=-0.02,
        crop_type=2,
    )
    logger.info(f"SVM Prediction: {svm_pred}")
    
    # RF prediction
    rf_pred = engine.predict_rf(
        city_water_pressure=85.0,
        tariff_slot=2,
        weather_24h=1,
        active_buildings=12,
    )
    logger.info(f"RF Prediction: {rf_pred}")
    
    # Decision fusion
    fused = engine.fuse_predictions(
        water_L=ann_pred["water_volume_L"],
        fertilizer_mL=ann_pred["fertilizer_dose_mL"],
        disease_label=svm_pred["disease_label"],
        time_slot=rf_pred["time_slot"],
        priority=rf_pred["building_priority"],
    )
    logger.info(f"\nFused Recommendation:")
    logger.info(json.dumps(fused, indent=2))
    
    return fused


def example_batch_prediction():
    """Example: Batch prediction from CSV."""
    logger.info("\n=== BATCH PREDICTION ===\n")
    
    engine = KatsInferenceEngine()
    
    # Create sample data
    X_ann = pd.DataFrame({
        "temp": [20.0, 22.0, 21.5],
        "humidity": [70.0, 65.0, 68.0],
        "solar_radiation": [5.0, 6.0, 5.5],
        "wind_speed": [7.0, 8.0, 7.5],
        "soil_moisture": [45.0, 50.0, 48.0],
        "soil_EC": [900, 950, 925],
        "floor_level": [1, 2, 3],
        "orientation": [180, 180, 180],
    })
    
    X_svm = pd.DataFrame({
        "NDVI": [0.60, 0.65, 0.62],
        "NIR_red": [2.5, 2.8, 2.7],
        "red_edge": [0.45, 0.50, 0.48],
        "SWIR": [0.25, 0.30, 0.28],
        "3day_NDVI_delta": [-0.05, -0.02, -0.03],
        "crop_type": [1, 2, 1],
    })
    
    X_rf = pd.DataFrame({
        "city_water_pressure": [80.0, 85.0, 82.0],
        "tariff_slot": [1, 2, 2],
        "weather_24h": [0, 1, 1],
        "active_buildings": [10, 12, 11],
    })
    
    # Predict
    predictions = engine.predict(X_ann=X_ann, X_svm=X_svm, X_rf=X_rf)
    
    # Display results
    logger.info("ANN Predictions:")
    logger.info(predictions["ann"].to_string())
    logger.info("\nSVM Predictions:")
    logger.info(predictions["svm"].to_string())
    logger.info("\nRF Predictions:")
    logger.info(predictions["rf"].to_string())
    
    return predictions


if __name__ == "__main__":
    logger.info("\n" + "=" * 70)
    logger.info("KATS INFERENCE ENGINE - EXAMPLES")
    logger.info("=" * 70)
    
    try:
        # Run examples
        single_result = example_single_prediction()
        batch_results = example_batch_prediction()
        
        logger.info("\n" + "=" * 70)
        logger.info("Examples completed successfully!")
        logger.info("=" * 70 + "\n")
    
    except Exception as e:
        logger.exception(f"Error running examples: {e}")
