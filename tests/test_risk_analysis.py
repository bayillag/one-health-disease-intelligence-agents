# tests/test_risk_analysis.py

import unittest
import pandas as pd
import numpy as np
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.epidemiological_modeling_engine import EpidemiologicalModelingEngine

class TestRiskAnalysis(unittest.TestCase):
    """
    Automated test suite for Risk Analysis and Epidemiological Modeling.
    Validates probabilistic scoring and mathematical R0 threshold logic.
    """

    def setUp(self):
        self.risk_agent = RiskAnalysisAgent()
        self.model_engine = EpidemiologicalModelingEngine()

    # --- 1. PROBABILISTIC SCORING: LOGISTIC SIGMOID ---
    def test_outbreak_probability_logic(self):
        """
        Ensures that high-suitability environmental indicators combined with 
        active clinical cases result in high risk probabilities.
        """
        # Scenario: Optimal temperature (24C), High Humidity (80%), and Active Cases
        high_risk_row = pd.Series({
            "temperature_lst": 24.0,
            "relative_humidity": 80.0,
            "active_cases": 5,
            "population": 10000
        })
        
        # Scenario: Non-optimal conditions and zero cases
        low_risk_row = pd.Series({
            "temperature_lst": 45.0, # Too hot for many pathogens
            "relative_humidity": 10.0, # Too dry
            "active_cases": 0,
            "population": 10000
        })
        
        high_prob = self.risk_agent._calculate_logistic_probability(high_risk_row)
        low_prob = self.risk_agent._calculate_logistic_probability(low_risk_row)
        
        # Assertions
        self.assertGreater(high_prob, 0.7, "High suitability scenario failed to reach high probability.")
        self.assertLess(low_prob, 0.3, "Low suitability scenario failed to reach low probability.")

    # --- 2. EPIDEMIOLOGICAL MODELING: R0 & HIT ---
    def test_r0_calculation_accuracy(self):
        """
        Validates the Basic Reproduction Number (R0) formula logic.
        Formula: R0 = (Beta * S_eff) / (Gamma + Mu + Phi)
        """
        # Standard test parameters
        beta = 2.95
        susceptible = 1000
        total_n = 1000
        vax_coverage = 0.0 # No protection
        
        result = self.model_engine.calculate_r0(
            transmission_rate=beta,
            susceptible_population=susceptible,
            total_population=total_n,
            vaccination_coverage=vax_coverage
        )
        
        # Denominator calculation (from engine constants): 
        # Gamma (1/10.8) + Mu (0.0571) = 0.0926 + 0.0571 = 0.1497
        # R0 = (2.95 * 1.0) / 0.1497 ~= 19.7
        self.assertGreater(result["r0"], 10.0)
        self.assertEqual(result["epidemiological_status"], "Epidemic Persistent (DFE Unstable)")

    def test_herd_immunity_threshold(self):
        """
        Verifies the HIT calculation: HIT = 1 - (1 / R0).
        If R0 = 2.0, HIT must be 50.0%.
        """
        # We manipulate inputs to force an R0 of exactly 2.0
        # Denominator is ~0.1497. We need numerator to be ~0.2994.
        # beta * S_eff = 0.2994
        
        result = self.model_engine.calculate_r0(
            transmission_rate=0.2994, 
            susceptible_population=1000,
            total_population=1000,
            vaccination_coverage=0.0
        )
        
        self.assertAlmostEqual(result["r0"], 2.0, places=1)
        self.assertEqual(result["herd_immunity_threshold_pct"], 50.0)

    # --- 3. BOUNDEDNESS & STABILITY ---
    def test_vaccination_impact_on_r0(self):
        """
        Ensures that increasing vaccination coverage monotonically 
        decreases the Basic Reproduction Number (R0).
        """
        base_r0 = self.model_engine.calculate_r0(2.0, 1000, 1000, 0.1)["r0"]
        high_vax_r0 = self.model_engine.calculate_r0(2.0, 1000, 1000, 0.9)["r0"]
        
        self.assertLess(high_vax_r0, base_r0, "Increased vaccination failed to reduce R0.")

    def test_dfe_stability_transition(self):
        """
        Verifies Theorem 3 (Slide 25): If R0 < 1, the DFE is stable.
        """
        # Force a very low transmission rate
        result = self.model_engine.calculate_r0(
            transmission_rate=0.01, 
            susceptible_population=100,
            total_population=1000,
            vaccination_coverage=0.9
        )
        
        self.assertLess(result["r0"], 1.0)
        self.assertIn("Controlled", result["epidemiological_status"])

if __name__ == "__main__":
    unittest.main()
