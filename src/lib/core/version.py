import subprocess

def is_latest_version():
    return get_local_version() == get_remote_version()

def get_local_version(format=True):
    local = subprocess.check_output(
            ["git", "describe", "--always"]
        )

    if format:
        local = str(local, "utf-8").strip()

    return local

def get_remote_version(format=True):
    remote = subprocess.check_output(
            ["git", "describe", "--always", "origin/master"]
        )

    if format:
        remote = str(remote, "utf-8").strip()

    return remote

