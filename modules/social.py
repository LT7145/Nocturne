"""
social.py — nocturne social-media enumeration dispatcher.

The platform scrapers come from snscrape (https://github.com/JustAnotherArchivist/snscrape),
installed as a dependency — see requirements.txt. snscrape doesn't expose a main();
instead each of its modules defines Scraper subclasses sharing a common interface:

    scraper = SomeScraper(target)
    for item in scraper.get_items():
        print(item)

This module maps a friendly "<platform> <mode>" CLI onto those classes, runs the
scraper, and streams results to stdout (so `-o file` / piping stays clean).

snscrape is imported lazily, only once a platform is actually selected, so the rest of
nocturne keeps working when it isn't installed.

Usage:
    nocturne social <platform> [mode] <target> [--limit N] [--entity]

Examples:
    nocturne social instagram user natgeo
    nocturne social instagram natgeo                # 'user' is the default mode
    nocturne social reddit user someuser
    nocturne social reddit subreddit netsec
    nocturne social twitter user jack
    nocturne social telegram durov
    nocturne social facebook user somepage
    nocturne social mastodon profile @Gargron@mastodon.social
    nocturne social --list                          # show platforms/modes
"""

import importlib
import sys


# platform -> { mode: ("ScraperClassName", "help blurb") }
# Class names are strings, resolved against snscrape.modules.<platform> at dispatch
# time — see _resolve(). Keeps this table importable without snscrape present.
REGISTRY = {
    "instagram": {
        "user":     ("InstagramUserScraper",     "posts from a username (no leading @)"),
        "hashtag":  ("InstagramHashtagScraper",  "posts for a hashtag (no leading #)"),
        "location": ("InstagramLocationScraper", "posts for a numeric location ID"),
    },
    "reddit": {
        "user":       ("RedditUserScraper",       "submissions + comments by a user"),
        "subreddit":  ("RedditSubredditScraper",  "submissions + comments in a subreddit"),
        "search":     ("RedditSearchScraper",     "submissions + comments matching a query"),
        "submission": ("RedditSubmissionScraper", "a single submission by ID + its comments"),
    },
    "twitter": {
        "user":     ("TwitterUserScraper",     "tweets from a username (no leading @)"),
        "profile":  ("TwitterProfileScraper",  "tweets + replies from a profile"),
        "search":   ("TwitterSearchScraper",   "tweets matching a search query"),
        "hashtag":  ("TwitterHashtagScraper",  "tweets for a hashtag (no leading #)"),
    },
    "facebook": {
        "user":      ("FacebookUserScraper",      "posts from a user/page"),
        "community": ("FacebookCommunityScraper", "posts from a community"),
        "group":     ("FacebookGroupScraper",     "posts from a group ID"),
    },
    "telegram": {
        "channel": ("TelegramChannelScraper", "posts from a public channel"),
    },
    "mastodon": {
        "profile": ("MastodonProfileScraper", "toots from @user@instance or a profile URL"),
        "toot":    ("MastodonTootScraper",    "a single toot by URL"),
    },
}

# Where the default mode isn't just the first key, or where a platform has one
# obvious mode, spell out the default explicitly for clarity.
DEFAULT_MODE = {
    "instagram": "user",
    "reddit": "user",
    "twitter": "user",
    "facebook": "user",
    "telegram": "channel",
    "mastodon": "profile",
}

HELP_FLAGS = ("-h", "--help", "--list")


def _print_usage():
    print("usage: nocturne social <platform> [mode] <target> [--limit N] [--entity]\n")
    print("platforms and modes:")
    for platform, modes in REGISTRY.items():
        default = DEFAULT_MODE[platform]
        print(f"  {platform}")
        for mode, (_cls, blurb) in modes.items():
            tag = "  (default)" if mode == default else ""
            print(f"      {mode:<11} {blurb}{tag}")
    print("\noptions:")
    print("  --limit N, -n N   stop after N results")
    print("  --entity          print the profile/channel summary instead of the feed")
    print("\nexamples:")
    print("  nocturne social instagram user natgeo")
    print("  nocturne social reddit subreddit netsec --limit 50")
    print("  nocturne social telegram durov")
    print("  nocturne social mastodon profile @Gargron@mastodon.social")


def _resolve(platform, class_name):
    """Import snscrape.modules.<platform> and pull out the named scraper class."""
    try:
        module = importlib.import_module(f"snscrape.modules.{platform}")
    except ImportError as e:
        raise ImportError(
            f"the social module needs snscrape ({e}); "
            "install it with: pip install -r requirements.txt"
        ) from e
    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(
            f"snscrape has no {class_name} for '{platform}'; "
            "your installed version may not match requirements.txt"
        ) from e


def _parse_flags(rest):
    """Pull recognised flags out of the argv tail; return (positional, opts)."""
    positional = []
    opts = {"limit": None, "entity": False}
    i = 0
    while i < len(rest):
        arg = rest[i]
        if arg in ("--limit", "-n"):
            if i + 1 >= len(rest):
                raise ValueError(f"{arg} needs a number")
            try:
                opts["limit"] = int(rest[i + 1])
            except ValueError:
                raise ValueError(f"{arg} needs an integer, got {rest[i + 1]!r}")
            i += 2
        elif arg == "--entity":
            opts["entity"] = True
            i += 1
        else:
            positional.append(arg)
            i += 1
    return positional, opts


def _run(scraper_cls, target, opts):
    """Instantiate a scraper and stream its items to stdout."""
    scraper = scraper_cls(target)

    # --entity prints the profile/channel summary object instead of the feed,
    # for scrapers that support it (Instagram user, Telegram channel, etc.).
    if opts["entity"]:
        if opts["limit"] is not None:
            print("[!] --limit has no effect with --entity", file=sys.stderr)
        entity = scraper.entity  # snscrape.base.Scraper exposes this property
        if entity is None:
            print("[!] no entity info available for this target", file=sys.stderr)
        else:
            print(entity)
        return

    count = 0
    limit = opts["limit"]
    for item in scraper.get_items():
        print(item)  # each Item's __str__ is its canonical URL / identifier
        count += 1
        if limit is not None and count >= limit:
            break

    if count == 0:
        print("[!] no results (private/empty target, or scraper blocked)", file=sys.stderr)
    else:
        print(f"[+] {count} result(s)", file=sys.stderr)


def main(argv):
    if not argv or argv[0] in HELP_FLAGS:
        _print_usage()
        return

    platform = argv[0].lower()
    if platform not in REGISTRY:
        print(f"[!] unknown platform '{platform}'\n", file=sys.stderr)
        _print_usage()
        sys.exit(1)

    rest = argv[1:]
    modes = REGISTRY[platform]

    # nocturne's own usage points people at "nocturne <module> -h", so honour a help
    # flag anywhere in the tail rather than scraping a target literally named "-h".
    if any(arg in HELP_FLAGS for arg in rest):
        _print_usage()
        return

    # Second token is a mode only if it matches one; otherwise it's the target
    # and we fall back to the platform default (so `social telegram durov` works).
    if rest and rest[0] in modes:
        mode = rest[0]
        rest = rest[1:]
    else:
        mode = DEFAULT_MODE[platform]

    try:
        positional, opts = _parse_flags(rest)
    except ValueError as e:
        print(f"[!] {e}", file=sys.stderr)
        sys.exit(1)

    if not positional:
        print(f"[!] no target given for '{platform} {mode}'\n", file=sys.stderr)
        _print_usage()
        sys.exit(1)

    target = positional[0]
    class_name, _blurb = modes[mode]

    try:
        scraper_cls = _resolve(platform, class_name)
    except ImportError as e:
        print(f"[!] {e}", file=sys.stderr)
        sys.exit(1)

    try:
        _run(scraper_cls, target, opts)
    except Exception as e:  # noqa: BLE001 — surface scraper errors cleanly to the CLI
        print(f"[!] {platform} {mode} failed: {e}", file=sys.stderr)
        sys.exit(1)
