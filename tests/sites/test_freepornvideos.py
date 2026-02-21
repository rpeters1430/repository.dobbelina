"""
Test module for freepornvideos site
"""

import pytest
from resources.lib.sites import freepornvideos


class TestFreePornVideos:
    """Test cases for freepornvideos site functionality"""

    def test_site_initialization(self):
        """Test that the site is properly initialized"""
        assert freepornvideos.site.name == "freepornvideos"
        assert "[COLOR hotpink]FreePornVideos[/COLOR]" in freepornvideos.site.title
        assert freepornvideos.site.url == "https://www.freepornvideos.xxx/"
        assert "freepornvideos.png" in freepornvideos.site.image

    def test_main_function_structure(self):
        """Test that Main function exists and has expected structure"""
        # This is a basic smoke test to ensure the function exists
        assert hasattr(freepornvideos, "Main")
        assert callable(freepornvideos.Main)

    def test_list_function_structure(self):
        """Test that List function exists and has expected structure"""
        assert hasattr(freepornvideos, "List")
        assert callable(freepornvideos.List)

    def test_playvid_function_structure(self):
        """Test that Playvid function exists and has expected structure"""
        assert hasattr(freepornvideos, "Playvid")
        assert callable(freepornvideos.Playvid)

    def test_search_function_structure(self):
        """Test that Search function exists and has expected structure"""
        assert hasattr(freepornvideos, "Search")
        assert callable(freepornvideos.Search)

    def test_lookupinfo_function_structure(self):
        """Test that Lookupinfo function exists and has expected structure"""
        assert hasattr(freepornvideos, "Lookupinfo")
        assert callable(freepornvideos.Lookupinfo)

    def test_related_function_structure(self):
        """Test that Related function exists and has expected structure"""
        assert hasattr(freepornvideos, "Related")
        assert callable(freepornvideos.Related)

    def test_gotopage_function_structure(self):
        """Test that GotoPage function exists and has expected structure"""
        assert hasattr(freepornvideos, "GotoPage")
        assert callable(freepornvideos.GotoPage)

    @pytest.mark.parametrize(
        "function_name",
        ["Main", "List", "Playvid", "Search", "Lookupinfo", "Related", "GotoPage"],
    )
    def test_functions_exist(self, function_name):
        """Test that all functions exist and are callable"""
        func = getattr(freepornvideos, function_name)
        assert callable(func)

    def test_bs4_usage_in_list_function(self):
        """Test that List function uses BeautifulSoup instead of regex"""
        import inspect

        source = inspect.getsource(freepornvideos.List)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select" in source

        # Should not use the old regex-based utils.videos_list
        assert "utils.videos_list" not in source
        assert "delimiter" not in source
        assert "re_videopage" not in source

    def test_error_handling_in_list_function(self):
        """Test that List function has proper error handling"""
        import inspect

        source = inspect.getsource(freepornvideos.List)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_video_item_parsing_logic(self):
        """Test that video item parsing uses bs4 methods"""
        import inspect

        source = inspect.getsource(freepornvideos.List)

        # Should use bs4 selectors
        assert "div.item" in source
        assert "select_one" in source
        assert "safe_get_attr" in source
        assert "safe_get_text" in source

    def test_pagination_handling(self):
        """Test that pagination is handled with bs4"""
        import inspect

        source = inspect.getsource(freepornvideos.List)

        # Should use bs4 for pagination
        assert "soup.select_one" in source
        assert "page-current" in source or "page" in source

    def test_context_menu_structure(self):
        """Test that context menu is properly structured"""
        import inspect

        source = inspect.getsource(freepornvideos.List)

        # Should have context menu items
        assert "contextm=" in source
        assert "Lookupinfo" in source
        assert "Related" in source

    def test_video_playback_patterns(self):
        """Test that Playvid function has multiple source extraction patterns"""
        import inspect

        source = inspect.getsource(freepornvideos.Playvid)

        # Should have multiple regex patterns for video source extraction
        assert "Pattern 1:" in source
        assert "Pattern 2:" in source
        assert "Pattern 3:" in source
        assert "Pattern 4:" in source

    def test_quality_selection_logic(self):
        """Test that quality selection logic is present"""
        import inspect

        source = inspect.getsource(freepornvideos.Playvid)

        # Should have quality selection
        assert "utils.selector" in source
        assert "Select quality" in source

    def test_fallback_to_resolveurl(self):
        """Test that there's fallback to resolveurl when no sources found"""
        import inspect

        source = inspect.getsource(freepornvideos.Playvid)

        # Should have fallback
        assert "resolveurl" in source
        assert "No video sources found" in source
