from scrapling import StealthyFetcher

DEFAULT_UA = "Mozilla/5.0 (Windows; U; Windows NT 5.2;. en-US) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.86 Safari/537.36 Quark/10.16.5.1140"

def get_user_agent(custom=None):
    return custom if custom else DEFAULT_UA

def scrape_profile(url: str) -> dict:
    """
    Fetches a profile page and extracts name/description.
    Returns a dict rather than a mashed-together string so callers
    can actually use the data.
    """
    page = StealthyFetcher.fetch(url=url, google_search=True, real_chrome=True)

    name_el = page.re_first("h2 span::text")
    desc_el = page.re_first("p span.description::text")

    name = name_el.strip() if name_el else None
    desc = desc_el.strip() if desc_el else None

    return {
        "url": url,
        "name": name,
        "description": desc,
    }

if __name__ == "__main__":
    result = scrape_profile("https://www.linkedin.com/in/laykyaw-tun/")
    print(result)