# run_pipeline.py

import os
import json
import pandas as pd
from src.agents.data_ingestion_agent import DataIngestionAgent
from src.agents.risk_analysis_agent import RiskAnalysisAgent
from src.agents.disease_informatics_engine import DiseaseInformaticsEngine
from src.agents.analytics_suite import OneHealthAnalyticsSuite
from src.agents.epidemiological_modeling_engine import EpidemiologicalModelingEngine
from src.agents.epi_toolbox import OneHealthEpidemiologicalToolbox
from src.agents.dashboard_visualization_engine import DashboardVisualizationEngine
from src.agents.forewarning_query_engine import ForewarningQueryEngine
from src.agents.prediction_bulletin_engine import PredictionBulletinEngine

def ensure_directory_structures():
    """Guarantees that all required project subdirectories exist prior to execution."""
    dirs = [
        "data/raw",
        "data/processed",
        "src/utils",
        "src/agents",
        "src/dashboard",
        "docs/bulletins"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("[INIT] Workspace directories verified and configured.")

def create_mock_source_data():
    """Generates localized sample source files if they are not already present in the folder."""
    vet_path = "data/raw/veterinary_records.csv"
    climate_path = "data/raw/climate_layers.csv"
    
    if not os.path.exists(vet_path):
        # Primary district-level clinical records representing Southwest Ethiopia
        vet_data = {
            "district": ["Jinka", "Bako Gazer", "Hammer", "Asayita", "Yabelo", "Gode"],
            "region": ["South_Ethiopia", "South_Ethiopia", "South_Ethiopia", "Afar", "Oromia", "Somali"],
            "disease_name": ["Anthrax", "Anthrax", "Foot and Mouth Disease", "Peste des Petits Ruminants", "Anthrax", "Rift Valley Fever"],
            "species": ["cattle", "cattle", "cattle", "goat", "cattle", "sheep"],
            "active_cases": [12, 4, 0, 18, 9, 1],
            "population": [45000, 32000, 15000, 68000, 89000, 54000],
            "deaths": [3, 1, 0, 5, 2, 0],
            "year": [2025, 2025, 2025, 2025, 2025, 2025],
            "latitude": [5.78, 5.92, 5.20, 11.56, 4.88, 5.10],
            "longitude": [36.56, 36.65, 36.45, 41.44, 38.08, 43.50]
        }
        pd.DataFrame(vet_data).to_csv(vet_path, index=False)
        print(f"[INIT] Created sample veterinary records database at: {vet_path}")
        
    if not os.path.exists(climate_path):
        # Environmental layers matching identical spatial districts
        climate_data = {
            "district": ["Jinka", "Bako Gazer", "Hammer", "Asayita", "Yabelo", "Gode"],
            "region": ["South_Ethiopia", "South_Ethiopia", "South_Ethiopia", "Afar", "Oromia", "Somali"],
            "temperature_lst": [27.5, 26.1, 29.4, 38.0, 32.4, 34.2],
            "relative_humidity": [82.0, 75.0, 50.0, 45.0, 50.0, 40.0],
            "precipitation_mm": [185.0, 140.0, 45.0, 60.0, 85.0, 45.0]
        }
        pd.DataFrame(climate_data).to_csv(climate_path, index=False)
        print(f"[INIT] Created sample climate metrics database at: {climate_path}")

def main():
    ensure_directory_structures()
    create_mock_source_data()
    
    print("\n=== STARTING ONE HEALTH AUTOMATED INTELLIGENCE PIPELINE ===")
    
    # --------------------------------------------------------------------
    # PHASE 1: DATA INGESTION & SCHEMATIC VALIDATION
    # --------------------------------------------------------------------
    print("\n[PHASE 1] Executing Data Ingestion validation checks...")
    # Initialize DataIngestionAgent under secure credentials
    ingestion_agent = DataIngestionAgent(user_role="vet_lab_staff")
    
    raw_vet_df = ingestion_agent.ingest_veterinary_records("data/raw/veterinary_records.csv")
    raw_climate_df = ingestion_agent.ingest_climate_data("data/raw/climate_layers.csv")
    
    # --------------------------------------------------------------------
    # PHASE 2: EPIDEMIOLOGICAL AND RISK MODELING
    # --------------------------------------------------------------------
    print("\n[PHASE 2] Executing spatiotemporal risk analysis & epidemiological modeling...")
    analysis_agent = RiskAnalysisAgent()
    modeled_risk_df = analysis_agent.evaluate_risk_matrix(raw_vet_df, raw_climate_df)
    
    # Export processed risk assessments for the R Shiny dashboard
    output_path = "data/processed/risk_assessment_output.csv"
    modeled_risk_df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Model assessments exported to: {output_path}")
    
    # --------------------------------------------------------------------
    # PHASE 3: TRANSMISSION THRESHOLD MODELING (R0)
    # --------------------------------------------------------------------
    print("\n[PHASE 3] Simulating basic reproduction numbers (R0) and threshold limits...")
    model_engine = EpidemiologicalModelingEngine()
    
    # Simulating a high-consequence Anthrax introduction in South Ethiopia (Jinka)
    jinka_row = modeled_risk_df[modeled_risk_df["district"] == "Jinka"].iloc[0]
    
    # Evaluate under low intervention coverage
    low_intervention = model_engine.calculate_r0(
        transmission_rate=2.95, # High environmental pressure
        susceptible_population=int(jinka_row["population"]),
        total_population=287502,
        vaccination_coverage=0.45,
        isolation_rate=0.0
    )
    # Evaluate under optimal targeted intervention
    optimal_intervention = model_engine.calculate_r0(
        transmission_rate=2.95,
        susceptible_population=int(jinka_row["population"]),
        total_population=287502,
        vaccination_coverage=0.94,
        isolation_rate=0.259
    )
    print(f"Jinka Baseline R0 (45% Vax): {low_intervention['r0']} -> {low_intervention['epidemiological_status']}")
    print(f"Jinka Targeted R0 (94% Vax + isolation): {optimal_intervention['r0']} -> {optimal_intervention['epidemiological_status']}")

    # --------------------------------------------------------------------
    # PHASE 4: ACTIVE SERO-SURVEILLANCE SAMPLING DESIGN
    # --------------------------------------------------------------------
    print("\n[PHASE 4] Calculating active sero-surveillance sampling plan designs...")
    toolbox = OneHealthEpidemiologicalToolbox()
    
    # Calculate required sample size with Finite Population Correction (FPC)
    sampling_targets = toolbox.calculate_required_sample_size(
        expected_prevalence=0.10, # Expected prevalence 10%
        precision=0.05,            # +/- 5% absolute precision
        population_size=1500       # Target local pastoralist herd size
    )
    print(f"Surveillance design: FPC-corrected sample size target is {sampling_targets['fpc_corrected_sample_size']} animals out of 1,500.")

    # --------------------------------------------------------------------
    # PHASE 5: COMPILING VISUALIZATION AND GIS ASSETS
    # --------------------------------------------------------------------
    print("\n[PHASE 5] Compiling GIS features and interactive dashboard assets...")
    vis_engine = DashboardVisualizationEngine(modeled_risk_df)
    
    # Generate spatial GeoJSON Point Feature Collection
    geojson_payload = vis_engine.compile_geojson_collection()
    
    geojson_path = "docs/risk_map_example.json"
    with open(geojson_path, "w") as f:
        json.dump(geojson_payload, f, indent=2)
    print(f"[SUCCESS] Spatial GeoJSON mapping assets saved to: {geojson_path}")
    
    # --------------------------------------------------------------------
    # PHASE 6: DOCUMENT ARCHIVING & CATALOGUING
    # --------------------------------------------------------------------
    print("\n[PHASE 6] Indexing generated early-warning bulletins...")
    bulletin_library = PredictionBulletinEngine()
    
    # Index the newly compiled forecast
    new_report_meta = {
        "id": "rep_003",
        "title": "August 2026 prediction report of October 2026 - Part 1",
        "publish_date": "2026-08-09",
        "forecast_target_month": "October 2026",
        "category": "Prediction",
        "is_latest": True,
        "file_path": "docs/bulletins/bulletin_2026_08.md"
    }
    bulletin_library.add_new_report(new_report_meta)
    
    print("[SUCCESS] Multi-agent processing run concluded successfully.")
    print("=============================================================")

if __name__ == "__main__":
    main()
