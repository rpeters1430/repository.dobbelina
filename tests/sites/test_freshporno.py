"""
Test module for freshporno site
"""

import pytest
from resources.lib.sites import freshporno


class TestFreshPorno:
    """Test cases for freshporno site functionality"""

    def test_site_initialization(self):
        """Test that the site is properly initialized"""
        assert freshporno.site.name == "freshporno"
        assert "[COLOR hotpink]FreshPorno[/COLOR]" in freshporno.site.title
        assert freshporno.site.url == "https://freshporno.org/"
        assert "freshporno.png" in freshporno.site.image

    def test_main_function_structure(self):
        """Test that Main function exists and has expected structure"""
        assert hasattr(freshporno, "Main")
        assert callable(freshporno.Main)

    def test_list_function_structure(self):
        """Test that List function exists and has expected structure"""
        assert hasattr(freshporno, "List")
        assert callable(freshporno.List)

    def test_playvid_function_structure(self):
        """Test that Playvid function exists and has expected structure"""
        assert hasattr(freshporno, "Playvid")
        assert callable(freshporno.Playvid)

    def test_search_function_structure(self):
        """Test that Search function exists and has expected structure"""
        assert hasattr(freshporno, "Search")
        assert callable(freshporno.Search)

    def test_tags_function_structure(self):
        """Test that Tags function exists and has expected structure"""
        assert hasattr(freshporno, "Tags")
        assert callable(freshporno.Tags)

    def test_channels_function_structure(self):
        """Test that Channels function exists and has expected structure"""
        assert hasattr(freshporno, "Channels")
        assert callable(freshporno.Channels)

    def test_models_function_structure(self):
        """Test that Models function exists and has expected structure"""
        assert hasattr(freshporno, "Models")
        assert callable(freshporno.Models)

    def test_lookupinfo_function_structure(self):
        """Test that Lookupinfo function exists and has expected structure"""
        assert hasattr(freshporno, "Lookupinfo")
        assert callable(freshporno.Lookupinfo)

    @pytest.mark.parametrize(
        "function_name",
        [
            "Main",
            "List",
            "Playvid",
            "Search",
            "Tags",
            "Channels",
            "Models",
            "Lookupinfo",
        ],
    )
    def test_functions_exist(self, function_name):
        """Test that all functions exist and are callable"""
        func = getattr(freshporno, function_name)
        assert callable(func)

    def test_bs4_usage_in_list_function(self):
        """Test that List function uses BeautifulSoup or soup_videos_list"""
        import inspect

        source = inspect.getsource(freshporno.List)

        # Should use BeautifulSoup or helper
        assert "utils.parse_html" in source
        assert "soup.select" in source or "utils.soup_videos_list" in source

        # Should not use old regex patterns
        assert "re.compile" not in source
        assert "thumbs-inner" in source  # It's okay to have it in the spec now

    def test_bs4_usage_in_tags_function(self):
        """Test that Tags function uses BeautifulSoup"""
        import inspect

        source = inspect.getsource(freshporno.Tags)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select" in source
        assert "fa-tag" in source

    def test_bs4_usage_in_channels_function(self):
        """Test that Channels function uses BeautifulSoup"""
        import inspect

        source = inspect.getsource(freshporno.Channels)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select_one" in source
        assert "content-wrapper" in source

    def test_bs4_usage_in_models_function(self):
        """Test that Models function uses BeautifulSoup"""
        import inspect

        source = inspect.getsource(freshporno.Models)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select_one" in source
        assert "content-wrapper" in source

    def test_error_handling_in_list_function(self):
        """Test that List function has proper error handling (via helper)"""
        import inspect

        source = inspect.getsource(freshporno.List)

        # Should have try-except blocks or use helper which has them
        assert "try:" in source or "utils.soup_videos_list" in source

    def test_error_handling_in_tags_function(self):
        """Test that Tags function has proper error handling"""
        import inspect

        source = inspect.getsource(freshporno.Tags)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_error_handling_in_channels_function(self):
        """Test that Channels function has proper error handling"""
        import inspect

        source = inspect.getsource(freshporno.Channels)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_error_handling_in_models_function(self):
        """Test that Models function has proper error handling"""
        import inspect

        source = inspect.getsource(freshporno.Models)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_video_item_parsing_logic(self):
        """Test that video item parsing uses bs4 methods or helper"""
        import inspect

        source = inspect.getsource(freshporno.List)

        # Should use bs4 selectors or helper
        assert ".thumbs-inner" in source
        assert "select_one" in source or "utils.soup_videos_list" in source

    def test_pagination_handling_in_list(self):
        """Test that pagination is handled with bs4 or helper"""
        import inspect

        source = inspect.getsource(freshporno.List)

        # Should use bs4 for pagination or helper
        assert "soup.select_one" in source or "utils.soup_videos_list" in source
        assert "a.next" in source

    def test_pagination_handling_in_models(self):
        """Test that pagination is handled with bs4 in Models function"""
        import inspect

        source = inspect.getsource(freshporno.Models)

        # Should use bs4 for pagination
        assert "soup.select_one" in source
        assert "a.next" in source

    def test_context_menu_structure(self):
        """Test that context menu is properly structured"""
        import inspect

        source = inspect.getsource(freshporno.List)

        # Should have context menu items
        assert "contextm=" in source
        assert "Lookupinfo" in source

    def test_kvs_decoder_usage(self):
        """Test that Playvid function uses KVS decoder"""
        import inspect

        source = inspect.getsource(freshporno.Playvid)

        # Should import and use KVS decoder
        assert "kvs_decode" in source
        assert "license_code" in source
        assert "video_url:" in source

    def test_video_source_patterns(self):
        """Test that Playvid function has multiple video source patterns"""
        import inspect

        source = inspect.getsource(freshporno.Playvid)

        # Should have multiple patterns for video sources
        assert "video_url:" in source
        assert "video_alt_url:" in source
        assert "video_alt_url2:" in source

    def test_quality_selection_logic(self):
        """Test that quality selection logic is present"""
        import inspect

        source = inspect.getsource(freshporno.Playvid)

        # Should have quality selection
        assert "utils.selector" in source
        assert "Select quality" in source

    def test_fallback_download_button(self):
        """Test that there's fallback to download button when no sources found"""
        import inspect

        source = inspect.getsource(freshporno.Playvid)

        # Should have fallback
        assert "btn-download" in source
        assert "No Videos found" in source

    def test_tag_icon_detection(self):
        """Test that tag function properly detects tag icons"""
        import inspect

        source = inspect.getsource(freshporno.Tags)

        # Should look for tag icons
        assert "i.fa-tag" in source

    def test_channel_model_count_extraction(self):
        """Test that channels and models functions extract video counts"""
        import inspect

        source_channels = inspect.getsource(freshporno.Channels)
        source_models = inspect.getsource(freshporno.Models)

        # Should extract video counts
        assert "video_match" in source_channels
        assert "video_match" in source_models
        assert r"(\d+)" in source_channels
        assert r"(\d+)" in source_models

    def test_image_extraction_logic(self):
        """Test that image extraction logic is preserved"""
        import inspect

        source_channels = inspect.getsource(freshporno.Channels)
        source_models = inspect.getsource(freshporno.Models)

        # Should handle image extraction
        assert "data-original" in source_channels
        assert "data-original" in source_models
        assert "no image" in source_channels
        assert "no image" in source_models

    def test_name_formatting(self):
        """Test that names are properly formatted with video counts"""
        import inspect

        source_channels = inspect.getsource(freshporno.Channels)
        source_models = inspect.getsource(freshporno.Models)

        # Should format names with video counts
        assert ".format(" in source_channels
        assert ".format(" in source_models

    def test_search_keyword_handling(self):
        """Test that search function handles keywords properly"""
        import inspect

        source = inspect.getsource(freshporno.Search)

        # Should handle keyword replacement
        assert 'replace(" ", "-")' in source
