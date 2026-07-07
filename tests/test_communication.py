# tests/test_communication.py

import unittest
import pandas as pd
import json
from agents.forewarning_query_engine import ForewarningQueryEngine
from agents.dashboard_visualization_engine import DashboardVisualizationEngine
from agents.prediction_bulletin_engine import PredictionBulletinEngine

class TestCommunicationEngines(unittest.TestCase):
    """
    Automated test suite for Communication and Visualization Engines.
    Validates data filtering, GIS payload structure, and bulletin indexing.
    """

    def setUp(self):
        # Mock Integrated Risk Assessment Data
        self.mock_risk_df = pd.DataFrame({
            "district": ["Jinka", "Bako Gazer", "Asayita"],
            "region": ["South_Ethiopia", "South_Ethiopia", "Afar"],
            "disease_name": ["Anthrax", "Foot and Mouth Disease", "Anthrax"],
            "species": ["cattle", "cattle", "goat"],
            "active_cases": [10, 0, 15],
            "population": [5000, 2000, 8000],
            "deaths": [2, 0, 4],
            "latitude": [5.78, 5.92, 11.56],
            "longitude": [36.56, 36.65, 41.44],
            "risk_probability": [0.85, 0.12, 0.92],
            "risk_class": ["Very High Risk", "Low Risk", "Very High Risk"],
            "temperature_lst": [25.0, 26.0, 38.0],
            "relative_humidity": [70.0, 65.0, 40.0],
            "precipitation_mm": [100.0, 80.0, 20.0]
        })

    # --- 1. FOREWARNING QUERY ENGINE TESTS ---
    def test_region_single_disease_query(self):
        """Validates filtering by region and pathogen."""
        engine = ForewarningQueryEngine(self.mock_risk_df)
        results = engine.query_region_single_disease("South_Ethiopia", "Anthrax")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["district"], "Jinka")
        self.assertEqual(results[0]["risk_class"], "Very High Risk")

    def test_district_query_context(self):
        """Verifies high-resolution district data retrieval with biophysical context."""
        engine = ForewarningQueryEngine(self.mock_risk_df)
        res = engine.query_district_single_disease("Jinka", "Anthrax")
        
        self.assertIsNotNone(res)
        self.assertEqual(res["risk_outcome"]["classification"], "Very High Risk")
        self.assertIn("biophysical_context", res)
        self.assertEqual(res["biophysical_context"]["land_surface_temp"], 25.0)

    # --- 2. VISUALIZATION ENGINE TESTS ---
    def test_geojson_feature_collection_structure(self):
        """Ensures generated GeoJSON complies with standard RFC 7946 schemas."""
        vis = DashboardVisualizationEngine(self.mock_risk_df)
        geojson = vis.compile_geojson_collection()
        
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertEqual(len(geojson["features"]), 3)
        # Verify first feature geometry
        first_feature = geojson["features"][0]
        self.assertEqual(first_feature["geometry"]["type"], "Point")
        self.assertEqual(first_feature["geometry"]["coordinates"], [36.56, 5.78])
        # Verify properties mapping
        self.assertEqual(first_feature["properties"]["district"], "Jinka")

    def test_dashboard_kpi_aggregation(self):
        """Verifies that national metrics are summed correctly for the dashboard."""
        vis = DashboardVisualizationEngine(self.mock_risk_df)
        payload = vis.compile_analytical_dashboard_payload()
        
        self.assertEqual(payload["kpis"]["national_case_total"], 25) # 10 + 0 + 15
        self.assertEqual(payload["distributions"]["risk_levels"]["Very High Risk"], 2)

    # --- 3. BULLETIN LIBRARY TESTS ---
    def test_bulletin_catalog_search(self):
        """Validates metadata-based search within the forecast library."""
        lib = PredictionBulletinEngine()
        # Search for 'August' in mock catalog titles (defined in the class)
        res = lib.query_bulletin_library(search_query="August")
        
        self.assertGreater(len(res), 0)
        self.assertIn("August", res[0]["title"])

    def test_report_indexing_and_latest_flag(self):
        """Ensures that newly added reports are correctly indexed and marked as 'latest'."""
        lib = PredictionBulletinEngine()
        initial_count = len(lib.catalog)
        
        new_entry = {
            "id": "test_01", 
            "title": "Test Report", 
            "forecast_target_month": "Dec 2026", 
            "category": "Prediction"
        }
        lib.add_new_report(new_entry)
        
        self.assertEqual(len(lib.catalog), initial_count + 1)
        self.assertTrue(lib.catalog[0]["is_latest"])
        self.assertFalse(lib.catalog[1]["is_latest"]) # Verification that previous was demoted

if __name__ == "__main__":
    unittest.main()
