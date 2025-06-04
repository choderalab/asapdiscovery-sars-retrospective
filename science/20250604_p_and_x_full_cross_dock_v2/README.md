# Implementing Everything in Nextflow: Part 2

## Notes
Multiple nextflow workflows can't be run at the same time within the same directory unless the workDir is specified each time you run it. To make it explicit I've moved all the workflows to their own directories, with their own script directories.

The only file assumed to be present is `params.curatedFragalysis = "${params.dataPath}/mpro_fragalysis-04-01-24_curated"`, which I have manually curated, which means it will likely need to be included in the data for the paper, as automatically generating it from a fragalysis download is difficult.
