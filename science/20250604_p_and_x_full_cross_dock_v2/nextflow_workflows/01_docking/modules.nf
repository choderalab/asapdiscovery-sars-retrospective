process CROSS_DOCK_BY_LIGAND {
    publishDir "${params.dockedFiles}/${posit_method}_${num_poses}_poses", mode: 'link', overwrite: true
    conda "${params.drugforge}"
    tag "cross-dock ${compound_name}"
    clusterOptions '--partition "cpu" --cpus-per-task=32'
    errorStrategy = { task.exitStatus in [137,140,143,247] ? 'retry' : 'finish' } // retry if the task is killed bc out of memory or time, otherwise ignore and move on

    // Dynamic memory allocation
    memory { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 8.GB : 256.GB }

    // Dynamic time allocation
    time { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 2.h : 2.h }
//     time { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 30.m : 10.m }

    input:
    tuple path(input_dir), path(prepped_dir), val(compound_name), path(ligandFile2d)
    val posit_method
    val selector
    val num_poses

    output:
    path("*_docked/*"), emit: docked

    script:
    """
    asap-docking cross-docking \
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
    --num-poses "${num_poses}" \
    --use-dask \
    --dask-type local \
    --dask-n-workers 32
    """
}