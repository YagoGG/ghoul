import platform
import requests
from six.moves import urllib

from utils import prompt_user_password


class GitHubClient():
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None

    def call_endpoint(self, endpoint, method='GET',
                      depaginate=False, **kwargs):
        """Make a query to GitHub's API.

        Args:
            endpoint (str): Path of the endpoint to call.
            method (str): HTTP verb for the query. Defaults to 'GET'.
            depaginate(bool): Whether to read all the potential pages or not.
                If set to True, all the pages will be merged into the output.
                Defaults to False.
            **kwargs: Arbitrary arguments accepted by requests.

        Returns:
            Dict(str, Any): Parsed JSON response from GitHub's API.

        Raises:
            requests.exceptions.HTTPError: After a non-OK status code is
                returned.
        """
        url = urllib.parse.urljoin(self.base_url, endpoint)
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.token:
            headers.update({'Authorization': 'token ' + self.token})

        r = requests.request(method, url, headers=headers, **kwargs)

        r.raise_for_status()

        if depaginate:
            res = r.json()

            try:
                while r.links['next']['url']:
                    url = r.links['next']['url']
                    r = requests.request(method, url,
                                         headers=headers, **kwargs)

                    r.raise_for_status()

                    res.extend(r.json())  # Add this page to the main result
            except KeyError:
                pass
            finally:
                return res

        if r.text == '':
            return None

        return r.json()

    def create_token(self, user, password, scopes):
        """Ask GitHub's OAuth Authorizations API for a new token.

        Args:
            user (str): GitHub handle of the token's owner.
            password (str): Password for the GitHub account of the token's
                owner.
            scopes (List(str)): List of scopes authorized for the token.
        """

        data = {
            'scopes': scopes,
            'note': 'Ghoul (%s)' % platform.node(),
            'note_url': 'https://github.com/YagoGG/ghoul'
        }

        res = self.call_endpoint('/authorizations', 'POST', json=data,
                                 auth=(user, password))

        self.set_token(user, res['id'], res['token'])

    def authorize(self, scopes=['repo']):
        """Generate and validate an OAuth authentication token.

        Args:
            scopes (List(str)): List of scopes authorized for the token.
                Defaults to ['repo'].

        Returns:
            Tuple(str, int, str): A tuple with the username, the  token's ID
                and the token itself.
        """
        while not self.token:
            self.user, password = prompt_user_password()

            try:
                self.create_token(self.user, password, scopes)
            except requests.exceptions.HTTPError as ex:
                if (ex.response.status_code == 401 and
                        ex.response.json()['message'] == 'Bad credentials'):
                    print('Wrong credentials. Please try again.')
                elif (ex.response.status_code == 422 and
                      ex.response.json()['errors'][0]['code'] ==
                      'already_exists'):
                    # A token for this machine already exists, so that one has
                    # to be deleted before creating a new one (it's not
                    # possible to get it back after its creation)
                    res = self.call_endpoint('/authorizations', 'GET',
                                             auth=(self.user, password),
                                             depaginate=True)

                    # Look for the old token
                    for item in res:
                        if (item['app']['name'] ==
                                'Ghoul (%s)' % platform.node()):
                            # Delete the old token
                            self.call_endpoint('/authorizations/' +
                                               str(item['id']), 'DELETE',
                                               auth=(self.user, password))
                            # Create a new token
                            self.create_token(self.user, password, scopes)
                else:
                    print('GitHub API HTTP error!')
                    print(ex.response.text)
                    raise

        return self.get_token()

    def get_token(self):
        return (self.user, self.token_id, self.token)

    def set_token(self, user, token_id, token):
        # TODO: Check that the token works properly
        self.user = user
        self.token_id = token_id
        self.token = token

    def get_issue(self, repo_owner, repo, issue):
        res = self.call_endpoint('/repos/%s/%s/issues/%s' %
                                 (repo_owner, repo, issue), 'GET')
        return res

    def get_pr(self, repo_owner, repo, pr):
        res = self.call_endpoint('/repos/%s/%s/pulls/%s' %
                                 (repo_owner, repo, pr), 'GET')
        return res

    def get_comments(self, repo_owner, repo, issue, amount=1):
        # TODO: This shouldn't depaginate all the comments for that issue,
        # since the desired amount may be gathered before reading the last page
        res = self.call_endpoint('/repos/%s/%s/issues/%s/comments' %
                                 (repo_owner, repo, issue), 'GET',
                                 depaginate=amount > 30)
        return res[-amount:]

    def post_comment(self, repo_owner, repo, issue, comment):
        data = {'body': comment}

        res = self.call_endpoint('/repos/%s/%s/issues/%s/comments' %
                                 (repo_owner, repo, issue), 'POST', json=data)
        return res
