# security/check_dependencies.py

import os
import sys

# Approved enterprise registry baseline for the One Health workspace
APPROVED_REGISTRY = [
    "pandas",
    "numpy",
    "scikit-learn",
    "google-genai",
    "google-cloud-trace",
    "mcp",
    "jsonschema",
    "fastapi",
    "uvicorn",
    "requests",
    "semgrep",
    "folium",
    "jinja2"
]

def verify_dependencies(requirements_file_path: str) -> None:
    """
    Reads requirements.txt, cleans version constraints, and verifies
    each package against our vetted enterprise allowlist.
    """
    if not os.path.exists(requirements_file_path):
        print(f"[SECURITY ERROR] requirements.txt not found at: {requirements_file_path}")
        sys.exit(1)
        
    with open(requirements_file_path, "r") as f:
        lines = f.readlines()

    unvetted_packages = []
    
    for line in lines:
        cleaned_line = line.strip()
        # Skip comments and empty lines
        if not cleaned_line or cleaned_line.startswith("#"):
            continue
            
        # Parse package name by stripping version constraints
        # Handles '==', '>=', '<=', '>', '<'
        package_name = cleaned_line
        for op in ["==", ">=", "<=", ">", "<"]:
            if op in cleaned_line:
                package_name = cleaned_line.split(op)[0].strip()
                break
                
        package_name_lower = package_name.lower()
        
        if package_name_lower not in APPROVED_REGISTRY:
            unvetted_packages.append(package_name)

    if unvetted_packages:
        print("[SECURITY VIOLATION] Unvetted dependency packages detected:")
        for pkg in unvetted_packages:
            print(f"  - {pkg}")
        print("\nDeployment blocked. To prevent slopsquatting, use exclusively approved enterprise packages.")
        sys.exit(1)

    print("[SUCCESS] All packages verified against the vetted enterprise registry.")
    sys.exit(0)

if __name__ == "__main__":
    # Assumes run is executed from root directory containing requirements.txt
    verify_dependencies("requirements.txt")
