import unittest

from models.report import PageDetails
from services.scraper import parse_html
from services.seo_validator import validate_seo


SAMPLE_HTML = """
<html>
  <head>
    <title>Example SEO Page Title</title>
    <meta name="description" content="This is an example meta description that is long enough for SEO validation." />
    <link rel="canonical" href="https://www.example.com/" />
  </head>
  <body>
    <h1>Main Heading</h1>
    <h2>Subheading</h2>
    <p>Word one two three four five.</p>
    <img src="a.jpg" alt="described" />
    <img src="b.jpg" />
  </body>
</html>
"""


class TestScraper(unittest.TestCase):
    def test_parse_html_extracts_expected_fields(self):
        details = parse_html(SAMPLE_HTML)

        self.assertEqual(details.title, "Example SEO Page Title")
        self.assertIn("example meta description", details.meta_description)
        self.assertEqual(details.canonical_url, "https://www.example.com/")
        self.assertEqual(details.h1_tags, ["Main Heading"])
        self.assertEqual(details.h2_tags, ["Subheading"])
        self.assertEqual(details.image_count, 2)
        self.assertEqual(details.missing_alt_count, 1)
        self.assertGreater(details.word_count, 0)


class TestSeoValidator(unittest.TestCase):
    def test_validate_seo_returns_expected_statuses(self):
        page_details = parse_html(SAMPLE_HTML)
        checks = validate_seo(page_details)

        self.assertEqual(checks.title_check, "PASS")
        self.assertEqual(checks.meta_description_check, "PASS")
        self.assertEqual(checks.h1_check, "PASS")
        self.assertEqual(checks.alt_text_check, "WARNING")
        self.assertEqual(checks.content_length_check, "FAIL")

    def test_missing_title_fails(self):
        checks = validate_seo(PageDetails())
        self.assertEqual(checks.title_check, "FAIL")


if __name__ == "__main__":
    unittest.main()
