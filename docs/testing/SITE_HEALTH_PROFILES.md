# Site Health Profiles

`config/site_profiles.json` defines per-site expectations for broad smoke scans and strict priority site monitoring.

## Purpose

Profiles specify content type, FlareSolverr requirement, tier level, and strict contracts for the 17 core priority sites.

## Schema

```json
{
  "default": {
    "supports": {
      "main": true,
      "list": true,
      "categories": true,
      "search": true,
      "play": true
    },
    "content_type": "video",
    "requires_flaresolverr": false,
    "harness": {
      "playback_not_testable": false,
      "search_results_optional": false,
      "categories_optional": false
    },
    "strict_contract": {
      "min_video_items": 5,
      "min_unique_title_ratio": 0.8,
      "min_unique_url_ratio": 0.8,
      "max_count_drop_ratio": 0.7,
      "sample_count": 1,
      "allowed_hosts": [],
      "required_stages": ["listing", "playback", "media"],
      "advisory_fields": ["thumbnail", "description"]
    }
  },
  "sites": {
    "pornhub": {
      "tier": 1
    },
    "thothub": {
      "tier": 1
    }
  }
}
```

## Field Meanings

- `tier`: Priority marker. `1` indicates one of the 17 core priority sites subject to strict daily monitoring and issue automation.
- `strict_contract`:
  - `min_video_items`: Minimum number of video items required in a listing.
  - `min_unique_title_ratio`: Minimum ratio of unique titles required.
  - `min_unique_url_ratio`: Minimum ratio of unique item URLs required.
  - `max_count_drop_ratio`: Maximum allowed drop in item count compared to previous healthy baseline.
  - `allowed_hosts`: Explicit list of allowed domain names for video listing and media links.
  - `required_stages`: Stages that must pass for the run to be marked `HEALTHY` (`listing`, `playback`, `media`).
