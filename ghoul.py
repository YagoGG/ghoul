#!/usr/bin/env python
import argparse
import os
import sys
import subprocess
import tempfile
from textwrap import TextWrapper

import git
import requests

import repo_lib
from github import GitHubClient
from utils import get_stored_credentials, set_stored_credentials

"""
Todo:
    * All output messages should be wrapped.
    * Config files with different scopes (system/global/local)
"""

CREDENTIALS_FILE = os.path.expanduser('~/.ghoulconfig')


def get_text_editor_input(initial_msg):
    """Read user's text input through the system's default text editor.

    If the EDITOR environment variable isn't set, vi will be used instead.
    Anything written before the CROP_MARK won't be returned in the function's
    output.

    Args:
        initial_msg (str): String to place at the beginning of the file, that
            will appear when the editor is opened before the CROP_MARK.

    Returns:
        str: The content the user wrote in the text editor.

    Todo:
        * Preferrably use the text editor set in a config file.
    """
    EDITOR = os.environ.get('EDITOR', 'vi')
    CROP_MARK = ('\n\nAnything above this line will be ignored:\n' +
                 ('-' * 34) + '>8' + ('-' * 34) + '\n')

    wrapper = TextWrapper(replace_whitespace=False, drop_whitespace=False)
    initial_msg = '\n'.join(wrapper.wrap(initial_msg))
    initial_msg += CROP_MARK

    with tempfile.NamedTemporaryFile(suffix='.md') as temp:
        temp.write(initial_msg.encode('utf-8'))
        temp.flush()  # Write buffer to the file
        subprocess.call([EDITOR, temp.name])

        # The pointer was already after the initial message, but we return to
        # the beginning just in case the user added content before the mark
        temp.seek(0)
        return temp.read().decode('utf-8').split(CROP_MARK, 1)[1].strip()


# Initialize the GitHub client
gh = GitHubClient('https://api.github.com')

user, token_id, token = get_stored_credentials(CREDENTIALS_FILE)

if None in (token_id, token):  # There wasn't any token stored. Create one
    user, token_id, token = gh.authorize()
    set_stored_credentials(user, token_id, token, CREDENTIALS_FILE)
else:
    # TODO: Make sure that the token is valid
    gh.set_token(user, token_id, token)


def comment(args):
    """Post a comment in a pull request/issue.

    ghoul comment [options] <issue>

        -m MESSAGE, --message MESSAGE
            The comment's body. If not set, the system's default text editor
            will open to ask for it.

        <issue>
            The GitHub pull request/issue number where place the comment.

    Todo:
        * Support file uploads.
        * Add "edit" option.
        * Add "template" option (like git commit's -t/--template).
        * Handle invalid issue numbers.
        * Indent last_comment so it looks like a quote.
    """
    message = args.message
    if message is None:
        title = gh.get_issue(owner, repo, args.issue)['title']
        last_comment = '<No previous comments>'
        try:
            last_comment = gh.get_comments(owner, repo, args.issue)[0]['body']
        except IndexError:
            pass

        message = get_text_editor_input('Please enter the message for your '
                                        'comment. Remember that comments '
                                        'support GitHub Flavored Markdown '
                                        '(GFM). An empty message aborts the '
                                        'operation.\n\n'
                                        '#%s %s\n' % (args.issue, title) +
                                        'Last comment:\n' + last_comment)
    if message == '':
        print('Aborting comment due to empty message.')
        sys.exit(1)

    gh.post_comment(owner, repo, args.issue, message)
    sys.exit(0)


def review(args):
    """Clones the branch in an existing pull request.

    ghoul review [options] <pull_request>

    Todo:
        * Add a "cleanup" option, to remove the created branch and remote.
        * Support cloning through SSH (see head.repo.ssh_url).
    """
    try:
        pr = gh.get_pr(owner, repo, args.pull_request)
    except requests.exceptions.HTTPError:
        print('Couldn\'t find pull request #%s in %s/%s.' %
              (args.pull_request, owner, repo))
        print('Make sure the number is correct and that you have read '
              'permissions for this GitHub repository.')
        sys.exit(1)

    clone_url = pr['head']['repo']['clone_url']
    fork_branch = pr['head']['ref']
    fork_owner = pr['head']['repo']['owner']['login']

    repo_lib.fetch_fork(clone_url, fork_branch, fork_owner)
    repo_lib.checkout(fork_branch, fork_owner)
    sys.exit(0)


argparser = argparse.ArgumentParser()
argparser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
argparser.add_argument('-r', '--remote')

subparsers = argparser.add_subparsers(help='sub-command help')
comment_parser = subparsers.add_parser('comment')
comment_parser.add_argument('issue', type=int)
comment_parser.add_argument('-m', '--message')
comment_parser.set_defaults(func=comment)

review_parser = subparsers.add_parser('review')
review_parser.add_argument('pull_request', type=int)
review_parser.set_defaults(func=review)

args = argparser.parse_args()

owner = repo = None
working_remote = args.remote

# If no remote was specified in the arguments, this fallback order is followed.
# When one of these doesn't exist, the next one is checked:
#   1) upstraem
#   2) origin
#   3) current branch's tracking branch remote
if args.remote is None:
    current_remote = repo_lib.get_current_remote()
    remotes = ['upstream', 'origin', current_remote.remote_name]
    for remote in remotes:
        try:
            owner, repo = repo_lib.get_remote_info(remote)
            working_remote = remote
            break
        except git.exc.GitCommandError as ex:
            # Ignore the exception if it was for a non-existing remote
            if 'No such remote' not in ex.stderr:
                raise
else:
    owner, repo = repo_lib.get_remote_info(args.remote)

args.func(args)
