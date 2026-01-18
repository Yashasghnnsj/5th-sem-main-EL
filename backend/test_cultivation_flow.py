import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def print_result(step, response):
    print(f"\n--- {step} ---")
    if response.status_code in [200, 201]:
        print("SUCCESS")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"FAILED ({response.status_code})")
        print(response.text)

def test_workflow():
    # 1. Start Cultivation
    print("\n[1] Starting Cultivation...")
    resp = requests.post(f"{BASE_URL}/cultivation/start", json={"start_date": "2024-06-01"})
    print_result("Start Cultivation", resp)
    if resp.status_code != 200: return

    # 2. Get Dashboard (Should be at Phase 1: Nursery)
    print("\n[2] Getting Dashboard (Phase 1)...")
    resp = requests.get(f"{BASE_URL}/cultivation/dashboard")
    print_result("Dashboard Phase 1", resp)

    # 3. Update to Next Phase
    print("\n[3] Updating to Phase 2...")
    resp = requests.post(f"{BASE_URL}/cultivation/update", json={"action": "next"})
    print_result("Update Phase", resp)

    # 4. Get Dashboard Again (Should be at Phase 2: Transplanting)
    print("\n[4] Getting Dashboard (Phase 2)...")
    resp = requests.get(f"{BASE_URL}/cultivation/dashboard")
    print_result("Dashboard Phase 2", resp)
    
    # 5. Get Full Static Lifecycle
    print("\n[5] Fetching Static Lifecycle...")
    resp = requests.get(f"{BASE_URL}/knowledge/paddy/lifecycle")
    print_result("Static Lifecycle", resp)

if __name__ == "__main__":
    test_workflow()
