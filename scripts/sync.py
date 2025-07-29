import subprocess

wsl_distro = "Ubuntu"
wsl_user = "anonymous"

wsl_wallet = "/home/anonymous/.config/solana/id.json"
wsl_idl = "/home/anonymous/plug_and_play_audit_addon/audit_merkle_anchor/target/idl/audit_merkle_anchor.json"

win_wallet = "/mnt/c/Users/PC/Desktop/plug_and_play_audit_addon/scripts/wallet.json"
win_idl = "/mnt/c/Users/PC/Desktop/plug_and_play_audit_addon/scripts/idl.json"

# Copy wallet.json
result1 = subprocess.run(["wsl", "-d", wsl_distro, "-u", wsl_user, "cp", wsl_wallet, win_wallet], capture_output=True, text=True)
print(result1.stdout, result1.stderr)
# Copy idl.json
result2 = subprocess.run(["wsl", "-d", wsl_distro, "-u", wsl_user, "cp", wsl_idl, win_idl], capture_output=True, text=True)
print(result2.stdout, result2.stderr)

print("Files synced from WSL!")