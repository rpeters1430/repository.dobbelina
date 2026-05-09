import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = ROOT / "plugin.video.cumination"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PLUGIN_PATH) not in sys.path:
    sys.path.insert(0, str(PLUGIN_PATH))

def ensure_stubs():
    if "kodi_six" in sys.modules:
        return

    # xbmc core module
    xbmc = types.ModuleType("kodi_six.xbmc")
    xbmc.LOGDEBUG = 0
    xbmc.LOGINFO = 1
    xbmc.LOGNOTICE = 2
    xbmc.LOGWARNING = 3
    xbmc.LOGERROR = 4
    xbmc.log = lambda *args, **kwargs: print(f"KODI LOG: {args}")
    xbmc.executebuiltin = lambda *args, **kwargs: print(f"KODI EXECUTE: {args}")
    xbmc.getSkinDir = lambda: "skin.estuary"
    xbmc.getInfoLabel = lambda key: "19.0" if "BuildVersion" in key else ""
    xbmc.getInfoImage = lambda key: ""
    xbmc.getCondVisibility = lambda *args, **kwargs: False
    xbmc.sleep = lambda ms: None
    xbmc.executeJSONRPC = lambda *args, **kwargs: '{"result": {"version": {"major": 19}}}'
    xbmc.getSupportedMedia = lambda *args, **kwargs: '{"video": ["mp4", "mkv", "m3u8"]}'

    class _Player:
        def isPlaying(self): return False
        def stop(self): pass
    xbmc.Player = _Player

    # xbmcaddon module
    xbmcaddon = types.ModuleType("kodi_six.xbmcaddon")
    class _Addon:
        def __init__(self, addon_id="plugin.video.cumination"):
            self.addon_id = addon_id
        def getAddonInfo(self, key):
            if key == "path": return str(PLUGIN_PATH)
            if key == "profile": return str(ROOT / ".profile")
            if key == "version":
                if self.addon_id == "xbmc.addon": return "19.0.0"
                return "1.0.0"
            return ""
        def getSetting(self, key): return "0"
        def getLocalizedString(self, string_id): return str(string_id)
        def setSetting(self, key, value): pass
        def openSettings(self): pass
    xbmcaddon.Addon = _Addon

    # xbmcplugin module
    xbmcplugin = types.ModuleType("kodi_six.xbmcplugin")
    xbmcplugin.addDirectoryItem = lambda *args, **kwargs: True
    xbmcplugin.endOfDirectory = lambda *args, **kwargs: None
    xbmcplugin.setContent = lambda *args, **kwargs: None
    xbmcplugin.addSortMethod = lambda *args, **kwargs: None
    xbmcplugin.setResolvedUrl = lambda *args, **kwargs: None
    xbmcplugin.SORT_METHOD_TITLE = 10

    # xbmcgui module
    xbmcgui = types.ModuleType("kodi_six.xbmcgui")
    class _ListItem:
        def __init__(self, label=""): self.label = label
        def setInfo(self, *args, **kwargs): pass
        def setArt(self, *args, **kwargs): pass
        def addContextMenuItems(self, items, replaceItems=False): pass
        def addStreamInfo(self, *args, **kwargs): pass
        def setSubtitles(self, *args, **kwargs): pass
        def setProperty(self, *args, **kwargs): pass
        def setContentLookup(self, *args, **kwargs): pass
        def setPath(self, path): self.path = path
        def getVideoInfoTag(self):
            class Tag:
                def setMediaType(self, *args, **kwargs): pass
                def setTitle(self, *args, **kwargs): pass
            return Tag()
    class _Dialog:
        def notification(self, *args, **kwargs): print(f"KODI NOTIFY: {args}")
        def numeric(self, *args, **kwargs): return "1"
        def select(self, *args, **kwargs): return 0
        def ok(self, *args, **kwargs): return True
    class _DialogProgress:
        def create(self, *args, **kwargs): pass
        def update(self, *args, **kwargs): pass
        def close(self): pass
        def iscanceled(self): return False
    class _WindowXMLDialog:
        def __init__(self, *args, **kwargs): pass
        def show(self): pass
        def close(self): pass
    class _WindowDialog:
        def __init__(self, *args, **kwargs): pass
        def show(self): pass
        def close(self): pass
    xbmcgui.ListItem = _ListItem
    xbmcgui.Dialog = _Dialog
    xbmcgui.DialogProgress = _DialogProgress
    xbmcgui.WindowXMLDialog = _WindowXMLDialog
    xbmcgui.WindowDialog = _WindowDialog

    # xbmcvfs module
    xbmcvfs = types.ModuleType("kodi_six.xbmcvfs")
    def _translatePath(path):
        if path.startswith("special://temp/"):
            return path.replace("special://temp/", str(ROOT / "temp") + "/")
        if path.startswith("special://home/"):
            return path.replace("special://home/", str(ROOT) + "/")
        return path
    xbmcvfs.translatePath = _translatePath
    xbmcvfs.exists = lambda path: False
    xbmcvfs.mkdirs = lambda path: None
    xbmcvfs.makeLegalFilename = lambda path: path

    kodi_six = types.ModuleType("kodi_six")
    kodi_six.xbmc = xbmc
    kodi_six.xbmcaddon = xbmcaddon
    kodi_six.xbmcplugin = xbmcplugin
    kodi_six.xbmcgui = xbmcgui
    kodi_six.xbmcvfs = xbmcvfs

    sys.modules["kodi_six"] = kodi_six
    sys.modules["kodi_six.xbmc"] = xbmc
    sys.modules["kodi_six.xbmcaddon"] = xbmcaddon
    sys.modules["kodi_six.xbmcplugin"] = xbmcplugin
    sys.modules["kodi_six.xbmcgui"] = xbmcgui
    sys.modules["kodi_six.xbmcvfs"] = xbmcvfs
    sys.modules["xbmc"] = xbmc
    sys.modules["xbmcaddon"] = xbmcaddon
    sys.modules["xbmcplugin"] = xbmcplugin
    sys.modules["xbmcgui"] = xbmcgui
    sys.modules["xbmcvfs"] = xbmcvfs

    storage_module = types.ModuleType("StorageServer")
    class _StorageServer:
        def __init__(self, *args, **kwargs): pass
        def cacheFunction(self, *args, **kwargs):
            if args and callable(args[0]): return args[0](*args[1:])
            return None
        def get(self, *args, **kwargs): return None
        def set(self, *args, **kwargs): pass
    storage_module.StorageServer = _StorageServer
    sys.modules["StorageServer"] = storage_module

    # Set sys.argv
    sys.argv = ["plugin.video.cumination", "1", ""]

ensure_stubs()
