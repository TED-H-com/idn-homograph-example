# IDN Homograph Attack Awareness Demo

**English** · [繁體中文](README.zh-TW.md)

A single-page, bilingual demo for showing coworkers how an IDN homograph attack hides a fake domain behind a familiar spelling.

**Project page:** https://ted-h-com.github.io/idn-homograph-example/

**Live demo:** https://project-9ogsa.vercel.app

The whole demo is one static `index.html` with a 中文 / English toggle, written in April 2026 as a SOC study note. It opens with a question (which of these two links is fake?), walks through a seven-step phishing kill chain based on [BBC reporting](https://www.bbc.com/news/articles/cly00jnnxypo) on Booking.com "reservation hijack" scams, explains why the Latin and Cyrillic letters look identical, and ends with a defense checklist.

The example brand, Example Bank, is fictional. Its real domain, `examplebank.example`, and the lookalike (the first a swapped for a Cyrillic а, which the browser turns into `xn--exmplebank-0qi.example`) both sit under `.example`, a top-level domain that RFC 2606 reserves for examples, so nobody can register either one.

## Preview locally

Open `index.html` in a browser, or serve the folder:

```bash
git clone https://github.com/TED-H-com/idn-homograph-example
cd idn-homograph-example
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploy your own copy

For coworkers who want to rebuild this demo from the template. There is no build step: Vercel serves `index.html` as is, and `vercel.json` adds the response headers.

### Option A: Vercel CLI (about two minutes)

```bash
# install the CLI if you do not have it yet
npm install -g vercel

# from the project folder
cd idn-homograph-example
vercel
```

The first run asks a few setup questions; the defaults are fine. When it finishes you get a `https://<project>.vercel.app` URL. The first deployment of a new project always goes to production. After that, `vercel` creates a preview deployment and `vercel --prod` updates production.

### Option B: import from GitHub (for ongoing updates)

1. Push this folder to a GitHub repository.
2. Go to https://vercel.com/new
3. Import that repository.
4. Set Framework Preset to **Other** (it is a plain static site).
5. Leave Build Command and Output Directory empty.
6. Click Deploy. Later pushes to the production branch redeploy automatically.

### Option C: drag and drop (simplest, for a one-off)

1. Go to https://vercel.com/drop
2. Drag the project folder, or a `.zip` of it, onto the page.

## Files

```
idn-homograph-example/
├── index.html                  the demo (bilingual, all content and styles inline)
├── vercel.json                 Vercel settings (security headers, clean URLs)
├── site/                       project page for GitHub Pages, generated from site/page.json
├── .github/workflows/pages.yml deploys site/ to GitHub Pages
├── LICENSE                     MIT license
├── README.md                   this file
└── README.zh-TW.md             Traditional Chinese version
```

## How to present it

Suggested flow:

1. **Open the page and ask:** "Which of these two links is fake?" Most people cannot tell, or guess wrong.
2. **Have them click the second link.** The address bar shows an `xn--` Punycode name instead of the familiar spelling.
3. **Explain why:** the Cyrillic а (U+0430) and the Latin a (U+0061) look the same on screen but are different characters.
4. **Connect it to the Booking.com case:** this is how guests in the recent news were tricked.
5. **Close with defenses:** MFA, do not log in or pay from links in messages, and check the root domain at the right end of the address.

## Notes

- Neither link is supposed to load. Both domains are reserved and never resolve, so expect a "site can't be reached" error (or a browser warning on the fake one). That is expected, not a bug: the lesson is in the address bar.
- If the browser shows the `xn--` form even in the link text, its homograph protection is working. That is a good teaching point in itself.
- The page carries a `noindex, nofollow` robots meta tag, and `vercel.json` sends the same `X-Robots-Tag` header, so the deployment stays out of search results. `vercel.json` also sends `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Referrer-Policy: no-referrer`.
- The $2,000 and 580% figures in the kill chain are not in the linked BBC article. Check their sources before you quote them.

## Architecture Notes & Concrete Examples

### Punycode Encoding Explained
Internationalized Domain Names (IDNs) allow domains to contain characters from non-Latin scripts (e.g., Cyrillic, Greek, or Chinese). To make these non-ASCII characters work with the existing DNS infrastructure, they are converted into an ASCII-compatible format called **Punycode**.

When a domain contains non-ASCII characters, it is prefixed with `xn--`. For example, if an attacker registers a lookalike domain using a Cyrillic "а" instead of a Latin "a":
- **Real domain:** `examplebank.example`
- **Lookalike domain:** `exаmplebank.example`
- **Punycode (what the browser connects to):** `xn--exmplebank-0qi.example`

### Sample Confusable Vectors (Homoglyphs)
The attack relies on homoglyphs—characters from different scripts that look identical (or very similar) but have completely different Unicode values. Below are common examples used in IDN homograph attacks:

| Latin Character | Cyrillic Character | Visual Result |
| --------------- | ------------------ | ------------- |
| a (U+0061)      | а (U+0430)         | Identical     |
| c (U+0063)      | с (U+0441)         | Identical     |
| e (U+0065)      | е (U+0435)         | Identical     |
| o (U+006F)      | о (U+043E)         | Identical     |
| p (U+0070)      | р (U+0440)         | Identical     |

### Defensive Strategies
Because a homograph phishing link looks visually identical to the real link, user vigilance alone is rarely enough. A defense-in-depth approach is required:

1. **Root Domain Verification:** Always check the rightmost root domain in the address bar.
2. **Notice `xn--` in the Address Bar:** If you click a familiar-looking link and the address bar changes to an `xn--` URL, the browser's homograph protection is warning you.
3. **Never Log in or Pay from a Message Link:** Instead, open the app, manually type the URL, or use a trusted bookmark. Any message requesting a wire transfer is almost always a scam.
4. **Multi-Factor Authentication (MFA):** Use robust MFA solutions like FIDO2 or passkeys. They actively resist credential phishing, meaning a stolen password alone isn't enough to compromise the account.
5. **Keep Browsers Updated:** Modern browsers (Chrome, Edge, Firefox) have built-in IDN display policies that detect homographs. Staying current keeps these checks working.
6. **Enterprise Controls:** Security teams should use defensive domain registration, implement DMARC/SPF/DKIM, monitor DNS for newly registered domains (NRDs), and actively scan for brand lookalikes using tools like `dnstwist`.

## Customize

- **Example brand and domains:** the fictional brand name (Example Bank) appears in the page title, the header, the note under the demo links, and the footer. The real and lookalike domains appear in both demo links (link text and `href`), the address-bar hint, the "Why can't you spot it?" explanation, the "How attackers weaponize it" list, and the checklist. Search `index.html` for `mplebank`, which matches the real domain, the lookalike, and its `xn--` form, replace every occurrence, then recompute the Punycode form. For example, `python3 -c 'print("exаmplebank.example".encode("idna"))'` (the `а` in that string is Cyrillic) prints `b'xn--exmplebank-0qi.example'`. Keep both names under a reserved top-level domain such as `.example` or `.test` (RFC 2606, RFC 6761). A lookalike under a real top-level domain is a name that anyone could register.
- **Logo:** the `.brand-mark` block holds a small inline SVG (a generic bank icon), so the page loads no external images. Replace the SVG to change it.
- **More lookalike letters:** add rows to the `.char-table` block in the same format (a Latin cell, a Cyrillic cell, then the 一模一樣 / Identical cells).
- **Colors:** edit the CSS variables in `:root` at the top of `index.html`.

## License

MIT, see LICENSE.
