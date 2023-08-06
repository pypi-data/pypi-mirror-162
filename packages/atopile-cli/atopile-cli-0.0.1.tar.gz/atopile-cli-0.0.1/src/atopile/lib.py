from attr import define
import git
from pathlib import Path
import logging
from .config import atopile_DIR
from hashlib import sha1
import yaml
from typing import List
from urllib.parse import urlsplit

log = logging.getLogger(__name__)

library_path = atopile_DIR / 'library'
library_tracker_path = library_path / '.tracker.yaml'

@define
class LibEntry:
    remote: str
    local: Path

    def slim_remote(self):
        purl = urlsplit(self.remote)
        purl = purl._replace(scheme='')
        if purl.netloc.startswith('www.'):
            purl = purl._replace(netloc=purl.netloc[4:])
        return purl.geturl()[2:]

    def sha1_remote(self):
        return sha1(self.slim_remote().encode()).digest().hex()

    def clone(self) -> git.Repo:
        try:
            repo = git.Repo.clone_from(self.remote, self.local)
        except git.GitCommandError:
            log.error(f'{self.remote} isn\'t a git repo, doesn\'t exist or isn\'t accessible')
            raise
        return repo

    def check_local(self) -> bool:
        try:
            repo = git.Repo(self.local)
        except git.InvalidGitRepositoryError:
            log.error(f'local points to {str(self.local)}, but that isn\'t a git repo')
            raise
        except git.NoSuchPathError:
            log.info(f'Local copy of {self.slim_remote()} not found')
            return False
        else:
            return True

    @classmethod
    def from_remote(cls, remote: str) -> 'LibEntry':
        self = cls(remote, '')
        # get the directory name to clone into
        # using a hash here to get a unique with safe (hex chars)
        self.local = library_path / self.sha1_remote()
        return self
    
    @classmethod
    def from_local(cls, local: Path) -> 'LibEntry':
        try:
            repo = git.Repo(local)
        except git.InvalidGitRepositoryError:
            log.error(f'{local} isn\'t a git repo')
            raise
        remote = repo.remotes[0]
        return cls(remote, local)

def load_lib_entries_from_tracker() -> List[LibEntry]:
    try:
        with library_tracker_path.open() as f:
            tracker_data = yaml.safe_load(f)
    except FileNotFoundError:
        return []

    entries = []
    for entry in tracker_data:
        entries.append(
            LibEntry(
                remote=entry['remote'],
                local=Path(entry['local'])
            )
        )
    return entries
    
def dump_lib_entries_to_tracker(entries: List[LibEntry]):
    tracker_data = []
    for entry in entries:
        tracker_data.append({
            'local': str(entry.local),
            'remote': entry.remote,
        })

    with library_tracker_path.open('w') as f:
        yaml.safe_dump(tracker_data, f)

def generate_table_rows(entry: LibEntry, libs: List[Path]) -> str:
    ouptut = ''
    for lib in libs:
        # format name and uri
        name = f'{entry.slim_remote()}/{lib.name}'
        name = name.replace('/', '{slash}')
        uri = str((entry.local / lib).absolute())
        ouptut += f'  (lib (name "{name}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n'
    return ouptut

def dump_libs(entries: List[LibEntry], where: Path):
    sym_lib_table = '(sym_lib_table\n'
    fp_lib_table = '(fp_lib_table\n'
    for entry in entries:
        sym_libs = entry.local.glob('**/*.kicad_sym')
        mod_libs = entry.local.glob('**/*.kicad_mod')
        sym_lib_table += generate_table_rows(entry, sym_libs)
        fp_lib_table += generate_table_rows(entry, mod_libs)

    sym_lib_table += ')\n'
    fp_lib_table += ')\n'

    with (where / 'sym-lib-table').open('w') as f:
        f.write(sym_lib_table)

    with (where / 'fp-lib-table').open('w') as f:
        f.write(fp_lib_table)

def add_lib(path: str, subproject_pattern: str, project_dir: Path):
    # check whether it's in the tracker already
    entries = load_lib_entries_from_tracker()

    # clone stuff and/or add it to the tracker
    if Path(path).exists():
        new_entry = LibEntry.from_local(path)
        new_entry.check_local()
    else:
        new_entry = LibEntry.from_remote(path)
        if not new_entry.check_local():
            new_entry.clone()
    # TODO: replace the 3d model path

    slim_remotes = {e.slim_remote(): e for e in entries}
    if new_entry.slim_remote() in slim_remotes:
        new_entry = slim_remotes[new_entry.slim_remote()]
    else:
        entries.append(new_entry)
        dump_lib_entries_to_tracker(entries)
    
    # add it to the project lib list
    config_path = project_dir / '.atopile.yaml'
    try: 
        with config_path.open() as f:
            config_data = yaml.safe_load(f)
    except FileNotFoundError:
        config_data = {}

    all_subproject_libs = config_data.get('libs') or {}
    if '*' not in subproject_pattern:
        subproject_pattern = ('**/*' + subproject_pattern + '*.kicad_pro')

    for subproject in project_dir.glob(subproject_pattern):
        if subproject.suffix != '.kicad_pro':
            log.error(f'{str(subproject)} isn\'t a valid sub-project')
            exit()

        libs = all_subproject_libs.get(subproject) or []
        if new_entry.slim_remote() not in libs:
            libs.append(new_entry.slim_remote())
        all_subproject_libs[str(subproject.relative_to(project_dir))] = libs

        # update the symbol and component linking files
        libs = [entry for entry in entries if entry.slim_remote() in libs]
        dump_libs(libs, subproject.parent)

    config_data['libs'] = all_subproject_libs

    with config_path.open('w') as f:
        yaml.safe_dump(config_data, f)
