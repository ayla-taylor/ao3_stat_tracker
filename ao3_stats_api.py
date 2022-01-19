# This was primarily taken from https://github.com/ArmindoFlores/ao3_api.git and modified for my purposes
# My changes only occur in the get_statistics method of the Session class


import requests
from bs4 import BeautifulSoup

from AO3 import threadable, utils
from AO3.requester import requester
from AO3.users import User


class GuestSession:
    """
    AO3 guest session object
    """

    def __init__(self):
        self.is_authed = False
        self.authenticity_token = None
        self.username = ""
        self.session = requests.Session()

    @property
    def user(self):
        return User(self.username, self, False)

    @threadable.threadable
    def refresh_auth_token(self):
        """Refreshes the authenticity token.
        This function is threadable.

        Raises:
            utils.UnexpectedResponseError: Couldn't refresh the token
        """

        # For some reason, the auth token in the root path only works if you're 
        # unauthenticated. To get around that, we check if this is an authed
        # session and, if so, get the token from the profile page.

        if self.is_authed:
            req = self.session.get(f"https://archiveofourown.org/users/{self.username}")
        else:
            req = self.session.get("https://archiveofourown.org")

        if req.status_code == 429:
            raise utils.HTTPError("We are being rate-limited. Try again in a while or reduce the number of requests")

        soup = BeautifulSoup(req.content, "lxml")
        token = soup.find("input", {"name": "authenticity_token"})
        if token is None:
            raise utils.UnexpectedResponseError("Couldn't refresh token")
        self.authenticity_token = token.attrs["value"]

    def get(self, *args, **kwargs):
        """Request a web page and return a Response object"""

        if self.session is None:
            req = requester.request("get", *args, **kwargs)
        else:
            req = requester.request("get", *args, **kwargs, session=self.session)
        if req.status_code == 429:
            raise utils.HTTPError("We are being rate-limited. Try again in a while or reduce the number of requests")
        return req

    def request(self, url):
        """Request a web page and return a BeautifulSoup object.

        Args:
            url (str): Url to request

        Returns:
            bs4.BeautifulSoup: BeautifulSoup object representing the requested page's html
        """

        req = self.get(url)
        soup = BeautifulSoup(req.content, "lxml")
        return soup

    def post(self, *args, **kwargs):
        """Make a post request with the current session

        Returns:
            requests.Request
        """

        req = self.session.post(*args, **kwargs)
        if req.status_code == 429:
            raise utils.HTTPError("We are being rate-limited. Try again in a while or reduce the number of requests")
        return req

    def __del__(self):
        self.session.close()


class Session(GuestSession):
    """
    AO3 session object
    """

    def __init__(self, username, password):
        """Creates a new AO3 session object

        Args:
            username (str): AO3 username
            password (str): AO3 password

        Raises:
            utils.LoginError: Login was unsucessful (wrong username or password)
        """

        super().__init__()
        self.is_authed = True
        self.username = username
        self.url = "https://archiveofourown.org/users/%s" % self.username

        self.session = requests.Session()

        soup = self.request("https://archiveofourown.org/users/login")
        self.authenticity_token = soup.find("input", {"name": 'authenticity_token'})["value"]
        payload = {'user[login]': username,
                   'user[password]': password,
                   'authenticity_token': self.authenticity_token}
        post = self.post("https://archiveofourown.org/users/login", params=payload, allow_redirects=False)
        if not post.status_code == 302:
            raise utils.LoginError("Invalid username or password")

    def __getstate__(self):
        d = {}
        for attr in self.__dict__:
            if isinstance(self.__dict__[attr], BeautifulSoup):
                d[attr] = (self.__dict__[attr].encode(), True)
            else:
                d[attr] = (self.__dict__[attr], False)
        return d

    def __setstate__(self, d):
        for attr in d:
            value, issoup = d[attr]
            if issoup:
                self.__dict__[attr] = BeautifulSoup(value, "lxml")
            else:
                self.__dict__[attr] = value

    def extract_stats(self, data, d: dict) -> dict:
        """helper fuction to create the stats dictionaries"""
        for field in data:
            name = field.getText()[:-1].lower().replace(" ", "_")
            if field.next_sibling is not None and field.next_sibling.next_sibling is not None:
                value = field.next_sibling.next_sibling.getText().replace(",", "")
                if value.isdigit():
                    d[name] = int(value)
        return d

    def get_statistics(self, year=None):
        """Pulls statistics for the signed in user and all of their works"""
        # Modified to get all the stats for all the individual tasks for each work - AT, 1/18/2022
        year = "All+Years" if year is None else str(year)
        url = f"https://archiveofourown.org/users/{self.username}/stats?year={year}"
        soup = self.request(url)
        stats = {}
        dt = soup.find("dl", {"class": "statistics meta group"})
        titles = soup.find_all("dt")
        text = soup.find_all("dl", {"class": "stats"})
        work_stats = dict()
        index = 7
        title_names = []
        for x in titles:
            if x.getText()[0] == '\n':
                name, words = x.getText().split('\n')[1:-1]
                title_names.append((name, int(words.split()[0][1:])))
        if text is not None:
            for i, story in enumerate(text):
                current_stats = {}
                index += 6
                current_stats['words'] = title_names[i][1]
                current_stats = self.extract_stats(story.findAll("dt"), current_stats)
                work_stats[title_names[i][0]] = current_stats
        if dt is not None:
            stats = self.extract_stats(dt.findAll("dt"), stats)
        return stats, work_stats

    @staticmethod
    def str_format(string):
        """Formats a given string

        Args:
            string (str): String to format

        Returns:
            str: Formatted string
        """

        return string.replace(",", "")
