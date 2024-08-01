So it looks like using local dask on lilac is working.

I can forward the dask output with something like 
```bash
ssh -o ServerAliveInterval=120 -A -L 8001:localhost:9000 lilac ssh -L 9000:127.0.0.1:8787 -N lt18
```
and then open a browser on my local machine to `localhost:8001` to see the dask dashboard.

Now I'm checking PR #1005 to see if that will make multipose docking work sufficiently to get some results.

This was the initial test:
[run_cross_docking_multiple_poses_local_dask_test.sh](run_cross_docking_multiple_poses_local_dask_test.sh)

But loading the whole fragalysis directory takes awhile, so I tried this:
[run_cross_docking_multiple_poses_local_dask_test_single_pdb.sh](run_cross_docking_multiple_poses_local_dask_test_single_pdb.sh)

I also tried this to speed things up more, but it fails (no poses found):
[run_cross_docking_multiple_poses_local_dask_test_single_pdb_single_lig.sh](run_cross_docking_multiple_poses_local_dask_test_single_pdb_single_lig.sh)

About here is when I realized that I should try to get the results saving properly.

So I ended up using this script for a while to troubleshoot actually getting the results to save (in #1009): [run_cross_docking_multiple_poses_local_dask_test_single_pdb_multipose_results_saving.sh](run_cross_docking_multiple_poses_local_dask_test_single_pdb_multipose_results_saving.sh)


That is basically working now (as of https://github.com/choderalab/asapdiscovery/pull/1009/commits/3e6cde3d085103d9d0877ef7be95f53820d426bd)

So I made a version that runs as an array job (an array job across each ligand that uses dask to parallelize docking across each structure) here: [run_cross_docking_multiple_poses_local_dask_multipose_saving_array.sh](run_cross_docking_multiple_poses_local_dask_multipose_saving_array.sh)

Unfortunately I forgot a `/` in the output directory, so the results look like "20240424_multi_pose_docking_cross_docking1" with the final number corresponding to the ligand number. I've fixed that in the script just in case I need to run it again.
