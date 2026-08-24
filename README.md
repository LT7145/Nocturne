<p align="center">
    <picture>
        <img src="config/bridy.png" alt="Nocturne" width='400' />
    </picture>
<p>

# Nocturne

Nocturne, Python-based reconnaissance toolkit for security research, CTFs, authorized penetration testing. Bringing multiple recon capabilities together under a single CLI, rather than seperate tools of enumeration

# Features
* Unified CLI for multiple recon modules (`web`, `social`)
*  Fast, configurable, and scriptable for automation
*  Built for CTF and security research use cases
*  Status output goes to stderr, results to stdout - safe to pipe

# Requirements
* Python 3.8+
* pip

# Installation

Clone the repository:
```bash
git clone https://github.com/LT7145/Nocturne.git
```
Install dependencies:
```bash
cd Nocturne
pip install -r requirements.txt
```
Verify:
```bash
python3 nocturne.py --help
```
Nocturne currently runs from the repository directory; there is no packaged
`nocturne` entry point yet.

# Usage
```bash
python3 nocturne.py <module> [options]
```
Run `python3 nocturne.py --help` to list modules, or `python3 nocturne.py <module> -h` for a
module's own options.

## web - subdomain and directory enumeration
The target is positional; `sub` and `dir` are the available modes. Subdomain enumeration:
```bash
python3 nocturne.py web example.com -m sub -w wordlists/subs.txt -c 200,301,403
```
Directory enumeration:
```bash
python3 nocturne.py web https://example.com -m dir -w wordlists/dirs.txt -t 25 -o found.txt
```

## social - social media enumeration
Wraps the [snscrape](https://github.com/JustAnotherArchivist/snscrape) scrapers behind a
`<platform> [mode] <target>` CLI. The mode is optional and falls back to the platform default:
```bash
python3 nocturne.py social --list                    # all platforms and modes
python3 nocturne.py social instagram user natgeo
python3 nocturne.py social reddit subreddit netsec --limit 50
python3 nocturne.py social telegram durov            # 'channel' is the default mode
python3 nocturne.py social mastodon profile @Gargron@mastodon.social
python3 nocturne.py social twitter user jack --entity
```
`--limit N` stops after N results; `--entity` prints the profile/channel summary instead of
the feed.

> **Note:** snscrape is no longer maintained and the platforms it targets actively block
> scraping, so several of these scrapers may fail against live targets. Nocturne reports
> such failures as `[!] <platform> <mode> failed: ...` and exits non-zero.

## art
```bash
python3 nocturne.py art
```

# Contributing 
Issues and pull requests are welcomed. Please open an issue to discuss changes before submitting PR

# Disclaimer
Nocturne is intended for authorized security testing and educational purposes. Please do not use it against systems you do not own or have explicit permission to test

# License
MIT - see [LICENSE](LICENSE).

The `social` module depends on [snscrape](https://github.com/JustAnotherArchivist/snscrape),
which is licensed separately under the GPL-3.0. It is installed as a dependency, not
bundled with this repository.
