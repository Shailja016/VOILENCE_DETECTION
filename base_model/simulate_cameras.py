import requests
import time
import os

BACKEND_URL = "http://localhost:4000/api/cameras"
SCAN_INTERVAL = 30 # seconds

def get_cameras():
    try:
        response = requests.get(BACKEND_URL)
        if response.status_code == 200:
            return response.json().get('cameras', [])
    except Exception as e:
        print(f"Error fetching cameras: {e}")
    return []

def trigger_scan(camera_id):
    try:
        print(f"Triggering scan for {camera_id}...")
        response = requests.post(f"{BACKEND_URL}/{camera_id}/scan")
        if response.status_code == 201:
            result = response.json()
            violence = result['incident']['violence']
            risk = result['ai_analysis']['risk_level']
            print(f"  Result: Violence={violence}, Risk={risk}")
        else:
            print(f"  Scan failed: {response.status_code}")
    except Exception as e:
        print(f"  Error triggering scan: {e}")

def run_simulation():
    print("Starting Multi-Camera Simulation...")
    while True:
        cameras = get_cameras()
        if not cameras:
            print("No cameras found. Waiting...")
        else:
            for cam in cameras:
                trigger_scan(cam['camera_id'])
                time.sleep(2) # Small gap between cameras
        
        print(f"Waiting {SCAN_INTERVAL} seconds for next cycle...")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    run_simulation()
