workflow {
    // Collect all .csv files into a channel
    csv_files = Channel.fromPath("${params.inputDir}/*.csv")

    // Pass the collected files to the process
    COMBINE_CHEMICAL_SIMILARITY_DATA(csv_files)
}

