import numpy as np
import random
from typing import List, Tuple

class HashFunction:
    """
    Implementation of F_q-linear universal hash functions.
    Maps F_q^k -> F_q^l using random matrix multiplication.
    
    """
    
    def __init__(self, k: int, l: int, q: int = None):
        self.k = k
        self.l = l
        self.q = q or (2**256 - 2**224 + 2**192 + 2**128 - 1)
        
        # Generate random l x k matrix (the hash function itself)
        # Each entry is a random element in F_q
        self.matrix = np.array(
            [[random.randint(0, self.q - 1) for _ in range(k)] for _ in range(l)],
            dtype=object
        )
    
    def hash(self, x: List[int]) -> List[int]:
        if len(x) != self.k:
            raise ValueError(f"Input dimension mismatch. Expected {self.k}, got {len(x)}")
        
        result = []
        for i in range(self.l):
            val = 0
            for j in range(self.k):
                val = (val + self.matrix[i][j] * x[j]) % self.q
            result.append(val)
        
        return result
    
    def has_surjective_property(self, subspace_dim: int) -> bool:
        return subspace_dim >= self.l