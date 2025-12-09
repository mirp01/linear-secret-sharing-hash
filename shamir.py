import random
from typing import List, Tuple

"""
    Shamir's Secret Sharing Scheme implementation.

    This module provides functionality to split a secret into multiple shares
    such that only a specified threshold of shares is required to reconstruct the secret.

"""

class ShamirSecretSharing:
    
    def __init__(self, prime: int = None):
        self.prime = prime or 61 * 1000000007  # Large prime

    # Math stuff

    def _mod_inverse(self, a: int, m: int) -> int:
        if a < 0:
            a = (a % m + m) % m
        g, x, _ = self._extended_gcd(a, m)
        if g != 1:
            raise ValueError("Modular inverse does not exist")
        return x % m
    
    def _extended_gcd(self, a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = self._extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    # Evaluate polynomial at x

    def _evaluate_polynomial(self, coeffs: List[int], x: int) -> int:
        result = 0
        for coeff in reversed(coeffs):
            result = (result * x + coeff) % self.prime
        return result
    
    # Split secret into shares

    def split_secret(self, secret: bytes, n: int, k: int) -> List[List[Tuple[int, int]]]:
        if k > n or k < 2:
            raise ValueError("Invalid parameters: require 2 <= k <= n")
        
        # Convert secret to bytes if it's a string
        if isinstance(secret, str):
            secret = secret.encode('utf-8')
        
        byte_shares = []  # One entry per byte of secret
        
        for byte_value in secret:
            if byte_value >= self.prime:
                raise ValueError(f"Byte value too large for field")
            
            # Generate random coefficients for P(x) = byte_value + a1*x + a2*x^2 + ... + a(k-1)*x^(k-1)
            
            coeffs = [byte_value] + [random.randint(0, self.prime - 1) for _ in range(k - 1)]
            
            shares_for_byte = []
            
            x_values = list(range(1, n + 1))
            
            for x in x_values:
                y = self._evaluate_polynomial(coeffs, x)
                shares_for_byte.append((x, y))
            
            byte_shares.append(shares_for_byte)
        
        shares = []
        for share_index in range(n):
            share = []
            for byte_index in range(len(secret)):
                share.append(byte_shares[byte_index][share_index])
            shares.append(share)
        
        return shares
    
    def reconstruct_secret(self, shares: List[List[Tuple[int, int]]]) -> bytes:
        if not shares:
            raise ValueError("Null shares provided")
        
        num_bytes = len(shares[0])
        reconstructed_bytes = []
        
        # Reconstruct each byte separately
        for byte_index in range(num_bytes):
            byte_shares = [share[byte_index] for share in shares]
            
            # Use Lagrange interpolation to find P(0) using modular arithmetic

            secret = 0
            for j, (xj, yj) in enumerate(byte_shares):
                
                numerator = 1
                denominator = 1
                
                for i, (xi, _) in enumerate(byte_shares):
                    if i != j:
                        numerator = (numerator * (0 - xi)) % self.prime
                        denominator = (denominator * (xj - xi)) % self.prime
                
                basis = (numerator * self._mod_inverse(denominator, self.prime)) % self.prime
                secret = (secret + yj * basis) % self.prime
            
            secret = secret % self.prime
            
            # Ensure byte is in valid range

            if secret > 255:
                secret = secret % 256
            
            reconstructed_bytes.append(secret)
        
        return bytes(reconstructed_bytes)
    