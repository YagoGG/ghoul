import sys

import git
import giturlparse

try:
    repo = git.Repo()
except Exception:
    print('Couldn\'t find a valid Git repository!')
    sys.exit()


def get_remote_info(remote_name, host='github.com'):
    """Identify the owner and the repository of a remote.

    The output returned is the one corresponding to the first URL in the remote
    whose host matches the one specified in the arguments.

    Args:
        remote_name (str): Name of the remote to analyze.

    Returns:
        Tuple(str, str): A tuple with the names of both the owner and the repo.

    Todo:
        * Add an option for reading the n-th host-compatible URL.
        * Add an option for interactively asking the user which is the desired
            host URL, if more than one.
    """
    remote = git.remote.Remote(repo, remote_name)

    for url in remote.urls:
        parsed_url = giturlparse.parse(url)
        if parsed_url.host == host:
            return (parsed_url.owner, parsed_url.repo)
        return(None, None)


def get_current_remote():
    """Get the remote of the this branch's tracking branch.

    Returns:
        git.remote.Remote: GitPython remote object.
    """
    tracking = repo.active_branch.tracking_branch()
    if tracking is None:
        print('The current Git branch has no tracking remote.')
        sys.exit()
    return tracking


def fetch_fork(url, branches=None, remote_name='fork'):
    """Add a fork's remote, fetch it and load it locally using a rebase.

    Args:
        url (str): Git clone URL for the fork's remote repository.
        branches (List(str)): List of branches to fetch. Can be a string as
            well if it's just a single branch. If set to None, all of them will
            be gathered. Defaults to None.
        remote_name (str): The desired name for the remote created for the
            fork. Defaults to 'fork'.

    Returns:
        git.util.IterableList(FetchInfo, ...): A list of FetchInfo instances
            providing detailed information about the fetch results.
    """
    try:
        remote = repo.create_remote(remote_name, url)
    except git.exc.GitCommandError as ex:
        if 'already exists' not in ex.stderr:
            raise
        remote = repo.remote(remote_name)
    return remote.pull(branches, rebase=True)


def checkout(branch, remote=None):
    """Switch to a different branch.

    Args:
        branch (str): Branch to checkout.
        remote (str): Remote where the branch belongs to. Defaults to None.
    """
    if remote is not None:
        branch = '%s/%s' % (remote, branch)
    repo.git.checkout(branch)
