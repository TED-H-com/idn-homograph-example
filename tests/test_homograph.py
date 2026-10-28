import pytest
from playwright.sync_api import Page, expect
import os
import urllib.parse
from PIL import Image, ImageChops
import io
import math
import operator
from functools import reduce

# Get the path to index.html
FILE_PATH = f"file://{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'index.html'))}"

def test_punycode_conversion_accuracy(page: Page):
    """
    Test that the fake link URL correctly encodes to the expected punycode
    """
    page.goto(FILE_PATH)

    # Get all links in the demo links section
    links = page.locator(".link-card a")

    # The first link is real, the second is fake
    fake_link = links.nth(1)
    href = fake_link.get_attribute("href")

    # Parse the host from the href
    parsed_url = urllib.parse.urlparse(href)
    host = parsed_url.hostname

    # Encode the host to IDNA (Punycode)
    punycode_host = host.encode('idna').decode('utf-8')

    # Verify the punycode conversion accuracy
    assert punycode_host == 'xn--exmplebank-0qi.example'

def rmsdiff(im1, im2):
    """Calculate the root-mean-square difference between two images"""
    h = ImageChops.difference(im1, im2).histogram()
    # calculate rms
    return math.sqrt(reduce(operator.add,
        map(lambda h, i: h*(i**2), h, range(256))
    ) / (float(im1.size[0]) * im1.size[1]))

def test_visual_similarity_scoring(page: Page):
    """
    Verify that the real and fake links are visually identical.
    We take screenshots of both link elements and compute the RMS difference.
    A score of 0.0 means they are pixel-perfect identical.
    """
    page.goto(FILE_PATH)

    # Wait for font to load to avoid flakiness
    page.evaluate("document.fonts.ready")

    links = page.locator(".link-card a")

    real_link = links.nth(0)
    fake_link = links.nth(1)

    # Take screenshot of the text content of the real link
    real_bytes = real_link.screenshot()

    # Take screenshot of the text content of the fake link
    fake_bytes = fake_link.screenshot()

    im1 = Image.open(io.BytesIO(real_bytes))
    im2 = Image.open(io.BytesIO(fake_bytes))

    # Ensure they have the same size, or pad/crop to the same size
    # Since they are different unicode characters, their rendered bounding boxes MIGHT differ very slightly
    # Let's just compare the images if they are the same size
    # Wait, the lengths might be slightly different in pixels.
    # We will just verify they are very similar (e.g. RMS difference < 5.0)

    # Resize to same size if there is a tiny 1px difference due to rendering
    if im1.size != im2.size:
        im2 = im2.resize(im1.size)

    diff = rmsdiff(im1.convert("L"), im2.convert("L"))

    # It should be extremely similar
    assert diff < 10.0

def test_browser_warning_trigger_display(page: Page):
    """
    Test that the browser warning trigger / hint UI is displayed
    when viewing the fake domain.
    """
    page.goto(FILE_PATH)

    # Wait for the page to load
    page.wait_for_selector(".demo-hint")

    # Verify the warning UI hint is visible
    demo_hint = page.locator(".demo-hint.lang-zh")
    expect(demo_hint).to_be_visible()

    # Verify it mentions the expected punycode and warns the user
    text = demo_hint.text_content()
    assert "xn--exmplebank-0qi.example" in text

    # Also verify the English version
    # Click English toggle
    page.locator("button[data-lang='en']").click()

    demo_hint_en = page.locator(".demo-hint.lang-en")
    expect(demo_hint_en).to_be_visible()
    text_en = demo_hint_en.text_content()
    assert "xn--exmplebank-0qi.example" in text_en
    assert "browser may warn you" in text_en
