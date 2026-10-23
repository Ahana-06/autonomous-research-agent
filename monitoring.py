import time
import pandas as pd
from datetime import datetime

class AgentMonitor:
    def __init__(self, log_file="agent_audit_logs.csv"):
        self.log_file = log_file
        self.initialize_log()

    def initialize_log(self):
        try:
            pd.read_csv(self.log_file)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["timestamp", "query", "tokens", "estimated_cost_usd", "safety_status"])
            df.to_csv(self.log_file, index=False)

    def log_interaction(self, query: str, tokens: int = 150):
        # 1. Safety Check / Guardrail
        blocked_keywords = ["hack", "exploit", "malware", "illegal"]
        safety_status = "Safe"
        for kw in blocked_keywords:
            if kw in query.lower():
                safety_status = "Flagged / Blocked"

        # 2. Prompt Cost Calculation (e.g., approx $0.0002 per 1k tokens)
        cost = (tokens / 1000.0) * 0.002

        # 3. Save to Log CSV
        new_row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "tokens": tokens,
            "estimated_cost_usd": round(cost, 5),
            "safety_status": safety_status
        }
        
        df = pd.read_csv(self.log_file)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.log_file, index=False)
        return safety_status
    