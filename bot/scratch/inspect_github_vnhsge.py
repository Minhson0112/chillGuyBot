import urllib.request
import json

url = "https://raw.githubusercontent.com/Xdao85/VNHSGE/main/Dataset/VNHSGE-V/JSON%20format/eval/Biology/MET_Bio_IE_2019.json"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print(f"Total questions in History: {len(data)}")
        if data:
            print("First question sample:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
