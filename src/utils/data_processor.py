"""
KATS Data Preprocessing Pipeline
Urban rooftop farming ML models: ANN, SVM, Random Forest + Decision Fusion Layer

This module provides robust, extensible data preprocessing for three specialized models:
1. ANN Regressor (The Biologist) - predicts water_volume_L and fertilizer_dose_mL
2. SVM Classifier (The Guard) - predicts crop disease classification
3. Random Forest (The Strategist) - predicts urban scheduling (time_slot, building_priority)

Author: KATS ML Engineering Team
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Paths (configurable)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "ANN"  # Contains raw CSVs
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Disease mapping for SVM
DISEASE_LABEL_MAP = {
    "Healthy": 0,
    "Mild": 1,
    "Moderate": 2,
    "Severe": 3,
    "Unknown": 1,  # Default to Mild if unknown
}


# ============================================================================
# DATA LOADING UTILITIES
# ============================================================================

def load_csv_safe(filepath: str) -> Optional[pd.DataFrame]:
    """
    Safely load a CSV file with error handling and validation.
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        DataFrame if successful, None otherwise
    """
    try:
        logger.info(f"Loading CSV: {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"  -> Loaded {len(df)} rows x {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return None


def load_excel_safe(filepath: str, sheet_name: int = 0) -> Optional[pd.DataFrame]:
    """
    Safely load an Excel file with error handling.
    
    Args:
        filepath: Path to Excel file
        sheet_name: Sheet index (default: 0)
        
    Returns:
        DataFrame if successful, None otherwise
    """
    try:
        logger.info(f"Loading Excel: {filepath} (sheet {sheet_name})")
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        logger.info(f"  -> Loaded {len(df)} rows x {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return None


def safe_column_rename(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Safely rename columns that exist, log missing ones.
    
    Args:
        df: Input DataFrame
        mapping: Dict of {old_name: new_name} to apply
        
    Returns:
        DataFrame with renamed columns
    """
    rename_dict = {}
    for old, new in mapping.items():
        if old in df.columns:
            rename_dict[old] = new
        else:
            logger.warning(f"Column '{old}' not found in DataFrame")
    
    return df.rename(columns=rename_dict)


def get_or_generate_column(
    df: pd.DataFrame,
    col_name: str,
    source_col: Optional[str] = None,
    transform_fn: Optional[callable] = None,
    default_generator: Optional[callable] = None,
) -> pd.DataFrame:
    """
    Get column if exists; otherwise generate it via transform or default generator.
    
    Args:
        df: Input DataFrame
        col_name: Column name to get/generate
        source_col: Column to transform (if applicable)
        transform_fn: Function to apply to source_col
        default_generator: Function(df) -> Series if col_name doesn't exist and no source
        
    Returns:
        DataFrame with the column ensured
    """
    if col_name in df.columns:
        logger.info(f"Column '{col_name}' found in dataset")
        return df
    
    if source_col and source_col in df.columns and transform_fn:
        logger.info(f"Generating '{col_name}' from '{source_col}'")
        df[col_name] = transform_fn(df[source_col])
        return df
    
    if default_generator:
        logger.info(f"Generating '{col_name}' using default generator")
        df[col_name] = default_generator(df)
        return df
    
    logger.warning(f"Could not generate '{col_name}' - using zeros")
    df[col_name] = 0.0
    return df


def fill_missing_values(
    df: pd.DataFrame,
    numeric_strategy: str = "mean",
    categorical_strategy: str = "mode",
) -> pd.DataFrame:
    """
    Fill missing values in DataFrame.
    
    Args:
        df: Input DataFrame
        numeric_strategy: 'mean', 'median', or 'zero'
        categorical_strategy: 'mode' or 'forward_fill'
        
    Returns:
        DataFrame with missing values filled
    """
    logger.info(f"Filling missing values (numeric={numeric_strategy}, categorical={categorical_strategy})")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=["object"]).columns
    
    for col in numeric_cols:
        if df[col].isna().sum() > 0:
            if numeric_strategy == "mean":
                df[col].fillna(df[col].mean(), inplace=True)
            elif numeric_strategy == "median":
                df[col].fillna(df[col].median(), inplace=True)
            elif numeric_strategy == "zero":
                df[col].fillna(0, inplace=True)
            logger.debug(f"  Filled numeric column '{col}'")
    
    for col in categorical_cols:
        if df[col].isna().sum() > 0:
            if categorical_strategy == "mode":
                mode_val = df[col].mode()
                fill_val = mode_val[0] if len(mode_val) > 0 else "Unknown"
                df[col].fillna(fill_val, inplace=True)
            elif categorical_strategy == "forward_fill":
                df[col].fillna(method="ffill", inplace=True)
            logger.debug(f"  Filled categorical column '{col}'")
    
    return df


def encode_categorical_columns(
    df: pd.DataFrame,
    encoders_dict: Optional[Dict[str, LabelEncoder]] = None,
) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
    """
    Encode categorical columns to numeric labels.
    
    Args:
        df: Input DataFrame
        encoders_dict: Pre-fitted encoders (for inference); if None, fit new ones
        
    Returns:
        Tuple of (encoded_df, encoders_dict)
    """
    if encoders_dict is None:
        encoders_dict = {}
    
    encoded_df = df.copy()
    categorical_cols = encoded_df.select_dtypes(include=["object"]).columns
    
    for col in categorical_cols:
        if col not in encoders_dict:
            logger.info(f"Fitting encoder for categorical column '{col}'")
            encoders_dict[col] = LabelEncoder()
            encoders_dict[col].fit(encoded_df[col].astype(str).unique())
        
        encoded_df[col] = encoders_dict[col].transform(encoded_df[col].astype(str))
        logger.debug(f"  Encoded '{col}' to numeric labels")
    
    return encoded_df, encoders_dict


def scale_numeric_features(
    df: pd.DataFrame,
    feature_cols: List[str],
    scaler: Optional[StandardScaler] = None,
) -> Tuple[pd.DataFrame, StandardScaler]:
    """
    Scale numeric feature columns to standard normal distribution.
    
    Args:
        df: Input DataFrame
        feature_cols: List of columns to scale
        scaler: Pre-fitted scaler (for inference); if None, fit new one
        
    Returns:
        Tuple of (scaled_df, scaler)
    """
    if scaler is None:
        logger.info(f"Fitting scaler for {len(feature_cols)} feature columns")
        scaler = StandardScaler()
        scaler.fit(df[feature_cols])
    else:
        logger.info(f"Applying pre-fitted scaler to {len(feature_cols)} columns")
    
    scaled_df = df.copy()
    scaled_df[feature_cols] = scaler.transform(df[feature_cols])
    logger.debug(f"  Scaled {len(feature_cols)} features")
    
    return scaled_df, scaler


# ============================================================================
# ANN PROCESSOR (The Biologist)
# ============================================================================

class ANNDataProcessor:
    """
    Processor for ANN Regressor (predicts water_volume_L, fertilizer_dose_mL).
    
    Target KATS ANN Schema:
    Features: temp, humidity, solar_radiation, wind_speed, soil_moisture, soil_EC,
              floor_level, orientation
    Targets: water_volume_L, fertilizer_dose_mL
    """
    
    FEATURE_MAPPING = {
        # Map available columns to ANN schema
        "temperature": "temp",
        "humidity": "humidity",
        "sunlight_exposure": "solar_radiation",
        "wind_speed": "wind_speed",
        "soil_moisture": "soil_moisture",
    }
    
    ANN_REQUIRED_FEATURES = [
        "temp",
        "humidity",
        "solar_radiation",
        "wind_speed",
        "soil_moisture",
        "soil_EC",
        "floor_level",
        "orientation",
    ]
    
    ANN_TARGETS = ["water_volume_L", "fertilizer_dose_mL"]
    
    def __init__(self):
        self.scaler = None
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw DataFrame into ANN-ready format.
        
        Args:
            df: Raw input DataFrame
            
        Returns:
            Processed DataFrame with ANN schema
        """
        logger.info("=" * 70)
        logger.info("ANN DATA PROCESSING (The Biologist)")
        logger.info("=" * 70)
        
        df = df.copy()
        
        # Step 1: Rename columns to match KATS schema
        logger.info("Step 1: Mapping columns to ANN schema")
        for src_col, tgt_col in self.FEATURE_MAPPING.items():
            if src_col in df.columns:
                df.rename(columns={src_col: tgt_col}, inplace=True)
        
        # Step 2: Generate missing features
        logger.info("Step 2: Generating missing features")
        
        # soil_EC (electrical conductivity) - proxy from organic_matter or N/P/K
        def gen_soil_ec(x):
            if "organic_matter" in x.index:
                return np.abs(np.random.normal(800, 150)) + x.get("organic_matter", 0) * 100
            elif "N" in x.index:
                return (x.get("N", 0) + x.get("P", 0) + x.get("K", 0)) / 10 + np.random.normal(0, 50)
            else:
                return np.random.uniform(400, 1200)
        
        df = get_or_generate_column(
            df, "soil_EC",
            default_generator=lambda x: x.apply(gen_soil_ec, axis=1)
        )
        
        # floor_level (1-5 levels, urban farming specific)
        df = get_or_generate_column(
            df, "floor_level",
            default_generator=lambda x: np.random.randint(1, 6, len(x))
        )
        
        # orientation (0-360 degrees)
        df = get_or_generate_column(
            df, "orientation",
            default_generator=lambda x: np.random.uniform(0, 360, len(x))
        )
        
        # Step 3: Generate target variables
        logger.info("Step 3: Generating target variables")
        
        # water_volume_L - derived from soil_moisture, rainfall, irrigation_frequency
        def gen_water_volume(row):
            base = 50.0
            if "soil_moisture" in row.index:
                base += (100 - row["soil_moisture"]) * 0.3
            if "rainfall" in row.index:
                base -= row["rainfall"] * 0.05
            if "irrigation_frequency" in row.index:
                base += row["irrigation_frequency"] * 10
            return np.clip(base + np.random.normal(0, 5), 10, 200)
        
        df = get_or_generate_column(
            df, "water_volume_L",
            default_generator=lambda x: x.apply(gen_water_volume, axis=1)
        )
        
        # fertilizer_dose_mL - derived from fertilizer_usage, crop, growth_stage
        def gen_fertilizer_dose(row):
            base = 30.0
            if "fertilizer_usage" in row.index:
                base = row["fertilizer_usage"] / 10
            if "growth_stage" in row.index:
                base *= (1.0 + row["growth_stage"] * 0.2)
            return np.clip(base + np.random.normal(0, 3), 5, 150)
        
        df = get_or_generate_column(
            df, "fertilizer_dose_mL",
            default_generator=lambda x: x.apply(gen_fertilizer_dose, axis=1)
        )
        
        # Step 4: Select and validate required features
        logger.info("Step 4: Selecting required features")
        missing_features = [f for f in self.ANN_REQUIRED_FEATURES if f not in df.columns]
        if missing_features:
            logger.error(f"Missing required features: {missing_features}")
            raise ValueError(f"Cannot generate: {missing_features}")
        
        feature_cols = self.ANN_REQUIRED_FEATURES + self.ANN_TARGETS
        df = df[[c for c in feature_cols if c in df.columns]]
        
        # Step 5: Handle missing values
        logger.info("Step 5: Handling missing values")
        df = fill_missing_values(df, numeric_strategy="mean")
        
        # Step 6: Scale features
        logger.info("Step 6: Scaling numeric features")
        df, self.scaler = scale_numeric_features(df, self.ANN_REQUIRED_FEATURES)
        
        logger.info(f"ANN dataset shape: {df.shape}")
        logger.info("ANN processing complete!\n")
        
        return df


# ============================================================================
# SVM PROCESSOR (The Guard)
# ============================================================================

class SVMDataProcessor:
    """
    Processor for SVM Classifier (predicts crop disease classification).
    
    Target KATS SVM Schema:
    Features: NDVI, NIR_red, red_edge, SWIR, 3day_NDVI_delta, crop_type
    Target: disease_label (0=Healthy, 1=Mild, 2=Moderate, 3=Severe)
    """
    
    SVM_REQUIRED_FEATURES = [
        "NDVI",
        "NIR_red",
        "red_edge",
        "SWIR",
        "3day_NDVI_delta",
        "crop_type",
    ]
    
    SVM_TARGET = "disease_label"
    
    def __init__(self):
        self.label_encoder = None
        self.scaler = None
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw DataFrame into SVM-ready format.
        
        Args:
            df: Raw input DataFrame
            
        Returns:
            Processed DataFrame with SVM schema
        """
        logger.info("=" * 70)
        logger.info("SVM DATA PROCESSING (The Guard)")
        logger.info("=" * 70)
        
        df = df.copy()
        
        # Step 1: Map NDVI_index to NDVI
        logger.info("Step 1: Mapping columns to SVM schema")
        if "NDVI_index" in df.columns:
            df.rename(columns={"NDVI_index": "NDVI"}, inplace=True)
        
        # Step 2: Generate missing spectral features
        logger.info("Step 2: Generating missing spectral indices")
        
        # NIR_red ratio (Normalized Difference Vegetation Index alternative)
        df = get_or_generate_column(
            df, "NIR_red",
            default_generator=lambda x: np.random.uniform(1.5, 4.0, len(x))
        )
        
        # red_edge index (enhanced vegetation index)
        df = get_or_generate_column(
            df, "red_edge",
            default_generator=lambda x: np.random.uniform(0.3, 0.8, len(x))
        )
        
        # SWIR (shortwave infrared)
        df = get_or_generate_column(
            df, "SWIR",
            default_generator=lambda x: np.random.uniform(0.1, 0.6, len(x))
        )
        
        # 3day_NDVI_delta (temporal change)
        def gen_ndvi_delta(row):
            if "NDVI" in row.index:
                return row["NDVI"] * np.random.uniform(-0.05, 0.05)
            else:
                return np.random.uniform(-0.1, 0.1)
        
        df = get_or_generate_column(
            df, "3day_NDVI_delta",
            default_generator=lambda x: x.apply(gen_ndvi_delta, axis=1)
        )
        
        # Step 3: Ensure crop_type exists
        logger.info("Step 3: Ensuring crop_type")
        if "crop_type" not in df.columns:
            if "label" in df.columns:
                df.rename(columns={"label": "crop_type"}, inplace=True)
            else:
                logger.warning("No crop_type column found, filling with 'Unknown'")
                df["crop_type"] = "Unknown"
        
        # Step 4: Map disease status to disease_label
        logger.info("Step 4: Mapping disease status to KATS disease_label")
        if "crop_disease_status" in df.columns:
            df[self.SVM_TARGET] = df["crop_disease_status"].map(DISEASE_LABEL_MAP)
        else:
            logger.warning("No crop_disease_status found, generating random disease labels")
            df[self.SVM_TARGET] = np.random.choice(list(DISEASE_LABEL_MAP.values()), len(df))
        
        # Handle any NaN values in disease_label
        df[self.SVM_TARGET].fillna(1, inplace=True)
        
        # Step 5: Select required features
        logger.info("Step 5: Selecting required features")
        required_cols = self.SVM_REQUIRED_FEATURES + [self.SVM_TARGET]
        available_cols = [c for c in required_cols if c in df.columns]
        df = df[available_cols]
        
        # Step 6: Encode categorical columns
        logger.info("Step 6: Encoding categorical columns")
        df, self.label_encoder = encode_categorical_columns(df)
        
        # Step 7: Handle missing values
        logger.info("Step 7: Handling missing values")
        df = fill_missing_values(df, numeric_strategy="mean")
        
        # Step 8: Scale numeric features
        logger.info("Step 8: Scaling numeric features")
        numeric_features = [c for c in self.SVM_REQUIRED_FEATURES if c in df.columns and c != "crop_type"]
        if numeric_features:
            df, self.scaler = scale_numeric_features(df, numeric_features)
        
        logger.info(f"SVM dataset shape: {df.shape}")
        logger.info("SVM processing complete!\n")
        
        return df


# ============================================================================
# RF PROCESSOR (The Strategist)
# ============================================================================

class RFDataProcessor:
    """
    Processor for Random Forest (urban scheduling predictions).
    
    Target KATS RF Schema:
    Features: city_water_pressure, tariff_slot, weather_24h, active_buildings
    Targets: time_slot, building_priority
    """
    
    RF_REQUIRED_FEATURES = [
        "city_water_pressure",
        "tariff_slot",
        "weather_24h",
        "active_buildings",
    ]
    
    RF_TARGETS = ["time_slot", "building_priority"]
    
    def __init__(self):
        self.scaler = None
    
    def _generate_synthetic_urban_dataset(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        Generate synthetic urban scheduling dataset if none exists.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Synthetic DataFrame with RF schema
        """
        logger.info(f"Generating synthetic urban scheduling dataset ({n_samples} samples)")
        
        # Create realistic urban farming scheduling data
        np.random.seed(42)
        data = {
            "city_water_pressure": np.random.uniform(40, 120, n_samples),  # PSI
            "tariff_slot": np.random.choice([1, 2, 3], n_samples),  # Peak, Off-peak, Super off-peak
            "weather_24h": np.random.choice(["Sunny", "Cloudy", "Rainy", "Foggy"], n_samples),
            "active_buildings": np.random.randint(5, 50, n_samples),  # Number of active rooftop units
            "time_slot": np.random.randint(0, 8, n_samples),  # 8 time slots (3-hour windows)
            "building_priority": np.random.randint(1, 6, n_samples),  # Priority level 1-5
        }
        
        df = pd.DataFrame(data)
        
        # Add realistic correlations
        # Higher water pressure -> earlier time slots for irrigation
        df.loc[df["city_water_pressure"] < 60, "time_slot"] = np.random.choice([0, 1, 2], sum(df["city_water_pressure"] < 60))
        
        # Off-peak tariff -> higher priority
        df.loc[df["tariff_slot"] != 1, "building_priority"] = np.minimum(5, df.loc[df["tariff_slot"] != 1, "building_priority"] + 1)
        
        # Rainy weather -> lower irrigation priority
        df.loc[df["weather_24h"] == "Rainy", "building_priority"] = np.maximum(1, df.loc[df["weather_24h"] == "Rainy", "building_priority"] - 1)
        
        logger.info(f"  Generated synthetic dataset: {df.shape}")
        return df
    
    def process(self, df_rf: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Process RF data or generate synthetic dataset if none provided.
        
        Args:
            df_rf: Optional raw RF input DataFrame
            
        Returns:
            Processed DataFrame with RF schema
        """
        logger.info("=" * 70)
        logger.info("RF DATA PROCESSING (The Strategist)")
        logger.info("=" * 70)
        
        # Use provided data or generate synthetic
        if df_rf is None or len(df_rf) == 0:
            logger.warning("No RF dataset provided, generating synthetic urban scheduling data")
            df = self._generate_synthetic_urban_dataset(n_samples=1000)
        else:
            df = df_rf.copy()
            logger.info(f"Processing provided RF dataset: {df.shape}")
        
        # Step 1: Generate missing features if needed
        logger.info("Step 1: Generating missing urban scheduling features")
        
        # city_water_pressure - proxy from Rainfall or other availability
        if "Rainfall_mm" in df.columns and "city_water_pressure" not in df.columns:
            def gen_pressure(row):
                rainfall = row.get("Rainfall_mm", 0)
                return np.clip(100 - rainfall * 0.02, 40, 120)
            df["city_water_pressure"] = df.apply(gen_pressure, axis=1)
        else:
            df = get_or_generate_column(
                df, "city_water_pressure",
                default_generator=lambda x: np.random.uniform(40, 120, len(x))
            )
        
        # tariff_slot (1=Peak, 2=Off-peak, 3=Super off-peak)
        df = get_or_generate_column(
            df, "tariff_slot",
            default_generator=lambda x: np.random.choice([1, 2, 3], len(x))
        )
        
        # weather_24h
        if "Weather_Condition" in df.columns and "weather_24h" not in df.columns:
            df.rename(columns={"Weather_Condition": "weather_24h"}, inplace=True)
        else:
            df = get_or_generate_column(
                df, "weather_24h",
                default_generator=lambda x: np.random.choice(["Sunny", "Cloudy", "Rainy", "Foggy"], len(x))
            )
        
        # active_buildings (number of rooftop farms needing irrigation)
        if "active_buildings" not in df.columns:
            df["active_buildings"] = np.random.randint(5, 50, len(df))
        else:
            logger.info(f"Column 'active_buildings' found in dataset")
        
        # Step 2: Generate target variables
        logger.info("Step 2: Generating target variables")
        
        # time_slot (8 time slots: 0-7, representing 3-hour windows)
        if "time_slot" not in df.columns:
            df["time_slot"] = np.random.randint(0, 8, len(df))
        
        # building_priority (1-5, influenced by tariff and weather)
        if "building_priority" not in df.columns:
            def gen_priority(row):
                base = np.random.randint(1, 6)
                if row.get("tariff_slot", 1) != 1:  # Off-peak
                    base = min(5, base + 1)
                if row.get("weather_24h", "") == "Rainy":  # Rainy
                    base = max(1, base - 1)
                return base
            df["building_priority"] = df.apply(gen_priority, axis=1)
        
        # Step 3: Select required features
        logger.info("Step 3: Selecting required features")
        required_cols = self.RF_REQUIRED_FEATURES + self.RF_TARGETS
        available_cols = [c for c in required_cols if c in df.columns]
        df = df[available_cols]
        
        # Step 4: Encode categorical columns
        logger.info("Step 4: Encoding categorical columns")
        df, _ = encode_categorical_columns(df)
        
        # Step 5: Handle missing values
        logger.info("Step 5: Handling missing values")
        df = fill_missing_values(df, numeric_strategy="mean")
        
        # Step 6: Scale numeric features
        logger.info("Step 6: Scaling numeric features")
        numeric_features = [c for c in self.RF_REQUIRED_FEATURES if c in df.columns]
        if numeric_features:
            df, self.scaler = scale_numeric_features(df, numeric_features)
        
        logger.info(f"RF dataset shape: {df.shape}")
        logger.info("RF processing complete!\n")
        
        return df


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class KATSPreprocessingPipeline:
    """
    Main orchestrator for KATS preprocessing pipeline.
    Loads raw datasets and runs all three model-specific processors.
    """
    
    def __init__(self, raw_data_dir: Path = RAW_DATA_DIR):
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = PROCESSED_DATA_DIR
        
        self.ann_processor = ANNDataProcessor()
        self.svm_processor = SVMDataProcessor()
        self.rf_processor = RFDataProcessor()
        
        logger.info(f"KATS Preprocessing Pipeline initialized")
        logger.info(f"  Raw data directory: {self.raw_data_dir}")
        logger.info(f"  Processed data directory: {self.processed_data_dir}")
    
    def run(self) -> Dict[str, pd.DataFrame]:
        """
        Execute the full preprocessing pipeline.
        
        Returns:
            Dictionary with processed datasets for each model
        """
        logger.info("\n")
        logger.info("╔" + "=" * 68 + "╗")
        logger.info("║" + " " * 68 + "║")
        logger.info("║  KATS PREPROCESSING PIPELINE START".ljust(68) + "║")
        logger.info("║  Urban Rooftop Farming ML Models".ljust(68) + "║")
        logger.info("║" + " " * 68 + "║")
        logger.info("╚" + "=" * 68 + "╝")
        logger.info("")
        
        results = {}
        
        # ANN Processing
        logger.info("PHASE 1: Loading ANN input datasets...")
        df_crop_rec = load_csv_safe(str(self.raw_data_dir / "Crop_recommendationV2.csv"))
        if df_crop_rec is not None:
            results["ann"] = self.ann_processor.process(df_crop_rec)
            output_path = self.processed_data_dir / "train_ann_processed.csv"
            results["ann"].to_csv(output_path, index=False)
            logger.info(f"✓ Saved ANN dataset to {output_path}\n")
        else:
            logger.error("✗ Failed to load Crop_recommendationV2.csv\n")
        
        # SVM Processing
        logger.info("PHASE 2: Loading SVM input datasets...")
        df_smart_farming = load_csv_safe(str(self.raw_data_dir / "Smart_Farming_Crop_Yield_2024.csv"))
        if df_smart_farming is not None:
            results["svm"] = self.svm_processor.process(df_smart_farming)
            output_path = self.processed_data_dir / "train_svm_processed.csv"
            results["svm"].to_csv(output_path, index=False)
            logger.info(f"✓ Saved SVM dataset to {output_path}\n")
        else:
            logger.error("✗ Failed to load Smart_Farming_Crop_Yield_2024.csv\n")
        
        # RF Processing
        logger.info("PHASE 3: Loading RF input datasets...")
        df_crop_yield = load_csv_safe(str(self.raw_data_dir.parent / "RF" / "crop_yield.csv"))
        if df_crop_yield is not None and len(df_crop_yield) > 0:
            results["rf"] = self.rf_processor.process(df_crop_yield)
        else:
            logger.warning("RF dataset not found or empty, generating synthetic dataset")
            results["rf"] = self.rf_processor.process(None)
        
        output_path = self.processed_data_dir / "train_rf_processed.csv"
        results["rf"].to_csv(output_path, index=False)
        logger.info(f"✓ Saved RF dataset to {output_path}\n")
        
        # Summary
        logger.info("╔" + "=" * 68 + "╗")
        logger.info("║  PREPROCESSING COMPLETE".ljust(68) + "║")
        logger.info("║" + " " * 68 + "║")
        if "ann" in results:
            logger.info(f"║  ✓ ANN dataset: {results['ann'].shape[0]} rows x {results['ann'].shape[1]} cols".ljust(68) + "║")
        if "svm" in results:
            logger.info(f"║  ✓ SVM dataset: {results['svm'].shape[0]} rows x {results['svm'].shape[1]} cols".ljust(68) + "║")
        if "rf" in results:
            logger.info(f"║  ✓ RF dataset: {results['rf'].shape[0]} rows x {results['rf'].shape[1]} cols".ljust(68) + "║")
        logger.info("║" + " " * 68 + "║")
        logger.info("╚" + "=" * 68 + "╝")
        logger.info("")
        
        return results


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """
    Main entry point for command-line execution.
    """
    try:
        pipeline = KATSPreprocessingPipeline()
        results = pipeline.run()
        logger.info("All preprocessing complete. Check 'data/processed/' for outputs.")
        return 0
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
