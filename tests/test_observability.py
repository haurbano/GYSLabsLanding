import unittest
from pathlib import Path


class ObservabilityMarkupTests(unittest.TestCase):
    def setUp(self):
        self.html = Path(__file__).resolve().parents[1].joinpath("index.html").read_text()

    def test_loads_shared_umami_tracker(self):
        self.assertIn('src="https://track.haurtech.com/script.js"', self.html)
        self.assertIn('data-website-id="cfd04108-33d5-4264-9f36-e547a700099a"', self.html)

    def test_contact_ctas_use_anonymous_semantic_events(self):
        self.assertIn('data-umami-event="contact_email"', self.html)
        self.assertIn('data-umami-event="contact_whatsapp"', self.html)
        self.assertNotIn('data-umami-event="contact_email:', self.html)
        self.assertNotIn('data-umami-event="contact_whatsapp:', self.html)


if __name__ == "__main__":
    unittest.main()

class ErrorTrackingMarkupTests(unittest.TestCase):
    def test_loads_a_scrubbed_glitchtip_configuration(self):
        root = Path(__file__).resolve().parents[1]
        html = root.joinpath("index.html").read_text()
        config = root.joinpath("sentry.js").read_text()
        self.assertIn('src="https://browser.sentry-cdn.com/7.120.4/bundle.min.js"', html)
        self.assertIn('src="sentry.js"', html)
        self.assertIn('@ingest.haurtech.com/5', config)
        self.assertIn('sendDefaultPii: false', config)
        self.assertIn('beforeBreadcrumb: () => null', config)
        self.assertIn('delete event.request', config)
        self.assertIn('delete event.breadcrumbs', config)
