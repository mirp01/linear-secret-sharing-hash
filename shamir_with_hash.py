from hash import HashFunction
import random
from typing import List, Tuple


class LSSSWithHashing:
    
    def __init__(self, code_rate: float = 0.5, security_param: int = 128):
        self.code_rate = code_rate
        self.security_param = security_param
        self.q = 2**256 - 2**224 + 2**192 + 2**128 - 1
    
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
            result = (result * x + coeff) % self.q
        return result
    
    def _sample_preimage(self, secret: List[int], hash_func: HashFunction) -> List[int]:
        t = hash_func.t
        
        x = [random.randint(0, self.q - 1) for _ in range(t)]
        
        h_x = hash_func.hash(x)
        
        adjustment = [(secret[i] - h_x[i]) % self.q for i in range(len(secret))]

        #UNFINISHED
        
        return x
    
    def split_secret(self, secret: bytes, n: int, t: int) -> Tuple[List[List[Tuple[int, int]]], HashFunction]:
        if t >  n or t < 2:
            raise ValueError("Invalid parameters")
        
        if isinstance(secret, str):
            secret = secret.encode('utf-8')
        
        t_dim = max(t, 8) 
        l_dim = len(secret) 
        hash_func = HashFunction(t_dim, l_dim, self.q)
        
        # Process each byte
        byte_shares = []
        
        for byte_value in secret:
            if byte_value >= self.q:
                raise ValueError(f"Byte value {byte_value} too large for field")
            
            coeffs = [byte_value] + [random.randint(0, self.q - 1) for _ in range(t - 1)]
            
            shares_for_byte = []
            
            x_values = list(range(1, n + 1))
            
            for x in x_values:
                y = self._evaluate_polynomial(coeffs, x)
                shares_for_byte.append((x, y))
            
            byte_shares.append(shares_for_byte)
        
        organized_shares = []
        for share_index in range(n):
            share = []
            for byte_index in range(len(secret)):
                share.append(byte_shares[byte_index][share_index])
            organized_shares.append(share)
        
        return organized_shares, hash_func
    
    def reconstruct_secret(self, shares: List[List[Tuple[int, int]]], hash_func: HashFunction) -> bytes:
        if not shares:
            raise ValueError("Null shares provided")
        
        num_bytes = len(shares[0])
        reconstructed_bytes = []
        
        for byte_index in range(num_bytes):
            byte_shares = [share[byte_index] for share in shares]
            
            secret = 0
            
            for j, (xj, yj) in enumerate(byte_shares):
                numerator = 1
                denominator = 1
                
                for i, (xi, _) in enumerate(byte_shares):
                    if i != j:
                        numerator = (numerator * (0 - xi)) % self.q
                        denominator = (denominator * (xj - xi)) % self.q
                
                basis = (numerator * self._mod_inverse(denominator, self.q)) % self.q
                secret = (secret + yj * basis) % self.q
            
            secret = secret % self.q
            
            if secret > 255:
                secret = secret % 256
            
            reconstructed_bytes.append(secret)
        
        return bytes(reconstructed_bytes)
