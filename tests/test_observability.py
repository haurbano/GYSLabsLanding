import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# La instrumentación vive ahora en las tres páginas del sitio, no solo en la
# raíz: cada una carga el tracker y el scrub de errores por su cuenta.
PAGES = ("index.html", "agents/index.html", "greentax/index.html")


class ObservabilityMarkupTests(unittest.TestCase):
    def test_every_page_loads_shared_umami_tracker(self):
        for page in PAGES:
            with self.subTest(page=page):
                html = ROOT.joinpath(page).read_text()
                self.assertIn('src="https://track.haurtech.com/script.js"', html)
                self.assertIn('data-website-id="cfd04108-33d5-4264-9f36-e547a700099a"', html)

    def test_contact_ctas_use_anonymous_semantic_events(self):
        for page in PAGES:
            with self.subTest(page=page):
                html = ROOT.joinpath(page).read_text()
                self.assertIn('data-umami-event="contact_email"', html)
                self.assertIn('data-umami-event="contact_whatsapp"', html)
                self.assertNotIn('data-umami-event="contact_email:', html)
                self.assertNotIn('data-umami-event="contact_whatsapp:', html)

    def test_no_event_names_beyond_the_two_allowed(self):
        allowed = {"contact_email", "contact_whatsapp"}
        for page in PAGES:
            with self.subTest(page=page):
                html = ROOT.joinpath(page).read_text()
                found = set(re.findall(r'data-umami-event="([^"]*)"', html))
                self.assertEqual(found - allowed, set())

    def test_no_dynamic_umami_properties(self):
        # data-umami-event-<prop> es cómo Umami adjunta propiedades: ninguna
        # página puede mandar rutas, ids, montos ni texto del visitante.
        for page in PAGES:
            with self.subTest(page=page):
                html = ROOT.joinpath(page).read_text()
                self.assertNotIn("data-umami-event-", html)


class ErrorTrackingMarkupTests(unittest.TestCase):
    def test_every_page_loads_a_scrubbed_glitchtip_configuration(self):
        config = ROOT.joinpath("sentry.js").read_text()
        self.assertIn("@ingest.haurtech.com/5", config)
        self.assertIn("sendDefaultPii: false", config)
        self.assertIn("beforeBreadcrumb: () => null", config)
        self.assertIn("delete event.request", config)
        self.assertIn("delete event.breadcrumbs", config)

        for page in PAGES:
            with self.subTest(page=page):
                html = ROOT.joinpath(page).read_text()
                self.assertIn('src="https://browser.sentry-cdn.com/7.120.4/bundle.min.js"', html)
                self.assertIn("sentry.js", html)


class NavigationTests(unittest.TestCase):
    """Las tres páginas son un solo sitio: los enlaces entre ellas y los
    anclas internos tienen que existir de verdad."""

    def test_home_links_to_both_service_pages(self):
        html = ROOT.joinpath("index.html").read_text()
        self.assertIn('href="/agents"', html)
        self.assertIn('href="/greentax"', html)

    def test_greentax_links_to_the_client_portal(self):
        html = ROOT.joinpath("greentax/index.html").read_text()
        self.assertIn('href="https://greentax.gyslabs.com/clientes/"', html)

    def test_in_page_anchors_resolve(self):
        for page in PAGES:
            with self.subTest(page=page):
                html = ROOT.joinpath(page).read_text()
                for anchor in set(re.findall(r'href="#([^"]+)"', html)):
                    self.assertIn(f'id="{anchor}"', html, f"{page}: #{anchor} no existe")


if __name__ == "__main__":
    unittest.main()
