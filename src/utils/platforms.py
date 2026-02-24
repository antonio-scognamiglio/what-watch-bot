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
}

# Per-platform URL builder functions.
# Each lambda takes a title string (already a raw Python string) and returns a full URL.
# Space encoding strategy is chosen per-platform based on their search query behaviour.
_PLATFORM_URL_BUILDERS = {
    "Netflix": lambda t: f"https://www.netflix.com/search?q={quote_plus(t)}",

    # primevideo.com handles both + and %20 but %20 is cleaner in the address bar
    "Amazon Prime Video": lambda t: f"https://www.primevideo.com/search/ref=atv_sr_sug_7?phrase={quote(t, safe='')}",

    # Disney+ uses a path segment, must be %20
    "Disney+": lambda t: f"https://www.disneyplus.com/search/{quote(t, safe='')}",

    # Apple TV+ uses term= param, %20 preferred
    "Apple TV+": lambda t: f"https://tv.apple.com/it/search?term={quote(t, safe='')}",

    # NOW TV uses q= param with %20 style
    "NOW TV": lambda t: f"https://www.nowtv.it/ricerca?q={quote(t, safe='')}",

    # Rakuten uses q= param, %20 style (+ incorrectly shows as literal + in their UI)
    "Rakuten TV": lambda t: f"https://www.rakuten.tv/it/search?q={quote(t, safe='')}",

    # Mediaset uses a path segment
    "Mediaset Infinity": lambda t: f"https://mediasetinfinity.mediaset.it/search/keyword/{quote(t, safe='')}",

    # RaiPlay uses a fragment (#), browsers don't encode the fragment — raw spaces are fine
    "RaiPlay": lambda t: f"https://www.raiplay.it/ricerca.html#{quote(t, safe='')}",

    # Pluto TV uses q= param with %20
    "Pluto TV": lambda t: f"https://pluto.tv/it/search?q={quote(t, safe='')}",

    # Plex uses query= param with %20
    "Plex": lambda t: f"https://app.plex.tv/desktop/#!/search?query={quote(t, safe='')}",

    # MUBI uses query= param with %20
    "MUBI": lambda t: f"https://mubi.com/it/search?query={quote(t, safe='')}",

    # YouTube search_query= officially supports + encoding
    "YouTube": lambda t: f"https://www.youtube.com/results?search_query={quote_plus(t)}",
    "YouTube Premium": lambda t: f"https://www.youtube.com/results?search_query={quote_plus(t)}",

    # Paramount+ uses a path segment
    "Paramount+": lambda t: f"https://www.paramountplus.com/it/search/{quote(t, safe='')}/",
}


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
