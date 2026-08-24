#!/usr/bin/env python3
import sys
import argparse
from functools import partial
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import urllib3

DEFAULT_UA = "Mozilla/5.0 (compatible; Nocturne/1.0)"

def get_user_agent(custom=None):
    return custom if custom else DEFAULT_UA

def load_wordlist(fpath):
    try:
        with open(fpath, 'r', errors='ignore') as f:
            lst = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            print(f"[*] Loaded: {len(lst)}, from {fpath}")
            return lst
    except FileNotFoundError:
        print(f"[!] Error: '{fpath}' not found")
        return []
    except OSError as e:
        # a directory, a bad symlink, no read permission - same outcome, no wordlist
        print(f"[!] Error: cannot read '{fpath}': {e.strerror}")
        return []


def build_session(threads, verify=True, user_agent=None):
    # one session = reused TCP conns, way faster than a bare requests.get per word
    s = requests.Session()
    s.headers.update({"User-Agent": get_user_agent(user_agent)})
    s.verify = verify
    adapter = requests.adapters.HTTPAdapter(pool_connections=threads, pool_maxsize=threads)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


def split_scheme(target, scheme="https"):
    if target.startswith("http://"):
        scheme = "http"
        target = target[7:]  # since http:// = 7
    elif target.startswith("https://"):
        scheme = "https"
        target = target[8:]
    return scheme, target.strip("/")


def checking_subdomains(sub, session, domain, scheme="https", timeout=3):
    url = f"{scheme}://{sub}.{domain}"
    try:
        r = session.get(url, timeout=timeout, allow_redirects=False)
        return (url, r.status_code, r.headers.get("Location"))
    except requests.exceptions.RequestException:
        return None


def checking_paths(word, session, base, timeout=3):
    url = f"{base}/{word.lstrip('/')}"
    try:
        r = session.get(url, timeout=timeout, allow_redirects=False)
        return (url, r.status_code, r.headers.get("Location"))
    except requests.exceptions.RequestException:
        return None


def run_scan(fn, wordlist, threads, codes=None):
    found = []
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(fn, word): word for word in wordlist}
        try:
            for fut in as_completed(futures):
                result = fut.result()
                if not result:
                    continue
                url, code, loc = result
                if codes and code not in codes:
                    continue
                extra = f" -> {loc}" if loc else ""
                print(f"[+] Obtained: {code} Url: {url}{extra}")
                found.append((url, code))
        except KeyboardInterrupt:
            print("\n[!] Interrupted - cancelling remaining work")
            ex.shutdown(wait=False, cancel_futures=True)
    return found


def enumerate_subdom(domain, wordlist, scheme="https", threads=10, timeout=3, verify=True, codes=None,
                     user_agent=None):
    scheme, domain = split_scheme(domain, scheme)
    print(f"[*] Mode: subdomain enumeration - target: {scheme}://{domain}\n")
    session = build_session(threads, verify, user_agent)
    fn = partial(checking_subdomains, session=session, domain=domain, scheme=scheme, timeout=timeout)
    return run_scan(fn, wordlist, threads, codes)


def enumerate_dirs(target, wordlist, scheme="https", threads=10, timeout=3, verify=True, codes=None,
                   user_agent=None):
    scheme, host = split_scheme(target, scheme)
    base = f"{scheme}://{host}"
    print(f"[*] Mode: directory enumeration - target: {base}\n")
    session = build_session(threads, verify, user_agent)
    fn = partial(checking_paths, session=session, base=base, timeout=timeout)
    return run_scan(fn, wordlist, threads, codes)


def parse_codes(raw):
    if not raw or raw.lower() == "all":
        return None
    try:
        return {int(c) for c in raw.split(",") if c.strip()}
    except ValueError:
        print(f"[!] Error: bad status filter '{raw}'")
        sys.exit(1)


# argv=None -> argparse reads sys.argv (standalone run).
# nocturne.py passes the args after "web" as a list instead.
def main(argv=None):
    p = argparse.ArgumentParser(prog="nocturne web",
                                description="web enumeration (subdomains / directories)")
    p.add_argument("Example Command: nocturne web scanme.nmap.org -m sub -w wordlist")
    p.add_argument("target", help="domain or url, e.g. example.com or https://example.com")
    p.add_argument("-w", "--wordlist", required=True, help="path to wordlist")
    p.add_argument("-m", "--mode", choices=["sub", "dir"], default="sub", help="enumeration mode")
    p.add_argument("-t", "--threads", type=int, default=10, help="worker threads")
    p.add_argument("--timeout", type=float, default=3, help="per-request timeout in seconds")
    p.add_argument("-c", "--codes", default="all", help="status codes to show, e.g. 200,301,403 or 'all'")
    p.add_argument("-k", "--insecure", action="store_true", help="skip TLS verification (lab / self-signed)")
    p.add_argument("-A", "--user-agent", help=f"custom User-Agent (default: {DEFAULT_UA})")
    p.add_argument("-o", "--output", help="write found urls to file")
    args = p.parse_args(argv)

    if args.insecure:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    wordlist = load_wordlist(args.wordlist)
    if not wordlist:
        sys.exit(1)

    codes = parse_codes(args.codes)
    runner = enumerate_subdom if args.mode == "sub" else enumerate_dirs
    found = runner(args.target, wordlist, threads=args.threads, timeout=args.timeout,
                   verify=not args.insecure, codes=codes, user_agent=args.user_agent)

    print(f"\n[*] Done - {len(found)} hit(s)")

    if args.output:
        with open(args.output, "w") as f:
            for url, code in sorted(found):
                f.write(f"{code} {url}\n")
        print(f"[*] Written to {args.output}")


if __name__ == "__main__":
    main()
