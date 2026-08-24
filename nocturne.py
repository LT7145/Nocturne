#!/usr/bin/env python3
import sys

from modules import web_enumerator, art, social

VERSION = "1.1"

BANNER = r"""
 _   _            _
| \ | | ___   ___| |_ _   _ _ __ _ __   ___
|  \| |/ _ \ / __| __| | | | '__| '_ \ / _ \
| |\  | (_) | (__| |_| |_| | |  | | | |  __/
|_| \_|\___/ \___|\__|\__,_|_|  |_| |_|\___|
             Multi-reconnaissance toolkit  v: {v}
""".format(v=VERSION)


# module name -> (help text, handler that takes the remaining argv list)
# add a new tool: drop it in modules/, import it above, add one line here.
MODULES = {
    "web": ("web enumeration (subdomains / directories)", web_enumerator.main),
    "art": ("print the nocturne mascot", art.main),
    "social": ("social media enumeration (instagram/reddit/twitter/facebook/telegram/mastodon)", social.main),
}


def print_usage():
    print("usage: nocturne <module> [options]\n")
    print("modules:")
    for name, (desc, _) in MODULES.items():
        print(f"  {name:<8} {desc}")
    print("\noptions:")
    print("  -h, --help     show this message")
    print("  -V, --version  show the nocturne version")
    print("\nrun 'nocturne <module> -h' for a module's options")


def main():
    print(BANNER, file=sys.stderr)  # stderr so piped stdout / -o stay clean
    argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        print_usage()
        sys.exit(0 if argv else 1)

    if argv[0] in ("-V", "--version"):
        print(f"nocturne {VERSION}")
        return

    cmd, rest = argv[0], argv[1:]
    if cmd not in MODULES:
        print(f"[!] unknown module '{cmd}'\n")
        print_usage()
        sys.exit(1)

    _, handler = MODULES[cmd]
    handler(rest)  # hands the args after the module name to that tool


if __name__ == "__main__":
    main()
