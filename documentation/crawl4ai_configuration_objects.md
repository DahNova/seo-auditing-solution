# Crawl4AI Custom LLM Context
Generated on: 2025-06-15T06:14:25.764Z
Total files: 3

---

## Configuration Objects - Memory
Source: crawl4ai_config_objects_memory_content.llm.md

# Detailed Outline for crawl4ai - config_objects Component

**Target Document Type:** memory
**Target Output Filename Suggestion:** `llm_memory_config_objects.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2024-05-24
---

## 1. Introduction to Configuration Objects in Crawl4ai

*   **1.1. Purpose of Configuration Objects**
    *   Explanation: Configuration objects in `crawl4ai` serve to centralize and manage settings for various components and behaviors of the library. This includes browser setup, individual crawl run parameters, LLM provider interactions, proxy settings, and more.
    *   Benefit: This approach enhances code readability by grouping related settings, improves maintainability by providing a clear structure for configurations, and offers ease of customization for users to tailor the library's behavior to their specific needs.
*   **1.2. General Principles and Usage**
    *   **1.2.1. Immutability/Cloning:**
        *   Concept: Most configuration objects are designed with a `clone()` method, allowing users to create modified copies without altering the original configuration instance. This promotes safer state management, especially when reusing base configurations for multiple tasks.
        *   Method: `clone(**kwargs)` on most configuration objects.
    *   **1.2.2. Serialization and Deserialization:**
        *   Concept: `crawl4ai` configuration objects can be serialized to dictionary format (e.g., for saving to JSON) and deserialized back into their respective class instances.
        *   Methods:
            *   `dump() -> dict`: Serializes the object to a dictionary suitable for JSON, often using the internal `to_serializable_dict` helper.
            *   `load(data: dict) -> ConfigClass` (Static Method): Deserializes an object from a dictionary, often using the internal `from_serializable_dict` helper.
            *   `to_dict() -> dict`: Converts the object to a standard Python dictionary.
            *   `from_dict(data: dict) -> ConfigClass` (Static Method): Creates an instance from a standard Python dictionary.
        *   Helper Functions:
            *   `crawl4ai.async_configs.to_serializable_dict(obj: Any, ignore_default_value: bool = False) -> Dict`: Recursively converts objects into a serializable dictionary format, handling complex types like enums and nested objects.
            *   `crawl4ai.async_configs.from_serializable_dict(data: Any) -> Any`: Reconstructs Python objects from the serializable dictionary format.
*   **1.3. Scope of this Document**
    *   Statement: This document provides a factual API reference for the primary configuration objects within the `crawl4ai` library, detailing their purpose, initialization parameters, attributes, and key methods.

## 2. Core Configuration Objects

### 2.1. `BrowserConfig`
Located in `crawl4ai.async_configs`.

*   **2.1.1. Purpose:**
    *   Description: The `BrowserConfig` class is used to configure the settings for a browser instance and its associated contexts when using browser-based crawler strategies like `AsyncPlaywrightCrawlerStrategy`. It centralizes all parameters that affect the creation and behavior of the browser.
*   **2.1.2. Initialization (`__init__`)**
    *   Signature:
        ```python
        class BrowserConfig:
            def __init__(
                self,
                browser_type: str = "chromium",
                headless: bool = True,
                browser_mode: str = "dedicated",
                use_managed_browser: bool = False,
                cdp_url: Optional[str] = None,
                use_persistent_context: bool = False,
                user_data_dir: Optional[str] = None,
                chrome_channel: Optional[str] = "chromium", # Note: 'channel' is preferred
                channel: Optional[str] = "chromium",
                proxy: Optional[str] = None,
                proxy_config: Optional[Union[ProxyConfig, dict]] = None,
                viewport_width: int = 1080,
                viewport_height: int = 600,
                viewport: Optional[dict] = None,
                accept_downloads: bool = False,
                downloads_path: Optional[str] = None,
                storage_state: Optional[Union[str, dict]] = None,
                ignore_https_errors: bool = True,
                java_script_enabled: bool = True,
                sleep_on_close: bool = False,
                verbose: bool = True,
                cookies: Optional[List[dict]] = None,
                headers: Optional[dict] = None,
                user_agent: Optional[str] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36",
                user_agent_mode: Optional[str] = "",
                user_agent_generator_config: Optional[dict] = None, # Default is {} in __init__
                text_mode: bool = False,
                light_mode: bool = False,
                extra_args: Optional[List[str]] = None,
                debugging_port: int = 9222,
                host: str = "localhost"
            ): ...
        ```
    *   Parameters:
        *   `browser_type (str, default: "chromium")`: Specifies the browser engine to use. Supported values: `"chromium"`, `"firefox"`, `"webkit"`.
        *   `headless (bool, default: True)`: If `True`, runs the browser without a visible GUI. Set to `False` for debugging or visual interaction.
        *   `browser_mode (str, default: "dedicated")`: Defines how the browser is initialized. Options: `"builtin"` (uses built-in CDP), `"dedicated"` (new instance each time), `"cdp"` (connects to an existing CDP endpoint specified by `cdp_url`), `"docker"` (runs browser in a Docker container).
        *   `use_managed_browser (bool, default: False)`: If `True`, launches the browser using a managed approach (e.g., via CDP or Docker), allowing for more advanced control. Automatically set to `True` if `browser_mode` is `"builtin"`, `"docker"`, or if `cdp_url` is provided, or if `use_persistent_context` is `True`.
        *   `cdp_url (Optional[str], default: None)`: The URL for the Chrome DevTools Protocol (CDP) endpoint. If not provided and `use_managed_browser` is active, it might be set by an internal browser manager.
        *   `use_persistent_context (bool, default: False)`: If `True`, uses a persistent browser context (profile), saving cookies, localStorage, etc., across sessions. Requires `user_data_dir`. Sets `use_managed_browser=True`.
        *   `user_data_dir (Optional[str], default: None)`: Path to a directory for storing user data for persistent sessions. If `None` and `use_persistent_context` is `True`, a temporary directory might be used.
        *   `chrome_channel (Optional[str], default: "chromium")`: Specifies the Chrome channel (e.g., "chrome", "msedge", "chromium-beta"). Only applicable if `browser_type` is "chromium".
        *   `channel (Optional[str], default: "chromium")`: Preferred alias for `chrome_channel`. Set to `""` for Firefox or WebKit.
        *   `proxy (Optional[str], default: None)`: A string representing the proxy server URL (e.g., "http://username:password@proxy.example.com:8080").
        *   `proxy_config (Optional[Union[ProxyConfig, dict]], default: None)`: A `ProxyConfig` object or a dictionary specifying detailed proxy settings. Overrides the `proxy` string if both are provided.
        *   `viewport_width (int, default: 1080)`: Default width of the browser viewport in pixels.
        *   `viewport_height (int, default: 600)`: Default height of the browser viewport in pixels.
        *   `viewport (Optional[dict], default: None)`: A dictionary specifying viewport dimensions, e.g., `{"width": 1920, "height": 1080}`. If set, overrides `viewport_width` and `viewport_height`.
        *   `accept_downloads (bool, default: False)`: If `True`, allows files to be downloaded by the browser.
        *   `downloads_path (Optional[str], default: None)`: Directory path where downloaded files will be stored. Required if `accept_downloads` is `True`.
        *   `storage_state (Optional[Union[str, dict]], default: None)`: Path to a JSON file or a dictionary containing the browser's storage state (cookies, localStorage, etc.) to load.
        *   `ignore_https_errors (bool, default: True)`: If `True`, HTTPS certificate errors will be ignored.
        *   `java_script_enabled (bool, default: True)`: If `True`, JavaScript execution is enabled on web pages.
        *   `sleep_on_close (bool, default: False)`: If `True`, introduces a small delay before the browser is closed.
        *   `verbose (bool, default: True)`: If `True`, enables verbose logging for browser operations.
        *   `cookies (Optional[List[dict]], default: None)`: A list of cookie dictionaries to be set in the browser context. Each dictionary should conform to Playwright's cookie format.
        *   `headers (Optional[dict], default: None)`: A dictionary of additional HTTP headers to be sent with every request made by the browser.
        *   `user_agent (Optional[str], default: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36")`: The User-Agent string the browser will use.
        *   `user_agent_mode (Optional[str], default: "")`: Mode for generating the User-Agent string. If set (e.g., to "random"), `user_agent_generator_config` can be used.
        *   `user_agent_generator_config (Optional[dict], default: {})`: Configuration dictionary for the User-Agent generator if `user_agent_mode` is active.
        *   `text_mode (bool, default: False)`: If `True`, attempts to disable images and other rich content to potentially speed up loading for text-focused crawls.
        *   `light_mode (bool, default: False)`: If `True`, disables certain background browser features for potential performance gains.
        *   `extra_args (Optional[List[str]], default: None)`: A list of additional command-line arguments to pass to the browser executable upon launch.
        *   `debugging_port (int, default: 9222)`: The port to use for the browser's remote debugging protocol (CDP).
        *   `host (str, default: "localhost")`: The host on which the browser's remote debugging protocol will listen.
*   **2.1.3. Key Public Attributes/Properties:**
    *   All parameters listed in `__init__` are available as public attributes with the same names and types.
    *   `browser_hint (str)`: [Read-only] - A string representing client hints (Sec-CH-UA) generated based on the `user_agent` string. This is automatically set during initialization.
*   **2.1.4. Key Public Methods:**
    *   `from_kwargs(cls, kwargs: dict) -> BrowserConfig` (Static Method):
        *   Purpose: Creates a `BrowserConfig` instance from a dictionary of keyword arguments.
    *   `to_dict(self) -> dict`:
        *   Purpose: Converts the `BrowserConfig` instance into a dictionary representation.
    *   `clone(self, **kwargs) -> BrowserConfig`:
        *   Purpose: Creates a deep copy of the current `BrowserConfig` instance. Keyword arguments can be provided to override specific attributes in the new instance.
    *   `dump(self) -> dict`:
        *   Purpose: Serializes the `BrowserConfig` object into a dictionary format that is suitable for JSON storage or transmission, utilizing the `to_serializable_dict` helper.
    *   `load(cls, data: dict) -> BrowserConfig` (Static Method):
        *   Purpose: Deserializes a `BrowserConfig` object from a dictionary (typically one created by `dump()`), utilizing the `from_serializable_dict` helper.

### 2.2. `CrawlerRunConfig`
Located in `crawl4ai.async_configs`.

*   **2.2.1. Purpose:**
    *   Description: The `CrawlerRunConfig` class encapsulates all settings that control the behavior of a single crawl operation performed by `AsyncWebCrawler.arun()` or multiple operations within `AsyncWebCrawler.arun_many()`. This includes parameters for content processing, page interaction, caching, and media handling.
*   **2.2.2. Initialization (`__init__`)**
    *   Signature:
        ```python
        class CrawlerRunConfig:
            def __init__(
                self,
                url: Optional[str] = None,
                word_count_threshold: int = MIN_WORD_THRESHOLD,
                extraction_strategy: Optional[ExtractionStrategy] = None,
                chunking_strategy: Optional[ChunkingStrategy] = RegexChunking(),
                markdown_generator: Optional[MarkdownGenerationStrategy] = DefaultMarkdownGenerator(),
                only_text: bool = False,
                css_selector: Optional[str] = None,
                target_elements: Optional[List[str]] = None, # Default is [] in __init__
                excluded_tags: Optional[List[str]] = None, # Default is [] in __init__
                excluded_selector: Optional[str] = "", # Default is "" in __init__
                keep_data_attributes: bool = False,
                keep_attrs: Optional[List[str]] = None, # Default is [] in __init__
                remove_forms: bool = False,
                prettify: bool = False,
                parser_type: str = "lxml",
                scraping_strategy: Optional[ContentScrapingStrategy] = None, # Instantiated with WebScrapingStrategy() if None
                proxy_config: Optional[Union[ProxyConfig, dict]] = None,
                proxy_rotation_strategy: Optional[ProxyRotationStrategy] = None,
                locale: Optional[str] = None,
                timezone_id: Optional[str] = None,
                geolocation: Optional[GeolocationConfig] = None,
                fetch_ssl_certificate: bool = False,
                cache_mode: CacheMode = CacheMode.BYPASS,
                session_id: Optional[str] = None,
                shared_data: Optional[dict] = None,
                wait_until: str = "domcontentloaded",
                page_timeout: int = PAGE_TIMEOUT,
                wait_for: Optional[str] = None,
                wait_for_timeout: Optional[int] = None,
                wait_for_images: bool = False,
                delay_before_return_html: float = 0.1,
                mean_delay: float = 0.1,
                max_range: float = 0.3,
                semaphore_count: int = 5,
                js_code: Optional[Union[str, List[str]]] = None,
                js_only: bool = False,
                ignore_body_visibility: bool = True,
                scan_full_page: bool = False,
                scroll_delay: float = 0.2,
                process_iframes: bool = False,
                remove_overlay_elements: bool = False,
                simulate_user: bool = False,
                override_navigator: bool = False,
                magic: bool = False,
                adjust_viewport_to_content: bool = False,
                screenshot: bool = False,
                screenshot_wait_for: Optional[float] = None,
                screenshot_height_threshold: int = SCREENSHOT_HEIGHT_THRESHOLD,
                pdf: bool = False,
                capture_mhtml: bool = False,
                image_description_min_word_threshold: int = IMAGE_DESCRIPTION_MIN_WORD_THRESHOLD,
                image_score_threshold: int = IMAGE_SCORE_THRESHOLD,
                table_score_threshold: int = 7,
                exclude_external_images: bool = False,
                exclude_all_images: bool = False,
                exclude_social_media_domains: Optional[List[str]] = None, # Uses SOCIAL_MEDIA_DOMAINS if None
                exclude_external_links: bool = False,
                exclude_social_media_links: bool = False,
                exclude_domains: Optional[List[str]] = None, # Default is [] in __init__
                exclude_internal_links: bool = False,
                verbose: bool = True,
                log_console: bool = False,
                capture_network_requests: bool = False,
                capture_console_messages: bool = False,
                method: str = "GET",
                stream: bool = False,
                check_robots_txt: bool = False,
                user_agent: Optional[str] = None,
                user_agent_mode: Optional[str] = None,
                user_agent_generator_config: Optional[dict] = None, # Default is {} in __init__
                deep_crawl_strategy: Optional[DeepCrawlStrategy] = None,
                experimental: Optional[Dict[str, Any]] = None # Default is {} in __init__
            ): ...
        ```
    *   Parameters:
        *   `url (Optional[str], default: None)`: The target URL for this specific crawl run.
        *   `word_count_threshold (int, default: MIN_WORD_THRESHOLD)`: Minimum word count for a text block to be considered significant during content processing.
        *   `extraction_strategy (Optional[ExtractionStrategy], default: None)`: Strategy for extracting structured data from the page. If `None`, `NoExtractionStrategy` is used.
        *   `chunking_strategy (Optional[ChunkingStrategy], default: RegexChunking())`: Strategy to split content into chunks before extraction.
        *   `markdown_generator (Optional[MarkdownGenerationStrategy], default: DefaultMarkdownGenerator())`: Strategy for converting HTML to Markdown.
        *   `only_text (bool, default: False)`: If `True`, attempts to extract only textual content, potentially ignoring structural elements beneficial for rich Markdown.
        *   `css_selector (Optional[str], default: None)`: A CSS selector defining the primary region of the page to focus on for content extraction. The raw HTML is reduced to this region.
        *   `target_elements (Optional[List[str]], default: [])`: A list of CSS selectors. If provided, only the content within these elements will be considered for Markdown generation and structured data extraction. Unlike `css_selector`, this does not reduce the raw HTML but scopes the processing.
        *   `excluded_tags (Optional[List[str]], default: [])`: A list of HTML tag names (e.g., "nav", "footer") to be removed from the HTML before processing.
        *   `excluded_selector (Optional[str], default: "")`: A CSS selector specifying elements to be removed from the HTML before processing.
        *   `keep_data_attributes (bool, default: False)`: If `True`, `data-*` attributes on HTML elements are preserved during cleaning.
        *   `keep_attrs (Optional[List[str]], default: [])`: A list of specific HTML attribute names to preserve during HTML cleaning.
        *   `remove_forms (bool, default: False)`: If `True`, all `<form>` elements are removed from the HTML.
        *   `prettify (bool, default: False)`: If `True`, the cleaned HTML output is "prettified" for better readability.
        *   `parser_type (str, default: "lxml")`: The HTML parser to be used by the scraping strategy (e.g., "lxml", "html.parser").
        *   `scraping_strategy (Optional[ContentScrapingStrategy], default: WebScrapingStrategy())`: The strategy for scraping content from the HTML.
        *   `proxy_config (Optional[Union[ProxyConfig, dict]], default: None)`: Proxy configuration for this specific run. Overrides any proxy settings in `BrowserConfig`.
        *   `proxy_rotation_strategy (Optional[ProxyRotationStrategy], default: None)`: Strategy to use for rotating proxies if multiple are available.
        *   `locale (Optional[str], default: None)`: Locale to set for the browser context (e.g., "en-US", "fr-FR"). Affects `Accept-Language` header and JavaScript `navigator.language`.
        *   `timezone_id (Optional[str], default: None)`: Timezone ID to set for the browser context (e.g., "America/New_York", "Europe/Paris"). Affects JavaScript `Date` objects.
        *   `geolocation (Optional[GeolocationConfig], default: None)`: A `GeolocationConfig` object or dictionary to set the browser's mock geolocation.
        *   `fetch_ssl_certificate (bool, default: False)`: If `True`, the SSL certificate information for the main URL will be fetched and included in the `CrawlResult`.
        *   `cache_mode (CacheMode, default: CacheMode.BYPASS)`: Defines caching behavior for this run. See `CacheMode` enum for options.
        *   `session_id (Optional[str], default: None)`: An identifier for a browser session. If provided, `crawl4ai` will attempt to reuse an existing page/context associated with this ID, or create a new one and associate it.
        *   `shared_data (Optional[dict], default: None)`: A dictionary for passing custom data between hooks during the crawl lifecycle.
        *   `wait_until (str, default: "domcontentloaded")`: Playwright's page navigation wait condition (e.g., "load", "domcontentloaded", "networkidle", "commit").
        *   `page_timeout (int, default: PAGE_TIMEOUT)`: Maximum time in milliseconds for page navigation and other page operations.
        *   `wait_for (Optional[str], default: None)`: A CSS selector or a JavaScript expression (prefixed with "js:"). The crawler will wait until this condition is met before proceeding.
        *   `wait_for_timeout (Optional[int], default: None)`: Specific timeout in milliseconds for the `wait_for` condition. If `None`, `page_timeout` is used.
        *   `wait_for_images (bool, default: False)`: If `True`, attempts to wait for all images on the page to finish loading.
        *   `delay_before_return_html (float, default: 0.1)`: Delay in seconds to wait just before the final HTML content is retrieved from the page.
        *   `mean_delay (float, default: 0.1)`: Used with `arun_many`. The mean base delay in seconds between processing URLs.
        *   `max_range (float, default: 0.3)`: Used with `arun_many`. The maximum additional random delay (added to `mean_delay`) between processing URLs.
        *   `semaphore_count (int, default: 5)`: Used with `arun_many` and semaphore-based dispatchers. The maximum number of concurrent crawl operations.
        *   `js_code (Optional[Union[str, List[str]]], default: None)`: A string or list of strings containing JavaScript code to be executed on the page after it loads.
        *   `js_only (bool, default: False)`: If `True`, indicates that this `arun` call is primarily for JavaScript execution on an already loaded page (within a session) and a full page navigation might not be needed.
        *   `ignore_body_visibility (bool, default: True)`: If `True`, proceeds with content extraction even if the `<body>` element is not deemed visible by Playwright.
        *   `scan_full_page (bool, default: False)`: If `True`, the crawler will attempt to scroll through the entire page to trigger lazy-loaded content.
        *   `scroll_delay (float, default: 0.2)`: Delay in seconds between each scroll step when `scan_full_page` is `True`.
        *   `process_iframes (bool, default: False)`: If `True`, attempts to extract and inline content from `<iframe>` elements.
        *   `remove_overlay_elements (bool, default: False)`: If `True`, attempts to identify and remove common overlay elements (popups, cookie banners) before content extraction.
        *   `simulate_user (bool, default: False)`: If `True`, enables heuristics to simulate user interactions (like mouse movements) to potentially bypass some anti-bot measures.
        *   `override_navigator (bool, default: False)`: If `True`, overrides certain JavaScript `navigator` properties to appear more like a standard browser.
        *   `magic (bool, default: False)`: If `True`, enables a combination of techniques (like `remove_overlay_elements`, `simulate_user`) to try and handle dynamic/obfuscated sites.
        *   `adjust_viewport_to_content (bool, default: False)`: If `True`, attempts to adjust the browser viewport size to match the dimensions of the page content.
        *   `screenshot (bool, default: False)`: If `True`, a screenshot of the page will be taken and included in `CrawlResult.screenshot`.
        *   `screenshot_wait_for (Optional[float], default: None)`: Additional delay in seconds to wait before taking the screenshot.
        *   `screenshot_height_threshold (int, default: SCREENSHOT_HEIGHT_THRESHOLD)`: If page height exceeds this, a full-page screenshot strategy might be different.
        *   `pdf (bool, default: False)`: If `True`, a PDF version of the page will be generated and included in `CrawlResult.pdf`.
        *   `capture_mhtml (bool, default: False)`: If `True`, an MHTML archive of the page will be captured and included in `CrawlResult.mhtml`.
        *   `image_description_min_word_threshold (int, default: IMAGE_DESCRIPTION_MIN_WORD_THRESHOLD)`: Minimum word count for surrounding text to be considered as an image description.
        *   `image_score_threshold (int, default: IMAGE_SCORE_THRESHOLD)`: Heuristic score threshold for an image to be included in `CrawlResult.media`.
        *   `table_score_threshold (int, default: 7)`: Heuristic score threshold for an HTML table to be considered a data table and included in `CrawlResult.media`.
        *   `exclude_external_images (bool, default: False)`: If `True`, images hosted on different domains than the main page URL are excluded.
        *   `exclude_all_images (bool, default: False)`: If `True`, all images are excluded from `CrawlResult.media`.
        *   `exclude_social_media_domains (Optional[List[str]], default: SOCIAL_MEDIA_DOMAINS from config)`: List of social media domains whose links should be excluded.
        *   `exclude_external_links (bool, default: False)`: If `True`, all links pointing to external domains are excluded from `CrawlResult.links`.
        *   `exclude_social_media_links (bool, default: False)`: If `True`, links to domains in `exclude_social_media_domains` are excluded.
        *   `exclude_domains (Optional[List[str]], default: [])`: A list of specific domains whose links should be excluded.
        *   `exclude_internal_links (bool, default: False)`: If `True`, all links pointing to the same domain are excluded.
        *   `verbose (bool, default: True)`: Enables verbose logging for this specific crawl run. Overrides `BrowserConfig.verbose`.
        *   `log_console (bool, default: False)`: If `True`, browser console messages are captured (requires `capture_console_messages=True` to be effective).
        *   `capture_network_requests (bool, default: False)`: If `True`, captures details of network requests and responses made by the page.
        *   `capture_console_messages (bool, default: False)`: If `True`, captures messages logged to the browser's console.
        *   `method (str, default: "GET")`: HTTP method to use, primarily for `AsyncHTTPCrawlerStrategy`.
        *   `stream (bool, default: False)`: If `True` when using `arun_many`, results are yielded as an async generator instead of returned as a list at the end.
        *   `check_robots_txt (bool, default: False)`: If `True`, `robots.txt` rules for the domain will be checked and respected.
        *   `user_agent (Optional[str], default: None)`: User-Agent string for this specific run. Overrides `BrowserConfig.user_agent`.
        *   `user_agent_mode (Optional[str], default: None)`: User-Agent generation mode for this specific run.
        *   `user_agent_generator_config (Optional[dict], default: {})`: Configuration for User-Agent generator for this run.
        *   `deep_crawl_strategy (Optional[DeepCrawlStrategy], default: None)`: Strategy to use for deep crawling beyond the initial URL.
        *   `experimental (Optional[Dict[str, Any]], default: {})`: A dictionary for passing experimental or beta parameters.
*   **2.2.3. Key Public Attributes/Properties:**
    *   All parameters listed in `__init__` are available as public attributes with the same names and types.
*   **2.2.4. Deprecated Property Handling (`__getattr__`, `_UNWANTED_PROPS`)**
    *   Behavior: Attempting to access a deprecated property (e.g., `bypass_cache`, `disable_cache`, `no_cache_read`, `no_cache_write`) raises an `AttributeError`. The error message directs the user to use the `cache_mode` parameter with the appropriate `CacheMode` enum member instead.
    *   List of Deprecated Properties and their `CacheMode` Equivalents:
        *   `bypass_cache`: Use `cache_mode=CacheMode.BYPASS`.
        *   `disable_cache`: Use `cache_mode=CacheMode.DISABLE`.
        *   `no_cache_read`: Use `cache_mode=CacheMode.WRITE_ONLY`.
        *   `no_cache_write`: Use `cache_mode=CacheMode.READ_ONLY`.
*   **2.2.5. Key Public Methods:**
    *   `from_kwargs(cls, kwargs: dict) -> CrawlerRunConfig` (Static Method):
        *   Purpose: Creates a `CrawlerRunConfig` instance from a dictionary of keyword arguments.
    *   `dump(self) -> dict`:
        *   Purpose: Serializes the `CrawlerRunConfig` object to a dictionary suitable for JSON storage, handling complex nested objects using `to_serializable_dict`.
    *   `load(cls, data: dict) -> CrawlerRunConfig` (Static Method):
        *   Purpose: Deserializes a `CrawlerRunConfig` object from a dictionary (typically one created by `dump()`), using `from_serializable_dict`.
    *   `to_dict(self) -> dict`:
        *   Purpose: Converts the `CrawlerRunConfig` instance into a dictionary representation. Complex objects like strategies are typically represented by their class name or a simplified form.
    *   `clone(self, **kwargs) -> CrawlerRunConfig`:
        *   Purpose: Creates a deep copy of the current `CrawlerRunConfig` instance. Keyword arguments can be provided to override specific attributes in the new instance.

### 2.3. `LLMConfig`
Located in `crawl4ai.async_configs`.

*   **2.3.1. Purpose:**
    *   Description: The `LLMConfig` class provides configuration for interacting with Large Language Model (LLM) providers. It includes settings for the provider name, API token, base URL, and various model-specific parameters like temperature and max tokens.
*   **2.3.2. Initialization (`__init__`)**
    *   Signature:
        ```python
        class LLMConfig:
            def __init__(
                self,
                provider: str = DEFAULT_PROVIDER, # e.g., "openai/gpt-4o-mini"
                api_token: Optional[str] = None,
                base_url: Optional[str] = None,
                temperature: Optional[float] = None,
                max_tokens: Optional[int] = None,
                top_p: Optional[float] = None,
                frequency_penalty: Optional[float] = None,
                presence_penalty: Optional[float] = None,
                stop: Optional[List[str]] = None,
                n: Optional[int] = None,
            ): ...
        ```
    *   Parameters:
        *   `provider (str, default: DEFAULT_PROVIDER)`: The identifier for the LLM provider and model (e.g., "openai/gpt-4o-mini", "ollama/llama3.3", "gemini/gemini-1.5-pro").
        *   `api_token (Optional[str], default: None)`: The API token for authenticating with the LLM provider. If `None`, it attempts to load from environment variables based on the provider (e.g., `OPENAI_API_KEY` for OpenAI, `GEMINI_API_KEY` for Gemini). Can also be set as "env:YOUR_ENV_VAR_NAME".
        *   `base_url (Optional[str], default: None)`: A custom base URL for the LLM API endpoint, useful for self-hosted models or proxies.
        *   `temperature (Optional[float], default: None)`: Controls the randomness of the LLM's output. Higher values (e.g., 0.8) make output more random, lower values (e.g., 0.2) make it more deterministic.
        *   `max_tokens (Optional[int], default: None)`: The maximum number of tokens the LLM should generate in its response.
        *   `top_p (Optional[float], default: None)`: Nucleus sampling parameter. The model considers only tokens with cumulative probability mass up to `top_p`.
        *   `frequency_penalty (Optional[float], default: None)`: Penalizes new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
        *   `presence_penalty (Optional[float], default: None)`: Penalizes new tokens based on whether they have appeared in the text so far, increasing the model's likelihood to talk about new topics.
        *   `stop (Optional[List[str]], default: None)`: A list of sequences where the API will stop generating further tokens.
        *   `n (Optional[int], default: None)`: The number of completions to generate for each prompt.
*   **2.3.3. Key Public Attributes/Properties:**
    *   All parameters listed in `__init__` are available as public attributes with the same names and types.
*   **2.3.4. Key Public Methods:**
    *   `from_kwargs(cls, kwargs: dict) -> LLMConfig` (Static Method):
        *   Purpose: Creates an `LLMConfig` instance from a dictionary of keyword arguments.
    *   `to_dict(self) -> dict`:
        *   Purpose: Converts the `LLMConfig` instance into a dictionary representation.
    *   `clone(self, **kwargs) -> LLMConfig`:
        *   Purpose: Creates a deep copy of the current `LLMConfig` instance. Keyword arguments can be provided to override specific attributes in the new instance.

### 2.4. `GeolocationConfig`
Located in `crawl4ai.async_configs`.

*   **2.4.1. Purpose:**
    *   Description: The `GeolocationConfig` class stores settings for mocking the browser's geolocation, including latitude, longitude, and accuracy.
*   **2.4.2. Initialization (`__init__`)**
    *   Signature:
        ```python
        class GeolocationConfig:
            def __init__(
                self,
                latitude: float,
                longitude: float,
                accuracy: Optional[float] = 0.0
            ): ...
        ```
    *   Parameters:
        *   `latitude (float)`: The latitude coordinate (e.g., 37.7749 for San Francisco).
        *   `longitude (float)`: The longitude coordinate (e.g., -122.4194 for San Francisco).
        *   `accuracy (Optional[float], default: 0.0)`: The accuracy of the geolocation in meters.
*   **2.4.3. Key Public Attributes/Properties:**
    *   `latitude (float)`: Stores the latitude.
    *   `longitude (float)`: Stores the longitude.
    *   `accuracy (Optional[float])`: Stores the accuracy.
*   **2.4.4. Key Public Methods:**
    *   `from_dict(cls, geo_dict: dict) -> GeolocationConfig` (Static Method):
        *   Purpose: Creates a `GeolocationConfig` instance from a dictionary.
    *   `to_dict(self) -> dict`:
        *   Purpose: Converts the `GeolocationConfig` instance to a dictionary: `{"latitude": ..., "longitude": ..., "accuracy": ...}`.
    *   `clone(self, **kwargs) -> GeolocationConfig`:
        *   Purpose: Creates a copy of the `GeolocationConfig` instance, allowing for overriding specific attributes with `kwargs`.

### 2.5. `ProxyConfig`
Located in `crawl4ai.async_configs` (and `crawl4ai.proxy_strategy`).

*   **2.5.1. Purpose:**
    *   Description: The `ProxyConfig` class encapsulates the configuration for a single proxy server, including its address, authentication credentials (if any), and optionally its public IP address.
*   **2.5.2. Initialization (`__init__`)**
    *   Signature:
        ```python
        class ProxyConfig:
            def __init__(
                self,
                server: str,
                username: Optional[str] = None,
                password: Optional[str] = None,
                ip: Optional[str] = None,
            ): ...
        ```
    *   Parameters:
        *   `server (str)`: The proxy server URL, including protocol and port (e.g., "http://127.0.0.1:8080", "socks5://proxy.example.com:1080").
        *   `username (Optional[str], default: None)`: The username for proxy authentication, if required.
        *   `password (Optional[str], default: None)`: The password for proxy authentication, if required.
        *   `ip (Optional[str], default: None)`: The public IP address of the proxy server. If not provided, it will be automatically extracted from the `server` string if possible.
*   **2.5.3. Key Public Attributes/Properties:**
    *   `server (str)`: The proxy server URL.
    *   `username (Optional[str])`: The username for proxy authentication.
    *   `password (Optional[str])`: The password for proxy authentication.
    *   `ip (Optional[str])`: The public IP address of the proxy. This is either user-provided or automatically extracted from the `server` string during initialization via the internal `_extract_ip_from_server` method.
*   **2.5.4. Key Public Methods:**
    *   `_extract_ip_from_server(self) -> Optional[str]` (Internal method):
        *   Purpose: Extracts the IP address component from the `self.server` URL string.
    *   `from_string(cls, proxy_str: str) -> ProxyConfig` (Static Method):
        *   Purpose: Creates a `ProxyConfig` instance from a string.
        *   Formats:
            *   `'ip:port:username:password'`
            *   `'ip:port'` (no authentication)
    *   `from_dict(cls, proxy_dict: dict) -> ProxyConfig` (Static Method):
        *   Purpose: Creates a `ProxyConfig` instance from a dictionary with keys "server", "username", "password", and "ip".
    *   `from_env(cls, env_var: str = "PROXIES") -> List[ProxyConfig]` (Static Method):
        *   Purpose: Loads a list of `ProxyConfig` objects from a comma-separated environment variable. Each proxy string in the variable should conform to the format accepted by `from_string`.
    *   `to_dict(self) -> dict`:
        *   Purpose: Converts the `ProxyConfig` instance to a dictionary: `{"server": ..., "username": ..., "password": ..., "ip": ...}`.
    *   `clone(self, **kwargs) -> ProxyConfig`:
        *   Purpose: Creates a copy of the `ProxyConfig` instance, allowing for overriding specific attributes with `kwargs`.

### 2.6. `HTTPCrawlerConfig`
Located in `crawl4ai.async_configs`.

*   **2.6.1. Purpose:**
    *   Description: The `HTTPCrawlerConfig` class holds configuration settings specific to direct HTTP-based crawling strategies (e.g., `AsyncHTTPCrawlerStrategy`), which do not use a full browser environment.
*   **2.6.2. Initialization (`__init__`)**
    *   Signature:
        ```python
        class HTTPCrawlerConfig:
            def __init__(
                self,
                method: str = "GET",
                headers: Optional[Dict[str, str]] = None,
                data: Optional[Dict[str, Any]] = None,
                json: Optional[Dict[str, Any]] = None,
                follow_redirects: bool = True,
                verify_ssl: bool = True,
            ): ...
        ```
    *   Parameters:
        *   `method (str, default: "GET")`: The HTTP method to use for the request (e.g., "GET", "POST", "PUT").
        *   `headers (Optional[Dict[str, str]], default: None)`: A dictionary of custom HTTP headers to send with the request.
        *   `data (Optional[Dict[str, Any]], default: None)`: Data to be sent in the body of the request, typically for "POST" or "PUT" requests (e.g., form data).
        *   `json (Optional[Dict[str, Any]], default: None)`: JSON data to be sent in the body of the request. If provided, the `Content-Type` header is typically set to `application/json`.
        *   `follow_redirects (bool, default: True)`: If `True`, the crawler will automatically follow HTTP redirects.
        *   `verify_ssl (bool, default: True)`: If `True`, SSL certificates will be verified. Set to `False` to ignore SSL errors (use with caution).
*   **2.6.3. Key Public Attributes/Properties:**
    *   All parameters listed in `__init__` are available as public attributes with the same names and types.
*   **2.6.4. Key Public Methods:**
    *   `from_kwargs(cls, kwargs: dict) -> HTTPCrawlerConfig` (Static Method):
        *   Purpose: Creates an `HTTPCrawlerConfig` instance from a dictionary of keyword arguments.
    *   `to_dict(self) -> dict`:
        *   Purpose: Converts the `HTTPCrawlerConfig` instance into a dictionary representation.
    *   `clone(self, **kwargs) -> HTTPCrawlerConfig`:
        *   Purpose: Creates a deep copy of the current `HTTPCrawlerConfig` instance. Keyword arguments can be provided to override specific attributes in the new instance.
    *   `dump(self) -> dict`:
        *   Purpose: Serializes the `HTTPCrawlerConfig` object to a dictionary.
    *   `load(cls, data: dict) -> HTTPCrawlerConfig` (Static Method):
        *   Purpose: Deserializes an `HTTPCrawlerConfig` object from a dictionary.

## 3. Enumerations and Helper Constants

### 3.1. `CacheMode` (Enum)
Located in `crawl4ai.cache_context`.

*   **3.1.1. Purpose:**
    *   Description: The `CacheMode` enumeration defines the different caching behaviors that can be applied to a crawl operation. It is used in `CrawlerRunConfig` to control how results are read from and written to the cache.
*   **3.1.2. Enum Members:**
    *   `ENABLE (str)`: Value: "ENABLE". Description: Enables normal caching behavior. The crawler will attempt to read from the cache first, and if a result is not found or is stale, it will perform the crawl and write the new result to the cache.
    *   `DISABLE (str)`: Value: "DISABLE". Description: Disables all caching. The crawler will not read from or write to the cache. Every request will be a fresh crawl.
    *   `READ_ONLY (str)`: Value: "READ_ONLY". Description: The crawler will only attempt to read from the cache. If a result is found, it will be used. If not, the crawl will not proceed further for that URL, and no new data will be written to the cache.
    *   `WRITE_ONLY (str)`: Value: "WRITE_ONLY". Description: The crawler will not attempt to read from the cache. It will always perform a fresh crawl and then write the result to the cache.
    *   `BYPASS (str)`: Value: "BYPASS". Description: The crawler will skip reading from the cache for this specific operation and will perform a fresh crawl. The result of this crawl *will* be written to the cache. This is the default `cache_mode` for `CrawlerRunConfig`.
*   **3.1.3. Usage:**
    *   Example:
        ```python
        from crawl4ai import CrawlerRunConfig, CacheMode
        config = CrawlerRunConfig(cache_mode=CacheMode.ENABLE) # Use cache fully
        config_bypass = CrawlerRunConfig(cache_mode=CacheMode.BYPASS) # Force fresh crawl, then cache
        ```

## 4. Serialization Helper Functions
Located in `crawl4ai.async_configs`.

### 4.1. `to_serializable_dict(obj: Any, ignore_default_value: bool = False) -> Dict`

*   **4.1.1. Purpose:**
    *   Description: This utility function recursively converts various Python objects, including `crawl4ai` configuration objects, into a dictionary format that is suitable for JSON serialization. It uses a `{ "type": "ClassName", "params": { ... } }` structure for custom class instances to enable proper deserialization later.
*   **4.1.2. Parameters:**
    *   `obj (Any)`: The Python object to be serialized.
    *   `ignore_default_value (bool, default: False)`: If `True`, when serializing class instances, parameters whose current values match their `__init__` default values might be excluded from the "params" dictionary. (Note: The exact behavior depends on the availability of default values in the class signature and handling of empty/None values).
*   **4.1.3. Returns:**
    *   `Dict`: A dictionary representation of the input object, structured for easy serialization (e.g., to JSON) and later deserialization by `from_serializable_dict`.
*   **4.1.4. Key Behaviors:**
    *   **Basic Types:** `str`, `int`, `float`, `bool`, `None` are returned as is.
    *   **Enums:** Serialized as `{"type": "EnumClassName", "params": enum_member.value}`.
    *   **Datetime Objects:** Serialized to their ISO 8601 string representation.
    *   **Lists, Tuples, Sets, Frozensets:** Serialized by recursively calling `to_serializable_dict` on each of their elements, returning a list.
    *   **Plain Dictionaries:** Serialized as `{"type": "dict", "value": {key: serialized_value, ...}}`.
    *   **Class Instances (e.g., Config Objects):**
        *   The object's class name is stored in the "type" field.
        *   Parameters from the `__init__` signature and attributes from `__slots__` (if defined) are collected.
        *   Their current values are recursively serialized and stored in the "params" dictionary.
        *   The structure is `{"type": "ClassName", "params": {"param_name": serialized_param_value, ...}}`.

### 4.2. `from_serializable_dict(data: Any) -> Any`

*   **4.2.1. Purpose:**
    *   Description: This utility function reconstructs Python objects, including `crawl4ai` configuration objects, from the serializable dictionary format previously created by `to_serializable_dict`.
*   **4.2.2. Parameters:**
    *   `data (Any)`: The dictionary (or basic data type) to be deserialized. This is typically the output of `to_serializable_dict` after being, for example, loaded from a JSON string.
*   **4.2.3. Returns:**
    *   `Any`: The reconstructed Python object (e.g., an instance of `BrowserConfig`, `LLMConfig`, a list, a plain dictionary, etc.).
*   **4.2.4. Key Behaviors:**
    *   **Basic Types:** `str`, `int`, `float`, `bool`, `None` are returned as is.
    *   **Typed Dictionaries (from `to_serializable_dict`):**
        *   If `data` is a dictionary and contains a "type" key:
            *   If `data["type"] == "dict"`, it reconstructs a plain Python dictionary from `data["value"]` by recursively deserializing its items.
            *   Otherwise, it attempts to locate the class specified by `data["type"]` within the `crawl4ai` module.
                *   If the class is an `Enum`, it instantiates the enum member using `data["params"]` (the enum value).
                *   If it's a regular class, it recursively deserializes the items in `data["params"]` and uses them as keyword arguments (`**kwargs`) to instantiate the class.
    *   **Lists:** If `data` is a list, it reconstructs a list by recursively calling `from_serializable_dict` on each of its elements.
    *   **Legacy Dictionaries:** If `data` is a dictionary but does not conform to the "type" key structure (for backward compatibility), it attempts to deserialize its values.

## 5. Cross-References and Relationships

*   **5.1. `BrowserConfig` Usage:**
    *   Typically instantiated once and passed to the `AsyncWebCrawler` constructor via its `config` parameter.
    *   `browser_config = BrowserConfig(headless=False)`
    *   `crawler = AsyncWebCrawler(config=browser_config)`
    *   It defines the global browser settings that will be used for all subsequent crawl operations unless overridden by `CrawlerRunConfig` on a per-run basis.
*   **5.2. `CrawlerRunConfig` Usage:**
    *   Passed to the `arun()` or `arun_many()` methods of `AsyncWebCrawler`.
    *   `run_config = CrawlerRunConfig(screenshot=True, cache_mode=CacheMode.BYPASS)`
    *   `result = await crawler.arun(url="https://example.com", config=run_config)`
    *   Allows for fine-grained control over individual crawl requests, overriding global settings from `BrowserConfig` or `AsyncWebCrawler`'s defaults where applicable (e.g., `user_agent`, `proxy_config`, `cache_mode`).
*   **5.3. `LLMConfig` Usage:**
    *   Instantiated and passed to LLM-based extraction strategies (e.g., `LLMExtractionStrategy`) or content filters (`LLMContentFilter`) during their initialization.
    *   `llm_conf = LLMConfig(provider="openai/gpt-4o-mini", api_token="sk-...")`
    *   `extraction_strategy = LLMExtractionStrategy(llm_config=llm_conf, schema=my_schema)`
*   **5.4. `GeolocationConfig` and `ProxyConfig` Usage:**
    *   `GeolocationConfig` is typically instantiated and assigned to the `geolocation` parameter of `CrawlerRunConfig`.
        *   `geo_conf = GeolocationConfig(latitude=34.0522, longitude=-118.2437)`
        *   `run_config = CrawlerRunConfig(geolocation=geo_conf)`
    *   `ProxyConfig` can be assigned to the `proxy_config` parameter of `BrowserConfig` (for a global proxy applied to all contexts) or `CrawlerRunConfig` (for a proxy specific to a single crawl run).
        *   `proxy_conf = ProxyConfig(server="http://myproxy:8080")`
        *   `browser_config = BrowserConfig(proxy_config=proxy_conf)` (global)
        *   `run_config = CrawlerRunConfig(proxy_config=proxy_conf)` (per-run)
*   **5.5. `HTTPCrawlerConfig` Usage:**
    *   Used when the `crawler_strategy` for `AsyncWebCrawler` is set to `AsyncHTTPCrawlerStrategy` (for non-browser-based HTTP requests).
    *   `http_conf = HTTPCrawlerConfig(method="POST", json={"key": "value"})`
    *   `http_strategy = AsyncHTTPCrawlerStrategy(http_crawler_config=http_conf)`
    *   `crawler = AsyncWebCrawler(crawler_strategy=http_strategy)`
    *   Alternatively, parameters like `method`, `data`, `json` can be passed directly to `arun()` when using `AsyncHTTPCrawlerStrategy` if they are part of the `CrawlerRunConfig`.

---


## Configuration Objects - Reasoning
Source: crawl4ai_config_objects_reasoning_content.llm.md

Okay, I'm ready to generate the detailed "Reasoning & Problem-Solving Framework" document for the `config_objects` component based on the provided outline and information.

```markdown
# Detailed Outline for crawl4ai - config_objects Component

**Target Document Type:** reasoning
**Target Output Filename Suggestion:** `llm_reasoning_config_objects.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2024-05-24
---

## 1. Introduction to Configuration in Crawl4ai

*   1.1. **The "Why": The Importance of Configuration**
    *   1.1.1. **Explaining how configuration objects provide granular control over crawling.**
        Crawl4ai is designed to tackle a wide array of web crawling and scraping tasks, from simple page fetches to complex interactions with dynamic websites and data extraction using LLMs. To manage this complexity effectively, Crawl4ai employs a system of dedicated configuration objects. These objects allow you to precisely define how the crawler behaves at different stages: how the browser is set up, how individual web pages are processed, and how interactions with Large Language Models (LLMs) are handled.
        Without a robust configuration system, you'd be forced to pass numerous, often-conflicting parameters to a single function, making your code hard to read, maintain, and debug. Configuration objects provide a structured, organized, and explicit way to tell Crawl4ai exactly what you want it to do.

    *   1.1.2. **Discussing the benefits of separating browser setup (`BrowserConfig`) from individual crawl behavior (`CrawlerRunConfig`) and LLM settings (`LLMConfig`).**
        The separation of concerns is a key design principle in Crawl4ai's configuration system:
        *   **`BrowserConfig`:** This object dictates the *environment* in which your crawls will run. It handles aspects like which browser to use (Chrome, Firefox), whether to run in headless mode, proxy settings, and browser identity (user-agent). This setup is typically done once per `AsyncWebCrawler` instance or per logical group of crawling tasks that require the same browser environment.
        *   **`CrawlerRunConfig`:** This object controls the specifics of *each individual crawl operation* (e.g., a single call to `arun()`). It defines how a particular URL is fetched, what content to extract, which JavaScript to execute on the page, caching behavior for that specific URL, and any media capture settings (screenshots, PDFs). This allows you to use the same browser setup to crawl different URLs with vastly different processing requirements.
        *   **`LLMConfig`:** When leveraging LLMs for tasks like content summarization or structured data extraction, `LLMConfig` centralizes all settings related to the LLM provider, model choice, API keys, and generation parameters (like temperature or max tokens). This keeps LLM-specific details separate from the core crawling and browser logic.

        This separation offers significant advantages:
        *   **Modularity:** You can define a browser setup once and reuse it for many different crawl tasks, each with its own `CrawlerRunConfig`.
        *   **Clarity:** It's easier to understand which settings affect which part of the crawling process.
        *   **Maintainability:** Changes to browser setup don't require modifying every crawl task's configuration, and vice-versa.
        *   **Flexibility:** You can easily swap out different LLM providers or models without altering your core crawling logic.

    *   1.1.3. **Overview of how these objects work together to achieve complex crawling scenarios.**
        Imagine you need to crawl a series of product pages.
        1.  You'd first instantiate an `AsyncWebCrawler` with a `BrowserConfig` that sets up a browser with, perhaps, a common desktop user-agent and no proxy.
        2.  Then, for each product page URL, you'd call `crawler.arun()` with a `CrawlerRunConfig`. This `CrawlerRunConfig` might specify:
            *   A `css_selector` to target only the main product information block.
            *   An `extraction_strategy` (like `JsonCssExtractionStrategy` or `LLMExtractionStrategy` with an `LLMConfig`) to pull out the product name, price, and description.
            *   `screenshot=True` to capture an image of the product page.
        3.  If another part of your task involves crawling blog posts from the same site, you could reuse the same `AsyncWebCrawler` (and thus the same `BrowserConfig`) but pass a *different* `CrawlerRunConfig` to `arun()` tailored for blog posts (e.g., different selectors, a different extraction strategy focused on article text).

        This layered approach allows you to build sophisticated crawlers by combining these configuration objects in a logical and manageable way.

*   1.2. **Core Philosophy: Flexibility and Reusability**
    *   1.2.1. **How the design promotes creating base configurations and specializing them.**
        A common and highly recommended pattern is to define "base" configuration objects that capture common settings for your project or for a specific type of task. Then, for individual crawls or variations, you can use the `clone()` method to create a new instance of the configuration object and override only the specific parameters you need to change. This significantly reduces code duplication and makes your configurations easier to manage.

        For example, you might have a `base_browser_config` for all your crawls and a `base_ecommerce_run_config` for scraping e-commerce sites. When scraping a specific e-commerce site, you'd clone `base_ecommerce_run_config` and only adjust, say, the `css_selector` or `extraction_strategy`.

    *   1.2.2. **The role of `clone()`, `dump()`, and `load()` in managing configuration lifecycle.**
        Crawl4ai's configuration objects come with built-in methods to streamline their management:
        *   **`clone(**kwargs)`:** Creates a deep copy of the configuration object, allowing you to override specific parameters for the new instance without affecting the original. This is perfect for creating specialized versions from a base configuration.
        *   **`dump()`:** Serializes the configuration object into a Python dictionary. This dictionary can then be easily saved to a JSON or YAML file, stored in a database, or transmitted over a network.
        *   **`load(data: dict)`:** A static method on each configuration class that reconstructs a configuration object from a dictionary (typically one produced by `dump()`). This allows you to load configurations from external sources, making your crawling setup more dynamic and shareable.

        These methods facilitate:
        *   **Versioning:** Store different configuration versions in files.
        *   **Sharing:** Easily share configurations between different parts of your application or with team members.
        *   **Dynamic Setup:** Load configurations based on runtime parameters or external inputs.

*   1.3. **Scope of This Guide**
    *   1.3.1. **What this guide will cover (deep dive into reasoning for `BrowserConfig`, `CrawlerRunConfig`, `LLMConfig`, `GeolocationConfig`, `ProxyConfig`, `HTTPCrawlerConfig`).**
        This guide focuses on the *reasoning* behind using various configuration objects and their parameters. We'll explore *how* to make effective choices, *why* certain features are designed the way they are, and *when* to use specific settings to solve common crawling challenges. We will perform a deep dive into:
        *   `BrowserConfig`: For setting up the browser's environment and identity.
        *   `CrawlerRunConfig`: For tailoring individual crawl operations.
        *   `LLMConfig`: For configuring interactions with Large Language Models.
        *   And touch upon specialized configs like `GeolocationConfig`, `ProxyConfig`, and `HTTPCrawlerConfig` for specific use cases.
    *   1.3.2. **Briefly mentioning where to find exhaustive API parameter lists (referencing a "memory" document or API docs).**
        While this guide provides practical examples and discusses many key parameters, it is not an exhaustive API reference. For a complete list of all available parameters, their types, default values, and concise descriptions, please refer to the official API documentation or the "Foundational Memory" document for `config_objects` if available. This guide aims to complement that factual information by providing the "how-to" and "why."

## 2. Mastering `BrowserConfig`: Setting Up Your Crawler's Identity and Environment

*   2.1. **Understanding `BrowserConfig`: Beyond Default Behavior**
    *   2.1.1. **When is the default `BrowserConfig` sufficient?**
        If you're performing simple crawls of public, static websites that don't have strong anti-bot measures, the default `BrowserConfig` (which you get by simply instantiating `AsyncWebCrawler()` without a custom config) might work perfectly fine. It typically launches a headless Chromium browser with a generic user-agent. For quick tests or very straightforward tasks, this is often all you need.

    *   2.1.2. **Key scenarios demanding `BrowserConfig` customization:**
        You'll need to customize `BrowserConfig` when your crawling tasks become more complex or when you encounter challenges like:
        *   **Evading Bot Detection:** Many websites employ techniques to identify and block automated crawlers. Customizing user-agents, browser hints, and even browser behavior can help your crawler appear more like a regular human user.
        *   **Testing Geo-Specific Content:** If a website serves different content based on the user's geographic location, you'll need to configure the browser to simulate originating from that specific region (using `GeolocationConfig` within `CrawlerRunConfig`, but also ensuring your browser's IP via a proxy in `BrowserConfig` aligns).
        *   **Using Proxies:** To rotate IP addresses, mask your origin, or access geo-restricted content, configuring proxies is essential.
        *   **Managing Browser Resources and Performance:** For large-scale crawls, controlling browser features (like disabling images or JavaScript) or using different browser modes (like Docker) can significantly impact performance and resource consumption.
        *   **Persistent Sessions and Authenticated Crawling:** If you need to log into a website and maintain that session across multiple crawl operations, `BrowserConfig` provides options for persistent contexts.

*   2.2. **Strategic `BrowserConfig` Customizations**
    *   2.2.1. **Crafting a Believable Browser Identity**
        *   **`user_agent` and `user_agent_mode`:**
            *   **Why faking User-Agents can be crucial:** The User-Agent string is one of the first pieces of information a web server receives. Many sites use it to tailor content or, more critically for crawlers, to identify and block non-standard or known bot User-Agents. Using a common, legitimate browser User-Agent makes your crawler less conspicuous.
            *   **Choosing between a static `user_agent` and `user_agent_mode="random"`:**
                *   **Static `user_agent`:** Use this if you want to consistently mimic a specific browser and OS combination. This can be useful for targeting mobile-specific views or ensuring consistent rendering.
                *   **`user_agent_mode="random"`:** Crawl4ai will use its built-in `ValidUAGenerator` to pick a common, valid User-Agent for each new browser context (or potentially page, depending on strategy details). This can help avoid patterns if a site tracks User-Agents over time. The `user_agent_generator_config` parameter can be used to further customize the random generation if needed, for example, to only generate User-Agents for a specific OS or device type.
            *   **Trade-offs and when to use each:**
                *   Static: More predictable, good for specific targeting.
                *   Random: Better for avoiding simple User-Agent-based blocking over many requests, but ensure the randomness still aligns with common browser profiles.
            *   **Code Example: Setting a specific User-Agent vs. using random generation.**
                ```python
                from crawl4ai import BrowserConfig

                # Specific User-Agent
                config_specific_ua = BrowserConfig(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                print(f"Specific UA Config: {config_specific_ua.user_agent}")

                # Random User-Agent (default behavior when user_agent_mode="random" or just not set with a static UA)
                config_random_ua = BrowserConfig(user_agent_mode="random")
                # Note: The actual UA is generated when the browser context is created by AsyncWebCrawler
                # We can inspect the generated UA through the browser_hint which is derived from it.
                print(f"Random UA Config (Hint): {config_random_ua.browser_hint}")
                # Example for generating one manually:
                from crawl4ai.user_agent_generator import ValidUAGenerator
                ua_gen = ValidUAGenerator()
                random_ua_example = ua_gen.generate()
                print(f"Example Random UA: {random_ua_example}")
                ```

        *   **`browser_hint` and `sec-ch-ua` headers:**
            *   **How these contribute to a more convincing browser profile:** Modern browsers send Client Hints (like `Sec-CH-UA`, `Sec-CH-UA-Mobile`, `Sec-CH-UA-Platform`) that provide more granular information about the browser than the traditional User-Agent string. Crawl4ai automatically generates a plausible `browser_hint` (which populates `Sec-CH-UA`) based on the `user_agent` to enhance authenticity.
            *   **Ensuring consistency:** It's vital that your Client Hints are consistent with your main User-Agent string. Crawl4ai aims to do this automatically. If you manually set headers, ensure they don't contradict your chosen `user_agent`.

    *   2.2.2. **Headless vs. Headful: The Visibility Trade-off (`headless`)**
        *   **Why use headless mode (`headless=True`, default):**
            *   **Servers & Automation:** Ideal for running crawlers on servers or in automated CI/CD pipelines where no graphical interface is available or needed.
            *   **Speed & Resources:** Generally consumes fewer resources than a full GUI browser, leading to faster crawls, especially at scale.
        *   **When headful mode (`headless=False`) is essential:**
            *   **Debugging:** Visually inspecting what the browser sees is invaluable for debugging issues with page rendering, element selection, or unexpected site behavior.
            *   **Anti-Bot Measures:** Some sophisticated websites can detect headless browsers (e.g., by checking for specific JavaScript properties or rendering inconsistencies). Running in headful mode can sometimes bypass these checks.
        *   **Impact on performance and detectability:** Headless is faster but potentially more detectable. Headful is slower, uses more resources, but can appear more like a real user.
        *   **Decision Guide: Choosing the right mode for your task.**
            *   Start with `headless=True` for production and automated runs.
            *   Switch to `headless=False` when:
                *   Debugging selectors or interactions.
                *   You suspect the site is blocking headless browsers.
                *   You need to manually perform actions like solving a CAPTCHA during a setup phase.
            ```python
            from crawl4ai import BrowserConfig

            # Default: Headless
            config_headless = BrowserConfig() # headless=True is the default
            print(f"Headless mode: {config_headless.headless}")

            # Explicitly Headful for debugging
            config_headful = BrowserConfig(headless=False)
            print(f"Headful mode: {config_headful.headless}")
            ```

    *   2.2.3. **Controlling the Browser's Lifecycle and Environment**
        *   **`browser_mode` ("builtin", "dedicated", "cdp", "docker"):**
            *   **Explaining each mode and its typical use case:**
                *   `"dedicated"` (Default): Launches a fresh, isolated browser instance for the `AsyncWebCrawler`. This is good for most use cases, ensuring no state leaks between different crawler instances if you were to run multiple in the same script (though typically you'd use one `AsyncWebCrawler` and multiple `arun` calls).
                *   `"builtin"`: (More advanced) Intended for scenarios where Crawl4ai manages a long-lived browser process in the background, potentially shared across different crawler objects or Python processes. This can be more resource-efficient for very frequent, short-lived crawl tasks. It leverages `use_managed_browser=True` and a CDP connection to this managed browser.
                *   `"cdp"` (or `use_managed_browser=True` with a `cdp_url`): Allows you to connect Crawl4ai to an *existing* Chrome/Chromium browser instance that has been launched with a remote debugging port. Useful if you want to control a browser you've launched manually or one managed by another tool.
                *   `"docker"`: Facilitates running the browser inside a Docker container. Crawl4ai can manage launching a browser in a container and connecting to it. This is excellent for consistent environments and isolating dependencies. (Requires Docker setup and relevant browser images).
            *   **"dedicated":**
                *   Pros: Simple to understand, good isolation for typical `AsyncWebCrawler` usage.
                *   Cons: Can be resource-intensive if you're instantiating many `AsyncWebCrawler` objects each with its own dedicated browser, instead of reusing one `AsyncWebCrawler` for multiple `arun` calls.
            *   **"cdp" / `use_managed_browser=True`:** This implies that Crawl4ai will try to connect to a browser via the Chrome DevTools Protocol (CDP).
                *   If `cdp_url` is provided in `BrowserConfig`, it uses that.
                *   If `browser_mode` is "builtin" or "docker", Crawl4ai's internal `ManagedBrowser` (or a Docker strategy) would start a browser and provide the `cdp_url` internally.
        *   **`use_persistent_context` and `user_data_dir`:**
            *   **The power of persistent sessions:** When `use_persistent_context=True`, Playwright (the underlying browser automation library) attempts to save and reuse browser state (cookies, local storage, etc.) across sessions, using the directory specified by `user_data_dir`. This is invaluable for:
                *   **Authenticated Crawls:** Log in once (manually or scripted), and subsequent crawls with the same `user_data_dir` can often bypass the login process.
                *   **Maintaining Preferences:** Site preferences, "accept cookies" banners, etc., can be remembered.
            *   **Workflow for authenticated crawling:**
                1.  **Initial Setup Run:**
                    ```python
                    # First run: Login and save session
                    login_browser_config = BrowserConfig(
                        headless=False,  # Often easier to do initial login with a visible browser
                        use_persistent_context=True,
                        user_data_dir="./my_browser_profile" # Choose a path
                    )
                    # ... (code to navigate to login page, fill credentials, submit using crawler.arun() with appropriate js_code)
                    # After successful login, close the crawler. The session is saved in "./my_browser_profile".
                    ```
                2.  **Subsequent Runs:**
                    ```python
                    # Subsequent runs: Reuse the saved profile
                    reuse_browser_config = BrowserConfig(
                        headless=True, # Can now run headless
                        use_persistent_context=True,
                        user_data_dir="./my_browser_profile" # Must be the same path
                    )
                    # ... (crawler.arun() calls to access protected pages will now use the saved session)
                    ```
            *   **Best Practice:** Use distinct `user_data_dir` paths for different websites or different user accounts to keep sessions isolated.
            *   **Note:** `use_persistent_context=True` automatically implies `use_managed_browser=True` because persistent contexts are a feature of Playwright's browser contexts launched via CDP.

    *   2.2.4. **Navigating Networks: Proxies and SSL (`proxy_config`, `ignore_https_errors`)**
        *   **Integrating Proxies with `proxy_config` (referencing `ProxyConfig` object):**
            *   **Why use proxies:**
                *   **IP Rotation:** Avoid rate limits or blocks by distributing requests across multiple IP addresses.
                *   **Geo-Targeting:** Access content specific to a certain geographic region by using a proxy located in that region.
                *   **Anonymity/Privacy:** Mask your crawler's true origin IP (though be mindful of the proxy provider's logging policies).
            *   **How to structure the `proxy_config` dictionary:**
                The `proxy_config` parameter in `BrowserConfig` expects a dictionary compatible with Playwright's proxy settings. Typically, this includes:
                *   `server`: The proxy server address (e.g., `"http://proxy.example.com:8080"` or `"socks5://proxy.example.com:1080"`).
                *   `username` (optional): Username for proxy authentication.
                *   `password` (optional): Password for proxy authentication.
                A `ProxyConfig` object from `crawl4ai.async_configs` can also be used here by converting it to a dictionary with `my_proxy_config.to_dict()`.
            *   **Workflow: Implementing a basic proxy rotation:**
                While Crawl4ai has a more advanced `ProxyRotationStrategy` (covered elsewhere), a simple rotation can be achieved by dynamically creating `BrowserConfig` instances:
                ```python
                # Conceptual: Basic proxy rotation
                proxies = [
                    {"server": "http://proxy1.example.com:8080", "username": "user1", "password": "p1"},
                    {"server": "http://proxy2.example.com:8080", "username": "user2", "password": "p2"},
                ]
                current_proxy_index = 0

                def get_next_proxy_config_dict():
                    nonlocal current_proxy_index
                    proxy_details = proxies[current_proxy_index % len(proxies)]
                    current_proxy_index += 1
                    return proxy_details

                # In your loop or arun_many setup:
                # proxy_dict = get_next_proxy_config_dict()
                # browser_cfg = BrowserConfig(proxy_config=proxy_dict)
                # crawler = AsyncWebCrawler(config=browser_cfg)
                # await crawler.arun(...)
                ```
            *   **Code Example: Configuring a single authenticated proxy.**
                ```python
                from crawl4ai import BrowserConfig

                proxy_settings = {
                    "server": "http://myproxy.service.com:3128",
                    "username": "proxy_user",
                    "password": "proxy_password"
                }
                config_with_proxy = BrowserConfig(proxy_config=proxy_settings)

                # To use with AsyncWebCrawler:
                # async with AsyncWebCrawler(config=config_with_proxy) as crawler:
                #     result = await crawler.arun(url="https://api.ipify.org?format=json") # Check your IP
                #     print(result.html)
                ```
        *   **`ignore_https_errors`:**
            *   **When this might be needed:** Primarily for development or testing environments where you might encounter self-signed SSL certificates or other non-production SSL configurations.
            *   **Warning:** Setting `ignore_https_errors=True` in a production environment or when accessing sensitive sites is **highly discouraged** as it bypasses crucial security checks, making your crawler vulnerable to man-in-the-middle attacks. Use with extreme caution.

    *   2.2.5. **Fine-tuning for Performance (`text_mode`, `light_mode`, `extra_args`)**
        *   **`text_mode=True`:**
            *   **Benefits:** This mode attempts to disable the loading of images, CSS, and fonts, and may also disable JavaScript depending on the underlying strategy implementation. This can significantly speed up page loads and reduce bandwidth consumption, especially for sites where you are primarily interested in textual content.
        *   **`light_mode=True`:**
            *   **How it differs:** `light_mode` is a more aggressive optimization. It not only includes `text_mode` behaviors but also enables a set of browser launch arguments (`BROWSER_DISABLE_OPTIONS` in `browser_manager.py`) designed to disable various background features, rendering optimizations, and GPU acceleration. This is aimed at achieving maximum performance gains, especially in resource-constrained environments or for very large-scale crawls where every millisecond counts.
        *   **`extra_args`:**
            *   **Unlocking advanced browser capabilities and optimizations:** This parameter allows you to pass a list of custom command-line arguments directly to the browser when it's launched. This is a powerful way to enable or disable specific browser features not covered by other `BrowserConfig` options.
            *   **Common and useful flags:**
                *   `"--disable-gpu"`: Can resolve issues on systems without proper GPU drivers or in headless environments.
                *   `"--no-sandbox"`: Often required when running Chrome/Chromium inside Docker containers, especially as root.
                *   `"--disable-extensions"`: Prevents any installed browser extensions from interfering with the crawl.
                *   `"--disable-dev-shm-usage"`: Can prevent crashes in Docker due to limited shared memory.
            *   **Where to find lists of available browser arguments:** Search for "Chromium command line switches" or "Firefox command line options" for comprehensive lists.
            *   **Code Example:**
                ```python
                from crawl4ai import BrowserConfig

                performance_config = BrowserConfig(
                    light_mode=True, # Includes text_mode and other optimizations
                    extra_args=["--disable-blink-features=AutomationControlled"] # Example: Hiding automation flags
                )
                # Use this config with AsyncWebCrawler
                ```

*   2.3. **Best Practices for `BrowserConfig`**
    *   2.3.1. **Start simple, add complexity as needed:** Don't over-configure from the outset. Begin with defaults and only add customizations as specific needs or problems arise.
    *   2.3.2. **Prioritize realistic browser profiles for stealth:** If evading bot detection is a goal, ensure your `user_agent`, `browser_hint` (implicitly handled by `user_agent`), and other settings present a common and consistent browser profile.
    *   2.3.3. **Use persistent contexts for authenticated sessions:** Leverage `use_persistent_context=True` and `user_data_dir` for sites requiring login, to avoid re-authenticating on every run.
    *   2.3.4. **Be mindful of resource consumption:** Headful mode, multiple "dedicated" browser instances, and not using `light_mode` or `text_mode` can consume more resources. Optimize for your environment and scale.

*   2.4. **Troubleshooting Common `BrowserConfig` Issues**
    *   2.4.1. **Browser not launching or crashing:**
        *   Check Playwright installation: Run `playwright install` or `crawl4ai-setup`.
        *   Missing system dependencies: Especially on Linux, ensure all required libraries for the browser (e.g., Chromium dependencies) are installed. `crawl4ai-doctor` might help.
        *   `extra_args` conflicts: Some launch arguments might conflict or be invalid.
        *   Resource limits: Particularly in Docker or VMs, ensure sufficient CPU/memory. Consider `--disable-dev-shm-usage` if using Docker.
    *   2.4.2. **Pages not rendering correctly (potential `user_agent` or JS issues):**
        *   Try `headless=False` to visually inspect.
        *   Ensure `javascript_enabled=True` in `CrawlerRunConfig` (default) if the site relies heavily on JS.
        *   Experiment with different `user_agent` strings; some sites serve different content or block based on UA.
    *   2.4.3. **Proxy connection failures:**
        *   Verify proxy server address, port, username, and password.
        *   Test the proxy outside of Crawl4ai (e.g., with `curl` or in a browser) to ensure it's working.
        *   Check for firewall issues blocking connections to the proxy.
    *   2.4.4. **Debugging Tip: Always try `headless=False` first.** This is the single most useful step for diagnosing many browser-related issues, as it lets you see exactly what the browser is doing (or not doing).

## 3. Tailoring Crawls with `CrawlerRunConfig`: Precision in Every Operation

*   3.1. **The Purpose of `CrawlerRunConfig`: Granular Control per Crawl**
    *   3.1.1. **Why it's distinct from `BrowserConfig`:**
        While `BrowserConfig` sets up the *global environment* for the browser (how it launches, its identity, network settings), `CrawlerRunConfig` dictates the *specifics for a single `arun()` operation*. This separation is crucial because you might use the same browser instance (configured once with `BrowserConfig`) to crawl multiple URLs, each requiring different processing steps. For example, one URL might need a screenshot, another might need JavaScript execution, and a third might target a specific CSS selector for content extraction.

    *   3.1.2. **How it empowers you to customize each `arun()` or tasks within `arun_many()`:**
        By passing a `CrawlerRunConfig` object to `crawler.arun()` (or as part of the task definition in `crawler.arun_many()`), you gain fine-grained control over:
        *   What part of the page to focus on (`css_selector`, `target_elements`).
        *   What content to exclude (`excluded_tags`, `excluded_selector`).
        *   How content is extracted and transformed (`extraction_strategy`, `markdown_generator`).
        *   Page interactions (`js_code`, `wait_for`).
        *   Media capture (`screenshot`, `pdf`).
        *   Link and media filtering.
        *   Caching behavior for that specific URL.
        *   And much more.
        This allows for highly tailored and efficient crawling workflows.

*   3.2. **Strategies for Effective Content Extraction**
    *   3.2.1. **Scoping Your Extraction (`css_selector`, `target_elements`)**
        *   **`css_selector`:**
            *   **Impact:** This parameter is powerful. When set, Crawl4ai attempts to isolate the HTML content to *only the element(s) matching this CSS selector* **before** most other processing (like cleaning, Markdown generation, or structured extraction) occurs. This means the `cleaned_html` and subsequently the `markdown` output will be derived *only* from this selected portion.
            *   **Use Case:** You want to extract only the main article body from a news website, ignoring headers, footers, sidebars, and ads. Setting `css_selector=".article-content"` would achieve this.
            *   **Benefit:** Significantly reduces noise and focuses all downstream processing on the relevant content, which can improve the quality of Markdown and structured data, and also speed up LLM-based extractions by providing less context.
        *   **`target_elements`:**
            *   **How it differs:** Unlike `css_selector` which pre-filters the raw HTML, `target_elements` (a list of CSS selectors) primarily influences *downstream processing*, particularly Markdown generation and structured data extraction strategies like `JsonCssExtractionStrategy`. The initial `cleaned_html` (if `css_selector` is not also used) will still represent the broader page content. However, when generating Markdown or extracting structured fields, only the content within these `target_elements` will be considered.
            *   **Use Case:** You want to generate Markdown primarily from the main article body (`<article>`) but also need to extract the author's name from a `<div class="author-bio">` and the publication date from a `<time>` element, which might be outside the main article. You could set `target_elements=["article", ".author-bio", "time"]`.
            *   **Benefit:** Allows for more nuanced content selection for different purposes. You can get a broad `cleaned_html` (useful for general context) while focusing Markdown generation and specific data extraction on distinct parts of the page.
        *   **Decision Guide: `css_selector` for pre-filtering raw HTML vs. `target_elements` for post-cleaning focus.**
            *   Use `css_selector` when you are confident that *all* relevant information for *all* downstream tasks (Markdown, structured extraction, etc.) is contained within a single, selectable region of the page. This is the most aggressive filtering.
            *   Use `target_elements` when you need to generate Markdown or extract data from *multiple, potentially disparate sections* of the page, or when your `extraction_strategy` needs to "see" more of the page structure to correctly identify fields that might be outside the main content block.
            *   You *can* use them together: `css_selector` would first limit the HTML, and then `target_elements` would further refine which parts of that limited HTML are used for specific downstream tasks.
        *   **Code Example: Illustrating the difference in output.**
            ```python
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, NoExtractionStrategy, DefaultMarkdownGenerator

            sample_html = """
            <html><body>
                <header><h1>Site Title</h1><nav><a>Home</a></nav></header>
                <main id='content'>
                    <article class='main-story'><h2>Article Heading</h2><p>Main article text.</p></article>
                    <aside class='sidebar'><p>Sidebar content.</p></aside>
                </main>
                <footer><p>Copyright info</p></footer>
            </body></html>
            """

            async def run_example():
                async with AsyncWebCrawler() as crawler:
                    # Scenario 1: Using css_selector
                    config_css = CrawlerRunConfig(css_selector="article.main-story")
                    result_css = await crawler.arun(url=f"raw://{sample_html}", config=config_css)
                    print(f"--- With css_selector='article.main-story' ---")
                    print(f"Cleaned HTML (snippet):\n{result_css.cleaned_html[:200]}\n") # Will be only the article
                    print(f"Markdown:\n{result_css.markdown.raw_markdown}\n")

                    # Scenario 2: Using target_elements
                    # Note: DefaultMarkdownGenerator implicitly uses target_elements if set.
                    # If no target_elements, it uses the whole cleaned_html (or content from css_selector if that's set).
                    config_target = CrawlerRunConfig(
                        target_elements=["article.main-story", "aside.sidebar"],
                        # To make the effect clear, let's use a custom Markdown generator
                        # that explicitly respects target_elements for its input.
                        # The default one would also work similarly.
                        markdown_generator=DefaultMarkdownGenerator()
                    )
                    result_target = await crawler.arun(url=f"raw://{sample_html}", config=config_target)
                    print(f"--- With target_elements=['article.main-story', 'aside.sidebar'] ---")
                    print(f"Cleaned HTML (snippet):\n{result_target.cleaned_html[:200]}\n") # Will be the whole page
                    print(f"Markdown (focused on targets):\n{result_target.markdown.raw_markdown}\n")
                    # The markdown here will primarily be from the article and sidebar combined.

                    # Scenario 3: Using both css_selector and target_elements
                    config_both = CrawlerRunConfig(
                        css_selector="main#content", # First, limit to main
                        target_elements=["article.main-story"] # Then, for markdown, only the article within main
                    )
                    result_both = await crawler.arun(url=f"raw://{sample_html}", config=config_both)
                    print(f"--- With css_selector='main#content' AND target_elements=['article.main-story'] ---")
                    print(f"Cleaned HTML (snippet):\n{result_both.cleaned_html[:200]}\n") # Will be main#content
                    print(f"Markdown (focused on article within main):\n{result_both.markdown.raw_markdown}\n")


            await run_example()
            ```

    *   3.2.2. **Refining Content by Exclusion (`excluded_tags`, `excluded_selector`)**
        *   **How `excluded_tags` globally removes unwanted tag types:** This parameter takes a list of HTML tag names (e.g., `['script', 'style', 'nav', 'footer', 'header', 'form', 'button', 'input', 'textarea', 'select', 'option']`). Before any other processing, Crawl4ai will remove all occurrences of these tags and their content from the HTML. This is a blunt but effective way to strip common non-content elements.
        *   **Using `excluded_selector` for more specific CSS-based exclusions:** If you need to remove elements based on their class, ID, or other attributes (e.g., ad banners with class `.ad-banner`, comment sections in `<div id="comments">`), provide a CSS selector string. All matching elements will be removed. This is more targeted than `excluded_tags`.
        *   **Impact on `cleaned_html` and subsequent Markdown/extraction:** Both `excluded_tags` and `excluded_selector` modify the HTML *before* it becomes the `cleaned_html` and before Markdown generation or structured data extraction. This means the excluded content will not appear in any downstream outputs.
        *   **Code Example: Removing navigation and footer before Markdown generation.**
            ```python
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

            sample_html_nav_footer = """
            <html><body>
                <nav><a>Home</a> <a>About</a></nav>
                <article><p>Main content here.</p></article>
                <div class="advertisement"><p>Buy now!</p></div>
                <footer><p>&copy; 2024</p></footer>
            </body></html>
            """

            async def run_exclusion_example():
                config_exclusions = CrawlerRunConfig(
                    excluded_tags=['nav', 'footer'],
                    excluded_selector=".advertisement"
                )
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url=f"raw://{sample_html_nav_footer}", config=config_exclusions)
                    print("--- HTML after exclusions ---")
                    print(result.cleaned_html)
                    print("\n--- Markdown after exclusions ---")
                    print(result.markdown.raw_markdown)
            
            await run_exclusion_example()
            # Expected output will not contain <nav>, <footer>, or <div class="advertisement">
            ```

    *   3.2.3. **Choosing Your Extraction Toolkit (`extraction_strategy`, `chunking_strategy`, `markdown_generator`, `only_text`)**
        *   **The default pipeline:** If you don't specify these, Crawl4ai uses:
            *   `WebScrapingStrategy` (which handles basic HTML cleaning, link/media extraction).
            *   `DefaultMarkdownGenerator` (which converts the `cleaned_html` to Markdown).
            *   `NoExtractionStrategy` (meaning `result.extracted_content` will be `None`).
        *   **When to use `only_text=True`:** If your sole goal is to get a plain text representation of the page's main content, and you don't need Markdown, HTML structure, or structured data, setting `only_text=True` can be a quick and efficient option. It typically tries to extract the "body" text and may perform some basic cleaning. The result will be in `result.markdown.raw_markdown` (despite the name, it will be plain text).
        *   **Plugging in `LLMExtractionStrategy`:**
            *   **Why:** This strategy is powerful when:
                *   The data you want is not easily selectable with CSS or XPath (e.g., it's embedded in prose).
                *   The website structure is inconsistent across pages.
                *   You need to infer or transform data based on context.
            *   **Workflow:**
                1.  Define a Pydantic model representing the schema of the data you want to extract.
                2.  Instantiate an `LLMConfig` with your LLM provider details.
                3.  Instantiate `LLMExtractionStrategy(schema=YourPydanticModel.model_json_schema(), llm_config=your_llm_config, instruction="Your specific extraction instructions...")`.
                4.  Pass this strategy to `CrawlerRunConfig(extraction_strategy=your_llm_extraction_strategy)`.
                The extracted data will be available as a JSON string in `result.extracted_content`.
            *   (Cross-reference to `LLMConfig` section for LLM-specific settings like `provider`, `api_token`, `temperature`).
        *   **Custom `chunking_strategy`:**
            *   By default, `LLMExtractionStrategy` might send the entire relevant HTML (or Markdown, depending on its `input_format`) to the LLM. If this content is too large for the LLM's context window, you can provide a `chunking_strategy` (e.g., `RegexChunking`) to `LLMExtractionStrategy`. This strategy will break the input into smaller, manageable chunks before sending them to the LLM.
            *   When to use: For very long documents where you still want to apply LLM extraction across the entire content.
        *   **Custom `markdown_generator`:**
            *   If the `DefaultMarkdownGenerator` doesn't produce Markdown in the exact style or with the specific conversions you need, you can implement your own class inheriting from `MarkdownGenerationStrategy` and pass an instance to `CrawlerRunConfig(markdown_generator=YourCustomMarkdownGenerator())`.
        *   **Code Example: Using `CrawlerRunConfig` with `LLMExtractionStrategy` for structured data from an article.**
            ```python
            from crawl4ai import (
                AsyncWebCrawler, CrawlerRunConfig, LLMConfig, 
                LLMExtractionStrategy, NoExtractionStrategy
            )
            from pydantic import BaseModel, Field
            import json
            import os

            # Define Pydantic schema for extraction
            class ArticleInfo(BaseModel):
                headline: str = Field(..., description="The main headline of the article")
                author: str = Field(None, description="The author of the article, if available")
                publication_date: str = Field(None, description="The publication date, if available")

            sample_article_html = """
            <html><body>
                <article>
                    <h1>Amazing Discovery in AI</h1>
                    <p class='byline'>By Dr. AI Expert on 2024-05-24</p>
                    <p>Scientists today announced a breakthrough...</p>
                </article>
            </body></html>
            """

            async def run_llm_extraction():
                # Configure LLM (using OpenAI for this example)
                # Ensure OPENAI_API_KEY is set in your environment
                llm_conf = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY"))
                
                extraction_strategy = LLMExtractionStrategy(
                    llm_config=llm_conf,
                    schema=ArticleInfo.model_json_schema(),
                    instruction="Extract the headline, author, and publication date from the article content."
                )

                config_llm_extract = CrawlerRunConfig(
                    extraction_strategy=extraction_strategy,
                    # LLMExtractionStrategy defaults to "markdown" input, so no need to change input_format
                    # unless you want to feed it raw HTML, then set extraction_strategy.input_format = "html"
                )

                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url=f"raw://{sample_article_html}", config=config_llm_extract)
                    if result.success and result.extracted_content:
                        extracted_data = json.loads(result.extracted_content)
                        # LLMExtractionStrategy often returns a list of extracted items
                        if isinstance(extracted_data, list) and extracted_data:
                             article_info = ArticleInfo(**extracted_data[0]) # Assuming one main article
                             print(f"Headline: {article_info.headline}")
                             print(f"Author: {article_info.author}")
                             print(f"Date: {article_info.publication_date}")
                        elif isinstance(extracted_data, dict) : # Sometimes it might be a single object
                             article_info = ArticleInfo(**extracted_data)
                             print(f"Headline: {article_info.headline}")
                             print(f"Author: {article_info.author}")
                             print(f"Date: {article_info.publication_date}")
                    else:
                        print(f"Extraction failed or no content: {result.error_message}")
            
            # await run_llm_extraction() # Uncomment to run, requires OPENAI_API_KEY
            ```

    *   3.2.4. **Attribute Handling (`keep_data_attributes`, `keep_attrs`)**
        *   **Why `keep_data_attributes=True` can be useful:** HTML `data-*` attributes are often used by JavaScript frameworks to store state or custom metadata. By default, many cleaning processes might strip these. If this data is important for your extraction or understanding of the page, set `keep_data_attributes=True`.
        *   **Using `keep_attrs` to preserve specific essential attributes:** `keep_attrs` takes a list of attribute names (e.g., `['href', 'src', 'id', 'class', 'title']`). During the HTML cleaning process, only these specified attributes (and `data-*` attributes if `keep_data_attributes` is true) will be retained on tags. All other attributes will be removed. This helps in producing cleaner, more focused HTML for downstream tasks.
            *   Default important attributes like `href` for `<a>` tags and `src` for `<img>` tags are usually kept by the default scraping strategy (`WebScrapingStrategy`) logic, but `keep_attrs` provides explicit control.
            ```python
            from crawl4ai import CrawlerRunConfig

            # Keep only 'id' and 'data-custom' attributes
            config_attrs = CrawlerRunConfig(
                keep_attrs=['id'], 
                keep_data_attributes=True # This would keep 'data-custom'
            )
            # Example of how it affects cleaned_html:
            # HTML: <div id="main" class="container" data-custom="value" style="color:red">Content</div>
            # Cleaned (conceptual): <div id="main" data-custom="value">Content</div>
            ```

*   3.3. **Managing Page Dynamics and Interactions**
    *   3.3.1. **Interacting with Dynamic Pages (`js_code`, `wait_for`, `scan_full_page`, `scroll_delay`)**
        *   **`js_code`:**
            *   **Executing arbitrary JavaScript:** This is your primary tool for interacting with page elements like clicking buttons, filling forms, expanding sections, or triggering custom JavaScript functions defined on the page.
            *   **Single strings vs. lists of JS commands:**
                *   A single string: For a simple, one-off action.
                *   A list of strings: For a sequence of actions. Crawl4ai will execute them in order.
            *   **Code Example: Clicking a "Load More" button multiple times (conceptual).**
                ```python
                # Conceptual - actual selector depends on the target site
                js_load_more_multiple = [
                    "document.querySelector('.load-more-button').click();",
                    "await new Promise(r => setTimeout(r, 2000));", # Wait 2s for content
                    "document.querySelector('.load-more-button').click();",
                    "await new Promise(r => setTimeout(r, 2000));", # Wait again
                    "document.querySelector('.load-more-button').click();"
                ]
                config_load_more = CrawlerRunConfig(js_code=js_load_more_multiple)
                # result = await crawler.arun(url="some-infinite-scroll-page.com", config=config_load_more)
                ```
        *   **`wait_for`:**
            *   **Ensuring critical content is present:** Many dynamic pages load content asynchronously. `wait_for` tells Crawl4ai to pause and wait until a specific condition is met before proceeding with content extraction or further `js_code` execution.
            *   **CSS selectors vs. JS expressions:**
                *   `wait_for="css:.my-element"`: Waits until an element matching the CSS selector `.my-element` appears in the DOM.
                *   `wait_for="js:() => window.myAppDataLoaded === true"`: Waits until the provided JavaScript expression evaluates to `true`. This is powerful for waiting on custom application states.
            *   **Impact on reliability:** Using `wait_for` dramatically increases the reliability of crawls on dynamic sites by preventing premature content extraction before necessary elements are loaded.
            *   **Code Example: Waiting for a specific `div` with ID `#results-container` to appear.**
                ```python
                config_wait_for_div = CrawlerRunConfig(
                    js_code="document.querySelector('#search-button').click();", # Perform a search
                    wait_for="css:#results-container" # Wait for results to load
                )
                # result = await crawler.arun(url="search-page.com", config=config_wait_for_div)
                ```
        *   **`scan_full_page` and `scroll_delay`:**
            *   **How this combination helps:**
                *   `scan_full_page=True`: Instructs Crawl4ai to attempt to scroll through the entire page, from top to bottom. This is designed to trigger lazy-loaded images or content that only appears as the user scrolls.
                *   `scroll_delay` (float, seconds): Specifies the pause duration between each scroll step during `scan_full_page`. A small delay (e.g., 0.2 to 0.5 seconds) gives the browser time to load newly visible content.
            *   **Tuning `scroll_delay`:** If images or content are still missing, try increasing `scroll_delay`. If the page loads quickly, a smaller delay might suffice.

    *   3.3.2. **Controlling Time (`page_timeout`, `wait_for_timeout`, `delay_before_return_html`, `mean_delay`, `max_range`)**
        *   **`page_timeout` and `wait_for_timeout`:**
            *   `page_timeout` (milliseconds, default from `config.PAGE_TIMEOUT` e.g., 60000): The maximum time allowed for the initial page navigation (the `page.goto()` call) to complete.
            *   `wait_for_timeout` (milliseconds): If `wait_for` is specified, this is the maximum time to wait for that condition to be met. If not set, it often defaults to `page_timeout`.
            *   **Purpose:** These prevent your crawler from hanging indefinitely on slow-loading pages or if a `wait_for` condition is never satisfied.
        *   **`delay_before_return_html` (float, seconds, default 0.1):**
            *   Sometimes, even after a page signals "load" or a `wait_for` condition is met, there might be final JavaScript rendering updates. This parameter introduces a small, fixed delay just before the HTML content is grabbed, potentially capturing these last-moment changes.
        *   **`mean_delay` & `max_range` (for `arun_many`):**
            *   These parameters are primarily used by dispatchers like `MemoryAdaptiveDispatcher` when you call `crawler.arun_many()`.
            *   `mean_delay` (seconds, default 0.1): The average base delay between consecutive requests to the *same domain*.
            *   `max_range` (seconds, default 0.3): A random amount of additional delay (between 0 and `max_range`) is added to `mean_delay`.
            *   **Purpose:** This introduces jitter and helps in polite crawling, making your requests less predictable and reducing the load on the target server.

    *   3.3.3. **Handling Embedded Content (`process_iframes`)**
        *   **When to set `process_iframes=True`:** If the content you need to extract is located inside an `<iframe>` on the page, setting this to `True` will instruct Crawl4ai to attempt to locate, access, and extract content from within iframes.
        *   **Limitations and complexities:**
            *   **Cross-Origin Restrictions:** Browsers enforce security policies that can prevent access to the content of iframes from a different domain unless specific CORS headers are set.
            *   **Nested Iframes:** Deeply nested iframes can be challenging to navigate.
            *   **Performance:** Processing iframes adds overhead and can slow down crawls.
            *   Currently, Crawl4ai's default iframe processing is basic and might merge content. For highly specific iframe interactions, you might need custom `js_code` targeting the iframe's content document.

*   3.4. **Media and Link Management Strategies**
    *   3.4.1. **Capturing Visuals and Documents (`screenshot`, `pdf`, `capture_mhtml`)**
        *   **Use cases:**
            *   `screenshot=True`: Captures a PNG image of the viewport (or full page if configured). Useful for visual verification, archiving page appearance, or when image-based analysis is needed. Result in `result.screenshot` (base64 string).
            *   `pdf=True`: Generates a PDF representation of the page. Good for archiving articles or creating printable versions. Result in `result.pdf` (bytes).
            *   `capture_mhtml=True`: Saves the page as an MHTML (.mht) archive. This format bundles all page resources (HTML, CSS, images, JS) into a single file, allowing for offline viewing with near-perfect fidelity. Result in `result.mhtml` (string).
        *   **How `scan_full_page` and `wait_for_images` can improve capture quality:**
            *   `scan_full_page=True`: Ensures lazy-loaded content is visible before capture.
            *   `wait_for_images=True`: Attempts to wait for images to fully load before taking a screenshot or PDF, leading to more complete visuals.

    *   3.4.2. **Curating Media (`image_score_threshold`, `exclude_external_images`, `exclude_all_images`)**
        *   **`image_score_threshold` (int, default from `config.IMAGE_SCORE_THRESHOLD` e.g., 3):**
            *   Crawl4ai internally scores images based on heuristics (size, alt text, proximity to content). This threshold filters out images with scores below the specified value. Higher values mean more stringent filtering (fewer, more "important" images).
        *   **`exclude_external_images=True`:** If set, images hosted on domains different from the crawled page's domain will be excluded from `result.media["images"]`. Useful for focusing on first-party content.
        *   **`exclude_all_images=True`:** If you don't need any image data at all, setting this to `True` will skip all image processing and `result.media["images"]` will be empty. This can improve performance.

    *   3.4.3. **Managing Links (`exclude_external_links`, `exclude_social_media_links`, `exclude_domains`, `exclude_internal_links`)**
        *   **Strategies for cleaning up the `links` output:**
            *   `exclude_external_links=True`: Only internal links (links to the same base domain) will be included in `result.links["internal"]`. `result.links["external"]` will be empty.
            *   `exclude_social_media_links=True`: Removes links pointing to common social media domains (Facebook, Twitter, LinkedIn, etc., defined in `config.SOCIAL_MEDIA_DOMAINS`) from both internal and external link lists.
            *   `exclude_domains=['ads.example.com', 'tracker.net']`: Provide a list of specific domains. Any link pointing to these domains will be excluded.
            *   `exclude_internal_links=True`: Only external links will be included in `result.links["external"]`. `result.links["internal"]` will be empty. Useful if you're only interested in outgoing links.

*   3.5. **Caching and Session Persistence (`cache_mode`, `session_id`)**
    *   3.5.1. **`cache_mode`: Optimizing for Speed and Freshness**
        *   This enum (`from crawl4ai import CacheMode`) controls how Crawl4ai interacts with its local cache for a given `arun()` call.
        *   `CacheMode.ENABLED` (Default if not set explicitly, but `CrawlerRunConfig` defaults to `BYPASS` if no `cache_mode` is passed in `__init__`):
            *   Reads from cache if a fresh entry exists for the URL.
            *   If not, fetches from the network and writes the result to the cache.
            *   **Use When:** Good for development to iterate quickly on parsing/extraction logic without re-fetching, or for crawling relatively static content.
        *   `CacheMode.BYPASS`:
            *   Ignores the cache completely. Always fetches the URL from the network.
            *   Does *not* write the result to the cache.
            *   **Use When:** You always need the absolute latest version of a page, or when debugging fetching/rendering issues.
        *   `CacheMode.READ_ONLY`:
            *   Only reads from the cache if an entry exists.
            *   Does *not* fetch from the network if the URL is not in the cache.
            *   Does *not* write to the cache.
            *   **Use When:** You want to run your processing logic strictly against a pre-existing cached dataset without making any network requests.
        *   `CacheMode.WRITE_ONLY`:
            *   Always fetches the URL from the network.
            *   Always writes (or overwrites) the result to the cache.
            *   Does *not* read from the cache before fetching.
            *   **Use When:** You want to populate or refresh your cache with the latest content.
        *   `CacheMode.DISABLED`:
            *   Completely disables any interaction with the cache system for this run. No reads, no writes.
            *   This is stronger than `BYPASS` as `BYPASS` might still involve some cache system overhead (e.g., checking if it should bypass).
            *   **Use When:** You want to ensure the cache system is not touched at all, perhaps for performance testing of raw fetching.
        *   **Decision Guide: Choosing the right cache mode.**
            *   **Development/Iteration:** `ENABLED` (to speed up repeated runs while changing extraction logic).
            *   **Production (Dynamic Content):** `BYPASS` or `ENABLED` with appropriate cache expiry (not directly settable via `CacheMode` but by cache implementation).
            *   **Production (Static/Archival Content):** `ENABLED` or `WRITE_ONLY` (for initial population) followed by `READ_ONLY` or `ENABLED`.
            *   **Testing against fixed data:** `READ_ONLY`.
            *   **Cache warming:** `WRITE_ONLY`.

    *   3.5.2. **`session_id`: Orchestrating Multi-Step Crawls**
        *   **How `session_id` allows sequential `arun()` calls to reuse the same browser page and context:**
            When you provide the same `session_id` string to multiple `arun()` calls within the *same* `AsyncWebCrawler` instance, Crawl4ai will reuse the existing browser page and its context (cookies, local storage, current URL, DOM state) for those calls, instead of opening a new page/tab for each.
        *   **Workflow: Simulating a login and subsequent data fetch.**
            1.  **First `arun()` (Establish Session & Login):**
                ```python
                # login_config = CrawlerRunConfig(
                #     url="https://example.com/login",
                #     session_id="my_secure_session",
                #     js_code=[
                #         "document.querySelector('#username').value = 'user';",
                #         "document.querySelector('#password').value = 'pass';",
                #         "document.querySelector('button[type=submit]').click();"
                #     ],
                #     wait_for="css:.user-dashboard" # Wait for a post-login element
                # )
                # login_result = await crawler.arun(config=login_config)
                ```
            2.  **Second `arun()` (Access Protected Page - using same `session_id`):**
                ```python
                # dashboard_config = CrawlerRunConfig(
                #     url="https://example.com/dashboard", # Navigate to a new page in the same session
                #     session_id="my_secure_session", # Crucial: same session_id
                #     # No js_code needed if already logged in, or add JS for dashboard interactions
                # )
                # dashboard_result = await crawler.arun(config=dashboard_config)
                ```
            3.  **Third `arun()` (Perform further actions - using same `session_id` and `js_only=True`):**
                If you just want to execute more JavaScript on the *current page* of the session without navigating:
                ```python
                # click_button_config = CrawlerRunConfig(
                #     session_id="my_secure_session",
                #     js_code="document.querySelector('#load-user-data-button').click();",
                #     wait_for="css:.user-data-loaded",
                #     js_only=True # Tells Crawl4ai not to navigate, just run JS on the current page
                # )
                # data_result = await crawler.arun(config=click_button_config)
                ```
        *   **Important: `js_only=True`**
            *   When `js_only=True` is set in `CrawlerRunConfig`, Crawl4ai will *not* perform a `page.goto(url)` operation. Instead, it will execute the provided `js_code` (if any) on the *current page* associated with the `session_id`.
            *   The `url` parameter in `CrawlerRunConfig` is effectively ignored when `js_only=True`.
            *   This is very useful for multi-step interactions on the same page (e.g., clicking multiple "load more" buttons, filling out different parts of a form sequentially).
        * **Cleaning Up:** Remember to kill the session when done to free up browser resources:
            ```python
            # await crawler.kill_session("my_secure_session")
            ```

*   3.6. **Best Practices for `CrawlerRunConfig`**
    *   3.6.1. **Test selectors and JS snippets in your browser's developer console first:** This saves a lot of time and helps ensure your selectors are correct and your JS code behaves as expected before integrating it into Crawl4ai.
    *   3.6.2. **Start with broader selectors and refine if necessary:** It's often easier to start with a more general `css_selector` or `target_elements` and then narrow it down if you're getting too much noise, rather than starting too specific and missing content.
    *   3.6.3. **Use `cache_mode=CacheMode.BYPASS` when testing changes** to selectors, JS code, or extraction strategies to ensure you're always working with fresh page content.
    *   3.6.4. **Combine `js_code` with appropriate `wait_for` conditions for reliability:** Don't assume JS actions complete instantly. Always wait for a clear indicator (an element appearing, a JS variable changing) that the action has had its desired effect.

*   3.7. **Troubleshooting Common `CrawlerRunConfig` Issues**
    *   3.7.1. **Content not being extracted as expected:**
        *   **Selector Issues:** Double-check your `css_selector` or selectors within your `extraction_strategy`. Test them in the browser devtools.
        *   **Dynamic Content Not Loaded:** The content might be loaded by JavaScript after the initial page load. Use `wait_for`, `js_code` to trigger loading, or `scan_full_page`. Try with `headless=False` in `BrowserConfig` to see what the browser is actually rendering.
    *   3.7.2. **Timeouts:**
        *   **Page taking too long:** Increase `page_timeout`.
        *   **`wait_for` condition never met:** Your selector might be wrong, the JS condition might never become true, or the element simply doesn't appear within the `wait_for_timeout`. Debug with `headless=False`.
    *   3.7.3. **JavaScript errors:**
        *   Set `log_console=True` in `BrowserConfig` (or the `arun` call directly if supported) to see browser console messages, which can reveal JS errors.
        *   Test your `js_code` snippets in the browser console.
    *   3.7.4. **`extraction_strategy` not yielding desired output:**
        *   **For `JsonCssExtractionStrategy`:** Verify your schema selectors.
        *   **For `LLMExtractionStrategy`:** Refine your Pydantic schema, improve your `instruction`, adjust `LLMConfig` parameters (like `temperature`), or provide better/more context if using `chunking_strategy`. Ensure the `input_format` for the strategy ("markdown" or "html") matches the type of content that will yield the best results from the LLM.

## 4. Configuring LLM Interactions with `LLMConfig`

*   4.1. **Purpose: Centralized LLM Settings**
    *   4.1.1. **Why `LLMConfig` is essential when using `LLMExtractionStrategy`, `LLMContentFilter`, or other LLM-powered components.**
        When your crawling workflow involves interacting with Large Language Models (e.g., for extracting structured data from unstructured text using `LLMExtractionStrategy`, or for filtering relevant content using `LLMContentFilter`), `LLMConfig` provides a dedicated and centralized place to manage all settings related to these interactions. This includes specifying which LLM provider and model to use, API keys, and parameters that control the LLM's generation behavior (like temperature, max tokens, etc.).

    *   4.1.2. **How it promotes consistency in LLM calls.**
        By encapsulating LLM settings in a separate object, you ensure that:
        *   All LLM-powered components in your Crawl4ai setup can share the same configuration if desired, leading to consistent behavior.
        *   You can easily switch LLM providers or models by changing the `LLMConfig` in one place, without needing to modify every strategy that uses an LLM.
        *   LLM-specific details are kept separate from the core browser and crawl run configurations, improving code organization.

*   4.2. **Core `LLMConfig` Parameters and Their Impact**
    *   4.2.1. **Provider Setup (`provider`, `api_token`, `base_url`)**
        *   **Choosing the right `provider` (e.g., "openai/gpt-4o-mini", "ollama/llama3", "groq/llama3-70b-8192"):**
            *   Crawl4ai leverages the [LiteLLM](https://litellm.ai/) library, which supports a vast range of LLM providers (OpenAI, Azure OpenAI, Anthropic, Cohere, Google Gemini, Ollama, Groq, and many more). The `provider` string typically follows the format `"provider_name/model_name"`.
            *   **Considerations for choosing a provider/model:**
                *   **Cost:** Different models and providers have varying pricing structures.
                *   **Model Capabilities:** Some models excel at specific tasks (e.g., instruction following, summarization, code generation).
                *   **Context Window Size:** The maximum amount of text the model can process at once.
                *   **Speed/Latency:** How quickly the model responds.
                *   **Availability & Rate Limits:** Ensure the provider can handle your expected load.
                *   **Open vs. Closed Source:** Ollama allows running open-source models locally, while others are API-based.
        *   **`api_token`: How to securely provide API keys (direct string vs. `env:YOUR_ENV_VAR`).**
            *   **Direct String:** You can pass the API key directly: `api_token="sk-..."`. **Not recommended for production code.**
            *   **Environment Variable (Recommended):** Use the `env:` prefix to tell Crawl4ai to read the key from an environment variable: `api_token="env:OPENAI_API_KEY"`. This is much more secure as it keeps secrets out of your codebase. Crawl4ai automatically looks for common environment variables like `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, etc., based on the `provider` if `api_token` is not explicitly set.
        *   **`base_url`: When to use this for self-hosted models (like local Ollama) or custom API gateways.**
            *   If you are running an LLM locally (e.g., using Ollama, which defaults to `http://localhost:11434`), or if you are routing API calls through a custom gateway or proxy, you'll need to set the `base_url` to point to the correct endpoint.
            *   For many cloud providers, LiteLLM knows the default `base_url`, so you often don't need to set it.
        *   **Code Example: Configuring for OpenAI vs. a local Ollama instance.**
            ```python
            from crawl4ai import LLMConfig
            import os

            # OpenAI Configuration (assumes OPENAI_API_KEY is set in environment)
            openai_config = LLMConfig(
                provider="openai/gpt-4o-mini",
                # api_token=os.getenv("OPENAI_API_KEY") # Or let Crawl4ai find it
            )
            print(f"OpenAI Provider: {openai_config.provider}")

            # Local Ollama Configuration (Llama3 running via Ollama)
            ollama_config = LLMConfig(
                provider="ollama/llama3", 
                base_url="http://localhost:11434", # Default Ollama endpoint
                api_token="ollama" # Standard token for Ollama if no specific auth
            )
            print(f"Ollama Provider: {ollama_config.provider}, Base URL: {ollama_config.base_url}")
            
            # Groq Configuration (Llama3-70b via Groq, fast inference)
            groq_config = LLMConfig(
                provider="groq/llama3-70b-8192",
                api_token=os.getenv("GROQ_API_KEY") # Needs GROQ_API_KEY env var
            )
            print(f"Groq Provider: {groq_config.provider}")
            ```

    *   4.2.2. **Fine-tuning LLM Generation (`temperature`, `max_tokens`, `top_p`, etc.)**
        These parameters control the behavior of the LLM when it generates text.
        *   **`temperature` (float, typically 0.0 to 2.0):**
            *   Controls the randomness of the output.
            *   Lower values (e.g., 0.0 - 0.3): More deterministic, focused, and factual. Good for precise data extraction or when you want predictable output based on a strict schema.
            *   Higher values (e.g., 0.7 - 1.0+): More creative, diverse, and potentially surprising. Better for tasks like summarization, brainstorming, or generating varied text.
        *   **`max_tokens` (int):**
            *   The maximum number of tokens (words/sub-words) the LLM should generate in its response.
            *   Crucial for managing costs (as most APIs charge per token) and ensuring the output doesn't become excessively long.
            *   Set it based on the expected length of your desired output (e.g., for a short summary vs. a detailed extraction).
        *   **`top_p` (float, typically 0.0 to 1.0):**
            *   An alternative to `temperature` for controlling randomness, known as nucleus sampling. The model considers only the tokens whose cumulative probability mass exceeds `top_p`.
            *   A common value is 0.9. Lower values make the output more focused.
            *   Usually, you'd use either `temperature` or `top_p`, not both simultaneously (or set one to its neutral default, e.g., `top_p=1.0` if using `temperature`).
        *   **Other parameters (`frequency_penalty`, `presence_penalty`, `stop`, `n`):**
            *   `frequency_penalty` (float): Penalizes tokens that have already appeared frequently, encouraging the model to use different words.
            *   `presence_penalty` (float): Penalizes tokens that have appeared at all, encouraging novelty.
            *   `stop` (string or list of strings): Sequences where the API will stop generating further tokens.
            *   `n` (int): How many completions to generate for each prompt.
            *   **When to use:** These are more advanced and used for specific fine-tuning, e.g., reducing repetition or generating multiple candidate outputs. Consult your LLM provider's documentation for details on how they interpret these.
        *   **Use Case: Adjusting parameters for extracting a strict JSON schema vs. generating a summary.**
            *   **Strict JSON Schema Extraction:** `temperature=0.1`, `top_p=1.0` (or not set), `max_tokens` appropriate for the schema size.
            *   **Creative Summary Generation:** `temperature=0.7`, `top_p=0.9`, `max_tokens` set to desired summary length.

*   4.3. **Workflow: Integrating `LLMConfig` in Your Crawl**
    *   4.3.1. **Step 1: Instantiate `LLMConfig` with your desired settings.**
        ```python
        from crawl4ai import LLMConfig
        import os
        
        my_llm_config = LLMConfig(
            provider="openai/gpt-4o-mini",
            api_token=os.getenv("OPENAI_API_KEY"),
            temperature=0.2,
            max_tokens=1024
        )
        ```
    *   4.3.2. **Step 2: Pass the `LLMConfig` instance to an LLM-dependent strategy.**
        For example, if using `LLMExtractionStrategy`:
        ```python
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
        from pydantic import BaseModel

        class MyData(BaseModel):
            name: str
            value: int

        llm_extraction_strategy = LLMExtractionStrategy(
            llm_config=my_llm_config,
            schema=MyData.model_json_schema(),
            instruction="Extract name and value."
        )
        ```
    *   4.3.3. **Step 3: Include that strategy in your `CrawlerRunConfig`.**
        ```python
        from crawl4ai import CrawlerRunConfig

        my_run_config = CrawlerRunConfig(
            extraction_strategy=llm_extraction_strategy
            # ... other run config settings
        )
        ```
    *   **Code Example: A complete flow showing `LLMConfig` -> `LLMExtractionStrategy` -> `CrawlerRunConfig` -> `arun()`.**
        ```python
        from crawl4ai import AsyncWebCrawler, LLMConfig, LLMExtractionStrategy, CrawlerRunConfig
        from pydantic import BaseModel, Field
        import json
        import os

        class Product(BaseModel):
            product_name: str = Field(description="The name of the product")
            price: float = Field(description="The price of the product")

        sample_product_page_html = """
        <html><body>
            <div class='product-details'>
                <h2>Awesome Gadget X1000</h2>
                <p class='price-tag'>Price: $99.99</p>
                <p>This gadget does amazing things...</p>
            </div>
        </body></html>
        """

        async def run_full_llm_flow():
            # 1. LLMConfig
            llm_conf = LLMConfig(
                provider="openai/gpt-4o-mini", 
                api_token=os.getenv("OPENAI_API_KEY"), # Ensure this is set
                temperature=0.1
            )

            # 2. LLMExtractionStrategy
            product_extraction_strategy = LLMExtractionStrategy(
                llm_config=llm_conf,
                schema=Product.model_json_schema(),
                instruction="From the provided HTML, extract the product name and its price."
            )

            # 3. CrawlerRunConfig
            product_run_config = CrawlerRunConfig(
                extraction_strategy=product_extraction_strategy,
                # LLMExtractionStrategy expects HTML input by default if input_format is not changed
                input_format="html" # Explicitly telling the strategy to use HTML
            )

            # 4. AsyncWebCrawler and arun()
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=f"raw://{sample_product_page_html}", 
                    config=product_run_config
                )

                if result.success and result.extracted_content:
                    try:
                        extracted_data_list = json.loads(result.extracted_content)
                        if extracted_data_list: # LLMExtractionStrategy often returns a list
                            product_info = Product(**extracted_data_list[0])
                            print(f"Product: {product_info.product_name}, Price: ${product_info.price}")
                        else:
                            print("LLM returned no data.")
                    except json.JSONDecodeError:
                        print(f"Failed to parse LLM JSON output: {result.extracted_content}")
                    except Exception as e:
                        print(f"Error processing extracted data: {e}")
                else:
                    print(f"Crawl or extraction failed: {result.error_message}")
        
        # if os.getenv("OPENAI_API_KEY"):
        #     await run_full_llm_flow()
        # else:
        #     print("OPENAI_API_KEY not set. Skipping LLMConfig example.")
        ```

*   4.4. **Best Practices for `LLMConfig`**
    *   4.4.1. **Use environment variables for API keys:** Never hardcode API keys in your scripts. Use `api_token="env:YOUR_KEY_NAME"`.
    *   4.4.2. **Start with conservative `max_tokens`:** This helps manage costs, especially during testing. Increase it only if necessary for the desired output length.
    *   4.4.3. **Test prompts and parameters iteratively:** LLM behavior can be sensitive to prompting and parameters. Start with simple prompts and gradually refine them. Test with low `temperature` for predictability first.
    *   4.4.4. **Be aware of rate limits:** Different LLM providers have different rate limits. If you're making many calls, implement appropriate delays or use a queueing system to avoid hitting these limits. Crawl4ai's built-in backoff in `perform_completion_with_backoff` helps, but sustained high volume might still be an issue.

*   4.5. **Troubleshooting `LLMConfig` and LLM Interactions**
    *   4.5.1. **Authentication errors (invalid API key, incorrect provider string):**
        *   Double-check your `api_token` and ensure the environment variable is correctly set and accessible.
        *   Verify the `provider` string matches one supported by LiteLLM and that you have the necessary access/credits for that provider.
        *   If using `base_url`, ensure it's correct and the local LLM server (like Ollama) is running.
    *   4.5.2. **LLM not following instructions or schema (if `extraction_type="schema"`):**
        *   **Prompt Engineering:** This is key. Your `instruction` needs to be very clear, specific, and unambiguous. Provide examples within the prompt if necessary.
        *   **Parameter Tuning:** Adjust `temperature`. For schema extraction, very low (e.g., 0.0 or 0.1) is usually best.
        *   **Model Choice:** Some models are better at instruction-following or JSON generation than others. Experiment if one model isn't working.
        *   **Schema Complexity:** If your Pydantic schema is very complex, the LLM might struggle. Try simplifying it or breaking down the extraction into multiple steps/prompts.
        *   **Input Content:** Ensure the `input_format` for your `LLMExtractionStrategy` ("markdown" or "html") provides the LLM with the most useful version of the content. Sometimes, clean Markdown is better; other times, the raw HTML structure helps.
    *   4.5.3. **Rate limit errors from the LLM provider:**
        *   The `perform_completion_with_backoff` utility in Crawl4ai attempts to handle transient rate limits with exponential backoff.
        *   If you consistently hit rate limits, you may need to reduce the concurrency of your LLM calls (e.g., process fewer chunks in parallel) or request a higher rate limit from your provider.
    *   4.5.4. **Unexpectedly high costs (monitor token usage):**
        *   Keep `max_tokens` as low as feasible for your task.
        *   Be mindful of input token count, especially if using `LLMExtractionStrategy` on large chunks of text. Optimize `chunk_size` in your `chunking_strategy`.
        *   Monitor your LLM provider's billing dashboard regularly.

## 5. Specialized Configuration Objects: `GeolocationConfig`, `ProxyConfig`, `HTTPCrawlerConfig`

These objects provide targeted configuration for specific advanced crawling needs.

*   5.1. **Simulating Location with `GeolocationConfig`**
    *   5.1.1. **Purpose: Why you might need to make the browser appear from a specific geographic location.**
        Websites can serve different content, prices, or even different site versions based on the user's perceived geographic location (often determined by IP address, but also potentially by browser geolocation APIs). `GeolocationConfig` allows you to override the browser's reported GPS coordinates.
    *   5.1.2. **Use Cases:**
        *   **Accessing Geo-Restricted Websites or Content:** Some sites block access or show limited content to users outside specific regions.
        *   **Testing Localization and Internationalization:** Verify that your website correctly displays language, currency, and content for different locales.
        *   **Scraping Geo-Specific Data:** Collect data that varies by location, like local search results, store availability, or regional pricing.
    *   5.1.3. **How to use:**
        1.  Instantiate `GeolocationConfig` with the desired `latitude`, `longitude`, and optionally `accuracy` (in meters).
            ```python
            from crawl4ai.async_configs import GeolocationConfig
            paris_location = GeolocationConfig(latitude=48.8566, longitude=2.3522, accuracy=50.0)
            ```
        2.  Pass this object to the `geolocation` parameter of `CrawlerRunConfig`.
            ```python
            from crawl4ai import CrawlerRunConfig
            run_config_paris = CrawlerRunConfig(geolocation=paris_location)
            ```
        *   **Important Note:** For `GeolocationConfig` to be truly effective in making a website *believe* you are in that location, you usually also need to route your traffic through a **proxy server located in that same geographic region**. Setting GPS coordinates alone might not be enough if your IP address still points to your actual location.
    *   5.1.4. **Interaction with browser permissions (Playwright handles this implicitly when geolocation is set).**
        When you set geolocation via Playwright (which Crawl4ai uses under the hood), it typically also grants the necessary browser permission for the page to access this spoofed location information, mimicking a user clicking "Allow" on a location access prompt.
    *   **Code Example: Crawling a site as if from Paris, France (assuming a Paris proxy is also configured in `BrowserConfig`).**
        ```python
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, GeolocationConfig

        async def crawl_from_paris():
            # Assume proxy_for_paris is configured in BrowserConfig
            # For this example, we'll just show GeolocationConfig
            paris_browser_config = BrowserConfig(
                # proxy_config={"server": "http://paris-proxy.example.com:8080"} # Illustrative
            )
            
            paris_location = GeolocationConfig(latitude=48.8566, longitude=2.3522, accuracy=100.0)
            
            # Also good to set locale and timezone to match
            paris_run_config = CrawlerRunConfig(
                geolocation=paris_location,
                locale="fr-FR",
                timezone_id="Europe/Paris"
            )

            async with AsyncWebCrawler(config=paris_browser_config) as crawler:
                # A site that shows location-based info
                result = await crawler.arun(url="https://www.iplocation.net/", config=paris_run_config)
                if result.success:
                    print("--- Page content (should reflect Paris if proxy and geo are working) ---")
                    print(result.markdown.raw_markdown[:500]) 
                else:
                    print(f"Crawl failed: {result.error_message}")
        
        # await crawl_from_paris()
        ```

*   5.2. **Detailed Proxy Setup with `ProxyConfig`**
    *   5.2.1. **When to use `ProxyConfig` object vs. the simpler `proxy` string in `BrowserConfig`.**
        *   The `proxy` parameter directly in `BrowserConfig` (e.g., `BrowserConfig(proxy="http://user:pass@host:port")`) is a simpler way to set a proxy for Playwright, but it's a Playwright-level string.
        *   The `proxy_config` parameter in `BrowserConfig` expects a dictionary like `{"server": "...", "username": "...", ...}` which Playwright also accepts.
        *   The `crawl4ai.async_configs.ProxyConfig` object is a Pydantic model that helps structure these details, especially useful if you are:
            *   Programmatically constructing proxy configurations.
            *   Building a custom `ProxyRotationStrategy` that needs to manage a list of `ProxyConfig` objects.
            *   Needing to store or pass around proxy details in a typed way.
            *   It also includes an `ip` field, which can be useful for internal tracking or verification, though it's not directly used by Playwright's connection mechanism.
        When passing to `BrowserConfig(proxy_config=...)`, you'd typically use `my_proxy_config_object.to_dict()`.
    *   5.2.2. **Key parameters of `ProxyConfig` object: `server`, `username`, `password`, `ip`.**
        *   `server` (str): The proxy server URL (e.g., `"http://127.0.0.1:8080"`, `"socks5://myproxy.com:1080"`).
        *   `username` (Optional[str]): Username for proxy authentication.
        *   `password` (Optional[str]): Password for proxy authentication.
        *   `ip` (Optional[str]): The IP address of the proxy. This is more for your internal tracking or if your proxy provider gives you an outbound IP to verify against; Playwright itself primarily uses the `server` field for connection.
    *   5.2.3. **How `ProxyConfig` instances are typically managed by a `ProxyRotationStrategy`.**
        If you're using a `ProxyRotationStrategy` (detailed in its own documentation section), that strategy would typically hold a list of `ProxyConfig` objects. Its `get_next_proxy()` method would return one of these `ProxyConfig` objects, which would then be used to configure the `proxy_config` (via its dictionary representation) for a `BrowserConfig` or directly within a `CrawlerRunConfig` if the strategy involves per-run proxy changes.
    *   **Code Example: Creating `ProxyConfig` objects.**
        ```python
        from crawl4ai.async_configs import ProxyConfig, BrowserConfig

        # Create ProxyConfig objects
        proxy1 = ProxyConfig(
            server="http://proxy1.example.com:8000", 
            username="user1", 
            password="password1",
            ip="1.2.3.4" # For your reference
        )
        proxy2 = ProxyConfig(
            server="socks5://proxy2.example.com:1080",
            ip="5.6.7.8"
        )

        print(f"Proxy 1 Server: {proxy1.server}")
        
        # To use with BrowserConfig:
        # browser_cfg = BrowserConfig(proxy_config=proxy1.to_dict())
        # Or if you have a list and a rotation strategy:
        # rotation_strategy = RoundRobinProxyStrategy(proxies=[proxy1, proxy2])
        # next_proxy_obj = await rotation_strategy.get_next_proxy()
        # if next_proxy_obj:
        #     browser_cfg = BrowserConfig(proxy_config=next_proxy_obj.to_dict())
        ```

*   5.3. **Lightweight Crawling with `HTTPCrawlerConfig`**
    *   5.3.1. **Understanding the `AsyncHTTPCrawlerStrategy`:**
        *   **When it's a better choice:** The default `AsyncPlaywrightCrawlerStrategy` uses a full browser (Playwright), which is powerful but resource-intensive. For tasks that don't require JavaScript execution, complex DOM interactions, or browser rendering, the `AsyncHTTPCrawlerStrategy` is a much lighter and faster alternative. It makes direct HTTP requests using the `requests` library (via `httpx` for async).
        *   Ideal for:
            *   Scraping static HTML sites.
            *   Accessing APIs that return JSON, XML, or other text-based data.
            *   Downloading files directly.
        *   **Trade-offs:**
            *   Cannot execute JavaScript. Content rendered by client-side JS will be missed.
            *   No DOM interaction capabilities (like clicking buttons).
            *   Doesn't handle complex browser features like cookies or sessions automatically in the same way Playwright does (though you can manage headers manually).
    *   5.3.2. **Purpose of `HTTPCrawlerConfig`: Tailoring direct HTTP requests.**
        When you use `AsyncHTTPCrawlerStrategy`, the `HTTPCrawlerConfig` object allows you to specify details for the HTTP request itself, such as the method, headers, and body data.
    *   5.3.3. **Key Parameters of `HTTPCrawlerConfig`:**
        *   `method` (str, default "GET"): The HTTP method (e.g., "GET", "POST", "PUT", "DELETE").
        *   `headers` (Optional[Dict[str, str]]): Custom HTTP headers to send with the request.
        *   `data` (Optional[Dict[str, Any]]): Dictionary of data to be form-urlencoded and sent in the request body (typically for "POST" requests with `Content-Type: application/x-www-form-urlencoded`).
        *   `json` (Optional[Dict[str, Any]]): Dictionary of data to be JSON-encoded and sent in the request body (typically for "POST" or "PUT" requests with `Content-Type: application/json`).
        *   `follow_redirects` (bool, default True): Whether `httpx` should automatically follow HTTP redirects (3xx status codes).
        *   `verify_ssl` (bool, default True): Whether to verify SSL certificates. Set to `False` with caution, similar to `ignore_https_errors` in `BrowserConfig`.
    *   5.3.4. **Workflow:**
        1.  Instantiate `AsyncHTTPCrawlerStrategy`.
            ```python
            from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
            http_strategy = AsyncHTTPCrawlerStrategy()
            ```
        2.  Create an `AsyncWebCrawler` instance, passing this strategy.
            ```python
            # crawler = AsyncWebCrawler(crawler_strategy=http_strategy)
            ```
        3.  When calling `crawler.arun()`, if you need to customize the HTTP request (e.g., for a POST), create an `HTTPCrawlerConfig` and pass it via `CrawlerRunConfig`.
            ```python
            from crawl4ai.async_configs import HTTPCrawlerConfig, CrawlerRunConfig
            
            # http_post_config = HTTPCrawlerConfig(
            #     method="POST",
            #     json={"key": "value"},
            #     headers={"X-Custom-Header": "MyValue"}
            # )
            # run_config_http = CrawlerRunConfig(
            #     # Note: When using AsyncHTTPCrawlerStrategy, its specific config
            #     # is often passed directly to arun or its strategy methods,
            #     # rather than through CrawlerRunConfig's generic 'experimental' field.
            #     # However, let's assume for consistency or future enhancement
            #     # it could be passed like this:
            #     experimental={"http_crawler_config": http_post_config.to_dict()}
            # )
            # For current direct use with arun():
            # result = await crawler.arun(
            #     url="https://api.example.com/submit",
            #     method="POST", # Pass directly to arun when using AsyncHTTPCrawlerStrategy
            #     json_data={"key": "value"}, # Pass directly
            #     headers={"X-Custom-Header": "MyValue"} # Pass directly
            # )
            ```
            **Correction/Clarification:** `AsyncHTTPCrawlerStrategy.crawl()` directly accepts `method`, `headers`, `data`, `json_data`, etc. as keyword arguments. `HTTPCrawlerConfig` is more of a Pydantic model to structure these, but they are passed directly to `arun` when the active strategy is `AsyncHTTPCrawlerStrategy`. `CrawlerRunConfig` is less relevant for these HTTP-specific parameters when *not* using a browser-based strategy.

    *   **Code Example: Fetching data from a JSON API using `AsyncHTTPCrawlerStrategy`.**
        ```python
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
        import json

        async def fetch_json_api():
            # 1. Use AsyncHTTPCrawlerStrategy
            http_strategy = AsyncHTTPCrawlerStrategy()
            
            # 2. Create Crawler with this strategy
            async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
                # 3. Call arun, passing HTTP-specific params directly
                result = await crawler.arun(
                    url="https://jsonplaceholder.typicode.com/todos/1",
                    method="GET" # Default, but explicit here
                )

                if result.success:
                    print(f"Status Code: {result.status_code}")
                    try:
                        # The 'html' field will contain the raw response body
                        todo_data = json.loads(result.html) 
                        print("Fetched TODO Data:")
                        print(todo_data)
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON response: {result.html[:200]}")
                else:
                    print(f"API call failed: {result.error_message}")

        # await fetch_json_api()
        ```

## 6. Efficiently Managing Configurations: `clone()`, `dump()`, and `load()`

*   6.1. **The Rationale: Why Manage Configurations Programmatically?**
    Manually creating and managing numerous configuration objects with slight variations can quickly become tedious, error-prone, and lead to code duplication. Crawl4ai provides `clone()`, `dump()`, and `load()` methods on its configuration objects (`BrowserConfig`, `CrawlerRunConfig`, `LLMConfig`, etc.) to address these challenges. Programmatic management offers:
    *   **Reduced Repetition:** Define base configurations once and create variations easily.
    *   **Modularity and Reusability:** Store and load common configurations, promoting a "don't repeat yourself" (DRY) approach.
    *   **Persistence:** Save configurations to files (JSON, YAML) for later use, version control, or sharing across different scripts or team members.
    *   **Dynamic Configuration:** Load or modify configurations at runtime based on external inputs or application logic.
    *   **Improved Readability:** Complex setups can be broken down into smaller, named configurations, making the overall code easier to understand.

*   6.2. **`clone(**kwargs)`: Creating Variations with Ease**
    *   6.2.1. **How it works:** The `clone()` method, available on configuration objects like `BrowserConfig` and `CrawlerRunConfig`, performs a *deep copy* of the original configuration object. You can then pass keyword arguments to `clone()` to override specific attributes in the newly created copy. The original object remains unchanged.
    *   6.2.2. **Use Cases:**
        *   **Creating slightly different `CrawlerRunConfig` objects:**
            *   For different sections of a website (e.g., product pages vs. blog posts) that share most crawl settings but require different `extraction_strategy` or `css_selector`.
            *   For A/B testing different `wait_for` conditions or `js_code` snippets.
        *   **Generating multiple `BrowserConfig` instances:**
            *   For testing with different user agents, proxy settings, or headless modes while keeping other browser settings consistent.
    *   6.2.3. **Code Example:**
        ```python
        from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode
        # from crawl4ai.extraction_strategy import SomeExtractionStrategy # Placeholder

        # --- BrowserConfig Cloning ---
        base_browser_config = BrowserConfig(
            headless=True,
            user_agent="MyDefaultAgent/1.0"
        )

        # Clone for debugging (headful)
        debug_browser_config = base_browser_config.clone(headless=False, verbosity=True)
        print(f"Base headless: {base_browser_config.headless}, Debug headless: {debug_browser_config.headless}")

        # Clone for a specific mobile UA
        mobile_browser_config = base_browser_config.clone(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"
        )
        print(f"Mobile UA: {mobile_browser_config.user_agent}")

        # --- CrawlerRunConfig Cloning ---
        base_run_config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            word_count_threshold=50,
            screenshot=False
        )

        # Config for scraping articles, needs specific extraction and screenshot
        # Assuming ArticleExtractionStrategy is a defined class
        # article_strategy = SomeExtractionStrategy(type="article") 
        article_run_config = base_run_config.clone(
            # extraction_strategy=article_strategy, 
            screenshot=True,
            css_selector="main.article-body"
        )
        print(f"Article config screenshot: {article_run_config.screenshot}, CSS: {article_run_config.css_selector}")

        # Config for scraping product listings, different strategy, no screenshot
        # Assuming ProductListExtractionStrategy is a defined class
        # product_list_strategy = SomeExtractionStrategy(type="product_list")
        product_list_run_config = base_run_config.clone(
            # extraction_strategy=product_list_strategy,
            css_selector="ul.product-grid"
        )
        print(f"Product list screenshot: {product_list_run_config.screenshot}, CSS: {product_list_run_config.css_selector}")
        ```

*   6.3. **`dump()` and `load(data: dict)`: Persistence and Portability**
    *   6.3.1. **`dump()`:**
        *   **How it serializes:** The `dump()` method converts the configuration object's state into a Python dictionary. This dictionary is designed to be JSON-serializable, meaning it contains only basic Python types (strings, numbers, booleans, lists, dictionaries) and representations of nested configuration objects.
        *   **What can be serialized:**
            *   Basic attributes (strings, ints, bools).
            *   Nested Crawl4ai configuration objects (e.g., a `GeolocationConfig` within a `CrawlerRunConfig` will also be `dump`ed).
            *   Enum members are typically serialized to their string values.
        *   **Limitations:** `dump()` primarily serializes the *configurable parameters* of the object. It generally cannot serialize:
            *   Arbitrary Python objects assigned to attributes (e.g., custom, non-Crawl4ai class instances like a complex `extraction_strategy` instance that isn't just a basic Crawl4ai strategy). If you need to persist such complex objects, you'd typically handle their serialization and deserialization separately (e.g., using `pickle` with caution, or by re-instantiating them based on some stored identifier).
            *   Runtime state that isn't part of the initial configuration.
    *   6.3.2. **`load(data: dict)`:**
        *   **How it reconstructs:** This is a *static method* on the configuration class (e.g., `BrowserConfig.load(my_dict)`). It takes a dictionary (usually one produced by `dump()`) and creates a new instance of the configuration object, populating it with the values from the dictionary.
        *   **Ensuring dictionary structure:** The input dictionary should have keys that correspond to the parameters of the configuration object's `__init__` method or its settable attributes. Nested config objects in the dictionary will also be reconstructed using their respective `load()` methods.
    *   6.3.3. **Workflow: Saving and Loading Configurations**
        1.  **Create and Configure:** Instantiate and set up your config object.
            ```python
            # my_browser_config = BrowserConfig(user_agent="TestAgent/1.0", headless=False)
            ```
        2.  **Dump to Dictionary:**
            ```python
            # config_dict = my_browser_config.dump()
            ```
        3.  **Save to File (e.g., JSON):**
            ```python
            import json
            # with open("browser_settings.json", "w") as f:
            #     json.dump(config_dict, f, indent=4)
            ```
        4.  **Later, Load from File:**
            ```python
            # with open("browser_settings.json", "r") as f:
            #     loaded_dict_from_file = json.load(f)
            ```
        5.  **Reconstruct Object using `load()`:**
            ```python
            # loaded_browser_config = BrowserConfig.load(loaded_dict_from_file)
            # print(f"Loaded User-Agent: {loaded_browser_config.user_agent}")
            ```
    *   **Code Example: Saving a `BrowserConfig` to JSON and then loading it back.**
        ```python
        from crawl4ai import BrowserConfig
        import json
        import os

        # 1. Create and configure
        original_browser_config = BrowserConfig(
            user_agent="MyPersistentAgent/2.0", 
            headless=True,
            extra_args=["--incognito"],
            proxy_config={"server": "http://testproxy.com:1234"}
        )
        print(f"Original Config: {original_browser_config.user_agent}, Headless: {original_browser_config.headless}")

        # 2. Dump to dictionary
        config_as_dict = original_browser_config.dump()
        print(f"\nDumped Dictionary:\n{json.dumps(config_as_dict, indent=2)}")

        # 3. Save to JSON file
        file_path = "my_saved_browser_config.json"
        with open(file_path, "w") as f:
            json.dump(config_as_dict, f, indent=2)
        print(f"\nSaved config to {file_path}")

        # 4. Load from JSON file
        with open(file_path, "r") as f:
            loaded_dict = json.load(f)
        
        # 5. Reconstruct object using load()
        loaded_config = BrowserConfig.load(loaded_dict)
        print(f"\nLoaded Config from file: {loaded_config.user_agent}, Headless: {loaded_config.headless}")
        print(f"Loaded Proxy Server: {loaded_config.proxy_config.get('server') if loaded_config.proxy_config else 'None'}")

        # Clean up
        os.remove(file_path)
        ```

*   6.4. **Best Practices for Configuration Management**
    *   6.4.1. **Define base configurations:** For settings that are common across many crawls (e.g., a standard `BrowserConfig` for your organization, or a default `CrawlerRunConfig` for a type of website), define them once.
    *   6.4.2. **Use `clone()` for variations:** When you need slight modifications for specific tasks, use `base_config.clone(param_to_override=new_value)`. This keeps your code DRY and makes it clear what's changing.
    *   6.4.3. **Store complex/reused configurations externally:** For configurations that are elaborate or used across multiple scripts/projects, save them as JSON or YAML files and load them using `ConfigClass.load()`. This decouples configuration from code.
    *   6.4.4. **Consider versioning your configuration files:** If your external configuration files evolve, use a version control system (like Git) to track changes, just as you would with your code. This helps in managing different setups or rolling back if needed.

## 7. Advanced Scenarios: Combining Configuration Objects for Powerful Workflows

*   7.1. **Introduction: The Synergy of Configuration Objects**
    The true power of Crawl4ai's configuration system shines when you combine different configuration objects (`BrowserConfig`, `CrawlerRunConfig`, `LLMConfig`, `GeolocationConfig`, etc.) to tackle complex, real-world crawling challenges. Each object controls a specific aspect of the crawl, and their interplay allows for highly tailored and sophisticated behavior. This section explores several scenarios to illustrate this synergy.

*   7.2. **Scenario 1: Geo-Targeted Content Extraction with Specific Browser Identity and Proxies**
    *   **Objective:** Crawl a news website that serves different content based on the user's country, appearing as a mobile user from Germany, and routing traffic through a German proxy server.
    *   **`BrowserConfig` Elements:**
        *   `user_agent`: A User-Agent string for a common mobile browser in Germany (e.g., Chrome on Android).
            *   *Why:* To make the server believe the request is from a mobile device.
        *   `proxy_config`: Details of a proxy server located in Germany.
            *   *Why:* The IP address is a primary way websites determine location.
        *   `channel` (if Chromium-based): Could be set to "chrome" to ensure Chrome-specific behavior if the UA is Chrome.
    *   **`CrawlerRunConfig` Elements:**
        *   `geolocation`: An instance of `GeolocationConfig` with latitude/longitude for a city in Germany (e.g., Berlin).
            *   *Why:* To provide GPS coordinates that match the desired location, for sites using browser geolocation APIs.
        *   `locale`: Set to "de-DE".
            *   *Why:* To set the `Accept-Language` header and JavaScript `navigator.language` to German, further reinforcing the German user profile.
        *   `timezone_id`: Set to "Europe/Berlin".
            *   *Why:* To make the browser's reported timezone consistent with Germany.
        *   `extraction_strategy`: An appropriate strategy to extract news headlines and summaries.
    *   **Workflow Explanation:**
        1.  The `BrowserConfig` launches a browser that routes its traffic through the German proxy, making all network requests appear to originate from Germany. Its User-Agent string identifies it as a German mobile user.
        2.  The `CrawlerRunConfig` then instructs this browser context to report German GPS coordinates, set its language to German, and use a German timezone.
        3.  When `arun()` navigates to the news URL, the website should (if it performs geo-targeting) serve the German version of its content.
        4.  The specified `extraction_strategy` then processes this German-specific content.
    *   **Code Example: Setting up this combined configuration.**
        ```python
        from crawl4ai import (
            AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, 
            GeolocationConfig, CacheMode
        )
        # Assume an appropriate extraction strategy, e.g., for news articles
        # from crawl4ai.extraction_strategy import SomeArticleExtractionStrategy 

        async def crawl_german_news():
            german_proxy = {
                "server": "http://your-german-proxy.com:port", # Replace with actual proxy
                # "username": "proxy_user", # If authenticated
                # "password": "proxy_pass"  # If authenticated
            }

            browser_cfg_german = BrowserConfig(
                user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36", # Example Android Chrome
                proxy_config=german_proxy,
                headless=True 
            )

            geo_config_berlin = GeolocationConfig(latitude=52.5200, longitude=13.4050, accuracy=100.0)
            
            # article_strategy = SomeArticleExtractionStrategy() # Replace with actual strategy

            run_cfg_german_news = CrawlerRunConfig(
                geolocation=geo_config_berlin,
                locale="de-DE",
                timezone_id="Europe/Berlin",
                # extraction_strategy=article_strategy,
                cache_mode=CacheMode.BYPASS # Ensure fresh content for geo-testing
            )

            async with AsyncWebCrawler(config=browser_cfg_german) as crawler:
                # Use a site that shows location or IP for testing, e.g., ipinfo.io
                result = await crawler.arun(url="https://ipinfo.io/json", config=run_cfg_german_news)
                
                if result.success:
                    print("--- Geo-Targeted Crawl Result (ipinfo.io) ---")
                    print(result.html) # Should show German IP and location details
                    # For a real news site, you'd inspect result.markdown or result.extracted_content
                else:
                    print(f"Crawl failed: {result.error_message}")

        # await crawl_german_news() # Uncomment to run with a real proxy
        ```

*   7.3. **Scenario 2: High-Volume Data Extraction from API-like Endpoints (No JS) with Rate Limiting**
    *   **Objective:** Efficiently scrape data from a list of 1000 product API endpoints (e.g., `api.example.com/product/{id}`) that return JSON and are known to be static (no JavaScript rendering needed). Ensure polite crawling to avoid overwhelming the server.
    *   **Strategy Choice:** `AsyncHTTPCrawlerStrategy` is ideal here for speed and low overhead.
    *   **`HTTPCrawlerConfig` Elements (if needed per request, often passed directly to `arun` with HTTP strategy):**
        *   `headers`: If the API requires specific headers like an `Authorization` token or `Accept: application/json`.
        *   `method`: Likely "GET" for fetching product data.
    *   **`CrawlerRunConfig` Elements:**
        *   `extraction_strategy`: `NoExtractionStrategy` if the API returns clean JSON directly in `result.html`. If it returns HTML containing JSON (e.g., in a `<script>` tag), you might need a custom extractor or a simple regex in post-processing.
        *   `cache_mode`: `CacheMode.ENABLED` might be good if product data doesn't change extremely frequently, or `CacheMode.BYPASS` if always fresh data is paramount.
    *   **Dispatcher & Rate Limiting:**
        *   Use `crawler.arun_many()` with its default `MemoryAdaptiveDispatcher`.
        *   Configure the `CrawlerRunConfig` (passed to `arun_many`) with `mean_delay` and `max_range` to introduce delays between requests to the *same domain*.
        *   The `MemoryAdaptiveDispatcher` itself can also be configured with a `RateLimiter` instance for more global control if needed, but per-domain delays via `CrawlerRunConfig` are often sufficient for politeness.
    *   **Workflow Explanation:**
        1.  Instantiate `AsyncWebCrawler` with `AsyncHTTPCrawlerStrategy`.
        2.  Prepare a list of product API URLs.
        3.  Create a `CrawlerRunConfig` that includes `mean_delay` and `max_range` for polite crawling.
        4.  Call `crawler.arun_many(urls=product_urls, config=run_config_with_delay)`.
        5.  The dispatcher will manage concurrency (based on memory by default) and inter-request delays.
        6.  Each result's `html` attribute will contain the raw JSON response from the API.
    *   **Code Example: Fetching data from a list of URLs using `AsyncHTTPCrawlerStrategy`.**
        ```python
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
        from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
        from crawl4ai.async_dispatchers import MemoryAdaptiveDispatcher, RateLimiter # For more advanced control
        import json
        import asyncio

        # Sample product IDs
        product_ids = list(range(1, 21)) # Let's do 20 for a quick demo
        api_urls = [f"https://jsonplaceholder.typicode.com/todos/{pid}" for pid in product_ids]

        async def fetch_product_apis():
            http_strategy = AsyncHTTPCrawlerStrategy()
            
            # Configure run config for politeness
            # This will apply per-domain delays managed by the dispatcher
            run_config_polite = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                mean_delay=0.5,  # Average 0.5s delay between requests to jsonplaceholder.typicode.com
                max_range=0.3,   # Add random 0-0.3s to that
                # No specific extraction_strategy needed as API returns JSON directly in result.html
            )
            
            # Optional: Configure the dispatcher itself if more control than CrawlerRunConfig's delay offers
            # custom_dispatcher = MemoryAdaptiveDispatcher(
            #     rate_limiter=RateLimiter(base_delay=(0.5, 1.0)) # Global rate limiting
            # )

            async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
                print(f"Fetching {len(api_urls)} URLs...")
                results_stream = await crawler.arun_many(
                    urls=api_urls, 
                    config=run_config_polite,
                    # dispatcher=custom_dispatcher # If using custom dispatcher
                )
                
                all_product_data = []
                async for result_container in results_stream: # Assuming stream=True in run_config_polite
                    result = result_container.result # Access the CrawlResult
                    if result.success:
                        try:
                            product_data = json.loads(result.html)
                            all_product_data.append(product_data)
                            print(f"Fetched: {product_data.get('title', 'N/A')[:30]}...")
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON for {result.url}: {result.html[:100]}")
                    else:
                        print(f"Failed {result.url}: {result.error_message}")
                
                print(f"\nSuccessfully fetched {len(all_product_data)} product details.")
                # print("Sample of first product:", all_product_data[0] if all_product_data else "None")

        # await fetch_product_apis()
        ```
        *Note: For `arun_many`, `CrawlerRunConfig`'s `mean_delay` and `max_range` are hints for the dispatcher's internal per-domain rate limiting. The `RateLimiter` object passed to the dispatcher provides more explicit global control.*

*   7.4. **Scenario 3: Multi-Step Authenticated Crawl with LLM-based Data Summarization**
    *   **Objective:**
        1.  Log into a website.
        2.  Navigate to a user-specific dashboard page.
        3.  Extract structured data (e.g., a list of recent orders) from the dashboard.
        4.  Use an LLM to generate a brief summary of these orders.
    *   **`BrowserConfig` Elements:**
        *   `use_persistent_context=True`, `user_data_dir="my_site_profile"`: To save and reuse login cookies/session.
        *   `headless=False` (recommended for initial login script development).
    *   **`CrawlerRunConfig` (Step 1: Login):**
        *   `url`: Login page URL.
        *   `session_id`: A unique ID, e.g., "my_dashboard_session".
        *   `js_code`: JavaScript to fill username, password, and click submit.
        *   `wait_for`: CSS selector or JS condition confirming successful login (e.g., visibility of a dashboard element or URL change).
        *   `cache_mode=CacheMode.BYPASS` (to ensure login is attempted).
    *   **`CrawlerRunConfig` (Step 2: Navigate & Extract Data - using same `session_id`):**
        *   `url`: Dashboard page URL.
        *   `session_id`: Must be "my_dashboard_session".
        *   `extraction_strategy`: An instance of `JsonCssExtractionStrategy` (or `LLMExtractionStrategy`) configured to extract order details.
        *   `cache_mode=CacheMode.BYPASS` (to get fresh dashboard data).
    *   **`LLMConfig` (for summarization, if using an LLM strategy for it):**
        *   `provider`, `api_token`.
        *   `temperature`, `max_tokens` suitable for summarization.
    *   **Post-processing or an `LLMSummarizationStrategy`:**
        *   If summarization is a separate step: After getting `extracted_content` (list of orders), manually call an LLM with this data.
        *   If using a hypothetical `LLMSummarizationStrategy`: This strategy would take the extracted order data (perhaps from a previous `extraction_strategy` or directly from the page content if simple enough) and use the LLM to summarize it. This would be part of the `CrawlerRunConfig` for Step 2.
    *   **Workflow Explanation:**
        1.  The first `arun()` call uses `js_code` to log in. The session (cookies) is stored due to `use_persistent_context`.
        2.  The second `arun()` call reuses the `session_id`. Playwright/Crawl4ai uses the stored cookies, allowing access to the dashboard. The `extraction_strategy` then pulls the order data.
        3.  The extracted order data (JSON string from `result.extracted_content`) is parsed.
        4.  This data is then passed to an LLM for summarization (either via another `LLMExtractionStrategy` configured for summarization or a direct API call).
    *   **Code Example: Focusing on the `CrawlerRunConfig` aspects.**
        ```python
        from crawl4ai import (
            AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, LLMConfig,
            LLMExtractionStrategy, CacheMode
        )
        from pydantic import BaseModel, Field
        import json
        import os

        # --- Schemas ---
        class OrderItem(BaseModel):
            item_name: str
            quantity: int
            price: float

        class DashboardData(BaseModel):
            user_name: str
            recent_orders: list[OrderItem]

        # --- Mock HTML ---
        LOGIN_PAGE_HTML = "<html><body><form><input name='user'><input name='pass' type='password'><button type='submit'>Login</button></form></body></html>"
        DASHBOARD_HTML_TEMPLATE = """
        <html><body><div id='dashboard'>
            Welcome, {user_name}!
            <h2>Recent Orders</h2>
            <ul id='order-list'>
                <li><span>Order 1: Widget A (2) @ $10.00</span></li>
                <li><span>Order 2: Gadget B (1) @ $25.50</span></li>
            </ul>
        </div></body></html>
        """

        async def run_authenticated_llm_summary():
            session_id = "auth_crawl_session"
            user_data_dir = "./auth_browser_profile" # For session persistence
            
            # For real use, ensure OPENAI_API_KEY is set
            if not os.getenv("OPENAI_API_KEY"):
                print("OPENAI_API_KEY not set. Skipping authenticated LLM summary example.")
                return

            # Browser config with persistence
            browser_cfg = BrowserConfig(
                use_persistent_context=True, 
                user_data_dir=user_data_dir,
                headless=True # Set to False to observe login if needed
            )

            # LLM Config for extraction & summarization
            llm_conf = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY"), temperature=0.2)

            # Strategy to extract orders from dashboard
            order_extraction_strategy = LLMExtractionStrategy(
                llm_config=llm_conf,
                schema=DashboardData.model_json_schema(),
                instruction="Extract the username and all recent orders from the dashboard HTML. For each order, get item name, quantity, and price.",
                input_format="html" # Feed raw HTML for LLM to parse structure
            )

            async with AsyncWebCrawler(config=browser_cfg) as crawler:
                # Step 1: Simulate Login (replace with actual login logic for a real site)
                # For this example, we'll just navigate to a mock "login successful" page
                # In a real scenario, js_code would fill and submit the login form.
                print("Simulating login...")
                login_config = CrawlerRunConfig(
                    url=f"raw://{LOGIN_PAGE_HTML.replace('{user_name}', 'TestUser')}", # Mock successful login state
                    session_id=session_id,
                    wait_for="css:body" # Just wait for body to exist on this mock page
                )
                login_result = await crawler.arun(config=login_config)
                if not login_result.success:
                    print(f"Login step failed: {login_result.error_message}")
                    return
                print("Login step simulated/completed.")

                # Step 2: Navigate to dashboard and extract orders
                print("Navigating to dashboard and extracting orders...")
                dashboard_html = DASHBOARD_HTML_TEMPLATE.replace("{user_name}", "TestUser") # Mock dashboard
                dashboard_config = CrawlerRunConfig(
                    url=f"raw://{dashboard_html}", # Use mock dashboard HTML
                    session_id=session_id,
                    extraction_strategy=order_extraction_strategy,
                    cache_mode=CacheMode.BYPASS
                )
                dashboard_result = await crawler.arun(config=dashboard_config)

                if not dashboard_result.success or not dashboard_result.extracted_content:
                    print(f"Dashboard data extraction failed: {dashboard_result.error_message}")
                    await crawler.kill_session(session_id)
                    return
                
                print("Orders extracted successfully.")
                extracted_data = json.loads(dashboard_result.extracted_content)
                
                # LLMExtractionStrategy might return a list, take the first element.
                dashboard_info = DashboardData(**(extracted_data[0] if isinstance(extracted_data, list) else extracted_data))
                print(f"Welcome, {dashboard_info.user_name}!")
                for order in dashboard_info.recent_orders:
                    print(f" - {order.item_name} (x{order.quantity}) at ${order.price}")

                # Step 3: Summarize orders using another LLM call (can be part of a more complex strategy or separate)
                if dashboard_info.recent_orders:
                    print("Summarizing orders...")
                    orders_text = "\n".join([f"- {o.item_name} (x{o.quantity}) for ${o.price}" for o in dashboard_info.recent_orders])
                    
                    summarization_prompt = f"Summarize these orders for {dashboard_info.user_name}:\n{orders_text}\n\nSummary:"
                    
                    # Using a generic completion method for simplicity, could also be another LLMExtractionStrategy
                    from crawl4ai.utils import perform_completion_with_backoff # Assuming direct LiteLLM call
                    summary_response = await perform_completion_with_backoff(
                        provider=llm_conf.provider,
                        prompt=summarization_prompt, # Note: LiteLLM uses 'messages' array usually
                        messages=[{"role": "user", "content": summarization_prompt}],
                        api_key=llm_conf.api_token,
                        base_url=llm_conf.base_url,
                        max_tokens=100
                    )
                    summary_text = summary_response.choices[0].message.content
                    print(f"\nOrder Summary:\n{summary_text}")

                # Clean up session
                await crawler.kill_session(session_id)
                # And remove profile dir if it was for temp use
                # import shutil; shutil.rmtree(user_data_dir, ignore_errors=True)
        
        # await run_authenticated_llm_summary() # Uncomment to run
        ```

*   7.5. **Scenario 4: Dynamic Content Scraping with Robust Error Handling and Fallbacks**
    *   **Objective:** Scrape product details from an e-commerce site where some product attributes (e.g., "discounted price," "stock level") might load dynamically or not be present for all items. The goal is to get as much data as possible and handle missing pieces gracefully.
    *   **`BrowserConfig` Elements:**
        *   Standard setup, potentially with `headless=False` during development for observation.
    *   **`CrawlerRunConfig` Elements (and Python control flow):**
        *   **Initial Load & Wait:**
            *   `url`: The product page URL.
            *   `wait_for`: A selector for a core element that *must* be present (e.g., product title or main image).
        *   **Attempting to Trigger Dynamic Content (if applicable):**
            *   `js_code`: May include clicks on tabs (e.g., "Specifications," "Reviews") or scrolls if certain data is lazy-loaded upon such interactions.
            *   Further `wait_for` calls after each interaction to allow content to load.
        *   **Extraction Strategy (e.g., `JsonCssExtractionStrategy` or `LLMExtractionStrategy`):**
            *   The schema should define fields as `Optional` where data might be missing (e.g., `discounted_price: Optional[float] = None`).
            *   For CSS-based extraction, selectors for optional fields should be robust enough not to break if the element isn't found (the strategy should handle this by returning `None` for that field).
        *   **Python-Level Fallbacks/Retries (Conceptual):**
            While `CrawlerRunConfig` itself doesn't have direct retry logic for parts of an extraction, you can structure your Python code around `arun()`:
            ```python
            # Conceptual Python-level retry for an optional element
            # result = await crawler.arun(config=initial_config)
            # extracted_data = json.loads(result.extracted_content)[0]
            # if not extracted_data.get("stock_level"):
            #     print("Stock level not found, trying to click 'Check Stock' button...")
            #     retry_config = initial_config.clone(
            #         js_code="document.querySelector('#check-stock-btn')?.click();",
            #         wait_for="css:.stock-info-loaded", # Wait for stock info to appear
            #         js_only=True, # Operate on the same page
            #         session_id="product_page_session" # Ensure same page
            #     )
            #     stock_result = await crawler.arun(config=retry_config)
            #     # Re-extract or merge results
            ```
    *   **Workflow Explanation:**
        1.  Load the main page and wait for essential static elements.
        2.  If certain data is known to be dynamic (e.g., loaded on a tab click), use `js_code` to trigger that interaction, followed by another `wait_for`.
        3.  Use an extraction strategy with an optional schema.
        4.  If key optional data is missing, and there's a known interaction to reveal it (like clicking a button), you can make a subsequent `arun()` call (with `js_only=True` and the same `session_id`) to perform that action and then attempt to re-extract or extract just that missing piece.
    *   **Code Example (Conceptual - focusing on the idea of layered attempts):**
        ```python
        from crawl4ai import (
            AsyncWebCrawler, BrowserConfig, CrawlerRunConfig,
            JsonCssExtractionStrategy, CacheMode # Example using CSS strategy
        )
        import json

        # Define a schema where some fields are optional
        PRODUCT_SCHEMA = {
            "name": "Product Info",
            "baseSelector": "div.product-main", # Assuming a main product container
            "fields": [
                {"name": "title", "selector": "h1.product-title", "type": "text"},
                {"name": "price", "selector": ".price-current", "type": "text"},
                # Optional field: discount might not always be there
                {"name": "discounted_price", "selector": ".price-discounted", "type": "text", "default": None},
                # Optional field: stock might load after a click
                {"name": "stock_status", "selector": ".stock-status-display", "type": "text", "default": "Unknown"}
            ]
        }
        
        # Mock HTMLs
        INITIAL_HTML = """
        <div class='product-main'>
            <h1 class='product-title'>Super Widget</h1>
            <span class='price-current'>$100</span>
            <!-- Discounted price and stock are not initially visible -->
            <button id='show-details-btn'>Show More Details</button>
            <div id='extra-details' style='display:none;'>
                 <span class='price-discounted'>$80</span>
                 <span class='stock-status-display'>In Stock</span>
            </div>
        </div>
        """
        HTML_AFTER_CLICK = INITIAL_HTML.replace("style='display:none;'", "style='display:block;'")


        async def crawl_dynamic_product():
            session_id = "dynamic_product_session"
            extraction_strategy = JsonCssExtractionStrategy(PRODUCT_SCHEMA)

            async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
                # --- Attempt 1: Initial Load ---
                print("--- Attempt 1: Initial Load ---")
                config_attempt1 = CrawlerRunConfig(
                    url=f"raw://{INITIAL_HTML}",
                    session_id=session_id,
                    extraction_strategy=extraction_strategy,
                    cache_mode=CacheMode.BYPASS
                )
                result1 = await crawler.arun(config=config_attempt1)
                data1 = {}
                if result1.success and result1.extracted_content:
                    data1_list = json.loads(result1.extracted_content)
                    if data1_list: data1 = data1_list[0]
                print(f"Initial Data: {data1}")

                # --- Attempt 2: Click button and re-evaluate (or re-extract if strategy supports it) ---
                # If some data is missing (e.g., stock_status is 'Unknown' or discounted_price is None)
                # and we know an action can reveal it.
                if data1.get("stock_status") == "Unknown" or not data1.get("discounted_price"):
                    print("\n--- Attempt 2: Clicking 'Show More Details' ---")
                    
                    # For this raw HTML example, we'll just "navigate" to the state after click
                    # In a real scenario, js_code would click the button.
                    config_attempt2 = CrawlerRunConfig(
                        url=f"raw://{HTML_AFTER_CLICK}", # Simulating state after click
                        session_id=session_id, # Maintain session
                        # js_code="document.getElementById('show-details-btn')?.click();", # Real interaction
                        # wait_for="css:#extra-details[style*='display:block']", # Wait for it to be visible
                        js_only=False, # Set to True if js_code is used on existing page
                        extraction_strategy=extraction_strategy, # Re-extract
                        cache_mode=CacheMode.BYPASS
                    )
                    result2 = await crawler.arun(config=config_attempt2)
                    data2 = {}
                    if result2.success and result2.extracted_content:
                        data2_list = json.loads(result2.extracted_content)
                        if data2_list: data2 = data2_list[0]
                    print(f"Data after interaction: {data2}")
                    # In a real app, you'd merge data1 and data2 intelligently
                
                await crawler.kill_session(session_id)

        # await crawl_dynamic_product()
        ```
        This conceptual example shows how you might chain `arun` calls with different `CrawlerRunConfig`s (sharing a `session_id`) to handle dynamic content revealing steps. More robust solutions might involve custom retry logic in Python or more sophisticated `wait_for` JS expressions.


## 8. Conclusion and Further Exploration

*   8.1. **Recap of the power and flexibility offered by Crawl4ai's configuration objects.**
    Throughout this guide, we've explored how `BrowserConfig`, `CrawlerRunConfig`, `LLMConfig`, and other specialized configuration objects in Crawl4ai provide a powerful and flexible framework for tailoring your web crawling and scraping tasks. From defining browser identity and environment to controlling per-page interactions, content extraction, media handling, and LLM integration, these objects give you granular control over every aspect of the crawl. The separation of concerns and methods like `clone()`, `dump()`, and `load()` further enhance reusability and manageability of your configurations.

*   8.2. **Encouragement to experiment with different combinations.**
    The true strength of Crawl4ai's configuration system lies in the ability to combine these objects and their parameters in creative ways to solve unique challenges. Don't hesitate to experiment:
    *   Try different `user_agent` strings with varying `headless` modes.
    *   Combine `css_selector` with `target_elements` for precise content focus.
    *   Use `js_code` and `wait_for` to navigate complex SPAs.
    *   Integrate `LLMExtractionStrategy` with fine-tuned `LLMConfig` settings for difficult extractions.
    *   Leverage `session_id` for multi-step workflows.
    The more you experiment, the better you'll understand how to harness the full potential of Crawl4ai for your specific needs.

*   8.3. **Pointers to other relevant documentation sections.**
    This guide has focused on the "how" and "why" of using configuration objects. For more details on specific areas, please refer to:
    *   **API Reference / "Foundational Memory" Document for `config_objects`:** For an exhaustive list of all parameters, their types, and default values.
    *   **Documentation on Specific Strategies:** Deep dives into `LLMExtractionStrategy`, `JsonCssExtractionStrategy`, `AsyncHTTPCrawlerStrategy`, various `MarkdownGenerationStrategy` and `ContentFilterStrategy` options.
    *   **Advanced Browser Management:** Detailed guides on `use_persistent_context`, `user_data_dir`, Docker integration, and managing browser profiles.
    *   **`arun_many()` and Dispatchers:** For understanding how to efficiently crawl multiple URLs in parallel and customize dispatch behavior with `MemoryAdaptiveDispatcher`, `SemaphoreDispatcher`, and `RateLimiter`.
    *   **Hooks and Custom Callbacks:** For advanced customization of the crawling lifecycle.

By mastering these configuration objects, you can build robust, efficient, and highly customized web crawlers with Crawl4ai. Happy crawling!
```

---


## Configuration Objects - Examples
Source: crawl4ai_config_objects_examples_content.llm.md

```markdown
# Examples Document for crawl4ai - config_objects Component

**Target Document Type:** Examples Collection
**Target Output Filename Suggestion:** `llm_examples_config_objects.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2025-05-24
---

This document provides a collection of runnable code examples demonstrating how to use the various configuration objects within the `crawl4ai` library. These examples are designed to showcase diverse usage patterns and help users quickly understand how to configure the crawler for their specific needs.

## 1. Introduction to Configuration Objects

### 1.1. Overview: Purpose and interaction of `BrowserConfig`, `CrawlerRunConfig`, `LLMConfig`, `ProxyConfig`, and `GeolocationConfig`.

The `crawl4ai` library utilizes several key configuration objects to manage different aspects of the crawling and data extraction process:

*   **`BrowserConfig`**: Controls the browser's launch and behavior, such as its type (Chromium, Firefox, WebKit), headless mode, proxy settings, user agent, viewport size, and persistent contexts. This configuration is typically passed when initializing the `AsyncWebCrawler`.
*   **`CrawlerRunConfig`**: Dictates the behavior for each specific `arun()` call. This includes URL-specific settings like caching modes, JavaScript execution, waiting conditions, screenshot/PDF generation, content processing strategies (extraction, chunking, markdown), and run-specific overrides for browser settings like locale or geolocation.
*   **`LLMConfig`**: Configures the Large Language Model (LLM) provider and its parameters when using LLM-based extraction strategies (e.g., `LLMExtractionStrategy`). It includes provider name, API token, base URL, and generation parameters like temperature and max tokens.
*   **`ProxyConfig`**: A dedicated object for defining proxy server details, including server URL, authentication credentials (username/password), and IP. It can be used within `BrowserConfig` (for browser-wide proxy) or `CrawlerRunConfig` (for run-specific proxy, especially with HTTP-based strategies or proxy rotation).
*   **`GeolocationConfig`**: Specifies geolocation data (latitude, longitude, accuracy) to simulate a specific geographic location for the browser context, often used within `CrawlerRunConfig`.

These objects interact to provide fine-grained control. For instance, `BrowserConfig` sets up the general browser environment, while `CrawlerRunConfig` can override or augment these settings for individual crawl tasks. `LLMConfig`, `ProxyConfig`, and `GeolocationConfig` are often nested within `BrowserConfig` or `CrawlerRunConfig` to provide specialized configurations.

---
### 1.2. Example: Basic workflow - Creating default instances of each config object and passing them to `AsyncWebCrawler` or relevant strategies.

This example shows the most basic initialization of config objects and how they might be passed to the crawler.

```python
import asyncio
import os
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    LLMConfig,
    ProxyConfig,
    GeolocationConfig,
    CacheMode
)

async def basic_config_workflow():
    # 1. BrowserConfig: Default settings (headless chromium)
    browser_config = BrowserConfig()
    print(f"Default BrowserConfig: {browser_config.to_dict()}")

    # 2. GeolocationConfig (Optional, for specific location simulation)
    geolocation_config = GeolocationConfig(latitude=37.7749, longitude=-122.4194) # San Francisco
    print(f"\nGeolocationConfig: {geolocation_config.to_dict()}")

    # 3. ProxyConfig (Optional, if a proxy is needed)
    # For this example, we'll assume no proxy is needed for the default BrowserConfig.
    # If one were, it could be:
    # proxy_config = ProxyConfig(server="http://myproxy.com:8080")
    # browser_config_with_proxy = BrowserConfig(proxy_config=proxy_config)

    # 4. LLMConfig (Optional, only if using LLM-based extraction)
    # Requires an API key, e.g., from environment
    llm_config = LLMConfig(
        provider="openai/gpt-4o-mini",
        api_token=os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE") # Replace or set env var
    )
    print(f"\nLLMConfig (provider only shown if token is placeholder): {llm_config.provider}")

    # 5. CrawlerRunConfig: Default settings, but can integrate other configs
    # For a specific run, you might pass geolocation or an LLM strategy
    crawler_run_config_basic = CrawlerRunConfig(
        url="https://example.com",
        cache_mode=CacheMode.BYPASS # For this demo, bypass cache
    )
    print(f"\nBasic CrawlerRunConfig: {crawler_run_config_basic.to_dict(exclude_none=True)}")

    crawler_run_config_with_geo = CrawlerRunConfig(
        url="https://example.com/geo-specific-content",
        geolocation=geolocation_config,
        cache_mode=CacheMode.BYPASS
    )
    print(f"\nCrawlerRunConfig with Geolocation: {crawler_run_config_with_geo.to_dict(exclude_none=True)}")

    # To use LLMConfig, you'd typically pass it to an LLMExtractionStrategy,
    # which then goes into CrawlerRunConfig.extraction_strategy.
    # from crawl4ai.extraction_strategy import LLMExtractionStrategy
    # llm_extraction_strategy = LLMExtractionStrategy(llm_config=llm_config, schema={"title": "Page title"})
    # crawler_run_config_with_llm = CrawlerRunConfig(
    #     url="https://example.com/article",
    #     extraction_strategy=llm_extraction_strategy,
    #     cache_mode=CacheMode.BYPASS
    # )
    # print(f"\nCrawlerRunConfig with LLM Strategy (conceptual): {crawler_run_config_with_llm.to_dict(exclude_none=True)}")


    # Using AsyncWebCrawler with the basic browser config
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("\n--- Running basic crawl ---")
        result = await crawler.arun(config=crawler_run_config_basic)
        if result.success:
            print(f"Successfully crawled {result.url}. Markdown length: {len(result.markdown.raw_markdown)}")
        else:
            print(f"Failed to crawl {result.url}: {result.error_message}")

        # Example with geolocation (on a site that might use it)
        # For a real test, use a site like https://mylocation.org/
        print("\n--- Running crawl with geolocation (conceptual) ---")
        result_geo = await crawler.arun(config=crawler_run_config_with_geo)
        if result_geo.success:
            print(f"Successfully crawled {result_geo.url} (geo). Markdown length: {len(result_geo.markdown.raw_markdown)}")
        else:
            print(f"Failed to crawl {result_geo.url} (geo): {result_geo.error_message}")


if __name__ == "__main__":
    asyncio.run(basic_config_workflow())
```

---
## 2. `GeolocationConfig` Examples

### 2.1. Example: Basic initialization of `GeolocationConfig` for a specific location (e.g., San Francisco).

This example shows how to initialize `GeolocationConfig` with latitude and longitude, defaulting accuracy to 0.0.

```python
import asyncio
from crawl4ai import GeolocationConfig, CrawlerRunConfig, AsyncWebCrawler

async def basic_geolocation_config():
    # San Francisco coordinates
    sf_geo_config = GeolocationConfig(latitude=37.7749, longitude=-122.4194)
    print(f"San Francisco GeolocationConfig: {sf_geo_config.to_dict()}")

    # To see its effect, you need a site that uses geolocation.
    # We'll use a placeholder for demonstration.
    # A good test site could be https://mylocation.org/ or https://www.gps-coordinates.net/
    run_config = CrawlerRunConfig(
        url="https://www.whatismybrowser.com/detect/what-is-my-user-agent", # Shows some geo info
        geolocation=sf_geo_config,
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"\nCrawled {result.url} with geolocation. HTML snippet (first 500 chars):")
            # You would typically parse the HTML to find location-specific content
            # For this example, we just print part of the HTML.
            # print(result.html[:500]) # The actual page might not show the spoofed geo directly
            print("Geolocation spoofing applied. Check a geo-sensitive site for full effect.")
        else:
            print(f"Failed to crawl: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(basic_geolocation_config())
```

---
### 2.2. Example: Initializing `GeolocationConfig` with latitude, longitude, and custom accuracy.

This example demonstrates setting a specific accuracy for the geolocation.

```python
import asyncio
from crawl4ai import GeolocationConfig

async def geolocation_with_accuracy():
    # Paris coordinates with 100 meters accuracy
    paris_geo_config = GeolocationConfig(
        latitude=48.8566,
        longitude=2.3522,
        accuracy=100.0  # Accuracy in meters
    )
    print(f"Paris GeolocationConfig with accuracy: {paris_geo_config.to_dict()}")
    # You would then use this in CrawlerRunConfig like the previous example.

if __name__ == "__main__":
    asyncio.run(geolocation_with_accuracy())
```

---
### 2.3. Example: Creating `GeolocationConfig` from a dictionary using `GeolocationConfig.from_dict()`.

This shows how to instantiate `GeolocationConfig` from a dictionary, useful for dynamic configurations.

```python
import asyncio
from crawl4ai import GeolocationConfig

async def geolocation_from_dict_example():
    geo_data_dict = {
        "latitude": 51.5074,  # London
        "longitude": 0.1278,
        "accuracy": 50.0
    }
    london_geo_config = GeolocationConfig.from_dict(geo_data_dict)
    print(f"London GeolocationConfig from_dict: {london_geo_config.to_dict()}")
    assert london_geo_config.latitude == 51.5074
    assert london_geo_config.accuracy == 50.0

if __name__ == "__main__":
    asyncio.run(geolocation_from_dict_example())
```

---
### 2.4. Example: Converting `GeolocationConfig` to a dictionary using `to_dict()`.

Demonstrates serializing a `GeolocationConfig` instance back into a dictionary.

```python
import asyncio
from crawl4ai import GeolocationConfig

async def geolocation_to_dict_example():
    tokyo_geo_config = GeolocationConfig(latitude=35.6895, longitude=139.6917, accuracy=75.0)
    config_dict = tokyo_geo_config.to_dict()
    print(f"Tokyo GeolocationConfig as dict: {config_dict}")
    assert config_dict["latitude"] == 35.6895
    assert config_dict["accuracy"] == 75.0

if __name__ == "__main__":
    asyncio.run(geolocation_to_dict_example())
```

---
### 2.5. Example: Cloning `GeolocationConfig` and modifying accuracy using `clone()`.

Shows how to create a copy of a `GeolocationConfig` instance and modify specific attributes.

```python
import asyncio
from crawl4ai import GeolocationConfig

async def geolocation_clone_example():
    original_geo_config = GeolocationConfig(latitude=40.7128, longitude=-74.0060) # New York
    print(f"Original NY GeolocationConfig: {original_geo_config.to_dict()}")

    # Clone and modify accuracy
    cloned_geo_config = original_geo_config.clone(accuracy=25.0)
    print(f"Cloned NY GeolocationConfig with new accuracy: {cloned_geo_config.to_dict()}")

    assert cloned_geo_config.latitude == original_geo_config.latitude
    assert cloned_geo_config.accuracy == 25.0
    assert original_geo_config.accuracy == 0.0 # Original remains unchanged

if __name__ == "__main__":
    asyncio.run(geolocation_clone_example())
```

---
### 2.6. Example: Integrating `GeolocationConfig` into `CrawlerRunConfig` to simulate location for a crawl.

This example explicitly shows passing `GeolocationConfig` to `CrawlerRunConfig` for a simulated crawl.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, GeolocationConfig, CacheMode

async def integrate_geolocation_in_crawler_run():
    # Berlin coordinates
    berlin_geo = GeolocationConfig(latitude=52.5200, longitude=13.4050, accuracy=10.0)

    # Configure the specific run to use this geolocation
    # Use a site that might reflect geolocation, e.g., a weather site or Google search
    run_config_with_geo = CrawlerRunConfig(
        url="https://www.google.com/search?q=weather", # Google search might show location-based results
        geolocation=berlin_geo,
        cache_mode=CacheMode.BYPASS, # Ensure fresh fetch for demo
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        print(f"Crawling with geolocation for Berlin: {berlin_geo.to_dict()}")
        result = await crawler.arun(config=run_config_with_geo)
        if result.success:
            print(f"Successfully crawled {result.url} with simulated Berlin location.")
            # Inspect result.html or result.markdown for signs of location-based content
            # For instance, search for "Berlin" in the content
            if "Berlin" in result.html[:2000]: # Check first 2000 chars of raw HTML
                 print("Berlin might be reflected in the page content.")
            else:
                 print("Berlin not obviously reflected in initial HTML content (site might not use precise geo or requires more interaction).")
        else:
            print(f"Failed to crawl: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(integrate_geolocation_in_crawler_run())
```

---
## 3. `ProxyConfig` Examples

### 3.1. Example: Basic initialization of `ProxyConfig` with a server URL.

Shows how to set up a simple proxy without authentication.

```python
import asyncio
from crawl4ai import ProxyConfig

async def basic_proxy_config():
    proxy_config = ProxyConfig(server="http://myproxy.example.com:8080")
    print(f"Basic ProxyConfig: {proxy_config.to_dict()}")
    assert proxy_config.server == "http://myproxy.example.com:8080"
    assert proxy_config.ip == "myproxy.example.com" # IP is extracted

if __name__ == "__main__":
    asyncio.run(basic_proxy_config())
```

---
### 3.2. Example: Initializing `ProxyConfig` with server, username, and password for an authenticated proxy.

Demonstrates setting up an authenticated proxy.

```python
import asyncio
from crawl4ai import ProxyConfig

async def authenticated_proxy_config():
    auth_proxy_config = ProxyConfig(
        server="http://authproxy.example.com:3128",
        username="proxyuser",
        password="proxypassword123"
    )
    print(f"Authenticated ProxyConfig: {auth_proxy_config.to_dict()}")
    assert auth_proxy_config.username == "proxyuser"

if __name__ == "__main__":
    asyncio.run(authenticated_proxy_config())
```

---
### 3.3. Example: Initializing `ProxyConfig` with an explicit IP address.

This example shows specifying the IP address directly, which can be useful if the server URL is complex or resolution is tricky.

```python
import asyncio
from crawl4ai import ProxyConfig

async def explicit_ip_proxy_config():
    proxy_config_with_ip = ProxyConfig(
        server="http://hostname.that.is.not.ip:9999",
        ip="192.168.1.100" # Explicitly set the IP
    )
    print(f"ProxyConfig with explicit IP: {proxy_config_with_ip.to_dict()}")
    assert proxy_config_with_ip.ip == "192.168.1.100"

if __name__ == "__main__":
    asyncio.run(explicit_ip_proxy_config())
```

---
### 3.4. Example: Demonstrating automatic IP extraction from the server URL in `ProxyConfig`.

`ProxyConfig` attempts to extract the IP/hostname from the server URL if `ip` is not provided.

```python
import asyncio
from crawl4ai import ProxyConfig

async def auto_ip_extraction_proxy_config():
    # IP extraction from http://ip:port
    proxy1 = ProxyConfig(server="http://123.45.67.89:8000")
    print(f"Proxy 1 (IP from http): {proxy1.to_dict()}")
    assert proxy1.ip == "123.45.67.89"

    # IP extraction from https://hostname:port
    proxy2 = ProxyConfig(server="https://secureproxy.example.net:8443")
    print(f"Proxy 2 (Hostname from https): {proxy2.to_dict()}")
    assert proxy2.ip == "secureproxy.example.net"

    # IP extraction from socks5://hostname:port
    proxy3 = ProxyConfig(server="socks5://socksp.example.org:1080")
    print(f"Proxy 3 (Hostname from socks5): {proxy3.to_dict()}")
    assert proxy3.ip == "socksp.example.org"
    
    # IP extraction from just hostname:port (assumes http)
    proxy4 = ProxyConfig(server="anotherproxy.com:7070")
    print(f"Proxy 4 (Hostname from hostname:port): {proxy4.to_dict()}")
    assert proxy4.ip == "anotherproxy.com"


if __name__ == "__main__":
    asyncio.run(auto_ip_extraction_proxy_config())
```

---
### 3.5. Example: Creating `ProxyConfig` from a string in 'ip:port' format using `ProxyConfig.from_string()`.

Illustrates creating a `ProxyConfig` object from a simple 'ip:port' string.

```python
import asyncio
from crawl4ai import ProxyConfig

async def proxy_from_simple_string():
    proxy_str = "192.168.1.50:8888"
    proxy_config = ProxyConfig.from_string(proxy_str)
    print(f"ProxyConfig from '{proxy_str}': {proxy_config.to_dict()}")
    assert proxy_config.server == "http://192.168.1.50:8888"
    assert proxy_config.ip == "192.168.1.50"
    assert proxy_config.username is None

if __name__ == "__main__":
    asyncio.run(proxy_from_simple_string())
```

---
### 3.6. Example: Creating `ProxyConfig` from a string in 'ip:port:username:password' format using `ProxyConfig.from_string()`.

Shows creating an authenticated `ProxyConfig` object from a formatted string.

```python
import asyncio
from crawl4ai import ProxyConfig

async def proxy_from_auth_string():
    proxy_auth_str = "proxy.example.net:3128:user123:pass456"
    proxy_config = ProxyConfig.from_string(proxy_auth_str)
    print(f"ProxyConfig from '{proxy_auth_str}': {proxy_config.to_dict()}")
    assert proxy_config.server == "http://proxy.example.net:3128"
    assert proxy_config.ip == "proxy.example.net"
    assert proxy_config.username == "user123"
    assert proxy_config.password == "pass456"

if __name__ == "__main__":
    asyncio.run(proxy_from_auth_string())
```

---
### 3.7. Example: Creating `ProxyConfig` from a dictionary using `ProxyConfig.from_dict()`.

Demonstrates instantiating `ProxyConfig` from a dictionary.

```python
import asyncio
from crawl4ai import ProxyConfig

async def proxy_from_dict_example():
    proxy_data_dict = {
        "server": "socks5://secure.proxy.com:1080",
        "username": "sockuser",
        "password": "sockpassword"
    }
    proxy_config = ProxyConfig.from_dict(proxy_data_dict)
    print(f"ProxyConfig from_dict: {proxy_config.to_dict()}")
    assert proxy_config.server == "socks5://secure.proxy.com:1080"
    assert proxy_config.username == "sockuser"

if __name__ == "__main__":
    asyncio.run(proxy_from_dict_example())
```

---
### 3.8. Example: Loading a single `ProxyConfig` from the `PROXIES` environment variable using `ProxyConfig.from_env()`.

Shows how to load proxy settings from an environment variable.

```python
import asyncio
import os
from crawl4ai import ProxyConfig

async def proxy_from_env_single():
    env_var_name = "MY_CRAWLER_PROXIES" # Custom env var name
    proxy_string_in_env = "10.0.0.1:8000:envuser:envpass"

    # Temporarily set the environment variable for this example
    os.environ[env_var_name] = proxy_string_in_env
    
    try:
        proxy_configs = ProxyConfig.from_env(env_var=env_var_name)
        assert len(proxy_configs) == 1
        proxy_config = proxy_configs[0]
        
        print(f"Loaded ProxyConfig from env var '{env_var_name}': {proxy_config.to_dict()}")
        assert proxy_config.server == "http://10.0.0.1:8000"
        assert proxy_config.username == "envuser"
        assert proxy_config.password == "envpass"
    finally:
        del os.environ[env_var_name] # Clean up

if __name__ == "__main__":
    asyncio.run(proxy_from_env_single())
```

---
### 3.9. Example: Loading multiple `ProxyConfig` instances from a comma-separated `PROXIES` environment variable.

Demonstrates loading a list of proxies if the environment variable contains multiple comma-separated proxy strings.

```python
import asyncio
import os
from crawl4ai import ProxyConfig

async def proxy_from_env_multiple():
    env_var_name = "PROXIES" # Default env var name
    multiple_proxy_strings = "10.0.0.1:8000,10.0.0.2:8001:user2:pass2"

    os.environ[env_var_name] = multiple_proxy_strings
    
    try:
        proxy_configs = ProxyConfig.from_env() # Uses "PROXIES" by default
        print(f"Loaded {len(proxy_configs)} ProxyConfigs from env var '{env_var_name}':")
        for i, pc in enumerate(proxy_configs):
            print(f"  Proxy {i+1}: {pc.to_dict()}")
        
        assert len(proxy_configs) == 2
        assert proxy_configs[0].server == "http://10.0.0.1:8000"
        assert proxy_configs[1].server == "http://10.0.0.2:8001"
        assert proxy_configs[1].username == "user2"
    finally:
        del os.environ[env_var_name]

if __name__ == "__main__":
    asyncio.run(proxy_from_env_multiple())
```

---
### 3.10. Example: Converting `ProxyConfig` to a dictionary using `to_dict()`.

Shows serializing a `ProxyConfig` instance back to a dictionary.

```python
import asyncio
from crawl4ai import ProxyConfig

async def proxy_to_dict_example():
    proxy_config = ProxyConfig(
        server="https_proxy.example.com:443", 
        username="user", 
        password="secure"
    )
    config_dict = proxy_config.to_dict()
    print(f"ProxyConfig as dict: {config_dict}")
    assert config_dict["server"] == "https_proxy.example.com:443" # Note: schema is not added by default by constructor if not present
    assert config_dict["username"] == "user"

if __name__ == "__main__":
    asyncio.run(proxy_to_dict_example())
```

---
### 3.11. Example: Cloning `ProxyConfig` and changing server details using `clone()`.

Demonstrates creating a modified copy of a `ProxyConfig` instance.

```python
import asyncio
from crawl4ai import ProxyConfig

async def proxy_clone_example():
    original_proxy = ProxyConfig(server="http://original.proxy.com:8000", username="orig_user")
    print(f"Original ProxyConfig: {original_proxy.to_dict()}")

    cloned_proxy = original_proxy.clone(server="http://new.proxy.com:8080", username="new_user", password="new_password")
    print(f"Cloned ProxyConfig with new details: {cloned_proxy.to_dict()}")

    assert cloned_proxy.server == "http://new.proxy.com:8080"
    assert cloned_proxy.username == "new_user"
    assert original_proxy.server == "http://original.proxy.com:8000" # Original is unchanged

if __name__ == "__main__":
    asyncio.run(proxy_clone_example())
```

---
### 3.12. Example: Using `ProxyConfig` within `BrowserConfig` to set a browser-level proxy.

This shows how `ProxyConfig` is used to configure the proxy for all browser activity.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, ProxyConfig, CrawlerRunConfig

# This example requires a running proxy server to test against.
# For demonstration, we'll use httpbin.org/ip which returns the requester's IP.
# If run through a proxy, it should show the proxy's IP.

async def browser_level_proxy():
    # Replace with your actual proxy details
    # For this example, let's assume a (non-functional) placeholder
    proxy_details = ProxyConfig(server="http://your-proxy-server.com:8080") 
    # If your proxy requires auth:
    # proxy_details = ProxyConfig(server="http://your-proxy-server.com:8080", username="user", password="pass")


    browser_config = BrowserConfig(
        proxy_config=proxy_details,
        headless=True, # Usually True for automated tasks
        verbose=True
    )
    
    # A URL that shows your IP address
    test_url = "https://httpbin.org/ip"
    run_config = CrawlerRunConfig(url=test_url)

    print(f"Attempting to crawl {test_url} via proxy: {proxy_details.server}")
    print("NOTE: This example will likely fail or show your direct IP if the placeholder proxy is not replaced with a real, working proxy.")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Successfully crawled {result.url}.")
            # The response content should ideally show the proxy's IP
            print(f"Response content (first 200 chars): {result.html[:200]}")
            # If using a real proxy, you'd parse result.html (which is JSON from httpbin.org/ip)
            # and check if 'origin' IP matches your proxy's IP.
        else:
            print(f"Failed to crawl via proxy: {result.error_message}")
            print("This could be due to the proxy server not being reachable, incorrect credentials, or other network issues.")

if __name__ == "__main__":
    # asyncio.run(browser_level_proxy())
    print("Skipping browser_level_proxy example as it requires a live proxy server.")
    print("To run, replace placeholder proxy details and uncomment asyncio.run().")
```

---
### 3.13. Example: Using `ProxyConfig` within `CrawlerRunConfig` for HTTP-specific crawler strategies.

When using `AsyncHTTPCrawlerStrategy` (not browser-based), `ProxyConfig` can be passed via `CrawlerRunConfig`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, ProxyConfig
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy # For non-browser crawling

async def http_crawler_with_proxy():
    # Replace with your actual proxy details
    proxy_details = ProxyConfig(server="http://your-http-proxy.com:8000")

    # This config applies only to this specific run, not the browser (if one were used elsewhere)
    run_config_with_proxy = CrawlerRunConfig(
        url="https://api.ipify.org?format=json", # A simple API to get IP
        proxy_config=proxy_details,
        verbose=True
    )

    # Initialize crawler with an HTTP-based strategy
    http_strategy = AsyncHTTPCrawlerStrategy()
    
    print(f"Attempting HTTP GET for {run_config_with_proxy.url} via proxy: {proxy_details.server}")
    print("NOTE: This example will likely fail or show your direct IP if the placeholder proxy is not replaced.")

    async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
        result = await crawler.arun(config=run_config_with_proxy)
        if result.success:
            print(f"Successfully fetched {result.url}.")
            print(f"Response content: {result.html}")
            # Parse result.html (JSON) to check if 'ip' matches your proxy's IP.
        else:
            print(f"Failed to fetch via proxy: {result.error_message}")

if __name__ == "__main__":
    # asyncio.run(http_crawler_with_proxy())
    print("Skipping http_crawler_with_proxy example as it requires a live proxy server.")
    print("To run, replace placeholder proxy details and uncomment asyncio.run().")

```

---
## 4. `BrowserConfig` Examples

### 4.1. Basic Initialization

#### 4.1.1. Example: Default initialization of `BrowserConfig`.
This uses default settings: Chromium, headless mode, standard viewport.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def default_browser_config_init():
    browser_cfg = BrowserConfig()
    print(f"Default BrowserConfig: {browser_cfg.to_dict(exclude_none=True)}")

    # Demonstrate its use
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://example.com", config=CrawlerRunConfig())
        if result.success:
            print(f"Crawled successfully with default browser config. Page title: {result.metadata.get('title')}")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(default_browser_config_init())
```

---
#### 4.1.2. Example: Specifying `browser_type` as "firefox".
Shows how to launch Firefox instead of the default Chromium.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def firefox_browser_config():
    browser_cfg = BrowserConfig(browser_type="firefox", headless=True) # Ensure headless for automation
    print(f"Firefox BrowserConfig: {browser_cfg.to_dict(exclude_none=True)}")
    assert browser_cfg.browser_type == "firefox"

    # Demonstrate its use
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://example.com", config=CrawlerRunConfig())
        if result.success:
            print(f"Crawled successfully with Firefox. Page title: {result.metadata.get('title')}")
        else:
            print(f"Crawl failed with Firefox: {result.error_message}")
            print("Ensure Firefox is installed and accessible by Playwright.")

if __name__ == "__main__":
    asyncio.run(firefox_browser_config())
```

---
#### 4.1.3. Example: Specifying `browser_type` as "webkit".
Shows how to launch WebKit (Safari's engine).

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def webkit_browser_config():
    browser_cfg = BrowserConfig(browser_type="webkit", headless=True) # Ensure headless
    print(f"WebKit BrowserConfig: {browser_cfg.to_dict(exclude_none=True)}")
    assert browser_cfg.browser_type == "webkit"

    # Demonstrate its use
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://example.com", config=CrawlerRunConfig())
        if result.success:
            print(f"Crawled successfully with WebKit. Page title: {result.metadata.get('title')}")
        else:
            print(f"Crawl failed with WebKit: {result.error_message}")
            print("Ensure WebKit is installed and accessible by Playwright.")

if __name__ == "__main__":
    asyncio.run(webkit_browser_config())
```

---
#### 4.1.4. Example: Running `BrowserConfig` in headed mode (`headless=False`) for visual debugging.
Launches a visible browser window. Useful for observing the crawl.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def headed_browser_config():
    # Note: In some environments (like CI/CD), headed mode might not be possible or may require Xvfb.
    try:
        browser_cfg = BrowserConfig(headless=False) # Visible browser window
        print(f"Headed BrowserConfig: {browser_cfg.to_dict(exclude_none=True)}")
        assert not browser_cfg.headless

        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            print("Attempting to launch a visible browser to crawl example.com...")
            print("The browser window should appear briefly.")
            result = await crawler.arun(url="https://example.com", config=CrawlerRunConfig(page_timeout=10000)) # 10s timeout
            if result.success:
                print(f"Crawled successfully with a visible browser. Page title: {result.metadata.get('title')}")
            else:
                print(f"Crawl failed with visible browser: {result.error_message}")
    except Exception as e:
        print(f"Could not run headed browser example (this is common in restricted environments): {e}")
        print("Skipping headed browser test.")


if __name__ == "__main__":
    # This example might require a display server.
    # asyncio.run(headed_browser_config())
    print("Skipping headed_browser_config example. Uncomment to run if you have a display server.")
```

---
### 4.2. Browser Mode and Management

#### 4.2.1. Example: Using `browser_mode="builtin"` for Playwright's managed CDP.
This mode is for connecting to Playwright's own managed browser instance via CDP, typically for advanced control or specific scenarios.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

# Note: 'builtin' mode often implies a more complex setup where the browser is
# launched and managed by Playwright in a specific way, and Crawl4ai connects to it.
# For a simple demonstration, it might behave similarly to 'dedicated' if not carefully orchestrated.
# The key is `use_managed_browser=True` and letting the BrowserManager handle CDP details.

async def builtin_browser_mode_config():
    # 'builtin' mode primarily signals that the browser lifecycle is managed
    # internally, often implying connection to a persistent browser instance.
    # `use_managed_browser` is True implicitly.
    # For this test, the cdp_url will be set by the internal ManagedBrowser.
    
    browser_cfg = BrowserConfig(
        browser_mode="builtin", 
        headless=True,
        verbose=True
    )
    print(f"Builtin mode BrowserConfig: {browser_cfg.to_dict(exclude_none=True)}")
    assert browser_cfg.browser_mode == "builtin"
    assert browser_cfg.use_managed_browser # Should be True for builtin

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # The crawler will internally manage the browser and connect via CDP
        print("Crawler will use its managed browser instance via CDP (builtin mode).")
        result = await crawler.arun(url="https://example.com", config=CrawlerRunConfig())
        if result.success:
            print(f"Crawled successfully with 'builtin' browser mode. Page title: {result.metadata.get('title')}")
        else:
            print(f"Crawl failed with 'builtin' browser mode: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(builtin_browser_mode_config())
```

---
#### 4.2.2. Example: Using `browser_mode="docker"` (conceptual outline, actual Docker setup is external).
This mode implies Crawl4ai connecting to a browser running inside a Docker container. Actual Docker setup is beyond this example's scope.

```python
import asyncio
from crawl4ai import BrowserConfig # AsyncWebCrawler, CrawlerRunConfig (not directly run here)

# This is a conceptual outline. Running this requires:
# 1. A Docker image with a browser and Playwright server (or just browser with CDP enabled).
# 2. The Docker container running and exposing the CDP port.
# 3. The `cdp_url` correctly pointing to the Docker container's exposed port.

async def docker_browser_mode_conceptual():
    # Assume Docker container exposes CDP on localhost:9222
    # The cdp_url would be set by the (not-yet-implemented) DockerBrowserStrategy.
    # For now, browser_mode="docker" signals intent; actual connection uses cdp_url.
    
    docker_cdp_url = "ws://localhost:9222/devtools/browser/some-id" # Example CDP URL from Docker
    
    browser_cfg_docker_intent = BrowserConfig(
        browser_mode="docker",
        headless=True # Usually true for Docker
    )
    # When a DockerBrowserStrategy is implemented, it would handle launching/connecting
    # and setting the cdp_url. For now, this mode serves as a placeholder.
    # To actually connect to a Dockerized browser, you'd use 'custom' mode with a cdp_url.
    print(f"Conceptual Docker mode BrowserConfig (intent): {browser_cfg_docker_intent.to_dict(exclude_none=True)}")
    assert browser_cfg_docker_intent.browser_mode == "docker"
    assert browser_cfg_docker_intent.use_managed_browser # Docker mode implies managed connection

    print("\nTo actually connect to a Dockerized browser, you'd typically use:")
    browser_cfg_docker_connect = BrowserConfig(
        browser_mode="custom", # Or 'dedicated' if Crawl4ai itself starts the Docker container
        cdp_url=docker_cdp_url, # The actual CDP endpoint of the browser in Docker
        headless=True 
    )
    print(f"Actual connection to Dockerized browser would use: {browser_cfg_docker_connect.to_dict(exclude_none=True)}")

if __name__ == "__main__":
    asyncio.run(docker_browser_mode_conceptual())
    print("\nNote: 'docker' mode is currently more of an intent. For actual connection to a pre-existing Dockerized browser, use 'custom' mode with its cdp_url.")
```

---
#### 4.2.3. Example: Connecting to an externally managed browser via CDP URL using `browser_mode="custom"` and `cdp_url`.
If you have a browser already running (e.g., manually, or by another tool) and its Chrome DevTools Protocol endpoint is known.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

# This example requires an external Chrome/Chromium instance started with remote debugging enabled.
# E.g., /path/to/chrome --remote-debugging-port=9222 --headless --user-data-dir=/tmp/mychromedata
# Then find the browser's CDP endpoint (e.g., from http://localhost:9222/json/version -> webSocketDebuggerUrl)

async def custom_cdp_connection():
    # Replace with your actual CDP URL. This is a common placeholder.
    # If no browser is running at this CDP, the example will fail.
    external_cdp_url = "ws://localhost:9222/devtools/browser/some-unique-id" 
    
    # For a real test, you must get this from an actual running browser instance.
    # e.g. by navigating to http://localhost:9222/json in another browser
    # and copying the webSocketDebuggerUrl for a "page" type target.
    # Or, if connecting to the browser endpoint, it would be like:
    # external_cdp_url = "ws://localhost:9222/devtools/browser/...." (from /json/version)


    # Using a known CDP URL implies 'custom' management.
    browser_cfg = BrowserConfig(
        cdp_url=external_cdp_url, # This signals to connect to an existing browser
        browser_mode="custom"     # Explicitly set custom mode
    )
    print(f"Custom CDP BrowserConfig: {browser_cfg.to_dict(exclude_none=True)}")
    assert browser_cfg.cdp_url == external_cdp_url
    assert browser_cfg.use_managed_browser # Connecting via CDP means it's "managed" in this context

    print(f"\nAttempting to connect to external browser via CDP: {external_cdp_url}")
    print("Ensure a browser is running with remote debugging enabled on the specified port and path.")
    
    try:
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url="https://example.com", config=CrawlerRunConfig())
            if result.success:
                print(f"Successfully crawled using external browser. Page title: {result.metadata.get('title')}")
            else:
                print(f"Crawl failed using external browser: {result.error_message}")
    except Exception as e:
        print(f"Failed to connect or crawl with external browser: {e}")
        print("Common reasons: No browser at CDP URL, incorrect CDP URL, network issues.")

if __name__ == "__main__":
    # asyncio.run(custom_cdp_connection())
    print("Skipping custom_cdp_connection example as it requires a pre-configured external browser with CDP.")
    print("To run, start a browser with remote debugging and update 'external_cdp_url'.")
```

---
#### 4.2.4. Example: Enabling a persistent browser context with `use_persistent_context=True` and specifying `user_data_dir`.
Saves browser state (cookies, localStorage, etc.) to a directory, allowing sessions to persist across crawler restarts.

```python
import asyncio
import shutil
from pathlib import Path
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def persistent_context_example():
    # Create a temporary directory for user data
    user_data_path = Path("./temp_crawl4ai_user_data_persistent")
    if user_data_path.exists():
        shutil.rmtree(user_data_path) # Clean up from previous runs
    user_data_path.mkdir(parents=True, exist_ok=True)

    print(f"Using persistent user data directory: {user_data_path.resolve()}")

    browser_cfg_persistent = BrowserConfig(
        use_persistent_context=True,
        user_data_dir=str(user_data_path.resolve()), # Must be an absolute path for Playwright
        headless=True, # Can be False for debugging the persistent state
        verbose=True
    )
    # `use_persistent_context=True` automatically implies `use_managed_browser=True`.
    print(f"Persistent Context BrowserConfig: {browser_cfg_persistent.to_dict(exclude_none=True)}")
    assert browser_cfg_persistent.use_persistent_context
    assert browser_cfg_persistent.user_data_dir == str(user_data_path.resolve())

    # First run: crawl a page, maybe set a cookie (implicitly or explicitly)
    run_config1 = CrawlerRunConfig(url="https://httpbin.org/cookies/set?mycookie=myvalue")
    
    async with AsyncWebCrawler(config=browser_cfg_persistent) as crawler:
        print("\n--- First run: Setting a cookie ---")
        result1 = await crawler.arun(config=run_config1)
        if result1.success:
            print(f"First run to {result1.url} successful.")
            # httpbin.org/cookies/set redirects to /cookies, which shows current cookies
            if "mycookie" in result1.html and "myvalue" in result1.html:
                 print("Cookie 'mycookie=myvalue' likely set and visible in response.")
            else:
                 print("Cookie might not be immediately visible in this response, check next run.")
        else:
            print(f"First run failed: {result1.error_message}")

    # Second run: with the same BrowserConfig (and thus same user_data_dir)
    # The cookie "mycookie" should persist.
    run_config2 = CrawlerRunConfig(url="https://httpbin.org/cookies") # This page shows received cookies

    async with AsyncWebCrawler(config=browser_cfg_persistent) as crawler: # Reuses the same persistent context
        print("\n--- Second run: Checking for persisted cookie ---")
        result2 = await crawler.arun(config=run_config2)
        if result2.success:
            print(f"Second run to {result2.url} successful.")
            print(f"Response content (cookies): {result2.html}")
            if "mycookie" in result2.html and "myvalue" in result2.html:
                print("SUCCESS: Cookie 'mycookie=myvalue' persisted across runs!")
            else:
                print("FAILURE: Cookie did not persist or was not found.")
        else:
            print(f"Second run failed: {result2.error_message}")

    # Clean up the temporary directory
    if user_data_path.exists():
        shutil.rmtree(user_data_path)
    print(f"\nCleaned up user data directory: {user_data_path.resolve()}")

if __name__ == "__main__":
    asyncio.run(persistent_context_example())
```

---
#### 4.2.5. Example: Specifying Chrome browser channel using `channel="chrome"`.
Launches the stable Chrome browser if installed, instead of Chromium.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def chrome_channel_config():
    # This requires Google Chrome (stable channel) to be installed.
    # Playwright will attempt to find it.
    browser_cfg = BrowserConfig(
        browser_type="chromium", # Still 'chromium' as base type for Playwright
        channel="chrome",        # Specify 'chrome' channel
        headless=True
    )
    print(f"Chrome Channel BrowserConfig: {browser_cfg.to_dict(exclude_none=True)}")
    assert browser_cfg.channel == "chrome"

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print("Attempting to crawl with Google Chrome (stable channel)...")
        result = await crawler.arun(url="https://example.com", config=CrawlerRunConfig())
        if result.success:
            print(f"Crawled successfully with Chrome channel. Page title: {result.metadata.get('title')}")
            # To truly verify, one might check specific Chrome-only features or detailed UA string,
            # but that's beyond simple config demonstration.
        else:
            print(f"Crawl failed with Chrome channel: {result.error_message}")
            print("Ensure Google Chrome (stable) is installed and accessible by Playwright.")

if __name__ == "__main__":
    asyncio.run(chrome_channel_config())
```

---
#### 4.2.6. Example: Specifying Microsoft Edge browser channel using `channel="msedge"`.
Launches Microsoft Edge browser if installed.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def msedge_channel_config():
    # This requires Microsoft Edge (stable channel) to be installed.
    browser_cfg = BrowserConfig(
        browser_type="chromium", # Base type for Playwright
        channel="msedge",        # Specify 'msedge' channel
        headless=True
    )
    print(f"MS Edge Channel BrowserConfig: {browser_cfg.to_dict(exclude_none=True)}")
    assert browser_cfg.channel == "msedge"

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print("Attempting to crawl with Microsoft Edge (stable channel)...")
        result = await crawler.arun(url="https://example.com", config=CrawlerRunConfig())
        if result.success:
            print(f"Crawled successfully with MS Edge channel. Page title: {result.metadata.get('title')}")
        else:
            print(f"Crawl failed with MS Edge channel: {result.error_message}")
            print("Ensure Microsoft Edge (stable) is installed and accessible by Playwright.")

if __name__ == "__main__":
    asyncio.run(msedge_channel_config())
```

---
### 4.3. Proxy Configuration in `BrowserConfig`

#### 4.3.1. Example: Setting a simple proxy string using the `proxy` parameter.
This is a shorthand for providing proxy details directly as a string.

```python
import asyncio
from crawl4ai import BrowserConfig #, AsyncWebCrawler, CrawlerRunConfig

async def simple_proxy_string_in_browserconfig():
    # Format: "scheme://user:pass@host:port" or "scheme://host:port"
    # This is a non-functional placeholder.
    proxy_server_string = "http://user:password@proxy.example.com:8080" 
    
    browser_cfg = BrowserConfig(proxy=proxy_server_string, headless=True)
    print(f"BrowserConfig with simple proxy string: {browser_cfg.proxy}")
    
    # The `proxy` string is parsed internally into Playwright's proxy format.
    # To demonstrate its effect, one would typically use it with AsyncWebCrawler:
    # async with AsyncWebCrawler(config=browser_cfg) as crawler:
    #     result = await crawler.arun(url="https://httpbin.org/ip")
    #     print(result.html) # Should show proxy's IP
    
    print(f"Proxy server string set to: {browser_cfg.proxy}")
    # Note: The ProxyConfig object is not explicitly created or exposed when using the 'proxy' string directly.
    # If you need to access ProxyConfig attributes, use the `proxy_config` parameter with a ProxyConfig object.

if __name__ == "__main__":
    asyncio.run(simple_proxy_string_in_browserconfig())
```

---
#### 4.3.2. Example: Using a detailed `ProxyConfig` object via the `proxy_config` parameter.
Provides more structured control over proxy settings.

```python
import asyncio
from crawl4ai import BrowserConfig, ProxyConfig #, AsyncWebCrawler, CrawlerRunConfig

async def detailed_proxy_object_in_browserconfig():
    # This is a non-functional placeholder.
    proxy_obj = ProxyConfig(
        server="http://anotherproxy.example.com:3128",
        username="proxy_user_obj",
        password="proxy_password_obj"
    )
    
    browser_cfg = BrowserConfig(proxy_config=proxy_obj, headless=True)
    print(f"BrowserConfig with ProxyConfig object: {browser_cfg.proxy_config.to_dict()}") # type: ignore
    assert browser_cfg.proxy_config.server == "http://anotherproxy.example.com:3128" # type: ignore

    # To demonstrate its effect:
    # async with AsyncWebCrawler(config=browser_cfg) as crawler:
    #     result = await crawler.arun(url="https://httpbin.org/ip")
    #     print(result.html) # Should show proxy's IP
    print("ProxyConfig object set. For a live test, replace placeholder with a real proxy.")

if __name__ == "__main__":
    asyncio.run(detailed_proxy_object_in_browserconfig())
```

---
### 4.4. Viewport and Display Settings

#### 4.4.1. Example: Setting custom viewport dimensions using `viewport_width` and `viewport_height`.
Controls the initial size of the browser window/viewport.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def custom_viewport_dimensions():
    browser_cfg = BrowserConfig(
        viewport_width=1920,
        viewport_height=1080,
        headless=True
    )
    print(f"BrowserConfig with custom viewport: Width={browser_cfg.viewport_width}, Height={browser_cfg.viewport_height}")
    assert browser_cfg.viewport_width == 1920
    assert browser_cfg.viewport_height == 1080

    # Demonstrate by checking JavaScript window dimensions
    run_config = CrawlerRunConfig(
        js_code="JSON.stringify({width: window.innerWidth, height: window.innerHeight})"
    )
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://example.com", config=run_config)
        if result.success and result.js_execution_result:
            dims = result.js_execution_result
            print(f"JS reported dimensions: {dims}")
            # Note: Playwright viewport might differ slightly from window.innerWidth/Height due to scrollbars etc.
            # This example primarily shows the config is passed.
            assert dims.get("width") is not None # Check if JS executed
        else:
            print(f"Crawl or JS execution failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(custom_viewport_dimensions())
```

---
#### 4.4.2. Example: Setting viewport dimensions using the `viewport` dictionary parameter.
An alternative way to set viewport size, overriding individual width/height parameters if both are set.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig
import json

async def viewport_dict_parameter():
    viewport_dimensions = {"width": 800, "height": 600}
    browser_cfg = BrowserConfig(
        viewport=viewport_dimensions,
        headless=True,
        # If viewport_width/height were also set, 'viewport' dict takes precedence
        viewport_width=1200 # This will be overridden by the viewport dict
    )
    print(f"BrowserConfig with viewport dict: {browser_cfg.viewport}")
    print(f"Effective viewport_width: {browser_cfg.viewport_width}") # Should be 800
    print(f"Effective viewport_height: {browser_cfg.viewport_height}") # Should be 600

    assert browser_cfg.viewport_width == 800
    assert browser_cfg.viewport_height == 600

    # Demonstrate by checking JavaScript window dimensions
    run_config = CrawlerRunConfig(
        js_code="JSON.stringify({width: window.innerWidth, height: window.innerHeight})"
    )
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://example.com", config=run_config)
        if result.success and result.js_execution_result:
            dims = result.js_execution_result
            print(f"JS reported dimensions: {dims}")
            # Similar to above, exact match might vary due to browser chrome
            assert dims.get("width") is not None
        else:
            print(f"Crawl or JS execution failed: {result.error_message}")
            
if __name__ == "__main__":
    asyncio.run(viewport_dict_parameter())
```

---
### 4.5. Downloads and Storage State

#### 4.5.1. Example: Enabling file downloads with `accept_downloads=True` and specifying `downloads_path`.
Allows the browser to download files triggered by page interactions or navigations.

```python
import asyncio
import os
import shutil
from pathlib import Path
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def enable_file_downloads():
    # Create a temporary directory for downloads
    temp_downloads_dir = Path("./temp_crawl4ai_downloads")
    if temp_downloads_dir.exists():
        shutil.rmtree(temp_downloads_dir)
    temp_downloads_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloads will be saved to: {temp_downloads_dir.resolve()}")

    browser_cfg = BrowserConfig(
        accept_downloads=True,
        downloads_path=str(temp_downloads_dir.resolve()),
        headless=True
    )
    print(f"BrowserConfig for downloads: accept_downloads={browser_cfg.accept_downloads}, path={browser_cfg.downloads_path}")
    assert browser_cfg.accept_downloads
    assert browser_cfg.downloads_path == str(temp_downloads_dir.resolve())
    
    # A small, publicly downloadable file (e.g., a sample text file or small image)
    # This URL directly triggers a download for a sample PDF from an educational site
    download_trigger_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

    run_config = CrawlerRunConfig(
        url=download_trigger_url,
        # For direct downloads, Playwright often handles it without JS click.
        # If it was a button: js_code="document.querySelector('#downloadButton').click();"
        # We also need to give it time for the download to complete.
        page_timeout=30000 # 30 seconds for download
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"Attempting to download from: {download_trigger_url}")
        result = await crawler.arun(config=run_config)
        
        if result.success:
            print("Crawl part successful. Checking for downloaded files...")
            if result.downloaded_files:
                print(f"Files downloaded to {browser_cfg.downloads_path}:")
                for file_path in result.downloaded_files:
                    print(f"  - {file_path} (Size: {Path(file_path).stat().st_size} bytes)")
                assert len(result.downloaded_files) > 0
            else:
                print("No files reported as downloaded by the crawler. The page might not have triggered a download as expected, or the download event was missed.")
        else:
            print(f"Crawl failed: {result.error_message}")
            
    # Clean up
    if temp_downloads_dir.exists():
        shutil.rmtree(temp_downloads_dir)
    print(f"Cleaned up downloads directory: {temp_downloads_dir.resolve()}")

if __name__ == "__main__":
    asyncio.run(enable_file_downloads())
```

---
#### 4.5.2. Example: Loading browser state (cookies, localStorage) from a file path using `storage_state`.
Restores a previously saved browser session.

```python
import asyncio
import json
import shutil
from pathlib import Path
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def load_storage_state_from_file():
    # Create a dummy storage state file for this example
    storage_state_path = Path("./temp_crawl4ai_storage_state.json")
    dummy_storage_state = {
        "cookies": [{
            "name": "persistent_cookie", "value": "loaded_from_file",
            "domain": "httpbin.org", "path": "/", "expires": -1,
            "httpOnly": False, "secure": False, "sameSite": "Lax"
        }],
        "origins": [{
            "origin": "https://httpbin.org",
            "localStorage": [{"name": "persistent_ls_item", "value": "loaded_from_file_ls"}]
        }]
    }
    with open(storage_state_path, 'w') as f:
        json.dump(dummy_storage_state, f)

    print(f"Using storage state from file: {storage_state_path.resolve()}")

    browser_cfg = BrowserConfig(
        storage_state=str(storage_state_path.resolve()),
        headless=True,
        verbose=True
    )
    print(f"BrowserConfig with storage_state file: {browser_cfg.storage_state}")
    
    # URL to check cookies and localStorage
    check_url = "https://httpbin.org/anything" 
    # JS to retrieve localStorage (httpbin doesn't show it directly in /anything)
    js_to_get_ls = "JSON.stringify(localStorage.getItem('persistent_ls_item'))"

    run_config = CrawlerRunConfig(url=check_url, js_code=js_to_get_ls)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Crawled {result.url} with loaded storage state.")
            response_data = json.loads(result.html) # httpbin.org/anything returns JSON
            
            # Check for cookie
            if "persistent_cookie=loaded_from_file" in response_data.get("headers", {}).get("Cookie", ""):
                print("SUCCESS: Cookie 'persistent_cookie' was loaded and sent!")
            else:
                print(f"Cookie not found in request headers. Cookies: {response_data.get('headers', {}).get('Cookie')}")

            # Check for localStorage item (via JS execution result)
            if result.js_execution_result == '"loaded_from_file_ls"': # JS returns JSON string
                print("SUCCESS: localStorage item 'persistent_ls_item' was loaded!")
            else:
                print(f"localStorage item not found or incorrect. JS result: {result.js_execution_result}")
        else:
            print(f"Crawl failed: {result.error_message}")

    # Clean up
    if storage_state_path.exists():
        storage_state_path.unlink()
    print(f"\nCleaned up storage state file: {storage_state_path.resolve()}")

if __name__ == "__main__":
    asyncio.run(load_storage_state_from_file())
```

---
#### 4.5.3. Example: Loading browser state from an in-memory dictionary using `storage_state`.
Allows providing cookies and localStorage directly as a Python dictionary.

```python
import asyncio
import json
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def load_storage_state_from_dict():
    in_memory_storage_state = {
        "cookies": [{
            "name": "mem_cookie", "value": "loaded_from_dict",
            "url": "https://httpbin.org" # More robust to use 'url' or 'domain'/'path'
        }],
        "origins": [{
            "origin": "https://httpbin.org",
            "localStorage": [{"name": "mem_ls_item", "value": "loaded_from_dict_ls"}]
        }]
    }
    print(f"Using in-memory storage state: {in_memory_storage_state}")

    browser_cfg = BrowserConfig(
        storage_state=in_memory_storage_state,
        headless=True,
        verbose=True
    )
    
    check_url = "https://httpbin.org/anything"
    js_to_get_ls = "JSON.stringify(localStorage.getItem('mem_ls_item'))"
    run_config = CrawlerRunConfig(url=check_url, js_code=js_to_get_ls)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Crawled {result.url} with in-memory storage state.")
            response_data = json.loads(result.html)
            
            if "mem_cookie=loaded_from_dict" in response_data.get("headers", {}).get("Cookie", ""):
                print("SUCCESS: Cookie 'mem_cookie' was loaded and sent!")
            else:
                print(f"Cookie not found in request headers. Cookies: {response_data.get('headers', {}).get('Cookie')}")

            if result.js_execution_result == '"loaded_from_dict_ls"':
                print("SUCCESS: localStorage item 'mem_ls_item' was loaded!")
            else:
                print(f"localStorage item not found or incorrect. JS result: {result.js_execution_result}")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(load_storage_state_from_dict())
```

---
### 4.6. Security and Scripting Control

#### 4.6.1. Example: Enforcing HTTPS error checks by setting `ignore_https_errors=False`.
By default, Crawl4ai (via Playwright) ignores HTTPS errors. This shows how to enforce them.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def enforce_https_errors():
    browser_cfg = BrowserConfig(
        ignore_https_errors=False, # Default is True
        headless=True
    )
    print(f"BrowserConfig with ignore_https_errors={browser_cfg.ignore_https_errors}")
    assert not browser_cfg.ignore_https_errors
    
    # Use a site with a known SSL issue (e.g., expired, self-signed)
    # expired.badssl.com is a good test site for this
    # For safety in automated tests, we won't hit a live "bad" SSL site by default.
    # test_url_with_ssl_issue = "https://expired.badssl.com/"
    test_url_good_ssl = "https://example.com"


    print(f"Attempting to crawl {test_url_good_ssl} (should succeed).")
    run_config = CrawlerRunConfig(url=test_url_good_ssl)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Successfully crawled {test_url_good_ssl} with HTTPS errors NOT ignored.")
        else:
            print(f"Crawl failed for {test_url_good_ssl}: {result.error_message}")

    # To test the error case:
    # print(f"\nAttempting to crawl {test_url_with_ssl_issue} (should fail due to SSL error).")
    # run_config_bad_ssl = CrawlerRunConfig(url=test_url_with_ssl_issue)
    # async with AsyncWebCrawler(config=browser_cfg) as crawler:
    #     result_bad = await crawler.arun(config=run_config_bad_ssl)
    #     if not result_bad.success and "net::ERR_CERT_DATE_INVALID" in result_bad.error_message: # Or similar error
    #         print(f"SUCCESS: Crawl failed as expected for {test_url_with_ssl_issue} due to SSL error: {result_bad.error_message[:100]}...")
    #     elif result_bad.success:
    #         print(f"UNEXPECTED: Crawl succeeded for {test_url_with_ssl_issue}, SSL error might not have been caught.")
    #     else:
    #         print(f"Crawl failed for {test_url_with_ssl_issue} for other reasons: {result_bad.error_message}")
    print("\nNote: Actual test for HTTPS error enforcement requires a site like expired.badssl.com.")


if __name__ == "__main__":
    asyncio.run(enforce_https_errors())
```

---
#### 4.6.2. Example: Disabling JavaScript execution in pages by setting `java_script_enabled=False`.
Prevents JavaScript from running, which can speed up crawls but might break sites reliant on JS.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def disable_javascript():
    browser_cfg = BrowserConfig(
        java_script_enabled=False, # Default is True
        headless=True
    )
    print(f"BrowserConfig with java_script_enabled={browser_cfg.java_script_enabled}")
    assert not browser_cfg.java_script_enabled
    
    # A page that uses JS to modify content
    # httpbin.org/html includes a simple script
    test_url = "https://httpbin.org/html" 
    run_config = CrawlerRunConfig(url=test_url)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"Attempting to crawl {test_url} with JavaScript disabled.")
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Successfully crawled {test_url}.")
            # Look for signs that JS did NOT run.
            # The sample JS on httpbin.org/html adds "Hello, world!" to an h1.
            # If JS is disabled, this text should be absent or different.
            # The original h1 on httpbin.org/html is "Herman Melville - Moby-Dick"
            if "Moby-Dick" in result.html and "Hello, world!" not in result.html:
                print("SUCCESS: JavaScript seems to have been disabled (JS-added content not found).")
            else:
                print("JavaScript execution state is inconclusive from this page's content.")
                # print(result.html) # For debugging
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(disable_javascript())
```

---
### 4.7. Headers, Cookies, and User Agent Customization

#### 4.7.1. Example: Adding a list of custom `cookies` to be set in the browser context.
These cookies will be sent with all requests made by this browser context.

```python
import asyncio
import json
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def custom_cookies_browser_config():
    custom_cookies_list = [
        {"name": "my_custom_cookie", "value": "cookie_value_123", "url": "https://httpbin.org"},
        {"name": "another_cookie", "value": "more_data", "domain": ".httpbin.org", "path": "/"}
    ]
    browser_cfg = BrowserConfig(cookies=custom_cookies_list, headless=True)
    print(f"BrowserConfig with custom cookies: {browser_cfg.cookies}")
    
    # httpbin.org/cookies shows cookies sent by the client
    run_config = CrawlerRunConfig(url="https://httpbin.org/cookies")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Crawled {result.url} with custom cookies.")
            response_data = json.loads(result.html) # httpbin returns JSON
            print(f"Cookies received by server: {response_data.get('cookies')}")
            assert "my_custom_cookie" in response_data.get("cookies", {})
            assert response_data.get("cookies", {}).get("my_custom_cookie") == "cookie_value_123"
            assert "another_cookie" in response_data.get("cookies", {})
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(custom_cookies_browser_config())
```

---
#### 4.7.2. Example: Setting default `headers` for all requests made within the browser context.
These headers will be added to every HTTP request.

```python
import asyncio
import json
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def default_headers_browser_config():
    custom_headers_dict = {
        "X-Custom-Header": "Crawl4AI-Test",
        "Accept-Language": "de-DE,de;q=0.9" # Example: German language preference
    }
    browser_cfg = BrowserConfig(headers=custom_headers_dict, headless=True)
    print(f"BrowserConfig with default headers: {browser_cfg.headers}")
    
    # httpbin.org/headers shows headers received by the server
    run_config = CrawlerRunConfig(url="https://httpbin.org/headers")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Crawled {result.url} with custom default headers.")
            response_data = json.loads(result.html) # httpbin returns JSON
            print(f"Headers received by server (excerpt):")
            received_headers = response_data.get("headers", {})
            for key, value in custom_headers_dict.items():
                print(f"  {key}: {received_headers.get(key)}")
                assert received_headers.get(key) == value
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(default_headers_browser_config())
```

---
#### 4.7.3. Example: Setting a specific `user_agent` string.
Overrides the default Playwright user agent.

```python
import asyncio
import json
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def specific_user_agent_config():
    my_ua_string = "MyCustomCrawler/1.0 (compatible; MyBot/0.1; +http://mybot.example.com)"
    browser_cfg = BrowserConfig(user_agent=my_ua_string, headless=True)
    print(f"BrowserConfig with specific User-Agent: {browser_cfg.user_agent}")
    assert browser_cfg.user_agent == my_ua_string
    
    # httpbin.org/user-agent shows the User-Agent header received by the server
    run_config = CrawlerRunConfig(url="https://httpbin.org/user-agent")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Crawled {result.url} with specific User-Agent.")
            response_data = json.loads(result.html)
            print(f"User-Agent received by server: {response_data.get('user-agent')}")
            assert response_data.get('user-agent') == my_ua_string
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(specific_user_agent_config())
```

---
#### 4.7.4. Example: Generating a random `user_agent` by setting `user_agent_mode="random"`.
Uses the built-in user agent generator to pick a random, valid user agent.

```python
import asyncio
import json
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def random_user_agent_config():
    # user_agent_mode="random" will use ValidUAGenerator by default
    browser_cfg = BrowserConfig(user_agent_mode="random", headless=True, verbose=True)
    # The actual user_agent string is generated upon BrowserConfig initialization if mode is random.
    print(f"BrowserConfig with random User-Agent mode. Generated UA: {browser_cfg.user_agent}")
    assert browser_cfg.user_agent is not None 
    assert browser_cfg.user_agent != BrowserConfig().user_agent # Should be different from default
    
    run_config = CrawlerRunConfig(url="https://httpbin.org/user-agent")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Crawled {result.url} with a random User-Agent.")
            response_data = json.loads(result.html)
            print(f"User-Agent received by server: {response_data.get('user-agent')}")
            assert response_data.get('user-agent') == browser_cfg.user_agent # Check if it matches the one set
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(random_user_agent_config())
```

---
#### 4.7.5. Example: Customizing random user agent generation using `user_agent_generator_config` (e.g., specifying device type or OS).
Allows fine-tuning the type of random user agent generated.

```python
import asyncio
import json
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def custom_random_user_agent_config():
    # Example: Generate a random user agent for a Linux Desktop
    ua_gen_config = {"device_type": "desktop", "os_name": "linux"}
    
    browser_cfg = BrowserConfig(
        user_agent_mode="random",
        user_agent_generator_config=ua_gen_config,
        headless=True,
        verbose=True
    )
    generated_ua = browser_cfg.user_agent
    print(f"BrowserConfig with custom random UA generation. Config: {ua_gen_config}")
    print(f"Generated UA: {generated_ua}")
    
    # Basic check if the UA string seems plausible for Linux
    assert "Linux" in generated_ua or "X11" in generated_ua
    
    run_config = CrawlerRunConfig(url="https://httpbin.org/user-agent")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Crawled {result.url} with custom random User-Agent.")
            response_data = json.loads(result.html)
            print(f"User-Agent received by server: {response_data.get('user-agent')}")
            assert response_data.get('user-agent') == generated_ua
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(custom_random_user_agent_config())
```

---
#### 4.7.6. Example: Demonstrating `BrowserConfig` automatically setting `sec-ch-ua` client hint headers.
`BrowserConfig` automatically derives and sets appropriate `Sec-CH-UA` client hint headers based on the `user_agent`.

```python
import asyncio
import json
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def sec_ch_ua_header_demonstration():
    # Using a specific User-Agent that would imply certain client hints
    # This UA is for Chrome 116 on Linux
    ua_string = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    
    browser_cfg = BrowserConfig(user_agent=ua_string, headless=True, verbose=True)
    print(f"BrowserConfig User-Agent: {browser_cfg.user_agent}")
    print(f"Automatically generated Sec-CH-UA client hint: {browser_cfg.browser_hint}")
    
    # Expected client hint might look something like:
    # '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"'
    # The exact value depends on the UAGen library's parsing of the UA.
    assert "Chromium" in browser_cfg.browser_hint or "Google Chrome" in browser_cfg.browser_hint
    assert "116" in browser_cfg.browser_hint

    run_config = CrawlerRunConfig(url="https://httpbin.org/headers")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Crawled {result.url}. Checking received headers by server...")
            response_data = json.loads(result.html)
            received_headers = response_data.get("headers", {})
            
            print(f"  User-Agent: {received_headers.get('User-Agent')}")
            print(f"  Sec-Ch-Ua: {received_headers.get('Sec-Ch-Ua')}") # Case-insensitive matching might be needed for real server
            
            # Check if the Sec-CH-UA header set by BrowserConfig was received
            # Note: httpbin.org might not show all client hints perfectly, or Playwright might override some.
            # This primarily tests that BrowserConfig correctly *sets* it for Playwright.
            # The actual sent header can depend on Playwright's behavior with that browser version.
            if browser_cfg.browser_hint.strip('"') in received_headers.get('Sec-Ch-Ua', '').strip('"'):
                 print("SUCCESS: Sec-CH-UA client hint seems to be correctly passed through.")
            else:
                 print("NOTE: Sec-CH-UA might differ slightly due to Playwright/browser behavior or httpbin.org limitations.")
                 print(f"   Expected hint from BrowserConfig: {browser_cfg.browser_hint}")

        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(sec_ch_ua_header_demonstration())
```

---
### 4.8. Performance and Other Browser Settings

#### 4.8.1. Example: Using `text_mode=True` to attempt disabling images and rich content for faster text-focused crawls.
This mode aims to block resources like images, fonts, and potentially some scripts to speed up loading for text extraction.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def text_mode_config():
    browser_cfg = BrowserConfig(text_mode=True, headless=True, verbose=True)
    print(f"BrowserConfig with text_mode: {browser_cfg.text_mode}")
    assert browser_cfg.text_mode
    
    # A page with images
    run_config = CrawlerRunConfig(url="https://example.com") # example.com has an IANA logo

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"Attempting to crawl {run_config.url} in text_mode.")
        # We'll also capture network requests to see if image requests are blocked.
        result = await crawler.arun(config=run_config.clone(capture_network_requests=True))
        
        if result.success:
            print(f"Successfully crawled {run_config.url} in text_mode.")
            
            image_requests_found = False
            if result.network_requests:
                for req in result.network_requests:
                    if req.get("event_type") == "request" and req.get("resource_type") == "image":
                        image_requests_found = True
                        print(f"Found image request (unexpected in text_mode): {req.get('url')}")
                        break
            
            if not image_requests_found:
                print("SUCCESS: No image requests were detected, as expected in text_mode.")
            else:
                print("WARNING: Image requests were detected. Text_mode might not have fully blocked them for this site/browser.")
            
            # Check if images are absent in the rendered HTML (might be harder to verify reliably)
            # print(f"HTML (first 500 chars):\n{result.html[:500]}")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(text_mode_config())
```

---
#### 4.8.2. Example: Using `light_mode=True` to disable certain background browser features for performance.
`light_mode` applies a set of browser flags (defined in `BROWSER_DISABLE_OPTIONS` in `browser_manager.py`) to reduce resource usage.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def light_mode_config():
    browser_cfg = BrowserConfig(light_mode=True, headless=True, verbose=True)
    print(f"BrowserConfig with light_mode: {browser_cfg.light_mode}")
    print(f"Extra args applied by light_mode (subset shown): {browser_cfg.extra_args[:5]}...")
    assert browser_cfg.light_mode
    # Check if some known light_mode flags are present in extra_args
    assert "--disable-background-networking" in browser_cfg.extra_args 
    
    run_config = CrawlerRunConfig(url="https://example.com")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"Attempting to crawl {run_config.url} in light_mode.")
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Successfully crawled {run_config.url} in light_mode.")
            # Effect of light_mode is on browser resource usage, not directly visible in content typically.
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(light_mode_config())
```

---
#### 4.8.3. Example: Passing additional command-line `extra_args` to the browser launcher.
Allows fine-grained control over browser behavior by passing Chromium/Firefox specific flags.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def extra_args_config():
    # Example: Disable GPU (often useful in headless environments)
    # and set a custom window size (though viewport is preferred for content area)
    custom_args = [
        "--disable-gpu", 
        "--window-size=800,600" # Note: viewport_width/height is preferred for content area
    ]
    browser_cfg = BrowserConfig(extra_args=custom_args, headless=True) # Usually headless with these args
    print(f"BrowserConfig with extra_args: {browser_cfg.extra_args}")
    assert "--disable-gpu" in browser_cfg.extra_args
    
    run_config = CrawlerRunConfig(url="https://example.com")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"Attempting to crawl {run_config.url} with extra browser arguments.")
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Successfully crawled {run_config.url} with extra arguments.")
            # Verifying effect of these args often requires deeper inspection or specific test pages.
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(extra_args_config())
```

---
#### 4.8.4. Example: Setting a custom `debugging_port` and `host` for the browser's remote debugging.
Useful if the default port (9222) is in use or for specific network configurations.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

# Note: This example primarily shows config. It might be hard to verify the port
# change without external tools unless use_managed_browser is also True
# and we try to connect to the new CDP URL.

async def custom_debugging_port_host():
    custom_port = 9333
    custom_host = "127.0.0.1" # Often 'localhost' or '127.0.0.1'

    # This is most relevant for use_managed_browser=True or browser_mode='builtin'
    # as it tells the ManagedBrowser which port to launch on.
    browser_cfg = BrowserConfig(
        debugging_port=custom_port,
        host=custom_host,
        headless=True,
        use_managed_browser=True, # To see the effect of debugging_port
        verbose=True
    )
    print(f"BrowserConfig with custom debugging_port={browser_cfg.debugging_port} and host={browser_cfg.host}")
    assert browser_cfg.debugging_port == custom_port
    assert browser_cfg.host == custom_host

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"Attempting to launch managed browser on {custom_host}:{custom_port} and crawl.")
        # The ManagedBrowser instance within AsyncWebCrawler will use these settings.
        # If successful, it means the browser launched on the custom port and CDP connection was made.
        result = await crawler.arun(url="https://example.com", config=CrawlerRunConfig())
        if result.success:
            print(f"Successfully crawled. Managed browser likely used {custom_host}:{custom_port}.")
        else:
            print(f"Crawl failed: {result.error_message}. This could be due to port conflict or other launch issues.")
            print("Ensure the custom port is available.")
            
if __name__ == "__main__":
    asyncio.run(custom_debugging_port_host())
```

---
#### 4.8.5. Example: Enabling verbose logging for browser operations via `verbose=True`.
Provides more detailed output from the `AsyncWebCrawler` and underlying strategies.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def verbose_browser_logging():
    # Set verbose=True in BrowserConfig
    # This will be picked up by the AsyncLogger if not overridden by CrawlerRunConfig
    browser_cfg = BrowserConfig(verbose=True, headless=True)
    print(f"BrowserConfig verbose setting: {browser_cfg.verbose}")
    
    # CrawlerRunConfig can also have a verbose setting, which might take precedence for that run.
    # Here, we don't set it in CrawlerRunConfig, so BrowserConfig's verbose should apply.
    run_config = CrawlerRunConfig(url="https://example.com")

    print("\nRunning crawl with verbose=True in BrowserConfig. Expect more detailed logs.")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # The logger used by the crawler will inherit verbosity from browser_cfg
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"\nCrawl successful. Verbose logs should have been printed during the process.")
        else:
            print(f"\nCrawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(verbose_browser_logging())
```

---
#### 4.8.6. Example: Using `sleep_on_close=True` to pause before the browser fully closes (useful for debugging).
This is useful when `headless=False` to inspect the final state of the browser before it closes.

```python
import asyncio
from crawl4ai import BrowserConfig, AsyncWebCrawler, CrawlerRunConfig

async def sleep_on_close_example():
    # This is most effective with headless=False
    # In a script, the pause might not be very noticeable if headless=True
    browser_cfg = BrowserConfig(
        sleep_on_close=True, 
        headless=False, # Set to False to see the browser window pause
        verbose=True
    )
    print(f"BrowserConfig with sleep_on_close={browser_cfg.sleep_on_close}")
    
    run_config = CrawlerRunConfig(url="https://example.com")

    print("\nRunning crawl. Browser window should appear and pause for a moment before closing if headless=False.")
    print("(If headless=True, the effect is a slight delay before script termination).")
    try:
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(config=run_config)
            if result.success:
                print(f"Crawl successful. Browser should have paused before closing (if visible).")
            else:
                print(f"Crawl failed: {result.error_message}")
    except Exception as e:
        print(f"Could not run headed browser example for sleep_on_close (common in restricted environments): {e}")
        print("Skipping sleep_on_close headed test.")


if __name__ == "__main__":
    # asyncio.run(sleep_on_close_example())
    print("Skipping sleep_on_close_example. Uncomment to run, preferably with headless=False if you have a display.")
```

---
### 4.9. `BrowserConfig` Utility Methods

#### 4.9.1. Example: Creating `BrowserConfig` from a dictionary of keyword arguments using `BrowserConfig.from_kwargs()`.
Useful for creating config objects dynamically.

```python
import asyncio
from crawl4ai import BrowserConfig

async def browserconfig_from_kwargs():
    kwargs = {
        "browser_type": "firefox",
        "headless": False,
        "viewport_width": 1200,
        "user_agent": "MyTestAgent/1.0"
    }
    browser_cfg = BrowserConfig.from_kwargs(kwargs)
    
    print("BrowserConfig created from_kwargs:")
    print(f"  Browser Type: {browser_cfg.browser_type}")
    print(f"  Headless: {browser_cfg.headless}")
    print(f"  Viewport Width: {browser_cfg.viewport_width}")
    print(f"  User Agent: {browser_cfg.user_agent}")

    assert browser_cfg.browser_type == "firefox"
    assert not browser_cfg.headless
    assert browser_cfg.viewport_width == 1200
    assert browser_cfg.user_agent == "MyTestAgent/1.0"

if __name__ == "__main__":
    asyncio.run(browserconfig_from_kwargs())
```

---
#### 4.9.2. Example: Converting `BrowserConfig` instance to a dictionary using `to_dict()`.
Serializes the config object's attributes to a Python dictionary.

```python
import asyncio
from crawl4ai import BrowserConfig

async def browserconfig_to_dict():
    browser_cfg = BrowserConfig(
        browser_type="webkit",
        headless=True,
        proxy="http://proxy.internal:3128",
        verbose=False
    )
    config_dict = browser_cfg.to_dict()

    print("BrowserConfig instance:")
    print(f"  Original object browser_type: {browser_cfg.browser_type}")
    print(f"  Original object proxy: {browser_cfg.proxy}")
    
    print("\nConverted to dictionary:")
    for key, value in config_dict.items():
        # Only print a few for brevity if it's too long
        if key in ["browser_type", "headless", "proxy", "verbose", "user_agent"]:
             print(f"  {key}: {value}")
    
    assert config_dict["browser_type"] == "webkit"
    assert config_dict["headless"] is True
    assert config_dict["proxy"] == "http://proxy.internal:3128"
    assert config_dict["verbose"] is False # Check a default that was changed or not set

if __name__ == "__main__":
    asyncio.run(browserconfig_to_dict())
```

---
#### 4.9.3. Example: Cloning a `BrowserConfig` instance and modifying its `headless` mode using `clone()`.
Creates a new instance with optionally overridden attributes.

```python
import asyncio
from crawl4ai import BrowserConfig

async def browserconfig_clone_modify():
    original_cfg = BrowserConfig(browser_type="chromium", headless=True, viewport_width=1024)
    print(f"Original Config: headless={original_cfg.headless}, viewport_width={original_cfg.viewport_width}")

    # Clone and change headless mode, keep other settings
    cloned_cfg_headed = original_cfg.clone(headless=False)
    print(f"Cloned Config (headed): headless={cloned_cfg_headed.headless}, viewport_width={cloned_cfg_headed.viewport_width}")

    assert original_cfg.headless is True # Original unchanged
    assert cloned_cfg_headed.headless is False # Cloned is modified
    assert cloned_cfg_headed.browser_type == original_cfg.browser_type # Unspecified attributes are copied
    assert cloned_cfg_headed.viewport_width == original_cfg.viewport_width

if __name__ == "__main__":
    asyncio.run(browserconfig_clone_modify())
```

---
#### 4.9.4. Example: Serializing `BrowserConfig` to a JSON-compatible dictionary using `dump()`.
The `dump()` method leverages `to_serializable_dict` for JSON compatibility.

```python
import asyncio
import json
from crawl4ai import BrowserConfig, ProxyConfig

async def browserconfig_dump_json_compatible():
    proxy_obj = ProxyConfig(server="http://jsondump.proxy:1234")
    browser_cfg = BrowserConfig(
        browser_type="firefox",
        headless=False,
        proxy_config=proxy_obj, # Nested object
        extra_args=["--some-flag"]
    )
    
    # dump() calls to_serializable_dict() internally
    dumped_dict = browser_cfg.dump() 

    print("Dumped BrowserConfig (JSON compatible):")
    print(json.dumps(dumped_dict, indent=2))

    # Check if nested ProxyConfig was serialized correctly
    assert dumped_dict["params"]["proxy_config"]["type"] == "ProxyConfig"
    assert dumped_dict["params"]["proxy_config"]["params"]["server"] == "http://jsondump.proxy:1234"
    assert dumped_dict["params"]["browser_type"] == "firefox"
    
    # Verify it can be loaded back (see next example)

if __name__ == "__main__":
    asyncio.run(browserconfig_dump_json_compatible())
```

---
#### 4.9.5. Example: Deserializing `BrowserConfig` from a dictionary (potentially read from JSON) using `load()`.
The `load()` method reconstructs a `BrowserConfig` instance from its serialized form.

```python
import asyncio
from crawl4ai import BrowserConfig, ProxyConfig

async def browserconfig_load_from_dict():
    serialized_data = {
        "type": "BrowserConfig",
        "params": {
            "browser_type": "webkit",
            "headless": True,
            "proxy_config": {
                "type": "ProxyConfig",
                "params": {"server": "http://jsonload.proxy:5678"}
            },
            "user_agent": "LoadedAgent/2.0",
            "extra_args": ["--another-flag"]
        }
    }
    
    loaded_cfg = BrowserConfig.load(serialized_data)
    
    print("Loaded BrowserConfig from dictionary:")
    print(f"  Browser Type: {loaded_cfg.browser_type}")
    print(f"  Headless: {loaded_cfg.headless}")
    print(f"  User Agent: {loaded_cfg.user_agent}")
    print(f"  Extra Args: {loaded_cfg.extra_args}")
    if loaded_cfg.proxy_config:
        print(f"  Proxy Server: {loaded_cfg.proxy_config.server}")

    assert isinstance(loaded_cfg, BrowserConfig)
    assert loaded_cfg.browser_type == "webkit"
    assert loaded_cfg.headless is True
    assert isinstance(loaded_cfg.proxy_config, ProxyConfig)
    assert loaded_cfg.proxy_config.server == "http://jsonload.proxy:5678" # type: ignore
    assert loaded_cfg.user_agent == "LoadedAgent/2.0"
    assert "--another-flag" in loaded_cfg.extra_args

if __name__ == "__main__":
    asyncio.run(browserconfig_load_from_dict())
```

---
## 5. `HTTPCrawlerConfig` Examples (For non-browser HTTP crawling)
`HTTPCrawlerConfig` is used with strategies like `AsyncHTTPCrawlerStrategy` that make direct HTTP requests without a full browser.

### 5.1. Example: Basic `HTTPCrawlerConfig` for a GET request (default).

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig
# from crawl4ai import AsyncWebCrawler, AsyncHTTPCrawlerStrategy (for full example)

async def basic_httpcrawler_config():
    http_cfg = HTTPCrawlerConfig() # Defaults to method="GET"
    print(f"Default HTTPCrawlerConfig: {http_cfg.to_dict()}")
    assert http_cfg.method == "GET"
    
    # To use it:
    # strategy = AsyncHTTPCrawlerStrategy(http_config=http_cfg)
    # async with AsyncWebCrawler(crawler_strategy=strategy) as crawler:
    #     result = await crawler.arun(url="https://httpbin.org/get")
    #     print(result.html)

if __name__ == "__main__":
    asyncio.run(basic_httpcrawler_config())
```

---
### 5.2. Example: Configuring a POST request with form `data` using `HTTPCrawlerConfig`.

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig
# from crawl4ai import AsyncWebCrawler, AsyncHTTPCrawlerStrategy (for full example)
# import json

async def post_form_data_httpcrawler_config():
    form_payload = {"key1": "value1", "key2": "value2"}
    http_cfg = HTTPCrawlerConfig(method="POST", data=form_payload)
    
    print(f"HTTPCrawlerConfig for POST with form data: {http_cfg.to_dict()}")
    assert http_cfg.method == "POST"
    assert http_cfg.data == form_payload
    
    # To use it:
    # strategy = AsyncHTTPCrawlerStrategy() # Default config is fine, override in arun
    # async with AsyncWebCrawler(crawler_strategy=strategy) as crawler:
    #     run_cfg = CrawlerRunConfig(url="https://httpbin.org/post", http_config=http_cfg)
    #     result = await crawler.arun(config=run_cfg)
    #     if result.success:
    #         response_data = json.loads(result.html)
    #         print(f"Server received form data: {response_data.get('form')}")
    #         assert response_data.get('form') == form_payload

if __name__ == "__main__":
    asyncio.run(post_form_data_httpcrawler_config())
    print("Note: For a live test, you'd use this with AsyncHTTPCrawlerStrategy.")
```

---
### 5.3. Example: Configuring a POST request with a `json` payload using `HTTPCrawlerConfig`.

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig
# from crawl4ai import AsyncWebCrawler, AsyncHTTPCrawlerStrategy (for full example)
# import json

async def post_json_payload_httpcrawler_config():
    json_payload = {"name": "Crawl4AI", "version": "0.6.3"}
    http_cfg = HTTPCrawlerConfig(method="POST", json=json_payload) # Use 'json' parameter
    
    print(f"HTTPCrawlerConfig for POST with JSON payload: {http_cfg.to_dict()}")
    assert http_cfg.method == "POST"
    assert http_cfg.json == json_payload
    
    # To use it:
    # strategy = AsyncHTTPCrawlerStrategy()
    # async with AsyncWebCrawler(crawler_strategy=strategy) as crawler:
    #     run_cfg = CrawlerRunConfig(url="https://httpbin.org/post", http_config=http_cfg)
    #     result = await crawler.arun(config=run_cfg)
    #     if result.success:
    #         response_data = json.loads(result.html)
    #         print(f"Server received JSON data: {response_data.get('json')}")
    #         assert response_data.get('json') == json_payload

if __name__ == "__main__":
    asyncio.run(post_json_payload_httpcrawler_config())
    print("Note: For a live test, you'd use this with AsyncHTTPCrawlerStrategy.")
```

---
### 5.4. Example: Setting custom `headers` for an HTTP request via `HTTPCrawlerConfig`.

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig
# from crawl4ai import AsyncWebCrawler, AsyncHTTPCrawlerStrategy (for full example)
# import json

async def custom_headers_httpcrawler_config():
    custom_http_headers = {
        "X-API-Key": "mysecretapikey",
        "Content-Type": "application/json" # Though httpx might set this for json payload
    }
    http_cfg = HTTPCrawlerConfig(headers=custom_http_headers, method="GET")
    
    print(f"HTTPCrawlerConfig with custom headers: {http_cfg.headers}")
    assert http_cfg.headers["X-API-Key"] == "mysecretapikey"
    
    # To use it:
    # strategy = AsyncHTTPCrawlerStrategy()
    # async with AsyncWebCrawler(crawler_strategy=strategy) as crawler:
    #     run_cfg = CrawlerRunConfig(url="https://httpbin.org/headers", http_config=http_cfg)
    #     result = await crawler.arun(config=run_cfg)
    #     if result.success:
    #         response_data = json.loads(result.html)
    #         print(f"Server received headers (excerpt):")
    #         received_headers = response_data.get("headers", {})
    #         assert received_headers.get("X-Api-Key") == "mysecretapikey" # HTTP headers are case-insensitive

if __name__ == "__main__":
    asyncio.run(custom_headers_httpcrawler_config())
    print("Note: For a live test, you'd use this with AsyncHTTPCrawlerStrategy.")
```

---
### 5.5. Example: Disabling automatic redirect following (`follow_redirects=False`) in `HTTPCrawlerConfig`.

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig, AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy

async def no_redirect_httpcrawler_config():
    http_cfg_no_redirect = HTTPCrawlerConfig(follow_redirects=False)
    print(f"HTTPCrawlerConfig with follow_redirects={http_cfg_no_redirect.follow_redirects}")
    assert not http_cfg_no_redirect.follow_redirects
    
    # httpbin.org/redirect/1 will redirect once
    redirect_url = "https://httpbin.org/redirect/1"
    run_config = CrawlerRunConfig(url=redirect_url)
    
    strategy = AsyncHTTPCrawlerStrategy(http_config=http_cfg_no_redirect)
    async with AsyncWebCrawler(crawler_strategy=strategy) as crawler:
        print(f"Attempting to crawl {redirect_url} with redirects disabled.")
        result = await crawler.arun(config=run_config)
        if result.success:
            print(f"Crawl to {result.url} status: {result.status_code}")
            # Expecting a 302 status code since redirects are off
            assert result.status_code in [301, 302, 303, 307, 308] 
            print(f"SUCCESS: Received redirect status {result.status_code} as expected.")
            print(f"Location header: {result.response_headers.get('Location')}")
        else:
            # This might happen if the test URL itself changes or there's an issue
            print(f"Crawl failed or did not behave as expected: {result.error_message}")
            print(f"Status code: {result.status_code}")


if __name__ == "__main__":
    asyncio.run(no_redirect_httpcrawler_config())
```

---
### 5.6. Example: Disabling SSL certificate verification (`verify_ssl=False`) in `HTTPCrawlerConfig`.
**Warning:** Disabling SSL verification is a security risk and should only be used in trusted environments or for specific testing purposes.

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig, AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy

async def no_ssl_verify_httpcrawler_config():
    http_cfg_no_ssl = HTTPCrawlerConfig(verify_ssl=False)
    print(f"HTTPCrawlerConfig with verify_ssl={http_cfg_no_ssl.verify_ssl}")
    assert not http_cfg_no_ssl.verify_ssl
    
    # Use a site with a self-signed or expired certificate for testing
    # For example: "https://self-signed.badssl.com/" or "https://expired.badssl.com/"
    # For this example, we'll use a regular site, as hitting badssl might cause other issues in CI.
    # The real test is that it *doesn't* fail on a bad SSL site.
    test_url_bad_ssl = "https://expired.badssl.com/" 
    test_url_good_ssl = "https://example.com"

    print(f"Attempting to crawl {test_url_bad_ssl} with SSL verification disabled.")
    print("NOTE: This test is more meaningful if tested against a site with actual SSL issues.")
    
    strategy = AsyncHTTPCrawlerStrategy(http_config=http_cfg_no_ssl)
    async with AsyncWebCrawler(crawler_strategy=strategy) as crawler:
        run_config_bad = CrawlerRunConfig(url=test_url_bad_ssl)
        result_bad = await crawler.arun(config=run_config_bad)
        if result_bad.success:
            print(f"Successfully crawled {test_url_bad_ssl} (SSL errors were ignored).")
        else:
            # It might still fail for other reasons (e.g., site down)
            print(f"Crawl to {test_url_bad_ssl} failed, but not necessarily due to SSL: {result_bad.error_message}")

        # Verify it still works for good SSL sites
        run_config_good = CrawlerRunConfig(url=test_url_good_ssl)
        result_good = await crawler.arun(config=run_config_good)
        if result_good.success:
             print(f"Successfully crawled {test_url_good_ssl} as well.")

if __name__ == "__main__":
    asyncio.run(no_ssl_verify_httpcrawler_config())
```

---
### 5.7. Example: Creating `HTTPCrawlerConfig` using `HTTPCrawlerConfig.from_kwargs()`.

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig

async def httpcrawlerconfig_from_kwargs():
    kwargs = {
        "method": "PUT",
        "headers": {"Authorization": "Bearer mytoken"},
        "json_payload": {"update_key": "new_value"} # Note: constructor uses 'json'
    }
    # The from_kwargs will map json_payload to json if the class expects 'json'
    # Let's check the actual constructor signature for 'json' vs 'json_payload'
    # The HTTPCrawlerConfig constructor takes 'json' not 'json_payload'.
    # So for from_kwargs, we should use the correct parameter names.
    kwargs_correct = {
        "method": "PUT",
        "headers": {"Authorization": "Bearer mytoken"},
        "json": {"update_key": "new_value"} 
    }

    http_cfg = HTTPCrawlerConfig.from_kwargs(kwargs_correct)
    
    print("HTTPCrawlerConfig created from_kwargs:")
    print(f"  Method: {http_cfg.method}")
    print(f"  Headers: {http_cfg.headers}")
    print(f"  JSON Payload: {http_cfg.json}")

    assert http_cfg.method == "PUT"
    assert http_cfg.headers["Authorization"] == "Bearer mytoken"
    assert http_cfg.json["update_key"] == "new_value"

if __name__ == "__main__":
    asyncio.run(httpcrawlerconfig_from_kwargs())
```

---
### 5.8. Example: Converting `HTTPCrawlerConfig` to a dictionary using `to_dict()`.

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig

async def httpcrawlerconfig_to_dict():
    http_cfg = HTTPCrawlerConfig(
        method="DELETE",
        headers={"X-Request-ID": "123xyz"},
        follow_redirects=False
    )
    config_dict = http_cfg.to_dict()

    print("HTTPCrawlerConfig instance:")
    print(f"  Original method: {http_cfg.method}")
    
    print("\nConverted to dictionary:")
    print(json.dumps(config_dict, indent=2))
    
    assert config_dict["method"] == "DELETE"
    assert config_dict["headers"]["X-Request-ID"] == "123xyz"
    assert config_dict["follow_redirects"] is False

if __name__ == "__main__":
    asyncio.run(httpcrawlerconfig_to_dict())
```

---
### 5.9. Example: Cloning `HTTPCrawlerConfig` and changing the HTTP method using `clone()`.

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig

async def httpcrawlerconfig_clone_modify():
    original_cfg = HTTPCrawlerConfig(method="GET", verify_ssl=True)
    print(f"Original Config: method={original_cfg.method}, verify_ssl={original_cfg.verify_ssl}")

    cloned_cfg = original_cfg.clone(method="PATCH", verify_ssl=False)
    print(f"Cloned Config: method={cloned_cfg.method}, verify_ssl={cloned_cfg.verify_ssl}")

    assert original_cfg.method == "GET"
    assert cloned_cfg.method == "PATCH"
    assert cloned_cfg.verify_ssl is False
    assert original_cfg.verify_ssl is True # Original unchanged

if __name__ == "__main__":
    asyncio.run(httpcrawlerconfig_clone_modify())
```

---
### 5.10. Example: Serializing `HTTPCrawlerConfig` using `dump()`.

```python
import asyncio
import json
from crawl4ai import HTTPCrawlerConfig

async def httpcrawlerconfig_dump():
    http_cfg = HTTPCrawlerConfig(
        method="OPTIONS",
        headers={"Origin": "https://example.com"},
        data={"ping": "true"}
    )
    
    dumped_dict = http_cfg.dump()

    print("Dumped HTTPCrawlerConfig (JSON compatible):")
    print(json.dumps(dumped_dict, indent=2))
    
    assert dumped_dict["type"] == "HTTPCrawlerConfig"
    assert dumped_dict["params"]["method"] == "OPTIONS"
    assert dumped_dict["params"]["data"]["ping"] == "true"

if __name__ == "__main__":
    asyncio.run(httpcrawlerconfig_dump())
```

---
### 5.11. Example: Deserializing `HTTPCrawlerConfig` using `load()`.

```python
import asyncio
from crawl4ai import HTTPCrawlerConfig

async def httpcrawlerconfig_load():
    serialized_data = {
        "type": "HTTPCrawlerConfig",
        "params": {
            "method": "HEAD",
            "headers": {"Cache-Control": "no-cache"},
            "follow_redirects": False
        }
    }
    
    loaded_cfg = HTTPCrawlerConfig.load(serialized_data)
    
    print("Loaded HTTPCrawlerConfig from dictionary:")
    print(f"  Method: {loaded_cfg.method}")
    print(f"  Headers: {loaded_cfg.headers}")
    print(f"  Follow Redirects: {loaded_cfg.follow_redirects}")

    assert isinstance(loaded_cfg, HTTPCrawlerConfig)
    assert loaded_cfg.method == "HEAD"
    assert loaded_cfg.headers["Cache-Control"] == "no-cache"
    assert loaded_cfg.follow_redirects is False

if __name__ == "__main__":
    asyncio.run(httpcrawlerconfig_load())
```

---
## 6. `CrawlerRunConfig` Examples

### 6.1. Basic Initialization

#### 6.1.1. Example: Default initialization of `CrawlerRunConfig`.
Creates a `CrawlerRunConfig` with all default values. The `url` will need to be provided when calling `arun`.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler

async def default_crawler_run_config():
    run_cfg = CrawlerRunConfig() # No URL specified here
    print(f"Default CrawlerRunConfig: {run_cfg.to_dict(exclude_none=True)}")
    assert run_cfg.url is None # URL must be passed to arun if not set here

    # Example of using it (requires URL in arun)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com", config=run_cfg)
        if result.success:
            print(f"Crawled example.com with default run config. Markdown length: {len(result.markdown.raw_markdown)}")

if __name__ == "__main__":
    asyncio.run(default_crawler_run_config())
```

---
#### 6.1.2. Example: Specifying the target `url` directly within `CrawlerRunConfig`.
The `url` can be part of the config object itself.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler

async def url_in_crawler_run_config():
    run_cfg_with_url = CrawlerRunConfig(url="https://example.org")
    print(f"CrawlerRunConfig with URL: {run_cfg_with_url.to_dict(exclude_none=True)}")
    assert run_cfg_with_url.url == "https://example.org"

    # Example of using it (arun will use the URL from config)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg_with_url) # No URL needed here
        if result.success:
            print(f"Crawled {result.url} using URL from config. Markdown length: {len(result.markdown.raw_markdown)}")

if __name__ == "__main__":
    asyncio.run(url_in_crawler_run_config())
```

---
### 6.2. Content Processing & Extraction

#### 6.2.1. Example: Adjusting `word_count_threshold` to control content block filtering.
Lower threshold means more (potentially shorter) blocks are kept.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def word_count_threshold_example():
    # Default is 200, let's try a much lower one
    run_cfg_low_wct = CrawlerRunConfig(
        url="https://news.ycombinator.com", 
        word_count_threshold=10, # Keep blocks with at least 10 words
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result_low = await crawler.arun(config=run_cfg_low_wct)
        if result_low.success:
            print(f"Markdown length with WCT=10: {len(result_low.markdown.raw_markdown)}")

            run_cfg_high_wct = CrawlerRunConfig(
                url="https://news.ycombinator.com",
                word_count_threshold=100, # Keep blocks with at least 100 words
                cache_mode=CacheMode.BYPASS
            )
            result_high = await crawler.arun(config=run_cfg_high_wct)
            if result_high.success:
                print(f"Markdown length with WCT=100: {len(result_high.markdown.raw_markdown)}")
                # Expect result_low.markdown to be longer or include more diverse small blocks
                assert len(result_low.markdown.raw_markdown) >= len(result_high.markdown.raw_markdown)
            else:
                print(f"Crawl with high WCT failed: {result_high.error_message}")
        else:
            print(f"Crawl with low WCT failed: {result_low.error_message}")

if __name__ == "__main__":
    asyncio.run(word_count_threshold_example())
```

---
#### 6.2.2. Example: Integrating a custom `extraction_strategy` (e.g., `NoExtractionStrategy`).
`NoExtractionStrategy` skips structured data extraction, only providing HTML/Markdown.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import NoExtractionStrategy

async def no_extraction_strategy_example():
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        extraction_strategy=NoExtractionStrategy(),
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url} with NoExtractionStrategy.")
            print(f"Extracted content: {result.extracted_content}") # Should be None or empty
            assert result.extracted_content is None or result.extracted_content == "[]" # Default is "[]" from NoExtraction
            print(f"Markdown content (first 100 chars): {result.markdown.raw_markdown[:100]}")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(no_extraction_strategy_example())
```

---
#### 6.2.3. Example: Using `RegExChunking` as the `chunking_strategy`.
Splits content based on regular expressions, useful before passing to some extraction strategies.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode
from crawl4ai.chunking_strategy import RegExChunking
# For LLMExtractionStrategy to show effect of chunking
from crawl4ai.extraction_strategy import LLMExtractionStrategy 
from crawl4ai import LLMConfig
import os

async def regex_chunking_example():
    # This example is more meaningful if combined with an extraction strategy
    # that processes chunks, like LLMExtractionStrategy.

    # Define a schema for LLM extraction
    schema = {"key_topics": "List the main topics discussed in this text."}
    llm_config_test = LLMConfig(
        provider="openai/gpt-4o-mini", 
        api_token=os.getenv("OPENAI_API_KEY_PLACEHOLDER", "YOUR_API_KEY")
    )
    
    # Chunk by paragraphs (approximate regex)
    regex_chunker = RegExChunking(patterns=[r"\n\s*\n"]) # Split on blank lines

    # If OPENAI_API_KEY_PLACEHOLDER is set to a real key, this test will make an API call.
    if llm_config_test.api_token == "YOUR_API_KEY":
        print("Skipping RegExChunking with LLM example due to missing OpenAI API key.")
        extraction_strat = None
    else:
        extraction_strat = LLMExtractionStrategy(
            llm_config=llm_config_test,
            schema=schema,
            # Note: The chunking_strategy is applied *before* LLM extraction if the LLM strategy expects chunks.
            # However, LLMExtractionStrategy itself handles chunking internally if content is too long.
            # To demonstrate RegExChunking independently, one might process its output directly.
            # For this example, we'll let LLMExtractionStrategy use it.
        )


    run_cfg = CrawlerRunConfig(
        url="https://en.wikipedia.org/wiki/Python_(programming_language)",
        chunking_strategy=regex_chunker, # This will be used by LLMExtractionStrategy if it's configured to take pre-chunked input
        extraction_strategy=extraction_strat,
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=50 # Get more content for chunking
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url}.")
            if result.extracted_content:
                print(f"Extracted content (potentially from chunks): {result.extracted_content[:500]}...")
            else:
                print("No structured content extracted (or API key missing). Markdown was still generated from chunked/full content.")
            print(f"Markdown (first 300 chars): {result.markdown.raw_markdown[:300]}")
            # To truly verify RegExChunking effect, one would need to inspect how LLMExtractionStrategy uses it,
            # or use a custom strategy that explicitly consumes `crawler_run_config.chunking_strategy.chunk(content)`.
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(regex_chunking_example())
```

---
#### 6.2.4. Example: Configuring `DefaultMarkdownGenerator` for `markdown_generator`.
Allows customization of how Markdown is generated (e.g., with/without citations, different content source).

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def custom_markdown_generator_example():
    # Generate Markdown without citations
    md_gen_no_citations = DefaultMarkdownGenerator(
        options={"citations": False} # html2text option
    )
    run_cfg_no_cite = CrawlerRunConfig(
        url="https://example.com",
        markdown_generator=md_gen_no_citations,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        result_no_cite = await crawler.arun(config=run_cfg_no_cite)
        if result_no_cite.success:
            print("--- Markdown without Citations (first 300 chars) ---")
            print(result_no_cite.markdown.raw_markdown[:300])
            # DefaultMarkdownGenerator produces raw_markdown and markdown_with_citations
            # We expect raw_markdown to be the one without reference style links.
            assert "]: http" not in result_no_cite.markdown.raw_markdown # Heuristic check
        
        # Generate Markdown from raw HTML instead of cleaned HTML
        md_gen_from_raw = DefaultMarkdownGenerator(content_source="raw_html")
        run_cfg_raw_html = CrawlerRunConfig(
             url="https://example.com",
             markdown_generator=md_gen_from_raw,
             cache_mode=CacheMode.BYPASS
        )
        result_raw = await crawler.arun(config=run_cfg_raw_html)
        if result_raw.success:
            print("\n--- Markdown from Raw HTML (first 300 chars) ---")
            print(result_raw.markdown.raw_markdown[:300])
            # This might be much noisier than from cleaned_html
            
if __name__ == "__main__":
    asyncio.run(custom_markdown_generator_example())
```

---
#### 6.2.5. Example: Enabling `only_text=True` for text-only extraction from HTML.
Strips all HTML tags, leaving only the text content.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def only_text_example():
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        only_text=True,
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url} with only_text=True.")
            print(f"Cleaned HTML (should be just text): {result.cleaned_html[:300]}")
            assert "<" not in result.cleaned_html[:10] # Heuristic: no HTML tags at start
            print(f"Markdown (should be similar to cleaned_html): {result.markdown.raw_markdown[:300]}")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(only_text_example())
```

---
#### 6.2.6. Example: Using `css_selector` to focus HTML processing on a specific part of the page.
The `cleaned_html` (and thus default Markdown) will only contain content from the matched selector.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def css_selector_focus_example():
    # On example.com, let's try to get only the content within the first <p> tag inside <div>
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        css_selector="div > p:first-of-type", # Selects the first paragraph in the main div
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url}, focusing on 'div > p:first-of-type'.")
            print(f"Cleaned HTML: {result.cleaned_html}")
            # Expected: "This domain is for use in illustrative examples in documents..."
            assert "illustrative examples" in result.cleaned_html
            assert "More information..." not in result.cleaned_html # Content from other <p>
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(css_selector_focus_example())
```

---
#### 6.2.7. Example: Specifying multiple `target_elements` for focused Markdown generation.
Markdown and structured extraction will focus on these elements, but other page data (links, media) is still gathered from the whole page.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def target_elements_example():
    # On example.com, target the <h1> and the link <a>
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        target_elements=["h1", "div > p > a"], # Target heading and the "More information" link
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url} with target_elements=['h1', 'div > p > a'].")
            print(f"Generated Markdown (focused on targets):\n{result.markdown.raw_markdown}")
            assert "Example Domain" in result.markdown.raw_markdown
            assert "More information..." in result.markdown.raw_markdown
            # The first paragraph's text should NOT be in the markdown if not targeted
            assert "illustrative examples" not in result.markdown.raw_markdown

            # Check if all links from the page are still collected (they should be)
            print(f"\nTotal internal links found on page: {len(result.links.get('internal', []))}")
            assert len(result.links.get("internal", [])) > 0 
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(target_elements_example())
```

---
#### 6.2.8. Example: Excluding specific HTML tags (e.g., `nav`, `footer`) using `excluded_tags`.
These tags and their content will be removed from `cleaned_html`.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def excluded_tags_example():
    # Let's try to exclude <p> tags from example.com
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        excluded_tags=["p"],
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url} excluding <p> tags.")
            print(f"Cleaned HTML (should not contain <p>):\n{result.cleaned_html}")
            assert "<p>" not in result.cleaned_html.lower()
            assert "illustrative examples" not in result.cleaned_html # This text is in a <p>
            assert "Example Domain" in result.cleaned_html # The <h1> should remain
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(excluded_tags_example())
```

---
#### 6.2.9. Example: Excluding elements based on a CSS selector using `excluded_selector`.
Removes elements matching the CSS selector from `cleaned_html`.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def excluded_selector_example():
    # Exclude the link "More information..." on example.com which is in a <p> inside a <div>
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        excluded_selector="div > p > a", # CSS selector for the link
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url} excluding 'div > p > a'.")
            print(f"Cleaned HTML:\n{result.cleaned_html}")
            assert "More information..." not in result.cleaned_html
            assert "illustrative examples" in result.cleaned_html # The rest of the <p> should be there
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(excluded_selector_example())
```

---
#### 6.2.10. Example: Preserving `data-*` attributes during HTML cleaning with `keep_data_attributes=True`.
By default, many attributes are stripped. This keeps `data-*` attributes.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def keep_data_attributes_example():
    sample_html_with_data_attr = """
    <html><body>
        <div data-testid="main-content" data-analytics-id="section1">
            <p>Some important text.</p>
            <span data-custom-info="extra detail">More text.</span>
        </div>
    </body></html>
    """
    run_cfg = CrawlerRunConfig(
        url=f"raw://{sample_html_with_data_attr}",
        keep_data_attributes=True,
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled content with keep_data_attributes=True.")
            print(f"Cleaned HTML:\n{result.cleaned_html}")
            assert 'data-testid="main-content"' in result.cleaned_html
            assert 'data-analytics-id="section1"' in result.cleaned_html
            assert 'data-custom-info="extra detail"' in result.cleaned_html
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(keep_data_attributes_example())
```

---
#### 6.2.11. Example: Specifying a custom list of HTML attributes to preserve using `keep_attrs`.
Allows fine-grained control over which attributes are kept.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def keep_specific_attributes_example():
    sample_html_with_attrs = """
    <html><body>
        <article id="article-123" class="blog-post important" style="color:blue;" title="My Article">
            <h1>Title</h1>
            <a href="/path" data-linkid="789">Link</a>
        </article>
    </body></html>
    """
    # We want to keep 'id', 'class' from the article, and 'href' from the link
    # and also data-linkid
    run_cfg = CrawlerRunConfig(
        url=f"raw://{sample_html_with_attrs}",
        keep_attrs=["id", "class", "href", "data-linkid"], 
        # keep_data_attributes=False (default), so only "data-linkid" if explicitly listed here.
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled content with keep_attrs=['id', 'class', 'href', 'data-linkid'].")
            cleaned_html = result.cleaned_html
            print(f"Cleaned HTML:\n{cleaned_html}")
            assert 'id="article-123"' in cleaned_html
            assert 'class="blog-post important"' in cleaned_html # Classes are usually kept by default cleaner for semantic reasons
            assert 'href="/path"' in cleaned_html
            assert 'data-linkid="789"' in cleaned_html
            assert 'style="color:blue;"' not in cleaned_html # style should be removed
            assert 'title="My Article"' not in cleaned_html # title should be removed
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(keep_specific_attributes_example())
```

---
#### 6.2.12. Example: Removing all `<form>` elements from HTML using `remove_forms=True`.
Useful for cleaning up pages before text extraction if forms are noisy.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def remove_forms_example():
    html_with_form = """
    <html><body>
        <p>Some text before form.</p>
        <form action="/submit">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name"><br>
            <input type="submit" value="Submit">
        </form>
        <p>Some text after form.</p>
    </body></html>
    """
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_with_form}",
        remove_forms=True,
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled content with remove_forms=True.")
            cleaned_html = result.cleaned_html
            print(f"Cleaned HTML (should not contain <form>):\n{cleaned_html}")
            assert "<form" not in cleaned_html.lower()
            assert "Some text before form." in cleaned_html
            assert "Some text after form." in cleaned_html
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(remove_forms_example())
```

---
#### 6.2.13. Example: Enabling HTML prettifying of the cleaned HTML output with `prettify=True`.
Formats the `cleaned_html` to be more human-readable.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def prettify_html_example():
    # A simple, unformatted HTML string
    raw_html = "<html><body><div><p>Hello</p><p>World</p></div></body></html>"
    run_cfg = CrawlerRunConfig(
        url=f"raw://{raw_html}",
        prettify=True,
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled content with prettify=True.")
            cleaned_html = result.cleaned_html
            print(f"Prettified Cleaned HTML:\n{cleaned_html}")
            # Prettified HTML usually has more newlines and indentation
            assert cleaned_html.count('\n') > 3 # Heuristic check for newlines
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(prettify_html_example())
```

---
#### 6.2.14. Example: Changing the HTML parser to "html.parser" using `parser_type`.
The default is "lxml". "html.parser" is Python's built-in parser.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode

async def change_parser_type_example():
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        parser_type="html.parser", # Use Python's built-in parser
        cache_mode=CacheMode.BYPASS
    )
    
    print(f"Using parser_type: {run_cfg.parser_type}")
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url} using 'html.parser'.")
            # Behavior should be largely similar for well-formed HTML
            assert "Example Domain" in result.cleaned_html
        else:
            print(f"Crawl failed with 'html.parser': {result.error_message}")

if __name__ == "__main__":
    asyncio.run(change_parser_type_example())
```

---
#### 6.2.15. Example: Specifying a custom `scraping_strategy` (e.g., `PDFScrapingStrategy` - if applicable).
Demonstrates using a different strategy for content scraping, here for PDF files.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode
from crawl4ai.content_scraping_strategy import WebScrapingStrategy # Default
# For PDF, we'd import PDF相关的strategies
from crawl4ai.processors.pdf import PDFCrawlerStrategy, PDFScrapingStrategy
# Note: PDFScrapingStrategy is typically used by PDFCrawlerStrategy, not directly by AsyncWebCrawler for a URL.
# This example will show how to set it conceptually if a strategy took it.
# A more realistic PDF example uses PDFCrawlerStrategy directly.

async def custom_scraping_strategy_conceptual():
    # This is conceptual for CrawlerRunConfig.scraping_strategy if a strategy used it.
    # In practice, for PDF, you'd use PDFCrawlerStrategy.
    
    # Conceptual: if AsyncWebCrawler could directly use PDFScrapingStrategy via config
    # (It doesn't by default for generic URLs; PDF processing has its own flow)
    # pdf_scraping_strat = PDFScrapingStrategy() 
    # run_cfg_pdf = CrawlerRunConfig(
    #     url="file:///path/to/your/document.pdf", # Example local PDF
    #     scraping_strategy=pdf_scraping_strat,
    #     cache_mode=CacheMode.BYPASS
    # )
    # print(f"Conceptual CrawlerRunConfig with PDFScrapingStrategy: {run_cfg_pdf.scraping_strategy}")


    # More realistic usage for PDF:
    # Use PDFCrawlerStrategy directly if you know it's a PDF
    pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" # A sample PDF
    
    # We need a PDF-specific crawler strategy, not just scraping_strategy in CrawlerRunConfig
    # This example demonstrates where scraping_strategy *would* go if a generic URL crawler used it.
    # The PDF files provided show PDFCrawlerStrategy and PDFContentScrapingStrategy.
    # PDFContentScrapingStrategy is the equivalent scraper for PDFs.
    
    # Correct way for PDF:
    pdf_crawler_strategy = PDFCrawlerStrategy()
    pdf_scraping_config = PDFScrapingStrategy() # This is the content scraper for PDFs
    
    run_config_for_pdf = CrawlerRunConfig(
        url=pdf_url,
        scraping_strategy=pdf_scraping_config, # This is what the PDFCrawlerStrategy would use internally
        cache_mode=CacheMode.BYPASS
    )

    print(f"Using PDFScrapingStrategy conceptually in CrawlerRunConfig for a PDF URL: {pdf_url}")
    
    # The AsyncWebCrawler's default Playwright strategy won't use run_config.scraping_strategy.
    # We need to pass the PDFCrawlerStrategy to AsyncWebCrawler itself.
    async with AsyncWebCrawler(crawler_strategy=pdf_crawler_strategy) as crawler:
        # The run_config's scraping_strategy will be passed to pdf_crawler_strategy.crawl()
        # if pdf_crawler_strategy.crawl() is designed to accept it via **kwargs
        # and then pass it to its internal scraper.
        # The provided PDF __init__.py passes the 'save_images_locally', 'extract_images' etc.
        # directly from CrawlerRunConfig to the PDFContentScrapingStrategy.
        
        # For this example, let's adjust CrawlerRunConfig to pass params PDFContentScrapingStrategy expects:
        pdf_specific_run_config = CrawlerRunConfig(
            url=pdf_url,
            extract_images=True, # A param PDFContentScrapingStrategy uses
            cache_mode=CacheMode.BYPASS
        )

        result = await crawler.arun(config=pdf_specific_run_config)
        if result.success:
            print(f"Successfully processed PDF {result.url}.")
            print(f"Markdown content (first 300 chars):\n{result.markdown.raw_markdown[:300]}")
            if result.media and result.media.get("images"):
                print(f"Extracted {len(result.media['images'])} images from PDF.")
        else:
            print(f"Failed to process PDF: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(custom_scraping_strategy_conceptual())
```

---
### 6.3. Proxy Configuration for a Specific Run

#### 6.3.1. Example: Providing a `ProxyConfig` object to `CrawlerRunConfig.proxy_config`.
This overrides any proxy set in `BrowserConfig` for this specific `arun` call.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, ProxyConfig

async def run_specific_proxy():
    # Browser might have a default proxy or no proxy
    browser_cfg = BrowserConfig(headless=True, verbose=True) 
    
    # Proxy for this specific run (non-functional placeholder)
    run_proxy = ProxyConfig(server="http://runspecificproxy.example.com:8888")
    
    run_cfg_with_proxy = CrawlerRunConfig(
        url="https://httpbin.org/ip", # Shows requester IP
        proxy_config=run_proxy
    )
    print(f"CrawlerRunConfig with specific proxy: {run_cfg_with_proxy.proxy_config.to_dict()}") # type: ignore

    print("NOTE: This example will likely fail or show your direct IP if the placeholder proxy is not replaced.")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg_with_proxy)
        if result.success:
            print(f"Crawled {result.url} using run-specific proxy.")
            print(f"Response (should show proxy IP): {result.html}")
        else:
            print(f"Crawl with run-specific proxy failed: {result.error_message}")

if __name__ == "__main__":
    # asyncio.run(run_specific_proxy())
    print("Skipping run_specific_proxy example as it requires a live proxy server.")
```

---
#### 6.3.2. Example: Using `RoundRobinProxyStrategy` for `proxy_rotation_strategy`.
Demonstrates setting up a proxy rotation strategy for `arun_many` or multiple `arun` calls.

```python
import asyncio
from crawl4ai import (
    AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, 
    ProxyConfig, RoundRobinProxyStrategy
)

async def proxy_rotation_example():
    # List of proxies (non-functional placeholders)
    proxies = [
        ProxyConfig(server="http://proxy1.example.com:8000"),
        ProxyConfig(server="http://proxy2.example.com:8001", username="user2", password="p2"),
        ProxyConfig(server="http://proxy3.example.com:8002"),
    ]
    
    proxy_rotator = RoundRobinProxyStrategy(proxies=proxies)
    
    # Browser config (no proxy set here, it will be set per run)
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    urls_to_crawl = [
        "https://httpbin.org/ip?site=1",
        "https://httpbin.org/ip?site=2",
        "https://httpbin.org/ip?site=3",
        "https://httpbin.org/ip?site=4" # Will cycle back to proxy1
    ]

    print("NOTE: This example will likely fail or show direct IPs if placeholder proxies are not replaced.")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for i, url in enumerate(urls_to_crawl):
            # Get next proxy from strategy and create a run_config with it
            # The proxy_rotation_strategy itself is passed to CrawlerRunConfig
            run_cfg = CrawlerRunConfig(
                url=url,
                proxy_rotation_strategy=proxy_rotator # The crawler will call get_next_proxy()
            )
            
            # The `arun` method will internally use proxy_rotation_strategy.get_next_proxy()
            # to set the proxy_config for the actual call if proxy_rotation_strategy is present.
            # The proxy_config will be set inside the AsyncPlaywrightCrawlerStrategy.
            
            print(f"\n--- Crawling {url} (Attempt {i+1}) ---")
            # current_proxy_for_run = await proxy_rotator.get_next_proxy() # This is what arun would do
            # print(f"Expected proxy for this run: {current_proxy_for_run.server if current_proxy_for_run else 'None'}")

            result = await crawler.arun(config=run_cfg)
            
            if result.success:
                print(f"Crawled {result.url} successfully.")
                print(f"Response (should show IP of proxy {i % len(proxies) + 1}): {result.html}")
            else:
                print(f"Crawl for {result.url} failed: {result.error_message}")
            
            await asyncio.sleep(0.5) # Small delay between requests

if __name__ == "__main__":
    # asyncio.run(proxy_rotation_example())
    print("Skipping proxy_rotation_example as it requires live proxy servers.")
```

---
### 6.4. Localization and Geolocation for a Specific Run

#### 6.4.1. Example: Setting browser `locale` (e.g., "es-ES") for the crawl.
This can affect language of the page, date/number formats.

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def set_browser_locale_for_run():
    browser_cfg = BrowserConfig(headless=True, verbose=True) # Default locale (usually en-US)
    
    run_cfg_spanish = CrawlerRunConfig(
        url="https://httpbin.org/headers", # This endpoint shows request headers
        locale="es-ES" # Spanish (Spain)
    )
    print(f"CrawlerRunConfig with locale: {run_cfg_spanish.locale}")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg_spanish)
        if result.success:
            print(f"Crawled {result.url} with locale 'es-ES'.")
            response_data = json.loads(result.html)
            accept_language_header = response_data.get("headers", {}).get("Accept-Language")
            print(f"Accept-Language header sent: {accept_language_header}")
            # Playwright typically sets Accept-Language based on locale
            assert accept_language_header and "es-ES" in accept_language_header.split(',')[0]
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(set_browser_locale_for_run())
```

---
#### 6.4.2. Example: Setting browser `timezone_id` (e.g., "Europe/Madrid") for the crawl.
Affects JavaScript `Date` objects and potentially server-side logic based on timezone.

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def set_browser_timezone_for_run():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    run_cfg_madrid_tz = CrawlerRunConfig(
        url="https://httpbin.org/anything", # We'll execute JS to get timezone
        timezone_id="Europe/Madrid",
        js_code="JSON.stringify({offset: new Date().getTimezoneOffset(), localeString: new Date().toLocaleString('en-US', {timeZoneName:'short'})})"
    )
    print(f"CrawlerRunConfig with timezone_id: {run_cfg_madrid_tz.timezone_id}")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg_madrid_tz)
        if result.success and result.js_execution_result:
            print(f"Crawled {result.url} with timezone 'Europe/Madrid'.")
            js_result = result.js_execution_result
            print(f"JS Date info: {js_result}")
            # For Madrid (CET/CEST), offset is -60 (CET) or -120 (CEST) from UTC.
            # localeString might show 'CET' or 'CEST'.
            # This is a heuristic check.
            assert js_result.get("offset") in [-60, -120] or "CET" in js_result.get("localeString", "") or "CEST" in js_result.get("localeString", "")
        elif not result.js_execution_result:
            print(f"JS execution did not return a result for timezone check.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(set_browser_timezone_for_run())
```

---
#### 6.4.3. Example: Providing a `GeolocationConfig` object for the crawl.
Simulates a specific GPS location for the browser.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, GeolocationConfig

async def set_geolocation_for_run():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # Sydney, Australia
    sydney_geo = GeolocationConfig(latitude=-33.8688, longitude=151.2093, accuracy=50.0)
    
    run_cfg_sydney = CrawlerRunConfig(
        url="https://www.gps-coordinates.net/my-location", # This site shows your detected location
        geolocation=sydney_geo,
        wait_for="css=#address", # Wait for the address to be populated
        page_timeout=20000, # Give it time
        verbose=True
    )
    print(f"CrawlerRunConfig with geolocation: {run_cfg_sydney.geolocation.to_dict()}")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"Attempting to crawl {run_cfg_sydney.url} simulating Sydney location.")
        result = await crawler.arun(config=run_cfg_sydney)
        if result.success:
            print(f"Successfully crawled {result.url} with simulated Sydney location.")
            # Check if the page content reflects Sydney
            # print(f"Page HTML (first 1000 chars):\n{result.html[:1000]}")
            if "Sydney" in result.html or "Australia" in result.html:
                 print("SUCCESS: Sydney or Australia mentioned in page, geolocation likely worked.")
            else:
                 print("Geolocation effect not immediately obvious in HTML. Manual check of site behavior needed.")
        else:
            print(f"Crawl failed: {result.error_message}")
            print("This might be due to the test site's behavior or if permissions for geolocation were not granted by the browser context setup.")

if __name__ == "__main__":
    asyncio.run(set_geolocation_for_run())
```

---
### 6.5. Caching Behavior with `CacheMode`

#### 6.5.1. Example: Enabling full read/write caching with `cache_mode=CacheMode.ENABLED`.
Reads from cache if available, otherwise fetches and writes to cache. (Default if no mode is set by user and cache is available).

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from crawl4ai.utils import get_cache_dir # Helper to find cache location

async def cache_enabled_example():
    # Ensure cache dir exists for this test
    cache_dir = get_cache_dir()
    print(f"Using cache directory: {cache_dir}")

    run_cfg = CrawlerRunConfig(
        url="https://example.com", # A static page, good for caching demo
        cache_mode=CacheMode.ENABLED
    )
    
    browser_cfg = BrowserConfig(headless=True, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # First run: Should fetch and cache
        print("\n--- First run (CacheMode.ENABLED) ---")
        start_time1 = time.perf_counter()
        result1 = await crawler.arun(config=run_cfg)
        duration1 = time.perf_counter() - start_time1
        if result1.success:
            print(f"First run successful. Duration: {duration1:.2f}s. Cached: {result1.metadata.get('cached', False)}")
            assert not result1.metadata.get('cached', False) # Should not be cached on first run (unless already in DB)
        else:
            print(f"First run failed: {result1.error_message}")
            return

        # Second run: Should read from cache
        print("\n--- Second run (CacheMode.ENABLED) ---")
        start_time2 = time.perf_counter()
        result2 = await crawler.arun(config=run_cfg) # Same URL and config
        duration2 = time.perf_counter() - start_time2
        if result2.success:
            print(f"Second run successful. Duration: {duration2:.2f}s. Cached: {result2.metadata.get('cached', False)}")
            assert result2.metadata.get('cached', True) # Should be cached now
            assert duration2 < duration1 # Cached read should be faster
            assert result1.markdown.raw_markdown == result2.markdown.raw_markdown
        else:
            print(f"Second run failed: {result2.error_message}")

if __name__ == "__main__":
    asyncio.run(cache_enabled_example())
```

---
#### 6.5.2. Example: Bypassing the cache for a single run with `cache_mode=CacheMode.BYPASS`.
Ignores existing cache and fetches fresh data, but still writes the new data to cache.

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig

async def cache_bypass_example():
    run_cfg_cache_first = CrawlerRunConfig(
        url="https://example.com/cache_test_page_bypass", 
        cache_mode=CacheMode.ENABLED # First, ensure it's cached
    )
    run_cfg_bypass = CrawlerRunConfig(
        url="https://example.com/cache_test_page_bypass", # Same URL
        cache_mode=CacheMode.BYPASS # This run will bypass read but still write
    )
    browser_cfg = BrowserConfig(headless=True, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # First run: Populate cache
        print("\n--- First run (CacheMode.ENABLED to populate cache) ---")
        await crawler.arun(config=run_cfg_cache_first)
        print("Cache potentially populated.")

        # Second run: Bypass cache (should fetch fresh, then write to cache)
        print("\n--- Second run (CacheMode.BYPASS) ---")
        start_time_bypass = time.perf_counter()
        result_bypass = await crawler.arun(config=run_cfg_bypass)
        duration_bypass = time.perf_counter() - start_time_bypass
        if result_bypass.success:
            print(f"Bypass run successful. Duration: {duration_bypass:.2f}s. Cached flag: {result_bypass.metadata.get('cached', False)}")
            # 'cached' flag is True if data was retrieved from cache. For BYPASS, it should be False for the read part.
            assert not result_bypass.metadata.get('cached', False) 
        else:
            print(f"Bypass run failed: {result_bypass.error_message}")
            return

        # Third run: Normal enabled mode, should now read the data written by BYPASS run
        print("\n--- Third run (CacheMode.ENABLED, after BYPASS) ---")
        start_time_cached = time.perf_counter()
        result_cached_after_bypass = await crawler.arun(config=run_cfg_cache_first) # Use ENABLED config
        duration_cached = time.perf_counter() - start_time_cached
        if result_cached_after_bypass.success:
            print(f"Cached run successful. Duration: {duration_cached:.2f}s. Cached flag: {result_cached_after_bypass.metadata.get('cached', False)}")
            assert result_cached_after_bypass.metadata.get('cached', True)
            assert duration_cached < duration_bypass
        else:
            print(f"Cached run after bypass failed: {result_cached_after_bypass.error_message}")


if __name__ == "__main__":
    asyncio.run(cache_bypass_example())
```

---
#### 6.5.3. Example: Disabling all caching operations with `cache_mode=CacheMode.DISABLED`.
Neither reads from nor writes to the cache.

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig

async def cache_disabled_example():
    run_cfg = CrawlerRunConfig(
        url="https://example.com/cache_test_page_disabled",
        cache_mode=CacheMode.DISABLED
    )
    browser_cfg = BrowserConfig(headless=True, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # First run
        print("\n--- First run (CacheMode.DISABLED) ---")
        start_time1 = time.perf_counter()
        result1 = await crawler.arun(config=run_cfg)
        duration1 = time.perf_counter() - start_time1
        if result1.success:
            print(f"First run successful. Duration: {duration1:.2f}s. Cached: {result1.metadata.get('cached', False)}")
            assert not result1.metadata.get('cached', False) # Should not be cached
        else:
            print(f"First run failed: {result1.error_message}")
            return

        # Second run: Should also fetch fresh as cache is disabled
        print("\n--- Second run (CacheMode.DISABLED) ---")
        start_time2 = time.perf_counter()
        result2 = await crawler.arun(config=run_cfg) # Same URL and config
        duration2 = time.perf_counter() - start_time2
        if result2.success:
            print(f"Second run successful. Duration: {duration2:.2f}s. Cached: {result2.metadata.get('cached', False)}")
            assert not result2.metadata.get('cached', False) # Still not cached
            # Durations might be similar as both are fresh fetches
            print(f"Durations: Run1={duration1:.2f}s, Run2={duration2:.2f}s")
        else:
            print(f"Second run failed: {result2.error_message}")

if __name__ == "__main__":
    asyncio.run(cache_disabled_example())
```

---
#### 6.5.4. Example: Configuring cache for read-only access with `cache_mode=CacheMode.READ_ONLY`.
Only reads from cache if data exists; does not write new data if fetched fresh.

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig, AsyncDBManager

async def cache_readonly_example():
    url_readonly = "https://example.com/cache_test_page_readonly"
    
    # Ensure the item is NOT in cache initially by using a unique URL or clearing
    # For this test, we'll first try to read (should fail to find in cache), then try to write (should not write)
    
    run_cfg_readonly = CrawlerRunConfig(url=url_readonly, cache_mode=CacheMode.READ_ONLY)
    run_cfg_enabled = CrawlerRunConfig(url=url_readonly, cache_mode=CacheMode.ENABLED) # To check if it was written
    
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    db_manager = AsyncDBManager() # For direct cache check

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Ensure item is not in cache
        await db_manager.adelete_url_cache(url_readonly)
        print(f"Ensured {url_readonly} is not in cache.")

        # First run: READ_ONLY mode, item not in cache. Should fetch fresh, NOT write.
        print("\n--- First run (CacheMode.READ_ONLY, item not in cache) ---")
        result_fetch = await crawler.arun(config=run_cfg_readonly)
        if result_fetch.success:
            print(f"READ_ONLY (fetch): Successful. Cached: {result_fetch.metadata.get('cached', False)}")
            assert not result_fetch.metadata.get('cached', False)
        else:
            print(f"READ_ONLY (fetch) failed: {result_fetch.error_message}")
            return

        # Check if it was written to cache (it shouldn't have been)
        cached_item_after_readonly = await db_manager.aget_cached_url(url_readonly)
        if cached_item_after_readonly is None:
            print("SUCCESS: Item was NOT written to cache after READ_ONLY fetch, as expected.")
        else:
            print("FAILURE: Item was unexpectedly written to cache after READ_ONLY fetch.")
            await db_manager.adelete_url_cache(url_readonly) # Clean for next step

        # Now, let's populate the cache using ENABLED mode
        print("\n--- Populating cache (CacheMode.ENABLED) ---")
        await crawler.arun(config=run_cfg_enabled)
        print("Cache populated.")

        # Second run: READ_ONLY mode, item IS in cache. Should read from cache.
        print("\n--- Second run (CacheMode.READ_ONLY, item IS in cache) ---")
        start_time_read = time.perf_counter()
        result_read_cache = await crawler.arun(config=run_cfg_readonly)
        duration_read = time.perf_counter() - start_time_read
        if result_read_cache.success:
            print(f"READ_ONLY (read cache): Successful. Duration: {duration_read:.2f}s. Cached: {result_read_cache.metadata.get('cached', False)}")
            assert result_read_cache.metadata.get('cached', True)
        else:
            print(f"READ_ONLY (read cache) failed: {result_read_cache.error_message}")
        
        # Clean up
        await db_manager.adelete_url_cache(url_readonly)


if __name__ == "__main__":
    asyncio.run(cache_readonly_example())
```

---
#### 6.5.5. Example: Configuring cache for write-only access with `cache_mode=CacheMode.WRITE_ONLY`.
Always fetches fresh data, but writes it to the cache. Does not read from cache even if data exists.

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig, AsyncDBManager

async def cache_writeonly_example():
    url_writeonly = "https://example.com/cache_test_page_writeonly"
    run_cfg_writeonly = CrawlerRunConfig(url=url_writeonly, cache_mode=CacheMode.WRITE_ONLY)
    run_cfg_enabled = CrawlerRunConfig(url=url_writeonly, cache_mode=CacheMode.ENABLED)
    
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    db_manager = AsyncDBManager()

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Ensure item is not in cache
        await db_manager.adelete_url_cache(url_writeonly)
        print(f"Ensured {url_writeonly} is not in cache.")

        # First run: WRITE_ONLY. Should fetch fresh AND write to cache.
        print("\n--- First run (CacheMode.WRITE_ONLY) ---")
        result_write1 = await crawler.arun(config=run_cfg_writeonly)
        if result_write1.success:
            print(f"WRITE_ONLY run 1: Successful. Cached flag: {result_write1.metadata.get('cached', False)}")
            assert not result_write1.metadata.get('cached', False) # Read part is skipped
        else:
            print(f"WRITE_ONLY run 1 failed: {result_write1.error_message}")
            return

        # Check if it was written
        cached_item_after_write1 = await db_manager.aget_cached_url(url_writeonly)
        if cached_item_after_write1:
            print("SUCCESS: Item was written to cache after first WRITE_ONLY run.")
        else:
            print("FAILURE: Item was NOT written to cache after first WRITE_ONLY run.")
            return

        # Second run: WRITE_ONLY again. Should still fetch fresh (not read cache), then overwrite cache.
        print("\n--- Second run (CacheMode.WRITE_ONLY, item is in cache) ---")
        # To verify it fetches fresh, we'd need a page that changes content, or compare timestamps.
        # For simplicity, we'll just confirm the behavior.
        start_time_write2 = time.perf_counter()
        result_write2 = await crawler.arun(config=run_cfg_writeonly)
        duration_write2 = time.perf_counter() - start_time_write2
        if result_write2.success:
            print(f"WRITE_ONLY run 2: Successful. Duration: {duration_write2:.2f}s. Cached flag: {result_write2.metadata.get('cached', False)}")
            assert not result_write2.metadata.get('cached', False)
        else:
            print(f"WRITE_ONLY run 2 failed: {result_write2.error_message}")
        
        # Clean up
        await db_manager.adelete_url_cache(url_writeonly)

if __name__ == "__main__":
    asyncio.run(cache_writeonly_example())
```

---
#### 6.5.6. Example: Showing modern equivalent for deprecated `bypass_cache=True` (uses `CacheMode.BYPASS`).
The `bypass_cache=True` flag in older versions is now `cache_mode=CacheMode.BYPASS`.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, CacheMode

async def deprecated_bypass_cache_equivalent():
    # Old way (would raise warning or error in newer versions if directly used as param)
    # run_cfg_old = CrawlerRunConfig(bypass_cache=True) 

    # New way
    run_cfg_new = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    
    print("Demonstrating CacheMode.BYPASS (equivalent to old bypass_cache=True):")
    print(f"  cache_mode: {run_cfg_new.cache_mode}")
    
    # Verify behavior (conceptual, actual test in CacheMode.BYPASS example)
    # - It will not read from cache.
    # - It will fetch fresh data.
    # - It will write the fetched data to cache.
    assert run_cfg_new.cache_mode == CacheMode.BYPASS
    print("This configuration means the crawler will ignore existing cache entries for reading but will update the cache with the new data.")

if __name__ == "__main__":
    asyncio.run(deprecated_bypass_cache_equivalent())
```

---
#### 6.5.7. Example: Showing modern equivalent for deprecated `disable_cache=True` (uses `CacheMode.DISABLED`).
The `disable_cache=True` flag in older versions is now `cache_mode=CacheMode.DISABLED`.

```python
import asyncio
from crawl4ai import CrawlerRunConfig, CacheMode

async def deprecated_disable_cache_equivalent():
    # Old way (would raise warning or error in newer versions if directly used as param)
    # run_cfg_old = CrawlerRunConfig(disable_cache=True)

    # New way
    run_cfg_new = CrawlerRunConfig(cache_mode=CacheMode.DISABLED)

    print("Demonstrating CacheMode.DISABLED (equivalent to old disable_cache=True):")
    print(f"  cache_mode: {run_cfg_new.cache_mode}")
    
    # Verify behavior (conceptual, actual test in CacheMode.DISABLED example)
    # - It will not read from cache.
    # - It will fetch fresh data.
    # - It will NOT write the fetched data to cache.
    assert run_cfg_new.cache_mode == CacheMode.DISABLED
    print("This configuration means the crawler will neither read from nor write to the cache.")

if __name__ == "__main__":
    asyncio.run(deprecated_disable_cache_equivalent())
```

---
### 6.6. Session Management and Shared Data

#### 6.6.1. Example: Using `session_id` to maintain a persistent browser context across multiple `arun` calls.
Allows subsequent `arun` calls to reuse the same browser page/tab and its state (cookies, localStorage, JS context).

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def session_id_example():
    my_session_id = "my_persistent_web_session_123"
    browser_cfg = BrowserConfig(headless=True, verbose=True) # Keep browser open across arun calls if session_id is used

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # First call: Visit a page, set a cookie via JS
        js_set_cookie = "document.cookie = 'session_test_cookie=hello_crawl4ai; path=/';"
        run_cfg1 = CrawlerRunConfig(
            url="https://httpbin.org/anything", # Initial page
            session_id=my_session_id,
            js_code=js_set_cookie
        )
        print(f"\n--- First call with session_id='{my_session_id}', setting cookie ---")
        result1 = await crawler.arun(config=run_cfg1)
        if result1.success:
            print(f"First call to {result1.url} successful.")
        else:
            print(f"First call failed: {result1.error_message}")
            return

        # Second call: Visit another page on the same domain, cookie should be sent
        run_cfg2 = CrawlerRunConfig(
            url="https://httpbin.org/cookies", # This page shows cookies
            session_id=my_session_id # Crucial: use the same session_id
        )
        print(f"\n--- Second call with session_id='{my_session_id}', checking cookie ---")
        result2 = await crawler.arun(config=run_cfg2)
        if result2.success:
            print(f"Second call to {result2.url} successful.")
            response_data = json.loads(result2.html)
            print(f"Cookies received by server: {response_data.get('cookies')}")
            assert "session_test_cookie" in response_data.get("cookies", {})
            assert response_data.get("cookies", {}).get("session_test_cookie") == "hello_crawl4ai"
            print("SUCCESS: Cookie persisted across calls within the same session_id!")
        else:
            print(f"Second call failed: {result2.error_message}")
        
        # Important: Clean up the session if you're done with it and it's not managed by use_persistent_context
        await crawler.crawler_strategy.kill_session(my_session_id)
        print(f"\nSession '{my_session_id}' explicitly killed.")


if __name__ == "__main__":
    asyncio.run(session_id_example())
```

---
#### 6.6.2. Example: Passing `shared_data` dictionary for use in custom hooks (hooks themselves are external to this component).
`shared_data` is a way to pass arbitrary data to and between custom hook functions if you've implemented them.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy # To attach hooks

async def shared_data_example():
    # Define a simple hook that accesses shared_data
    async def my_custom_before_goto_hook(page, context, url, shared_data, **kwargs):
        print(f"[HOOK - before_goto] Accessing shared_data: {shared_data}")
        shared_data["hook_modified_value"] = "value_set_by_hook"
        # This hook could, for example, conditionally set headers based on shared_data
        return page

    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # The strategy where hooks are attached
    crawler_strategy = AsyncPlaywrightCrawlerStrategy(config=browser_cfg)
    crawler_strategy.set_hook("before_goto", my_custom_before_goto_hook)
    
    initial_shared_data = {"user_id": 123, "task_type": "data_collection"}
    
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        shared_data=initial_shared_data.copy() # Pass a copy to avoid modification issues if reused
    )
    print(f"CrawlerRunConfig with initial shared_data: {run_cfg.shared_data}")

    async with AsyncWebCrawler(crawler_strategy=crawler_strategy) as crawler:
        print("\n--- Running crawl with shared_data and custom hook ---")
        result = await crawler.arun(config=run_cfg)
        
        if result.success:
            print(f"Crawl to {result.url} successful.")
            # Check if the hook modified the shared_data (if the hook logic does so)
            # The hook we defined modifies the dictionary passed to it.
            # The `run_cfg.shared_data` is the one passed, so it should be modified.
            print(f"Shared data after crawl (modified by hook): {run_cfg.shared_data}")
            assert run_cfg.shared_data["hook_modified_value"] == "value_set_by_hook"
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(shared_data_example())
```

---
### 6.7. Page Navigation, Waits, and Timing

#### 6.7.1. Example: Changing `wait_until` to "load" or "networkidle".
Controls when Playwright considers navigation complete. Default is "domcontentloaded".

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def wait_until_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    url_to_crawl = "https://example.com" # A simple, fast-loading page

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Test with "domcontentloaded" (default)
        run_cfg_dom = CrawlerRunConfig(url=url_to_crawl, wait_until="domcontentloaded")
        start_time_dom = time.perf_counter()
        await crawler.arun(config=run_cfg_dom)
        duration_dom = time.perf_counter() - start_time_dom
        print(f"Wait_until 'domcontentloaded' duration: {duration_dom:.2f}s")

        # Test with "load" (waits for all resources like images)
        run_cfg_load = CrawlerRunConfig(url=url_to_crawl, wait_until="load")
        start_time_load = time.perf_counter()
        await crawler.arun(config=run_cfg_load)
        duration_load = time.perf_counter() - start_time_load
        print(f"Wait_until 'load' duration: {duration_load:.2f}s")
        # For a simple page, 'load' might not be much longer than 'domcontentloaded'
        # but for image-heavy pages, it would be.

        # Test with "networkidle" (waits for network to be idle for 500ms)
        run_cfg_idle = CrawlerRunConfig(url=url_to_crawl, wait_until="networkidle")
        start_time_idle = time.perf_counter()
        await crawler.arun(config=run_cfg_idle)
        duration_idle = time.perf_counter() - start_time_idle
        print(f"Wait_until 'networkidle' duration: {duration_idle:.2f}s")
        # 'networkidle' can be significantly longer if there are background network activities

if __name__ == "__main__":
    asyncio.run(wait_until_example())
```

---
#### 6.7.2. Example: Setting a custom `page_timeout` for page operations.
Maximum time (in ms) for operations like page navigation. Default is 60000ms (60s).

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def page_timeout_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # A URL that is intentionally slow or non-existent to trigger timeout
    # httpbin.org/delay/X can simulate a slow response
    slow_url = "https://httpbin.org/delay/5" # Delays for 5 seconds

    # Set a short timeout to demonstrate
    run_cfg_short_timeout = CrawlerRunConfig(url=slow_url, page_timeout=2000) # 2 seconds
    
    print(f"Attempting to crawl {slow_url} with page_timeout=2000ms.")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg_short_timeout)
        if not result.success:
            print(f"Crawl failed as expected due to timeout: {result.error_message}")
            assert "Timeout" in result.error_message or "timeout" in result.error_message.lower()
        else:
            print("Crawl succeeded unexpectedly (timeout might not have triggered).")

if __name__ == "__main__":
    asyncio.run(page_timeout_example())
```

---
#### 6.7.3. Example: Using `wait_for` with a CSS selector before proceeding.
Waits for a specific element to appear in the DOM.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def wait_for_css_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # Simulate a page where content appears after a delay
    # We'll use JS to add an element after 2 seconds
    html_content_delayed = """
    <html><body>
        <div id='loading'>Loading...</div>
        <script>
            setTimeout(() => {
                const newElem = document.createElement('p');
                newElem.id = 'late-content';
                newElem.textContent = 'Content has arrived!';
                document.body.appendChild(newElem);
                document.getElementById('loading').remove();
            }, 2000);
        </script>
    </body></html>
    """
    
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_content_delayed}",
        wait_for="css:#late-content", # Wait for the element with id 'late-content'
        page_timeout=5000 # Overall timeout for the operation
    )
    
    print("Attempting to crawl page with delayed content, waiting for '#late-content'.")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawl successful. Cleaned HTML: {result.cleaned_html}")
            assert "Content has arrived!" in result.cleaned_html
            assert "Loading..." not in result.cleaned_html # Should be removed by the script
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(wait_for_css_example())
```

---
#### 6.7.4. Example: Using `wait_for` with a JavaScript predicate.
Waits for a JavaScript expression to evaluate to true.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def wait_for_js_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # Simulate a page where a JS variable changes after a delay
    html_js_var_delayed = """
    <html><body>
        <p id="status">Initializing...</p>
        <script>
            window.myAppStatus = 'pending';
            setTimeout(() => {
                window.myAppStatus = 'ready';
                document.getElementById('status').textContent = 'Application is Ready!';
            }, 2500);
        </script>
    </body></html>
    """
    
    js_predicate = "window.myAppStatus === 'ready'"
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_js_var_delayed}",
        wait_for=f"js:{js_predicate}",
        page_timeout=5000
    )
    
    print(f"Attempting to crawl page, waiting for JS: `{js_predicate}`.")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawl successful after JS condition met.")
            print(f"Cleaned HTML: {result.cleaned_html}")
            assert "Application is Ready!" in result.cleaned_html
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(wait_for_js_example())
```

---
#### 6.7.5. Example: Setting a specific `wait_for_timeout` for the `wait_for` condition.
If `wait_for` condition is not met within this timeout (in ms), the crawl proceeds or fails based on overall `page_timeout`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def wait_for_timeout_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    html_never_appears = "<html><body><p>Content</p></body></html>"
    
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_never_appears}",
        wait_for="css:#nonexistent-element",
        wait_for_timeout=1000, # Wait only 1 second for this specific element
        page_timeout=5000      # Overall page timeout
    )
    
    print("Attempting to crawl, waiting for a nonexistent element with a short wait_for_timeout.")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        start_time = asyncio.get_event_loop().time()
        result = await crawler.arun(config=run_cfg)
        duration = asyncio.get_event_loop().time() - start_time
        
        if result.success:
            print(f"Crawl completed (likely after wait_for_timeout). Duration: {duration:.2f}s")
            # The crawl might succeed if page_timeout is longer and wait_for_timeout is just a pause point
            # Playwright's wait_for_selector with timeout usually throws an error if not found.
            # Crawl4ai's behavior might proceed if overall page_timeout isn't hit by this.
            # Let's check if the error message indicates a timeout related to the selector.
            # The current implementation of AsyncPlaywrightCrawlerStrategy would lead to an overall timeout.
            # If the wait_for_timeout is meant to be non-fatal, the strategy logic would need adjustment.
            # For now, we expect the page.wait_for_selector to raise a TimeoutError.
            print(f"Crawl error_message (if any): {result.error_message}")
            # assert "Timeout" in result.error_message if result.error_message else False
            # This behavior depends on how Playwright's timeout for wait_for_selector is handled.
            # If it raises and is caught, error_message will have it. If it's ignored, it might proceed.
            # Given current code, it's more likely the overall page_timeout will be hit if wait_for never resolves.
            # Let's assume for this test that wait_for failing to find element leads to crawl failing.
            if result.error_message and "Timeout" in result.error_message: # Playwright TimeoutError
                 print("Wait_for timed out as expected, and crawl might have failed due to it.")
            else:
                 print("Crawl succeeded, wait_for_timeout might have just passed and execution continued.")

        else: # More likely scenario if wait_for is critical
            print(f"Crawl failed as expected. Duration: {duration:.2f}s. Error: {result.error_message}")
            assert "Timeout" in result.error_message # Expecting a timeout error

if __name__ == "__main__":
    asyncio.run(wait_for_timeout_example())
```

---
#### 6.7.6. Example: Enabling `wait_for_images=True` to ensure images are loaded.
Attempts to wait until all (or most) images on the page have finished loading.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def wait_for_images_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    # A page with several images. Wikipedia pages are good for this.
    url_with_images = "https://en.wikipedia.org/wiki/Cat"
    
    run_cfg = CrawlerRunConfig(
        url=url_with_images,
        wait_for_images=True,
        screenshot=True # Take a screenshot to visually verify if images loaded
    )
    
    print(f"Attempting to crawl {url_with_images} with wait_for_images=True.")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawl successful for {url_with_images}.")
            if result.screenshot:
                print("Screenshot captured. Manually inspect 'wait_for_images_screenshot.png' to see if images are loaded.")
                with open("wait_for_images_screenshot.png", "wb") as f:
                    import base64
                    f.write(base64.b64decode(result.screenshot))
            # Check if media extraction found images (though this happens after HTML retrieval)
            if result.media and result.media.get("images"):
                print(f"Found {len(result.media['images'])} image entries.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(wait_for_images_example())
```

---
#### 6.7.7. Example: Setting `delay_before_return_html` to pause before final HTML retrieval.
Adds a fixed delay (in seconds) just before the final HTML content is grabbed from the page.

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def delay_before_html_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        delay_before_return_html=2.0 # Wait 2 seconds
    )
    print(f"Configured delay_before_return_html: {run_cfg.delay_before_return_html}s")
    
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"Crawling {run_cfg.url} with a 2s delay before HTML retrieval.")
        start_time = time.perf_counter()
        result = await crawler.arun(config=run_cfg)
        duration = time.perf_counter() - start_time
        
        if result.success:
            print(f"Crawl successful. Total duration: {duration:.2f}s (should be > 2s).")
            assert duration >= 2.0
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(delay_before_html_example())
```

---
### 6.8. `arun_many` Specific Timing and Concurrency

#### 6.8.1. Example: Configuring `mean_delay` and `max_range` for randomized delays between `arun_many` requests.
This adds a random delay between `(mean_delay - max_range)` and `(mean_delay + max_range)` seconds for each request in `arun_many`.

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def arun_many_delay_example():
    browser_cfg = BrowserConfig(headless=True, verbose=False) # Keep logs cleaner for this demo
    urls = [f"https://example.com?page={i}" for i in range(3)] # 3 dummy URLs

    run_cfg = CrawlerRunConfig(
        mean_delay=1.0,  # Average 1 second delay
        max_range=0.5,   # Delay will be between 0.5s and 1.5s
        cache_mode=CacheMode.BYPASS # Ensure actual fetches
    )
    print(f"Configured for arun_many: mean_delay={run_cfg.mean_delay}, max_range={run_cfg.max_range}")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print("Running arun_many with delays...")
        start_time = time.perf_counter()
        # arun_many itself doesn't take these; they are interpreted by dispatchers.
        # The default MemoryAdaptiveDispatcher uses these.
        results = await crawler.arun_many(urls=urls, config=run_cfg)
        total_duration = time.perf_counter() - start_time
        
        success_count = sum(1 for r in results if r.success)
        print(f"Finished {success_count}/{len(urls)} crawls.")
        print(f"Total duration for {len(urls)} crawls: {total_duration:.2f}s")
        
        # Expected duration: roughly num_urls * mean_delay + (sum of actual fetch times)
        # For 3 URLs, with mean_delay=1, expect at least 2 * 0.5 = 1s of added delay, up to 2 * 1.5 = 3s
        # This is a rough check, actual network time also contributes.
        # If all example.com fetches are very fast (<0.1s), total should be around 1-3s + (3*~0.1s)
        # A more robust test would mock the fetch time.
        # For now, we just check it took longer than if no delays.
        assert total_duration > (len(urls) -1) * (run_cfg.mean_delay - run_cfg.max_range) if len(urls)>1 else True

if __name__ == "__main__":
    asyncio.run(arun_many_delay_example())
```

---
#### 6.8.2. Example: Adjusting `semaphore_count` to control concurrency in `arun_many`.
Limits the number of concurrent crawl operations when using `arun_many` with dispatchers that respect it (like `SemaphoreDispatcher`).

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.async_dispatcher import SemaphoreDispatcher # Explicitly use SemaphoreDispatcher

async def arun_many_semaphore_example():
    browser_cfg = BrowserConfig(headless=True, verbose=False)
    # More URLs to demonstrate concurrency clearly
    urls = [f"https://httpbin.org/delay/1?id={i}" for i in range(6)] # Each takes ~1s

    run_cfg_concurrency_2 = CrawlerRunConfig(
        semaphore_count=2, # Allow only 2 concurrent crawls
        cache_mode=CacheMode.BYPASS
    )
    print(f"Configured for arun_many: semaphore_count={run_cfg_concurrency_2.semaphore_count}")

    # Use SemaphoreDispatcher to respect semaphore_count
    dispatcher = SemaphoreDispatcher(max_concurrent_tasks=run_cfg_concurrency_2.semaphore_count)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"Running arun_many with {len(urls)} URLs and semaphore_count=2...")
        start_time = time.perf_counter()
        results = await crawler.arun_many(urls=urls, config=run_cfg_concurrency_2, dispatcher=dispatcher)
        total_duration = time.perf_counter() - start_time
        
        success_count = sum(1 for r in results if r.success)
        print(f"Finished {success_count}/{len(urls)} crawls.")
        print(f"Total duration: {total_duration:.2f}s")
        
        # With 6 URLs, each taking ~1s, and concurrency of 2:
        # Expected time is roughly (num_urls / concurrency) * per_url_time
        # (6 / 2) * 1s = 3s (plus overhead)
        # Without semaphore, it might be closer to 1s if all run truly parallel (unlikely for 6 heavy tasks)
        # or up to 6s if strictly sequential.
        # This is a heuristic check
        assert total_duration >= (len(urls) / run_cfg_concurrency_2.semaphore_count) * 1.0 
        assert total_duration < len(urls) * 1.0 # Should be faster than purely sequential

if __name__ == "__main__":
    asyncio.run(arun_many_semaphore_example())
```

---
### 6.9. Page Interaction, Anti-Bot, and Dynamic Content

#### 6.9.1. Example: Executing a single JavaScript string using `js_code`.
Runs arbitrary JavaScript on the page after it loads.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def single_js_code_example():
    browser_cfg = BrowserConfig(headless=True)
    
    js_to_run = "document.body.innerHTML = '<h1>JavaScript Was Here!</h1>';"
    run_cfg = CrawlerRunConfig(
        url="https://example.com", # Original page content will be replaced
        js_code=js_to_run
    )
    
    print(f"Running JS: {js_to_run}")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url} after JS execution.")
            print(f"Cleaned HTML: {result.cleaned_html}")
            assert "JavaScript Was Here!" in result.cleaned_html
            assert "Example Domain" not in result.cleaned_html # Original H1 should be gone
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(single_js_code_example())
```

---
#### 6.9.2. Example: Executing a list of JavaScript snippets using `js_code`.
Runs multiple JavaScript snippets sequentially.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def list_js_code_example():
    browser_cfg = BrowserConfig(headless=True)
    
    js_snippets = [
        "document.body.insertAdjacentHTML('beforeend', '<p id=\\'js_step1\\'>Step 1 Complete</p>');",
        "document.getElementById('js_step1').style.color = 'blue';",
        "window.js_result = document.getElementById('js_step1').outerHTML;" # Store for verification
    ]
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        js_code=js_snippets,
        # We need to retrieve the window.js_result
        # This can be done by having the last JS snippet return something,
        # or by executing another JS snippet to retrieve it in a subsequent step.
        # For simplicity, let's assume the crawler strategy can pick up the last expression value
        # (if it's a string, Playwright's page.evaluate often returns it).
        # More reliably, explicitly return the value:
        # js_snippets.append("window.js_result;")
    )
    
    print(f"Running JS snippets sequentially.")
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # To get a JS execution result, the last JS statement must evaluate to a serializable value.
        # Let's modify js_snippets for this.
        run_cfg.js_code.append("window.js_result;") # type: ignore
        
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawled {result.url} after multiple JS executions.")
            print(f"Cleaned HTML (should contain 'Step 1 Complete'):\n{result.cleaned_html[:300]}")
            assert "Step 1 Complete" in result.cleaned_html
            
            print(f"JS Execution Result (outerHTML of #js_step1): {result.js_execution_result}")
            assert result.js_execution_result and 'style="color: blue;"' in result.js_execution_result
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(list_js_code_example())
```

---
#### 6.9.3. Example: Using `js_only=True` for subsequent calls within a session to only execute JS.
Useful for multi-step interactions where you only want to run JS on an already loaded page in a session, without a full page navigation.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def js_only_example():
    session_id = "js_only_session"
    browser_cfg = BrowserConfig(headless=True, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Step 1: Load the page
        run_cfg1 = CrawlerRunConfig(url="https://example.com", session_id=session_id)
        print("\n--- Step 1: Loading initial page ---")
        result1 = await crawler.arun(config=run_cfg1)
        if not result1.success:
            print(f"Initial page load failed: {result1.error_message}")
            return
        print(f"Initial page '{result1.url}' loaded. HTML length: {len(result1.html)}")

        # Step 2: Execute JS only, no re-navigation
        js_to_modify = "document.body.innerHTML = '<h1>JS Only Update!</h1>'; 'JS Executed';"
        run_cfg2 = CrawlerRunConfig(
            url=result1.url, # Important: use the same URL or the one currently loaded in session
            session_id=session_id,
            js_code=js_to_modify,
            js_only=True # This is key
        )
        print("\n--- Step 2: Executing JS only on the current page ---")
        result2 = await crawler.arun(config=run_cfg2)
        if result2.success:
            print(f"JS-only update successful for {result2.url}.")
            print(f"Cleaned HTML after JS-only: {result2.cleaned_html}")
            assert "JS Only Update!" in result2.cleaned_html
            assert "Example Domain" not in result2.cleaned_html
            print(f"JS Execution Result: {result2.js_execution_result}")
            assert result2.js_execution_result == "JS Executed"
        else:
            print(f"JS-only update failed: {result2.error_message}")
        
        await crawler.crawler_strategy.kill_session(session_id)
        print(f"\nSession '{session_id}' killed.")

if __name__ == "__main__":
    asyncio.run(js_only_example())
```

---
#### 6.9.4. Example: Enabling `scan_full_page=True` and setting `scroll_delay` to handle lazy-loaded content.
The crawler will attempt to scroll through the entire page, pausing between scrolls, to trigger lazy-loading.

```python
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def scan_full_page_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True, viewport_height=300) # Smaller viewport to make scrolling more evident
    
    # A page known for long content or lazy loading (e.g., a long blog post or news article)
    # For this demo, we'll use a simple page and check total scroll time.
    # Real effect is best seen on pages that actually lazy-load images/content.
    url_to_scan = "https://en.wikipedia.org/wiki/Web_scraping" 
    
    run_cfg_scan = CrawlerRunConfig(
        url=url_to_scan,
        scan_full_page=True,
        scroll_delay=0.2,  # 0.2 seconds delay between scroll steps
        cache_mode=CacheMode.BYPASS
    )
    print(f"Crawling {url_to_scan} with scan_full_page=True, scroll_delay={run_cfg_scan.scroll_delay}s")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        start_time = time.perf_counter()
        result = await crawler.arun(config=run_cfg_scan)
        duration = time.perf_counter() - start_time
        
        if result.success:
            print(f"Crawl successful. Duration: {duration:.2f}s (includes scrolling time).")
            print(f"Markdown length: {len(result.markdown.raw_markdown)}")
            # On a long page, the duration should be noticeably longer than a non-scrolling crawl.
            # And more content/images might be present in result.html/result.media
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(scan_full_page_example())
```

---
#### 6.9.5. Example: Enabling `process_iframes=True` to attempt extracting content from iframes.
**Note:** Iframe processing can be complex and success depends heavily on iframe structure and cross-origin policies.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def process_iframes_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # Need a URL that reliably contains accessible iframes for a good demo.
    # W3Schools iframe example page:
    iframe_test_url = "https://www.w3schools.com/tags/tryit.asp?filename=tryhtml_iframe_name"
    
    run_cfg_iframes = CrawlerRunConfig(
        url=iframe_test_url,
        process_iframes=True,
        cache_mode=CacheMode.BYPASS,
        wait_for="iframe#iframeResult" # Wait for the specific iframe to ensure it's targetable
    )
    print(f"Crawling {iframe_test_url} with process_iframes=True.")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg_iframes)
        if result.success:
            print(f"Crawl successful for {iframe_test_url}.")
            print(f"Cleaned HTML (first 1000 chars):\n{result.cleaned_html[:1000]}")
            # Check for content known to be inside an iframe on that page.
            # The W3Schools example iframe usually loads "demo_iframe.htm" which contains "This is an iframe".
            if "This is an iframe" in result.cleaned_html:
                print("SUCCESS: Content from iframe seems to be included in cleaned_html.")
            else:
                print("Content from iframe not found or iframe structure is complex/cross-origin restricted.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(process_iframes_example())
```

---
#### 6.9.6. Example: Using `remove_overlay_elements=True` to dismiss popups/modals.
Attempts to automatically find and remove common overlay/popup elements before content extraction.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def remove_overlays_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # A page that might have a cookie consent banner or modal.
    # This is hard to test reliably with a public static URL as overlays are dynamic.
    # We'll simulate an overlay with raw HTML for this example.
    html_with_overlay = """
    <html><body>
        <div id="page-content">Main page text here.</div>
        <div id="cookie-banner" style="position:fixed; bottom:0; background:lightgray; width:100%; padding:10px; text-align:center;">
            This is a cookie banner! <button onclick="this.parentElement.remove()">Accept</button>
        </div>
        <div class="modal-overlay" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5);">
            <div class="modal-content" style="background:white; margin:15% auto; padding:20px; width:50%;">A promotional modal!</div>
        </div>
    </body></html>
    """
    
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_with_overlay}",
        remove_overlay_elements=True,
        cache_mode=CacheMode.BYPASS
    )
    print(f"Crawling content with remove_overlay_elements=True.")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawl successful.")
            cleaned_html = result.cleaned_html
            print(f"Cleaned HTML (should not contain overlay/banner):\n{cleaned_html}")
            assert "cookie-banner" not in cleaned_html.lower() # Check by ID
            assert "modal-overlay" not in cleaned_html.lower() # Check by class
            assert "Main page text here." in cleaned_html # Main content should remain
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(remove_overlays_example())
```

---
#### 6.9.7. Example: Enabling `simulate_user=True` for basic user interaction simulation.
Triggers basic mouse movements and scrolls to mimic user presence, potentially bypassing some simple anti-bot measures.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def simulate_user_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True) # Can be False to observe
    
    run_cfg = CrawlerRunConfig(
        url="https://example.com", # A simple page for demonstration
        simulate_user=True,
        cache_mode=CacheMode.BYPASS
    )
    print(f"Crawling {run_cfg.url} with simulate_user=True.")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawl successful with user simulation.")
            # The effect of simulate_user is subtle and hard to verify programmatically
            # on a simple page. It's more about behavior during the crawl.
            # If there were JS event listeners for mouse/scroll, they might have been triggered.
            print(f"Markdown (first 300 chars):\n{result.markdown.raw_markdown[:300]}")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(simulate_user_example())
```

---
#### 6.9.8. Example: Enabling `override_navigator=True` to modify browser navigator properties.
Modifies properties like `navigator.webdriver` to make the browser appear less like an automated tool.

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def override_navigator_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # JS to check navigator.webdriver property
    js_check_webdriver = "JSON.stringify({webdriver: navigator.webdriver})"
    
    run_cfg_override = CrawlerRunConfig(
        url="https://httpbin.org/anything", # Any page will do for this JS check
        override_navigator=True,
        js_code=js_check_webdriver,
        cache_mode=CacheMode.BYPASS
    )
    print(f"Crawling with override_navigator=True.")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg_override)
        if result.success and result.js_execution_result:
            print(f"Crawl successful with navigator override.")
            webdriver_status = result.js_execution_result
            print(f"navigator.webdriver status: {webdriver_status}")
            # When overridden, navigator.webdriver should be false
            assert webdriver_status.get("webdriver") is False
        elif not result.js_execution_result:
             print(f"JS execution did not return a result for webdriver check.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(override_navigator_example())
```

---
#### 6.9.9. Example: Using `magic=True` for automated handling of common anti-bot measures like overlays.
`magic=True` is a convenience flag that enables several anti-bot evasion techniques, including `remove_overlay_elements` and `override_navigator`.

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def magic_mode_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # HTML with an overlay and JS that checks navigator.webdriver
    html_with_magic_challenges = """
    <html><body>
        <div id="page-content">Main content.</div>
        <div id="my-overlay" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.3);">Overlay</div>
        <script>
            window.webdriverStatus = navigator.webdriver;
        </script>
    </body></html>
    """
    js_get_webdriver = "JSON.stringify({webdriver: window.webdriverStatus})"

    run_cfg_magic = CrawlerRunConfig(
        url=f"raw://{html_with_magic_challenges}",
        magic=True,
        js_code=js_get_webdriver, # Check webdriver status after magic applies
        cache_mode=CacheMode.BYPASS
    )
    print(f"Crawling with magic=True.")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg_magic)
        if result.success:
            print(f"Crawl successful with magic mode.")
            
            # Check overlay removal
            print(f"Cleaned HTML (overlay should be gone):\n{result.cleaned_html}")
            assert "my-overlay" not in result.cleaned_html # Magic mode should remove it
            assert "Main content." in result.cleaned_html

            # Check navigator override
            if result.js_execution_result:
                webdriver_status = result.js_execution_result
                print(f"navigator.webdriver status (via JS): {webdriver_status}")
                assert webdriver_status.get("webdriver") is False # Magic mode should override this
            else:
                print("JS execution for webdriver check did not yield result.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(magic_mode_example())
```

---
#### 6.9.10. Example: Using `adjust_viewport_to_content=True` to dynamically resize viewport.
Resizes the browser viewport to fit the dimensions of the rendered page content. This is useful for accurate screenshots of the entire logical page.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def adjust_viewport_example():
    # A page that's taller than the default viewport
    # We'll use a raw HTML example with a defined large height for predictability
    tall_page_html = """
    <html><head><style>body {{ margin: 0; }} #tall-div {{ height: 2000px; width: 500px; background: lightblue; }}</style></head>
    <body><div id="tall-div">This is a tall div.</div></body></html>
    """
    
    browser_cfg = BrowserConfig(
        headless=True, 
        verbose=True,
        viewport_width=800, # Initial viewport
        viewport_height=600
    )
    
    run_cfg = CrawlerRunConfig(
        url=f"raw://{tall_page_html}",
        adjust_viewport_to_content=True,
        screenshot=True, # Capture screenshot to see the effect
        cache_mode=CacheMode.BYPASS
    )
    print(f"Crawling with adjust_viewport_to_content=True. Initial viewport: 800x600.")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print(f"Crawl successful.")
            if result.screenshot:
                print("Screenshot captured. If adjust_viewport_to_content worked, it should show the full 2000px height.")
                # Playwright's screenshot of full page might not directly reflect viewport size change,
                # but the internal logic for determining content height would have used the adjusted viewport.
                # The primary effect is on how Playwright calculates "full page".
                # It's hard to verify viewport size change directly without inspecting browser internals during run.
                # The key is that `page.content()` or screenshot operations consider the full content.
                print("Effect is primarily on internal full-page calculations for Playwright.")
            else:
                print("Screenshot not captured.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(adjust_viewport_example())
```

---
### 6.10. Media Capturing and Processing Options

#### 6.10.1. Example: Enabling screenshots with `screenshot=True`.
Captures a screenshot of the page.

```python
import asyncio
import base64
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def enable_screenshot_example():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        screenshot=True,
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success and result.screenshot:
            print(f"Screenshot captured for {result.url}.")
            screenshot_path = Path("./example_com_screenshot.png")
            with open(screenshot_path, "wb") as f:
                f.write(base64.b64decode(result.screenshot))
            print(f"Screenshot saved to {screenshot_path.resolve()}")
            assert screenshot_path.exists() and screenshot_path.stat().st_size > 0
            screenshot_path.unlink() # Clean up
        elif not result.screenshot:
            print("Screenshot was enabled but not captured.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(enable_screenshot_example())
```

---
#### 6.10.2. Example: Using `screenshot_wait_for` (float) to add a delay before taking a screenshot.
Adds a specific delay (in seconds) before the screenshot is taken, useful for animations or late-loading elements.

```python
import asyncio
import base64
from pathlib import Path
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def screenshot_wait_for_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # Page that might have some animation or late change
    # For demo, we'll just time it.
    url_to_crawl = "https://example.com" 
    delay_seconds = 1.5
    
    run_cfg = CrawlerRunConfig(
        url=url_to_crawl,
        screenshot=True,
        screenshot_wait_for=delay_seconds, # Wait 1.5 seconds before screenshot
        cache_mode=CacheMode.BYPASS
    )
    print(f"Crawling {url_to_crawl}, will wait {delay_seconds}s before screenshot.")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        start_time = time.perf_counter()
        result = await crawler.arun(config=run_cfg)
        duration = time.perf_counter() - start_time
        
        if result.success and result.screenshot:
            print(f"Screenshot captured. Total crawl duration: {duration:.2f}s (should be >= {delay_seconds}s).")
            assert duration >= delay_seconds
            # Save for manual inspection if needed
            # screenshot_path = Path("./delayed_screenshot.png")
            # with open(screenshot_path, "wb") as f:
            #     f.write(base64.b64decode(result.screenshot))
            # print(f"Screenshot saved to {screenshot_path.resolve()}")
            # screenshot_path.unlink()
        else:
            print(f"Crawl or screenshot failed: {result.error_message if result else 'Unknown error'}")

if __name__ == "__main__":
    asyncio.run(screenshot_wait_for_example())
```

---
#### 6.10.3. Example: Customizing `screenshot_height_threshold` for full-page screenshot strategy.
If page height exceeds this threshold, Playwright might use a different strategy for full-page screenshots (e.g. stitching). Default is 20000.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def screenshot_height_threshold_example():
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    
    # This primarily affects how Playwright takes the full page screenshot internally.
    # The output (base64 image) will still be the full page.
    run_cfg = CrawlerRunConfig(
        url="https://en.wikipedia.org/wiki/Python_(programming_language)", # A long page
        screenshot=True,
        screenshot_height_threshold=5000, # Lower threshold, might trigger stitching earlier
        cache_mode=CacheMode.BYPASS
    )
    print(f"Crawling with screenshot_height_threshold={run_cfg.screenshot_height_threshold}.")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success and result.screenshot:
            print(f"Screenshot captured for long page.")
            # Verification of the *strategy* change is internal to Playwright
            # and not easily asserted from outside. The result is still a full screenshot.
            assert len(result.screenshot) > 1000 # Check if screenshot data exists
        else:
            print(f"Crawl or screenshot failed: {result.error_message if result else 'Unknown error'}")

if __name__ == "__main__":
    asyncio.run(screenshot_height_threshold_example())
```

---
#### 6.10.4. Example: Enabling PDF generation with `pdf=True`.
Generates a PDF of the rendered page.

```python
import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def enable_pdf_generation():
    browser_cfg = BrowserConfig(headless=True) # PDF generation requires headless
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        pdf=True,
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success and result.pdf:
            print(f"PDF generated for {result.url}.")
            pdf_path = Path("./example_com_page.pdf")
            with open(pdf_path, "wb") as f:
                f.write(result.pdf)
            print(f"PDF saved to {pdf_path.resolve()}")
            assert pdf_path.exists() and pdf_path.stat().st_size > 0
            pdf_path.unlink() # Clean up
        elif not result.pdf:
            print("PDF was enabled but not generated.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(enable_pdf_generation())
```

---
#### 6.10.5. Example: Enabling MHTML archive capture with `capture_mhtml=True`.
Saves the page as an MHTML archive, which includes all resources (CSS, images, JS) in a single file.

```python
import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def capture_mhtml_example():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(
        url="https://example.com",
        capture_mhtml=True,
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success and result.mhtml:
            print(f"MHTML archive captured for {result.url}.")
            mhtml_path = Path("./example_com_page.mhtml")
            with open(mhtml_path, "w", encoding="utf-8") as f: # MHTML is text-based
                f.write(result.mhtml)
            print(f"MHTML saved to {mhtml_path.resolve()}")
            assert mhtml_path.exists() and mhtml_path.stat().st_size > 0
            mhtml_path.unlink() # Clean up
        elif not result.mhtml:
            print("MHTML was enabled but not captured.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(capture_mhtml_example())
```

---
#### 6.10.6. Example: Setting `image_description_min_word_threshold` for image alt/desc processing.
Filters image descriptions (alt text or surrounding text) based on word count.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def image_desc_threshold_example():
    # HTML with images having varying alt text lengths
    html_with_img_alts = """
    <html><body>
        <img src="img1.jpg" alt="A single word">
        <img src="img2.jpg" alt="This is a short description of five words">
        <img src="img3.jpg" alt="This alt text is definitely longer and should pass a higher threshold.">
    </body></html>
    """
    # Default for image_description_min_word_threshold is 50 in config.py, but often effectively lower if not using LLM for desc.
    # The WebScrapingStrategy uses it for finding desc from surrounding text.
    # Here, we test its effect on alt text directly (assuming internal logic considers alt text length)
    
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_with_img_alts}",
        image_description_min_word_threshold=4, # Only consider alts/desc with >= 4 words
        cache_mode=CacheMode.BYPASS
    )
    
    print(f"Crawling with image_description_min_word_threshold={run_cfg.image_description_min_word_threshold}.")
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success and result.media and result.media.get("images"):
            print(f"Images found: {len(result.media['images'])}")
            for img in result.media["images"]:
                print(f"  src: {img.get('src')}, alt: '{img.get('alt')}', desc: '{img.get('desc')}'")
            
            # Expect only img2 and img3 to have their alt text considered substantial enough for desc
            # (assuming desc field is populated from alt if alt meets threshold)
            # This depends on the scraping strategy's logic for populating 'desc'.
            # The default WebScrapingStrategy populates 'desc' from parent text if alt is short.
            # A direct test of the threshold on 'alt' itself is tricky without knowing exact internal logic.
            # Let's assume the intent is that 'alt' contributes to 'desc' if long enough.
            
            # This test is more conceptual about the parameter's existence.
            # The actual filtering based on this threshold happens within the scraping strategy logic.
            # For now, we confirm that images are extracted.
            assert len(result.media["images"]) == 3 
            print("Parameter set. Actual filtering of descriptions occurs in scraping strategy.")

        else:
            print(f"Crawl failed or no images: {result.error_message if result else 'No result'}")

if __name__ == "__main__":
    asyncio.run(image_desc_threshold_example())
```

---
#### 6.10.7. Example: Setting `image_score_threshold` for filtering images by relevance.
Images scoring below this heuristic threshold might be discarded.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def image_score_threshold_example():
    # WebScrapingStrategy scores images. Default threshold is 3.
    # Images with good alt text, dimensions, and not from common "ignore" patterns get higher scores.
    
    html_with_varied_images = """
    <html><body>
        <img src="good_image.jpg" alt="A very descriptive alt text for a good image" width="300" height="200"> <!-- High score -->
        <img src="icon.png" alt="icon" width="16" height="16"> <!-- Low score -->
        <img src="decorative.gif"> <!-- No alt, no dimensions, likely low score -->
    </body></html>
    """
    
    run_cfg_high_thresh = CrawlerRunConfig(
        url=f"raw://{html_with_varied_images}",
        image_score_threshold=4, # Higher threshold, expect fewer images
        cache_mode=CacheMode.BYPASS
    )
    run_cfg_low_thresh = CrawlerRunConfig(
        url=f"raw://{html_with_varied_images}",
        image_score_threshold=1, # Lower threshold, expect more images
        cache_mode=CacheMode.BYPASS
    )
    
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"\n--- Crawling with image_score_threshold={run_cfg_high_thresh.image_score_threshold} ---")
        result_high = await crawler.arun(config=run_cfg_high_thresh)
        images_high = result_high.media.get("images", []) if result_high.success else []
        print(f"Images found (high threshold): {len(images_high)}")
        for img in images_high: print(f"  - {img.get('src')}, score: {img.get('score')}")

        print(f"\n--- Crawling with image_score_threshold={run_cfg_low_thresh.image_score_threshold} ---")
        result_low = await crawler.arun(config=run_cfg_low_thresh)
        images_low = result_low.media.get("images", []) if result_low.success else []
        print(f"Images found (low threshold): {len(images_low)}")
        for img in images_low: print(f"  - {img.get('src')}, score: {img.get('score')}")
        
        if result_high.success and result_low.success:
             assert len(images_high) <= len(images_low)
             if images_high: # Check if the good image passed the high threshold
                 assert any(img.get('src') == "good_image.jpg" for img in images_high)
             if len(images_low) > len(images_high): # Check if lower threshold included more
                 assert any(img.get('src') == "icon.png" for img in images_low) or \
                        any(img.get('src') == "decorative.gif" for img in images_low)

if __name__ == "__main__":
    asyncio.run(image_score_threshold_example())
```

---
#### 6.10.8. Example: Setting `table_score_threshold` for filtering tables by relevance.
Tables scoring below this heuristic threshold might be discarded. Default is 7.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def table_score_threshold_example():
    html_with_tables = """
    <html><body>
        <p>Layout table (low score):</p>
        <table><tr><td>Cell 1</td><td>Cell 2</td></tr></table>

        <p>Data table (high score):</p>
        <table id="data-table-1">
            <caption>My Data</caption>
            <thead><tr><th>Header 1</th><th>Header 2</th></tr></thead>
            <tbody>
                <tr><td>Data A1</td><td>Data B1</td></tr>
                <tr><td>Data A2</td><td>Data B2</td></tr>
            </tbody>
        </table>
    </body></html>
    """
    
    run_cfg_high_thresh = CrawlerRunConfig(
        url=f"raw://{html_with_tables}",
        table_score_threshold=10, # Higher threshold, expect fewer/no tables
        cache_mode=CacheMode.BYPASS
    )
    run_cfg_low_thresh = CrawlerRunConfig(
        url=f"raw://{html_with_tables}",
        table_score_threshold=5,  # Lower threshold, data table should pass
        cache_mode=CacheMode.BYPASS
    )
    
    browser_cfg = BrowserConfig(headless=True, verbose=True)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"\n--- Crawling with table_score_threshold={run_cfg_high_thresh.table_score_threshold} ---")
        result_high = await crawler.arun(config=run_cfg_high_thresh)
        tables_high = result_high.media.get("tables", []) if result_high.success else []
        print(f"Tables found (high threshold): {len(tables_high)}")
        for i, tbl in enumerate(tables_high): print(f"  - Table {i} caption: {tbl.get('caption', 'N/A')}")

        print(f"\n--- Crawling with table_score_threshold={run_cfg_low_thresh.table_score_threshold} ---")
        result_low = await crawler.arun(config=run_cfg_low_thresh)
        tables_low = result_low.media.get("tables", []) if result_low.success else []
        print(f"Tables found (low threshold): {len(tables_low)}")
        for i, tbl in enumerate(tables_low): print(f"  - Table {i} caption: {tbl.get('caption', 'N/A')}")
        
        if result_high.success and result_low.success:
            assert len(tables_high) <= len(tables_low)
            if tables_low: # The data table should be found with lower threshold
                assert any("My Data" in tbl.get("caption", "") for tbl in tables_low)
            if not tables_high: # High threshold might exclude all
                print("High threshold correctly excluded tables.")

if __name__ == "__main__":
    asyncio.run(table_score_threshold_example())
```

---
#### 6.10.9. Example: Enabling `exclude_external_images=True` to ignore images from other domains.
Only images hosted on the same domain (or subdomains) as the crawled URL will be included.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def exclude_external_images_example():
    html_with_mixed_images = """
    <html><body>
        <p>Internal Image:</p>
        <img src="/images/local_image.png" alt="Local">
        <p>External Image:</p>
        <img src="https://cdn.anotherdomain.com/image.jpg" alt="External CDN">
        <p>Same domain, different subdomain (should be kept if base domain matches):</p>
        <img src="https://img.example.com/another_local.png" alt="Subdomain Local">
    </body></html>
    """
    
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_with_mixed_images}", # Base URL for context
        # url="https://example.com", # If using a live page, set base_url for raw HTML
        base_url="https://example.com",   # Needed for raw HTML to determine internal/external
        exclude_external_images=True,
        cache_mode=CacheMode.BYPASS
    )
    
    print(f"Crawling with exclude_external_images=True. Base URL for resolving: {run_cfg.base_url}")
    browser_cfg = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success and result.media and result.media.get("images"):
            print(f"Images found: {len(result.media['images'])}")
            external_found = False
            internal_found_count = 0
            for img in result.media["images"]:
                print(f"  - Src: {img.get('src')}, Alt: {img.get('alt')}")
                if "anotherdomain.com" in img.get('src', ''):
                    external_found = True
                if "example.com" in img.get('src', '') or img.get('src', '').startswith("/images"):
                    internal_found_count +=1
            
            assert not external_found, "External image was not excluded"
            assert internal_found_count == 2, f"Expected 2 internal/same-domain images, found {internal_found_count}"
            print("SUCCESS: External images excluded, internal/same-domain images kept.")
        else:
            print(f"Crawl failed or no images: {result.error_message if result else 'No result'}")

if __name__ == "__main__":
    asyncio.run(exclude_external_images_example())
```

---
#### 6.10.10. Example: Enabling `exclude_all_images=True` to remove all images.
No images will be processed or included in `result.media["images"]`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def exclude_all_images_example():
    html_with_images = """
    <html><body>
        <img src="local.jpg" alt="Local">
        <img src="https://cdn.example.com/external.png" alt="External">
    </body></html>
    """
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_with_images}",
        exclude_all_images=True,
        cache_mode=CacheMode.BYPASS
    )
    
    print(f"Crawling with exclude_all_images=True.")
    browser_cfg = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            images_found = result.media.get("images", [])
            print(f"Images found: {len(images_found)}")
            assert not images_found, "Images were found even though exclude_all_images was True."
            print("SUCCESS: All images were excluded.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(exclude_all_images_example())
```

---
### 6.11. Link and Domain Filtering Options

#### 6.11.1. Example: Customizing the list of `exclude_social_media_domains`.
Provide your own list of social media domains to exclude, overriding or extending the default list.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def custom_social_media_domains_example():
    html_with_links = """
    <html><body>
        <a href="https://facebook.com/somepage">Facebook</a>
        <a href="https://linkedin.com/in/someone">LinkedIn</a>
        <a href="https://mycustomsocial.net/profile">My Custom Social</a>
        <a href="https://example.com/internal">Internal</a>
    </body></html>
    """
    
    # Default list includes facebook.com, linkedin.com, etc.
    # Let's exclude only "mycustomsocial.net" and keep others for this test.
    # To do this, we must also enable exclude_social_media_links=True.
    custom_social_domains = ["mycustomsocial.net"]
    
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_with_links}",
        base_url="https://anotherexample.com", # To make example.com external
        exclude_social_media_links=True, # This flag enables the filtering
        exclude_social_media_domains=custom_social_domains, # Provide our custom list
        cache_mode=CacheMode.BYPASS
    )
    
    print(f"Crawling with custom exclude_social_media_domains: {custom_social_domains}")
    browser_cfg = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            print("Links found in result.links['external']:")
            mycustomsocial_found = False
            facebook_found = False
            linkedin_found = False
            for link_info in result.links.get("external", []):
                print(f"  - {link_info.get('href')}")
                if "mycustomsocial.net" in link_info.get('href', ''):
                    mycustomsocial_found = True
                if "facebook.com" in link_info.get('href', ''):
                    facebook_found = True
                if "linkedin.com" in link_info.get('href', ''):
                    linkedin_found = True
            
            assert not mycustomsocial_found, "Custom social domain 'mycustomsocial.net' was not excluded."
            # Since we overrode the list, default social domains should now be included if not in our custom list.
            # However, exclude_social_media_links = True with a custom list should *only* exclude those in the custom list from the "social" category.
            # The behavior of exclude_social_media_domains is to *add* to the default list if not replacing.
            # The provided code has exclude_social_media_domains take precedence and replaces the default if exclude_social_media_links is true
            # (Looking at `async_webcrawler.py` processing of these flags).
            # The code's logic is: if `exclude_social_media_links` is true, it uses `self.config.exclude_social_media_domains` (which defaults to `config.SOCIAL_MEDIA_DOMAINS`)
            # So, if `exclude_social_media_domains` is set in `CrawlerRunConfig`, it effectively *replaces* the default list for that run.
            print("As exclude_social_media_domains was set, it replaces the default list.")
            assert facebook_found, "Facebook link was unexpectedly excluded with custom list."
            assert linkedin_found, "LinkedIn link was unexpectedly excluded with custom list."
            print("SUCCESS: Custom social media domain excluded, others (not in custom list) were kept.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(custom_social_media_domains_example())
```

---
#### 6.11.2. Example: Enabling `exclude_external_links=True` to remove links to other domains.
Only links within the same base domain as the crawled URL will be kept in `result.links`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def exclude_external_links_example():
    html_with_mixed_links = """
    <html><body>
        <a href="/internal-page">Internal Page</a>
        <a href="https://example.com/another-internal">Another Internal</a>
        <a href="https://sub.example.com/sub-internal">Subdomain Internal</a>
        <a href="https://otherdomain.com/external-page">External Page</a>
    </body></html>
    """
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_with_mixed_links}",
        base_url="https://example.com", # Define the base domain for this raw HTML
        exclude_external_links=True,
        cache_mode=CacheMode.BYPASS
    )
    
    print(f"Crawling with exclude_external_links=True. Base URL: {run_cfg.base_url}")
    browser_cfg = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            external_links = result.links.get("external", [])
            internal_links = result.links.get("internal", [])
            print(f"External links found: {len(external_links)}")
            for link in external_links: print(f"  - {link.get('href')}")
            print(f"Internal links found: {len(internal_links)}")
            for link in internal_links: print(f"  - {link.get('href')}")

            assert not external_links, "External links were not excluded."
            assert len(internal_links) == 3, f"Expected 3 internal links, found {len(internal_links)}."
            print("SUCCESS: External links excluded, internal links kept.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(exclude_external_links_example())
```

---
#### 6.11.3. Example: Enabling `exclude_social_media_links=True` (uses `exclude_social_media_domains` list).
Filters out links to common social media platforms using the default or a custom list.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode, config as crawl4ai_config

async def exclude_social_media_links_example():
    html_with_social_links = f"""
    <html><body>
        <a href="https://example.com/normal">Normal Link</a>
        <a href="https://{crawl4ai_config.SOCIAL_MEDIA_DOMAINS[0]}/someuser">Social Media Link 1</a>
        <a href="https://{crawl4ai_config.SOCIAL_MEDIA_DOMAINS[1]}/anotheruser">Social Media Link 2</a>
    </body></html>
    """
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_with_social_links}",
        base_url="https://example.com",
        exclude_social_media_links=True, # Uses default SOCIAL_MEDIA_DOMAINS list
        cache_mode=CacheMode.BYPASS
    )
    
    print(f"Crawling with exclude_social_media_links=True.")
    browser_cfg = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            external_links = result.links.get("external", [])
            print(f"External links found ({len(external_links)}):")
            social_links_found = 0
            for link_info in external_links:
                print(f"  - {link_info.get('href')}")
                if any(domain in link_info.get('href', '') for domain in crawl4ai_config.SOCIAL_MEDIA_DOMAINS):
                    social_links_found +=1
            
            assert social_links_found == 0, f"Found {social_links_found} social media links, expected 0."
            # There are no "internal" links to example.com in this raw HTML case, so internal will be empty.
            # The "Normal Link" is considered external here if base_url is example.com and link is relative
            # For this test, it is important that social links are not present in *any* list.
            # Since they are external, they would appear in external_links if not filtered.
            
            # Check internal links too (though none are social here)
            internal_links = result.links.get("internal", [])
            for link_info in internal_links:
                 if any(domain in link_info.get('href', '') for domain in crawl4ai_config.SOCIAL_MEDIA_DOMAINS):
                    social_links_found +=1 # Should not happen
            assert social_links_found == 0, "Social media links found in internal links."

            print("SUCCESS: Social media links were excluded.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(exclude_social_media_links_example())
```

---
#### 6.11.4. Example: Providing a custom list of `exclude_domains` for link filtering.
Blacklist specific domains from appearing in the extracted links.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def custom_exclude_domains_example():
    html_with_various_links = """
    <html><body>
        <a href="https://example.com/page1">Allowed Internal</a>
        <a href="https://www.allowed-external.com/path">Allowed External</a>
        <a href="https://www.blocked-domain1.com/content">Blocked Domain 1</a>
        <a href="http://sub.blocked-domain2.org/another">Blocked Domain 2</a>
    </body></html>
    """
    excluded_domains_list = ["blocked-domain1.com", "blocked-domain2.org"]
    
    run_cfg = CrawlerRunConfig(
        url=f"raw://{html_with_various_links}",
        base_url="https://example.com",
        exclude_domains=excluded_domains_list,
        cache_mode=CacheMode.BYPASS
    )
    
    print(f"Crawling with exclude_domains: {excluded_domains_list}")
    browser_cfg = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(config=run_cfg)
        if result.success:
            all_links = result.links.get("internal", []) + result.links.get("external", [])
            print(f"Total links found after filtering: {len(all_links)}")
            
            blocked_found = False
            for link_info in all_links:
                print(f"  - {link_info.get('href')}")
                if any(blocked_domain in link_info.get('href', '') for blocked_domain in excluded_domains_list):
                    blocked_found = True
                    print(f"ERROR: Found a blocked domain link: {link_info.get('href')}")
            
            assert not blocked_found, "One or more explicitly excluded domains were found in links."
            assert len(all_links) == 2 # Only the two allowed links should remain
            print("SUCCESS: Specified domains were excluded from links.")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(custom_exclude_domains_example())
```

---
#### 6.11.5. Example: Enabling `exclude_internal_links=True` to remove links within the same domain.
Only external links will be kept in `result.links`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

async def exclude_internal_links_example():
    html_with_mixed_links = """
    <html><body>
        <a href="/internal-page1">Internal Page 1</a>
        <a href="https://example.com/internal-page2">Internal Page 2</a>
        <

---

