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

### On Windows

* **Windows 10/11** operating system
* **Python 3.10** or higher
* **PowerShell** with administrator rights (required if accessing Windows Security logs)
* A code editor (VSCode recommended)
* **Windows Subsystem for Linux (WSL 2)** installed and configured

### On WSL (Ubuntu)

* **Solana CLI tools** ([installation guide](https://solana.com/docs/intro/installation))
* **Rust & Cargo** (for building Anchor programs)
* **Anchor CLI** (via AVM)
* Local Solana testnet (`solana-test-validator` or `anchor localnet`)

### Notes

* Ensure your WSL distro has internet access to install packages.
* Your Python scripts on Windows will sync wallets and IDLs from WSL, so paths must be correctly mapped.
* Optional but recommended: Node.js and npm/yarn if you plan to run frontend or JS clients interacting with the program.

---


## 🔧 Solana & Anchor Setup (WSL)

### 1️⃣ Install Solana CLI (in WSL)

Follow the official guide: [Solana Installation](https://solana.com/docs/intro/installation)

```bash
# In WSL Ubuntu
curl --proto '=https' --tlsv1.2 -sSfL https://solana-install.solana.workers.dev | bash
```

Verify:

```bash
solana --version
```

---

### 2️⃣ Install Rust (in WSL)

Follow the official guide: [Rust Installation](https://www.rust-lang.org/tools/install)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustc --version
cargo --version
```

---

### 3️⃣ Install Anchor via AVM

```bash
# Install Anchor Version Manager
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force

# Install & use the latest Anchor CLI
avm install latest
avm use latest

# Verify
anchor --version
```

---

### 4️⃣ Create Project Folder

```bash
cd ~
mkdir -p plug_and_play_audit_addon
cd plug_and_play_audit_addon
```

---

### 5️⃣ Initialize a New Anchor Project

```bash
anchor init audit_merkle_anchor
cd audit_merkle_anchor
```

Folder structure after scaffold:

```
Anchor.toml
Cargo.toml
programs/
tests/
```

---
## 6️⃣ Generate or Get Program ID

When you scaffold a new project, Anchor creates a **program keypair**:

```
target/deploy/audit_merkle_anchor-keypair.json
```

Get the **public key** (Program ID) from it:

```bash
solana-keygen pubkey target/deploy/audit_merkle_anchor-keypair.json
```

Output example:

```
8EL9PCpkZddir83rkbxvsNK8eeBhrjHJTqzjYryUbnng
```

Update:

1. `programs/audit_merkle_anchor/src/lib.rs`:

```rust
declare_id!("8EL9PCpkZddir83rkbxvsNK8eeBhrjHJTqzjYryUbnng");
```

2. `Anchor.toml` under `[programs.localnet]`:

```toml
audit_merkle_anchor = "8EL9PCpkZddir83rkbxvsNK8eeBhrjHJTqzjYryUbnng"
```

---
## 7️⃣ Add the Smart Contract Code

Copy your `lib.rs` smart contract into:

```
programs/audit_merkle_anchor/src/lib.rs
```

```rust
#![allow(deprecated)]
use anchor_lang::prelude::*;

declare_id!("8EL9PCpkZddir83rkbxvsNK8eeBhrjHJTqzjYryUbnng"); // Replace with your Program ID

#[program]
pub mod audit_merkle_anchor {
    use super::*;
    pub fn submit_root(ctx: Context<SubmitRoot>, root: [u8; 32]) -> Result<()> {
        let root_account = &mut ctx.accounts.root_account;
        let clock = Clock::get()?;
        root_account.root = root;
        root_account.timestamp = clock.unix_timestamp;
        root_account.user = *ctx.accounts.user.key;
        msg!("Merkle root updated for user: {}", ctx.accounts.user.key());
        Ok(())
    }
}

#[derive(Accounts)]
pub struct SubmitRoot<'info> {
    #[account(
        init_if_needed,
        payer = user,
        space = 8 + 32 + 8 + 32,
        seeds = [b"merkle", user.key().as_ref()],
        bump
    )]
    pub root_account: Account<'info, RootAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct RootAccount {
    pub root: [u8; 32],
    pub timestamp: i64,
    pub user: Pubkey,
}
```

---
## 7️⃣ Deploy Program to Localnet

### Option A: Automatic (Recommended)

```bash
# Build + start validator + deploy
anchor localnet
```

* Anchor auto-builds the program before deploying.

### Option B: Manual

```bash
# Start Solana validator
solana-test-validator

# Build program
anchor build

# Deploy program
anchor deploy
```

---

## 8️⃣ Verify Deployment

```bash
solana program show <YourProgramID>
```

* Confirms program is deployed, executable, and ready for testing.

---

## 🪟 Windows Setup & Usage

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/chauhan-pratham/solana-secure-logging-prototype
cd plug_and_play_audit_addon
```

### 2️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Usage: Main Workflow

### Sync Wallet & IDL (Important)

Before submitting Merkle roots, make sure your wallet and program IDL are synced:

```bash
python scripts/sync.py
```

---

### Method 1: Web Interface (Recommended)

1. **Start the Web Interface**

```bash
streamlit run scripts/app.py
```

2. **Using the GUI**

* Click **Collect Logs** to gather Windows Event Logs (requires administrator rights)
* Click **Build Merkle Tree** to process and hash the logs
* Click **Submit to Blockchain** to anchor the Merkle root on Solana
* Click **Verify Logs** to check log integrity
* View operation history in the **History** tab

> ✅ Recommended for most users: interactive workflow, real-time status, built-in error handling, visual verification, and operation history tracking.

---

### Method 2: Command Line

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

---

## 😠 Troubleshooting

* **Solana errors:** Ensure the validator is running:

```bash
anchor localnet
# or
solana-test-validator
```

* **Sync errors:** WSL must be running; check that wallet.json and IDL exist in the expected paths.
* **Streamlit UI not updating:** Restart Streamlit after any code changes.
* **Verbose logs:** Only summary lines are shown; check logs for full details if needed.

---

## 📙 References

* [Solana Cookbook](https://solanacookbook.com/)
* [Anchor Book](https://book.anchor-lang.com/)
* [pymerkle](https://github.com/fmerg/pymerkle/)
* [Streamlit](https://streamlit.io/)

---

## 📝 Notes

* Keep `wallet.json` and `idl.json` in sync with your deployed program.
* Never share your `wallet.json` private key publicly.
* For production, use environment variables or config files for sensitive information.
* The system is modular and can be extended for multi-client or cloud setups.

---

## 🔒 Security Considerations

* Run PowerShell as administrator for Security log access.
* Merkle trees provide cryptographic proofs of log integrity.
* Each log entry is individually hashed for verification.
* Anchoring to blockchain prevents tampering with historical data.

---

## 📂 Logs Structure

The system generates three types of log files:

* `application_log_[timestamp].json`
* `system_log_[timestamp].json`
* `security_log_[timestamp].json`

Each file contains up to 100 of the most recent events from their respective Windows Event Log categories.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

