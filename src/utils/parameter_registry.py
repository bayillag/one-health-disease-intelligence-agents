# src/utils/parameter_registry.py

from typing import Dict, Any

"""
Environmental Parameter Registry for One Health Disease Intelligence.
Defines biophysical boundaries, temporal intervals, resolutions, and units 
for 18 satellite-derived and meteorological parameters.
"""

ENVIRONMENTAL_PARAMETER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "relative_humidity": {
        "resolution_deg": 2.5,
        "interval": "1 Month",
        "units": "%",
        "valid_range": (0.0, 100.0)
    },
    "sea_level_pressure": {
        "resolution_deg": 2.5,
        "interval": "1 Month",
        "units": "Pa",
        "valid_range": (80000.0, 110000.0)
    },
    "cloud_cover": {
        "resolution_deg": 0.5,
        "interval": "1 Month",
        "units": "%",
        "valid_range": (0.0, 100.0)
    },
    "temperature": {
        "resolution_deg": 0.5,
        "interval": "1 Month",
        "units": "°C",
        "valid_range": (-50.0, 60.0)
    },
    "diurnal_temperature": {
        "resolution_deg": 0.5,
        "interval": "1 Month",
        "units": "°C",
        "valid_range": (0.0, 40.0)
    },
    "maximum_temperature": {
        "resolution_deg": 0.5,
        "interval": "1 Month",
        "units": "°C",
        "valid_range": (-50.0, 60.0)
    },
    "minimum_temperature": {
        "resolution_deg": 0.5,
        "interval": "1 Month",
        "units": "°C",
        "valid_range": (-60.0, 50.0)
    },
    "precipitation": {
        "resolution_deg": 0.5,
        "interval": "1 Month",
        "units": "mm",
        "valid_range": (0.0, 2000.0)
    },
    "soil_moisture": {
        "resolution_deg": 0.5,
        "interval": "1 Month",
        "units": "kg/m²",
        "valid_range": (0.0, 1000.0)
    },
    "vapour_pressure": {
        "resolution_deg": 0.5,
        "interval": "1 Month",
        "units": "hPa",
        "valid_range": (0.0, 100.0)
    },
    "wetness": {
        "resolution_deg": 0.5,
        "interval": "1 Month",
        "units": "Days",
        "valid_range": (0.0, 31.0)
    },
    "air_temperature": {
        "resolution_deg": 2.5,
        "interval": "1 Month",
        "units": "°C",
        "valid_range": (-50.0, 60.0)
    },
    "wind_speed": {
        "resolution_deg": 2.5,
        "interval": "1 Month",
        "units": "m/s",
        "valid_range": (0.0, 120.0)
    },
    "ndvi": {
        "resolution_deg": 0.0045,  # ~500m resolution
        "interval": "8 Days",
        "units": "Index",
        "valid_range": (-1.0, 1.0)
    },
    "lst": {
        "resolution_deg": 0.009,   # ~1km resolution
        "interval": "16 Days",
        "units": "°C",
        "valid_range": (-50.0, 80.0)
    },
    "evi": {
        "resolution_deg": 0.0045,
        "interval": "8 Days",
        "units": "Index",
        "valid_range": (-1.0, 1.0)
    },
    "pet": {
        "resolution_deg": 0.0045,
        "interval": "8 Days",
        "units": "kg/m²/8day",
        "valid_range": (0.0, 500.0)
    },
    "lai": {
        "resolution_deg": 0.0045,
        "interval": "8 Days",
        "units": "m²/m²",
        "valid_range": (0.0, 10.0)
    }
}
