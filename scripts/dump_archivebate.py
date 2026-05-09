import requests
import re
import json
import html as htmlmod

def dump_livewire():
    url = "https://archivebate.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    
    wire_match = re.search(r'wire:initial-data="([^"]+)"', resp.text)
    if wire_match:
        data = json.loads(htmlmod.unescape(wire_match.group(1)))
        print(json.dumps(data, indent=2))
    else:
        print("Not found")

if __name__ == "__main__":
    dump_livewire()
