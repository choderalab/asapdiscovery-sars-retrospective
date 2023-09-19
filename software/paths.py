from pathlib import Path
import yaml
from collections import namedtuple

with open(Path(__file__).parent / 'paths.yaml', 'r') as f:
    path_dict = yaml.safe_load(f)
    prefixes = {key: Path(p) for key, p in path_dict['prefix'].items()}
    prefix = prefixes['lilac'] if prefixes['lilac'].exists() else prefixes['ap_local']

Paths = namedtuple('Paths', list(path_dict['paths'].keys()))
paths = Paths(*list(prefix / p for p in path_dict['paths'].values()))


