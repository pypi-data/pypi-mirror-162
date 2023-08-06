from json import load, dump
from os.path import exists
from typing import Union


def load_config_file(config_path: str = 'config.json') -> dict[str, Union[str, int]]:
    """Loads a dictionary of API connection arguments from a config file.

    Args:
        config_path (str, optional): The path to the config json. Defaults to
            'config.json'.

    Returns:
        dict[str, Union[str, int]]: A dictionary of API connection arguments.
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = load(f)
    return config


def update_config_file(
    config_path: str = 'config.json',
    reddit_client_id: str = '',
    reddit_client_secret: str = '',
    reddit_refresh_token: str = '',
    reddit_user_agent: str = '',
    reddit_redirect_domain: str = '',
    reddit_redirect_port: int = 8080,
    twitter_bearer_token: str = '',
) -> None:
    """_summary_

    Args:
        config_path (str, optional): The path to the config json. Defaults to
            'config.json'.
        reddit_client_id (str, optional): The Reddit client ID. Defaults to ''.
        reddit_client_secret (str, optional): The Reddit client secret.
            Defaults to ''.
        reddit_refresh_token (str, optional): The Reddit refresh token.
            Defaults to ''.
        reddit_user_agent (str, optional): A user agent string to use with the
            Reddit API. Defaults to ''.
        reddit_redirect_domain (str, optional): If using the external script
            to obtain a Reddit refresh token, this url is where you will log
            on to Reddit to authorize with your credentials. Defaults to ''.
        reddit_port (int, optional): If using the external script to obtain a
            Reddit refresh token, this will be the connection port using the
            redirect domain where you will log on to Reddit to authorize with
            your credentials. Defaults to 8080.
        twitter_bearer_token (str, optional): _description_. Defaults to ''.
    """
    json_kwargs = {
        'Reddit_client_id': reddit_client_id,
        'Reddit_client_secret': reddit_client_secret,
        'Reddit_refresh_token': reddit_refresh_token,
        'Reddit_user_agent': reddit_user_agent,
        'Reddit_redirect_domain': reddit_redirect_domain,
        'Reddit_redirect_port': reddit_redirect_port,
        'Twitter_bearer_token': twitter_bearer_token,
    }
    if exists(config_path):
        config = load_config_file(config_path)
        config.update(
            {
                key: value
                for key, value in json_kwargs.items()
                if value and value != 8080
            }
        )
    else:
        config = json_kwargs
    with open(config_path, 'w', encoding='utf-8') as f:
        dump(config, f, indent=4)
