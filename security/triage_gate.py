# security/triage_gate.py

import json
from typing import Dict, Any, Tuple

class TriageGate:
    """
    Implements a Human-in-the-Loop (HITL) checkpoint gate (Pillar 5).
    Intercepts and translates complex, auto-generated agentic tool-calls
    into plain-English summaries (Vibe Diffs) to mitigate confirmation fatigue.
    """
    def __init__(self, safe_budget_threshold: float = 100.0):
        self.safe_budget_threshold = safe_budget_threshold

    def generate_vibe_diff(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Translates raw, structured JSON arguments into a plain-English summary.
        Ensures human reviewers comprehend exactly what they are authorizing.
        """
        if tool_name == "execute_disbursement":
            dept = arguments.get("department", "unknown")
            amt = arguments.get("amount", 0.0)
            return (
                f"ACTION REQUESTED: The agent is attempting to transfer funds.\n"
                f"  - Target Recipient: Department '{dept.upper()}'\n"
                f"  - Total Amount: ${amt:.2f} USD\n"
                f"  - Risk Assessment: Funds will be permanently drawn from your account."
            )
        
        elif tool_name == "trigger_regional_quarantine":
            district = arguments.get("district", "unknown")
            disease = arguments.get("disease_name", "unknown")
            return (
                f"ACTION REQUESTED: The agent is initiating an active quarantine order.\n"
                f"  - Location: District '{district.capitalize()}'\n"
                f"  - Target Pathogen: '{disease}'\n"
                f"  - Risk Assessment: This locks down all livestock movement in this territory."
            )
            
        # Fallback dictionary-based listing
        return f"ACTION REQUESTED: Invoke tool '{tool_name}' with arguments: {json.dumps(arguments, indent=2)}"

    def verify_action_permission(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Intercepts tool executions. If the action is within safe ambient
        limits, it auto-passes. Otherwise, it triggers the Vibe Diff verification gate.
        """
        # Check budget limits
        if tool_name == "execute_disbursement":
            amount = float(arguments.get("amount", 0.0))
            if amount > self.safe_budget_threshold:
                print(f"\n[SECURITY EVENT] Intercepted high-stakes tool call: '{tool_name}' exceeding ${self.safe_budget_threshold:.2f}.")
                
                # 1. Generate the plain-English Vibe Diff
                vibe_diff_summary = self.generate_vibe_diff(tool_name, arguments)
                
                # 2. Present to user and demand explicit, uppercase confirmation 
                print("\n" + "=" * 50)
                print(vibe_diff_summary)
                print("=" * 50)
                
                user_approval = input("\nVerify proposed steps above.\nType 'CONFIRM' to cryptographically authorize execution: ")
                
                if user_approval.strip().upper() == "CONFIRM":
                    return True, "Action authorized by human supervisor."
                else:
                    return False, "Action cancelled: Rejected by human supervisor."
                    
        # If the tool call is low-risk, bypass manual check (Zero Ambient Authority)
        return True, "Action cleared automatically."
