"""
Test the pip install of libvirt-python which needs to link to a system installed library.
"""
import logging
import shutil
import subprocess

import pytest

from tests.conftest import Package
from tests.conftest import package_ids

log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def check_system_requirements():
    if shutil.which("gcc") is None:
        pytest.skip("Could not find the `gcc` binary")
    pkg_config_path = shutil.which("pkg-config")
    if pkg_config_path is None:
        pytest.skip("Could not find the `pkg-config` binary")
    assert pkg_config_path
    ret = subprocess.run([pkg_config_path, "libvirt"], shell=False, check=False)
    if ret.returncode != 0:
        pytest.skip("The `libvirt` system package is not installed")


@pytest.fixture(
    scope="module",
    params=[
        Package("libvirt-python", version="8.5.0", upgrade="8.6.0"),
    ],
    ids=package_ids,
)
def package(request, check_system_requirements):
    return request.param


def test_package(project, package, package_type):
    project.run_common_tests(package, package_type)
