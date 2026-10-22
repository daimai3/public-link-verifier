import unittest

from verify_links import PageParser, normalized_url


class LinkParserTest(unittest.TestCase):
    def test_link_and_noindex(self):
        parser = PageParser()
        parser.feed('<meta name="robots" content="noindex, follow"><a href="https://vietnabi.com/" rel="nofollow">보기</a>')
        self.assertTrue(parser.noindex)
        self.assertEqual(parser.links, [("https://vietnabi.com/", "nofollow")])

    def test_url_normalization(self):
        self.assertEqual(normalized_url("HTTPS://Vietnabi.com/a//#part"), "https://vietnabi.com/a")
        with self.assertRaises(ValueError):
            normalized_url("javascript:alert(1)")


if __name__ == "__main__":
    unittest.main()
