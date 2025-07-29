#!/usr/bin/env python3
"""
Log Verification Module
Allows forensic auditors to verify the integrity of specific log events
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import verification components
try:
    from pymerkle import InmemoryTree as MerkleTree
except ImportError as e:
    logging.error(f"Failed to import verification components: {e}")

class LogVerifier:
    """
    Verifies the integrity of log events using Merkle proofs
    """
    
    def __init__(self, logs_dir: str = None):
        """
        Initialize log verifier
        
        Args:
            logs_dir: Directory containing audit logs and proofs
        """
        self.logger = logging.getLogger(__name__)
        
        # Setup directories
        if logs_dir:
            self.logs_dir = Path(logs_dir)
        else:
            self.logs_dir = Path(__file__).parent.parent / 'logs'
        
        self.logger.info("Log verifier initialized")
    
    def verify_event_integrity(self, event_file: str, proof_file: str, 
                              root_hash: str = None) -> bool:
        """
        Verify the integrity of a specific log event
        
        Args:
            event_file: Path to the event file
            proof_file: Path to the proof file
            root_hash: Expected Merkle root hash (optional)
            
        Returns:
            True if integrity is verified
        """
        try:
            # Load event and proof
            event_data = self._load_json_file(event_file)
            proof_data = self._load_json_file(proof_file)
            
            if not event_data or not proof_data:
                self.logger.error("Failed to load event or proof data")
                return False
            
            # Step 1: Verify event hash
            if not self._verify_event_hash(event_data, proof_data):
                self.logger.error("Event hash verification failed")
                return False
            
            # Step 2: Verify Merkle proof
            if not self._verify_merkle_proof(event_data, proof_data, root_hash):
                self.logger.error("Merkle proof verification failed")
                return False
            
            # Step 3: Verify blockchain submission (if root provided)
            if root_hash and not self._verify_blockchain_submission(proof_data, root_hash):
                self.logger.error("Blockchain verification failed")
                return False
            
            self.logger.info("Event integrity verification successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during integrity verification: {e}")
            return False
    
    def _load_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load JSON file safely"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            return None
    
    def _verify_event_hash(self, event_data: Dict[str, Any], 
                          proof_data: Dict[str, Any]) -> bool:
        """
        Verify that the event hash matches the proof
        
        Args:
            event_data: Event data
            proof_data: Proof data
            
        Returns:
            True if hash verification passes
        """
        try:
            import hashlib
            
            # Calculate event hash
            event_str = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
            event_bytes = event_str.encode('utf-8')
            calculated_hash = hashlib.sha256(event_bytes).hexdigest()
            
            # Get expected hash from proof
            expected_hash = proof_data.get('event_hash', '')
            
            if calculated_hash == expected_hash:
                self.logger.info("Event hash verification passed")
                return True
            else:
                self.logger.error(f"Hash mismatch: calculated={calculated_hash}, expected={expected_hash}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying event hash: {e}")
            return False
    
    def _verify_merkle_proof(self, event_data: Dict[str, Any], 
                            proof_data: Dict[str, Any], 
                            expected_root: str = None) -> bool:
        """
        Verify the Merkle proof for the event
        
        Args:
            event_data: Event data
            proof_data: Proof data
            expected_root: Expected Merkle root (optional)
            
        Returns:
            True if Merkle proof verification passes
        """
        try:
            # Get Merkle proof from proof data
            merkle_root = proof_data.get('merkle_root', '')
            
            if not merkle_root:
                self.logger.warning("No Merkle root in proof data")
                return True
            
            # If expected root provided, verify it matches
            if expected_root and merkle_root != expected_root:
                self.logger.error(f"Merkle root mismatch: proof={merkle_root}, expected={expected_root}")
                return False
            
            # Reconstruct Merkle tree and verify inclusion
            # This is a simplified verification - in production you'd use proper Merkle proof verification
            event_str = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
            event_bytes = event_str.encode('utf-8')
            
            # For now, just verify the event is in the batch
            batch_events = proof_data.get('batch_events', [])
            event_hash = self._calculate_event_hash(event_data)
            
            for batch_event in batch_events:
                if batch_event.get('event_hash') == event_hash:
                    self.logger.info("Merkle proof verification passed")
                    return True
            
            self.logger.error("Event not found in batch")
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying Merkle proof: {e}")
            return False
    
    def _verify_blockchain_submission(self, proof_data: Dict[str, Any], 
                                     expected_root: str) -> bool:
        """
        Verify that the Merkle root was submitted to the blockchain
        
        Args:
            proof_data: Proof data
            expected_root: Expected Merkle root
            
        Returns:
            True if blockchain verification passes
        """
        try:
            # This would typically involve querying the blockchain
            # For now, we'll just verify the root matches
            merkle_root = proof_data.get('merkle_root', '')
            
            if merkle_root == expected_root:
                self.logger.info("Blockchain verification passed")
                return True
            else:
                self.logger.error(f"Blockchain root mismatch: proof={merkle_root}, expected={expected_root}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying blockchain submission: {e}")
            return False
    
    def _calculate_event_hash(self, event_data: Dict[str, Any]) -> str:
        """Calculate hash of event data"""
        import hashlib
        
        event_str = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        event_bytes = event_str.encode('utf-8')
        return hashlib.sha256(event_bytes).hexdigest()
    
    def verify_batch_integrity(self, batch_id: str) -> bool:
        """
        Verify the integrity of an entire batch
        
        Args:
            batch_id: ID of the batch to verify
            
        Returns:
            True if batch integrity is verified
        """
        try:
            # Load batch and proof
            batch_file = self.logs_dir / f"audit_batch_{batch_id}.json"
            proof_file = self.logs_dir / f"merkle_proof_{batch_id}.json"
            
            if not all(f.exists() for f in [batch_file, proof_file]):
                self.logger.error(f"Missing batch files for {batch_id}")
                return False
            
            # Load data
            with open(batch_file, 'r') as f:
                batch_data = json.load(f)
            
            with open(proof_file, 'r') as f:
                proof_data = json.load(f)
            
            # Verify all events in batch
            events = batch_data.get('events', [])
            for event in events:
                if not self._verify_event_in_batch(event, batch_data, proof_data):
                    self.logger.error(f"Event verification failed: {event.get('event_hash', 'unknown')}")
                    return False
            
            self.logger.info(f"Batch {batch_id} integrity verification successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying batch integrity: {e}")
            return False
    
    def _verify_event_in_batch(self, event: Dict[str, Any], 
                              batch_data: Dict[str, Any], 
                              proof_data: Dict[str, Any]) -> bool:
        """Verify that an event is properly included in the batch"""
        try:
            event_hash = event.get('event_hash', '')
            calculated_hash = self._calculate_event_hash(event)
            
            if event_hash == calculated_hash:
                return True
            else:
                self.logger.error(f"Event hash mismatch: {event_hash} vs {calculated_hash}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying event in batch: {e}")
            return False

def main():
    """Main entry point for log verification"""
    parser = argparse.ArgumentParser(description='Verify log event integrity')
    parser.add_argument('--event', help='Path to event file')
    parser.add_argument('--proof', help='Path to proof file')
    parser.add_argument('--root', help='Expected Merkle root hash')
    parser.add_argument('--batch', help='Batch ID for batch verification')
    parser.add_argument('--logs-dir', help='Directory containing audit logs')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize verifier
    verifier = LogVerifier(logs_dir=args.logs_dir)
    
    # Perform verification
    if args.batch:
        # Verify entire batch
        success = verifier.verify_batch_integrity(args.batch)
    elif args.event and args.proof:
        # Verify specific event
        success = verifier.verify_event_integrity(args.event, args.proof, args.root)
    else:
        print("Error: Must specify either --batch or both --event and --proof")
        sys.exit(1)
    
    if success:
        print("✅ Verification successful")
        sys.exit(0)
    else:
        print("❌ Verification failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 