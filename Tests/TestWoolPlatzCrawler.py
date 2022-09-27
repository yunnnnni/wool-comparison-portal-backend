import unittest
from WoolPlatzCrawler import WoolPlatzCrawler


class TestWoolPlatzCrawler(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crawler = WoolPlatzCrawler()

    def test_get_sub_types(self):
        ret_val = self.crawler.get_sub_types("")
        self.assertEqual(ret_val, [])

    def test_parse_product_info(self):
        ret_val = self.crawler.parse_product_info("")
        self.assertEqual(ret_val, {})

    def test_get_product_url(self):
        ret_val = self.crawler.get_product_url("")
        self.assertEqual(ret_val, "")


if __name__ == '__main__':
    unittest.main()
