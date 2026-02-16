from resources.lib import sites


def test_removed_sites_not_in_auto_import_list():
    assert "luxuretv" not in sites.__all__
    assert "missav" not in sites.__all__
