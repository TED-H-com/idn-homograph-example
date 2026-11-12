import pytest
import time
import os
from playwright.sync_api import sync_playwright

def test_performance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        index_path = os.path.join(base_dir, 'index.html')

        start = time.time()
        page.goto(f"file://{index_path}")
        page.wait_for_load_state("networkidle")
        load_time = time.time() - start

        metrics = page.evaluate("() => performance.memory ? performance.memory.usedJSHeapSize : 0")

        # Latency benchmark
        assert load_time < 3.0, f"Page load took too long: {load_time}s"

        # Memory benchmark (JS heap size)
        assert metrics < 50_000_000, f"Memory footprint too high: {metrics} bytes"

        # Toggle language and measure time
        toggle_start = time.time()
        page.click("button[data-lang='en']")
        toggle_time = time.time() - toggle_start
        assert toggle_time < 0.5, f"Language toggle took too long: {toggle_time}s"

        browser.close()
