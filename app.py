import streamlit as st
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
POWERSHELL_SCRIPT = ROOT_DIR / 'powershell' / 'collect_logs.ps1'
SIGN_SCRIPT = ROOT_DIR / 'scripts' / 'sign_latest_log.py'
MERKLE_SCRIPT = ROOT_DIR / 'scripts' / 'hash_and_build_merkle.py'
SUBMIT_SCRIPT = ROOT_DIR / 'scripts' / 'submit_root.py'
SYNC_SCRIPT = ROOT_DIR / 'scripts' / 'sync_wsl_files.py'

st.set_page_config(page_title="Plug and Play Audit Addon", layout="wide")

st.title("🔌 Plug and Play Audit Addon")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Workflow", "History", "Settings", "About"])

def run_command(command, shell=False):
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        # Only show the last non-empty line (summary or error)
        all_lines = (result.stdout + result.stderr).splitlines()
        summary_lines = [line for line in all_lines if line.strip()]
        if summary_lines:
            summary = summary_lines[-1]
        else:
            summary = "No output."
        if result.returncode == 0:
            return summary, ""
        else:
            return f"Error: {summary}", ""
    except Exception as e:
        return (f"Exception: {e}", "")

if page == "Workflow":
    st.header("Workflow Steps")
    col1, col2, col3, col4, col5 = st.columns(5)
    if col1.button("🗂️ Collect Logs"):
        st.info("Collecting logs...")
        summary, _ = run_command(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(POWERSHELL_SCRIPT)])
        if "successfully" in summary.lower() or summary.startswith("Operation completed"):
            st.success(summary)
        else:
            st.error(summary)
    if col2.button("✍️ Sign Logs"):
        st.info("Signing logs...")
        summary, _ = run_command([sys.executable, str(SIGN_SCRIPT)])
        if "successfully" in summary.lower() or summary.startswith("Operation completed"):
            st.success(summary)
        else:
            st.error(summary)
    if col3.button("🌳 Build Merkle Tree"):
        st.info("Building Merkle tree...")
        summary, _ = run_command([sys.executable, str(MERKLE_SCRIPT)])
        if "successfully" in summary.lower() or summary.startswith("Operation completed"):
            st.success(summary)
        else:
            st.error(summary)
    if col4.button("🚀 Submit Merkle Root"):
        st.info("Syncing files from WSL before submitting...")
        sync_summary, _ = run_command([sys.executable, str(SYNC_SCRIPT)])
        if "success" in sync_summary.lower():
            st.success(sync_summary)
            st.info("Submitting Merkle root to Solana...")
            summary, _ = run_command([sys.executable, str(SUBMIT_SCRIPT)])
            if "successfully" in summary.lower() or summary.startswith("Operation completed"):
                st.success(summary)
            else:
                st.error(summary)
        else:
            st.error(f"Sync failed: {sync_summary}")
    if col5.button("⚡ Run All Steps"):
        st.info("Running all steps...")
        summary1, _ = run_command(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(POWERSHELL_SCRIPT)])
        summary2, _ = run_command([sys.executable, str(SIGN_SCRIPT)])
        summary3, _ = run_command([sys.executable, str(MERKLE_SCRIPT)])
        st.info("Syncing files from WSL before submitting...")
        sync_summary, _ = run_command([sys.executable, str(SYNC_SCRIPT)])
        if "success" in sync_summary.lower():
            st.success(sync_summary)
            summary4, _ = run_command([sys.executable, str(SUBMIT_SCRIPT)])
            all_summaries = f"Collect Logs: {summary1}\nSign Logs: {summary2}\nBuild Merkle Tree: {summary3}\nSubmit Merkle Root: {summary4}"
            if all(s.startswith("Operation completed") or "successfully" in s.lower() for s in [summary1, summary2, summary3, summary4]):
                st.success("All steps completed successfully.")
            else:
                st.error("Some steps failed. See details below.")
            with st.expander("Show Details"):
                st.code(all_summaries)
        else:
            st.error(f"Sync failed: {sync_summary}")
            with st.expander("Show Details"):
                st.code(f"Collect Logs: {summary1}\nSign Logs: {summary2}\nBuild Merkle Tree: {summary3}\nSync: {sync_summary}")

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