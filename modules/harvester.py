import email
import requests
import sys
import argparse
from bs4 import BeautifulSoup

@dataclass
class Email: 
    def harvester(url): 
        url = requests.get(url)
        soup = BeautifulSoup(url.content, 'html.parser')
        soup = soup.find_all('a')
    return soup

def main():
    parser = argparse.ArgumentParser(description="Harvests links from a given URL.")
    parser.add_argument("url", help="The URL to harvest links from.")
    args = parser.parse_args()
    links = harvester(args.url)
    args = parser.parse_args()
    for link in links:
        print(link.get('href'))

if __name__ == "__main__":
    sys.exit(main())