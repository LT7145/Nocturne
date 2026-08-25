import requests
import argparse
import json
import re
import sys
import time
import hashlib
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
import mmh3

# Constants
NVD_API_BASE   = "https://services.nvd.nist.gov/rest/json/cves/2.0"
SHODAN_CVEDB   = "https://cvedb.shodan.io/cves"      # free, no key, CPE-based
NVD_API_KEY    = None              # set to bump rate limit ~5 -> ~50 per 30s
RATE_DELAY     = 6.0               # seconds between unauthenticated NVD calls
CISA_DATABASE  = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
USER_AGENT     = "Nocturne-CVEScanner/1.0"



if __init__ == "__main__"
