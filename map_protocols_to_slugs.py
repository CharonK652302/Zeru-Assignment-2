import requests
import pandas as pd
import json
import argparse
from difflib import get_close_matches

API_PROTOCOLS = "https://api.llama.fi/protocols"

def fetch_all_protocols():
    resp = requests.get(API_PROTOCOLS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def build_slug_map(protocols_csv):
    df = pd.read_csv(protocols_csv)
    names = df['protocol'].astype(str).str.strip().unique().tolist()
    print(f"Loaded {len(names)} unique protocol names from {protocols_csv}")

    all_protos = fetch_all_protocols()
    llama_names = {p['name'].lower(): p['slug'] for p in all_protos if 'slug' in p and p.get('slug')}
    slug_map = {}
    for name in names:
        lower = name.lower()
        if lower in llama_names:
            slug_map[name] = llama_names[lower]
            continue
        # fuzzy match by name
        candidates = get_close_matches(lower, list(llama_names.keys()), n=3, cutoff=0.75)
        if candidates:
            slug_map[name] = llama_names[candidates[0]]
        else:
            slug_map[name] = None
    return slug_map

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocols-file', default='protocols.csv')
    parser.add_argument('--out', default='data/protocol_slug_map.json')
    args = parser.parse_args()
    out = args.out
    mapping = build_slug_map(args.protocols_file)
    with open(out, 'w') as f:
        json.dump(mapping, f, indent=2)
    print('Wrote', out)
