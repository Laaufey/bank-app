import requests
import environ
env = environ.Env()
environ.Env.read_env()
stocks_auth_token_1 = env("STOCKS_AUTH_TOKEN_1")
stocks_auth_token_2 = env("STOCKS_AUTH_TOKEN_2")
stocks_auth_token_3 = env("STOCKS_AUTH_TOKEN_3")


headers = {
    'Content-Type': 'application/json',
    # 'Authorization': stocks_auth_token_1
    # 'Authorization': stocks_auth_token_2
    'Authorization': stocks_auth_token_3
}


def get_meta_data(ticker):
    url = 'https://api.tiingo.com/tiingo/daily/{}'.format(ticker)
    response = requests.get(url, headers=headers)
    return response.json


def get_price_data(ticker):
    url = 'https://api.tiingo.com/tiingo/daily/{}/prices'.format(ticker)
    response = requests.get(url, headers=headers)
    return response.json()[0]


def get_apple_price():
    url = 'https://api.tiingo.com/tiingo/daily/aapl/prices'
    response = requests.get(url, headers=headers)
    return response.json()[0]


def get_google_price():
    url = 'https://api.tiingo.com/tiingo/daily/googl/prices'
    response = requests.get(url, headers=headers)
    return response.json()[0]


def get_microsoft_price():
    url = 'https://api.tiingo.com/tiingo/daily/msft/prices'
    response = requests.get(url, headers=headers)
    return response.json()[0]


def get_amazon_price():
    url = 'https://api.tiingo.com/tiingo/daily/amzn/prices'
    response = requests.get(url, headers=headers)
    return response.json()[0]


def get_tesla_price():
    url = 'https://api.tiingo.com/tiingo/daily/tsla/prices'
    response = requests.get(url, headers=headers)
    return response.json()[0]


def get_tesla_info():
    url = 'https://api.tiingo.com/tiingo/daily/tsla'
    response = requests.get(url, headers=headers)
    return response.json()
