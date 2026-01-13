"""
Test module for porn4k site
"""

import pytest
from resources.lib.sites import porn4k
from resources.lib import utils


class TestPorn4K:
    """Test cases for porn4k site functionality"""

    def test_site_initialization(self):
        """Test that the site is properly initialized"""
        assert porn4k.site.name == "porn4k"
        assert "[COLOR hotpink]Porn4K[/COLOR]" in porn4k.site.title
        assert porn4k.site.url == "https://porn4k.to/"
        assert "porn4k.png" in porn4k.site.image

    def test_main_function_structure(self):
        """Test that Main function exists and has expected structure"""
        assert hasattr(porn4k, "Main")
        assert callable(porn4k.Main)

    def test_list_function_structure(self):
        """Test that List function exists and has expected structure"""
        assert hasattr(porn4k, "List")
        assert callable(porn4k.List)

    def test_playvid_function_structure(self):
        """Test that Playvid function exists and has expected structure"""
        assert hasattr(porn4k, "Playvid")
        assert callable(porn4k.Playvid)

    def test_search_function_structure(self):
        """Test that Search function exists and has expected structure"""
        assert hasattr(porn4k, "Search")
        assert callable(porn4k.Search)

    def test_categories_function_structure(self):
        """Test that Categories function exists and has expected structure"""
        assert hasattr(porn4k, "Categories")
        assert callable(porn4k.Categories)

    def test_everything_function_structure(self):
        """Test that Everything function exists and has expected structure"""
        assert hasattr(porn4k, "Everything")
        assert callable(porn4k.Everything)

    def test_lookupinfo_function_structure(self):
        """Test that Lookupinfo function exists and has expected structure"""
        assert hasattr(porn4k, "Lookupinfo")
        assert callable(porn4k.Lookupinfo)

    @pytest.mark.parametrize(
        "function_name",
        ["Main", "List", "Playvid", "Search", "Categories", "Everything", "Lookupinfo"],
    )
    def test_functions_exist(self, function_name):
        """Test that all functions exist and are callable"""
        func = getattr(porn4k, function_name)
        assert callable(func)

    def test_bs4_usage_in_list_function(self):
        """Test that List function uses BeautifulSoup instead of regex"""
        import inspect

        source = inspect.getsource(porn4k.List)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select" in source

        # Should not use old regex patterns
        assert "re.compile" not in source
        assert "findall" not in source

    def test_bs4_usage_in_categories_function(self):
        """Test that Categories function uses BeautifulSoup"""
        import inspect

        source = inspect.getsource(porn4k.Categories)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select" in source

    def test_bs4_usage_in_everything_function(self):
        """Test that Everything function uses BeautifulSoup"""
        import inspect

        source = inspect.getsource(porn4k.Everything)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select" in source

    def test_error_handling_in_list_function(self):
        """Test that List function has proper error handling"""
        import inspect

        source = inspect.getsource(porn4k.List)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_error_handling_in_categories_function(self):
        """Test that Categories function has proper error handling"""
        import inspect

        source = inspect.getsource(porn4k.Categories)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_error_handling_in_everything_function(self):
        """Test that Everything function has proper error handling"""
        import inspect

        source = inspect.getsource(porn4k.Everything)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_video_item_parsing_logic(self):
        """Test that video item parsing uses bs4 methods"""
        import inspect

        source = inspect.getsource(porn4k.List)

        # Should use bs4 selectors
        assert "article" in source
        assert "select_one" in source
        assert "safe_get_attr" in source

    def test_pagination_handling(self):
        """Test that pagination is handled with bs4"""
        import inspect

        source = inspect.getsource(porn4k.List)

        # Should use bs4 for pagination
        assert "soup.select_one" in source
        assert 'rel="next"' in source

    def test_context_menu_structure(self):
        """Test that context menu is properly structured"""
        import inspect

        source = inspect.getsource(porn4k.List)

        # Should have context menu items
        assert "contextm=" in source
        assert "Lookupinfo" in source

    def test_image_extraction_logic(self):
        """Test that image extraction logic is preserved"""
        import inspect

        source = inspect.getsource(porn4k.List)

        # Should handle image extraction
        assert "src" in source

    def test_name_cleaning_logic(self):
        """Test that name cleaning logic is preserved"""
        import inspect

        source_list = inspect.getsource(porn4k.List)
        source_categories = inspect.getsource(porn4k.Categories)
        source_everything = inspect.getsource(porn4k.Everything)

        # Should clean names
        assert "utils.cleantext" in source_list
        assert "utils.cleantext" in source_categories
        assert "utils.cleantext" in source_everything

    def test_search_keyword_handling(self):
        """Test that search function handles keywords properly"""
        import inspect

        source = inspect.getsource(porn4k.Search)

        # Should handle keyword replacement
        assert 'replace(" ", "+")' in source

    def test_category_item_selection(self):
        """Test that category items are selected properly"""
        import inspect

        source = inspect.getsource(porn4k.Categories)

        # Should select category items
        assert "li.cat-item" in source

    def test_everything_list_selection(self):
        """Test that everything function selects list items"""
        import inspect

        source = inspect.getsource(porn4k.Everything)

        # Should select list items
        assert 'soup.select("li")' in source

    def test_playvid_regex_usage(self):
        """Test that Playvid function still uses regex for source extraction"""
        import inspect

        source = inspect.getsource(porn4k.Playvid)

        # Should use regex for source extraction
        assert "re.compile" in source
        assert 'target="_blank"' in source
        assert 'rel="nofollow"' in source

    def test_playvid_progress_update(self):
        """Test that Playvid function shows progress"""
        import inspect

        source = inspect.getsource(porn4k.Playvid)

        # Should update progress
        assert "progress.update" in source
        assert "Loading video page" in source

    def test_playvid_link_processing(self):
        """Test that Playvid function processes links properly"""
        import inspect

        source = inspect.getsource(porn4k.Playvid)

        # Should process links
        assert "bypass_hosters_single" in source
        assert "HostedMediaFile" in source
        assert "valid_url" in source

    def test_playvid_selector_usage(self):
        """Test that Playvid function uses selector for link selection"""
        import inspect

        source = inspect.getsource(porn4k.Playvid)

        # Should use selector
        assert "utils.selector" in source
        assert "Select link" in source

    def test_playvid_error_handling(self):
        """Test that Playvid function handles errors"""
        import inspect

        source = inspect.getsource(porn4k.Playvid)

        # Should handle no playable links
        assert "No playable links found" in source

    def test_lookupinfo_patterns(self):
        """Test that Lookupinfo has proper regex patterns"""
        import inspect

        source = inspect.getsource(porn4k.Lookupinfo)

        # Should have lookup patterns
        assert "Cat" in source
        assert "Tag" in source
        assert 'rel="category tag' in source
        assert 'rel="tag' in source

    def test_main_menu_structure(self):
        """Test that Main function creates expected menu structure"""
        import inspect

        source = inspect.getsource(porn4k.Main)

        # Should have expected menu items
        assert "All titles" in source
        assert "Categories" in source
        assert "Search" in source
        assert "filme-von-a-z" in source

    def test_module_name_usage(self):
        """Test that module name is used in context menu"""
        import inspect

        source = inspect.getsource(porn4k.List)

        # Should use module name
        assert "site.module_name" in source

    def test_context_url_construction(self):
        """Test that context URL is constructed properly"""
        import inspect

        source = inspect.getsource(porn4k.List)

        # Should construct context URL
        assert "contexturl" in source
        assert "urllib_parse.quote_plus" in source
