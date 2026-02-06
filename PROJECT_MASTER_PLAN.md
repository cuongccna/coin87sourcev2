### 🏛 Giai đoạn 1: Hệ thống Crawl đa nguồn & Quản lý Database

Mục tiêu: Xây dựng một "Cỗ máy" rỗng nhưng có thể lắp ráp bất kỳ "động cơ" (nguồn tin) nào vào sau này mà không cần sửa code lõi.

#### 🛠 Task 1.1: Thiết kế Database & Quản lý cấu hình (The Foundation)

**Mục đích:** Tạo nơi lưu trữ linh hoạt. Quan trọng nhất là bảng `Source` phải có cột `config` dạng JSON để chúng ta có thể thay đổi URL, API Key của nguồn tin ngay trong Database mà không cần redeploy code.

**Prompt 1.1 (Copy vào AI Copilot):**

```text
Role: Senior Backend Engineer (Python/SQLAlchemy Specialist).
Context: Starting the "Coin87" project - a crypto news aggregator.
Task: Set up the Database Schema using SQLAlchemy (Async) and PostgreSQL.

Requirements:
1. Setup: Use `python-dotenv` to load `DATABASE_URL` from .env file. Create a `DatabaseSession` manager class.
2. Define Models:
   - `Source` table:
     - id: Integer (Primary Key)
     - name: String (e.g., "CoinTelegraph RSS")
     - source_type: Enum ("rss", "twitter", "api", "telegram")
     - config: JSONB (CRITICAL: specific configs like {"rss_url": "..."} or {"api_key": "..."})
     - is_active: Boolean (default True)
     - trust_score: Float (default 5.0)
     - created_at: DateTime
   - `News` table:
     - id: Integer (Primary Key)
     - source_id: ForeignKey to Source.id
     - title: String
     - url: String (Unique Index - to prevent duplicates)
     - raw_content: Text
     - published_at: DateTime
     - created_at: DateTime (default Now)
3. Migration Script: Provide a script to initialize these tables in the DB.
4. Constraint: No mock data. Strictly strict typing.

```

---

#### ⚙️ Task 1.2: Xây dựng Kiến trúc Plugin (The Abstract Engine)

**Mục đích:** Áp dụng Design Pattern (Factory/Strategy). Chúng ta cần một class cha (`BaseCrawler`) quy định luật chơi. Mọi nguồn tin sau này (RSS, Telegram...) đều phải tuân thủ luật này. Điều này giúp dự án dễ dàng mở rộng (Scalable).

**Prompt 1.2 (Copy vào AI Copilot):**

```text
Role: Software Architect.
Context: Building the crawler engine for Coin87 based on the DB models created in Task 1.1.
Task: Implement the Abstract Plugin Architecture.

Requirements:
1. Create an abstract base class `BaseCrawler` (in `crawlers/base.py`).
   - Must have an abstract method `async def fetch_data(self) -> List[dict]:`
   - Must have an `__init__` that accepts the `config` dictionary from the Source model.
2. Create a `CrawlerFactory` class.
   - It should have a method `get_crawler(source_type: str, config: dict) -> BaseCrawler`.
   - Logic: If source_type is 'rss', return an instance of RSSCrawler (we will implement this next). If 'twitter', raise NotImplementedError for now.
3. Architecture: The goal is to allow the main system to loop through active Sources from DB, call `CrawlerFactory.get_crawler()`, and then call `.fetch_data()` without knowing the specific implementation details.
4. Constraint: Use `abc` module for abstract classes. Focus on clean, extensible code structure.

```

---

#### 🔌 Task 1.3: Thực thi Plugin RSS & Chạy Test (The First Spark)

**Mục đích:** Hiện thực hóa con bot đầu tiên. RSS là nguồn free, dễ nhất, chúng ta làm trước để test luồng dữ liệu từ: **Web -> Parser -> Database**.

**Prompt 1.3 (Copy vào AI Copilot):**

```text
Role: Python Developer.
Context: Implementing the specific RSS logic for Coin87.
Task: Implement the RSSCrawler and the Main Execution Loop.

Requirements:
1. Implement `RSSCrawler` class inheriting from `BaseCrawler`.
   - Use `feedparser` library (run in an executor if it's blocking) or an async alternative to fetch data from the URL found in `config['rss_url']`.
   - Return a list of dictionaries with keys: `title`, `url`, `published_at`, `raw_content`.
2. Create `main_crawler.py`:
   - Connect to DB.
   - Query all `Source` where `is_active=True`.
   - Loop through sources:
     - Instantiate the crawler via `CrawlerFactory`.
     - `await crawler.fetch_data()`.
     - Save new items to the `News` table.
     - CRITICAL: Handle duplicates. Check if `url` exists in DB before inserting. Use `upsert` or simple `exist` check.
   - Log the process (e.g., "Fetched 5 new items from CoinTelegraph").
3. Constraint: No hardcoded URLs. Create a seeder script to insert one sample RSS source (e.g., Coindesk) into the `Source` table for testing.

```

---

### ✅ Checklist kiểm thử cho Giai đoạn 1 (Sau khi xong Task 1.3)

1. **DB Check:** Mở PostgreSQL, bảng `Source` đã có dòng dữ liệu cấu hình RSS chưa?
2. **Duplicate Check:** Chạy script `main_crawler.py` 2 lần liên tiếp. Lần 2 **không** được phép insert thêm dòng nào vào bảng `News` (vì tin đã tồn tại).
3. **Flexibility Check:** Thử vào DB sửa cột `config` của nguồn đó sang một URL RSS khác (ví dụ từ Coindesk sang CoinTelegraph). Chạy lại script. Nếu nó lấy được tin mới từ nguồn mới mà không cần sửa code => **Bạn đã thành công.**

========================================================================================================================================

---

### 🛠 Task 1.4: Bộ vệ sinh dữ liệu & Bộ lọc thô (The Janitor & Gatekeeper)

**Mục đích:**

1. **Vệ sinh (Sanitize):** Loại bỏ HTML tags, script, quảng cáo, khoảng trắng thừa.
2. **Lọc thô (Hard Filter):** Loại bỏ tin dựa trên quy tắc cứng (Rule-based). Ví dụ: Nội dung quá ngắn (< 20 từ), chứa từ khóa cấm (Casino, Betting, Terms of Service), hoặc thiếu tiêu đề.

**Prompt 1.4 (Copy vào AI Copilot):**

```text
Role: Python Backend Developer.
Context: Enhancing the Crawler engine for Coin87. We need a pre-processing layer to save AI costs.
Task: Implement a `ContentProcessor` utility class.

Requirements:
1. Libraries: Use `BeautifulSoup` (bs4) for HTML stripping and standard `re` (regex).
2. Create `clean_text(html_content: str) -> str`:
   - Remove all HTML tags, `<script>`, `<style>`.
   - Collapse multiple spaces/newlines into single ones.
   - Trim leading/trailing whitespace.
3. Create `is_valid_candidate(title: str, content: str) -> bool`:
   - Return False if content length is < 50 words (Too short to be news).
   - Return False if title contains blacklisted keywords (Load from a predefined list e.g., ["Login", "Subscribe", "Privacy Policy", "Casino"]).
   - Return False if title is all uppercase or has excessive special characters (Spam detection).
4. Integration: Update the `RSSCrawler` (from Task 1.3) to utilize this `ContentProcessor` BEFORE returning data. If `is_valid_candidate` is False, discard the item immediately.
5. Constraint: Pure logic, highly optimized for speed. No external API calls here.

```

---

### 🔍 Task 1.5: Chống trùng lặp nội dung mờ (Fuzzy Deduplication)

**Mục đích:**
URL khác nhau chưa chắc nội dung khác nhau (do các trang copy lại của nhau). Để tránh lưu 2 bản tin giống hệt nhau (tốn bộ nhớ và gây khó chịu cho user), chúng ta cần so sánh độ tương đồng của Tiêu đề/Nội dung.

* Nếu Tin A giống Tin B > 85% => Bỏ qua.

**Prompt 1.5 (Copy vào AI Copilot):**

```text
Role: Python Data Engineer.
Context: Preventing duplicate content in Coin87 to ensure uniqueness and save storage.
Task: Implement a Fuzzy Deduplication Service.

Requirements:
1. Library: Use `thefuzz` (formerly fuzzywuzzy) or Python's built-in `difflib`.
2. Logic: Create a service `DuplicateChecker`.
   - Method `is_duplicate(new_title: str, session: AsyncSession) -> bool`:
   - Logic: Query the last 50 news titles from the `News` table (published within the last 24h).
   - Compare `new_title` against these 50 titles using Levenshtein Distance (Token Set Ratio).
   - Threshold: If similarity score > 85, consider it a duplicate and return True.
3. Integration: Integrate this check into the `main_crawler.py` loop.
   - Step 1: Check exact URL match (Task 1.3).
   - Step 2: Check Content Validity (Task 1.4).
   - Step 3: Check Fuzzy Duplicate (Task 1.5).
   - Only if all pass => Insert into DB.
4. Constraint: Optimize query to only fetch `title` column for comparison, not the whole content (for performance).

```

---

### ✅ Quy trình xử lý dữ liệu mới (Pipeline)

Sau khi thêm 2 task này, luồng dữ liệu của bạn sẽ chặt chẽ như sau:

1. **Fetch:** Tải dữ liệu từ RSS.
2. **Cleaner (Task 1.4):** Lột sạch HTML, đưa về text thuần.
3. **Gatekeeper (Task 1.4):**
* *Nội dung < 50 từ?* => **VỨT**.
* *Tiêu đề chứa "Cá độ"?* => **VỨT**.


4. **Deduplicator (Task 1.5):**
* *Đã có bài viết tương tự 90% trong DB chưa?* => Có => **VỨT**.


5. **Save DB:** Lưu dữ liệu sạch.
6. **AI Analysis:** (Giai đoạn sau) Chỉ chạy trên những tin đã sống sót qua 5 bước trên.

### 🧪 Test Case bổ sung cho Task 1.4 & 1.5

1. **Test Filter Ngắn:** Tạo một RSS item giả chỉ có dòng chữ "Click here to read more". Hệ thống phải **tự động loại bỏ**, không lưu vào DB.
2. **Test Filter Keyword:** Tạo item có tiêu đề "Policy Update". Hệ thống phải loại bỏ.
3. **Test Trùng lặp:**
* Insert tin A: "Bitcoin đạt mốc 100k USD".
* Thử insert tin B: "Bitcoin vừa chạm mốc 100.000 đô la".
* Hệ thống `FuzzyLogic` phải nhận diện sự tương đồng và **từ chối** tin B.


=============================================================================================================================


1. **Gán nhãn (Tagging):** Biết ngay bài viết nói về đồng nào (BTC, ETH, SOL...).
2. **Lọc nhiễu (Noise Filtering):** Nếu nguồn là trang tài chính tổng hợp (như Bloomberg/Forbes) mà bài viết nói về "Giá gạo xuất khẩu" -> Loại bỏ ngay, không cho vào DB.

Chúng ta sẽ thêm **Task 1.6** vào Giai đoạn 1.

---

### 🏷️ Task 1.6: Bộ phân loại từ khóa & Gán nhãn tài sản (The Tagger)

**Mục đích:**
Sử dụng một bộ từ điển (Dictionary/Taxonomy) đã định nghĩa trước để quét Tiêu đề và Nội dung.

* **Input:** "Ethereum vừa nâng cấp Dencun giúp giảm phí gas."
* **Output:**
* **Coins:** `['ETH']`
* **Topic:** `['Upgrade', 'Layer2']`
* **Decision:** Giữ lại (vì có từ khóa Crypto).



**Prompt 1.6 (Copy vào AI Copilot):**

```text
Role: Python Data Engineer (NLP Focus).
Context: Coin87 needs a cost-effective way to tag news and filter out non-crypto noise BEFORE AI processing.
Task: Implement a `KeywordTagger` service and update the Database Model.

Requirements:
1. Database Update:
   - Update `News` table (defined in Task 1.1) to add a column `tags` (type: ARRAY of Strings or JSONB) and `topic_category` (String).
   - Create a migration script for this change.

2. Taxonomy Structure (Define in a separate file `taxonomy.py`):
   - Create a dictionary mapping coins to keywords.
     Example: `{'BTC': ['bitcoin', 'btc', 'satoshi'], 'ETH': ['ethereum', 'eth', 'vitalik'], 'SOL': ['solana', 'sol']}`.
   - Create a dictionary for topics.
     Example: `{'DeFi': ['defi', 'dex', 'swap', 'staking'], 'Regulation': ['sec', 'ban', 'law', 'regulation'], 'Macro': ['fed', 'cpi', 'inflation']}`.

3. Logic Implementation (`services/tagger.py`):
   - Class `KeywordTagger`:
     - Method `extract_tags(text: str) -> list`: Scans text (title + content) against the taxonomy. Returns list of found coins (e.g., ['BTC', 'ETH']).
     - Method `is_relevant(text: str) -> bool`: Returns True if ANY crypto-related keyword is found.
   
4. Integration:
   - Update `main_crawler.py`. After `ContentProcessor` (Task 1.4) and `DuplicateChecker` (Task 1.5):
   - Run `tagger.is_relevant(text)`. If False -> Discard (Log as "Irrelevant Noise").
   - If True -> Run `tagger.extract_tags(text)` -> Save these tags into the `News.tags` column in DB.

5. Constraint: Case-insensitive matching. Use fast string matching (or compiled regex for performance). 

```

---

### 🔄 Quy trình xử lý dữ liệu hoàn chỉnh (Giai đoạn 1)

Với việc bổ sung Task 1.6, luồng dữ liệu của bạn đã trở nên rất chuyên nghiệp và tối ưu chi phí:

1. **Crawl (Task 1.3):** Lấy tin về.
2. **Clean (Task 1.4):** Xóa HTML, lọc tin rác (ngắn, keywords cấm).
3. **Deduplicate (Task 1.5):** Kiểm tra xem tin này đã có chưa (tránh trùng lặp).
4. **Tag & Filter Noise (Task 1.6):**
* *Tin này có nói về Crypto/Coin nào không?*
* Không (VD: Tin về Bất động sản) -> **VỨT**.
* Có (VD: Tin về BTC) -> **Gắn nhãn "BTC"** -> **LƯU DATABASE**.



---

### ✅ Checklist kiểm thử cho Task 1.6

1. **Test Gán nhãn:** Đưa vào một đoạn văn mẫu: *"Solana vượt mặt Ethereum về khối lượng giao dịch DEX"*.
* Kết quả mong đợi trong DB: cột `tags` phải chứa `['SOL', 'ETH']`, cột `topic_category` có thể chứa `['DeFi']`.


2. **Test Lọc nhiễu:** Đưa vào một đoạn văn mẫu từ nguồn tài chính: *"Giá vàng hôm nay tăng nhẹ do căng thẳng địa chính trị"*.
* Kết quả mong đợi: Hệ thống từ chối lưu bài này vì không tìm thấy từ khóa Crypto nào.


===================================================================================================================================


---

### 🛡️ Task 1.7: Cơ chế "Tàng hình" & Quản lý Request (The Stealth Requester)

**Vấn đề:** Các nguồn tin (đặc biệt là các trang lớn) thường chặn các bot. Nếu bạn gửi request liên tục với cùng một `User-Agent` hoặc IP, bạn sẽ bị chặn (Block/Rate Limit) rất nhanh.
**Giải pháp:** Xây dựng một lớp `NetworkClient` thông minh có khả năng giả lập hành vi con người.

**Mục đích:**

1. **Random User-Agent:** Mỗi lần gọi là một định danh khác nhau (Chrome trên Win, Safari trên Mac, v.v.).
2. **Exponential Backoff:** Nếu lỗi mạng, đừng thử lại ngay. Hãy chờ 1s, rồi 2s, rồi 4s... để tránh bị server đích đánh dấu là Spam.
3. **Timeout Management:** Đặt giới hạn thời gian chặt chẽ để thread không bị treo mãi mãi.

**Prompt 1.7 (Copy vào AI Copilot):**

```text
Role: Python Network Engineer.
Context: Building a robust fetching layer for Coin87 crawler to avoid being blocked by target servers.
Task: Implement a `SmartRequestClient` using `httpx` and `tenacity`.

Requirements:
1. Libraries: `httpx` (async), `tenacity` (for retry logic), `fake-useragent`.
2. Implementation (`utils/network.py`):
   - Create a singleton `SmartClient`.
   - Method `get(url: str, params: dict = None) -> Response`.
   - Logic:
     - Automatically inject a random `User-Agent` header for every request using `fake-useragent`.
     - Set strict timeouts (e.g., connect=5s, read=10s).
     - Implement Retry logic using `tenacity`:
       - Retry up to 3 times on `ConnectTimeout` or `5xx` errors.
       - Use "Exponential Backoff" (wait 1s, then 2s, then 4s).
       - Do NOT retry on `404` or `403` (Forbidden).
3. Integration: Replace the direct `feedparser` HTTP fetching in `RSSCrawler` (Task 1.3) with this `SmartClient` to fetch the XML content first, then parse string.
4. Constraint: Log every retry attempt to understand network health.

```

---

### ⏱️ Task 1.8: Chuẩn hóa Thời gian & Metadata (The Timekeeper)

**Vấn đề:** Mỗi nguồn tin định dạng ngày tháng khác nhau:

* Nguồn A: `Mon, 27 Jan 2026 14:00:00 GMT`
* Nguồn B: `2026-01-27T14:00:00+07:00`
* Nguồn C: `2 hours ago`
Nếu không quy đổi về một chuẩn duy nhất (UTC), timeline tin tức của bạn sẽ loạn xạ. Tin mới thì nằm dưới, tin cũ lại trồi lên.

**Giải pháp:** Dùng thư viện parser mạnh để ép mọi định dạng về **UTC Timestamp**.

**Prompt 1.8 (Copy vào AI Copilot):**

```text
Role: Python Data Engineer.
Context: Coin87 aggregates news from global sources. Timezones are messy. We need strict time normalization.
Task: Implement a `DateNormalizer` and `MetadataExtractor` service.

Requirements:
1. Library: Use `dateparser` (powerful parsing for human-readable strings) and standard `datetime`.
2. Logic (`services/normalizer.py`):
   - Method `normalize_date(date_str: str) -> datetime`:
     - Must return a standard Python `datetime` object in **UTC timezone**.
     - Handle relative dates (e.g., "10 mins ago") correctly.
     - If date parsing fails, fallback to `datetime.utcnow()` but log a warning "Date parsing failed".
   - Method `extract_author(raw_author: str) -> str`:
     - Clean up author names (remove "By ", remove emails). If empty, return "Unknown".
3. Integration:
   - Update `RSSCrawler`. When extracting data, pass the raw date string through `normalize_date` BEFORE assigning it to the `News` model.
4. Constraint: Ensure the Database `News.published_at` column is timezone-aware (TIMESTAMP WITH TIME ZONE).

```

---

### 🔌 Task 1.9: Circuit Breaker & Giám sát sức khỏe nguồn tin (The Health Monitor)

**Vấn đề:** Nếu một nguồn tin chết (URL thay đổi, server sập), Crawler vẫn cứ cố lao đầu vào lấy tin mỗi 15 phút. Điều này lãng phí tài nguyên và làm rác log file lỗi.
**Giải pháp:** Cơ chế "Cầu dao điện" (Circuit Breaker).

**Mục đích:**

* Nếu 1 nguồn lỗi liên tiếp 5 lần -> Tạm ngắt (Set `is_active=False` hoặc trạng thái `Cooldown`).
* Gửi cảnh báo (Log error) để Admin biết mà sửa link.

**Prompt 1.9 (Copy vào AI Copilot):**

```text
Role: Senior Backend Engineer.
Context: Optimizing crawler efficiency. We need to stop crawling broken sources automatically.
Task: Implement a `SourceHealthMonitor` (Circuit Breaker pattern).

Requirements:
1. Database Update:
   - Add columns to `Source` table: `consecutive_failures` (int, default 0), `last_error_log` (Text).
2. Logic Update in `main_crawler.py`:
   - Wrap the fetching process in a Try/Except block.
   - **On Success:**
     - Reset `consecutive_failures` to 0.
   - **On Failure (Exception):**
     - Increment `consecutive_failures` += 1.
     - Update `last_error_log` with the exception message.
     - **Circuit Breaker Rule:** If `consecutive_failures` >= 5:
       - Set `is_active` = False.
       - Log "Source {name} disabled due to too many failures."
3. Constraint: Do not stop the entire loop if one source fails. The show must go on for other sources.

```

---

### 📊 Tổng kết Giai đoạn 1 (Hoàn chỉnh)

Với việc bổ sung 3 task này, kiến trúc Giai đoạn 1 của bạn đã đạt chuẩn Production:

1. **Task 1.1 - 1.3:** Khung sườn, DB, Crawler cơ bản.
2. **Task 1.4 - 1.5:** Lọc rác thô, chống trùng lặp (Logic nội dung).
3. **Task 1.6:** Phân loại, gán nhãn Topic/Coin (Logic nghiệp vụ).
4. **Task 1.7:** Fake User-Agent, Retry thông minh (Logic mạng).
5. **Task 1.8:** Chuẩn hóa thời gian UTC (Logic dữ liệu).
6. **Task 1.9:** Tự động ngắt nguồn hỏng (Logic vận hành).

### ✅ Test Case bổ sung cho 3 Task mới

| ID | Quy trình Test | Kết quả mong đợi |
| --- | --- | --- |
| **TC 1.7** | Chặn mạng (Simulate Network Fail) | Hệ thống phải thử lại (Retry) 3 lần, mỗi lần cách nhau lâu hơn, sau đó mới báo lỗi. Không được crash. |
| **TC 1.8** | Test Múi giờ | Đưa vào 2 bài viết: Bài A (`10:00 +07:00`) và Bài B (`04:00 UTC`). Hệ thống phải hiểu 2 mốc này là **bằng nhau** và lưu vào DB cùng giá trị UTC. |
| **TC 1.9** | Test Nguồn chết | Cố tình sửa URL của một nguồn thành link sai (404). Chạy Crawler 5 lần. Sau lần thứ 5, vào DB kiểm tra cột `is_active` của nguồn đó phải chuyển sang `False`. |


=====================================================================================================================================


Hầu hết RSS miễn phí chỉ cho bạn 2-3 dòng mô tả (Teaser) và yêu cầu người dùng "Click to read more". Nếu bạn chỉ ném 3 dòng này cho AI, nó sẽ **không đủ dữ kiện** để đánh giá đây là Scam hay Bullish, dẫn đến việc bạn tốn tiền AI mà kết quả hời hợt.

Chúng ta cần một **"Thợ lặn"** để lặn vào trang gốc và lôi toàn bộ nội dung + ảnh đại diện về.

---

### 🎨 Task 1.10: Trình làm giàu nội dung & Trích xuất Ảnh (The Enricher)

**Mục đích:**

1. **Full Text Extraction:** Biến đoạn tin ngắn cũn cỡn từ RSS thành bài viết đầy đủ. AI cần ngữ cảnh đầy đủ để "bắt bài" cá voi hoặc phát hiện lừa đảo.
2. **Thumbnail Extraction:** Lấy URL ảnh đại diện (OG Image) để hiển thị lên App cho đẹp (App tin tức mà không có ảnh thì user sẽ chán ngay).

**Công nghệ:** Sử dụng thư viện `trafilatura` (Hiện đang là thư viện tốt nhất, nhanh và nhẹ hơn `newspaper3k` để cào nội dung chính của bài báo, bỏ qua menu/footer/quảng cáo).

**Prompt 1.10 (Copy vào AI Copilot):**

```text
Role: Python Data Engineer.
Context: Free RSS feeds often truncate content. To maximize AI analysis value and UI appeal, we need full text and images.
Task: Implement a `ContentEnricher` service using `trafilatura`.

Requirements:
1. Library: `trafilatura` (for efficient main text/image extraction).
2. Database Update:
   - Add column `image_url` (String) to `News` table.
   - Add column `is_full_content` (Boolean, default False) to `News` table.
3. Logic (`services/enricher.py`):
   - Method `enrich_news(url: str, html: str = None) -> dict`:
     - If `html` is provided (from Task 1.3), use `trafilatura.extract(html)`.
     - If not, use `trafilatura.fetch_url(url)` then extract.
     - Extract `main_text` and `image_url` (look for <meta property="og:image">).
     - Return `{'full_text': ..., 'image_url': ...}`.
4. Integration Strategy (Smart Enrichment):
   - In `main_crawler.py`: Check the length of `raw_content` from RSS.
   - If length < 500 characters (likely a snippet):
     - Call `enricher.enrich_news(url)`.
     - Update `raw_content` with the full text.
     - Set `is_full_content` = True.
     - Save `image_url` to DB.
   - If length is sufficient, just try to extract the image from the RSS enclosure tags.
5. Constraint: Set a strict timeout (e.g., 3s) for fetching full text. If it fails, keep the original snippet. Don't let one slow site block the pipeline.

```

---

### 🏛 TỔNG KẾT GIAI ĐOẠN 1: PHÁO ĐÀI DỮ LIỆU (THE DATA FORTRESS)

Chúc mừng bạn! Với trọn bộ 10 Task này, bạn không còn xây dựng một "con bot crawl" đơn giản nữa, mà bạn đã thiết kế xong một **Hệ thống xử lý thông tin cấp độ Enterprise**.

Hãy nhìn lại cỗ máy bạn sắp code:

| Tầng (Layer) | Task | Chức năng (Value) |
| --- | --- | --- |
| **Foundation** | 1.1, 1.2 | Database linh hoạt & Kiến trúc Plugin mở rộng. |
| **Ingestion** | 1.3, 1.7 | Lấy tin từ mọi nguồn, tự động fake User-Agent để tránh bị chặn. |
| **Cleaning** | 1.4, 1.8 | Lọc rác HTML, chuẩn hóa giờ giấc UTC (Toàn cầu). |
| **Quality Control** | 1.5, 1.9 | Chống trùng lặp nội dung & Tự ngắt nguồn hỏng. |
| **Intelligence** | 1.6, 1.10 | Phân loại Coin/Topic & Tự động lấy Full bài + Ảnh. |


====================================================================================================================================

**Giai đoạn 2: Bộ lọc AI (The AI Brain)**.

Nếu Giai đoạn 1 là "Tay chân" (thu thập), thì Giai đoạn 2 là "Bộ não". Ở giai đoạn này, sai lầm lớn nhất của các Solo Dev là: **Dùng AI như một công cụ tóm tắt văn bản (Summarizer) thay vì một chuyên gia phân tích (Analyst).**

Người dùng Coin87 không trả tiền để đọc tóm tắt (họ có thể dùng Google Translate). Họ trả tiền để biết:

1. **Sentiment:** Tin này là FUD (Dìm giá) hay FOMO (Đẩy giá)?
2. **Alpha:** Có kèo (opportunity) nào trong này không?
3. **Safety:** Đây có phải là Scam/Rug-pull không?

Dưới đây là 5 Task chuyên sâu để biến Gemini thành một "Crypto Expert" thực thụ, tối ưu chi phí và hiệu năng.

---

### 🧠 Task 2.1: Thiết kế "System Prompt" chuyên dụng cho Crypto (The Persona)

**Mục đích:** Thay vì prompt chung chung "Summarize this", chúng ta phải ép AI đóng vai một **Senior Market Analyst**. Nó phải hiểu thuật ngữ ngành (Liquidity, Airdrop, Mainnet, Rug pull) và trả về định dạng **JSON Strict Mode** để code dễ xử lý.

**Prompt 2.1 (Copy vào AI Copilot):**

```text
Role: Prompt Engineer.
Context: Designing the core system prompt for Coin87's AI analysis engine (powered by Gemini 1.5 Flash).
Task: Create a `PromptBuilder` service.

Requirements:
1. Logic (`services/ai/prompts.py`):
   - Define a constant `SYSTEM_INSTRUCTION`:
     "You are Coin87, a ruthless Senior Crypto Analyst. Your job is to filter noise, identify scams, and find 'Alpha' (trading opportunities). You speak in facts, brief and direct. Never use financial advice disclaimers. Output strictly in JSON."
   - Method `build_analysis_prompt(title: str, content: str, source_trust: float) -> str`:
     - Combine system instruction with the news content.
     - Demand specific JSON fields:
       - `summary` (string, max 2 sentences, focused on market impact).
       - `sentiment` (enum: 'Bullish', 'Bearish', 'Neutral').
       - `category` (enum: 'Tech', 'Regulation', 'Market', 'Scam', 'Community').
       - `impact_score` (int, 1-10).
       - `detected_coins` (list of strings, e.g., ['BTC', 'ETH']).
       - `is_spam_scam` (boolean).
       - `reasoning` (string, why you gave this score).
2. Constraint: The prompt must explicitly forbid "hallucinating" coins that are not mentioned in the text.

```

---

### 🛡️ Task 2.2: Xây dựng AI Client & JSON Guardrails (The Translator)

**Mục đích:** AI đôi khi trả về Markdown, đôi khi trả về Text thường dù đã bảo trả về JSON. Task này xây dựng cơ chế **"Ép kiểu" (Type Enforcement)**. Nếu JSON lỗi, tự động sửa hoặc yêu cầu AI làm lại.

**Prompt 2.2 (Copy vào AI Copilot):**

```text
Role: Python Backend Developer.
Context: Integrating Google Gemini API with strict output validation.
Task: Implement `GeminiClient` with Pydantic validation.

Requirements:
1. Libraries: `google-generativeai`, `pydantic`.
2. Define Pydantic Model (`schemas/ai_output.py`):
   - Create class `AIAnalysisResult(BaseModel)` matching the fields defined in Task 2.1.
3. Implementation (`services/ai/client.py`):
   - Initialize Gemini model (`gemini-1.5-flash` for speed/cost).
   - Method `analyze_text(text: str) -> AIAnalysisResult`:
     - Call `model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})`.
     - Parse the response text into the Pydantic model.
     - **Error Handling:** If parsing fails (JSONDecodeError), retry once with a simpler prompt. If it fails again, log error and return a default "Neutral" result.
4. Constraint: Use `tenacity` for retrying API connection errors (503/500).

```

---

### ⚡ Task 2.3: Hàng đợi xử lý bất đồng bộ (The Async Worker)

**Mục đích:** Khi Crawler lấy về 100 tin cùng lúc, bạn không thể gọi Gemini 100 lần ngay lập tức (sẽ bị Rate Limit hoặc tốn tiền). Bạn cần một hàng đợi (Queue) để xử lý từ từ.

* **Cơ chế:** Producer (Crawler) đẩy tin vào Queue -> Consumer (AI Worker) lấy ra xử lý từng cái một.

**Prompt 2.3 (Copy vào AI Copilot):**

```text
Role: System Architect.
Context: Handling burst traffic from crawlers. We need a queue to decouple crawling from AI processing.
Task: Implement an In-Memory Async Queue (or Redis Queue).

Requirements:
1. Architecture:
   - Use `asyncio.Queue` (for MVP) or `redis` (for Production). Let's start with `asyncio.Queue` to keep it simple for now, but design interfaces to swap later.
2. Components:
   - `AnalysisQueue`: A singleton class to `put(news_id)` and `get()`.
   - `AIWorker`: A background task (started on app startup) that runs strictly in a loop:
     - `while True:`
       - `news_id = await queue.get()`
       - Fetch news content from DB.
       - Call `GeminiClient.analyze_text`.
       - Update DB with results.
       - `await asyncio.sleep(2)` (Rate limit throttling to avoid hitting Google's RPM limit).
3. Integration: Update `main_crawler.py` to push `news.id` to this queue after saving raw news.

```

---

### ⚖️ Task 2.4: Chiến lược phân bổ Model thích ứng (Adaptive Brain)

**Mục đích:** Đây là tư duy tiết kiệm chi phí kiểu Do Thái.

* Tin ngắn, tin từ nguồn ít quan trọng -> Dùng **Gemini Flash** (Rẻ, nhanh).
* Tin dài, tin Breaking News, tin từ nguồn uy tín cao -> Dùng **Gemini Pro** (Thông minh hơn, đắt hơn).

**Prompt 2.4 (Copy vào AI Copilot):**

```text
Role: Python Developer (Optimization).
Context: Optimizing AI costs while maintaining quality for high-value news.
Task: Implement `ModelSelector` logic.

Requirements:
1. Configuration:
   - Load `GEMINI_FLASH_KEY` and `GEMINI_PRO_KEY` from .env.
2. Logic Update in `GeminiClient`:
   - Method `select_model(content_length: int, source_trust_score: float) -> GenerativeModel`:
   - Rule 1: If `source_trust_score` > 8.0 (High Tier Source) AND `content_length` > 2000 chars => Use **Gemini Pro**.
   - Rule 2: Else => Use **Gemini Flash**.
3. Benefit: This ensures we burn "expensive fuel" only where it matters (deep analysis of trusted sources), and use "cheap fuel" for general scanning.

```

---

### 🕵️ Task 2.5: Bộ lọc Scam & Keyword chuyên sâu (The Scam Shield)

**Mục đích:** AI đôi khi quá ngây thơ. Chúng ta cần một lớp "Logic cứng" (Hard rules) đè lên kết quả AI để phát hiện các mẫu lừa đảo phổ biến trong Crypto mà AI có thể bỏ qua.

* Ví dụ: Bài viết có chứa Contract Address lạ, yêu cầu "Connect Wallet", hoặc các cụm từ "Giveaway x2".

**Prompt 2.5 (Copy vào AI Copilot):**

```text
Role: Security Specialist / Python Dev.
Context: Crypto is full of scams. AI might miss subtle social engineering patterns. We need a regex-based post-processor.
Task: Implement `ScamDetector` service.

Requirements:
1. Logic (`services/security.py`):
   - Method `check_scam_indicators(content: str, ai_result: AIAnalysisResult) -> AIAnalysisResult`:
   - **Pattern Matching:** Use Regex to find patterns like:
     - "Send ETH to..."
     - "Claim airdrop at [bit.ly links]"
     - "Validation required"
   - **Override Logic:**
     - If patterns match => Force `ai_result.is_spam_scam = True` and `ai_result.impact_score = 0`.
     - Append warning to `ai_result.reasoning`: "[AUTO-DETECT] Suspicious scam patterns found."
2. Integration: Call this method immediately after receiving the response from Gemini in the `AIWorker`.

```

---

### 🚀 Tổng kết Giai đoạn 2

Sau khi hoàn thành 5 Task này, "Bộ não" của Coin87 sẽ hoạt động như sau:

1. **Crawler** ném tin vào **Queue** (Task 2.3).
2. **Worker** lấy tin ra, quyết định dùng **Flash hay Pro** (Task 2.4).
3. **Prompt Builder** tạo yêu cầu đóng vai "Chuyên gia phân tích" (Task 2.1).
4. **AI Client** gọi Gemini và ép trả về **JSON** (Task 2.2).
5. **Scam Detector** rà soát lần cuối bằng Regex để chặn lừa đảo (Task 2.5).
6. **Kết quả:** Dữ liệu sạch, có đánh giá Bullish/Bearish, điểm số Impact -> Lưu xuống Database.



===============================================================================================================================



Nếu bạn gửi nguyên văn một bài báo dài 5000 từ vào chỉ để AI kết luận "Tin này tốt", bạn đang **đốt tiền** vô ích. Hơn nữa, nếu bạn không dạy AI cách học (Few-shot learning), nó sẽ trả lời rất ngẫu nhiên.

Để tối ưu hóa chi phí đến mức tối đa và ép chất lượng lên mức chuyên gia, tôi đề xuất thêm **3 Task "Tối ưu hóa Token & Học tăng cường"** cho Giai đoạn 2 này.

---

### 📉 Task 2.6: Chiến lược xử lý theo Lô (Batch Processing Strategy)

**Vấn đề:** Gửi 10 request cho 10 tin tức riêng lẻ sẽ tiêu tốn 10 lần "System Instruction" (Lời dẫn hệ thống). Lời dẫn này thường dài (bạn quy định vai trò, format JSON...). Lặp lại nó là lãng phí.
**Giải pháp:** Gom 5-10 tin tức vào **1 Request duy nhất**.

* **Chi phí:** Giảm khoảng 40-50% số lượng token input.
* **Tốc độ:** Nhanh hơn nhiều so với gọi tuần tự.

**Prompt 2.6 (Copy vào AI Copilot):**

```text
Role: Python Backend Optimization Engineer.
Context: Reducing Gemini API costs by reducing redundant system prompt tokens.
Task: Implement `BatchNewsProcessor` logic in the Async Worker.

Requirements:
1. Logic Update (`services/ai/worker.py`):
   - Modify the `AnalysisQueue` to support `get_batch(batch_size=5)`.
   - Instead of processing one by one, wait for up to 5 seconds to collect a batch of 5 news items (or process whatever is available if timeout).
2. Prompt Engineering Update (`services/ai/prompts.py`):
   - Create `build_batch_prompt(news_list: List[dict]) -> str`:
     - Input: A list of `{'id': 1, 'title': '...', 'content': '...'}`.
     - Structure: 
       "Analyze the following list of crypto news items. Return a JSON Object where keys are the News IDs and values are the analysis objects.
       [Item 1]: ...
       [Item 2]: ... "
3. Schema Update:
   - Update Pydantic model to expect `Dict[str, AIAnalysisResult]` instead of a single object.
4. Error Handling:
   - If a batch fails (JSON Error), the code must implement a "Fallback Mechanism": Break the batch down and try processing each item individually (Safety net).

```

---

### ✂️ Task 2.7: Nén ngữ cảnh thông minh (Context Compression)

**Vấn đề:** Các bài báo thường chứa rất nhiều "rác" ở phần đầu và cuối (giới thiệu tác giả, disclaimer, link bài cũ...). AI không cần những thứ này để đánh giá.
**Giải pháp:** Chỉ giữ lại những phần chứa thông tin (Title + 30% đầu bài + Các câu chứa số liệu/tên coin).

**Prompt 2.7 (Copy vào AI Copilot):**

```text
Role: NLP Data Engineer.
Context: AI input tokens are expensive. We need to strip fluff without losing semantic meaning before sending to Gemini.
Task: Implement `TokenOptimizer` service.

Requirements:
1. Logic (`services/ai/optimizer.py`):
   - Method `compress_content(title: str, content: str, max_chars: int = 3000) -> str`:
     - Strategy 1 (Head & Tail): Keep the first 1000 chars (Introduction) and the last 500 chars (Conclusion).
     - Strategy 2 (Keyword Preservation): Scan the middle part. Only keep sentences that contain specific entities (extracted in Task 1.6 like '$BTC', 'SEC', 'Binance') or numbers/percentages ('%', '$').
     - Combine: `Title + Head + [Relevant Middle Sentences] + Tail`.
     - Hard Limit: Ensure the total length strictly never exceeds `max_chars`.
2. Integration:
   - Call `TokenOptimizer.compress_content` inside the `AIWorker` BEFORE adding the news to the batch/prompt.
3. Benefit: This reduces input tokens by 60-70% for long articles while keeping the "Alpha" (numbers and entities).

```

---

### 🎓 Task 2.8: Học qua ví dụ (Few-Shot Prompting Injection)

**Vấn đề:** Dù bạn mô tả kỹ đến đâu, AI đôi khi vẫn đánh giá sai "Sentiment". Ví dụ: "Binance bị phạt 4 tỷ đô" -> AI nghĩ là "Tiêu cực" (Bearish). Nhưng thực tế thị trường coi đó là "Tích cực" (Bullish) vì rủi ro pháp lý đã xong.
**Giải pháp:** Cung cấp cho AI một "Bộ đáp án mẫu" (Knowledge Base) ngay trong prompt để nó bắt chước cách tư duy của chuyên gia.

**Prompt 2.8 (Copy vào AI Copilot):**

```text
Role: Senior Prompt Engineer.
Context: Improving AI accuracy using In-Context Learning (Few-Shot Prompting).
Task: Create a `FewShotExamples` registry and inject it into the prompt.

Requirements:
1. Data Setup (`services/ai/examples.py`):
   - Create a list of 3-5 static examples.
   - Format:
     Example 1:
     Input: "Binance agrees to pay $4B fine to settle US charges."
     Output: {"sentiment": "Bullish", "reasoning": "Settlement removes uncertainty. Market reacts positively to closure.", "impact_score": 9}
     Example 2:
     Input: "New memecoin PEPE2.0 launches with 5000% APY staking."
     Output: {"sentiment": "Neutral", "is_spam_scam": true, "reasoning": "High APY typical of ponzi/rug-pull schemes.", "impact_score": 2}
2. Integration:
   - Update `PromptBuilder` (Task 2.1) to insert these examples section between the `SYSTEM_INSTRUCTION` and the `User Content`.
   - Header: "### REFERENCE EXAMPLES (FOLLOW THIS LOGIC):"
3. Benefit: Drastically improves the "Reasoning" quality and alignment with crypto-native thinking, reducing the need for expensive GPT-4 models. We can stick to Gemini Flash.

```

---

### 🚀 Tổng kết Giai đoạn 2 (Đã tối ưu hóa)

Sau khi thêm 3 Task này, quy trình AI của bạn sẽ đạt hiệu suất cực cao:

1. **Nén tin (Task 2.7):** Bài báo 2000 từ -> Nén còn 600 từ (Giữ lại số liệu, bỏ rác). **(Tiết kiệm 70% tiền)**.
2. **Gom Lô (Task 2.6):** 10 tin nén -> Gom vào 1 Request. **(Tiết kiệm 50% tiền System Prompt)**.
3. **Học mẫu (Task 2.8):** Kèm theo 3 ví dụ chuyên gia vào prompt. AI (bản rẻ tiền Flash) sẽ trả lời thông minh ngang ngửa bản đắt tiền (Pro) nhờ có mẫu để bắt chước.

========================================================================================================================================

**Giai đoạn 3: Mô hình kinh doanh & Phân phối (Monetization & Distribution)**.

Đây là giai đoạn biến hệ thống "đam mê" thành "cỗ máy kiếm tiền". Tư duy cốt lõi ở đây là: **Dữ liệu thô thì rẻ, nhưng Dữ liệu đã phân tích (Alpha) thì vô giá.**

Chúng ta sẽ xây dựng một hệ thống API chặt chẽ, nơi người dùng Free chỉ nhìn thấy phần nổi của tảng băng, còn người dùng Pro (trả tiền) mới nhìn thấy toàn bộ "kho báu" mà AI đã tìm ra.

Dưới đây là 5 Task chuyên sâu để xây dựng một Backend bán dữ liệu tự động hoá hoàn toàn.

---

### 🔑 Task 3.1: Cơ sở hạ tầng API & Quản lý định danh (The Gatekeeper)

**Mục đích:** Xây dựng khung FastAPI và hệ thống cấp phát "Chìa khóa" (API Key). Mỗi người dùng (Client) phải có một định danh riêng lưu trong Database để chúng ta kiểm soát.

**Prompt 3.1 (Copy vào AI Copilot):**

```text
Role: Senior Backend Engineer (FastAPI).
Context: Setting up the monetization layer for Coin87. We need secure user management.
Task: Initialize FastAPI and User/Auth Models.

Requirements:
1. Database Update (`models/user.py`):
   - Create `User` table:
     - `id`: UUID (Primary Key).
     - `email`: String (Unique).
     - `api_key`: String (Unique, Indexed, generated using secrets.token_urlsafe).
     - `tier`: Enum ('free', 'pro', 'enterprise').
     - `c87_balance`: Decimal (for gamification later).
     - `requests_this_month`: Integer (default 0).
     - `is_active`: Boolean.
   - Create `APIKeyLog` table: To track usage history per key.
2. Logic (`core/security.py`):
   - Implement `get_api_key` dependency.
   - Logic: Extract `X-API-KEY` from header.
   - Query DB to validate. If invalid/inactive -> Raise 401 Unauthorized.
   - Return the `User` object to the route.
3. Endpoints (`routers/auth.py`):
   - `POST /v1/auth/register`: Create user, auto-generate API Key, return it ONCE.
   - `POST /v1/auth/rotate-key`: Generate a new key for existing user (security best practice).
4. Constraint: Use `passlib` for password hashing if password login is needed, but prioritize API Key flow.

```

---

### 🚧 Task 3.2: Hệ thống Giới hạn tốc độ đa tầng (Tiered Rate Limiting)

**Mục đích:** Ngăn chặn lạm dụng và tạo động lực mua hàng.

* **Free:** Rất chậm (ví dụ: 10 request/giờ) -> Chỉ đủ dùng thử.
* **Pro:** Nhanh (1000 request/giờ) -> Đủ để chạy trading bot.

Chúng ta sẽ dùng **Redis** để đếm số lần gọi API siêu tốc độ (In-memory) thay vì chọc vào Database liên tục.

**Prompt 3.2 (Copy vào AI Copilot):**

```text
Role: DevOps / Backend Engineer.
Context: Protecting the API from abuse and enforcing business tiers.
Task: Implement Redis-based Rate Limiting (Throttling).

Requirements:
1. Infrastructure: Use `redis-py` (async) to connect to a Redis instance (load URL from .env).
2. Logic (`core/ratelimit.py`):
   - Create a dependency `RateLimiter`.
   - Input: The `User` object (from Task 3.1).
   - Logic:
     - Define Quotas: FREE_LIMIT = 10/hour, PRO_LIMIT = 1000/hour.
     - Key in Redis: `rate_limit:{user_id}:{current_hour}`.
     - Operation: `INCR` key. If value > limit -> Raise 429 Too Many Requests.
     - Set `EXPIRE` on key for 1 hour.
3. Headers:
   - Inject headers into response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
4. Constraint: Fail open strategy (if Redis is down, allow request but log error) OR Fail closed (deny). Choose Fail Open for better UX initially.

```

---

### 🎭 Task 3.3: Bộ lọc dữ liệu thông minh (The Paywall Logic)

**Mục đích:** Đây là chức năng quan trọng nhất để bán hàng.

* Endpoint `GET /news` trả về dữ liệu khác nhau tùy theo Tier của người dùng.
* Người dùng Free: Thấy Title, Link, Date. **(Dữ liệu AI bị ẩn/làm mờ).**
* Người dùng Pro: Thấy Sentiment, Impact Score, Reasoning, Coins.

**Prompt 3.3 (Copy vào AI Copilot):**

```text
Role: Python Developer.
Context: Serving news data with conditional visibility based on user subscription.
Task: Implement the News Endpoint with Pydantic Polymorphism.

Requirements:
1. Pydantic Schemas (`schemas/news.py`):
   - `NewsPublic` (Minimal): id, title, published_at, url, source_name.
   - `NewsPro` (Inherits Public): ai_summary, impact_score, sentiment, detected_coins, reasoning, is_scam.
2. Endpoint (`routers/news.py`):
   - `GET /v1/news`:
   - Parameters: `limit`, `offset`, `coin_filter`, `sentiment_filter`.
   - Dependency: `get_api_key` (Task 3.1).
   - Logic:
     - Fetch data from DB.
     - If `user.tier` == 'free':
       - Return List[NewsPublic].
       - (Optional) You can return `NewsPro` but with AI fields set to null or "UPGRADE_TO_VIEW".
     - If `user.tier` == 'pro':
       - Return List[NewsPro].
3. Constraint: Optimize SQL query. Do not select AI columns from DB if user is Free (save bandwidth).

```

---

### 💸 Task 3.4: Tích hợp thanh toán tự động (SePay Webhook)

**Mục đích:** Tự động hóa quy trình thu tiền. Khi người dùng chuyển khoản theo mã QR (SePay), hệ thống nhận Webhook và lập tức nâng cấp Tier cho user. Không can thiệp thủ công.

**Prompt 3.4 (Copy vào AI Copilot):**

```text
Role: Fintech Backend Developer.
Context: Automating subscriptions via bank transfer (SePay).
Task: Implement Payment Webhook Handler.

Requirements:
1. Database Update:
   - Create `Transaction` table: `id`, `user_id`, `amount`, `currency`, `sepay_transaction_id`, `status`, `created_at`.
2. Endpoint (`routers/payment.py`):
   - `POST /v1/webhook/sepay`:
   - Validate SePay signature/token (Security check to prevent fake requests).
   - Parse body: Identify `user_id` (usually passed in the transfer content format like "C87 USER_123").
   - Logic:
     - Record Transaction in DB.
     - If amount >= 50,000 VND (example):
       - Update `User.tier` = 'pro'.
       - OR Add equivalent `$C87` tokens to `User.c87_balance`.
     - Respond 200 OK to SePay.
3. Constraint: Idempotency. Check if `sepay_transaction_id` already exists to prevent double-crediting if SePay retries the webhook.

```

---

### 📊 Task 3.5: Dashboard Analytics & Theo dõi sử dụng (Usage Tracking)

**Mục đích:**

1. Người dùng cần biết họ còn bao nhiêu lượt request (để biết đường nâng cấp).
2. Bạn (Admin) cần biết ai đang dùng nhiều nhất, nguồn tin nào được truy xuất nhiều nhất.

**Prompt 3.5 (Copy vào AI Copilot):**

```text
Role: Backend Developer.
Context: Providing visibility into API usage for both users and admins.
Task: Implement Analytics Middleware and User Dashboard Endpoint.

Requirements:
1. Middleware (`core/middleware.py`):
   - Create `UsageLoggerMiddleware`.
   - For every request, increment `User.requests_this_month` in DB (or Redis for speed, then sync to DB).
   - Log the endpoint accessed and response time.
2. Endpoint (`routers/user.py`):
   - `GET /v1/users/me`:
   - Return current plan, requests used/limit, expiration date, and $C87 balance.
3. Background Task (APScheduler - reuse from Phase 1/2 setup):
   - Create a job "Reset Quotas" running on the 1st of every month.
   - Reset `requests_this_month` = 0 for all users.
4. Constraint: Ensure strict locking or atomic updates (using `User.requests_this_month + 1`) to avoid race conditions during high concurrency.

```

---

### 🚀 Tổng kết Giai đoạn 3 (Đã sẵn sàng kinh doanh)

Sau khi hoàn thành 5 Task này, bạn đã có một **SaaS (Software as a Service)** hoàn chỉnh:

1. **Task 3.1:** Cửa chính (Đăng ký/Login).
2. **Task 3.2:** Bảo vệ cửa (Rate Limit).
3. **Task 3.3:** Quầy hàng (Phân loại hàng thường/hàng xịn).
4. **Task 3.4:** Máy thu ngân tự động (SePay).
5. **Task 3.5:** Sổ sách kế toán (Analytics).

========================================================================================================================================


---

### 🚀 Task 3.6: Chiến lược Caching Đa tầng (The Speed Demon)

**Vấn đề:** Tin tức không thay đổi liên tục từng giây, nhưng User (hoặc Bot của họ) lại có thói quen gọi API liên tục (Polling) để check tin mới. Nếu 1000 user gọi `/news` cùng lúc, Database sẽ quá tải dù dữ liệu chẳng có gì mới.
**Giải pháp:** Dùng Redis để lưu kết quả trả về. Nếu tin chưa đổi, trả ngay từ RAM (Redis) thay vì chọc vào Database.

**Prompt 3.6 (Copy vào AI Copilot):**

```text
Role: Backend Performance Engineer.
Context: Reducing Database load and latency for Coin87 API.
Task: Implement "Look-aside Caching" for GET endpoints using Redis.

Requirements:
1. Logic (`services/cache.py`):
   - Decorator `@cache_response(ttl_seconds=60)`:
     - Check Redis for key `api:cache:{request.url}:{query_params}`.
     - If HIT: Return JSON directly from Redis (Latency < 5ms).
     - If MISS: Execute function, store result in Redis with TTL.
2. Smart Invalidation Strategy:
   - When a NEW news item is inserted (via Crawler/AI Worker):
     - Emit an event to clear keys related to `/news` listing.
     - This ensures users see new data immediately, but serve cached data otherwise.
3. Tiered Caching (Business Logic):
   - Free Users: Force 60s Cache TTL (They see news slightly delayed).
   - Pro Users: 10s Cache TTL (They see news faster).
4. Constraint: Use `fastapi-cache` or implement custom logic using `redis-py`. Ensure serialization handles Pydantic models correctly.

```

---

### 📚 Task 3.7: Tài liệu API tương tác & SDK (The Developer Magnet)

**Vấn đề:** Bạn bán API, khách hàng của bạn là Dev. Nếu Document sơ sài, họ sẽ không biết cách tích hợp và bỏ đi. Swagger mặc định của FastAPI là chưa đủ chuyên nghiệp để bán tiền triệu.
**Giải pháp:** Tùy biến Swagger UI, bổ sung mô tả chi tiết, ví dụ Code mẫu (Curl, Python, JS).

**Prompt 3.7 (Copy vào AI Copilot):**

```text
Role: Developer Advocate / Technical Writer.
Context: The API is the product. We need world-class documentation to convert visitors into paid users.
Task: Enhance FastAPI Swagger/OpenAPI documentation.

Requirements:
1. Config (`main.py`):
   - Customize `FastAPI(title="Coin87 Intelligence API", description=..., version="1.0")`.
   - Add `tags_metadata` to group endpoints logically (e.g., "Market Intelligence", "Account", "System").
2. Schema Enrichment:
   - Go through every Pydantic model (`schemas/*.py`) and add `Field(..., description="Explain what this field means", example="BTC")`.
   - Ensure the "Response Model" for errors (400, 401, 429) is clearly documented so devs know how to handle rate limits.
3. Authentication Guide:
   - Add a detailed description in the Swagger header explaining: "How to get an API Key", "How to pass it in headers (X-API-KEY)", and "Tier limits".
4. Constraint: The documentation must be auto-generated from code. No manual markdown files that get out of sync.

```

---

### 🔔 Task 3.8: Real-time Webhooks (The "Alpha" Push)

**Vấn đề:** Các quỹ đầu tư và Trading Bot ghét việc phải gọi API (Polling) liên tục. Họ muốn **BẠN** báo cho họ ngay khi có biến (Push). Đây là tính năng "Pro" đắt giá nhất.
**Giải pháp:** Cho phép người dùng đăng ký URL (Webhook). Khi có tin `impact_score > 8` (Tin cực nóng), hệ thống tự bắn dữ liệu sang server của họ.

**Prompt 3.8 (Copy vào AI Copilot):**

```text
Role: Senior Backend Architect.
Context: Pro users need instant alerts for high-impact news. Polling is too slow.
Task: Implement a Webhook Dispatcher System.

Requirements:
1. Database Update:
   - Create `WebhookSubscription` table: `id`, `user_id`, `target_url`, `min_impact_score` (filter), `secret_key` (for signing).
2. Logic (`services/webhook.py`):
   - Create a background task `dispatch_webhooks(news_item: News)`:
     - Query all subscriptions where `news_item.impact_score >= sub.min_impact_score`.
     - For each sub, send a POST request to `target_url` with the news JSON.
     - Security: Sign the payload using HMAC-SHA256 with the `secret_key` so users verify it's truly from Coin87.
3. Resilience:
   - If the user's server returns 500 or timeout, retry 3 times with exponential backoff (reuse `tenacity` logic from Task 1.7).
   - If it fails 10 times consecutively, auto-disable the subscription to save resources.
4. Constraint: This feature is strictly for `PRO` tier users. Enforce this check at the registration endpoint.

```

---

### 💎 Tổng kết Giai đoạn 3 (Đẳng cấp Expert)

Với việc bổ sung 3 Task này, hệ thống của bạn đã nhảy vọt từ "Dự án cá nhân" sang "Sản phẩm thương mại chuyên nghiệp":

1. **Task 3.6 (Caching):** Giúp server chịu tải hàng nghìn user mà CPU vẫn nhàn rỗi, **tiết kiệm tiền thuê VPS/Database**.
2. **Task 3.7 (Docs):** Biến API thành một sản phẩm dễ hiểu, dễ mua, dễ dùng, **tăng tỷ lệ chuyển đổi khách hàng**.
3. **Task 3.8 (Webhooks):** Tính năng "Sát thủ" để bán gói Pro giá cao. Các Bot trader sẵn sàng trả tiền để nhận tin nhanh hơn đám đông dù chỉ 1 giây.



=======================================================================================================================================


**Giai đoạn 4: Ứng dụng PWA Gamification (The Face)**.

Đây là nơi mọi logic phức tạp bên dưới (Backend, AI, Crawl) hội tụ lại thành một trải nghiệm đơn giản trên tay người dùng.

Tư duy cốt lõi ở đây là: **"Biến người dùng thành Nhân viên" (User as Worker)**.
Chúng ta không thuê nhân viên kiểm duyệt tin. Chúng ta tạo ra giao diện để người dùng "chơi" (Vote Real/Fake) và trả công cho họ bằng token ảo ($C87). Chính hành động này giúp hệ thống của bạn ngày càng thông minh hơn.

Dưới đây là 8 Task chi tiết để xây dựng PWA từ con số 0 đến khi sẵn sàng Viral.

---

### 📱 Task 4.1: Khung sườn Mobile-First & PWA Manifest (The Shell)

**Mục đích:** Tạo một Web App nhưng hoạt động y hệt Native App (có icon trên màn hình chính, không thanh địa chỉ, splash screen). Sử dụng **Next.js (App Router)** vì nó hỗ trợ Server Component (SEO tốt cho bản tin) và Client Component (tương tác mượt).

**Prompt 4.1 (Copy vào AI Copilot):**

```text
Role: Senior Frontend Developer (Next.js Specialist).
Context: Building Coin87 as a high-performance PWA.
Task: Initialize Next.js project with PWA configuration.

Requirements:
1. Setup:
   - Use `create-next-app` with TypeScript, Tailwind CSS, ESLint.
   - Install `next-pwa` or `@ducanh2912/next-pwa`.
2. Manifest Configuration (`manifest.json`):
   - Name: "Coin87 - Crypto Intelligence".
   - Short Name: "Coin87".
   - Display: "standalone" (removes browser address bar).
   - Background Color: "#0f172a" (Dark mode default).
   - Icons: Define paths for 192x192 and 512x512 icons (placeholders for now).
3. Layout (`app/layout.tsx`):
   - Define metadata specifically for mobile (viewport-fit=cover, apple-mobile-web-app-capable).
   - Implement a strictly Dark Mode UI theme (Slate-900 background, Slate-50 text) to look professional/crypto-native.
4. Constraint: The structure must use the "App Router" directory. Ensure `sw.js` (Service Worker) is generated on build.

```

---

### 📰 Task 4.2: Dòng tin thông minh & Infinite Scroll (The Feed)

**Mục đích:** Hiển thị tin tức. Nhưng quan trọng là **Logic hiển thị theo Tier**.

* Nếu User Free: Chỉ hiện Title + Source + Time. Phần `AI Summary` bị ẩn.
* Load tin theo trang (Pagination) để không làm đơ điện thoại.

**Prompt 4.2 (Copy vào AI Copilot):**

```text
Role: Frontend Developer.
Context: Displaying the news feed efficiently.
Task: Implement `NewsFeed` component with Infinite Scroll.

Requirements:
1. Libraries: `swr` (for data fetching/caching), `react-intersection-observer` (for infinite scroll trigger).
2. Data Fetching:
   - Hook `useNews(page, filters)` calling `GET /v1/news` from our FastAPI backend.
   - Handle "Loading" state (Skeleton UI - strictly no spinners, use pulsating blocks).
   - Handle "Error" state.
3. Component UI (`components/NewsCard.tsx`):
   - Layout: Minimalist Card.
   - Visual Hierarchy: Title (Bold) > Source/Time (Gray, Small) > Tags (Badges).
   - **Tier Logic:**
     - Check user tier (mock context for now or fetch from /v1/users/me).
     - If Tier == Free: Render the `AI Summary` text but apply a CSS `blur-sm` filter and `user-select-none`. Overlay a "Lock Icon" button over the blurred text.
     - If Tier == Pro: Render full clear text with sentiment color coding (Green border for Bullish, Red for Bearish).
4. Constraint: Mobile-first responsive design. Touch targets (buttons) must be at least 44px height.

```

---

### 🎮 Task 4.3: Cơ chế Vote & Hiệu ứng Gamification (The Game)

**Mục đích:** Đây là tính năng "Money Maker". Mỗi lần user đọc tin, họ sẽ thấy 2 nút: "Trust" ✅ và "Fake" ❌.

* Khi bấm -> Gọi API -> Cộng điểm $C87 -> Hiệu ứng pháo hoa nhỏ/rung máy (Haptic) để tạo cảm giác thỏa mãn (Dopamine hit).

**Prompt 4.3 (Copy vào AI Copilot):**

```text
Role: UX/UI Engineer.
Context: Gamifying the news validation process.
Task: Implement the Voting Mechanism with Haptic Feedback.

Requirements:
1. Component (`components/VoteActions.tsx`):
   - Two buttons: "Legit/Trust" (Green Thumb Up) and "FUD/Fake" (Red Thumb Down).
2. Logic:
   - On Click:
     - Optimistic UI: Immediately disable buttons and show "+5 $C87" animation floating up.
     - API Call: `POST /v1/news/{id}/vote` (payload: {vote_type: 'trust'}).
     - Haptic: Use `navigator.vibrate(50)` (if supported) to give physical feedback.
3. State Persistence:
   - If user has already voted on this news (check `voted` field from API response), show the buttons as "Selected" and disabled.
4. Animation: Use `framer-motion` for a subtle "pop" effect when the button is pressed.
5. Constraint: Keep it snappy. No lagging animations.

```

---

**Prompt 4.4 (Copy vào AI Copilot):**

```text
Role: Fullstack Developer (Next.js + FastAPI).
Context: Simple Authentication flow. Source of truth is the Database.
Task: Implement Login and API Key Retrieval.

Requirements:
1. Backend Logic (`routers/auth.py`):
   - `POST /v1/auth/login`:
   - Input: `{ email: string }`.
   - Logic:
     - Check `User` table in Postgres.
     - If User exists: Return `{ api_key: user.api_key, tier: user.tier }`.
     - If User does not exist: Create new User, generate distinct `api_key`, save to DB, and return it.

2. Frontend Logic (`context/AuthContext.tsx`):
   - Create a Context to hold `user` and `apiKey` in memory (React State).
   - Method `login(email)`:
     - Call Backend API.
     - On success: Set `apiKey` into State.
     - **Constraint:** Do NOT save `apiKey` to `localStorage`. Keep it in memory only.

3. UI (`app/login/page.tsx`):
   - Simple Input Email & Button "Enter Coin87".
   - On submit -> Call `login(email)` -> Redirect to Dashboard.

```

---

### 💳 Task 4.5: Ví $C87 & Nâng cấp (Load từ Database)

**Mục đích:** Hiển thị thông tin tài khoản. Mọi số liệu (Số dư, Tier) phải load trực tiếp từ Database lên giao diện. Không tính toán ở Client.

**Prompt 4.5 (Copy vào AI Copilot):**

```text
Role: Frontend Developer.
Context: Displaying user profile data fetched strictly from the Database.
Task: Implement Profile & Upgrade UI.

Requirements:
1. Data Fetching:
   - Use `useSWR` to fetch `GET /v1/users/me`.
   - Headers: `{ "X-API-KEY": apiKey }` (from AuthContext).
   - The Backend looks up the User by API Key in the DB and returns current `$C87` balance and `tier`.

2. UI Components:
   - `UserProfile`: Show Email, Tier (Free/Pro), and Balance.
   - `UpgradeButton`:
     - If Tier is 'Free', show "Upgrade to Pro".
     - On Click: Show SePay QR Code modal.
     - Note: The QR content should include the User's Email or ID so the backend can verify the payment later.

3. Constraint: If the API Key is invalid or missing, redirect user back to Login page immediately.

```

---

### 🏆 Task 4.6: Bảng xếp hạng (Leaderboard) - "Social Proof"

**Mục đích:** Kích thích sự cạnh tranh. "Ai là người săn tin giỏi nhất tuần?".

**Prompt 4.6 (Copy vào AI Copilot):**

```text
Role: Frontend Developer.
Context: Increasing user engagement via competition.
Task: Implement Leaderboard Page.

Requirements:
1. API Integration:
   - Call `GET /v1/users/leaderboard` (Backend needs to support this: Top users by $C87 balance or Votes cast).
2. UI (`app/leaderboard/page.tsx`):
   - List Top 10 users.
   - Highlight the current user's rank at the bottom (sticky).
   - Use Gold/Silver/Bronze icons for Top 3.
3. Constraint: Cache this data heavily (e.g., revalidate every 1 hour) because it doesn't need to be real-time.

```

---

### 🔔 Task 4.7: Thông báo đẩy (Push Notifications) - "Retention"

**Mục đích:** Nhắc user quay lại app. "Có biến! Bitcoin vừa sập, vào vote ngay!".

**Prompt 4.7 (Copy vào AI Copilot):**

```text
Role: PWA Specialist.
Context: Re-engaging users with alerts.
Task: Implement Service Worker Push Notifications.

Requirements:
1. UI:
   - Add a "Bell" icon in the header.
   - On click, request `Notification.requestPermission()`.
2. Logic:
   - If granted, subscribe user via Service Worker `pushManager`.
   - Send the `subscription` object to Backend (`POST /v1/notifications/subscribe`).
3. Constraint: Handle the "Permission Denied" state gracefully (don't nag the user).

```

---

### ⚙️ Task 4.8: Cấu hình Offline (Offline Support)

**Mục đích:** Dù mất mạng, user vẫn phải mở được app và đọc được những tin đã load (Cache-first strategy).

**Prompt 4.8 (Copy vào AI Copilot):**

```text
Role: PWA Performance Engineer.
Context: Ensuring app works in patchy network conditions.
Task: Configure Workbox for Offline Caching.

Requirements:
1. Next-PWA Config (`next.config.js`):
   - Configure `runtimeCaching`.
   - Cache Strategy for `/v1/news`: `NetworkFirst` (Try to get fresh news, if failed, show cached news).
   - Cache Strategy for Images/Assets: `CacheFirst` (Assets don't change often).
   - Cache Strategy for API POST (Votes): `BackgroundSync` (Save vote in queue, retry when online).
2. Benefit: Seamless experience even in elevators or tunnels.

```

---

### 🏁 Tổng kết Giai đoạn 4

Bạn đã có lộ trình chi tiết để xây dựng "Mặt tiền" cho Coin87.

1. **Task 4.1 - 4.2:** Khung app và Dòng tin (Core).
2. **Task 4.3:** Gamification (Vote kiếm tiền).
3. **Task 4.4 - 4.5:** Quản lý tài khoản và Nâng cấp (Tiền thật).
4. **Task 4.6 - 4.8:** Tăng trưởng và Tối ưu trải nghiệm.



==================================================================================================================================


---

### 📱 Task 4.9: Thanh điều hướng Bottom Bar & Safe Area (The Native Feel)

**Vấn đề:** Web thường dùng Menu Hamburger (3 gạch) ở góc trên. Nhưng trên Mobile, ngón tay cái rất khó với tới đó. App hiện đại phải có thanh điều hướng ở dưới đáy (Bottom Navigation).
**Thách thức PWA:** Trên iPhone đời mới (có tai thỏ/Dynamic Island), thanh dưới cùng thường bị đè lên vạch "Home Indicator". Bạn phải xử lý vùng an toàn (`safe-area-inset`) nếu không muốn App trông "rẻ tiền".

**Prompt 4.9 (Copy vào AI Copilot):**

```text
Role: Senior Frontend Developer (Mobile UX Specialist).
Context: Creating a native-like navigation experience for Coin87 PWA.
Task: Implement a Sticky Bottom Navigation Bar with Safe Area handling.

Requirements:
1. Component (`components/BottomNav.tsx`):
   - Fixed position at the bottom of the screen (`fixed bottom-0 w-full`).
   - Items: Feed (Home Icon), Leaderboard (Trophy Icon), Settings/Profile (User Icon).
   - Visual Style: Glassmorphism (Background blur), dark semi-transparent theme.
   - **Active State:** The selected icon should glow or have a different color (e.g., Gold for Coin87 theme).

2. CSS Safety (`globals.css`):
   - Handle iOS Safe Areas (The Home Indicator area).
   - Use `padding-bottom: env(safe-area-inset-bottom)` to prevent the navbar from being covered by the iPhone gesture bar.
   - Add `z-index: 50` to ensure it floats above all content.

3. Interaction:
   - Tap targets must be large (min 44x44px).
   - Add a subtle scale animation (0.95x) on click using `framer-motion` to mimic native button press feel.

4. Layout Adjustment:
   - Add `padding-bottom` to the main content container equal to the Navbar height + 20px, ensuring the last news card isn't hidden behind the navbar.

```

---

### 👆 Task 4.10: Vuốt để Vote "Tinder-style" (The Addictive Interaction)

**Vấn đề:** Việc bấm nút "Trust/Fake" lặp đi lặp lại rất nhàm chán.
**Giải pháp:** Biến việc lọc tin thành một trò chơi.

* **Vuốt phải:** Trust (Tin chuẩn) -> Hiện màu Xanh.
* **Vuốt trái:** Fake (Tin rác) -> Hiện màu Đỏ.
Cảm giác vuốt vật lý kết hợp với rung (Haptic) sẽ tạo ra "Dopamine Loop", khiến user nghiện việc lọc tin cho bạn.

**Prompt 4.10 (Copy vào AI Copilot):**

```text
Role: Creative Frontend Developer (Animation Specialist).
Context: Gamifying the news validation process using gestures.
Task: Implement Tinder-style Swipeable Cards.

Requirements:
1. Library: Use `framer-motion` (Use `useMotionValue`, `useTransform`).
2. Component Interaction (`components/SwipeableNewsCard.tsx`):
   - Wrap the News Card in a `motion.div`.
   - Enable `drag="x"` (Horizontal dragging).
   - **Visual Feedback:**
     - As user drags RIGHT: Rotate card slightly clockwise, overlay turns GREEN (Opacity increases with drag distance).
     - As user drags LEFT: Rotate card slightly counter-clockwise, overlay turns RED.
   - **Snap Logic (`onDragEnd`):**
     - If drag distance > 100px: Trigger Vote API, fly the card out of the screen, and auto-load the next card.
     - If drag distance < 100px: Spring back to center (Reset).

3. Haptic Feedback:
   - Trigger `navigator.vibrate(20)` when the drag crosses the threshold (letting the user know "If you release now, it counts").

4. Fallback: Keep the physical buttons (Task 4.3) below the card for users who prefer clicking, but make Swiping the primary interaction.

```

---

### 🏁 TỔNG KẾT GIAI ĐOẠN 4 (HOÀN HẢO)

Chúc mừng bạn! Với việc bổ sung 2 task này, Coin87 PWA của bạn đã đạt chuẩn App thương mại:

1. **Task 4.1 - 4.2:** Khung sườn & Hiển thị (Core).
2. **Task 4.3 + 4.10:** Cơ chế Vote (Bấm nút + Vuốt Tinder).
3. **Task 4.4 - 4.5:** Login & Ví (Logic database chặt chẽ).
4. **Task 4.6 - 4.7:** Giữ chân User (Ranking + Push).
5. **Task 4.8:** Offline Mode (Ổn định).
6. **Task 4.9:** Cảm giác Native (Bottom Nav).


=======================================================================================================================================


**Giai đoạn 5: Cỗ máy Sự thật & Tự động hóa (The Truth Engine & Automation)**.
**5 Prompt thực chiến (Battle-tested)** được thiết kế để AI Copilot của bạn code ra đúng các logic kiểm chứng (CoinGecko/CryptoQuant/Nansen) mà chúng ta đã thảo luận.

Tôi đã chia nhỏ thành các module cụ thể. Bạn hãy copy từng prompt theo thứ tự để thực hiện.

---

### 📋 Task 5.1: Database Schema & AI Taxonomy (Cấu trúc dữ liệu phân loại)

**Mục đích:** Dạy hệ thống biết "Loại tin" (Category) để áp dụng quy trình kiểm tra riêng biệt. Tin "Dự báo giá" cần check chart, tin "Mainnet" cần check GitHub/Blog.

**Prompt 5.1 (Copy vào Copilot):**

```text
Role: Database Architect & Prompt Engineer.
Context: Implementing the "Truth Engine" for Coin87. We need to categorize news strictly to apply different verification strategies.
Task: Update Database and AI Prompt logic.

Requirements:
1. Database Update (`models/news.py`):
   - Add column `category_type` (Enum):
     - `MARKET_MOVE`: Price predictions, pumps, dumps, whale movements.
     - `PROJECT_UPDATE`: Mainnet launches, upgrades, forks, maintenance.
     - `PARTNERSHIP`: New listings, VC funding, collaborations.
     - `SECURITY`: Hacks, scams, rug pulls, regulatory bans.
     - `OPINION`: Editorials, influencer thoughts (Low verification value).
   - Add column `verification_status` (Enum): `PENDING`, `VERIFIED`, `FLAGGED`, `DEBUNKED`.
   - Add column `evidence_data` (JSONB): To store the proof (e.g., {"price_change_24h": "+5%", "volume_spike": "yes"}).

2. AI Prompt Update (`services/ai/prompts.py`):
   - Modify the System Instruction.
   - Add a rule: "Classify the news into one of these categories: [MARKET_MOVE, PROJECT_UPDATE, PARTNERSHIP, SECURITY, OPINION]. If it contains price numbers or 'bull/bear' keywords, it is MARKET_MOVE."
   - Update the JSON Output Schema to include `category_type`.

3. Migration: Create a script to migrate the DB.

```

---

### 🔗 Task 5.2: Logic "Tier 1 Check" (Kiểm chứng chéo nguồn uy tín)

**Mục đích:** Code logic kiểm tra xem các "ông lớn" có xác nhận tin này không. Nếu nguồn Tier 3 nói X, mà 4 tiếng sau Tier 1 chưa nói gì => Flag là "Unverified".

**Prompt 5.2 (Copy vào Copilot):**

```text
Role: Python Logic Developer.
Context: Implementing "Proof of Source". We trust news more if Tier 1 sources report it.
Task: Implement `Tier1Verifier` Service.

Requirements:
1. Configuration:
   - Define a constant `TIER_1_SOURCE_IDS`: List of IDs corresponding to Bloomberg, CoinDesk, Official Project Blogs in our DB.

2. Logic (`services/truth_engine/cross_check.py`):
   - Method `verify_tier1_consensus(target_news: News) -> bool`:
     - If `target_news.source_id` is already in `TIER_1_SOURCE_IDS`, return True (Auto-trust).
     - If not:
       - Query DB for other news items published within [target_time - 2h, target_time + 12h].
       - Filter where `source_id` is in `TIER_1_SOURCE_IDS`.
       - Use `thefuzz` (fuzzy matching) to compare titles.
       - If Similarity > 85%: Return True (Tier 1 confirmed it).
       - Else: Return False.

3. Integration:
   - Call this method in the `EvaluationJob` (Task 5.1). If returns False, set `verification_status` = 'PENDING_CONSENSUS'.

```

---

### 📉 Task 5.3: Logic "Market Data Check" (Kiểm chứng bằng Binance API)

**Mục đích:** Code logic dùng dữ liệu thật để bóc trần tin giả. Tin nói "Volume bùng nổ" mà API báo Volume giảm => Đánh dấu "Exaggerated" (Phóng đại).

**Prompt 5.3 (Copy vào Copilot):**

```text
Role: Python Data Engineer.
Context: Implementing "Data-Driven Verification" (CryptoQuant style).
Task: Implement `MarketVerifier` using Binance API.

Requirements:
1. Logic (`services/truth_engine/market_check.py`):
   - Only run this for news where `category_type` == 'MARKET_MOVE'.
   - Method `check_market_reality(symbol: str, publish_time: datetime, sentiment: str) -> dict`:
     - Fetch OHLCV data from Binance for the 4-hour window AFTER `publish_time`.
     - Metrics to check:
       - `Price Change %`.
       - `Volume Change %` (vs previous 4h).
     - **Verification Rules:**
       - If Sentiment='Bullish' AND Price increased > 1% AND Volume increased > 5%: Result = "VERIFIED".
       - If Sentiment='Bullish' BUT Price dropped > 2%: Result = "DEBUNKED" (False signal).
       - Else: Result = "NEUTRAL".
     - Return the result and the raw data (to save in `evidence_data`).

2. Constraint: Handle cases where the symbol is not listed on Binance (return "UNVERIFIABLE").

```

---

### 🗳️ Task 5.4: Logic "Smart User Reputation" (Trọng số người dùng)

**Mục đích:** Code logic tính điểm người dùng. Người vote đúng nhiều sẽ trở thành "Expert". Vote của Expert có giá trị cao hơn.

**Prompt 5.4 (Copy vào Copilot):**

```text
Role: Backend Logic Developer.
Context: Implementing User Reputation System (Nansen/StackOverflow style).
Task: Implement `UserReputationService` and Weighted Voting.

Requirements:
1. Database Update (`models/user.py`):
   - Add `reputation_score` (Int, default 100).
   - Add `correct_votes` (Int), `total_votes` (Int).

2. Logic (`services/voting.py`):
   - **Weight Calculation:**
     - `vote_power = log10(reputation_score)`. (Example: Score 100 = Power 2, Score 1000 = Power 3).
     - Pro Tier users get `vote_power * 1.5`.
   - **Reputation Update Logic (Run nightly):**
     - For each resolved news (Verified/Debunked):
       - If User voted "Trust" and news is "VERIFIED": User Score += 10.
       - If User voted "Trust" but news is "DEBUNKED": User Score -= 20 (Penalty for supporting fake news).
       - Clamp score: Min 0.

3. API Update: When fetching vote counts for a news item, sum the `vote_power`, not just the raw count.

```

---

### 🏆 Task 5.5: Logic Tính điểm Trust Score Nguồn tin (Công thức tổng hợp)

**Mục đích:** Code công thức cuối cùng để xếp hạng nguồn tin. Đây là "Hồ sơ năng lực" của nguồn tin.

**Prompt 5.5 (Copy vào Copilot):**

```text
Role: Data Scientist / Python Developer.
Context: Calculating the final "Trust Score" for each News Source based on evidence.
Task: Implement the `TrustScoreEngine`.

Requirements:
1. Logic (`services/truth_engine/scorer.py`):
   - Method `calculate_source_trust(source_id: int) -> float`:
     - Fetch all news from this source in the last 30 days.
     - **Metrics:**
       - `Verification_Rate`: (Count of VERIFIED / Total Market/Project News).
       - `Tier1_Alignment`: How often do they match Tier 1 sources?
       - `Community_Approval`: Average weighted vote ratio.
     - **Formula:**
       - `Raw_Score = (Verification_Rate * 0.5) + (Tier1_Alignment * 0.3) + (Community_Approval * 0.2)`.
       - Scale to 0-10.
   - Execution: Run this as a background job every 24 hours.

2. Action:
   - If `Trust Score` drops below 3.0: Automatically set `Source.is_active = False`.
   - If `Trust Score` > 8.0: Mark source as `GOLD_TIER` (High priority display in UI).

```

---

===============================================================================================================================


Để AI và hệ thống hiểu ai là "Tier 1", chúng ta cần định danh dựa trên **Domain (Tên miền)** hoặc **Identity** cố định.

Dưới đây là danh sách cụ thể các nguồn **Tier 1 (Uy tín tuyệt đối)** trong thị trường Crypto, được chia theo nhóm để hệ thống kiểm chứng chéo hiệu quả hơn.

---

### 🏛️ Danh sách Nguồn Tier 1 (Cấu hình cứng cho hệ thống)

Bạn hãy cung cấp danh sách này cho AI để nó tạo ra một `Config File` hoặc `Seeder` khởi tạo ban đầu.

#### Nhóm A: Báo chí Tài chính Chính thống (Mainstream Finance)

*Dùng để kiểm chứng các tin tức vĩ mô, pháp lý (SEC, ETF), dòng tiền lớn.*

1. **Bloomberg Crypto** (`bloomberg.com/crypto`)
2. **Reuters** (`reuters.com`)
3. **CNBC Crypto** (`cnbc.com/cryptoworld`)
4. **Forbes Digital Assets** (`forbes.com/digital-assets`)

#### Nhóm B: Báo chí Crypto Chuyên sâu (Top-tier Crypto Journalism)

*Dùng để kiểm chứng tin tức thị trường, dự án, scandal.*
5.  **CoinDesk** (`coindesk.com`) - *Tiêu chuẩn vàng về báo chí crypto.*
6.  **The Block** (`theblock.co`) - *Nổi tiếng với dữ liệu chuyên sâu.*
7.  **Decrypt** (`decrypt.co`)
8.  **CoinTelegraph** (`cointelegraph.com`) - *Tốc độ nhanh nhất (tuy nhiên cần cẩn thận vì đôi khi giật tít, nhưng độ phủ sóng là số 1).*

#### Nhóm C: Dữ liệu & Nghiên cứu (Data & Research)

*Dùng để kiểm chứng tin đồn về On-chain, Hack, Smart Money.*
9.  **Glassnode Insights** (`insights.glassnode.com`)
10. **Messari** (`messari.io`)
11. **PeckShieldAlert** (Nguồn X/Twitter) - *Số 1 về bảo mật/Hack.*
12. **ZachXBT** (Nguồn X/Mirror) - *Thám tử on-chain uy tín nhất.*

#### Nhóm D: Nguồn Chính chủ (Official Foundations)

*Dùng để kiểm chứng tin nâng cấp kỹ thuật (Project Update).*
13. **Ethereum Foundation Blog** (`blog.ethereum.org`)
14. **Bitcoin Core** (`bitcoincore.org`)
15. **Solana Blog** (`solana.com/news`)

---

### 🛠️ Prompt 5.2 (Đã cập nhật chi tiết)

Chúng ta sẽ yêu cầu AI tạo ra một file cấu hình chứa danh sách này và viết logic: **"Nếu domain của bài viết thuộc danh sách này -> Auto Trust"**.

**Prompt 5.2 (Copy vào Copilot):**

```text
Role: Python Data Engineer.
Context: Implementing the "Proof of Source" logic. We cannot rely on random DB IDs. We must identify Tier 1 sources by their fixed Domains/Identities.
Task: Implement `Tier1Registry` and Update Consensus Logic.

Requirements:
1. Configuration (`config/tier1_sources.py`):
   - Define a dictionary `TIER_1_DOMAINS` grouping sources by category:
     ```python
     TIER_1_DOMAINS = {
         "MAINSTREAM": ["bloomberg.com", "reuters.com", "cnbc.com", "forbes.com"],
         "CRYPTO_JOURNALISM": ["coindesk.com", "theblock.co", "decrypt.co", "cointelegraph.com"],
         "DATA_RESEARCH": ["glassnode.com", "messari.io"],
         "OFFICIAL": ["blog.ethereum.org", "solana.com", "bitcoincore.org"]
     }
     # Flatten list for easy searching
     ALL_TIER_1_DOMAINS = [d for sublist in TIER_1_DOMAINS.values() for d in sublist]
     ```

2. Database Seeder (`scripts/seed_tier1.py`):
   - Write a script to check `Source` table.
   - For each domain in `ALL_TIER_1_DOMAINS`:
     - If it exists in DB: Update `trust_score` = 9.5 and `is_tier1` = True.
     - If not exists: Create a placeholder Source with `trust_score` = 9.5.

3. Logic Update (`services/truth_engine/cross_check.py`):
   - Method `is_tier1_source(url: str) -> bool`:
     - Extract domain from URL.
     - Return True if domain is in `ALL_TIER_1_DOMAINS`.
   
   - Method `verify_consensus(target_news: News) -> dict`:
     - **Step 1:** Check if `target_news` itself is from a Tier 1 source (using `is_tier1_source`).
       - If YES: Return `{'status': 'VERIFIED', 'reason': 'Direct report from Tier 1 Source'}`.
     - **Step 2:** If NO (it's from a small blog/Twitter):
       - Query DB for other news items in the last 12h.
       - Filter items where `is_tier1_source(item.url)` is True.
       - Use NLP/Fuzzy match to find if any Tier 1 news covers the same topic.
       - If match found: Return `{'status': 'VERIFIED', 'reason': 'Confirmed by Tier 1 consensus'}`.
       - Else: Return `{'status': 'UNVERIFIED', 'reason': 'No Tier 1 coverage found yet'}`.

4. Constraint: The domain matching must be robust (handle subdomains e.g., `crypto.news.yahoo.com` matches `yahoo.com`).



### 💡 Tại sao làm thế này lại Tốt hơn?

1. **Minh bạch:** Bạn nhìn vào code là biết ngay ai là "Ông lớn".
2. **Linh hoạt:** Sau này muốn thêm "Binance Blog" vào Tier 1, bạn chỉ cần thêm string `"binance.com"` vào file config, không cần sửa DB ID.
3. **Chính xác:** Hệ thống sẽ tự động nâng điểm uy tín cho các nguồn này ngay từ đầu.

Bạn hãy dùng Prompt này nhé, nó sẽ giải quyết triệt để vấn đề "AI không biết ai là ai".


====================================================================================================================================


Việc tách danh sách này ra file `JSON` bên ngoài giúp bạn có thể cập nhật danh sách nguồn uy tín này bất cứ lúc nào (thậm chí cập nhật nóng - Hot Reload) mà không đụng vào Source Code.

Dưới đây là **Prompt 5.2 đã được điều chỉnh** theo hướng **Dynamic Configuration**.

---

### 🔗 Task 5.2 (Adjusted): Load cấu hình Tier 1 từ JSON & Kiểm chứng chéo

**Mục đích:** Xây dựng file cấu hình `tier1_sources.json` và code logic để hệ thống đọc danh sách này khi khởi động.

**Prompt 5.2 (Copy vào Copilot):**

```text
Role: Python Backend Developer.
Context: Implementing "Proof of Source" logic. The list of Tier 1 Trusted Sources must be dynamic and configurable via an external JSON file, NOT hardcoded in Python.
Task: Implement JSON Config Loader and Tier 1 Verification Service.

Requirements:
1. Configuration File (`config/tier1_sources.json`):
   - Create a JSON file with this structure (Add actual domains from Bloomberg, Reuters, CoinDesk, etc.):
     ```json
     {
       "MAINSTREAM": ["bloomberg.com", "reuters.com", "cnbc.com", "forbes.com"],
       "CRYPTO_JOURNALISM": ["coindesk.com", "theblock.co", "decrypt.co", "cointelegraph.com"],
       "DATA_RESEARCH": ["glassnode.com", "messari.io"],
       "OFFICIAL": ["ethereum.org", "solana.com", "bitcoincore.org", "sec.gov"]
     }
     ```

2. Config Loader (`core/config_loader.py`):
   - Implement a utility function `load_tier1_domains() -> List[str]`:
     - Open `config/tier1_sources.json`.
     - Parse the JSON.
     - Flatten all lists into a single set of domains for O(1) lookup.
     - Handle `FileNotFoundError` or `JSONDecodeError` gracefully (Log error and return empty list to prevent crash).

3. Logic Update (`services/truth_engine/cross_check.py`):
   - Initialize the `TIER_1_SET` using `load_tier1_domains()` at service startup.
   - Method `is_tier1_source(url: str) -> bool`:
     - Extract domain from URL (handle `www.` or subdomains).
     - Check if it exists in `TIER_1_SET`.
   
   - Method `verify_consensus(target_news: News) -> dict`:
     - **Step 1:** Check if `target_news` itself is from a Tier 1 source.
       - If YES: Return `{'status': 'VERIFIED', 'reason': 'Direct report from Tier 1 Source'}`.
     - **Step 2:** If NO:
       - Query DB for other news items in the last 12h.
       - Check if any of them match `is_tier1_source(item.url)`.
       - Use Fuzzy matching on Titles.
       - If match found: Return `{'status': 'VERIFIED', 'reason': 'Confirmed by Tier 1 consensus'}`.

4. Constraint: Ensure the loader supports comments or ignores fields starting with "_" in JSON if we need to add metadata later.
```

### 📝 Ví dụ nội dung file `config/tier1_sources.json` mẫu:

Bạn hãy tạo file này và paste nội dung sau vào để hệ thống có dữ liệu chạy ngay:

```json
{
  "_comment": "Danh sách các nguồn tin Tier 1 dùng để kiểm chứng sự thật",
  "MAINSTREAM": [
    "bloomberg.com",
    "reuters.com",
    "cnbc.com",
    "wsj.com",
    "forbes.com"
  ],
  "CRYPTO_JOURNALISM": [
    "coindesk.com",
    "theblock.co",
    "decrypt.co",
    "cointelegraph.com",
    "beincrypto.com",
    "cryptoslate.com"
  ],
  "DATA_RESEARCH": [
    "glassnode.com",
    "messari.io",
    "kaiko.com",
    "dune.com"
  ],
  "OFFICIAL_&_GOV": [
    "sec.gov",
    "cftc.gov",
    "ethereum.org",
    "blog.ethereum.org",
    "solana.com",
    "bitcoincore.org"
  ]
}

```



===================================================================================================================================


Nếu App chỉ hiển thị một danh sách tin tức trôi tuồn tuột theo thời gian (Chronological Order) thì nó chỉ là cái máy đọc RSS rẻ tiền. Để user trả tiền, App phải biết **sắp xếp**, **gom nhóm** và **nêu bật** những gì quan trọng nhất.

Dưới đây là **5 Task nâng cao (5.6 - 5.10)** tập trung hoàn toàn vào việc: **Tối ưu thuật toán hiển thị & Trải nghiệm đọc tin thông minh.**

---

### 📚 Task 5.6: Thuật toán Gom nhóm Tin tức (Story Clustering)

**Vấn đề:** Khi một sự kiện lớn xảy ra (ví dụ: "Binance niêm yết Token X"), sẽ có 50 nguồn cùng đưa tin. Nếu App hiện 50 dòng tin giống hệt nhau nối đuôi nhau, User sẽ thấy "Rác" (Spam).
**Giải pháp:** Gom tất cả lại thành 1 **"Chủ đề" (Story Cluster)**. Hiển thị 1 bài uy tín nhất (Tier 1), và ghi chú nhỏ bên dưới: *"Cũng được đưa tin bởi 49 nguồn khác"*.

**Prompt 5.6 (Copy vào Copilot):**

```text
Role: NLP Data Scientist.
Context: Cleaning up the user feed. Multiple sources report the same event. We need to group them into "Stories".
Task: Implement `NewsClusteringService`.

Requirements:
1. Database Update (`models/news.py`):
   - Add `cluster_id` (UUID, nullable).
   - Add `is_cluster_lead` (Boolean, default False).

2. Logic (`services/clustering.py`):
   - Run periodically (e.g., every 10 mins) on recent news (last 24h).
   - Algorithm:
     - Fetch news with `cluster_id` IS NULL.
     - Compare embedding vectors (or use simple TF-IDF/Jaccard Similarity on Titles) with existing clusters from the last 6 hours.
     - Threshold: If Similarity > 75% -> Assign same `cluster_id`.
     - **Leader Selection:** Within a cluster, pick the news item with the highest `Source.trust_score` as the `is_cluster_lead=True`. All others become children.
   
3. API Output (`routers/news.py`):
   - When calling `GET /news`:
     - Only return items where `is_cluster_lead=True` (or items with no cluster).
     - Include a field `related_count` (number of other items in the cluster).
     - This drastically cleans up the UI.

```

---

### 🔥 Task 5.7: Thuật toán "Ranking Nóng" (The 'Hotness' Score)

**Vấn đề:** Sắp xếp theo thời gian (Mới nhất) không phải lúc nào cũng tốt. Một tin "Sập sàn" cách đây 2 tiếng quan trọng hơn một tin "Update nhỏ" cách đây 5 phút.
**Giải pháp:** Áp dụng thuật toán giống **Hacker News** hoặc **Reddit**: `Điểm Nóng = (Trust * Impact) / (Thời gian + 2)^Gravity`.

**Prompt 5.7 (Copy vào Copilot):**

```text
Role: Backend Algorithm Engineer.
Context: Sorting news to show "High Value" content first, not just "Newest".
Task: Implement Dynamic Ranking Algorithm.

Requirements:
1. Logic (`services/ranking.py`):
   - Define Formula: `Hot_Score = ( (Trust_Score * Impact_Score) + (User_Votes * 2) ) / pow((Age_In_Hours + 2), 1.5)`
   - `Trust_Score`: From Source (0-10).
   - `Impact_Score`: From AI (0-10).
   - `Age_In_Hours`: Time since published.
   - `1.5`: Gravity factor (Higher = News decays faster).

2. Database Optimization:
   - Since calculating this on the fly for thousands of rows is slow, create a Materialized View or a Cached Column `ranking_score` that updates every 5-10 minutes.

3. API Integration:
   - `GET /v1/news?sort=trending`: Order by `ranking_score DESC`.
   - `GET /v1/news?sort=latest`: Order by `published_at DESC`.

```

---

### 🌊 Task 5.8: Phát hiện "Sóng" thị trường (Narrative Detection)

**Vấn đề:** Thị trường Crypto chạy theo "Narrative" (Câu chuyện). Ví dụ: Tuần này là "AI Coins", tuần sau là "RWA". User muốn biết **Chủ đề nào đang hot nhất?**
**Giải pháp:** Phân tích tần suất từ khóa (Tags) tăng đột biến để phát hiện Trend.

**Prompt 5.8 (Copy vào Copilot):**

```text
Role: Data Analyst.
Context: Identifying current market narratives (Trending Topics).
Task: Implement `TrendDetectionService`.

Requirements:
1. Logic (`services/trends.py`):
   - Analyze `News.tags` and `News.category` from the last 24 hours vs the last 7 days.
   - Calculate **Velocity**: `(Count_Last_24h - Avg_Daily_Count) / Avg_Daily_Count`.
   - If Velocity > 2.0 (200% increase), mark as "Trending Narrative".
   
2. API Endpoint (`routers/trends.py`):
   - `GET /v1/trends/narratives`:
   - Returns list: `[{ "tag": "AI", "velocity": 3.5, "sample_news": [...] }, { "tag": "Solana", "velocity": 2.1 }]`.

3. UI Implication: Use this to display a "Hot Topics" bar at the top of the PWA.

```

---

### 🎯 Task 5.9: Cá nhân hóa dòng tin (Personalized Watchlist Feed)

**Vấn đề:** User giữ coin $SOL, họ không muốn lướt qua 100 tin về $ETH để tìm tin $SOL.
**Giải pháp:** Tính năng "Watchlist Priority".

**Prompt 5.9 (Copy vào Copilot):**

```text
Role: Backend Developer.
Context: Delivering personalized value to Pro Users.
Task: Implement Watchlist Filtering Logic.

Requirements:
1. Database Update (`models/user.py`):
   - Add `watchlist`: JSONB or Array of Strings (e.g., `["BTC", "ETH", "FET"]`).

2. API Logic (`routers/news.py`):
   - Endpoint: `GET /v1/news/feed?type=for_you`.
   - Logic:
     - Filter news where `detected_coins` overlaps with `user.watchlist`.
     - **Boost Logic:** Even in the "General Feed", if a news item matches the User's Watchlist, artificially increase its `ranking_score` (from Task 5.7) by factor 1.5x so it floats to the top for THAT specific user.
   
3. Constraint: Ensure good indexing on `detected_coins` (GIN Index in Postgres) for fast filtering.

```

---

### 📌 Task 5.10: "Ghim" của Ban biên tập (Editor's Choice / Pinned)

**Vấn đề:** Đôi khi thuật toán sai, hoặc có sự kiện "Thiên nga đen" (Black Swan) cực kỳ quan trọng mà Admin muốn ghim lên đầu bất chấp thuật toán.
**Giải pháp:** Quyền lực tối cao của Admin.

**Prompt 5.10 (Copy vào Copilot):**

```text
Role: CMS Developer.
Context: Manual override for important news.
Task: Implement Admin Pinning System.

Requirements:
1. Database Update:
   - Add column `is_pinned`: Boolean (default False).
   - Add column `pinned_until`: DateTime (nullable).

2. Admin API (`routers/admin.py`):
   - `POST /v1/admin/news/{id}/pin`: Body `{ "duration_hours": 4 }`.
   - Logic: Set `is_pinned=True` and `pinned_until = Now + 4h`.

3. Ranking Logic Update (Task 5.7):
   - Modify the Sort Order:
   - Always put `is_pinned=True` items at the VERY TOP, regardless of score or date.
   - Then follow `ranking_score`.

4. Auto-Unpin:
   - The Scheduler (Task 5.1) should check every hour: If `Now > pinned_until`, set `is_pinned=False`.

```

---

### 🏛️ TỔNG KẾT GIAI ĐOẠN 5 (10 TASKS) - CỖ MÁY SỰ THẬT HOÀN HẢO

Bây giờ Giai đoạn 5 của bạn đã cực kỳ mạnh mẽ. Nó không chỉ kiểm tra sự thật mà còn tối ưu hóa hiển thị để **thỏa mãn người dùng trả tiền**.

1. **Chất lượng (Quality):**
* Task 5.1: Phân loại tin.
* Task 5.2: Kiểm chứng Tier 1 (Config JSON).
* Task 5.3: Kiểm chứng Market Data.
* Task 5.4: User Reputation.
* Task 5.5: Scoring Nguồn tin.


2. **Hiển thị (Curated Experience):**
* Task 5.6: Gom nhóm (Chống Spam).
* Task 5.7: Ranking Nóng (Thuật toán HackerNews).
* Task 5.8: Bắt Trend (Narrative).
* Task 5.9: Cá nhân hóa (Watchlist).
* Task 5.10: Admin Ghim (Quyền lực biên tập).



=========================================================================================================================================

**Giai đoạn 6: Triển khai Hạ tầng & Vận hành (Deployment & DevOps)**.

Với tư cách là **Solo Dev**, mục tiêu của giai đoạn này là: **"Set and Forget" (Cài một lần, chạy mãi mãi)**. Bạn không muốn nửa đêm phải dậy reset server. Hệ thống phải tự động, bảo mật và tiết kiệm chi phí tối đa.

Tôi đề xuất mô hình **Docker Compose trên một VPS Linux** (như Hetzner hoặc DigitalOcean) kết hợp với **GitHub Actions** để tự động hóa việc deploy.

Dưới đây là 5 Task cốt lõi để đưa Coin87 lên Internet một cách chuyên nghiệp.

---

### 🐳 Task 6.1: Docker hóa toàn bộ ứng dụng (Containerization)

**Mục đích:** Đảm bảo code chạy trên máy bạn thế nào thì lên server chạy y hệt thế ấy. Không còn lỗi "It works on my machine".
**Cấu trúc:**

* Backend (FastAPI) -> Docker Image.
* Frontend (Next.js) -> Docker Image.
* Worker (Celery/AI) -> Docker Image (Tái sử dụng code Backend).

**Prompt 6.1 (Copy vào Copilot):**

```text
Role: DevOps Engineer.
Context: Preparing Coin87 for production deployment using Docker.
Task: Create Dockerfiles and docker-compose.yml.

Requirements:
1. Backend Dockerfile (`backend/Dockerfile`):
   - Use `python:3.11-slim`.
   - Install dependencies from `requirements.txt`.
   - Use Multi-stage build to keep image size small.
   - Command: `uvicorn main:app --host 0.0.0.0 --port 8000`.

2. Frontend Dockerfile (`frontend/Dockerfile`):
   - Use `node:18-alpine`.
   - Build Next.js app (`npm run build`).
   - Run in production mode (`npm start`).

3. Docker Compose (`docker-compose.prod.yml`):
   - Services: `db` (Postgres 16), `redis` (Redis 7), `api` (Backend), `worker` (AI/Crawl), `web` (Frontend).
   - Networking: All services share a `coin87-network`.
   - Volumes: Persist Postgres data (`pgdata:/var/lib/postgresql/data`) so we don't lose data on restart.
   - Environment: Load variables from `.env`.
   - Restart Policy: `always` (Auto-restart if crashes).

4. Constraint: Ensure the Backend waits for DB to be ready before starting (use `depends_on` or a `wait-for-it` script).

```

---

### 🛡️ Task 6.2: Thiết lập VPS & Bảo mật "Pháo đài" (Server Hardening)

**Mục đích:** Trước khi đưa code lên, server phải an toàn. Chúng ta cần cài đặt tường lửa, chặn SSH bằng mật khẩu (chỉ dùng Key), và cài đặt các công cụ cần thiết.

**Prompt 6.2 (Copy vào Copilot):**

```text
Role: System Administrator (Security Focus).
Context: Setting up a fresh Ubuntu VPS for a crypto application. Security is paramount.
Task: Create a Shell Script (`scripts/setup_server.sh`) to automate server hardening.

Requirements:
1. System Updates: `apt update && apt upgrade -y`.
2. Install Docker: Install Docker Engine and Docker Compose plugin officially.
3. Firewall (UFW):
   - Deny incoming by default.
   - Allow SSH (Port 22 - or custom port).
   - Allow HTTP (80) and HTTPS (443).
   - Enable UFW.
4. SSH Hardening:
   - Modify `/etc/ssh/sshd_config`.
   - `PasswordAuthentication no` (Force SSH Key).
   - `PermitRootLogin no` (Create a sudo user 'coin87_admin').
5. Fail2Ban: Install and configure to ban IPs that spam SSH login attempts.
6. Swap Memory: Create a 4GB Swap file (Critical for AI processing stability on low-RAM VPS).

```

---

### 🌐 Task 6.3: Cổng kết nối & SSL Tự động (Nginx & Certbot)

**Mục đích:** User truy cập qua domain `coin87.com` (HTTPS) thay vì `IP:3000`. Nginx sẽ đứng giữa làm "Lễ tân" điều phối request.

* Request vào `/v1/` -> Chuyển sang Backend Container.
* Request vào `/` -> Chuyển sang Frontend Container.

**Prompt 6.3 (Copy vào Copilot):**

```text
Role: DevOps / Network Engineer.
Context: Configuring Nginx as a Reverse Proxy with Auto-SSL.
Task: Create Nginx Config and Certbot setup.

Requirements:
1. Nginx Config (`nginx/conf.d/app.conf`):
   - Upstream definitions for `api_upstream` (port 8000) and `web_upstream` (port 3000).
   - Location `/v1/`: Proxy pass to `http://api_upstream`.
   - Location `/`: Proxy pass to `http://web_upstream`.
   - Security Headers: Add HSTS, X-Frame-Options, X-Content-Type-Options.

2. SSL Setup:
   - Use a helper container `certbot` in docker-compose.
   - Script to auto-renew Let's Encrypt certificates every 60 days.

3. Optimization: Enable Gzip compression in Nginx for faster JSON/HTML delivery.

```

---

### 🚀 Task 6.4: Pipeline Tự động hóa (CI/CD with GitHub Actions)

**Mục đích:** Bạn code xong -> Push lên GitHub -> **Hệ thống tự động**: Chạy test -> Build Docker Image -> Đẩy lên Server -> Restart lại App.
Không cần SSH vào server gõ lệnh thủ công nữa.

**Prompt 6.4 (Copy vào Copilot):**

```text
Role: DevOps Engineer (CI/CD Specialist).
Context: Automating the deployment workflow for a solo dev.
Task: Create GitHub Actions Workflow (`.github/workflows/deploy.yml`).

Requirements:
1. Trigger: On push to `main` branch.
2. Job 1: Build & Push:
   - Log in to Docker Hub (secrets.DOCKER_USERNAME).
   - Build `backend`, `frontend`, `worker` images.
   - Push images with tag `latest`.
3. Job 2: Deploy to VPS:
   - Use `appleboy/ssh-action` to SSH into the VPS.
   - Commands:
     - `cd /opt/coin87`.
     - `git pull`.
     - `docker-compose pull` (Get new images).
     - `docker-compose up -d` (Restart containers).
     - `docker system prune -f` (Clean up old images).

```

---

### 🚑 Task 6.5: Giám sát & Sao lưu (Monitoring & Backup)

**Mục đích:**

1. **Backup:** Dữ liệu người dùng (User, Ví tiền) là quan trọng nhất. Phải backup DB hàng ngày gửi lên Cloud (Google Drive/S3).
2. **Monitor:** Nếu App sập, Bot Telegram phải báo ngay cho bạn.

**Prompt 6.5 (Copy vào Copilot):**

```text
Role: Site Reliability Engineer (SRE).
Context: Ensuring data safety and uptime visibility.
Task: Implement Backup Script and Health Check Bot.

Requirements:
1. DB Backup Script (`scripts/backup_db.sh`):
   - Dump Postgres database to a compressed file (`pg_dump`).
   - Timestamp the filename.
   - Retention policy: Delete backups older than 7 days locally.
   - (Optional prompt) Suggest using `rclone` to sync this file to Google Drive.

2. Health Check Service (`services/monitor.py` - run as separate small container):
   - Loop every 1 minute.
   - Ping `https://coin87.com/v1/health`.
   - If status != 200:
     - Send Telegram Alert to Admin: "🚨 ALERT: Coin87 API is DOWN!".
   - Check Disk Space: If usage > 90%, send alert.

3. Cronjob: Add the backup script to the host's crontab to run daily at 03:00 AM.

```

---

### 🏁 TỔNG KẾT GIAI ĐOẠN 6

Sau khi hoàn thành 5 Task này, bạn sẽ có một hệ thống **Production-Grade**:

1. **Task 6.1:** Đóng gói gọn gàng (Docker).
2. **Task 6.2:** Nhà an toàn (VPS Hardening).
3. **Task 6.3:** Cổng chính chuyên nghiệp (HTTPS/Domain).
4. **Task 6.4:** Công nhân tự động (CI/CD).
5. **Task 6.5:** Bảo hiểm (Backup & Alert).

=====================================================================================================================================



### 💾 Task 7.1: Lưu vết Dữ liệu (Content Versioning)

**Mục đích:** Khi Crawler chạy lại và cập nhật nội dung (từ Snippet -> Full), hoặc khi AI chạy lại, chúng ta không được ghi đè (overwrite) mất dữ liệu cũ. Cần lưu lịch sử để lỡ AI chạy sai còn khôi phục được.

**Prompt 7.1 (Copy vào Copilot):**

```text
Role: Database Architect.
Context: We need to track changes in news content to prevent data loss and enable audit trails.
Task: Implement Content Versioning Strategy.

Requirements:
1. Database Schema (`models/history.py`):
   - Create table `NewsHistory`:
     - `id`: UUID.
     - `news_id`: ForeignKey to News.
     - `version_number`: Integer.
     - `content_snapshot`: Text (The raw content at that time).
     - `ai_analysis_snapshot`: JSONB (The AI result at that time).
     - `changed_by`: String (e.g., 'crawler_v1', 'ai_worker', 'admin').
     - `created_at`: DateTime.

2. Logic (`services/news_service.py`):
   - Before updating any `News` record (e.g., enriching content or saving AI result):
     - Copy the *current* state of the News record.
     - Insert into `NewsHistory`.
     - Increment `version_number`.
   - Only then perform the Update on the main table.

3. Goal: Ensure we can always rollback to the original RSS snippet if the enrichment process fails or produces garbage.

```

---

### 🧠 Task 7.2: Điểm tin cậy AI & Kiểm soát Ngân sách (AI Confidence & Cost Guard)

**Mục đích:**

1. AI phải biết "khiêm tốn". Nếu nó không chắc, nó phải báo `confidence: low`.
2. Tránh việc vòng lặp lỗi khiến AI gọi API liên tục làm "cháy túi" tiền API.

**Prompt 7.2 (Copy vào Copilot):**

```text
Role: AI Engineer / Backend Dev.
Context: improving AI reliability and cost control.
Task: Add Confidence Score and Budget Circuit Breaker.

Requirements:
1. Prompt Update (`services/ai/prompts.py`):
   - Update System Instruction: "You must provide a 'confidence_score' (0.0 to 1.0). If the news is vague, ambiguous, or lacks data, lower the score."
   - Update Pydantic Model: Add `confidence_score: float`.

2. Budget Logic (`services/ai/cost_guard.py`):
   - Redis Key: `ai_cost:monthly:{YYYY_MM}`.
   - Every time Gemini is called:
     - Estimate cost (Input chars + Output chars).
     - `INCRBY` the Redis key.
   - **Circuit Breaker:**
     - Define `MONTHLY_LIMIT_USD = 50`.
     - Before calling API: Check if current cost > Limit.
     - If Yes: Raise `BudgetExceededException` (Stop processing or switch to a free fallback model/logic).

3. UI Logic implication: If `confidence_score` < 0.6, display a "Low Confidence" badge on the UI to warn users.

```

---

### 🔥 Task 7.3: Cơ chế Đốt Token & Nền kinh tế $C87 (Token Sink)

**Mục đích:** Giải quyết lạm phát. User kiếm được $C87 thì phải có chỗ tiêu.

* **Tiêu tiền để:** Mở khóa phân tích sâu, Ghim bình luận, Đổi màu Nick.

**Prompt 7.3 (Copy vào Copilot):**

```text
Role: Game Designer / Backend Dev.
Context: Creating utility for the $C87 token to prevent inflation.
Task: Implement Token Spending Mechanics.

Requirements:
1. Database Update (`models/transaction.py`):
   - Add `TransactionType` enum: `EARN_VOTE`, `SPEND_UNLOCK`, `SPEND_BOOST`.

2. Logic (`routers/economy.py`):
   - Endpoint `POST /v1/economy/spend`:
     - Input: `{ "action": "UNLOCK_ALPHA", "news_id": 123 }`.
     - Cost: 50 $C87.
     - Logic:
       - Check user balance. If < 50, return 400.
       - Deduct 50 from `User.c87_balance`.
       - Log transaction.
       - Return success.

3. Frontend Integration:
   - On the News Detail page (Task 4.2), if User is Free Tier but wants to see the AI Verdict:
   - Show button: "Unlock this analysis for 50 $C87".
   - This creates a "Micro-transaction" loop without real money.

```

---

### 🖼️ Task 7.4: Dynamic SEO & Social Sharing (Open Graph)

**Mục đích:** Để khi user share link lên Facebook/Zalo, nó hiện ra cái ảnh đẹp lung linh (chứa Giá coin + Tiêu đề + Logo), chứ không phải cái ảnh trơn tuột. Đây là cách kéo traffic miễn phí tốt nhất.

**Prompt 7.4 (Copy vào Copilot):**

```text
Role: Next.js Developer.
Context: Optimizing social sharing (OG Images).
Task: Implement Dynamic Open Graph Images using `@vercel/og`.

Requirements:
1. Implementation (`app/news/[id]/opengraph-image.tsx`):
   - Use `ImageResponse` from `next/og`.
   - Fetch news details (Title, Sentiment, Source).
   - **Design:**
     - Background: Dark Gradient.
     - Text: Large Title.
     - Badge: "Bullish" (Green) or "Bearish" (Red).
     - Footer: "Read on Coin87".
   - Logic: This generates a PNG on the fly when a bot (Facebook/Twitter crawler) hits the URL.

2. Metadata (`app/news/[id]/page.tsx`):
   - Ensure `generateMetadata` function correctly points to this dynamic image route.

```

---

### 🤖 Task 7.5: Bot "Mồi lửa" (Cold Start Seeder)

**Mục đích:** Giải quyết vấn đề "App vắng tanh như chùa bà đanh" ngày đầu ra mắt.
Bot sẽ tự động vote dựa trên Sentiment của AI để tạo cảm giác cộng đồng sôi động.

**Prompt 7.5 (Copy vào Copilot):**

```text
Role: Python Automation Script.
Context: Solving the "Cold Start" problem. We need initial activity on the platform.
Task: Implement Seeder Bots.

Requirements:
1. Logic (`scripts/seeder_bot.py`):
   - Create 5-10 "System Users" (Bots) in the DB with generic names.
   - Run a schedule (every 30 mins).
   - Scan recent news (last 2 hours) with 0 votes.
   - **Decision Logic:**
     - If AI Sentiment is 'Bullish' and Confidence > 0.8:
       - Bots randomly vote "Trust" (3-5 votes).
     - If AI Sentiment is 'Bearish':
       - Bots randomly vote "FUD" (Trust/Fake logic).
   - **Constraint:** Randomize the timing so they don't all vote at the exact same second.

2. Goal: Ensure new users see some activity bars, encouraging them to join the voting (Herd Mentality).

```

---

### 🛡️ Task 7.6: Quản lý Migration (Database Ops)

**Mục đích:** Trong quá trình phát triển, bạn sẽ sửa DB liên tục (thêm cột, sửa bảng). Nếu không có công cụ quản lý, DB sẽ bị lỗi.
Sử dụng **Alembic** để quản lý thay đổi DB an toàn.

**Prompt 7.6 (Copy vào Copilot):**

```text
Role: Python DevOps.
Context: Managing database schema changes safely.
Task: Initialize and Configure Alembic.

Requirements:
1. Setup:
   - Install `alembic`.
   - Run `alembic init alembic`.
   - Configure `alembic.ini` to read the Database URL from `.env`.

2. Integration:
   - Update `alembic/env.py` to import your SQLAlchemy `Base` model.
   - This allows Alembic to "autogenerate" migrations by comparing code vs database.

3. Workflow Documentation:
   - Create a `README_DB.md` explaining the steps:
     1. Change model in python code.
     2. Run `alembic revision --autogenerate -m "Added trust score"`.
     3. Run `alembic upgrade head`.

```

---

### 🏁 TỔNG KẾT GIAI ĐOẠN 7 (HOÀN THIỆN)

Bây giờ bộ hồ sơ dự án của bạn đã **Vô cùng hoàn chỉnh**.

1. **Lưu vết (Task 7.1):** Không sợ mất dữ liệu.
2. **Thông minh & Tiết kiệm (Task 7.2):** AI chạy ổn định, không đốt tiền.
3. **Kinh tế (Task 7.3):** Token $C87 có giá trị thực tế trong App.
4. **Lan truyền (Task 7.4):** Share link đẹp, hút user.
5. **Mồi lửa (Task 7.5):** App luôn sôi động.
6. **An toàn (Task 7.6):** Sửa DB không sợ lỗi.



=========================================================================================================================================


### 🤖 Task 7.5 (Revised): Bot Mồi An toàn (The Ethical Seeder)

**Mục đích:** Tạo hiệu ứng đám đông ban đầu (Cold Start) nhưng **cô lập hoàn toàn** dữ liệu của Bot khỏi thuật toán đánh giá sự thật (Truth Engine) và Reputation System. Bot chỉ để "làm đẹp đội hình" (Visual only), không có quyền quyết định đúng sai.

**Prompt 7.5 (Copy vào Copilot):**

```text
Role: Database Architect & Python Backend Dev.
Context: Implementing Seeder Bots to solve "Cold Start". We need absolute data separation between Human and Bot activities for future ML training and Audit.
Task: Implement Seeder Bots with Explicit Data Tagging.

Requirements:
1. Database Schema Update (`models/vote.py`):
   - Define Enum: `VoteOrigin` = ['HUMAN', 'SYSTEM_BOT'].
   - Update `Vote` table:
     - Add column `origin`: Enum(VoteOrigin), default='HUMAN'.
     - Add Index on `origin` for fast filtering.
   - (Keep `is_system_bot` in User table for account management, but rely on `Vote.origin` for analytics).

2. Seeder Logic (`scripts/seeder_bot.py`):
   - When the bot casts a vote, explicitly set `origin='SYSTEM_BOT'`.
   - Sunset Logic: Stop running if `App_Launch_Date > 14 days` OR `Real_User_Activity > Threshold`.

3. Query Logic (The "Firewall"):
   - **For UI (News Feed Counters):**
     - `SELECT COUNT(*) FROM votes` (Include everything to show big numbers).
   - **For Truth Engine / Reputation (Phase 5):**
     - `SELECT COUNT(*) FROM votes WHERE origin = 'HUMAN'` (STRICTLY exclude bots).
   - **For User Activity Feeds / Public Profiles:**
     - `SELECT * FROM votes WHERE origin = 'HUMAN'` (Bots should be invisible ghost workers).

4. Constraint: Ensure that if a Human clicks on a Bot's profile (if accessible), they see "No recent activity" or a generic placeholder, never a list of automated votes.
```

### 🛡️ Phân tích độ an toàn sau khi sửa:

1. **Cách ly dữ liệu:** Dù Bot có vote 1 triệu lần, thì `Trust Score` của nguồn tin vẫn không đổi. Bot chỉ tạo hiệu ứng tâm lý (Visual) cho User mới vào thấy "đông vui".
2. **Tự động nhường sân:** Code có đoạn check `Organic activity`. Khi người thật bắt đầu vào chơi (ví dụ: có > 50 vote thật/giờ), Bot tự động "biết điều" đi ngủ để không làm loãng cộng đồng.
3. **Cơ chế tự hủy (Sunset):** Sau 14 ngày, script tự động tắt vĩnh viễn. Coin87 sẽ quay về trạng thái organic 100%.