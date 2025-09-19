import os
import requests
import pandas as pd
import argparse
import time
from pathlib import Path

# Load API key from environment variable
API_KEY = os.getenv("ETHERSCAN_API_KEY")

# Base URLs for supported chains
BASE_URLS = {
    "ethereum": "https://api.etherscan.io/api",
    "polygon": "https://api.polygonscan.com/api",
    "bsc": "https://api.bscscan.com/api",
    # Add more networks if needed (arbitrum, optimism, etc.)
}

def fetch_abi(address, network):
    """Fetch contract ABI + metadata from explorer API"""
    base_url = BASE_URLS.get(network.lower())
    if not base_url:
        return None, None, "unsupported-network"

    url = f"{base_url}?module=contract&action=getsourcecode&address={address}&apikey={API_KEY}"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        j = r.json()

        if j.get("status") == "1" and len(j.get("result", [])) > 0:
            result = j["result"][0]
            contract_name = result.get("ContractName", "Unknown")
            abi = result.get("ABI", None)
            if abi and abi != "Contract source code not verified":
                return abi, contract_name, "ok"
            else:
                return None, contract_name, "not-verified"
        else:
            return None, None, "not-found"
    except Exception as e:
        return None, None, str(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--addresses", default="data/addresses_discovered.csv")
    parser.add_argument("--out-dir", default="abis")
    parser.add_argument("--out-log", default="data/abi_fetch_results.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.addresses)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for _, row in df.iterrows():
        addr = row["contract_address"]
        proto = row["protocol"]
        net = row["network"]

        if not isinstance(addr, str) or not addr.startswith("0x"):
            rows.append({**row, "status": "skip", "contract_name": "Unknown"})
            continue

        abi, contract_name, status = fetch_abi(addr, net)
        if abi:
            # Save ABI file
            net_dir = out_dir / net
            net_dir.mkdir(parents=True, exist_ok=True)
            abi_path = net_dir / f"{addr}.json"
            with open(abi_path, "w") as f:
                f.write(abi)

            rows.append({**row, "status": "ok", "abi_path": str(abi_path), "contract_name": contract_name})
        else:
            rows.append({**row, "status": status, "contract_name": contract_name})

        # Be polite: don’t spam the API
        time.sleep(0.25)

    outdf = pd.DataFrame(rows)
    outdf.to_csv(args.out_log, index=False)
    print(f"Wrote ABI results to {args.out_log}")