# src/agents/epi_toolbox.py

import math
from typing import Dict, Any, List, Optional

class OneHealthEpidemiologicalToolbox:
    """
    Provides field-level epidemiological utilities for surveillance design
    and intervention management.
    
    Implements:
    - Tiered Control Programme recommendations.
    - Active Surveillance Sampling (Cochran + Finite Population Correction).
    - Exposure Analysis (Relative Risk & Odds Ratio).
    """
    def __init__(self):
        pass

    # --- 1. CONTROL PROGRAMME ---
    def get_control_programme(self, disease_name: str, risk_class: str) -> Dict[str, Any]:
        """
        Maps computed risk levels to structured, actionable intervention 
        tiers matching regional veterinary standards.
        """
        if risk_class in ["Very High Risk", "High Risk"]:
            return {
                "intervention_tier": "Tier 1: Emergency Mobilization",
                "actions": [
                    f"Initiate ring vaccination for susceptible hosts against {disease_name} within an 8km radius.",
                    "Implement 'Zero-Movement' checkpoints and regional quarantine.",
                    "Deploy active surveillance teams for daily clinical monitoring and carcass disposal.",
                    "Notify regional public health units of high zoonotic potential."
                ],
                "reporting_frequency": "Daily",
                "color_code": "#d9534f" # Red
            }
        elif risk_class == "Medium Risk":
            return {
                "intervention_tier": "Tier 2: Enhanced Surveillance",
                "actions": [
                    f"Prioritize targeted sample collection in high-density districts.",
                    f"Conduct sero-surveillance to verify regional herd immunity against {disease_name}.",
                    "Host biosecurity awareness workshops with local community leaders and pastoralists.",
                    "Inventory check of vaccine cold-chain and diagnostic reagents."
                ],
                "reporting_frequency": "Weekly",
                "color_code": "#f0ad4e" # Yellow
            }
        else:
            return {
                "intervention_tier": "Tier 3: Routine Monitoring",
                "actions": [
                    "Maintain standard passive case reporting workflows.",
                    "Review environmental risk factor deltas monthly.",
                    "Coordinate routine tick/vector control programs."
                ],
                "reporting_frequency": "Monthly",
                "color_code": "#5cb85c" # Green
            }

    # --- 2. SAMPLING PLANS (Slide 38) ---
    def calculate_required_sample_size(
        self, 
        expected_prevalence: float,  # P (0.0 to 1.0)
        precision: float,            # d (Absolute precision, e.g. 0.05)
        population_size: int,        # N (Total local herd size)
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculates the minimum required sample size for active surveillance.
        Utilizes the Cochran formula with Finite Population Correction (FPC).
        """
        if not (0 < expected_prevalence < 1):
            raise ValueError("Expected prevalence must be between 0.0 and 1.0.")
        if not (0 < precision < 1):
            raise ValueError("Precision limit must be between 0.0 and 1.0.")
            
        # Z-score lookup for 95% Confidence Interval
        z = 1.96 if confidence_level == 0.95 else 2.58 if confidence_level == 0.99 else 1.645
        
        # 1. Base Cochran Sample Size (Infinite Population)
        # n0 = (Z^2 * P * (1-P)) / d^2
        n_raw = (z**2 * expected_prevalence * (1.0 - expected_prevalence)) / (precision**2)
        
        # 2. Apply Finite Population Correction (FPC)
        # n = n0 / (1 + (n0 / N))
        n_adjusted = n_raw / (1.0 + (n_raw / population_size))
        
        required_samples = int(math.ceil(n_adjusted))
        
        return {
            "raw_sample_size_cochran": int(math.ceil(n_raw)),
            "fpc_corrected_sample_size": required_samples,
            "sampling_fraction_percentage": round((required_samples / population_size) * 100, 2),
            "parameters": {
                "z_score": z,
                "expected_prevalence": expected_prevalence,
                "precision": precision
            }
        }

    # --- 3. EPI CALCULATOR (Exposure Analysis) ---
    def calculate_relative_risk(
        self, 
        exposed_cases: int,      # (A)
        exposed_healthy: int,    # (B)
        unexposed_cases: int,    # (C)
        unexposed_healthy: int   # (D)
    ) -> Dict[str, Any]:
        """
        Calculates Relative Risk (RR) and Odds Ratio (OR) from a 2x2 contingency table.
        Used to identify specific environmental or management risk factors.
        """
        total_exposed = exposed_cases + exposed_healthy
        total_unexposed = unexposed_cases + unexposed_healthy
        
        if total_exposed == 0 or total_unexposed == 0:
            raise ValueError("Exposed and unexposed cohort totals must be > 0.")
            
        # 1. Relative Risk: (Incidence in exposed) / (Incidence in unexposed)
        # RR = (A / (A+B)) / (C / (C+D))
        risk_exposed = exposed_cases / total_exposed
        risk_unexposed = unexposed_cases / total_unexposed
        relative_risk = risk_exposed / risk_unexposed if risk_unexposed > 0 else 0.0
        
        # 2. Odds Ratio: (Odds of exposure in cases) / (Odds of exposure in controls)
        # OR = (A * D) / (B * C)
        odds_numerator = exposed_cases * unexposed_healthy
        odds_denominator = exposed_healthy * unexposed_cases
        odds_ratio = odds_numerator / odds_denominator if odds_denominator > 0 else 0.0
        
        # Interpretation logic
        interpretation = "Neutral"
        if relative_risk > 1.2:
            interpretation = "Positive correlation: Exposure increases risk."
        elif relative_risk < 0.8:
            interpretation = "Negative correlation: Exposure appears protective."
            
        return {
            "relative_risk": round(relative_risk, 4),
            "odds_ratio": round(odds_ratio, 4),
            "risk_in_exposed_pct": round(risk_exposed * 100, 2),
            "risk_in_unexposed_pct": round(risk_unexposed * 100, 2),
            "statistical_summary": interpretation
        }
