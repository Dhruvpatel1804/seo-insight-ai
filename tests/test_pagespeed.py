import unittest

from services.pagespeed import parse_pagespeed_response


SAMPLE_PAGESPEED_RESPONSE = {
    "lighthouseResult": {
        "categories": {
            "performance": {"score": 0.85}
        },
        "audits": {
            "largest-contentful-paint": {"displayValue": "2.1 s"},
            "cumulative-layout-shift": {"displayValue": "0.04"},
            "first-contentful-paint": {"displayValue": "1.0 s"},
            "speed-index": {"displayValue": "2.8 s"},
            "total-blocking-time": {"displayValue": "120 ms"},
        },
    }
}


class TestPageSpeedParser(unittest.TestCase):
    def test_parse_pagespeed_response(self):
        metrics = parse_pagespeed_response(SAMPLE_PAGESPEED_RESPONSE)

        self.assertEqual(metrics.performance_score, 85.0)
        self.assertEqual(metrics.lcp, "2.1 s")
        self.assertEqual(metrics.cls, "0.04")
        self.assertEqual(metrics.fcp, "1.0 s")
        self.assertEqual(metrics.speed_index, "2.8 s")
        self.assertEqual(metrics.inp_or_tbt, "120 ms")


if __name__ == "__main__":
    unittest.main()
