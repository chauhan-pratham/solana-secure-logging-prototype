import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
import getpass
from typing import Optional

class SecureKeyManager:
    def __init__(self, key_dir: str = "endpoint_keys"):
        self.key_dir = key_dir
        os.makedirs(key_dir, exist_ok=True)
        self.salt_file = os.path.join(key_dir, "salt.bin")
        self.encrypted_priv_file = os.path.join(key_dir, "ed25519_private.encrypted")
        self.pub_file = os.path.join(key_dir, "ed25519_public.hex")
        
    def _get_key_from_password(self, password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def generate_keys(self, password: str) -> None:
        sk = SigningKey.generate()
        pk = sk.verify_key
        key, salt = self._get_key_from_password(password)
        fernet = Fernet(key)
        encrypted_priv = fernet.encrypt(sk.encode(encoder=HexEncoder))
        with open(self.encrypted_priv_file, 'wb') as f:
            f.write(encrypted_priv)
        with open(self.salt_file, 'wb') as f:
            f.write(salt)
        with open(self.pub_file, 'w') as f:
            f.write(pk.encode(encoder=HexEncoder).decode())
        print(f"Keys generated and encrypted:")
        print(f"  Private (encrypted): {self.encrypted_priv_file}")
        print(f"  Public: {self.pub_file}")
        print(f"  Salt: {self.salt_file}")
    
    def load_private_key(self, password: str) -> SigningKey:
        try:
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
            with open(self.encrypted_priv_file, 'rb') as f:
                encrypted_priv = f.read()
            key, _ = self._get_key_from_password(password, salt)
            fernet = Fernet(key)
            priv_hex = fernet.decrypt(encrypted_priv).decode()
            priv_bytes = bytes.fromhex(priv_hex) if all(c in '0123456789abcdefABCDEF' for c in priv_hex) and len(priv_hex) == 64 else priv_hex.encode()
            return SigningKey(priv_bytes)
        except Exception as e:
            raise Exception(f"Failed to load private key: {e}")
    
    def load_public_key(self) -> VerifyKey:
        try:
            with open(self.pub_file, 'r') as f:
                pub_hex = f.read().strip()
            pub_bytes = bytes.fromhex(pub_hex) if all(c in '0123456789abcdefABCDEF' for c in pub_hex) and len(pub_hex) == 64 else pub_hex.encode()
            return VerifyKey(pub_bytes)
        except Exception as e:
            raise Exception(f"Failed to load public key: {e}")
    
    def sign_data(self, data: bytes, password: str) -> bytes:
        sk = self.load_private_key(password)
        return sk.sign(data).signature
    
    def verify_data(self, data: bytes, signature: bytes) -> bool:
        pk = self.load_public_key()
        try:
            pk.verify(data, signature)
            return True
        except Exception:
            return False

def main() -> None:
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python secure_key_manager.py gen-keys")
        print("  python secure_key_manager.py sign <data_file> <signature_file>")
        print("  python secure_key_manager.py verify <data_file> <signature_file>")
        sys.exit(1)
    manager = SecureKeyManager()
    command = sys.argv[1]
    if command == "gen-keys":
        password = getpass.getpass("Enter password for private key encryption: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords don't match!")
            sys.exit(1)
        manager.generate_keys(password)
    elif command == "sign":
        if len(sys.argv) != 4:
            print("Usage: python secure_key_manager.py sign <data_file> <signature_file>")
            sys.exit(1)
        password = getpass.getpass("Enter password: ")
        with open(sys.argv[2], 'rb') as f:
            data = f.read()
        signature = manager.sign_data(data, password)
        with open(sys.argv[3], 'wb') as f:
            f.write(signature)
        print(f"Data signed. Signature saved to {sys.argv[3]}")
    elif command == "verify":
        if len(sys.argv) != 4:
            print("Usage: python secure_key_manager.py verify <data_file> <signature_file>")
            sys.exit(1)
        with open(sys.argv[2], 'rb') as f:
            data = f.read()
        with open(sys.argv[3], 'rb') as f:
            signature = f.read()
        if manager.verify_data(data, signature):
            print("Signature is valid.")
        else:
            print("Signature verification failed.")
            sys.exit(1)
    else:
        print("Unknown command. Use gen-keys, sign, or verify.")
        sys.exit(1)

if __name__ == "__main__":
    main() 