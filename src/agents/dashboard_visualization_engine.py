# src/agents/dashboard_visualization_engine.py

import pandas as pd
import json
from typing import Dict, Any, List

class DashboardVisualizationEngine:
    """
    Translates processed epidemiological risk matrices into structured 
    payloads for interactive web and GIS dashboard modules.
    
    Demonstrates:
    - Data Marshalling: Formatting agent outputs for UI consumption.
    - Geospatial Compilation: Generating valid GeoJSON for GIS interoperability.
    - Statistical Aggregation: Compiling KPI metrics for executive dashboards.
    """
    def __init__(self, processed_df: pd.DataFrame):
        # Expects the outcome of RiskAnalysisAgent.evaluate_risk_matrix()
        self.df = processed_df

    # --- 1. ANALYTICAL DASHBOARD PAYLOAD ---
    def compile_analytical_dashboard_payload(self) -> Dict[str, Any]:
        """
        Aggregates risk and case data into a JSON structure designed for 
        plotting widgets (e.g., Pie charts of risk levels, Bar charts of cases).
        """
        if self.df.empty:
            return {"error": "Dataset is empty."}
            
        # Risk distribution counts (for the Pie charts)
        risk_counts = self.df["risk_class"].value_counts().to_dict()
        
        # Species-specific burden (for Bar charts)
        species_burden = self.df.groupby("species")["active_cases"].sum().to_dict()
        
        # Regional summaries (for State-wise results tables)
        regional_summary = self.df.groupby("region").agg(
            total_cases=("active_cases", "sum"),
            avg_risk_prob=("risk_probability", "mean"),
            total_population=("population", "sum")
        ).to_dict(orient="index")
        
        return {
            "kpis": {
                "active_outbreaks": int((self.df["active_cases"] > 0).sum()),
                "national_case_total": int(self.df["active_cases"].sum()),
                "total_monitored_hosts": int(self.df["population"].sum())
            },
            "distributions": {
                "risk_levels": risk_counts,
                "species_burden": species_burden
            },
            "regional_data": regional_summary
        }

    # --- 2. RISK-MAP INTENSITY ARRAYS (Heatmaps) ---
    def compile_risk_map_arrays(self, target_disease: str) -> List[Dict[str, Any]]:
        """
        Generates coordinate intensity arrays for spatial heatmaps.
        Uses the 'risk_probability' (0.0 - 1.0) as the weight for each point.
        """
        disease_filter = self.df["disease_name"].str.lower() == target_disease.lower().strip()
        filtered_df = self.df[disease_filter]
        
        heat_points = []
        for _, row in filtered_df.iterrows():
            heat_points.append({
                "lat": float(row["latitude"]),
                "lng": float(row["longitude"]),
                "weight": float(row["risk_probability"]),
                "district": row["district"],
                "risk_level": row["risk_class"]
            })
        return heat_points

    # --- 3. ONLINE GIS MAPS (GeoJSON) ---
    def compile_geojson_collection(self) -> Dict[str, Any]:
        """
        Converts the processed dataframe into a standard GeoJSON FeatureCollection.
        This asset is interoperable with Leaflet, Mapbox, and desktop GIS like QGIS.
        """
        features = []
        
        for _, row in self.df.iterrows():
            # Construct a GeoJSON 'Feature' object
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row["longitude"]), float(row["latitude"])]
                },
                "properties": {
                    "district": row["district"],
                    "region": row["region"],
                    "disease": row["disease_name"],
                    "species": row["species"],
                    "active_cases": int(row["active_cases"]),
                    "deaths": int(row["deaths"]),
                    "risk_probability": float(row["risk_probability"]),
                    "risk_class": row["risk_class"],
                    "environmental_suite": {
                        "temp_lst": float(row.get("temperature_lst", 0)),
                        "humidity": float(row.get("relative_humidity", 0)),
                        "precip_mm": float(row.get("precipitation_mm", 0))
                    }
                }
            }
            features.append(feature)
            
        # Wrap into a FeatureCollection
        return {
            "type": "FeatureCollection",
            "metadata": {
                "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "record_count": len(features)
            },
            "features": features
        }

    def save_geojson(self, file_path: str) -> bool:
        """Utility to write the GeoJSON payload to the docs/ directory."""
        try:
            payload = self.compile_geojson_collection()
            with open(file_path, "w") as f:
                json.dump(payload, f, indent=2)
            return True
        except Exception as e:
            print(f"[VISUALIZATION ERROR] Failed to save GeoJSON: {e}")
            return False
