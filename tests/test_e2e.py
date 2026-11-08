import pytest
import threading
import http.server
import socketserver
import os
import random
from playwright.sync_api import Page, expect

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), **kwargs)

@pytest.fixture(scope="session", autouse=True)
def http_server():
    server = socketserver.TCPServer(("", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    yield f"http://localhost:{port}"
    server.shutdown()
    server.server_close()

def test_language_toggle_root_index(page: Page, http_server: str):
    """Test language toggle in the root index.html."""
    page.goto(f"{http_server}/index.html")

    # Initially in zh
    expect(page.locator("html")).to_have_attribute("lang", "zh-TW")
    expect(page.locator("body")).not_to_have_class("en")
    expect(page.locator(".lang-zh").first).to_be_visible()
    expect(page.locator(".lang-en").first).to_be_hidden()

    # Click EN
    page.click("button[data-lang='en']")
    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(page.locator("body")).to_have_class("en")
    expect(page.locator(".lang-zh").first).to_be_hidden()
    expect(page.locator(".lang-en").first).to_be_visible()

    # Click ZH
    page.click("button[data-lang='zh']")
    expect(page.locator("html")).to_have_attribute("lang", "zh-TW")
    expect(page.locator("body")).not_to_have_class("en")
    expect(page.locator(".lang-zh").first).to_be_visible()
    expect(page.locator(".lang-en").first).to_be_hidden()


def test_language_toggle_site_index(page: Page, http_server: str):
    """Test language toggle in the site/index.html."""
    page.goto(f"{http_server}/site/index.html")

    # Wait for the script to apply initial state based on data-lang="en"
    expect(page.locator("html")).to_have_attribute("lang", "en")

    # Click zh
    page.click("button[data-language='zh']")
    expect(page.locator("html")).to_have_attribute("lang", "zh-Hant")
    expect(page.locator("html")).to_have_attribute("data-lang", "zh")
    expect(page).to_have_url(f"{http_server}/site/index.html?lang=zh-TW")

    # Check localStorage
    lang_pref = page.evaluate("window.localStorage.getItem('tedh-project-lang')")
    assert lang_pref == "zh"

    expect(page.locator("button[data-language='zh']")).to_have_attribute("aria-pressed", "true")
    expect(page.locator("button[data-language='en']")).to_have_attribute("aria-pressed", "false")

    # Click en
    page.click("button[data-language='en']")
    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(page.locator("html")).to_have_attribute("data-lang", "en")
    expect(page).to_have_url(f"{http_server}/site/index.html")

    lang_pref = page.evaluate("window.localStorage.getItem('tedh-project-lang')")
    assert lang_pref == "en"

    expect(page.locator("button[data-language='zh']")).to_have_attribute("aria-pressed", "false")
    expect(page.locator("button[data-language='en']")).to_have_attribute("aria-pressed", "true")

def test_mobile_navigation(page: Page, http_server: str):
    """Test mobile navigation in site/index.html."""
    import re
    # Ensure viewport is small enough to show the mobile menu button
    page.set_viewport_size({"width": 800, "height": 600})
    page.goto(f"{http_server}/site/index.html")

    menu_button = page.locator(".menu-button")
    site_nav = page.locator(".site-nav")

    expect(menu_button).to_have_attribute("aria-expanded", "false")
    expect(site_nav).not_to_have_class(re.compile(r"is-open"))

    # Open menu
    menu_button.click()
    expect(menu_button).to_have_attribute("aria-expanded", "true")
    expect(site_nav).to_have_class("site-nav is-open")

    # Close via Escape
    page.keyboard.press("Escape")
    expect(menu_button).to_have_attribute("aria-expanded", "false")
    # Because there's a space or no space, we can just check it doesn't have is-open
    expect(site_nav).not_to_have_class("site-nav is-open")
    expect(site_nav).to_have_class("site-nav")

    # Open menu again
    menu_button.click()
    expect(site_nav).to_have_class("site-nav is-open")

    # Close via clicking a link
    page.locator(".site-nav a").first.click()
    expect(menu_button).to_have_attribute("aria-expanded", "false")
    expect(site_nav).to_have_class("site-nav")

def test_copy_to_clipboard(http_server: str, browser):
    """Test copy to clipboard in site/index.html."""
    context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
    page = context.new_page()
    page.goto(f"{http_server}/site/index.html")

    copy_button = page.locator("button[data-copy='code-1']")
    target_code = page.locator("#code-1")

    # Click copy button
    copy_button.click()

    # Wait for class to be added
    expect(copy_button).to_have_class("copy is-done")

    # Verify clipboard content
    clipboard_text = page.evaluate("navigator.clipboard.readText()")

    # Expect the text in the clipboard to match target innerText
    expected_text = target_code.inner_text().strip()
    assert clipboard_text.strip() == expected_text

def test_flow_diagram_rendering(page: Page, http_server: str):
    """Test that Flow diagrams are correctly rendered by flow.js."""
    page.goto(f"{http_server}/site/index.html")

    # flow.js runs automatically on DOMContentLoaded or similar, so wait for SVG injection
    # In index.html, we have multiple <figure class="fd"> elements
    first_figure = page.locator("figure.fd").first

    # Wait for the svg element to appear
    svg = first_figure.locator("svg.fd-svg")
    expect(svg).to_be_attached()

    # Verify it has is-drawn (we can use regex to match it having the class)
    import re
    expect(first_figure).to_have_class(re.compile(r"is-drawn"))

    # Check for the pulse element inside the svg
    pulse = svg.locator("circle.fd-pulse")
    expect(pulse).to_be_attached()

    # Check that wire paths are generated inside the svg
    expect(svg.locator("path.fd-wire")).to_be_attached()
