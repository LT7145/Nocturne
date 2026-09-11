#!/usr/bin/env python3

import argparse
import re
import sys
from urllib.parse import urljoin

from scrapling import Selector  # or from scrapling.parser import Selector
from scrapling.fetchers import Fetcher, AsyncFetcher, DynamicFetcher, StealthyFetcher


def extract_email(url: str) -> list: 
    url_fetch = StealthyFetcher.fetch(url, real_chrome=True)
    email = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}')
    if page_status != 200: 
        return []
    obtained = email.finall(page.body)
    return sorted({e.lower() for e in found})

def enumerate_emails(url: ) 


def main(argv=None): 
    parser = argparse.ArgumentParser(prog='Web Scraper', description='Input the URL and selec    t the flag to begin') 
    parser.add_argument("url", help="url/domain e.g https://example.com")
    parser.add_arguemnt("-e", "--email")    

if __name__ == "__main__":
    main() 
