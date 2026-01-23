import requests
import time
import sys

URL = "http://localhost:8001/ask"

def wait_for_ai():
    print("Waiting for AI Engine to come online...")
    for i in range(15): # Wait up to 30 seconds
        try:
            # We send a dummy request to check connectivity
            # Note: The engine expects a POST with 'query'
            response = requests.post(URL, json={"query": "test", "k": 1}, timeout=60)
            if response.status_code == 200:
                print("\n[SUCCESS] AI Engine is online and responding!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f". (Status: {response.status_code})", end="", flush=True)
        except requests.exceptions.ConnectionError:
            print(".", end="", flush=True)
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
        
        time.sleep(2)
    
    print("\n[FAIL] AI Engine did not respond after 30 seconds.")
    return False

if __name__ == "__main__":
    if not wait_for_ai():
        sys.exit(1)
