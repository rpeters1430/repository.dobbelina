"""
Test module for hdporn92 site
"""

import pytest
from resources.lib.sites import hdporn92
from resources.lib import utils


class TestHDPorn92:
    """Test cases for hdporn92 site functionality"""

    def test_site_initialization(self):
        """Test that the site is properly initialized"""
        assert hdporn92.site.name == "hdporn92"
        assert "[COLOR hotpink]Hdporn92[/COLOR]" in hdporn92.site.title
        assert hdporn92.site.url == "https://hdporn92.com/"
        assert "hdporn92.png" in hdporn92.site.image

    def test_main_function_structure(self):
        """Test that Main function exists and has expected structure"""
        assert hasattr(hdporn92, 'Main')
        assert callable(hdporn92.Main)

    def test_list_function_structure(self):
        """Test that List function exists and has expected structure"""
        assert hasattr(hdporn92, 'List')
        assert callable(hdporn92.List)

    def test_playvid_function_structure(self):
        """Test that Playvid function exists and has expected structure"""
        assert hasattr(hdporn92, 'Playvid')
        assert callable(hdporn92.Playvid)

    def test_search_function_structure(self):
        """Test that Search function exists and has expected structure"""
        assert hasattr(hdporn92, 'Search')
        assert callable(hdporn92.Search)

    def test_categories_function_structure(self):
        """Test that Categories function exists and has expected structure"""
        assert hasattr(hdporn92, 'Categories')
        assert callable(hdporn92.Categories)

    def test_tags_function_structure(self):
        """Test that Tags function exists and has expected structure"""
        assert hasattr(hdporn92, 'Tags')
        assert callable(hdporn92.Tags)

    def test_lookupinfo_function_structure(self):
        """Test that Lookupinfo function exists and has expected structure"""
        assert hasattr(hdporn92, 'Lookupinfo')
        assert callable(hdporn92.Lookupinfo)

    @pytest.mark.parametrize("function_name", [
        'Main', 'List', 'Playvid', 'Search', 'Categories', 'Tags', 'Lookupinfo'
    ])
    def test_functions_exist(self, function_name):
        """Test that all functions exist and are callable"""
        func = getattr(hdporn92, function_name)
        assert callable(func)

    def test_bs4_usage_in_list_function(self):
        """Test that List function uses BeautifulSoup instead of regex"""
        import inspect
        source = inspect.getsource(hdporn92.List)
        
        # Should use BeautifulSoup
        assert 'utils.parse_html' in source
        assert 'soup.select' in source
        
        # Should not use old regex patterns
        assert 're.compile' not in source
        assert 'findall' not in source

    def test_bs4_usage_in_categories_function(self):
        """Test that Categories function uses BeautifulSoup"""
        import inspect
        source = inspect.getsource(hdporn92.Categories)
        
        # Should use BeautifulSoup
        assert 'utils.parse_html' in source
        assert 'soup.select' in source

    def test_bs4_usage_in_tags_function(self):
        """Test that Tags function uses BeautifulSoup"""
        import inspect
        source = inspect.getsource(hdporn92.Tags)
        
        # Should use BeautifulSoup
        assert 'utils.parse_html' in source
        assert 'soup.select' in source

    def test_error_handling_in_list_function(self):
        """Test that List function has proper error handling"""
        import inspect
        source = inspect.getsource(hdporn92.List)
        
        # Should have try-except blocks
        assert 'try:' in source
        assert 'except' in source
        assert 'utils.kodilog' in source

    def test_error_handling_in_categories_function(self):
        """Test that Categories function has proper error handling"""
        import inspect
        source = inspect.getsource(hdporn92.Categories)
        
        # Should have try-except blocks
        assert 'try:' in source
        assert 'except' in source
        assert 'utils.kodilog' in source

    def test_error_handling_in_tags_function(self):
        """Test that Tags function has proper error handling"""
        import inspect
        source = inspect.getsource(hdporn92.Tags)
        
        # Should have try-except blocks
        assert 'try:' in source
        assert 'except' in source
        assert 'utils.kodilog' in source

    def test_video_item_parsing_logic(self):
        """Test that video item parsing uses bs4 methods"""
        import inspect
        source = inspect.getsource(hdporn92.List)
        
        # Should use bs4 selectors
        assert 'article' in source
        assert 'select_one' in source
        assert 'safe_get_attr' in source

    def test_pagination_handling_in_list(self):
        """Test that pagination is handled with bs4 in List function"""
        import inspect
        source = inspect.getsource(hdporn92.List)
        
        # Should use bs4 for pagination
        assert 'soup.select_one' in source
        assert '.pagination' in source
        assert '.current' in source

    def test_pagination_handling_in_categories(self):
        """Test that pagination is handled with bs4 in Categories function"""
        import inspect
        source = inspect.getsource(hdporn92.Categories)
        
        # Should use bs4 for pagination
        assert 'soup.select_one' in source
        assert '.pagination' in source
        assert '.current' in source

    def test_context_menu_structure(self):
        """Test that context menu is properly structured"""
        import inspect
        source = inspect.getsource(hdporn92.List)
        
        # Should have context menu items
        assert 'contextm=' in source
        assert 'Lookupinfo' in source

    def test_image_extraction_logic(self):
        """Test that image extraction logic is preserved"""
        import inspect
        source_list = inspect.getsource(hdporn92.List)
        source_categories = inspect.getsource(hdporn92.Categories)
        
        # Should handle image extraction
        assert 'poster' in source_list
        assert 'src' in source_list
        assert 'poster' in source_categories
        assert 'src' in source_categories

    def test_name_cleaning_logic(self):
        """Test that name cleaning logic is preserved"""
        import inspect
        source_list = inspect.getsource(hdporn92.List)
        source_categories = inspect.getsource(hdporn92.Categories)
        source_tags = inspect.getsource(hdporn92.Tags)
        
        # Should clean names
        assert 'utils.cleantext' in source_list
        assert 'utils.cleantext' in source_categories
        assert 'utils.cleantext' in source_tags

    def test_nothing_found_handling(self):
        """Test that "Nothing found" handling is preserved"""
        import inspect
        source = inspect.getsource(hdporn92.List)
        
        # Should handle nothing found
        assert '>Nothing found</h1>' in source
        assert 'notify(msg="Nothing found")' in source

    def test_search_keyword_handling(self):
        """Test that search function handles keywords properly"""
        import inspect
        source = inspect.getsource(hdporn92.Search)
        
        # Should handle keyword replacement
        assert 'replace(" ", "+")' in source

    def test_category_filter_parameter(self):
        """Test that categories function adds filter parameter"""
        import inspect
        source = inspect.getsource(hdporn92.Categories)
        
        # Should add filter parameter to URLs
        assert '?filter=latest' in source

    def test_tag_filter_parameter(self):
        """Test that tags function adds filter parameter"""
        import inspect
        source = inspect.getsource(hdporn92.Tags)
        
        # Should add filter parameter to URLs
        assert '?filter=latest' in source

    def test_tag_link_selection(self):
        """Test that tag links are selected properly"""
        import inspect
        source = inspect.getsource(hdporn92.Tags)
        
        # Should select tag links with aria-label
        assert 'a[href*="/tag/"][aria-label]' in source

    def test_tag_url_extraction(self):
        """Test that tag URL extraction is implemented"""
        import inspect
        source = inspect.getsource(hdporn92.Tags)
        
        # Should extract tag part from URL
        assert '/tag/' in source
        assert 'find(' in source

    def test_sorting_logic(self):
        """Test that categories are sorted alphabetically"""
        import inspect
        source = inspect.getsource(hdporn92.Categories)
        
        # Should sort by name
        assert 'sorted(' in source
        assert 'key=lambda x: x[0].lower()' in source

    def test_playvid_regex_usage(self):
        """Test that Playvid function still uses regex for iframe extraction"""
        import inspect
        source = inspect.getsource(hdporn92.Playvid)
        
        # Should use regex for iframe extraction
        assert 're.compile' in source
        assert '<iframe' in source
        assert 'allowfullscreen' in source

    def test_playvid_progress_update(self):
        """Test that Playvid function shows progress"""
        import inspect
        source = inspect.getsource(hdporn92.Playvid)
        
        # Should update progress
        assert 'progress.update' in source
        assert 'Loading video page' in source

    def test_playvid_embed_handling(self):
        """Test that Playvid function handles embed pages"""
        import inspect
        source = inspect.getsource(hdporn92.Playvid)
        
        # Should handle embed pages
        assert 'embedhtml' in source
        assert 'get_packed_data' in source
        assert 'var links=' in source

    def test_playvid_json_parsing(self):
        """Test that Playvid function parses JSON data"""
        import inspect
        source = inspect.getsource(hdporn92.Playvid)
        
        # Should parse JSON
        assert 'json.loads' in source
        assert 'hls2' in source

    def test_playvid_error_handling(self):
        """Test that Playvid function handles errors"""
        import inspect
        source = inspect.getsource(hdporn92.Playvid)
        
        # Should handle no videos found
        assert 'No Videos found' in source

    def test_lookupinfo_patterns(self):
        """Test that Lookupinfo has proper regex patterns"""
        import inspect
        source = inspect.getsource(hdporn92.Lookupinfo)
        
        # Should have lookup patterns
        assert 'Cat' in source
        assert 'Model' in source
        assert 'category/' in source
        assert 'actor/' in source

    def test_main_menu_structure(self):
        """Test that Main function creates expected menu structure"""
        import inspect
        source = inspect.getsource(hdporn92.Main)
        
        # Should have expected menu items
        assert 'Categories' in source
        assert 'Actors' in source
        assert 'Tags' in source
        assert 'Search' in source
        assert '?filter=latest' in source
