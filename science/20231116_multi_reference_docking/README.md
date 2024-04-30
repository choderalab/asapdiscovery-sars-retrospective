Ended up running the array version of this! Easier than managing the memory issues

[run_cross_docking_array.sh](cluster_scripts%2Frun_cross_docking_array.sh)

I still hadn't done the LeaveSimilarOutSelector logic by this point so this has the potential problem of including
stereoisomeric pairs, which normally isn't a problem because I can exclude them in post, but for multiref posit docking,
that isn't the case.

There also aren't dataset splits for this, so any of that work will have to be done later.