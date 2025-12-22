"""
Tests for favorites.py database operations
"""
import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # Initialize the database schema
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS favorites (name, url, mode, image, duration, quality);
        CREATE TABLE IF NOT EXISTS keywords (keyword);
        CREATE TABLE IF NOT EXISTS custom_sites (author, name, title, url, image, about, version, installed_at, enabled, module_file);
        CREATE TABLE IF NOT EXISTS custom_lists (name);
        CREATE TABLE IF NOT EXISTS custom_listitems (name, url, mode, image, list_id);
    """)
    conn.commit()
    conn.close()

    yield path

    # Cleanup
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def mock_basics(temp_db, monkeypatch):
    """Mock the basics module with temp database"""
    from resources.lib import basics
    monkeypatch.setattr(basics, 'favoritesdb', temp_db)
    return basics


@pytest.fixture
def favorites_module(temp_db, monkeypatch):
    """Import favorites module with mocked database"""
    # Patch the database path before importing
    import sys
    from resources.lib import basics

    # Store original
    original_favdb = basics.favoritesdb

    # Set to temp
    monkeypatch.setattr(basics, 'favoritesdb', temp_db)

    # Reload the favorites module to pick up the new database path
    if 'resources.lib.favorites' in sys.modules:
        del sys.modules['resources.lib.favorites']

    # Re-import with patched path
    from resources.lib import favorites

    # Also patch the module-level favoritesdb variable
    monkeypatch.setattr(favorites, 'favoritesdb', temp_db)

    yield favorites

    # Restore
    basics.favoritesdb = original_favdb


class TestFavoritesBasicCRUD:
    """Test basic Create, Read, Update, Delete operations"""

    def test_addFav(self, favorites_module, temp_db):
        """Test adding a favorite"""
        favorites_module.addFav(
            mode='pornhub.Playvid',
            name='Test Video',
            url='https://example.com/video1',
            img='https://example.com/thumb.jpg',
            duration='10:30',
            quality='720p'
        )

        # Verify it was added
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT * FROM favorites WHERE url = ?", ('https://example.com/video1',))
        result = c.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 'Test Video'
        assert result[1] == 'https://example.com/video1'
        assert result[2] == 'pornhub.Playvid'
        assert result[3] == 'https://example.com/thumb.jpg'
        assert result[4] == '10:30'
        assert result[5] == '720p'

    def test_select_favorite(self, favorites_module, temp_db):
        """Test selecting a favorite"""
        # Add a favorite first
        favorites_module.addFav(
            mode='xvideos.Playvid',
            name='Another Video',
            url='https://example.com/video2',
            img='https://example.com/thumb2.jpg',
            duration='5:00',
            quality='1080p'
        )

        # Select it
        result = favorites_module.select_favorite('https://example.com/video2')

        assert result is not None
        assert result[0] == 'Another Video'
        assert result[1] == 'https://example.com/video2'
        assert result[2] == 'xvideos.Playvid'

    def test_select_favorite_not_found(self, favorites_module):
        """Test selecting a non-existent favorite"""
        result = favorites_module.select_favorite('https://example.com/nonexistent')
        assert result is None

    def test_update_favorite(self, favorites_module, temp_db):
        """Test updating a favorite"""
        # Add a favorite
        favorites_module.addFav(
            mode='spankbang.Playvid',
            name='Original Name',
            url='https://example.com/video3',
            img='https://example.com/thumb3.jpg',
            duration='15:00',
            quality='480p'
        )

        # Update it
        favorites_module.update_favorite(
            mode='spankbang.Playvid',
            name='Updated Name',
            url='https://example.com/video3',
            img='https://example.com/new_thumb.jpg',
            duration='15:30',
            quality='1080p'
        )

        # Verify update
        result = favorites_module.select_favorite('https://example.com/video3')
        assert result[0] == 'Updated Name'
        assert result[3] == 'https://example.com/new_thumb.jpg'
        assert result[4] == '15:30'
        assert result[5] == '1080p'

    def test_delFav(self, favorites_module, temp_db):
        """Test deleting a favorite"""
        # Add a favorite
        favorites_module.addFav(
            mode='eporner.Playvid',
            name='To Be Deleted',
            url='https://example.com/video4',
            img='https://example.com/thumb4.jpg',
            duration='8:00',
            quality='720p'
        )

        # Verify it exists
        result = favorites_module.select_favorite('https://example.com/video4')
        assert result is not None

        # Delete it
        favorites_module.delFav('https://example.com/video4')

        # Verify it's gone
        result = favorites_module.select_favorite('https://example.com/video4')
        assert result is None


class TestFavoritesDuplicates:
    """Test duplicate handling"""

    def test_delete_duplicates(self, favorites_module, temp_db):
        """Test deleting duplicate favorites"""
        # Add the same URL twice
        favorites_module.addFav(
            mode='pornhub.Playvid',
            name='Video 1',
            url='https://example.com/dup',
            img='https://example.com/thumb.jpg',
            duration='10:00',
            quality='720p'
        )
        favorites_module.addFav(
            mode='pornhub.Playvid',
            name='Video 1 Duplicate',
            url='https://example.com/dup',
            img='https://example.com/thumb.jpg',
            duration='10:00',
            quality='720p'
        )

        # Verify we have 2 entries
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM favorites WHERE url = ?", ('https://example.com/dup',))
        count = c.fetchone()[0]
        conn.close()
        assert count == 2

        # Delete duplicates
        favorites_module.delete_duplicates()

        # Verify we now have only 1
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM favorites WHERE url = ?", ('https://example.com/dup',))
        count = c.fetchone()[0]
        conn.close()
        assert count == 1


class TestFavoritesMovement:
    """Test favorite movement functions"""

    def test_move_fav_to_top(self, favorites_module, temp_db):
        """Test moving favorite to top"""
        # Add multiple favorites
        for i in range(3):
            favorites_module.addFav(
                mode='pornhub.Playvid',
                name=f'Video {i}',
                url=f'https://example.com/video{i}',
                img='https://example.com/thumb.jpg',
                duration='10:00',
                quality='720p'
            )

        # Move the first video to top
        favorites_module.move_fav_to_top('https://example.com/video0')

        # Verify it's now at the highest rowid
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT url FROM favorites ORDER BY ROWID DESC LIMIT 1")
        top_url = c.fetchone()[0]
        conn.close()

        assert top_url == 'https://example.com/video0'

    def test_move_fav_to_bottom(self, favorites_module, temp_db):
        """Test moving favorite to bottom"""
        # Add multiple favorites
        for i in range(3):
            favorites_module.addFav(
                mode='pornhub.Playvid',
                name=f'Video {i}',
                url=f'https://example.com/video{i}',
                img='https://example.com/thumb.jpg',
                duration='10:00',
                quality='720p'
            )

        # Move the last video to bottom
        favorites_module.move_fav_to_bottom('https://example.com/video2')

        # Verify it's now at the lowest rowid
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT url FROM favorites ORDER BY ROWID ASC LIMIT 1")
        bottom_url = c.fetchone()[0]
        conn.close()

        assert bottom_url == 'https://example.com/video2'


class TestCustomSites:
    """Test custom site database operations"""

    def test_get_new_site_id_empty(self, favorites_module, temp_db):
        """Test getting new site ID when database is empty"""
        site_id = favorites_module.get_new_site_id()
        assert site_id == 1

    def test_get_new_site_id_with_existing(self, favorites_module, temp_db):
        """Test getting new site ID with existing sites"""
        # Add a custom site
        favorites_module.add_custom_site(
            author='testauthor',
            name='testsite',
            title='Test Site',
            url='https://testsite.com',
            image='test.png',
            about='test_about',
            version='1.0',
            module_file='custom_1'
        )

        # Get next ID
        site_id = favorites_module.get_new_site_id()
        assert site_id == 2

    def test_add_custom_site(self, favorites_module, temp_db):
        """Test adding a custom site"""
        favorites_module.add_custom_site(
            author='myauthor',
            name='mysite',
            title='My Custom Site',
            url='https://mycustomsite.com',
            image='mysite.png',
            about='mysite_about',
            version='2.0',
            module_file='custom_1'
        )

        # Verify it was added
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT * FROM custom_sites WHERE name = ?", ('mysite',))
        result = c.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 'myauthor'
        assert result[1] == 'mysite'
        assert result[2] == 'My Custom Site'
        assert result[3] == 'https://mycustomsite.com'
        assert result[6] == '2.0'

    def test_select_custom_sites_attributes(self, favorites_module, temp_db):
        """Test selecting custom site attributes"""
        # Add a custom site
        favorites_module.add_custom_site(
            author='author1',
            name='site1',
            title='Site One',
            url='https://site1.com',
            image='site1.png',
            about='site1_about',
            version='1.0',
            module_file='custom_1'
        )

        # Select attributes
        result = favorites_module.select_custom_sites_attributes(
            ('author1', 'site1'),
            'title', 'version'
        )

        assert len(result) == 1
        assert result[0][0] == 'Site One'
        assert result[0][1] == '1.0'

    def test_select_custom_sites_attributes_all(self, favorites_module, temp_db):
        """Test selecting all custom sites"""
        # Add multiple sites
        for i in range(3):
            favorites_module.add_custom_site(
                author=f'author{i}',
                name=f'site{i}',
                title=f'Site {i}',
                url=f'https://site{i}.com',
                image=f'site{i}.png',
                about=f'site{i}_about',
                version='1.0',
                module_file=f'custom_{i}'
            )

        # Select all
        result = favorites_module.select_custom_sites_attributes(None, 'name')
        assert len(result) == 3

    def test_select_custom_sites_invalid_column(self, favorites_module):
        """Test that invalid column names are rejected"""
        with pytest.raises(ValueError, match="Invalid column name"):
            favorites_module.select_custom_sites_attributes(None, 'invalid_column')

    def test_enabled_custom_sites(self, favorites_module, temp_db):
        """Test getting enabled custom sites"""
        # Add sites with different enabled states
        favorites_module.add_custom_site(
            author='author1',
            name='enabled_site',
            title='Enabled Site',
            url='https://enabled.com',
            image='enabled.png',
            about='enabled_about',
            version='1.0',
            module_file='custom_enabled'
        )

        # Enable it
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("UPDATE custom_sites SET enabled = 1 WHERE name = ?", ('enabled_site',))
        conn.commit()
        conn.close()

        # Get enabled sites
        enabled = favorites_module.enabled_custom_sites()
        assert 'custom_enabled' in enabled

    def test_get_custom_data(self, favorites_module, temp_db):
        """Test getting custom site data"""
        # Add a site
        favorites_module.add_custom_site(
            author='dataauthor',
            name='datasite',
            title='Data Site',
            url='https://datasite.com',
            image='data.png',
            about='data_about',
            version='1.0',
            module_file='custom_data'
        )

        # Get data
        result = favorites_module.get_custom_data('dataauthor', 'datasite')
        assert result is not None
        assert result[0] == 'Data Site'
        assert result[1] == 'data.png'
        assert result[2] == 'data_about'
        assert result[3] == 'https://datasite.com'

    def test_get_custom_data_not_found(self, favorites_module):
        """Test getting data for non-existent site"""
        result = favorites_module.get_custom_data('nonexistent', 'site')
        assert result == (None, None, None, None)

    def test_disable_custom_site_by_module(self, favorites_module, temp_db):
        """Test disabling a custom site by module name"""
        # Add an enabled site
        favorites_module.add_custom_site(
            author='author',
            name='todisable',
            title='To Disable',
            url='https://todisable.com',
            image='disable.png',
            about='disable_about',
            version='1.0',
            module_file='custom_disable'
        )

        # Enable it first
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("UPDATE custom_sites SET enabled = 1 WHERE module_file = ?", ('custom_disable',))
        conn.commit()
        conn.close()

        # Disable it
        favorites_module.disable_custom_site_by_module('custom_disable')

        # Verify it's disabled
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT enabled FROM custom_sites WHERE module_file = ?", ('custom_disable',))
        enabled = c.fetchone()[0]
        conn.close()

        assert enabled == 0

    def test_get_custom_site_title_by_module(self, favorites_module, temp_db):
        """Test getting custom site title by module"""
        # Add a site
        favorites_module.add_custom_site(
            author='titleauthor',
            name='titlesite',
            title='Title Site',
            url='https://titlesite.com',
            image='title.png',
            about='title_about',
            version='1.0',
            module_file='custom_title'
        )

        # Get title
        title = favorites_module.get_custom_site_title_by_module('custom_title')
        assert title == 'Title Site'


class TestCustomLists:
    """Test custom lists functionality"""

    def test_get_custom_lists_empty(self, favorites_module):
        """Test getting custom lists when none exist"""
        lists = favorites_module.get_custom_lists()
        assert lists == []

    def test_get_custom_lists(self, favorites_module, temp_db):
        """Test getting custom lists"""
        # Add some lists
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("INSERT INTO custom_lists VALUES (?)", ('My List 1',))
        c.execute("INSERT INTO custom_lists VALUES (?)", ('My List 2',))
        conn.commit()
        conn.close()

        # Get lists
        lists = favorites_module.get_custom_lists()
        assert len(lists) == 2
        assert lists[0][1] == 'My List 1'
        assert lists[1][1] == 'My List 2'

    def test_get_custom_listitems_empty(self, favorites_module):
        """Test getting custom list items when none exist"""
        items = favorites_module.get_custom_listitems()
        assert items == []


class TestGetSiteName:
    """Test the get_site_name helper function"""

    def test_get_site_name_by_domain(self, favorites_module):
        """Test getting site name by domain match"""
        # Create mock AdultSite instances
        mock_site = Mock()
        mock_site.url = 'https://example.com/'
        mock_site.title = 'Example Site'
        mock_site.name = 'example'

        adultsites = [mock_site]

        result = favorites_module.get_site_name('example', 'example.com', adultsites)
        assert result == 'Example Site'

    def test_get_site_name_by_name(self, favorites_module):
        """Test getting site name by site name match"""
        # Create mock AdultSite instances
        mock_site = Mock()
        mock_site.url = 'https://different.com/'
        mock_site.title = 'Different Site'
        mock_site.name = 'example'

        adultsites = [mock_site]

        result = favorites_module.get_site_name('example', 'notmatching.com', adultsites)
        assert result == 'Different Site'

    def test_get_site_name_removed(self, favorites_module):
        """Test getting site name for removed site"""
        result = favorites_module.get_site_name('removed', 'removed.com', [])
        assert 'removed' in result
        assert '(removed)' in result
