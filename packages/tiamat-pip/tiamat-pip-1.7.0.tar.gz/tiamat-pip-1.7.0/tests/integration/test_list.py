def test_pip_list(project, package, package_type):
    """
    Test that we can list packages.
    """
    installed_packages = project.run("pip", "list")
    if package_type == "builtin":
        assert package.name not in installed_packages.stdout
    else:
        assert package.name in installed_packages.stdout


def test_pip_list_frozen(project, package, package_type):
    """
    Test that we can list the packages frozen into the binary.
    """
    frozen_packages = project.run("pip", "frozen")
    if package_type == "builtin":
        assert package.name in frozen_packages.stdout
    else:
        assert package.name not in frozen_packages.stdout
