#!/usr/bin/env python3
import os
import time
import argparse
import multiprocessing
import numpy as np
import socket
from datetime import datetime


def cpu_intensive_task(task_id, complexity=10000000, return_dict=None):
    """A CPU-intensive task that performs mathematical operations."""
    hostname = socket.gethostname()
    cpu_id = multiprocessing.current_process().name
    pid = os.getpid()
    
    start_time = time.time()
    
    # Some CPU-intensive computation
    result = 0
    for i in range(complexity):
        result += np.sin(i) * np.cos(i)
    
    end_time = time.time()
    duration = end_time - start_time
    
    task_info = {
        'task_id': task_id,
        'hostname': hostname,
        'cpu_id': cpu_id,
        'pid': pid,
        'duration': duration,
        'start_time': start_time,
        'end_time': end_time
    }
    
    if return_dict is not None:
        return_dict[task_id] = task_info
    
    return task_info


def run_sequential(num_tasks, complexity):
    """Run tasks sequentially."""
    print(f"Running {num_tasks} tasks sequentially...")
    
    start_time = time.time()
    results = {}
    
    for i in range(num_tasks):
        result = cpu_intensive_task(i, complexity)
        results[i] = result
        print(f"Task {i} completed on {result['hostname']} (PID: {result['pid']}) in {result['duration']:.2f} seconds")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    return results, total_time


def run_parallel(num_tasks, num_processes, complexity):
    """Run tasks in parallel using multiprocessing."""
    print(f"Running {num_tasks} tasks in parallel with {num_processes} processes...")
    
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    
    start_time = time.time()
    
    # Create a pool of worker processes
    pool = multiprocessing.Pool(processes=num_processes)
    
    # Submit tasks to the pool
    for i in range(num_tasks):
        job = pool.apply_async(cpu_intensive_task, args=(i, complexity, return_dict))
        jobs.append(job)
    
    # Wait for all tasks to complete
    for job in jobs:
        job.get()
    
    # Close the pool and wait for workers to exit
    pool.close()
    pool.join()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Print individual task results
    for task_id in sorted(return_dict.keys()):
        result = return_dict[task_id]
        print(f"Task {task_id} completed on {result['hostname']} (PID: {result['pid']}) in {result['duration']:.2f} seconds")
    
    return dict(return_dict), total_time


def analyze_results(sequential_results, sequential_time, parallel_results, parallel_time, num_processes):
    """Analyze and compare the results of sequential and parallel runs."""
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    
    # Calculate speedup
    speedup = sequential_time / parallel_time
    efficiency = speedup / num_processes
    
    print(f"Total sequential execution time: {sequential_time:.2f} seconds")
    print(f"Total parallel execution time:   {parallel_time:.2f} seconds")
    print(f"Speedup:                         {speedup:.2f}x")
    print(f"Parallel efficiency:             {efficiency:.2f} ({efficiency*100:.2f}%)")
    
    # Check if tasks ran on different processors/nodes
    seq_hosts = {result['hostname'] for result in sequential_results.values()}
    par_hosts = {result['hostname'] for result in parallel_results.values()}
    
    print("\nProcessor/Node Distribution:")
    print(f"Sequential tasks ran on {len(seq_hosts)} hosts: {', '.join(seq_hosts)}")
    print(f"Parallel tasks ran on {len(par_hosts)} hosts: {', '.join(par_hosts)}")
    
    # Count unique PIDs
    seq_pids = {result['pid'] for result in sequential_results.values()}
    par_pids = {result['pid'] for result in parallel_results.values()}
    
    print(f"\nUnique processes used:")
    print(f"Sequential: {len(seq_pids)} processes")
    print(f"Parallel:   {len(par_pids)} processes")
    
    # Check overlapping executions in parallel mode
    par_times = [(r['start_time'], r['end_time']) for r in parallel_results.values()]
    max_concurrent = 0
    
    for i, (start_i, end_i) in enumerate(par_times):
        concurrent = 1
        for j, (start_j, end_j) in enumerate(par_times):
            if i != j and start_j < end_i and end_j > start_i:
                concurrent += 1
        max_concurrent = max(max_concurrent, concurrent)
    
    print(f"\nMaximum concurrent executions detected: {max_concurrent}")
    
    # Check for SLURM environment
    slurm_jobid = os.environ.get('SLURM_JOB_ID')
    slurm_cpus = os.environ.get('SLURM_CPUS_PER_TASK')
    slurm_nodes = os.environ.get('SLURM_JOB_NUM_NODES')
    slurm_tasks_per_node = os.environ.get('SLURM_TASKS_PER_NODE')
    
    print("\nSLURM Environment:")
    if slurm_jobid:
        print(f"SLURM_JOB_ID: {slurm_jobid}")
        print(f"SLURM_CPUS_PER_TASK: {slurm_cpus}")
        print(f"SLURM_JOB_NUM_NODES: {slurm_nodes}")
        print(f"SLURM_TASKS_PER_NODE: {slurm_tasks_per_node}")
    else:
        print("Not running under SLURM or SLURM environment variables not found.")
    
    # Conclusion
    print("\nCONCLUSION:")
    if speedup > 1.5:
        print("✅ Parallelization is working effectively! Significant speedup achieved.")
    elif speedup > 1.0:
        print("⚠️ Parallelization provides some benefit, but the speedup is modest.")
    else:
        print("❌ Parallelization is not effective. Sequential execution was faster.")
        print("   This could be due to overhead or resource contention.")


def main():
    parser = argparse.ArgumentParser(description='Test multiprocessing performance on SLURM')
    parser.add_argument('-t', '--tasks', type=int, default=10, help='Number of tasks to run')
    parser.add_argument('-p', '--processes', type=int, default=None, 
                        help='Number of processes to use (defaults to number of CPU cores)')
    parser.add_argument('-c', '--complexity', type=int, default=10000000, 
                        help='Task complexity (higher values mean longer tasks)')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output file to save results (optional)')
    
    args = parser.parse_args()
    
    # Set number of processes to use
    if args.processes is None:
        if 'SLURM_CPUS_PER_TASK' in os.environ:
            args.processes = int(os.environ['SLURM_CPUS_PER_TASK'])
        else:
            args.processes = multiprocessing.cpu_count()
    
    # Print system info
    print(f"Running on host: {socket.gethostname()}")
    print(f"System has {multiprocessing.cpu_count()} CPU cores available")
    print(f"Test configured to use {args.processes} processes for parallel execution")
    print(f"Task complexity: {args.complexity}")
    print("\n" + "="*80)
    
    # Run sequential test
    seq_results, seq_time = run_sequential(args.tasks, args.complexity)
    
    print("\n" + "="*80)
    
    # Run parallel test
    par_results, par_time = run_parallel(args.tasks, args.processes, args.complexity)
    
    # Analyze results
    analyze_results(seq_results, seq_time, par_results, par_time, args.processes)
    
    # Save results to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(f"Test run on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Host: {socket.gethostname()}\n")
            f.write(f"Tasks: {args.tasks}\n")
            f.write(f"Processes: {args.processes}\n")
            f.write(f"Complexity: {args.complexity}\n")
            f.write(f"Sequential time: {seq_time:.2f} seconds\n")
            f.write(f"Parallel time: {par_time:.2f} seconds\n")
            f.write(f"Speedup: {seq_time/par_time:.2f}x\n")
            
            f.write("\nSequential task details:\n")
            for task_id, result in seq_results.items():
                f.write(f"Task {task_id}: {result['hostname']} (PID: {result['pid']}) - {result['duration']:.2f}s\n")
            
            f.write("\nParallel task details:\n")
            for task_id, result in par_results.items():
                f.write(f"Task {task_id}: {result['hostname']} (PID: {result['pid']}) - {result['duration']:.2f}s\n")


if __name__ == "__main__":
    main()
