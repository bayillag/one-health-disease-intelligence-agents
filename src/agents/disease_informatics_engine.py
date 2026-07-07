# src/agents/disease_informatics_engine.py

import pandas as pd
from typing import Dict, Any, List
from utils.disease_profiles import DISEASE_PATHOGEN_REGISTRY

class DiseaseInformaticsEngine:
    """
    Implements the 9 primary descriptive analytics workflows for the 
    Disease Informatics dashboard module.
    
    Transforms integrated datasets into regional metrics, disease rankings, 
    and zoonotic incident summaries.
    """
    def __init__(self, integrated_df: pd.DataFrame):
        # Master dataframe containing merged veterinary records and climate metrics
        self.df = integrated_df
        self.pathogen_registry = DISEASE_PATHOGEN_REGISTRY

    # --- 1. REGION WISE (State Wise) ---
    def get_region_wise_metrics(self) -> pd.DataFrame:
        """Aggregates active cases and susceptible livestock populations by Region."""
        return self.df.groupby("region").agg(
            total_active_cases=("active_cases", "sum"),
            total_susceptible_population=("population", "sum"),
            affected_districts=("district", "nunique")
        ).reset_index()

    # --- 2. DISEASE WISE ---
    def get_disease_wise_metrics(self) -> pd.DataFrame:
        """Aggregates epidemiological metrics grouped by specific disease types."""
        return self.df.groupby("disease_name").agg(
            total_incidents=("active_cases", "sum"),
            total_deaths=("deaths", "sum"),
            affected_regions=("region", "nunique"),
            affected_districts=("district", "nunique")
        ).reset_index()

    # --- 3. CASE BY OUTBREAKS ---
    def get_outbreak_case_counts(self) -> pd.DataFrame:
        """Returns detailed records for all districts with active (>0) outbreaks."""
        active_outbreaks = self.df[self.df["active_cases"] > 0]
        return active_outbreaks[
            ["district", "region", "disease_name", "species", "active_cases", "risk_class"]
        ].sort_values(by="active_cases", ascending=False).reset_index(drop=True)

    # --- 4. YEAR WISE ---
    def get_annual_trends(self) -> pd.DataFrame:
        """Summarizes national disease burden trends across reporting years."""
        return self.df.groupby("year").agg(
            annual_cases=("active_cases", "sum"),
            annual_deaths=("deaths", "sum")
        ).reset_index()

    # --- 5. LIVESTOCK POPULATION ---
    def get_livestock_population_by_species(self) -> pd.DataFrame:
        """Summarizes host population demographics by species."""
        return self.df.groupby("species").agg(
            total_population=("population", "sum")
        ).reset_index()

    # --- 6. TOP 10 LIVESTOCK DISTRICTS ---
    def get_top_10_livestock_districts(self) -> pd.DataFrame:
        """Identifies the top 10 districts with the highest host population density."""
        district_summary = self.df.groupby(["district", "region"]).agg(
            total_pop=("population", "sum")
        ).reset_index()
        return district_summary.nlargest(10, "total_pop")

    # --- 7. TOP 10 DISEASES ---
    def get_top_10_diseases(self) -> pd.DataFrame:
        """Ranks the top 10 pathogens by total reported case count (attacks)."""
        disease_summary = self.get_disease_wise_metrics()
        return disease_summary.nlargest(10, "total_active_cases")

    # --- 8. REPORT GENERATION ---
    def compile_informatics_report(self) -> Dict[str, Any]:
        """Synthesizes a high-level summary JSON for the Communication Agent."""
        region_metrics = self.get_region_wise_metrics()
        
        # Identify highest burden areas
        highest_cases_region = region_metrics.loc[region_metrics["total_active_cases"].idxmax()] if not region_metrics.empty else None
        
        return {
            "metadata": {
                "total_districts_reporting": int(self.df["district"].nunique()),
                "total_active_cases_national": int(self.df["active_cases"].sum())
            },
            "geographic_focus": {
                "highest_burden_region": highest_cases_region["region"] if highest_cases_region is not None else "N/A",
                "max_cases_in_region": int(highest_cases_region["total_active_cases"]) if highest_cases_region is not None else 0
            }
        }

    # --- 9. ZOONOTIC DISEASES ---
    def get_zoonotic_disease_incidences(self) -> pd.DataFrame:
        """
        Dynamically filters the database to isolate pathogens with 
        confirmed zoonotic potential as defined in the disease profiles.
        """
        # Determine zoonotic pathogens from registry
        zoonotic_keys = [pathogen for pathogen, meta in self.pathogen_registry.items() if meta["zoonotic"]]
        
        zoonotics_df = self.df[self.df["disease_name"].isin(zoonotic_keys)]
        
        return zoonotics_df.groupby("disease_name").agg(
            outbreak_locations=("district", "nunique"),
            total_zoonotic_cases=("active_cases", "sum"),
            associated_deaths=("deaths", "sum")
        ).reset_index()
