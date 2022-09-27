import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, List


HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "br, gzip, deflate",
    "Accept-Language": "de-DE",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}


def get_product_url(product_name: str) -> str:
    query_params = {
        "type": "suggest",
        "searchQuery": product_name,
        "sortBy": 0,
        "offset": 0,
        "limit": 16,
        "account": "SQ-119572-1"  # TODO: will account expire? get account automatically
    }
    try:
        r = requests.get("https://dynamic.sooqr.com/suggest/script/", params=query_params, headers=HEADERS)
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


def parse_product_info(product_url: str) -> Dict:
    try:
        r = requests.get(product_url, headers=HEADERS)
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


def get_sub_types(product_url: str) -> List[str]:
    try:
        r = requests.get(product_url, headers=HEADERS)
        soup = BeautifulSoup(r.content)

        variant_name = soup.find("span", {"class": "variants-title-txt"}).text
        soup.find_all("div", {"class": "variants-sb-box-item"})
        sub_types = []
        for ele in soup.find_all("div", {"class": "variants-sb-box-item"}):
            sub_types.append(f"{variant_name} {ele.find('span')['data-list-text']}")

        return sub_types
    except Exception as e:
        return {}


if __name__ == "__main__":
    target_product = "DMC Natura XL"
    product_url = get_product_url(target_product)
    time.sleep(1.2)
    product_info = parse_product_info(product_url)
    time.sleep(1.0)
    sub_types = get_sub_types(product_url)


    print()