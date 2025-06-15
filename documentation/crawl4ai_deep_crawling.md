# Crawl4AI Custom LLM Context
Generated on: 2025-06-15T06:14:41.314Z
Total files: 3

---

## Deep Crawling - Memory
Source: crawl4ai_deep_crawling_memory_content.llm.md

Okay, I have read and processed the information. I will now generate the detailed "Foundational Memory" document for the `deep_crawling` component of `crawl4ai`, based on the outline from the previous step and the provided code snippets.

```markdown
# Detailed Foundational Memory for crawl4ai - deep_crawling Component

**Target Document Type:** memory
**Target Output Filename Suggestion:** `llm_memory_deep_crawling.md`
**Library Version Context:** 0.6.3 (from `crawl4ai/__version__.py`)
**Outline Generation Date:** 2024-05-24
---

## 1. Introduction to Deep Crawling

*   1.1. Purpose: The `deep_crawling` component provides functionalities for recursively crawling web pages starting from an initial URL. It includes strategies for different traversal orders (BFS, DFS, Best-First), mechanisms for filtering which URLs to visit, and methods for scoring URLs to prioritize crawling.
*   1.2. Core Concepts:
    *   1.2.1. Definition of Deep Crawling in Crawl4ai context: The process of discovering and fetching multiple web pages by following links from an initial set of URLs, adhering to specified depth, page limits, and filtering/scoring rules.
    *   1.2.2. Key Abstractions:
        *   `DeepCrawlStrategy`: Defines the algorithm for traversing linked web pages (e.g., BFS, DFS).
        *   `URLFilter`: Determines whether a discovered URL should be considered for crawling.
        *   `URLScorer`: Assigns a score to URLs to influence crawling priority, especially in strategies like Best-First.

## 2. `DeepCrawlStrategy` Interface and Implementations

*   **2.1. `DeepCrawlStrategy` (Abstract Base Class)**
    *   Source: `crawl4ai/deep_crawling/base_strategy.py`
    *   2.1.1. Purpose: Defines the abstract base class for all deep crawling strategies, outlining the core methods required for traversal logic, resource management, URL validation, and link discovery.
    *   2.1.2. Key Abstract Methods:
        *   `async def _arun_batch(self, start_url: str, crawler: AsyncWebCrawler, config: CrawlerRunConfig) -> List[CrawlResult]`:
            *   Description: Core logic for batch (non-streaming) deep crawling. Processes URLs level by level (or according to strategy) and returns all results once the crawl is complete or limits are met.
        *   `async def _arun_stream(self, start_url: str, crawler: AsyncWebCrawler, config: CrawlerRunConfig) -> AsyncGenerator[CrawlResult, None]`:
            *   Description: Core logic for streaming deep crawling. Processes URLs and yields `CrawlResult` objects as they become available.
        *   `async def shutdown(self) -> None`:
            *   Description: Cleans up any resources used by the deep crawl strategy, such as signaling cancellation events.
        *   `async def can_process_url(self, url: str, depth: int) -> bool`:
            *   Description: Validates a given URL and current depth against configured filters and limits to decide if it should be processed.
        *   `async def link_discovery(self, result: CrawlResult, source_url: str, current_depth: int, visited: Set[str], next_level: List[tuple], depths: Dict[str, int]) -> None`:
            *   Description: Extracts links from a `CrawlResult`, validates them using `can_process_url`, optionally scores them, and appends valid URLs (and their parent references) to the `next_level` list. Updates the `depths` dictionary for newly discovered URLs.
    *   2.1.3. Key Concrete Methods:
        *   `async def arun(self, start_url: str, crawler: AsyncWebCrawler, config: Optional[CrawlerRunConfig] = None) -> RunManyReturn`:
            *   Description: Main entry point for initiating a deep crawl. It checks if a `CrawlerRunConfig` is provided and then delegates to either `_arun_stream` or `_arun_batch` based on the `config.stream` flag.
        *   `def __call__(self, start_url: str, crawler: AsyncWebCrawler, config: CrawlerRunConfig)`:
            *   Description: Makes the strategy instance callable, directly invoking the `arun` method.
    *   2.1.4. Attributes:
        *   `_cancel_event (asyncio.Event)`: Event to signal cancellation of the crawl.
        *   `_pages_crawled (int)`: Counter for the number of pages successfully crawled.

*   **2.2. `BFSDeepCrawlStrategy`**
    *   Source: `crawl4ai/deep_crawling/bfs_strategy.py`
    *   2.2.1. Purpose: Implements a Breadth-First Search (BFS) deep crawling strategy, exploring all URLs at the current depth level before moving to the next.
    *   2.2.2. Inheritance: `DeepCrawlStrategy`
    *   2.2.3. Initialization (`__init__`)
        *   2.2.3.1. Signature:
            ```python
            def __init__(
                self,
                max_depth: int,
                filter_chain: FilterChain = FilterChain(),
                url_scorer: Optional[URLScorer] = None,
                include_external: bool = False,
                score_threshold: float = -float('inf'),
                max_pages: int = float('inf'),
                logger: Optional[logging.Logger] = None,
            ):
            ```
        *   2.2.3.2. Parameters:
            *   `max_depth (int)`: Maximum depth to crawl relative to the `start_url`.
            *   `filter_chain (FilterChain`, default: `FilterChain()`)`: A `FilterChain` instance to apply to discovered URLs.
            *   `url_scorer (Optional[URLScorer]`, default: `None`)`: An optional `URLScorer` to score URLs. If provided, URLs below `score_threshold` are skipped, and for crawls exceeding `max_pages`, higher-scored URLs are prioritized.
            *   `include_external (bool`, default: `False`)`: If `True`, allows crawling of URLs from external domains.
            *   `score_threshold (float`, default: `-float('inf')`)`: Minimum score (if `url_scorer` is used) for a URL to be processed.
            *   `max_pages (int`, default: `float('inf')`)`: Maximum total number of pages to crawl.
            *   `logger (Optional[logging.Logger]`, default: `None`)`: An optional logger instance. If `None`, a default logger is created.
    *   2.2.4. Key Implemented Methods:
        *   `_arun_batch(...)`: Implements BFS traversal by processing URLs level by level. It collects all results from a level before discovering links for the next level. All results are returned as a list upon completion.
        *   `_arun_stream(...)`: Implements BFS traversal, yielding `CrawlResult` objects as soon as they are processed within a level. Link discovery for the next level happens after all URLs in the current level are processed and their results yielded.
        *   `can_process_url(...)`: Validates URL format, applies the `filter_chain`, and checks depth limits. For the start URL (depth 0), filtering is bypassed.
        *   `link_discovery(...)`: Extracts internal (and optionally external) links, normalizes them, checks against `visited` set and `can_process_url`. If a `url_scorer` is present and `max_pages` limit is a concern, it scores and sorts valid links, selecting the top ones within `remaining_capacity`.
        *   `shutdown(...)`: Sets an internal `_cancel_event` to signal graceful termination and records the end time in `stats`.
    *   2.2.5. Key Attributes/Properties:
        *   `stats (TraversalStats)`: [Read-only] - Instance of `TraversalStats` tracking the progress and statistics of the crawl.
        *   `max_depth (int)`: Maximum crawl depth.
        *   `filter_chain (FilterChain)`: The filter chain used.
        *   `url_scorer (Optional[URLScorer])`: The URL scorer used.
        *   `include_external (bool)`: Flag for including external URLs.
        *   `score_threshold (float)`: URL score threshold.
        *   `max_pages (int)`: Maximum pages to crawl.

*   **2.3. `DFSDeepCrawlStrategy`**
    *   Source: `crawl4ai/deep_crawling/dfs_strategy.py`
    *   2.3.1. Purpose: Implements a Depth-First Search (DFS) deep crawling strategy, exploring as far as possible along each branch before backtracking.
    *   2.3.2. Inheritance: `BFSDeepCrawlStrategy` (Note: Leverages much of the `BFSDeepCrawlStrategy`'s infrastructure but overrides traversal logic to use a stack.)
    *   2.3.3. Initialization (`__init__`)
        *   2.3.3.1. Signature: (Same as `BFSDeepCrawlStrategy`)
            ```python
            def __init__(
                self,
                max_depth: int,
                filter_chain: FilterChain = FilterChain(),
                url_scorer: Optional[URLScorer] = None,
                include_external: bool = False,
                score_threshold: float = -float('inf'),
                max_pages: int = infinity,
                logger: Optional[logging.Logger] = None,
            ):
            ```
        *   2.3.3.2. Parameters: Same as `BFSDeepCrawlStrategy`.
    *   2.3.4. Key Overridden/Implemented Methods:
        *   `_arun_batch(...)`: Implements DFS traversal using a LIFO stack. Processes one URL at a time, discovers its links, and adds them to the stack (typically in reverse order of discovery to maintain a natural DFS path). Collects all results in a list.
        *   `_arun_stream(...)`: Implements DFS traversal using a LIFO stack, yielding `CrawlResult` for each processed URL as it becomes available. Discovered links are added to the stack for subsequent processing.

*   **2.4. `BestFirstCrawlingStrategy`**
    *   Source: `crawl4ai/deep_crawling/bff_strategy.py`
    *   2.4.1. Purpose: Implements a Best-First Search deep crawling strategy, prioritizing URLs based on scores assigned by a `URLScorer`. It uses a priority queue to manage URLs to visit.
    *   2.4.2. Inheritance: `DeepCrawlStrategy`
    *   2.4.3. Initialization (`__init__`)
        *   2.4.3.1. Signature:
            ```python
            def __init__(
                self,
                max_depth: int,
                filter_chain: FilterChain = FilterChain(),
                url_scorer: Optional[URLScorer] = None,
                include_external: bool = False,
                max_pages: int = float('inf'),
                logger: Optional[logging.Logger] = None,
            ):
            ```
        *   2.4.3.2. Parameters:
            *   `max_depth (int)`: Maximum depth to crawl.
            *   `filter_chain (FilterChain`, default: `FilterChain()`)`: Chain of filters to apply.
            *   `url_scorer (Optional[URLScorer]`, default: `None`)`: Scorer to rank URLs. Crucial for this strategy; if not provided, URLs might effectively be processed in FIFO order (score 0).
            *   `include_external (bool`, default: `False`)`: Whether to include external links.
            *   `max_pages (int`, default: `float('inf')`)`: Maximum number of pages to crawl.
            *   `logger (Optional[logging.Logger]`, default: `None`)`: Logger instance.
    *   2.4.4. Key Implemented Methods:
        *   `_arun_batch(...)`: Aggregates results from `_arun_best_first` into a list.
        *   `_arun_stream(...)`: Yields results from `_arun_best_first` as they are generated.
        *   `_arun_best_first(...)`: Core logic for best-first traversal. Uses an `asyncio.PriorityQueue` where items are `(score, depth, url, parent_url)`. URLs are processed in batches (default size 10) from the priority queue. Discovered links are scored and added to the queue.
    *   2.4.5. Key Attributes/Properties:
        *   `stats (TraversalStats)`: [Read-only] - Traversal statistics object.
        *   `BATCH_SIZE (int)`: [Class constant, default: 10] - Number of URLs to process concurrently from the priority queue.

## 3. URL Filtering Mechanisms

*   **3.1. `URLFilter` (Abstract Base Class)**
    *   Source: `crawl4ai/deep_crawling/filters.py`
    *   3.1.1. Purpose: Defines the abstract base class for all URL filters, providing a common interface for deciding whether a URL should be processed.
    *   3.1.2. Key Abstract Methods:
        *   `apply(self, url: str) -> bool`:
            *   Description: Abstract method that must be implemented by subclasses. It takes a URL string and returns `True` if the URL passes the filter (should be processed), and `False` otherwise.
    *   3.1.3. Key Attributes/Properties:
        *   `name (str)`: [Read-only] - The name of the filter, typically the class name.
        *   `stats (FilterStats)`: [Read-only] - An instance of `FilterStats` to track how many URLs were processed, passed, and rejected by this filter.
        *   `logger (logging.Logger)`: [Read-only] - A logger instance specific to this filter, initialized lazily.
    *   3.1.4. Key Concrete Methods:
        *   `_update_stats(self, passed: bool) -> None`: Updates the `stats` object (total, passed, rejected counts).

*   **3.2. `FilterChain`**
    *   Source: `crawl4ai/deep_crawling/filters.py`
    *   3.2.1. Purpose: Manages a sequence of `URLFilter` instances. A URL must pass all filters in the chain to be considered valid.
    *   3.2.2. Initialization (`__init__`)
        *   3.2.2.1. Signature:
            ```python
            def __init__(self, filters: List[URLFilter] = None):
            ```
        *   3.2.2.2. Parameters:
            *   `filters (List[URLFilter]`, default: `None`)`: An optional list of `URLFilter` instances to initialize the chain with. If `None`, an empty chain is created.
    *   3.2.3. Key Public Methods:
        *   `add_filter(self, filter_: URLFilter) -> FilterChain`:
            *   Description: Adds a new `URLFilter` instance to the end of the chain.
            *   Returns: `(FilterChain)` - The `FilterChain` instance itself, allowing for method chaining.
        *   `async def apply(self, url: str) -> bool`:
            *   Description: Applies each filter in the chain to the given URL. If any filter returns `False` (rejects the URL), this method immediately returns `False`. If all filters pass, it returns `True`. Handles both synchronous and asynchronous `apply` methods of individual filters.
            *   Returns: `(bool)` - `True` if the URL passes all filters, `False` otherwise.
    *   3.2.4. Key Attributes/Properties:
        *   `filters (Tuple[URLFilter, ...])`: [Read-only] - An immutable tuple containing the `URLFilter` instances in the chain.
        *   `stats (FilterStats)`: [Read-only] - An instance of `FilterStats` tracking the aggregated statistics for the entire chain (total URLs processed, passed, and rejected by the chain as a whole).

*   **3.3. `URLPatternFilter`**
    *   Source: `crawl4ai/deep_crawling/filters.py`
    *   3.3.1. Purpose: Filters URLs based on whether they match a list of specified string patterns. Supports glob-style wildcards and regular expressions.
    *   3.3.2. Inheritance: `URLFilter`
    *   3.3.3. Initialization (`__init__`)
        *   3.3.3.1. Signature:
            ```python
            def __init__(
                self,
                patterns: Union[str, Pattern, List[Union[str, Pattern]]],
                use_glob: bool = True, # Deprecated, glob is always used for strings if not regex
                reverse: bool = False,
            ):
            ```
        *   3.3.3.2. Parameters:
            *   `patterns (Union[str, Pattern, List[Union[str, Pattern]]])`: A single pattern string/compiled regex, or a list of such patterns. String patterns are treated as glob patterns by default unless they are identifiable as regex (e.g., start with `^`, end with `$`, contain `\d`).
            *   `use_glob (bool`, default: `True`)`: [Deprecated] This parameter's functionality is now implicitly handled by pattern detection.
            *   `reverse (bool`, default: `False`)`: If `True`, the filter rejects URLs that match any of the patterns. If `False` (default), it accepts URLs that match any pattern and rejects those that don't match any.
    *   3.3.4. Key Implemented Methods:
        *   `apply(self, url: str) -> bool`:
            *   Description: Checks if the URL matches any of the configured patterns. Simple suffix/prefix/domain patterns are checked first for performance. For more complex patterns, it uses `fnmatch.translate` (for glob-like strings) or compiled regex objects. The outcome is affected by the `reverse` flag.
    *   3.3.5. Internal Categorization:
        *   `PATTERN_TYPES`: A dictionary mapping pattern types (SUFFIX, PREFIX, DOMAIN, PATH, REGEX) to integer constants.
        *   `_simple_suffixes (Set[str])`: Stores simple suffix patterns (e.g., `.html`).
        *   `_simple_prefixes (Set[str])`: Stores simple prefix patterns (e.g., `/blog/`).
        *   `_domain_patterns (List[Pattern])`: Stores compiled regex for domain-specific patterns (e.g., `*.example.com`).
        *   `_path_patterns (List[Pattern])`: Stores compiled regex for more general path patterns.

*   **3.4. `ContentTypeFilter`**
    *   Source: `crawl4ai/deep_crawling/filters.py`
    *   3.4.1. Purpose: Filters URLs based on their expected content type, primarily by inferring it from the file extension in the URL.
    *   3.4.2. Inheritance: `URLFilter`
    *   3.4.3. Initialization (`__init__`)
        *   3.4.3.1. Signature:
            ```python
            def __init__(
                self,
                allowed_types: Union[str, List[str]],
                check_extension: bool = True,
                ext_map: Dict[str, str] = _MIME_MAP, # _MIME_MAP is internal
            ):
            ```
        *   3.4.3.2. Parameters:
            *   `allowed_types (Union[str, List[str]])`: A single MIME type string (e.g., "text/html") or a list of allowed MIME types. Can also be partial types like "image/" to allow all image types.
            *   `check_extension (bool`, default: `True`)`: If `True` (default), the filter attempts to determine the content type by looking at the URL's file extension. If `False`, all URLs pass this filter (unless `allowed_types` is empty).
            *   `ext_map (Dict[str, str]`, default: `ContentTypeFilter._MIME_MAP`)`: A dictionary mapping file extensions to their corresponding MIME types. A comprehensive default map is provided.
    *   3.4.4. Key Implemented Methods:
        *   `apply(self, url: str) -> bool`:
            *   Description: Extracts the file extension from the URL. If `check_extension` is `True` and an extension is found, it checks if the inferred MIME type (or the extension itself if MIME type is unknown) is among the `allowed_types`. If no extension is found, it typically allows the URL (assuming it might be an HTML page or similar).
    *   3.4.5. Static Methods:
        *   `_extract_extension(url: str) -> str`: [Cached] Extracts the file extension from a URL path, handling query parameters and fragments.
    *   3.4.6. Class Variables:
        *   `_MIME_MAP (Dict[str, str])`: A class-level dictionary mapping common file extensions to MIME types.

*   **3.5. `DomainFilter`**
    *   Source: `crawl4ai/deep_crawling/filters.py`
    *   3.5.1. Purpose: Filters URLs based on a whitelist of allowed domains or a blacklist of blocked domains. Supports subdomain matching.
    *   3.5.2. Inheritance: `URLFilter`
    *   3.5.3. Initialization (`__init__`)
        *   3.5.3.1. Signature:
            ```python
            def __init__(
                self,
                allowed_domains: Union[str, List[str]] = None,
                blocked_domains: Union[str, List[str]] = None,
            ):
            ```
        *   3.5.3.2. Parameters:
            *   `allowed_domains (Union[str, List[str]]`, default: `None`)`: A single domain string or a list of domain strings. If provided, only URLs whose domain (or a subdomain thereof) is in this list will pass.
            *   `blocked_domains (Union[str, List[str]]`, default: `None`)`: A single domain string or a list of domain strings. URLs whose domain (or a subdomain thereof) is in this list will be rejected.
    *   3.5.4. Key Implemented Methods:
        *   `apply(self, url: str) -> bool`:
            *   Description: Extracts the domain from the URL. First, checks if the domain is in `_blocked_domains` (rejects if true). Then, if `_allowed_domains` is specified, checks if the domain is in that list (accepts if true). If `_allowed_domains` is not specified and the URL was not blocked, it passes.
    *   3.5.5. Static Methods:
        *   `_normalize_domains(domains: Union[str, List[str]]) -> Set[str]`: Converts input domains to a set of lowercase strings.
        *   `_is_subdomain(domain: str, parent_domain: str) -> bool`: Checks if `domain` is a subdomain of (or equal to) `parent_domain`.
        *   `_extract_domain(url: str) -> str`: [Cached] Extracts the domain name from a URL.

*   **3.6. `ContentRelevanceFilter`**
    *   Source: `crawl4ai/deep_crawling/filters.py`
    *   3.6.1. Purpose: Filters URLs by fetching their `<head>` section, extracting text content (title, meta tags), and scoring its relevance against a given query using the BM25 algorithm.
    *   3.6.2. Inheritance: `URLFilter`
    *   3.6.3. Initialization (`__init__`)
        *   3.6.3.1. Signature:
            ```python
            def __init__(
                self,
                query: str,
                threshold: float,
                k1: float = 1.2,
                b: float = 0.75,
                avgdl: int = 1000,
            ):
            ```
        *   3.6.3.2. Parameters:
            *   `query (str)`: The query string to assess relevance against.
            *   `threshold (float)`: The minimum BM25 score required for the URL to be considered relevant and pass the filter.
            *   `k1 (float`, default: `1.2`)`: BM25 k1 parameter (term frequency saturation).
            *   `b (float`, default: `0.75`)`: BM25 b parameter (length normalization).
            *   `avgdl (int`, default: `1000`)`: Assumed average document length for BM25 calculations (typically based on the head content).
    *   3.6.4. Key Implemented Methods:
        *   `async def apply(self, url: str) -> bool`:
            *   Description: Asynchronously fetches the HTML `<head>` content of the URL using `HeadPeeker.peek_html`. Extracts title and meta description/keywords. Calculates the BM25 score of this combined text against the `query`. Returns `True` if the score is >= `threshold`.
    *   3.6.5. Helper Methods:
        *   `_build_document(self, fields: Dict) -> str`: Constructs a weighted document string from title and meta tags.
        *   `_tokenize(self, text: str) -> List[str]`: Simple whitespace tokenizer.
        *   `_bm25(self, document: str) -> float`: Calculates the BM25 score.

*   **3.7. `SEOFilter`**
    *   Source: `crawl4ai/deep_crawling/filters.py`
    *   3.7.1. Purpose: Filters URLs by performing a quantitative SEO quality assessment based on the content of their `<head>` section (e.g., title length, meta description presence, canonical tags, robots meta tags, schema.org markup).
    *   3.7.2. Inheritance: `URLFilter`
    *   3.7.3. Initialization (`__init__`)
        *   3.7.3.1. Signature:
            ```python
            def __init__(
                self,
                threshold: float = 0.65,
                keywords: List[str] = None,
                weights: Dict[str, float] = None,
            ):
            ```
        *   3.7.3.2. Parameters:
            *   `threshold (float`, default: `0.65`)`: The minimum aggregated SEO score (typically 0.0 to 1.0 range, though individual factor weights can exceed 1) required for the URL to pass.
            *   `keywords (List[str]`, default: `None`)`: A list of keywords to check for presence in the title.
            *   `weights (Dict[str, float]`, default: `None`)`: A dictionary to override default weights for various SEO factors (e.g., `{"title_length": 0.2, "canonical": 0.15}`).
    *   3.7.4. Key Implemented Methods:
        *   `async def apply(self, url: str) -> bool`:
            *   Description: Asynchronously fetches the HTML `<head>` content. Calculates scores for individual SEO factors (title length, keyword presence, meta description, canonical tag, robots meta tag, schema.org presence, URL quality). Aggregates these scores using the defined `weights`. Returns `True` if the total score is >= `threshold`.
    *   3.7.5. Helper Methods (Scoring Factors):
        *   `_score_title_length(self, title: str) -> float`
        *   `_score_keyword_presence(self, text: str) -> float`
        *   `_score_meta_description(self, desc: str) -> float`
        *   `_score_canonical(self, canonical: str, original: str) -> float`
        *   `_score_schema_org(self, html: str) -> float`
        *   `_score_url_quality(self, parsed_url) -> float`
    *   3.7.6. Class Variables:
        *   `DEFAULT_WEIGHTS (Dict[str, float])`: Default weights for each SEO factor.

*   **3.8. `FilterStats` Data Class**
    *   Source: `crawl4ai/deep_crawling/filters.py`
    *   3.8.1. Purpose: A data class to track statistics for URL filtering operations, including total URLs processed, passed, and rejected.
    *   3.8.2. Fields:
        *   `_counters (array.array)`: An array of unsigned integers storing counts for `[total, passed, rejected]`.
    *   3.8.3. Properties:
        *   `total_urls (int)`: Returns the total number of URLs processed.
        *   `passed_urls (int)`: Returns the number of URLs that passed the filter.
        *   `rejected_urls (int)`: Returns the number of URLs that were rejected.

## 4. URL Scoring Mechanisms

*   **4.1. `URLScorer` (Abstract Base Class)**
    *   Source: `crawl4ai/deep_crawling/scorers.py`
    *   4.1.1. Purpose: Defines the abstract base class for all URL scorers. Scorers assign a numerical value to URLs, which can be used to prioritize crawling.
    *   4.1.2. Key Abstract Methods:
        *   `_calculate_score(self, url: str) -> float`:
            *   Description: Abstract method to be implemented by subclasses. It takes a URL string and returns a raw numerical score.
    *   4.1.3. Key Concrete Methods:
        *   `score(self, url: str) -> float`:
            *   Description: Calculates the final score for a URL by calling `_calculate_score` and multiplying the result by the scorer's `weight`. It also updates the internal `ScoringStats`.
            *   Returns: `(float)` - The weighted score.
    *   4.1.4. Key Attributes/Properties:
        *   `weight (ctypes.c_float)`: [Read-write] - The weight assigned to this scorer. The raw score calculated by `_calculate_score` will be multiplied by this weight. Default is 1.0. Stored as `ctypes.c_float` for memory efficiency.
        *   `stats (ScoringStats)`: [Read-only] - An instance of `ScoringStats` that tracks statistics for this scorer (number of URLs scored, total score, min/max scores).

*   **4.2. `KeywordRelevanceScorer`**
    *   Source: `crawl4ai/deep_crawling/scorers.py`
    *   4.2.1. Purpose: Scores URLs based on the presence and frequency of specified keywords within the URL string itself.
    *   4.2.2. Inheritance: `URLScorer`
    *   4.2.3. Initialization (`__init__`)
        *   4.2.3.1. Signature:
            ```python
            def __init__(self, keywords: List[str], weight: float = 1.0, case_sensitive: bool = False):
            ```
        *   4.2.3.2. Parameters:
            *   `keywords (List[str])`: A list of keyword strings to search for in the URL.
            *   `weight (float`, default: `1.0`)`: The weight to apply to the calculated score.
            *   `case_sensitive (bool`, default: `False`)`: If `True`, keyword matching is case-sensitive. Otherwise, both the URL and keywords are converted to lowercase for matching.
    *   4.2.4. Key Implemented Methods:
        *   `_calculate_score(self, url: str) -> float`:
            *   Description: Counts how many of the provided `keywords` are present in the `url`. The score is the ratio of matched keywords to the total number of keywords (0.0 to 1.0).
    *   4.2.5. Helper Methods:
        *   `_url_bytes(self, url: str) -> bytes`: [Cached] Converts URL to bytes, lowercasing if not case-sensitive.

*   **4.3. `PathDepthScorer`**
    *   Source: `crawl4ai/deep_crawling/scorers.py`
    *   4.3.1. Purpose: Scores URLs based on their path depth (number of segments in the URL path). It favors URLs closer to an `optimal_depth`.
    *   4.3.2. Inheritance: `URLScorer`
    *   4.3.3. Initialization (`__init__`)
        *   4.3.3.1. Signature:
            ```python
            def __init__(self, optimal_depth: int = 3, weight: float = 1.0):
            ```
        *   4.3.3.2. Parameters:
            *   `optimal_depth (int`, default: `3`)`: The path depth considered ideal. URLs at this depth get the highest score.
            *   `weight (float`, default: `1.0`)`: The weight to apply to the calculated score.
    *   4.3.4. Key Implemented Methods:
        *   `_calculate_score(self, url: str) -> float`:
            *   Description: Calculates the path depth of the URL. The score is `1.0 / (1.0 + abs(depth - optimal_depth))`, meaning URLs at `optimal_depth` score 1.0, and scores decrease as depth deviates. Uses a lookup table for common small differences for speed.
    *   4.3.5. Static Methods:
        *   `_quick_depth(path: str) -> int`: [Cached] Efficiently calculates path depth without full URL parsing.

*   **4.4. `ContentTypeScorer`**
    *   Source: `crawl4ai/deep_crawling/scorers.py`
    *   4.4.1. Purpose: Scores URLs based on their inferred content type, typically derived from the file extension.
    *   4.4.2. Inheritance: `URLScorer`
    *   4.4.3. Initialization (`__init__`)
        *   4.4.3.1. Signature:
            ```python
            def __init__(self, type_weights: Dict[str, float], weight: float = 1.0):
            ```
        *   4.4.3.2. Parameters:
            *   `type_weights (Dict[str, float])`: A dictionary mapping file extensions (e.g., "html", "pdf") or MIME type patterns (e.g., "text/html", "image/") to scores. Patterns ending with '$' are treated as exact extension matches.
            *   `weight (float`, default: `1.0`)`: The weight to apply to the calculated score.
    *   4.4.4. Key Implemented Methods:
        *   `_calculate_score(self, url: str) -> float`:
            *   Description: Extracts the file extension from the URL. Looks up the score in `type_weights` first by exact extension match (if pattern ends with '$'), then by general extension. If no direct match, it might try matching broader MIME type categories if defined in `type_weights`. Returns 0.0 if no match found.
    *   4.4.5. Static Methods:
        *   `_quick_extension(url: str) -> str`: [Cached] Efficiently extracts file extension.

*   **4.5. `FreshnessScorer`**
    *   Source: `crawl4ai/deep_crawling/scorers.py`
    *   4.5.1. Purpose: Scores URLs based on dates found within the URL string, giving higher scores to more recent dates.
    *   4.5.2. Inheritance: `URLScorer`
    *   4.5.3. Initialization (`__init__`)
        *   4.5.3.1. Signature:
            ```python
            def __init__(self, weight: float = 1.0, current_year: int = [datetime.date.today().year]): # Actual default is dynamic
            ```
        *   4.5.3.2. Parameters:
            *   `weight (float`, default: `1.0`)`: The weight to apply to the calculated score.
            *   `current_year (int`, default: `datetime.date.today().year`)`: The reference year to calculate freshness against.
    *   4.5.4. Key Implemented Methods:
        *   `_calculate_score(self, url: str) -> float`:
            *   Description: Uses a regex to find year patterns (YYYY) in the URL. If multiple years are found, it uses the latest valid year. The score is higher for years closer to `current_year`, using a predefined lookup for small differences or a decay function for larger differences. If no year is found, a default score (0.5) is returned.
    *   4.5.5. Helper Methods:
        *   `_extract_year(self, url: str) -> Optional[int]`: [Cached] Extracts the most recent valid year from the URL.

*   **4.6. `DomainAuthorityScorer`**
    *   Source: `crawl4ai/deep_crawling/scorers.py`
    *   4.6.1. Purpose: Scores URLs based on a predefined list of domain authority weights. This allows prioritizing or de-prioritizing URLs from specific domains.
    *   4.6.2. Inheritance: `URLScorer`
    *   4.6.3. Initialization (`__init__`)
        *   4.6.3.1. Signature:
            ```python
            def __init__(
                self,
                domain_weights: Dict[str, float],
                default_weight: float = 0.5,
                weight: float = 1.0,
            ):
            ```
        *   4.6.3.2. Parameters:
            *   `domain_weights (Dict[str, float])`: A dictionary mapping domain names (e.g., "example.com") to their authority scores (typically between 0.0 and 1.0).
            *   `default_weight (float`, default: `0.5`)`: The score to assign to URLs whose domain is not found in `domain_weights`.
            *   `weight (float`, default: `1.0`)`: The overall weight to apply to the calculated score.
    *   4.6.4. Key Implemented Methods:
        *   `_calculate_score(self, url: str) -> float`:
            *   Description: Extracts the domain from the URL. If the domain is in `_domain_weights`, its corresponding score is returned. Otherwise, `_default_weight` is returned. Prioritizes top domains for faster lookup.
    *   4.6.5. Static Methods:
        *   `_extract_domain(url: str) -> str`: [Cached] Efficiently extracts the domain from a URL.

*   **4.7. `CompositeScorer`**
    *   Source: `crawl4ai/deep_crawling/scorers.py`
    *   4.7.1. Purpose: Combines the scores from multiple `URLScorer` instances. Each constituent scorer contributes its weighted score to the final composite score.
    *   4.7.2. Inheritance: `URLScorer`
    *   4.7.3. Initialization (`__init__`)
        *   4.7.3.1. Signature:
            ```python
            def __init__(self, scorers: List[URLScorer], normalize: bool = True):
            ```
        *   4.7.3.2. Parameters:
            *   `scorers (List[URLScorer])`: A list of `URLScorer` instances to be combined.
            *   `normalize (bool`, default: `True`)`: If `True`, the final composite score is normalized by dividing the sum of weighted scores by the number of scorers. This can help keep scores in a more consistent range.
    *   4.7.4. Key Implemented Methods:
        *   `_calculate_score(self, url: str) -> float`:
            *   Description: Iterates through all scorers in its list, calls their `score(url)` method (which applies individual weights), and sums up these scores. If `normalize` is `True`, divides the total sum by the number of scorers.
    *   4.7.5. Key Concrete Methods (overrides `URLScorer.score`):
        *   `score(self, url: str) -> float`:
            *   Description: Calculates the composite score and updates its own `ScoringStats`. Note: The individual scorers' stats are updated when their `score` methods are called internally.

*   **4.8. `ScoringStats` Data Class**
    *   Source: `crawl4ai/deep_crawling/scorers.py`
    *   4.8.1. Purpose: A data class to track statistics for URL scoring operations, including the number of URLs scored, total score, and min/max scores.
    *   4.8.2. Fields:
        *   `_urls_scored (int)`: Count of URLs scored.
        *   `_total_score (float)`: Sum of all scores.
        *   `_min_score (Optional[float])`: Minimum score encountered.
        *   `_max_score (Optional[float])`: Maximum score encountered.
    *   4.8.3. Key Methods:
        *   `update(self, score: float) -> None`: Updates the statistics with a new score.
        *   `get_average(self) -> float`: Calculates and returns the average score.
        *   `get_min(self) -> float`: Lazily initializes and returns the minimum score.
        *   `get_max(self) -> float`: Lazily initializes and returns the maximum score.

## 5. `DeepCrawlDecorator`

*   Source: `crawl4ai/deep_crawling/base_strategy.py`
*   5.1. Purpose: A decorator class that transparently adds deep crawling functionality to the `AsyncWebCrawler.arun` method if a `deep_crawl_strategy` is specified in the `CrawlerRunConfig`.
*   5.2. Initialization (`__init__`)
    *   5.2.1. Signature:
        ```python
        def __init__(self, crawler: AsyncWebCrawler):
        ```
    *   5.2.2. Parameters:
        *   `crawler (AsyncWebCrawler)`: The `AsyncWebCrawler` instance whose `arun` method is to be decorated.
*   5.3. `__call__` Method
    *   5.3.1. Signature:
        ```python
        @wraps(original_arun)
        async def wrapped_arun(url: str, config: CrawlerRunConfig = None, **kwargs):
        ```
    *   5.3.2. Functionality: This method wraps the original `arun` method of the `AsyncWebCrawler`.
        *   It checks if `config` is provided, has a `deep_crawl_strategy` set, and if `DeepCrawlDecorator.deep_crawl_active` context variable is `False` (to prevent recursion).
        *   If these conditions are met:
            *   It sets `DeepCrawlDecorator.deep_crawl_active` to `True`.
            *   It calls the `arun` method of the specified `config.deep_crawl_strategy`.
            *   It handles potential streaming results from the strategy by wrapping them in an async generator.
            *   Finally, it resets `DeepCrawlDecorator.deep_crawl_active` to `False`.
        *   If the conditions are not met, it calls the original `arun` method of the crawler.
*   5.4. Class Variable:
    *   `deep_crawl_active (ContextVar)`:
        *   Purpose: A `contextvars.ContextVar` used as a flag to indicate if a deep crawl is currently in progress for the current asynchronous context. This prevents the decorator from re-triggering deep crawling if the strategy itself calls the crawler's `arun` or `arun_many` methods.
        *   Default Value: `False`.

## 6. `TraversalStats` Data Model

*   Source: `crawl4ai/models.py`
*   6.1. Purpose: A data class for storing and tracking statistics related to a deep crawl traversal.
*   6.2. Fields:
    *   `start_time (datetime)`: The timestamp (Python `datetime` object) when the traversal process began. Default: `datetime.now()`.
    *   `end_time (Optional[datetime])`: The timestamp when the traversal process completed. Default: `None`.
    *   `urls_processed (int)`: The total number of URLs that were successfully fetched and processed. Default: `0`.
    *   `urls_failed (int)`: The total number of URLs that resulted in an error during fetching or processing. Default: `0`.
    *   `urls_skipped (int)`: The total number of URLs that were skipped (e.g., due to filters, already visited, or depth limits). Default: `0`.
    *   `total_depth_reached (int)`: The maximum depth reached from the start URL during the crawl. Default: `0`.
    *   `current_depth (int)`: The current depth level being processed by the crawler (can fluctuate during the crawl, especially for BFS). Default: `0`.

## 7. Configuration for Deep Crawling (`CrawlerRunConfig`)

*   Source: `crawl4ai/async_configs.py`
*   7.1. Purpose: `CrawlerRunConfig` is the primary configuration object passed to `AsyncWebCrawler.arun()` and `AsyncWebCrawler.arun_many()`. It contains various settings that control the behavior of a single crawl run, including those specific to deep crawling.
*   7.2. Relevant Fields:
    *   `deep_crawl_strategy (Optional[DeepCrawlStrategy])`:
        *   Type: `Optional[DeepCrawlStrategy]` (where `DeepCrawlStrategy` is the ABC from `crawl4ai.deep_crawling.base_strategy`)
        *   Default: `None`
        *   Description: Specifies the deep crawling strategy instance (e.g., `BFSDeepCrawlStrategy`, `DFSDeepCrawlStrategy`, `BestFirstCrawlingStrategy`) to be used for the crawl. If `None`, deep crawling is disabled, and only the initial URL(s) will be processed.
    *   *Note: Parameters like `max_depth`, `max_pages`, `filter_chain`, `url_scorer`, `score_threshold`, and `include_external` are not direct attributes of `CrawlerRunConfig` for deep crawling. Instead, they are passed to the constructor of the chosen `DeepCrawlStrategy` instance, which is then assigned to `CrawlerRunConfig.deep_crawl_strategy`.*

## 8. Utility Functions

*   **8.1. `normalize_url_for_deep_crawl(url: str, source_url: str) -> str`**
    *   Source: `crawl4ai/deep_crawling/utils.py` (or `crawl4ai/utils.py` if it's a general utility)
    *   8.1.1. Purpose: Normalizes a URL found during deep crawling. This typically involves resolving relative URLs against the `source_url` to create absolute URLs and removing URL fragments (`#fragment`).
    *   8.1.2. Signature: `def normalize_url_for_deep_crawl(url: str, source_url: str) -> str:`
    *   8.1.3. Parameters:
        *   `url (str)`: The URL string to be normalized.
        *   `source_url (str)`: The URL of the page where the `url` was discovered. This is used as the base for resolving relative paths.
    *   8.1.4. Returns: `(str)` - The normalized, absolute URL without fragments.

*   **8.2. `efficient_normalize_url_for_deep_crawl(url: str, source_url: str) -> str`**
    *   Source: `crawl4ai/deep_crawling/utils.py` (or `crawl4ai/utils.py`)
    *   8.2.1. Purpose: Provides a potentially more performant version of URL normalization specifically for deep crawling scenarios, likely employing optimizations to avoid repeated or complex parsing operations. (Note: Based on the provided code, this appears to be the same as `normalize_url_for_deep_crawl` if only one is present, or it might contain specific internal optimizations not exposed differently at the API level but used by strategies).
    *   8.2.2. Signature: `def efficient_normalize_url_for_deep_crawl(url: str, source_url: str) -> str:`
    *   8.2.3. Parameters:
        *   `url (str)`: The URL string to be normalized.
        *   `source_url (str)`: The URL of the page where the `url` was discovered.
    *   8.2.4. Returns: `(str)` - The normalized, absolute URL, typically without fragments.

## 9. PDF Processing Integration (`crawl4ai.processors.pdf`)
    *   9.1. Overview of PDF processing in Crawl4ai: While not directly part of the `deep_crawling` package, PDF processing components can be used in conjunction if a deep crawl discovers PDF URLs and they need to be processed. The `PDFCrawlerStrategy` can fetch PDFs, and `PDFContentScrapingStrategy` can extract content from them.
    *   **9.2. `PDFCrawlerStrategy`**
        *   Source: `crawl4ai/processors/pdf/__init__.py`
        *   9.2.1. Purpose: An `AsyncCrawlerStrategy` designed to "crawl" PDF files. In practice, this usually means downloading the PDF content. It returns a minimal `AsyncCrawlResponse` that signals to a `ContentScrapingStrategy` (like `PDFContentScrapingStrategy`) that the content is a PDF.
        *   9.2.2. Inheritance: `AsyncCrawlerStrategy`
        *   9.2.3. Initialization (`__init__`)
            *   9.2.3.1. Signature: `def __init__(self, logger: AsyncLogger = None):`
            *   9.2.3.2. Parameters:
                *   `logger (AsyncLogger`, default: `None`)`: An optional logger instance.
        *   9.2.4. Key Methods:
            *   `async def crawl(self, url: str, **kwargs) -> AsyncCrawlResponse`:
                *   Description: For a PDF URL, this method typically signifies that the URL points to a PDF. It constructs an `AsyncCrawlResponse` with a `Content-Type` header of `application/pdf` and a placeholder HTML. The actual PDF processing (downloading and content extraction) is usually handled by a subsequent scraping strategy.
    *   **9.3. `PDFContentScrapingStrategy`**
        *   Source: `crawl4ai/processors/pdf/__init__.py`
        *   9.3.1. Purpose: A `ContentScrapingStrategy` specialized in extracting text, images (optional), and metadata from PDF files. It uses a `PDFProcessorStrategy` (like `NaivePDFProcessorStrategy`) internally.
        *   9.3.2. Inheritance: `ContentScrapingStrategy`
        *   9.3.3. Initialization (`__init__`)
            *   9.3.3.1. Signature:
                ```python
                def __init__(self,
                             save_images_locally: bool = False,
                             extract_images: bool = False,
                             image_save_dir: str = None,
                             batch_size: int = 4,
                             logger: AsyncLogger = None):
                ```
            *   9.3.3.2. Parameters:
                *   `save_images_locally (bool`, default: `False`)`: If `True`, extracted images will be saved to the local disk.
                *   `extract_images (bool`, default: `False`)`: If `True`, attempts to extract images from the PDF.
                *   `image_save_dir (str`, default: `None`)`: The directory where extracted images will be saved if `save_images_locally` is `True`.
                *   `batch_size (int`, default: `4`)`: The number of PDF pages to process in parallel batches (if the underlying processor supports it).
                *   `logger (AsyncLogger`, default: `None`)`: An optional logger instance.
        *   9.3.4. Key Methods:
            *   `scrape(self, url: str, html: str, **params) -> ScrapingResult`:
                *   Description: Takes the URL (which should point to a PDF or a local PDF path) and processes it. It downloads the PDF if it's a remote URL, then uses the internal `pdf_processor` to extract content. It formats the extracted text into basic HTML and collects image and link information.
            *   `async def ascrape(self, url: str, html: str, **kwargs) -> ScrapingResult`:
                *   Description: Asynchronous version of the `scrape` method, typically by running the synchronous `scrape` method in a separate thread.
        *   9.3.5. Helper Methods:
            *   `_get_pdf_path(self, url: str) -> str`: Downloads a PDF from a URL to a temporary file if it's not a local path.
    *   **9.4. `NaivePDFProcessorStrategy`**
        *   Source: `crawl4ai/processors/pdf/processor.py`
        *   9.4.1. Purpose: A concrete implementation of `PDFProcessorStrategy` that uses `PyPDF2` (or similar libraries if extended) to extract text, images, and metadata from PDF documents page by page or in batches.
        *   9.4.2. Initialization (`__init__`)
            *   Signature: `def __init__(self, image_dpi: int = 144, image_quality: int = 85, extract_images: bool = True, save_images_locally: bool = False, image_save_dir: Optional[Path] = None, batch_size: int = 4)`
            *   Parameters: [Details parameters for image extraction quality, saving, and batch processing size.]
        *   9.4.3. Key Methods:
            *   `process(self, pdf_path: Path) -> PDFProcessResult`:
                *   Description: Processes a single PDF file sequentially, page by page. Extracts metadata, text, and optionally images from each page.
            *   `process_batch(self, pdf_path: Path) -> PDFProcessResult`:
                *   Description: Processes a PDF file by dividing its pages into batches and processing these batches in parallel using a thread pool, potentially speeding up extraction for large PDFs.
        *   9.4.4. Helper Methods:
            *   `_process_page(self, page, image_dir: Optional[Path]) -> PDFPage`: Processes a single PDF page object.
            *   `_extract_images(self, page, image_dir: Optional[Path]) -> List[Dict]`: Extracts images from a page.
            *   `_extract_links(self, page) -> List[str]`: Extracts hyperlinks from a page.
            *   `_extract_metadata(self, pdf_path: Path, reader=None) -> PDFMetadata`: Extracts metadata from the PDF.
    *   **9.5. PDF Data Models**
        *   Source: `crawl4ai/processors/pdf/processor.py`
        *   9.5.1. `PDFMetadata`:
            *   Purpose: Stores metadata extracted from a PDF document.
            *   Fields:
                *   `title (Optional[str])`: The title of the PDF.
                *   `author (Optional[str])`: The author(s) of the PDF.
                *   `producer (Optional[str])`: The software used to produce the PDF.
                *   `created (Optional[datetime])`: The creation date of the PDF.
                *   `modified (Optional[datetime])`: The last modification date of the PDF.
                *   `pages (int)`: The total number of pages in the PDF. Default: `0`.
                *   `encrypted (bool)`: `True` if the PDF is encrypted, `False` otherwise. Default: `False`.
                *   `file_size (Optional[int])`: The size of the PDF file in bytes. Default: `None`.
        *   9.5.2. `PDFPage`:
            *   Purpose: Stores content extracted from a single page of a PDF document.
            *   Fields:
                *   `page_number (int)`: The page number (1-indexed).
                *   `raw_text (str)`: The raw text extracted from the page. Default: `""`.
                *   `markdown (str)`: Markdown representation of the page content. Default: `""`.
                *   `html (str)`: Basic HTML representation of the page content. Default: `""`.
                *   `images (List[Dict])`: A list of dictionaries, each representing an extracted image with details like format, path/data, dimensions. Default: `[]`.
                *   `links (List[str])`: A list of hyperlink URLs found on the page. Default: `[]`.
                *   `layout (List[Dict])`: Information about the layout of text elements on the page (e.g., coordinates). Default: `[]`.
        *   9.5.3. `PDFProcessResult`:
            *   Purpose: Encapsulates the results of processing a PDF document.
            *   Fields:
                *   `metadata (PDFMetadata)`: The metadata of the processed PDF.
                *   `pages (List[PDFPage])`: A list of `PDFPage` objects, one for each page processed.
                *   `processing_time (float)`: The time taken to process the PDF, in seconds. Default: `0.0`.
                *   `version (str)`: The version of the PDF processor. Default: `"1.1"`.

## 10. Version Information (`crawl4ai.__version__`)
*   Source: `crawl4ai/__version__.py`
*   10.1. `__version__ (str)`: A string representing the current installed version of the `crawl4ai` library (e.g., "0.6.3").

## 11. Asynchronous Configuration (`crawl4ai.async_configs`)
    *   11.1. Overview: The `crawl4ai.async_configs` module contains configuration classes used throughout the library, including those relevant for network requests like proxies (`ProxyConfig`) and general crawler/browser behavior.
    *   **11.2. `ProxyConfig`**
        *   Source: `crawl4ai/async_configs.py` (and `crawl4ai/proxy_strategy.py`)
        *   11.2.1. Purpose: Represents the configuration for a single proxy server, including its address, port, and optional authentication credentials.
        *   11.2.2. Initialization (`__init__`)
            *   11.2.2.1. Signature:
                ```python
                def __init__(
                    self,
                    server: str,
                    username: Optional[str] = None,
                    password: Optional[str] = None,
                    ip: Optional[str] = None,
                ):
                ```
            *   11.2.2.2. Parameters:
                *   `server (str)`: The proxy server URL (e.g., "http://proxy.example.com:8080", "socks5://proxy.example.com:1080").
                *   `username (Optional[str]`, default: `None`)`: The username for proxy authentication, if required.
                *   `password (Optional[str]`, default: `None`)`: The password for proxy authentication, if required.
                *   `ip (Optional[str]`, default: `None`)`: Optionally, the specific IP address of the proxy server. If not provided, it's inferred from the `server` URL.
        *   11.2.3. Key Static Methods:
            *   `from_string(proxy_str: str) -> ProxyConfig`:
                *   Description: Creates a `ProxyConfig` instance from a string representation. Expected format is "ip:port:username:password" or "ip:port".
                *   Returns: `(ProxyConfig)`
            *   `from_dict(proxy_dict: Dict) -> ProxyConfig`:
                *   Description: Creates a `ProxyConfig` instance from a dictionary.
                *   Returns: `(ProxyConfig)`
            *   `from_env(env_var: str = "PROXIES") -> List[ProxyConfig]`:
                *   Description: Loads a list of proxy configurations from a comma-separated string in an environment variable.
                *   Returns: `(List[ProxyConfig])`
        *   11.2.4. Key Methods:
            *   `to_dict(self) -> Dict`: Converts the `ProxyConfig` instance to a dictionary.
            *   `clone(self, **kwargs) -> ProxyConfig`: Creates a copy of the instance, optionally updating attributes with `kwargs`.

    *   **11.3. `ProxyRotationStrategy` (ABC)**
        *   Source: `crawl4ai/proxy_strategy.py`
        *   11.3.1. Purpose: Abstract base class defining the interface for proxy rotation strategies.
        *   11.3.2. Key Abstract Methods:
            *   `async def get_next_proxy(self) -> Optional[ProxyConfig]`: Asynchronously gets the next `ProxyConfig` from the strategy.
            *   `def add_proxies(self, proxies: List[ProxyConfig])`: Adds a list of `ProxyConfig` objects to the strategy's pool.
    *   **11.4. `RoundRobinProxyStrategy`**
        *   Source: `crawl4ai/proxy_strategy.py`
        *   11.4.1. Purpose: A simple proxy rotation strategy that cycles through a list of proxies in a round-robin fashion.
        *   11.4.2. Inheritance: `ProxyRotationStrategy`
        *   11.4.3. Initialization (`__init__`)
            *   11.4.3.1. Signature: `def __init__(self, proxies: List[ProxyConfig] = None):`
            *   11.4.3.2. Parameters:
                *   `proxies (List[ProxyConfig]`, default: `None`)`: An optional initial list of `ProxyConfig` objects.
        *   11.4.4. Key Implemented Methods:
            *   `add_proxies(self, proxies: List[ProxyConfig])`: Adds new proxies to the internal list and reinitializes the cycle.
            *   `async def get_next_proxy(self) -> Optional[ProxyConfig]`: Returns the next proxy from the cycle. Returns `None` if no proxies are available.

## 12. HTML to Markdown Conversion (`crawl4ai.markdown_generation_strategy`)
    *   12.1. `MarkdownGenerationStrategy` (ABC)
        *   Source: `crawl4ai/markdown_generation_strategy.py`
        *   12.1.1. Purpose: Abstract base class defining the interface for strategies that convert HTML content to Markdown.
        *   12.1.2. Key Abstract Methods:
            *   `generate_markdown(self, input_html: str, base_url: str = "", html2text_options: Optional[Dict[str, Any]] = None, content_filter: Optional[RelevantContentFilter] = None, citations: bool = True, **kwargs) -> MarkdownGenerationResult`:
                *   Description: Abstract method to convert the given `input_html` string into a `MarkdownGenerationResult` object.
                *   Parameters:
                    *   `input_html (str)`: The HTML content to convert.
                    *   `base_url (str`, default: `""`)`: The base URL used for resolving relative links within the HTML.
                    *   `html2text_options (Optional[Dict[str, Any]]`, default: `None`)`: Options to pass to the underlying HTML-to-text conversion library.
                    *   `content_filter (Optional[RelevantContentFilter]`, default: `None`)`: An optional filter to apply to the HTML before Markdown conversion, potentially to extract only relevant parts.
                    *   `citations (bool`, default: `True`)`: If `True`, attempts to convert hyperlinks into Markdown citations with a reference list.
                    *   `**kwargs`: Additional keyword arguments.
                *   Returns: `(MarkdownGenerationResult)`
    *   12.2. `DefaultMarkdownGenerator`
        *   Source: `crawl4ai/markdown_generation_strategy.py`
        *   12.2.1. Purpose: The default implementation of `MarkdownGenerationStrategy`. It uses the `CustomHTML2Text` class (an enhanced `html2text.HTML2Text`) for the primary conversion and can optionally apply a `RelevantContentFilter`.
        *   12.2.2. Inheritance: `MarkdownGenerationStrategy`
        *   12.2.3. Initialization (`__init__`)
            *   12.2.3.1. Signature:
                ```python
                def __init__(
                    self,
                    content_filter: Optional[RelevantContentFilter] = None,
                    options: Optional[Dict[str, Any]] = None,
                    content_source: str = "cleaned_html", # "raw_html", "fit_html"
                ):
                ```
            *   12.2.3.2. Parameters:
                *   `content_filter (Optional[RelevantContentFilter]`, default: `None`)`: An instance of a content filter strategy (e.g., `BM25ContentFilter`, `PruningContentFilter`) to be applied to the `input_html` before Markdown conversion. If `None`, no pre-filtering is done.
                *   `options (Optional[Dict[str, Any]]`, default: `None`)`: A dictionary of options to configure the `CustomHTML2Text` converter (e.g., `{"body_width": 0, "ignore_links": False}`).
                *   `content_source (str`, default: `"cleaned_html"`)`: Specifies which HTML source to use for Markdown generation if multiple are available (e.g., from `CrawlResult`). Options: `"cleaned_html"` (default), `"raw_html"`, `"fit_html"`. This parameter is primarily used when the generator is part of a larger crawling pipeline.
        *   12.2.4. Key Methods:
            *   `generate_markdown(self, input_html: str, base_url: str = "", html2text_options: Optional[Dict[str, Any]] = None, content_filter: Optional[RelevantContentFilter] = None, citations: bool = True, **kwargs) -> MarkdownGenerationResult`:
                *   Description: Converts HTML to Markdown. If a `content_filter` is provided (either at init or as an argument), it's applied first to get "fit_html". Then, `CustomHTML2Text` converts the chosen HTML (input_html or fit_html) to raw Markdown. If `citations` is True, links in the raw Markdown are converted to citation format.
                *   Returns: `(MarkdownGenerationResult)`
            *   `convert_links_to_citations(self, markdown: str, base_url: str = "") -> Tuple[str, str]`:
                *   Description: Parses Markdown text, identifies links, replaces them with citation markers (e.g., `[text]^(1)`), and generates a corresponding list of references.
                *   Returns: `(Tuple[str, str])` - A tuple containing the Markdown with citations and the Markdown string of references.

## 13. Content Filtering (`crawl4ai.content_filter_strategy`)
    *   13.1. `RelevantContentFilter` (ABC)
        *   Source: `crawl4ai/content_filter_strategy.py`
        *   13.1.1. Purpose: Abstract base class for strategies that filter HTML content to extract only the most relevant parts, typically before Markdown conversion or further processing.
        *   13.1.2. Key Abstract Methods:
            *   `filter_content(self, html: str) -> List[str]`:
                *   Description: Abstract method that takes an HTML string and returns a list of strings, where each string is a chunk of HTML deemed relevant.
    *   13.2. `BM25ContentFilter`
        *   Source: `crawl4ai/content_filter_strategy.py`
        *   13.2.1. Purpose: Filters HTML content by extracting text chunks and scoring their relevance to a user query (or an inferred page query) using the BM25 algorithm.
        *   13.2.2. Inheritance: `RelevantContentFilter`
        *   13.2.3. Initialization (`__init__`)
            *   13.2.3.1. Signature:
                ```python
                def __init__(
                    self,
                    user_query: Optional[str] = None,
                    bm25_threshold: float = 1.0,
                    language: str = "english",
                ):
                ```
            *   13.2.3.2. Parameters:
                *   `user_query (Optional[str]`, default: `None`)`: The query to compare content against. If `None`, the filter attempts to extract a query from the page's metadata.
                *   `bm25_threshold (float`, default: `1.0`)`: The minimum BM25 score for a text chunk to be considered relevant.
                *   `language (str`, default: `"english"`)`: The language used for stemming tokens.
        *   13.2.4. Key Implemented Methods:
            *   `filter_content(self, html: str, min_word_threshold: int = None) -> List[str]`: Parses HTML, extracts text chunks (paragraphs, list items, etc.), scores them with BM25 against the query, and returns the HTML of chunks exceeding the threshold.
    *   13.3. `PruningContentFilter`
        *   Source: `crawl4ai/content_filter_strategy.py`
        *   13.3.1. Purpose: Filters HTML content by recursively pruning less relevant parts of the DOM tree based on a composite score (text density, link density, tag weights, etc.).
        *   13.3.2. Inheritance: `RelevantContentFilter`
        *   13.3.3. Initialization (`__init__`)
            *   13.3.3.1. Signature:
                ```python
                def __init__(
                    self,
                    user_query: Optional[str] = None,
                    min_word_threshold: Optional[int] = None,
                    threshold_type: str = "fixed", # or "dynamic"
                    threshold: float = 0.48,
                ):
                ```
            *   13.3.3.2. Parameters:
                *   `user_query (Optional[str]`, default: `None`)`: [Not directly used by pruning logic but inherited].
                *   `min_word_threshold (Optional[int]`, default: `None`)`: Minimum word count for an element to be considered for scoring initially (default behavior might be more nuanced).
                *   `threshold_type (str`, default: `"fixed"`)`: Specifies how the `threshold` is applied. "fixed" uses the direct value. "dynamic" adjusts the threshold based on content characteristics.
                *   `threshold (float`, default: `0.48`)`: The score threshold for pruning. Elements below this score are removed.
        *   13.3.4. Key Implemented Methods:
            *   `filter_content(self, html: str, min_word_threshold: int = None) -> List[str]`: Parses HTML, applies the pruning algorithm to the body, and returns the remaining significant HTML blocks as a list of strings.
    *   13.4. `LLMContentFilter`
        *   Source: `crawl4ai/content_filter_strategy.py`
        *   13.4.1. Purpose: Uses a Large Language Model (LLM) to determine the relevance of HTML content chunks based on a given instruction.
        *   13.4.2. Inheritance: `RelevantContentFilter`
        *   13.4.3. Initialization (`__init__`)
            *   13.4.3.1. Signature:
                ```python
                def __init__(
                    self,
                    llm_config: Optional[LLMConfig] = None,
                    instruction: Optional[str] = None,
                    chunk_token_threshold: int = CHUNK_TOKEN_THRESHOLD, # Default from config
                    overlap_rate: float = OVERLAP_RATE,            # Default from config
                    word_token_rate: float = WORD_TOKEN_RATE,        # Default from config
                    verbose: bool = False,
                    logger: Optional[AsyncLogger] = None,
                    ignore_cache: bool = True
                ):
                ```
            *   13.4.3.2. Parameters:
                *   `llm_config (Optional[LLMConfig])`: Configuration for the LLM (provider, API key, model, etc.).
                *   `instruction (Optional[str])`: The instruction given to the LLM to guide content filtering (e.g., "Extract only the main article content, excluding headers, footers, and ads.").
                *   `chunk_token_threshold (int)`: Maximum number of tokens per chunk sent to the LLM.
                *   `overlap_rate (float)`: Percentage of overlap between consecutive chunks.
                *   `word_token_rate (float)`: Estimated ratio of words to tokens, used for chunking.
                *   `verbose (bool`, default: `False`)`: Enables verbose logging for LLM operations.
                *   `logger (Optional[AsyncLogger]`, default: `None`)`: Custom logger instance.
                *   `ignore_cache (bool`, default: `True`)`: If `True`, bypasses any LLM response caching for this operation.
        *   13.4.4. Key Implemented Methods:
            *   `filter_content(self, html: str, ignore_cache: bool = True) -> List[str]`:
                *   Description: Chunks the input HTML. For each chunk, it sends a request to the configured LLM with the chunk and the `instruction`. The LLM is expected to return the relevant part of the chunk. These relevant parts are then collected and returned.
```

---


## Deep Crawling - Reasoning
Source: crawl4ai_deep_crawling_reasoning_content.llm.md

```markdown
# Detailed Outline for crawl4ai - deep_crawling Component

**Target Document Type:** reasoning
**Target Output Filename Suggestion:** `reasoning_deep_crawling.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2025-05-24
---

## 1. Introduction to Deep Crawling with Crawl4ai

Deep crawling is a fundamental capability for comprehensive web data extraction. This section introduces what deep crawling means in the context of Crawl4ai, why it's essential, and provides an overview of how Crawl4ai empowers you to perform sophisticated, multi-page crawls.

*   **1.1. What is Deep Crawling and Why Do You Need It?**
    *   **Explanation of deep crawling:** Deep crawling, unlike single-page scraping, involves systematically discovering and fetching web pages by following hyperlinks from an initial set of "seed" URLs. It's the process of exploring a website's structure to gather information spread across multiple pages. Crawl4ai's deep crawling component automates this exploration, allowing you to define the boundaries and priorities of your crawl.
    *   **Common scenarios requiring deep crawling:**
        *   **Building a comprehensive site index:** Discovering all pages within a website for search engine indexing or sitemap generation. For example, indexing all articles on a news website or all products on an e-commerce site.
        *   **Scraping data from multiple interconnected pages:** Extracting detailed information that isn't available on a single page, such as product specifications from individual product pages linked from a category page.
        *   **Discovering all content within a specific domain or sub-domain:** Ensuring all relevant content under `blog.example.com` is found and processed.
        *   **SEO analysis and site structure understanding:** Mapping out how pages are linked, identifying orphaned pages, or analyzing internal link distribution.
        *   **Monitoring website changes:** Regularly crawling a site to detect new content, updated pages, or broken links.
    *   **Core problems solved by Crawl4ai's `deep_crawling` component:**
        *   **URL Frontier Management:** Efficiently managing the queue of URLs to visit.
        *   **Visited URL Tracking:** Preventing re-crawling of already processed pages.
        *   **Depth Control:** Limiting how many "hops" the crawler takes from the seed URL.
        *   **Scope Management:** Using filters to define which URLs are relevant and should be processed.
        *   **Crawl Prioritization:** Using scorers to decide which URLs are more important to visit next.
        *   **Resource Management:** Providing mechanisms (`max_pages`) to limit the overall crawl size.

*   **1.2. When to Choose Deep Crawling Over Single-Page Crawling**
    *   **Decision factors:**
        *   **Data Distribution:** If the information you need is spread across multiple interlinked pages (e.g., an e-commerce site with category pages, product listing pages, and individual product detail pages), deep crawling is necessary. Single-page crawling is sufficient if all required data is on one page or a known, small set of URLs.
        *   **Link Discovery:** If you need to discover new URLs dynamically based on the content of previously crawled pages, deep crawling is the way to go.
        *   **Site Mapping/Full Site Analysis:** If your goal is to understand the structure of an entire site or a significant portion of it, deep crawling is essential.
    *   **Trade-offs:**
        *   **Comprehensiveness vs. Speed/Resources:** Deep crawling provides more comprehensive data but typically takes longer and consumes more bandwidth and processing resources than single-page crawls.
        *   **Complexity:** Configuring an effective deep crawl (with appropriate strategies, filters, and scorers) can be more complex than a simple single-page fetch.
        *   **Scope Control:** Without proper filters and limits (`max_depth`, `max_pages`), deep crawls can easily become too broad and inefficient.

*   **1.3. Overview of Crawl4ai's Deep Crawling Architecture**
    *   **High-level explanation:**
        Crawl4ai's deep crawling is orchestrated by a `DeepCrawlStrategy` (like `BFSDeepCrawlStrategy`, `DFSDeepCrawlStrategy`, or `BestFirstCrawlingStrategy`). When a page is crawled, this strategy is responsible for:
        1.  Extracting new links from the page.
        2.  Applying a `FilterChain` (a sequence of `URLFilter` instances) to determine if a discovered URL should be considered for further crawling.
        3.  Optionally, using a `URLScorer` (especially with `BestFirstCrawlingStrategy`) to assign a priority to valid URLs, influencing the order in which they are visited.
        4.  Adding valid (and potentially scored) URLs to a frontier (queue or priority queue) for future processing.
        5.  Managing visited URLs to avoid redundant crawls and controlling the depth and extent of the crawl.
    *   **Role of `DeepCrawlDecorator`:**
        This decorator is an internal mechanism that transparently adds deep crawling capabilities to the standard `AsyncWebCrawler.arun()` method when a `deep_crawl_strategy` is specified in `CrawlerRunConfig`. Users typically don't interact with it directly but should be aware that it's the component enabling this extended functionality.
    *   `* Diagram: [Conceptual diagram of the deep crawling workflow:
        Seed URL -> AsyncWebCrawler.arun() -> DeepCrawlDecorator -> (if deep_crawl_strategy in CrawlerRunConfig) -> DeepCrawlStrategy.arun()
        Within DeepCrawlStrategy.arun():
            Fetch Page -> Process Page (Extract Links) -> For each Link:
                -> FilterChain.apply(link) -> (if valid) -> URLScorer.score(link) -> Add to Frontier -> Select Next URL from Frontier -> Fetch Page ... ]`

## 2. Core Concepts: Strategies, Filters, and Scorers

To effectively use deep crawling, understanding its three main pillars is crucial: the strategy dictates *how* you explore, filters decide *what* to explore, and scorers (especially for Best-First) determine *in what order* to explore.

*   **2.1. Understanding `DeepCrawlStrategy`**
    *   **Purpose:** The `DeepCrawlStrategy` is the heart of the deep crawling process. It's an interface (an abstract base class) that defines the logic for traversing a website. Concrete implementations provide different exploration patterns.
    *   **Why different strategies exist:**
        *   **BFS (Breadth-First Search):** Explores websites level by level. Good for a complete, systematic scan up to a certain depth.
        *   **DFS (Depth-First Search):** Explores one branch of a website as deeply as possible before backtracking. Useful for following specific paths.
        *   **Best-First Search:** Uses a scoring mechanism to prioritize URLs, visiting the most "promising" ones first. Ideal for targeted crawling where relevance is key.
    *   **How to select the right strategy for your goal:**
        *   **Comprehensive Site Mapping:** BFS is often preferred.
        *   **Finding Specific Content Quickly (if path is known or can be guided):** DFS can be efficient.
        *   **Targeted Crawling (e.g., based on keywords, freshness, authority):** Best-First is the most powerful.
        *   **Resource Constraints:** BFS can be memory-intensive for wide sites. DFS might be better for deep, narrow sites if `max_depth` is managed. Best-First's resource usage depends on the scorer and queue size.
        *   `* Decision Table:
            | Goal                          | Recommended Strategy | Key Considerations                      |
            |-------------------------------|----------------------|-----------------------------------------|
            | Full site index up to depth X | BFS                  | Memory for wide sites, `max_depth`      |
            | Explore specific section deep | DFS                  | `max_depth`, avoiding traps             |
            | Find most relevant pages      | Best-First           | Scorer quality, `max_pages`             |
            | Quick overview of a site      | BFS with low `max_depth`| Speed vs. completeness                |
            `
*   **2.2. The Role of URL Filters (`URLFilter` & `FilterChain`)**
    *   **Purpose:** Filters are essential for controlling the scope and efficiency of your deep crawl. They decide whether a discovered URL should be added to the crawling queue or discarded. Without filters, a crawler might wander into irrelevant parts of a website, get stuck in "crawler traps" (like infinite calendars), or consume excessive resources.
    *   **How `FilterChain` allows combining multiple filters:** `FilterChain` takes a list of `URLFilter` instances. When a URL is evaluated, it's passed through each filter in the chain sequentially. If *any* filter in the chain rejects the URL (returns `False`), the URL is discarded. It must pass *all* filters to be considered valid. This allows for creating sophisticated, layered filtering logic.
    *   **Benefits of effective filtering:**
        *   **Efficiency:** Reduces the number of pages fetched and processed, saving time and bandwidth.
        *   **Relevance:** Focuses the crawl on content that matches your objectives.
        *   **Resource Management:** Prevents excessive memory usage by keeping the URL frontier manageable.
        *   **Avoiding Traps:** Helps avoid sections of a website that might lead to an infinite number of unique URLs (e.g., calendars, faceted search results with many parameter combinations).

*   **2.3. The Power of URL Scoring (`URLScorer` & `CompositeScorer`)**
    *   **Purpose:** URL scoring is primarily used by the `BestFirstCrawlingStrategy`. It assigns a numerical score to each valid URL, indicating its priority. The strategy then picks URLs from the frontier based on these scores (typically highest score first). This allows the crawler to intelligently prioritize which parts of a website to explore.
    *   **How `CompositeScorer` enables multi-faceted URL evaluation:** Often, a single criterion isn't enough to determine a URL's importance. `CompositeScorer` allows you to combine multiple individual `URLScorer` instances (e.g., one for keyword relevance, one for freshness, one for domain authority). Each individual scorer contributes to an overall score, often with weights you can define, providing a more nuanced and effective prioritization.
    *   **Impact of scoring on crawl efficiency and result quality:**
        *   **Efficiency:** Good scoring can dramatically improve efficiency by guiding the crawler to relevant content much faster, especially if you have a `max_pages` limit.
        *   **Result Quality:** By prioritizing high-value pages, scoring ensures that the most important data is collected even if the crawl is stopped before exploring the entire site. The definition of "high-value" is determined by your scoring logic.

## 3. Deep Crawling Strategies In-Depth

Let's dive into each specific strategy, understanding its mechanics, use cases, and how to configure it.

*   **3.1. Breadth-First Search (`BFSDeepCrawlStrategy`)**
    *   **3.1.1. Understanding BFS Traversal**
        *   **What is BFS?** Breadth-First Search explores a website layer by layer. It starts with the seed URL(s) (level 0), then crawls all pages directly linked from the seeds (level 1), then all pages linked from level 1 pages (level 2), and so on. It uses a FIFO (First-In, First-Out) queue to manage URLs for each level.
        *   **Pros:**
            *   Finds the shortest path to all reachable pages.
            *   Systematic and predictable exploration pattern.
            *   Good for getting a broad overview of a site's structure quickly, especially at shallow depths.
        *   **Cons:**
            *   Can consume significant memory for websites with a large number of links per page (wide sites), as it needs to store all URLs of a given level before moving to the next.
            *   May take a long time to reach content buried deep within the site structure.
        *   **Typical Use Cases:**
            *   Full site mapping up to a certain depth.
            *   Discovering all pages for a small to medium-sized website.
            *   Finding broken links or orphaned pages (when combined with analysis of all discovered URLs).
        *   `* Diagram: [Visual representation of BFS traversal, showing levels and queue behavior.
            Example:
                Level 0: A
                Queue: [A] -> Process A, discover B, C
                Level 1: B, C
                Queue: [B, C] -> Process B, discover D, E. Process C, discover F
                Level 2: D, E, F
                Queue: [D, E, F] -> ...
            ]`
    *   **3.1.2. Practical Usage of `BFSDeepCrawlStrategy`**
        *   **How to instantiate and pass it to `CrawlerRunConfig`:**
            ```python
            from crawl4ai import BFSDeepCrawlStrategy, CrawlerRunConfig

            bfs_strategy = BFSDeepCrawlStrategy(max_depth=3) # Example: crawl up to 3 levels deep
            run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)
            # ... then pass run_config to crawler.arun() or crawler.arun_many()
            ```
        *   **Key configuration parameters:**
            *   `max_depth (int)`: Crucial for BFS. Defines how many levels deep the crawl will go. A `max_depth` of 0 crawls only the seed URL(s). A `max_depth` of 1 crawls seeds and pages directly linked from them.
            *   `filter_chain (Optional[FilterChain])`: URLs discovered at each level are passed through this chain before being added to the next level's queue.
            *   `url_scorer (Optional[URLScorer])`: While BFS is primarily level-ordered, a scorer *can* be used to influence the processing order *within* a given level if multiple URLs are fetched concurrently in batches. However, it doesn't change the fundamental level-by-level exploration. (This is less common for pure BFS compared to Best-First).
            *   `max_pages (int, default=infinity)`: A global limit on the total number of pages to crawl. The crawl will stop if `max_pages` or `max_depth` is reached, whichever comes first.
            *   `include_external (bool, default=False)`: If `True`, BFS will also explore links to external domains, respecting `max_depth` for those external paths as well. Use with caution and strong `DomainFilter`s.
        *   `* Code Example: [Setting up a BFS crawl to explore 'example.com' up to depth 2, only HTML pages, max 100 pages]`
            ```python
            from crawl4ai import (
                AsyncWebCrawler, CrawlerRunConfig, BrowserConfig,
                BFSDeepCrawlStrategy, FilterChain, DomainFilter, ContentTypeFilter
            )
            import asyncio

            async def bfs_example_crawl():
                # Filters: Only allow 'example.com' and only HTML files
                filters = FilterChain(filters=[
                    DomainFilter(allowed_domains=["example.com"]),
                    ContentTypeFilter(allowed_types=['.html', '.htm'])
                ])

                # BFS Strategy: Max depth 2, max 100 pages, apply filters
                bfs_strategy = BFSDeepCrawlStrategy(
                    max_depth=2,
                    filter_chain=filters,
                    max_pages=100
                )

                run_config = CrawlerRunConfig(
                    deep_crawl_strategy=bfs_strategy,
                    verbose=True
                )

                browser_config = BrowserConfig(headless=True)
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    result_container = await crawler.arun(
                        url="https://example.com",
                        config=run_config
                    )
                    # In batch mode (default for arun without stream=True in strategy),
                    # result_container will be a list of CrawlResult objects
                    for i, result in enumerate(result_container):
                        if result.success:
                            print(f"Crawled {i+1}: {result.url} (Depth: {result.metadata.get('depth')})")
                        else:
                            print(f"Failed {i+1}: {result.url} - {result.error_message}")

            if __name__ == "__main__":
                asyncio.run(bfs_example_crawl())
            ```
    *   **3.1.3. Best Practices for BFS**
        *   **Memory Management:** For very wide sites (many links per page), BFS can consume a lot of memory because it holds all URLs of the current level. If memory is a concern, consider a lower `max_depth` or switching to DFS/Best-First for more targeted exploration.
        *   **Effective `max_depth`:** Choose `max_depth` carefully. A small increase in depth can lead to an exponential increase in pages crawled.
        *   **Filtering:** Always use `DomainFilter` to keep the crawl focused. Add other filters (`ContentTypeFilter`, `URLPatternFilter`) as needed to refine scope.
    *   **3.1.4. Common Pitfalls with BFS**
        *   **Excessive Memory on Large/Wide Sites:** Setting `max_depth` too high without considering site width can lead to out-of-memory errors.
        *   **Crawling Irrelevant Content:** Not using filters can result in crawling large, unwanted sections of a site or even external sites if `include_external` is accidentally enabled without proper domain filtering.
        *   **Time Consumption:** BFS aims for breadth, so reaching very specific, deep content might take longer than with DFS or a well-tuned Best-First strategy.

*   **3.2. Depth-First Search (`DFSDeepCrawlStrategy`)**
    *   **3.2.1. Understanding DFS Traversal**
        *   **What is DFS?** Depth-First Search explores as far as possible along each branch before backtracking. It uses a LIFO (Last-In, First-Out) stack to manage URLs. When it discovers new links on a page, those links are added to the top of the stack, and the crawler immediately proceeds to the newest link.
        *   **Pros:**
            *   Can reach deep content very quickly if it happens to be on the current exploration path.
            *   Potentially lower memory footprint for deep, narrow sites compared to BFS, as it doesn't need to store all URLs at a given level.
        *   **Cons:**
            *   Can get "stuck" exploring a very deep or infinite branch, potentially missing content in other, shallower branches if `max_pages` or another limit is hit.
            *   The order of discovery is less predictable than BFS and may not provide a balanced view of the site quickly.
        *   **Typical Use Cases:**
            *   Following a specific path through a website (e.g., a series of articles, a product configuration wizard).
            *   Exploring a single section of a website as deeply as possible.
            *   When memory is a primary concern and the target content is known to be deep.
        *   `* Diagram: [Visual representation of DFS traversal, showing stack behavior.
            Example:
                Stack: [A] -> Pop A, discover B, C. Push C, then B.
                Stack: [B, C] -> Pop B, discover D, E. Push E, then D.
                Stack: [D, E, C] -> Pop D ... and so on.
            ]`
    *   **3.2.2. Practical Usage of `DFSDeepCrawlStrategy`**
        *   **How to instantiate and pass it to `CrawlerRunConfig`:**
            ```python
            from crawl4ai import DFSDeepCrawlStrategy, CrawlerRunConfig

            dfs_strategy = DFSDeepCrawlStrategy(max_depth=5) # Example: explore up to 5 links deep
            run_config = CrawlerRunConfig(deep_crawl_strategy=dfs_strategy)
            ```
        *   **Key configuration parameters:**
            *   `max_depth (int)`: Critically important for DFS to prevent infinite loops or excessively deep crawls.
            *   `filter_chain (Optional[FilterChain])`: Essential for guiding DFS and preventing it from exploring irrelevant paths.
            *   `url_scorer (Optional[URLScorer])`: Less commonly used with pure DFS, as the stack naturally dictates order. If used, it might influence which of the newly discovered links from a page gets pushed to the stack (and thus processed) first.
            *   `max_pages (int, default=infinity)`: Stops the crawl if this limit is reached.
            *   `include_external (bool, default=False)`: Controls whether DFS follows external links.
        *   `* Code Example: [Setting up a DFS crawl to explore a blog, prioritizing paths under '/blog/archive/']`
            ```python
            from crawl4ai import (
                AsyncWebCrawler, CrawlerRunConfig, BrowserConfig,
                DFSDeepCrawlStrategy, FilterChain, URLPatternFilter
            )
            import asyncio

            async def dfs_example_crawl():
                # Filter to keep crawl within /blog/ subdirectories
                filters = FilterChain(filters=[
                    URLPatternFilter(patterns=["https://example.com/blog/.*"])
                ])

                dfs_strategy = DFSDeepCrawlStrategy(
                    max_depth=10,      # Allow going reasonably deep
                    filter_chain=filters,
                    max_pages=50       # But limit total pages
                )

                run_config = CrawlerRunConfig(
                    deep_crawl_strategy=dfs_strategy,
                    verbose=True
                )

                browser_config = BrowserConfig(headless=True)
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    # Using stream=True in strategy for immediate results
                    dfs_strategy.stream = True # Overriding here for demo
                    async for result in await crawler.arun(
                        url="https://example.com/blog/",
                        config=run_config
                    ):
                        if result.success:
                            print(f"Crawled (DFS): {result.url} (Depth: {result.metadata.get('depth')})")
                        else:
                            print(f"Failed (DFS): {result.url} - {result.error_message}")

            if __name__ == "__main__":
                asyncio.run(dfs_example_crawl())
            ```
    *   **3.2.3. Best Practices for DFS**
        *   **Mandatory `max_depth`:** Always set a reasonable `max_depth` to prevent the crawler from getting lost in very deep or cyclical paths.
        *   **Targeted Filtering:** Use `URLPatternFilter` or other specific filters to guide the DFS along the paths you're interested in.
        *   **Monitor `max_pages`:** If `max_pages` is hit before `max_depth` in many branches, your DFS might not be exploring the site effectively.
    *   **3.2.4. Common Pitfalls with DFS**
        *   **Crawler Traps:** DFS is particularly susceptible to getting stuck in "crawler traps" (e.g., links generating unique URLs infinitely, like calendars or poorly designed filters).
        *   **Missing Broad Content:** If relevant content is spread across many shallow branches, DFS might miss much of it if it goes deep into one branch and hits `max_pages`.
        *   **Order of Discovery:** The order in which pages are discovered can feel random if the site structure isn't well understood or filters aren't guiding the crawl.

*   **3.3. Best-First Search (`BestFirstCrawlingStrategy`)**
    *   **3.3.1. Understanding Best-First Traversal**
        *   **What is Best-First?** This strategy uses a priority queue to manage the URL frontier. Each URL added to the frontier is assigned a score by a `URLScorer`. The crawler always picks the URL with the highest score from the priority queue to process next.
        *   **Pros:**
            *   Highly efficient for targeted crawling when you can define what makes a URL "good" or "relevant."
            *   Focuses crawler resources on the most promising areas of a website first.
            *   Adaptable: By changing the scoring logic, you can radically alter the crawl's focus.
        *   **Cons:**
            *   Effectiveness is *heavily* dependent on the quality and design of the `URLScorer`. A bad scorer leads to a bad crawl.
            *   Can be more complex to configure due to the need to design and implement scoring logic.
            *   Might miss some relevant content if it consistently scores low and `max_pages` is reached.
        *   **Typical Use Cases:**
            *   Finding pages most relevant to a specific set of keywords.
            *   Prioritizing pages from high-authority domains or known good sources.
            *   Crawling recently updated or fresh content first.
            *   Combining multiple factors (e.g., relevance, freshness, authority) for sophisticated prioritization.
        *   `* Diagram: [Visual representation of Best-First traversal.
            1. Seed URL -> Scorer -> Add to PriorityQueue (URL, Score)
            2. Pop highest score URL from PQ -> Fetch & Process -> Discover Links
            3. For each Link: Filter -> (if valid) -> Scorer -> Add to PQ (Link, Score)
            4. Repeat from step 2.
            Show PQ reordering as new items are added with different scores.]`
    *   **3.3.2. Practical Usage of `BestFirstCrawlingStrategy`**
        *   **How to instantiate and pass it to `CrawlerRunConfig`:**
            ```python
            from crawl4ai import (
                BestFirstCrawlingStrategy, CrawlerRunConfig,
                KeywordRelevanceScorer, DomainFilter, FilterChain
            )

            # Scorer: Prioritize URLs with 'ai' and 'ethics'
            keyword_scorer = KeywordRelevanceScorer(keywords=['ai', 'ethics'], weight=1.0)

            # Filter: Only 'example.com'
            domain_filter = DomainFilter(allowed_domains=['example.com'])
            filter_chain = FilterChain(filters=[domain_filter])

            best_first_strategy = BestFirstCrawlingStrategy(
                url_scorer=keyword_scorer,
                filter_chain=filter_chain,
                max_depth=5,
                max_pages=200
            )
            run_config = CrawlerRunConfig(deep_crawl_strategy=best_first_strategy)
            ```
        *   **Crucial role of `url_scorer`:** This is the defining component. You *must* provide a `URLScorer` instance. This could be a single scorer or a `CompositeScorer`.
        *   **Interaction with `filter_chain`:** Filters are applied *before* scoring. Only URLs that pass all filters are then scored and considered for the priority queue.
        *   **Parameters:**
            *   `max_depth (int)`: Still relevant to prevent excessively deep exploration, even if scores guide the way.
            *   `max_pages (int, default=infinity)`: Important for limiting the overall crawl size.
            *   `include_external (bool, default=False)`: If `True`, external URLs that pass filters will also be scored and added to the queue.
        *   `* Code Example: [Setting up a Best-First crawl using CompositeScorer to find recent articles about "AI in finance" from specific financial news domains]`
            ```python
            from crawl4ai import (
                AsyncWebCrawler, CrawlerRunConfig, BrowserConfig,
                BestFirstCrawlingStrategy, FilterChain, DomainFilter,
                KeywordRelevanceScorer, FreshnessScorer, CompositeScorer
            )
            import asyncio
            from datetime import datetime

            async def best_first_example_crawl():
                # Scorers
                keyword_scorer = KeywordRelevanceScorer(
                    keywords=['ai', 'finance', 'fintech'],
                    weight=0.6
                )
                freshness_scorer = FreshnessScorer(
                    current_year=datetime.now().year,
                    weight=0.4
                )
                composite_scorer = CompositeScorer(
                    scorers=[keyword_scorer, freshness_scorer]
                )

                # Filters
                allowed_domains = ["reputablefinance.news", "fintechinsider.com"]
                filters = FilterChain(filters=[
                    DomainFilter(allowed_domains=allowed_domains)
                ])

                best_first_strategy = BestFirstCrawlingStrategy(
                    url_scorer=composite_scorer,
                    filter_chain=filters,
                    max_depth=4,
                    max_pages=100,
                    stream=True # Get results as they come
                )

                run_config = CrawlerRunConfig(
                    deep_crawl_strategy=best_first_strategy,
                    verbose=True
                )
                browser_config = BrowserConfig(headless=True)

                async with AsyncWebCrawler(config=browser_config) as crawler:
                    start_urls = [f"https://{domain}/" for domain in allowed_domains]
                    async for result in await crawler.arun_many(
                        urls=start_urls,
                        config=run_config
                    ):
                        if result.success:
                            print(f"Crawled (Best-First): {result.url} (Score: {result.metadata.get('score', 'N/A')}, Depth: {result.metadata.get('depth')})")

            if __name__ == "__main__":
                asyncio.run(best_first_example_crawl())
            ```
    *   **3.3.3. Best Practices for Best-First**
        *   **Design Effective Scoring:** The success of Best-First hinges on this. Think carefully about what makes a URL valuable for your goal.
        *   **Iterative Refinement:** Test your scorers. Observe the crawl path. Adjust weights and logic in your `CompositeScorer` or custom scorers based on results.
        *   **Balance Complexity and Performance:** While `CompositeScorer` is powerful, very complex scoring logic involving many external calls or heavy computations per URL can slow down the decision-making process.
        *   **Combine with Strong Filters:** Filters reduce the number of URLs that need to be scored, improving efficiency.
    *   **3.3.4. Common Pitfalls with Best-First**
        *   **Poor Scorer Configuration:** If the scorer doesn't align with your goals, the crawl will be misguided and inefficient (e.g., a keyword scorer with irrelevant keywords).
        *   **Score Normalization (if building custom composite logic):** Ensure scores from different components are on a somewhat comparable scale or that weights account for differences. `CompositeScorer` handles weighting but doesn't inherently normalize scores from sub-scorers.
        *   **Ignoring Potentially Valuable Branches:** If a relevant section of a site consistently scores low due to a quirk in the scoring logic, it might be missed if `max_pages` is too restrictive. Consider periodic "exploration" phases or adjusting scores.
        *   **Over-reliance on a Single Metric:** A `CompositeScorer` is often better than relying on just one type of score (e.g., just keywords) which might be too narrow.

## 4. Fine-Tuning Your Crawl: URL Filtering

Filters are your first line of defense against an unmanageable or irrelevant crawl. They ensure that only URLs meeting your criteria are even considered for fetching and further processing.

*   **4.1. The Importance of Effective Filtering**
    *   **Why filter?**
        *   **Save Resources:** Every skipped URL saves bandwidth, processing time, and memory.
        *   **Improve Speed:** A focused crawl finishes faster.
        *   **Enhance Relevance:** Ensures the data you collect is pertinent to your objectives.
        *   **Avoid Crawler Traps:** Prevents the crawler from getting stuck in infinite loops (e.g., calendars, endlessly paginated archives with slight URL variations).
        *   **Respect Site Policies:** Can be used to avoid crawling sensitive or disallowed sections (though `robots.txt` is the primary mechanism for this).
    *   **How `FilterChain` processes filters sequentially:**
        When you provide a `FilterChain` with multiple filters, a URL must pass *all* of them to be accepted. If `Filter1.apply(url)` returns `False`, the URL is rejected, and `Filter2`, `Filter3`, etc., are not even called for that URL. This "short-circuiting" behavior means you should order your filters strategically.
        `* Diagram: [URL -> Filter1 -> (if True) -> Filter2 -> (if True) -> Filter3 -> (if True) -> Accepted | (if False at any step) -> Rejected]`

*   **4.2. `DomainFilter`**
    *   **4.2.1. Purpose:** The most fundamental filter. It restricts the crawl to specific domains or subdomains (`allowed_domains`) and/or explicitly blocks certain domains (`blocked_domains`).
    *   **4.2.2. How it Works:** It extracts the netloc (e.g., `www.example.com`) from a URL.
        *   If `allowed_domains` is specified, the URL's domain (or a parent domain) must be in this list.
        *   If `blocked_domains` is specified, the URL's domain (or a parent domain) must *not* be in this list.
        *   If both are specified, it must satisfy the allow condition AND not satisfy the block condition.
        *   It handles subdomains correctly: if `example.com` is allowed, `blog.example.com` is also allowed. If `example.com` is blocked, `blog.example.com` is also blocked.
    *   **4.2.3. Configuration & Usage:**
        ```python
        from crawl4ai import DomainFilter, FilterChain

        # Allow only 'example.com' and its subdomains
        allow_example = DomainFilter(allowed_domains=["example.com"])

        # Block 'ads.example.com' and 'tracker.com'
        block_ads = DomainFilter(blocked_domains=["ads.example.com", "tracker.com"])

        # Combine them: only example.com, but not ads.example.com
        combined_filter = FilterChain(filters=[allow_example, block_ads])
        ```
        *   Wildcard usage is not directly supported in the `allowed_domains` list itself (e.g., `*.example.com`). You'd typically allow `example.com` which implicitly covers subdomains. For more complex pattern matching, use `URLPatternFilter`.
        *   `* Code Example: [Allowing 'blog.example.com' and 'docs.example.com', explicitly blocking 'ads.example.com', assuming 'example.com' is the main domain for other content.]`
            ```python
            # This setup means only blog.example.com and docs.example.com are allowed
            # and ads.example.com (if it were a subdomain of an allowed domain) would be blocked.
            # A more typical setup to crawl ONLY these two subdomains:
            specific_subdomains_filter = DomainFilter(allowed_domains=["blog.example.com", "docs.example.com"])

            # If you wanted to crawl example.com but exclude ads.example.com:
            crawl_main_exclude_ads = FilterChain(filters=[
                DomainFilter(allowed_domains=["example.com"]),
                DomainFilter(blocked_domains=["ads.example.com"])
            ])
            ```
    *   **4.2.4. Best Practices:**
        *   Almost always start your `FilterChain` with a `DomainFilter` specifying `allowed_domains` to keep your crawl focused.
        *   Be precise if you only want specific subdomains. Allowing a TLD (Top-Level Domain) like `.com` is generally not what you want unless you intend a very broad crawl.

*   **4.3. `ContentTypeFilter`**
    *   **4.3.1. Purpose:** To filter URLs based on their likely file extension, thereby inferring the content type. This is a quick way to avoid downloading large binary files, images, or unwanted document types.
    *   **4.3.2. How it Works:** By default (`check_extension=True`), it extracts the extension from the URL's path (e.g., `.html`, `.pdf`, `.jpg`). It then checks if this extension (or its corresponding MIME type via an internal map) is present in the `allowed_types`.
    *   **4.3.3. Configuration & Usage:**
        ```python
        from crawl4ai import ContentTypeFilter

        # Only allow HTML and PDF files
        html_pdf_filter = ContentTypeFilter(allowed_types=['.html', '.htm', '.pdf'])
        # OR by MIME type partial match (less common for this filter but possible):
        # html_pdf_filter_mime = ContentTypeFilter(allowed_types=['text/html', 'application/pdf'])
        ```
        *   The `allowed_types` can be a list of extensions (e.g., `'.jpg'`) or partial MIME types (e.g., `'image/'`, `'text/html'`).
        *   `check_extension=True` (default) is generally faster as it avoids needing actual content type from HTTP headers. Set to `False` if you must rely on `Content-Type` headers (note: this filter as shown in `filters.py` primarily works on extensions for pre-fetch filtering).
        *   `* Code Example: [Filtering to only allow HTML, HTM, and PHP files]`
            ```python
            webpage_filter = ContentTypeFilter(allowed_types=['.html', '.htm', '.php'])
            # This would allow URLs like:
            # https://example.com/page.html
            # https://example.com/article.php
            # But would block:
            # https://example.com/image.jpg
            # https://example.com/document.pdf
            ```
    *   **4.3.4. Best Practices:** Use this early in your filter chain to quickly discard URLs pointing to unwanted file types, saving bandwidth and processing for HEAD requests or full fetches that later filters might trigger.

*   **4.4. `URLPatternFilter`**
    *   **4.4.1. Purpose:** Provides fine-grained control over which URLs to process based on matching them against regular expressions or glob-style patterns.
    *   **4.4.2. How it Works:** It takes a list of `patterns`. For each URL, it checks if the URL string matches any of these patterns. The behavior depends on the `reverse` flag.
    *   **4.4.3. Configuration & Usage:**
        ```python
        from crawl4ai import URLPatternFilter

        # Allow only URLs under '/blog/' or '/products/'
        blog_products_filter = URLPatternFilter(
            patterns=[r".*/blog/.*", r".*/products/.*"] # Regex patterns
        )

        # Exclude URLs containing '/archive/' or '/temp/'
        exclude_archive_filter = URLPatternFilter(
            patterns=[r".*/archive/.*", r".*/temp/.*"],
            reverse=True # Exclude if matches
        )
        ```
        *   `patterns`: A list of strings. These are treated as regular expressions by default (Python's `re` module). The provided code shows `fnmatch.translate` is used, which converts glob patterns to regex, but also handles direct regex if it detects regex-specific characters like `^`, `$`, `\d`.
        *   `reverse (bool, default=False)`: If `False` (default), the URL passes if it matches *any* pattern. If `True`, the URL passes only if it matches *none* of the patterns (effectively a blocklist).
        *   `* Code Example: [Allowing only URLs matching '/articles/[year]/[month]/[slug]' and excluding any URL containing '?replytocom=']`
            ```python
            article_path_filter = URLPatternFilter(
                patterns=[r"/articles/\d{4}/\d{2}/[\w-]+/?$"] # Matches /articles/YYYY/MM/slug
            )
            no_reply_filter = URLPatternFilter(
                patterns=[r"\?replytocom="],
                reverse=True # Exclude if it contains replytocom
            )
            # In a FilterChain, these would apply sequentially
            # final_chain = FilterChain(filters=[article_path_filter, no_reply_filter])
            ```
    *   **4.4.4. Best Practices:**
        *   Use for complex URL structures that `DomainFilter` or `ContentTypeFilter` can't handle.
        *   Test your regular expressions thoroughly to ensure they match what you intend and don't have unintended side effects or performance issues. Online regex testers can be very helpful.
        *   Prefer simpler string methods or other filters if a regex is overkill, as regex can be slower.

*   **4.5. `ContentRelevanceFilter` (Requires HEAD requests)**
    *   **4.5.1. Purpose:** To pre-filter URLs based on the relevance of their metadata (title, meta description, keywords found in the `<head>` section) to a given query, using the BM25 ranking algorithm. This helps in prioritizing or including only pages that are likely to be about a specific topic *before* downloading the full content.
    *   **4.5.2. How it Works:**
        1.  Performs an HTTP HEAD request to fetch the headers of the URL.
        2.  If successful, it uses `HeadPeek` to extract text content from `<title>`, `<meta name="description">`, and `<meta name="keywords">` tags from the response (if the HEAD response contains enough of the head, which is not guaranteed and server-dependent. Often, servers don't send body content with HEAD).
        3.  Calculates a BM25 relevance score between the extracted text and the user-provided `query`.
        4.  The URL passes if the score is above the specified `threshold`.
        *   **Important Note on HEAD requests:** While HEAD requests are designed to be lightweight, not all servers implement them correctly or return meaningful content previews in the head. Some servers might return the full HTML head, others might return very little, and some might even block HEAD requests. The effectiveness of this filter depends heavily on server behavior.
    *   **4.5.3. Configuration & Usage:**
        ```python
        from crawl4ai import ContentRelevanceFilter

        relevance_filter = ContentRelevanceFilter(
            query="AI in healthcare applications",
            threshold=0.3,  # Adjust based on desired strictness
            # k1=1.2, b=0.75, avgdl=1000 are BM25 parameters, defaults are usually fine
        )
        ```
        *   `query (str)`: The search query to compare against.
        *   `threshold (float)`: The minimum BM25 score for a URL to pass.
        *   `k1`, `b`, `avgdl`: BM25 algorithm parameters. Defaults are generally reasonable.
        *   `* Code Example: [Filtering for pages potentially relevant to "sustainable energy solutions" with a score threshold of 0.25]`
            ```python
            # Assuming this filter is part of a FilterChain
            sustainable_energy_filter = ContentRelevanceFilter(
                query="sustainable energy solutions impact",
                threshold=0.25
            )
            # This would attempt to fetch HEAD for candidate URLs and check their head content.
            ```
    *   **4.5.4. When to Use:**
        *   When you need a preliminary content relevance check before committing to a full page download and processing.
        *   For highly targeted crawls where topic relevance is paramount.
        *   Be mindful of the performance implications: each HEAD request adds network latency. This filter is best used after broader, faster filters (like `DomainFilter`, `ContentTypeFilter`).
        *   Test with target sites to see if their HEAD responses are useful for this filter.

*   **4.6. `SEOFilter` (Requires HEAD requests)**
    *   **4.6.1. Purpose:** To filter URLs based on a quantitative assessment of their basic on-page SEO quality, derived from elements in the `<head>` section.
    *   **4.6.2. How it Works:**
        1.  Similar to `ContentRelevanceFilter`, it performs an HTTP HEAD request.
        2.  It then uses `HeadPeek` to extract information like title length, presence and length of meta description, canonical URL validity, robots meta tag status (e.g., `noindex`), schema.org markup presence, and general URL "quality" heuristics (length, parameters, underscores).
        3.  Each factor is scored, and a weighted total score is calculated.
        4.  The URL passes if the total score is above the specified `threshold`.
    *   **4.6.3. Configuration & Usage:**
        ```python
        from crawl4ai import SEOFilter

        seo_quality_filter = SEOFilter(
            threshold=0.65,  # Pages must meet at least 65% of SEO quality checks
            keywords=['data science', 'machine learning'], # Optional: boost score if these appear
            # weights: Optional dict to customize scoring of different SEO factors
        )
        ```
        *   `threshold (float)`: Minimum overall SEO score (0.0 to 1.0) for the URL to pass.
        *   `keywords (Optional[List[str]])`: If provided, presence of these keywords in title or meta description can boost the score.
        *   `weights (Optional[Dict[str, float]])`: Allows customization of how much each SEO factor (e.g., `"title_length"`, `"meta_description"`, `"canonical"`) contributes to the total score. See `SEOFilter.DEFAULT_WEIGHTS` for default factors and their weights.
        *   `* Code Example: [Filtering for pages with an SEO score > 0.7, particularly looking for pages optimized for "python programming tutorials"]`
            ```python
            python_tutorial_seo_filter = SEOFilter(
                threshold=0.7,
                keywords=["python programming tutorials", "learn python"]
            )
            # This filter would favor pages that are generally well-optimized for SEO
            # and also contain the specified keywords.
            ```
    *   **4.6.4. When to Use:**
        *   Performing SEO audits to quickly identify pages with potential on-page issues.
        *   Targeting well-optimized pages for content scraping or analysis.
        *   Like `ContentRelevanceFilter`, be aware of HEAD request overhead. Use after faster filters.

*   **4.7. Building Effective `FilterChain`s**
    *   **Order of filters matters:** This is crucial for performance.
        1.  **Fastest, broadest filters first:** Start with `DomainFilter` to immediately exclude irrelevant domains. Follow with `ContentTypeFilter` to discard unwanted file types by extension. `URLPatternFilter` with simple patterns can also be early.
        2.  **More expensive filters later:** Filters requiring network requests (like `ContentRelevanceFilter`, `SEOFilter`) or complex computations should come last, so they only operate on a reduced set of URLs.
    *   **Combining allow and deny logic:** Use multiple `DomainFilter` or `URLPatternFilter` instances (some with `reverse=True`) to create include/exclude rules. For example, allow `example.com` but block `example.com/private/`.
    *   `* Code Example: [A FilterChain demonstrating strategic ordering]`
        ```python
        from crawl4ai import (
            FilterChain, DomainFilter, ContentTypeFilter, URLPatternFilter,
            ContentRelevanceFilter
        )

        # Goal: Crawl blog posts about "AI ethics" on 'myblog.com',
        #       excluding PDFs and archive sections, ensuring basic relevance.

        # 1. Domain Filter: Only 'myblog.com'
        domain_filter = DomainFilter(allowed_domains=["myblog.com"])

        # 2. Content Type Filter: Only HTML
        content_type_filter = ContentTypeFilter(allowed_types=['.html', '.htm'])

        # 3. URL Pattern Filter: Exclude '/archive/'
        archive_exclude_filter = URLPatternFilter(patterns=[r"/archive/"], reverse=True)

        # 4. Content Relevance Filter: Must be somewhat about "AI ethics"
        relevance_filter = ContentRelevanceFilter(query="AI ethics", threshold=0.2)


        effective_chain = FilterChain(filters=[
            domain_filter,
            content_type_filter,
            archive_exclude_filter,
            relevance_filter  # This one makes HEAD requests, so it's last
        ])

        # This chain would be passed to a DeepCrawlStrategy
        # bfs_strategy = BFSDeepCrawlStrategy(max_depth=3, filter_chain=effective_chain)
        ```
        This example shows how to layer filters: first, quickly narrow down by domain and content type, then apply URL pattern rules, and finally, perform the more costly relevance check on the remaining candidates.

## 5. Prioritizing URLs: Scoring Mechanisms

URL scoring is the cornerstone of the `BestFirstCrawlingStrategy`. It allows you to define what "best" means for your crawl, guiding the crawler to explore the most promising URLs first.

*   **5.1. Why Score URLs?**
    *   **Guided Exploration:** Directs the `BestFirstCrawlingStrategy` to URLs that are most likely to contain the information you seek.
    *   **Resource Optimization:** If you have a `max_pages` limit or a time constraint, scoring helps ensure that the most valuable pages are processed before the limit is reached.
    *   **Relevance Ranking:** Allows you to implicitly rank discovered pages by their potential importance or relevance to your task.
    *   **Focus:** Helps concentrate crawling efforts on specific types of content (e.g., fresh news, product pages, high-authority articles).

*   **5.2. `CompositeScorer`: Combining Multiple Signals**
    *   **How it works:** `CompositeScorer` takes a list of individual `URLScorer` instances. For a given URL, it calls the `score()` method of each child scorer. The final score for the URL is typically a weighted sum of the scores from these individual scorers. Each child scorer's raw score is multiplied by its assigned `weight` (which defaults to 1.0 if not specified when adding the scorer to the `CompositeScorer`).
        ```python
        from crawl4ai import CompositeScorer, KeywordRelevanceScorer, PathDepthScorer

        keyword_scorer = KeywordRelevanceScorer(keywords=["news", "update"], weight=0.7)
        path_scorer = PathDepthScorer(optimal_depth=2, weight=0.3)

        # The CompositeScorer will calculate:
        # final_score = (keyword_scorer.score(url) * 0.7) + (path_scorer.score(url) * 0.3)
        # Note: The individual scorers' `weight` parameter is used by CompositeScorer.
        # It is more common to set weights when adding to CompositeScorer if that API exists,
        # or ensure individual scorers output in a way that their inherent weight makes sense.
        # Based on the code: CompositeScorer sums the results of `scorer.score(url)` directly,
        # which already includes the scorer's own weight.
        # So, the weights are applied within each scorer before summing.

        # Corrected understanding based on code:
        # Each scorer's score() method already incorporates its own weight.
        # CompositeScorer simply sums these pre-weighted scores.
        composite_scorer = CompositeScorer(scorers=[keyword_scorer, path_scorer])
        # final_score = keyword_scorer.score(url) + path_scorer.score(url)
        # where keyword_scorer.score(url) is raw_keyword_score * 0.7
        # and path_scorer.score(url) is raw_path_score * 0.3
        ```
    *   **Normalizing scores:** The individual scorers in Crawl4ai are generally designed to output scores that are somewhat normalized (often between 0 and 1 before their internal weight is applied). However, if you create custom scorers with vastly different output ranges, their contribution to the `CompositeScorer` might be skewed. It's good practice to design custom scorers to produce scores in a relatively consistent range (e.g., 0-1) before their `weight` is applied, or adjust their individual `weight`s accordingly to balance their influence in the `CompositeScorer`. The `CompositeScorer` itself simply sums the already weighted scores from its child scorers.
    *   `* Code Example: [Creating a CompositeScorer combining KeywordRelevanceScorer, FreshnessScorer, and DomainAuthorityScorer. Keyword relevance is most important, followed by freshness, then domain authority.]`
        ```python
        from crawl4ai import (
            CompositeScorer, KeywordRelevanceScorer, FreshnessScorer,
            DomainAuthorityScorer
        )
        from datetime import datetime

        # Scorer for keywords, highly weighted
        keyword_scorer = KeywordRelevanceScorer(
            keywords=["financial analysis", "market trends"],
            weight=0.5 # This weight is applied internally by KeywordRelevanceScorer
        )

        # Scorer for freshness, moderately weighted
        freshness_scorer = FreshnessScorer(
            current_year=datetime.now().year,
            weight=0.3
        )

        # Scorer for domain authority, less weighted
        domain_scorer = DomainAuthorityScorer(
            domain_weights={"bloomberg.com": 0.9, "reuters.com": 0.85, "wsj.com": 0.95},
            default_weight=0.5, # For other domains
            weight=0.2
        )

        # CompositeScorer sums the weighted scores from each child scorer
        final_url_scorer = CompositeScorer(
            scorers=[keyword_scorer, freshness_scorer, domain_scorer]
        )
        # Example URL score calculation:
        # url = "https://www.bloomberg.com/news/articles/2023-10-26/ai-impact-on-finance"
        # score_for_url = final_url_scorer.score(url)
        # This would be:
        # (raw_keyword_score_for_url * 0.5) + \
        # (raw_freshness_score_for_url * 0.3) + \
        # (raw_domain_score_for_url * 0.2)
        ```

*   **5.3. `KeywordRelevanceScorer`**
    *   **5.3.1. Purpose:** Scores URLs based on how many of the specified keywords appear within the URL string itself. This is a simple way to prioritize URLs that seem topically relevant by their path or query parameters.
    *   **5.3.2. How it Works:** It iterates through the provided list of `keywords`. For each keyword, it checks if it's present in the URL (case-insensitively by default). The score is typically proportional to the number of matched keywords, normalized by the total number of keywords, and then multiplied by the scorer's `weight`.
    *   **5.3.3. Configuration & Usage:**
        ```python
        from crawl4ai import KeywordRelevanceScorer

        # Prioritize URLs related to Python or Machine Learning
        tech_keyword_scorer = KeywordRelevanceScorer(
            keywords=["python", "machine learning", "pytorch"],
            weight=1.0,       # Overall weight for this scorer
            case_sensitive=False # Default
        )
        ```
        *   `keywords (List[str])`: A list of keywords to search for in the URL.
        *   `weight (float, default=1.0)`: A multiplier applied to the raw score.
        *   `case_sensitive (bool, default=False)`: Whether keyword matching should be case-sensitive.
        *   `* Code Example: [Scoring URLs for a job board, prioritizing those containing "remote", "engineer", or "developer"]`
            ```python
            job_url_scorer = KeywordRelevanceScorer(
                keywords=["remote", "engineer", "developer", "software"],
                weight=1.0
            )
            # Example scores:
            # score1 = job_url_scorer.score("https://jobs.example.com/remote-software-engineer-position") # high score
            # score2 = job_url_scorer.score("https://jobs.example.com/marketing-manager-sf")         # lower score
            ```

*   **5.4. `DomainAuthorityScorer` (Conceptual/External Data)**
    *   **5.4.1. Purpose:** To give preference to URLs from domains that are considered more authoritative or trustworthy. This requires you to provide the authority scores.
    *   **5.4.2. How it Works:** It uses a dictionary (`domain_weights`) that maps domain names (e.g., `"wikipedia.org"`) to numerical authority scores (e.g., `0.9`). When a URL is scored, its domain is extracted. If the domain is in `domain_weights`, its score is used; otherwise, `default_weight` is applied. This raw score is then multiplied by the scorer's overall `weight`.
    *   **5.4.3. Configuration & Usage:**
        ```python
        from crawl4ai import DomainAuthorityScorer

        authority_scorer = DomainAuthorityScorer(
            domain_weights={
                "wikipedia.org": 0.9,
                "scholar.google.com": 0.85,
                "archive.org": 0.7
            },
            default_weight=0.3, # Score for domains not in the list
            weight=1.0          # Overall weight for this scorer's contribution
        )
        ```
        *   `domain_weights (Dict[str, float])`: A dictionary mapping domain strings to their authority scores (typically 0-1).
        *   `default_weight (float, default=0.5)`: Score assigned to URLs from domains not explicitly listed in `domain_weights`.
        *   `weight (float, default=1.0)`: Multiplier for the final score from this scorer.
        *   `* Code Example: [In a news crawl, giving higher scores to URLs from 'bbc.com', 'nytimes.com', and 'reuters.com']`
            ```python
            news_authority_scorer = DomainAuthorityScorer(
                domain_weights={
                    "bbc.com": 0.95,
                    "nytimes.com": 0.9,
                    "reuters.com": 0.88
                },
                default_weight=0.4, # Other news sources
                weight=1.0
            )
            # score_bbc = news_authority_scorer.score("https://www.bbc.com/news/world-europe-12345")
            # score_local_blog = news_authority_scorer.score("https://my-local-blog.com/news-update")
            ```
    *   **5.4.4. Note:** This scorer's effectiveness depends entirely on the quality and relevance of the `domain_weights` you provide. There's no built-in mechanism in Crawl4ai to automatically determine domain authority; you must supply this data.

*   **5.5. `FreshnessScorer`**
    *   **5.5.1. Purpose:** To prioritize URLs that appear to contain more recent content, typically by looking for date patterns (especially years) in the URL string.
    *   **5.5.2. How it Works:** It uses regular expressions to find date patterns (like YYYY/MM/DD, YYYY-MM-DD, YYYY_MM_DD, or just YYYY) in the URL. It extracts the most recent valid year found. The score is then calculated based on the difference between this extracted year and the `current_year` provided during initialization. More recent years get higher scores. The pre-defined `_FRESHNESS_SCORES` list provides a quick lookup for common year differences.
    *   **5.5.3. Configuration & Usage:**
        ```python
        from crawl4ai import FreshnessScorer
        from datetime import datetime

        # Prioritize content from the current year or last few years
        current_year = datetime.now().year
        freshness_scorer = FreshnessScorer(
            current_year=current_year,
            weight=1.0
        )
        ```
        *   `current_year (int)`: The reference year for calculating freshness.
        *   `weight (float, default=1.0)`: Multiplier for the final score.
        *   Date patterns detected: The `_date_pattern` regex in `scorers.py` looks for common date formats.
        *   `* Code Example: [Prioritizing news articles or blog posts from 2023 onwards, assuming current year is 2024]`
            ```python
            # Assuming it's 2024
            recent_content_scorer = FreshnessScorer(current_year=2024, weight=1.0)
            # score_2023 = recent_content_scorer.score("https://example.com/blog/2023/10/my-article") # High score
            # score_2020 = recent_content_scorer.score("https://example.com/archive/2020/old-post") # Lower score
            # score_no_date = recent_content_scorer.score("https://example.com/about-us")      # Default score (0.5)
            ```

*   **5.6. `PathDepthScorer`**
    *   **5.6.1. Purpose:** Scores URLs based on their path depth, which is the number of segments in the URL path (e.g., `/folder1/folder2/page.html` has depth 3). This can be used to prefer shallower pages (often more important) or pages around a specific `optimal_depth`.
    *   **5.6.2. How it Works:** It parses the URL to count the number of segments in its path. The scoring logic (from `_LOOKUP_SCORES`) gives higher scores to depths closer to `optimal_depth`. Depths further away receive progressively lower scores.
    *   **5.6.3. Configuration & Usage:**
        ```python
        from crawl4ai import PathDepthScorer

        # Prefer pages with a path depth of 2 or 3
        path_scorer = PathDepthScorer(
            optimal_depth=2, # Or 3, depending on preference
            weight=1.0
        )
        ```
        *   `optimal_depth (int, default=3)`: The path depth considered most desirable.
        *   `weight (float, default=1.0)`: Multiplier for the final score.
        *   `* Code Example: [Slightly preferring top-level category pages (depth 1) or main articles (depth 2)]`
            ```python
            shallow_page_scorer = PathDepthScorer(optimal_depth=1, weight=1.0)
            # score_depth1 = shallow_page_scorer.score("https://example.com/products/")  # High score (closer to 1.0)
            # score_depth3 = shallow_page_scorer.score("https://example.com/products/category/item") # Lower score
            ```
        The scoring is based on the difference from `optimal_depth`, using `_SCORE_LOOKUP = [1.0, 0.5, 0.333..., 0.25]`. A difference of 0 gets 1.0, 1 gets 0.5, etc.

*   **5.7. `ContentTypeScorer`**
    *   **5.7.1. Purpose:** Assigns scores to URLs based on their inferred content type, primarily determined by the file extension. This allows prioritizing certain types of content (e.g., HTML pages over images or documents).
    *   **5.7.2. How it Works:** It extracts the file extension from the URL. If this extension is found as a key in the `type_weights` dictionary provided during initialization, the corresponding score is used. If the extension is not found, a default score of 0.0 is typically assigned (unless `type_weights` provides a wildcard or default). The raw score is then multiplied by the scorer's `weight`.
    *   **5.7.3. Configuration & Usage:**
        ```python
        from crawl4ai import ContentTypeScorer

        html_priority_scorer = ContentTypeScorer(
            type_weights={
                '.html': 1.0,
                '.htm': 1.0,
                '.pdf': 0.7,
                '.doc': 0.5,
                '.jpg': 0.2,
                '.png': 0.2
            },
            weight=1.0
        )
        ```
        *   `type_weights (Dict[str, float])`: A dictionary mapping file extensions (including the dot, e.g., `'.html'`) to scores.
        *   `weight (float, default=1.0)`: Multiplier for the final score.
        *   `* Code Example: [Prioritizing HTML and PDF documents, while down-weighting images and executables for a document-focused crawl]`
            ```python
            document_content_scorer = ContentTypeScorer(
                type_weights={
                    '.html': 1.0, '.htm': 1.0,
                    '.pdf': 0.9, '.doc': 0.8, '.docx': 0.8,
                    '.txt': 0.7,
                    '.jpg': 0.1, '.png': 0.1, '.gif': 0.1,
                    '.exe': 0.0, '.zip': 0.05
                },
                weight=1.0
            )
            # score_html = document_content_scorer.score("https://example.com/index.html") # High
            # score_zip = document_content_scorer.score("https://example.com/archive.zip") # Low
            ```

*   **5.8. `URLScorer` (Base Class)**
    *   If the built-in scorers or their combination via `CompositeScorer` don't meet your specific needs, you can create a highly custom scorer by inheriting from the `URLScorer` base class.
    *   **Key method to implement:** `_calculate_score(self, url: str) -> float`. This method should take a URL string and return a float representing its score. Remember that the `score(self, url:str)` public method will automatically multiply this by `self._weight`.
    *   Consider the range of scores your custom scorer produces to ensure it integrates well if used within a `CompositeScorer`.

## 6. Configuring and Running Deep Crawls

The `CrawlerRunConfig` object is central to configuring how any specific crawl, including deep crawls, behaves. You'll pass your chosen `DeepCrawlStrategy` (along with its configured filters and scorers) to it.

*   **6.1. The Role of `CrawlerRunConfig`**
    *   The `deep_crawl_strategy` parameter of `CrawlerRunConfig` is how you enable and configure deep crawling for a specific `arun()` or `arun_many()` call.
    *   You instantiate your chosen strategy (e.g., `BFSDeepCrawlStrategy`), configure it with any `FilterChain` and `URLScorer` instances, and then assign this strategy object to `CrawlerRunConfig.deep_crawl_strategy`.
    *   `* Code Example: [Illustrating how strategy is passed to CrawlerRunConfig]`
        ```python
        from crawl4ai import (
            AsyncWebCrawler, CrawlerRunConfig, BFSDeepCrawlStrategy,
            DomainFilter, FilterChain
        )
        import asyncio

        # 1. Define Filters and Scorers (if needed)
        my_filters = FilterChain(filters=[DomainFilter(allowed_domains=["example.com"])])

        # 2. Instantiate and Configure the Strategy
        my_bfs_strategy = BFSDeepCrawlStrategy(max_depth=2, filter_chain=my_filters)

        # 3. Create CrawlerRunConfig and assign the strategy
        my_run_config = CrawlerRunConfig(
            deep_crawl_strategy=my_bfs_strategy,
            # ... other run-specific settings like cache_mode, verbosity, etc.
            cache_mode=CacheMode.BYPASS,
            verbose=True
        )

        async def main():
            async with AsyncWebCrawler() as crawler:
                results = await crawler.arun(url="https://example.com", config=my_run_config)
                for result in results: # arun returns a CrawlResultContainer
                    if result.success:
                        print(f"Crawled: {result.url} - Depth: {result.metadata.get('depth')}")
        # asyncio.run(main())
        ```

*   **6.2. Essential Global Deep Crawl Parameters in `DeepCrawlStrategy` (and reflected in `CrawlerRunConfig`)**
    These parameters are generally set on the strategy object itself.
    *   **`max_depth`:**
        *   **Meaning:**
            *   **BFS:** The maximum number of levels to explore from the seed URL(s). Level 0 is the seed.
            *   **DFS:** The maximum number of links to follow down a single path before backtracking.
            *   **Best-First:** While primarily score-driven, `max_depth` still acts as an upper limit on how deep any single path can go, preventing infinite exploration even if scores are high.
        *   **Strategies for choosing `max_depth`:**
            *   Start small (e.g., 1 or 2) and observe the number of pages found.
            *   Increase incrementally based on your understanding of the target site's structure and your data needs.
            *   For very large sites, a high `max_depth` can lead to an enormous number of URLs.
        *   `* Diagram: [Show two small site graphs. One with max_depth=1, showing only direct links. Another with max_depth=2, showing links of links. Highlight the exponential growth potential.]`
    *   **`max_pages`:**
        *   **How it acts as a global stop condition:** Regardless of `max_depth` or strategy, the crawl will halt once `max_pages` have been successfully processed.
        *   **Interaction with `max_depth` and strategy:**
            *   A crawl might hit `max_pages` before reaching `max_depth` on all branches.
            *   For BFS, this means some deeper levels might not be touched.
            *   For DFS, this means some branches might not be fully explored.
            *   For Best-First, this means lower-scoring URLs might never be visited.
        *   **Use cases:**
            *   Budgeting crawl resources (time, bandwidth, API calls if any).
            *   Getting a quick sample or overview of a site.
            *   Preventing runaway crawls on unexpectedly large sites.
    *   **`include_external` (Context: Typically a parameter on the strategy, e.g., `BestFirstCrawlingStrategy` and other strategies in `crawl4ai`):**
        *   **What it does:** If `True`, the crawler will follow links to domains different from the seed URL's domain.
        *   **When to use it:**
            *   Discovering backlinks or references to your site from external sources (though this is usually done by starting crawls on those external sources).
            *   Exploring a small, trusted ecosystem of related websites.
        *   **Potential pitfalls:**
            *   **Crawl Scope Explosion:** The web is vast. Without *extremely* strict filters (`DomainFilter` for allowed external domains, `URLPatternFilter`), enabling `include_external` can lead to an unmanageably large and irrelevant crawl.
            *   **Resource Drain:** Crawling external sites consumes your resources for potentially off-topic content.
            *   **Best Practice:** Keep `include_external=False` (the default for most strategies) unless you have a very specific reason and robust filters in place. If you need to crawl multiple specific domains, it's often better to run separate, focused crawls for each or use `arun_many` with a list of seed URLs.

*   **6.3. Practical Examples of `CrawlerRunConfig` for Deep Crawls**
    *   `* Code Example: [BFS crawl limited to depth 3 within 'example.com', only HTML pages, verbose logging]`
        ```python
        bfs_strat_example = BFSDeepCrawlStrategy(
            max_depth=3,
            filter_chain=FilterChain(filters=[
                DomainFilter(allowed_domains=["example.com"]),
                ContentTypeFilter(allowed_types=['.html', '.htm'])
            ])
        )
        run_config_bfs = CrawlerRunConfig(
            deep_crawl_strategy=bfs_strat_example,
            verbose=True,
            cache_mode=CacheMode.BYPASS # Forcing fresh crawl for example
        )
        # Usage: await crawler.arun(url="https://example.com", config=run_config_bfs)
        ```
    *   `* Code Example: [DFS crawl following '/blog/' paths, max 50 pages, stream results]`
        ```python
        dfs_strat_example = DFSDeepCrawlStrategy(
            max_depth=10, # DFS can go deep
            max_pages=50,
            filter_chain=FilterChain(filters=[
                URLPatternFilter(patterns=[r"https://example.com/blog/.*"])
            ]),
            stream=True # Yield results as they are found
        )
        run_config_dfs = CrawlerRunConfig(
            deep_crawl_strategy=dfs_strat_example,
            verbose=True
        )
        # Usage:
        # async for result in await crawler.arun(url="https://example.com/blog/", config=run_config_dfs):
        #     # process result
        ```
    *   `* Code Example: [Best-First crawl for "AI ethics" articles, prioritizing recent, high-authority sources, excluding PDFs, max 100 pages]`
        ```python
        from crawl4ai import KeywordRelevanceScorer, FreshnessScorer, DomainAuthorityScorer, CompositeScorer, ContentTypeFilter
        from datetime import datetime

        # Scorers
        keyword_scorer_ai_ethics = KeywordRelevanceScorer(keywords=["AI ethics", "responsible AI"], weight=0.6)
        freshness_scorer_recent = FreshnessScorer(current_year=datetime.now().year, weight=0.25)
        authority_scorer_news = DomainAuthorityScorer(
            domain_weights={"techcrunch.com": 0.8, "wired.com": 0.85},
            default_weight=0.4,
            weight=0.15
        )
        composite_scorer_ai = CompositeScorer(scorers=[
            keyword_scorer_ai_ethics, freshness_scorer_recent, authority_scorer_news
        ])

        # Filters
        filter_chain_ai = FilterChain(filters=[
            DomainFilter(allowed_domains=["techcrunch.com", "wired.com", "another-news-site.com"]),
            ContentTypeFilter(allowed_types=['.html']) # Exclude PDFs by only allowing HTML
        ])

        best_first_strat_ai = BestFirstCrawlingStrategy(
            url_scorer=composite_scorer_ai,
            filter_chain=filter_chain_ai,
            max_pages=100,
            max_depth=5 # Still good to have a depth limit
        )
        run_config_best_first_ai = CrawlerRunConfig(
            deep_crawl_strategy=best_first_strat_ai,
            verbose=True
        )
        # Usage: await crawler.arun(url="https://techcrunch.com", config=run_config_best_first_ai)
        ```

*   **6.4. Integrating with `AsyncWebCrawler.arun()` and `AsyncWebCrawler.arun_many()`**
    *   **`arun(url="seed_url", config=run_config_with_deep_crawl)`:**
        When you call `arun` with a `CrawlerRunConfig` that includes a `deep_crawl_strategy`, the deep crawling process starts from the single `seed_url`. The `DeepCrawlDecorator` intercepts this and delegates to your strategy.
    *   **`arun_many(urls=["seed1", "seed2"], config=run_config_with_deep_crawl)`:**
        If you use `arun_many`, Crawl4ai will typically initiate *independent* deep crawls starting from each seed URL in the `urls` list. Each deep crawl will adhere to the `max_depth`, `max_pages`, filters, and scorers defined in the *same* `run_config_with_deep_crawl`.
        *   **Important Consideration:** The `max_pages` limit in this scenario usually applies *per seed URL's deep crawl task* if the dispatcher handles them as separate tasks. If you need a global `max_pages` across all seed URLs in an `arun_many` call, that would require a more custom dispatcher or a wrapper around `arun_many` to track the total pages. The default behavior is often per-task limits.
        *   If `stream=True` is set on the strategy (or within the `run_config`), results from the different deep crawls initiated by `arun_many` will be yielded as they become available.

## 7. Understanding the `DeepCrawlDecorator`

While you primarily interact with deep crawling through `CrawlerRunConfig` and strategy objects, it's helpful to have a conceptual understanding of the `DeepCrawlDecorator`.

*   **7.1. How Deep Crawling is Activated (Conceptual)**
    *   **Role of `DeepCrawlDecorator`:** The `DeepCrawlDecorator` is a Python decorator that wraps the `AsyncWebCrawler.arun()` method. When `arun()` is called, the decorator checks if the `config` argument (an instance of `CrawlerRunConfig`) has a `deep_crawl_strategy` defined.
    *   If a `deep_crawl_strategy` is present *and* deep crawling is not already active (see `deep_crawl_active` below), the decorator intercepts the call. Instead of the standard single-page crawl, it invokes the `arun()` method of your specified `deep_crawl_strategy` instance, passing along the crawler, seed URL, and configuration.
    *   If no `deep_crawl_strategy` is set, or if deep crawling is already active, the decorator allows the original `arun()` method (for single-page crawling) to proceed.
    *   **The `deep_crawl_active` `ContextVar`:** This is a context variable (from Python's `contextvars` module). The decorator sets `deep_crawl_active` to `True` before calling the strategy's `arun()` method and resets it to `False` afterwards.
        *   **Purpose:** Its primary function is to prevent accidental recursive deep crawls. If your `deep_crawl_strategy` internally calls `crawler.arun()` (which it typically does to fetch individual pages), this flag ensures that those internal calls perform standard single-page fetches and don't try to initiate another layer of deep crawling using the same strategy.

*   **7.2. What This Means for You as a User**
    *   **Transparency:** For most use cases, the `DeepCrawlDecorator` operates transparently. You don't need to instantiate or call it directly.
    *   **Centralized Configuration:** You enable and configure deep crawling by setting the `deep_crawl_strategy` attribute in your `CrawlerRunConfig` object. This is the main entry point.
    *   **Awareness for Advanced Scenarios:** Understanding its existence is useful if:
        *   You are debugging complex deep crawling behavior and want to trace the execution flow.
        *   You are developing very custom strategies that might need to interact with or be aware of this context.

## 8. Monitoring and Analyzing Deep Crawl Performance

Understanding what happened during your deep crawl is key to optimizing it.

*   **8.1. Using `TraversalStats`**
    *   **Accessing `TraversalStats`:**
        *   The `BFSDeepCrawlStrategy`, `DFSDeepCrawlStrategy`, and `BestFirstCrawlingStrategy` (and their base class `DeepCrawlStrategy`) maintain a `self.stats` attribute of type `TraversalStats`.
        *   After a crawl initiated by one of these strategies completes (or even during, if you have access to the strategy instance), you can inspect `strategy_instance.stats`.
        *   The strategies also log these stats upon completion (or at intervals if verbose logging is high).
    *   **Key Metrics and Their Meaning (from `TraversalStats` in `crawl4ai/deep_crawling/base_strategy.py` and related files):**
        *   `start_time`, `end_time`: The overall start and end Python `datetime` objects for the crawl.
        *   `urls_processed` (often part of `FilterStats` within a strategy or a general counter): Total number of unique URLs that were actually fetched and processed by the crawler.
        *   `urls_failed`: Count of URLs that resulted in an error during fetching or processing.
        *   `urls_skipped`: Count of URLs that were discovered but discarded by the `FilterChain` or other conditions (e.g., already visited, exceeded `max_depth`).
        *   `total_depth_reached`: The maximum depth level explored during the crawl.
        *   `current_depth` (Relevant for strategies like BFS/DFS): The current depth level being explored.
        *   Individual filters (`URLFilter` subclasses) also have their own `FilterStats` (`filter.stats`) which track `total_urls` processed by that filter, `passed_urls`, and `rejected_urls`. This is very useful for seeing which filter is having the most impact.
    *   **Interpreting Stats for Optimization:**
        *   **High `urls_skipped` (overall) or high `rejected_urls` (for a specific filter):** This indicates your filters are very active. Review them to ensure they aren't too restrictive or are correctly configured.
        *   **`total_depth_reached` < `max_depth` (when `max_pages` is high):** This could mean the crawl exhausted all discoverable links within the filter scope before reaching the maximum depth, or filters are preventing deeper exploration.
        *   **Crawl finishes too quickly and `urls_processed` is low:** Check seed URLs, initial filters, and `max_depth/max_pages` limits.
        *   **Crawl takes too long:**
            *   Are filters too loose?
            *   Is `max_depth` or `max_pages` too high for the site?
            *   Are expensive filters/scorers (requiring network or heavy computation) being used excessively?
    *   `* Code Example: [Accessing stats after a BFS crawl (assuming batch mode)]`
        ```python
        # ... (setup bfs_strategy and run_config as in previous examples) ...
        # async with AsyncWebCrawler(config=browser_config) as crawler:
        #     results_container = await crawler.arun(
        #         url="https://example.com",
        #         config=run_config_with_bfs_strategy # run_config_with_bfs_strategy.deep_crawl_strategy is bfs_strategy
        #     )
        #
        #     # Access stats from the strategy instance
        #     crawl_stats = run_config_with_bfs_strategy.deep_crawl_strategy.stats
        #     print(f"\n--- Crawl Statistics ---")
        #     print(f"Start Time: {crawl_stats.start_time}")
        #     # Note: urls_processed might be better tracked by summing successful results
        #     # or by inspecting filter stats on the FilterChain if available.
        #     # TraversalStats itself in the provided code doesn't explicitly have urls_processed.
        #     # Let's assume we count successful results:
        #     print(f"URLs Successfully Processed: {len([r for r in results_container if r.success])}")
        #     print(f"URLs Failed: {len([r for r in results_container if not r.success])}") # Approximation
        #     print(f"URLs Skipped by Filters (Example): {getattr(run_config_with_bfs_strategy.deep_crawl_strategy.filter_chain, 'stats', FilterStats()).rejected_urls if run_config_with_bfs_strategy.deep_crawl_strategy.filter_chain else 'N/A'}")
        #     print(f"Max Depth Reached: {crawl_stats.total_depth_reached}")
        #     if crawl_stats.end_time:
        #          print(f"End Time: {crawl_stats.end_time}")
        #          print(f"Duration: {crawl_stats.end_time - crawl_stats.start_time}")
        #     else:
        #          print("Crawl may still be in progress or ended prematurely.")

        # Note: The TraversalStats model has start_time, end_time, urls_processed, urls_failed, urls_skipped, total_depth_reached, current_depth
        # The strategy code increments self._pages_crawled for successful crawls towards max_pages
        # and self.stats.urls_skipped for links skipped by filters.
        ```

*   **8.2. Logging in Deep Crawls**
    *   Crawl4ai's `AsyncLogger` (if `verbose=True` in `CrawlerRunConfig` or `BrowserConfig`) provides valuable insights. During deep crawls, you'll see:
        *   URLs being added to the frontier/queue/stack.
        *   Actions taken by filters (e.g., "URL rejected by DomainFilter").
        *   Scores assigned to URLs if using `BestFirstCrawlingStrategy` with a `URLScorer`.
        *   Newly discovered links from each page.
        *   Errors encountered during fetching or processing.
    *   **Setting verbosity:**
        *   `verbose=True` (default) provides a good level of detail.
        *   For extremely detailed debugging, you might need to delve into the library's source or add custom logging within custom components.
        *   The logger uses tags (e.g., `[BFS]`, `[FILTER]`, `[SCORE]`) to help identify the source of log messages.

## 9. Best Practices for Effective Deep Crawling

Crafting an effective deep crawl involves more than just setting a strategy; it requires planning, careful configuration, and ethical considerations.

*   **9.1. Planning Your Crawl Strategy**
    *   **Define Clear Objectives:**
        *   What specific data are you trying to collect? (e.g., all product names and prices, all blog post titles and content, site structure).
        *   What is the precise scope of your crawl? (e.g., a single subdomain, specific path patterns, content related to certain keywords).
        *   Clearly defined objectives will guide your choice of strategy, filters, and scorers.
    *   **Analyze Target Website Structure:**
        *   **`robots.txt`:** Always check `robots.txt` first (e.g., `https://example.com/robots.txt`) to understand disallowed paths. Crawl4ai can do this automatically if `check_robots_txt=True` (in `CrawlerRunConfig`).
        *   **Sitemaps:** Look for XML sitemaps (`/sitemap.xml`). They often provide a good list of canonical URLs and can be a great source of seed URLs.
        *   **URL Patterns:** Observe common URL structures for different content types (e.g., `/blog/YYYY/MM/DD/slug`, `/product/category/item-id`). This helps in crafting `URLPatternFilter`s.
        *   **Navigation:** Understand how users (and thus crawlers) navigate the site. Are there clear menus, breadcrumbs, pagination?
    *   **Estimate Crawl Size:**
        *   Before launching a full deep crawl, try a very limited crawl (e.g., `max_depth=1` or `2`, `max_pages=50`) to get a sense of how many URLs are discovered per level.
        *   This helps in estimating resource consumption and setting realistic `max_depth` and `max_pages` for the full crawl.

*   **9.2. Configuring for Efficiency and Relevance**
    *   **Filter Aggressively, Then Loosen:**
        *   Start with a restrictive `DomainFilter` to stay within your target domain(s).
        *   Add `ContentTypeFilter` early to exclude unwanted file types.
        *   Use `URLPatternFilter` to include/exclude specific paths.
        *   Only if necessary, add more computationally expensive filters like `ContentRelevanceFilter` or `SEOFilter` later in the chain.
    *   **Control Scope with `max_depth` and `max_pages`:**
        *   These are your primary safety nets against runaway crawls.
        *   Set them based on your objectives and initial site analysis.
    *   **Choose the Right Strategy:**
        *   BFS for broad, systematic coverage of shallow sites.
        *   DFS for deep dives into specific paths (with careful depth control).
        *   Best-First for targeted crawling based on relevance, freshness, or other criteria (requires good scorer design).
    *   **Iterate on Scorer Design (for Best-First):**
        *   Start with simple scorers.
        *   Run test crawls, analyze the types of URLs being prioritized, and refine your scorer weights or logic.
        *   Use `CompositeScorer` to combine multiple weak signals into a stronger one.
    *   **Test Filter and Scorer Logic:**
        *   Before a large crawl, test your `FilterChain` and `URLScorer` logic with a small, representative set of sample URLs to ensure they behave as expected.

*   **9.3. Ethical and Respectful Crawling**
    *   **Respect `robots.txt`:** Set `check_robots_txt=True` in your `CrawlerRunConfig`. Crawl4ai's `RobotsParser` will then automatically check `robots.txt` for each domain.
    *   **Implement Politeness Delays:**
        *   Crawl4ai's default dispatcher strategies often include rate limiting and backoff mechanisms.
        *   You can configure `mean_delay` and `max_range` in `CrawlerRunConfig` if using `arun_many` to introduce delays between individual `arun` calls managed by the dispatcher.
        *   Avoid hitting any single server too frequently.
    *   **Identify and Handle Sensitive Data Responsibly:** If your crawl might encounter personally identifiable information (PII) or other sensitive data, ensure you have mechanisms to either avoid it (via filters) or handle it according to privacy regulations and ethical guidelines.
    *   **Avoid Overwhelming Servers:** Monitor your crawl's impact. If you notice server errors (5xx status codes) or very slow responses, reduce your crawl rate or concurrency.
    *   **User-Agent:** While Crawl4ai provides a default User-Agent, consider setting a custom one that identifies your bot and provides a way to contact you if site administrators have questions (e.g., `MyCoolBot/1.0 (+http://mybotinfo.example.com)`).

*   **9.4. Handling Common Challenges**
    *   **Crawler Traps:**
        *   **Solution:** Use a sensible `max_depth`. Employ `URLPatternFilter` to exclude patterns that lead to traps (e.g., infinitely deep calendar links, search facets creating unique URLs for every combination).
        *   **Example:** A filter like `URLPatternFilter(patterns=[r"/calendar/\d{4}/\d{2}/\d{2}/.*"], reverse=True)` could block deep calendar paths.
    *   **Session-Dependent Content:**
        *   **Challenge:** If deep pages require a login session established on an earlier page.
        *   **Solution:** Use Crawl4ai's session persistence features.
            1.  Perform an initial crawl/interaction to log in, then save the `storage_state` from the browser context.
            2.  For subsequent deep crawls, load this `storage_state` into `BrowserConfig` or `CrawlerRunConfig` to reuse the session.
            *   Refer to the [Session Management](./session-management.md) and [Advanced Features](./advanced-features.md#5-session-persistence--local-storage) guides for details.
    *   **AJAX-Loaded Content / JavaScript-Generated Links:**
        *   **Challenge:** If links are not present in the initial HTML but are loaded or generated by JavaScript.
        *   **Solution:** Ensure your base crawling strategy (e.g., `AsyncPlaywrightCrawlerStrategy`, which is default) is used, as it executes JavaScript. You might need to use `wait_for` in `CrawlerRunConfig` to allow time for JS to execute and render links before link discovery happens.
    *   **Large-Scale Crawls:**
        *   **Challenge:** In-memory `visited` sets and URL frontiers can become bottlenecks for very large crawls (millions of pages).
        *   **Solution:** For enterprise-scale crawls, consider:
            *   Distributed crawling architecture (breaking the crawl into smaller, manageable parts).
            *   Using a persistent, disk-based queue (e.g., Redis, RabbitMQ) for the URL frontier.
            *   Using a distributed database or bloom filter service for the `visited` set.
            *   Crawl4ai's current built-in strategies are primarily designed for single-instance operation with in-memory tracking.

## 10. Troubleshooting Common Deep Crawling Issues

Even with careful planning, deep crawls can sometimes behave unexpectedly. Here's how to diagnose common problems.

*   **10.1. Crawl Not Going Deep Enough / Stopping Prematurely**
    *   **Check `max_depth` and `max_pages`:** Are these limits set too low for your target?
        *   `print(f"Config: max_depth={my_strategy.max_depth}, max_pages={my_strategy.max_pages}")`
    *   **Inspect Filters:**
        *   Are your filters (`DomainFilter`, `URLPatternFilter`, `ContentTypeFilter`, etc.) too aggressive?
        *   **Debugging Tip:** Temporarily disable filters one by one or simplify them to see if they are the cause. Add logging within custom filters or enable verbose logging in Crawl4ai to see filter decisions.
        *   `* Code Example: [Temporarily disabling a filter chain for debugging]`
            ```python
            # original_filter_chain = my_strategy.filter_chain
            # my_strategy.filter_chain = None # Temporarily disable for a test run
            # ... run crawl ...
            # my_strategy.filter_chain = original_filter_chain # Restore
            ```
    *   **Examine Link Discovery:**
        *   Are links being correctly extracted from the initial pages? After an `arun` call on a seed URL, inspect `result.links`.
        *   If links are JavaScript-generated, ensure your `wait_for` or other JS execution settings are adequate.
    *   **`include_external` Behavior:** If you *intend* to crawl subdomains but they are treated as external (and `include_external=False`), they won't be followed. Ensure your `DomainFilter` correctly specifies all allowed (sub)domains if `include_external` is `False`.

*   **10.2. Crawling Too Many Irrelevant Pages**
    *   **Tighten Filters:** This is the most common solution.
        *   Make `DomainFilter` more specific.
        *   Refine `URLPatternFilter` to exclude unwanted paths.
        *   Add a `ContentTypeFilter` if you're getting many non-HTML pages.
    *   **Refine Scoring (for Best-First):** If using `BestFirstCrawlingStrategy`, improve your `URLScorer` to give lower scores to irrelevant URL patterns or domains.
    *   **Verify `include_external`:** Ensure it's `False` (default for most strategies) if you don't intend to leave your primary domain(s).

*   **10.3. Performance Bottlenecks**
    *   **Network-Intensive Filters:** `ContentRelevanceFilter` and `SEOFilter` make HEAD requests for each URL they evaluate. If your `FilterChain` applies these to many URLs, it will significantly slow down the link processing phase.
        *   **Solution:** Place these filters *after* faster filters that can eliminate many URLs without network calls.
    *   **Complex Regex:** Very complex or inefficient regular expressions in `URLPatternFilter` can be slow.
        *   **Solution:** Simplify regex where possible. Test regex performance independently.
    *   **Complex Scoring Logic:** If your custom `URLScorer` or `CompositeScorer` performs heavy computations or external API calls for every URL, it will become a bottleneck for `BestFirstCrawlingStrategy`.
        *   **Solution:** Optimize scorer logic. Cache external API results if possible.
    *   **BFS Memory Usage:** As mentioned, BFS on very wide sites can lead to high memory usage.
        *   **Solution:** Limit `max_depth`, or consider DFS/Best-First for parts of the crawl.
    *   **Logging Overhead:** Extremely verbose logging to the console or file can add overhead. Reduce verbosity for production runs once debugging is complete.

*   **10.4. Using Logs for Diagnosis**
    *   **Enable Verbose Logging:** Set `verbose=True` in `CrawlerRunConfig` and/or `BrowserConfig`.
    *   **Look for Key Log Messages:**
        *   Messages indicating a URL is being added to the queue/stack.
        *   Filter actions: "URL [url] rejected by [FilterName]" or "URL [url] passed [FilterName]".
        *   Scorer outputs: "URL [url] scored [score] by [ScorerName]" (if scorers log verbosely).
        *   Link discovery: "Discovered [N] links on [page_url]".
        *   Errors: Any exceptions or error messages during fetching, processing, or strategy execution.
    *   **Custom Logging:** Add `self.logger.debug(...)` or `self.logger.info(...)` statements within your custom filters or scorers to trace their specific behavior.

## 11. Advanced Deep Crawling: Customization and Integration

When built-in components aren't enough, Crawl4ai's modular design allows you to create custom strategies, filters, and scorers.

*   **11.1. Why and When to Create Custom Components**
    *   **Unique Filtering Logic:** You might need to filter URLs based on criteria not covered by existing filters, e.g., checking against a dynamic blocklist from an API, or complex domain-specific path rules.
    *   **Domain-Specific Scoring Heuristics:** Your definition of a "valuable" URL might involve proprietary business logic, data from your own databases, or very specific content cues that standard scorers don't address.
    *   **Novel Traversal Strategies:** While BFS, DFS, and Best-First cover many cases, you might envision a hybrid approach or a strategy tailored to a very unusual site structure.
    *   **Integration with External Systems:** Custom components can interact with external APIs or databases during the filtering or scoring process.

*   **11.2. Implementing a Custom `DeepCrawlStrategy`**
    *   **Key methods to override (from `DeepCrawlStrategy` base class):**
        *   `async def _arun_batch(self, start_url: str, crawler: AsyncWebCrawler, config: CrawlerRunConfig) -> List[CrawlResult]:` Implement the core non-streaming traversal logic here. You'll manage the frontier (queue/stack/priority queue), call `crawler.arun_many()` for batches of URLs, and use `self.link_discovery()` and `self.can_process_url()`.
        *   `async def _arun_stream(self, start_url: str, crawler: AsyncWebCrawler, config: CrawlerRunConfig) -> AsyncGenerator[CrawlResult, None]:` Implement the streaming version of the traversal logic. Yield `CrawlResult` objects as they become available.
        *   `async def can_process_url(self, url: str, depth: int) -> bool:` (Often relies on `self.filter_chain`) This method determines if a given URL should be processed based on depth and filters.
        *   `async def link_discovery(self, result: CrawlResult, source_url: str, current_depth: int, visited: Set[str], next_level: List[Tuple], depths: Dict[str, int]) -> None:` (Helper method) Extracts links from a `CrawlResult`, applies `can_process_url`, and adds valid URLs to `next_level` and updates `depths`.
    *   **Managing state:** Your custom strategy will need to manage:
        *   A **frontier** of URLs to visit (e.g., `asyncio.Queue` for BFS, `list` for DFS stack, `asyncio.PriorityQueue` for Best-First).
        *   A **visited set** to avoid re-processing URLs.
        *   **URL depths** to respect `max_depth`.
        *   Counters for `max_pages`.
    *   `* Code Example: [Skeleton for a custom strategy that crawls based on page title length (longer titles first - a simplistic example)]`
        ```python
        from crawl4ai import DeepCrawlStrategy, CrawlResult, AsyncWebCrawler, CrawlerRunConfig
        import asyncio
        from typing import List, AsyncGenerator, Set, Dict, Tuple

        class TitleLengthPriorityStrategy(DeepCrawlStrategy):
            def __init__(self, max_depth: int = 3, max_pages: int = 100, **kwargs):
                super().__init__(max_depth=max_depth, max_pages=max_pages, **kwargs)
                self.priority_queue = asyncio.PriorityQueue() # (score, url, depth, parent_url)
                # Note: Lower numbers = higher priority for asyncio.PriorityQueue

            async def _process_page_and_discover_links(
                self, url: str, depth: int, parent_url: str,
                crawler: AsyncWebCrawler, config: CrawlerRunConfig,
                visited: Set[str]
            ) -> AsyncGenerator[CrawlResult, None]:
                if url in visited or depth > self.max_depth or self._pages_crawled >= self.max_pages:
                    return

                visited.add(url)
                # Create a config for fetching a single page
                page_config = config.clone(deep_crawl_strategy=None) # Ensure no recursive deep crawl
                
                # arun returns a CrawlResultContainer, access the first (and only) result
                crawl_result_container = await crawler.arun(url=url, config=page_config)
                page_result = crawl_result_container.results[0] if crawl_result_container.results else None

                if page_result and page_result.success:
                    self._pages_crawled += 1
                    page_result.metadata = page_result.metadata or {}
                    page_result.metadata["depth"] = depth
                    page_result.metadata["parent_url"] = parent_url
                    yield page_result

                    # Discover links
                    new_links_to_score = []
                    # Simplified link discovery for example
                    if page_result.links:
                        for link_type in ["internal", "external"]: # Or just internal
                            for link_info in page_result.links.get(link_type, []):
                                next_url = link_info.get("href")
                                if next_url and await self.can_process_url(next_url, depth + 1):
                                     if next_url not in visited: # Check visited again before adding to score
                                        new_links_to_score.append(next_url)
                    
                    for new_url in set(new_links_to_score): # Process unique new links
                        # Fetch title (simplified, real scorer would be more robust)
                        # This is inefficient here, a real scorer would be separate
                        temp_page_config = config.clone(deep_crawl_strategy=None, only_text=True, word_count_threshold=0) # very light fetch
                        try:
                            temp_result_container = await crawler.arun(url=new_url, config=temp_page_config)
                            temp_result = temp_result_container.results[0] if temp_result_container.results else None
                            title_len = len(temp_result.metadata.get("title", "")) if temp_result and temp_result.metadata else 0
                            score = -title_len # Negative because lower number = higher priority
                            if new_url not in visited: # Final check before putting in queue
                                await self.priority_queue.put((score, new_url, depth + 1, url))
                        except Exception as e:
                            if self.logger: self.logger.warning(f"Scoring error for {new_url}: {e}")


            async def _arun_stream(self, start_url: str, crawler: AsyncWebCrawler, config: CrawlerRunConfig) -> AsyncGenerator[CrawlResult, None]:
                self.reset_stats() # Important!
                visited: Set[str] = set()
                await self.priority_queue.put((0, start_url, 0, None)) # Initial score 0 for seed

                while not self.priority_queue.empty() and self._pages_crawled < self.max_pages:
                    _score, current_url, current_depth, parent_url = await self.priority_queue.get()
                    
                    if current_url in visited:
                        continue

                    async for page_result in self._process_page_and_discover_links(
                        current_url, current_depth, parent_url, crawler, config, visited
                    ):
                        yield page_result
                self.log_stats()
            
            # _arun_batch would collect all yields from _arun_stream
            async def _arun_batch(self, start_url: str, crawler: AsyncWebCrawler, config: CrawlerRunConfig) -> List[CrawlResult]:
                results = []
                async for result in self._arun_stream(start_url, crawler, config):
                    results.append(result)
                return results

        # Usage:
        # title_strategy = TitleLengthPriorityStrategy(max_depth=3)
        # run_config_custom = CrawlerRunConfig(deep_crawl_strategy=title_strategy)
        ```

*   **11.3. Developing a Custom `URLFilter`**
    *   **Inheriting from `URLFilter`:** Your custom filter class must inherit from `crawl4ai.deep_crawling.filters.URLFilter`.
    *   **Implementing `apply(self, url: str) -> bool`:** This is the core method. It takes a URL string and must return `True` if the URL should pass the filter, or `False` if it should be rejected.
        *   You can also make `apply` an `async def` if it needs to perform asynchronous operations (e.g., an API call to check a dynamic blocklist).
    *   **Leveraging `FilterStats`:**
        *   Call `self._update_stats(passed=True/False)` at the end of your `apply` method to correctly update the filter's statistics (`total_urls`, `passed_urls`, `rejected_urls`).
    *   `* Code Example: [A filter that blocks URLs with more than 5 path segments or URLs containing a specific query parameter 'sessionid']`
        ```python
        from crawl4ai import URLFilter, FilterStats
        from urllib.parse import urlparse, parse_qs

        class PathAndQueryParamFilter(URLFilter):
            def __init__(self, max_segments=5, forbidden_param="sessionid", **kwargs):
                super().__init__(**kwargs) # Pass name if desired
                self.max_segments = max_segments
                self.forbidden_param = forbidden_param

            # This can be async if needed: async def apply(self, url: str) -> bool:
            def apply(self, url: str) -> bool:
                parsed_url = urlparse(url)
                path_segments = parsed_url.path.strip('/').split('/')
                
                # Check path depth
                if len(path_segments) > self.max_segments:
                    self._update_stats(passed=False)
                    return False

                # Check for forbidden query parameter
                query_params = parse_qs(parsed_url.query)
                if self.forbidden_param in query_params:
                    self._update_stats(passed=False)
                    return False
                
                self._update_stats(passed=True)
                return True

        # Usage:
        # custom_filter = PathAndQueryParamFilter(max_segments=4, forbidden_param="tracking_id")
        # filter_chain = FilterChain(filters=[custom_filter])
        ```

*   **11.4. Designing a Custom `URLScorer`**
    *   **Inheriting from `URLScorer`:** Your custom scorer class must inherit from `crawl4ai.deep_crawling.scorers.URLScorer`.
    *   **Implementing `_calculate_score(self, url: str) -> float`:** This method takes a URL string and must return a float representing its "raw" score (before the scorer's `weight` is applied).
        *   This method can also be `async def` if it needs to perform asynchronous operations (e.g., fetching external data to inform the score).
    *   **Score Range:** It's good practice to design your `_calculate_score` to return values in a somewhat consistent range (e.g., 0.0 to 1.0) to make it easier to combine with other scorers in a `CompositeScorer`. The final score returned by the public `score()` method will be `_calculate_score(url) * self.weight`.
    *   `* Code Example: [A scorer that assigns higher scores to URLs ending with '.html' or '.php' and containing the word 'article']`
        ```python
        from crawl4ai import URLScorer

        class ArticlePageScorer(URLScorer):
            def __init__(self, weight: float = 1.0, **kwargs):
                super().__init__(weight=weight, **kwargs) # Pass name if desired

            # Can be async: async def _calculate_score(self, url: str) -> float:
            def _calculate_score(self, url: str) -> float:
                score = 0.0
                if url.lower().endswith(('.html', '.htm', '.php')):
                    score += 0.5
                if 'article' in url.lower():
                    score += 0.5
                return min(score, 1.0) # Cap score at 1.0

        # Usage:
        # article_scorer = ArticlePageScorer(weight=0.8)
        # composite_scorer = CompositeScorer(scorers=[article_scorer, ...])
        ```

*   **11.5. Integrating Deep Crawling with Other Crawl4ai Features**
    *   **Combining with Extraction Strategies:**
        *   **How it works:** The `DeepCrawlStrategy` (BFS, DFS, Best-First) is responsible for discovering and fetching pages. Each `CrawlResult` object it yields (in stream mode) or returns (in batch mode) contains the HTML content. This `CrawlResult` is then passed to the extraction pipeline defined in your `CrawlerRunConfig` (e.g., `LLMExtractionStrategy`, `JsonCssExtractionStrategy`).
        *   **Data Flow:** `DeepCrawlStrategy` produces `CrawlResult` -> `AsyncWebCrawler`'s main loop -> `ExtractionStrategy` (if defined) consumes `CrawlResult.html` or `CrawlResult.markdown` -> Populates `CrawlResult.extracted_content`.
        *   **Ensuring Compatibility:** Built-in deep crawl strategies yield standard `CrawlResult` objects, which are directly usable by extraction strategies. If you build a very custom strategy, ensure it also yields or returns `CrawlResult` instances.
    *   **Authenticated Deep Crawls:**
        *   **Challenge:** Many websites require login to access deeper content. A deep crawl needs to maintain this session.
        *   **Solution:**
            1.  **Initial Login:** Perform a separate, initial `crawler.arun()` call to the login page. Use `js_code` to fill in login forms and submit.
            2.  **Save Session State:** After successful login, save the browser's `storage_state` (cookies, localStorage):
                ```python
                # In the login part of your script
                # login_page_result = await crawler.arun(...)
                # await page.context.storage_state(path="my_session_state.json")
                ```
                (Assuming `page` is accessible, or via a hook that gets the context). A more robust way is to use a dedicated `BrowserConfig` with `user_data_dir` for persistence across crawler instances, or use the `session_id` feature if you keep the same crawler instance.
            3.  **Deep Crawl with Session:** For the subsequent deep crawl, configure `BrowserConfig` to use this saved state or `CrawlerRunConfig` to reuse a session via `session_id`:
                ```python
                # Option A: Persistent context via user_data_dir (for multiple crawler instances)
                # browser_config_authed = BrowserConfig(user_data_dir="path/to/my_profile_with_login")
                # async with AsyncWebCrawler(config=browser_config_authed) as authed_crawler:
                #    await authed_crawler.arun(..., config=deep_crawl_run_config)

                # Option B: Reusing a session within the same crawler instance
                # deep_crawl_run_config.session_id = "my_authed_session"
                # (after initial login that established this session)
                # await crawler.arun(..., config=deep_crawl_run_config)
                ```
        *   **Considerations:**
            *   **Token Refresh/Session Expiry:** Long crawls might encounter session expiry. More advanced solutions might need hooks or custom logic to detect expired sessions and re-authenticate.
            *   **AJAX/SPA Logins:** Ensure login interactions are fully completed (e.g., using `wait_for` for redirection or dashboard elements) before saving state or proceeding.
        *   `* Scenario Walkthrough: [Conceptual steps for deep crawling a members-only forum]`
            1.  Create `CrawlerRunConfig` for login: `js_code` to fill login form, `wait_for` a dashboard element.
            2.  `crawler.arun()` to login page with this config. Save `session_id` (e.g., "forum_session").
            3.  Create `CrawlerRunConfig` for deep crawl:
                *   `deep_crawl_strategy` (e.g., BFS to find all threads).
                *   `session_id="forum_session"` to reuse the logged-in state.
                *   Filters to stay within forum sections.
            4.  `crawler.arun()` with the forum's starting URL and deep crawl config.

## 12. Conclusion and Further Exploration

Crawl4ai's `deep_crawling` component offers a powerful and flexible toolkit for exploring websites beyond a single page. By understanding and combining strategies, filters, and scorers, you can tailor your crawls to a wide variety of tasks, from comprehensive site indexing to highly targeted data extraction.

*   **Recap:**
    *   Choose the right **strategy** (BFS, DFS, Best-First) based on your exploration goals.
    *   Use **filters** (`DomainFilter`, `ContentTypeFilter`, `URLPatternFilter`, etc.) to precisely define the scope of your crawl and improve efficiency.
    *   Leverage **scorers** (especially with `BestFirstCrawlingStrategy`) to prioritize URLs and focus on the most relevant content.
    *   Configure everything through `CrawlerRunConfig` and its `deep_crawl_strategy` parameter.
    *   Monitor your crawls using `TraversalStats` and logs to optimize performance.
*   **Encouragement:** The best way to master deep crawling is to experiment!
    *   Start with simple configurations and gradually add complexity.
    *   Test different filter combinations and scorer weightings.
    *   Observe how your changes affect the crawl path and results.
*   **Pointers to Other Relevant Documentation:**
    *   **Basic Crawling:** [Simple Crawling Guide](../core/simple-crawling.md)
    *   **Configuration:** [Browser, Crawler & LLM Configuration](../core/browser-crawler-config.md)
    *   **Specific Filters/Scorers API:** (Refer to API documentation if available, or source code comments)
    *   **Extraction Strategies:** [No-LLM Extraction Strategies](../extraction/no-llm-strategies.md), [LLM-based Extraction](../extraction/llm-extraction.md)
    *   **Session Management & Authentication:** [Session Management](./session-management.md), [Hooks & Auth](./hooks-auth.md)
    *   **Advanced Page Interaction:** [Page Interaction](./page-interaction.md)

Happy deep crawling with Crawl4ai!
```

---


## Deep Crawling - Examples
Source: crawl4ai_deep_crawling_examples_content.llm.md

```markdown
# Examples Outline for crawl4ai - deep_crawling Component

**Target Document Type:** Examples Collection
**Target Output Filename Suggestion:** `llm_examples_deep_crawling.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2025-05-24
---

This document provides a collection of runnable Python code examples for the `deep_crawling` component of the `crawl4ai` library. Each example aims to demonstrate a specific feature or usage pattern.

---
## 1. Deep Crawling Strategies

This section will cover the different traversal and processing strategies available for deep crawling.

### 1.1. `DeepCrawlDecorator`

#### 1.1.1. Example: Basic application of `DeepCrawlDecorator` to an `AsyncWebCrawler` instance.

This example shows how to apply the `DeepCrawlDecorator` to an `AsyncWebCrawler` instance, which augments its `arun` method with deep crawling capabilities.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import DeepCrawlDecorator, BFSDeeepCrawlStrategy

# Basic setup - crawl4ai_server needs to be running for live examples
# For simplicity, we'll often use example.com or raw HTML for self-contained tests.

async def decorator_basic_application():
    crawler = AsyncWebCrawler()
    # The decorator enhances the crawler instance
    deep_crawl_decorator = DeepCrawlDecorator(crawler)
    
    # The original arun method is still available if needed
    # For deep crawling, the decorated arun will be used implicitly 
    # when a deep_crawl_strategy is set in CrawlerRunConfig.
    
    print(f"Crawler 'arun' method before decoration: {crawler.arun}")
    
    # Apply the decorator
    # This typically happens inside the AsyncWebCrawler when a strategy is provided
    # but for demonstration, we can show it being applied manually.
    # In practice, you don't call DeepCrawlDecorator directly like this for arun.
    # The AsyncWebCrawler's __init__ or arun method would handle this.
    # This example is more conceptual to show the decorator's existence.

    # A more realistic scenario is providing the strategy to CrawlerRunConfig:
    bfs_strategy = BFSDeeepCrawlStrategy(max_depth=0)
    config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)

    # When arun is called with a config that has a deep_crawl_strategy,
    # the decorator's logic (if active) would take over.
    # Let's simulate a simple crawl
    try:
        async with crawler: # Ensure crawler is started and closed
            result = await crawler.arun(url="http://example.com", config=config)
            if result.success:
                print(f"Successfully crawled {result.url} using decorator (implicitly).")
                print(f"Decorator active status: {deep_crawl_decorator.deep_crawl_active.get()}")
            else:
                print(f"Crawl failed: {result.error_message}")
    except Exception as e:
        print(f"An error occurred: {e}")


asyncio.run(decorator_basic_application())
```

#### 1.1.2. Example: Triggering a deep crawl via the decorated `arun` method using `BFSDeeepCrawlStrategy`.

This example demonstrates how providing a `deep_crawl_strategy` in `CrawlerRunConfig` automatically triggers the deep crawling logic managed by `DeepCrawlDecorator`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

async def trigger_deep_crawl_with_decorator():
    # Define a BFS strategy
    bfs_strategy = BFSDeeepCrawlStrategy(max_depth=1, max_pages=3) 
    
    # Configure the crawler run to use this strategy
    run_config = CrawlerRunConfig(
        deep_crawl_strategy=bfs_strategy,
        # For real crawls, ensure verbosity or specific logging for clarity
        # For this example, we'll print basic info from results
    )

    async with AsyncWebCrawler() as crawler:
        # The DeepCrawlDecorator is implicitly active due to deep_crawl_strategy in config
        print(f"Starting deep crawl with BFS strategy for http://example.com (max_depth=1, max_pages=3)")
        results_container = await crawler.arun(url="http://example.com", config=run_config)
        
        crawled_count = 0
        if results_container: # arun returns a list/generator container
            print("\n--- Crawl Results ---")
            async for result in results_container: # If stream=True
                if result.success:
                    crawled_count += 1
                    print(f"Crawled: {result.url} (Depth: {result.metadata.get('depth', 'N/A')})")
                else:
                    print(f"Failed: {result.url} - {result.error_message}")
            if not isinstance(results_container, types.AsyncGeneratorType): # if stream=False (batch mode)
                 for result in results_container:
                    if result.success:
                        crawled_count +=1
                        print(f"Crawled: {result.url} (Depth: {result.metadata.get('depth', 'N/A')})")
                    else:
                        print(f"Failed: {result.url} - {result.error_message}")


        print(f"\nTotal pages processed by deep crawl: {crawled_count}")

# Note: example.com might not have many links or varied depth.
# For a more illustrative output, a mock server or a known simple site would be better.
import types
asyncio.run(trigger_deep_crawl_with_decorator())
```

#### 1.1.3. Example: Showing `DeepCrawlDecorator` respects the `deep_crawl_active` context to prevent recursion.

This example conceptually illustrates how `DeepCrawlDecorator` uses a `ContextVar` (`deep_crawl_active`) to prevent recursive deep crawls if the decorated method were to call itself indirectly with another deep crawl strategy.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import DeepCrawlDecorator, BFSDeeepCrawlStrategy

async def decorator_recursion_prevention():
    # This is a conceptual example. In a real scenario, the AsyncWebCrawler
    # manages the decorator and its context.
    
    crawler_instance = AsyncWebCrawler()
    decorator = DeepCrawlDecorator(crawler_instance)

    # Simulate an initial call that sets the context
    print(f"Initial deep_crawl_active: {decorator.deep_crawl_active.get()}")
    token = decorator.deep_crawl_active.set(True)
    print(f"After setting, deep_crawl_active: {decorator.deep_crawl_active.get()}")

    # Now, imagine original_arun (if called within the strategy) tries to start another deep crawl
    # The decorator's __call__ would check deep_crawl_active.get()
    # If True, it would call the original_arun directly, not the strategy.

    # Simulate what would happen if a nested deep crawl was attempted:
    # A config that would normally trigger a deep crawl
    nested_strategy = BFSDeeepCrawlStrategy(max_depth=0)
    nested_config = CrawlerRunConfig(deep_crawl_strategy=nested_strategy)

    # If decorator.__call__(original_arun) is invoked while deep_crawl_active is True:
    if nested_config.deep_crawl_strategy and not decorator.deep_crawl_active.get():
        print("This part (nested deep crawl strategy execution) should NOT be reached if active.")
        # strategy_result = await nested_strategy.arun(...) 
    elif nested_config.deep_crawl_strategy and decorator.deep_crawl_active.get():
        print("Deep crawl already active. Nested strategy will be bypassed, original_arun would be called.")
        # original_arun_result = await original_arun(...)
    else:
        print("Not a deep crawl config or context not active.")

    decorator.deep_crawl_active.reset(token)
    print(f"After reset, deep_crawl_active: {decorator.deep_crawl_active.get()}")
    
    # In a real run with AsyncWebCrawler, this management is internal.
    # This example is to show the ContextVar's role.

asyncio.run(decorator_recursion_prevention())
```

### 1.2. `DeepCrawlStrategy` (Abstract Base Class - Conceptual)

#### 1.2.1. Note: This is an ABC.
Examples will use concrete implementations like `BFSDeeepCrawlStrategy`, `DFSDeeepCrawlStrategy`, and `BestFirstCrawlingStrategy`. This section provides conceptual examples of how the base strategy's `arun` method works.

#### 1.2.2. Example: Conceptual demonstration of the `arun` method dispatching to `_arun_batch` (non-streaming).

This shows that if `config.stream` is `False` (or not set, as `False` is default for strategies not explicitly setting it), the `arun` method of a `DeepCrawlStrategy` (like `BFSDeeepCrawlStrategy`) will internally call its `_arun_batch` method.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy # Using BFS as a concrete example

async def conceptual_arun_batch_dispatch():
    strategy = BFSDeeepCrawlStrategy(max_depth=0) # max_depth=0 for minimal crawl
    config = CrawlerRunConfig(stream=False) # Explicitly non-streaming

    # Mock the _arun_batch method to confirm it's called
    original_arun_batch = strategy._arun_batch
    called_arun_batch = False
    async def mock_arun_batch(*args, **kwargs):
        nonlocal called_arun_batch
        called_arun_batch = True
        # Simulate returning a list of results
        return await original_arun_batch(*args, **kwargs) 
    strategy._arun_batch = mock_arun_batch

    async with AsyncWebCrawler() as crawler:
        await strategy.arun(start_url="http://example.com", crawler=crawler, config=config)

    if called_arun_batch:
        print("Conceptual: strategy.arun() correctly dispatched to _arun_batch() for non-streaming mode.")
    else:
        print("Conceptual: strategy.arun() DID NOT dispatch to _arun_batch().")
    
    # Restore original method
    strategy._arun_batch = original_arun_batch

asyncio.run(conceptual_arun_batch_dispatch())
```

#### 1.2.3. Example: Conceptual demonstration of the `arun` method dispatching to `_arun_stream` (streaming).

This shows that if `config.stream` is `True`, the `arun` method of a `DeepCrawlStrategy` (like `BFSDeeepCrawlStrategy`) will internally call its `_arun_stream` method.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy # Using BFS as a concrete example

async def conceptual_arun_stream_dispatch():
    strategy = BFSDeeepCrawlStrategy(max_depth=0)
    config = CrawlerRunConfig(stream=True) # Explicitly streaming

    # Mock the _arun_stream method
    original_arun_stream = strategy._arun_stream
    called_arun_stream = False
    async def mock_arun_stream(*args, **kwargs):
        nonlocal called_arun_stream
        called_arun_stream = True
        # Simulate yielding results from an async generator
        async for item in original_arun_stream(*args, **kwargs):
            yield item
    strategy._arun_stream = mock_arun_stream
    
    async with AsyncWebCrawler() as crawler:
        async for _ in strategy.arun(start_url="http://example.com", crawler=crawler, config=config):
            pass # Consume the generator

    if called_arun_stream:
        print("Conceptual: strategy.arun() correctly dispatched to _arun_stream() for streaming mode.")
    else:
        print("Conceptual: strategy.arun() DID NOT dispatch to _arun_stream().")

    # Restore original method
    strategy._arun_stream = original_arun_stream

asyncio.run(conceptual_arun_stream_dispatch())
```

#### 1.2.4. Example: Demonstrating `ValueError` when `CrawlerRunConfig` is not provided to `arun`.

This example demonstrates that calling `strategy.arun(...)` without a `config` (or with `config=None`) raises a `ValueError`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

async def arun_without_config():
    strategy = BFSDeeepCrawlStrategy(max_depth=0)
    async with AsyncWebCrawler() as crawler:
        try:
            await strategy.arun(start_url="http://example.com", crawler=crawler, config=None)
        except ValueError as e:
            print(f"Caught expected ValueError: {e}")
        except Exception as e:
            print(f"Caught unexpected error: {e}")
        else:
            print("ValueError was not raised as expected.")

asyncio.run(arun_without_config())
```

#### 1.2.5. Example: Demonstrating the `__call__` method making the strategy instance callable.

The `__call__` method allows a strategy instance to be called directly like a function, which internally calls its `arun` method.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

async def strategy_is_callable():
    strategy = BFSDeeepCrawlStrategy(max_depth=0, max_pages=1)
    config = CrawlerRunConfig()

    async with AsyncWebCrawler() as crawler:
        print("Calling strategy instance directly using __call__...")
        # This is equivalent to strategy.arun(...)
        results_container = await strategy(start_url="http://example.com", crawler=crawler, config=config)
        
        if results_container:
            for result in results_container: # If batch mode
                 if result.success:
                    print(f"Callable strategy crawled: {result.url}")
                 else:
                    print(f"Callable strategy failed for {result.url}: {result.error_message}")
        else:
            print("Strategy call did not return results.")

asyncio.run(strategy_is_callable())
```

### 1.3. `BFSDeeepCrawlStrategy` (Breadth-First Search)

#### 1.3.1. **Initialization & Basic Usage**

##### 1.3.1.1. Example: Initializing `BFSDeeepCrawlStrategy` with a `max_depth` of 1 and performing a basic batch crawl.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

async def bfs_basic_batch_crawl():
    # Initialize BFS strategy: crawl up to 1 level deep from the start URL
    # and fetch a maximum of 5 pages in total.
    bfs_strategy = BFSDeeepCrawlStrategy(max_depth=1, max_pages=5)
    
    # Create a run configuration using this strategy
    # stream=False is the default for batch mode
    run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting BFS batch crawl (max_depth=1, max_pages=5) on http://example.com...")
        # arun returns a list of CrawlResult objects in batch mode
        results_list = await crawler.arun(url="http://example.com", config=run_config)
        
        print(f"\n--- BFS Batch Crawl Results (max_depth=1, max_pages=5) ---")
        if results_list:
            for result in results_list:
                if result.success:
                    print(f"Crawled: {result.url} (Depth: {result.metadata.get('depth')})")
                else:
                    print(f"Failed: {result.url} - {result.error_message}")
            print(f"Total pages processed: {len(results_list)}")
        else:
            print("No results returned from crawl.")

# Note: example.com has very few links, so it might not reach max_pages=5 or depth=1.
# A site with more links like docs.crawl4ai.com would be more illustrative if accessible.
asyncio.run(bfs_basic_batch_crawl())
```

##### 1.3.1.2. Example: Performing a BFS crawl in stream mode (`config.stream=True`).

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

async def bfs_stream_crawl():
    # Initialize BFS strategy
    bfs_strategy = BFSDeeepCrawlStrategy(max_depth=1, max_pages=3)
    
    # Enable stream mode in the run configuration
    run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy, stream=True)

    async with AsyncWebCrawler() as crawler:
        print("Starting BFS stream crawl (max_depth=1, max_pages=3) on http://example.com...")
        # arun returns an async generator in stream mode
        results_generator = await crawler.arun(url="http://example.com", config=run_config)
        
        print(f"\n--- BFS Stream Crawl Results ---")
        processed_count = 0
        async for result in results_generator:
            processed_count +=1
            if result.success:
                print(f"Streamed: {result.url} (Depth: {result.metadata.get('depth')})")
            else:
                print(f"Stream Failed: {result.url} - {result.error_message}")
        print(f"Total pages streamed: {processed_count}")

asyncio.run(bfs_stream_crawl())
```

#### 1.3.2. **Controlling Crawl Depth and Scope**

##### 1.3.2.1. Example: Demonstrating `max_depth` limiting the crawl (e.g., `max_depth=0` for only the start URL).

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

async def bfs_max_depth_zero():
    # max_depth=0 means only the starting URL will be crawled.
    bfs_strategy = BFSDeeepCrawlStrategy(max_depth=0, max_pages=5) # max_pages won't be hit
    run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting BFS crawl with max_depth=0 on http://example.com...")
        results_list = await crawler.arun(url="http://example.com", config=run_config)
        
        print(f"\n--- BFS Crawl Results (max_depth=0) ---")
        if results_list:
            for result in results_list:
                print(f"Crawled: {result.url} (Depth: {result.metadata.get('depth')})")
            print(f"Total pages processed: {len(results_list)}")
            assert len(results_list) == 1, "Should only crawl the start URL with max_depth=0"
            assert results_list[0].metadata.get('depth') == 0, "Depth should be 0"
        else:
            print("No results returned.")

asyncio.run(bfs_max_depth_zero())
```

##### 1.3.2.2. Example: Demonstrating `max_pages` limiting the number of crawled pages.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

# For this example, we'll use a site that likely has more than 2 links accessible
# from the start page to demonstrate max_pages.
# If docs.crawl4ai.com is not available, replace with another suitable site.
# Or, use raw HTML with multiple links.
TARGET_URL = "https://docs.crawl4ai.com/core/async-web-crawler/" 

async def bfs_max_pages_limit():
    # Crawl up to depth 2, but stop after 2 pages.
    bfs_strategy = BFSDeeepCrawlStrategy(max_depth=2, max_pages=2)
    run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print(f"Starting BFS crawl with max_pages=2 on {TARGET_URL}...")
        results_list = await crawler.arun(url=TARGET_URL, config=run_config)
        
        print(f"\n--- BFS Crawl Results (max_pages=2) ---")
        crawled_urls = []
        if results_list:
            for result in results_list:
                if result.success:
                    print(f"Crawled: {result.url} (Depth: {result.metadata.get('depth')})")
                    crawled_urls.append(result.url)
            print(f"Total pages processed: {len(results_list)}")
            # The number of results might be slightly more than max_pages
            # due to how BFS processes levels, but pages_crawled stat should be accurate.
            # print(f"Strategy stats: Pages crawled = {bfs_strategy.stats._pages_crawled}")
            # For simplicity, we check len(results_list) but acknowledge bfs_strategy.stats is more precise.
            assert len(crawled_urls) <= 2, "Should process at most max_pages"
        else:
            print("No results returned.")

asyncio.run(bfs_max_pages_limit())
```

##### 1.3.2.3. Example: BFS crawl including external links (`include_external=True`).

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

# We need a page with known external links. example.com might have iana.org.
# For a more robust test, a mock HTML would be better.
RAW_HTML_WITH_EXTERNAL_LINK = """
<html><body>
    <a href="http://example.com/internal">Internal Link</a>
    <a href="https://www.iana.org/domains/reserved">External IANA Link</a>
    <a href="http://another-external.com">Another External</a>
</body></html>
"""
START_URL_RAW = f"raw://{RAW_HTML_WITH_EXTERNAL_LINK}"


async def bfs_include_external():
    # Crawl depth 1, include external links, limit to 3 pages to see some externals.
    bfs_strategy = BFSDeeepCrawlStrategy(max_depth=1, max_pages=3, include_external=True)
    run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print(f"Starting BFS crawl including external links (max_depth=1, max_pages=3)...")
        results_list = await crawler.arun(url=START_URL_RAW, config=run_config)
        
        print(f"\n--- BFS Crawl Results (include_external=True) ---")
        external_found = False
        if results_list:
            for result in results_list:
                if result.success:
                    print(f"Crawled: {result.url} (Depth: {result.metadata.get('depth')})")
                    if "iana.org" in result.url or "another-external.com" in result.url:
                        external_found = True
                else:
                    print(f"Failed: {result.url} - {result.error_message}")
            print(f"Total pages processed: {len(results_list)}")
            assert external_found, "Expected to crawl at least one external link."
        else:
            print("No results returned.")

asyncio.run(bfs_include_external())
```

#### 1.3.3. **Filtering and Scoring**

##### 1.3.3.1. Example: Using `BFSDeeepCrawlStrategy` with a `FilterChain` to include/exclude specific URLs.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy, FilterChain, URLPatternFilter, DomainFilter

RAW_HTML_FOR_FILTERING = """
<html><body>
    <a href="http://example.com/page1.html">Page 1 (HTML)</a>
    <a href="http://example.com/image.png">Image (PNG)</a>
    <a href="http://example.com/docs/doc1.pdf">Doc 1 (PDF)</a>
    <a href="http://external.com/anotherpage">External Page</a>
    <a href="http://example.com/blog/post1">Blog Post 1</a>
</body></html>
"""
START_URL_RAW_FILTER = f"raw://{RAW_HTML_FOR_FILTERING}"

async def bfs_with_filter_chain():
    # Allow only HTML files from example.com
    filter_chain = FilterChain(filters=[
        DomainFilter(allowed_domains=["example.com"]),
        URLPatternFilter(patterns=["*.html"]) 
    ])
    
    bfs_strategy = BFSDeeepCrawlStrategy(max_depth=1, max_pages=5, filter_chain=filter_chain)
    run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting BFS crawl with FilterChain (allow *.html from example.com)...")
        results_list = await crawler.arun(url=START_URL_RAW_FILTER, config=run_config)
        
        print(f"\n--- BFS Crawl Results (with FilterChain) ---")
        crawled_urls = []
        if results_list:
            for result in results_list:
                if result.success:
                    print(f"Crawled: {result.url}")
                    crawled_urls.append(result.url)
            print(f"Total pages processed: {len(results_list)}")
            
            assert all("example.com" in url for url in crawled_urls if url != START_URL_RAW_FILTER), "Only example.com URLs should be crawled (excluding start)."
            assert all(url.endswith(".html") for url in crawled_urls if url != START_URL_RAW_FILTER), "Only .html URLs should be crawled (excluding start)."
            assert "http://example.com/page1.html" in crawled_urls
            assert "http://example.com/image.png" not in crawled_urls
            assert "http://example.com/docs/doc1.pdf" not in crawled_urls
            assert "http://external.com/anotherpage" not in crawled_urls
            assert "http://example.com/blog/post1" not in crawled_urls

        else:
            print("No results returned.")

asyncio.run(bfs_with_filter_chain())
```

##### 1.3.3.2. Example: Using `BFSDeeepCrawlStrategy` with a `url_scorer` and `score_threshold` to prune links.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy, PathDepthScorer

RAW_HTML_FOR_SCORING = """
<html><body>
    <a href="/page1">Page 1 (depth 1)</a>
    <a href="/category/page2">Page 2 (depth 2)</a>
    <a href="/category/sub/page3">Page 3 (depth 3)</a>
    <a href="/very/deep/path/page4">Page 4 (depth 4)</a>
</body></html>
"""
START_URL_RAW_SCORE = f"raw://{RAW_HTML_FOR_SCORING}"


async def bfs_with_scorer_and_threshold():
    # Score by path depth, optimal depth is 1.
    # Threshold will prune links that are too deep (lower score).
    # PathDepthScorer gives 1.0 for optimal, 0.5 for diff 1, 0.33 for diff 2, etc.
    url_scorer = PathDepthScorer(optimal_depth=1) 
    score_threshold = 0.4  # This should allow depth 1 (score 1.0) and depth 2 (score 0.5) links, but not depth 3 (score 0.33)

    bfs_strategy = BFSDeeepCrawlStrategy(
        max_depth=3, 
        max_pages=5, 
        url_scorer=url_scorer, 
        score_threshold=score_threshold
    )
    run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting BFS crawl with URL scorer and threshold (optimal_depth=1, threshold=0.4)...")
        results_list = await crawler.arun(url=START_URL_RAW_SCORE, config=run_config)
        
        print(f"\n--- BFS Crawl Results (with Scorer & Threshold) ---")
        crawled_urls = []
        if results_list:
            for result in results_list:
                if result.success:
                    print(f"Crawled: {result.url} (Depth: {result.metadata.get('depth')}, Score: {result.metadata.get('score', 'N/A')})")
                    crawled_urls.append(result.url)
            print(f"Total pages processed: {len(results_list)}")
            
            assert any("/page1" in url for url in crawled_urls)
            assert any("/category/page2" in url for url in crawled_urls)
            assert not any("/category/sub/page3" in url for url in crawled_urls)
            assert not any("/very/deep/path/page4" in url for url in crawled_urls)
        else:
            print("No results returned.")

asyncio.run(bfs_with_scorer_and_threshold())
```

#### 1.3.4. **URL Processing Logic**

##### 1.3.4.1. Example: Demonstrating `can_process_url` for valid and invalid URL formats (e.g., missing scheme, unsupported scheme).

The `can_process_url` method is primarily used internally by strategies. We can test its behavior directly for demonstration.

```python
import asyncio
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

async def demo_can_process_url_formats():
    strategy = BFSDeeepCrawlStrategy(max_depth=1) # Filters are not applied at depth 0 by default

    print("Testing can_process_url (at depth=1, default filters):")
    
    valid_http_url = "http://example.com/page"
    can_process_http = await strategy.can_process_url(valid_http_url, depth=1)
    print(f"Can process '{valid_http_url}'? {can_process_http}")
    assert can_process_http

    valid_https_url = "https://example.com/secure"
    can_process_https = await strategy.can_process_url(valid_https_url, depth=1)
    print(f"Can process '{valid_https_url}'? {can_process_https}")
    assert can_process_https

    url_missing_scheme = "example.com/page" # This would typically be resolved by normalize_url_for_deep_crawl
                                          # but can_process_url expects a full URL.
                                          # Let's assume it's already normalized to http://example.com/page
    # For direct test of can_process_url, it would fail if scheme is missing before normalization
    # Assuming it's passed post-normalization phase where scheme is present for this check
    
    url_ftp_scheme = "ftp://example.com/file"
    can_process_ftp = await strategy.can_process_url(url_ftp_scheme, depth=1)
    print(f"Can process '{url_ftp_scheme}' (unsupported scheme)? {can_process_ftp}")
    assert not can_process_ftp # FTP is not a supported scheme by default

    url_no_netloc = "http:///page" # Invalid netloc
    can_process_no_netloc = await strategy.can_process_url(url_no_netloc, depth=1)
    print(f"Can process '{url_no_netloc}' (no netloc)? {can_process_no_netloc}")
    assert not can_process_no_netloc
    
    # Depth 0 always bypasses filters in default can_process_url logic of strategies
    can_process_depth_zero = await strategy.can_process_url(url_ftp_scheme, depth=0)
    print(f"Can process '{url_ftp_scheme}' at depth 0 (bypassing filters)? {can_process_depth_zero}")
    assert can_process_depth_zero

asyncio.run(demo_can_process_url_formats())
```

##### 1.3.4.2. Example: Demonstrating `can_process_url` with a `filter_chain` that rejects certain URLs.

```python
import asyncio
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy, FilterChain, URLPatternFilter

async def demo_can_process_url_with_filter():
    # Filter chain that rejects URLs containing "admin"
    filter_chain = FilterChain(filters=[
        URLPatternFilter(patterns=["*admin*"], reverse=True) # reverse=True means reject if matches
    ])
    strategy = BFSDeeepCrawlStrategy(max_depth=1, filter_chain=filter_chain)

    print("Testing can_process_url with a filter_chain (rejecting '*admin*'):")

    url_to_allow = "http://example.com/dashboard"
    can_process_allow = await strategy.can_process_url(url_to_allow, depth=1)
    print(f"Can process '{url_to_allow}'? {can_process_allow}")
    assert can_process_allow

    url_to_reject = "http://example.com/admin/login"
    can_process_reject = await strategy.can_process_url(url_to_reject, depth=1)
    print(f"Can process '{url_to_reject}'? {can_process_reject}")
    assert not can_process_reject

asyncio.run(demo_can_process_url_with_filter())
```

#### 1.3.5. **Link Discovery**

The `link_discovery` method is internal. Its effects are best observed through the URLs selected for the next level of a crawl.

##### 1.3.5.1. Example: Showing how `link_discovery` populates the `next_level` for BFS.

This conceptual example shows how `link_discovery` (if it were public and directly callable for this purpose) would take a `CrawlResult` and populate a `next_level` list.

```python
import asyncio
from crawl4ai.models import CrawlResult, Links, Link
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy
from crawl4ai.utils import normalize_url_for_deep_crawl

# Simulate a CrawlResult
mock_crawl_result = CrawlResult(
    url="http://example.com/source",
    html="<a href='/page1'>Page 1</a> <a href='page2.html'>Page 2</a>",
    success=True,
    links=Links(
        internal=[
            Link(href="/page1", text="Page 1"),
            Link(href="page2.html", text="Page 2")
        ],
        external=[]
    )
)

async def demo_link_discovery_populates_next_level():
    strategy = BFSDeeepCrawlStrategy(max_depth=1)
    
    # Simulate internal state for link_discovery
    source_url = mock_crawl_result.url
    current_depth = 0
    visited = {source_url}
    next_level_links = [] # This is what link_discovery populates
    depths = {source_url: 0}

    # Call link_discovery (conceptually)
    # In real code, this is an internal method: strategy.link_discovery(...)
    # We'll manually simulate its core logic for this demonstration.
    
    next_depth = current_depth + 1
    if next_depth <= strategy.max_depth:
        discovered_links_from_result = []
        for link_type in ["internal", "external"] if strategy.include_external else ["internal"]:
            for link_obj in getattr(mock_crawl_result.links, link_type, []):
                link_href = link_obj.href
                if link_href:
                    # Normalize URL (simplified for example)
                    abs_url = normalize_url_for_deep_crawl(link_href, source_url)
                    if abs_url and abs_url not in visited:
                        if await strategy.can_process_url(abs_url, next_depth):
                             if strategy.url_scorer:
                                score = await strategy.url_scorer.score(abs_url)
                                if score < strategy.score_threshold:
                                    strategy.stats.urls_skipped +=1
                                    continue
                             discovered_links_from_result.append((abs_url, source_url))
                             visited.add(abs_url)
                             depths[abs_url] = next_depth
        
        next_level_links.extend(discovered_links_from_result)


    print(f"Source URL: {source_url}")
    print(f"Discovered and added to next_level (url, parent_url):")
    for link_info in next_level_links:
        print(f"  - {link_info[0]} (from {link_info[1]}) at depth {depths[link_info[0]]}")

    assert ("http://example.com/page1", "http://example.com/source") in next_level_links
    assert ("http://example.com/page2.html", "http://example.com/source") in next_level_links
    assert depths.get("http://example.com/page1") == 1
    assert depths.get("http://example.com/page2.html") == 1

asyncio.run(demo_link_discovery_populates_next_level())
```

##### 1.3.5.2. Example: How `link_discovery` respects `max_pages` when adding new links.

This conceptual example shows how `link_discovery` would limit adding new links if `max_pages` is about to be reached.

```python
import asyncio
from crawl4ai.models import CrawlResult, Links, Link
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy
from crawl4ai.utils import normalize_url_for_deep_crawl


mock_crawl_result_many_links = CrawlResult(
    url="http://example.com/source_many",
    html="""
        <a href="/link1">1</a> <a href="/link2">2</a> <a href="/link3">3</a>
        <a href="/link4">4</a> <a href="/link5">5</a>
    """,
    success=True,
    links=Links(
        internal=[
            Link(href="/link1"), Link(href="/link2"), Link(href="/link3"),
            Link(href="/link4"), Link(href="/link5")
        ]
    )
)

async def demo_link_discovery_respects_max_pages():
    # Max 3 pages total, already crawled 1 (the start URL)
    # So, only 2 more pages can be added from discovered links.
    strategy = BFSDeeepCrawlStrategy(max_depth=1, max_pages=3)
    strategy._pages_crawled = 1 # Simulate start URL already crawled

    source_url = mock_crawl_result_many_links.url
    current_depth = 0
    visited = {source_url}
    next_level_links_tuples = []
    depths = {source_url: 0}

    # Manual simulation of link_discovery's core logic for this specific scenario
    next_depth = current_depth + 1
    valid_links_to_consider = []
    
    if next_depth <= strategy.max_depth:
        for link_type in ["internal"]: # Assuming include_external is False
            for link_obj in getattr(mock_crawl_result_many_links.links, link_type, []):
                link_href = link_obj.href
                if link_href:
                    abs_url = normalize_url_for_deep_crawl(link_href, source_url)
                    if abs_url and abs_url not in visited:
                        if await strategy.can_process_url(abs_url, next_depth):
                            valid_links_to_consider.append(abs_url)
                            # visited.add(abs_url) # Add to visited only if selected
                            # depths[abs_url] = next_depth # Add depth only if selected
    
    remaining_capacity = strategy.max_pages - strategy._pages_crawled
    
    if remaining_capacity > 0 and valid_links_to_consider:
        # If scoring is involved, links would be sorted by score here. For simplicity, we take first N.
        selected_links = valid_links_to_consider[:remaining_capacity]
        if len(valid_links_to_consider) > remaining_capacity and strategy.logger:
            strategy.logger.info(f"Limiting to {remaining_capacity} URLs due to max_pages limit")
            
        for sel_url in selected_links:
            next_level_links_tuples.append((sel_url, source_url))
            visited.add(sel_url)
            depths[sel_url] = next_depth

    print(f"Source URL: {source_url}")
    print(f"Pages already crawled: {strategy._pages_crawled}")
    print(f"Max pages: {strategy.max_pages}, Remaining capacity: {remaining_capacity}")
    print(f"Discovered and added to next_level due to max_pages limit:")
    for link_url, parent_url in next_level_links_tuples:
        print(f"  - {link_url} (from {parent_url}) at depth {depths.get(link_url)}")
    
    assert len(next_level_links_tuples) <= remaining_capacity, f"Expected {remaining_capacity} links, got {len(next_level_links_tuples)}"
    assert len(next_level_links_tuples) == 2 # 3 (max_pages) - 1 (already_crawled) = 2

asyncio.run(demo_link_discovery_respects_max_pages())
```

#### 1.3.6. **Shutdown**

##### 1.3.6.1. Example: Demonstrating the `shutdown` method and its effect on crawl stats (e.g., `end_time`).

```python
import asyncio
import time
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

async def demo_shutdown_method():
    strategy = BFSDeeepCrawlStrategy(max_depth=1)
    print(f"Initial strategy stats: Start time: {strategy.stats.start_time}, End time: {strategy.stats.end_time}")
    
    # Simulate some activity
    strategy.stats.urls_processed = 5
    await asyncio.sleep(0.1) # Simulate time passing
    
    await strategy.shutdown()
    
    print(f"Stats after shutdown: Start time: {strategy.stats.start_time}, End time: {strategy.stats.end_time}")
    assert strategy.stats.end_time is not None, "End time should be set after shutdown"
    assert strategy.stats.end_time > strategy.stats.start_time, "End time should be after start time"

asyncio.run(demo_shutdown_method())
```

### 1.4. `DFSDeeepCrawlStrategy` (Depth-First Search)

#### 1.4.1. **Initialization & Basic Usage**

##### 1.4.1.1. Example: Initializing `DFSDeeepCrawlStrategy` with a `max_depth` of 2 and performing a basic batch DFS crawl.
For DFS, a site with clear branching is needed to see the depth-first behavior. `example.com` has limited depth. We'll use a mock structure.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import DFSDeeepCrawlStrategy

# Mock HTML for DFS demonstration
# Page A -> B, C
# Page B -> D
# Page C -> E
RAW_HTML_DFS_A = "<html><body><a href='raw://PAGE_B'>B</a> <a href='raw://PAGE_C'>C</a></body></html>"
RAW_HTML_DFS_B = "<html><body><a href='raw://PAGE_D'>D</a></body></html>"
RAW_HTML_DFS_C = "<html><body><a href='raw://PAGE_E'>E</a></body></html>"
RAW_HTML_DFS_D = "<html><body>Depth 2 D</body></html>"
RAW_HTML_DFS_E = "<html><body>Depth 2 E</body></html>"

# Replace placeholders with actual raw content for the crawler
START_URL_DFS = f"raw://{RAW_HTML_DFS_A.replace('PAGE_B', RAW_HTML_DFS_B).replace('PAGE_C', RAW_HTML_DFS_C).replace('PAGE_D', RAW_HTML_DFS_D).replace('PAGE_E', RAW_HTML_DFS_E)}"

async def dfs_basic_batch_crawl():
    dfs_strategy = DFSDeeepCrawlStrategy(max_depth=2, max_pages=5)
    run_config = CrawlerRunConfig(deep_crawl_strategy=dfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting DFS batch crawl (max_depth=2, max_pages=5)...")
        # arun for DFS is expected to return results in a somewhat depth-first order
        results_list = await crawler.arun(url=START_URL_DFS, config=run_config)
        
        print(f"\n--- DFS Batch Crawl Results (Order may vary based on internal async processing but generally depth-first) ---")
        crawled_urls_with_depth = []
        if results_list:
            for result in results_list:
                if result.success:
                    depth = result.metadata.get('depth', 'N/A')
                    print(f"Crawled: {result.url_for_display()} (Depth: {depth})") # Using url_for_display for raw URLs
                    crawled_urls_with_depth.append((result.url_for_display(), depth))
            print(f"Total pages processed: {len(results_list)}")
            
            # Assertions to check if expected pages were crawled (order can be tricky with async)
            # We expect all 5 mock pages if max_pages=5 and max_depth=2 allows
            page_names = [url_display.split("<body>")[1].split("</body>")[0].strip() for url_display, _ in crawled_urls_with_depth if "raw://" in url_display and "<body>" in url_display]
            assert "Depth 2 D" in page_names or "Depth 2 E" in page_names, "Expected to reach depth 2"

        else:
            print("No results returned from crawl.")
            
# Replace placeholders correctly for the crawler to understand nested raw URLs
# This is tricky because the raw URL itself contains other raw URLs.
# A proper mock server or carefully crafted single raw HTML would be better.
# For now, this is a conceptual example of the expected DFS behavior.
# The current raw URL setup is too complex for simple string replacement.

async def dfs_basic_batch_crawl_simplified():
    # Simpler mock for easier verification.
    # A -> B ; B -> C
    html_c = "<html><body>Page C (depth 2)</body></html>"
    html_b = f"<html><body>Page B (depth 1) <a href='raw://{html_c}'>Link to C</a></body></html>"
    start_url_dfs_simple = f"raw://<html><body>Page A (depth 0) <a href='raw://{html_b}'>Link to B</a></body></html>"

    dfs_strategy = DFSDeeepCrawlStrategy(max_depth=2, max_pages=3)
    run_config = CrawlerRunConfig(deep_crawl_strategy=dfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting DFS batch crawl (max_depth=2, max_pages=3) on simplified mock...")
        results_list = await crawler.arun(url=start_url_dfs_simple, config=run_config)
        
        print(f"\n--- DFS Batch Crawl Results (Simplified Mock) ---")
        crawled_info = []
        if results_list:
            for result in results_list:
                if result.success:
                    depth = result.metadata.get('depth', 'N/A')
                    # Extract a simple identifier from the raw HTML for easier assertion
                    content_id = "Unknown"
                    if "Page A" in result.html: content_id="A"
                    elif "Page B" in result.html: content_id="B"
                    elif "Page C" in result.html: content_id="C"
                    print(f"Crawled: Page {content_id} (Depth: {depth})")
                    crawled_info.append({"id": content_id, "depth": depth, "url": result.url_for_display()})
            print(f"Total pages processed: {len(results_list)}")
            
            # Expected order for DFS: A, B, C (or A, C, B depending on link order in A if it had multiple)
            # With the given structure (A -> B, B -> C), order should be A, B, C
            if len(crawled_info) == 3:
                assert crawled_info[0]["id"] == "A" and crawled_info[0]["depth"] == 0
                assert crawled_info[1]["id"] == "B" and crawled_info[1]["depth"] == 1
                assert crawled_info[2]["id"] == "C" and crawled_info[2]["depth"] == 2
                print("DFS order appears correct for this simplified structure.")
            else:
                print(f"Expected 3 pages, got {len(crawled_info)}. Crawled: {crawled_info}")


asyncio.run(dfs_basic_batch_crawl_simplified())
```

##### 1.4.1.2. Example: Performing a DFS crawl in stream mode (`config.stream=True`), highlighting the order of results.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import DFSDeeepCrawlStrategy

# Simplified mock for DFS streaming order demonstration
# A -> B, D
# B -> C
# D -> E
async def dfs_stream_crawl_order():
    html_e = "<html><body>Page E (depth 2 from D)</body></html>"
    html_d = f"<html><body>Page D (depth 1) <a href='raw://{html_e}'>Link to E</a></body></html>"
    html_c = "<html><body>Page C (depth 2 from B)</body></html>"
    html_b = f"<html><body>Page B (depth 1) <a href='raw://{html_c}'>Link to C</a></body></html>"
    start_url_dfs_stream = f"raw://<html><body>Page A (depth 0) <a href='raw://{html_b}'>Link to B</a> <a href='raw://{html_d}'>Link to D</a></body></html>"


    dfs_strategy = DFSDeeepCrawlStrategy(max_depth=2, max_pages=5)
    # Stream mode
    run_config = CrawlerRunConfig(deep_crawl_strategy=dfs_strategy, stream=True)

    async with AsyncWebCrawler() as crawler:
        print("Starting DFS stream crawl (max_depth=2, max_pages=5)...")
        results_generator = await crawler.arun(url=start_url_dfs_stream, config=run_config)
        
        print(f"\n--- DFS Stream Crawl Results (Order of processing) ---")
        crawled_order_ids = []
        async for result in results_generator:
            if result.success:
                depth = result.metadata.get('depth', 'N/A')
                content_id = "Unknown"
                if "Page A" in result.html: content_id="A"
                elif "Page B" in result.html: content_id="B"
                elif "Page C" in result.html: content_id="C"
                elif "Page D" in result.html: content_id="D"
                elif "Page E" in result.html: content_id="E"
                print(f"Streamed: Page {content_id} (Depth: {depth})")
                crawled_order_ids.append(content_id)
            else:
                print(f"Stream Failed: {result.url_for_display()} - {result.error_message}")
        
        print(f"Crawled order: {crawled_order_ids}")
        # Expected DFS orders (stack behavior, depends on which link is pushed last/first):
        # If D is processed before B from A: A, D, E, B, C
        # If B is processed before D from A: A, B, C, D, E
        # The `reverse=True` on new_links in dfs_strategy.py means the *first* link in HTML is processed *last* by stack.
        # So, if A has links to B then D, D will be put on stack last, thus popped (processed) first.
        expected_order_1 = ['A', 'D', 'E', 'B', 'C'] # If "Link to D" is processed from stack first
        expected_order_2 = ['A', 'B', 'C', 'D', 'E'] # If "Link to B" is processed from stack first

        # Given the current DFS implementation pushes in reversed order of discovery
        # and HTML link order is B then D, D gets added to stack on top of B.
        # So D's branch should be explored first.
        assert crawled_order_ids == expected_order_1 or crawled_order_ids == expected_order_2, \
            f"DFS order incorrect. Expected one of {expected_order_1} or {expected_order_2}, got {crawled_order_ids}"


asyncio.run(dfs_stream_crawl_order())
```

#### 1.4.2. **Controlling Crawl Depth and Scope**

##### 1.4.2.1. Example: Demonstrating `max_depth` limiting the DFS crawl.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import DFSDeeepCrawlStrategy

async def dfs_max_depth_limit():
    html_c = "<html><body>Page C (depth 2)</body></html>"
    html_b = f"<html><body>Page B (depth 1) <a href='raw://{html_c}'>Link to C</a></body></html>"
    start_url_dfs_simple = f"raw://<html><body>Page A (depth 0) <a href='raw://{html_b}'>Link to B</a></body></html>"

    # Set max_depth to 1. Page C (depth 2) should not be crawled.
    dfs_strategy = DFSDeeepCrawlStrategy(max_depth=1, max_pages=5)
    run_config = CrawlerRunConfig(deep_crawl_strategy=dfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting DFS crawl with max_depth=1...")
        results_list = await crawler.arun(url=start_url_dfs_simple, config=run_config)
        
        print(f"\n--- DFS Crawl Results (max_depth=1) ---")
        crawled_pages_at_depth = {}
        if results_list:
            for result in results_list:
                if result.success:
                    depth = result.metadata.get('depth')
                    crawled_pages_at_depth.setdefault(depth, []).append(result.url_for_display())
                    print(f"Crawled: {result.url_for_display()} (Depth: {depth})")
            print(f"Total pages processed: {len(results_list)}")
            
            assert 0 in crawled_pages_at_depth
            assert 1 in crawled_pages_at_depth
            assert 2 not in crawled_pages_at_depth, "Should not crawl beyond max_depth=1"
            assert len(results_list) == 2 # Page A and Page B
        else:
            print("No results returned.")

asyncio.run(dfs_max_depth_limit())
```

##### 1.4.2.2. Example: Demonstrating `max_pages` limiting the number of crawled pages during DFS.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import DFSDeeepCrawlStrategy

async def dfs_max_pages_limit():
    html_c = "<html><body>Page C (depth 2)</body></html>"
    html_b = f"<html><body>Page B (depth 1) <a href='raw://{html_c}'>Link to C</a></body></html>"
    start_url_dfs_simple = f"raw://<html><body>Page A (depth 0) <a href='raw://{html_b}'>Link to B</a></body></html>"

    # max_pages = 2 means only Page A and Page B should be crawled.
    dfs_strategy = DFSDeeepCrawlStrategy(max_depth=2, max_pages=2)
    run_config = CrawlerRunConfig(deep_crawl_strategy=dfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting DFS crawl with max_pages=2...")
        results_list = await crawler.arun(url=start_url_dfs_simple, config=run_config)
        
        print(f"\n--- DFS Crawl Results (max_pages=2) ---")
        crawled_count = 0
        if results_list:
            for result in results_list:
                if result.success:
                    crawled_count +=1
                    print(f"Crawled: {result.url_for_display()} (Depth: {result.metadata.get('depth')})")
            print(f"Total pages processed: {crawled_count}")
            assert crawled_count <= 2, "Should process at most max_pages"
             # Check strategy's internal count for precision
            assert strategy._pages_crawled <= 2
        else:
            print("No results returned.")

asyncio.run(dfs_max_pages_limit())
```

#### 1.4.3. **Traversal Order**

##### 1.4.3.1. Example: A small site crawl demonstrating the LIFO (stack-like) behavior of DFS link processing.
(This is effectively covered by 1.4.1.2. The stream mode example shows the order of processing which is a direct result of LIFO.)
We can re-emphasize it or consider this covered. For completeness, a slight variation:

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import DFSDeeepCrawlStrategy

async def dfs_lifo_demonstration():
    # Structure: A -> [B, D], B -> C, D -> E
    # HTML links in order: B then D
    # DFS stack (simplified, top is right):
    # Initial: [A]
    # Pop A, discover B, D. Push D, then B. Stack: [B, D]
    # Pop D, discover E. Push E. Stack: [B, E]
    # Pop E. Stack: [B]
    # Pop B, discover C. Push C. Stack: [C]
    # Pop C. Stack: []
    # Expected processing order: A, D, E, B, C (because D is pushed last from A's links, so processed first)
    
    html_e = "<html><body>Page E (child of D)</body></html>"
    html_d = f"<html><body>Page D <a href='raw://{html_e}'>To E</a></body></html>"
    html_c = "<html><body>Page C (child of B)</body></html>"
    html_b = f"<html><body>Page B <a href='raw://{html_c}'>To C</a></body></html>"
    # Links in A are ordered B then D
    start_url_dfs_lifo = f"raw://<html><body>Page A <a href='raw://{html_b}'>To B</a> <a href='raw://{html_d}'>To D</a></body></html>"

    dfs_strategy = DFSDeeepCrawlStrategy(max_depth=2, max_pages=5)
    run_config = CrawlerRunConfig(deep_crawl_strategy=dfs_strategy, stream=True) # Stream to see order

    async with AsyncWebCrawler() as crawler:
        print("Demonstrating DFS LIFO behavior (stream mode)...")
        crawled_ids_in_order = []
        async for result in await crawler.arun(url=start_url_dfs_lifo, config=run_config):
            if result.success:
                content_id = "Unknown"
                if "Page A" in result.html: content_id="A"
                elif "Page B" in result.html: content_id="B"
                elif "Page C" in result.html: content_id="C"
                elif "Page D" in result.html: content_id="D"
                elif "Page E" in result.html: content_id="E"
                print(f"Processed: Page {content_id} (Depth: {result.metadata.get('depth')})")
                crawled_ids_in_order.append(content_id)
        
        print(f"\nActual processing order: {crawled_ids_in_order}")
        # Based on current DFS strategy (reversing links before adding to stack):
        # Links from A: B, D. Reversed: D, B. Stack (top right): [B, D]
        # Pop D, links: E. Stack: [B, E]
        # Pop E. Stack: [B]
        # Pop B, links: C. Stack: [C]
        # Pop C. Stack: []
        # Order: A, D, E, B, C
        expected_order = ['A', 'D', 'E', 'B', 'C']
        assert crawled_ids_in_order == expected_order, f"Expected LIFO order {expected_order}, got {crawled_ids_in_order}"

asyncio.run(dfs_lifo_demonstration())
```

### 1.5. `BestFirstCrawlingStrategy`

#### 1.5.1. **Initialization & Basic Usage**

##### 1.5.1.1. Example: Initializing `BestFirstCrawlingStrategy` with `max_depth` and a `url_scorer`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy, KeywordRelevanceScorer

async def best_first_init_and_usage():
    # Score URLs based on keyword "product"
    keyword_scorer = KeywordRelevanceScorer(keywords=["product"])
    
    best_first_strategy = BestFirstCrawlingStrategy(
        max_depth=1, 
        max_pages=3,
        url_scorer=keyword_scorer
    )
    
    run_config = CrawlerRunConfig(deep_crawl_strategy=best_first_strategy)

    # Mock HTML for demonstration
    html_product = "<html><body><a href='/product-page.html'>Cool Product</a> Product details...</body></html>"
    html_blog = "<html><body><a href='/blog-post.html'>Blog Post</a> News and updates...</body></html>"
    html_contact = "<html><body><a href='/contact.html'>Contact Us</a> Get in touch...</body></html>"
    
    start_url_best_first = f"""raw://<html><body>
        <h1>Welcome</h1>
        <a href="raw://{html_product.replace('"', '&quot;')}">View Product</a>
        <a href="raw://{html_blog.replace('"', '&quot;')}">Read Blog</a>
        <a href="raw://{html_contact.replace('"', '&quot;')}">Contact</a>
    </body></html>"""


    async with AsyncWebCrawler() as crawler:
        print("Starting Best-First crawl (scoring for 'product')...")
        results_list = await crawler.arun(url=start_url_best_first, config=run_config)
        
        print(f"\n--- Best-First Crawl Results (Batch) ---")
        if results_list:
            for result in results_list:
                if result.success:
                    print(f"Crawled: {result.url_for_display()} (Score: {result.metadata.get('score', 'N/A')}, Depth: {result.metadata.get('depth')})")
            # Expect product page to be crawled due to higher score
            assert any("product-page.html" in res.url_for_display() for res in results_list if res.success), "Product page should have been crawled."
        else:
            print("No results from crawl.")

asyncio.run(best_first_init_and_usage())
```

##### 1.5.1.2. Example: Performing a Best-First crawl in batch mode.
(Covered by 1.5.1.1, as batch mode is default if `stream=False` is not specified or is False in `CrawlerRunConfig` for the strategy)

##### 1.5.1.3. Example: Performing a Best-First crawl in stream mode.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy, KeywordRelevanceScorer

async def best_first_stream_mode():
    keyword_scorer = KeywordRelevanceScorer(keywords=["feature"])
    
    best_first_strategy = BestFirstCrawlingStrategy(
        max_depth=1, 
        max_pages=3,
        url_scorer=keyword_scorer
    )
    
    run_config = CrawlerRunConfig(deep_crawl_strategy=best_first_strategy, stream=True)

    html_feature = "<html><body><a href='/new-feature.html'>New Feature</a> Details about feature...</body></html>"
    html_about = "<html><body><a href='/about-us.html'>About Us</a> Company info...</body></html>"
    
    start_url_stream = f"""raw://<html><body>
        <a href="raw://{html_feature.replace('"', '&quot;')}">Amazing Feature</a>
        <a href="raw://{html_about.replace('"', '&quot;')}">About Page</a>
    </body></html>"""

    async with AsyncWebCrawler() as crawler:
        print("Starting Best-First stream crawl (scoring for 'feature')...")
        results_generator = await crawler.arun(url=start_url_stream, config=run_config)
        
        print(f"\n--- Best-First Stream Crawl Results ---")
        async for result in results_generator:
            if result.success:
                print(f"Streamed: {result.url_for_display()} (Score: {result.metadata.get('score', 'N/A')}, Depth: {result.metadata.get('depth')})")
            else:
                print(f"Stream Failed: {result.url_for_display()} - {result.error_message}")

asyncio.run(best_first_stream_mode())
```

#### 1.5.2. **Priority-Based Crawling**

##### 1.5.2.1. Example: Demonstrating how `url_scorer` (e.g., `KeywordRelevanceScorer`) influences the crawl order.
(Effectively demonstrated in 1.5.1.1 and 1.5.1.3 where pages containing the keyword are prioritized. We can make a more direct comparison here.)

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy, KeywordRelevanceScorer

async def best_first_order_influence():
    # Scenario 1: Prioritize "tutorials"
    tutorial_scorer = KeywordRelevanceScorer(keywords=["tutorial"])
    strategy_tut = BestFirstCrawlingStrategy(max_depth=1, max_pages=3, url_scorer=tutorial_scorer)
    config_tut = CrawlerRunConfig(deep_crawl_strategy=strategy_tut, stream=True)

    # Scenario 2: Prioritize "pricing"
    pricing_scorer = KeywordRelevanceScorer(keywords=["pricing"])
    strategy_price = BestFirstCrawlingStrategy(max_depth=1, max_pages=3, url_scorer=pricing_scorer)
    config_price = CrawlerRunConfig(deep_crawl_strategy=strategy_price, stream=True)

    html_home = """<html><body>
        <a href="raw_tut.html">Tutorials</a>
        <a href="raw_price.html">Pricing Info</a>
        <a href="raw_blog.html">Blog</a>
    </body></html>"""
    html_tut = "<html><body>Learn with our tutorial.</body></html>"
    html_price = "<html><body>Check our pricing plans.</body></html>"
    html_blog = "<html><body>Latest news from our blog.</body></html>"
    
    # Create self-contained raw URLs
    start_url = f"raw://{html_home.replace('raw_tut.html', f'raw://{html_tut.replace(&quot;,&quot;&amp;quot;&quot;)}').replace('raw_price.html', f'raw://{html_price.replace(&quot;,&quot;&amp;quot;&quot;)}').replace('raw_blog.html', f'raw://{html_blog.replace(&quot;,&quot;&amp;quot;&quot;)}')}"


    async with AsyncWebCrawler() as crawler:
        print("\n--- Crawling with 'tutorial' priority ---")
        order_tut = []
        async for result in await crawler.arun(url=start_url, config=config_tut):
            if result.success:
                order_tut.append(result.url_for_display())
                print(f"  Crawled (tut): {result.url_for_display()} Score: {result.metadata.get('score')}")
        
        print("\n--- Crawling with 'pricing' priority ---")
        order_price = []
        async for result in await crawler.arun(url=start_url, config=config_price): # Re-crawl for new strategy application
            if result.success:
                order_price.append(result.url_for_display())
                print(f"  Crawled (price): {result.url_for_display()} Score: {result.metadata.get('score')}")
        
        # Assertions are tricky due to async nature and BATCH_SIZE. 
        # The goal is that the higher-scored item (if within the first BATCH_SIZE) appears earlier.
        # For a small number of links (3 in this case), it should be quite deterministic.
        # Assuming BATCH_SIZE is >= 3 or more links are processed per batch.

        # Check if "tutorial" related page is prioritized in first run (could be 2nd after start_url)
        if len(order_tut) > 1:
            assert any("tutorial" in url_disp.lower() for url_disp in order_tut[1:2]), \
                f"Tutorial link was not prioritized. Order: {order_tut}"
        
        # Check if "pricing" related page is prioritized in second run
        if len(order_price) > 1:
            assert any("pricing" in url_disp.lower() for url_disp in order_price[1:2]), \
                f"Pricing link was not prioritized. Order: {order_price}"

asyncio.run(best_first_order_influence())
```

##### 1.5.2.2. Example: Showing how `BATCH_SIZE` affects the processing of URLs from the priority queue.

`BATCH_SIZE` in `BestFirstCrawlingStrategy` determines how many URLs are fetched from the priority queue at once to be processed by `crawler.arun_many`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy, KeywordRelevanceScorer
from crawl4ai.deep_crawling.bff_strategy import BATCH_SIZE as BFF_BATCH_SIZE # Import to show its value

# This example is more conceptual as BATCH_SIZE is a module-level constant.
# We can illustrate its effect by showing how many URLs are processed in parallel
# if we could control it or if the number of high-priority URLs is less/more than BATCH_SIZE.

# For demonstration, let's assume we have many high-priority links.
# The strategy will pull BATCH_SIZE of them at a time.
async def best_first_batch_size_effect():
    print(f"Current BATCH_SIZE for BestFirstCrawlingStrategy: {BFF_BATCH_SIZE}")

    # Create more links than BATCH_SIZE to see the batching effect
    num_links = BFF_BATCH_SIZE + 5 
    links_html = ""
    for i in range(num_links):
        # All links will have the keyword to make them high priority
        html_content = f"<html><body>Content with keyword 'important' number {i}</body></html>"
        links_html += f"<a href='raw_link_{i}.html'>Link {i} (important)</a>\n"
        # This creates placeholder names, actual content needs to be embedded for raw://
        # For simplicity in this example, we won't fully embed, but focus on the number of links
        # that *would* be processed.

    start_url_batch_effect = f"raw://<html><body>{links_html}</body></html>"
    
    # Mock the crawler.arun_many to see how many URLs it receives in one call
    class MockCrawler(AsyncWebCrawler):
        async def arun_many(self, urls, config, **kwargs):
            print(f"MockCrawler.arun_many called with {len(urls)} URLs: {urls[:3]}...") # Show first 3
            # Simulate successful crawl for all
            mock_results = []
            for i, url_str in enumerate(urls):
                # Simplified HTML content based on the URL
                html_content = f"<html><body>Mock content for {url_str.split('/')[-1]}</body></html>"
                # Determine depth; for this mock, assume all are depth 1 if not start_url
                depth = 1 if url_str != start_url_batch_effect else 0
                
                mock_results.append(self._create_crawl_result(
                    url=url_str,
                    html=html_content, # Create some HTML for each
                    success=True,
                    status_code=200,
                    metadata={"depth": depth, "score": 1.0}, # Mock score
                    config=config
                ))
            return mock_results

    scorer = KeywordRelevanceScorer(keywords=["important"])
    strategy = BestFirstCrawlingStrategy(max_depth=1, max_pages=num_links + 1, url_scorer=scorer)
    # Note: max_pages is set high to not interfere with BATCH_SIZE demonstration for link discovery
    
    run_config = CrawlerRunConfig(deep_crawl_strategy=strategy)

    async with MockCrawler() as crawler:
        print(f"Starting Best-First crawl with {num_links} high-priority links...")
        # This will call arun_many multiple times if num_links > BATCH_SIZE
        results_list = await crawler.arun(url=start_url_batch_effect, config=run_config)
        
        print(f"\n--- Best-First Crawl (BATCH_SIZE effect) ---")
        if results_list:
            print(f"Total pages processed: {len(results_list)-1}") # -1 for the start URL itself
            # Further assertions could be made if arun_many was more intricately mocked to track calls.
        else:
            print("No results returned.")
    print("Observe the 'MockCrawler.arun_many called with...' print statements.")
    print("If num_links > BATCH_SIZE, you should see multiple calls to arun_many, "
          f"each with up to {BFF_BATCH_SIZE} URLs.")

asyncio.run(best_first_batch_size_effect())
```

#### 1.5.3. **Controlling Crawl Scope**

##### 1.5.3.1. Example: Best-First crawl with `max_depth` reached.
(Similar to BFS/DFS max_depth, BestFirst also respects it.)

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy, PathDepthScorer

async def best_first_max_depth():
    html_c = "<html><body>Page C (depth 2)</body></html>"
    html_b = f"<html><body>Page B (depth 1) <a href='raw://{html_c}'>Link to C</a></body></html>"
    start_url_simple = f"raw://<html><body>Page A (depth 0) <a href='raw://{html_b}'>Link to B</a></body></html>"

    # Score by path depth, optimal is 0 to ensure links are explored if possible
    scorer = PathDepthScorer(optimal_depth=0) 
    
    # max_depth=1 should stop before Page C
    strategy = BestFirstCrawlingStrategy(max_depth=1, max_pages=5, url_scorer=scorer)
    run_config = CrawlerRunConfig(deep_crawl_strategy=strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting Best-First crawl with max_depth=1...")
        results_list = await crawler.arun(url=start_url_simple, config=run_config)
        
        print(f"\n--- Best-First Crawl Results (max_depth=1) ---")
        crawled_depths = set()
        if results_list:
            for result in results_list:
                if result.success:
                    depth = result.metadata.get('depth')
                    crawled_depths.add(depth)
                    print(f"Crawled: {result.url_for_display()} (Depth: {depth})")
            print(f"Depths crawled: {crawled_depths}")
            assert 2 not in crawled_depths, "Should not have crawled to depth 2"
            assert len(results_list) == 2 # Page A and Page B
        else:
            print("No results.")

asyncio.run(best_first_max_depth())
```

##### 1.5.3.2. Example: Best-First crawl with `max_pages` reached.
(Similar to BFS/DFS max_pages, BestFirst also respects it.)

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy, PathDepthScorer

async def best_first_max_pages():
    html_c = "<html><body>Page C (depth 2)</body></html>"
    html_b = f"<html><body>Page B (depth 1) <a href='raw://{html_c}'>Link to C</a></body></html>"
    start_url_simple = f"raw://<html><body>Page A (depth 0) <a href='raw://{html_b}'>Link to B</a></body></html>"
    
    scorer = PathDepthScorer(optimal_depth=0) # Score to explore if possible
    
    # max_pages=2 should process only Page A and Page B
    strategy = BestFirstCrawlingStrategy(max_depth=2, max_pages=2, url_scorer=scorer)
    run_config = CrawlerRunConfig(deep_crawl_strategy=strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting Best-First crawl with max_pages=2...")
        results_list = await crawler.arun(url=start_url_simple, config=run_config)
        
        crawled_count = 0
        if results_list:
            print(f"\n--- Best-First Crawl Results (max_pages=2) ---")
            for result in results_list:
                if result.success:
                    crawled_count += 1
                    print(f"Crawled: {result.url_for_display()} (Depth: {result.metadata.get('depth')})")
            print(f"Total pages processed: {crawled_count}")
            assert crawled_count <= 2
            # Check strategy's internal count for precision
            assert strategy._pages_crawled <= 2
        else:
            print("No results.")
            
asyncio.run(best_first_max_pages())
```

#### 1.5.4. **Link Discovery and Scoring**

##### 1.5.4.1. Example: `link_discovery` adding new links to the priority queue based on their scores.
(This is implicitly shown in examples 1.5.1.1 and 1.5.2.1, where higher-scored links are processed. The priority queue mechanism itself is internal to `BestFirstCrawlingStrategy`.)
This conceptual example will show how `link_discovery` calculates scores and would (internally) add items with scores to the priority queue.

```python
import asyncio
from crawl4ai.models import CrawlResult, Links, Link
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy, KeywordRelevanceScorer
from crawl4ai.utils import normalize_url_for_deep_crawl

mock_crawl_result_for_scoring = CrawlResult(
    url="http://example.com/home",
    html="""
        <a href="/product-feature.html">Feature Page</a>
        <a href="/about-us.html">About Page</a>
        <a href="/another-feature.html">Another Feature</a>
    """,
    success=True,
    links=Links(
        internal=[
            Link(href="/product-feature.html"), Link(href="/about-us.html"), Link(href="/another-feature.html")
        ]
    )
)

async def demo_best_first_link_discovery_scoring():
    scorer = KeywordRelevanceScorer(keywords=["feature"]) # Prioritize "feature"
    strategy = BestFirstCrawlingStrategy(max_depth=1, url_scorer=scorer)
    
    # Simulate internal state for link_discovery
    source_url = mock_crawl_result_for_scoring.url
    current_depth = 0 # Depth of the source_url
    visited = {source_url}
    # PriorityQueue would store (negative_score, depth, url, parent_url)
    # We'll simulate the items that would be put into it.
    priority_queue_items_to_add = [] 
    depths = {source_url: 0}

    # Manual simulation of link_discovery's core logic
    next_depth = current_depth + 1
    if next_depth <= strategy.max_depth:
        for link_obj in mock_crawl_result_for_scoring.links.internal:
            abs_url = normalize_url_for_deep_crawl(link_obj.href, source_url)
            if abs_url and abs_url not in visited:
                if await strategy.can_process_url(abs_url, next_depth): # Standard checks
                    score = await strategy.url_scorer.score(abs_url) # Score the URL
                    # Store with negative score because asyncio.PriorityQueue is a min-heap
                    priority_queue_items_to_add.append((-score, next_depth, abs_url, source_url))
                    visited.add(abs_url) # Mark as "to be processed"
                    depths[abs_url] = next_depth
    
    # Sort by score (descending, as priority queue would handle)
    priority_queue_items_to_add.sort(key=lambda x: x[0], reverse=True) # Actually sorts by -score asc -> score desc

    print(f"Source URL: {source_url}")
    print(f"Items that would be added to priority queue (score, depth, url, parent):")
    for neg_score, depth_val, url_val, parent_val in priority_queue_items_to_add:
        print(f"  - Score: {-neg_score:.2f}, Depth: {depth_val}, URL: {url_val}")

    assert len(priority_queue_items_to_add) == 3
    # Check if "feature" links have higher scores (lower negative_score, appear earlier after sort)
    assert "product-feature.html" in priority_queue_items_to_add[0][2] or "another-feature.html" in priority_queue_items_to_add[0][2]
    assert "product-feature.html" in priority_queue_items_to_add[1][2] or "another-feature.html" in priority_queue_items_to_add[1][2]
    assert "about-us.html" in priority_queue_items_to_add[2][2] # Should have lower score

asyncio.run(demo_best_first_link_discovery_scoring())
```

---
## 2. URL Filters

This section demonstrates how to use various filters to control which URLs are processed during a deep crawl.

### 2.1. `FilterStats`

#### 2.1.1. Example: Accessing `total_urls`, `passed_urls`, and `rejected_urls` from a `FilterStats` object after applying a filter.

```python
import asyncio
from crawl4ai.deep_crawling import URLPatternFilter, FilterStats

async def demo_filter_stats():
    # Create a filter (e.g., allow only .html files)
    html_filter = URLPatternFilter(patterns=["*.html"])

    urls_to_test = [
        "http://example.com/index.html",
        "http://example.com/script.js",
        "http://example.com/about.html",
        "http://example.com/image.png",
    ]

    print("Applying URLPatternFilter (allow *.html):")
    for url in urls_to_test:
        # The apply method updates stats internally
        passed = await html_filter.apply(url) 
        print(f"  URL: {url}, Passed: {passed}")

    # Access the stats from the filter instance
    stats = html_filter.stats
    print(f"\n--- Filter Stats ---")
    print(f"Total URLs processed: {stats.total_urls}")
    print(f"Passed URLs: {stats.passed_urls}")
    print(f"Rejected URLs: {stats.rejected_urls}")

    assert stats.total_urls == 4
    assert stats.passed_urls == 2
    assert stats.rejected_urls == 2

asyncio.run(demo_filter_stats())
```

### 2.2. `FilterChain`

#### 2.2.1. Example: Creating a `FilterChain` with `DomainFilter` and `URLPatternFilter`.

```python
import asyncio
from crawl4ai.deep_crawling import FilterChain, DomainFilter, URLPatternFilter

async def create_filter_chain():
    # Filter 1: Allow only 'example.com'
    domain_filter = DomainFilter(allowed_domains=["example.com"])
    
    # Filter 2: Allow only URLs ending with '.html' or '.htm'
    pattern_filter = URLPatternFilter(patterns=["*.html", "*.htm"])
    
    # Create a chain: URL must pass BOTH filters
    filter_chain = FilterChain(filters=[domain_filter, pattern_filter])
    
    print(f"FilterChain created with {len(filter_chain.filters)} filters.")

    url1 = "http://example.com/page.html" # Should pass
    url2 = "http://example.com/script.js" # Should fail pattern_filter
    url3 = "http://otherexample.com/page.html" # Should fail domain_filter
    url4 = "http://otherexample.com/image.png" # Should fail both

    print(f"\nTesting URL: {url1} -> Passed: {await filter_chain.apply(url1)}")
    print(f"Testing URL: {url2} -> Passed: {await filter_chain.apply(url2)}")
    print(f"Testing URL: {url3} -> Passed: {await filter_chain.apply(url3)}")
    print(f"Testing URL: {url4} -> Passed: {await filter_chain.apply(url4)}")

    assert await filter_chain.apply(url1) == True
    assert await filter_chain.apply(url2) == False
    assert await filter_chain.apply(url3) == False
    assert await filter_chain.apply(url4) == False
    
    print("\nDomainFilter stats:", domain_filter.stats.passed_urls, "passed,", domain_filter.stats.rejected_urls, "rejected.")
    print("PatternFilter stats:", pattern_filter.stats.passed_urls, "passed,", pattern_filter.stats.rejected_urls, "rejected.")
    print("FilterChain aggregated stats:", filter_chain.stats.passed_urls, "passed,", filter_chain.stats.rejected_urls, "rejected.")


asyncio.run(create_filter_chain())
```

#### 2.2.2. Example: Applying a `FilterChain` within a `BFSDeeepCrawlStrategy` and observing filtered results.
(This was effectively covered in 1.3.3.1. That example shows a `FilterChain` used with `BFSDeeepCrawlStrategy`.)

#### 2.2.3. Example: Checking aggregated `FilterStats` from a `FilterChain`.
(This was effectively covered in 2.2.1, where `filter_chain.stats` are printed.)

### 2.3. `URLPatternFilter`

#### 2.3.1. Example: Using `URLPatternFilter` to allow only URLs matching a specific regex pattern.

```python
import asyncio
from crawl4ai.deep_crawling import URLPatternFilter

async def url_pattern_regex():
    # Allow URLs that look like product pages, e.g., /products/item123
    regex_pattern = r"/products/item\d+"
    product_filter = URLPatternFilter(patterns=[regex_pattern]) # use_glob=False is default for regex

    url_product = "http://example.com/products/item123"
    url_blog = "http://example.com/blog/my-post"

    print(f"Testing with regex pattern: {regex_pattern}")
    print(f"URL: {url_product}, Passed: {await product_filter.apply(url_product)}")
    print(f"URL: {url_blog}, Passed: {await product_filter.apply(url_blog)}")

    assert await product_filter.apply(url_product) == True
    assert await product_filter.apply(url_blog) == False

asyncio.run(url_pattern_regex())
```

#### 2.3.2. Example: Using `URLPatternFilter` with `reverse=True` to disallow URLs matching a pattern.

```python
import asyncio
from crawl4ai.deep_crawling import URLPatternFilter

async def url_pattern_reverse():
    # Disallow URLs containing 'admin' or 'login'
    disallow_patterns = [r".*admin.*", r".*login.*"]
    admin_block_filter = URLPatternFilter(patterns=disallow_patterns, reverse=True)

    url_safe = "http://example.com/dashboard"
    url_admin = "http://example.com/admin/panel"
    url_login = "http://example.com/user/login/page"

    print(f"Testing with reverse patterns: {disallow_patterns}")
    print(f"URL: {url_safe}, Passed: {await admin_block_filter.apply(url_safe)}")
    print(f"URL: {url_admin}, Passed: {await admin_block_filter.apply(url_admin)}")
    print(f"URL: {url_login}, Passed: {await admin_block_filter.apply(url_login)}")

    assert await admin_block_filter.apply(url_safe) == True
    assert await admin_block_filter.apply(url_admin) == False
    assert await admin_block_filter.apply(url_login) == False

asyncio.run(url_pattern_reverse())
```

#### 2.3.3. Example: `URLPatternFilter` with `use_glob=True` for wildcard matching.

```python
import asyncio
from crawl4ai.deep_crawling import URLPatternFilter

async def url_pattern_glob():
    # Allow only .jpg or .png images in an /assets/ directory using glob
    # use_glob=True is effectively default when patterns don't look like regex
    # but we can be explicit. The categorization logic determines this.
    # Forcing glob by not using regex-like characters.
    # This filter's internal logic auto-detects glob for simple patterns like "*.jpg"
    # If you want to force fnmatch style globbing over regex for ambiguous patterns,
    # there isn't a direct `use_glob` parameter on URLPatternFilter itself.
    # The categorization of pattern types (SUFFIX, PREFIX, DOMAIN, PATH, REGEX)
    # handles this. Let's demonstrate a simple suffix pattern.
    
    # Example: Allow only *.jpg or *.png
    image_filter_suffix = URLPatternFilter(patterns=["*.jpg", "*.png"]) # This will be categorized as SUFFIX

    url_jpg = "http://example.com/image.jpg"
    url_png = "http://example.com/photo.png"
    url_gif = "http://example.com/animation.gif"

    print("Testing with SUFFIX patterns: ['*.jpg', '*.png']")
    print(f"URL: {url_jpg}, Passed: {await image_filter_suffix.apply(url_jpg)}")
    print(f"URL: {url_png}, Passed: {await image_filter_suffix.apply(url_png)}")
    print(f"URL: {url_gif}, Passed: {await image_filter_suffix.apply(url_gif)}")

    assert await image_filter_suffix.apply(url_jpg) == True
    assert await image_filter_suffix.apply(url_png) == True
    assert await image_filter_suffix.apply(url_gif) == False

asyncio.run(url_pattern_glob())
```
*Self-correction: The `use_glob` parameter was mentioned in the prompt for `URLPatternFilter`, but it's not a direct constructor parameter. The filter categorizes patterns and applies fnmatch-like logic for SUFFIX, PREFIX, etc. The above example demonstrates this behavior for SUFFIX.*

#### 2.3.4. Example: `URLPatternFilter` demonstrating "SUFFIX" pattern type (e.g., `*.html`).
(Covered by 2.3.3 with `*.jpg`, `*.png`. A specific `*.html` example is similar)

```python
import asyncio
from crawl4ai.deep_crawling import URLPatternFilter

async def url_pattern_suffix_html():
    html_filter = URLPatternFilter(patterns=["*.html"]) # Categorized as SUFFIX

    url_html = "http://example.com/index.html"
    url_php = "http://example.com/index.php"
    
    print("Testing SUFFIX pattern: '*.html'")
    print(f"URL: {url_html}, Passed: {await html_filter.apply(url_html)}")
    print(f"URL: {url_php}, Passed: {await html_filter.apply(url_php)}")

    assert await html_filter.apply(url_html) == True
    assert await html_filter.apply(url_php) == False

asyncio.run(url_pattern_suffix_html())
```

#### 2.3.5. Example: `URLPatternFilter` demonstrating "PREFIX" pattern type (e.g., `/blog/*`).

```python
import asyncio
from crawl4ai.deep_crawling import URLPatternFilter

async def url_pattern_prefix_blog():
    # Note: For `URLPatternFilter`, a pattern like "/blog/*" would be treated as a REGEX
    # or a general PATH if it doesn't have special regex characters.
    # The internal categorization distinguishes between simple wildcards and full regex.
    # Let's use a pattern that is clearly a prefix and would be handled by fnmatch-like logic.
    # The `_categorize_pattern` method would likely treat "/blog/*" as PATH or REGEX.
    # To demonstrate a pure prefix, we'd use a simpler pattern without the trailing `*` if it's not a glob pattern.
    # If "/blog/*" is intended as a glob, it's treated as such for PATH.
    
    # Let's use a pattern that clearly falls into PREFIX category: "http://example.com/blog/"
    # And another that would be a PATH type: "/blog/*"
    
    # This will be categorized as PATH due to the wildcard if not complex enough for REGEX
    blog_path_filter = URLPatternFilter(patterns=["*/blog/*"]) 

    url_blog_post = "http://example.com/blog/my-first-post"
    url_blog_main = "http://example.com/blog/"
    url_products = "http://example.com/products/item"

    print("Testing PATH pattern: '*/blog/*'") # Will match URLs containing /blog/
    print(f"URL: {url_blog_post}, Passed: {await blog_path_filter.apply(url_blog_post)}")
    print(f"URL: {url_blog_main}, Passed: {await blog_path_filter.apply(url_blog_main)}")
    print(f"URL: {url_products}, Passed: {await blog_path_filter.apply(url_products)}")

    assert await blog_path_filter.apply(url_blog_post) == True
    assert await blog_path_filter.apply(url_blog_main) == True
    assert await blog_path_filter.apply(url_products) == False
    
    # To strictly test _simple_prefixes (checked before general path patterns):
    # This uses exact string startswith logic.
    simple_prefix_filter = URLPatternFilter(patterns=["http://example.com/blog"]) 
    # This will not match /blog/ as a prefix, but as a PATH pattern if it makes it there.
    # The internal categorization logic is: SUFFIX -> DOMAIN -> PREFIX -> PATH/REGEX
    # So, "http://example.com/blog" would be a simple prefix.

    print("\nTesting simple prefix pattern: 'http://example.com/blog'")
    print(f"URL: {url_blog_post}, Passed: {await simple_prefix_filter.apply(url_blog_post)}") # True
    print(f"URL: http://example.com/blog, Passed: {await simple_prefix_filter.apply('http://example.com/blog')}") # True
    print(f"URL: {url_products}, Passed: {await simple_prefix_filter.apply(url_products)}") # False
    
    assert await simple_prefix_filter.apply(url_blog_post) == True


asyncio.run(url_pattern_prefix_blog())
```

#### 2.3.6. Example: `URLPatternFilter` demonstrating "DOMAIN" pattern type (e.g., `*.example.com`).

```python
import asyncio
from crawl4ai.deep_crawling import URLPatternFilter

async def url_pattern_domain():
    # This pattern type matches the domain part of the URL.
    # "*.example.com" would allow "www.example.com", "blog.example.com", but not "example.com" itself
    # or "badexample.com".
    # The internal logic converts "*.example.com" into a regex like r"[^/]+\.example\.com" for domain matching.
    
    domain_filter = URLPatternFilter(patterns=["*.example.com"]) 

    url_subdomain = "http://blog.example.com/article"
    url_maindomain = "http://example.com/main" # This should NOT pass if pattern is strictly *.example.com
    url_other_sub = "http://www.example.com/page"
    url_external = "http://another.domain.com"
    
    # If we want to include example.com itself, we'd need another pattern "example.com" or a regex.
    # Let's test with "example.com" to show it's treated as a domain pattern
    main_domain_filter = URLPatternFilter(patterns=["example.com"])


    print("Testing DOMAIN pattern: '*.example.com'")
    print(f"URL: {url_subdomain}, Passed: {await domain_filter.apply(url_subdomain)}")
    print(f"URL: {url_maindomain}, Passed: {await domain_filter.apply(url_maindomain)}") # Expected False
    print(f"URL: {url_other_sub}, Passed: {await domain_filter.apply(url_other_sub)}")
    print(f"URL: {url_external}, Passed: {await domain_filter.apply(url_external)}")
    
    assert await domain_filter.apply(url_subdomain) == True
    assert await domain_filter.apply(url_maindomain) == False # `*.example.com` does not match `example.com`
    assert await domain_filter.apply(url_other_sub) == True
    assert await domain_filter.apply(url_external) == False

    print("\nTesting DOMAIN pattern: 'example.com'")
    print(f"URL: {url_subdomain}, Passed: {await main_domain_filter.apply(url_subdomain)}") # True (subdomain of example.com)
    print(f"URL: {url_maindomain}, Passed: {await main_domain_filter.apply(url_maindomain)}") # True
    
    assert await main_domain_filter.apply(url_subdomain) == True
    assert await main_domain_filter.apply(url_maindomain) == True


asyncio.run(url_pattern_domain())
```

#### 2.3.7. Example: `URLPatternFilter` demonstrating "PATH" pattern type (e.g., `/products/electronics/*`).
(Covered by 2.3.5 with `*/blog/*`. The categorization logic handles these general path/glob-like patterns after specific prefix/suffix/domain.)

### 2.4. `ContentTypeFilter`

*Note: `ContentTypeFilter` examples ideally require a live server or a mock HTTP server to return actual `Content-Type` headers. For self-contained examples, we'll primarily rely on the extension-based fallback.*

#### 2.4.1. Example: Using `ContentTypeFilter` to allow only "text/html" URLs.

```python
import asyncio
from crawl4ai.deep_crawling import ContentTypeFilter

async def content_type_html_only():
    # This filter will primarily use URL extensions if check_extension=True (default)
    # as we are not making live HTTP requests in this isolated example.
    html_only_filter = ContentTypeFilter(allowed_types=["text/html"])

    url_html = "http://example.com/index.html"
    url_pdf = "http://example.com/document.pdf"
    url_no_ext = "http://example.com/api/data" # No extension, would rely on Content-Type header in live scenario

    print("Testing ContentTypeFilter (allow 'text/html', relies on extension here):")
    print(f"URL: {url_html}, Passed: {await html_only_filter.apply(url_html)}")
    print(f"URL: {url_pdf}, Passed: {await html_only_filter.apply(url_pdf)}")
    print(f"URL: {url_no_ext}, Passed: {await html_only_filter.apply(url_no_ext)}")
    print("Note: For URLs without extensions, this filter would need live HTTP HEAD requests to check Content-Type header.")

    assert await html_only_filter.apply(url_html) == True
    assert await html_only_filter.apply(url_pdf) == False
    # Without live request, url_no_ext might pass if default behavior is permissive or fail if strict.
    # The current implementation's apply method is synchronous and relies on _check_url_cached.
    # _check_url_cached primarily uses extension. If check_extension=False, it would always return True
    # unless a live check was made (which is not part of the filter's apply method directly).
    # For this test, it defaults to True if no extension and check_extension=True
    assert await html_only_filter.apply(url_no_ext) == True 


asyncio.run(content_type_html_only())
```

#### 2.4.2. Example: `ContentTypeFilter` allowing a list of types, e.g., ["text/html", "application/pdf"].

```python
import asyncio
from crawl4ai.deep_crawling import ContentTypeFilter

async def content_type_html_and_pdf():
    multi_type_filter = ContentTypeFilter(allowed_types=["text/html", "application/pdf"])

    url_html = "http://example.com/index.html"
    url_pdf = "http://example.com/report.pdf"
    url_jpg = "http://example.com/image.jpg"

    print("Testing ContentTypeFilter (allow 'text/html', 'application/pdf'):")
    print(f"URL: {url_html}, Passed: {await multi_type_filter.apply(url_html)}")
    print(f"URL: {url_pdf}, Passed: {await multi_type_filter.apply(url_pdf)}")
    print(f"URL: {url_jpg}, Passed: {await multi_type_filter.apply(url_jpg)}")
    
    assert await multi_type_filter.apply(url_html) == True
    assert await multi_type_filter.apply(url_pdf) == True
    assert await multi_type_filter.apply(url_jpg) == False

asyncio.run(content_type_html_and_pdf())
```

#### 2.4.3. Example: `ContentTypeFilter` with `check_extension=True` (default) vs. `check_extension=False` using URL extensions.

```python
import asyncio
from crawl4ai.deep_crawling import ContentTypeFilter

async def content_type_check_extension_toggle():
    url_html_like_no_ext = "http://example.com/about-us" # Could be HTML
    url_pdf_like_no_ext = "http://example.com/download/report" # Could be PDF

    # Default: check_extension=True
    filter_check_ext = ContentTypeFilter(allowed_types=["text/html"])
    # If no extension, it defaults to True (allows processing, hoping Content-Type header confirms)
    print(f"With check_extension=True (default):")
    print(f"  URL: {url_html_like_no_ext}, Passed: {await filter_check_ext.apply(url_html_like_no_ext)}")
    assert await filter_check_ext.apply(url_html_like_no_ext) == True

    # check_extension=False: Ignores extensions, always passes unless live HEAD request fails (not tested here)
    filter_no_check_ext = ContentTypeFilter(allowed_types=["text/html"], check_extension=False)
    # This will always return True from apply() because it skips extension check
    print(f"With check_extension=False:")
    print(f"  URL: {url_html_like_no_ext}, Passed: {await filter_no_check_ext.apply(url_html_like_no_ext)}")
    print(f"  URL: http://example.com/image.jpg, Passed: {await filter_no_check_ext.apply('http://example.com/image.jpg')}")
    
    assert await filter_no_check_ext.apply(url_html_like_no_ext) == True
    assert await filter_no_check_ext.apply("http://example.com/image.jpg") == True 
    # (Passes because it doesn't check extension; live HEAD would be needed to actually filter)

asyncio.run(content_type_check_extension_toggle())
```

### 2.5. `DomainFilter`

#### 2.5.1. Example: `DomainFilter` allowing only URLs from "example.com" and its subdomains.

```python
import asyncio
from crawl4ai.deep_crawling import DomainFilter

async def domain_filter_allow_specific():
    # Allows example.com and any subdomains like www.example.com, blog.example.com
    domain_filter = DomainFilter(allowed_domains=["example.com"])

    url_main = "http://example.com/page"
    url_sub = "http://blog.example.com/article"
    url_external = "http://anotherdomain.com"

    print("Testing DomainFilter (allow 'example.com' and subdomains):")
    print(f"URL: {url_main}, Passed: {await domain_filter.apply(url_main)}")
    print(f"URL: {url_sub}, Passed: {await domain_filter.apply(url_sub)}")
    print(f"URL: {url_external}, Passed: {await domain_filter.apply(url_external)}")

    assert await domain_filter.apply(url_main) == True
    assert await domain_filter.apply(url_sub) == True
    assert await domain_filter.apply(url_external) == False

asyncio.run(domain_filter_allow_specific())
```

#### 2.5.2. Example: `DomainFilter` blocking URLs from "ads.example.com".

```python
import asyncio
from crawl4ai.deep_crawling import DomainFilter

async def domain_filter_block_specific():
    # Blocks ads.example.com and its subdomains (e.g., tracker.ads.example.com)
    # but allows other example.com URLs if no allowed_domains is set (or if it includes example.com)
    domain_filter = DomainFilter(blocked_domains=["ads.example.com"])
    # By default, if allowed_domains is None, all non-blocked domains are permitted.

    url_allowed_sub = "http://blog.example.com/article"
    url_blocked_sub = "http://ads.example.com/banner"
    url_deep_blocked = "http://tracker.ads.example.com/pixel" # Also blocked as subdomain of ads.example.com
    url_main = "http://example.com/main"

    print("Testing DomainFilter (block 'ads.example.com'):")
    print(f"URL: {url_allowed_sub}, Passed: {await domain_filter.apply(url_allowed_sub)}")
    print(f"URL: {url_blocked_sub}, Passed: {await domain_filter.apply(url_blocked_sub)}")
    print(f"URL: {url_deep_blocked}, Passed: {await domain_filter.apply(url_deep_blocked)}")
    print(f"URL: {url_main}, Passed: {await domain_filter.apply(url_main)}")

    assert await domain_filter.apply(url_allowed_sub) == True
    assert await domain_filter.apply(url_blocked_sub) == False
    assert await domain_filter.apply(url_deep_blocked) == False
    assert await domain_filter.apply(url_main) == True

asyncio.run(domain_filter_block_specific())
```

#### 2.5.3. Example: Combining `allowed_domains` and `blocked_domains`.

```python
import asyncio
from crawl4ai.deep_crawling import DomainFilter

async def domain_filter_combined():
    # Allow example.com but specifically block sub.example.com
    domain_filter = DomainFilter(
        allowed_domains=["example.com"],
        blocked_domains=["sub.example.com"]
    )

    url_main_allowed = "http://www.example.com/page" # Subdomain of example.com, allowed
    url_blocked_sub = "http://sub.example.com/secret" # Specifically blocked
    url_other_sub_allowed = "http://blog.example.com/article" # Allowed as subdomain of example.com
    url_external = "http://another.com" # Not in allowed_domains

    print("Testing DomainFilter (allow 'example.com', block 'sub.example.com'):")
    print(f"URL: {url_main_allowed}, Passed: {await domain_filter.apply(url_main_allowed)}")
    print(f"URL: {url_blocked_sub}, Passed: {await domain_filter.apply(url_blocked_sub)}")
    print(f"URL: {url_other_sub_allowed}, Passed: {await domain_filter.apply(url_other_sub_allowed)}")
    print(f"URL: {url_external}, Passed: {await domain_filter.apply(url_external)}")

    assert await domain_filter.apply(url_main_allowed) == True
    assert await domain_filter.apply(url_blocked_sub) == False
    assert await domain_filter.apply(url_other_sub_allowed) == True
    assert await domain_filter.apply(url_external) == False

asyncio.run(domain_filter_combined())
```

### 2.6. `ContentRelevanceFilter`
*Note: Requires live HTTP requests to fetch `<head>` content. For isolated tests, mocking or a stable example site is needed. We'll use a simplified direct call for demonstration.*

#### 2.6.1. Example: Using `ContentRelevanceFilter` with a query and threshold to filter pages based on head content relevance.

```python
import asyncio
from crawl4ai.deep_crawling import ContentRelevanceFilter
# Mock HeadPeek for testing without live requests
from unittest.mock import patch

# This example will mock HeadPeek.peek_html to simulate responses
async def demo_content_relevance_filter():
    query = "Python programming tutorial"
    # Threshold: Score must be >= 0.1 to pass
    relevance_filter = ContentRelevanceFilter(query=query, threshold=0.1) 

    # Mock HTML heads
    html_head_relevant = """
    <head>
        <title>Advanced Python Programming Tutorial</title>
        <meta name="description" content="Learn Python programming concepts and best practices.">
        <meta name="keywords" content="Python, programming, tutorial, advanced">
    </head>
    """
    html_head_irrelevant = """
    <head>
        <title>Best Coffee Recipes</title>
        <meta name="description" content="Discover amazing coffee recipes.">
        <meta name="keywords" content="coffee, recipes, morning, brew">
    </head>
    """

    url_relevant = "http://example.com/python-tutorial"
    url_irrelevant = "http://example.com/coffee-recipes"

    print(f"Testing ContentRelevanceFilter with query: '{query}' and threshold: 0.1")

    # Patch HeadPeek.peek_html to return our mock heads
    with patch('crawl4ai.deep_crawling.filters.HeadPeek.peek_html') as mock_peek:
        # First call to apply (for url_relevant)
        mock_peek.return_value = html_head_relevant
        passed_relevant = await relevance_filter.apply(url_relevant)
        print(f"  URL: {url_relevant}, Passed: {passed_relevant}, Score: {relevance_filter._last_score:.2f}") # _last_score is for demo
        assert passed_relevant

        # Second call to apply (for url_irrelevant)
        mock_peek.return_value = html_head_irrelevant
        passed_irrelevant = await relevance_filter.apply(url_irrelevant)
        print(f"  URL: {url_irrelevant}, Passed: {passed_irrelevant}, Score: {relevance_filter._last_score:.2f}")
        assert not passed_irrelevant

asyncio.run(demo_content_relevance_filter())
```

#### 2.6.2. Example: Demonstrating different `k1` and `b` BM25 parameters.

```python
import asyncio
from crawl4ai.deep_crawling import ContentRelevanceFilter
from unittest.mock import patch

async def demo_bm25_params_relevance_filter():
    query = "web scraping tools"
    
    html_head_content = """
    <head>
        <title>Top Web Scraping Tools and Libraries</title>
        <meta name="description" content="A comprehensive list of web scraping tools.">
    </head>
    """
    url_test = "http://example.com/scraping-tools"

    # Filter 1: Default k1 and b
    filter_default_params = ContentRelevanceFilter(query=query, threshold=0.01)
    
    # Filter 2: Higher k1 (more sensitive to term frequency)
    filter_high_k1 = ContentRelevanceFilter(query=query, threshold=0.01, k1=2.0)

    # Filter 3: Lower b (less penalty for document length)
    filter_low_b = ContentRelevanceFilter(query=query, threshold=0.01, b=0.5)

    with patch('crawl4ai.deep_crawling.filters.HeadPeek.peek_html', return_value=html_head_content):
        await filter_default_params.apply(url_test)
        score_default = filter_default_params._last_score # Internal for demo
        print(f"Score with default BM25 params (k1={filter_default_params.k1}, b={filter_default_params.b}): {score_default:.4f}")

        await filter_high_k1.apply(url_test)
        score_high_k1 = filter_high_k1._last_score
        print(f"Score with high k1 (k1={filter_high_k1.k1}, b={filter_high_k1.b}): {score_high_k1:.4f}")
        
        await filter_low_b.apply(url_test)
        score_low_b = filter_low_b._last_score
        print(f"Score with low b (k1={filter_low_b.k1}, b={filter_low_b.b}): {score_low_b:.4f}")

    # Exact score assertions can be brittle, but we expect scores to change.
    # For this specific content and query, higher k1 might slightly increase score if query terms are frequent.
    # Lower b might increase score if avgdl is small relative to this doc's length.
    assert score_default != score_high_k1 or score_default != score_low_b, "BM25 scores should differ with parameter changes."

asyncio.run(demo_bm25_params_relevance_filter())
```

### 2.7. `SEOFilter`

#### 2.7.1. Example: Using `SEOFilter` with a threshold to filter pages based on SEO quality score.

```python
import asyncio
from crawl4ai.deep_crawling import SEOFilter
from unittest.mock import patch

async def demo_seo_filter_threshold():
    # Example: Require a minimum SEO score of 0.7
    seo_filter = SEOFilter(threshold=0.7)

    html_head_good_seo = """
    <head>
        <title>Optimize Your SEO: A Comprehensive Guide (55 chars)</title>
        <meta name="description" content="Learn SEO best practices to improve your website ranking. This guide covers keywords, on-page optimization, and link building. (150 chars)">
        <link rel="canonical" href="http://example.com/seo-guide" />
        <meta name="robots" content="index, follow">
        <script type="application/ld+json">{"@context": "https://schema.org"}</script>
    </head>
    """
    url_good_seo = "http://example.com/seo-guide"

    html_head_poor_seo = "<head><title>Seo</title></head>" # Short title, no meta, etc.
    url_poor_seo = "http://example.com/bad-seo"
    
    print(f"Testing SEOFilter with threshold 0.7:")
    with patch('crawl4ai.deep_crawling.filters.HeadPeek.peek_html') as mock_peek:
        mock_peek.return_value = html_head_good_seo
        passed_good = await seo_filter.apply(url_good_seo)
        print(f"  URL (Good SEO): {url_good_seo}, Passed: {passed_good}, Score: {seo_filter._last_score:.2f}")
        assert passed_good

        mock_peek.return_value = html_head_poor_seo
        passed_poor = await seo_filter.apply(url_poor_seo)
        print(f"  URL (Poor SEO): {url_poor_seo}, Passed: {passed_poor}, Score: {seo_filter._last_score:.2f}")
        assert not passed_poor

asyncio.run(demo_seo_filter_threshold())
```

#### 2.7.2. Example: `SEOFilter` with custom `keywords` to check for keyword presence in title/meta.

```python
import asyncio
from crawl4ai.deep_crawling import SEOFilter
from unittest.mock import patch

async def demo_seo_filter_keywords():
    # Filter requires "Crawl4AI" in title/meta, and overall score >= 0.5
    seo_filter = SEOFilter(threshold=0.5, keywords=["Crawl4AI", "web scraping"])

    html_head_with_keyword = """
    <head>
        <title>Crawl4AI: The Best Web Scraping Tool</title>
        <meta name="description" content="Discover Crawl4AI for efficient web scraping.">
        <meta name="robots" content="index, follow"> 
    </head>
    """ # Missing canonical but has keywords
    url_with_keyword = "http://example.com/crawl4ai-tool"

    html_head_no_keyword = """
    <head>
        <title>A Generic Web Tool</title>
        <meta name="description" content="This is a tool for the web.">
        <meta name="robots" content="index, follow">
        <link rel="canonical" href="http://example.com/generic-tool" />
    </head>
    """ # Good general SEO but missing keywords
    url_no_keyword = "http://example.com/generic-tool"

    print(f"Testing SEOFilter with keywords ['Crawl4AI', 'web scraping'] and threshold 0.5:")
    with patch('crawl4ai.deep_crawling.filters.HeadPeek.peek_html') as mock_peek:
        mock_peek.return_value = html_head_with_keyword
        passed_with_kw = await seo_filter.apply(url_with_keyword)
        print(f"  URL (With Keyword): {url_with_keyword}, Passed: {passed_with_kw}, Score: {seo_filter._last_score:.2f}")
        assert passed_with_kw # Keyword presence significantly boosts score

        mock_peek.return_value = html_head_no_keyword
        passed_no_kw = await seo_filter.apply(url_no_keyword)
        print(f"  URL (No Keyword): {url_no_keyword}, Passed: {passed_no_kw}, Score: {seo_filter._last_score:.2f}")
        assert not passed_no_kw # Lack of keyword drops score below threshold

asyncio.run(demo_seo_filter_keywords())
```

#### 2.7.3. Example: `SEOFilter` with custom `weights` for different SEO factors.

```python
import asyncio
from crawl4ai.deep_crawling import SEOFilter
from unittest.mock import patch

async def demo_seo_filter_weights():
    # Emphasize title length and canonical tag more than others
    custom_weights = {
        "title_length": 0.3,  # Default 0.15
        "title_kw": 0.1,      # Default 0.18
        "meta_description": 0.1, # Default 0.12
        "canonical": 0.3,     # Default 0.10
        "robot_ok": 0.1,      # Default 0.20
        "schema_org": 0.05,   # Default 0.10
        "url_quality": 0.05   # Default 0.15
    } # Sum should ideally be 1.0 but filter normalizes internally if not.
    
    seo_filter = SEOFilter(threshold=0.6, weights=custom_weights)

    html_strong_title_canonical = """
    <head>
        <title>Perfect Title Length For Custom SEO Weights Test (50char)</title>
        <meta name="description" content="Short description."> 
        <link rel="canonical" href="http://example.com/custom-weights" />
        <meta name="robots" content="index, follow">
    </head>
    """
    url_strong_tc = "http://example.com/custom-weights"

    html_weak_title_canonical = """
    <head>
        <title>Tiny</title> 
        <meta name="description" content="Very very very long description that will be penalized for length if that factor has weight, but here title and canonical matter most.">
        <meta name="robots" content="index, follow">
    </head>
    """ # No canonical, bad title length
    url_weak_tc = "http://example.com/weak-title-canonical"

    print(f"Testing SEOFilter with custom weights (emphasizing title_length, canonical):")
    with patch('crawl4ai.deep_crawling.filters.HeadPeek.peek_html') as mock_peek:
        mock_peek.return_value = html_strong_title_canonical
        passed_strong = await seo_filter.apply(url_strong_tc)
        print(f"  URL (Strong T/C): {url_strong_tc}, Passed: {passed_strong}, Score: {seo_filter._last_score:.2f}")
        assert passed_strong

        mock_peek.return_value = html_weak_title_canonical
        passed_weak = await seo_filter.apply(url_weak_tc)
        print(f"  URL (Weak T/C): {url_weak_tc}, Passed: {passed_weak}, Score: {seo_filter._last_score:.2f}")
        assert not passed_weak

asyncio.run(demo_seo_filter_weights())
```

---
## 3. URL Scorers

This section showcases how to score URLs to guide priority-based crawling strategies like `BestFirstCrawlingStrategy`.

### 3.1. `ScoringStats`

#### 3.1.1. Example: Accessing `urls_scored`, `total_score`, `min_score`, and `max_score` from a `ScoringStats` object.

```python
import asyncio
from crawl4ai.deep_crawling import KeywordRelevanceScorer # Any scorer will do

async def demo_scoring_stats():
    scorer = KeywordRelevanceScorer(keywords=["apple", "banana"])

    urls = [
        "http://example.com/apple-pie",       # Score: 0.5 (1/2 keywords)
        "http://example.com/banana-bread",    # Score: 0.5
        "http://example.com/apple-and-banana",# Score: 1.0 (2/2 keywords)
        "http://example.com/orange-juice"     # Score: 0.0
    ]
    
    scores_achieved = []
    for url in urls:
        score = await scorer.score(url) # score() updates stats
        scores_achieved.append(score)

    stats = scorer.stats
    print(f"--- Scoring Stats for KeywordRelevanceScorer ---")
    print(f"URLs Scored: {stats.urls_scored}")
    print(f"Total Score Sum: {stats.total_score:.2f}") # Sum of (score * weight), weight is 1.0 here
    print(f"Min Score: {stats.min_score:.2f}")
    print(f"Max Score: {stats.max_score:.2f}")
    print(f"Average Score: {stats.average_score:.2f}")

    assert stats.urls_scored == 4
    assert abs(stats.total_score - (0.5 + 0.5 + 1.0 + 0.0)) < 0.01
    assert abs(stats.min_score - 0.0) < 0.01
    assert abs(stats.max_score - 1.0) < 0.01
    assert abs(stats.average_score - 2.0/4) < 0.01


asyncio.run(demo_scoring_stats())
```

### 3.2. `CompositeScorer`

#### 3.2.1. Example: Creating a `CompositeScorer` with `KeywordRelevanceScorer` and `PathDepthScorer`, assigning weights.

```python
import asyncio
from crawl4ai.deep_crawling import CompositeScorer, KeywordRelevanceScorer, PathDepthScorer

async def demo_composite_scorer():
    # Scorer 1: Keyword relevance (weight 0.7)
    keyword_scorer = KeywordRelevanceScorer(keywords=["guide"], weight=0.7)
    
    # Scorer 2: Path depth, optimal at 2 (weight 0.3)
    depth_scorer = PathDepthScorer(optimal_depth=2, weight=0.3)

    composite_scorer = CompositeScorer(scorers=[keyword_scorer, depth_scorer])

    url1 = "http://example.com/guides/main-guide.html" # Keyword match, depth 2
    # kw_score = 1.0 * 0.7 = 0.7
    # depth_score (optimal_depth=2, current_depth=2, diff=0) = 1.0 * 0.3 = 0.3
    # total = 0.7 + 0.3 = 1.0
    
    url2 = "http://example.com/blog/post" # No keyword, depth 2
    # kw_score = 0.0 * 0.7 = 0.0
    # depth_score (optimal_depth=2, current_depth=2, diff=0) = 1.0 * 0.3 = 0.3
    # total = 0.0 + 0.3 = 0.3

    url3 = "http://example.com/guides/intro" # Keyword match, depth 1
    # kw_score = 1.0 * 0.7 = 0.7
    # depth_score (optimal_depth=2, current_depth=1, diff=1) = 0.5 * 0.3 = 0.15
    # total = 0.7 + 0.15 = 0.85

    score1 = await composite_scorer.score(url1)
    score2 = await composite_scorer.score(url2)
    score3 = await composite_scorer.score(url3)

    print(f"URL: {url1}, Composite Score: {score1:.4f}")
    print(f"URL: {url2}, Composite Score: {score2:.4f}")
    print(f"URL: {url3}, Composite Score: {score3:.4f}")

    assert abs(score1 - 1.0) < 0.01
    assert abs(score2 - 0.3) < 0.01
    assert abs(score3 - 0.85) < 0.01
    
    # Check stats of individual scorers and composite
    print(f"\nComposite Scorer Stats: Avg={composite_scorer.stats.average_score:.2f}")
    print(f"  Keyword Scorer Stats: Avg={keyword_scorer.stats.average_score:.2f}")
    print(f"  Depth Scorer Stats: Avg={depth_scorer.stats.average_score:.2f}")


asyncio.run(demo_composite_scorer())
```

#### 3.2.2. Example: `CompositeScorer` with `normalize=True` to scale scores.

When `normalize=True`, the final score is divided by the number of scorers if there are scorers, ensuring it stays roughly in the 0-1 range if individual scorers are also in that range.

```python
import asyncio
from crawl4ai.deep_crawling import CompositeScorer, KeywordRelevanceScorer, PathDepthScorer

async def demo_composite_scorer_normalized():
    keyword_scorer = KeywordRelevanceScorer(keywords=["guide"], weight=1.0) # Unweighted for clarity
    depth_scorer = PathDepthScorer(optimal_depth=2, weight=1.0)       # Unweighted for clarity

    # With normalize=True, final score will be (kw_score + depth_score) / 2
    composite_scorer_norm = CompositeScorer(
        scorers=[keyword_scorer, depth_scorer], 
        normalize=True
    )

    url1 = "http://example.com/guides/main-guide.html" # Keyword match, depth 2
    # kw_score = 1.0
    # depth_score = 1.0
    # total_raw = 2.0; normalized = 2.0 / 2 = 1.0
    
    url2 = "http://example.com/blog/post" # No keyword, depth 2
    # kw_score = 0.0
    # depth_score = 1.0
    # total_raw = 1.0; normalized = 1.0 / 2 = 0.5

    score1_norm = await composite_scorer_norm.score(url1)
    score2_norm = await composite_scorer_norm.score(url2)

    print(f"URL: {url1}, Normalized Composite Score: {score1_norm:.4f}")
    print(f"URL: {url2}, Normalized Composite Score: {score2_norm:.4f}")
    
    assert abs(score1_norm - 1.0) < 0.01
    assert abs(score2_norm - 0.5) < 0.01

asyncio.run(demo_composite_scorer_normalized())
```

### 3.3. `KeywordRelevanceScorer`

#### 3.3.1. Example: Scoring URLs based on the presence of specific keywords.

```python
import asyncio
from crawl4ai.deep_crawling import KeywordRelevanceScorer

async def demo_keyword_relevance_scorer():
    scorer = KeywordRelevanceScorer(keywords=["apple", "banana", "cherry"])

    url1 = "http://example.com/apple-pie-recipe" # 1 keyword
    url2 = "http://example.com/banana-and-cherry-smoothie" # 2 keywords
    url3 = "http://example.com/orange-juice" # 0 keywords
    url4 = "http://example.com/apple-banana-cherry-fruit-salad" # 3 keywords

    score1 = await scorer.score(url1)
    score2 = await scorer.score(url2)
    score3 = await scorer.score(url3)
    score4 = await scorer.score(url4)

    print(f"URL: {url1}, Score: {score1:.2f} (Expected: ~0.33)")
    print(f"URL: {url2}, Score: {score2:.2f} (Expected: ~0.67)")
    print(f"URL: {url3}, Score: {score3:.2f} (Expected: 0.00)")
    print(f"URL: {url4}, Score: {score4:.2f} (Expected: 1.00)")
    
    assert abs(score1 - 1/3) < 0.01
    assert abs(score2 - 2/3) < 0.01
    assert abs(score3 - 0.0) < 0.01
    assert abs(score4 - 1.0) < 0.01

asyncio.run(demo_keyword_relevance_scorer())
```

#### 3.3.2. Example: `KeywordRelevanceScorer` with `case_sensitive=True`.

```python
import asyncio
from crawl4ai.deep_crawling import KeywordRelevanceScorer

async def demo_keyword_relevance_case_sensitive():
    # Case-sensitive matching
    scorer_cs = KeywordRelevanceScorer(keywords=["Apple"], case_sensitive=True)
    # Default: case-insensitive
    scorer_ci = KeywordRelevanceScorer(keywords=["Apple"])


    url_exact_match = "http://example.com/Apple-iPhone"
    url_lowercase_match = "http://example.com/apple-ipad"
    url_no_match = "http://example.com/orange-device"

    print("--- Case-Sensitive Scorer (keyword: 'Apple') ---")
    print(f"URL: {url_exact_match}, Score: {await scorer_cs.score(url_exact_match):.2f}")
    print(f"URL: {url_lowercase_match}, Score: {await scorer_cs.score(url_lowercase_match):.2f}")
    print(f"URL: {url_no_match}, Score: {await scorer_cs.score(url_no_match):.2f}")

    assert abs(await scorer_cs.score(url_exact_match) - 1.0) < 0.01
    assert abs(await scorer_cs.score(url_lowercase_match) - 0.0) < 0.01
    assert abs(await scorer_cs.score(url_no_match) - 0.0) < 0.01

    print("\n--- Case-Insensitive Scorer (keyword: 'Apple') ---")
    print(f"URL: {url_exact_match}, Score: {await scorer_ci.score(url_exact_match):.2f}")
    print(f"URL: {url_lowercase_match}, Score: {await scorer_ci.score(url_lowercase_match):.2f}")
    
    assert abs(await scorer_ci.score(url_exact_match) - 1.0) < 0.01
    assert abs(await scorer_ci.score(url_lowercase_match) - 1.0) < 0.01

asyncio.run(demo_keyword_relevance_case_sensitive())
```

### 3.4. `PathDepthScorer`

#### 3.4.1. Example: `PathDepthScorer` with an `optimal_depth` of 2.

```python
import asyncio
from crawl4ai.deep_crawling import PathDepthScorer

async def demo_path_depth_scorer_optimal_2():
    scorer = PathDepthScorer(optimal_depth=2)

    url_depth0 = "http://example.com"                  # diff = 2, score ~0.33
    url_depth1 = "http://example.com/category"         # diff = 1, score 0.5
    url_depth2 = "http://example.com/category/product" # diff = 0, score 1.0
    url_depth3 = "http://example.com/cat/prod/details" # diff = 1, score 0.5
    url_depth4 = "http://example.com/cat/prod/det/rev" # diff = 2, score ~0.33

    print(f"PathDepthScorer with optimal_depth=2:")
    print(f"URL: {url_depth0} (depth 0), Score: {await scorer.score(url_depth0):.3f}")
    print(f"URL: {url_depth1} (depth 1), Score: {await scorer.score(url_depth1):.3f}")
    print(f"URL: {url_depth2} (depth 2), Score: {await scorer.score(url_depth2):.3f}")
    print(f"URL: {url_depth3} (depth 3), Score: {await scorer.score(url_depth3):.3f}")
    print(f"URL: {url_depth4} (depth 4), Score: {await scorer.score(url_depth4):.3f}")
    
    assert abs(await scorer.score(url_depth2) - 1.0) < 0.01
    assert abs(await scorer.score(url_depth1) - 0.5) < 0.01
    assert abs(await scorer.score(url_depth3) - 0.5) < 0.01

asyncio.run(demo_path_depth_scorer_optimal_2())
```

#### 3.4.2. Example: Demonstrating how scores decrease as path depth deviates from `optimal_depth`.
(This is covered by 3.4.1.)

### 3.5. `ContentTypeScorer`

#### 3.5.1. Example: `ContentTypeScorer` prioritizing ".html" and ".pdf" URLs over others based on `type_weights`.
*Note: This scorer relies on URL extensions primarily, as live HEAD requests are not part of its `score` method.*

```python
import asyncio
from crawl4ai.deep_crawling import ContentTypeScorer

async def demo_content_type_scorer():
    type_weights = {
        ".html": 1.0,
        ".pdf": 0.8,
        ".jpg": 0.2,
        # Other types get default 0.1 (not explicitly shown here)
    }
    scorer = ContentTypeScorer(type_weights=type_weights)

    url_html = "http://example.com/index.html"
    url_pdf = "http://example.com/document.pdf"
    url_jpg = "http://example.com/image.jpg"
    url_txt = "http://example.com/notes.txt" # Not in weights, gets default 0.1

    print(f"ContentTypeScorer with weights: {type_weights}")
    print(f"URL: {url_html}, Score: {await scorer.score(url_html):.2f}")
    print(f"URL: {url_pdf}, Score: {await scorer.score(url_pdf):.2f}")
    print(f"URL: {url_jpg}, Score: {await scorer.score(url_jpg):.2f}")
    print(f"URL: {url_txt}, Score: {await scorer.score(url_txt):.2f}")
    
    assert abs(await scorer.score(url_html) - 1.0) < 0.01
    assert abs(await scorer.score(url_pdf) - 0.8) < 0.01
    assert abs(await scorer.score(url_jpg) - 0.2) < 0.01
    assert abs(await scorer.score(url_txt) - 0.1) < 0.01 # Default for unlisted

asyncio.run(demo_content_type_scorer())
```

### 3.6. `FreshnessScorer`

#### 3.6.1. Example: `FreshnessScorer` scoring URLs with recent years higher.

```python
import asyncio
from datetime import datetime
from crawl4ai.deep_crawling import FreshnessScorer

async def demo_freshness_scorer():
    current_year = datetime.now().year
    scorer = FreshnessScorer(current_year=current_year)

    url_current_year = f"http://example.com/news/{current_year}/article"
    url_last_year = f"http://example.com/archive/{current_year - 1}/report"
    url_five_years_ago = f"http://example.com/blog/{current_year - 5}/post"
    url_ten_years_ago = f"http://example.com/old/{current_year - 10}/story"
    url_no_year = "http://example.com/static-page"

    print(f"FreshnessScorer (current year: {current_year}):")
    score_current = await scorer.score(url_current_year)
    score_last = await scorer.score(url_last_year)
    score_five_ago = await scorer.score(url_five_years_ago)
    score_ten_ago = await scorer.score(url_ten_years_ago)
    score_no_year = await scorer.score(url_no_year)
    
    print(f"URL: {url_current_year}, Score: {score_current:.2f} (Expected: 1.0)")
    print(f"URL: {url_last_year}, Score: {score_last:.2f} (Expected: 0.9)")
    print(f"URL: {url_five_years_ago}, Score: {score_five_ago:.2f} (Expected: 0.5)")
    print(f"URL: {url_ten_years_ago}, Score: {score_ten_ago:.2f} (Expected: ~0.1)") # 1.0 - 10 * 0.1 = 0, capped at 0.1
    print(f"URL: {url_no_year}, Score: {score_no_year:.2f} (Expected: 0.5 - default)")

    assert abs(score_current - 1.0) < 0.01
    assert abs(score_last - 0.9) < 0.01
    assert abs(score_five_ago - 0.5) < 0.01
    assert abs(score_ten_ago - 0.1) < 0.01 # Max(0.1, 1.0 - 10*0.1)
    assert abs(score_no_year - 0.5) < 0.01


asyncio.run(demo_freshness_scorer())
```

#### 3.6.2. Example: Demonstrating `FreshnessScorer` with a custom `current_year`.

```python
import asyncio
from crawl4ai.deep_crawling import FreshnessScorer

async def demo_freshness_scorer_custom_year():
    # Pretend it's 2030 for scoring purposes
    custom_current_year = 2030
    scorer = FreshnessScorer(current_year=custom_current_year)

    url_actually_2024 = "http://example.com/event/2024/details" # 6 years old relative to 2030
    # Expected score: max(0.1, 1.0 - 6 * 0.1) = max(0.1, 0.4) = 0.4
    # If using lookup: index 6 is out of bounds, so fallback calculation.
    # _FRESHNESS_SCORES has 6 elements (index 0-5). Year diff 6 is 1.0 - 6*0.1 = 0.4

    score_2024 = await scorer.score(url_actually_2024)
    print(f"FreshnessScorer (custom current year: {custom_current_year}):")
    print(f"URL: {url_actually_2024}, Score: {score_2024:.2f}")
    
    assert abs(score_2024 - 0.4) < 0.01

asyncio.run(demo_freshness_scorer_custom_year())
```

### 3.7. `DomainAuthorityScorer`

#### 3.7.1. Example: `DomainAuthorityScorer` with a custom `domain_weights` dictionary.

```python
import asyncio
from crawl4ai.deep_crawling import DomainAuthorityScorer

async def demo_domain_authority_custom_weights():
    domain_weights = {
        "wikipedia.org": 0.9,
        "github.com": 0.8,
        "example.com": 0.5  # Default is 0.5, but explicitly setting
    }
    scorer = DomainAuthorityScorer(domain_weights=domain_weights)

    url_wiki = "https://en.wikipedia.org/wiki/Web_scraping"
    url_github = "https://github.com/crawl4ai/crawl4ai"
    url_example = "http://www.example.com/somepage" # Subdomain is fine
    url_unknown = "http://unknownsite.net/path"

    print(f"DomainAuthorityScorer with custom weights:")
    print(f"URL: {url_wiki}, Score: {await scorer.score(url_wiki):.2f}")
    print(f"URL: {url_github}, Score: {await scorer.score(url_github):.2f}")
    print(f"URL: {url_example}, Score: {await scorer.score(url_example):.2f}")
    print(f"URL: {url_unknown}, Score: {await scorer.score(url_unknown):.2f} (default weight)")

    assert abs(await scorer.score(url_wiki) - 0.9) < 0.01
    assert abs(await scorer.score(url_github) - 0.8) < 0.01
    assert abs(await scorer.score(url_example) - 0.5) < 0.01
    assert abs(await scorer.score(url_unknown) - scorer.default_weight) < 0.01 # default_weight is 0.5

asyncio.run(demo_domain_authority_custom_weights())
```

#### 3.7.2. Example: `DomainAuthorityScorer` showing the effect of `default_weight`.

```python
import asyncio
from crawl4ai.deep_crawling import DomainAuthorityScorer

async def demo_domain_authority_default_weight():
    # No custom weights, so all domains get default_weight unless they are in the pre-cached top domains
    # Default_weight defaults to 0.5
    scorer_default = DomainAuthorityScorer() 
    
    # Custom default weight
    scorer_custom_default = DomainAuthorityScorer(default_weight=0.3)

    url_random1 = "http://random-new-site.xyz/page"
    url_random2 = "http://another-unknown-domain.io/blog"

    print(f"DomainAuthorityScorer with default_weight={scorer_default.default_weight}:")
    print(f"  URL: {url_random1}, Score: {await scorer_default.score(url_random1):.2f}")
    
    print(f"\nDomainAuthorityScorer with custom default_weight={scorer_custom_default.default_weight}:")
    print(f"  URL: {url_random2}, Score: {await scorer_custom_default.score(url_random2):.2f}")

    # Check if the score matches the default_weight for domains not in the top_domains cache
    # (Assuming these random domains are not in the small pre-cached list)
    assert abs(await scorer_default.score(url_random1) - 0.5) < 0.01 
    assert abs(await scorer_custom_default.score(url_random2) - 0.3) < 0.01

asyncio.run(demo_domain_authority_default_weight())
```

---
## 4. Integration Examples

Showcasing how different deep crawling components can be combined.

### 4.1. Example: `BFSDeeepCrawlStrategy` with a `FilterChain` (`DomainFilter` + `URLPatternFilter`) and a simple `PathDepthScorer`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import (
    BFSDeeepCrawlStrategy, FilterChain, DomainFilter, URLPatternFilter, PathDepthScorer
)

RAW_HTML_INTEGRATION_1 = """
<html><body>
    <a href="http://example.com/docs/page1.html">Docs Page 1</a>
    <a href="http://example.com/blog/post1.html">Blog Post 1 (depth 2)</a>
    <a href="http://example.com/docs/page2.pdf">Docs Page 2 (PDF)</a>
    <a href="http://anotherexample.com/external.html">External HTML</a>
    <a href="http://example.com/very/deep/page.html">Deep Page (depth 3)</a>
</body></html>
"""
START_URL_INTEGRATION_1 = f"raw://{RAW_HTML_INTEGRATION_1}"

async def bfs_integration_example():
    # Filters: Only example.com, only .html files
    filter_chain = FilterChain(filters=[
        DomainFilter(allowed_domains=["example.com"]),
        URLPatternFilter(patterns=["*.html"])
    ])
    
    # Scorer: Prioritize pages with path depth 1 (e.g. /docs/)
    # Threshold will allow only high-scored links based on this.
    # Optimal depth 1, score for depth 1 = 1.0; depth 2 = 0.5; depth 3 = 0.33
    url_scorer = PathDepthScorer(optimal_depth=1)
    score_threshold = 0.6 # Allows only depth 1 pages

    bfs_strategy = BFSDeeepCrawlStrategy(
        max_depth=2, 
        max_pages=5,
        filter_chain=filter_chain,
        url_scorer=url_scorer,
        score_threshold=score_threshold
    )
    run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)

    async with AsyncWebCrawler() as crawler:
        print("Starting BFS integration crawl...")
        results_list = await crawler.arun(url=START_URL_INTEGRATION_1, config=run_config)
        
        print(f"\n--- BFS Integration Results ---")
        crawled_urls = []
        if results_list:
            for result in results_list:
                if result.success:
                    print(f"Crawled: {result.url} (Depth: {result.metadata.get('depth')}, Score: {result.metadata.get('score')})")
                    crawled_urls.append(result.url)
            
            # Expected: Only "http://example.com/docs/page1.html" (depth 1, .html, on domain, score 1.0)
            # "/blog/post1.html" is depth 2, score 0.5 (below threshold)
            # "/docs/page2.pdf" fails pattern filter
            # "external.html" fails domain filter
            # "/very/deep/page.html" is depth 3, score 0.33 (below threshold)
            assert "http://example.com/docs/page1.html" in crawled_urls
            assert len(crawled_urls) == 2 # Start URL + one matched page
            assert "http://example.com/blog/post1.html" not in crawled_urls
            assert "http://example.com/docs/page2.pdf" not in crawled_urls
            assert "http://anotherexample.com/external.html" not in crawled_urls
            assert "http://example.com/very/deep/page.html" not in crawled_urls
        else:
            print("No results.")

asyncio.run(bfs_integration_example())
```

### 4.2. Example: `BestFirstCrawlingStrategy` driven by a `CompositeScorer` (`KeywordRelevanceScorer` + `FreshnessScorer`) and filtered by `ContentTypeFilter`.

```python
import asyncio
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import (
    BestFirstCrawlingStrategy, CompositeScorer, KeywordRelevanceScorer, 
    FreshnessScorer, ContentTypeFilter
)

RAW_HTML_INTEGRATION_2 = f"""
<html><body>
    <a href="/news/{datetime.now().year}/ai-breakthrough.html">AI Breakthrough ({datetime.now().year})</a>
    <a href="/news/{datetime.now().year-1}/old-ai-news.html">Old AI News ({datetime.now().year-1})</a>
    <a href="/tech/general-tech.html">General Tech ({datetime.now().year})</a>
    <a href="/news/{datetime.now().year}/ai-update.pdf">AI Update PDF ({datetime.now().year})</a>
</body></html>
"""
START_URL_INTEGRATION_2 = f"raw://{RAW_HTML_INTEGRATION_2}"

async def best_first_integration_example():
    # Scorers
    keyword_scorer = KeywordRelevanceScorer(keywords=["ai"], weight=0.6)
    freshness_scorer = FreshnessScorer(current_year=datetime.now().year, weight=0.4)
    composite_scorer = CompositeScorer(scorers=[keyword_scorer, freshness_scorer])

    # Filter: Only HTML content
    content_filter = ContentTypeFilter(allowed_types=["text/html"])
    filter_chain = FilterChain(filters=[content_filter])

    strategy = BestFirstCrawlingStrategy(
        max_depth=1,
        max_pages=3, # Start URL + 2 more
        url_scorer=composite_scorer,
        filter_chain=filter_chain
    )
    run_config = CrawlerRunConfig(deep_crawl_strategy=strategy, stream=True) # Stream to see order

    async with AsyncWebCrawler() as crawler:
        print("Starting Best-First integration crawl...")
        crawled_items_in_order = []
        async for result in await crawler.arun(url=START_URL_INTEGRATION_2, config=run_config):
            if result.success:
                print(f"Crawled: {result.url_for_display()} (Score: {result.metadata.get('score'):.2f}, Depth: {result.metadata.get('depth')})")
                crawled_items_in_order.append(result.url_for_display())
        
        print(f"\nCrawled order: {crawled_items_in_order}")
        # Expected:
        # 1. Start URL
        # 2. AI Breakthrough (current year, "ai" keyword) - Highest score
        # 3. General Tech (current year, no "ai") OR Old AI News (last year, "ai" keyword)
        #    - AI Breakthrough: kw_score=1*0.6=0.6, fresh_score=1*0.4=0.4. Total=1.0
        #    - Old AI News: kw_score=1*0.6=0.6, fresh_score=0.9*0.4=0.36. Total=0.96
        #    - General Tech: kw_score=0*0.6=0.0, fresh_score=1*0.4=0.4. Total=0.4
        #    - AI Update PDF: Filtered out by ContentTypeFilter
        # So, order after start URL should be AI Breakthrough, then Old AI News.
        if len(crawled_items_in_order) >= 3: # Start URL + 2 others
            assert "ai-breakthrough.html" in crawled_items_in_order[1]
            assert "old-ai-news.html" in crawled_items_in_order[2]
        assert not any("ai-update.pdf" in url for url in crawled_items_in_order)

asyncio.run(best_first_integration_example())
```

### 4.3. Example: `DFSDeeepCrawlStrategy` with `max_pages` and `max_depth` to show interaction.
(This has been demonstrated in 1.4.2.1 and 1.4.2.2 where either `max_depth` or `max_pages` can limit the crawl first.)

### 4.4. Example: Using `DeepCrawlDecorator` to initiate a `BFSDeeepCrawlStrategy` with a `FilterChain` including `ContentRelevanceFilter`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import (
    BFSDeeepCrawlStrategy, FilterChain, ContentRelevanceFilter
)
from unittest.mock import patch # To mock HeadPeek

async def decorator_bfs_content_relevance():
    query = "important information"
    # Filter chain with content relevance
    filter_chain = FilterChain(filters=[
        ContentRelevanceFilter(query=query, threshold=0.1)
    ])

    bfs_strategy = BFSDeeepCrawlStrategy(
        max_depth=1, 
        max_pages=3,
        filter_chain=filter_chain
    )
    run_config = CrawlerRunConfig(deep_crawl_strategy=bfs_strategy)

    html_relevant_head = "<head><title>Key Info</title><meta name='description' content='This page contains important information about our services.'></head>"
    html_irrelevant_head = "<head><title>Random Stuff</title><meta name='description' content='Some other details.'></head>"
    
    start_html = f"""<html><body>
        <a href="raw_relevant.html">Relevant Link</a>
        <a href="raw_irrelevant.html">Irrelevant Link</a>
    </body></html>"""
    
    # Create self-contained raw URLs (simplified)
    relevant_page_content = f"raw://{html_relevant_head}<body>Relevant content</body></html>"
    irrelevant_page_content = f"raw://{html_irrelevant_head}<body>Irrelevant content</body></html>"
    
    start_url_content_rel = start_html.replace("raw_relevant.html", relevant_page_content.replace('"', '&quot;')) \
                                     .replace("raw_irrelevant.html", irrelevant_page_content.replace('"', '&quot;'))
    start_url_content_rel = f"raw://{start_url_content_rel}"


    # Mock HeadPeek.peek_html to control responses for filter
    # This mapping helps return the correct head content for each URL
    mock_heads = {
        relevant_page_content: html_relevant_head, # Key by the full raw URL string
        irrelevant_page_content: html_irrelevant_head
    }
    
    async def mock_peek_html_func(url_to_peek):
        # For raw URLs, the actual URL is the content itself. We need to find the one that matches.
        for mock_url_key, head_content in mock_heads.items():
            if mock_url_key == url_to_peek: # Direct match for raw URLs
                 return head_content
        return "" # Default for unexpected URLs

    with patch('crawl4ai.deep_crawling.filters.HeadPeek.peek_html', side_effect=mock_peek_html_func):
        async with AsyncWebCrawler() as crawler: # Decorator is active via run_config
            print("Starting Decorator + BFS + ContentRelevanceFilter crawl...")
            results_list = await crawler.arun(url=start_url_content_rel, config=run_config)
            
            crawled_urls = []
            if results_list:
                print("\n--- Crawl Results ---")
                for result in results_list:
                    if result.success:
                        print(f"Crawled: {result.url_for_display()}")
                        crawled_urls.append(result.url_for_display())
                
                assert any(u == relevant_page_content for u in crawled_urls), "Relevant page should have been crawled."
                assert not any(u == irrelevant_page_content for u in crawled_urls), "Irrelevant page should have been filtered."
            else:
                print("No results.")

asyncio.run(decorator_bfs_content_relevance())
```

### 4.5. Example: `BestFirstCrawlingStrategy` using a `url_scorer` that includes `DomainAuthorityScorer` to prioritize high-authority external links when `include_external=True`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import (
    BestFirstCrawlingStrategy, DomainAuthorityScorer
)

RAW_HTML_INTEGRATION_DOMAIN_AUTH = """
<html><body>
    <a href="https://www.wikipedia.org">Wikipedia (High Auth)</a>
    <a href="http://example-blog.blogspot.com">Personal Blog (Low Auth)</a>
    <a href="https://github.com/crawl4ai">Crawl4AI GitHub (Mid/High Auth)</a>
</body></html>
"""
START_URL_INTEGRATION_DA = f"raw://{RAW_HTML_INTEGRATION_DOMAIN_AUTH}"

async def best_first_domain_authority_external():
    # Scorer: Prioritize by domain authority
    # Note: DomainAuthorityScorer has some pre-defined weights, wikipedia.org and github.com are usually high.
    domain_scorer = DomainAuthorityScorer() 

    strategy = BestFirstCrawlingStrategy(
        max_depth=1,
        max_pages=3, # Start URL + 2 external links
        url_scorer=domain_scorer,
        include_external=True # Crucial for this example
    )
    run_config = CrawlerRunConfig(deep_crawl_strategy=strategy, stream=True)

    async with AsyncWebCrawler() as crawler:
        print("Starting Best-First crawl prioritizing high-authority external links...")
        crawled_urls_in_order = []
        async for result in await crawler.arun(url=START_URL_INTEGRATION_DA, config=run_config):
            if result.success:
                score = result.metadata.get('score', 'N/A')
                print(f"Crawled: {result.url} (Score: {score:.2f})")
                crawled_urls_in_order.append(result.url)
        
        print(f"\nCrawled order (after start URL): {[url.split('//')[1] for url in crawled_urls_in_order[1:]]}")
        
        # Expected order (after start URL): wikipedia.org, then github.com (or vice-versa), then blogspot.com
        # This depends on the default scores in DomainAuthorityScorer.
        # Wikipedia usually has a very high score.
        if len(crawled_urls_in_order) > 1:
            assert "wikipedia.org" in crawled_urls_in_order[1], "Wikipedia (high authority) should be prioritized."
        if len(crawled_urls_in_order) > 2:
             assert "github.com" in crawled_urls_in_order[2] or "blogspot.com" in crawled_urls_in_order[2]

asyncio.run(best_first_domain_authority_external())
```

---
## 5. Advanced Scenarios & Edge Cases

### 5.1. Example: Deep crawling a site where initial pages have no links, but deeper pages (found via alternative means, if simulatable) do.
*This scenario is hard to demonstrate without a mock server or very specific site structure. The core idea is that if the `start_url` itself has no links, the crawl stops unless the strategy has other means to find URLs (not typical for these strategies without custom `link_discovery` or being fed URLs externally).*
*A conceptual example: if `arun` was called with multiple start URLs, and one of them had links.*

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy

RAW_HTML_NO_LINKS = "<html><body>No links here.</body></html>"
RAW_HTML_WITH_LINKS = "<html><body><a href='http://example.com/final'>Final Page</a></body></html>"

# Create a scenario where the first URL has no links, but we want to show that if other URLs
# were added to the queue (e.g., from a different source or a modified strategy), they'd be processed.
# This tests the strategy's ability to continue if the queue is populated externally/later.
# For this example, we'll use a simple BFS and "manually" add to its queue for demo.

async def advanced_no_initial_links():
    strategy = BFSDeeepCrawlStrategy(max_depth=1, max_pages=3)
    run_config = CrawlerRunConfig(deep_crawl_strategy=strategy)
    
    start_url_no_links = f"raw://{RAW_HTML_NO_LINKS}"
    second_url_with_links = f"raw://{RAW_HTML_WITH_LINKS}"

    async with AsyncWebCrawler() as crawler:
        print(f"Attempting crawl starting with URL that has no links: {start_url_no_links}")
        
        # First, try to crawl the page with no links. Expected: only start_url is processed.
        results1_container = await crawler.arun(url=start_url_no_links, config=run_config)
        results1 = [res async for res in results1_container] if hasattr(results1_container, '__aiter__') else results1_container

        print(f"Results from first crawl (no links): {[r.url_for_display() for r in results1]}")
        assert len(results1) == 1

        # Now, let's conceptualize how a strategy might continue if new URLs are added.
        # The actual strategies' queues are internal. We'll simulate a new crawl.
        # If the strategy's queue was externally populated, it would process them.
        # For a direct test, we'd need to modify the strategy or use a more complex setup.
        # This is more about the crawler's ability to handle an empty next_level from one source.
        
        print(f"\nSimulating a scenario where another URL with links is processed by the *same strategy instance* (if possible):")
        # To truly test this with the same strategy instance maintaining state,
        # we'd need to call its internal methods or re-architect this test.
        # For simplicity, we show that a *new* crawl with a populated start will work.
        
        results2_container = await crawler.arun(url=second_url_with_links, config=run_config)
        results2 = [res async for res in results2_container] if hasattr(results2_container, '__aiter__') else results2_container

        print(f"Results from second crawl (with links):")
        found_final_page = False
        for r in results2:
            print(f"  - {r.url_for_display()} (Depth: {r.metadata.get('depth')})")
            if "example.com/final" in r.url_for_display():
                found_final_page = True
        assert len(results2) >= 2 # start URL + final page
        assert found_final_page

asyncio.run(advanced_no_initial_links())
```

### 5.2. Example: Handling a `score_threshold` so high in `BFSDeeepCrawlStrategy` or `BestFirstCrawlingStrategy` that no new links are added.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeeepCrawlStrategy, PathDepthScorer

RAW_HTML_FOR_HIGH_THRESHOLD = """
<html><body>
    <a href="/page1">Page 1</a>
    <a href="/category/page2">Page 2</a>
</body></html>
"""
START_URL_RAW_HIGH_THRESHOLD = f"raw://{RAW_HTML_FOR_HIGH_THRESHOLD}"

async def high_score_threshold_no_new_links():
    # Scorer that gives scores between 0 and 1
    url_scorer = PathDepthScorer(optimal_depth=0) 
    
    # Set a threshold higher than any possible score (e.g., PathDepthScorer max is 1.0)
    high_threshold = 1.1 

    strategy = BFSDeeepCrawlStrategy( # Could also be BestFirstCrawlingStrategy
        max_depth=1, 
        max_pages=5,
        url_scorer=url_scorer,
        score_threshold=high_threshold
    )
    run_config = CrawlerRunConfig(deep_crawl_strategy=strategy)

    async with AsyncWebCrawler() as crawler:
        print(f"Starting crawl with very high score_threshold ({high_threshold})...")
        results_list = await crawler.arun(url=START_URL_RAW_HIGH_THRESHOLD, config=run_config)
        
        print(f"\n--- Crawl Results (High Threshold) ---")
        crawled_urls_count = 0
        if results_list:
            for result in results_list:
                if result.success:
                    crawled_urls_count +=1
                    print(f"Crawled: {result.url_for_display()} (Depth: {result.metadata.get('depth')}, Score: {result.metadata.get('score', 'N/A')})")
            
            # Expect only the start URL to be crawled, as all discovered links will fail threshold
            assert crawled_urls_count == 1, "Only the start URL should be crawled with such a high threshold."
            assert strategy.stats.urls_skipped > 0, "Links should have been skipped due to threshold."
            print(f"URLs skipped by scorer: {strategy.stats.urls_skipped}")
        else:
            print("No results (unexpected).")

asyncio.run(high_score_threshold_no_new_links())
```

### 5.3. Example: Demonstrating the behavior of `max_pages` in BFS when a level has more links than the remaining page capacity.
(This was covered effectively by 1.3.5.2, which simulates the internal logic of `link_discovery` respecting `max_pages`.)

### 5.4. Example: `URLPatternFilter` with complex regex to match very specific URL structures.

```python
import asyncio
from crawl4ai.deep_crawling import URLPatternFilter

async def complex_regex_url_pattern():
    # Regex to match URLs like: /archive/YYYY/MM/DD/article-slug-with-hyphens.html
    # Where YYYY is 20xx, MM is 01-12, DD is 01-31.
    complex_pattern = r"/archive/20\d{2}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/[a-z0-9-]+(\.html)?$"
    
    archive_filter = URLPatternFilter(patterns=[complex_pattern])

    urls_to_test = [
        "http://example.com/archive/2023/05/15/my-great-article.html", # Match
        "http://example.com/archive/2024/12/31/another-post",          # Match (optional .html)
        "http://example.com/archive/2022/13/01/invalid-month.html",    # No Match (invalid month)
        "http://example.com/blog/2023/05/15/my-great-article.html",    # No Match (wrong base path)
        "http://example.com/archive/1999/01/01/old-article.html"      # No Match (year doesn't start with 20)
    ]

    print(f"Testing with complex regex pattern: {complex_pattern}")
    for url in urls_to_test:
        passed = await archive_filter.apply(url)
        print(f"  URL: {url}, Passed: {passed}")

    assert await archive_filter.apply(urls_to_test[0]) == True
    assert await archive_filter.apply(urls_to_test[1]) == True
    assert await archive_filter.apply(urls_to_test[2]) == False
    assert await archive_filter.apply(urls_to_test[3]) == False
    assert await archive_filter.apply(urls_to_test[4]) == False

asyncio.run(complex_regex_url_pattern())
```

### 5.5. Example: A `FilterChain` where one filter passes a URL but a subsequent filter rejects it.

```python
import asyncio
from crawl4ai.deep_crawling import FilterChain, DomainFilter, URLPatternFilter

async def filter_chain_sequential_rejection():
    # Filter 1: Allow 'example.com' (will pass 'http://example.com/admin/login')
    domain_filter = DomainFilter(allowed_domains=["example.com"])
    
    # Filter 2: Reject anything with 'admin' (will reject 'http://example.com/admin/login')
    no_admin_filter = URLPatternFilter(patterns=["*admin*"], reverse=True)
    
    filter_chain = FilterChain(filters=[domain_filter, no_admin_filter])

    url_admin_on_domain = "http://example.com/admin/login"
    url_safe_on_domain = "http://example.com/dashboard"

    print("Testing FilterChain: DomainFilter (allow example.com) -> URLPatternFilter (reject *admin*)")
    
    passed_admin = await filter_chain.apply(url_admin_on_domain)
    print(f"URL: {url_admin_on_domain}, Passed Chain: {passed_admin}")
    print(f"  DomainFilter passed: {await domain_filter.apply(url_admin_on_domain)}") # Apply individually to see
    print(f"  NoAdminFilter passed: {await no_admin_filter.apply(url_admin_on_domain)}")
    assert not passed_admin # Should be rejected by the second filter

    passed_safe = await filter_chain.apply(url_safe_on_domain)
    print(f"URL: {url_safe_on_domain}, Passed Chain: {passed_safe}")
    print(f"  DomainFilter passed: {await domain_filter.apply(url_safe_on_domain)}")
    print(f"  NoAdminFilter passed: {await no_admin_filter.apply(url_safe_on_domain)}")
    assert passed_safe # Should pass both filters

asyncio.run(filter_chain_sequential_rejection())
```

---
End of Examples Document.
```

---

