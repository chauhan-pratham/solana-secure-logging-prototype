import json
import hashlib
from pathlib import Path
from pymerkle import InmemoryTree as MerkleTree, verify_inclusion
from typing import List, Dict, Any, Optional

class ProofOfInclusion:
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.hashes_dir = self.logs_dir / "hashes"
        self.roots_dir = self.logs_dir / "roots"
        
    def find_log_entry(self, target_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        json_files = [f for f in self.logs_dir.iterdir() if f.suffix == '.json']
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8-sig') as f:
                    processes = json.load(f)
                for idx, process in enumerate(processes):
                    if self._entries_match(process, target_entry):
                        return {
                            'file': json_file.name,
                            'index': idx,
                            'entry': process,
                            'file_path': str(json_file)
                        }
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
                continue
        return None
    
    def _entries_match(self, entry1: Dict[str, Any], entry2: Dict[str, Any]) -> bool:
        entry1_normalized = json.dumps(entry1, sort_keys=True)
        entry2_normalized = json.dumps(entry2, sort_keys=True)
        return entry1_normalized == entry2_normalized
    
    def generate_proof(self, target_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        entry_info = self.find_log_entry(target_entry)
        if not entry_info:
            print(f"Log entry not found in collected logs")
            return None
        tree = MerkleTree(algorithm='sha3_256')
        json_files = [f for f in self.logs_dir.iterdir() if f.suffix == '.json']
        entry_position = None
        current_position = 0
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8-sig') as f:
                    processes = json.load(f)
                for idx, process in enumerate(processes):
                    process_bytes = json.dumps(process, sort_keys=True).encode("utf-8")
                    tree.append_entry(process_bytes)
                    if (json_file.name == entry_info['file'] and idx == entry_info['index']):
                        entry_position = current_position
                    current_position += 1
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                continue
        if entry_position is None:
            print("Could not determine entry position in Merkle tree")
            return None
        try:
            proof = tree.prove_inclusion(entry_position, len(tree.leaves))
            return {
                'entry_info': entry_info,
                'merkle_root': tree.get_state().hex(),
                'entry_position': entry_position,
                'proof': proof,
                'proof_algorithm': 'sha3_256',
                'total_entries': len(tree.leaves)
            }
        except Exception as e:
            print(f"Error generating proof: {e}")
            return None
    
    def verify_proof(self, proof_data: Dict[str, Any], target_entry: Dict[str, Any]) -> bool:
        try:
            entry_bytes = json.dumps(target_entry, sort_keys=True).encode("utf-8")
            entry_hash = hashlib.sha3_256(entry_bytes).digest()
            root = bytes.fromhex(proof_data['merkle_root'])
            proof = proof_data['proof']
            return bool(verify_inclusion(entry_hash, root, proof))
        except Exception as e:
            print(f"Error verifying proof: {e}")
        return False
    
    def save_proof(self, proof_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proof_{timestamp}.json"
        if not isinstance(filename, str):
            raise ValueError("filename must be a string")
        proof_file = self.logs_dir / "proofs" / filename
        proof_file.parent.mkdir(exist_ok=True)
        try:
            with open(proof_file, 'w') as f:
                json.dump(proof_data, f, indent=2)
            print(f"Proof saved to: {proof_file}")
            return str(proof_file)
        except Exception as e:
            print(f"Error saving proof: {e}")
            return str(proof_file)  # Return the intended path even if failed
    
    def load_proof(self, proof_file: str) -> Optional[Dict[str, Any]]:
        try:
            with open(proof_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading proof: {e}")
            return None

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python proof_of_inclusion.py generate <entry_json>")
        print("  python proof_of_inclusion.py verify <proof_file> <entry_json>")
        print("  python proof_of_inclusion.py find <entry_json>")
        sys.exit(1)
    poi = ProofOfInclusion()
    command = sys.argv[1]
    if command == "generate":
        if len(sys.argv) != 3:
            print("Usage: python proof_of_inclusion.py generate <entry_json>")
            sys.exit(1)
        try:
            with open(sys.argv[2], 'r') as f:
                target_entry = json.load(f)
        except Exception as e:
            print(f"Error loading entry JSON: {e}")
            sys.exit(1)
        proof = poi.generate_proof(target_entry)
        if proof:
            proof_file = poi.save_proof(proof)
            print(f"Proof generated and saved to: {proof_file}")
        else:
            print("Failed to generate proof")
            sys.exit(1)
    elif command == "verify":
        if len(sys.argv) != 4:
            print("Usage: python proof_of_inclusion.py verify <proof_file> <entry_json>")
            sys.exit(1)
        proof_data = poi.load_proof(sys.argv[2])
        if not proof_data:
            print("Failed to load proof")
            sys.exit(1)
        try:
            with open(sys.argv[3], 'r') as f:
                target_entry = json.load(f)
        except Exception as e:
            print(f"Error loading entry JSON: {e}")
            sys.exit(1)
        result = poi.verify_proof(proof_data, target_entry)
        if result:
            print("Proof verification successful!")
        else:
            print("Proof verification failed!")
            sys.exit(1)
    elif command == "find":
        if len(sys.argv) != 3:
            print("Usage: python proof_of_inclusion.py find <entry_json>")
            sys.exit(1)
        try:
            with open(sys.argv[2], 'r') as f:
                target_entry = json.load(f)
        except Exception as e:
            print(f"Error loading entry JSON: {e}")
            sys.exit(1)
        entry_info = poi.find_log_entry(target_entry)
        if entry_info:
            print(f"Entry found in: {entry_info['file']} at index {entry_info['index']}" )
        else:
            print("Entry not found in collected logs")
            sys.exit(1)
    else:
        print("Unknown command. Use generate, verify, or find.")
        sys.exit(1)

if __name__ == "__main__":
    main() 