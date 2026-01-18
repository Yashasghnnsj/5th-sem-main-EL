import requests

def test_analyze_image():
    url = "http://127.0.0.1:5000/api/analyze-image"
    files = {'image': ('test.jpg', b'dummy content', 'image/jpeg')}
    
    print(f"Testing {url}...")
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error Response: {response.text}")
        else:
            print(f"Success Response: {response.json()}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_analyze_image()
