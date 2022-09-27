import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, List
from random import randint
import itertools


class WoolPlatzCrawler:
    def __init__(self, account:str="SQ-119572-1", query_url:str="https://dynamic.sooqr.com/suggest/script/"):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "br, gzip, deflate",
            "Accept-Language": "de-DE",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }
        self.account = account
        self.query_url = query_url

    def get_product_info(self, mark: str, product: str) -> List[Dict]:
        product_root_url = self.get_product_url(f"{mark} {product}")
        target_product_list = self.get_sub_types(product_root_url)
        product_info_list = []
        for target_product in target_product_list:
            product_url = self.get_product_url(target_product)
            product_info = self.parse_product_info(product_url)
            product_info_list.append(product_info)
            time.sleep(randint(100, 1000) / 1000)
        return product_info_list

    def get_product_url(self, product_name: str) -> str:
        query_params = {
            "type": "suggest",
            "searchQuery": product_name,
            "sortBy": 0,
            "offset": 0,
            "limit": 16,
            "account": self.account  # TODO: will account expire? get account automatically
        }
        try:
            r = requests.get(self.query_url, params=query_params, headers=self.headers)
            html_doc = re.findall(r"\"html\":\"(.*)\"", str(r.content))[0].replace("\\\\n", " ").replace("\\\\t", " ").replace(
                "\\\\", "")
            soup = BeautifulSoup(html_doc)
            product_url_list = soup.find_all("a", {"class": "productlist-imgholder"}, href=True)
            if len(product_url_list) == 0:
                raise ValueError
            product_url = product_url_list[0]["href"]  # get url of the first element
            return product_url
        except Exception as e:
            return ""

    def parse_product_info(self, product_url: str) -> Dict:
        try:
            r = requests.get(product_url, headers=self.headers)
            soup = BeautifulSoup(r.content)

            product_info = {}
            product_info["Artikel"] = soup.find(id="pageheadertitle").text
            product_info["Verfügbarkeit"] = soup.find("div", {"id": "ContentPlaceHolder1_upStockInfoDescription"}).find(
                "span").text
            product_info["Preis"] = soup.find("span", {"class": "product-price-amount"}).text  # TODO: currency?
            # TODO: validation
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
            return {}

    def get_sub_types(self, product_url: str) -> List[str]:
        try:
            r = requests.get(product_url, headers=self.headers)
            soup = BeautifulSoup(r.content)

            variant_name = soup.find("span", {"class": "variants-title-txt"}).text
            soup.find_all("div", {"class": "variants-sb-box-item"})
            sub_types = []
            for ele in soup.find_all("div", {"class": "variants-sb-box-item"}):
                sub_types.append(f"{variant_name} {ele.find('span')['data-list-text']}")

            return sub_types
        except Exception as e:
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