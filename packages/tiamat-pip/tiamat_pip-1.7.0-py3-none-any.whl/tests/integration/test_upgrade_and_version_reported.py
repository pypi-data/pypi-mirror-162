import logging
import sys

import attr
import pytest

log = logging.getLogger(__name__)


@attr.s(frozen=True, slots=True)
class Package:
    name: str = attr.ib()
    version: str = attr.ib()
    upgrade: str = attr.ib()

    @version.default
    def _default_version(self):
        if self.name == "jinja2":
            if sys.version_info < (3, 7):
                return "2.11.3"
            return "3.0.0"
        if self.name == "napalm":
            if sys.version_info < (3, 7):
                return "3.4.0"
            return "3.4.1"

    @upgrade.default
    def _default_upgrade(self):
        if self.name == "jinja2":
            if sys.version_info < (3, 7):
                return "3.0.0"
            return "3.1.0"
        if self.name == "napalm":
            if sys.version_info < (3, 7):
                return "3.4.1"
            return "4.0.0"


def package_ids(value):
    return f"{value.name}=={value.version}"


@pytest.fixture(
    scope="module",
    params=[
        Package(name="jinja2"),
        # Package(name="napalm"),
    ],
    ids=package_ids,
)
def package(request):
    return request.param


def test_dunder_version(project, package, package_type):
    code = f"""
    import sys
    import {package.name}
    sys.stdout.write({package.name}.__version__)
    sys.stdout.flush()
    """
    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == package.version
    installed_packages = project.get_installed_packages(
        include_frozen=package_type == "builtin"
    )
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.version

    ret = project.run("pip", "install", f"{package.name}=={package.upgrade}")
    assert ret.exitcode == 0
    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == package.upgrade
    installed_packages = project.get_installed_packages()
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.upgrade


def test_pkg_resources(project, package, package_type):
    code = f"""
    import sys
    import pkg_resources
    print("pkg_resources.__file__:", pkg_resources.__file__, file=sys.stderr, flush=True)
    print("pkg_resources.working_set.entries:", pkg_resources.working_set.entries, file=sys.stderr, flush=True)
    print("pkg_resources.working_set.by_key:", pkg_resources.working_set.by_key, file=sys.stderr, flush=True)
    distribution = pkg_resources.get_distribution("{package.name}")
    print("distribution:", repr(distribution), file=sys.stderr, flush=True)
    sys.stdout.write(distribution.version)
    sys.stdout.flush()
    """
    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == package.version
    installed_packages = project.get_installed_packages(
        include_frozen=package_type == "builtin"
    )
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.version

    ret = project.run("pip", "install", f"{package.name}=={package.upgrade}")
    assert ret.exitcode == 0
    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == package.upgrade
    installed_packages = project.get_installed_packages()
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.upgrade


def test_importlib_metadata_backport(project, package, package_type):
    code = f"""
    import sys
    import importlib_metadata
    sys.stdout.write(importlib_metadata.version("{package.name}"))
    sys.stdout.flush()
    """
    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == package.version
    installed_packages = project.get_installed_packages(
        include_frozen=package_type == "builtin"
    )
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.version

    ret = project.run("pip", "install", f"{package.name}=={package.upgrade}")
    assert ret.exitcode == 0
    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == package.upgrade
    installed_packages = project.get_installed_packages()
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.upgrade


def test_importlib_metadata_stdlib(project, package, package_type):
    if sys.version_info < (3, 8):
        pytest.skip("'importlib.metadata' only exists on Py3.8+")

    code = f"""
    import sys
    import importlib.metadata
    sys.stdout.write(importlib.metadata.version("{package.name}"))
    sys.stdout.flush()
    """
    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == package.version
    installed_packages = project.get_installed_packages(
        include_frozen=package_type == "builtin"
    )
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.version

    ret = project.run("pip", "install", f"{package.name}=={package.upgrade}")
    assert ret.exitcode == 0
    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == package.upgrade
    installed_packages = project.get_installed_packages()
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.upgrade
