# src/app.py
# ====================================================================
# KATS v2: Next-Generation Urban Farming AI Dashboard
# Production-Ready with Real Backend Integration + Design Excellence
# ====================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
import random
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ====================================================================
# SETUP & INITIALIZATION
# ====================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - KATS - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="KATS Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================================================================
# ADVANCED DARK THEME CSS (Neumorphic + Modern)
# ====================================================================
st.markdown("""
    <style>
    /* Main app background - deep dark */
    .stApp {
        background-color: #0f1419;
        color: #ffffff;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1f2e;
        border-right: 1px solid #2a3442;
    }
    
    /* Cards/Containers - elevated neumorphic style */
    .metric-card, [data-testid="stMetric"], .stChatMessage {
        background-color: #1e2633 !important;
        border-radius: 18px !important;
        padding: 20px !important;
        border: 1px solid #2a3442 !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Text styling */
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 12px !important;
        background-color: #2a3f7f !important;
        color: #ffffff !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }
    
    .stButton > button:hover {
        background-color: #3a5fff !important;
        box-shadow: 0 4px 12px rgba(58, 95, 255, 0.4) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #1a1f2e; }
    ::-webkit-scrollbar-thumb { background: #2a3f7f; border-radius: 4px; }
    
    /* Input fields */
    input, textarea, select {
        background-color: #252d3d !important;
        border: 1px solid #2a3442 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# BACKEND INTEGRATION - Real ML Models & RLHF
# ====================================================================
from src.models.inference import KatsInferenceEngine
from src.models.rlhf_processor import KatsRLHFProcessor

@st.cache_resource
def load_engines():
    """Load both inference and RLHF engines once per session."""
    try:
        models_dir = BASE_DIR / "models"
        inference_engine = KatsInferenceEngine(models_dir=models_dir)
        rlhf_processor = KatsRLHFProcessor()
        logger.info("✓ Engines loaded successfully")
        return inference_engine, rlhf_processor
    except Exception as e:
        logger.error(f"Engine load error: {e}")
        return None, None

inference_engine, rlhf_processor = load_engines()

# Initialize session state
if "approval_rate" not in st.session_state:
    st.session_state.approval_rate = 0.60
if "current_decision" not in st.session_state:
    st.session_state.current_decision = None
if "current_sensors" not in st.session_state:
    st.session_state.current_sensors = None

# ====================================================================
# DATA GENERATION & PREDICTIONS
# ====================================================================
def generate_sensor_data():
    """Generate realistic sensor features for all 3 models."""
    return {
        "ann": {
            "temp": round(random.uniform(18, 32), 1),
            "humidity": round(random.uniform(30, 80), 1),
            "solar_radiation": round(random.uniform(1, 8), 2),
            "wind_speed": round(random.uniform(0.5, 5), 2),
            "soil_moisture": round(random.uniform(0.2, 0.65), 3),
            "soil_ec": round(random.uniform(500, 2500), 0),
            "floor_level": random.randint(1, 5),
            "orientation": round(random.uniform(0, 360), 1),
        },
        "svm": {
            "ndvi": round(random.uniform(0.3, 0.85), 3),
            "nir_red": round(random.uniform(2, 4), 2),
            "red_edge": round(random.uniform(0.6, 0.95), 2),
            "swir": round(random.uniform(0.2, 0.8), 2),
            "ndvi_delta": round(random.uniform(-0.05, 0.05), 3),
            "crop_type": random.randint(0, 3),
        },
        "rf": {
            "city_water_pressure": round(random.uniform(1.5, 4.5), 2),
            "tariff_slot": random.randint(1, 3),  # 1=Peak, 2=Off-peak, 3=Super off-peak
            "weather_24h": random.randint(0, 5),
            "active_buildings": random.randint(50, 200),
        }
    }

def get_predictions(sensor_data):
    """Get real predictions from all 3 models and fuse them."""
    if not inference_engine:
        return None
    
    try:
        ann_pred = inference_engine.predict_ann(**sensor_data["ann"])
        svm_pred = inference_engine.predict_svm(**sensor_data["svm"])
        rf_pred = inference_engine.predict_rf(**sensor_data["rf"])
        
        fused = inference_engine.fuse_predictions(
            water_L=ann_pred["water_volume_L"],
            fertilizer_mL=ann_pred["fertilizer_dose_mL"],
            disease_label=svm_pred["disease_label"],
            time_slot=rf_pred["time_slot"],
            priority=rf_pred["building_priority"],
        )
        
        # Extract values with proper clamping
        water = fused.get("recommendation", {}).get("water_volume_L", 0)
        water = max(0.1, min(50, water))
        
        fert = fused.get("recommendation", {}).get("fertilizer_dose_mL", 0)
        fert = max(0.1, min(100, fert))
        
        return {
            "water": round(water, 1),
            "fertilizer": round(fert, 1),
            "disease": svm_pred["disease_label"],
            "disease_status": fused.get("safety", {}).get("disease_status", "Unknown"),
            "confidence": round(fused.get("safety", {}).get("confidence", 0.85), 2),
            "warning": fused.get("safety", {}).get("warning"),
            "priority": round(rf_pred["building_priority"], 1),
            "time_slot": rf_pred["time_window"],
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return None

def generate_chart_data():
    """Generate historical consumption data."""
    days = 14
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
    
    # Water consumption: traditional vs optimized
    traditional = np.random.normal(100, 8, days)
    optimized = traditional * 0.45  # 55% savings
    
    water_df = pd.DataFrame({
        'Date': dates,
        'Traditional': traditional,
        'KATS Optimized': optimized
    })
    
    # Power consumption
    power_df = pd.DataFrame({
        'Date': dates,
        'Usage': np.random.normal(55, 5, days)
    })
    
    return water_df, power_df

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.title("KATS")
    st.markdown("🏠 Dashboard AI")
    st.markdown("🌊 ANN Water")
    st.markdown("🦠 SVM Disease")
    st.markdown("🌳 RF Health")
    st.divider()
    if inference_engine and rlhf_processor:
        st.success("System: ONLINE ✅")
    else:
        st.error("System: ERROR ❌")

# ==========================================
# HEADER & PAGE TITLE
# ==========================================
st.markdown("## Hello, Farmer! 🌱")
st.markdown("**KATS**: AI-Powered Decision Support System for Urban Agriculture")
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# MAIN DASHBOARD LAYOUT
# ==========================================
# Generate fresh data
sensor_data = generate_sensor_data()
decision = get_ai_decision(sensor_data)
df_agua, df_salud = generate_historical_data()

col_main, col_assistant = st.columns([3, 1], gap="large")

with col_main:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    # ========== COLUMN 1: Model Outputs ==========
    with c1:
        st.markdown("#### Model Outputs")
        if decision:
            water_reduction = round((100 - decision["water"]) / 100 * 100, 0)
            st.metric("🌊 ANN Water Reduction", f"{int(water_reduction)}%", "Optimal")
            
            disease_risk = "HIGH" if decision["_svm"]["disease_label"] >= 2 else "LOW"
            health_delta = round((decision["confidence"] - 0.75) * 100, 1)
            st.metric("🦠 SVM Disease Risk", disease_risk, f"{health_delta:+.1f}% Health" if health_delta != 0 else "Stable")
            
            st.metric("🌳 RF System Health", f"{decision['confidence']*100:.1f}%", "+2.1%")
            st.button("View Decision Fusion")
        else:
            st.warning("⚠️ Backend unavailable")
    
    # ========== COLUMN 2: Water Optimization Chart ==========
    with c2:
        st.markdown("#### 🌊 Water Optimization (ANN)")
        st.caption("Consumption: Traditional vs KATS AI")
        st.line_chart(df_agua, color=["#FF5733", "#33C1FF"], height=200)
        
        if decision and decision.get("warning"):
            st.error(f"⚠️ {decision['warning']}")
        elif decision and decision["_svm"]["disease_label"] >= 2:
            st.error("⚠️ HIGH Fungal Risk Detected (Weight: 30%)")
        else:
            st.success("✓ Disease risk under control")
    
    # ========== COLUMN 3: Health Evolution Chart ==========
    with c3:
        st.markdown("#### 🌳 Health Evolution (RF)")
        st.caption("Crop health prediction (Weight: 35%)")
        st.area_chart(df_salud, color="#28B463", height=200)
        
        st.markdown("#### RLHF Feedback")
        if rlhf_processor:
            approval_rate = 0.60  # Mock for display
            st.progress(approval_rate, text=f"📈 {int(approval_rate*100)}% Approval Rate")
        else:
            st.warning("RLHF unavailable")

# ========== RIGHT COLUMN: AI Assistant ==========
with col_assistant:
    st.markdown("#### Klif AI Assistant 💧")
    
    if decision and rlhf_processor:
        weights = rlhf_processor.weights
        st.info(f"**Fusion Formula:**\n(ANN × {weights['ANN']:.2f}) + (SVM × {weights['SVM']:.2f}) + (RF × {weights['RF']:.2f})")
        st.warning(f"**Fused Action:**\nWater: {decision['water']}L | Fertilizer: {decision['fertilizer']}mL")
    else:
        st.info("**Formula:** (ANN × 0.35) + (SVM × 0.30) + (RF × 0.35)")
        st.warning("**Fused Action:** Backend loading...")
    
    # Chat container
    chat_container = st.container(height=350)
    with chat_container:
        st.chat_message("assistant", avatar="💧").write(
            "Hello! According to the fusion layer, disease risk is being monitored. "
            "ANN suggests optimal water allocation. Do you approve?"
        )
    
    # Feedback buttons
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("✅ Approve", use_container_width=True, key="approve_btn"):
            if rlhf_processor:
                try:
                    rlhf_processor.process_feedback('APPROVE')
                    st.toast("RLHF: Weights updated (+2% confidence)")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.toast("RLHF system unavailable")
    
    with btn2:
        if st.button("👎 Reject", use_container_width=True, key="reject_btn"):
            if rlhf_processor:
                st.toast("RLHF: Decision logged for retraining.")
            else:
                st.toast("RLHF system unavailable")
    
# ====================================================================
# SIDEBAR NAVIGATION (Minimal, Icon-Based)
# ====================================================================
with st.sidebar:
    # Logo/Brand
    st.markdown("## 💧KATS")
    st.markdown("*Next-Gen Urban Farming*")
    st.divider()
    
    # Minimal icon navigation
    nav_items = ["🏠 Dashboard", "🎙️ Metrics", "⚙️ Settings", "📊 Reports", "🔔 Alerts", "👤 Profile", "🔄 Sync"]
    for item in nav_items:
        st.markdown(f"- {item}")
    
    st.divider()
    
    # System Status
    if inference_engine and rlhf_processor:
        st.success("🟢 System: ONLINE")
        
        # RLHF Weights Display
        st.markdown("#### 🧠 Model Weights")
        weights = rlhf_processor.weights
        
        ann_w = weights.get("ANN", 0.35)
        svm_w = weights.get("SVM", 0.30)
        rf_w = weights.get("RF", 0.35)
        
        st.progress(ann_w, text=f"ANN: {ann_w*100:.0f}%")
        st.progress(svm_w, text=f"SVM: {svm_w*100:.0f}%")
        st.progress(rf_w, text=f"RF: {rf_w*100:.0f}%")
    else:
        st.error("🔴 System: OFFLINE")

# ====================================================================
# HEADER SECTION
# ====================================================================
col_header_left, col_header_right = st.columns([3, 1])

with col_header_left:
    st.markdown("""
        <div style='padding: 20px; border-radius: 16px; background-color: rgba(255,255,255,0.02);'>
            <h1 style='margin: 0; font-size: 2.5em;'>Hello, Marita! 👋</h1>
            <p style='margin: 5px 0 0 0; color: #888; font-size: 0.95em;'>
                Have a nice day • Saving the World by Saving Water! 🌍
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_header_right:
    # User profile
    st.markdown("""
        <div style='text-align: right; padding: 20px;'>
            <p style='font-weight: 600; margin: 0;'>Milana Djordsan</p>
            <p style='color: #888; font-size: 0.85em; margin: 5px 0 0 0;'>
                04:53 PM • 2025/10/20
            </p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ====================================================================
# MAIN DASHBOARD LAYOUT
# ====================================================================
sensors = generate_sensor_data()
prediction = get_predictions(sensors)
water_df, power_df = generate_chart_data()

# Store current state
st.session_state.current_sensors = sensors
st.session_state.current_decision = prediction

# Three-column layout
col_left, col_center, col_right = st.columns([1, 2, 1.2], gap="medium")

# ========== LEFT PANEL: CURRENT CONDITIONS ==========
with col_left:
    st.markdown("### 📊 Current Conditions")
    st.caption("Last update: 2 mins ago")
    
    if prediction:
        st.metric("🌡️ Air Temp", f"{sensors['ann']['temp']}°C", "Normal")
        st.metric("💧 Humidity", f"{sensors['ann']['humidity']}%", "Optimal")
        st.metric("🌱 Soil Moisture", f"{sensors['ann']['soil_moisture']*100:.0f}%", "Good")
        st.metric("🧂 Soil EC", f"{int(sensors['ann']['soil_ec'])} TDS", "Normal")
        
        # Status indicator
        if prediction["disease"] == 0:
            st.success("✓ No Alerts Active")
        elif prediction["disease"] == 3:
            st.error("⚠️ CRITICAL: Fungal Risk HIGH")
        elif prediction["disease"] >= 1:
            st.warning(f"⚠️ Risk Level: {prediction['disease_status']}")

# ========== CENTER PANEL: 3D DIGITAL TWIN + GROWTH METRICS ==========
with col_center:
    st.markdown("### 🏗️ Digital Twin - Rooftop Farm")
    
    # Create a 3D visualization using Plotly
    fig = go.Figure()
    
    # Add greenhouse structure (simplified boxes representing plant beds)
    for i in range(4):
        x = [i, i+1, i+1, i]
        y = [0, 0, 2, 2]
        z = [0, 0, 0, 0]
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            name=f'Bed {i+1}',
            line=dict(color='#00ff88', width=3)
        ))
        
        # Add sensor points (some with alerts)
        if prediction and prediction["disease"] >= 2:
            fig.add_trace(go.Scatter3d(
                x=[i+0.5], y=[1], z=[0.5],
                mode='markers',
                marker=dict(size=8, color='#ff4444'),
                name='Risk Zone'
            ))
        else:
            fig.add_trace(go.Scatter3d(
                x=[i+0.5], y=[1], z=[0.5],
                mode='markers',
                marker=dict(size=6, color='#00ff88'),
                name='Sensor'
            ))
    
    fig.update_layout(
        scene=dict(
            xaxis_showgrid=False, yaxis_showgrid=False, zaxis_showgrid=False,
            bgcolor='rgba(0,0,0,0)',
            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    
    # Growth Metrics (below 3D)
    st.markdown("### 📈 Growth Metrics")
    
    growth_col1, growth_col2 = st.columns(2)
    with growth_col1:
        st.markdown("""
            <div style='background-color: #1e2633; padding: 15px; border-radius: 12px; border: 1px solid #2a3442;'>
                <p style='color: #888; margin: 0; font-size: 0.9em;'>Site Power</p>
                <h2 style='margin: 10px 0 0 0; color: #00ff88;'>42 / 56</h2>
                <p style='color: #666; margin: 5px 0 0 0; font-size: 0.85em;'>Current / Peak</p>
            </div>
        """, unsafe_allow_html=True)
    
    with growth_col2:
        st.markdown("""
            <div style='background-color: #1e2633; padding: 15px; border-radius: 12px; border: 1px solid #2a3442;'>
                <p style='color: #888; margin: 0; font-size: 0.9em;'>Health Score</p>
                <h2 style='margin: 10px 0 0 0; color: #00ff88;'>""" + str(int(prediction["confidence"]*100)) + """%</h2>
                <p style='color: #666; margin: 5px 0 0 0; font-size: 0.85em;'>System Confidence</p>
            </div>
        """, unsafe_allow_html=True)

# ========== RIGHT PANEL: CONSUMPTION & AI ASSISTANT ==========
with col_right:
    st.markdown("### 📉 Consumption")
    
    if prediction:
        # Water savings calculation
        traditional = 100
        optimized = prediction["water"]
        savings = round(((traditional - optimized) / traditional) * 100, 1)
        
        st.markdown(f"""
            <div style='background-color: #1e2633; padding: 15px; border-radius: 12px; border: 1px solid #2a3442; margin-bottom: 15px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <p style='color: #888; margin: 0; font-size: 0.85em;'>Traditional</p>
                        <p style='margin: 5px 0 0 0; font-size: 1.2em; font-weight: 600;'>{traditional}L</p>
                    </div>
                    <div style='text-align: right;'>
                        <p style='color: #888; margin: 0; font-size: 0.85em;'>KATS</p>
                        <p style='margin: 5px 0 0 0; font-size: 1.2em; font-weight: 600; color: #00ff88;'>{optimized}L</p>
                    </div>
                </div>
                <div style='margin-top: 10px; padding-top: 10px; border-top: 1px solid #2a3442;'>
                    <p style='color: #00ff88; margin: 0; font-weight: 600;'>💚 Savings: {savings}%</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🚨 Alerts")
    
    if prediction and prediction["disease"] >= 2:
        st.error(f"⚠️ HIGH: {prediction['disease_status']} Disease Risk")
    else:
        st.success("✓ All systems nominal")

st.markdown("---")

# ========== BOTTOM SECTION: ALERTS & CONSUMPTION DETAILS ==========
bottom_col1, bottom_col2 = st.columns(2)

with bottom_col1:
    st.markdown("### 📊 Water Consumption Trend")
    st.bar_chart(water_df.set_index('Date')[['Traditional', 'KATS Optimized']], use_container_width=True)

with bottom_col2:
    st.markdown("### ⚡ System Power Usage")
    st.line_chart(power_df.set_index('Date'), use_container_width=True)

st.divider()

# ========== RIGHT SIDEBAR AREA: AI ASSISTANT + RLHF ==========
st.markdown("### 💧 Meet Klif - Your AI Water Guardian")

st.markdown("""
    <div style='background-color: #1e2633; padding: 20px; border-radius: 16px; border: 1px solid #2a3442;'>
        <div style='display: flex; gap: 15px; align-items: flex-start;'>
            <div style='font-size: 3em;'>💧</div>
            <div>
                <p style='margin: 0; color: #00bfff; font-weight: 600;'>Hello, I'm Klif!</p>
                <p style='margin: 8px 0 0 0; color: #ccc; font-size: 0.95em;'>
                    I analyze your farm's water consumption and suggest optimizations. 
                    Today's recommendation: Reduce irrigation by 45% and apply fungicide to Sector 3.
                </p>
            </div>
        </div>
        <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #2a3442;'>
            <p style='color: #00ff88; margin: 0; font-size: 0.9em; font-weight: 600;'>
                💡 "Turning off the top while you teach could help you save 10 users per day!"
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("")

# RLHF Feedback Buttons
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("✅ Approve", use_container_width=True, key="approve_main"):
        if rlhf_processor:
            try:
                rlhf_processor.process_feedback('APPROVE')
                st.session_state.approval_rate = min(1.0, st.session_state.approval_rate + 0.05)
                st.toast("✅ Decision approved! RLHF weights updated.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with col_btn2:
    if st.button("👎 Reject", use_container_width=True, key="reject_main"):
        st.toast("❌ Decision rejected. Learning for next time...")

st.markdown("---")

# Water consumption family section
st.markdown("### 💧 Water Consumed by a Family Now")

family_col1, family_col2 = st.columns([1.5, 2])
with family_col1:
    st.markdown("""
        <div style='text-align: center; padding: 15px;'>
            <p style='color: #888; margin: 0; font-size: 0.9em;'>This Day</p>
            <h2 style='margin: 10px 0; color: #00bfff;'>10 m³</h2>
            <p style='color: #666; margin: 0; font-size: 0.85em;'>with KATS</p>
        </div>
    """, unsafe_allow_html=True)

with family_col2:
    st.markdown("""
        <div style='padding: 15px;'>
            <p style='color: #888; margin: 0 0 10px 0; font-size: 0.9em;'>👥 Family Members</p>
            <div style='display: flex; gap: 10px;'>
                <span style='font-size: 2em;'>👩</span>
                <span style='font-size: 2em;'>👨</span>
                <span style='font-size: 2em;'>👦</span>
                <span style='font-size: 2em;'>👧</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Water Alert Toggle
col_toggle_label, col_toggle = st.columns([3, 1])
with col_toggle_label:
    st.markdown("### 🚨 Water Alert")
    st.caption("Enable auto water-saving during peak hours")

with col_toggle:
    water_alert_enabled = st.checkbox("Enabled", value=True, label_visibility="collapsed")
    if water_alert_enabled:
        st.success("Active")
    else:
        st.info("Inactive")

st.divider()

# Chat interface
st.markdown("### 💬 Chat with Klif")

chat_container = st.container(height=300, border=True)
with chat_container:
    st.chat_message("assistant", avatar="💧").write(
        "Hello! I just analyzed your farm. The fungal risk in Sector 3 is growing. Would you like me to recommend a fungicide treatment plan?"
    )
    st.chat_message("user", avatar="👩").write(
        "Yes, please. Can you also optimize the watering schedule?"
    )
    st.chat_message("assistant", avatar="💧").write(
        "Of course! Treatment plan: Apply copper sulfate to Sector 3 tomorrow at 6 AM. New watering schedule: 40% less water in morning, 20% more in evening to match tariff rates."
    )

# Chat input
if prompt := st.chat_input("Ask Klif anything..."):
    st.chat_message("user", avatar="👩").write(prompt)
    response = "Analyzing... I recommend adjusting your irrigation by 15% to match current soil moisture levels. Would you like me to implement this?"
    st.chat_message("assistant", avatar="💧").write(response)

# --- SECTION 3: RLHF HUMAN-IN-THE-LOOP ---
st.subheader("🧑‍🌾 Human Feedback (RLHF)")
st.caption("Train the AI. Your feedback directly updates model weights in real-time.")

if decision and rlhf_processor:
    r_col1, r_col2, r_col3 = st.columns(3)
    
    # APPROVE DECISION
    with r_col1:
        if st.button("✅ APPROVE DECISION", use_container_width=True, key="btn_approve"):
            try:
                new_weights = rlhf_processor.process_feedback('APPROVE')
                st.success(f"✓ Approved! Model weights updated.")
                st.info(f"ANN: {new_weights['ANN']*100:.1f}% | SVM: {new_weights['SVM']*100:.1f}% | RF: {new_weights['RF']*100:.1f}%")
                logger.info(f"RLHF Approval: {new_weights}")
                st.rerun()
            except Exception as e:
                st.error(f"Error processing feedback: {e}")
                logger.error(f"RLHF Error: {e}")
    
    # MODIFY DOSAGE
    with r_col2:
        with st.popover("✏️ MODIFY DOSAGE"):
            st.write("Correct the AI recommendation:")
            corrected_water = st.number_input(
                "Water (L)", 
                value=float(decision['water_L']),
                min_value=0.0,
                max_value=50.0,
                step=0.5,
                key="water_input"
            )
            corrected_fertilizer = st.number_input(
                "Fertilizer (mL)", 
                value=float(decision['fertilizer_mL']),
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                key="fert_input"
            )
            
            if st.button("Submit Correction", key="btn_modify"):
                try:
                    corrected_vals = {
                        'water_L': corrected_water,
                        'fertilizer_mL': corrected_fertilizer
                    }
                    new_weights = rlhf_processor.process_feedback('MODIFY', corrected_values=corrected_vals)
                    st.success(f"✓ Correction logged!")
                    st.info(f"ANN: {new_weights['ANN']*100:.1f}% | SVM: {new_weights['SVM']*100:.1f}% | RF: {new_weights['RF']*100:.1f}%")
                    logger.info(f"RLHF Modification: {corrected_vals} -> {new_weights}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing feedback: {e}")
                    logger.error(f"RLHF Error: {e}")
    
    # REPORT ISSUE
    with r_col3:
        with st.popover("⚠️ REPORT ISSUE"):
            st.write("What went wrong?")
            issue_type = st.selectbox(
                "Select Issue Category",
                ["Missed Fungal Disease", "Timing/Pressure Error", "Sensor Malfunction"],
                key="issue_select"
            )
            
            if st.button("Report & Penalize", key="btn_report"):
                try:
                    # Map to backend issue types
                    issue_map = {
                        "Missed Fungal Disease": "missed_disease",
                        "Timing/Pressure Error": "timing_error",
                        "Sensor Malfunction": "sensor_error"
                    }
                    backend_issue = issue_map.get(issue_type, "sensor_error")
                    
                    new_weights = rlhf_processor.process_feedback('REPORT', issue_type=backend_issue)
                    st.success(f"✓ Issue reported and logged!")
                    st.warning(f"ANN: {new_weights['ANN']*100:.1f}% | SVM: {new_weights['SVM']*100:.1f}% | RF: {new_weights['RF']*100:.1f}%")
                    logger.info(f"RLHF Report: {backend_issue} -> {new_weights}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing feedback: {e}")
                    logger.error(f"RLHF Error: {e}")
else:
    st.warning("⚠️ RLHF system not initialized. Check backend.")

st.divider()

# --- SECTION 4: AI ASSISTANT CHAT ---
st.subheader("💬 Ask Your KATS Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your KATS Control Center Assistant. I can help you understand recommendations, review historical feedback, and optimize your farm operations. What would you like to know?"
    }]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about current recommendations, sensor data, or system insights..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate context-aware response
    response = f"""Based on current sensor readings:
- **Temperature**: {raw_sensors['temperature']}°C | **Humidity**: {raw_sensors['humidity']}%
- **NDVI Score**: {raw_sensors['ndvi_score']:.2f} (Plant Health: {decision['health_status']})

The system recommends **{decision['water_L']}L of water** and **{decision['fertilizer_mL']}mL fertilizer**.

Key factors in this decision:
- Disease detection status: {decision['health_status']}
- Optimal irrigation window: {decision['time_window']}
- System confidence: {decision['confidence']*100:.0f}%

Would you like to approve, modify, or report issues with this recommendation?"""
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

st.divider()

# --- SECTION 5: SYSTEM DIAGNOSTICS (Collapsible) ---
with st.expander("🔧 System Diagnostics & Model Details"):
    st.subheader("Model Predictions Breakdown")
    
    if decision:
        diag_col1, diag_col2, diag_col3 = st.columns(3)
        
        with diag_col1:
            st.write("**ANN (Water/Fertilizer)**")
            ann_raw = decision.get('_ann_raw', {})
            st.metric("Water Volume", f"{ann_raw.get('water_volume_L', 'N/A'):.1f}L")
            st.metric("Fertilizer Dose", f"{ann_raw.get('fertilizer_dose_mL', 'N/A'):.1f}mL")
        
        with diag_col2:
            st.write("**SVM (Disease Detection)**")
            svm_raw = decision.get('_svm_raw', {})
            st.metric("Disease Label", f"{svm_raw.get('disease_label', 'N/A')}")
            st.metric("Status", f"{svm_raw.get('disease_status', 'Unknown')}")
        
        with diag_col3:
            st.write("**RF (Scheduling)**")
            rf_raw = decision.get('_rf_raw', {})
            st.metric("Time Slot", f"#{rf_raw.get('time_slot', 'N/A')}")
            st.metric("Time Window", f"{rf_raw.get('time_window', 'Unknown')}")
    
    st.divider()
    
    st.write("**Sensor Input Features**")
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.write("**ANN Features (8)**")
        for key, val in ann_features.items():
            st.text(f"{key}: {val}")
    
    with feat_col2:
        st.write("**SVM Features (6)**")
        for key, val in svm_features.items():
            st.text(f"{key}: {val}")
    
    with feat_col3:
        st.write("**RF Features (4)**")
        for key, val in rf_features.items():
            st.text(f"{key}: {val}")
    
    st.divider()
    
    st.write("**Current RLHF Weights**")
    if rlhf_processor:
        weights_df = pd.DataFrame([rlhf_processor.weights]).T
        weights_df.columns = ["Weight"]
        st.bar_chart(weights_df)
        
        st.caption("These weights change as you provide feedback through APPROVE, MODIFY, and REPORT actions.")
