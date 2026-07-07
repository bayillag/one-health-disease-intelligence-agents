# src/agents/data_ingestion_agent.py

import os
import pandas as pd
from typing import Dict, Any, List, Optional
from utils.parameter_registry import ENVIRONMENTAL_PARAMETER_REGISTRY

class DataIngestionAgent:
    """
    Ingests, cleans, and validates satellite-derived meteorological 
    and district veterinary datasets based on biophysical constraints.
    
    Demonstrates:
    - Pillar 1 & 4 Security: Sandboxing and supply-chain defense.
    - Context Engineering: Providing structured data for downstream reasoning.
    """
    def __init__(self, user_role: str):
        self.user_role = user_role
        self.authorized_roles = ["vet_lab_staff", "epidemiologist", "administrator"]
        self.parameter_registry = ENVIRONMENTAL_PARAMETER_REGISTRY

    def _is_authorized(self) -> bool:
        """Verifies if the current user session has permission to access sensitive records."""
        return self.user_role in self.authorized_roles

    def ingest_veterinary_records(self, file_path: str) -> pd.DataFrame:
        """
        Loads and validates raw veterinary clinical records from CSV.
        Enforces RBAC on sensitive health data.
        """
        if not self._is_authorized():
            raise PermissionError(
                f"Security Violation: User role '{self.user_role}' is not authorized "
                "to access raw veterinary clinical records."
            )
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Veterinary records file not found at: {file_path}")
            
        df = pd.read_csv(file_path)
        
        # Enforce strict schema validation
        required_cols = [
            "district", "region", "disease_name", "species", 
            "active_cases", "population", "deaths", "year", 
            "latitude", "longitude"
        ]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Ingestion Schema Error: Missing required column '{col}' in veterinary database.")
        
        # Data type alignment and sanity cleaning
        df["active_cases"] = df["active_cases"].fillna(0).astype(int)
        df["population"] = df["population"].astype(int)
        df["deaths"] = df["deaths"].fillna(0).astype(int)
        df["latitude"] = df["latitude"].astype(float)
        df["longitude"] = df["longitude"].astype(float)
        
        return df

    def ingest_climate_data(self, file_path: str) -> pd.DataFrame:
        """
        Loads and validates satellite climate layers or weather station data.
        Applies automated boundary clipping to 18 biophysical factors.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Climate layers file not found at: {file_path}")
            
        df = pd.read_csv(file_path)
        
        # Verify geographical identifiers
        if "district" not in df.columns or "region" not in df.columns:
            raise ValueError("Ingestion Error: Climate dataset must contain 'district' and 'region' identifiers.")
            
        return self._validate_and_clip_parameters(df)

    def _validate_and_clip_parameters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Scans input climate dataframe and clamps parameters that exceed 
        logical biophysical boundaries to prevent sensor noise from biasing the model.
        """
        validated_df = df.copy()
        
        # Iterate through columns matching our 18 registered parameters
        for parameter, metadata in self.parameter_registry.items():
            if parameter in validated_df.columns:
                min_val, max_val = metadata["valid_range"]
                
                # Identify entries out of physical boundaries
                # e.g. Clamping Relative Humidity to 100% or NDVI to 1.0
                out_of_bounds_count = ((validated_df[parameter] < min_val) | 
                                      (validated_df[parameter] > max_val)).sum()
                
                if out_of_bounds_count > 0:
                    print(
                        f"[INGESTION LOG] Parameter '{parameter}': Found {out_of_bounds_count} "
                        f"anomalous entries exceeding logical range {metadata['valid_range']}. "
                        "Applying physical boundary clipping."
                    )
                    # Clamp anomalous values to the physical range defined in registry
                    validated_df[parameter] = validated_df[parameter].clip(lower=min_val, upper=max_val)
                    
        return validated_df
