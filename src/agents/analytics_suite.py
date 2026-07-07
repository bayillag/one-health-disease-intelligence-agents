# src/agents/analytics_suite.py

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

class OneHealthAnalyticsSuite:
    """
    Executes advanced analytical workflows for disease forecasting and mitigation.
    
    Implements:
    - Disease Forewarning & Hotspot detection.
    - Spatial Clustering (proximity-based grouping).
    - Impact Analysis (Intervention simulation).
    - Temporal Trend Analysis.
    """
    def __init__(self, risk_df: pd.DataFrame):
        # Master dataframe containing evaluated risk scores and climate metrics
        self.data = risk_df

    # --- 1. DISEASE FOREWARNING ---
    def get_priority_forewarning(self, top_n: int = 5) -> pd.DataFrame:
        """Retrieves the top-N highest risk districts for immediate attention."""
        return self.data.sort_values(by="risk_probability", ascending=False).head(top_n)[
            ["district", "region", "disease_name", "risk_probability", "risk_class"]
        ]

    # --- 2. FORECASTED PARAMETERS ---
    def get_climatic_profile(self, district: str) -> Dict[str, float]:
        """Returns the specific environmental parameters for a target district."""
        row = self.data[self.data["district"].str.lower() == district.lower().strip()]
        if row.empty:
            return {}
        res = row.iloc[0]
        return {
            "temp_lst": float(res["temperature_lst"]),
            "humidity": float(res["relative_humidity"]),
            "precipitation": float(res["precipitation_mm"])
        }

    # --- 3. DISEASE TRENDS ---
    def calculate_temporal_intensity(self, historical_df: pd.DataFrame) -> pd.DataFrame:
        """Analyzes historical case data to identify seasonal intensity peaks."""
        # Returns average cases per month to identify 'Outbreak Seasons'
        return historical_df.groupby("month")["active_cases"].mean().reset_index()

    # --- 4. IMPACT ANALYSIS (Intervention Simulation) ---
    def simulate_mitigation_impact(
        self, 
        vaccination_coverage: float, 
        isolation_rate: float,
        vaccine_efficacy: float = 0.724
    ) -> Dict[str, Any]:
        """
        Simulates the reduction in national/regional disease burden 
        given specific intervention targets.
        """
        base_cases = self.data["active_cases"].sum()
        
        # Mitigation multiplier based on protective coverage and isolation effectiveness
        # Derived from the SEIRV optimal control logic (Slide 26)
        protection_factor = (vaccination_coverage * vaccine_efficacy) + isolation_rate
        mitigation_multiplier = max(0.05, 1.0 - protection_factor) 
        
        simulated_cases = int(base_cases * mitigation_multiplier)
        prevented_cases = int(base_cases - simulated_cases)
        
        return {
            "intervention_targets": {
                "vax_coverage_pct": vaccination_coverage * 100,
                "isolation_rate_pct": isolation_rate * 100
            },
            "outcomes": {
                "baseline_cases": int(base_cases),
                "estimated_simulated_cases": simulated_cases,
                "estimated_prevented_cases": prevented_cases,
                "reduction_percentage": round((prevented_cases / base_cases) * 100, 2) if base_cases > 0 else 0.0
            }
        }

    # --- 5. DISEASE HOTSPOTS ---
    def get_hotspot_coordinates(self, min_risk: float = 0.6) -> List[Dict[str, Any]]:
        """Extracts spatial coordinates for high-risk zones for GIS heatmaps."""
        hotspots = self.data[self.data["risk_probability"] >= min_risk]
        return hotspots[["latitude", "longitude", "risk_probability", "district"]].to_dict(orient="records")

    # --- 6. DISEASE CLUSTERS ---
    def detect_spatial_clusters(self, radius_km: float = 50.0) -> List[Dict[str, Any]]:
        """
        Groups adjacent high-risk districts into spatial clusters.
        Essential for coordinating regional 'Ring Vaccination' protocols.
        """
        high_risk_zones = self.data[self.data["risk_class"].isin(["High Risk", "Very High Risk"])].copy()
        
        if len(high_risk_zones) < 2:
            return []

        clusters = []
        visited = set()

        # Simple greedy spatial clustering
        for i, row in high_risk_zones.iterrows():
            if row["district"] in visited:
                continue
                
            current_cluster = {
                "center_district": row["district"],
                "region": row["region"],
                "neighboring_high_risk_districts": []
            }
            visited.add(row["district"])
            
            for j, other in high_risk_zones.iterrows():
                if other["district"] in visited:
                    continue
                
                # Haversine distance approximation (1 degree lat ~= 111km)
                dist = np.sqrt(
                    (row["latitude"] - other["latitude"])**2 + 
                    (row["longitude"] - other["longitude"])**2
                ) * 111.0
                
                if dist <= radius_km:
                    current_cluster["neighboring_high_risk_districts"].append(other["district"])
                    visited.add(other["district"])
            
            if current_cluster["neighboring_high_risk_districts"]:
                clusters.append(current_cluster)
        
        return clusters

    # --- 7. LIVESTOCK & DISEASE MAPS (Mapping Payload) ---
    def compile_mapping_payload(self) -> Dict[str, Any]:
        """Compiles host distribution and active case counts for GIS layers."""
        return {
            "host_density": self.data[["district", "latitude", "longitude", "population"]].to_dict(orient="records"),
            "active_cases": self.data[self.data["active_cases"] > 0][
                ["district", "latitude", "longitude", "active_cases", "disease_name"]
            ].to_dict(orient="records")
        }
