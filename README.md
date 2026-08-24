<p align="center">
    <picture>
        <img src="config/bridy.png" alt="Nocturne" width='400' />
    </picture>
<p>

# Nocturne

Nocturne, Python-based reconnaissance toolkit for security research, CTFs, authorized penetration testing. Bringing multiple recon capabilities together under a single CLI, rather than seperate tools of enumeration

# Features
* Unified CLI for multiple recon modules (currently only web)
*  Fast, configurable, and scriptable for automation
*  Built for CTF and security research use cases

# Requirements
* Python 3.8+
* pip

# Installation

Clone the repository:
```bash
git clone https://github.com/LT7145/Nocturne.git
```
Install Dependencies:
```bash
pip install -r requirements.txt
```
Install Nocturne as a CLI command:
```bash
pip install .
```
Verify the install:
```bash
nocturne --help
```
# Usage
For now nocturne only supports web enumeration later additions will add more tools.
```bash
nocturne <module> <target> [options]
```
The target is positional sub and dir enumeration are the only ones available right now. Subdomain enumeration:
```bash
nocturne web example.com -m sub -w wordlists/subs.txt -c 200,301,403
```
Directory enumeration:
```bash
nocturne web https://example.com -m dir -w wordlists/dirs.txt -t 25 -o found.txt
```
Run `nocturne web -h` for the full option list.

# Contributing 
Issues and pull requests are welcomed. Please open an issue to discuss changes before submitting PR

# Disclaimer
Nocturne is intended for authorized security testing and educational purposes. Please do not use it against systems you do not own or have explicit permission to test

# License
MIT
