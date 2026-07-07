# src/agents/epidemiological_modeling_engine.py

import numpy as np
import math
from typing import Dict, Any, List

class EpidemiologicalModelingEngine:
    """
    Translates SEIRV compartmental differential equations and NGM theorems 
    into executable mathematical models.
    
    Demonstrates:
    - Mechanistic Modeling: Simulating disease transmission dynamics.
    - Threshold Analysis: Calculating R0 and Herd Immunity Thresholds (HIT).
    - Policy Simulation: Evaluating the impact of JIT isolation and vaccination.
    """
    def __init__(self):
        # Default biological constants for Foot-and-Mouth Disease (FMD) 
        # (Derived from Slides 19, 28, and 29)
        self.incubation_period = 3.6    # Days
        self.latent_period = 1.5        # Days
        self.infectious_period = 10.8    # Total duration (Subclinical + Clinical)
        self.natural_mortality = 0.0571  # mu_c (Slide 28)
        self.vaccine_efficacy = 0.724   # VE (Slide 30)

    def calculate_r0(
        self, 
        transmission_rate: float,      # beta
        susceptible_population: int,   # Sc
        total_population: int,         # N
        vaccination_coverage: float,   # alpha (0.0 to 1.0)
        isolation_rate: float = 0.0    # phi (Slide 26 control variable u2)
    ) -> Dict[str, Any]:
        """
        Calculates the Basic Reproduction Number (R0) and HIT.
        
        Formula (Generalized NGM): 
        R0 = (beta * S_eff) / (gamma + mu + phi)
        """
        # 1. Calculate kinetic rates
        gamma = 1.0 / self.infectious_period  # Recovery rate
        mu = self.natural_mortality           # Natural death rate
        
        # 2. Calculate Effective Susceptibility (S_eff)
        # Accounts for the proportion of population protected by vaccination
        protection_multiplier = 1.0 - (vaccination_coverage * self.vaccine_efficacy)
        s_effective = (susceptible_population / total_population) * protection_multiplier
        
        # 3. Calculate R0
        # Denominator includes recovery, natural death, and active isolation (phi)
        denominator = gamma + mu + isolation_rate
        r0 = (transmission_rate * s_effective) / denominator if denominator > 0 else 0.0
        r0 = round(r0, 4)
        
        # 4. Calculate Herd Immunity Threshold (HIT)
        hit = 1.0 - (1.0 / r0) if r0 > 1.0 else 0.0
        
        # 5. Stability Analysis (Theorem 3, Slide 25)
        if r0 > 1.0:
            status = "Epidemic Persistent (DFE Unstable)"
        elif r0 == 1.0:
            status = "Endemic Equilibrium"
        else:
            status = "Epidemic Controlled (DFE Locally Asymptotically Stable)"
            
        return {
            "r0": r0,
            "herd_immunity_threshold_pct": round(hit * 100, 2),
            "epidemiological_status": status,
            "parameters": {
                "effective_beta": round(transmission_rate * s_effective, 4),
                "total_removal_rate": round(denominator, 4)
            }
        }

    def simulate_seirv_dynamics(
        self,
        initial_state: Dict[str, int],
        transmission_rate: float,
        timesteps_days: int = 60,
        vaccination_rate: float = 0.0,
        isolation_rate: float = 0.0
    ) -> pd.DataFrame:
        """
        Euler-method solver for the SEIRV differential equations (Slide 22).
        Predicts the peak infection time and magnitude.
        """
        # Extract initial compartments
        S = initial_state.get("S", 1000)
        E = initial_state.get("E", 0)
        I = initial_state.get("I", 1)
        R = initial_state.get("R", 0)
        V = initial_state.get("V", 0)
        N = S + E + I + R + V
        
        # Rates
        sigma = 1.0 / self.latent_period
        gamma = 1.0 / self.infectious_period
        mu = self.natural_mortality
        
        history = []
        
        for t in range(timesteps_days):
            history.append({"day": t, "S": S, "E": E, "I": I, "R": R, "V": V, "Total": N})
            
            # Differential Equations (Simplified deterministic steps)
            new_infections = (transmission_rate * S * I) / N
            new_exposed_to_infected = sigma * E
            new_recoveries = gamma * I
            
            # State Updates
            dS = -new_infections - (vaccination_rate * S) - (mu * S)
            dE = new_infections - new_exposed_to_infected - (mu * E)
            dI = new_exposed_to_infected - new_recoveries - (isolation_rate * I) - (mu * I)
            dR = new_recoveries + (isolation_rate * I) - (mu * R)
            dV = (vaccination_rate * S) - (mu * V)
            
            S += dS
            E += dE
            I += dI
            R += dR
            V += dV
            
        return pd.DataFrame(history)

    def perform_sensitivity_analysis(self, base_beta: float) -> Dict[str, List[float]]:
        """
        Generates sensitivity curves for R0 based on varying vaccination levels.
        (Visualized in Slide 25)
        """
        vax_levels = np.linspace(0, 1, 11) # 0% to 100% coverage
        r0_results = []
        
        for v in vax_levels:
            res = self.calculate_r0(
                transmission_rate=base_beta,
                susceptible_population=1000,
                total_population=1000,
                vaccination_coverage=v
            )
            r0_results.append(res["r0"])
            
        return {
            "vaccination_coverage_increments": vax_levels.tolist(),
            "resulting_r0_values": r0_results
        }
