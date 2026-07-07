# src/agents/prediction_bulletin_engine.py

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class PredictionBulletinEngine:
    """
    Manages the indexing, archiving, and retrieval of published 
    Monthly Prediction Bulletin reports (2-month-ahead forecast files).
    
    Demonstrates:
    - Document Archiving: Managing a versioned library of agentic outputs.
    - Metadata Querying: Supporting UI-driven searches across the bulletin catalog.
    """
    def __init__(self):
        # Local mock database catalog of generated bulletin metadata.
        # In production, this would be backed by a database or a structured manifest.json.
        self.catalog: List[Dict[str, Any]] = [
            {
                "id": "rep_2026_06",
                "title": "June 2026 prediction report of August 2026 - Part 1",
                "publish_date": "2026-06-09",
                "forecast_target_month": "August 2026",
                "category": "Prediction",
                "is_latest": True,
                "file_path": "docs/bulletins/bulletin_2026_06.md"
            },
            {
                "id": "rep_2026_05",
                "title": "May 2026 prediction report of July 2026 - Part 1",
                "publish_date": "2026-05-08",
                "forecast_target_month": "July 2026",
                "category": "Prediction",
                "is_latest": False,
                "file_path": "docs/bulletins/bulletin_2026_05.md"
            },
            {
                "id": "rep_2026_04",
                "title": "April 2026 prediction report of June 2026 - Part 1",
                "publish_date": "2026-04-09",
                "forecast_target_month": "June 2026",
                "category": "Prediction",
                "is_latest": False,
                "file_path": "docs/bulletins/bulletin_2026_04.md"
            },
            {
                "id": "rep_2026_03",
                "title": "March 2026 prediction report of May 2026 - Part 1",
                "publish_date": "2026-03-20",
                "forecast_target_month": "May 2026",
                "category": "Prediction",
                "is_latest": False,
                "file_path": "docs/bulletins/bulletin_2026_03.md"
            }
        ]

    def add_new_report(self, report_metadata: Dict[str, Any]) -> None:
        """
        Appends a newly compiled bulletin to the active registry catalog.
        Automatically updates 'is_latest' flags.
        """
        # Set all existing reports to NOT latest
        for entry in self.catalog:
            entry["is_latest"] = False
            
        # Push new report to front of list
        report_metadata["is_latest"] = True
        self.catalog.insert(0, report_metadata)
        
        print(f"[CATALOG LOG] Indexed new report: {report_metadata['title']}")

    def query_bulletin_library(
        self, 
        search_query: Optional[str] = None, 
        year_filter: Optional[int] = None, 
        month_filter: Optional[str] = None, 
        category_filter: str = "All"
    ) -> List[Dict[str, Any]]:
        """
        Filters the bulletin catalog matching the dashboard library filters:
        - Free text search within report titles.
        - Target forecast year (e.g., 2026).
        - Target forecast month (e.g., 'August' or 'All Months').
        - Document categorization (e.g., 'Prediction' vs 'Validation').
        """
        filtered_list = self.catalog.copy()
        
        # 1. Filter: "Search reports..." text query
        if search_query and search_query.strip():
            q = search_query.strip().lower()
            filtered_list = [r for r in filtered_list if q in r["title"].lower()]
            
        # 2. Filter: Year selection (search within forecast target string)
        if year_filter:
            y_str = str(year_filter)
            filtered_list = [r for r in filtered_list if y_str in r["forecast_target_month"]]
            
        # 3. Filter: Month selection
        if month_filter and month_filter != "All Months":
            m_q = month_filter.strip().lower()
            filtered_list = [r for r in filtered_list if m_q in r["forecast_target_month"].lower()]
            
        # 4. Filter: Document type dropdown (e.g., 'Prediction' vs 'Validation')
        if category_filter != "All":
            c_q = category_filter.strip().lower()
            filtered_list = [r for r in filtered_list if r["category"].lower() == c_q]
            
        return filtered_list

    def get_latest_bulletin(self) -> Optional[Dict[str, Any]]:
        """Helper to quickly retrieve the most recently published forecast."""
        for r in self.catalog:
            if r.get("is_latest"):
                return r
        return self.catalog[0] if self.catalog else None

    def export_catalog_manifest(self, file_path: str) -> bool:
        """Saves the current catalog registry to a JSON file for the dashboard."""
        try:
            with open(file_path, "w") as f:
                json.dump(self.catalog, f, indent=2)
            return True
        except Exception as e:
            print(f"[CATALOG ERROR] Failed to export manifest: {e}")
            return False
