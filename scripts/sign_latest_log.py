import os
import sys
from pathlib import Path
import subprocess

def find_unsigned_logs(logs_dir):
    files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]
    unsigned = []
    for f in files:
        sig = f.replace('.json', '.sig')
        if not (logs_dir / sig).exists():
            unsigned.append(f)
    return unsigned

def main():
    logs_dir = Path(__file__).parent.parent / 'logs'
    key_dir = Path(__file__).parent.parent / 'endpoint_keys'
    priv_key = key_dir / 'ed25519_private.hex'
    if not priv_key.exists():
        print(f"Private key not found at {priv_key}. Run endpoint_keygen_and_sign.py gen-keys endpoint_keys first.")
        sys.exit(1)
    unsigned_logs = find_unsigned_logs(logs_dir)
    if not unsigned_logs:
        print("No unsigned log files found.")
        sys.exit(0)
    for log_file in unsigned_logs:
        log_path = logs_dir / log_file
        sig_path = logs_dir / (log_file.replace('.json', '.sig'))
        try:
            subprocess.run([
                sys.executable,
                str(Path(__file__).parent / 'endpoint_keygen_and_sign.py'),
                'sign',
                str(priv_key),
                str(log_path),
                str(sig_path)
            ], check=True)
            print("Log file signed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error signing {log_path}: {e}")

if __name__ == '__main__':
    main() 