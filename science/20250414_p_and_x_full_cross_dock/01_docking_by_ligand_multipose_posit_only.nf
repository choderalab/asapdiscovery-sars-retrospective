#!/usr/bin/env nextflow

params.numPoses = 100
params.take = 1

process CROSS_DOCK_BY_LIGAND {
    publishDir "${params.dockedFiles}/${posit_method}_multipose", mode: 'link', overwrite: true
    conda "${params.drugforge}"
    tag "cross-dock ${compound_name}"
    clusterOptions '--partition "cpu" --time=04:00:00 --mem=256GB --cpus-per-task=32'
    errorStrategy { task.exitStatus == 140 ? 'retry' : 'ignore' } // retry if the task is killed bc out of memory or time, otherwise ignore and move on

    // Dynamic memory allocation
    memory { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 8.GB : 8.GB }

    // Dynamic time allocation
    time { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 2.h : 2.h }

    input:
    tuple path(input_dir), path(prepped_dir), val(compound_name), path(ligandFile2d)
    val posit_method
    val selector

    output:
    path("*_docked"), emit: docked

    script:
    """
    asap-cli docking cross-docking \
    --target SARS-CoV-2-Mpro \
    --use-omega \
    --omega-dense \
    --allow-retries \
    --allow-final-clash \
    --relax-mode clash \
    --posit-method "${posit_method}" \
    --structure-selector "${selector}" \
    --fragalysis-dir ${input_dir} \
    --ligands "${ligandFile2d}" \
    --cache-dir "${prepped_dir}" \
    --output-dir "${compound_name}_docked" \
    --overwrite \
    --no-save-to-cache \
    --use-only-cache \
    --num-poses "${params.numPoses}" \
    --use-dask \
    --dask-type local \
    --dask-n-workers 32
    """
}

workflow {
    // load in input structure dir
    input_dir = Channel.fromPath("${params.curatedFragalysis}", type: 'dir')
    cache_dir = Channel.fromPath("${params.dataPath}/${params.fixedFragalysisCache}", type: 'dir')

    // Create a channel for each ligand file and flatten it
    ligand_files = Channel
        .fromPath("${params.ligandFiles}/${params.split2dligandFiles}/*.sdf")
        .map { file ->
            def id = file.name.toString().find(/([a-zA-Z0-9_-]+)\.sdf/) { match, code -> code }
            return tuple(id, file)
        }

    // Count ligand_files
    ligand_files.count().view { count -> "Total ligand files found: $count" }

    log.info "Taking ${params.take ?: 'all'} ligand files"

    // Create combinations for parallel processing
    docking_combinations = input_dir
        .combine(cache_dir)
        .combine(ligand_files)
        .take(params.take)

    // Run FRED and POSIT docking in parallel for each combination
//     CROSS_DOCK_BY_LIGAND(
//         docking_combinations,
//         "ALL",
//         "PairwiseSelector"
//     )
}