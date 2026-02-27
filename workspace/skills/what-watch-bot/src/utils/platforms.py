"""
platforms.py — Utility module for streaming platform URL generation.

Each platform handles URL-encoded query strings differently:
- quote_plus: spaces → '+' (good for: YouTube, Amazon, Netflix)
- quote:       spaces → '%20' (good for: Rakuten, Disney+, Apple TV+, most others)
- raw:         no encoding (good for: RaiPlay fragment URLs)
"""

from urllib.parse import quote, quote_plus


# Normalize redundant TMDB provider names to their canonical display name.
# Deduplication in get_watch_providers() uses the canonical name,
# so aliases pointing to the same name are automatically collapsed.
PROVIDER_ALIASES = {
    "Netflix with Ads":                  "Netflix",
    "Amazon Prime Video with Ads":       "Amazon Prime Video",
    "Infinity Selection Amazon Channel": "Amazon Prime Video",
    "Prime Video":                       "Amazon Prime Video",
    "Amazon Video":                      "Amazon Prime Video",
}

# Centralized registry acting as our Single Source of Truth for platforms.
# Contains all necessary metadata used by the TMDB API, the bot UI, and URL builders.
SUPPORTED_PLATFORMS = [
    # SUBSCRIPTION
    {"name": "Netflix",            "id": 8,   "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://www.netflix.com/search?q={quote_plus(t)}"},
    {"name": "Amazon Prime Video", "id": 119, "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://www.primevideo.com/search/ref=atv_sr_sug_7?phrase={quote(t, safe='')}"},
    {"name": "Disney+",            "id": 337, "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://www.disneyplus.com/search/{quote(t, safe='')}"},
    {"name": "Apple TV+",          "id": 350, "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://tv.apple.com/it/search?term={quote(t, safe='')}"},
    {"name": "NOW TV",             "id": 39,  "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://www.nowtv.it/ricerca?q={quote(t, safe='')}"},
    {"name": "Paramount+",         "id": 531, "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://www.paramountplus.com/it/search/{quote(t, safe='')}/"},
    {"name": "YouTube Premium",    "id": 188, "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://www.youtube.com/results?search_query={quote_plus(t)}"},
    {"name": "MUBI",               "id": 11,  "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://mubi.com/it/search?query={quote(t, safe='')}"},
    {"name": "TIMvision",          "id": 109, "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://www.timvision.it/search?q={quote(t, safe='')}"},
    {"name": "Sky Go",             "id": 29,  "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://skygo.sky.it/search/{quote(t, safe='')}"},
    {"name": "Infinity+",          "id": 110, "tier": "SUBSCRIPTION", "url_builder": lambda t: f"https://mediasetinfinity.mediaset.it/search/keyword/{quote(t, safe='')}"},

    # FREE
    {"name": "RaiPlay",            "id": 613, "tier": "FREE",         "url_builder": lambda t: f"https://www.raiplay.it/ricerca.html#{quote(t, safe='')}"},
    {"name": "Mediaset Infinity",  "id": 359, "tier": "FREE",         "url_builder": lambda t: f"https://mediasetinfinity.mediaset.it/search/keyword/{quote(t, safe='')}"},
    {"name": "YouTube",            "id": 192, "tier": "FREE",         "url_builder": lambda t: f"https://www.youtube.com/results?search_query={quote_plus(t)}"},
    {"name": "Rakuten TV",         "id": 35,  "tier": "FREE",         "url_builder": lambda t: f"https://www.rakuten.tv/it/search?q={quote(t, safe='')}"},
    {"name": "Pluto TV",           "id": 300, "tier": "FREE",         "url_builder": lambda t: f"https://pluto.tv/it/search?q={quote(t, safe='')}"},
    {"name": "Plex",               "id": 538, "tier": "FREE",         "url_builder": lambda t: f"https://app.plex.tv/desktop/#!/search?query={quote(t, safe='')}"},
]

# Backwards compatibility and fast O(1) lookups for the URL builders.
_PLATFORM_URL_BUILDERS = {p["name"]: p["url_builder"] for p in SUPPORTED_PLATFORMS}


def build_platform_url(raw_name: str, title: str) -> str | None:
    """
    Given a raw TMDB provider name and a title string, return a search URL
    for that platform. Returns None if the platform is not in the registry.

    Aliases are resolved before lookup so variants like 'Amazon Prime Video with Ads'
    still get the correct Amazon URL.
    """
    canonical = PROVIDER_ALIASES.get(raw_name, raw_name)
    builder = _PLATFORM_URL_BUILDERS.get(canonical)
    return builder(title) if builder else None


def normalize_provider_name(raw_name: str) -> str:
    """Return the canonical display name for a TMDB provider, resolving aliases."""
    return PROVIDER_ALIASES.get(raw_name, raw_name)
