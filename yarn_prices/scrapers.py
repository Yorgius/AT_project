
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests

from datetime import datetime


SITES = [
    {"title": "nitti",
    "url": "https://nitti.by/catalog/pryazha_1/26470/?oid=23622",
    "selector": ".info_item span.price_value"},
    
    {"title": "leonardo",
    "url": "https://leonardohobby.by/ishop/group_6157356002/",
    "selector": ".actual-price"},
    
    {"title": "klubok",
    "url": "https://1klubok.by/pryazha-pehorka/detskaya-novinka",
    "selector": "td.price-amount"},

    {"title": "yarnstore",
    "url": "https://yarnstore.by/products/detskaya-novinka-pehorka",
    "selector": ".tab-content div.price span",
    "headers": {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'cookie': 'PHPSESSID=h3tmppbickjivavvsq1gr4q650; _ga=GA1.2.1519017837.1672678506; _ym_uid=16726785061030010334; _ym_d=1672678506; browsed_products=270; _gid=GA1.2.2106586696.1675450826; _ym_isad=1; _ym_visorc=w',
        'dnt': '1',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }},

    {"title": "zigzagshop",
    "url": "https://zigzagshop.by/pryazha-pehorskaya-pt/16005-26369-detskaya-novinka.html#/14618-cvet-011_yarrozovyj",
    "selector": ".product-price-value > .product-price-col:nth-child(2) span"},

    {"title": "петелька",
    "url": "https://xn--80ajauevw6f.xn--90ais/p103514576-detskaya-novinka.html",
    "selector": ".b-product-cost__price span:first-child"},

    {"title": "kis",
    "url": "https://kis.by/pryazha-detskaya-novinka-1-motka-50g-200m-pekhorka-18-persik",
    "selector": ".price > span > span",
    "headers": {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': 'PHPSESSID=hqkl6621ccibba10sk19u5kko5; default=4qgp20t4ug3jta4fo6khhp9715; _ga=GA1.1.1598234847.1672678657; _ym_uid=1672678657503890543; _ym_d=1672678657; language=ru-ru; currency=BYN; _ym_isad=1; _ym_visorc=w; _ga_FLBNXB63MG=GS1.1.1675516077.7.1.1675517154.0.0.0',
        'dnt': '1',
        'referer': 'https://kis.by/index.php?route=product/search&search=%D0%B4%D0%B5%D1%82%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%B8%D0%BD%D0%BA%D0%B0',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }},
    

    {"title": "miya",
    "url": "https://miya.by/p106143454-pryazha-pehorka-detskaya.html",
    "selector": ".b-product-cost__price span"},

    # {"title": "https://kupimotok.by/",
    # "url": "",
    # "selector": ""},
]

class MagicSoup:
    def __init__(self, url: str, selector: str) -> float:
        self.url = url
        self.selector = selector

    def cook_soup(self, site_headers) -> None:
        response = requests.get(self.url, headers=site_headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            price = soup.select(self.selector)[0].text[:4]
            if self.is_price_correct(price):
                price = self.correct_comma_to_dot(price)
            price = self.convert_price_to_float(price)
        else:
            print('\n',response.status_code)
            price = 0

        return price

    # проверка на наличие в price символа <,>
    def is_price_correct(self, price: str) -> bool:
        return ',' in price

    # исправление символа <,> на <.>
    def correct_comma_to_dot(self, price: str) -> str:
        return price.replace(',', '.')

    # конвертация строкового значения price в float
    def convert_price_to_float(self, price: str) -> float:
        return float(price)

def magic_soup() -> list:
    data_set = []
    for site in tqdm(SITES, desc='fetching data...', colour='green'):
        data_set.append({'shop_name': site.get('title'), \
            'shop_url': site.get('url'), 
            'yarn_name': 'Pehorka', 
            'yarn_price': MagicSoup(site.get('url', ''), site.get('selector', '')).cook_soup(site.get('headers', {}))})
    return data_set
    # return [MagicSoup(*site.values()).tasting() for site in tqdm(SITES, 'fetching data...', colour='green')]

if __name__ == '__main__':
    for data_element in magic_soup():
        print(data_element)