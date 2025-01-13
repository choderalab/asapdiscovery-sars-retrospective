import datetime

print(f"Importing cli modules: {datetime.datetime.now()}")
import logging
from typing import Optional, Union

import click
from asapdiscovery.cli.cli_args import (
    active_site_chain,
    cache_dir,
    dask_args,
    fragalysis_dir,
    input_json,
    ligands,
    loglevel,
    md_args,
    ml_scorer,
    output_dir,
    overwrite,
    pdb_file,
    postera_args,
    ref_chain,
    save_to_cache,
    structure_dir,
    target,
    use_only_cache,
)
from asapdiscovery.data.operators.selectors.selector_list import StructureSelector
from asapdiscovery.data.services.postera.manifold_data_validation import TargetTags
from asapdiscovery.data.util.dask_utils import DaskType, FailureMode
from asapdiscovery.docking.openeye import POSIT_METHOD, POSIT_RELAX_MODE
from asapdiscovery.simulation.simulate import OpenMMPlatform
from asapdiscovery.workflows.docking_workflows.cross_docking import (
    CrossDockingWorkflowInputs,
    cross_docking_workflow,
)
from asapdiscovery.workflows.docking_workflows.large_scale_docking import (
    LargeScaleDockingInputs,
    large_scale_docking_workflow,
)
from asapdiscovery.workflows.docking_workflows.ligand_transfer_docking import (
    LigandTransferDockingWorkflowInputs,
    ligand_transfer_docking_workflow,
)
from asapdiscovery.workflows.docking_workflows.small_scale_docking import (
    SmallScaleDockingInputs,
    small_scale_docking_workflow,
)
from asapdiscovery.workflows.docking_workflows.symexp_crystal_packing import (
    SymExpCrystalPackingInputs,
    symexp_crystal_packing_workflow,
)

print(f"Importing cross_docking_workflow modules: {datetime.datetime.now()}")
from pathlib import Path
from shutil import rmtree

from asapdiscovery.data.operators.selectors.selector_list import StructureSelector
from asapdiscovery.data.readers.meta_structure_factory import MetaStructureFactory
from asapdiscovery.data.readers.molfile import MolFileFactory
from asapdiscovery.data.services.postera.manifold_data_validation import (
    rename_output_columns_for_manifold,
)
from asapdiscovery.data.util.dask_utils import BackendType, make_dask_client_meta
from asapdiscovery.data.util.logging import FileLogger
from asapdiscovery.docking.docking import (
    DockingInputMultiStructure,
    write_results_to_multi_sdf,
)
from asapdiscovery.docking.docking_data_validation import DockingResultCols
from asapdiscovery.docking.openeye import POSIT_METHOD, POSIT_RELAX_MODE, POSITDocker
from asapdiscovery.docking.scorer import ChemGauss4Scorer, MetaScorer
from asapdiscovery.modeling.protein_prep import ProteinPrepper
from asapdiscovery.workflows.docking_workflows.workflows import (
    DockingWorkflowInputsBase,
)
from pydantic import Field, PositiveInt

print(f"Done: {datetime.datetime.now()}")
