# IDN 同形異義字攻擊教學 Demo

[English](README.md) · **繁體中文**

一個單頁、中英雙語的教學 demo，用來向同事示範 IDN 同形異義字攻擊怎麼把假網域藏在熟悉的拼法後面。

**專案介紹頁：** https://ted-h-com.github.io/idn-homograph-example/?lang=zh-TW

**線上 demo：** https://project-9ogsa.vercel.app

整個 demo 就是一個靜態的 `index.html`，可切換中文 / English，是 2026 年 4 月寫的 SOC 學習筆記。頁面從一個問題開始（下面兩個連結，哪一個是假的？），接著依據 [BBC 的報導](https://www.bbc.com/news/articles/cly00jnnxypo)，把 Booking.com「訂房劫持」詐騙整理成七步釣魚攻擊鏈，再說明拉丁字母和西里爾字母為什麼看起來一模一樣，最後用一份防禦清單收尾。

範例品牌 Example Bank 是虛構的。它的正牌網域 `examplebank.example` 和仿冒網域（把第一個 a 換成西里爾字母 а，瀏覽器會轉成 `xn--exmplebank-0qi.example`）都在 `.example` 底下。這是 RFC 2606 保留給文件範例使用的頂級網域，任何人都無法註冊。

## 本機預覽

直接用瀏覽器打開 `index.html` 就能看，或啟動一個簡單的本機伺服器：

```bash
git clone https://github.com/TED-H-com/idn-homograph-example
cd idn-homograph-example
python3 -m http.server 8000
# 然後打開 http://localhost:8000
```

## 部署自己的版本

給想用這個範本重建 demo 的同事。這個專案不需要建置：Vercel 直接提供 `index.html`，`vercel.json` 負責加上回應標頭。

### 方法 A：Vercel CLI（約 2 分鐘）

```bash
# 安裝 CLI（如果還沒裝）
npm install -g vercel

# 在專案資料夾裡
cd idn-homograph-example
vercel
```

第一次執行會問幾個設定問題，全部用預設值就好。部署完會給你一個 `https://<專案名稱>.vercel.app` 網址。新專案的第一次部署一定會直接上正式環境；之後執行 `vercel` 只會產生預覽版，要更新正式版請用 `vercel --prod`。

### 方法 B：從 GitHub 匯入（適合之後要持續更新）

1. 把這個資料夾推到一個 GitHub repo。
2. 到 https://vercel.com/new
3. 匯入（Import）那個 repo。
4. Framework Preset 選 **Other**（因為是純靜態網站）。
5. Build Command 與 Output Directory 都留空。
6. 按 Deploy。之後推送到正式分支，就會自動重新部署。

### 方法 C：拖拉上傳（最簡單，適合一次性）

1. 到 https://vercel.com/drop
2. 把專案資料夾，或壓好的 `.zip`，直接拖進頁面。

## 檔案結構

```
idn-homograph-example/
├── index.html                  demo 主頁面（中英雙語，內容與樣式都在同一個檔案）
├── vercel.json                 Vercel 設定（安全標頭、clean URLs）
├── site/                       GitHub Pages 專案介紹頁，由 site/page.json 產生
├── .github/workflows/pages.yml 把 site/ 部署到 GitHub Pages
├── LICENSE                     MIT 授權條款
├── README.md                   英文說明
└── README.zh-TW.md             這份文件
```

## 給同事看的時候怎麼講

建議流程：

1. **打開頁面，直接問：**「下面這兩個連結，哪一個是假的？」大部分的人答不出來，或是猜錯。
2. **請他們點第二個連結。** 網址列會變成 `xn--` 開頭的 Punycode 名稱，而不是熟悉的拼法。
3. **解釋原理：** 西里爾字母 а（U+0430）和拉丁字母 a（U+0061）在螢幕上看起來一樣，其實是不同的字元。
4. **連回 Booking.com 詐騙案例：** 近期新聞裡的房客，就是被這類手法騙的。
5. **收尾講防禦：** 啟用 MFA、不從訊息裡的連結登入或付款、檢查網址最右邊的根網域。

## 注意事項

- 兩個連結本來就都不會正常開啟。兩個網域都是保留網域，永遠不會解析，所以會看到「無法連上這個網站」的錯誤頁（假連結也可能被瀏覽器警告擋下）。這是**預期行為**，不是 bug，重點在網址列。
- 如果瀏覽器連顯示的連結文字都變成 `xn--` 形式，表示它的同形字防護正在運作，這本身就是一個很好的教學點。
- 頁面有 `noindex, nofollow` 的 robots meta 標籤，`vercel.json` 也會送出同樣的 `X-Robots-Tag` 標頭，所以不會被搜尋引擎收錄。`vercel.json` 另外還會送出 `X-Content-Type-Options: nosniff`、`X-Frame-Options: DENY` 與 `Referrer-Policy: no-referrer`。
- 攻擊鏈裡的 2,000 美元與 580% 這兩個數字，不在所附的 BBC 文章裡。引用前請先確認出處。

## 架構筆記與具體範例

### Punycode 解析程序
國際化網域名稱（IDNs）允許網域包含非拉丁語系的字元（例如西里爾字母、希臘字母或中文字）。為了讓這些非 ASCII 字元能在現有的 DNS 架構下運作，它們會被轉換成一種稱為 **Punycode** 的 ASCII 相容格式。這個解析程序由 **IDNA2008** 標準規範，定義了 Unicode 字串如何透過 **ToASCII** 轉換程序處理並對應到 ASCII。

當網域包含非 ASCII 字元時，ToASCII 轉換會輸出一串以 `xn--` 開頭的字串。舉例來說，如果攻擊者註冊了一個仿冒網域，用西里爾字母的「а」取代拉丁字母的「a」：
- **正牌網域：** `examplebank.example`
- **仿冒網域：** `exаmplebank.example`
- **Punycode（瀏覽器實際連線的對象）：** `xn--exmplebank-0qi.example`

### Unicode 同形字混淆分類
這種攻擊依賴的是同形字（homoglyphs）——來自不同語系、看起來一模一樣（或非常相似）但 Unicode 碼位完全不同的字元。Unicode 聯盟將這些容易混淆的字元分為三大類：
- **全同文混淆 (Whole-Script Confusables)：** 整個網域都使用單一語系（例如西里爾字母），但看起來跟另一個語系（例如拉丁字母）的網域一模一樣。例如完全用西里爾字母註冊的 `epic.com`。
- **混雜同文混淆 (Mixed-Script Confusables)：** 在同一個網域中混用不同語系的字元（例如把其中一個拉丁字母 'a' 換成西里爾字母 'а'）。這是高度針對性釣魚攻擊（如本 demo）中最常見的手法。
- **同語系內混淆 (Same-Script Confusables)：** 同一個語系內看起來相似的字元（例如拉丁字母的 'l' 和 '1'，或是 'O' 和 '0'）。

以下是 IDN 同形異義字攻擊中常見的**混雜同文**混淆範例：

| 拉丁字母 | 西里爾字母 | 視覺結果 |
| -------- | ---------- | -------- |
| a (U+0061) | а (U+0430) | 一模一樣 |
| c (U+0063) | с (U+0441) | 一模一樣 |
| e (U+0065) | е (U+0435) | 一模一樣 |
| o (U+006F) | о (U+043E) | 一模一樣 |
| p (U+0070) | р (U+0440) | 一模一樣 |

### 瀏覽器顯示防禦機制
現代瀏覽器（Chrome, Firefox, Safari, Edge）採用複雜的 **IDN 顯示演算法 (IDN display algorithms)**，來決定網址列要顯示 Unicode 字元還是原始的 `xn--` Punycode。其目的是當網域看起來可疑時，退回顯示 Punycode 以防範同形字攻擊。

關鍵的防禦檢查包括：
- **允許語系清單 (Allowed Script Lists)：** 瀏覽器只會針對被認定為「安全」或符合使用者地區設定的語系顯示 Unicode。
- **混合語系檢查 (Script Mixing Checks)：** 瀏覽器會嚴格管制或直接封鎖那些以非自然人類語言方式混合語系的網域（例如在同一個網域標籤中混用西里爾字母和拉丁字母）。如果偵測到違規的語系混合，瀏覽器就會強制顯示 `xn--` Punycode，讓偽裝無所遁形。

### 防禦策略
因為同形字釣魚連結在視覺上跟真正的連結一模一樣，單靠使用者的警覺性是不夠的，必須採取深度防禦（Defense-in-depth）：

1. **檢查根網域：** 永遠檢查網址列最右邊的根網域。
2. **注意網址列的 `xn--`：** 如果你點了一個看起來很熟悉的連結，但網址列卻變成了 `xn--` 開頭的網址，這表示瀏覽器的同形字防護正在警告你。
3. **不要從訊息裡的連結登入或付款：** 自己打開 App、手動輸入網址，或是使用書籤。任何要求銀行轉帳的訊息，幾乎都是詐騙。
4. **多因素驗證 (MFA)：** 採用如 FIDO2 或 passkeys 等強大的 MFA 解決方案，它們能有效抵擋憑證釣魚，也就是說，即使密碼被盜也不會導致帳號被駭。
5. **保持瀏覽器更新：** 現代瀏覽器（Chrome, Edge, Firefox）都內建了 IDN 顯示政策來偵測同形字。保持更新才能確保這些檢查機制持續有效。
6. **企業層級的控管：** 資安團隊應採取防禦性網域註冊、實作 DMARC/SPF/DKIM、監控 DNS 中新註冊的網域（NRDs），並利用 `dnstwist` 等工具主動掃描自家品牌的仿冒網域。

## 自訂

- **範例品牌與網域：** 虛構品牌名稱（Example Bank）出現在頁面標題、頁首、demo 連結下方的說明和頁尾。正牌網域和仿冒網域則寫死在兩個 demo 連結（連結文字與 `href`）、網址列提示、「為什麼肉眼看不出來？」的說明、「攻擊者實際怎麼用」清單和防禦清單裡。在 `index.html` 裡搜尋 `mplebank`（正牌網域、仿冒網域和它的 `xn--` 形式都找得到），全部替換之後，再重新計算 Punycode。例如 `python3 -c 'print("exаmplebank.example".encode("idna"))'`（字串裡的 `а` 是西里爾字母）會印出 `b'xn--exmplebank-0qi.example'`。兩個網域都請放在 `.example` 或 `.test` 這類保留的頂級網域底下（RFC 2606、RFC 6761）。放在真實頂級網域底下的仿冒網域，任何人都能註冊。
- **Logo：** `.brand-mark` 區塊裡是一個內嵌的小 SVG（通用的銀行圖示），頁面不會從外部載入任何圖片。要換 Logo，直接替換這段 SVG。
- **更多相似字母：** 在 `.char-table` 區塊照原本的格式加一列（拉丁字母一格、西里爾字母一格，再加「一模一樣 / Identical」兩格）。
- **配色：** 修改 `index.html` 最上面 `:root` 裡的 CSS 變數。

## 授權

MIT，詳見 LICENSE。
