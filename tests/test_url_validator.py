import unittest

from core.exceptions import InvalidURLError
from util.url_validator import validate_url


class TestUrlValidator(unittest.TestCase):
    def test_accepts_public_https_url(self):
        result = validate_url("https://www.milestoneinternet.com/")
        self.assertEqual(result, "https://www.milestoneinternet.com/")

    def test_rejects_empty_url(self):
        with self.assertRaises(InvalidURLError):
            validate_url("   ")

    def test_rejects_non_http_scheme(self):
        with self.assertRaises(InvalidURLError):
            validate_url("ftp://example.com")

    def test_rejects_localhost(self):
        with self.assertRaises(InvalidURLError):
            validate_url("http://localhost/")

    def test_rejects_private_ip_literal(self):
        with self.assertRaises(InvalidURLError):
            validate_url("http://192.168.1.1/")

    def test_rejects_embedded_credentials(self):
        with self.assertRaises(InvalidURLError):
            validate_url("https://user:pass@example.com/")


if __name__ == "__main__":
    unittest.main()
