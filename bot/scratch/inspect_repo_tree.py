import urllib.request
import json

url = "https://api.github.com/repos/Xdao85/VNHSGE/git/trees/main?recursive=1"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        tree = json.loads(response.read().decode('utf-8'))['tree']
        json_files = []
        for item in tree:
            path = item['path']
            if path.startswith("Dataset/VNHSGE-V/JSON format/") and path.endswith(".json"):
                json_files.append(path)
        
        print(f"Found {len(json_files)} JSON files:")
        for p in json_files[:20]:
            print(f"  - {p}")
        if len(json_files) > 20:
            print(f"  ... and {len(json_files) - 20} more.")
except Exception as e:
    print(f"Error: {e}")
