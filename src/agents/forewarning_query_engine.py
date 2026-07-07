# src/agents/forewarning_query_engine.py

import pandas as pd
from typing import Dict, Any, List, Optional

class ForewarningQueryEngine:
    """
    Manages spatial and pathogen-specific queries to support localized 
    forewarning reports for regional veterinary officers and epidemiologists.
    
    Demonstrates:
    - Target Querying: Filtering high-resolution risk data for specific zones.
    - Automated Reporting: Compiling multi-pathogen risk profiles for regional states.
    """
    def __init__(self, assessment_df: pd.DataFrame):
        # Expects a fully processed dataframe from the RiskAnalysisAgent (evaluated_risk_matrix)
        self.df = assessment_df

    def _standardize_string(self, text: str) -> str:
        """Helper to ensure robust string matching across user inputs."""
        return str(text).lower().strip()

    # --- 1. REGION-WISE SINGLE DISEASE (State-Wise Single Disease) ---
    def query_region_single_disease(self, region: str, disease_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves the predicted risk levels across all districts within a specific
        region for ONE selected disease. 
        
        Use case: Identifying which woredas in 'Afar' are at risk of 'PPR'.
        """
        if self.df.empty:
            return []
            
        region_query = self._standardize_string(region)
        disease_query = self._standardize_string(disease_name)
        
        mask = (self.df["region"].str.lower() == region_query) & \
               (self.df["disease_name"].str.lower() == disease_query)
        
        filtered = self.df[mask].copy()
        
        # Sort by highest risk probability for prioritization
        sorted_results = filtered.sort_values(by="risk_probability", ascending=False)
        
        return sorted_results[
            ["district", "risk_probability", "risk_class", "active_cases"]
        ].to_dict(orient="records")

    # --- 2. REGION-WISE ALL DISEASES (State-wise All Disease) ---
    def query_region_all_diseases(self, region: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generates a comprehensive multi-pathogen risk summary for all districts 
        within a selected region.
        
        Use case: A regional head needs the full risk profile for 'South_Ethiopia'.
        """
        if self.df.empty:
            return {}
            
        region_query = self._standardize_string(region)
        filtered = self.df[self.df["region"].str.lower() == region_query].copy()
        
        # Structure the outcome as a dictionary keyed by district name
        summary_by_district = {}
        for district in filtered["district"].unique():
            district_df = filtered[filtered["district"] == district]
            
            # For each district, provide a list of pathogens sorted by risk
            summary_by_district[district] = district_df[
                ["disease_name", "risk_probability", "risk_class", "species"]
            ].sort_values(by="risk_probability", ascending=False).to_dict(orient="records")
            
        return summary_by_district

    # --- 3. DISTRICT-WISE SINGLE DISEASE ---
    def query_district_single_disease(self, district: str, disease_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a high-resolution, single-pathogen risk prediction for 
        one selected district/woreda, including biophysical context.
        
        Use case: A field vet in 'Jinka' needs the detailed 'Anthrax' risk report.
        """
        if self.df.empty:
            return None
            
        district_query = self._standardize_string(district)
        disease_query = self._standardize_string(disease_name)
        
        mask = (self.df["district"].str.lower() == district_query) & \
               (self.df["disease_name"].str.lower() == disease_query)
        
        match = self.df[mask]
        
        if match.empty:
            return None
            
        row = match.iloc[0]
        
        # Include biophysical parameters that drove the decision (Context Engineering)
        return {
            "metadata": {
                "district": row["district"],
                "region": row["region"],
                "pathogen": row["disease_name"]
            },
            "risk_outcome": {
                "probability": float(row["risk_probability"]),
                "classification": row["risk_class"],
                "active_cases_reported": int(row["active_cases"])
            },
            "biophysical_context": {
                "land_surface_temp": float(row.get("temperature_lst", 0.0)),
                "relative_humidity": float(row.get("relative_humidity", 0.0)),
                "precipitation": float(row.get("precipitation_mm", 0.0))
            }
        }

    def get_available_filters(self) -> Dict[str, List[str]]:
        """Utility to populate dashboard dropdown menus."""
        return {
            "regions": sorted(self.df["region"].unique().tolist()),
            "diseases": sorted(self.df["disease_name"].unique().tolist()),
            "districts": sorted(self.df["district"].unique().tolist())
        }
