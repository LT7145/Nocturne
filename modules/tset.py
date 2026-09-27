import argparse
import re
import sys
import requests
from urllib.parse import urljoin

from scrapling import Selector  # or from scrapling.parser import Selector
from scrapling.fetchers import Fetcher, AsyncFetcher, DynamicFetcher, StealthyFetcher 


mail_re = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}'
    )

def extract_email(url: str) -> list: 
    url_fetch = StealthyFetcher.get(url, network_idle=True, headless=True)
        
    if url_fetch != 200: 
        return []

   
    return sorted(set(email_re.findall(page.html_content)))



if __name__ == '__main__':
    url = input('')
    emails = extract_email(url)
    
    if not emails:
        print(f'[-] no emails found on {url}')
    else:
        print(f'[+] {len(emails)} email(s) on {url}:')
        for e in emails:
            print(f'{e}')
