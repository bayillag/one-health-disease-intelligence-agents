# tests/__init__.py

"""
Unit and Integration Test Suite for OneHealth-Sentinel.
Validates multi-agent reasoning, mathematical modeling, and security protocols.
"""

import os
import sys

# Ensure the 'src/' directory is in the system path so that test modules 
# can import agents and utilities using 'from agents...' syntax.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Shared Testing Constants
TEST_DATA_DIR = os.path.join(PROJECT_ROOT, "data/raw")
MOCK_VET_RECORDS = os.path.join(TEST_DATA_DIR, "veterinary_records.csv")
MOCK_CLIMATE_LAYERS = os.path.join(TEST_DATA_DIR, "climate_layers.csv")

# Metadata
__test_version__ = "1.0.0"
