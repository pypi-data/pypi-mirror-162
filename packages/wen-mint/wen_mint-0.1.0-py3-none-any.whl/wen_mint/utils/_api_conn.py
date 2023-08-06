from praw import Reddit
import tweepy

from ._config_io import load_config_file
from ..external_scripts._PRAW_refresh_token import request_refresh_token


def create_reddit_api_conn(config_path: str = 'config.json'):
    """Creates a PRAW reddit object with provided credentials from a local
    config json.

    Args:
        config_path (str, optional): The path to the config json. Defaults to
            'config.json'.

    Returns:
        object: A PRAW reddit object instantiated with credentials.
    """
    config = load_config_file(config_path)

    return Reddit(
        client_id=config['Reddit_client_id'],
        client_secret=config['Reddit_client_secret'],
        refresh_token=config['Reddit_refresh_token'],
        user_agent=config['Reddit_user_agent'],
    )


def connect_to_tweepy_api_v2(config_path: str = 'config.json') -> object:
    """Creates a Tweepy API V2 client object with provided credentials from a local
    config json.

    Args:
        config_path (str, optional): The path to the config json. Defaults to
            'config.json'.

    Returns:
        object: A Tweepy API V2 object instantiated with credentials.
    """
    config = load_config_file(config_path)
    return tweepy.Client(config['Twitter_bearer_token'])


def obtain_reddit_refresh_token(config_path: str = 'config.json', manual_scopes: bool = False):
    """Creates a redirect url that can be used to obtain a Reddit refresh token.

    Args:
        config_path (str, optional): The path to the config json. Defaults to
            'config.json'.
        manual_scopes (bool, optional): If you would like to be prompted to
            choose the connection scopes manually enable this arguement.
            Otherwise the scopes will be set as ['history', 'read',
            'wikiread', 'privatemessages'] which is slightly overpermissive
            but some scraping methods do not work with PRAW otherwise.
            Defaults to False.
    """
    request_refresh_token(config_path, manual_scopes)
