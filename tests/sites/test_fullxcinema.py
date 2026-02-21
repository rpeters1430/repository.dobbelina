"""
Test module for fullxcinema site
"""

import pytest
from resources.lib.sites import fullxcinema


class TestFullXCinema:
    """Test cases for fullxcinema site functionality"""

    def test_site_initialization(self):
        """Test that the site is properly initialized"""
        assert fullxcinema.site.name == "fullxcinema"
        assert "[COLOR hotpink]fullxcinema[/COLOR]" in fullxcinema.site.title
        assert fullxcinema.site.url == "https://fullxcinema.com/"
        assert "fullxcinema.png" in fullxcinema.site.image

    def test_main_function_structure(self):
        """Test that Main function exists and has expected structure"""
        assert hasattr(fullxcinema, "Main")
        assert callable(fullxcinema.Main)

    def test_list_function_structure(self):
        """Test that List function exists and has expected structure"""
        assert hasattr(fullxcinema, "List")
        assert callable(fullxcinema.List)

    def test_play_function_structure(self):
        """Test that Play function exists and has expected structure"""
        assert hasattr(fullxcinema, "Play")
        assert callable(fullxcinema.Play)

    def test_search_function_structure(self):
        """Test that Search function exists and has expected structure"""
        assert hasattr(fullxcinema, "Search")
        assert callable(fullxcinema.Search)

    def test_cat_function_structure(self):
        """Test that Cat function exists and has expected structure"""
        assert hasattr(fullxcinema, "Cat")
        assert callable(fullxcinema.Cat)

    def test_goto_page_function_structure(self):
        """Test that GotoPage function exists and has expected structure"""
        assert hasattr(fullxcinema, "GotoPage")
        assert callable(fullxcinema.GotoPage)

    def test_lookupinfo_function_structure(self):
        """Test that Lookupinfo function exists and has expected structure"""
        assert hasattr(fullxcinema, "Lookupinfo")
        assert callable(fullxcinema.Lookupinfo)

    def test_related_function_structure(self):
        """Test that Related function exists and has expected structure"""
        assert hasattr(fullxcinema, "Related")
        assert callable(fullxcinema.Related)

    @pytest.mark.parametrize(
        "function_name",
        ["Main", "List", "Play", "Search", "Cat", "GotoPage", "Lookupinfo", "Related"],
    )
    def test_functions_exist(self, function_name):
        """Test that all functions exist and are callable"""
        func = getattr(fullxcinema, function_name)
        assert callable(func)

    def test_bs4_usage_in_list_function(self):
        """Test that List function uses BeautifulSoup instead of regex"""
        import inspect

        source = inspect.getsource(fullxcinema.List)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select" in source

        # Should not use old utils.videos_list
        assert "utils.videos_list" not in source
        assert "delimiter" not in source
        assert "re_videopage" not in source

    def test_bs4_usage_in_cat_function(self):
        """Test that Cat function uses BeautifulSoup"""
        import inspect

        source = inspect.getsource(fullxcinema.Cat)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select" in source

    def test_error_handling_in_list_function(self):
        """Test that List function has proper error handling"""
        import inspect

        source = inspect.getsource(fullxcinema.List)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_error_handling_in_cat_function(self):
        """Test that Cat function has proper error handling"""
        import inspect

        source = inspect.getsource(fullxcinema.Cat)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_video_item_parsing_logic(self):
        """Test that video item parsing uses bs4 methods"""
        import inspect

        source = inspect.getsource(fullxcinema.List)

        # Should use bs4 selectors
        assert "article[data-video-id]" in source
        assert "select_one" in source
        assert "safe_get_attr" in source
        assert "safe_get_text" in source

    def test_should_watch_splitting_logic(self):
        """Test that the SHOULD WATCH splitting logic is preserved"""
        import inspect

        source = inspect.getsource(fullxcinema.List)

        # Should split at SHOULD WATCH
        assert ">SHOULD WATCH<" in source
        assert 'split(">SHOULD WATCH<")' in source

    def test_pagination_handling(self):
        """Test that pagination is handled with bs4"""
        import inspect

        source = inspect.getsource(fullxcinema.List)

        # Should handle pagination
        assert "Next" in source
        assert ".current" in source
        assert "find_next" in source

    def test_context_menu_structure(self):
        """Test that context menu is properly structured"""
        import inspect

        source = inspect.getsource(fullxcinema.List)

        # Should have context menu items
        assert "contextm=" in source
        assert "Lookupinfo" in source
        assert "Related" in source

    def test_duration_extraction(self):
        """Test that duration extraction logic is preserved"""
        import inspect

        source = inspect.getsource(fullxcinema.List)

        # Should handle duration extraction
        assert "fa-clock-o" in source
        assert "duration_tag" in source

    def test_image_extraction_logic(self):
        """Test that image extraction logic is preserved"""
        import inspect

        source = inspect.getsource(fullxcinema.List)

        # Should handle image extraction
        assert "data-main-thumb" in source

    def test_category_section_splitting(self):
        """Test that category section splitting is preserved"""
        import inspect

        source = inspect.getsource(fullxcinema.Cat)

        # Should split to focus on tags section
        assert 'title">Tags<' in source
        assert "split('title\">Tags<')" in source

    def test_category_link_selection(self):
        """Test that category links are selected properly"""
        import inspect

        source = inspect.getsource(fullxcinema.Cat)

        # Should select links with aria-label
        assert "a[href][aria-label]" in source

    def test_search_keyword_handling(self):
        """Test that search function handles keywords properly"""
        import inspect

        source = inspect.getsource(fullxcinema.Search)

        # Should handle keyword replacement
        assert 'replace(" ", "%20")' in source

    def test_play_function_regex_usage(self):
        """Test that Play function still uses regex for video extraction"""
        import inspect

        source = inspect.getsource(fullxcinema.Play)

        # Should use regex for video source extraction
        assert "regex=" in source
        assert '<source src="([^"]+)"' in source

    def test_play_function_iframe_handling(self):
        """Test that Play function handles iframe extraction"""
        import inspect

        source = inspect.getsource(fullxcinema.Play)

        # Should handle iframe extraction
        assert 'player">' in source
        assert "<iframe src=" in source

    def test_goto_page_functionality(self):
        """Test that GotoPage function handles URL replacement"""
        import inspect

        source = inspect.getsource(fullxcinema.GotoPage)

        # Should handle page replacement
        assert 'replace("/page/{}"' in source
        assert "Out of range" in source

    def test_lookupinfo_patterns(self):
        """Test that Lookupinfo has proper regex patterns"""
        import inspect

        source = inspect.getsource(fullxcinema.Lookupinfo)

        # Should have lookup patterns
        assert "Actor" in source
        assert "Category" in source
        assert "Tag" in source
        assert "/actor/" in source
        assert "/category/" in source
        assert "/tag/" in source

    def test_related_function_redirect(self):
        """Test that Related function redirects to List"""
        import inspect

        source = inspect.getsource(fullxcinema.Related)

        # Should redirect to List
        assert "Container.Update" in source
        assert "fullxcinema.List" in source

    def test_main_menu_structure(self):
        """Test that Main function creates expected menu structure"""
        import inspect

        source = inspect.getsource(fullxcinema.Main)

        # Should have expected menu items
        assert "Categories" in source
        assert "Search" in source
        assert "?filter=latest" in source

    def test_name_cleaning_logic(self):
        """Test that name cleaning logic is preserved"""
        import inspect

        source_list = inspect.getsource(fullxcinema.List)
        source_cat = inspect.getsource(fullxcinema.Cat)

        # Should clean names
        assert "utils.cleantext" in source_list
        assert "utils.cleantext" in source_cat
