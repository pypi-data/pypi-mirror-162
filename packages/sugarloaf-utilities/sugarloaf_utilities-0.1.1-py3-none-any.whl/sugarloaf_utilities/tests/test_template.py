from tempfile import TemporaryDirectory
from pathlib import Path
from sugarloaf_utilities.template import GenerateTemplate
import pytest
from typing import Iterator
from json import dump

@pytest.fixture
def output_dir() -> Iterator[Path]:
    with TemporaryDirectory() as output_dir:
        output_dir = Path(output_dir)

        sugarloaf_config_dir = output_dir / ".sugarloaf"
        sugarloaf_config_dir.mkdir()
        with open(sugarloaf_config_dir / "config.json", "w") as file:
            dump(dict(name="test"), file)

        yield output_dir

@pytest.fixture
def override_dir(output_dir) -> Path:
    override_path = output_dir / "override"
    override_path.mkdir()
    return override_path

def test_simple_merge(output_dir, override_dir):
    """
    Ensure that we merge template files and overrides
    """
    app_setup_path = override_dir / "app-setup"
    app_setup_path.mkdir()

    with open(app_setup_path / "test.tf", "w") as file:
        file.write("TEST")

    template_generator = GenerateTemplate()
    template_generator(output_dir, override_dir)

    build_directory = output_dir / template_generator.build_path

    # Templates were transferred over
    assert (build_directory / "app-monitoring").exists()

    # User overrides were transferred over
    assert (build_directory / "app-setup/test.tf").exists()


def test_terraform_state_file_in_output(output_dir, override_dir):
    """
    Ensure that we don't delete terraform state files that live within the build path
    """
    template_generator = GenerateTemplate()
    monitoring_directory = output_dir / template_generator.build_path / "app-monitoring"
    monitoring_directory.mkdir(parents=True)

    with open(monitoring_directory / "terraform.tfstate", "w") as file:
        file.write("STATE")

    # Perform the generation
    template_generator(output_dir, override_dir, confirm_delete=False)

    with open(monitoring_directory / "terraform.tfstate") as file:
        file.read().strip() == "STATE"
