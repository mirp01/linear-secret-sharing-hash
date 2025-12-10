import benchmarking
from benchmarking import PerformanceBenchmark

if __name__ == "__main__":
    benchmark = PerformanceBenchmark("simple")  # or "hashed"
    
    # Benchmark 1: Secret size scaling (1KB to 1MB)
    #secret_sizes = [1024, 10*1024, 50*1024, 100*1024, 500*1024, 1024*1024]
    secret_sizes = [1024, 10*1024, 50*1024]
    benchmark.benchmark_secret_size_scaling(secret_sizes, n=10, t=5)
    
    # Benchmark 2: Threshold scaling
    benchmark.benchmark_threshold_scaling(secret_size=10*1024, n=20, thresholds=[3, 5, 10, 15, 20])
    
    # Benchmark 3: Share count scaling
    benchmark.benchmark_share_count_scaling(secret_size=10*1024, t=5, share_counts=[5, 10, 20, 30, 50])
    
    # Print summary
    benchmark.print_summary()
    
    # Plot results
    benchmark.plot_secret_size_scaling()
    
    # Export results
    benchmark.export_results()