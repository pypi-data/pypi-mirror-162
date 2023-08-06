import argparse
from typing import Any

from .__version__ import __version__
from . import (
    update_config_file,
    obtain_reddit_refresh_token,
    CSVExtractor,
    RedditExtractor,
    TwitterExtractor,
)


def extract_from_csv(args: object):
    """Integrates the CLI with the csv extraction class.

    Args:
        args (object): Parsed arguments object from argparse.
    """
    kwargs = {}
    update_kwargs_from_loop(
        kwargs,
        {
            'post_column': args.post_column,
            'user_column': args.user_column,
            'low_precision': args.low_precision,
        },
    )
    scraper = CSVExtractor(**kwargs)

    kwargs = {'input_arg': args.input}
    update_kwargs_from_loop(
        kwargs, {'output_path': args.output, 'trim_random': args.random_sample}
    )
    scraper.extract_from_csv(**kwargs)
    if args.output is None:
        print(scraper)


def extract_from_scrape(args: object, api: str) -> None:
    """Integrates the CLI with the reddit and twitter scraping classes.

    Args:
        args (object): args (object): Parsed arguments object from argparse.
        api (str): Switches functionality to handle either the "reddit" class
            or the "twitter" class.

    Raises:
        ValueError: When "reddit" or "twitter" is not selected with the api
        argument.
    """
    kwargs = {}
    update_kwargs_from_loop(kwargs, {'config_path': args.config_path})

    if api == 'reddit':
        scraper = RedditExtractor(**kwargs)
        kwargs = {'input_arg': args.post_id}
    elif api == 'twitter':
        scraper = TwitterExtractor(**kwargs)
        kwargs = {'input_arg': args.conversation_id}
    else:
        raise ValueError('api string must specify "reddit" or "twitter"')

    update_kwargs_from_loop(
        kwargs, {'output_path': args.output, 'trim_random': args.random_sample}
    )
    scraper.scrape_addresses(**kwargs)
    if args.output is None:
        print(scraper)


def get_refresh_token(args: object):
    """Integrates the CLI with the obtain_reddit_refresh_token function.

    Args:
        args (object): Parsed arguments object from argparse.
    """
    kwargs = {'manual_scopes': args.manual_scopes}
    update_kwargs_from_loop(kwargs, {'config_path': args.config_path})
    obtain_reddit_refresh_token(**kwargs)


def config_generation(args: object):
    """Integrates the CLI with the update_config_file function.

    Args:
        args (object): Parsed arguments object from argparse.
    """
    kwargs = {}
    update_kwargs_from_loop(
        kwargs,
        {
            'config_path': args.output,
            'reddit_client_id': args.reddit_client_id,
            'reddit_client_secret': args.reddit_client_secret,
            'reddit_refresh_token': args.reddit_refresh_token,
            'reddit_user_agent': args.reddit_user_agent,
            'reddit_redirect_domain': args.reddit_redirect_domain,
            'twitter_bearer_token': args.twitter_bearer_token,
        },
    )
    if args.reddit_redirect_port is not None and args.reddit_redirect_port != 8080:
        kwargs.update({'reddit_redirect_port': args.reddit_redirect_port})
    update_config_file(**kwargs)


def update_kwargs_from_loop(kwargs: dict[str, Any], param_dict: dict[str, Any]):
    """Allows function defaults to stay intact when flags are unspecified by
    creating a dict of kwargs for only those that contain set values.

    Args:
        kwargs (dict[str, Any]): A dictionary of output keyword arguments to
            pass to the function that will be updated with set values.
        param_dict (dict[str, Any]): A dictionary of keys and values to
            extract when set obtained by argparse inputs.
    """

    for key, value in param_dict.items():
        if value is not None:
            kwargs.update({key: value})

def run_cmd_line():
    """Runs the argparse CLI functions."""
    parser = argparse.ArgumentParser(
        prog='Wen Mint',
        description='A command line interface for extracting Ethereum addresses from Reddit and Twitter',
    )
    parser.add_argument(
        '--version', version=f'%(prog)s {__version__}', action='version'
    )

    subparsers = parser.add_subparsers(help='Commands', dest='command')
    config = subparsers.add_parser(
        'generate_config',
        help='Generates a config file with API authentication credentials captured from flags',
    )
    refresh = subparsers.add_parser(
        'get_reddit_refresh_token',
        help='Facilitates obtaining a reddit refresh token using the reddit redirect url and port specified in the config file',
    )
    reddit = subparsers.add_parser(
        'reddit', help='Scrapes addresses from a comment thread on Reddit'
    )
    twitter = subparsers.add_parser(
        'twitter', help='Scrapes addresses from replies to a post on Twitter'
    )
    csv_extractor = subparsers.add_parser(
        'csv', help='Extracts addresses from a generated csv file.'
    )

    for subparser in [refresh, reddit, twitter]:
        subparser.add_argument(
            '--config_path',
            '-c',
            help='The path to the config json',
            metavar='FILEPATH',
            type=str,
        )

    for subparser in [reddit, twitter, csv_extractor]:
        subparser.add_argument(
            '--output',
            '-o',
            help='The path to the output csv. If empty, unique addresses will only be printed',
            metavar='FILEPATH',
            type=str,
        )
        subparser.add_argument(
            '--random_sample',
            '-r',
            help='Use this to optionally random sample a specific amount from unique addresses after a filter on one post (with address) per user is applied. If unspecified, results are untrimmed.',
            metavar='AMOUNT',
            type=int,
        )

    config.add_argument(
        '--output',
        '-o',
        help='The path to the output json. If it already exists it will be loaded first and overwritten using only specified flags.',
        metavar='FILEPATH',
        type=str,
    )
    config.add_argument(
        '--reddit_client_id',
        help='The client ID for the Reddit API',
        metavar='ID',
        type=str,
    )
    config.add_argument(
        '--reddit_client_secret',
        help='The client secret for the Reddit API',
        metavar='SECRET',
        type=str,
    )
    config.add_argument(
        '--reddit_refresh_token',
        help='The refresh token for the Reddit API',
        metavar='TOKEN',
        type=str,
    )
    config.add_argument(
        '--reddit_user_agent',
        help='The user agent for the Reddit API',
        metavar='AGENT',
        type=str,
    )
    config.add_argument(
        '--reddit_redirect_domain',
        help='When a new refresh token is required, use this to match the url you provided in your app settings',
        metavar='URL',
        type=str,
    )
    config.add_argument(
        '--reddit_redirect_port',
        help='The port with the redirect domain',
        metavar='PORT',
        type=int,
    )
    config.add_argument(
        '--twitter_bearer_token',
        help='The bearer token for the Twitter API',
        metavar='TOKEN',
        type=str,
    )

    refresh.add_argument(
        '--manual_scopes',
        help='Enable this flag to be prompted for the desired scopes for the token',
        action='store_true',
    )

    reddit.add_argument(
        'post_id',
        help='The ID of the Reddit post (without prefix)',
        metavar='ID',
        type=str,
    )

    twitter.add_argument(
        'conversation_id',
        help='The conversation ID of the Twitter thread',
        metavar='ID',
        type=int,
    )

    csv_extractor.add_argument(
        'input', help='The path to the input CSV', metavar='FILEPATH', type=str
    )
    csv_extractor.add_argument(
        '--low_precision',
        help='Use this to be extra aggressive about catching addresses. Not reccomended unless the input csv has done something wrong like stripping out newline characters',
        action='store_true',
    )
    csv_extractor.add_argument(
        '--post_column',
        help='Use this to set the default name for the post column to match the input csv',
        metavar='COLUMN',
        type=str,
    )
    csv_extractor.add_argument(
        '--user_column',
        help='Use this to set the default name for the user column to match the input csv',
        metavar='COLUMN',
        type=str,
    )

    args = parser.parse_args()

    if args.command == 'generate_config':
        config_generation(args)
    elif args.command == 'get_reddit_refresh_token':
        get_refresh_token(args)
    elif args.command == 'reddit':
        extract_from_scrape(args, api='reddit')
    elif args.command == 'twitter':
        extract_from_scrape(args, api='twitter')
    elif args.command == 'csv':
        extract_from_csv(args)

def main():
    run_cmd_line()


if __name__ == '__main__':
    main()
