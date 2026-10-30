try:
    import pkg_resources
except ImportError:
    import subprocess
    import sys

    def install_setuptools():
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])

    install_setuptools()
    import pkg_resources

    # Ensure pkg_resources is available
    try:
        import pkg_resources
    except ImportError:
        raise ImportError("pkg_resources could not be imported after installing setuptools")

    # Check if pkg_resources is still not available
    if 'pkg_resources' not in sys.modules:
        raise ImportError("pkg_resources is still not available after installing setuptools")

def list_installed_packages():
    installed_packages = pkg_resources.working_set
    installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
    for package in installed_packages_list:
        print(package)

if __name__ == "__main__":
    list_installed_packages()
