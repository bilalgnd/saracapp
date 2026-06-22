import requests

try:
    print("Fetching...")
    response = requests.get("https://api.github.com/repos/bilalgnd/saracapp/releases/latest", timeout=5)
    print("Status:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print("Tag:", data.get('tag_name'))
    else:
        print("Not 200")
except Exception as e:
    print("Exception:", e)
