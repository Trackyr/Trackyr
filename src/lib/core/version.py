import subprocess

def is_latest_version():
    return get_local_version() != get_remote_version()

def get_local_version(format=True):
    local = subprocess.check_output(
            ["git", "rev-parse", "HEAD"]
        )

    if format:
        local = str(local, "utf-8").strip()

    return local

def get_remote_version(format=True):
    remote = subprocess.check_output(
            ["git", "ls-remote", "https://github.com/Trackyr/Trackyr.git", "HEAD"]
        )

    if format:
        remote = str(remote, "utf-8").strip()
        remote = remote[:-5]

    return remote

if __name__ == "__main__":
    local = get_local_version()
    remote = get_remote_version()
    print(f"{local}={remote}={local==remote}")
