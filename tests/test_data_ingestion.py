# tests/test_data_ingestion.py

import unittest
import pandas as pd
import os
from agents.data_ingestion_agent import DataIngestionAgent

class TestDataIngestion(unittest.TestCase):
    """
    Automated test suite for the Data Ingestion Agent.
    Validates security authorization and biophysical range sanitization.
    """

    def setUp(self):
        # Paths to sample data created in run_pipeline.py
        self.vet_data_path = "data/raw/veterinary_records.csv"
        self.climate_data_path = "data/raw/climate_layers.csv"

    # --- 1. SECURITY: RBAC VERIFICATION ---
    def test_authorized_access(self):
        """Ensures that authorized roles can successfully ingest veterinary data."""
        agent = DataIngestionAgent(user_role="vet_lab_staff")
        try:
            df = agent.ingest_veterinary_records(self.vet_data_path)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertFalse(df.empty)
        except PermissionError:
            self.fail("DataIngestionAgent raised PermissionError for an authorized role.")

    def test_unauthorized_access(self):
        """Ensures that unauthorized roles are blocked from clinical data (Pillar 5)."""
        agent = DataIngestionAgent(user_role="public_guest")
        with self.assertRaises(PermissionError):
            agent.ingest_veterinary_records(self.vet_data_path)

    # --- 2. DATA INTEGRITY: SCHEMA VALIDATION ---
    def test_missing_file_error(self):
        """Ensures FileNotFoundError is raised for non-existent datasets."""
        agent = DataIngestionAgent(user_role="administrator")
        with self.assertRaises(FileNotFoundError):
            agent.ingest_climate_data("non_existent_file.csv")

    # --- 3. HARNESS ENGINEERING: RANGE VALIDATION (CLIPPING) ---
    def test_biophysical_clipping(self):
        """
        Verifies that anomalous sensor readings are clipped to physical boundaries.
        e.g., Relative Humidity > 100% or NDVI > 1.0.
        """
        agent = DataIngestionAgent(user_role="administrator")
        
        # Create a mock dataframe with out-of-range values
        anomalous_data = pd.DataFrame({
            "district": ["TestDistrict"],
            "region": ["TestRegion"],
            "relative_humidity": [115.0], # Impossible (>100%)
            "ndvi": [-1.5],               # Impossible (< -1.0)
            "temperature_lst": [45.0]     # Valid
        })
        
        # Save temp file
        temp_path = "data/raw/temp_test_clipping.csv"
        anomalous_data.to_csv(temp_path, index=False)
        
        # Run through ingestion
        cleaned_df = agent.ingest_climate_data(temp_path)
        
        # Assertions: values must be clamped to registry boundaries
        self.assertEqual(cleaned_df.loc[0, "relative_humidity"], 100.0)
        self.assertEqual(cleaned_df.loc[0, "ndvi"], -1.0)
        self.assertEqual(cleaned_df.loc[0, "temperature_lst"], 45.0) # Unchanged
        
        # Cleanup
        os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
