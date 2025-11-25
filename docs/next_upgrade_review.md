# Next Upgrade Review

## Snapshot of Current State
- **BeautifulSoup migration**: 57 of 137 sites (41.6%) converted, Phase 4 (JAV) completed; Phase 5 (Hentai/Anime) and Phase 6 (International) have not started. 【F:MODERNIZATION.md†L7-L11】【F:MODERNIZATION.md†L68-L117】【F:MODERNIZATION.md†L161-L187】【F:MODERNIZATION.md†L189-L217】
- **Testing**: 19/19 tests passing, but overall coverage is ~7% with only 3 site-specific test files and 11 site fixtures. Coverage for migrated sites is inconsistent. 【F:PROJECT_STATUS.md†L25-L63】【F:PROJECT_STATUS.md†L86-L107】
- **Linting**: Ruff reports 96 issues, dominated by 78 bare `except:` blocks across core and site scrapers. 【F:PROJECT_STATUS.md†L109-L141】

## Release Readiness Risks
1. **Error handling debt**: Bare `except:` usage in basics.py, favorites.py, cloudflare.py, and multiple cam scrapers increases the odds of masking production errors. 【F:PROJECT_STATUS.md†L109-L141】
2. **Test coverage gaps**: Only 7% coverage and minimal site fixtures mean regressions in the 57 migrated sites may slip through CI. 【F:PROJECT_STATUS.md†L25-L63】【F:PROJECT_STATUS.md†L86-L107】
3. **Unfinished migrations**: Hentai/Anime and International categories are untouched; upstream HTML shifts will continue to break regex-based scrapers. 【F:MODERNIZATION.md†L7-L11】【F:MODERNIZATION.md†L189-L217】【F:MODERNIZATION.md†L219-L247】
4. **CI signal limited**: No coverage or linting gates in GitHub Actions; builds can pass with failing style and minimal regression detection. 【F:PROJECT_STATUS.md†L109-L141】【F:PROJECT_STATUS.md†L150-L171】

## Recommended Actions for the Next Upgrade
1. **Finish Phase 5 & 6 migrations**: Prioritize Hentai/Anime and International sites using the existing `SoupSiteSpec` + helper patterns. Target 10 sites per release to keep velocity manageable. 【F:MODERNIZATION.md†L68-L117】【F:MODERNIZATION.md†L189-L247】
2. **Add CI enforcement**: Extend GitHub Actions to run `ruff check --fix --exit-zero` as a reporting step initially, then enforce failures; add `pytest --cov` to publish coverage (even if non-blocking) to track growth. 【F:PROJECT_STATUS.md†L109-L141】【F:PROJECT_STATUS.md†L150-L171】
3. **Raise error handling quality**: Replace bare `except:` with `except Exception as exc:` patterns and log failures with site context; start with basics.py, favorites.py, cloudflare.py, and cam scrapers. 【F:PROJECT_STATUS.md†L109-L141】
4. **Expand fixtures and site tests**: Create a test template for migrated sites (listing + playback + pagination), and require at least one HTML fixture per migrated site. Aim to lift coverage from 7% to 20% by covering the 57 Soup sites first. 【F:PROJECT_STATUS.md†L25-L63】【F:PROJECT_STATUS.md†L86-L107】
5. **Plan HTTP gateway consolidation**: Define a unified `fetch_url()` with timeout/retry/UA defaults and a registry of Cloudflare-requiring hosts to simplify future scraper updates. 【F:PROJECT_STATUS.md†L143-L171】

## Success Metrics to Track
- **Migration pace**: 10 sites per release until Phases 5–7 reach 50% completion.
- **Quality gates**: Ruff error count drops from 96 to <30; bare `except:` eliminated from core modules.
- **Testing**: Coverage increases from 7% to 20%+, with fixture count matching migrated sites.
- **Stability**: Fewer scraper hotfixes between releases as BS4 coverage grows.
