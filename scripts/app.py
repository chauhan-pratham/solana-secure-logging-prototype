import streamlit as st
import subprocess
import sys
from pathlib import Path

# Get the full absolute path to this file (app.py)
SCRIPT_PATH = Path(__file__).resolve()

# Go to project root: plug_and_play_audit_addon/
ROOT_DIR = SCRIPT_PATH.parent.parent

# Now define all script paths
POWERSHELL_SCRIPT = ROOT_DIR / 'powershell' / 'collect_logs.ps1'
SIGN_SCRIPT       = SCRIPT_PATH.parent / 'sign_latest_log.py'
MERKLE_SCRIPT     = SCRIPT_PATH.parent / 'hash_and_build_merkle.py'
SUBMIT_SCRIPT     = SCRIPT_PATH.parent / 'submit_root.py'



st.set_page_config(page_title="Plug and Play Audit Addon", layout="wide")

st.title("🔌 Plug and Play Audit Addon")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Workflow", "History", "Settings", "About"])

def run_command(command, shell=False):
    result = subprocess.run(command, shell=shell, capture_output=True, text=True)
    return result.stdout + result.stderr

if page == "Workflow":
    st.header("Workflow Steps")
    if st.button("🗂️ Collect Logs"):
        st.info("Collecting logs...")
        output = run_command(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(POWERSHELL_SCRIPT)])
        st.code(output)
    if st.button("✍️ Sign Logs"):
        st.info("Signing logs...")
        output = run_command([sys.executable, str(SIGN_SCRIPT)])
        st.code(output)
    if st.button("🌳 Build Merkle Tree"):
        st.info("Building Merkle tree...")
        output = run_command([sys.executable, str(MERKLE_SCRIPT)])
        st.code(output)
    if st.button("🚀 Submit Merkle Root"):
        st.info("Submitting Merkle root to Solana...")
        output = run_command([sys.executable, str(SUBMIT_SCRIPT)])
        st.code(output)
    if st.button("⚡ Run All Steps"):
        st.info("Running all steps...")
        output1 = run_command(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(POWERSHELL_SCRIPT)])
        output2 = run_command([sys.executable, str(SIGN_SCRIPT)])
        output3 = run_command([sys.executable, str(MERKLE_SCRIPT)])
        output4 = run_command([sys.executable, str(SUBMIT_SCRIPT)])
        st.code(output1 + output2 + output3 + output4)

elif page == "History":
    st.header("History (Coming Soon)")
elif page == "Settings":
    st.header("Settings (Coming Soon)")
elif page == "About":
    st.header("About")
    st.markdown("""
    - **Plug and Play Audit Addon**
    - Solana + Merkle Tree + Secure Logging
    - Built for regulatory compliance and trust
    """)
