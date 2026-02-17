# Archivebate.com — Site Analysis

**URL**: https://archivebate.com/
**Status**: Ready to implement
**Difficulty**: Medium (listing requires Livewire session; video page is trivial)

---

## How the Site Works

Archivebate is a cam archive site (Chaturbate, Stripchat, etc.) built on **Laravel + Livewire**.

- The **listing page** HTML is skeleton loaders only. Actual video items are injected by a
  Livewire XHR call (`POST /livewire/message/home-videos`) that requires a session cookie +
  CSRF token from the initial page GET.
- The **video page** (`/watch/NNNNNN`) is fully **server-rendered** — no JavaScript needed.
  The MixDrop iframe `src` is in the static HTML.
- Videos are hosted on **MixDrop** (`mixdrop.ag`). The actual CDN is `mxcontent.net` (MixDrop's
  CDN). ResolveURL already has a MixDrop plugin, so playback needs zero custom work.

---

## Video Page (Playvid) — trivial

A plain `getHtml()` call returns the iframe src in the static HTML.

```python
soup = utils.parse_html(utils.getHtml(url, site.url))
iframe = soup.select_one('iframe.video-frame')
# iframe['src'] == 'https://mixdrop.ag/e/1n4gew0pb0ov1x'
vp.play_from_link_to_resolve(iframe['src'])
```

**Confirmed selectors on `/watch/NNNNNN`:**

| Element | Selector | Note |
|---|---|---|
| Player iframe | `iframe.video-frame` | `src` = MixDrop embed URL |
| Thumbnail (og) | `meta[property="og:image"]` | `content` attr |
| Page title | `<title>` | format: `username Chaturbate webcam recordings, Archivebate` |

---

## Listing Page — two-step Livewire fetch

### Step 1 — GET the listing page

A normal `requests.Session().get()` to get:
- Session cookie (`archivebate_session`, `XSRF-TOKEN`) — set automatically by the server
- CSRF token — `<meta name="csrf-token" content="...">` in HTML
- Livewire component state — `wire:initial-data="..."` attribute on the component that has
  `wire:init="loadVideos"`

```python
import requests, re, json, html as htmlmod

session = requests.Session()
session.headers.update({'User-Agent': utils.USER_AGENT})

resp = session.get('https://archivebate.com/')
csrf = re.search(r'<meta name="csrf-token" content="([^"]+)"', resp.text).group(1)

match = re.search(
    r'wire:initial-data="([^"]+)"[^>]*wire:init="loadVideos"', resp.text
)
wire_state = json.loads(htmlmod.unescape(match.group(1)))
```

### Step 2 — POST to Livewire endpoint

```python
payload = {
    "fingerprint": wire_state['fingerprint'],
    "serverMemo":  wire_state['serverMemo'],
    "updates": [{
        "type": "callMethod",
        "payload": {"id": "x1", "method": "loadVideos", "params": []}
    }]
}

lw_resp = session.post(
    'https://archivebate.com/livewire/message/home-videos',
    json=payload,
    headers={
        'X-CSRF-TOKEN':   csrf,
        'X-Livewire':     'true',
        'Accept':         'application/json',
        'Referer':        'https://archivebate.com/',
    }
)

lw_data = lw_resp.json()
fragment = lw_data['effects']['html']   # HTML string to parse with BeautifulSoup
new_memo = lw_data['serverMemo']        # save this for pagination (next page call)
```

### Parsing the HTML fragment

```python
soup = utils.parse_html(fragment)
for item in soup.select('section.video_item'):
    link  = item.select_one('a[href*="/watch/"]')
    thumb = item.select_one('video.video-splash-mov')
    name  = item.select_one('a[href*="/profile/"]')
    dur   = item.select_one('.duration span')

    url   = link['href']                          # absolute URL already
    image = thumb.get('poster', '') if thumb else ''
    title = name.text.strip() if name else ''
    # dur.text.strip() gives e.g. '14:01' or '1:48:44'
```

**Confirmed selectors (36 items returned per page):**

| Field | Selector | Attribute/method |
|---|---|---|
| URL | `a[href*="/watch/"]` | `href` (already absolute) |
| Thumbnail | `video.video-splash-mov` | `poster` attr |
| Performer name | `a[href*="/profile/"]` | `.text.strip()` |
| Duration | `.duration span` | `.text.strip()` |

---

## Pagination — TODO (needs one more sniff session)

The `new_memo['data']` key came back `{}` in testing, which suggests **infinite scroll**
(Livewire `loadMore` pattern) rather than numbered pages.

**To figure out pagination**, run:
```bash
python scripts/codegen.py https://archivebate.com/ --sniff
```
Then scroll to the bottom of the page. The `[API]` output will show the next Livewire call.
Look for:
- The method name (likely `loadMore` or `loadVideos` with a page param)
- Any `page` or `cursor` value in the payload
- The updated `serverMemo` in the response (this becomes the state for the next call)

**Expected pattern** (guessed, needs confirmation):
```python
# Subsequent pages — pass updated serverMemo from previous response
payload = {
    "fingerprint": wire_state['fingerprint'],
    "serverMemo":  new_memo,          # from previous response
    "updates": [{
        "type": "callMethod",
        "payload": {"id": "x2", "method": "loadMore", "params": []}
        # OR: {"method": "loadVideos", "params": [2]}  -- if page-number based
    }]
}
```

---

## Other Listing URLs

These follow the same Livewire pattern but with a different component name:

| URL | Livewire component | Notes |
|---|---|---|
| `/` | `home-videos` | Latest videos |
| `/platform/Y2hhdHVyYmF0ZQ==` | unknown | Chaturbate only (base64 encoded) |
| `/platform/c3RyaXBjaGF0` | unknown | Stripchat only |
| `/gender/...` | unknown | Gender-filtered |

The base64 values decode to the platform name. Other platforms to check: Camsoda, OnlyFans, TikTok.

---

## Implementation Plan

### Files to create
- `plugin.video.cumination/resources/lib/sites/archivebate.py`
- `tests/fixtures/sites/archivebate_list.html` — save the Livewire fragment HTML
- `tests/fixtures/sites/archivebate_video.html` — copy of `/tmp/archivebate_video.html`
- `tests/sites/test_archivebate.py`

### Add to `__init__.py`
```python
# in resources/lib/sites/__init__.py __all__ list
'archivebate',
```

### Rough module skeleton

```python
site = AdultSite('archivebate', '[COLOR hotpink]Archivebate[/COLOR]',
                 'https://archivebate.com/', 'archivebate.png', 'archivebate')

def _livewire_list(url, method='loadVideos', params=None, memo=None):
    """Fetch a Livewire-rendered video listing. Returns (html_fragment, new_memo)."""
    import requests, json, html as htmlmod
    session = requests.Session()
    session.headers.update({'User-Agent': utils.USER_AGENT})

    resp = session.get(url)
    csrf = re.search(r'<meta name="csrf-token" content="([^"]+)"', resp.text).group(1)

    match = re.search(r'wire:initial-data="([^"]+)"[^>]*wire:init="loadVideos"', resp.text)
    if not match:
        return None, None
    wire_state = json.loads(htmlmod.unescape(match.group(1)))

    payload = {
        "fingerprint": wire_state['fingerprint'],
        "serverMemo":  memo or wire_state['serverMemo'],
        "updates": [{"type": "callMethod",
                     "payload": {"id": "lw1", "method": method,
                                 "params": params or []}}]
    }
    lw_resp = session.post(
        'https://archivebate.com/livewire/message/' + wire_state['fingerprint']['name'],
        json=payload,
        headers={'X-CSRF-TOKEN': csrf, 'X-Livewire': 'true',
                 'Accept': 'application/json', 'Referer': url}
    )
    data = lw_resp.json()
    return data['effects']['html'], data.get('serverMemo')


@site.register(default_mode=True)
def Main():
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    fragment, _memo = _livewire_list(url)
    if not fragment:
        utils.eod()
        return
    soup = utils.parse_html(fragment)
    for item in soup.select('section.video_item'):
        link  = item.select_one('a[href*="/watch/"]')
        thumb = item.select_one('video.video-splash-mov')
        name  = item.select_one('a[href*="/profile/"]')
        if not link:
            continue
        site.add_download_link(
            name.text.strip() if name else 'Video',
            link['href'],
            'Playvid',
            thumb.get('poster', '') if thumb else '',
        )
    # TODO: add pagination once loadMore mechanics are confirmed
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    soup = utils.parse_html(utils.getHtml(url, site.url))
    iframe = soup.select_one('iframe.video-frame')
    if iframe and iframe.get('src'):
        vp.play_from_link_to_resolve(iframe['src'])
        return
    vp.play_from_link_to_resolve(url)
```

---

## Known Issues / Gotchas

- `requests` is used directly (not `utils.getHtml`) because we need `requests.Session` for cookies.
  This is fine for Kodi — `requests` is available via `script.module.requests`.
- The Livewire `fingerprint.id` changes every page load — don't hardcode it.
- The CSRF token and session cookie expire; always fetch fresh on each `List()` call.
- MixDrop links sometimes require ResolveURL to be configured (user may need to enable the
  MixDrop resolver in ResolveURL settings).
- `video.video-splash-mov` `poster` is a `.jpg` thumbnail — works fine in Kodi.
