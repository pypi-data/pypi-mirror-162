import datetime as dt
import functools
import re
from typing import Callable, Union

import pandas as pd

from ._api_conn import create_reddit_api_conn, connect_to_tweepy_api_v2


def extract_and_output(func: Callable) -> object:
    """A decorator to modify the Ethereum address extraction methods of child
    classes of GeneralExtractor.

    Args:
        func (Callable): This affects the function where the decorator is
            applied.

    Returns:
        object: A pandas DataFrame with Ethereum addresses appended.
    """

    @functools.wraps(func)
    def wrapper(
        self,
        input_arg: Union[int, str],
        output_path: str = None,
        trim_random: int = None,
        *args,
        **kwargs,
    ) -> object:

        df = func(self, input_arg, output_path, trim_random, *args, **kwargs)
        df[self.address_column] = replace_text_with_addresses(
            df, self.post_column, whats_a_newline=self.low_precision
        )
        self.df = df[self.final_columns]
        if trim_random:
            self.df = self.sample_results(trim_random)
        if output_path is not None:
            self.df.to_csv(output_path)
        return self.df

    return wrapper


def replace_text_with_addresses(
    df: object, post_column: str, whats_a_newline: bool = False
) -> object:
    """Extracts Ethereum addresses from a post column.

    Args:
        df (object): A pandas dataframe.
        post_column (str): The name of the column that contains the text data
            to search for addresses.
        whats_a_newline (bool, optional): Use this in situations when you are
            stuck with an input where newline characters have been dropped
            without replacement. Defaults to True.

    Returns:
        object: A pandas series containing the extracted Ethereum addresses.
    """
    capture_group_label = 'capture_group'
    if whats_a_newline:
        address_regex = re.compile(
            r'\b(?P<' + capture_group_label + r'>\w+(?:[\-\.]\w+)*\.eth|0x[\da-f]{40})',
            flags=re.I,
        )
    else:
        address_regex = re.compile(
            r'(?<!\S)(?:"|\()?\b(?P<'
            + capture_group_label
            + r'>\w+(?:[\-\.]\w+)*\.eth|0x[\da-f]{40})\b',
            flags=re.I,
        )
    return df[post_column].str.extract(address_regex)[capture_group_label].str.lower()


class GeneralExtractor:
    """Base class for Ethereum address extractor classes."""

    def __init__(self) -> None:
        """Takes no arguments but passes default column names to child classes
        for convenience.
        """
        self.client = None
        self.response = None

        self.id_column = 'ID'
        self.post_column = 'Post Text'
        self.address_column = 'Address'
        self.user_column = 'Username'
        self.user_id_column = 'User ID'
        self.created_column = 'Created'

        self.final_columns = None

        self.df = None

    def __repr__(self) -> str:
        """Determines how the object is displayed in string format.

        Returns:
            str: A string with some basic info and the extracted addresses.
        """
        output = 'Ethereum Address Extractor: '
        if self.df is None:
            return output + 'Scraping uninilitialized.'
        else:
            return output + self._get_address_string()

    def __str__(self) -> str:
        """Determines how the object appears when printed.

        Returns:
            str: A string of space seperated extracted addresses.
        """
        return '' if self.df is None else self._get_address_string()

    def _trim_results(self) -> object:
        """Reduces the scraped dataframe to rows that contain addresses,
        with no duplicates across addresses and users.

        Returns:
            object: A Pandas DataFrame with incompletes and duplicates
            dropped.
        """
        if self.df is not None:
            return (
                self.df.dropna(subset=[self.address_column])
                .drop_duplicates(subset=[self.address_column])
                .drop_duplicates(subset=self.user_column)
            )

    def _get_address_list(self) -> list[str]:
        """Extracts list of addresses that have been trimmed from the scraped
        DataFrame.

        Returns:
            list[str]: A list of Ethereum addresses.
        """
        if self.df is not None:
            return self._trim_results()[self.address_column].to_numpy().tolist()

    def _get_address_string(self) -> str:
        """Extracts a space seperated string of Ethereum addresses that have
        been trimmed from the scraped dataframe.

        Returns:
            str: Ethereum addresses seperated by a single space.
        """
        if self.df is not None:
            return ' '.join(self._get_address_list())

    def sample_results(self, n: int) -> object:
        """Performs a random sample of the scraped data after it has been trimmed
        to exclude missing addresses and duplicates.

        Args:
            n (int): The size of the sample (if too big it will return the
            remaining length after trimming)

        Returns:
            object: A sample of n rows from the trimmed DataFrame
        """
        if self.df is None:
            return None
        elif n >= self.df.shape[0]:
            return self._trim_results()
        else:
            # To avoid the scenario of someone gaming giveaways by exploiting
            # the pseudorandomness, the random state is dependant on the time
            # that the function is run.
            random_state = int(dt.datetime.now().timestamp()) % 100000
            return self._trim_results().sample(n=n, random_state=random_state)


class RedditExtractor(GeneralExtractor):
    """Class that scrapes for Ethereum address comments on a Reddit post using
    PRAW and extracts them.
    """

    def __init__(self, config_path: str = 'config.json') -> None:
        """Initializes the Reddit scraper and extractor object.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
        """
        super().__init__()
        self.low_precision = False
        self.final_columns = [
            self.user_column,
            self.address_column,
            self.post_column,
            self.created_column,
        ]
        self._initialize_client(config_path)

    def _initialize_client(self, config_path: str = 'config.json') -> None:
        """Creates an attribute that contains the authenticated PRAW Reddit
        object for scraping.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
        """
        self.client = create_reddit_api_conn(config_path)

    @extract_and_output
    def scrape_addresses(
        self, post_id: str, output_path: str = None, trim_random: int = None
    ) -> object:
        """Scrapes for comments on a Reddit post using PRAW to a DataFrame,
        adding a column for the extracted Ethereum Addresses.

        Args:
            post_id (str): The post id to scrape for Reddit comments.
            output_path (str, optional): If provided, this will output a csv
                of the scrape with a column containing the extracted Ethereum
                address. Defaults to None.
            trim_random (int, optional): If selected, this will trim the
                output to a random selection of the amount specified across
                unique (and one address per user).

        Returns:
            object: A Pandas DataFrame of the scrape and the Ethereum
            addresses.
        """
        self.response = self.client.submission(post_id)
        self.response.comments.replace_more(limit=None)

        df = pd.DataFrame(
            [
                [comment.id, comment.author, comment.body, comment.created_utc]
                for comment in self.response.comments.list()
            ]
        )
        df.columns = [
            self.id_column,
            self.user_column,
            self.post_column,
            self.created_column,
        ]
        df = df.set_index(self.id_column, drop=True).sort_index()
        df[self.created_column] = pd.to_datetime(df[self.created_column], unit='s')

        return df


class TwitterExtractor(GeneralExtractor):
    def __init__(self, config_path: str = 'config.json') -> None:
        """Initializes the Twitter scraper and extractor object.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
        """
        super().__init__()
        self.low_precision = False
        self.final_columns = [
            self.user_id_column,
            self.user_column,
            self.address_column,
            self.post_column,
            self.created_column,
        ]
        self._initialize_client(config_path)
        self.kwargs = {
            'query': None,
            'tweet_fields': ['author_id', 'created_at'],
            'user_fields': ['username'],
            'expansions': ['author_id'],
            'max_results': 100,
        }

    def _initialize_client(self, config_path: str = 'config.json') -> None:
        """Creates an attribute that contains the authenticated Tweepy client
        object that will scrape using the V2 API.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
        """
        self.client = connect_to_tweepy_api_v2(config_path)

    def _extract_tweet_fields(self) -> list[tuple[int, str, int, object]]:
        """Extracts specific Tweet data from a Tweepy response object.

        Returns:
            list[tuple[int, str, int, object]]: A list containing the relevant
            Tweet data extracted from the Tweepy response object.
        """
        return [
            (tweet.id, tweet.text, tweet.author_id, tweet.created_at)
            for tweet in self.response.data
        ]

    def _extract_user_fields(self) -> list[tuple[int, str]]:
        """Extracts specific user data from the "includes" section of a
        Tweepy response object.

        Returns:
            list[tuple[int, str]]: A list containing user ids and usernames
                from the search.
        """
        return [(user.id, user.username) for user in self.response.includes['users']]

    def _update_query(self, query: str) -> None:
        """The Twitter V2 API search fields are a bit cumbersome, most of the
        parameters are stored in an attribute that contains them as keyword
        arguments. This function will update the dictionary to include
        information about the actual search query.

        Args:
            query (str): The Twitter API V2 seach query text.
        """
        self.kwargs.update({'query': query})

    def _get_paginated_replies(
        self,
    ) -> tuple[list[tuple[int, str, int, object]], list[tuple[int, str]]]:
        """Extracts Tweet replies looping through pagination until Twitter
        returns no further results from a query.

        Returns:
            tuple[list[tuple[int, str, int, object]], list[tuple[int, str]]]:
            Lists containing the combined data extracted from each section of
            the paginated search.
        """
        self.response = self.client.search_recent_tweets(**self.kwargs)
        next_token = self.response.meta.get('next_token', None)
        tweet_list = self._extract_tweet_fields()
        user_list = self._extract_user_fields()
        if not next_token:
            return tweet_list, user_list

        while next_token is not None:
            self.response = self.client.search_recent_tweets(
                next_token=next_token, **self.kwargs
            )
            tweet_list.extend(self._extract_tweet_fields())
            user_list.extend(self._extract_user_fields())
            next_token = self.response.meta.get('next_token', None)
        return tweet_list, user_list

    @extract_and_output
    def scrape_addresses(
        self,
        conversation_id: Union[str, int],
        output_path: str = None,
        trim_random: int = None,
    ) -> object:
        """Scrapes a Twitter thread from a conversation ID using API
        credentials provided in a config file. Twitter API use for free users
        will likely restrict to showing only results one week old or less.

        Args:
            conversation_id (Union[str, int]): The conversation ID for the
                Twitter thread
            output_path (str, optional): If an output is desired, specify the
                output path. Defaults to None.
            trim_random (int, optional): If selected, this will trim the
                output to a random selection of the amount specified across
                unique (and one address per user).

        Returns:
            object: A DataFrame of the the Tweet thread with the Ethereum
            addresses extracted in a seperate field.
        """

        self._update_query(f'conversation_id:{conversation_id}')

        tweets, users = self._get_paginated_replies()
        df = pd.DataFrame(tweets)
        df.columns = [
            self.id_column,
            self.post_column,
            self.user_id_column,
            self.created_column,
        ]
        users = pd.DataFrame(users)
        users.columns = [self.user_id_column, self.user_column]
        users = users.drop_duplicates(subset=[self.user_id_column]).set_index(
            self.user_id_column, drop=True
        )
        df = (
            df.join(users, how='left', on=self.user_id_column)
            .set_index(self.id_column, drop=True)
            .sort_index()
        )

        return df


class CSVExtractor(GeneralExtractor):
    """This class will extract addresses from an already exported CSV file
    with the ability to toggle the regex precision to work situations in which
    you are stuck using someone else's platform where they completely botch
    the post data by dropping newline characters without any replacement.
    """

    def __init__(
        self,
        post_column: str = None,
        user_column: str = None,
        low_precision: bool = True,
    ) -> None:
        """Creates a csv extractor obhect.

        Args:
            post_column (str, optional): Use this to overwrite the default post
                column from the parent class to fit the schema of the csv you
                are using. Defaults to None.
            user_column (str, optional): Use this to overwrite the default user
                column from the parent class to fit the schema of the csv you
                are using. Defaults to None.
            low_precision (bool, optional): Use this in situations when you
                are stuck with an input where newline characters have been
                dropped without replacement. Defaults to True.
        """
        super().__init__()
        self.low_precision = low_precision
        if post_column is not None:
            self.post_column = post_column
        if user_column is not None:
            self.user_column = user_column
        self.final_columns = [self.user_column, self.address_column, self.post_column]

    @extract_and_output
    def extract_from_csv(
        self, input_path: str, output_path: str = None, trim_random: int = None
    ) -> object:
        """Extracts Ethereum addresses from a csv file.

        Args:
            input_path (str): The path to the csv.
            output_path (str, optional): The path to export the new csv. If
                unset, it will only return a dataframe without saving to disk.
                Defaults to None.
            trim_random (int, optional): If selected, this will trim the
                output to a random selection of the amount specified across
                unique (and one address per user).

        Returns:
            object: A DataFrame that contains a column for the extracted
            address.
        """
        df = pd.read_csv(input_path)[[self.user_column, self.post_column]]
        return df
