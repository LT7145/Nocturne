<<<<<<< HEAD
#!/usr/bin/env python3

import argparse
import re
import sys
from urllib.parse import urljoin

from scrapling import Selector  # or from scrapling.parser import Selector
from scrapling.fetchers import Fetcher, AsyncFetcher, DynamicFetcher, StealthyFetcher

=======
import re
import argparse
from scrapling.fetchers import (
    Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher,
    FetcherSession, AsyncStealthySession, StealthySession, DynamicSession, AsyncDynamicSession
)

def harvest_emails(url: str, stealthy: bool = False) -> set[str]:

    emailRE = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
    
    page = StealthyFetcher.fetch(url) if stealthy else Fetcher.get(url)
    emails = set() 

    for href in page.css('a[href*="mailto:"]::attr(href)').getall():
        em = href.replace('mailto:', '').strip()
        if emailRE.fullmatch(em):
            emails.add(em)
            
    return emails 

def phone_harvester(url: str, stealthy: bool = False) -> set[str]:
    
    page = StealthyFetcher.fetch(url) if stealthy else Fetcher.get(url)
    REGEX = re.compile(r"\D") 

    phones = set()

    for href in page.css('a[href*="tel:"]::attr(href)'):
        result = str(href).replace("tel:","Phone Number: ").strip()
        digits = REGEX.sub("", result)
        if 7 <= len(digits) <= 15:
            phones.add(result)

    return phones

def main(argv=None):
>>>>>>> d6b6adb5986a34cd4de97280b225efa18c4dfbd2
