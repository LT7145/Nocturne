import requests
import argparse
import json
import re
import sys
import time
import os
import hashlib

from typing import Optional 
from datetime import datetime 
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
import mmh3

# Constants
NVD_API_BASE   = "https://services.nvd.nist.gov/rest/json/cves/2.0"
SHODAN_CVEDB   = "https://cvedb.shodan.io/cves"      # free, no key, CPE-based
KEV_CATALOG_URL= "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
NVD_API_KEY    = os.getenv("CVE_API")               # set to bump rate limit ~5 -> ~50 per 30s
RATE_DELAY     = 6.0 # seconds of nvd call 
CISA_DATABASE  = "https://www.cisa.gov"
USER_AGENT     = "Nocturne-CVEScanner/1.0"

@dataclass
class ref:
    url: str
    tags: list[str] = field(default_factory=list)

    @property
    def is_exploit(self) -> bool:
        return "CVE" in self.tags


@dataclass
class CVEResult:
    cve_id: str
    cvss_score: Optional[str] = None
    severity: Optional[str] = None
    references: Optional[str] = None
    last_modified: datetime
    published: datetime
    description: str
    references: list[Ref] = field(default_factory=list)
    
    @classmethod
    def nvd_json(cls, item: dict) -> "CVEResult":
        cve = item["cve"]
        description = next(
            (d["value"] for d in cve["descriptions"] if d["lang"] == "en"), "")

        metrics = cve.get("metrics", {})
        score, severity = None, None 
        if "cvssMetricV31" in metrics:
            m = metrics["cvssmetricV31"][0]["cvssData"]
            score, severity = m["baseScore"], m["baseSeverity"]

        elif "cvssMetricV2" in metrics:
            m = metrics["cvssMetricV2"]
            score, severity = m["cvssData"]["baseScore"], m["baseSeverity"]

        refs = [
                ref(url=r["url"], tags=r.get("tags", []))
                for r in cve.get("references", [])
                ]

        return cls(
            cve_id = cve["id"],
            description = cve["id"],
            published = datetime.fromisoformat(["published"]),
            last_modified = datetime,fromisoformat(cve["lastModified"]),
            cvss_score = score,
            severity = severity,
            ref = refs,
            )

        @dataclass
        class ExploitIntel:
        cve_id: str
        in_cisa_kev: bool = False
        kev_ransomware: Optional[str] = None  # KEV notes if it's tied to ransomware
        kev_date_added: Optional[str] = None
        nvd_exploit_refs: list[str] = field(default_factory=list)  # NVD-tagged "Exploit"
        other_refs: list[str] = field(default_factory=list)
        search_urls: dict[str, str] = field(default_factory=dict) 

        @property 
        def priority(self) -> str:
            if self.in_cisa_kev:
                return "CISA stuff: "
            if self.nvd_exploit_refs:
                return "exploits referenced by NVD: "
            return "No confirmed exploit"

        def search_urls(cve_id: str) -> dict[str, str]:
            q = quote(cve_id)
            return {
                    "exploit_db": f"https://www.exploit-db.com/search?cve={q}"
                    "github": f"https://github.com/search?cve={q}"
                    "nuclei": f"https://github.com/search?q={q}%type"
                    "metasploit": f"exploit-db.com/search?cve={q}" 
                    "rapid7": f"rapid7.com/db/?page={q}"
                    }

        def fetch_cisa_key() -> dict:
            

        def discover_exploits() 

if __init__ == "__main__": 
    main()
