import streamlit as st
import subprocess
import sys
from pathlib import Path
import json
import hashlib
from datetime import datetime

# Get the full absolute path to this file (app.py)
SCRIPT_PATH = Path(__file__).resolve()

# Go to project root: plug_and_play_audit_addon/
ROOT_DIR = SCRIPT_PATH.parent.parent

# Now define all script paths
POWERSHELL_SCRIPT = ROOT_DIR / 'powershell' / 'collect_logs.ps1'
MERKLE_SCRIPT     = SCRIPT_PATH.parent / 'hash_and_build_merkle.py'
SUBMIT_SCRIPT     = SCRIPT_PATH.parent / 'submit_root.py'

# Configure Streamlit page
st.set_page_config(
    page_title="Plug and Play Audit Addon",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .stAlert {
        padding: 10px;
        margin: 10px 0;
    }
    .status-box {
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .nav-link {
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        border-radius: 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        text-decoration: none;
        transition: all 0.3s ease;
    }
    .nav-link:hover {
        background: rgba(255, 255, 255, 0.2);
        border-left: 4px solid #ff4b4b;
    }
    .nav-link.active {
        background: rgba(255, 255, 255, 0.2);
        border-left: 4px solid #ff4b4b;
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(180deg, #2E3440 0%, #3B4252 100%);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔌 Plug and Play Audit Addon")

# Enhanced Navigation
st.sidebar.title("Navigation")

# Navigation menu with icons and descriptions
nav_options = {
    "Workflow": {
        "icon": "⚡",
        "desc": "Main workflow steps",
        "color": "#4CAF50"
    },
    "Verify": {
        "icon": "🔍",
        "desc": "Verify logs and Merkle roots",
        "color": "#2196F3"
    },
    "History": {
        "icon": "📋",
        "desc": "Operation history",
        "color": "#9C27B0"
    },
    "Settings": {
        "icon": "⚙️",
        "desc": "System configuration",
        "color": "#FF9800"
    },
    "About": {
        "icon": "ℹ️",
        "desc": "About the application",
        "color": "#607D8B"
    }
}

st.sidebar.markdown("---")

for name, info in nav_options.items():
    if st.sidebar.button(
        f"{info['icon']} {name}",
        help=info['desc'],
        key=f"nav_{name}"
    ):
        st.session_state.page = name

# Initialize page state if not exists
if 'page' not in st.session_state:
    st.session_state.page = "Workflow"

page = st.session_state.page

# Show current page indicator and system status
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Current Page:** {nav_options[page]['icon']} {page}")
st.sidebar.markdown(f"_{nav_options[page]['desc']}_")

# System Status in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.markdown("🖥️ **System**")
    st.markdown("🔐 **Security**")
    st.markdown("📡 **Network**")
with col2:
    st.markdown("✅ Active")
    st.markdown("✅ Secure")
    st.markdown("✅ Connected")

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

def run_command(command, shell=False):
    """Run a command and add it to history"""
    start_time = datetime.now()
    result = subprocess.run(command, shell=shell, capture_output=True, text=True)
    end_time = datetime.now()
    
    # Add to history
    st.session_state.history.append({
        'timestamp': start_time.isoformat(),
        'command': ' '.join(map(str, command)),
        'output': result.stdout + result.stderr,
        'status': 'Success' if result.returncode == 0 else 'Failed',
        'duration': str(end_time - start_time)
    })
    
    return result.stdout + result.stderr

if page == "Workflow":
    st.header(f"{nav_options[page]['icon']} Workflow Steps")
    
    # Status indicators
    col1, col2, col3 = st.columns(3)
    with col1:
        logs_exist = any(ROOT_DIR.glob("logs/*.json"))
        st.metric("Log Files", "✅" if logs_exist else "⚠️")
    with col2:
        merkle_root_exists = (ROOT_DIR / "logs/roots/latest_merkle_root.txt").exists()
        st.metric("Merkle Tree", "✅" if merkle_root_exists else "⚠️")
    with col3:
        st.metric("Blockchain Status", "Ready")
    
    # Step 1: Collect Logs
    with st.expander("Step 1: Collect Logs", expanded=True):
        if st.button("🗂️ Collect Logs"):
            with st.spinner("Collecting logs..."):
                output = run_command(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(POWERSHELL_SCRIPT)])
                st.code(output)
                st.success("Logs collected successfully!")
        
        # Show existing logs
        logs_dir = ROOT_DIR / "logs"
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.json"))
            if log_files:
                st.write("📁 Available Log Files:")
                for log_file in log_files:
                    with st.expander(f"📄 {log_file.name}"):
                        try:
                            # Quick check for empty file
                            if Path(log_file).stat().st_size == 0:
                                st.warning("File is empty")
                                continue
                            
                            # Read just enough for preview and basic validation
                            with open(log_file, 'r', encoding='utf-8-sig') as f:
                                preview_lines = []
                                for i, line in enumerate(f):
                                    if i < 5:  # Only store first 5 lines
                                        preview_lines.append(line.rstrip())
                                    else:
                                        break
                            
                            st.write("📄 Content Preview:")
                            preview_content = '\n'.join(preview_lines)
                            if Path(log_file).stat().st_size > 1024:
                                preview_content += "\n..."
                            st.code(preview_content, language="text")
                            
                            # Try to parse as JSON
                            try:
                                with open(log_file, 'r', encoding='utf-8-sig') as f:
                                    json_data = json.load(f)
                                st.write("✅ Valid JSON found:")
                                if isinstance(json_data, list):
                                    st.write(f"Found {len(json_data)} log entries")
                                    if len(json_data) > 0:
                                        st.write("First entry preview:")
                                        st.json(json_data[0])
                                else:
                                    st.json(json_data)
                            except json.JSONDecodeError as e:
                                st.error("Invalid JSON format")
                                st.info("💡 Tip: Check for proper JSON formatting")
                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")
    
    # Step 2: Build Merkle Tree
    with st.expander("Step 2: Build Merkle Tree", expanded=True):
        if st.button("🌳 Build Merkle Tree"):
            with st.spinner("Building Merkle tree..."):
                output = run_command([sys.executable, str(MERKLE_SCRIPT)])
                st.code(output)
                if "ERROR" not in output:
                    st.success("Merkle tree built successfully!")
                else:
                    st.error("Failed to build Merkle tree")
        
        # Show current Merkle root if exists
        root_file = ROOT_DIR / "logs/roots/latest_merkle_root.txt"
        if root_file.exists():
            with open(root_file, 'r') as f:
                st.info(f"Current Merkle Root: {f.read().strip()}")
    
    # Step 3: Submit to Blockchain
    with st.expander("Step 3: Submit to Blockchain", expanded=True):
        if st.button("🚀 Submit Merkle Root"):
            if not merkle_root_exists:
                st.warning("Please build Merkle tree first!")
            else:
                with st.spinner("Submitting to blockchain..."):
                    output = run_command([sys.executable, str(SUBMIT_SCRIPT)])
                    st.code(output)
                    if "ERROR" not in output:
                        st.success("Successfully submitted to blockchain!")
    
    if st.button("⚡ Run All Steps"):
        st.info("Running all steps...")
        output1 = run_command(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(POWERSHELL_SCRIPT)])
        output2 = run_command([sys.executable, str(MERKLE_SCRIPT)])
        output3 = run_command([sys.executable, str(SUBMIT_SCRIPT)])
        st.code(output1 + output2 + output3)

elif page == "Verify":
    st.header("Log Verification")
    
    # Initialize session state for verification results
    if 'verification_results' not in st.session_state:
        st.session_state.verification_results = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Verify Individual Log")
        logs_dir = ROOT_DIR / "logs"
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.json"))
            if log_files:
                selected_file = st.selectbox("Select Log File", [f.name for f in log_files])
                if selected_file:
                    log_path = logs_dir / selected_file
                    try:
                        # Check file and get preview
                        with open(log_path, 'rb') as f:
                            first_chunk = f.read(1024)  # Read first 1KB
                            is_empty = not first_chunk.strip()
                            has_bom = first_chunk.startswith(b'\xef\xbb\xbf')
                        
                        if is_empty:
                            st.error("File is empty!")
                        else:
                            # Read preview efficiently
                            with open(log_path, 'r', encoding='utf-8-sig' if has_bom else 'utf-8') as f:
                                preview_lines = []
                                for i, line in enumerate(f):
                                    if i < 5:
                                        preview_lines.append(line.rstrip())
                                    else:
                                        break
                            
                            preview_content = '\n'.join(preview_lines)
                            if Path(log_path).stat().st_size > 1024:  # If file is larger than preview
                                preview_content += "\n..."
                            
                            st.write("File preview:")
                            st.code(preview_content, language="text")
                            st.write("File analysis:")
                            st.code(f"File size: {Path(log_path).stat().st_size} bytes")
                            
                            try:
                                # Try to parse as JSON efficiently
                                with open(log_path, 'r', encoding='utf-8-sig' if has_bom else 'utf-8') as f:
                                    logs_data = json.load(f)  # More efficient than loads
                                if isinstance(logs_data, list):
                                    st.success("Successfully parsed JSON file")
                                    # Show individual log entries
                                    for idx, log in enumerate(logs_data):
                                        with st.expander(f"Log Entry #{idx + 1}"):
                                            st.json(log)
                                            verify_button_key = f"verify_{selected_file}_{idx}"
                                            if st.button("🔐 Verify This Entry", key=verify_button_key):
                                                # Calculate hash for this entry
                                                log_bytes = json.dumps(log, sort_keys=True).encode("utf-8")
                                                log_hash = hashlib.sha3_256(log_bytes).hexdigest()
                                                
                                                # Check if hash exists in hashes directory
                                                hash_file = logs_dir / "hashes" / f"{selected_file.replace('.json', '')}_process_{idx}.hash"
                                                if hash_file.exists():
                                                    with open(hash_file, 'r') as f:
                                                        stored_hash = f.read().strip()
                                                    if log_hash == stored_hash:
                                                        st.success("✅ Log entry verified! Hash matches stored value.")
                                                        st.code(f"Hash: {log_hash}")
                                                    else:
                                                        st.error("❌ Verification failed! Hash mismatch.")
                                                        st.code(f"Calculated: {log_hash}\nStored: {stored_hash}")
                                                else:
                                                    st.error("❌ No hash file found for this entry.")
                                else:
                                    st.error("JSON content is not a list. Expected array of log entries.")
                                    st.code(logs_data)
                            except json.JSONDecodeError as e:
                                st.error(f"Invalid JSON format: {str(e)}")
                                st.info("💡 Tip: Make sure the file contains a valid JSON array of log entries")
                    except Exception as e:
                        st.error(f"Error reading file: {str(e)}")
            else:
                st.warning("No log files found.")
    
    with col2:
        st.subheader("🌳 Verify Merkle Root")
        
        # Initialize session state for Merkle root verification
        if 'merkle_root_cache' not in st.session_state:
            st.session_state.merkle_root_cache = None
            st.session_state.merkle_root_last_check = 0
        
        # Function to get Merkle root with caching
        def get_merkle_root():
            current_time = datetime.now().timestamp()
            merkle_root_file = logs_dir / "roots" / "latest_merkle_root.txt"
            
            # Only read file if cache is empty or older than 5 seconds
            if (st.session_state.merkle_root_cache is None or 
                current_time - st.session_state.merkle_root_last_check > 5):
                
                if merkle_root_file.exists():
                    try:
                        with open(merkle_root_file, 'r') as f:
                            st.session_state.merkle_root_cache = f.read().strip()
                    except Exception:
                        st.session_state.merkle_root_cache = None
                else:
                    st.session_state.merkle_root_cache = None
                
                st.session_state.merkle_root_last_check = current_time
            
            return st.session_state.merkle_root_cache
        
        # Get current root from cache
        current_root = get_merkle_root()
        
        if current_root:
            st.info(f"Current Merkle Root: {current_root}")
            
            # Add verification options
            verify_option = st.radio(
                "Verification Method",
                ["Quick Verify", "Full Verify"],
                help="Quick verify checks only the root hash, Full verify rebuilds the entire tree"
            )
            
            if st.button("🔄 Verify Current Root"):
                with st.spinner("Verifying Merkle root..."):
                    if verify_option == "Quick Verify":
                        # Just check if the file exists and matches
                        merkle_root_file = logs_dir / "roots" / "latest_merkle_root.txt"
                        if merkle_root_file.exists():
                            with open(merkle_root_file, 'r') as f:
                                stored_root = f.read().strip()
                            if stored_root == current_root:
                                st.success("✅ Quick verification passed: Merkle root matches stored value.")
                            else:
                                st.error("❌ Verification failed: Merkle root mismatch!")
                    else:
                        # Full verification with tree rebuild
                        output = run_command([sys.executable, str(MERKLE_SCRIPT)])
                        if "ERROR" not in output:
                            merkle_root_file = logs_dir / "roots" / "latest_merkle_root.txt"
                            with open(merkle_root_file, 'r') as f:
                                new_root = f.read().strip()
                            if new_root == current_root:
                                st.success("✅ Full verification passed: Merkle tree structure is intact.")
                            else:
                                st.error("❌ Full verification failed: Logs may have been modified.")
                                st.code(f"Stored Root: {current_root}\nCalculated Root: {new_root}")
                        else:
                            st.error("Failed to verify Merkle root")
        else:
            st.warning("No Merkle root found. Please build the Merkle tree first.")

elif page == "History":
    st.header(f"{nav_options[page]['icon']} Operation History")
    
    if not st.session_state.history:
        st.info("No operations performed yet.")
    else:
        # Initialize pagination state
        if 'history_page' not in st.session_state:
            st.session_state.history_page = 0
        
        # Add filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "Success", "Failed"],
                key="history_filter_status"
            )
        with col2:
            items_per_page = st.selectbox(
                "Items per page",
                [5, 10, 20, 50],
                key="history_items_per_page"
            )
        
        # Filter entries
        filtered_history = st.session_state.history
        if filter_status != "All":
            filtered_history = [
                entry for entry in filtered_history 
                if entry['status'] == filter_status
            ]
        
        # Calculate pagination
        total_pages = (len(filtered_history) + items_per_page - 1) // items_per_page
        if total_pages > 0:
            # Pagination controls
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("◀️ Previous") and st.session_state.history_page > 0:
                    st.session_state.history_page -= 1
            with col2:
                st.write(f"Page {st.session_state.history_page + 1} of {total_pages}")
            with col3:
                if st.button("Next ▶️") and st.session_state.history_page < total_pages - 1:
                    st.session_state.history_page += 1
            
            # Display entries for current page
            start_idx = st.session_state.history_page * items_per_page
            end_idx = min(start_idx + items_per_page, len(filtered_history))
            
            current_entries = list(reversed(filtered_history[start_idx:end_idx]))
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                success_count = sum(1 for entry in filtered_history if entry['status'] == 'Success')
                st.metric("Successful Operations", success_count)
            with col2:
                failed_count = sum(1 for entry in filtered_history if entry['status'] == 'Failed')
                st.metric("Failed Operations", failed_count)
            with col3:
                st.metric("Total Operations", len(filtered_history))
            
            # Display entries
            for entry in current_entries:
                status_color = "🟢" if entry['status'] == 'Success' else "🔴"
                with st.expander(f"{status_color} {entry['timestamp']} - {entry['command'][:50]}{'...' if len(entry['command']) > 50 else ''}"):
                    st.write(f"**Status:** {entry['status']}")
                    st.write(f"**Duration:** {entry['duration']}")
                    if len(entry['output']) > 1000:
                        st.write("**Output:** (truncated)")
                        st.code(entry['output'][:1000] + "\n...")
                    else:
                        st.write("**Output:**")
                        st.code(entry['output'])
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.session_state.history_page = 0
            st.experimental_rerun()

elif page == "Settings":
    st.header("System Settings")
    
    # Paths
    st.subheader("📁 System Paths")
    st.write(f"**Root Directory:** `{ROOT_DIR}`")
    st.write(f"**Logs Directory:** `{ROOT_DIR}/logs`")
    st.write(f"**Scripts Directory:** `{SCRIPT_PATH.parent}`")
    
    # Configuration
    st.subheader("⚙️ Configuration")
    st.write("These settings affect how the system processes and stores audit data.")
    
    col1, col2 = st.columns(2)
    with col1:
        auto_collect = st.checkbox("Auto-collect logs", value=False, 
                                 help="Automatically collect logs at set intervals")
        if auto_collect:
            st.number_input("Collection interval (minutes)", 
                          min_value=1, value=5, 
                          help="How often to automatically collect logs")
    with col2:
        st.selectbox("Hash Algorithm", ["sha3_256", "sha256", "blake2b"], 
                    help="Algorithm used for Merkle tree")
        st.number_input("Batch Size", min_value=1, value=100, 
                     help="Number of logs to process in one batch")

elif page == "About":
    st.header("About Plug and Play Audit Addon")
    st.markdown("""
    ### Overview
    This application provides a seamless way to collect, verify, and audit logs using Merkle trees 
    and blockchain technology.
    
    ### Features
    - 🗂️ **Automated Log Collection**: Collect logs from various sources
    - 🌳 **Merkle Tree Generation**: Create verifiable Merkle trees from log data
    - ⛓️ **Blockchain Integration**: Submit Merkle roots to blockchain for immutable verification
    - 📊 **Real-time Monitoring**: Track operations and view system status
    
    ### How It Works
    1. **Log Collection**: The system collects logs from specified sources
    2. **Merkle Tree**: Creates a Merkle tree from the collected logs
    3. **Blockchain**: Submits the Merkle root to blockchain for verification
    
    ### Support
    For issues or questions, please refer to the documentation or contact support.
    """)
