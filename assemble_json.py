import json
import pandas as pd
import argparse
from pathlib import Path

def extract_contract_name(abi_json):
    """Fallback: try to guess a contract name from ABI (rarely available)."""
    try:
        abi = json.loads(abi_json)
        for item in abi:
            if item.get("type") == "constructor":
                return "ConstructorContract"
        return "GenericContract"
    except Exception:
        return "Unknown"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocols", default="protocols.csv")
    parser.add_argument("--addresses", default="data/addresses_discovered.csv")
    parser.add_argument("--abis", default="data/abi_fetch_results.csv")
    parser.add_argument("--out", default="final_output/protocols_with_abis.json")
    args = parser.parse_args()

    df_protocols = pd.read_csv(args.protocols)
    df_addresses = pd.read_csv(args.addresses)
    df_abis = pd.read_csv(args.abis)

    # Merge address and ABI results
    merged = df_addresses.merge(
        df_abis, on=["protocol", "network", "contract_address"], how="left"
    )

    results = []
    for _, row in merged.iterrows():
        proto = row["protocol"]
        net = row["network"]
        addr = row["contract_address"]

        abi_path = row.get("abi_path", None)
        if pd.isna(addr) or not isinstance(addr, str) or not addr.startswith("0x"):
            continue

        # Default values
        contract_name = row.get("contract_name", "Unknown")
        if pd.isna(contract_name) or contract_name in [None, "", "NaN", "nan"]:
            contract_name = "Unknown"

        verified = False
        events = []

        if isinstance(abi_path, str) and abi_path.endswith(".json"):
            try:
                with open(abi_path, "r") as f:
                    abi_json = f.read()
                # If contract_name still unknown, try ABI fallback
                if contract_name in [None, "Unknown", "GenericContract"]:
                    contract_name = extract_contract_name(abi_json)
                verified = True
                abi = json.loads(abi_json)
                events = [
                    f"{item['name']}({','.join([i['type'] for i in item.get('inputs', [])])})"
                    for item in abi if item.get("type") == "event"
                ]
            except Exception:
                pass

        results.append({
            "protocol": proto,
            "network": net,
            "contract_address": addr,
            "contract_name": contract_name,
            "verified": verified,
            "events": events,
            "abi_path": abi_path if isinstance(abi_path, str) else None
        })

    # Ensure output folder exists
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Wrote final JSON to {args.out}")