import requests

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Token d85a9d229a18b1b2f940b84c9e4c8c00c8474faa'
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
