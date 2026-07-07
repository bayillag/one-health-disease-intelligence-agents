# src/utils/disease_profiles.py

from typing import Dict, Any, List

"""
Master Pathogen Registry for One Health Disease Intelligence.
Defines biological boundaries, host species, and environmental triggers 
for 19 priority livestock diseases in the East African context.
"""

DISEASE_PATHOGEN_REGISTRY: Dict[str, Dict[str, Any]] = {
    "African Horse Sickness": {
        "acronym": "AHS",
        "primary_hosts": ["equine"],
        "zoonotic": False,
        "climate_triggers": ["temperature", "relative_humidity", "precipitation"],
        "risk_parameters": {"temp_min": 15.0, "humidity_min": 60.0, "notes": "Midge-borne; favored by hot, damp weather and marshy zones."}
    },
    "Anthrax": {
        "acronym": "Anth",
        "primary_hosts": ["cattle", "sheep", "goat", "camel", "equine"],
        "zoonotic": True,
        "climate_triggers": ["temperature", "precipitation", "soil_moisture"],
        "risk_parameters": {"notes": "Spore-former; outbreaks often follow long dry periods ended by heavy torrential rain."}
    },
    "Babesiosis": {
        "acronym": "Bab",
        "primary_hosts": ["cattle", "sheep", "goat"],
        "zoonotic": False,
        "climate_triggers": ["temperature", "relative_humidity", "ndvi"],
        "risk_parameters": {"temp_min": 20.0, "humidity_min": 60.0, "notes": "Tick-borne transmission; favored by humid, vegetated environments."}
    },
    "Blackleg / Black Quarter": {
        "acronym": "BQ",
        "primary_hosts": ["cattle", "sheep"],
        "zoonotic": False,
        "climate_triggers": ["soil_moisture", "precipitation"],
        "risk_parameters": {"notes": "Spore transmission from soil; risk rises during rainy seasons or when soil is excavated."}
    },
    "Contagious Bovine Pleuro-Pneumonia": {
        "acronym": "CBPP",
        "primary_hosts": ["cattle"],
        "zoonotic": False,
        "climate_triggers": ["temperature"],
        "risk_parameters": {"notes": "Direct contact transmission; climate indirectly drives transmission via herd clustering."}
    },
    "Contagious Caprine Pleuro-Pneumonia": {
        "acronym": "CCPP",
        "primary_hosts": ["goat"],
        "zoonotic": False,
        "climate_triggers": ["temperature", "relative_humidity"],
        "risk_parameters": {"temp_range": (15.0, 30.0), "notes": "High stocking density favors direct spread."}
    },
    "Fasciolosis": {
        "acronym": "Fasc",
        "primary_hosts": ["sheep", "goat", "cattle"],
        "zoonotic": True,
        "climate_triggers": ["precipitation", "soil_moisture", "wetness"],
        "risk_parameters": {"wet_days_min": 10.0, "notes": "Requires snail intermediate host in flooded pastures or marshlands."}
    },
    "Foot and Mouth Disease": {
        "acronym": "FMD",
        "primary_hosts": ["cattle", "pig", "sheep", "goat"],
        "zoonotic": False,
        "climate_triggers": ["temperature", "relative_humidity", "wind_speed"],
        "risk_parameters": {"temp_max": 28.0, "humidity_min": 60.0, "notes": "Aerosol spread is highly favored by high humidity."}
    },
    "Haemorrhagic Septicaemia": {
        "acronym": "HS",
        "primary_hosts": ["cattle"],
        "zoonotic": False,
        "climate_triggers": ["precipitation", "relative_humidity"],
        "risk_parameters": {"notes": "Directly associated with high-humidity and heavy rainy seasons."}
    },
    "Heartwater": {
        "acronym": "HW",
        "primary_hosts": ["cattle", "sheep", "goat"],
        "zoonotic": False,
        "climate_triggers": ["temperature", "relative_humidity", "ndvi"],
        "risk_parameters": {"notes": "Transmitted by Amblyomma ticks; favored by brush-covered warm savannah habitats."}
    },
    "Highly Pathogenic Avian Influenza": {
        "acronym": "HPAI",
        "primary_hosts": ["poultry"],
        "zoonotic": True,
        "climate_triggers": ["temperature", "precipitation", "cloud_cover"],
        "risk_parameters": {"notes": "Favored by cold, damp conditions and proximity to migratory waterfowl."}
    },
    "Lumpy Skin Disease": {
        "acronym": "LSD",
        "primary_hosts": ["cattle"],
        "zoonotic": False,
        "climate_triggers": ["temperature", "precipitation", "relative_humidity"],
        "risk_parameters": {"temp_min": 18.0, "humidity_min": 55.0, "notes": "Biting fly vectors proliferate during rainy, warm, and humid seasons."}
    },
    "Peste des Petits Ruminants": {
        "acronym": "PPR",
        "primary_hosts": ["sheep", "goat"],
        "zoonotic": False,
        "climate_triggers": ["temperature", "relative_humidity"],
        "risk_parameters": {"humidity_min": 10.0, "humidity_max": 45.0, "notes": "Dry, cold winds favor transmission."}
    },
    "Pneumonic Pasteurellosis": {
        "acronym": "PP",
        "primary_hosts": ["sheep", "goat"],
        "zoonotic": False,
        "climate_triggers": ["temperature", "precipitation"],
        "risk_parameters": {"notes": "Highly correlated with stress from sudden cold rains and temperature drops."}
    },
    "Rabies": {
        "acronym": "Rab",
        "primary_hosts": ["canine", "cattle", "sheep", "goat"],
        "zoonotic": True,
        "climate_triggers": ["temperature"],
        "risk_parameters": {"notes": "Transmitted via saliva/bites; constant threat with seasonal wildlife movement trends."}
    },
    "Rift Valley Fever": {
        "acronym": "RVF",
        "primary_hosts": ["sheep", "goat", "cattle", "camel"],
        "zoonotic": True,
        "climate_triggers": ["precipitation", "ndvi", "pet"],
        "risk_parameters": {"precip_min_30_days": 150.0, "ndvi_min": 0.55, "notes": "Abnormal rainfall spikes leading to flooding favor vector hatches."}
    },
    "Sheep Pox and Goat Pox": {
        "acronym": "SGP",
        "primary_hosts": ["sheep", "goat"],
        "zoonotic": False,
        "climate_triggers": ["temperature"],
        "risk_parameters": {"notes": "Increases in cool, dry transition seasons."}
    },
    "Theileriosis": {
        "acronym": "Theil",
        "primary_hosts": ["cattle"],
        "zoonotic": False,
        "climate_triggers": ["temperature", "relative_humidity", "ndvi"],
        "risk_parameters": {"temp_min": 18.0, "humidity_min": 55.0, "notes": "Tick vector transmission; thrives in warm, highly vegetated zones."}
    },
    "Trypanosomosis": {
        "acronym": "Tryp",
        "primary_hosts": ["cattle", "camel", "equine"],
        "zoonotic": False,
        "climate_triggers": ["relative_humidity", "ndvi", "lai"],
        "risk_parameters": {"humidity_min": 55.0, "ndvi_min": 0.45, "notes": "Tsetse vector requires humid riverine forests or bushy woodlands."}
    }
}
