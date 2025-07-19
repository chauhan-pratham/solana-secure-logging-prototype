import sys
import os
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder

USAGE = '''\
Usage:
  python endpoint_keygen_and_sign.py gen-keys <key_dir>
  python endpoint_keygen_and_sign.py sign <private_key_file> <log_file> <signature_file>
  python endpoint_keygen_and_sign.py verify <public_key_file> <log_file> <signature_file>
'''

def gen_keys(key_dir):
    os.makedirs(key_dir, exist_ok=True)
    sk = SigningKey.generate()
    pk = sk.verify_key
    priv_path = os.path.join(key_dir, 'ed25519_private.hex')
    pub_path = os.path.join(key_dir, 'ed25519_public.hex')
    with open(priv_path, 'w') as f:
        f.write(sk.encode(encoder=HexEncoder).decode())
    with open(pub_path, 'w') as f:
        f.write(pk.encode(encoder=HexEncoder).decode())
    print(f"Keys generated:\n  Private: {priv_path}\n  Public: {pub_path}")

def sign_log(private_key_file, log_file, signature_file):
    with open(private_key_file, 'r') as f:
        key_bytes = bytes.fromhex(f.read().strip())
    sk = SigningKey(key_bytes)
    with open(log_file, 'rb') as f:
        log_data = f.read()
    signature = sk.sign(log_data).signature
    with open(signature_file, 'wb') as f:
        f.write(signature)
    print(f"Log signed. Signature saved to {signature_file}")

def verify_log(public_key_file, log_file, signature_file):
    with open(public_key_file, 'r') as f:
        key_bytes = bytes.fromhex(f.read().strip())
    pk = VerifyKey(key_bytes)
    with open(log_file, 'rb') as f:
        log_data = f.read()
    with open(signature_file, 'rb') as f:
        signature = f.read()
    try:
        pk.verify(log_data, signature)
        print("Signature is valid.")
        sys.exit(0)
    except Exception as e:
        print(f"Signature verification failed: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'gen-keys' and len(sys.argv) == 3:
        gen_keys(sys.argv[2])
    elif cmd == 'sign' and len(sys.argv) == 5:
        sign_log(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'verify' and len(sys.argv) == 5:
        verify_log(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(USAGE)
        sys.exit(1)

if __name__ == '__main__':
    main() 