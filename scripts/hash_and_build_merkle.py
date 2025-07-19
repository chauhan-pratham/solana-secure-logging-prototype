import os
from pathlib import Path
import hashlib
import json
from pymerkle import InmemoryTree as MerkleTree
import sys
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder

# Define the path to the logs directory
logs_dir = Path(__file__).parent.parent / "logs"
key_dir = Path(__file__).parent.parent / "endpoint_keys"
pub_key_path = key_dir / "ed25519_public.hex"

# Load endpoint public key
if not pub_key_path.exists():
    print(f"\u274c Public key not found at {pub_key_path}. Run endpoint_keygen_and_sign.py gen-keys endpoint_keys first.")
    sys.exit(1)
with open(pub_key_path, 'r') as f:
    key_bytes = bytes.fromhex(f.read().strip())
pubkey = VerifyKey(key_bytes)

# Step 1: Read all .json log files
json_files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]

if not json_files:
    print("\u274c No log (.json) files found in logs/")
    exit(1)

# Step 2: Initialize the Merkle Tree
tree = MerkleTree(algorithm='sha3_256')

# Create directories for hashes and roots if they don't exist
hashes_dir = logs_dir / "hashes"
roots_dir = logs_dir / "roots"
hashes_dir.mkdir(exist_ok=True)
roots_dir.mkdir(exist_ok=True)

included_logs = 0
# Step 3: Loop through files and add each process entry to the tree
for file_name in json_files:
    file_path = logs_dir / file_name
    sig_path = logs_dir / file_name.replace('.json', '.sig')
    if not sig_path.exists():
        print(f"\u26a0\ufe0f Skipping {file_name}: signature file not found.")
        continue
    # Verify signature
    with open(file_path, 'rb') as f:
        log_data = f.read()
    with open(sig_path, 'rb') as f:
        signature = f.read()
    try:
        pubkey.verify(log_data, signature)
    except Exception as e:
        print(f"\u274c Skipping {file_name}: invalid signature. {e}")
        continue
    # If valid, parse JSON and add to Merkle tree
    with open(file_path, "r", encoding="utf-8-sig") as f:
        try:
            processes = json.load(f)
        except Exception as e:
            print(f"\u274c Failed to parse {file_name}: {e}")
            continue
    for idx, process in enumerate(processes):
        process_bytes = json.dumps(process, sort_keys=True).encode("utf-8")
        tree.append_entry(process_bytes)
        process_hash = hashlib.sha3_256(process_bytes).digest()
        hash_file_name = f"{file_name.replace('.json', '')}_process_{idx}.hash"
        hash_file_path = hashes_dir / hash_file_name
        hash_file_path.write_text(process_hash.hex())
    included_logs += 1

if included_logs == 0:
    print("\u274c No valid, signed logs found. Merkle tree not built.")
    sys.exit(1)

# Step 4: Get the final Merkle Root
root_bytes = tree.get_state()
root_hex = root_bytes.hex()

# Print the Merkle tree structure in the terminal
print("\nMerkle Tree Structure:")
print(f"Root: {root_hex}")
print("Leaves:")
for idx, leaf in enumerate(tree.leaves):
    print(f"  {idx}: {leaf.digest.hex()}")

# Step 5: Output and Save the Merkle Root
print(f"Merkle Tree built successfully!\nMerkle Root: {root_hex}")

root_file_path = roots_dir / "latest_merkle_root.txt"
root_file_path.write_text(root_hex)
print(f"Merkle root saved to: {root_file_path}")