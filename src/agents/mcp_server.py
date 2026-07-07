# src/agents/mcp_server.py

import asyncio
import json
import math
from typing import Dict, Any, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from utils.disease_profiles import DISEASE_PATHOGEN_REGISTRY

# Initialize the MCP Server for One Health Tools
server = Server("one-health-intelligence-tools")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Exposes the epidemiological toolset to the MCP client.
    Demonstrates 'Standardized Sockets' for agentic interoperability.
    """
    return [
        Tool(
            name="calculate_surveillance_sample_size",
            description=(
                "Calculates the minimum required sample size for active sero-surveillance "
                "using the Cochran formula with Finite Population Correction (FPC). "
                "Essential for designing statistically valid field testing plans."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "expected_prevalence": {
                        "type": "number", 
                        "description": "The expected disease prevalence in the herd (0.0 to 1.0)."
                    },
                    "precision": {
                        "type": "number", 
                        "description": "Desired absolute precision limit (e.g., 0.05 for +/- 5%)."
                    },
                    "population_size": {
                        "type": "integer", 
                        "description": "Total number of susceptible animals in the local herd (N)."
                    }
                },
                "required": ["expected_prevalence", "precision", "population_size"]
            }
        ),
        Tool(
            name="get_pathogen_profile",
            description=(
                "Retrieves the biological characteristics and environmental triggers "
                "for a specific priority livestock pathogen."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "disease_name": {
                        "type": "string",
                        "description": "The name of the disease (e.g., 'Anthrax', 'Rift Valley Fever')."
                    }
                },
                "required": ["disease_name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Executes tool logic based on the incoming JSON-RPC request from the client.
    """
    try:
        # --- TOOL 1: SURVEILLANCE SAMPLING CALCULATOR ---
        if name == "calculate_surveillance_sample_size":
            p = float(arguments["expected_prevalence"])
            d = float(arguments["precision"])
            N = int(arguments["population_size"])
            
            if not (0 < p < 1) or not (0 < d < 1):
                return [TextContent(type="text", text="Error: Prevalence and precision must be between 0 and 1.")]

            # 1. Base Cochran (Z=1.96 for 95% Confidence)
            n_raw = (1.96**2 * p * (1 - p)) / (d**2)
            
            # 2. Apply FPC (Slide 38)
            n_adj = n_raw / (1.0 + (n_raw / N))
            required_samples = int(math.ceil(n_adj))
            
            result = {
                "status": "success",
                "required_sample_size": required_samples,
                "sampling_fraction_pct": round((required_samples / N) * 100, 2),
                "methodology": "Cochran Formula with Finite Population Correction"
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # --- TOOL 2: PATHOGEN REGISTRY LOOKUP ---
        elif name == "get_pathogen_profile":
            disease = arguments["disease_name"]
            # Case-insensitive lookup in our static registry
            profile = next(
                (meta for name_key, meta in DISEASE_PATHOGEN_REGISTRY.items() 
                 if name_key.lower() == disease.lower()), 
                None
            )
            
            if not profile:
                return [TextContent(type="text", text=f"Error: Pathogen '{disease}' not found in registry.")]
            
            return [TextContent(type="text", text=json.dumps(profile, indent=2))]

        else:
            return [TextContent(type="text", text=f"Error: Tool '{name}' is not registered on this server.")]

    except Exception as e:
        return [TextContent(type="text", text=f"Execution Failed: {str(e)}")]

async def main():
    """
    Main entry point for the MCP server.
    Configures the stdio transport layer for local communication.
    """
    # Use standard input/output for local inter-process communication
    async with stdio_server() as (read, write):
        init_options = server.create_initialization_options()
        await server.run(read, write, init_options)

if __name__ == "__main__":
    # Start the async event loop
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
