Well, running with dask doesn't seem to be working:
https://github.com/choderalab/asapdiscovery/issues/965

So I'm going back to using local dask and running with job arrays

(asapdiscovery) paynea@lilac-ln02:/lila/data/chodera/paynea/asapdiscovery-sars-retrospective/science/20240403_multi_pose_docking_v2/self_docking$ ./split_input_sdf.sh
Reading '/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined.sdf'
Flattened molecules to 2D
Saving 205 SDF files to '/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_2d'
Saving 205 files of 1 molecules each
