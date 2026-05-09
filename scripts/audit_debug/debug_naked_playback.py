import sys
import os
import re
import json
import ssl
import time

# Disable SSL verification for debug script
ssl._create_default_https_context = ssl._create_unverified_context

# Add the project root and scripts directory to sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCRIPTS = os.path.join(ROOT, 'scripts')
sys.path.append(ROOT)
sys.path.append(SCRIPTS)

import stub_kodi
from resources.lib import utils

def test_naked_playback():
    print("Testing Naked.com Playback API...")
    
    # Using data for melissa-fumero (found in earlier step)
    mid = "997252"
    video_host = "video-gpu006-mojo-eu.vs3.com"
    
    timestamp = int(time.time() * 1000)
    
    # 1. Login room API
    login_url = f"https://www.naked.com/webservices/chat-room-interface.php?a=login_room&model_id={mid}&t={timestamp}"
    print(f"Requesting Login: {login_url}")
    try:
        login_data = utils._getHtml(login_url, "https://www.naked.com/")
        if login_data:
            print(f"Login Response: {login_data[:200]}...")
            data = json.loads(login_data)
            room_status = data.get("config", {}).get("room", {}).get("status")
            print(f"Room Status: {room_status}")
        else:
            print("Empty login response")
    except Exception as e:
        print(f"Login Error: {e}")

    # 2. Get stream URLs API - Try specific chat server
    chat_server = "chat008.vs3.com"
    stream_url = f"https://{chat_server}/chat/get-stream-urls.php?model_id={mid}&video_host={video_host}&t={timestamp}"
    print(f"\nRequesting Stream URLs: {stream_url}")
    try:
        stream_data = utils._getHtml(stream_url, "https://www.naked.com/")
        if stream_data:
            print(f"Stream Response: {stream_data[:200]}...")
            data = json.loads(stream_data)
            if data.get("data"):
                 hls = data["data"].get("hls")
                 if hls:
                     print(f"Found HLS stream: {hls[0].get('url')}")
                 else:
                     print("No HLS streams found")
            else:
                print(f"API Error: {data.get('error', 'Unknown error')}")
        else:
            print("Empty stream response")
    except Exception as e:
        print(f"Stream Error: {e}")

if __name__ == "__main__":
    test_naked_playback()
