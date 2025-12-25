"""
Tests for basics.py utility functions
"""

import pytest
import os
import tempfile
import shutil
import sqlite3
from unittest.mock import patch


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Initialize the database schema
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS favorites (name, url, mode, image, duration, quality);
        CREATE TABLE IF NOT EXISTS keywords (keyword);
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
def mock_basics_paths(monkeypatch):
    """Mock basics module paths"""
    from resources.lib import basics

    # Create temp directories for testing
    temp_root = tempfile.mkdtemp()
    temp_img = os.path.join(temp_root, "images")
    temp_custom = os.path.join(temp_root, "custom_sites")
    temp_temp = os.path.join(temp_root, "temp")

    os.makedirs(temp_img, exist_ok=True)
    os.makedirs(temp_custom, exist_ok=True)
    os.makedirs(temp_temp, exist_ok=True)

    monkeypatch.setattr(basics, "imgDir", temp_img)
    monkeypatch.setattr(basics, "customSitesDir", temp_custom)
    monkeypatch.setattr(basics, "tempDir", temp_temp)

    yield {
        "root": temp_root,
        "imgDir": temp_img,
        "customSitesDir": temp_custom,
        "tempDir": temp_temp,
    }

    # Cleanup
    shutil.rmtree(temp_root, ignore_errors=True)


class TestCumImage:
    """Test cum_image() function"""

    def test_cum_image_with_http_url(self):
        """Test that HTTP URLs are returned as-is"""
        from resources.lib import basics

        url = "https://example.com/image.jpg"
        result = basics.cum_image(url)

        assert result == url

    def test_cum_image_with_https_url(self):
        """Test that HTTPS URLs are returned as-is"""
        from resources.lib import basics

        url = "https://secure.example.com/image.png"
        result = basics.cum_image(url)

        assert result == url

    def test_cum_image_local_file(self, mock_basics_paths):
        """Test local filename returns path in imgDir"""
        from resources.lib import basics

        filename = "site_icon.png"
        result = basics.cum_image(filename)

        assert result == os.path.join(mock_basics_paths["imgDir"], filename)
        assert not result.startswith("http")

    def test_cum_image_custom_site(self, mock_basics_paths):
        """Test custom site image returns path in customSitesDir"""
        from resources.lib import basics

        filename = "custom_icon.png"
        result = basics.cum_image(filename, custom=True)

        assert result == os.path.join(mock_basics_paths["customSitesDir"], filename)


class TestGetResolution:
    """Test get_resolution() function"""

    def test_get_resolution_720p(self):
        """Test parsing 720p quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("720p")

        assert height == 720
        assert width == 1280  # 720 * 16/9

    def test_get_resolution_1080p(self):
        """Test parsing 1080p quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("1080p")

        assert height == 1080
        assert width == 1920  # 1080 * 16/9

    def test_get_resolution_480p(self):
        """Test parsing 480p quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("480p")

        assert height == 480
        assert width == 853  # 480 * 16/9 (rounded)

    def test_get_resolution_2160p_4k(self):
        """Test parsing 2160p (4K) quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("2160p")

        assert height == 2160
        assert width == 3840  # 2160 * 16/9

    def test_get_resolution_without_p_suffix(self):
        """Test parsing quality without 'p' suffix"""
        from resources.lib import basics

        width, height = basics.get_resolution("1080")

        assert height == 1080
        assert width == 1920

    def test_get_resolution_sd(self):
        """Test parsing SD quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("SD")

        assert width == 640
        assert height == 480

    def test_get_resolution_hd(self):
        """Test parsing HD quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("HD")

        assert width == 1280
        assert height == 720

    def test_get_resolution_fullhd(self):
        """Test parsing FULLHD quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("FULLHD")

        assert width == 1920
        assert height == 1080

    def test_get_resolution_fhd(self):
        """Test parsing FHD quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("FHD")

        assert width == 1920
        assert height == 1080

    def test_get_resolution_2k(self):
        """Test parsing 2K quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("2K")

        assert width == 2560
        assert height == 1440

    def test_get_resolution_4k(self):
        """Test parsing 4K quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("4K")

        assert width == 3840
        assert height == 2160

    def test_get_resolution_uhd(self):
        """Test parsing UHD quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("UHD")

        assert width == 3840
        assert height == 2160

    def test_get_resolution_8k(self):
        """Test parsing 8K quality"""
        from resources.lib import basics

        width, height = basics.get_resolution("8K")

        assert width == 7680
        assert height == 4320

    def test_get_resolution_lowercase(self):
        """Test parsing lowercase quality strings"""
        from resources.lib import basics

        width, height = basics.get_resolution("hd")

        assert width == 1280
        assert height == 720

    def test_get_resolution_mixed_case(self):
        """Test parsing mixed case quality strings"""
        from resources.lib import basics

        width, height = basics.get_resolution("FullHD")

        assert width == 1920
        assert height == 1080

    def test_get_resolution_with_whitespace(self):
        """Test parsing quality with whitespace"""
        from resources.lib import basics

        width, height = basics.get_resolution(" 1080p ")

        # String operations should handle whitespace
        assert height == 1080 or (width is None and height is None)

    def test_get_resolution_invalid(self):
        """Test parsing invalid quality returns None"""
        from resources.lib import basics

        width, height = basics.get_resolution("invalid")

        assert width is None
        assert height is None

    def test_get_resolution_empty(self):
        """Test parsing empty string"""
        from resources.lib import basics

        width, height = basics.get_resolution("")

        assert width is None
        assert height is None

    def test_get_resolution_numeric_only(self):
        """Test numeric-only resolution (edge case)"""
        from resources.lib import basics

        width, height = basics.get_resolution(720)

        # Should convert to string and parse
        assert height == 720
        assert width == 1280


class TestCleanTemp:
    """Test clean_temp() function"""

    def test_clean_temp(self, mock_basics_paths):
        """Test cleaning temp directory"""
        from resources.lib import basics

        temp_dir = mock_basics_paths["tempDir"]

        # Create some files in temp directory
        test_file1 = os.path.join(temp_dir, "test1.txt")
        test_file2 = os.path.join(temp_dir, "test2.txt")
        subdir = os.path.join(temp_dir, "subdir")

        os.makedirs(subdir, exist_ok=True)

        with open(test_file1, "w") as f:
            f.write("test content 1")
        with open(test_file2, "w") as f:
            f.write("test content 2")
        with open(os.path.join(subdir, "test3.txt"), "w") as f:
            f.write("test content 3")

        # Verify files exist
        assert os.path.exists(test_file1)
        assert os.path.exists(test_file2)
        assert os.path.exists(subdir)

        # Clean temp
        basics.clean_temp()

        # Verify directory is recreated but empty
        assert os.path.exists(temp_dir)
        assert len(os.listdir(temp_dir)) == 0


class TestKeys:
    """Test keys() database function"""

    def test_keys_empty_database(self, temp_db, monkeypatch):
        """Test keys() with empty database"""
        from resources.lib import basics

        monkeypatch.setattr(basics, "favoritesdb", temp_db)

        result = basics.keys()

        assert result == {}

    def test_keys_single_letter(self, temp_db, monkeypatch):
        """Test keys() with keywords starting with same letter"""
        from resources.lib import basics

        monkeypatch.setattr(basics, "favoritesdb", temp_db)

        # Add keywords
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("INSERT INTO keywords VALUES (?)", ("apple",))
        c.execute("INSERT INTO keywords VALUES (?)", ("apricot",))
        c.execute("INSERT INTO keywords VALUES (?)", ("avocado",))
        conn.commit()
        conn.close()

        result = basics.keys()

        assert "A" in result
        assert result["A"] == 3

    def test_keys_multiple_letters(self, temp_db, monkeypatch):
        """Test keys() with keywords starting with different letters"""
        from resources.lib import basics

        monkeypatch.setattr(basics, "favoritesdb", temp_db)

        # Add keywords
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("INSERT INTO keywords VALUES (?)", ("apple",))
        c.execute("INSERT INTO keywords VALUES (?)", ("banana",))
        c.execute("INSERT INTO keywords VALUES (?)", ("cherry",))
        c.execute("INSERT INTO keywords VALUES (?)", ("blueberry",))
        conn.commit()
        conn.close()

        result = basics.keys()

        assert "A" in result
        assert "B" in result
        assert "C" in result
        assert result["A"] == 1
        assert result["B"] == 2
        assert result["C"] == 1

    def test_keys_case_insensitive(self, temp_db, monkeypatch):
        """Test keys() groups keywords case-insensitively"""
        from resources.lib import basics

        monkeypatch.setattr(basics, "favoritesdb", temp_db)

        # Add keywords with different cases
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("INSERT INTO keywords VALUES (?)", ("Apple",))
        c.execute("INSERT INTO keywords VALUES (?)", ("avocado",))
        c.execute("INSERT INTO keywords VALUES (?)", ("APRICOT",))
        conn.commit()
        conn.close()

        result = basics.keys()

        # Should group by uppercase letter
        assert "A" in result
        assert result["A"] == 3


class TestSearchDir:
    """Test searchDir() function"""

    @patch("resources.lib.basics.eod")
    @patch("resources.lib.basics.addDir")
    def test_searchdir_no_alphabet_no_keywords(
        self, mock_addDir, mock_eod, temp_db, monkeypatch
    ):
        """Test searchDir without alphabet filter and no keywords"""
        from resources.lib import basics

        monkeypatch.setattr(basics, "favoritesdb", temp_db)

        # Mock addon.getSetting
        with patch.object(basics.addon, "getSetting", return_value="false"):
            basics.searchDir("http://example.com", "site.Search")

        # Should add the default search options
        assert mock_addDir.call_count >= 3  # One time search, Add Keyword, Alphabetical
        mock_eod.assert_called_once()

    @patch("resources.lib.basics.eod")
    @patch("resources.lib.basics.addDir")
    def test_searchdir_with_keywords(self, mock_addDir, mock_eod, temp_db, monkeypatch):
        """Test searchDir displays saved keywords"""
        from resources.lib import basics

        monkeypatch.setattr(basics, "favoritesdb", temp_db)

        # Add some keywords
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("INSERT INTO keywords VALUES (?)", ("test1",))
        c.execute("INSERT INTO keywords VALUES (?)", ("test2",))
        conn.commit()
        conn.close()

        # Mock addon.getSetting
        with patch.object(basics.addon, "getSetting", return_value="false"):
            basics.searchDir("http://example.com", "site.Search")

        # Should have added search options + 2 keywords
        assert mock_addDir.call_count >= 5
        mock_eod.assert_called_once()

    @patch("resources.lib.basics.eod")
    @patch("resources.lib.basics.addDir")
    def test_searchdir_alphabetical_filter(
        self, mock_addDir, mock_eod, temp_db, monkeypatch
    ):
        """Test searchDir with alphabetical filter"""
        from resources.lib import basics

        monkeypatch.setattr(basics, "favoritesdb", temp_db)

        # Add keywords
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("INSERT INTO keywords VALUES (?)", ("apple",))
        c.execute("INSERT INTO keywords VALUES (?)", ("apricot",))
        c.execute("INSERT INTO keywords VALUES (?)", ("banana",))
        conn.commit()
        conn.close()

        # Search for keywords starting with 'a'
        basics.searchDir("http://example.com", "site.Search", alphabet="a")

        # Should only add keywords starting with 'a' (2 keywords)
        # No search options are added when alphabet is specified
        assert mock_addDir.call_count == 2
        mock_eod.assert_called_once()

    @patch("resources.lib.basics.eod")
    @patch("resources.lib.basics.addDir")
    def test_searchdir_sorted_keywords(
        self, mock_addDir, mock_eod, temp_db, monkeypatch
    ):
        """Test searchDir with sorted keywords setting"""
        from resources.lib import basics

        monkeypatch.setattr(basics, "favoritesdb", temp_db)

        # Add keywords
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("INSERT INTO keywords VALUES (?)", ("zebra",))
        c.execute("INSERT INTO keywords VALUES (?)", ("apple",))
        c.execute("INSERT INTO keywords VALUES (?)", ("banana",))
        conn.commit()
        conn.close()

        # Mock sorted setting
        with patch.object(basics.addon, "getSetting", return_value="true"):
            basics.searchDir("http://example.com", "site.Search")

        # Should have been called (with sorted keywords)
        assert mock_addDir.call_count >= 3
        mock_eod.assert_called_once()
