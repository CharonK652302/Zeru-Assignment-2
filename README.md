# Zeru AI – Assignment 2

This project is my solution for Assignment 2 of the Zeru AI internship.  
The main goal was to collect contract addresses for DeFi protocols, fetch their ABIs, extract events, and assemble everything into a final JSON file.

---

## 📌 Problem Statement (in my own words)
- Given a list of protocols and networks, the task was to:
  1. Collect all contract addresses (where available).
  2. Fetch ABIs for those contracts using block explorers.
  3. Extract only **events** from the ABIs.
  4. Produce a structured JSON containing protocol, network, contract address, contract name, verification status, and events.

The instructions also mentioned that it’s fine if not all ABIs are available.  
Since the provided dataset did not directly contain addresses, I added a few **verified well-known contracts** manually to demonstrate the pipeline end-to-end.

---

## 📂 Project Structure
```
data/
 ├── protocols.csv              # Input dataset with protocols + networks
 ├── addresses_discovered.csv   # Discovered addresses (mostly blank, + manual entries)
 └── abi_fetch_results.csv      # Log file of ABI fetch results

abis/                           # Folder where ABI JSON files are saved

final_output/
 └── protocols_with_abis.json   # Final structured JSON output

map_protocols_to_slugs.py       # Standardizes protocol slugs
find_addresses.py               # Builds addresses_discovered.csv
fetch_abis.py                   # Fetches ABIs + contract names from explorers
assemble_json.py                # Merges everything into final JSON
```

---

## ⚙️ Setup
1. Clone the repo and enter the folder.
   ```bash
   git clone <repo-link>
   cd zeru-assignment-2
   ```

2. Install dependencies (requires Python 3.9+).
   ```bash
   pip install -r requirements.txt
   ```
   *(requirements: `pandas`, `requests`)*

3. Set your Etherscan API key (free plan is fine):
   ```bash
   $env:ETHERSCAN_API_KEY="your_api_key_here"   # PowerShell (Windows)
   export ETHERSCAN_API_KEY="your_api_key_here" # Linux/Mac
   ```

---

## ▶️ How to Run
### Step 1 – Fetch ABIs
```bash
python fetch_abis.py --addresses data/addresses_discovered.csv --out-dir abis
```
This script queries block explorers (Etherscan, Polygonscan, BscScan).  
It saves ABI files in the `abis/` folder and logs results in `abi_fetch_results.csv`.

### Step 2 – Assemble Final JSON
```bash
python assemble_json.py --protocols protocols.csv --addresses data/addresses_discovered.csv --abis data/abi_fetch_results.csv --out final_output/protocols_with_abis.json
```
This merges everything into one JSON file with:
- `protocol`
- `network`
- `contract_address`
- `contract_name`
- `verified`
- `events`
- `abi_path`

---

## 📝 Example Output
```json
{
  "protocol": "uniswap",
  "network": "ethereum",
  "contract_address": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
  "contract_name": "UniswapV2Factory",
  "verified": true,
  "events": [
    "PairCreated(address,address,address,uint256)",
    "FeeToSetterChanged(address,address)"
  ],
  "abi_path": "abis/ethereum/0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f.json"
}
```

For protocols where no ABI was available, the contract name is `"Unknown"` but the structure is still consistent.

---

## 📌 Notes
- Most rows in the dataset don’t have contract addresses.  
- For the demo, I **manually added well-known verified contracts** like Uniswap, Aave, Compound, QuickSwap, and PancakeSwap to `addresses_discovered.csv`.  
- The pipeline is scalable: once more addresses are added, it can fetch their ABIs and update the JSON automatically.

---

## 🎯 Summary
This project demonstrates:
- Collecting and organizing protocol data  
- Using block explorers to fetch verified ABIs  
- Extracting only events from ABIs  
- Building a clean, consistent JSON output  

Even though not all protocols had addresses available, the pipeline works end-to-end and can easily be extended as more addresses are discovered.
