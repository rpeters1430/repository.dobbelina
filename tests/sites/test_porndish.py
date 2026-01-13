"""
Test module for porndish site
"""

import pytest
from resources.lib.sites import porndish
from resources.lib import utils


class TestPornDish:
    """Test cases for porndish site functionality"""

    def test_site_initialization(self):
        """Test that the site is properly initialized"""
        assert porndish.site.name == "porndish"
        assert "[COLOR hotpink]Porndish[/COLOR]" in porndish.site.title
        assert porndish.site.url == "https://www.porndish.com/"
        assert "porndish.png" in porndish.site.image

    def test_main_function_structure(self):
        """Test that Main function exists and has expected structure"""
        assert hasattr(porndish, "Main")
        assert callable(porndish.Main)

    def test_list_function_structure(self):
        """Test that List function exists and has expected structure"""
        assert hasattr(porndish, "List")
        assert callable(porndish.List)

    def test_playvid_function_structure(self):
        """Test that Playvid function exists and has expected structure"""
        assert hasattr(porndish, "Playvid")
        assert callable(porndish.Playvid)

    @pytest.mark.parametrize("function_name", ["Main", "List", "Playvid"])
    def test_functions_exist(self, function_name):
        """Test that all functions exist and are callable"""
        func = getattr(porndish, function_name)
        assert callable(func)

    def test_bs4_usage_in_list_function(self):
        """Test that List function uses BeautifulSoup instead of regex"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should use BeautifulSoup
        assert "utils.parse_html" in source
        assert "soup.select_one" in source

        # Should not use old regex patterns
        assert "re.compile" not in source
        assert "findall" not in source

    def test_error_handling_in_list_function(self):
        """Test that List function has proper error handling"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should have try-except blocks
        assert "try:" in source
        assert "except" in source
        assert "utils.kodilog" in source

    def test_video_item_parsing_logic(self):
        """Test that video item parsing uses bs4 methods"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should use bs4 selectors
        assert "find_all" in source
        assert "safe_get_attr" in source

    def test_pagination_handling(self):
        """Test that pagination is handled with bs4"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should use bs4 for pagination
        assert "soup.select_one" in source
        assert 'rel="next"' in source

    def test_first_page_handling(self):
        """Test that first page is handled differently"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should handle first page differently
        assert "/page/1/" in source
        assert "New Porn Videos" in source

    def test_section_splitting_logic(self):
        """Test that section splitting logic is preserved"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should split at sections
        assert "More Porn Videos" in source
        assert "g1-pagination-end" in source

    def test_text_search_logic(self):
        """Test that text search logic is implemented"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should search for text content
        assert "find_all(text=lambda text:" in source
        assert "New Porn Videos" in source
        assert "More Porn Videos" in source

    def test_image_extraction_logic(self):
        """Test that image extraction logic is preserved"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should handle image extraction
        assert "data-src" in source
        assert 'find("img")' in source

    def test_name_cleaning_logic(self):
        """Test that name cleaning logic is preserved"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should clean names
        assert "utils.cleantext" in source

    def test_element_traversal_logic(self):
        """Test that element traversal logic is implemented"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should traverse elements
        assert "find_next" in source
        assert "parent" in source

    def test_video_link_selection(self):
        """Test that video links are selected properly"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should select video links
        assert "a[title][href]" in source

    def test_playvid_implementation(self):
        """Test that Playvid uses site link playback"""
        import inspect

        source = inspect.getsource(porndish.Playvid)

        # Should use site link playback
        assert "play_from_site_link" in source
        assert "direct_regex=None" in source

    def test_main_function_calls_list(self):
        """Test that Main function calls List with page 1"""
        import inspect

        source = inspect.getsource(porndish.Main)

        # Should call List with page 1
        assert "page/1/" in source

    def test_section_boundary_detection(self):
        """Test that section boundary detection is implemented"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should detect section boundaries
        assert "get_text()" in source
        assert "get(" in source
        assert "class" in source

    def test_conditional_section_parsing(self):
        """Test that conditional section parsing is implemented"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should have conditional parsing
        assert "if new_videos_section:" in source
        assert "if more_videos_section:" in source

    def test_fallback_image_search(self):
        """Test that fallback image search is implemented"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should have fallback image search
        assert 'find_next("img")' in source

    def test_data_validation(self):
        """Test that data validation is implemented"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should validate data
        assert "if name and videopage:" in source

    def test_pagination_class_detection(self):
        """Test that pagination class detection is implemented"""
        import inspect

        source = inspect.getsource(porndish.List)

        # Should detect pagination by class
        assert "'pagination'" in source
