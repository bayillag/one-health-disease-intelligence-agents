# One Health Disease Intelligence: Multi-Agent Spatiotemporal Forewarning and Epidemic Modeling for Zoonotic and High-Consequence Livestock Pathogens

### Subtitle: Bridging Climate Analytics and Veterinary Science via Secure Agentic Engineering
**Track:** Agents for Good  
**Primary Domain:** Southwest Ethiopian Rift Valley and Omo Basin (Monitored by the Jinka Regional Veterinary Laboratory)

---

## 1. Project Overview

In rural East Africa, pastoralist livelihoods and public health are continuously threatened by zoonotic and high-consequence livestock diseases. **OneHealth-Sentinel** is an autonomous multi-agent decision-support platform built on Google’s **Agent Development Kit (ADK)** and the **Model Context Protocol (MCP)**. 

The platform ingests **18 satellite-derived climatic and environmental parameters** (e.g., LST, NDVI, soil moisture), correlates them with local clinical records, and models the transmission dynamics ($R_0$) of **19 priority pathogens** (e.g., Anthrax, Rift Valley Fever, FMD). It automatically outputs spatiotemporal risk maps, active surveillance sampling plans, and plain-English summaries for field workers.

```
                  +-----------------------------------------+
                  |      INGESTION & VALIDATION ENGINE       |
                  | (Checks 18 biophysical range parameters)|
                  +-----------------------------------------+
                                       |
                                       v
                  +-----------------------------------------+
                  |       EPIDEMIOLOGICAL MODELING          |
                  | (Sigmoid scoring, R0, & FPC Sampling)   |
                  +-----------------------------------------+
                                       |
                                       v
                  +-----------------------------------------+
                  |         SECURE AGENTIC HARNESS          |
                  | (YAML Gating, JIT Downscoping, HITL)    |
                  +-----------------------------------------+
                                       |
                                       v
                  +-----------------------------------------+
                  |        INTERACTIVE R SHINY GUI          |
                  | (Value boxes, regional tables, charts)  |
                  +-----------------------------------------+
```

---

## 2. Key Course Concepts Demonstrated

### A. Multi-Agent Division of Labor (Google ADK)
The system is partitioned into three specialized, single-responsibility agents to prevent context rot and minimize attention dilution:
1.  **Data Ingestion Agent:** Authenticates incoming datasets, parses 18 biophysical parameters, and clips anomalous values exceeding hard physical boundaries.
2.  **Risk Analysis Agent:** Merges climate data with clinical records to evaluate spatiotemporal outbreak probabilities and compute mathematical $R_0$ values.
3.  **Communication Agent:** Generates technical Markdown bulletins, translates raw statistics into non-technical local summaries, and compiles GeoJSON FeatureCollection outputs for GIS mapping.

### B. Interoperable Tooling (Model Context Protocol)
The system features a fully compliant, stdio-based **MCP Server** (`src/agents/mcp_server.py`) that exposes active surveillance calculators (such as the Cochran sample size formula with Finite Population Correction) as standard, discoverable tools for any compliant LLM client, bypassing custom integration debt.

### C. Agent Skills & Progressive Disclosure (agentskills.io v0.9)
Rather than loading every operational instruction into a monolithic system prompt, the runtime implements **progressive disclosure**. The agent maintains lightweight metadata at startup and loads targeted, on-demand instructions (such as `bigquery_ingestion` or `forewarning_queries`) only when user query triggers match.

### D. Zero-Trust Security & Policy Server
To secure the execution loop against prompt injection and the *Confused Deputy* problem:
*   **Zero Ambient Authority:** The agent operates with JIT downscoped credentials scoped strictly to the execution task.
*   **Hybrid Policy Server:** Enforces structural gating (YAML-based tool access permissions) and semantic gating (Gemini-vetted input filtering).
*   **Vibe Diff Elicitation:** Intercepts high-stakes action tools to translate complex proposed steps into a plain-English summary, demanding explicit human-in-the-loop authorization.

one-health-disease-intelligence-agents/
│
├── README.md                                 # Complete project documentation & guide
├── requirements.txt                          # Python dependencies list
├── run_pipeline.py                           # Main automated execution run script
├── policies.yaml                             # Standard structural gating rules (Pillar 4)
├── .semgrep.yaml                             # Static security analysis rules (Pillar 6)
│
├── data/
│   ├── raw/                                  # Original source datasets
│   │   ├── veterinary_records.csv            # Raw district case histories (Ethiopia)
│   │   └── climate_layers.csv                # Raw satellite & meteorological measurements
│   │
│   └── processed/                            # Engineered datasets consumed by R Shiny
│       ├── cleaned_master_dataset.csv        # Normalized joined baseline table
│       └── risk_assessment_output.csv        # Evaluated risk, deltas, and R0 outcomes
│
├── specs/                                    # Spec-Driven Development files (SDD)
│   ├── user_service.md                       # Architectural specifications
│   └── surveillance_sampling.feature         # BDD Gherkin scenario definitions
│
├── security/                                 # Secure development harness modules
│   ├── check_dependencies.py                 # Dependency allowlist validator (SCA)
│   ├── firewall.py                           # LLM-based input prompt injection firewall
│   └── triage_gate.py                        # Human-in-the-loop Vibe Diff approval gate
│
├── notebooks/                                # Kaggle development notebooks
│   ├── 01_data_ingestion.ipynb               # Parameter range checking & ingestion validation
│   ├── 02_risk_analysis.ipynb                # Modeling and R0 analysis notebook
│   └── 03_agent_communication.ipynb          # Query workflows, advisories & GIS payloads
│
├── src/                                      # Core production codebase
│   ├── __init__.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── disease_profiles.py               # 19 Pathogen baseline biological characteristics
│   │   └── parameter_registry.py             # 18 Biophysical parameter range definitions
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── data_ingestion_agent.py           # Ingests, cleans, & validates climate boundaries
│   │   ├── risk_analysis_agent.py            # Outbreak probability and logistic scoring
│   │   ├── disease_informatics_engine.py      # Computes the 9 descriptive dashboard views
│   │   ├── analytics_suite.py                # Runs disease trends and spatial groupings
│   │   ├── epidemiological_modeling_engine.py # Implements NGM and basic reproduction (R0)
│   │   ├── epi_toolbox.py                    # Active sampling size design & RR/OR calculators
│   │   ├── dashboard_visualization_engine.py # Compiles GIS, Leaflet heatmaps, and JSON outputs
│   │   ├── forewarning_query_engine.py      # Implements multi-key spatial query workflows
│   │   ├── prediction_bulletin_engine.py     # Indexes, searches, and archives bulletins
│   │   └── mcp_server.py                     # Stdio-based JSON-RPC tool provider interface
│   │
│   └── dashboard/
│       └── app.R                             # Interactive R Shiny Web Application
│
├── tests/                                    # Automated unit testing suite
│   ├── __init__.py
│   ├── test_data_ingestion.py                # Tests boundary clipping of the 18 factors
│   ├── test_risk_analysis.py                 # Tests mathematical R0 calculations
│   └── test_communication.py                 # Tests query filtering and GeoJSON compilation
│
└── docs/                                     # Documentation, charts, and bulletins
    ├── architecture.png                      # Agent workflow diagram
    ├── risk_map_example.png                  # Sample geospatial map screenshot output
    ├── risk_map_example.json                  # Compiled GeoJSON spatial mapping asset
    └── bulletins/                            # Archive of completed prediction bulletins
        ├── bulletin_2026_06.md               # June 2026 forecast report
        └── bulletin_2026_05.md               # May 2026 forecast report
---

## 3. Operational Limitations & Reality Check

In keeping with professional and scientific rigor, the system is designed with a clear understanding of its empirical boundaries:
1.  **Assurance over Autonomy:** This multi-agent framework is engineered as a **decision-support tool** for veterinary officers and epidemiologists. High-stakes actions (such as initiating vaccination campaigns) require explicit human-in-the-loop authorization.
2.  **Managing Error Rates:** Under validation testing, our early-warning model exhibits a **10.76% false-negative rate** and a **3.94% false-positive rate**. By enforcing **Vibe Diff** summaries and the **Evaluation-Driven Development** suite, we keep the underlying biophysical calculations grounded and verifiable.
3.  **Glass Box Observability:** Traditional debugging practices fail when assessing stochastic, multi-turn AI reasoning loops. By instrumenting the execution environment with OpenTelemetry and tracing the **Vibe Trajectory**, we map exactly how a natural-language prompt translates into active tool invocations, ensuring full accountability.
