import requests
import time

def test_api():
    base_url = "http://localhost:8000/api"
    
    print("Testing /simulator/start...")
    try:
        start = time.time()
        res = requests.post(f"{base_url}/simulator/start", json={})
        print(f"Status: {res.status_code}")
        print(f"Time: {time.time() - start:.2f}s")
        print(f"Response: {res.text[:500]}") # First 500 chars
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
