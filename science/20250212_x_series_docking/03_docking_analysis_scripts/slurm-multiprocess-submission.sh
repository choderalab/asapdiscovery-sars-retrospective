#!/bin/bash
#SBATCH --job-name=mp_test
#SBATCH --output=mp_test_%j.out
#SBATCH --error=mp_test_%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=8  # Request 8 CPU cores
#SBATCH --mem=4G

# Load any required modules (uncomment and modify as needed)
# module load python/3.8

# load env
mamba activate harbor

# Create a directory for output files
mkdir -p mp_test_results

# Run the Python script with different numbers of processes
echo "Running multiprocessing tests..."

# First test with 1 process (essentially sequential)
echo "Test with 1 process:"
python multiprocessing_test.py --tasks 20 --processes 1 --complexity 10000000 --output mp_test_results/test_p1.txt

# Test with 2 processes
echo -e "\n\nTest with 2 processes:"
python multiprocessing_test.py --tasks 20 --processes 2 --complexity 10000000 --output mp_test_results/test_p2.txt

# Test with 4 processes
echo -e "\n\nTest with 4 processes:"
python multiprocessing_test.py --tasks 20 --processes 4 --complexity 10000000 --output mp_test_results/test_p4.txt

# Test with 8 processes (matches cpus-per-task)
echo -e "\n\nTest with 8 processes:"
python multiprocessing_test.py --tasks 20 --processes 8 --complexity 10000000 --output mp_test_results/test_p8.txt

# Test with auto-detection (should use SLURM_CPUS_PER_TASK)
echo -e "\n\nTest with auto-detected processes:"
python multiprocessing_test.py --tasks 20 --complexity 10000000 --output mp_test_results/test_auto.txt

echo "All tests completed"
