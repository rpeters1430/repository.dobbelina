---
name: bs4-migration-toolkit
description: Focused workflows for migrating Kodi site scrapers from fragile Regex patterns to robust BeautifulSoup4 (BS4) parsing. Use when refactoring site modules in plugin.video.cumination/resources/lib/sites/.
---

# BeautifulSoup4 Migration Toolkit

This skill guides the migration of site scrapers to use BeautifulSoup4 with the project's specialized helpers in `utils.py`.

## Core Helpers

Always import these from `resources.lib.utils`:

- `parse_html(html)`: Returns a BS4 object using `lxml` (fast) or `html.parser`.
- `safe_get_attr(element, attr, fallback_attrs=None)`: Safely extracts attributes with fallbacks.
- `safe_get_text(element)`: Safely extracts and strips text.
- `get_thumbnail(element)`: Robustly finds image URLs (handles `data-src`, `srcset`, etc.).
- `soup_videos_list(...)`: The declarative powerhouse for parsing video lists.

## The Declarative Approach: `soup_videos_list`

Instead of writing manual loops, use `soup_videos_list`. It takes a `selectors` dictionary.

### Example Selectors Config
```python
selectors = {
    'items': 'div.video-item',  # CSS selector for the video container
    'url': {'selector': 'a', 'attr': 'href'},
    'title': {'selector': 'h3', 'text': True},
    'thumbnail': {'selector': 'img', 'attr': 'data-src', 'fallback_attrs': ['src']},
    'duration': {'selector': '.duration', 'text': True},
    'pagination': {
        'selector': 'a.next-page',
        'attr': 'href',
        'text_matches': ['next', '>']
    }
}

from resources.lib.utils import parse_html, soup_videos_list
soup = parse_html(listhtml)
soup_videos_list(self, soup, selectors)
```

## Migration Workflow

1.  **Analyze**: Locate the `re.findall` or `re.search` calls in the legacy site module.
2.  **Inspect**: Use `scripts/codegen.py --dump-page` to get the actual HTML structure of the site.
3.  **Map**: Identify CSS selectors that match the data previously extracted by Regex.
4.  **Refactor**:
    - Replace Regex loops with `soup_videos_list`.
    - Use `parse_html` for individual page parsing (e.g., finding the video URL).
5.  **Validate**: Ensure thumbnails use `get_thumbnail` to avoid broken images from lazy-loading.

## Handling Common BS4 Obstacles

### Lazy Loading
Sites often hide the real image in `data-src` or `original`. `get_thumbnail` handles this automatically if you pass the `img` element.

### Relative URLs
`soup_videos_list` automatically resolves URLs if you provide a `base_url` or if `self.url` is set on the site object.

### Malformed HTML
`parse_html` is configured to be forgiving. If it fails, check if the site uses JavaScript to render content (requires a different approach).
