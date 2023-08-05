"""
Test package name canonicalization.

The actual package name is 311devs_peewee, and the canonical name is 311devs-peewee,
however we're using 311devs-PeeWee as an alternate name to confirm we can properly
resolve package names like pip does.
"""
import pytest

from tests.conftest import Package
from tests.conftest import package_ids


@pytest.fixture(
    scope="module",
    params=[
        Package(
            name="311devs-peewee",
            altname="311devs-PeeWee",
            version="2.10.1.3",
            upgrade="2.10.2.1",
        ),
    ],
    ids=package_ids,
)
def package(request):
    return request.param


def test_package(project, package, package_type):
    project.run_common_tests(package, package_type)
