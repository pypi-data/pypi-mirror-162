def clone_repo(repo_url: str, path: str):
    """
    Clone a repository.

    @repo_url: The url of the repository to clone.
    @repo_name: The name of the repository.
    """

    import subprocess
    import os

    subprocess.run(["git", "clone", repo_url, path])

    if not os.path.exists(path):
        return False
    
    return True


