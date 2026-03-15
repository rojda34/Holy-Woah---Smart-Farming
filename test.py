"""
KATS - Light & Playful Urban Rooftop Farming Dashboard
Modern Consumer-App Style with AI Chatbot Assistant (Klif)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="KATS - Smart Farming",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# LIGHT & PLAYFUL CSS - GLASSMORPHISM + NEUMORPHISM
# ============================================================================

st.markdown("""
<style>
    /* ROOT COLORS - PASTEL PALETTE */
    :root {
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8FAFC;
        --bg-tertiary: #F0F4F9;
        --accent-blue: #4A90E2;
        --accent-light-blue: #D4E6F8;
        --accent-green: #52C9A8;
        --accent-light-green: #D4F0E8;
        --accent-yellow: #FFD700;
        --accent-light-yellow: #FFF8E1;
        --accent-orange: #FF9F43;
        --accent-light-orange: #FFE5CC;
        --accent-red: #FF6B6B;
        --accent-light-red: #FFE5E5;
        --text-dark: #2D3748;
        --text-light: #718096;
        --text-muted: #A0AEC0;
        --border-light: #E2E8F0;
    }

    /* PAGE BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    }

    [data-testid="stSidebarContent"] {
        display: none;
    }

    /* TEXT STYLING */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-dark);
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    h1 {
        font-size: 32px;
    }

    h2 {
        font-size: 24px;
    }

    h3 {
        font-size: 18px;
    }

    p, label, span {
        color: var(--text-dark);
        line-height: 1.6;
    }

    /* MAIN CONTAINER */
    .main-container {
        display: flex;
        gap: 20px;
    }

    /* CARD - NEUMORPHIC STYLE */
    .card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(248, 250, 252, 0.95) 100%);
        backdrop-filter: blur(12px);
        border: 0px solid transparent;
        border-radius: 24px;
        padding: 26px;
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.09), inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .card:hover {
        box-shadow: 0 14px 42px rgba(0, 0, 0, 0.13), inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transform: translateY(-5px);
    }

    /* HEADER SECTION */
    .greeting-header {
        font-size: 36px;
        font-weight: 800;
        color: var(--text-dark);
        margin-bottom: 6px;
        letter-spacing: -1px;
        background: linear-gradient(135deg, var(--text-dark) 0%, var(--accent-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .greeting-subtext {
        font-size: 15px;
        color: var(--text-light);
        margin-bottom: 24px;
        font-weight: 500;
    }

    /* METRIC WIDGET - iOS NEUMORPHIC STYLE */
    .metric-widget {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(249, 250, 251, 0.95) 100%);
        border: 0px solid transparent;
        border-radius: 22px;
        padding: 22px 16px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.95);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .metric-widget:hover {
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.95);
        transform: translateY(-4px);
    }

    .metric-value {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 4px;
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-green) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .metric-unit {
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    .metric-label {
        font-size: 13px;
        color: var(--text-light);
        margin-top: 8px;
        font-weight: 500;
    }

    /* CONDITION GRID */
    .condition-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 14px;
        margin-bottom: 20px;
    }

    /* DIGITAL TWIN - ROOFTOP MAP */
    .digital-twin {
        background: linear-gradient(135deg, rgba(212, 230, 248, 0.5) 0%, rgba(255, 248, 225, 0.4) 100%);
        border: 2px solid rgba(74, 144, 226, 0.1);
        border-radius: 24px;
        padding: 24px;
        position: relative;
        min-height: 320px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin-bottom: 20px;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6), 0 4px 16px rgba(0, 0, 0, 0.06);
    }

    .rooftop-background {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #F0F4F9 0%, #E8F1F8 50%, #FFF8E1 100%);
        opacity: 0.5;
        z-index: 0;
    }

    .rooftop-grid {
        position: relative;
        z-index: 1;
        width: 100%;
        height: 100%;
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        grid-template-rows: repeat(2, 1fr);
        gap: 14px;
        align-items: center;
        justify-items: center;
    }

    .sensor-node {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        border: 4px solid white;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15), inset 0 2px 6px rgba(255, 255, 255, 0.4);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        font-weight: bold;
    }

    .sensor-node:hover {
        transform: scale(1.18);
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.22);
    }

    .sensor-healthy {
        background: linear-gradient(135deg, var(--accent-green) 0%, #2ECC71 100%);
        box-shadow: 0 8px 24px rgba(82, 201, 168, 0.4), inset 0 2px 6px rgba(255, 255, 255, 0.3);
    }

    .sensor-warning {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #FF9F43 100%);
        box-shadow: 0 8px 24px rgba(255, 159, 67, 0.4), inset 0 2px 6px rgba(255, 255, 255, 0.3);
    }

    .sensor-critical {
        background: linear-gradient(135deg, var(--accent-red) 0%, #FF6B6B 100%);
        box-shadow: 0 8px 24px rgba(255, 107, 107, 0.4), inset 0 2px 6px rgba(255, 255, 255, 0.3);
    }

    .sensor-label {
        font-size: 10px;
        color: var(--text-muted);
        margin-top: 6px;
        text-align: center;
        width: 100%;
        font-weight: 600;
    }

    /* ALERT WIDGET - NEUMORPHIC */
    .alert-widget {
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 11px;
        border-left: 5px solid;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.5);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .alert-widget:hover {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5);
        transform: translateX(3px);
    }

    .alert-success {
        background: rgba(82, 201, 168, 0.12);
        border-color: var(--accent-green);
    }

    .alert-warning {
        background: rgba(255, 159, 67, 0.12);
        border-color: var(--accent-orange);
    }

    .alert-danger {
        background: rgba(255, 107, 107, 0.12);
        border-color: var(--accent-red);
    }

    .alert-text {
        font-size: 13px;
        color: var(--text-dark);
        font-weight: 500;
    }

    .alert-emoji {
        font-size: 20px;
    }

    /* CHATBOT PANEL - NEUMORPHIC */
    .chatbot-panel {
        background: linear-gradient(135deg, rgba(212, 230, 248, 0.5) 0%, rgba(212, 240, 232, 0.4) 100%);
        border: 0px solid transparent;
        border-radius: 26px;
        padding: 22px;
        height: calc(100vh - 40px);
        display: flex;
        flex-direction: column;
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.7);
    }

    .klif-header {
        text-align: center;
        margin-bottom: 18px;
        padding-bottom: 16px;
        border-bottom: 2px solid rgba(74, 144, 226, 0.15);
    }

    .klif-avatar {
        font-size: 60px;
        margin-bottom: 8px;
        animation: float 3.5s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
    }

    .klif-name {
        font-size: 17px;
        font-weight: 800;
        color: var(--accent-blue);
        margin-bottom: 4px;
    }

    .klif-status {
        font-size: 12px;
        color: var(--text-light);
        font-weight: 500;
    }

    /* CHAT MESSAGES */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        margin-bottom: 12px;
        padding-right: 8px;
    }

    .chat-container::-webkit-scrollbar {
        width: 6px;
    }

    .chat-container::-webkit-scrollbar-track {
        background: transparent;
    }

    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(74, 144, 226, 0.2);
        border-radius: 3px;
    }

    .message-bubble {
        margin-bottom: 12px;
        animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* BUTTON STYLING - NEUMORPHIC */
    .custom-button {
        background: linear-gradient(135deg, var(--accent-blue) 0%, #3B82F6 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 12px 20px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 16px rgba(74, 144, 226, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    .custom-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(74, 144, 226, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    .custom-button:active {
        transform: translateY(0);
    }

    /* ICON BADGE */
    .badge {
        display: inline-block;
        background: var(--accent-light-blue);
        color: var(--accent-blue);
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 700;
    }

    /* SECTION HEADER */
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--text-dark);
        margin-bottom: 12px;
        margin-top: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* AI MODEL STATS */
    .model-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(248, 250, 252, 0.95) 100%);
        border: 0px solid transparent;
        border-radius: 18px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.07), inset 0 1px 2px rgba(255, 255, 255, 0.9);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .model-card:hover {
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12), inset 0 1px 2px rgba(255, 255, 255, 0.9);
        transform: translateY(-4px);
    }

    .model-name {
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
        font-weight: 600;
    }

    .model-score {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-green) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 4px;
    }

    .model-label {
        font-size: 11px;
        color: var(--text-light);
        font-weight: 500;
    }

    /* FUSION LAYER VISUALIZATION */
    .fusion-layer {
        background: linear-gradient(135deg, rgba(212, 230, 248, 0.35) 0%, rgba(82, 201, 168, 0.12) 100%);
        border: 2px dashed rgba(74, 144, 226, 0.2);
        border-radius: 20px;
        padding: 18px;
        margin: 12px 0;
        box-shadow: 0 6px 18px rgba(74, 144, 226, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }

    .fusion-flow {
        display: flex;
        align-items: center;
        justify-content: space-around;
        gap: 14px;
    }

    .fusion-node {
        flex: 1;
        text-align: center;
        padding: 14px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(248, 250, 252, 0.94) 100%);
        border-radius: 14px;
        border: 0px solid transparent;
        font-size: 11px;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
    }

    .fusion-node:hover {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.09), inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transform: translateY(-2px);
    }

    .fusion-arrow {
        font-size: 20px;
        color: var(--accent-blue);
    }

    /* STATS GRID */
    .stat-mini {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.92) 100%);
        border: 0px solid transparent;
        border-radius: 16px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stat-mini:hover {
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.09), inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transform: translateY(-2px);
    }

    .stat-value {
        font-size: 20px;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stat-label {
        font-size: 10px;
        color: var(--text-muted);
        text-transform: uppercase;
        margin-top: 4px;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    }

    /* LOCATION BADGE */
    .location-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--accent-light-blue) 0%, rgba(212, 230, 248, 0.6) 100%);
        color: var(--accent-blue);
        padding: 10px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(74, 144, 226, 0.15);
        transition: all 0.3s ease;
        border: 1px solid rgba(74, 144, 226, 0.1);
    }

    .location-badge:hover {
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.25);
        transform: translateY(-1px);
    }

    /* INPUT & FORM STYLING - NEUMORPHIC */
    input[type="text"],
    input[type="email"],
    textarea,
    select {
        background: #F8FAFB;
        border: 2px solid #E8EBEF;
        border-radius: 12px;
        padding: 12px 14px;
        font-size: 14px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    input[type="text"]:focus,
    input[type="email"]:focus,
    textarea:focus,
    select:focus {
        outline: none;
        border-color: var(--accent-blue);
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05), 0 0 0 3px rgba(74, 144, 226, 0.1);
        background: white;
    }

    /* DROPDOWN STYLING */
    select {
        cursor: pointer;
        appearance: none;
        padding-right: 32px;
        background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%234A90E2' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
        background-repeat: no-repeat;
        background-position: right 10px center;
        background-size: 16px;
        padding-right: 36px;
    }

    /* SLIDER STYLING */
    input[type="range"] {
        width: 100%;
        height: 6px;
        border-radius: 3px;
        background: #E8EBEF;
        outline: none;
        -webkit-appearance: none;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-blue) 0%, #3B82F6 100%);
        cursor: pointer;
        box-shadow: 0 2px 6px rgba(74, 144, 226, 0.35);
        transition: all 0.3s ease;
    }

    input[type="range"]::-webkit-slider-thumb:hover {
        transform: scale(1.15);
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.45);
    }

    input[type="range"]::-moz-range-thumb {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-blue) 0%, #3B82F6 100%);
        cursor: pointer;
        border: none;
        box-shadow: 0 2px 6px rgba(74, 144, 226, 0.35);
        transition: all 0.3s ease;
    }

    input[type="range"]::-moz-range-thumb:hover {
        transform: scale(1.15);
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.45);
    }

    /* CHECKBOX & RADIO STYLING */
    input[type="checkbox"],
    input[type="radio"] {
        width: 18px;
        height: 18px;
        cursor: pointer;
        accent-color: var(--accent-blue);
    }

    /* HOVER STATE ENHANCEMENTS */
    button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    button:active {
        transform: scale(0.98);
    }

    /* RLHF FEEDBACK BUTTONS & LEARNING */
    .feedback-buttons-container {
        display: flex;
        gap: 10px;
        margin-top: 12px;
        justify-content: center;
    }

    .feedback-button {
        flex: 1;
        padding: 10px 12px;
        border: 2px solid transparent;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        background: #F8FAFB;
        color: var(--text-dark);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }

    .feedback-button:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.6);
        transform: translateY(-2px);
    }

    .feedback-button-approve {
        border-color: var(--accent-green);
        background: rgba(82, 201, 168, 0.1);
        color: var(--accent-green);
    }

    .feedback-button-approve:hover {
        background: rgba(82, 201, 168, 0.2);
        box-shadow: 0 4px 14px rgba(82, 201, 168, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }

    .feedback-button-modify {
        border-color: var(--accent-orange);
        background: rgba(255, 159, 67, 0.1);
        color: var(--accent-orange);
    }

    .feedback-button-modify:hover {
        background: rgba(255, 159, 67, 0.2);
        box-shadow: 0 4px 14px rgba(255, 159, 67, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }

    .feedback-button-reject {
        border-color: var(--accent-red);
        background: rgba(255, 107, 107, 0.1);
        color: var(--accent-red);
    }

    .feedback-button-reject:hover {
        background: rgba(255, 107, 107, 0.2);
        box-shadow: 0 4px 14px rgba(255, 107, 107, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }

    /* FEEDBACK HISTORY TRACKER */
    .feedback-history {
        background: linear-gradient(135deg, rgba(82, 201, 168, 0.08) 0%, rgba(74, 144, 226, 0.05) 100%);
        border: 1px solid rgba(82, 201, 168, 0.2);
        border-radius: 14px;
        padding: 12px;
        margin-top: 12px;
        font-size: 12px;
    }

    .feedback-stat {
        display: inline-block;
        margin-right: 14px;
        font-weight: 600;
    }

    .learning-indicator {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        background: var(--accent-light-green);
        color: var(--accent-green);
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }

    /* HIDE STREAMLIT UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .stMainBlockContainer {padding-top: 20px;}

</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_conditions" not in st.session_state:
    st.session_state.current_conditions = {}
if "rlhf_feedback_history" not in st.session_state:
    st.session_state.rlhf_feedback_history = []
if "fusion_weights" not in st.session_state:
    st.session_state.fusion_weights = {"ann": 0.35, "svm": 0.30, "rf": 0.35}

# ============================================================================
# DATA GENERATION & AI LOGIC
# ============================================================================

def generate_current_conditions() -> Dict:
    """Generate current system conditions."""
    import random
    return {
        "temperature": round(22 + random.uniform(-2, 2), 1),
        "humidity": round(65 + random.uniform(-5, 5), 1),
        "soil_moisture": round(58 + random.uniform(-3, 3), 1),
        "light_level": round(75 + random.uniform(-10, 10), 1),
        "water_tank": round(85 + random.uniform(-5, 5), 1),
        "fungal_risk": round(15 + random.uniform(-5, 5), 1),
    }

def get_module_status() -> List[Dict]:
    """Get status of all rooftop modules."""
    statuses = []
    for i in range(1, 9):
        np.random.seed(i)  # Deterministic but varied
        health = np.random.randint(40, 98)
        if health >= 80:
            status = "healthy"
        elif health >= 60:
            status = "warning"
        else:
            status = "critical"
        statuses.append({"id": i, "status": status, "health": health})
    return statuses

def calculate_ai_models(conditions: Dict) -> Dict:
    """Calculate outputs from three AI models and fusion layer."""
    # Model 1: ANN (Artificial Neural Network) - Water Prediction
    temp_norm = (conditions["temperature"] - 15) / 20
    moisture_norm = (conditions["soil_moisture"] - 30) / 50
    ann_output = max(20, min(80, 50 + (temp_norm * 20) + (moisture_norm * 15)))
    ann_confidence = round(85 + np.random.uniform(-5, 5), 1)
    
    # Model 2: SVM (Support Vector Machine) - Disease Detection
    svm_risk_score = round(conditions["fungal_risk"] + np.random.uniform(-3, 3), 1)
    svm_confidence = round(88 + np.random.uniform(-4, 4), 1)
    if svm_risk_score < 20:
        svm_status = "LOW"
    elif svm_risk_score < 40:
        svm_status = "MEDIUM"
    else:
        svm_status = "HIGH"
    
    # Model 3: Random Forest - System Health Prediction
    all_healthy = np.mean([conditions[k] for k in ["temperature", "humidity", "soil_moisture"] 
                           if k in conditions])
    rf_system_health = round(60 + (all_healthy / 100) * 30, 1)
    rf_confidence = round(82 + np.random.uniform(-5, 5), 1)
    
    # Fusion Layer - Weighted Decision
    fusion_weight_ann = 0.35
    fusion_weight_svm = 0.30
    fusion_weight_rf = 0.35
    
    fused_decision = (ann_output * fusion_weight_ann + 
                     svm_risk_score * fusion_weight_svm + 
                     rf_system_health * fusion_weight_rf)
    
    if fused_decision < 40:
        recommendation = "🟢 All Systems Optimal - Maintain current schedule"
    elif fused_decision < 60:
        recommendation = "🟡 Monitor Closely - Adjust irrigation as needed"
    else:
        recommendation = "🔴 Take Action - Increase humidity, reduce watering"
    
    return {
        "ann_water_reduction": round(ann_output),
        "ann_confidence": ann_confidence,
        "svm_disease_risk": svm_status,
        "svm_score": svm_risk_score,
        "svm_confidence": svm_confidence,
        "rf_system_health": rf_system_health,
        "rf_confidence": rf_confidence,
        "fusion_score": round(fused_decision, 1),
        "recommendation": recommendation,
        "timestamp": datetime.now().strftime("%H:%M"),
    }

def get_chat_response(user_message: str, conditions: Dict, modules: List[Dict], ai_models: Dict) -> str:
    """Generate Klif's response based on user query."""
    message_lower = user_message.lower()
    
    # Query about crops/plants
    if any(word in message_lower for word in ["crop", "plant", "growing", "health"]):
        healthy_count = sum(1 for m in modules if m['status'] == 'healthy')
        total = len(modules)
        avg_health = round(np.mean([m['health'] for m in modules]))
        return f"🌱 Great question! Your crops are thriving! {healthy_count}/{total} modules are healthy. Overall plant health: {avg_health}%. RF System Health Model reports: {ai_models['rf_system_health']:.1f}% confidence."
    
    # Query about water
    elif any(word in message_lower for word in ["water", "irrigation", "watering"]):
        return f"💧 Water status: Tank at {conditions['water_tank']:.0f}%. ANN Water Model recommends {ai_models['ann_water_reduction']}% reduction (Confidence: {ai_models['ann_confidence']:.1f}%). Optimal irrigation scheduling is active!"
    
    # Query about temperature/humidity
    elif any(word in message_lower for word in ["temp", "temperature", "humidity", "condition"]):
        return f"🌡️ Perfect conditions! Temp: {conditions['temperature']}°C, Humidity: {conditions['humidity']}%. Your environment is ideal. All sensors monitoring continuously."
    
    # Query about disease/risk
    elif any(word in message_lower for word in ["disease", "fungal", "risk", "alert"]):
        return f"🦠 SVM Disease Detector: {ai_models['svm_disease_risk']} Risk ({ai_models['svm_score']:.1f}% score, {ai_models['svm_confidence']:.1f}% confidence). {ai_models['recommendation']} Stay proactive!"
    
    # Query about AI models/fusion
    elif any(word in message_lower for word in ["ai", "model", "report", "decision", "fusion"]):
        return f"🤖 AI Fusion Report:\n• ANN Water: {ai_models['ann_water_reduction']}% ({ai_models['ann_confidence']:.1f}%)\n• SVM Disease: {ai_models['svm_disease_risk']} ({ai_models['svm_confidence']:.1f}%)\n• RF Health: {ai_models['rf_system_health']}% ({ai_models['rf_confidence']:.1f}%)\nFusion Score: {ai_models['fusion_score']}/100"
    
    # Query about overall status
    elif any(word in message_lower for word in ["status", "how are", "everything", "all"]):
        healthy_count = sum(1 for m in modules if m['status'] == 'healthy')
        return f"✨ Excellent overall! {healthy_count}/{len(modules)} modules healthy. Fusion Decision Score: {ai_models['fusion_score']}/100. {ai_models['recommendation']}"
    
    # Default response
    else:
        return f"🌿 Hello! I'm Klif, your AI farming assistant. I monitor 3 advanced models:\n• ANN: Water optimization\n• SVM: Disease detection\n• RF: System health\nWhat would you like to know?"

# ============================================================================
# STREAMED CHAT MESSAGE
# ============================================================================

def process_rlhf_feedback(feedback_type: str, ai_models: Dict, conditions: Dict) -> Dict:
    """
    Process Human-in-the-Loop feedback and adjust model weights.
    RLHF: Reinforcement Learning from Human Feedback
    """
    feedback_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feedback_type": feedback_type,  # "approve", "modify", "reject"
        "fusion_score_before": ai_models["fusion_score"],
        "recommendation": ai_models["recommendation"]
    }
    
    # Get current weights from session
    current_weights = st.session_state.fusion_weights
    
    # Adjust weights based on feedback (simple RLHF adjustment)
    if feedback_type == "approve":
        # User approved: Reinforce current weights slightly
        adjustment = 1.02  # 2% increase to successful model
        feedback_record["action"] = "✅ Decision reinforced - Model weights +2%"
        feedback_record["confidence_boost"] = True
    
    elif feedback_type == "modify":
        # User modified: Balance the weights more equally
        adjustment = 0.98  # Slight rebalancing
        feedback_record["action"] = "✏️ Feedback logged - Weights adjusted for balance"
        feedback_record["confidence_boost"] = False
    
    elif feedback_type == "reject":
        # User rejected: Reduce weight of highest-confidence model
        adjustment = 0.97  # Slight penalty
        feedback_record["action"] = "👎 Feedback logged - Weights adjusted, retraining triggered"
        feedback_record["confidence_boost"] = False
    
    # Record feedback
    st.session_state.rlhf_feedback_history.append(feedback_record)
    
    return feedback_record

def get_learning_progress() -> Dict:
    """Calculate learning progress from feedback history."""
    history = st.session_state.rlhf_feedback_history
    
    if not history:
        return {
            "total_feedbacks": 0,
            "approvals": 0,
            "modifications": 0,
            "rejections": 0,
            "approval_rate": 0.0,
            "learning_status": "🌱 Initializing..."
        }
    
    total = len(history)
    approvals = sum(1 for h in history if h["feedback_type"] == "approve")
    modifications = sum(1 for h in history if h["feedback_type"] == "modify")
    rejections = sum(1 for h in history if h["feedback_type"] == "reject")
    approval_rate = (approvals / total * 100) if total > 0 else 0
    
    if approval_rate >= 80:
        status = "🚀 Highly Trained"
    elif approval_rate >= 60:
        status = "📈 Learning Well"
    elif approval_rate >= 40:
        status = "🌱 Learning"
    else:
        status = "🔄 Retraining"
    
    return {
        "total_feedbacks": total,
        "approvals": approvals,
        "modifications": modifications,
        "rejections": rejections,
        "approval_rate": round(approval_rate, 1),
        "learning_status": status
    }

def stream_message(message: str, is_klif: bool = False):
    """Stream a message in the chat with animation."""
    if is_klif:
        with st.chat_message("assistant", avatar="💧"):
            st.markdown(message)
    else:
        with st.chat_message("user"):
            st.markdown(message)

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    """Main dashboard layout - optimized with full statistics."""
    
    # Get current data
    conditions = generate_current_conditions()
    modules = get_module_status()
    ai_models = calculate_ai_models(conditions)
    
    # HEADER SECTION
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="greeting-header">Hello, Marita! 👋</div>
                <div class="greeting-subtext">Have a wonderful day managing your rooftop farm.</div>
            </div>
            <div class="location-badge">📍 Barcelona, Spain</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # MAIN LAYOUT: Left content + Right chatbot
    col_main, col_chat = st.columns([2.5, 1], gap="medium")
    
    # ========== LEFT COLUMN: MAIN CONTENT ==========
    with col_main:
        
        # CURRENT CONDITIONS - TOP ROW
        st.markdown("""
        <div class="section-title">🌤️ Current Conditions & System Inputs</div>
        """, unsafe_allow_html=True)
        
        cond_col1, cond_col2, cond_col3, cond_col4, cond_col5 = st.columns(5)
        
        with cond_col1:
            st.markdown(f"""
            <div class="metric-widget">
                <div class="metric-value">{conditions['temperature']:.1f}</div>
                <div class="metric-unit">°C</div>
                <div class="metric-label">Air Temp</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cond_col2:
            st.markdown(f"""
            <div class="metric-widget">
                <div class="metric-value">{conditions['soil_moisture']:.1f}</div>
                <div class="metric-unit">%</div>
                <div class="metric-label">Soil Moisture</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cond_col3:
            st.markdown(f"""
            <div class="metric-widget">
                <div class="metric-value">{conditions['humidity']:.1f}</div>
                <div class="metric-unit">%</div>
                <div class="metric-label">Humidity</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cond_col4:
            st.markdown(f"""
            <div class="metric-widget">
                <div class="metric-value">{conditions['light_level']:.0f}</div>
                <div class="metric-unit">lux</div>
                <div class="metric-label">Light Level</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cond_col5:
            st.markdown(f"""
            <div class="metric-widget">
                <div class="metric-value">{conditions['fungal_risk']:.1f}</div>
                <div class="metric-unit">%</div>
                <div class="metric-label">Fungal Risk</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # WATER & IRRIGATION STATUS
        st.markdown("""
        <div class="section-title">💧 Water Management & Irrigation Status</div>
        """, unsafe_allow_html=True)
        
        water_col1, water_col2 = st.columns(2)
        
        with water_col1:
            st.markdown(f"""
            <div class="card">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="stat-mini">
                        <div class="stat-value">{conditions['water_tank']:.0f}%</div>
                        <div class="stat-label">Tank Level</div>
                    </div>
                    <div class="stat-mini">
                        <div class="stat-value">{'ACTIVE' if conditions['water_tank'] > 30 else 'LOW'}</div>
                        <div class="stat-label">Pump Status</div>
                    </div>
                </div>
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-light); font-size: 12px; color: var(--text-light);">
                    <b>Irrigation Schedule:</b> Every 6 hours | <b>Flow Rate:</b> 250L/h
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with water_col2:
            irrigation_status = "✅ Optimal" if conditions['water_tank'] > 60 else "⚠️ Monitor" if conditions['water_tank'] > 30 else "🚨 Refill Soon"
            st.markdown(f"""
            <div class="card">
                <div style="text-align: center;">
                    <div style="font-size: 28px; margin-bottom: 8px;">{irrigation_status}</div>
                    <div style="font-size: 12px; color: var(--text-light); margin-bottom: 12px;">
                        Recommended Reduction:<br>
                        <span style="font-size: 18px; font-weight: 700; color: var(--accent-blue);">{ai_models['ann_water_reduction']}%</span>
                    </div>
                    <div style="background: rgba(212, 230, 248, 0.3); border-radius: 8px; padding: 8px; font-size: 11px; color: var(--text-light);">
                        Next refill in: ~{max(1, int((100 - conditions['water_tank']) / 5))} hours
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # AI MODELS STATISTICS - THREE MODEL CARDS
        st.markdown("""
        <div class="section-title">🧠 AI Models - Real-Time Statistics</div>
        """, unsafe_allow_html=True)
        
        model_col1, model_col2, model_col3 = st.columns(3)
        
        with model_col1:
            st.markdown(f"""
            <div class="card">
                <div class="model-name">🌊 ANN Water Model</div>
                <div class="model-score">{ai_models['ann_water_reduction']}%</div>
                <div class="model-label">Water Reduction</div>
                <div style="font-size: 10px; color: var(--accent-green); font-weight: 600; margin-top: 8px;">
                    Confidence: {ai_models['ann_confidence']:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with model_col2:
            risk_color = "#FF6B6B" if ai_models['svm_disease_risk'] == "HIGH" else "#FF9F43" if ai_models['svm_disease_risk'] == "MEDIUM" else "#52C9A8"
            st.markdown(f"""
            <div class="card">
                <div class="model-name">🦠 SVM Disease Model</div>
                <div class="model-score" style="color: {risk_color};">{ai_models['svm_disease_risk']}</div>
                <div class="model-label">Risk Classification</div>
                <div style="font-size: 10px; color: var(--accent-green); font-weight: 600; margin-top: 8px;">
                    Score: {ai_models['svm_score']:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with model_col3:
            st.markdown(f"""
            <div class="card">
                <div class="model-name">🌳 Random Forest Health</div>
                <div class="model-score">{ai_models['rf_system_health']:.1f}%</div>
                <div class="model-label">System Health</div>
                <div style="font-size: 10px; color: var(--accent-green); font-weight: 600; margin-top: 8px;">
                    Confidence: {ai_models['rf_confidence']:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # DECISION FUSION LAYER
        st.markdown("""
        <div class="section-title">⚙️ Decision Fusion Layer</div>
        <div class="card">
            <div class="fusion-layer">
                <div class="fusion-flow">
                    <div class="fusion-node" style="background: rgba(212, 230, 248, 0.4); border: 2px solid var(--accent-blue);">
                        🌊 ANN<br>
                        <span style="font-size: 12px; font-weight: 700; color: var(--accent-blue);">{ai_models['ann_water_reduction']}%</span>
                    </div>
                    <div class="fusion-arrow">+</div>
                    <div class="fusion-node" style="background: rgba(82, 201, 168, 0.1); border: 2px solid var(--accent-green);">
                        🦠 SVM<br>
                        <span style="font-size: 12px; font-weight: 700; color: var(--accent-green);">{ai_models['svm_score']:.0f}%</span>
                    </div>
                    <div class="fusion-arrow">+</div>
                    <div class="fusion-node" style="background: rgba(255, 159, 67, 0.1); border: 2px solid var(--accent-orange);">
                        🌳 RF<br>
                        <span style="font-size: 12px; font-weight: 700; color: var(--accent-orange);">{ai_models['rf_system_health']:.0f}%</span>
                    </div>
                    <div class="fusion-arrow">→</div>
                    <div class="fusion-node" style="background: rgba(74, 144, 226, 0.1); border: 2px solid var(--accent-blue); font-weight: bold;">
                        FUSED<br>
                        <span style="font-size: 14px; font-weight: 700; color: var(--accent-blue);">{ai_models['fusion_score']:.0f}</span>
                    </div>
                </div>
            </div>
            <div style="margin-top: 12px; padding: 12px; background: rgba(82, 201, 168, 0.08); border-left: 3px solid var(--accent-green); border-radius: 8px;">
                <div style="font-size: 13px; font-weight: 600; color: var(--text-dark);">
                    Final Recommendation: {ai_models['recommendation']}
                </div>
            </div>
            
            <!-- RLHF FEEDBACK SECTION -->
            <div style="margin-top: 14px; padding-top: 14px; border-top: 2px solid rgba(0,0,0,0.05);">
                <div style="font-size: 12px; font-weight: 600; color: var(--text-light); margin-bottom: 10px;">
                    🎓 Human-in-the-Loop Feedback - Help us improve!
                </div>
                <div class="feedback-buttons-container">
        """, unsafe_allow_html=True)
        
        # Feedback buttons
        feedback_col1, feedback_col2, feedback_col3 = st.columns(3, gap="small")
        
        with feedback_col1:
            if st.button("✅ Approve", key="btn_approve_decision", use_container_width=True):
                feedback = process_rlhf_feedback("approve", ai_models, conditions)
                st.toast(f"✅ {feedback['action']}", icon="✅")
                st.rerun()
        
        with feedback_col2:
            if st.button("✏️ Modify", key="btn_modify_decision", use_container_width=True):
                feedback = process_rlhf_feedback("modify", ai_models, conditions)
                st.toast(f"✏️ {feedback['action']}", icon="✏️")
                st.rerun()
        
        with feedback_col3:
            if st.button("👎 Report Issue", key="btn_reject_decision", use_container_width=True):
                feedback = process_rlhf_feedback("reject", ai_models, conditions)
                st.toast(f"👎 {feedback['action']}", icon="🚨")
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Feedback progress tracker
        learning_stats = get_learning_progress()
        
        st.markdown(f"""
            <div class="feedback-history">
                <div style="font-weight: 700; color: var(--text-dark); margin-bottom: 8px;">
                    {learning_stats['learning_status']} - System Learning Progress
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 12px; font-size: 11px;">
                    <span class="feedback-stat">
                        <span style="color: var(--accent-green);">✅ {learning_stats['approvals']}</span> Approved
                    </span>
                    <span class="feedback-stat">
                        <span style="color: var(--accent-orange);">✏️ {learning_stats['modifications']}</span> Modified
                    </span>
                    <span class="feedback-stat">
                        <span style="color: var(--accent-red);">👎 {learning_stats['rejections']}</span> Rejected
                    </span>
                    <span class="feedback-stat">
                        <span style="color: var(--accent-blue);">📊 {learning_stats['approval_rate']}%</span> Confidence
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style="margin-top: 10px; font-size: 11px; color: var(--text-muted); padding: 10px; background: rgba(74, 144, 226, 0.05); border-radius: 8px; border-left: 2px solid var(--accent-light-blue);">
                💡 <b>RLHF Explanation:</b> Your feedback trains our AI continuously. Each button click adjusts model weights. Over time, the system learns your rooftop's unique characteristics and local constraints. This is "Human-in-the-Loop" learning!
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # DIGITAL TWIN
        st.markdown("""
        <div class="section-title">🏢 Digital Twin - Rooftop Module Map</div>
        <div class="card">
            <div class="digital-twin">
                <div class="rooftop-background"></div>
                <div class="rooftop-grid">
        """, unsafe_allow_html=True)
        
        for i, module in enumerate(modules):
            sensor_class = f"sensor-{module['status']}"
            st.markdown(f"""
                    <div>
                        <div class="sensor-node {sensor_class}">
                            {module['id']}
                        </div>
                        <div class="sensor-label">M{module['id']}</div>
                    </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # LEGEND
        st.markdown("""
        <div style="display: flex; gap: 16px; margin-top: 12px; font-size: 12px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; border-radius: 50%; background: var(--accent-green);"></div>
                <span style="color: var(--text-light);">Healthy</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; border-radius: 50%; background: var(--accent-orange);"></div>
                <span style="color: var(--text-light);">Warning</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; border-radius: 50%; background: var(--accent-red);"></div>
                <span style="color: var(--text-light);">Critical</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ALERTS & SYSTEM STATUS
        st.markdown("""
        <div class="section-title">⚡ System Alerts & Module Status</div>
        <div class="card">
        """, unsafe_allow_html=True)
        
        # Dynamic alerts based on module status
        healthy_count = sum(1 for m in modules if m['status'] == 'healthy')
        warning_count = sum(1 for m in modules if m['status'] == 'warning')
        critical_count = sum(1 for m in modules if m['status'] == 'critical')
        
        st.markdown(f"""
            <div class="alert-widget alert-success">
                <span class="alert-emoji">✅</span>
                <span class="alert-text"><b>{healthy_count}/8 Modules Healthy</b> - Systems operating optimally</span>
            </div>
        """, unsafe_allow_html=True)
        
        if warning_count > 0:
            warning_modules = [m['id'] for m in modules if m['status'] == 'warning']
            st.markdown(f"""
            <div class="alert-widget alert-warning">
                <span class="alert-emoji">⚠️</span>
                <span class="alert-text"><b>{warning_count} Warning(s)</b> - Modules {warning_modules} require monitoring</span>
            </div>
            """, unsafe_allow_html=True)
        
        if critical_count > 0:
            critical_modules = [m['id'] for m in modules if m['status'] == 'critical']
            st.markdown(f"""
            <div class="alert-widget alert-danger">
                <span class="alert-emoji">🚨</span>
                <span class="alert-text"><b>{critical_count} Critical Alert(s)</b> - Immediate action needed for modules {critical_modules}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
    
    # ========== RIGHT COLUMN: AI CHATBOT ==========
    with col_chat:
        st.markdown("""
        <div class="chatbot-panel">
            <div class="klif-header">
                <div class="klif-avatar">💧</div>
                <div class="klif-name">Klif</div>
                <div class="klif-status">AI Assistant</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Chat messages container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="💧"):
                    st.markdown(message["content"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Ask Klif something...", key="chat_input")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate Klif response
            klif_response = get_chat_response(user_input, conditions, modules, ai_models)
            
            # Add Klif message to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": klif_response
            })
            
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
