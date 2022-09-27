import requests
from bs4 import BeautifulSoup
import re
import time


if __name__ == "__main__":
    myheaders = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "br, gzip, deflate",
        "Accept-Language": "de-DE",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    target_product = "Stylecraft Charm"
    query_params = {
        "searchQuery": target_product,
        "sortBy": 0,
        "offset": 0,
        "limit": 16,
        "account": "SQ-119572-1"  # TODO: will account expire? get account automatically
    }
    x = requests.get("https://dynamic.sooqr.com/suggest/script/", headers=myheaders, params=query_params)
    html_doc = re.findall(r"\"html\":\"(.*)\"", str(x.content))[0].replace("\\\\n", " ").replace("\\\\t", " ").replace(
        "\\\\", "")
    soup = BeautifulSoup(html_doc)
    product_url_list = soup.find_all("a", {"class": "productlist-imgholder"}, href=True)
    # TODO: error handling
    product_url = product_url_list[0]["href"]
    time.sleep(1.2)
    product_content = requests.get(product_url, headers=myheaders).content
    soup2 = BeautifulSoup(product_content)

    product_info = {}
    product_info["Verfügbarkeit"] = soup2.find("div", {"id": "ContentPlaceHolder1_upStockInfoDescription"}).find("span").text
    product_info["Preis"] = soup2.find("span", {"class": "product-price-amount"}).text  # TODO: currency?
    # TODO: validation

    specification_ele = soup2.find("div", {"id": "pdetailTableSpecs"})
    tr_ele_list = specification_ele.find_all("tr")
    specification_dict = {}
    for tr_ele in tr_ele_list:
        td_ele_list = tr_ele.find_all("td")
        if len(td_ele_list) == 2:
            specification_dict[td_ele_list[0].text] = td_ele_list[1].text
    # other specification can also be taken into account if required
    product_info["Zusammenstellung"] = specification_dict["Zusammenstellung"]
    product_info["Nadelstärke"] = specification_dict["Nadelstärke"]
    # product_info.update(specification_dict)
    print()