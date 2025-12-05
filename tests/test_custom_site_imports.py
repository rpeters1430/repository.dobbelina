import sys
import types


def test_custom_site_import_failure_reports(monkeypatch):
    sys.modules.setdefault('requests', types.SimpleNamespace())
    sys.modules.setdefault('resources.lib.sites', types.ModuleType('resources.lib.sites'))
    xbmcgui = sys.modules.get('kodi_six.xbmcgui')
    if xbmcgui and not hasattr(xbmcgui.Dialog, 'yesno'):
        setattr(xbmcgui.Dialog, 'yesno', lambda *args, **kwargs: True)
    import default as plugin_default

    plugin_default.addon.setSetting('custom_sites', 'true')

    disabled_modules = []
    logged_messages = []
    textboxes = []

    fake_favorites = types.SimpleNamespace(
        enabled_custom_sites=lambda: ['custom.bad', 'custom.good'],
        disable_custom_site_by_module=lambda module: disabled_modules.append(module),
        get_custom_site_title_by_module=lambda module: 'Title {0}'.format(module),
    )

    class _Dialog:
        def ok(self, *args, **kwargs):
            pass

        def yesno(self, *args, **kwargs):
            return True

    def fake_import(module_name):
        if module_name == 'custom.bad':
            error = ModuleNotFoundError("No module named 'missing_dependency'")
            error.name = 'missing_dependency'
            raise error
        return object()

    monkeypatch.setattr(plugin_default, 'favorites', fake_favorites)
    monkeypatch.setattr(plugin_default, 'dialog', _Dialog())
    monkeypatch.setattr(plugin_default.importlib, 'import_module', fake_import)
    monkeypatch.setattr(plugin_default.utils, 'kodilog', lambda message, level=None: logged_messages.append(message))
    monkeypatch.setattr(plugin_default.utils, 'textBox', lambda heading, body: textboxes.append((heading, body)))

    results = plugin_default.load_custom_sites()

    assert [entry['module'] for entry in results['loaded']] == ['custom.good']
    assert disabled_modules == ['custom.bad']
    assert any('missing_dependency' in body for _, body in textboxes)
    assert any('custom.bad' in log for log in logged_messages)


def test_custom_sites_health_display(monkeypatch):
    import default as plugin_default

    enabled_sites = [
        'custom.good',
        'custom.other',
        'custom.bad',
        'custom.dep',
        'custom.untried',
    ]
    plugin_default.custom_site_import_results['loaded'] = [
        {'module': 'custom.other'},
        {'module': 'custom.good'},
    ]
    plugin_default.custom_site_import_results['failed'] = [
        {'module': 'custom.dep', 'dependency': None, 'title': None},
        {'module': 'custom.bad', 'dependency': 'missing_dependency', 'title': 'Title custom.bad'},
    ]

    textboxes = []

    fake_favorites = types.SimpleNamespace(
        enabled_custom_sites=lambda: enabled_sites,
        get_custom_site_title_by_module=lambda module: 'Title {0}'.format(module),
    )

    monkeypatch.setattr(plugin_default, 'favorites', fake_favorites)
    monkeypatch.setattr(plugin_default.utils, 'textBox', lambda heading, body: textboxes.append((heading, body)))

    plugin_default.custom_sites_health()

    assert textboxes
    heading, body = textboxes[0]
    assert heading == 'Custom site health'
    assert body.split('[CR]') == [
        '[B]Loaded custom sites[/B]',
        '• Title custom.good',
        '• Title custom.other',
        '[B]Failed to load[/B]',
        '• Title custom.bad (missing_dependency)',
        '• Title custom.dep (import error)',
        '[B]Not attempted[/B]',
        '• Title custom.untried',
    ]
