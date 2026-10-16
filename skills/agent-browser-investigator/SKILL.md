---
name: agent-browser-investigator
description: Fast, token-efficient browser investigation workflow using vercel-labs/agent-browser. Use when exploring new sites, debugging broken scrapers, clicking past age gates/modals, or inspecting dynamic JS elements without context blowup.
---

# Agent-Browser Site Investigator

> **agent-browser is a dev/debug tool only.** Never use it inside site modules — it is not available in the Kodi runtime. Site modules must use standard HTTP requests and `BeautifulSoup4`.

`agent-browser` (from Vercel Labs) provides a fast, token-efficient browser automation CLI driven by Chrome DevTools Protocol (CDP). Unlike dumping raw HTML or heavy DOM trees, `agent-browser snapshot -i` returns a compact accessibility tree where interactive elements are tagged with short references (e.g. `[ref=e1]`).

---

## When to Reach for `agent-browser`

| Situation | Why use `agent-browser`? |
|---|---|
| **Exploring new sites** | Inspect video cards, categories, and pagination with minimal token usage. |
| **Bypassing age gates / modals** | Click past "I am 18+" or cookie modals using `@ref` tags before inspecting the page. |
| **Investigating broken scrapers** | Verify if a site changed its DOM structure or card selectors without dumping megabytes of HTML. |
| **Locating dynamic stream elements** | Probe `<video>`, `<iframe>`, or player play buttons interactively. |

---

## Quick Start via `site_tool.py`

The repository provides a pre-configured wrapper that opens the URL, takes an interactive snapshot with URLs, and cleanly shuts down the session:

```bash
# Basic inspection (interactive elements + URLs)
python scripts/site_tool.py agent-inspect https://example.com/videos

# Scope inspection to specific CSS container (e.g. video cards)
python scripts/site_tool.py agent-inspect https://example.com/videos --selector ".video-item"

# Click an element (e.g. age verification button) before snapshotting
python scripts/site_tool.py agent-inspect https://example.com/videos --click "@e1"

# Save screenshot while probing
python scripts/site_tool.py agent-inspect https://example.com/videos --screenshot debug.png

# Keep browser open for follow-up CLI interactions
python scripts/site_tool.py agent-inspect https://example.com/videos --keep-open
```

---

## Direct Interactive CLI Workflow

For deeper interactive debugging, use the `agent-browser` CLI directly (via local npm script or `npx`):

```bash
# Windows
scripts\node_modules\.bin\agent-browser.cmd <command>

# Linux / macOS / cross-platform
npx agent-browser <command>
```

### 1. Open the page
```bash
npx agent-browser open https://example.com/video/123
```

### 2. Take a compact snapshot
```bash
# Interactive elements only with URLs (recommended for AI agents to save tokens)
npx agent-browser snapshot -i -u

# Scope to a specific selector or limit depth
npx agent-browser snapshot -i -u -s "#main-content" -d 4
```
**Example Output:**
```
- button "Enter (18+)" [ref=e1]
- link "Trending" [ref=e2, url=https://example.com/trending]
- link "Big Buck Bunny" [ref=e3, url=https://example.com/watch/123]
```

### 3. Interact via refs
```bash
# Click a button (e.g. age verification or play button)
npx agent-browser click @e1

# Wait for dynamic DOM update
npx agent-browser wait 2000

# Retake snapshot after interaction
npx agent-browser snapshot -i -u
```

### 4. Inspect specific element HTML
```bash
# Extract the outer HTML of a specific element ref
npx agent-browser get html @e3

# Extract text content
npx agent-browser get text @e3
```

### 5. Always close when finished
```bash
npx agent-browser close
```

---

## Comparison: `agent-browser` vs `playwright-inspect`

| Feature | `agent-browser` | `playwright-inspect` (`codegen.py`) |
|---|---|---|
| **Primary focus** | Token-efficient AI agent CLI inspection | Headed manual human debugging with ad-blocking |
| **Output format** | Compact accessibility snapshot (`@e1`, `@e2`) | Raw DOM / DevTools window |
| **Context token impact** | Minimal (~200–800 tokens) | High (if dumping HTML) |
| **Stream Sniffing** | Manual inspection / CDP requests | Built-in regex stream sniffer (`--sniff`) |

---

## Hand-off to Kodi Scraper Implementation

Once you identify the site's layout:
1. **Cards & Selectors**: Use the extracted selectors to build `SoupSiteSpec` (e.g., `container_selector`, `title_selector`, `url_selector`).
2. **Fixture capture**: Save representative HTML using `python scripts/agent_browser_probe.py <url> --dump-html tests/fixtures/sites/<site>_list.html`.
3. **Scraper & Tests**: Implement the site module in `plugin.video.cumination/resources/lib/sites/` and unit test in `tests/sites/test_<site>.py`.
4. Refer to `kodi-site-maintenance` and `bs4-migration-toolkit` skills for coding standards.
