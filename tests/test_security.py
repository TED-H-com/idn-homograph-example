import unittest
import json
import os
import re

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_vercel_secure_headers(self):
        """Test that vercel.json contains the required secure headers."""
        vercel_path = os.path.join(self.base_dir, 'vercel.json')
        self.assertTrue(os.path.exists(vercel_path), "vercel.json not found")

        with open(vercel_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        self.assertIn('headers', config, "No headers configured in vercel.json")
        headers_config = config['headers'][0]['headers']

        header_keys = [h['key'] for h in headers_config]

        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'Referrer-Policy',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]

        for required in required_headers:
            self.assertIn(required, header_keys, f"Required secure header {required} is missing")

        # Verify specific header values
        for h in headers_config:
            if h['key'] == 'X-Content-Type-Options':
                self.assertEqual(h['value'], 'nosniff')
            elif h['key'] == 'X-Frame-Options':
                self.assertEqual(h['value'], 'DENY')
            elif h['key'] == 'Referrer-Policy':
                self.assertEqual(h['value'], 'no-referrer')

    def test_no_sensitive_credentials(self):
        """Test that no sensitive credentials (keys, tokens, secrets) are hardcoded."""
        # Simple regex for finding potential hardcoded secrets
        # Looking for things like api_key = "...", token: '...', secret="xxx"
        secret_pattern = re.compile(
            r'(?:api_key|apikey|secret|token|password)[\s]*[:=][\s]*["\'](?!.*(passkey|example|false|true|null|undefined))(.*?)["\']',
            re.IGNORECASE
        )

        # Files to exclude from the scan (like this test file itself)
        exclude_files = ['test_security.py']
        exclude_dirs = ['.git', '.github', 'tests', '__pycache__', 'env', 'venv']

        found_secrets = []

        for root, dirs, files in os.walk(self.base_dir):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file in exclude_files or file.endswith('.png') or file.endswith('.svg'):
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = secret_pattern.findall(content)
                        if matches:
                            found_secrets.append(f"Potential secret found in {file_path}")
                except UnicodeDecodeError:
                    # Skip binary files or files that can't be read as utf-8
                    pass

        self.assertEqual(len(found_secrets), 0, f"Sensitive credentials found:\n" + "\n".join(found_secrets))

    def test_no_dangerous_js_patterns(self):
        """Test that JavaScript files do not use dangerous functions like eval or unsanitized innerHTML."""
        dangerous_patterns = [
            (re.compile(r'\beval\s*\('), 'eval() used'),
            (re.compile(r'\bdocument\.write\s*\('), 'document.write() used'),
            (re.compile(r'\bsetTimeout\s*\(\s*["\']'), 'setTimeout with string (eval-like) used'),
            (re.compile(r'\bsetInterval\s*\(\s*["\']'), 'setInterval with string (eval-like) used'),
        ]

        # known safe usages, like the one in flow.js where ICONS[name] is used
        inner_html_pattern = re.compile(r'\.innerHTML\s*=')

        js_files = []
        for root, dirs, files in os.walk(self.base_dir):
            if '.git' in root or 'node_modules' in root:
                continue
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.join(root, file))

        for file_path in js_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                for pattern, message in dangerous_patterns:
                    self.assertFalse(pattern.search(content), f"{message} found in {file_path}")

                # Check innerHTML
                for i, line in enumerate(content.splitlines()):
                    if inner_html_pattern.search(line):
                        # Allow known safe ICONS lookup in flow.js
                        if "g.innerHTML = ICONS[name] || ICONS.hub;" in line:
                            continue
                        self.fail(f"Unsanitized innerHTML assignment found in {file_path} at line {i+1}:\n{line}")

    def test_parameter_validation(self):
        """Test that URL parameters are safely parsed and validated (no direct DOM injection)."""
        # Ensure that location.search is handled safely, e.g. using URLSearchParams
        url_search_pattern = re.compile(r'location\.search')
        url_search_params = re.compile(r'URLSearchParams')

        js_files = []
        for root, dirs, files in os.walk(self.base_dir):
            if '.git' in root or 'node_modules' in root:
                continue
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.join(root, file))

        for file_path in js_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if url_search_pattern.search(content):
                    self.assertTrue(
                        url_search_params.search(content),
                        f"Unsafe URL parameter parsing found in {file_path}. Use URLSearchParams instead."
                    )


if __name__ == '__main__':
    unittest.main()
