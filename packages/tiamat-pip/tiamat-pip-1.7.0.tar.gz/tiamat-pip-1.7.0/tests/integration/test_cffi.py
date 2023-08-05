import pytest

from tests.conftest import Package
from tests.conftest import package_ids


@pytest.fixture(
    scope="module",
    params=[
        Package(name="cffi", version="1.14.4", upgrade="1.15.1"),
    ],
    ids=package_ids,
)
def package(request):
    return request.param


def test_package(project, package, package_type):
    code = """
    import sys
    import time
    print("sys.path", sys.path)
    time.sleep(1)
    import json
    import cffi
    import _cffi_backend
    from cffi import FFI
    print(
        json.dumps(
            {
                "cffi": cffi.__file__,
                "_cffi_backend": _cffi_backend.__file__,
                "sys.path": sys.path,
            }
        ),
        file=sys.stderr,
        flush=True
    )
    try:
        FFI()
    except:
        raise
    """

    ret = project.run_code(code)
    assert ret.exitcode == 0

    installed_packages = project.get_installed_packages(
        include_frozen=package_type == "builtin"
    )
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.version

    ret = project.run("pip", "install", f"{package.name}=={package.upgrade}")
    assert ret.exitcode == 0
    installed_packages = project.get_installed_packages()
    assert package.name in installed_packages
    assert installed_packages[package.name] == package.upgrade

    ret = project.run_code(code)
    assert ret.exitcode == 0

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

        ret = project.run_code(code)
        assert ret.exitcode == 0
