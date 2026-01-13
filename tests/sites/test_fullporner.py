"""
Test module for fullporner site
"""

import pytest
from resources.lib.sites import fullporner
from resources.lib import utils


class TestFullPorner:
    """Test cases for fullporner site functionality"""

    def test_site_initialization(self):
        """Test that the site is properly initialized"""
        assert fullporner.site.name == "fullporner"
        assert "[COLOR hotpink]Fullporner[/COLOR]" in fullporner.site.title
        assert fullporner.site.url == "https://fullporner.org/"
        assert "fullporner.png" in fullporner.site.image

    def test_main_function_structure(self):
        """Test that Main function exists and has expected structure"""
        assert hasattr(fullporner, 'Main')
        assert callable(fullporner.Main)

    def test_list_function_structure(self):
        """Test that List function exists and has expected structure"""
        assert hasattr(fullporner, 'List')
        assert callable(fullporner.List)

    def test_playvid_function_structure(self):
        """Test that Playvid function exists and has expected structure"""
        assert hasattr(fullporner, 'Playvid')
        assert callable(fullporner.Playvid)

    def test_search_function_structure(self):
        """Test that Search function exists and has expected structure"""
        assert hasattr(fullporner, 'Search')
        assert callable(fullporner.Search)

    def test_categories_function_structure(self):
        """Test that Categories function exists and has expected structure"""
        assert hasattr(fullporner, 'Categories')
        assert callable(fullporner.Categories)

    def test_actors_function_structure(self):
        """Test that Actors function exists and has expected structure"""
        assert hasattr(fullporner, 'Actors')
        assert callable(fullporner.Actors)

    @pytest.mark.parametrize("function_name", [
        'Main', 'List', 'Playvid', 'Search', 'Categories', 'Actors'
    ])
    def test_functions_exist(self, function_name):
        """Test that all functions exist and are callable"""
        func = getattr(fullporner, function_name)
        assert callable(func)

    def test_bs4_usage_in_list_function(self):
        """Test that List function uses BeautifulSoup instead of regex"""
        import inspect
        source = inspect.getsource(fullporner.List)
        
        # Should use BeautifulSoup
        assert 'utils.parse_html' in source
        assert 'soup.select' in source
        
        # Should not use old regex patterns
        assert 're.compile' not in source
        assert 'findall' not in source

    def test_bs4_usage_in_categories_function(self):
        """Test that Categories function uses BeautifulSoup"""
        import inspect
        source = inspect.getsource(fullporner.Categories)
        
        # Should use BeautifulSoup
        assert 'utils.parse_html' in source
        assert 'soup.select' in source

    def test_bs4_usage_in_actors_function(self):
        """Test that Actors function uses BeautifulSoup"""
        import inspect
        source = inspect.getsource(fullporner.Actors)
        
        # Should use BeautifulSoup
        assert 'utils.parse_html' in source
        assert 'soup.select' in source

    def test_error_handling_in_list_function(self):
        """Test that List function has proper error handling"""
        import inspect
        source = inspect.getsource(fullporner.List)
        
        # Should have try-except blocks
        assert 'try:' in source
        assert 'except' in source
        assert 'utils.kodilog' in source

    def test_error_handling_in_categories_function(self):
        """Test that Categories function has proper error handling"""
        import inspect
        source = inspect.getsource(fullporner.Categories)
        
        # Should have try-except blocks
        assert 'try:' in source
        assert 'except' in source
        assert 'utils.kodilog' in source

    def test_error_handling_in_actors_function(self):
        """Test that Actors function has proper error handling"""
        import inspect
        source = inspect.getsource(fullporner.Actors)
        
        # Should have try-except blocks
        assert 'try:' in source
        assert 'except' in source
        assert 'utils.kodilog' in source

    def test_video_item_parsing_logic(self):
        """Test that video item parsing uses bs4 methods"""
        import inspect
        source = inspect.getsource(fullporner.List)
        
        # Should use bs4 selectors
        assert 'article' in source
        assert 'select_one' in source
        assert 'safe_get_attr' in source
        assert 'safe_get_text' in source

    def test_pagination_handling_in_list(self):
        """Test that pagination is handled with bs4 in List function"""
        import inspect
        source = inspect.getsource(fullporner.List)
        
        # Should use bs4 for pagination
        assert 'soup.select_one' in source
        assert '.pagination' in source
        assert '.current' in source

    def test_pagination_handling_in_actors(self):
        """Test that pagination is handled with bs4 in Actors function"""
        import inspect
        source = inspect.getsource(fullporner.Actors)
        
        # Should use bs4 for pagination
        assert 'soup.select_one' in source
        assert '.pagination' in source
        assert '.current' in source

    def test_image_extraction_logic(self):
        """Test that image extraction logic is preserved"""
        import inspect
        source_list = inspect.getsource(fullporner.List)
        source_categories = inspect.getsource(fullporner.Categories)
        source_actors = inspect.getsource(fullporner.Actors)
        
        # Should handle image extraction
        assert 'poster' in source_list
        assert 'src' in source_list
        assert 'src' in source_categories
        assert 'src' in source_actors

    def test_name_cleaning_logic(self):
        """Test that name cleaning logic is preserved"""
        import inspect
        source_list = inspect.getsource(fullporner.List)
        source_categories = inspect.getsource(fullporner.Categories)
        source_actors = inspect.getsource(fullporner.Actors)
        
        # Should clean names
        assert 'utils.cleantext' in source_list
        assert 'utils.cleantext' in source_categories
        assert 'utils.cleantext' in source_actors

    def test_duration_extraction(self):
        """Test that duration extraction logic is preserved"""
        import inspect
        source = inspect.getsource(fullporner.List)
        
        # Should handle duration extraction
        assert 'duration_tag' in source
        assert 'select_one("i")' in source

    def test_category_title_extraction(self):
        """Test that category title extraction is implemented"""
        import inspect
        source = inspect.getsource(fullporner.Categories)
        
        # Should extract category titles
        assert '.cat-title' in source
        assert 'title_tag' in source

    def test_search_keyword_handling(self):
        """Test that search function handles keywords properly"""
        import inspect
        source = inspect.getsource(fullporner.Search)
        
        # Should handle keyword replacement
        assert 'replace(" ", "+")' in source

    def test_category_filter_parameter(self):
        """Test that categories function adds filter parameter"""
        import inspect
        source = inspect.getsource(fullporner.Categories)
        
        # Should add filter parameter to URLs
        assert '&filter=latest' in source

    def test_sorting_logic(self):
        """Test that categories and actors are sorted alphabetically"""
        import inspect
        source_categories = inspect.getsource(fullporner.Categories)
        source_actors = inspect.getsource(fullporner.Actors)
        
        # Should sort by name
        assert 'sorted(' in source_categories
        assert 'sorted(' in source_actors
        assert 'key=lambda x: x[0].lower()' in source_categories
        assert 'key=lambda x: x[0].lower()' in source_actors

    def test_playvid_implementation(self):
        """Test that Playvid uses site link playback"""
        import inspect
        source = inspect.getsource(fullporner.Playvid)
        
        # Should use site link playback
        assert 'play_from_site_link' in source

    def test_main_menu_structure(self):
        """Test that Main function creates expected menu structure"""
        import inspect
        source = inspect.getsource(fullporner.Main)
        
        # Should have expected menu items
        assert 'Categories' in source
        assert 'Pornstars' in source
        assert 'Channels' in source
        assert 'Search' in source
