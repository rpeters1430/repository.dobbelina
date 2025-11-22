def test_tokyomotion_module_loads():
    # Ensure the new site module is importable in the BeautifulSoup-based stack
    from resources.lib.sites import tokyomotion

    assert tokyomotion.site.name == 'tokyomotion'
