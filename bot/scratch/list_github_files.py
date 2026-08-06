import urllib.request
import json

url = "https://api.github.com/repos/Xdao85/VNHSGE/contents/Dataset/VNHSGE-V/JSON%20format/train"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        files = json.loads(response.read().decode('utf-8'))
        for f in files:
            print(f"{f['name']} ({f['type']})")
except Exception as e:
    print(f"Error: {e}")
