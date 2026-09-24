import re
from scrapling.fetchers import (
    Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher,
    FetcherSession, AsyncStealthySession, StealthySession, DynamicSession, AsyncDynamicSession
)

#<a href="tel:+13154433611">315.443.3611</a>
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

print(phone_harvester(
    "https://www.crowdstrike.com/en-us/contact-us/",
    stealthy=True,
))