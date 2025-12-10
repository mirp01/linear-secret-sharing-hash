from shamir import ShamirSecretSharing
from shamir_with_hash import LSSSWithHashing

''' Example usage of Shamir's Secret Sharing and Linear Secret Sharing with Hashing '''


if __name__ == "__main__":
    sss = ShamirSecretSharing()
    
    # Example 1: Text secret
    print("=== Example 1: Text Secret ===")
    secret_text = "QuesoManchego"
    print(f"Original secret: {secret_text}")
    
    n_shares = 7
    threshold = 4
    shares = sss.split_secret(secret_text, n_shares, threshold)
    print(f"Generated {n_shares} shares (need {threshold} to reconstruct)")
    print(f"Each share has {len(shares[0])} byte-pairs")
    
    # Show first share as example
    print(f"\nFirst share (first 5 bytes): {shares[0][:5]}")
    
    # Reconstruct with threshold shares
    print(f"\nReconstructing with {threshold} shares...")
    reconstructed = sss.reconstruct_secret(shares[:threshold])
    print(f"Reconstructed secret: {reconstructed.decode('utf-8')}")
    print(f"Match: {reconstructed.decode('utf-8') == secret_text}")
    
    # Example 2: Reconstruct with different subset
    print("\n=== Example 2: Different Share Subset ===")
    subset = [shares[1], shares[3], shares[5], shares[6]]
    reconstruction2 = sss.reconstruct_secret(subset)
    print(f"Reconstructed from shares [1,3,5,6]: {reconstruction2.decode('utf-8')}")
    print(f"Match: {reconstruction2.decode('utf-8') == secret_text}")
    
    # Example 3: Binary/arbitrary data
    print("\n=== Example 3: Binary Data ===")
    secret_bytes = b"\x01\x02\x03\x04\x05"
    print(f"Original secret (hex): {secret_bytes.hex()}")
    
    shares_binary = sss.split_secret(secret_bytes, 5, 3)
    print(f"Generated 5 shares with random x-values")
    
    reconstruction3 = sss.reconstruct_secret(shares_binary[:3])
    print(f"Reconstructed secret (hex): {reconstruction3.hex()}")
    print(f"Match: {reconstruction3 == secret_bytes}")

    print("\nWITH HASHING-BASED SCHEME")
    
    # Initialize the hashing-based scheme
    sss_hash = LSSSWithHashing()
    
    # Test 1: Text Secret
    print("=== EXAMPLE 1: Text Secret ===")
    secret_text = "QuesoManchego"
    n_shares = 7
    threshold = 4
    
    print(f"Original secret: {secret_text}")
    print(f"Total shares: {n_shares}, Threshold: {threshold}\n")
    
    # Split secret
    shares, hash_func = sss_hash.split_secret(secret_text, n_shares, threshold)
    
    # Display first share details
    print(f"First share details (showing first 5 bytes):")
    print(shares[0][:5])
    print()
    
    # Reconstruct with exactly threshold shares
    reconstructed = sss_hash.reconstruct_secret(shares[:threshold], hash_func)
    print(f"Reconstructed secret: {reconstructed.decode('utf-8')}")
    print(f"Match: {reconstructed.decode('utf-8') == secret_text}\n")
    