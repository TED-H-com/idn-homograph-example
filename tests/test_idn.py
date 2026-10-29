import unittest
import urllib.parse
from html.parser import HTMLParser
import os

class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    self.links.append(value)

class TestIDNHomograph(unittest.TestCase):
    def setUp(self):
        # Load the index.html file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        index_path = os.path.join(base_dir, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()

    def test_links_contain_homographs(self):
        """Test that the expected links are present and correctly spoofed."""
        parser = LinkExtractor()
        parser.feed(self.html_content)

        real_href = None
        fake_href = None

        for href in parser.links:
            if 'exаmplebank.example' in href:
                fake_href = href
            elif 'examplebank.example' in href:
                real_href = href

        self.assertIsNotNone(real_href, "Real link not found in index.html")
        self.assertIsNotNone(fake_href, "Fake homograph link not found in index.html")

        # Ensure fake link is a homograph of real link
        real_domain = urllib.parse.urlparse(real_href).netloc
        fake_domain = urllib.parse.urlparse(fake_href).netloc

        # The fake domain should encode to a different punycode
        real_encoded = real_domain.encode('idna').decode('ascii')
        fake_encoded = fake_domain.encode('idna').decode('ascii')

        self.assertEqual(real_encoded, "examplebank.example")
        self.assertEqual(fake_encoded, "xn--exmplebank-0qi.example")

    def test_character_table_accuracy(self):
        """Test that the homograph characters encode to punycode properly."""
        # 'a', 'c', 'e', 'o', 'p'
        # verify that the IDNA encodings match expectations

        pairs = {
            'a': ('а', 'xn--80a'),
            'c': ('с', 'xn--q1a'),
            'e': ('е', 'xn--e1a'),
            'o': ('о', 'xn--n1a'),
            'p': ('р', 'xn--p1a')
        }

        for latin, (cyrillic, expected_punycode) in pairs.items():
            encoded = cyrillic.encode('idna').decode('ascii')
            self.assertEqual(encoded, expected_punycode)

if __name__ == '__main__':
    unittest.main()
