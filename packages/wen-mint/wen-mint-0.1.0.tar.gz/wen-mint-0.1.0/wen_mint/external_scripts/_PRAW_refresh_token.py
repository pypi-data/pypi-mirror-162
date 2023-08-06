#!/usr/bin/env python

import random
import socket
import sys

import praw

from ..utils._config_io import load_config_file

# Adapted from https://praw.readthedocs.io/en/stable/tutorials/refresh_token.html#refresh-token

f"""This example demonstrates the flow for retrieving a refresh token.

This tool can be used to conveniently create refresh tokens for later use with your web
application OAuth2 credentials.

To create a Reddit application visit the following link while logged into the account
you want to create a refresh token for: https://www.reddit.com/prefs/apps/


After the application is created, take note of:

- REDDIT_CLIENT_ID; the line just under "web app" in the upper left of the Reddit
  Application
- REDDIT_CLIENT_SECRET; the value to the right of "secret"

Generate a config file using them and then run this script to obtain the refresh token.
"""


def main():
    request_refresh_token('../config.json')

def request_refresh_token(config_path: str = '../config.json', manual_scopes: bool = False):

    config = load_config_file(config_path)
    redirect_domain = config['Reddit_redirect_domain']
    redirect_port = config['Reddit_redirect_port']
    redirect_url = f'http://{redirect_domain}:{redirect_port}'

    """Provide the program's entry point when directly executed."""
    if manual_scopes:
        scope_input = input(
            "Enter a comma separated list of scopes, or `*` for all scopes: "
        )
        scopes = [scope.strip() for scope in scope_input.strip().split(",")]
    else:
        scopes = ['history', 'read', 'wikiread', 'privatemessages']
    # If private messenges is not enabled, praw gives an error for redditors.partial_redditors
    reddit = praw.Reddit(
        redirect_uri=redirect_url,
        user_agent="obtain_refresh_token/v0 by u/bboe",
        client_id = config['Reddit_client_id'],
        client_secret = config['Reddit_client_secret']
        
    )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(scopes, state, "permanent")
    print(f"Now open this url in your browser: {url}")

    client = receive_connection(redirect_domain, redirect_port)
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
    }

    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message(client, params["error"])
        return 1

    refresh_token = reddit.auth.authorize(params["code"])
    send_message(client, f"Refresh token: {refresh_token}")
    return 0

def receive_connection(domain, port):
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    # Modification to reformat single redirect url to tuple format.
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((domain, port))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()


if __name__ == "__main__":
    sys.exit(main())
