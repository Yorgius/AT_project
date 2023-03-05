
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lxml import etree

import requests
from requests import session

from pprint import pprint


# base parser
class Soup:
    def __init__(self) -> None:
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    def get_page_source(self, url, need_response_by_selenium=False) -> None:
        match need_response_by_selenium:
            case True:
                option = webdriver.ChromeOptions()
                option.add_argument('--headless')
                driver = webdriver.Chrome(options=option)
                driver.set_window_size(1920, 1080)
                driver.implicitly_wait(5)
                
                driver.get(url)
                response = driver.page_source
                driver.quit()
                self.soup  = bs(response, 'lxml')
            case _:
                with session() as s:
                    self.response = s.get(url, headers=self.headers)
                    match self.response.status_code:
                        case 200:
                            self.soup  = bs(self.response.content, 'lxml')

    def get_item(self, selector):
        return self.soup.select_one(selector)

    def get_items(self, selector) -> list:
        return self.soup.select(selector)

    def is_item_present(self, selector) -> bool:
        return True if self.soup.select(selector) else False

    def get_item_in_tag(self, tag, selector):
        return tag.select_one(selector)

    def text_to_digit(self, text: str) -> float:
        return float(text.replace(',', '.'))

    def preparing_data(self, shop, url, price, colors) -> dict:
        return {
            'shop': shop,
            'url': url,
            'yarn': 'pehorka',
            'price': price,
            'colors': colors
        }


# https://miya.by/g8001755-pryazha-pehorka-detskaya
class MiyaParser(Soup):
    def __init__(self) -> None:
        super().__init__()
        self.shop = "miya"

        self.url = "https://miya.by"
        self.url_path = "/g8001755-pryazha-pehorka-detskaya/page_1"
        self.url_get_param = "?product_items_per_page=48"
        
        # Selectors
        self.selectors = {
            "paginator_last_button": ".b-pager__link_pos_last",
            "price": ".cs-goods-price span",
            "color_block": ".cs-product-gallery__item",
            "color_title": ".cs-goods-title",
            "color_availability": ".cs-goods-data__state",
        }

    def set_next_link_by_paginator(self) -> str:
        self.url_path = self.url_path[:-1] +  str(int(self.url_path[-1]) + 1) + self.url_get_param
        return self.url + self.url_path

    def get_price(self) -> float:
        price_text = self.get_item(self.selectors.get('price')).text[:4]
        return self.text_to_digit(price_text)
    
    def get_color_title(self, tag) -> list[str, str]:
        title_fragments = self.get_item_in_tag(tag, self.selectors.get('color_title')).text.lower().strip().split()
        result = [title_fragments[5].lstrip('0'), ' '.join(title_fragments[6:])]
        match result:
            case [str() as code, str()] if code.isdigit():
                return result
            case _:
                return []
    
    def get_color_availability(self, tag) -> str:
        return self.get_item_in_tag(tag, self.selectors.get('color_availability')).text.lower()

    def start_parsing(self) -> dict:
        url = self.url + self.url_path + self.url_get_param
        self.get_page_source(url, True)
        price = self.get_price()
        colors_data = []

        while True:
            tags = self.get_items(self.selectors.get("color_block"))
            for tag in tags:
                title = self.get_color_title(tag)
                if title:
                    availability = self.get_color_availability(tag)
                    title.append(availability)
                    colors_data.append(title)
            if self.is_item_present(self.selectors.get("paginator_last_button")):
                new_link = self.set_next_link_by_paginator()
                self.get_page_source(new_link, True)
            else:
                break
        return self.preparing_data(self.shop, self.url, price, colors_data)


# https://kis.by/vyazanie/pryazha?rdrf%5Bstock%5D=instock&rdrf%5Bman%5D%5B0%5D=107&rdrf%5Bfil%5D%5B115%5D%5B0%5D=3408&limit=100
class KisParser(Soup):
    def __init__(self) -> None:
        super().__init__()

        self.shop =  "kis"
        self.url = "https://kis.by"
        self.url_path = "/vyazanie/pryazha"
        self.url_filter = "?rdrf%5Bstock%5D=instock&rdrf%5Bman%5D%5B0%5D=107&rdrf%5Bfil%5D%5B115%5D%5B0%5D=3408&limit=100"

        self.selectors = {
            "link_from_first_item_in_catalog": "div.caption a",

            "price": ".price > span > span",
            "price_sale": "span.price-new span.autocalc-product-special",
            "color_link": "div.vblock a",
            "color_title": ".h1-prod-name",
            "color_availability": ".stock_status_success",
        }

    def set_new_link(self) -> str:
        link = self.get_item(self.selectors.get('link_from_first_item_in_catalog'))
        return link.attrs['href']

    def get_price(self) -> float:
        if self.is_item_present(self.selectors.get('price_sale')):
            price_text = self.get_item(self.selectors.get('price_sale')).text[:4]
        else:
            price_text = self.get_item(self.selectors.get('price')).text[:4]
        return self.text_to_digit(price_text)

    def get_color_title(self) -> list[str, str]:
        title_text = self.get_item(self.selectors.get('color_title')).text.lower()
        title_text = title_text.split(',')[-1]
        title_text = title_text.strip().strip('№').replace('-', ' ')
        title_fragments = title_text.split()
        return [title_fragments[0].lstrip('0'), ' '.join(title_fragments[1:])]

    def get_color_availability(self) -> str:
        item = self.get_item(self.selectors.get('color_availability'))
        return item.text.lower() if item else 'нет в наличии'

    def start_parsing(self) -> dict:
        url = self.url + self.url_path + self.url_filter
        self.get_page_source(url)
        new_link = self.set_new_link()
        self.get_page_source(new_link)
        
        price = self.get_price()
        colors_data = []
        title = self.get_color_title()
        availability = self.get_color_availability()

        title.append(availability)
        colors_data.append(title)

        color_links = [tag.attrs['href'] for tag in self.get_items(self.selectors.get('color_link'))]
        for link in color_links:
            self.get_page_source(link)
            
            title = self.get_color_title()
            availability = self.get_color_availability()
            title.append(availability)
            colors_data.append(title)
        return self.preparing_data(self.shop, self.url, price, colors_data)


# https://zigzagshop.by/pryazha-pehorskaya-pt/16005-26369-detskaya-novinka.html#/14618-cvet-011_yarrozovyj
class ZigzagParser(Soup):
    def __init__(self) -> None:
        super().__init__()
        self.shop = "zigzagshop"
        self.url = "https://zigzagshop.by"
        self.url_path = "/pryazha-pehorskaya-pt/16005-26369-detskaya-novinka.html#/14618-cvet-011_yarrozovyj"

        self.selectors = {
            "price": ".product-price-value > .product-price-col:nth-child(2) span",
            "color_block": ".combination-card",
            "color_title": ".combination-image",
            "color_availability": ""
        }

    def get_price(self) -> float:
        price_text = self.get_item(self.selectors.get('price')).text[:4]
        return self.text_to_digit(price_text)

    def get_color_title(self, tag) -> list[str, str]:
        interim_title = self.get_item_in_tag(tag, self.selectors.get('color_title')).attrs['title'].lower().strip('№').split()
        return [interim_title[0].lstrip('0'), ' '.join(interim_title[1:])]

    def get_color_availability(self) -> str:
        return 'в наличии'

    def start_parsing(self) -> dict:
        self.get_page_source(self.url + self.url_path)
        
        price = self.get_price()
        colors_data = []
        colors = self.get_items(self.selectors.get('color_block'))
        
        for color in colors:
            title = self.get_color_title(color)
            availability = self.get_color_availability()
            title.append(availability)
            colors_data.append(title)
        return self.preparing_data(self.shop, self.url, price, colors_data)


# https://yarnstore.by/products/detskaya-novinka-pehorka
class YarnstoreParser(Soup):
    def __init__(self) -> None:
        super().__init__()
        self.shop =  "yarnstore"
        self.url = "https://yarnstore.by"
        self.url_path = "/products/detskaya-novinka-pehorka"
        self.selectors = {
            "price": ".tab-content div.price span",
            "color_block": ".variant_name2.ienlarger",
            "color_title": "div:nth-child(2)",
            "color_availability": "div:nth-child(4)",
        }

    def get_price(self) -> float:
        price_text = self.get_item(self.selectors.get('price')).text[:4]
        return self.text_to_digit(price_text)
    
    def get_title(self, tag) -> list[str, str]:
        title_fragments = self.get_item_in_tag(tag, self.selectors.get('color_title')).text.lower().strip().split()
        return [title_fragments[1].lstrip('0'), ' '.join(title_fragments[2:])]
    
    def get_availability(self, tag) -> str:
        return self.get_item_in_tag(tag, self.selectors.get('color_availability')).text.lower().strip()
    
    def start_parsing(self) -> dict:
        url = self.url + self.url_path
        self.get_page_source(url)
        price = self.get_price()
        colors_data = []
        colors = self.get_items(self.selectors.get('color_block'))
        for color in colors:
            title = self.get_title(color)
            availability = self.get_availability(color)
            title.append(availability)
            colors_data.append(title)
        return self.preparing_data(self.shop, self.url, price, colors_data)


# https://1klubok.by/pryazha-pehorka/detskaya-novinka
class KlubokParser(Soup):
    def __init__(self) -> None:
        super().__init__()
        
        self.shop = "1klubok"
        self.url = "https://1klubok.by"
        self.url_path = "/pryazha-pehorka/detskaya-novinka"
        self.page_num = '?page=0'
        self.selectors = {
            "pager_last": ".pager-last",
            "price": "td.price-amount",
            "color_block": ".group-anons",
            "color_title": "a",
            "color_availability": ".group-anons.views-fieldset .nalich2",
        }

    def get_price(self) -> float:
        price_text = self.get_item(self.selectors.get('price')).text[:4]
        return self.text_to_digit(price_text)
    
    def get_title(self, tag) -> list[str, str]:
        title_fragments: str = self.get_item_in_tag(tag, self.selectors.get('color_title')).text.lower().strip()
        title_fragments = title_fragments.replace(' - ', ' ').replace(':', ' ').replace('-', ' ')
        title_fragments = title_fragments.replace('детская новинка', '').replace('пехорка', '').replace('цвет', '').strip()
        title_fragments = title_fragments.split()

        return [title_fragments[0].lstrip('0'), ' '.join(title_fragments[1:])]
    
    def get_availability(self, tag) -> str:
        return self.get_item_in_tag(tag, self.selectors.get('color_availability')).text.lower().strip()

    def start_parsing(self) -> dict:
        url = self.url + self.url_path + self.page_num
        self.get_page_source(url)
        price = self.get_price()
        colors_data = []

        while True:
            color_blocks = self.get_items(self.selectors.get('color_block'))

            for c_block in color_blocks:
                title = self.get_title(c_block)
                availability = self.get_availability(c_block)
                title.append(availability)
                colors_data.append(title)

            if self.is_item_present(self.selectors.get('pager_last')):
                self.page_num = self.page_num[:-1] + str(int(self.page_num[-1]) + 1)
                next_url = self.url + self.url_path + self.page_num
                self.get_page_source(next_url)
            else:
                break
        return self.preparing_data(self.shop, self.url, price, colors_data)


# https://leonardohobby.by/ishop/group_6157356002/
class LeonardoParser(Soup):
    def __init__(self) -> None:
        super().__init__()
        self.shop = "leonardo"
        self.url = "https://leonardohobby.by"
        self.url_path = "/ishop/group_6157356002/"
        self.selectors = {
            "price": ".actual-price",
            "color_block": ".color-item",
            "color_title": "a",
        }

    def get_price(self) -> float:
        price_text = self.get_item(self.selectors.get('price')).text[:4]
        return self.text_to_digit(price_text)
    
    def get_title(self, tag) -> list[str, str]:
        title_sentence: str = tag.select_one(self.selectors.get('color_title')).attrs['title']
        title_fragments = title_sentence.lower().replace('№', '').split()
        return [title_fragments[0].lstrip('0'), ' '.join(title_fragments[1:])]
    
    def start_parsing(self) -> dict:
        url = self.url + self.url_path
        self.get_page_source(url)

        price = self.get_price()
        colors_data = []
        c_blocks = self.get_items(self.selectors.get('color_block'))

        for c_block in c_blocks:
            title = self.get_title(c_block)
            title.append("в наличии")
            colors_data.append(title)
        return self.preparing_data(self.shop, self.url, price, colors_data)


# https://nitti.by/catalog/pryazha_1/26470/
class NittiParser(Soup):
    def __init__(self) -> None:
        # super().__init__()
        self.shop = "nitti"
        self.url = "https://nitti.by"
        self.url_path = "/catalog/pryazha_1/26470/"
        self.selectors = {
            "price": ".info_item span.price_value",
            "color_block": "#bx_117848907_26470_prop_1161_list li",
            "color_title": "i",
            "color_availability": "",
        }

    def create_list_of_urls(self):
        url = self.url + self.url_path
        self.get_page_source(url)

        x_path_selector = "//span[@itemprop='offers']/span[@itemprop='offers']"
        dom = etree.HTML(str(self.soup))
        self.url_parametrs = []
        for el in dom.xpath(x_path_selector):
            self.url_parametrs.append(el.find('a').get('href').split('?')[-1])

    def preparing_web_source(self):
        url = self.url + self.url_path
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1920, 1080)
        self.driver.get(url)

    def get_price(self) -> float:
        price_text = self.driver.find_element(By.CSS_SELECTOR, '.info_item span.price_value').get_attribute('textContent')[:4]
        return self.text_to_digit(price_text)

    def get_title(self) -> list[str, str]:
        title_fragments = self.driver.find_element(By.CSS_SELECTOR, '#bx_117848907_26470_skudiv .val').text.lower().split('-')
        return [title_fragments[0].lstrip('0'), ' '.join(title_fragments[1:])]

    def get_availability(self) -> str:
        return self.driver.find_element(By.CSS_SELECTOR, '.quantity_block_wrapper span.value').get_attribute('textContent').lower()

    def start_parsing(self) -> dict:
        self.preparing_web_source()
        price = self.get_price()
        colors_data = []

        c_blocks = self.driver.find_elements(By.CSS_SELECTOR, '#bx_117848907_26470_prop_1161_list li')
        for block in c_blocks:
            block.click()
            title = self.get_title()
            availability = self.get_availability()
            title.append(availability)
            colors_data.append(title)
        self.driver.quit()
        return self.preparing_data(self.shop, self.url, price, colors_data)


# https://xn--80ajauevw6f.xn--90ais/p103514576-detskaya-novinka.html
class PetelkaParser(Soup):
    def __init__(self) -> None:
        super().__init__()
        self.shop = "петелька"
        self.url = "https://xn--80ajauevw6f.xn--90ais"
        self.url_path = "/p103514576-detskaya-novinka.html"
        self.selectrors = {
            "price": ".b-product-cost__price span:first-child",
        }

    def get_price(self) -> float:
        return float(self.get_item(self.selectrors.get('price')).text[:4])
    
    def start_parsing(self) -> dict:
        url = self.url + self.url_path
        self.get_page_source(url)

        price = self.get_price()
        colors_data = []
        return self.preparing_data(self.shop, self.url, price, colors_data)


def create_data_set() -> list:
    parsers = [
        MiyaParser, 
        KisParser, 
        ZigzagParser, 
        YarnstoreParser, 
        KlubokParser, 
        LeonardoParser, 
        NittiParser, 
        # PetelkaParser
    ]
    return [parser().start_parsing() for parser in tqdm(parsers, colour='green', desc='Fetching data...')]

if __name__ == '__main__':
    pprint(create_data_set())