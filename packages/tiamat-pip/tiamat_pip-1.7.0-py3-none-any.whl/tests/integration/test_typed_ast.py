"""
Test the pip install of typed-ast.

Using any available wheel and from source.
This test is particularly important since when building from source, it needs
to link against the "embedded" python interpreter on our package.
It ensures we're properly packaging the Python headers and presenting them
when building a package which requires them.
"""
import logging
import sys

import pytest

from tests.conftest import Package
from tests.conftest import package_ids

log = logging.getLogger(__name__)


@pytest.fixture(
    scope="module",
    params=[
        Package("typed-ast", version="1.5.3", upgrade="1.5.4"),
    ],
    ids=package_ids,
)
def package(request):
    return request.param


def extra_args_ids(value):
    if not value:
        return "allow-wheel-install"
    return "build-from-source"


@pytest.mark.parametrize(
    "extra_args",
    (
        [],
        ["--no-binary", "typed-ast"],
    ),
    ids=extra_args_ids,
)
def test_package(project, package, package_type, extra_args):
    if extra_args and sys.platform.startswith("win"):
        pytest.skip("For now, source builds are being skipped on windows")

    installed_packages = project.get_installed_packages(
        include_frozen=package_type == "builtin"
    )
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.version

    ret = project.run(
        "pip", "install", *extra_args, f"{package.name}=={package.upgrade}"
    )
    assert ret.exitcode == 0
    installed_packages = project.get_installed_packages()
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.upgrade

    ret = project.run("pip", "uninstall", "-y", package.name)
    assert ret.exitcode == 0
    assert "as it is not installed" not in ret.stderr

    installed_packages = project.get_installed_packages()
    assert package.name not in installed_packages

    if package_type == "builtin":
        # We can uninstall the upgrade, but not the builtin
        installed_packages = project.get_installed_packages(
            include_frozen=package_type == "builtin"
        )
        assert package.name in installed_packages

        ret = project.run("pip", "uninstall", "-y", package.name)
        assert ret.exitcode != 0
        assert "as it is not installed" in ret.stderr
