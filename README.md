# Solana Secure Logging Prototype

A secure Windows event log collection and verification system that uses Merkle trees and Solana blockchain for tamper-evident logging.

## Overview

This system collects Windows Event Logs (Application, System, and Security), creates cryptographic proofs using Merkle trees, and anchors these proofs on the Solana blockchain for immutable verification.

---

## Features

- **Automated Log Collection**
  - Collects Windows Event Logs (Application, System, and Security)
  - Supports last 100 events from each log type
  - Automatic timestamping of log collections

- **Secure Processing**
  - Converts logs to JSON format for standardization
  - Creates individual hashes for each log entry
  - Builds Merkle trees for efficient verification
  - Stores all intermediate hashes for future validation

- **Blockchain Integration**
  - Anchors Merkle roots to Solana blockchain
  - Uses Solana's local testnet for development
  - Implements proper transaction handling using solders library

---

## Project Structure

```
├── powershell/                 # PowerShell scripts
│   └── collect_logs.ps1        # Event log collection script
├── scripts/                    # Python scripts
│   ├── app.py                 # Streamlit web application
│   ├── hash_and_build_merkle.py  # Merkle tree builder
│   ├── submit_root.py         # Blockchain submission
│   ├── verify_log.py          # Log verification script
│   ├── sync.py               # Synchronization utility
│   ├── idl.json              # Solana program interface
│   └── wallet.json           # Solana wallet configuration
├── README.md                       # Project readme
└── requirements.txt                # Python dependencies
```

## Prerequisites

- Windows operating system
- Python 3.10 or higher
- PowerShell with administrator rights (for Security log access)
- Solana CLI tools
- Local Solana testnet (for development)

## 🔧 Solana & Anchor Setup (WSL)

### 1. **Install Solana & Anchor (in WSL)**
```bash
# In WSL Ubuntu
curl --proto '=https' --tlsv1.2 -sSfL https://solana-install.solana.workers.dev | bash
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest
```

### 2. **Start Solana Localnet & Deploy Anchor Program**
```bash
# In WSL Ubuntu
cd ~/plug_and_play_audit_addon/audit_merkle_anchor
anchor localnet
# (or: solana-test-validator & anchor deploy)
```

### 3. **Sync Wallet/IDL from WSL to Windows**
```bash
python scripts/sync.py
```

---

## 💻 Usage: Main Workflow

### Method 1: Using the Web Interface (Recommended)

1. **Start the Web Interface**
```bash
streamlit run scripts/app.py
```

2. **Using the GUI**
- Click "Collect Logs" to gather Windows Event Logs (requires administrator access)
- Click "Build Merkle Tree" to process and hash the collected logs
- Click "Submit to Blockchain" to anchor the Merkle root on Solana
- Use "Verify Logs" tab to check log integrity
- View operation history in the "History" tab

### Method 2: Using Command Line

If you prefer using command-line tools directly:

1. **Collect Logs**
```powershell
# Run as administrator for full log access
.\powershell\collect_logs.ps1
```

2. **Process Logs and Build Merkle Tree**
```bash
python scripts/hash_and_build_merkle.py
```

3. **Submit to Blockchain**
```bash
python scripts/submit_root.py
```

Note: The GUI method is recommended as it provides:
- Interactive workflow guidance
- Real-time operation status
- Built-in error handling
- Visual verification tools
- Operation history tracking

---

## 😠 Troubleshooting
- **Solana errors:** Ensure validator is running (`anchor localnet` or `solana-test-validator`).
- **Sync errors:** Make sure WSL is running and files exist at the expected paths.
- **Streamlit UI not updating:** Restart Streamlit after code changes.
- **Verbose output:** Only summary lines are shown; check logs for details if needed.

---

## 📙 References
- [Solana Cookbook](https://solanacookbook.com/)
- [Anchor Book](https://book.anchor-lang.com/)
- [pymerkle](https://github.com/fmerg/pymerkle/)
- [Streamlit](https://streamlit.io/)

---

## 📝 Notes
- Always keep your `wallet.json` and `idl.json` in sync with your deployed program.
- Never share your `wallet.json` private key publicly.
- For production, use environment variables or config files for sensitive info.
- The system is modular and ready for further extension (multi-client, cloud, etc.).

---

## Security Considerations

- Run PowerShell as administrator to access Security logs
- Merkle trees provide cryptographic proof of log integrity
- Each log entry is individually hashed for verification
- Blockchain anchoring prevents tampering with historical data

## Logs Structure

The system creates three types of log files:
- `application_log_[timestamp].json`
- `system_log_[timestamp].json`
- `security_log_[timestamp].json`

Each log file contains up to 100 most recent events from their respective Windows Event Log categories.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request
