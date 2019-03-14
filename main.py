import os
import requests
import argparse
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')


def check_url_exists(url):
    requests.get(url).raise_for_status()


def normalize_bitlink(url):
    """Возвращает склеенный domain + id от битлинка."""
    url_domain = url.split('/')[-2]
    url_id = url.split('/')[-1]
    return f'{url_domain}/{url_id}'


def create_short_link(token, long_url):
    check_url_exists(long_url)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    json_settings = {
        "long_url": f"{long_url}"
    }
    response = requests.post("https://api-ssl.bitly.com/v4/bitlinks", json=json_settings, headers=headers)
    return response.json()['link']


def count_clicks_on_link(token, short_url):
    check_url_exists(short_url)
    url_for_response = normalize_bitlink(short_url)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        'unit': 'day',
        'units': '-1'
    }
    response = requests.get(f"https://api-ssl.bitly.com/v4/bitlinks/{url_for_response}/clicks/summary", headers=headers,
                            params=params)
    return response.json()['total_clicks']


def is_bitlink(url, token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url_for_response = normalize_bitlink(url)
    response = requests.get(f'https://api-ssl.bitly.com/v4/bitlinks/{url_for_response}', headers=headers)
    try:
        response.json()
        return True
    except:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Создаёт короткую ссылку или возвращает количество переходов по короткой ссылке')
    parser.add_argument('url', help='Которкая или длинная ссылка')
    args = parser.parse_args()
    url = args.url

    if is_bitlink(url, ACCESS_TOKEN):
        try:
            total_clicks = count_clicks_on_link(ACCESS_TOKEN, url)
            print('Количество переходов по ссылке', url, '-', total_clicks)
        except requests.exceptions.HTTPError:
            print("Не могу посчитать количество кликов по этой ссылке")
    else:
        try:
            short_url = create_short_link(ACCESS_TOKEN, url)
            print('Ваша короткая ссылка -', short_url)
        except requests.exceptions.HTTPError:
            print("Не могу создать короткую ссылку из этого url")
