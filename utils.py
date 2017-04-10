import getpass
import os
from six.moves import input


def get_stored_credentials(credentials_file):
    """Read the OAuth token information in credentials_file.

    The credentials file should have the following format:

        [<username>]
        <token_id>
        <token>

    Returns:
        Tuple(str, int, str): A tuple with the user's GitHub handle, the token
            ID and the token itelf. The three values will be None if the
            credentials file doesn't exist.
    """
    if os.path.isfile(credentials_file):
        with open(credentials_file, 'r') as fd:
            user = fd.readline().strip(' \n\t[]')
            token_id = fd.readline().strip()
            token = fd.readline().strip()

            return (user, token_id, token)
    else:
        return (None, None, None)


def set_stored_credentials(user, token_id, token, credentials_file):
    """Write the OAuth token information in credentials_file.

    See get_stored_credentials() for details on the credentials file's format.

    Args:
        user (str): The user's GitHub handle.
        token_id (int): The token's ID.
        token (str): The OAuth personal authentication token.
    """
    with open(credentials_file, 'w+') as fd:
        fd.write('[%s]\n' % user)
        fd.write(str(token_id) + '\n')
        fd.write(token)


def prompt_user_password(user=None, password=None):
        while not user:
            user = input('GitHub username: ')

        while not password:
            password = getpass.getpass('Password for \'%s\': ' % user)

        return (user, password)
