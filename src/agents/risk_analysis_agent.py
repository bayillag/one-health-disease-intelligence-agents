# src/agents/risk_analysis_agent.py

import pandas as pd
import numpy as np
from typing import Dict, Any, List

class RiskAnalysisAgent:
    """
    Combines parsed climate features and host population parameters to model
    the likelihood of zoonotic transmission risk across regional districts.
    
    Demonstrates:
    - Multi-Agent Reasoning (ADK): Translating raw data into structured risk outcomes.
    - Logistic Sigmoid Modeling: Computing spatiotemporal outbreak probabilities.
    """
    def __init__(self):
        # Statistically derived biological coefficients for pathogen survival
        # Mirroring Southwest Ethiopian Rift Valley target profiles (e.g. Anthrax, FMD)
        self.temp_optimum = 24.0       # Optimum temperature Celsius for target biological vectors
        self.temp_tolerance = 12.0     # Degrees Celsius deviation before suitability drops to zero
        self.humidity_threshold = 55.0  # Critical relative humidity percentage baseline
        self.density_normalization = 50000.0 # Population scale for density weight calculation

    def _calculate_biophysical_suitability(self, row: pd.Series) -> Dict[str, float]:
        """
        Calculates normalized suitability scores (0.0 to 1.0) for temperature 
        and humidity parameters.
        """
        # 1. Temperature Suitability (Linear drop-off from optimum)
        temp_obs = row.get("temperature_lst", 24.0)
        temp_dev = abs(temp_obs - self.temp_optimum)
        temp_score = max(0.0, 1.0 - (temp_dev / self.temp_tolerance))
        
        # 2. Humidity Suitability (Threshold-based saturation)
        rh_obs = row.get("relative_humidity", 50.0)
        humidity_score = 1.0 if rh_obs >= self.humidity_threshold else (rh_obs / self.humidity_threshold)
        
        return {
            "temp_suit": temp_score,
            "hum_suit": humidity_score
        }

    def _calculate_logistic_probability(self, row: pd.Series) -> float:
        """
        Calculates mathematical risk index using a logistic sigmoid function.
        Weights environmental suitability, host density, and active cases.
        """
        suitability = self._calculate_biophysical_suitability(row)
        
        # 1. Host Density Proxy (Normalized population)
        density_factor = min(1.0, row.get("population", 0) / self.density_normalization)
        
        # 2. Transmission Indicator (Presence of active clinical cases)
        active_case_trigger = 1 if row.get("active_cases", 0) > 0 else 0
        
        # 3. Linear Predictor (Z-score)
        # Weights (Beta coefficients) adjusted for high-consequence zoonoses
        linear_predictor = (
            (2.5 * suitability["temp_suit"]) + 
            (2.0 * suitability["hum_suit"]) + 
            (1.5 * density_factor) + 
            (3.0 * active_case_trigger) - 
            4.5  # Logit intercept to center the probability distribution
        )
        
        # Sigmoid Function: 1 / (1 + e^-z)
        probability = 1.0 / (1.0 + np.exp(-linear_predictor))
        
        return float(round(probability, 4))

    def evaluate_risk_matrix(self, vet_df: pd.DataFrame, climate_df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes a spatial join on 'district' and 'region' and derives localized risk scores.
        Outputs the master dataset required for the R Shiny dashboard.
        """
        # Perform inner join on geographical identifiers
        merged_df = pd.merge(
            vet_df, 
            climate_df[["district", "region", "temperature_lst", "relative_humidity", "precipitation_mm"]], 
            on=["district", "region"], 
            how="inner"
        )
        
        if merged_df.empty:
            raise ValueError(
                "Modeling Error: No matching geographical identifiers found between "
                "veterinary clinical records and climate layers. Check 'district' column naming."
            )
            
        # Apply the logistic probability model
        merged_df["risk_probability"] = merged_df.apply(self._calculate_logistic_probability, axis=1)
        
        # Map probabilities into standardized risk classifications (Slide 12 / 26)
        conditions = [
            (merged_df["risk_probability"] >= 0.8),
            (merged_df["risk_probability"] >= 0.5),
            (merged_df["risk_probability"] >= 0.25)
        ]
        choices = ["Very High Risk", "High Risk", "Medium Risk"]
        merged_df["risk_class"] = np.select(conditions, choices, default="Low Risk")
        
        return merged_df
