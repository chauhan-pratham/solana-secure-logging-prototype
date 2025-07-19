# scripts/submit_root.py
# The final, correct version using the latest solders.transaction and solders.message

import json
from pathlib import Path

from solana.rpc.api import Client
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM_ID

# --- 1. Load Configuration and Connect ---

http_client = Client("http://127.0.0.1:8899")

wallet_path = Path(__file__).parent / "wallet.json"
with open(wallet_path, "r") as f:
    keypair_data = json.load(f)
wallet_keypair = Keypair.from_bytes(bytes(keypair_data))

idl_path = Path(__file__).parent / "idl.json"
with open(idl_path, "r") as f:
    idl = json.load(f)
program_id = Pubkey.from_string(idl["address"])

# --- 2. Prepare Instruction Data ---

root_path = Path(__file__).parent.parent / "logs" / "roots" / "latest_merkle_root.txt"
if not root_path.exists():
    raise FileNotFoundError("latest_merkle_root.txt not found. Please run build_merkle.py first.")
root_hex = root_path.read_text().strip()
root_bytes = bytes.fromhex(root_hex)

submit_root_discriminator = bytes([15, 86, 198, 221, 22, 34, 184, 178])
instruction_data = submit_root_discriminator + root_bytes

# --- 3. Define Accounts and Instruction ---

(pda, _bump) = Pubkey.find_program_address(
    seeds=[b"merkle", bytes(wallet_keypair.pubkey())],
    program_id=program_id
)

accounts = [
    AccountMeta(pubkey=pda, is_signer=False, is_writable=True),
    AccountMeta(pubkey=wallet_keypair.pubkey(), is_signer=True, is_writable=True),
    AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
]

instruction = Instruction(
    program_id=program_id,
    data=instruction_data,
    accounts=accounts,
)

# --- 4. Create and Send the Transaction (Solders way) ---

# Step 4a: Fetch a recent blockhash
recent_blockhash = http_client.get_latest_blockhash().value.blockhash

# Step 4b: Build the message
message = Message([instruction], wallet_keypair.pubkey())

# Step 4c: Create the transaction
transaction = Transaction([wallet_keypair], message, recent_blockhash)

# Step 4d: Send the transaction
print("Submitting Merkle root...")
response = http_client.send_raw_transaction(bytes(transaction))
tx_signature = response.value

print(f"Merkle root submitted successfully! Transaction signature: {tx_signature}")