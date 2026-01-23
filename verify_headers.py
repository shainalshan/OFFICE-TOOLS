import requests

def verify_headers():
    url = "http://127.0.0.1:8000/background-changer/"
    try:
        print(f"Checking URL: {url}")
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        headers = response.headers
        coop = headers.get('Cross-Origin-Opener-Policy')
        coep = headers.get('Cross-Origin-Embedder-Policy')
        corp = headers.get('Cross-Origin-Resource-Policy')
        
        print("\n--- Security Headers ---")
        print(f"Cross-Origin-Opener-Policy: {coop}")
        print(f"Cross-Origin-Embedder-Policy: {coep}")
        print(f"Cross-Origin-Resource-Policy: {corp}")
        
        if coop == 'same-origin' and coep == 'require-corp':
            print("\nSUCCESS: Headers are correctly configured for Cross-Origin Isolation.")
        else:
            print("\nFAILURE: Missing or incorrect headers.")
            
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    verify_headers()
