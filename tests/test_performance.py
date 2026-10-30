import pytest
import os
import time
from playwright.sync_api import sync_playwright

def test_language_toggle_performance():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        page.goto(f"file://{base_dir}/index.html")

        # We can evaluate the toggling in browser context to avoid IPC overhead
        duration = page.evaluate('''() => {
            const start = performance.now();
            const btnEn = document.querySelector("button[data-lang='en']");
            const btnZh = document.querySelector("button[data-lang='zh']");
            for (let i = 0; i < 100; i++) {
                btnEn.click();
                btnZh.click();
            }
            return performance.now() - start;
        }''')

        duration_sec = duration / 1000.0
        print(f"\n100 toggle iterations (in-browser) took: {duration_sec:.3f} seconds")
        assert duration_sec < 0.5, "Language toggle is too slow"
        browser.close()

def test_animation_frame_rate():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        page.goto(f"file://{base_dir}/index.html")

        # Measure FPS over 1 second
        fps = page.evaluate('''() => {
            return new Promise(resolve => {
                let frames = 0;
                let start = performance.now();
                function tick(now) {
                    frames++;
                    if (now - start >= 1000) {
                        resolve(frames);
                    } else {
                        requestAnimationFrame(tick);
                    }
                }
                requestAnimationFrame(tick);
            });
        }''')

        print(f"\nMeasured FPS: {fps}")
        assert fps >= 30, "Frame rate is too low"
        browser.close()
