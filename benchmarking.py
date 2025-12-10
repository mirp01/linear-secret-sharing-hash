import time
import json
import statistics
from typing import List, Tuple
import matplotlib.pyplot as plt
from shamir import ShamirSecretSharing as SimpleShamir
from shamir_with_hash import LSSSWithHashing as HashedShamir

class PerformanceBenchmark:
    """
    Measures: latency, scalability across different parameters.
    Generates plots and summary statistics.
    """
    
    def __init__(self, implementation: "simple"):
        if implementation == "simple":
            self.shamir = SimpleShamir()
        else:
            self.shamir = HashedShamir()
        
        self.implementation = implementation

        self.results = {
            'secret_size': [],
            'n_shares': [],
            'threshold': [],
            'share_time_ms': [],
            'reconstruct_time_ms': [],
        }
    
    def benchmark_sharing(self, secret: bytes, n: int, t: int, iterations: int = 5) -> Tuple[float, float, float]:
        """
        Benchmark sharing phase.
        Returns: (min_time_ms, avg_time_ms, max_time_ms)
        """
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            _ = self.shamir.split_secret(secret, n, t)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        return min(times), statistics.mean(times), max(times)
    
    def benchmark_reconstruction(self, shares: List[List[Tuple[int, int]]], iterations: int = 5) -> Tuple[float, float, float]:
        """
        Benchmark reconstruction phase.
        Returns: (min_time_ms, avg_time_ms, max_time_ms)
        """
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            if self.implementation == "simple":
                _ = self.shamir.reconstruct_secret(shares)
            #else:
                #sss_hash = HashedShamir()

            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        return min(times), statistics.mean(times), max(times)
    
    def benchmark_secret_size_scaling(self, secret_sizes: List[int], n: int = 10, t: int = 5):
        print("\n" + "-"*70)
        print("BENCHMARK 1: Secret Size Scaling")
        print("-"*70)
        print(f"Parameters: n={n}, t={t}")
        print(f"Testing secret sizes: {secret_sizes}\n")
        
        for size in secret_sizes:
            secret = b'X' * size
            
            # Benchmart sharing
            min_share, avg_share, max_share = self.benchmark_sharing(secret, n, t)
            
            # Get shares for reconstruction benchmart
            shares = self.shamir.split_secret(secret, n, t)
            
            # Benchmart reconstruction
            min_recon, avg_recon, max_recon = self.benchmark_reconstruction(shares[:t])
            
            self.results['secret_size'].append(size)
            self.results['n_shares'].append(n)
            self.results['threshold'].append(t)
            self.results['share_time_ms'].append(avg_share)
            self.results['reconstruct_time_ms'].append(avg_recon)
            
            print(f"Secret size: {size:6d} bytes")
            print(f"  Sharing:       min={min_share:8.4f}ms  avg={avg_share:8.4f}ms  max={max_share:8.4f}ms")
            print(f"  Reconstruction: min={min_recon:8.4f}ms  avg={avg_recon:8.4f}ms  max={max_recon:8.4f}ms")
            print()
    
    def benchmark_threshold_scaling(self, secret_size: int, n: int, thresholds: List[int]):
        """
        Benchmark how performance scales with threshold t.
        """
        print("\n" + "-"*70)
        print("BENCHMARK 2: Threshold Scaling")
        print("-"*70)
        print(f"Parameters: secret_size={secret_size}, n={n}")
        print(f"Testing thresholds: {thresholds}\n")
        
        secret = b'X' * secret_size
        
        for t in thresholds:
            if t > n:
                print(f"Stipping t={t} (greater than n={n})")
                continue
            
            # Benchmark sharing
            min_share, avg_share, max_share = self.benchmark_sharing(secret, n, t)
            
            # Get shares for reconstruction benchmart
            shares = self.shamir.split_secret(secret, n, t)
            
            # Benchmart reconstruction
            if self.implementation == "simple":
                min_recon, avg_recon, max_recon = self.benchmark_reconstruction(shares[:t])
            else:
                sss_hash = HashedShamir()
                shares_hashing, hash_func = sss_hash.split_secret(secret, shares, threshold)
                reconstructed_hash = sss_hash.reconstruct_secret(shares_hashing[:threshold], hash_func)
            
            print(f"Threshold t: {t:2d}/{n}")
            print(f"  Sharing:       min={min_share:8.4f}ms  avg={avg_share:8.4f}ms  max={max_share:8.4f}ms")
            print(f"  Reconstruction: min={min_recon:8.4f}ms  avg={avg_recon:8.4f}ms  max={max_recon:8.4f}ms")
            print()
    
    def benchmark_share_count_scaling(self, secret_size: int, t: int, share_counts: List[int]):
        """
        Benchmark how performance scales with number of shares n.
        """
        print("\n" + "-"*70)
        print("BENCHMARK 3: Share Count Scaling")
        print("-"*70)
        print(f"Parameters: secret_size={secret_size}, t={t}")
        print(f"Testing share counts: {share_counts}\n")
        
        secret = b'X' * secret_size
        
        for n in share_counts:
            if t > n:
                print(f"Stipping n={n} (less than t={t})")
                continue
            
            # Benchmark sharing
            min_share, avg_share, max_share = self.benchmark_sharing(secret, n, t)
            
            # Get shares for reconstruction benchmark
            shares = self.shamir.split_secret(secret, n, t)
            
            # Benchmart reconstruction
            min_recon, avg_recon, max_recon = self.benchmark_reconstruction(shares[:t])
            
            print(f"Shares n: {n:3d} (with t={t})")
            print(f"  Sharing:       min={min_share:8.4f}ms  avg={avg_share:8.4f}ms  max={max_share:8.4f}ms")
            print(f"  Reconstruction: min={min_recon:8.4f}ms  avg={avg_recon:8.4f}ms  max={max_recon:8.4f}ms")
            print()
    
    def plot_secret_size_scaling(self):
        secret_sizes = [s for s in self.results['secret_size']]
        share_times = [t for t in self.results['share_time_ms']]
        recon_times = [t for t in self.results['reconstruct_time_ms']]
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10))
        
        # Plot 1: Sharing time vs secret size
        ax1.plot(secret_sizes, share_times, 'b-o', linewidth=2, markersize=8)
        ax1.set_xlabel('Secret Size (bytes)', fontsize=11)
        ax1.set_ylabel('Sharing Time (ms)', fontsize=11)
        ax1.set_title('Sharing Time vs Secret Size', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
        ax1.set_xscale('log')
        
        # Plot 2: Reconstruction time vs secret size
        ax2.plot(secret_sizes, recon_times, 'r-o', linewidth=2, markersize=8)
        ax2.set_xlabel('Secret Size (bytes)', fontsize=11)
        ax2.set_ylabel('Reconstruction Time (ms)', fontsize=11)
        ax2.set_title('Reconstruction Time vs Secret Size', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')
        ax2.set_xscale('log')
        
        # Plot 3: Both on same graph
        ax3.plot(secret_sizes, share_times, 'b-o', label='Sharing', linewidth=2, markersize=8)
        ax3.plot(secret_sizes, recon_times, 'r-o', label='Reconstruction', linewidth=2, markersize=8)
        ax3.set_xlabel('Secret Size (bytes)', fontsize=11)
        ax3.set_ylabel('Time (ms)', fontsize=11)
        ax3.set_title('Sharing vs Reconstruction Time', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        ax3.set_yscale('log')
        ax3.set_xscale('log')
        
        plt.tight_layout()
        plt.savefig('benchmark_secret_scaling.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def export_results(self, filename: str = 'benchmark_results.json'):
        """Export results to JSON for further analysis"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Results exported to {filename}")
    
    def print_summary(self):
        if not self.results['share_time_ms']:
            print("No results to summarize")
            return
        
        print("\n" + "="*70)
        print("SUMMARY STATISTICS")
        print("="*70)
        
        share_times = self.results['share_time_ms']
        recon_times = self.results['reconstruct_time_ms']
        
        print(f"\nSharing Phase:")
        print(f"  Min:    {min(share_times):8.4f} ms")
        print(f"  Max:    {max(share_times):8.4f} ms")
        print(f"  Avg:    {statistics.mean(share_times):8.4f} ms")
        print(f"  Median: {statistics.median(share_times):8.4f} ms")
        print(f"  StdDev: {statistics.stdev(share_times):8.4f} ms")
        
        print(f"\nReconstruction Phase:")
        print(f"  Min:    {min(recon_times):8.4f} ms")
        print(f"  Max:    {max(recon_times):8.4f} ms")
        print(f"  Avg:    {statistics.mean(recon_times):8.4f} ms")
        print(f"  Median: {statistics.median(recon_times):8.4f} ms")
        print(f"  StdDev: {statistics.stdev(recon_times):8.4f} ms")
        

