import requests
import re
import json
import html as htmlmod

def dump_platform_livewire():
    url = "https://archivebate.com/platform/Y2hhdHVyYmF0ZQ=="
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    
    wire_match = re.search(r'wire:initial-data="([^"]+)"', resp.text)
    wire_init_match = re.search(r'wire:init="([^"]+)"', resp.text)
    if wire_init_match:
        print(f"Wire Init: {wire_init_match.group(1)}")
    else:
        print("Wire Init not found")

if __name__ == "__main__":
    dump_platform_livewire()
