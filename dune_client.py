import requests
import time
from config import DUNE_API_KEY

class DuneClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.dune.com/api/v1"

    def get_query_results(self, query_id):
        # Trigger execution (for simplicity in v2 we assume we just want latest results)
        # Using the results endpoint directly
        url = f"{self.base_url}/query/{query_id}/results"
        headers = {"X-DUNE-API-KEY": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json().get('result', {}).get('rows', [])
            else:
                print(f"Dune API Error: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Dune Request Failed: {e}")
            return []

# Placeholder for Bribe Alpha Query (Votium Optimization)
# Query ID for Yield Basis or Votium could be added here
YIELD_BASIS_QUERY_ID = 3381618  # Example: Yield Basis metrics
