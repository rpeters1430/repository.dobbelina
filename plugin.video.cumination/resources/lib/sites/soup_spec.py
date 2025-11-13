"""Utilities for defining BeautifulSoup-driven site configs.

This module centralises the tiny per-site configuration objects that feed
``utils.soup_videos_list`` so individual site modules can focus on declaring
selectors instead of re-implementing boilerplate glue code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from resources.lib import utils


@dataclass(frozen=True)
class SoupSiteSpec:
    """Declarative configuration for ``utils.soup_videos_list`` calls.

    Args:
        selectors: Raw selector dictionary passed to ``soup_videos_list``.
        play_mode: Kodi mode string used when launching a video.
        contextm: Optional context menu entries shared across items.
        base_url: Overrides the base URL passed to ``soup_videos_list``.
        fanart: Optional fanart forwarded to ``soup_videos_list``.
        description: Static or selector driven description configuration.
    """

    selectors: Mapping[str, Any]
    play_mode: str = 'Playvid'
    contextm: Optional[Any] = None
    base_url: Optional[str] = None
    fanart: Optional[str] = None
    description: Optional[Any] = None

    def run(self, site, soup, **overrides) -> Dict[str, Any]:
        """Execute the configuration against ``soup`` for ``site``.

        Keyword arguments override dataclass attributes so callers can tweak
        context menus, base URLs or even selectors when necessary without
        re-defining an entirely new spec per scenario.
        """

        selectors = overrides.pop('selectors', self.selectors)
        options = {
            'play_mode': self.play_mode,
            'contextm': self.contextm,
            'base_url': self.base_url,
            'fanart': self.fanart,
            'description': self.description,
        }
        options.update(overrides)
        return utils.soup_videos_list(site, soup, selectors, **options)


__all__ = ['SoupSiteSpec']

