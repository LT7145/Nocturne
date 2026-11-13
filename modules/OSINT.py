import argparse
import re 
import requests 


from scrapling.fetchers import Fetcher, StealthySession, AsyncFetcher

def social_media(url: str, stealthy: bool = False) -> set[str]:
    page = StealthyFetcher.fetch(url) if stealthy else Fetcher.get(url)

    response_info = {
        'status': page.status,
        'reason': page.reason,
        'cookies': page.cookies,
        'headers': page.headers,
        'request_headers': page.request_headers,
        'history': page.history,
        'body': page.body,
        'encoding': page.encoding,
        'meta': page.meta,
    }

    url = response_info
    return url

output = social_media("https://www.instagram.com/")
output 