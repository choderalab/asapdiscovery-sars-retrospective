import multiprocessing as mp
from argparse import ArgumentParser
import pandas as pd
import harbor.analysis.cross_docking as cd
from pathlib import Path
import logging
from typing import Optional, Union
import os


# copied from asapdiscovery
class FileLogger:
    def __init__(
        self,
        logname: str,
        path: str,
        logfile: Optional[str] = None,
        level: Optional[Union[int, str]] = logging.DEBUG,
        format: Optional[
            str
        ] = "%(asctime)s | %(name)s | %(levelname)s | %(filename)s | %(funcName)s | %(message)s",
        stdout: Optional[bool] = False,
    ):
        self.name = logname
        self.logfile = logfile
        self.format = format
        self.level = level
        self.stdout = stdout

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)

        if self.logfile:
            self.handler = logging.FileHandler(
                os.path.join(path, self.logfile), mode="w"
            )
            self.handler.setLevel(self.level)
            self.formatter = logging.Formatter(self.format)
            self.handler.setFormatter(self.formatter)
            self.logger.addHandler(self.handler)

    def getLogger(self) -> logging.Logger:
        return self.logger

    def set_level(self, level: int) -> None:
        self.logger.setLevel(level)
        self.handler.setLevel(level)


def get_args():
    parser = ArgumentParser(description="Run full cross docking evaluation")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to the input csv file containing the cross docking data. "
        "Must contain columns:"
        "Query_Ligand,"
        "Reference_Structure,"
        "Reference_Ligand_SMILES,"
        "SMILES,docking-confidence-POSIT,"
        "RMSD,"
        "Pose_ID,"
        "POSIT_Method,"
        "Reference_Ligand,"
        "Docking_Score,"
        "Query_Structure,"
        "Reference_Structure_Date,"
        "Query_Structure_Date",
        required=True,
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to the output directory where the results will be stored",
        required=True,
    )
    parser.add_argument(
        "--n-cpus",
        type=int,
        help="Number of cpus to use for parallel processing",
        default=1,
    )
    parser.add_argument("--job-id", type=str, required=True)
    parser.add_argument(
        "--evaluator-json",
        type=Path,
        required=True,
        nargs="+",
        help="Path to the evaluator json file",
    )
    return parser.parse_args()


def main():
    args = get_args()
    output_dir = args.output / args.job_id
    output_dir.mkdir(exist_ok=True, parents=True)

    logger = FileLogger(
        logname="run_cross_docking_evaluators",
        path=output_dir,
        logfile="run_cross_docking_evaluators.log",
    ).getLogger()
    logger.info("Reading input data")
    df = pd.read_csv(args.input, index_col=0)

    logger.info(f"Reading in {len(args.evaluator_json)} evaluators")
    evaluators = [
        cd.Evaluator.from_json_file(evaluator_json)
        for evaluator_json in args.evaluator_json
    ]

    import os

    ncores = int(os.environ["SLURM_CPUS_PER_TASK"])
    nprocs = min(mp.cpu_count(), len(evaluators), args.n_cpus, ncores)
    logger.info(f"CPUs: {mp.cpu_count()}")
    logger.info(f"N Processes: {len(evaluators)}")
    logger.info(f"SLURM_CPUS_PER_TASK: {ncores}")
    logger.info(f"N Cores: {args.n_cpus}")
    logger.info(f"Running {len(evaluators)} evaluations across {nprocs} cpus")

    from functools import partial

    evaluator_with_df = partial(cd.Results.calculate_result, df=df)

    with mp.Pool(nprocs) as p:
        result = p.map_async(evaluator_with_df, evaluators)
        results = result.get()

    logger.info(f"Writing results to disk at {output_dir}")
    results_df = cd.Results.df_from_results(results)
    results_df.to_csv(output_dir / "results.csv", index=False)


if __name__ == "__main__":
    main()
