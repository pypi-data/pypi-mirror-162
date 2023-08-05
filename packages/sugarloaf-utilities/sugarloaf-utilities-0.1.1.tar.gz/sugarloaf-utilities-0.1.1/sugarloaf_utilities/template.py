from multiprocessing.sharedctypes import Value
from sugarloaf_utilities.components import get_ordered_packages
from click import command, option, Path as ClickPath, secho
from pathlib import Path
from pkg_resources import resource_filename
from typing import Optional, Union
from re import compile as re_compile
from shutil import copyfile, rmtree
from os import link, remove, symlink


def get_terraform_path(asset_name: Optional[str] = None) -> Path:
    submodule_path = Path("terraform")
    if asset_name:
        submodule_path /= asset_name
    return Path(resource_filename(__name__, str(submodule_path)))


class GenerateTemplate:
    def __init__(self):
        self.source_module_path = get_terraform_path()
        self.package_names = {package.name for package in get_ordered_packages()}

        # Files that often appear on disk but aren't intended for copy
        self.filename_blacklist = {".DS_Store", ".terraform"}

        # The compiled template will be built into this folder
        self.build_path = "build-infrastructure"

        # Keep the following files names during a overwrite of existing infrastructure
        # This allows clients to upgrade in a slightly smoother way without losing terraform state
        self.keep_files_in_migrate = [
            re_compile(r".*\.tfvars"),
            re_compile(r".*\.tfvars\.json"),
            re_compile(r".*\.tfstate"),
            re_compile(r".*\.tfstate\..*"),
            re_compile(r".*\.tflock"),
            re_compile(r".*\.tflock\..*"),
            re_compile(r".*\.terraform.lock"),
            re_compile(r".*\.terraform.lock\..*"),
        ]

    def __call__(self, output_path: Union[Path, str], override_path: Union[Path, str], confirm_delete: bool = True):
        output_path = Path(output_path)
        override_path = Path(override_path)

        if confirm_delete and not self.confirm_folder_ready(output_path):
            return

        output_infrastructure_path = output_path / self.build_path
        self.copy_base_modules(output_infrastructure_path)

        if override_path.exists():
            self.copy_user_overrides(output_infrastructure_path, override_path)

    def confirm_folder_ready(self, output_path: Union[Path, str]):
        """
        Determine whether we have already populated the output directory with
        our module files - if so, challenge and ask for user confirmation.

        """
        output_path = Path(output_path)

        if not (output_path / ".sugarloaf/config.json").exists():
            secho("Could not find the `.sugarloaf/config.json` file in this path.", fg="red")
            return False

        has_existing_data = any(
            (output_path / name).exists()
            for name in self.package_names
        )

        if not has_existing_data:
            return True

        secho("Existing infrastructure modules found.", fg="red")
        secho("Type the name of the output folder to continue...")
        confirmation = input("  > ")
        if confirmation != output_path.name:
            secho("Confirmation failed.", fg="red")
            return False
        return True

    def copy_base_modules(self, output_path: Path):
        """
        Copy the template files that are from the centralized infrastructure repo

        """

        for package_name in self.package_names:
            source_path = (self.source_module_path / package_name)
            if not source_path.exists():
                raise ValueError(f"Unable to find source package at path: `{source_path}`.\nYou might need to relink paths with `link-template`.")

            # Delete the destination path since we have received user confirmation
            # This cleans up any old files that may have been left over from a previous run, even
            # if we have removed their contents in a newer revision
            if (output_path / package_name).exists():
                self.remove_old_template_files(output_path / package_name)

            secho(f"Creating package: {package_name}", fg="green")

            for file_source_path in source_path.glob("**/*"):
                if not file_source_path.is_file() or self.file_in_blacklist(file_source_path):
                    continue
                file_output_path = output_path / file_source_path.relative_to(source_path.parent)
                # Create the parent directories if necessary first
                file_output_path.parent.mkdir(parents=True, exist_ok=True)
                copyfile(file_source_path, file_output_path)

    def copy_user_overrides(self, output_path: Path, override_path: Path):
        """
        Copy user-override files according to our conventions:
        - folders are supported as-is
        - the first root folder must be one of our predefined core packages

        """
        for path in override_path.glob("**/*"):
            if not path.is_file():
                continue
            if self.file_in_blacklist(path):
                secho(f"Skipping user-overide file, in blacklist: `{path}`", fg="yellow")
                continue

            destination_folder = str(path.relative_to(override_path)).split("/")[0]
            if destination_folder not in self.package_names:
                raise ValueError(f"Destination folder name is invalid: {path.name}")

            relative_path = path.relative_to(override_path)
            secho(f"Copying custom file: {relative_path}", fg="green")

            file_output = output_path / relative_path
            file_output.parent.mkdir(parents=True, exist_ok=True)
            link(path, file_output)

    def remove_old_template_files(self, root_path: Union[Path, str]):
        """
        Attempts to intelligently remove old template & override files since the values
        might have changed on disk and we don't want to end up with old files.

        """
        root_path = Path(root_path)

        # Clear out the files first according to our rules
        for delete_path in root_path.glob("**/*"):
            if not delete_path.is_file():
                continue
            should_remove = not any(
                keep_pattern.match(delete_path.name)
                for keep_pattern in self.keep_files_in_migrate
            )
            if should_remove:
                remove(delete_path)

        # Clear out any folders that are now empty
        for delete_path in self.walk_directories_dfs(root_path):
            if not delete_path.iterdir():
                remove(delete_path)

    def file_in_blacklist(self, path: Union[Path, str]) -> str:
        """
        Extends blacklist support to folders as well; ie. if any parts of the file path
        match the blacklist, we must

        """
        # also blacklist any parent folders
        return len(set(str(path).split("/")) & self.filename_blacklist) > 0

    def walk_directories_dfs(self, folder_path: Union[Path, str]):
        """
        Walk folder in dfs order, ie. returns most specific folders first. This method
        is useful to do a conditional deletion if folders have nested empty folders.

        """
        for path in Path(folder_path).iterdir(): 
            if path.is_dir(): 
                yield from self.walk_directories_dfs(path)
                continue
            yield path

@command()
@option("--output-path", type=ClickPath(exists=True, file_okay=False, dir_okay=True), required=True)
def main(output_path):
    """
    Template variables given the definition folder.

    We allow an "override" folder within the destination path. This allows clients to place custom
    terraform files into our centralized folders (ie. core-management/custom.tf, app-setup/custom.tfvars, etc)
    that are copied when the other files are re-generated. By convention, name your override
    files `{folder-name}/{file-name}.tf`. So for the previous examples you want `override/core-management/custom.tf`.
    We also support more complicated nesting structure like: `override/core-management/testing/custom.tf`.
    We create a hard link vs a symlink between these files because we want present as a full file to local
    utilities yet guarantee that if one file is edited the other is as well.

    """
    output_path = Path(output_path)

    template_generator = GenerateTemplate()
    template_generator(output_path, output_path / "override")


@command()
@option("--template-path", type=ClickPath(exists=True, file_okay=False, dir_okay=True), required=True)
@option("--hard", is_flag=True, default=False)
def link_templates(template_path: str, hard: bool):
    """
    Link the core template path (in the root of the git repostory) with symbolic links
    to the templates folder of the python package. This allows us to ship these files as
    part of the manifest to pypi.

    :param hard: Whether to hard-link the individual template files. This is necessary before
        deploying the package because sdist can only navigate paths that appear physically within
        the python package filetree. By default (when hard is not provided) it will soft-link the
        files, which is preferrable for local development. This soft linking allows the package to
        read underlying changes to the core modules while modifying locally.

    """
    source_path = Path(template_path).expanduser().resolve()

    desintation_path = get_terraform_path()
    if desintation_path.exists():
        rmtree(desintation_path)
    desintation_path.mkdir()

    for package in get_ordered_packages():
        source_package_path = source_path / package.name
        destination_package_path = desintation_path / package.name

        if not source_package_path.exists():
            raise ValueError(f"Source package does not exist: `{source_package_path}`")

        secho(f"Link paths: `{source_package_path}`->`{destination_package_path}`", fg="green")
        if hard:
            # Trace through each individual file and link these
            secho(" - Link: hard")
            for copy_file_path in source_package_path.glob("**/*"):
                if not copy_file_path.is_file():
                    continue
                relative_file_path = copy_file_path.relative_to(source_package_path)
                destination_file_path = destination_package_path / relative_file_path
                destination_file_path.parent.mkdir(parents=True, exist_ok=True)

                link(copy_file_path, destination_file_path)
        else:
            # Link the whole folder
            secho(" - Link: soft")
            symlink(source_package_path, destination_package_path)
