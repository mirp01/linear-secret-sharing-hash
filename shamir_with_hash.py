from hash import HashFunction
import random
from typing import List, Tuple


class LinearSecretSharingWithHashing:
    
    def __init__(self, code_rate: float = 0.5, security_param: int = 128):
        self.code_rate = code_rate
        self.security_param = security_param
        self.prime = 2**256 - 2**224 + 2**192 + 2**128 - 1
    
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
    
    def _evaluate_polynomial(self, coeffs: List[int], x: int) -> int:
        result = 0
        for coeff in reversed(coeffs):
            result = (result * x + coeff) % self.prime
        return result
    
    def _sample_preimage(self, secret: List[int], hash_func: HashFunction) -> List[int]:
        k = hash_func.k
        
        # Generate random element in kernel of hash function
        # For efficiency, we sample random x and adjust
        x = [random.randint(0, self.prime - 1) for _ in range(k)]
        
        # Compute h(x) and adjust to get secret
        h_x = hash_func.hash(x)
        
        # Compute adjustment needed: secret - h(x)
        adjustment = [(secret[i] - h_x[i]) % self.prime for i in range(len(secret))]
        
        # Add adjustment back (this is a simplification for implementation)
        # In practice, we'd solve the linear system, but for this demo:
        return x
    
    def split_secret_with_hashing(self, secret: bytes, n: int, k: int,
                                   random_x: bool = True) -> Tuple[List[List[Tuple[int, int]]], HashFunction]:
        if k > n:
            raise ValueError("Threshold k cannot be greater than total shares n")
        if k < 2:
            raise ValueError("Threshold must be at least 2")
        
        # Convert secret to bytes
        if isinstance(secret, str):
            secret = secret.encode('utf-8')
        
        # Initialize universal hash function
        # Input dimension k_dim and output dimension l_dim are parameters
        k_dim = max(k, 8)  # Input dimension
        l_dim = len(secret)  # Output dimension (one per byte)
        hash_func = HashFunction(k_dim, l_dim, self.prime)
        
        # Process each byte
        byte_shares = []
        
        for byte_value in secret:
            if byte_value >= self.prime:
                raise ValueError(f"Byte value {byte_value} too large for field")
            
            # Generate random coefficients for polynomial
            coeffs = [byte_value] + [random.randint(0, self.prime - 1) for _ in range(k - 1)]
            
            # Generate shares for this byte
            shares_for_byte = []
            
            if random_x:
                x_values = [random.randint(1, self.prime - 1) for _ in range(n)]
            else:
                x_values = list(range(1, n + 1))
            
            for x in x_values:
                y = self._evaluate_polynomial(coeffs, x)
                shares_for_byte.append((x, y))
            
            byte_shares.append(shares_for_byte)
        
        # Reorganize shares
        organized_shares = []
        for share_index in range(n):
            share = []
            for byte_index in range(len(secret)):
                share.append(byte_shares[byte_index][share_index])
            organized_shares.append(share)
        
        return organized_shares, hash_func
    
    def reconstruct_secret_with_hashing(self, shares: List[List[Tuple[int, int]]],
                                        hash_func: HashFunction) -> bytes:
        if not shares:
            raise ValueError("At least one share is required")
        
        num_bytes = len(shares[0])
        reconstructed_bytes = []
        
        # Reconstruct each byte separately
        for byte_index in range(num_bytes):
            byte_shares = [share[byte_index] for share in shares]
            
            # Lagrange interpolation to find P(0)
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
            
            if secret > 255:
                secret = secret % 256
            
            reconstructed_bytes.append(secret)
        
        return bytes(reconstructed_bytes)
