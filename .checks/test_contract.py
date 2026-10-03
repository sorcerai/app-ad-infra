import os
import json
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("calculator.html", "skan-audit.html")
VIEWPORTS = ((1280, 900), (390, 844))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class WhatsAppContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            lambda *args, **kwargs: QuietHandler(*args, directory=str(ROOT), **kwargs),
        )
        cls.addClassCleanup(server.server_close)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        cls.addClassCleanup(thread.join, timeout=2)
        cls.addClassCleanup(server.shutdown)
        cls.base_url = f"http://127.0.0.1:{server.server_port}"
        driver = sync_playwright().start()
        cls.addClassCleanup(driver.stop)
        endpoint = os.environ.get("PLAYWRIGHT_CDP_URL")
        if endpoint:
            cls.browser = driver.chromium.connect_over_cdp(endpoint)
        else:
            cls.browser = driver.chromium.launch(headless=True, executable_path=os.environ.get("PLAYWRIGHT_EXECUTABLE_PATH"))
            cls.addClassCleanup(cls.browser.close)

    def open_page(self, path, viewport, sdk_present):
        width, height = viewport
        context = self.browser.new_context(
            viewport={"width": width, "height": height},
            is_mobile=width < 600,
            has_touch=width < 600,
        )
        self.addCleanup(context.close)
        # Never load the production SDK or send analytics during CI.
        context.route("**/analytics/v2.js", lambda route: route.abort())
        context.route("**/api/analytics/event**", lambda route: route.abort())
        context.route("**/api/intent", lambda route: route.abort())
        # Exercise real popup navigation without contacting WhatsApp.
        context.route(
            "https://wa.me/**",
            lambda route: route.fulfill(
                status=200,
                content_type="text/html",
                body="<!doctype html><title>Intercepted WhatsApp destination</title>",
            ),
        )
        context.add_init_script("window.__goals = [];")
        if sdk_present:
            context.add_init_script(
                "window.searchOps = {track(name) { window.__goals.push(name); }};"
            )
        page = context.new_page()
        page.set_default_timeout(10000)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        response = page.goto(f"{self.base_url}/{path}", wait_until="domcontentloaded")
        self.assertEqual(response.status, 200)
        return context, page, errors

    def test_whatsapp_intent_and_navigation_with_and_without_sdk(self):
        for path in PAGES:
            for viewport in VIEWPORTS:
                for sdk_present in (True, False):
                    with self.subTest(path=path, viewport=viewport, sdk=sdk_present):
                        context, page, errors = self.open_page(
                            path, viewport, sdk_present
                        )
                        try:
                            for nested in (False, True):
                                with self.subTest(nested=nested):
                                    links = page.locator(
                                        'a[href^="https://wa.me/"]:visible'
                                    )
                                    link = links.last if nested else links.first
                                    href = link.get_attribute("href")
                                    target = link.get_attribute("target")
                                    click_target = link
                                    if nested:
                                        link.evaluate("""element => {
                                            const child = document.createElement('span');
                                            child.textContent = element.textContent;
                                            child.dataset.contractChild = 'true';
                                            element.replaceChildren(child);
                                        }""")
                                        click_target = link.locator(
                                            '[data-contract-child="true"]'
                                        )
                                    page.evaluate("window.__goals = []")
                                    with page.expect_popup() as popup_info:
                                        if viewport[0] < 600:
                                            click_target.tap()
                                        else:
                                            click_target.click()
                                    popup = popup_info.value
                                    popup.wait_for_load_state("domcontentloaded")
                                    self.assertEqual(popup.url, href)
                                    self.assertEqual(
                                        popup.title(),
                                        "Intercepted WhatsApp destination",
                                    )
                                    popup.close()
                                    self.assertEqual(
                                        page.evaluate("window.__goals"),
                                        ["whatsapp_click"] if sdk_present else [],
                                    )
                                    self.assertEqual(link.get_attribute("href"), href)
                                    self.assertEqual(
                                        link.get_attribute("target"), target
                                    )
                                    self.assertEqual(errors, [])
                        finally:
                            context.close()

    def test_non_whatsapp_click_does_not_emit_intent(self):
        for path in PAGES:
            with self.subTest(path=path):
                context, page, errors = self.open_page(path, VIEWPORTS[0], True)
                try:
                    original_url = page.url
                    page.locator("h1").click()
                    self.assertEqual(page.evaluate("window.__goals"), [])
                    self.assertEqual(page.url, original_url)
                    self.assertEqual(errors, [])
                finally:
                    context.close()

    def test_article_resources_navigation_returns_to_index(self):
        context, page, errors = self.open_page(
            "resources/mobile-app-ua-infrastructure-skan-mmp-and-uac-scaling-playbook.html",
            VIEWPORTS[1], False,
        )
        page.get_by_role("navigation").get_by_role("link", name="Resources").click()
        page.wait_for_load_state("domcontentloaded")
        self.assertEqual(page.url, self.base_url + "/resources/")
        self.assertEqual(page.locator("h1").count(), 1)
        self.assertEqual(errors, [])

    def test_roas_article_public_metadata_and_mobile_layout(self):
        for viewport in VIEWPORTS:
            context, page, errors = self.open_page(
                "resources/mobile-app-ua-infrastructure-skan-mmp-and-uac-scaling-playbook.html",
                viewport, False,
            )
            page.wait_for_load_state("networkidle")
            self.assertEqual(page.locator("h1").inner_text(), "SKAdNetwork ROAS audit for iOS app campaigns")
            canonical = page.locator('link[rel="canonical"]').get_attribute("href")
            graph = json.loads(page.locator('script[type="application/ld+json"]').inner_text())["@graph"]
            article = next(x for x in graph if x["@type"] == "TechArticle")
            self.assertEqual(article["mainEntityOfPage"], canonical)
            self.assertEqual(article["headline"], page.locator("h1").inner_text())
            faq = next(x for x in graph if x["@type"] == "FAQPage")
            for question in faq["mainEntity"]:
                self.assertEqual(page.get_by_role("heading", name=question["name"], exact=True).count(), 1)
                self.assertIn(question["acceptedAnswer"]["text"], page.locator("article").inner_text())
            self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), viewport[0])
            self.assertEqual(errors, [])
            context.close()


if __name__ == "__main__":
    unittest.main()
