# src/utils/perfect_data_generator.py
import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_perfect_data():
    os.makedirs("../../data/processed", exist_ok=True)
    np.random.seed(42)  # Ensures consistent perfect results
    
    # ==========================================
    # 1. ANN ("The Biologist") - Perfect Data
    # Formula: High temperature + High wind + Low humidity = LOTS OF WATER
    # ==========================================
    logging.info("Generating highly correlated data for ANN...")
    n_ann = 2500
    temp = np.random.uniform(15, 40, n_ann)
    humidity = np.random.uniform(20, 80, n_ann)
    solar_rad = np.random.uniform(200, 1000, n_ann)
    wind_speed = np.random.uniform(0, 20, n_ann)
    soil_moisture = np.random.uniform(0.1, 0.6, n_ann)
    soil_EC = np.random.uniform(0.5, 2.5, n_ann)
    floor_level = np.random.randint(1, 10, n_ann)
    orientation = np.random.randint(0, 4, n_ann)  # 0:North, 1:East, 2:South, 3:West

    # PERFECT CORRELATION FORMULAS
    # Water requirements linked directly to physical conditions (slight noise added)
    water_L = (temp * 0.8) + (wind_speed * 0.5) + (solar_rad * 0.02) - (humidity * 0.3) - (soil_moisture * 40)
    water_L = np.clip(water_L + np.random.normal(0, 2, n_ann), 0, 50)  # Prevent negative water
    
    # Fertilizer requirements linked directly to EC (Salinity) and humidity
    fertilizer_mL = (2.5 - soil_EC) * 20 + (solar_rad * 0.01)
    fertilizer_mL = np.clip(fertilizer_mL + np.random.normal(0, 1, n_ann), 0, 40)

    df_ann = pd.DataFrame({
        'temp': temp, 'humidity': humidity, 'solar_radiation': solar_rad,
        'wind_speed': wind_speed, 'soil_moisture': soil_moisture, 'soil_EC': soil_EC,
        'floor_level': floor_level, 'orientation': orientation,
        'water_volume_L': water_L, 'fertilizer_dose_mL': fertilizer_mL
    })
    
    # Scaling (Standardization)
    features_ann = ['temp', 'humidity', 'solar_radiation', 'wind_speed', 'soil_moisture', 'soil_EC', 'floor_level', 'orientation']
    df_ann[features_ann] = (df_ann[features_ann] - df_ann[features_ann].mean()) / df_ann[features_ann].std()
    df_ann.to_csv("../../data/processed/train_ann_processed.csv", index=False)

    # ==========================================
    # 2. SVM ("The Guard") - Perfect Data
    # Formula: High SWIR + Low NDVI = Fungal Infection (Class 3)
    # ==========================================
    logging.info("Generating highly correlated data for SVM...")
    n_svm = 1500
    
    NDVI = np.random.uniform(0.2, 0.9, n_svm)
    SWIR = np.random.uniform(0.1, 0.8, n_svm)
    red_edge = np.random.uniform(0.1, 0.5, n_svm)
    NIR_red = NDVI * np.random.uniform(1.5, 2.5, n_svm)
    ndvi_delta = np.random.uniform(-0.15, 0.05, n_svm)
    crop_type = np.random.randint(0, 3, n_svm)

    health_status = np.zeros(n_svm, dtype=int)
    for i in range(n_svm):
        if SWIR[i] > 0.6 and NDVI[i] < 0.5:
            health_status[i] = 3  # Fungal Infection
        elif red_edge[i] < 0.2 and NDVI[i] < 0.6:
            health_status[i] = 2  # Nitrogen Deficiency
        elif ndvi_delta[i] < -0.05:
            health_status[i] = 1  # Water Stress
        else:
            health_status[i] = 0  # Healthy

    df_svm = pd.DataFrame({
        'NDVI': NDVI, 'NIR_red': NIR_red, 'red_edge': red_edge,
        'SWIR': SWIR, '3day_NDVI_delta': ndvi_delta, 'crop_type': crop_type,
        'disease_label': health_status
    })
    
    features_svm = ['NDVI', 'NIR_red', 'red_edge', 'SWIR', '3day_NDVI_delta', 'crop_type']
    df_svm[features_svm] = (df_svm[features_svm] - df_svm[features_svm].mean()) / df_svm[features_svm].std()
    df_svm.to_csv("../../data/processed/train_svm_processed.csv", index=False)

    # ==========================================
    # 3. RF ("The Strategist") - Perfect Data
    # Formula: Low Water Pressure + High Tariff Rate = Postpone to Night (Slot 3)
    # ==========================================
    logging.info("Generating highly correlated data for RF...")
    n_rf = 50000  # 50K is sufficient for fast execution
    
    pressure = np.random.uniform(1.0, 6.0, n_rf)
    tariff = np.random.randint(1, 4, n_rf)  # 1:Peak, 2:Off-peak, 3:Super Off-peak
    weather = np.random.randint(0, 3, n_rf)
    buildings = np.random.randint(5, 100, n_rf)

    time_slot = np.zeros(n_rf, dtype=int)
    priority = np.zeros(n_rf)

    for i in range(n_rf):
        # Time Slot Logic
        if pressure[i] < 2.5 or tariff[i] == 1:
            time_slot[i] = 3  # Postpone to night
        elif tariff[i] == 2 and pressure[i] >= 2.5:
            time_slot[i] = 2
        else:
            time_slot[i] = 1

        # Priority Score Logic (High water pressure, fewer buildings = High priority)
        priority[i] = (pressure[i] * 20) - (buildings[i] * 0.5) + (tariff[i] * 10)
        
    df_rf = pd.DataFrame({
        'city_water_pressure': pressure, 'tariff_slot': tariff,
        'weather_24h': weather, 'active_buildings': buildings,
        'time_slot': time_slot, 'building_priority': priority
    })
    
    features_rf = ['city_water_pressure', 'tariff_slot', 'weather_24h', 'active_buildings']
    df_rf[features_rf] = (df_rf[features_rf] - df_rf[features_rf].mean()) / df_rf[features_rf].std()
    df_rf.to_csv("../../data/processed/train_rf_processed.csv", index=False)

    logging.info("ALL PERFECT DATASETS READY! (Saved to data/processed/)")

if __name__ == "__main__":
    generate_perfect_data()
