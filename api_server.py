"""
KATS API Server - Real-time ML Predictions for Dashboard
Routes trained models (ANN, SVM, RF) through REST endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import sys
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.models.inference import KatsInferenceEngine

# ============================================================================
# FLASK APP SETUP
# ============================================================================
app = Flask(__name__)
CORS(app)  # Enable CORS for React dashboard

# Load inference engine
try:
    engine = KatsInferenceEngine()
    print("✓ KATS Inference Engine loaded successfully")
except Exception as e:
    print(f"✗ Error loading inference engine: {e}")
    engine = None

# ============================================================================
# HEALTH CHECK
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API and models are loaded."""
    return jsonify({
        "status": "healthy" if engine else "error",
        "message": "KATS API is running",
        "models_loaded": engine is not None
    })

# ============================================================================
# ANN PREDICTIONS - Water & Fertilizer
# ============================================================================
@app.route('/api/predict/water-fertilizer', methods=['POST'])
def predict_water_fertilizer():
    """
    Predict water volume and fertilizer dose using ANN.
    
    Request body:
    {
        "temp": 22.5,
        "humidity": 65,
        "solar_radiation": 4.2,
        "wind_speed": 2.1,
        "soil_moisture": 45,
        "soil_ec": 850,
        "floor_level": 3,
        "orientation": 180
    }
    """
    if not engine:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        data = request.json
        
        # Validate required fields
        required = ['temp', 'humidity', 'solar_radiation', 'wind_speed', 
                   'soil_moisture', 'soil_ec', 'floor_level', 'orientation']
        if not all(k in data for k in required):
            return jsonify({"error": f"Missing fields. Required: {required}"}), 400
        
        # Make prediction
        prediction = engine.predict_ann(
            temp=float(data['temp']),
            humidity=float(data['humidity']),
            solar_radiation=float(data['solar_radiation']),
            wind_speed=float(data['wind_speed']),
            soil_moisture=float(data['soil_moisture']),
            soil_ec=float(data['soil_ec']),
            floor_level=int(data['floor_level']),
            orientation=float(data['orientation'])
        )
        
        return jsonify({
            "success": True,
            "model": "ANN",
            "water_volume_L": round(prediction['water_volume_L'], 2),
            "fertilizer_dose_mL": round(prediction['fertilizer_dose_mL'], 2)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# SVM PREDICTIONS - Disease Classification
# ============================================================================
@app.route('/api/predict/disease', methods=['POST'])
def predict_disease():
    """
    Predict crop disease status using SVM.
    
    Request body:
    {
        "ndvi": 0.65,
        "nir_red": 2.3,
        "red_edge": 0.45,
        "swir": 0.38,
        "ndvi_delta": 0.02,
        "crop_type": 1
    }
    """
    if not engine:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        data = request.json
        
        # Validate required fields
        required = ['ndvi', 'nir_red', 'red_edge', 'swir', 'ndvi_delta', 'crop_type']
        if not all(k in data for k in required):
            return jsonify({"error": f"Missing fields. Required: {required}"}), 400
        
        # Make prediction
        prediction = engine.predict_svm(
            ndvi=float(data['ndvi']),
            nir_red=float(data['nir_red']),
            red_edge=float(data['red_edge']),
            swir=float(data['swir']),
            ndvi_delta=float(data['ndvi_delta']),
            crop_type=int(data['crop_type'])
        )
        
        # Map to health percentage
        health_map = {0: 100, 1: 75, 2: 40, 3: 15}
        health = health_map.get(prediction['disease_label'], 50)
        
        return jsonify({
            "success": True,
            "model": "SVM",
            "disease_label": prediction['disease_label'],
            "disease_status": prediction['disease_status'],
            "health_percentage": health
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# RANDOM FOREST PREDICTIONS - Scheduling
# ============================================================================
@app.route('/api/predict/scheduling', methods=['POST'])
def predict_scheduling():
    """
    Predict optimal irrigation time slot and building priority using Random Forest.
    
    Request body:
    {
        "city_water_pressure": 3.2,
        "tariff_slot": 2,
        "weather_24h": 4,
        "active_buildings": 120
    }
    """
    if not engine:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        data = request.json
        
        # Validate required fields
        required = ['city_water_pressure', 'tariff_slot', 'weather_24h', 'active_buildings']
        if not all(k in data for k in required):
            return jsonify({"error": f"Missing fields. Required: {required}"}), 400
        
        # Make prediction
        prediction = engine.predict_rf(
            city_water_pressure=float(data['city_water_pressure']),
            tariff_slot=int(data['tariff_slot']),
            weather_24h=int(data['weather_24h']),
            active_buildings=int(data['active_buildings'])
        )
        
        # Map time slot to readable window
        time_slot_map = {
            0: "00:00-03:00",
            1: "03:00-06:00",
            2: "06:00-09:00",
            3: "09:00-12:00",
            4: "12:00-15:00",
            5: "15:00-18:00",
            6: "18:00-21:00",
            7: "21:00-24:00"
        }
        
        time_window = time_slot_map.get(prediction['time_slot'], "Unknown")
        
        return jsonify({
            "success": True,
            "model": "Random Forest",
            "time_slot": prediction['time_slot'],
            "time_window": time_window,
            "building_priority": round(prediction['building_priority'], 2),
            "confidence": round(prediction.get('confidence', 0.88) * 100, 1)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# COMBINED PREDICTIONS - Full Sensor Integration
# ============================================================================
@app.route('/api/predict/full-module', methods=['POST'])
def predict_full_module():
    """
    Get all predictions for a single module with complete sensor data.
    
    Request body:
    {
        "module_id": "BCN-001",
        "temp": 22.5,
        "humidity": 65,
        "solar_radiation": 4.2,
        "wind_speed": 2.1,
        "soil_moisture": 45,
        "soil_ec": 850,
        "floor_level": 3,
        "orientation": 180,
        "ndvi": 0.65,
        "nir_red": 2.3,
        "red_edge": 0.45,
        "swir": 0.38,
        "ndvi_delta": 0.02,
        "crop_type": 1,
        "city_water_pressure": 3.2,
        "tariff_slot": 2,
        "weather_24h": 4,
        "active_buildings": 120
    }
    """
    if not engine:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        data = request.json
        
        # Make all three predictions
        ann_pred = engine.predict_ann(
            temp=float(data['temp']),
            humidity=float(data['humidity']),
            solar_radiation=float(data['solar_radiation']),
            wind_speed=float(data['wind_speed']),
            soil_moisture=float(data['soil_moisture']),
            soil_ec=float(data['soil_ec']),
            floor_level=int(data['floor_level']),
            orientation=float(data['orientation'])
        )
        
        svm_pred = engine.predict_svm(
            ndvi=float(data['ndvi']),
            nir_red=float(data['nir_red']),
            red_edge=float(data['red_edge']),
            swir=float(data['swir']),
            ndvi_delta=float(data['ndvi_delta']),
            crop_type=int(data['crop_type'])
        )
        
        rf_pred = engine.predict_rf(
            city_water_pressure=float(data['city_water_pressure']),
            tariff_slot=int(data['tariff_slot']),
            weather_24h=int(data['weather_24h']),
            active_buildings=int(data['active_buildings'])
        )
        
        # Map health
        health_map = {0: 100, 1: 75, 2: 40, 3: 15}
        health = health_map.get(svm_pred['disease_label'], 50)
        
        # Map time window
        time_slot_map = {
            0: "00:00-03:00", 1: "03:00-06:00", 2: "06:00-09:00", 3: "09:00-12:00",
            4: "12:00-15:00", 5: "15:00-18:00", 6: "18:00-21:00", 7: "21:00-24:00"
        }
        time_window = time_slot_map.get(rf_pred['time_slot'], "Unknown")
        
        return jsonify({
            "success": True,
            "module_id": data.get('module_id', 'Unknown'),
            "timestamp": str(np.datetime64('now')),
            "water": {
                "volume_L": round(ann_pred['water_volume_L'], 2),
                "fertilizer_mL": round(ann_pred['fertilizer_dose_mL'], 2)
            },
            "health": {
                "disease_label": svm_pred['disease_label'],
                "status": svm_pred['disease_status'],
                "percentage": health
            },
            "scheduling": {
                "time_slot": rf_pred['time_slot'],
                "time_window": time_window,
                "building_priority": round(rf_pred['building_priority'], 2),
                "confidence": round(rf_pred.get('confidence', 0.88) * 100, 1)
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# RUN SERVER
# ============================================================================
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌾 KATS API Server Starting...")
    print("="*70)
    print("Endpoints:")
    print("  POST /api/predict/water-fertilizer  - ANN predictions")
    print("  POST /api/predict/disease           - SVM disease classification")
    print("  POST /api/predict/scheduling        - RF scheduling")
    print("  POST /api/predict/full-module       - All predictions combined")
    print("  GET  /api/health                    - Health check")
    print("="*70 + "\n")
    
    # Run on port 5000
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False
    )
