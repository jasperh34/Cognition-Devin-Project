import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
ORG_ID = os.getenv("ORG_ID")
BASE_URL = "https://api.devin.ai/v3"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

class DevinCallClient:

    #Includes safety checks for key and org_id which should be stored privately in .env
    def __init__(self):
        if not API_KEY:
            raise RuntimeError("Missing API Key")
        if not ORG_ID:
            raise RuntimeError("Missing Devin Org Id")

        self.org_id = ORG_ID
        self.headers = HEADERS


    #Returns JSON from API request. 
    def request(self, method, path, **kwargs):
        url = f"{BASE_URL}{path}"
        r = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)

        if not r.ok:
            raise RuntimeError(f"Devin API error {r.status_code}: {r.text}")

        return r.json()


    #Calls request() with method = POST for creating session
    def create_session(self, prompt, title=None, tags=None, max_acu_limit=5):
        payload = {"prompt": prompt, "title": title, "tags": tags or [], "max_acu_limit": max_acu_limit}
        return self.request("POST", f"/organizations/{self.org_id}/sessions",json=payload)


    #Calls request() with method = GET for getting session information
    def get_session(self, session_id):
        return self.request("GET", f"/organizations/{self.org_id}/sessions/{session_id}")


    #Calls request() with method = GET for listing session messages
    def list_messages(self, session_id):
        return self.request("GET", f"/organizations/{self.org_id}/sessions/{session_id}/messages")
    
