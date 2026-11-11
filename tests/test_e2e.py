import re
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

def test_site_lang_from_url_param(page: Page, http_server: str):
    """Test language preference from URL parameter."""
    # Test zh-TW
    page.goto(f"{http_server}/site/index.html?lang=zh-TW")
    expect(page.locator("html")).to_have_attribute("lang", "zh-Hant")
    expect(page.locator("html")).to_have_attribute("data-lang", "zh")

    # Test en
    page.goto(f"{http_server}/site/index.html?lang=en")
    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(page.locator("html")).to_have_attribute("data-lang", "en")

def test_site_lang_from_localstorage(browser, http_server: str):
    """Test language preference from localStorage."""
    context = browser.new_context()
    page = context.new_page()

    # Pre-set localStorage to 'zh'
    page.goto(f"{http_server}/site/index.html")
    page.evaluate("window.localStorage.setItem('tedh-project-lang', 'zh')")

    # Reload and check
    page.goto(f"{http_server}/site/index.html")
    expect(page.locator("html")).to_have_attribute("lang", "zh-Hant")
    expect(page.locator("html")).to_have_attribute("data-lang", "zh")

    context.close()

def test_site_segmenter_wbr_insertion(page: Page, http_server: str):
    """Test that wbr elements are inserted for Chinese headers if Intl.Segmenter is supported."""
    page.goto(f"{http_server}/site/index.html?lang=zh-TW")

    # Check if browser supports Intl.Segmenter
    supports_segmenter = page.evaluate("!!(window.Intl && Intl.Segmenter)")

    if supports_segmenter:
        # Check if a wbr tag was inserted inside a Chinese header
        wbr_count = page.evaluate("document.querySelectorAll('h1[lang^=\"zh\"] wbr, h2[lang^=\"zh\"] wbr, h1 [lang^=\"zh\"] wbr, h2 [lang^=\"zh\"] wbr').length")
        assert wbr_count > 0, "Expected <wbr> tags to be inserted in Chinese text."

def test_site_data_year_update(page: Page, http_server: str):
    """Test that elements with data-year are updated to the current year."""
    page.goto(f"{http_server}/site/index.html")

    import datetime
    current_year = str(datetime.datetime.now().year)

    # Find all elements with data-year and verify their text content
    year_elements = page.locator("[data-year]")
    count = year_elements.count()

    for i in range(count):
        assert year_elements.nth(i).inner_text() == current_year

def test_invalid_copy_target(http_server: str, browser):
    """Test copy behavior when target doesn't exist by modifying an existing button."""
    context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
    page = context.new_page()
    page.goto(f"{http_server}/site/index.html")

    # Use the first copy button available
    copy_button = page.locator("button[data-copy]").first

    # Modify the target of the real button before clicking it
    page.evaluate("document.querySelector('button[data-copy]').setAttribute('data-copy', 'non-existent-id')")

    # Click it, should not throw or change class since target doesn't exist
    copy_button.click()

    # Let any potential async operations complete
    page.wait_for_timeout(500)

    expect(copy_button).not_to_have_class("is-done")

    context.close()

def test_language_toggle_title_meta(page: Page, http_server: str):
    """Test title and meta description updates on language toggle."""
    page.goto(f"{http_server}/site/index.html")

    # Initial state (en)
    expect(page).to_have_title("idn-homograph-example · An IDN homograph attack awareness demo")
    meta_desc = page.locator('meta[name="description"]')
    expect(meta_desc).to_have_attribute("content", "A single-page, bilingual demo that shows how a Cyrillic letter can pass for a Latin one in a link, what the browser really opens, and how to defend against it.")

    # Switch to zh
    page.click("button[data-language='zh']")
    expect(page).to_have_title("idn-homograph-example · IDN 同形異義字攻擊的教學 demo")
    expect(meta_desc).to_have_attribute("content", "單頁、中英雙語的教學 demo：示範一個西里爾字母如何在連結裡冒充拉丁字母、瀏覽器實際連到哪裡，以及該怎麼防。")

    # Switch back to en
    page.click("button[data-language='en']")
    expect(page).to_have_title("idn-homograph-example · An IDN homograph attack awareness demo")
    expect(meta_desc).to_have_attribute("content", "A single-page, bilingual demo that shows how a Cyrillic letter can pass for a Latin one in a link, what the browser really opens, and how to defend against it.")


def test_language_toggle_removes_url_param_for_en(page: Page, http_server: str):
    """Test language toggle removes the URL parameter when switching to 'en'."""
    page.goto(f"{http_server}/site/index.html?lang=zh-TW")
    expect(page).to_have_url(f"{http_server}/site/index.html?lang=zh-TW")

    page.click("button[data-language='en']")
    expect(page).to_have_url(f"{http_server}/site/index.html")


def test_escape_key_behavior_navigation(page: Page, http_server: str):
    """Test escape key behavior for the navigation menu."""
    page.set_viewport_size({"width": 800, "height": 600})
    page.goto(f"{http_server}/site/index.html")

    menu_button = page.locator(".menu-button")
    site_nav = page.locator(".site-nav")

    # Open menu
    menu_button.click()
    expect(site_nav).to_have_class("site-nav is-open")

    # Press Escape to close it
    page.keyboard.press("Escape")
    expect(site_nav).to_have_class("site-nav")
    expect(menu_button).to_be_focused()

    # Press Escape again when already closed (should do nothing)
    page.keyboard.press("Escape")
    expect(site_nav).to_have_class("site-nav")


def test_missing_intl_segmenter(page: Page, http_server: str):
    """Simulate environments lacking Intl.Segmenter."""
    # We can override Intl.Segmenter before the page loads
    page.add_init_script("delete window.Intl.Segmenter;")
    page.goto(f"{http_server}/site/index.html?lang=zh-TW")

    # The script should not throw an error and the page should still function
    # Check if the title was set correctly to verify JS didn't crash before that point
    expect(page).to_have_title("idn-homograph-example · IDN 同形異義字攻擊的教學 demo")

    # And we shouldn't find any <wbr> tags inserted by the polyfill logic
    wbr_count = page.evaluate("document.querySelectorAll('wbr').length")
    assert wbr_count == 0


def test_lang_browser_locale_fallback(browser, http_server: str):
    """Test browser locale fallback in site/lang.js."""
    # Launch browser with specific locale
    context = browser.new_context(locale="zh-CN")
    page = context.new_page()
    page.goto(f"{http_server}/site/index.html")

    # Should default to zh based on browser locale
    expect(page.locator("html")).to_have_attribute("lang", "zh-Hant")
    expect(page.locator("html")).to_have_attribute("data-lang", "zh")

    context.close()

    # Now test with non-zh locale
    context = browser.new_context(locale="fr-FR")
    page = context.new_page()
    page.goto(f"{http_server}/site/index.html")

    # Should default to en based on fallback logic in lang.js
    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(page.locator("html")).to_have_attribute("data-lang", "en")
    context.close()

def test_lang_invalid_url_parameter(page: Page, http_server: str):
    """Test handling of invalid lang values in URL parameter."""
    page.goto(f"{http_server}/site/index.html?lang=invalid")

    # Should fallback to browser language (en by default in tests)
    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(page.locator("html")).to_have_attribute("data-lang", "en")


def test_flow_diagram_missing_data_fd(page: Page, http_server: str):
    """Test that flow diagrams without data-fd handle missing gracefully."""
    page.goto(f"{http_server}/site/index.html")

    # Let's inject a broken figure
    page.evaluate('''
        const fig = document.createElement("figure");
        fig.className = "fd";
        // No data-fd attribute
        document.body.appendChild(fig);
        // And manually trigger render
        TedFlow.render(fig);
    ''')

    # Ensure it wasn't marked as drawn because data-fd was missing
    is_drawn = page.evaluate('document.querySelector("figure.fd:not([data-fd])").classList.contains("is-drawn")')
    assert not is_drawn

def test_flow_diagram_malformed_data_fd(page: Page, http_server: str):
    """Test that flow diagrams with malformed data-fd handle gracefully."""
    page.goto(f"{http_server}/site/index.html")

    # Inject a malformed figure
    page.evaluate('''
        const fig = document.createElement("figure");
        fig.className = "fd";
        fig.setAttribute("data-fd", "{ invalid json }");
        document.body.appendChild(fig);
        TedFlow.render(fig);
    ''')

    is_drawn = page.evaluate('document.querySelector("figure.fd[data-fd=\\"{ invalid json }\\"]").classList.contains("is-drawn")')
    assert not is_drawn

def test_flow_diagram_frozen_at(page: Page, http_server: str):
    """Test fd-at URL parameter pauses animations."""
    page.goto(f"{http_server}/site/index.html?fd-at=2")

    # Ensure a diagram has the is-paused class when fd-at is specified
    first_figure = page.locator("figure.fd").first
    expect(first_figure).to_have_class(re.compile(r"is-paused"))

def test_flow_diagram_reduced_motion(browser, http_server: str):
    """Test prefers-reduced-motion applies is-static."""
    # Launch browser with reduced motion preference
    context = browser.new_context(color_scheme="dark") # not specifically motion but playwright can't set motion directly in new_context
    page = context.new_page()
    page.emulate_media(reduced_motion="reduce")

    page.goto(f"{http_server}/site/index.html")

    first_figure = page.locator("figure.fd").first
    expect(first_figure).to_have_class(re.compile(r"is-static"))
    context.close()

def test_flow_diagram_intersection_observer(page: Page, http_server: str):
    """Test intersection observer toggles is-paused class."""
    page.set_viewport_size({"width": 800, "height": 600})
    page.goto(f"{http_server}/site/index.html")

    first_figure = page.locator("figure.fd").first
    first_figure.scroll_into_view_if_needed()

    # Wait for IO to kick in (should be visible, not paused)
    expect(first_figure).not_to_have_class(re.compile(r"is-paused"))

    # Scroll to the bottom so it's out of view
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # Wait for the observer to mark it as paused
    expect(first_figure).to_have_class(re.compile(r"is-paused"))

    # Scroll back into view
    first_figure.scroll_into_view_if_needed()

    # Wait for it to become unpaused
    expect(first_figure).not_to_have_class(re.compile(r"is-paused"))
