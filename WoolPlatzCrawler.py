import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, List
from random import randint
import itertools
import logging


logging.basicConfig(format="[%(asctime)s] %(levelname)-8s %(filename)s:%(lineno)s(%(funcName)s): %(message)s",
                    level=logging.DEBUG)


class WoolPlatzCrawler:
    def __init__(self, account: str = "SQ-119572-1", query_url: str = "https://dynamic.sooqr.com/suggest/script/"):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "br, gzip, deflate",
            "Accept-Language": "de-DE",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }
        self.account = account
        self.query_url = query_url
        self.logger = logging.getLogger()

    def get_product_info(self, mark: str, product: str) -> List[Dict]:
        self.logger.debug(f"mark={mark}, product={product}")
        try:
            if not isinstance(mark, str):
                raise TypeError("mark is not a string!")
            if not mark:
                raise ValueError("mark is empty")
            if not isinstance(product, str):
                raise TypeError("product is not a string!")
            if not product:
                raise ValueError("product is empty")
            product_root_url = self.get_product_url(f"{mark} {product}")
            target_product_list = self.get_sub_types(product_root_url)
            product_info_list = []
            for target_product in target_product_list:
                self.logger.debug(f"target_product={target_product}")
                product_url = self.get_product_url(target_product)
                product_info = self.parse_product_info(product_url)
                if len(product_info) > 0:
                    product_info_list.append(product_info)
                    time_to_sleep = randint(100, 1000) / 1000
                    self.logger.debug(f"time_to_sleep={time_to_sleep}")
                    time.sleep(time_to_sleep)
            return product_info_list
        except Exception as e:
            self.logger.warning(f"error={e}")
            return ""

    def get_product_url(self, product_name: str) -> str:
        self.logger.debug(f"product_name={product_name}")
        try:
            if not isinstance(product_name, str):
                raise TypeError("product_name is not a string!")
            if not product_name:
                raise ValueError("product_url is empty")
            query_params = {
                "type": "suggest",
                "searchQuery": product_name,
                "sortBy": 0,
                "offset": 0,
                "limit": 16,
                "account": self.account  # TODO: will account expire? get account automatically
            }
            r = requests.get(self.query_url, params=query_params, headers=self.headers)
            html_doc = re.findall(r"\"html\":\"(.*)\"", str(r.content))[0].replace("\\\\n", " ").\
                replace("\\\\t"," ").replace("\\\\", "")
            soup = BeautifulSoup(html_doc, "html.parser")
            product_url_list = soup.find_all("a", {"class": "productlist-imgholder"}, href=True)
            if len(product_url_list) == 0:
                raise ValueError("can't find product url")
            product_url = product_url_list[0]["href"]  # get url of the first element
            self.logger.debug(f"product_url={product_url}")
            return product_url
        except Exception as e:
            self.logger.warning(f"error={e}")
            return ""

    def parse_product_info(self, product_url: str) -> Dict:
        self.logger.debug(f"product_url={product_url}")
        try:
            if not isinstance(product_url, str):
                raise TypeError("product_url is not a string!")
            if not product_url:
                raise ValueError("product_url is empty, can't parse product info")

            r = requests.get(product_url, headers=self.headers)
            soup = BeautifulSoup(r.content, "html.parser")

            product_info = {}
            product_info["Artikel"] = soup.find(id="pageheadertitle").text
            product_info["Verfügbarkeit"] = soup.find("div", {"id": "ContentPlaceHolder1_upStockInfoDescription"}).find(
                "span").text
            product_info["Preis"] = soup.find("span", {"class": "product-price-amount"}).text  # TODO: currency?
            # TODO: validation for product_info
            specification_ele = soup.find("div", {"id": "pdetailTableSpecs"})
            tr_ele_list = specification_ele.find_all("tr")
            specification_dict = {}
            for tr_ele in tr_ele_list:
                td_ele_list = tr_ele.find_all("td")
                if len(td_ele_list) == 2:
                    specification_dict[td_ele_list[0].text] = td_ele_list[1].text
            # other specification can also be taken into account if required
            product_info["Zusammenstellung"] = specification_dict["Zusammenstellung"]
            product_info["Nadelstärke"] = specification_dict["Nadelstärke"]

            return product_info
        except Exception as e:
            self.logger.warning(f"error={e}")
            return {}

    def get_sub_types(self, product_url: str) -> List[str]:
        self.logger.debug(f"product_url={product_url}")
        try:
            if not isinstance(product_url, str):
                raise TypeError("product_url is not a string!")
            if not product_url:
                raise ValueError("product_url is empty, can't get colors")

            r = requests.get(product_url, headers=self.headers)
            soup = BeautifulSoup(r.content, "html.parser")

            variant_name = soup.find("span", {"class": "variants-title-txt"}).text
            soup.find_all("div", {"class": "variants-sb-box-item"})
            sub_types = []
            for ele in soup.find_all("div", {"class": "variants-sb-box-item"}):
                # FIXME: product name in data-list-text is not always correct to build corresponded url
                try:
                    color = ele.find('span')['data-list-text']
                    sub_types.append(f"{variant_name} {color}")
                except Exception as e:
                    self.logger.warning(f"error={e}")
                    continue
            self.logger.debug(f"sub_types={sub_types}")
            return sub_types
        except Exception as e:
            self.logger.warning(f"error={e}")
            return []


if __name__ == "__main__":
    target_list = [
        {"mark": "DMC", "product": "Natura XL"},
        {"mark": "Drops", "product": "Safran"},
        {"mark": "Drops", "product": "Baby Merino Mix"},
        {"mark": "Hahn", "product": "Alpacca Speciale"},
        {"mark": "Stylecraft", "product": "Special double knit"}
    ]

    crawler = WoolPlatzCrawler()
    product_info_list = [crawler.get_product_info(**product) for product in target_list]
    product_info_list = list(itertools.chain(*product_info_list))
    print()
