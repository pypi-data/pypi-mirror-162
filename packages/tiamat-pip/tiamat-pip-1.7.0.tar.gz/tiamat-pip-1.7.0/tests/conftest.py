import logging
import os
import pathlib
from typing import Optional

import attr
import pytest

import tiamatpip
from tests.support.helpers import TiamatPipProject

log = logging.getLogger(__name__)

CODE_ROOT = pathlib.Path(tiamatpip.__file__).resolve().parent.parent


@attr.s(frozen=True, slots=True)
class Package:
    name: str = attr.ib()
    version: str = attr.ib()
    upgrade: str = attr.ib()
    altname: Optional[str] = attr.ib(default=None)


def package_ids(value):
    return f"{value.name}=={value.version}"


@pytest.fixture(scope="module", params=["pypath", "builtin"])
def package_type(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        Package(name="pep8", version="1.7.0", upgrade="1.7.1"),
    ],
    ids=package_ids,
)
def package(request):
    return request.param


@pytest.fixture(scope="module")
def built_project(request, tmp_path_factory, package, package_type):
    name = f"tiamat-{package.name}-{package.version.replace('.', '_')}-{package_type}"
    requirements = []
    if package_type == "builtin":
        requirements.append(f"{package.name}=={package.version}")
    instance = TiamatPipProject(
        name=name,
        path=tmp_path_factory.mktemp(name, numbered=False),
        one_dir=request.config.getoption("--singlebin") is False,
        requirements=requirements,
    )
    with instance:
        if os.environ.get("CI_RUN", "0") == "0":
            instance.copy_generated_project_to_temp()
        yield instance


@pytest.fixture
def project(built_project, package, package_type):
    try:
        log.info("Using built Project: %s", built_project)
        if package_type == "pypath":
            installed_packages = built_project.get_installed_packages()
            assert package.name not in installed_packages
            ret = built_project.run(
                "pip", "install", f"{package.name}=={package.version}"
            )
            assert ret.exitcode == 0
        yield built_project
    finally:
        built_project.delete_pypath()


# ----- CLI Options Setup ------------------------------------------------------------------------>
def pytest_addoption(parser):
    """
    Register argparse-style options and ini-style config values.
    """
    test_selection_group = parser.getgroup("Tests Selection")
    test_selection_group.addoption(
        "--singlebin",
        default=False,
        help="Choose singlebin instead of onedir to run the tests agaist.",
    )


# <---- CLI Options Setup -------------------------------------------------------------------------
