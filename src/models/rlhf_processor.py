# src/models/rlhf_processor.py

import json
import os
import logging
from datetime import datetime

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - RLHF ENGINE - %(levelname)s - %(message)s')

class KatsRLHFProcessor:
    """
    KATS Human-in-the-Loop Reinforcement Learning from Human Feedback (RLHF) Engine.
    Processes user feedback (Approve/Modify/Report) to dynamically update model confidence
    weights for the ML models (ANN, SVM, RF).
    """
    
    def __init__(self, weights_path="../../models/weights/fusion_weights.json", history_path="../../logs/rlhf_history.json"):
        self.weights_path = weights_path
        self.history_path = history_path
        self._ensure_directories()
        self.weights = self._load_weights()

    def _ensure_directories(self):
        """Ensures that required directories exist."""
        os.makedirs(os.path.dirname(self.weights_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)

    def _load_weights(self):
        """Load current model weights or initialize with default values."""
        if os.path.exists(self.weights_path):
            with open(self.weights_path, 'r') as f:
                return json.load(f)
        # Default KATS Architecture Weights
        return {"ANN": 0.35, "SVM": 0.30, "RF": 0.35}

    def _save_weights(self):
        """Normalize weights to sum to 1.0 (100%) and persist to file."""
        total = sum(self.weights.values())
        for model in self.weights:
            self.weights[model] = round(self.weights[model] / total, 3)
            
        with open(self.weights_path, 'w') as f:
            json.dump(self.weights, f, indent=4)
        logging.info(f"NEW SYSTEM WEIGHTS SAVED: {self.weights}")

    def _log_history(self, action, details):
        """Records feedback decision history to log file."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "resulting_weights": self.weights.copy()
        }
        
        history = []
        if os.path.exists(self.history_path):
            with open(self.history_path, 'r') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    pass
                    
        history.append(history_entry)
        with open(self.history_path, 'w') as f:
            json.dump(history, f, indent=4)

    def process_feedback(self, action: str, corrected_values: dict = None, issue_type: str = None) -> dict:
        """
        Process user feedback from the Farmer UI.
        action: 'APPROVE' (Approve), 'MODIFY' (Edit), 'REPORT' (Report Issue)
        """
        logging.info(f"User Feedback Received: {action}")

        if action == 'APPROVE':
            logging.info("Farmer approved the recommendation. Reinforcing all models (+2%).")
            # Equally strengthen all models (confidence refresh)
            for model in self.weights:
                self.weights[model] += 0.02

        elif action == 'MODIFY':
            logging.warning(f"Farmer manually corrected the recommendation. Corrected values: {corrected_values}")
            # If water or fertilizer was corrected, ANN made an error.
            if corrected_values and ('water_L' in corrected_values or 'fertilizer_mL' in corrected_values):
                logging.warning("ANN (The Biologist) made an error! Weight reduced by 3%.")
                self.weights['ANN'] = max(0.05, self.weights['ANN'] - 0.03)

        elif action == 'REPORT':
            logging.error(f"CRITICAL ISSUE REPORTED! Issue Type: {issue_type}")
            # If disease was missed while recommendations were given, SVM failed.
            if issue_type == 'missed_disease':
                logging.error("SVM (The Guard) missed disease! Weight reduced by 5%.")
                self.weights['SVM'] = max(0.05, self.weights['SVM'] - 0.05)
            # If network pressure dropped unexpectedly, RF miscalculated.
            elif issue_type == 'timing_error':
                logging.error("RF (The Strategist) failed to predict network collapse! Weight reduced by 5%.")
                self.weights['RF'] = max(0.05, self.weights['RF'] - 0.05)

        # Save new weights and log the transaction
        self._save_weights()
        self._log_history(action, {"corrected_values": corrected_values, "issue_type": issue_type})
        
        # Check for retraining needs
        self._check_retraining_needs()
        
        return self.weights

    def _check_retraining_needs(self):
        """Generates alarm for models whose weights fall below critical threshold."""
        for model, weight in self.weights.items():
            if weight < 0.20:  # If model weight drops below 20%
                logging.critical(f"🚨 ALARM: {model} model reliability in system dropped to {int(weight*100)}%!")
                logging.critical(f"🚨 ACTION REQUIRED: {model} model must be RETRAINED.")
                # Future: Can add subprocess here to auto-trigger train_models.py

if __name__ == "__main__":
    # QUICK TEST SCENARIOS
    rlhf = KatsRLHFProcessor()
    
    print("\n--- TEST 1: USER APPROVED ---")
    print(rlhf.process_feedback('APPROVE'))
    
    print("\n--- TEST 2: USER CORRECTED WATER ---")
    print(rlhf.process_feedback('MODIFY', corrected_values={'water_L': 8.5}))
    
    print("\n--- TEST 3: DISEASE WAS MISSED ---")
    # Report disease detection miss 3 times to trigger critical threshold
    rlhf.process_feedback('REPORT', issue_type='missed_disease')
    rlhf.process_feedback('REPORT', issue_type='missed_disease')
    print(rlhf.process_feedback('REPORT', issue_type='missed_disease'))
