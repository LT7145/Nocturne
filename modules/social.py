"""
social.py — nocturne social-media enumeration dispatcher.

The platform modules (instagram, reddit, twitter, facebook, telegram, mastodon)
are snscrape scraper libraries. They don't expose a main(); instead each defines
one or more Scraper subclasses that share a common interface:

    scraper = SomeScraper(target)
    for item in scraper.get_items():
        print(item)

This module maps a friendly "<platform> <mode>" CLI onto those classes, runs the
scraper, and streams results to stdout (so `-o file` / piping stays clean).

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

import sys

from modules import instagram, reddit, twitter, facebook, telegram, mastodon


# platform -> { mode: (ScraperClass, "help blurb") }
# The first mode listed for each platform is its default.
REGISTRY = {
    "instagram": {
        "user":     (instagram.InstagramUserScraper,     "posts from a username (no leading @)"),
        "hashtag":  (instagram.InstagramHashtagScraper,  "posts for a hashtag (no leading #)"),
        "location": (instagram.InstagramLocationScraper, "posts for a numeric location ID"),
    },
    "reddit": {
        "user":       (reddit.RedditUserScraper,       "submissions + comments by a user"),
        "subreddit":  (reddit.RedditSubredditScraper,  "submissions + comments in a subreddit"),
        "search":     (reddit.RedditSearchScraper,     "submissions + comments matching a query"),
        "submission": (reddit.RedditSubmissionScraper, "a single submission by ID + its comments"),
    },
    "twitter": {
        "user":     (twitter.TwitterUserScraper,     "tweets from a username (no leading @)"),
        "profile":  (twitter.TwitterProfileScraper,  "tweets + replies from a profile"),
        "search":   (twitter.TwitterSearchScraper,   "tweets matching a search query"),
        "hashtag":  (twitter.TwitterHashtagScraper,  "tweets for a hashtag (no leading #)"),
    },
    "facebook": {
        "user":      (facebook.FacebookUserScraper,      "posts from a user/page"),
        "community": (facebook.FacebookCommunityScraper, "posts from a community"),
        "group":     (facebook.FacebookGroupScraper,     "posts from a group ID"),
    },
    "telegram": {
        "channel": (telegram.TelegramChannelScraper, "posts from a public channel"),
    },
    "mastodon": {
        "profile": (mastodon.MastodonProfileScraper, "toots from @user@instance or a profile URL"),
        "toot":    (mastodon.MastodonTootScraper,    "a single toot by URL"),
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


def _print_usage():
    print("usage: nocturne social <platform> [mode] <target> [--limit N] [--entity]\n")
    print("platforms and modes:")
    for platform, modes in REGISTRY.items():
        default = DEFAULT_MODE[platform]
        print(f"  {platform}")
        for mode, (_cls, blurb) in modes.items():
            tag = "  (default)" if mode == default else ""
            print(f"      {mode:<11} {blurb}{tag}")
    print("\nexamples:")
    print("  nocturne social instagram user natgeo")
    print("  nocturne social reddit subreddit netsec --limit 50")
    print("  nocturne social telegram durov")
    print("  nocturne social mastodon profile @Gargron@mastodon.social")


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
    if not argv or argv[0] in ("-h", "--help", "--list"):
        _print_usage()
        return

    platform = argv[0].lower()
    if platform not in REGISTRY:
        print(f"[!] unknown platform '{platform}'\n", file=sys.stderr)
        _print_usage()
        sys.exit(1)

    rest = argv[1:]
    modes = REGISTRY[platform]

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
    scraper_cls, _blurb = modes[mode]

    try:
        _run(scraper_cls, target, opts)
    except Exception as e:  # noqa: BLE001 — surface scraper errors cleanly to the CLI
        print(f"[!] {platform} {mode} failed: {e}", file=sys.stderr)
        sys.exit(1)
