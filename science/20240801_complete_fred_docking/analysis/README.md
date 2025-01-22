# Post-Processing Steps

1. Organize data to make it easier to calculate RMSD
2. Filter similar poses and calculate RMSD to crystalized ligand 
3. Collect all csvs into a single csv
4. Run analysis

# 2024.12.13
Ok so after finally analyzing I realized that about half of the structures are aligned incorrectly.

# 2025.01.07
Figured out https://github.com/asapdiscovery/asapdiscovery/issues/1274
Re-doing everything starting from prep. Thankfully I wrote down everything as scripts so should be easy to reproduce.