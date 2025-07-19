# Plug and Play Audit Addon

A blockchain-integrated, tamper-evident logging and audit system for Windows endpoints, featuring:
- Secure log collection
- Cryptographic signing
- Merkle tree aggregation
- On-chain anchoring of Merkle roots to Solana
- Modern Streamlit web UI for all operations

---

## 🚀 Project Overview

This system enables:
- **Secure log collection** from Windows endpoints
- **Cryptographic signing** of logs for authenticity
- **Merkle tree aggregation** for tamper-evident batching
- **On-chain anchoring** of Merkle roots to Solana (via Anchor)
- **Modern Streamlit web UI** for all operations

---

## ✨ Features
- Collects and signs Windows Event Logs
- Builds Merkle trees and submits roots to Solana
- Minimal, summary-only output for clarity
- Automatic syncing of wallet/IDL from WSL before submission

---

## 🛠️ Setup & Installation

### 1. **Prerequisites**
- **Python 3.10+**
- **PowerShell** (for log collection on Windows)
- **WSL (Ubuntu)** for Solana/Anchor development
- **Solana CLI** ([Install Guide](https://docs.solana.com/cli/install-solana-cli-tools))
- **Anchor CLI** ([Install Guide](https://book.anchor-lang.com/chapter_2/installation.html))

### 2. **Clone the Repository**
```bash
cd <your-projects-folder>
git clone <repo-url> plug_and_play_audit_addon
cd plug_and_play_audit_addon
```

### 3. **Install Python Dependencies**
```bash
pip install -r requirements.txt
# If not present, install manually:
pip install streamlit pymerkle solana solders pycryptodome
```

### 4. **Install Solana & Anchor (in WSL)**
```bash
# In WSL Ubuntu
curl -sSfL https://release.solana.com/v1.18.11/install | sh
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest
```

### 5. **Start Solana Localnet & Deploy Anchor Program**
```bash
# In WSL Ubuntu
cd ~/plug_and_play_audit_addon/audit_merkle_anchor
anchor localnet
# (or: solana-test-validator & anchor deploy)
```

### 6. **Sync Wallet/IDL from WSL to Windows**
- Use the Streamlit UI “Sync from WSL” button, or run:
```bash
python scripts/sync_wsl_files.py
```

---

## 🖥️ Usage: Main Workflow

### **Start the Streamlit App**
```bash
streamlit run scripts/app.py
```

### **Workflow Steps (via UI):**
1. **Collect Logs**: Gathers Windows Event Logs
2. **Sign Logs**: Signs logs with endpoint key
3. **Build Merkle Tree**: Aggregates logs, generates Merkle root
4. **Submit Merkle Root**: Syncs wallet/IDL, submits root to Solana
5. **Run All Steps**: Executes the entire pipeline in order

- **All steps show only summary lines and errors for clarity.**

---

## 🗂️ File Structure (Key Files)
- `scripts/app.py` — Streamlit web app
- `scripts/sync_wsl_files.py` — Syncs wallet/IDL from WSL
- `scripts/submit_root.py` — Submits Merkle root to Solana
- `scripts/hash_and_build_merkle.py` — Builds Merkle tree
- `scripts/sign_latest_log.py` — Signs logs
- `logs/` — Collected logs and Merkle roots

---

## 🧠 Troubleshooting
- **Solana errors:** Ensure validator is running (`anchor localnet` or `solana-test-validator`).
- **Sync errors:** Make sure WSL is running and files exist at the expected paths.
- **Streamlit UI not updating:** Restart Streamlit after code changes.
- **Verbose output:** Only summary lines are shown; check logs for details if needed.

---

## 📚 References
- [Solana Cookbook](https://solanacookbook.com/)
- [Anchor Book](https://book.anchor-lang.com/)
- [pymerkle](https://github.com/LucaCappelletti94/pymerkle)
- [Streamlit](https://streamlit.io/)

---

## 📝 Notes
- Always keep your `wallet.json` and `idl.json` in sync with your deployed program.
- Never share your `wallet.json` private key publicly.
- For production, use environment variables or config files for sensitive info.
- The system is modular and ready for further extension (multi-client, cloud, etc.).

---

**For questions, improvements, or demo requests, contact the project maintainer.**
