# Updated DNS HTTPS Resource Record Measurements  

This repository contains code and analysis for an updated longitudinal study of DNS HTTPS and SVCB Resource Records, extending the methodology of the IMC 2024 paper *"Exploring the Ecosystem of DNS HTTPS Resource Records: An End-to-End Perspective."*

The updated analysis includes:
- New HTTPS/SVCB RR adoption trends  
- Updated DNSSEC signing and validation behavior  
- Provider-level effects behind observed spikes and dips  
- Comparison of dynamic vs overlapping domain populations  

---

## Dataset
This study uses updated DNS measurement snapshots for:
- Daily Tranco Top 1M domains  
- Overlapping domains persistent across the full observation window  

Original dataset and documentation:  
https://keyinfra.cs.virginia.edu/dns_http/

---

## Installation

Clone and set up environment:

```bash
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>

python3 -m venv env
source env/bin/activate

pip install -r requirements.txt
