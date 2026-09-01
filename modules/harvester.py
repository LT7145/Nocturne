import email
import requests
import sys
import argparse
from bs4 import BeautifulSoup

def harvest_links(url): 
    url = requests.get(url)
    soup = BeautifulSoup(url.content, 'html.parser')
    soup = soup.find_all('a')
    return soup

def harvest_email(url):
    url = requests.get(url)
    email = BeautifulSoup(url.content, 'html.parser')
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    output = soup.find_all(string=re.compile(email_pattern))
    return output

def main(argv=None):
    parser = argparse.ArgumentParser(description="Harvests links from a given URL.")
    parser.add_argument("url", help="The URL to harvest links from.")
    args = parser.parse_args()
    links = harvester(args.url)
    args = parser.parse_args()
    for link in links:
        print(link.get('href'))

if __name__ == "__main__":
    sys.exit(main())
