from multiprocessing.sharedctypes import Value
from click import option, secho, Path as ClickPath
from sugarloaf_utilities.components import get_ordered_packages
from subprocess import run
from os import getcwd
from pathlib import Path
from typing import Optional, List
from sugarloaf_utilities.template import GenerateTemplate


def find_parent_config_path(child_path: str) -> Path:
    # Traverse up the filepath until we find a .sugarloaf folder
    # that contains a configuration file
    child_path = Path(child_path)
    while child_path is not None:
        if (child_path / ".sugarloaf").exists():
            return child_path
        child_path = child_path.parent
    raise ValueError("No .sugarloaf configuration folder found in any parent directories.")


@option("--path", type=ClickPath(exists=True, file_okay=False, dir_okay=True), required=False)
@option("--subset", type=str, multiple=True, required=False)
@option("--debug", is_flag=True, default=False)
@option("-auto-approve", is_flag=True, default=False)
def chain_apply(path: Optional[str], subset: Optional[List[str]], auto_approve: bool, debug: bool):
    """
    Chained apply that "terraform apply" our packages in dependency order, by default requesting
    clients confirm each change that is applied. To override and have it accept changes by default, pass
    the -auto-approve flag. We will halt on any plan failure before attempting to run the next ones in the
    dependency graph.

    Will attempt to apply in the local directory. If all packages specified in the DAG definition
    are not found, will throw an error.

    :param debug: If this flag is provided, will refresh the template during every run. Useful for
    local debugging of the `sugarloaf-infrastructure` codebase.

    """
    current_path = Path(path) if path else Path(getcwd())
    packages = get_ordered_packages()

    if not (current_path / ".sugarloaf/config.json").exists():
        secho("Must be run in root project directory", fg="red")
        return

    # Generate new build configuration based on the latest core files
    if debug:
        #project_root = find_parent_config_path(current_path)
        secho("Debug: generating new templates...\n", fg="yellow")
        template_generator = GenerateTemplate()
        template_generator(current_path, current_path / "override", confirm_delete=False)
        secho("\n")

    apply_path = current_path / "build-infrastructure"

    if subset:
        packages = [package for package in packages if package.name in subset]

    missing_packages = []
    for package in packages:
        if not (apply_path / package.name).exists():
            missing_packages.append(package.name)
    if missing_packages:
        secho(f"Packages not found: {missing_packages}", fg="red")
        return

    for package in packages:
        secho(f"Applying package: `{package.name}`...", fg="yellow")
        response_init = run(["terraform", f"-chdir={(apply_path / package.name)}", "init"])
        if response_init.returncode != 0:
            secho(f"Init failed for module `{package.name}`, aborting...", fg="red")
            return
        response_apply = run(["terraform", f"-chdir={(apply_path / package.name)}", "apply", "-auto-approve" if auto_approve else ""])
        if response_apply.returncode != 0:
            secho(f"Plan failed for module `{package.name}`, aborting...", fg="red")
            return


@option("--path", type=ClickPath(exists=True, file_okay=False, dir_okay=True), required=False)
@option("--subset", type=str, multiple=True, required=False)
@option("-auto-approve", is_flag=True, default=False)
def chain_destroy(path: Optional[str], subset: Optional[List[str]], auto_approve: bool):
    """
    Chained destroy, will tear down resources in the opposite order that they are created. Accepts
    the same parameters as chain_apply.

    """
    apply_path = Path(path) if path else Path(getcwd())
    packages = get_ordered_packages()[::-1]

    if subset:
        packages = [package for package in packages if package.name in subset]

    missing_packages = []
    for package in packages:
        if not (apply_path / package.name).exists():
            missing_packages.append(package.name)
    if missing_packages:
        secho(f"Packages not found: {missing_packages}", fg="red")
        return

    for package in packages:
        secho(f"Destroying package: `{package.name}`...", fg="yellow")
        response_apply = run(["terraform", f"-chdir={(apply_path / package.name)}", "destroy", "-auto-approve" if auto_approve else ""])
        if response_apply.returncode != 0:
            secho(f"Plan failed for module `{package.name}`, aborting...", fg="red")
            return
