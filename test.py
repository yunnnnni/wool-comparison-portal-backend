import requests
from bs4 import BeautifulSoup
import re

if __name__ == "__main__":
    target_product = "Stylecraft Special double knit"
    query_params = {
        "searchQuery": target_product,
        "sortBy": 0,
        "offset": 0,
        "limit": 16,
        "account": "SQ-119572-1"  # TODO: will account expire? get account automatically
    }
    x = requests.get("https://dynamic.sooqr.com/suggest/script/", params=query_params)
    html_doc = re.findall(r"\"html\":\"(.*)\"", str(x.content))[0].replace("\\\\n", " ").replace("\\\\t", " ").replace(
        "\\\\", "")
    soup = BeautifulSoup(html_doc)
    product_url_list = soup.find_all("a", {"class": "productlist-imgholder"}, href=True)
    # TODO: error handling
    product_url = product_url_list[0]["href"]

    print()