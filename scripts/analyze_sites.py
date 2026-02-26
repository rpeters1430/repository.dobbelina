#!/usr/bin/env python3
"""Site Structure Analyzer for Cumination

Analyzes all site modules to understand:
- What functions are registered (Main, List, Playvid, Categories, Search, etc.)
- What the entry point is (default_mode=True)
- Whether it uses BeautifulSoup or regex
- What parameters each function expects
- Whether it's a webcam/live site

Outputs JSON reports for use in automated testing.
"""

# CRITICAL: Setup Kodi mocks BEFORE any other imports
import sys
from pathlib import Path

# Add plugin path to sys.path FIRST
ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = ROOT / "plugin.video.cumination"
SITES_DIR = PLUGIN_PATH / "resources" / "lib" / "sites"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PLUGIN_PATH))

# Set up sys.argv as Kodi would (required by many addons)
if len(sys.argv) < 3:
    sys.argv = ['plugin.video.cumination', '1', '']

# Setup Kodi mocks immediately
import types

# Create all mock modules
for mod_name in ['kodi_six', 'kodi_six.xbmc', 'kodi_six.xbmcaddon', 'kodi_six.xbmcplugin',
                 'kodi_six.xbmcgui', 'kodi_six.xbmcvfs', 'xbmc', 'xbmcaddon', 'xbmcplugin',
                 'xbmcgui', 'xbmcvfs', 'StorageServer', 'resolveurl', 'websocket']:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)

# Mock xbmcaddon.Addon
class _MockAddon:
    def __init__(self, addon_id=None):
        self.addon_id = addon_id or 'plugin.video.cumination'

    def getAddonInfo(self, key):
        if key == 'path':
            return str(PLUGIN_PATH)
        if key == 'profile':
            return str(ROOT / '.profile')
        if key == 'version':
            return '1.0.0'
        return ''

    def getSetting(self, key):
        return ''

    def setSetting(self, key, value):
        pass

    def getLocalizedString(self, string_id):
        return str(string_id)

sys.modules['xbmcaddon'].Addon = _MockAddon
sys.modules['kodi_six.xbmcaddon'].Addon = _MockAddon

# Mock essential xbmc functions
sys.modules['xbmc'].log = lambda *a, **k: None
sys.modules['kodi_six.xbmc'].log = lambda *a, **k: None
sys.modules['xbmc'].getInfoLabel = lambda key: '20.0' if 'BuildVersion' in key else ''
sys.modules['kodi_six.xbmc'].getInfoLabel = lambda key: '20.0' if 'BuildVersion' in key else ''
sys.modules['xbmc'].executebuiltin = lambda *a, **k: None
sys.modules['kodi_six.xbmc'].executebuiltin = lambda *a, **k: None
sys.modules['xbmc'].getSkinDir = lambda: 'skin.estuary'
sys.modules['kodi_six.xbmc'].getSkinDir = lambda: 'skin.estuary'
sys.modules['xbmc'].getCondVisibility = lambda *a, **k: False
sys.modules['kodi_six.xbmc'].getCondVisibility = lambda *a, **k: False

# Mock xbmcplugin functions
sys.modules['xbmcplugin'].addDirectoryItem = lambda *a, **k: True
sys.modules['xbmcplugin'].endOfDirectory = lambda *a, **k: None
sys.modules['xbmcplugin'].setContent = lambda *a, **k: None
sys.modules['xbmcplugin'].addSortMethod = lambda *a, **k: None
sys.modules['kodi_six.xbmcplugin'].addDirectoryItem = lambda *a, **k: True
sys.modules['kodi_six.xbmcplugin'].endOfDirectory = lambda *a, **k: None
sys.modules['kodi_six.xbmcplugin'].setContent = lambda *a, **k: None
sys.modules['kodi_six.xbmcplugin'].addSortMethod = lambda *a, **k: None

# Mock ListItem
class _MockListItem:
    def __init__(self, *a, **k):
        pass
    def setInfo(self, *a, **k):
        pass
    def setArt(self, *a, **k):
        pass
    def getVideoInfoTag(self):
        return type('VideoInfoTag', (), {'setMediaType': lambda *a, **k: None})()

sys.modules['xbmcgui'].ListItem = _MockListItem
sys.modules['kodi_six.xbmcgui'].ListItem = _MockListItem

# Mock xbmcvfs functions
sys.modules['xbmcvfs'].translatePath = lambda p: str(p).replace('special://profile', str(ROOT / '.profile'))
sys.modules['kodi_six.xbmcvfs'].translatePath = lambda p: str(p).replace('special://profile', str(ROOT / '.profile'))
sys.modules['xbmcvfs'].exists = lambda p: Path(str(p)).exists()
sys.modules['kodi_six.xbmcvfs'].exists = lambda p: Path(str(p)).exists()
sys.modules['xbmcvfs'].mkdirs = lambda p: Path(str(p)).mkdir(parents=True, exist_ok=True)
sys.modules['kodi_six.xbmcvfs'].mkdirs = lambda p: Path(str(p)).mkdir(parents=True, exist_ok=True)

# Mock StorageServer
class _MockStorage:
    def __init__(self, *args, **kwargs):
        pass
    def cacheFunction(self, fn, *args, **kwargs):
        return fn(*args, **kwargs)

sys.modules['StorageServer'].StorageServer = _MockStorage
import importlib
import inspect
import json
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Set


@dataclass
class FunctionInfo:
    """Information about a registered function"""
    name: str
    full_mode: str
    is_default: bool
    is_clean: bool
    parameters: List[str]
    required_params: List[str]
    optional_params: List[str]
    has_url_param: bool
    has_name_param: bool
    has_keyword_param: bool
    source_location: str


@dataclass
class SiteInfo:
    """Complete information about a site module"""
    name: str
    display_name: str
    base_url: str
    icon: str
    is_webcam: bool
    uses_beautifulsoup: bool
    uses_regex: bool
    uses_soup_spec: bool
    default_mode: str
    registered_functions: List[FunctionInfo]
    function_names: List[str]
    has_main: bool
    has_list: bool
    has_categories: bool
    has_search: bool
    has_play: bool
    source_file: str
    source_lines: int
    import_error: Optional[str] = None


def setup_kodi_mocks():
    """Kodi mocks are already set up at module level - this is a no-op"""
    pass


def analyze_source_code(file_path: Path) -> Dict[str, Any]:
    """Analyze source code using AST to detect patterns"""
    source = file_path.read_text(encoding='utf-8')

    uses_beautifulsoup = bool(
        re.search(r'\bparse_html\b|\bBeautifulSoup\b', source)
    )
    uses_regex = bool(
        re.search(r'\bre\.compile\b|\bre\.findall\b|\bre\.search\b', source)
    )
    uses_soup_spec = bool(
        re.search(r'\bSoupSiteSpec\b', source)
    )

    return {
        'uses_beautifulsoup': uses_beautifulsoup,
        'uses_regex': uses_regex,
        'uses_soup_spec': uses_soup_spec,
        'source_lines': len(source.splitlines()),
    }


def analyze_function(func: Any, site_name: str, mode_name: str) -> FunctionInfo:
    """Analyze a registered function"""
    try:
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())

        # Determine required vs optional
        required = []
        optional = []
        for param_name, param in sig.parameters.items():
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
            else:
                optional.append(param_name)

        # Get source location
        try:
            source_file = inspect.getsourcefile(func)
            source_lines = inspect.getsourcelines(func)
            location = f"{Path(source_file).name}:{source_lines[1]}"
        except:
            location = "unknown"

        return FunctionInfo(
            name=func.__name__,
            full_mode=mode_name,
            is_default=False,  # Will be updated later
            is_clean=False,    # Will be updated later
            parameters=params,
            required_params=required,
            optional_params=optional,
            has_url_param='url' in params,
            has_name_param='name' in params,
            has_keyword_param='keyword' in params,
            source_location=location,
        )
    except Exception as e:
        return None


def analyze_site(site_name: str) -> SiteInfo:
    """Analyze a single site module"""
    file_path = SITES_DIR / f"{site_name}.py"

    # Basic source analysis
    try:
        source_info = analyze_source_code(file_path)
    except Exception as e:
        return SiteInfo(
            name=site_name,
            display_name='',
            base_url='',
            icon='',
            is_webcam=False,
            uses_beautifulsoup=False,
            uses_regex=False,
            uses_soup_spec=False,
            default_mode='',
            registered_functions=[],
            function_names=[],
            has_main=False,
            has_list=False,
            has_categories=False,
            has_search=False,
            has_play=False,
            source_file=str(file_path),
            source_lines=0,
            import_error=f"Source analysis error: {type(e).__name__}: {str(e)}",
        )

    # Try to import the module
    try:
        module = importlib.import_module(f'resources.lib.sites.{site_name}')
    except Exception as e:
        return SiteInfo(
            name=site_name,
            display_name='',
            base_url='',
            icon='',
            is_webcam=False,
            uses_beautifulsoup=source_info['uses_beautifulsoup'],
            uses_regex=source_info['uses_regex'],
            uses_soup_spec=source_info['uses_soup_spec'],
            default_mode='',
            registered_functions=[],
            function_names=[],
            has_main=False,
            has_list=False,
            has_categories=False,
            has_search=False,
            has_play=False,
            source_file=str(file_path),
            source_lines=source_info['source_lines'],
            import_error=f"{type(e).__name__}: {str(e)}",
        )

    # Get site object
    site = getattr(module, 'site', None)
    if not site:
        return SiteInfo(
            name=site_name,
            display_name='',
            base_url='',
            icon='',
            is_webcam=False,
            uses_beautifulsoup=source_info['uses_beautifulsoup'],
            uses_regex=source_info['uses_regex'],
            uses_soup_spec=source_info['uses_soup_spec'],
            default_mode='',
            registered_functions=[],
            function_names=[],
            has_main=False,
            has_list=False,
            has_categories=False,
            has_search=False,
            has_play=False,
            source_file=str(file_path),
            source_lines=source_info['source_lines'],
            import_error="No 'site' object exported",
        )

    # Get site attributes
    display_name = getattr(site, 'get_clean_title', lambda: site_name)()
    base_url = getattr(site, 'url', '')
    icon = getattr(site, 'image', '')
    is_webcam = getattr(site, 'webcam', False)
    default_mode = getattr(site, 'default_mode', '')

    # Analyze registered functions
    from resources.lib.url_dispatcher import URL_Dispatcher

    registered_funcs = []
    func_registry = URL_Dispatcher.func_registry
    args_registry = URL_Dispatcher.args_registry
    kwargs_registry = URL_Dispatcher.kwargs_registry
    default_modes = URL_Dispatcher.default_modes
    clean_modes = URL_Dispatcher.clean_modes

    # Find all functions for this site
    site_modes = {k: v for k, v in func_registry.items() if k.startswith(f"{site_name}.")}

    for mode_name, func in site_modes.items():
        func_info = analyze_function(func, site_name, mode_name)
        if func_info:
            func_info.is_default = (mode_name in default_modes)
            func_info.is_clean = (mode_name in clean_modes)
            registered_funcs.append(func_info)

    # Detect function types
    func_names_lower = [f.name.lower() for f in registered_funcs]
    has_main = any('main' in name for name in func_names_lower) or bool(default_mode)
    has_list = any('list' in name for name in func_names_lower)
    has_categories = any('cat' in name or 'genre' in name for name in func_names_lower)
    has_search = any('search' in name for name in func_names_lower)
    has_play = any('play' in name for name in func_names_lower)

    return SiteInfo(
        name=site_name,
        display_name=display_name,
        base_url=base_url,
        icon=icon,
        is_webcam=is_webcam,
        uses_beautifulsoup=source_info['uses_beautifulsoup'],
        uses_regex=source_info['uses_regex'],
        uses_soup_spec=source_info['uses_soup_spec'],
        default_mode=default_mode,
        registered_functions=registered_funcs,
        function_names=[f.name for f in registered_funcs],
        has_main=has_main,
        has_list=has_list,
        has_categories=has_categories,
        has_search=has_search,
        has_play=has_play,
        source_file=str(file_path),
        source_lines=source_info['source_lines'],
    )


def discover_sites() -> List[str]:
    """Discover all site modules"""
    sites = []
    for file_path in sorted(SITES_DIR.glob('*.py')):
        name = file_path.stem
        if name not in {'__init__', 'soup_spec'}:
            sites.append(name)
    return sites


def generate_report(sites_info: List[SiteInfo]) -> Dict[str, Any]:
    """Generate comprehensive report"""
    total = len(sites_info)
    with_errors = [s for s in sites_info if s.import_error]
    successful = [s for s in sites_info if not s.import_error]

    beautifulsoup_sites = [s for s in successful if s.uses_beautifulsoup]
    regex_only_sites = [s for s in successful if s.uses_regex and not s.uses_beautifulsoup]
    soup_spec_sites = [s for s in successful if s.uses_soup_spec]
    webcam_sites = [s for s in successful if s.is_webcam]

    # Categorize by functionality
    with_main = [s for s in successful if s.has_main]
    with_list = [s for s in successful if s.has_list]
    with_categories = [s for s in successful if s.has_categories]
    with_search = [s for s in successful if s.has_search]
    with_play = [s for s in successful if s.has_play]

    # Missing critical functions
    missing_main = [s for s in successful if not s.has_main]
    missing_play = [s for s in successful if not s.has_play]

    return {
        'summary': {
            'total_sites': total,
            'successful_imports': len(successful),
            'import_errors': len(with_errors),
            'beautifulsoup_sites': len(beautifulsoup_sites),
            'regex_only_sites': len(regex_only_sites),
            'soup_spec_sites': len(soup_spec_sites),
            'webcam_sites': len(webcam_sites),
            'with_main': len(with_main),
            'with_list': len(with_list),
            'with_categories': len(with_categories),
            'with_search': len(with_search),
            'with_play': len(with_play),
            'missing_main': len(missing_main),
            'missing_play': len(missing_play),
        },
        'sites': [asdict(s) for s in sites_info],
        'errors': [
            {'name': s.name, 'error': s.import_error}
            for s in with_errors
        ],
        'missing_critical': {
            'missing_main': [s.name for s in missing_main],
            'missing_play': [s.name for s in missing_play],
        },
        'migration_status': {
            'beautifulsoup': [s.name for s in beautifulsoup_sites],
            'regex_only': [s.name for s in regex_only_sites],
            'soup_spec': [s.name for s in soup_spec_sites],
        },
        'webcam_sites': [s.name for s in webcam_sites],
    }


def main():
    print("Cumination Site Analyzer")
    print("=" * 60)
    print()

    # Discover sites
    print("Discovering sites...")
    site_names = discover_sites()
    print(f"Found {len(site_names)} sites")
    print()

    # Analyze each site
    print("Analyzing sites...")
    sites_info = []
    for i, name in enumerate(site_names, 1):
        print(f"  [{i:>3}/{len(site_names)}] {name:<30}", end='')
        info = analyze_site(name)
        sites_info.append(info)

        if info.import_error:
            print(f" [ERROR] {info.import_error[:50]}")
        else:
            funcs = len(info.registered_functions)
            bs = "BS" if info.uses_beautifulsoup else "  "
            wc = "WC" if info.is_webcam else "  "
            print(f" [OK] [{bs}] [{wc}] {funcs} functions")

    print()

    # Generate report
    print("Generating report...")
    report = generate_report(sites_info)

    # Save to file
    output_path = ROOT / 'results' / 'site_analysis.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    # Print summary
    print()
    print("Summary")
    print("=" * 60)
    print(f"Total sites:           {report['summary']['total_sites']}")
    print(f"Successful imports:    {report['summary']['successful_imports']}")
    print(f"Import errors:         {report['summary']['import_errors']}")
    print()
    print(f"BeautifulSoup sites:   {report['summary']['beautifulsoup_sites']}")
    print(f"Regex-only sites:      {report['summary']['regex_only_sites']}")
    print(f"SoupSiteSpec sites:    {report['summary']['soup_spec_sites']}")
    print(f"Webcam sites:          {report['summary']['webcam_sites']}")
    print()
    print(f"Sites with Main:       {report['summary']['with_main']}")
    print(f"Sites with List:       {report['summary']['with_list']}")
    print(f"Sites with Categories: {report['summary']['with_categories']}")
    print(f"Sites with Search:     {report['summary']['with_search']}")
    print(f"Sites with Play:       {report['summary']['with_play']}")
    print()

    if report['summary']['import_errors'] > 0:
        print("Sites with import errors:")
        for err in report['errors']:
            print(f"  - {err['name']}: {err['error']}")
        print()

    if report['summary']['missing_main'] > 0:
        print(f"Sites missing Main function ({report['summary']['missing_main']}):")
        print(f"  {', '.join(report['missing_critical']['missing_main'])}")
        print()

    if report['summary']['missing_play'] > 0:
        print(f"Sites missing Play function ({report['summary']['missing_play']}):")
        print(f"  {', '.join(report['missing_critical']['missing_play'])}")
        print()

    print(f"Report saved to: {output_path}")

    return 0 if report['summary']['import_errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
