import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import quote, urljoin, urlparse

import mmh3
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Constants
NVD_API_BASE  = "https://services.nvd.nist.gov/rest/json/cves/2.0"
SHODAN_CVEDB  = "https://cvedb.shodan.io/cves"
CISA_DATABASE = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
NVD_API_KEY   = os.getenv("CVE_API")
RATE_DELAY    = 6.0 if not NVD_API_KEY else 0.7
USER_AGENT    = "Nocturne-CVEScanner/1.0"

HEADERS = {"User-Agent": USER_AGENT}
if NVD_API_KEY:
    HEADERS["apiKey"] = NVD_API_KEY


@dataclass
class Reference:
    url: str
    tags: list[str] = field(default_factory=list)

    @property
    def is_exploit(self) -> bool:
        return "Exploit" in self.tags


@dataclass
class CVEResult:
    cve_id: str
    description: str
    published: datetime
    last_modified: datetime
    cvss_score: Optional[float] = None
    severity: Optional[str] = None
    references: list[Reference] = field(default_factory=list)

    @classmethod
    def nvd_json(cls, item: dict) -> "CVEResult":
        cve = item["cve"]

        description = next(
            (d["value"] for d in cve.get("descriptions", []) if d["lang"] == "en"),
            "",
        )

        metrics = cve.get("metrics", {})
        score = severity = None

        for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30"):
            if metrics.get(key):
                data = metrics[key][0]["cvssData"]
                score, severity = data["baseScore"], data["baseSeverity"]
                break
        else:
            if metrics.get("cvssMetricV2"):
                entry = metrics["cvssMetricV2"][0]
                score = entry["cvssData"]["baseScore"]
                severity = entry.get("baseSeverity")

        refs = [
            Reference(url=r["url"], tags=r.get("tags", []))
            for r in cve.get("references", [])
        ]

        return cls(
            cve_id=cve["id"],
            description=description,
            published=datetime.fromisoformat(cve["published"]),
            last_modified=datetime.fromisoformat(cve["lastModified"]),
            cvss_score=score,
            severity=severity,
            references=refs,
        )


@dataclass
class ExploitIntel:
    cve_id: str
    in_cisa_kev: bool = False
    kev_ransomware: Optional[str] = None
    kev_date_added: Optional[str] = None
    nvd_exploit_refs: list[str] = field(default_factory=list)
    other_refs: list[str] = field(default_factory=list)
    search_urls: dict[str, str] = field(default_factory=dict)

    @property
    def priority(self) -> str:
        if self.in_cisa_kev:
            return "KEV — actively exploited"
        if self.nvd_exploit_refs:
            return "Exploit referenced by NVD"
        return "No confirmed exploit"

    @staticmethod
    def build_search_urls(cve_id: str) -> dict[str, str]:
        q = quote(cve_id)
        return {
            "exploit_db":  f"https://www.exploit-db.com/search?cve={q}",
            "github":      f"https://github.com/search?q={q}&type=repositories",
            "nuclei":      f"https://github.com/search?q={q}+path%3A*.yaml&type=code",
            "rapid7":      f"https://www.rapid7.com/db/?q={q}",
        }

    @classmethod
    def build(cls, result: CVEResult, kev_catalog: dict) -> "ExploitIntel":
        entry = kev_catalog.get(result.cve_id)
        return cls(
            cve_id=result.cve_id,
            in_cisa_kev=entry is not None,
            kev_ransomware=(entry or {}).get("knownRansomwareCampaignUse"),
            kev_date_added=(entry or {}).get("dateAdded"),
            nvd_exploit_refs=[r.url for r in result.references if r.is_exploit],
            other_refs=[r.url for r in result.references if not r.is_exploit],
            search_urls=cls.build_search_urls(result.cve_id),
        )
    
        


def fetch_cisa_kev() -> dict:
    resp = requests.get(CISA_DATABASE, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    catalog = resp.json().get("vulnerabilities", [])
    return {v["cveID"]: v for v in catalog if "cveID" in v}


def fetch_nvd(keyword: Optional[str] = None,
              cve_id: Optional[str] = None,
              limit: int = 20) -> list[CVEResult]:
    params: dict[str, object] = {"resultsPerPage": limit}
    if cve_id:
        params["cveId"] = cve_id
    elif keyword:
        params["keywordSearch"] = keyword
    else:
        raise ValueError("need either keyword or cve_id")

    resp = requests.get(NVD_API_BASE, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    time.sleep(RATE_DELAY)

    return [CVEResult.nvd_json(item) for item in resp.json().get("vulnerabilities", [])]


def main() -> int:
    parser = argparse.ArgumentParser(description="Nocturne CVE scanner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-k", "--keyword", help="keyword search, e.g. 'apache struts'")
    group.add_argument("-c", "--cve", help="specific CVE ID, e.g. CVE-2024-3094")
    parser.add_argument("-n", "--limit", type=int, default=20, help="max results")
    parser.add_argument("--json", action="store_true", help="output raw JSON")
    args = parser.parse_args()

    try:
        results = fetch_nvd(keyword=args.keyword, cve_id=args.cve, limit=args.limit)
        kev = fetch_cisa_kev()
    except requests.RequestException as exc:
        print(f"[!] request failed: {exc}", file=sys.stderr)
        return 1

    intel = [ExploitIntel.build(r, kev) for r in results]

    if args.json:
        print(json.dumps(
            [{"cve": r.cve_id, "score": r.cvss_score, "severity": r.severity,
              "priority": i.priority, "kev_added": i.kev_date_added}
             for r, i in zip(results, intel)],
            indent=2,
        ))
        return 0

    for r, i in zip(results, intel):
        print(f"\n{r.cve_id}  [{r.severity or 'N/A'} {r.cvss_score or ''}]")
        print(f"  {i.priority}")
        if i.kev_date_added:
            print(f"  KEV added: {i.kev_date_added}  ransomware: {i.kev_ransomware}")
        print(f"  {r.description[:200]}")
        for url in i.nvd_exploit_refs[:3]:
            print(f"  exploit: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
