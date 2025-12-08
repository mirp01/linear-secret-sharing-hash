import time
import json
import statistics
from typing import List, Tuple
import matplotlib.pyplot as plt
from shamir import ShamirSecretSharing as SimpleShamir

class PerformanceBenchmark:
    """
    Comprehensive benchmark suite for Shamir's Secret Sharing schemes.
    Measures: latency, throughput, scalability across different parameters.
    """
    
    def __init__(self):
        self.shamir = SimpleShamir()
        self.results = {
            'secret_size': [],
            'n_shares': [],
            'threshold': [],
            'share_time_ms': [],
            'reconstruct_time_ms': [],
            'throughput_mbps': []
        }
    
    def benchmark_sharing(self, secret: bytes, n: int, k: int, iterations: int = 5) -> Tuple[float, float, float]:
        """
        Benchmark sharing phase.
        Returns: (min_time_ms, avg_time_ms, max_time_ms)
        """
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            _ = self.shamir.split_secret(secret, n, k)
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
            _ = self.shamir.reconstruct_secret(shares)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        return min(times), statistics.mean(times), max(times)
    
    def benchmark_secret_size_scaling(self, secret_sizes: List[int], n: int = 10, k: int = 5):
        """
        Benchmark how performance scales with secret size.
        """
        print("\n" + "="*70)
        print("BENCHMARK 1: Secret Size Scaling")
        print("="*70)
        print(f"Parameters: n={n}, k={k}")
        print(f"Testing secret sizes: {secret_sizes}\n")
        
        for size in secret_sizes:
            secret = b'X' * size
            
            # Benchmark sharing
            min_share, avg_share, max_share = self.benchmark_sharing(secret, n, k)
            
            # Get shares for reconstruction benchmark
            shares = self.shamir.split_secret(secret, n, k)
            
            # Benchmark reconstruction
            min_recon, avg_recon, max_recon = self.benchmark_reconstruction(shares[:k])
            
            # Calculate throughput (MB/s)
            throughput = (size / (1024 * 1024)) / (avg_share / 1000)  # MB/s
            
            self.results['secret_size'].append(size)
            self.results['n_shares'].append(n)
            self.results['threshold'].append(k)
            self.results['share_time_ms'].append(avg_share)
            self.results['reconstruct_time_ms'].append(avg_recon)
            self.results['throughput_mbps'].append(throughput)
            
            print(f"Secret size: {size:6d} bytes")
            print(f"  Sharing:       min={min_share:8.4f}ms  avg={avg_share:8.4f}ms  max={max_share:8.4f}ms")
            print(f"  Reconstruction: min={min_recon:8.4f}ms  avg={avg_recon:8.4f}ms  max={max_recon:8.4f}ms")
            print(f"  Throughput:    {throughput:8.4f} MB/s")
            print()
    
    def benchmark_threshold_scaling(self, secret_size: int, n: int, thresholds: List[int]):
        """
        Benchmark how performance scales with threshold k.
        """
        print("\n" + "="*70)
        print("BENCHMARK 2: Threshold Scaling")
        print("="*70)
        print(f"Parameters: secret_size={secret_size}, n={n}")
        print(f"Testing thresholds: {thresholds}\n")
        
        secret = b'X' * secret_size
        
        for k in thresholds:
            if k > n:
                print(f"Skipping k={k} (greater than n={n})")
                continue
            
            # Benchmark sharing
            min_share, avg_share, max_share = self.benchmark_sharing(secret, n, k)
            
            # Get shares for reconstruction benchmark
            shares = self.shamir.split_secret(secret, n, k)
            
            # Benchmark reconstruction
            min_recon, avg_recon, max_recon = self.benchmark_reconstruction(shares[:k])
            
            print(f"Threshold k: {k:2d}/{n}")
            print(f"  Sharing:       min={min_share:8.4f}ms  avg={avg_share:8.4f}ms  max={max_share:8.4f}ms")
            print(f"  Reconstruction: min={min_recon:8.4f}ms  avg={avg_recon:8.4f}ms  max={max_recon:8.4f}ms")
            print()
    
    def benchmark_share_count_scaling(self, secret_size: int, k: int, share_counts: List[int]):
        """
        Benchmark how performance scales with number of shares n.
        """
        print("\n" + "="*70)
        print("BENCHMARK 3: Share Count Scaling")
        print("="*70)
        print(f"Parameters: secret_size={secret_size}, k={k}")
        print(f"Testing share counts: {share_counts}\n")
        
        secret = b'X' * secret_size
        
        for n in share_counts:
            if k > n:
                print(f"Skipping n={n} (less than k={k})")
                continue
            
            # Benchmark sharing
            min_share, avg_share, max_share = self.benchmark_sharing(secret, n, k)
            
            # Get shares for reconstruction benchmark
            shares = self.shamir.split_secret(secret, n, k)
            
            # Benchmark reconstruction
            min_recon, avg_recon, max_recon = self.benchmark_reconstruction(shares[:k])
            
            print(f"Shares n: {n:3d} (with k={k})")
            print(f"  Sharing:       min={min_share:8.4f}ms  avg={avg_share:8.4f}ms  max={max_share:8.4f}ms")
            print(f"  Reconstruction: min={min_recon:8.4f}ms  avg={avg_recon:8.4f}ms  max={max_recon:8.4f}ms")
            print()
    
    def plot_secret_size_scaling(self):
        """Plot performance vs secret size"""
        secret_sizes = [s for s in self.results['secret_size']]
        share_times = [t for t in self.results['share_time_ms']]
        recon_times = [t for t in self.results['reconstruct_time_ms']]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
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
        
        # Plot 4: Throughput
        throughputs = [t for t in self.results['throughput_mbps']]
        ax4.plot(secret_sizes, throughputs, 'g-o', linewidth=2, markersize=8)
        ax4.set_xlabel('Secret Size (bytes)', fontsize=11)
        ax4.set_ylabel('Throughput (MB/s)', fontsize=11)
        ax4.set_title('Sharing Throughput vs Secret Size', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.set_xscale('log')
        
        plt.tight_layout()
        plt.savefig('benchmark_secret_scaling.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: benchmark_secret_scaling.png")
        plt.show()
    
    def export_results(self, filename: str = 'benchmark_results.json'):
        """Export results to JSON for further analysis"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Results exported to {filename}")
    
    def print_summary(self):
        """Print summary statistics"""
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
        
        throughputs = self.results['throughput_mbps']
        if throughputs:
            print(f"\nThroughput:")
            print(f"  Min:    {min(throughputs):8.4f} MB/s")
            print(f"  Max:    {max(throughputs):8.4f} MB/s")
            print(f"  Avg:    {statistics.mean(throughputs):8.4f} MB/s")

