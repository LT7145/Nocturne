<p align="center">
    <picture>
        <img src="config/bridy.png" alt="Nocturne" width='400' />
    </picture>
<p>

# Nocturne
Automated Reconnaissance Pipeline

# Notes
Automated Recon Pipeline — Build Order

A step-by-step plan for building the pipeline: individual scripts first, orchestrator second, TUI last.

Phase 0 — Planning & Contracts (before writing any code)
Define your stages. Pick a fixed set of recon phases you'll support first, e.g.:
Subdomain enumeration
Port/service scanning
Service fingerprinting / banner grabbing
Web tech detection (if targets include HTTP services)
(Optional later) vuln/CVE correlation
Design one shared I/O contract all scripts will follow:
Input: consistent CLI args (e.g. --target, --output, --timeout)
Output: structured JSON to stdout or a file (not raw text you have to regex later)
Exit codes: 0 success, 1 recoverable failure, 2 fatal/config error
Logging: stderr for logs, stdout reserved for data
Pick your run model — subprocess-per-tool vs. importable Python modules. Subprocess is easier if you're wrapping existing tools (subfinder, naabu, httpx, etc.); modules are faster if you're writing pure Python logic. This decision affects your orchestrator design, so lock it in now.
Decide on a working directory structure, e.g.:
   recon-pipeline/
   ├── scripts/
   ├── orchestrator/
   ├── schemas/
   ├── output/
   └── tui/
Phase 1 — Individual Scripts

Build and test each script standalone, one at a time, before touching orchestration.

Subdomain enumeration script
Wrap or reimplement enumeration (passive sources + optional brute force)
Output: JSON list of discovered subdomains + source
Port/service scan script
Wrap a scanner (naabu/masscan/nmap) or write your own
Output: JSON of host → open ports → service guess
Service fingerprinting script
Banner grab / version detection on discovered ports
Output: JSON of service name, version, confidence
(Optional) Web tech detection script
HTTP probing, tech stack fingerprinting (headers, JS libs, CMS)
Test each script in isolation
Run against known lab targets (your own homelab / HTB boxes / a deliberately vulnerable VM)
Confirm output matches your schema exactly
Handle edge cases: no results, timeouts, malformed target input, tool not installed

Definition of done for this phase: every script runs correctly on its own from the CLI, produces schema-valid JSON, and fails predictably (non-zero exit + logged reason) rather than crashing silently.

Phase 2 — Data Schemas & Validation
Write a JSON schema (or simple Python dataclass/Pydantic model) per stage's output.
Add a lightweight validation step each script runs before printing output — catches bugs before they propagate into the orchestrator.
Store schemas in schemas/ so the orchestrator and TUI can both import them instead of guessing field names.
Phase 3 — Orchestrator (glue layer)
Write a thin coordinator (Python script or bash) that:
Takes a target as input
Calls each script in sequence, passing output from one stage as input context to the next (e.g. subdomains → feed into port scan)
Captures stdout/stderr per stage, writes results to output/<target>/<stage>.json
Add error handling and retries
Timeouts per stage
Retry logic for flaky network calls
Continue-on-failure vs. abort-on-failure modes (configurable)
Add concurrency where safe (e.g. run fingerprinting on multiple hosts in parallel) — but only after the serial version works correctly.
Add a run manifest — a JSON file summarizing what ran, when, exit codes, and durations. This becomes your TUI's data source later.
Test end-to-end from the CLI repeatedly against lab targets until it's boring and reliable.

Definition of done for this phase: you can run one command, point it at a target, and get a complete, structured multi-stage recon output with no manual intervention.

Phase 4 — TUI (presentation layer)

Only start this once Phase 3 is stable and you've run it enough times to know what you actually want to see.

Pick your framework (Textual is the common modern choice for Python; curses if you want to go lower-level).
Build the TUI as a thin client over the orchestrator and manifest — it should not contain recon logic itself, just:
A way to kick off a run (calls the orchestrator)
Live status per stage (reads the run manifest / stage output files as they're written)
A results browser (reads the JSON output files and renders them as tables/trees)
Add live log tailing per stage if you want real-time feedback during long scans.
Polish last: color coding by severity/status, keybindings, export/report generation.
Phase 5 — Hardening & Extras (optional, after v1 works)
Config file support (targets list, scan profiles: quick/full/stealth)
Plugin system so new stages can be dropped into scripts/ without touching the orchestrator
Report generation (Markdown/HTML/PDF summary of a run)
Rate limiting / scope enforcement to avoid scanning out-of-scope hosts
Integration with your existing SIEM/Wazuh setup for logging pipeline runs as events
Quick Checklist
 Stage list finalized
 Shared I/O contract defined
 Run model chosen (subprocess vs. module)
 Each script built + tested standalone
 JSON schemas written per stage
 Orchestrator chains stages correctly
 Orchestrator handles errors/timeouts/retries
 End-to-end CLI run is stable
 TUI built as a thin client on top
 Polish and extras
