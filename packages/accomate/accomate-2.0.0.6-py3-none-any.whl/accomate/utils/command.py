import subprocess


def is_installed(package: str, test_command: str = "-v") -> bool:
    """
    Checks if a package is installed.
    """

    try:
        response = subprocess.check_output(f"{package} {test_command}", shell=True)
        return True
    except Exception as e:
        return False
