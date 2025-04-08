#!/bin/bash
#SBATCH --job-name=combine_scafold_date_split_results
#SBATCH --output=logs/combine_scafold_date_split_results.out
#SBATCH --error=logs/combine_scafold_date_split_results.err
#SBATCH --cpus-per-task 1
#SBATCH --partition=cpu
#SBATCH --mem=16GB
#SBATCH --time=0:30:00

source ~/.bashrc
conda activate harbor

echo Start
date

# Directory containing CSV files
input_dir="/data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit/scaffold_split"

# Output file
output_file="combined_results.csv"

touch "$input_dir/$output_file"

# Take header from first CSV file and write to output
head -n 1 $(find "$input_dir/*/" -name "*.csv" | head -n 1) > "$output_file"

# Append all files, skipping their headers
for file in "$input_dir/*"/*.csv; do
    tail -n +2 "$file" >> "$input_dir/$output_file"
done

echo "Combined CSV files into $output_file"


date
echo Done