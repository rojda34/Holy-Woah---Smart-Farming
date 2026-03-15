# 🏗️ KATS System Architecture

**Urban Rooftop Farming AI System - Technical Architecture Document**

---

## Table of Contents

1. [System Overview](#system-overview)
2. [3-Layer Pipeline](#3-layer-pipeline)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)

---

## System Overview

KATS is structured as a **three-layer decision support system** that combines real-time sensor data with AI model predictions and human feedback to provide optimal farming recommendations.

```
┌─────────────────────────────────────────────────────────────┐
│                     KATS SYSTEM                             │
│         Urban Rooftop Farming AI Platform                   │
└─────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐  ┌─────────┐  ┌──────────┐
   │  Layer  │  │  Layer  │  │  Layer   │
   │    1    │  │    2    │  │    3     │
   │ DATA    │  │   AI    │  │ FEEDBACK │
   └─────────┘  └─────────┘  └──────────┘
