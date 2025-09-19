import requests
import json
import pandas as pd
import argparse
import time
from urllib.parse import quote_plus

PROTO_API_BASE = 'https://api.llama.fi/protocol/'

def extract_addresses_from_protocol(slug):
    """Query DefiLlama for a given protocol slug and try to extract contract addresses."""
    url = PROTO_API_BASE + quote_plus(slug)
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return []
    j = r.json()

    candidates = []
    for key in ['addresses', 'contracts', 'contract_addresses',
                'contractsAddresses', 'contractAddresses']:
        if key in j:
            candidates.append(j[key])

    out = []
    for c in candidates:
        if isinstance(c, dict):
            for k, v in c.items():
                if isinstance(v, str) and v.startswith('0x'):
                    out.append(v)
                elif isinstance(v, list):
                    for a in v:
                        if isinstance(a, str) and a.startswith('0x'):
                            out.append(a)
                        elif isinstance(a, dict) and 'address' in a:
                            out.append(a['address'])
        elif isinstance(c, list):
            for item in c:
                if isinstance(item, str) and item.startswith('0x'):
                    out.append(item)
                elif isinstance(item, dict) and 'address' in item:
                    out.append(item['address'])

    return sorted(list(set([x.lower() for x in out])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocols-file', default='protocols.csv')
    parser.add_argument('--slug-map', default='data/protocol_slug_map.json')
    parser.add_argument('--out', default='data/addresses_discovered.csv')
    parser.add_argument('--limit', type=int, default=None,
                        help="Optional: limit to top N unique protocols for faster demo runs")
    args = parser.parse_args()

    df = pd.read_csv(args.protocols_file)
    slug_map = json.load(open(args.slug_map))

    unique_protocols = df['protocol'].unique().tolist()
    if args.limit:
        unique_protocols = unique_protocols[:args.limit]

    print(f"Found {len(unique_protocols)} unique protocols to query...")

    protocol_to_addresses = {}
    for proto in unique_protocols:
        slug = slug_map.get(proto)
        if not slug:
            protocol_to_addresses[proto] = []
            continue
        try:
            addresses = extract_addresses_from_protocol(slug)
            protocol_to_addresses[proto] = addresses
        except Exception as e:
            protocol_to_addresses[proto] = []
        time.sleep(0.2)  # polite delay

    rows = []
    for _, row in df.iterrows():
        proto = row['protocol']
        network = row['network']
        addresses = protocol_to_addresses.get(proto, [])
        if addresses:
            for a in addresses:
                rows.append({
                    'protocol': proto,
                    'network': network,
                    'contract_address': a,
                    'source': 'defillama-api'
                })
        else:
            rows.append({
                'protocol': proto,
                'network': network,
                'contract_address': None,
                'source': 'not-found'
            })

    outdf = pd.DataFrame(rows)
    outdf.to_csv(args.out, index=False)
    print(f"Wrote {args.out}")
