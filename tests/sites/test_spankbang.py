from resources.lib.sites import spankbang
from tests.conftest import fixture_mapped_get_html


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc="", *args, **kwargs):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": spankbang.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": spankbang.site.get_full_mode(mode),
            }
        )


def test_models_alphabet(monkeypatch):
    recorder = _Recorder()

    # Map the URL to the fixture
    # The URL used in spankbang.py is site.url + 'pornstars_alphabet'
    # site.url is 'https://spankbang.party/'
    url = "https://spankbang.party/pornstars_alphabet"
    fixture_mapped_get_html(
        monkeypatch, spankbang, {url: "spankbang_models_alphabet.html"}
    )

    monkeypatch.setattr(spankbang.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(spankbang.utils, "eod", lambda *args, **kwargs: None)

    spankbang.Models_alphabet(url)

    assert len(recorder.dirs) == 4
    assert recorder.dirs[0]["name"] == "A"
    assert recorder.dirs[0]["url"] == "https://spankbang.party/pornstars/a"
    assert recorder.dirs[0]["mode"] == "spankbang.Models"

    assert recorder.dirs[3]["name"] == "D"
    assert recorder.dirs[3]["url"] == "https://spankbang.party/pornstars/d"


def test_models(monkeypatch):
    recorder = _Recorder()

    url = "https://spankbang.party/pornstars/a"
    fixture_mapped_get_html(monkeypatch, spankbang, {url: "spankbang_models.html"})

    monkeypatch.setattr(spankbang.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(spankbang.utils, "eod", lambda *args, **kwargs: None)

    spankbang.Models(url)

    assert len(recorder.dirs) == 3
    # Note: spankbang.py adds video count to name: name + '[COLOR hotpink]{}[/COLOR]'.format(videos)
    # The fixture has '150', '200', '300'

    assert "Lexi Lore" in recorder.dirs[0]["name"]
    assert "150" in recorder.dirs[0]["name"]
    assert recorder.dirs[0]["url"] == "https://spankbang.party/pornstar/lexi+lore"
    assert recorder.dirs[0]["mode"] == "spankbang.List"

    assert "Eva Elfie" in recorder.dirs[1]["name"]
    assert "200" in recorder.dirs[1]["name"]

    assert "Angela White" in recorder.dirs[2]["name"]
    assert "300" in recorder.dirs[2]["name"]


def test_tags_pagination(monkeypatch):
    recorder = _Recorder()
    url = "https://spankbang.party/tags"
    fixture_mapped_get_html(monkeypatch, spankbang, {url: "spankbang_tags.html"})

    monkeypatch.setattr(spankbang.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(spankbang.utils, "eod", lambda *args, **kwargs: None)

    spankbang.Tags(url)

    # Should have 2 tags + 1 next page
    assert len(recorder.dirs) == 3

    # Check tags (sorted alphabetically by code)
    names = [d["name"] for d in recorder.dirs]
    assert "Anal" in names
    assert "Asian" in names

    # Check next page
    # The fixture has next link to /tags/3
    next_page = [d for d in recorder.dirs if "Next Page" in d["name"]]
    assert len(next_page) == 1
    assert next_page[0]["url"] == "https://spankbang.party/tags/3"
    assert (
        next_page[0]["mode"] == "spankbang.Tags"
    )  # Important: It should call Tags recursively, not List
