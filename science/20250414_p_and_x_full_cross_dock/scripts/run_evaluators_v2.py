import multiprocessing as mp
from functools import partial
from pathlib import Path
import click
from harbor.analysis.cross_docking import Evaluator, DockingDataModel, Results
from harbor.analysis.utils import FileLogger


@click.command()
@click.argument(
    "evaluator-jsons",
    nargs=-1,
    type=click.Path(exists=True),
)
@click.option(
    "--input-parquet",
    required=True,
    type=click.Path(exists=True),
    help="Path to the input parquet file containing the cross docking data.",
)
@click.option(
    "--output",
    type=Path,
    default="./",
    help="Path to the output directory where the results will be stored.",
)
@click.option(
    "--n-cpus",
    default=1,
    type=int,
    help="Number of CPUs to use for parallel processing.",
)
def run_evaluators(evaluator_jsons, input_parquet, output, n_cpus):
    output.mkdir(exist_ok=True, parents=True)

    logger = FileLogger(
        logname="run_cross_docking_evaluators",
        path=output,
        logfile="run_cross_docking_evaluators.log",
    ).getLogger()

    logger.info(f"Reading data model from {input_parquet}")
    data = DockingDataModel.deserialize(input_parquet)

    logger.info(f"Reading in {len(evaluator_jsons)} evaluators")
    evaluators = [Evaluator.from_json_file(evaluator) for evaluator in evaluator_jsons]

    nprocs = min(mp.cpu_count(), len(evaluators), n_cpus)
    logger.info(f"CPUs available: {mp.cpu_count()}")
    logger.info(f"Number of evaluators: {len(evaluators)}")
    logger.info(f"Using {nprocs} processes for evaluation")

    evaluator_with_data = partial(Results.calculate_result, df=data)

    with mp.Pool(nprocs) as pool:
        results = pool.map(evaluator_with_data, evaluators)

    logger.info(f"Writing results to disk at {output}")
    results_df = Results.df_from_results(results)
    results_df.to_csv(output / "results.csv", index=False)


if __name__ == "__main__":
    run_evaluators()
