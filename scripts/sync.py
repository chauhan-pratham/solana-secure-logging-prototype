import argparse, subprocess, sys
from pathlib import Path

def wsl_user(distro):
    r = subprocess.run(["wsl","-d",distro,"whoami"],capture_output=True,text=True)
    return r.stdout.strip() if r.returncode==0 else "anonymous"

def wsl_cat(distro,user,path):
    r = subprocess.run(["wsl","-d",distro,"-u",user,"cat",path],capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode(errors="replace"))
    return r.stdout

def main():
    scripts_dir = Path(__file__).parent
    p = argparse.ArgumentParser(description="Auto-sync wallet.json & idl.json from WSL → Windows repo")
    p.add_argument("--wsl-distro", default="Ubuntu", help="WSL distro (default: Ubuntu)")
    p.add_argument("--wsl-user", help="WSL username (default: auto-detected)")
    p.add_argument("--wsl-wallet", help="Path to wallet.json in WSL")
    p.add_argument("--wsl-idl", help="Path to idl.json in WSL")
    p.add_argument("--dest-dir", type=Path, default=scripts_dir, help="Destination folder (default: repo scripts/)")
    a = p.parse_args()

    user = a.wsl_user or wsl_user(a.wsl_distro)
    wallet = a.wsl_wallet or f"/home/{user}/.config/solana/id.json"
    idl = a.wsl_idl or f"/home/{user}/plug_and_play_audit_addon/audit_merkle_anchor/target/idl/audit_merkle_anchor.json"
    files = [(wallet, a.dest_dir/"wallet.json"), (idl, a.dest_dir/"idl.json")]

    print(f"Syncing from WSL (distro={a.wsl_distro}, user={user}) → {a.dest_dir}")
    errs=0
    for src,dst in files:
        try: dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(wsl_cat(a.wsl_distro,user,src)); print(f"✔ {src} -> {dst}")
        except Exception as e: print(f"[ERR] {src}: {e}"); errs+=1
    return 2 if errs else 0

if __name__=="__main__": sys.exit(main())
