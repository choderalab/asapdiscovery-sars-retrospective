import multiprocessing as mp
from argparse import ArgumentParser
import pandas as pd
import numpy as np
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

        # if self.stdout:
        #     console = Console()
        #     rich_handler = RichHandler(console=console)
        #     self.logger.addHandler(rich_handler)

    def getLogger(self) -> logging.Logger:
        return self.logger

    def set_level(self, level: int) -> None:
        self.logger.setLevel(level)
        self.handler.setLevel(level)


from pydantic import BaseModel


class Results(BaseModel):
    evaluator: cd.Evaluator
    fraction_good: cd.FractionGood

    def get_records(self) -> dict:
        mydict = self.evaluator.get_records()
        mydict.update(self.fraction_good.get_records())
        return mydict

    @classmethod
    def calculate_result(cls, evaluator: cd.Evaluator, df: pd.DataFrame) -> "Results":
        result = evaluator.run(df)
        return cls(evaluator=evaluator, fraction_good=result)

    @classmethod
    def calculate_results(
        cls, df: pd.DataFrame, evaluators: list[cd.Evaluator], cpus: int = 1
    ) -> list["Results"]:
        with mp.Pool(cpus) as p:
            return p.starmap(
                cls.calculate_result,
                [(evaluator, df) for evaluator in evaluators],
            )

    @classmethod
    def df_from_results(cls, results: list["Results"]) -> pd.DataFrame:
        return pd.DataFrame.from_records([result.get_records() for result in results])


def get_args():
    parser = ArgumentParser(description="Run full cross docking evaluation")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to the input csv file containing the cross docking data",
        required=True,
    )
    parser.add_argument("--date_dict_path", type=str, help="Path to the date dict")
    parser.add_argument(
        "--parameters",
        type=Path,
        help="Path to the parameters yaml file",
        required=False,
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to the output directory where the results will be stored",
        required=True,
    )
    parser.add_argument(
        "--n_cpus",
        type=int,
        help="Number of cpus to use for parallel processing",
        default=1,
    )
    return parser.parse_args()


def main():
    args = get_args()
    args.output.mkdir(exist_ok=True, parents=True)
    output_dir = args.output
    logger = FileLogger(
        logname="run_full_cross_docking_evaluation",
        path=args.output,
        logfile="run_full_cross_docking_evaluation.log",
    ).getLogger()
    logger.info("Reading input data")
    df = pd.read_csv(args.input)

    logger.info("Reading parameters")
    if args.parameters:
        settings = cd.Settings.from_yml_file(args.parameters)
    else:
        settings = cd.Settings(date_dict_path=args.date_dict_path)
    settings.to_yml_file(output_dir / "settings.yml")

    logger.info("Loading date dict")
    import json

    with open(settings.date_dict_path, "r") as f:
        date_dict = json.load(f)
    simplified_date_dict = {
        ref_structure: date_dict[ref_structure[:-3]]
        for ref_structure in df.Reference_Structure.unique()
    }

    logger.info("Setting up evaluators")
    evaluators = []

    # Set up pose selectors
    pose_selectors = [
        cd.PoseSelector(
            name="PoseSelection", variable="Pose_ID", number_to_return=n_poses
        )
        for n_poses in settings.n_poses
    ]
    # add a default one
    pose_selectors.append(
        cd.PoseSelector(name="Default", variable="Pose_ID", number_to_return=1)
    )

    # Set up dataset splits
    random_splits = [
        cd.RandomSplit(
            variable=settings.reference_ligand_column,
            n_splits=1,
            n_per_split=n_per_split,
        )
        for n_per_split in settings.n_per_split
    ]
    date_splits = [
        cd.DateSplit(
            variable=settings.reference_ligand_column,
            n_splits=1,
            n_per_split=n_per_split,
            date_dict=simplified_date_dict,
        )
        for n_per_split in settings.n_per_split
    ]

    # add structure choices
    structure_choices = [
        cd.StructureChoice(
            name="Dock_to_All", variable="Tanimoto", higher_is_better=True
        )
    ]
    structure_choices.extend(
        [
            cd.StructureChoice(
                name="ECFP4_Similarity",
                variable="Tanimoto",
                higher_is_better=True,
                number_to_return=n_structures,
            )
            for n_structures in settings.n_structures
        ]
    )
    structure_choices.extend(
        [
            cd.StructureChoice(
                name="MCSS_Similarity",
                variable="Num_Atoms_in_MCS",
                higher_is_better=True,
                number_to_return=n_structures,
            )
            for n_structures in settings.n_structures
        ]
    )

    # Add scorers
    scorers = [
        cd.Scorer(
            name="POSIT_Probability",
            variable="docking-confidence-POSIT",
            number_to_return=1,
        ),
        cd.Scorer(
            name="RMSD", variable="RMSD", higher_is_better=False, number_to_return=1
        ),
    ]
    rmsd_evaluator = cd.BinaryEvaluation(variable="RMSD", cutoff=settings.rmsd_cutoff)

    for scorer in scorers:
        for split in date_splits + random_splits:
            for selector in pose_selectors:
                for structure_choice in structure_choices:
                    evaluators.append(
                        cd.Evaluator(
                            selector=selector,
                            dataset_split=split,
                            structure_choice=structure_choice,
                            scorer=scorer,
                            evaluator=rmsd_evaluator,
                            groupby=[settings.query_ligand_column],
                            n_bootstraps=settings.n_bootstraps,
                        )
                    )

    nprocs = min(mp.cpu_count(), len(evaluators), args.n_cpus)
    logger.info(f"CPUs: {mp.cpu_count()}")
    logger.info(f"N Processes: {len(evaluators)}")
    logger.info(f"N Cores: {args.n_cpus}")
    logger.info(f"Running {len(evaluators)} evaluations across {nprocs} cpus")

    results = Results.calculate_results(df, evaluators, cpus=nprocs)

    logger.info(f"Writing results to disk at {output_dir}")
    results_df = Results.df_from_results(results)
    results_df.to_csv(output_dir / "results.csv", index=False)


if __name__ == "__main__":
    main()
