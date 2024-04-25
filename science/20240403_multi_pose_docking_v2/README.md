The goal of this directory is to run docking again while keeping multiple poses.

Note - most of these readmes were written afterwards.

I'm going to start with just re-docking, which I did here:
[20240415_self_docking](20240415_self_docking)

Cross docking didn't work at first
[20240416_cross_docking](20240416_cross_docking)

So I tried testing locally
[20240417_cross_docking_local_test](20240417_cross_docking_local_test)

Doubled checked the self docking to make sure it still worked
[20240417_self_docking](20240417_self_docking)

Tried a fix for the cross docking, which didn't work / wasn't good enough
[20240418_cross_docking](20240418_cross_docking)

Hugo reminded me that I could run with local dask, which helped speed things up.
[20240423_cross_docking_with_dask](20240423_cross_docking_with_dask)
I ran a ton of things in here, but this script is the one that ended up working 
[run_cross_docking_multiple_poses_local_dask_multipose_saving_array.sh](20240423_cross_docking_with_dask%2Frun_cross_docking_multiple_poses_local_dask_multipose_saving_array.sh)