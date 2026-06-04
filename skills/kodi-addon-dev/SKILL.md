---
name: kodi-addon-dev
description: Specialized guide for Kodi-specific APIs (xbmc, xbmcplugin), addon.xml schemas, and cross-version compatibility (Matrix/Nexus/Omega). Use when developing or refactoring Kodi addons, updating metadata, or handling Kodi-specific lifecycle events.
---

# Kodi Addon Development

This skill provides guidance for working with Kodi's Python API and addon structure.

## Core Modules

Kodi provides several internal modules. In this project, we use `kodi_six` to ensure compatibility between Python 2 (legacy) and Python 3 (Matrix+).

- `xbmc`: Core functions (logging, playback, built-ins).
- `xbmcaddon`: Addon settings and metadata.
- `xbmcgui`: UI elements (ListItems, Dialogs, Progress bars).
- `xbmcplugin`: Plugin-specific functions (adding directory items, resolving URLs).
- `xbmcvfs`: Virtual File System (file operations, path translation).

## Common Patterns

### Initializing an Addon
```python
from kodi_six import xbmcaddon
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
settings_val = addon.getSetting('my_setting')
```

### Logging
Always use the project's `kodilog` utility in `utils.py` for consistent formatting.
```python
from resources.lib.utils import kodilog
kodilog("Something happened", xbmc.LOGINFO)
```

### Adding Directory Items
Used to build the folder structure in Kodi.
```python
import sys
from kodi_six import xbmcgui, xbmcplugin
handle = int(sys.argv[1])
li = xbmcgui.ListItem("Video Title")
li.setArt({'thumb': 'http://image.url'})
# For Kodi 19+, use VideoInfoTag
if hasattr(li, 'getVideoInfoTag'):
    li.getVideoInfoTag().setTitle("Video Title")
else:
    li.setInfo('video', {'title': "Video Title"})

url = "plugin://plugin.video.cumination/?mode=Play&url=..."
xbmcplugin.addDirectoryItem(handle, url, li, isFolder=False)
```

## addon.xml Schema

Key attributes in `addon.xml`:
- `id`: Unique identifier (e.g., `plugin.video.cumination`).
- `version`: Semantic version. Must be bumped for updates.
- `provides`: Usually `video` for this project.
- `library`: The main entry point script (usually `default.py`).

## Compatibility (Matrix / Nexus / Omega)

- **Python 3**: All current Kodi versions (19, 20, 21) use Python 3.
- **Strings**: Use `six.ensure_str` or `six.ensure_text` when handling text from APIs.
- **Paths**: Use `xbmcvfs.translatePath` for local paths.

## Dispatcher Pattern
This project uses a custom `URL_Dispatcher` for routing requests.
```python
from resources.lib.url_dispatcher import URL_Dispatcher
url_dispatcher = URL_Dispatcher()

@url_dispatcher.register('MyMode')
def my_function(params):
    # params is a dict of query arguments
    pass
```
