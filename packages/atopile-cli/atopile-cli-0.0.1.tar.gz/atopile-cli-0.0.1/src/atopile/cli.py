import asyncio
import logging
from pathlib import Path

import click
import yaml

from .build import build
from .config import STAGE_DIR, STAGE_INCLUDES
from .utils import get_project_dir
from .lib import add_lib

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def ensure_dir(dir: Path):
    if not dir.exists():
        dir.mkdir(parents=True)
        log.info(f'creating {str(dir)}')

@click.group()
def cli():
    pass

@cli.command('build')
@click.argument('project-dir', required=False)
# @click.option('--target', required=False)
def build(project_dir):
    """Build your project."""
    if project_dir:
        project_dir = Path(project_dir)
    else:
        project_dir = get_project_dir()

    build(project_dir)
    
@cli.group('lib')
def lib():
    pass

@lib.command('add')
@click.argument('repo')
@click.option('--project-dir', default=None, help='project to add the dependency to, else project of CWD')
@click.option('--subproject', default='*', help='subproject to add the dependency to, else it\'s added to all. Glob matches .kicad_pro files')
def cli_add_lib(repo, project_dir, subproject):
    """Add a new library to the project's dependencies."""
    if project_dir:
        project_dir = Path(project_dir)
    else:
        project_dir = get_project_dir()

    add_lib(repo, subproject, project_dir)
    
@cli.group('stage-def')
def stage_def():
    pass

@stage_def.command('add')
@click.argument('path', required=False)
def cli_add_stage_def(path):
    """Add a search path to stages."""
    if path:
        path = Path(path)
        if not path.exists():
            log.error(f'{str(path)} doesn\'t exist!')
            return
        if not path.is_dir():
            path = path.parent
            log.warning(f'using {str(path)}; includes are the directories containing the stages.')
    else:
        path = Path('.')

    ensure_dir(STAGE_DIR)

    includes = []
    if STAGE_INCLUDES.exists():
        with STAGE_INCLUDES.open() as f:
            includes = yaml.safe_load(f)

    what_abs = str(path.absolute())
    if what_abs not in includes:
        includes += [what_abs]
    
        with STAGE_INCLUDES.open('w') as f:
            yaml.safe_dump(includes, f)

        log.info(f'added {str(what_abs)} do stage includes')
    else:
        log.info(f'{str(what_abs)} already in includes')

if __name__ == '__main__':
    cli()
