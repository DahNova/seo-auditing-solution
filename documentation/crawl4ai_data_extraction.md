# Crawl4AI Custom LLM Context
Generated on: 2025-06-15T06:14:57.281Z
Total files: 3

---

## Data Extraction - Memory
Source: crawl4ai_extraction_memory_content.llm.md

Okay, I will now generate the "Foundational Memory" document for the `extraction` component of `crawl4ai`, based on the outline you provided and the information I've processed from the codebase and existing documentation.

```markdown
# Detailed Outline for crawl4ai - extraction Component

**Target Document Type:** memory
**Target Output Filename Suggestion:** `llm_memory_extraction.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2024-05-24
---

## 1. Overview of Data Extraction in Crawl4ai

*   1.1. Purpose of the Extraction Component: The extraction component in Crawl4ai is responsible for parsing structured data from web content (HTML, text, Markdown) or PDF documents. It allows users to define how data should be identified and extracted, using various strategies ranging from rule-based (CSS, XPath, Regex) to LLM-powered approaches. Its goal is to transform raw crawled content into usable, structured information.
*   1.2. Core Concepts:
    *   1.2.1. `ExtractionStrategy`: This is an abstract base class (interface) that defines the contract for all specific extraction methods. Each strategy implements how data is extracted from the provided content.
    *   1.2.2. `ChunkingStrategy`: This is an abstract base class (interface) for strategies that preprocess content by splitting it into smaller, manageable chunks. This is particularly relevant for LLM-based extraction strategies that have token limits for their input.
    *   1.2.3. Schemas: Schemas define the structure of the data to be extracted. For non-LLM strategies like `JsonCssExtractionStrategy` or `JsonXPathExtractionStrategy`, schemas are typically dictionary-based, specifying selectors and field types. For `LLMExtractionStrategy`, schemas can be Pydantic models or JSON schema dictionaries that guide the LLM in structuring its output.
    *   1.2.4. `CrawlerRunConfig`: The `CrawlerRunConfig` object allows users to specify which `extraction_strategy` and `chunking_strategy` (if applicable) should be used for a particular crawl operation via its `arun()` method.

## 2. `ExtractionStrategy` Interface

*   2.1. Purpose: The `ExtractionStrategy` class, found in `crawl4ai.extraction_strategy`, serves as an abstract base class (ABC) defining the standard interface for all data extraction strategies within the Crawl4ai library. Implementations of this class provide specific methods for extracting structured data from content.
*   2.2. Key Abstract Methods:
    *   `extract(self, url: str, content: str, *q, **kwargs) -> List[Dict[str, Any]]`:
        *   Description: Abstract method intended to extract meaningful blocks or chunks from the given content. Subclasses must implement this.
        *   Parameters:
            *   `url (str)`: The URL of the webpage.
            *   `content (str)`: The HTML, Markdown, or text content of the webpage.
            *   `*q`: Variable positional arguments.
            *   `**kwargs`: Variable keyword arguments.
        *   Returns: `List[Dict[str, Any]]` - A list of extracted blocks or chunks, typically as dictionaries.
    *   `run(self, url: str, sections: List[str], *q, **kwargs) -> List[Dict[str, Any]]`:
        *   Description: Abstract method to process sections of text, often in parallel by default implementations in subclasses. Subclasses must implement this.
        *   Parameters:
            *   `url (str)`: The URL of the webpage.
            *   `sections (List[str])`: List of sections (strings) to process.
            *   `*q`: Variable positional arguments.
            *   `**kwargs`: Variable keyword arguments.
        *   Returns: `List[Dict[str, Any]]` - A list of processed JSON blocks.
*   2.3. Input Format Property:
    *   `input_format (str)`: [Read-only] - An attribute indicating the expected input format for the content to be processed by the strategy (e.g., "markdown", "html", "fit_html", "text"). Default is "markdown".

## 3. Non-LLM Based Extraction Strategies

*   ### 3.1. Class `NoExtractionStrategy`
    *   3.1.1. Purpose: A baseline `ExtractionStrategy` that performs no actual data extraction. It returns the input content as is, typically useful for scenarios where only raw or cleaned HTML/Markdown is needed without further structuring.
    *   3.1.2. Inheritance: `ExtractionStrategy`
    *   3.1.3. Initialization (`__init__`):
        *   3.1.3.1. Signature: `NoExtractionStrategy(**kwargs)`
        *   3.1.3.2. Parameters:
            *   `**kwargs`: Passed to the base `ExtractionStrategy` initializer.
    *   3.1.4. Key Public Methods:
        *   `extract(self, url: str, html: str, *q, **kwargs) -> List[Dict[str, Any]]`:
            *   Description: Returns the provided `html` content wrapped in a list containing a single dictionary: `[{"index": 0, "content": html}]`.
        *   `run(self, url: str, sections: List[str], *q, **kwargs) -> List[Dict[str, Any]]`:
            *   Description: Returns a list where each input section is wrapped in a dictionary: `[{"index": i, "tags": [], "content": section} for i, section in enumerate(sections)]`.

*   ### 3.2. Class `JsonCssExtractionStrategy`
    *   3.2.1. Purpose: Extracts structured data from HTML content using a JSON schema that defines CSS selectors to locate and extract data for specified fields. It uses BeautifulSoup4 for parsing and selection.
    *   3.2.2. Inheritance: `JsonElementExtractionStrategy` (which inherits from `ExtractionStrategy`)
    *   3.2.3. Initialization (`__init__`):
        *   3.2.3.1. Signature: `JsonCssExtractionStrategy(schema: Dict[str, Any], **kwargs)`
        *   3.2.3.2. Parameters:
            *   `schema (Dict[str, Any])`: The JSON schema defining extraction rules.
            *   `**kwargs`: Passed to the base class initializer. Includes `input_format` (default: "html").
    *   3.2.4. Schema Definition for `JsonCssExtractionStrategy`:
        *   3.2.4.1. `name (str)`: A descriptive name for the schema (e.g., "ProductDetails").
        *   3.2.4.2. `baseSelector (str)`: The primary CSS selector that identifies each root element representing an item to be extracted (e.g., "div.product-item").
        *   3.2.4.3. `fields (List[Dict[str, Any]])`: A list of dictionaries, each defining a field to be extracted from within each `baseSelector` element.
            *   Each field dictionary:
                *   `name (str)`: The key for this field in the output JSON object.
                *   `selector (str)`: The CSS selector for this field, relative to its parent element (either the `baseSelector` or a parent "nested" field).
                *   `type (str)`: Specifies how to extract the data. Common values:
                    *   `"text"`: Extracts the text content of the selected element.
                    *   `"attribute"`: Extracts the value of a specified HTML attribute.
                    *   `"html"`: Extracts the raw inner HTML of the selected element.
                    *   `"list"`: Extracts a list of items. The `fields` sub-key then defines the structure of each item in the list (if objects) or the `selector` directly targets list elements for primitive values.
                    *   `"nested"`: Extracts a nested JSON object. The `fields` sub-key defines the structure of this nested object.
                *   `attribute (str, Optional)`: Required if `type` is "attribute". Specifies the name of the HTML attribute to extract (e.g., "href", "src").
                *   `fields (List[Dict[str, Any]], Optional)`: Required if `type` is "list" (for a list of objects) or "nested". Defines the structure of the nested object or list items.
                *   `transform (str, Optional)`: A string indicating a transformation to apply to the extracted value (e.g., "lowercase", "uppercase", "strip").
                *   `default (Any, Optional)`: A default value to use if the selector does not find an element or the attribute is missing.
    *   3.2.5. Key Public Methods:
        *   `extract(self, url: str, html_content: str, *q, **kwargs) -> List[Dict[str, Any]]`:
            *   Description: Parses the `html_content` and applies the defined schema to extract structured data using CSS selectors.
    *   3.2.6. Features:
        *   3.2.6.1. Nested Extraction: Supports extracting complex, nested JSON objects by defining "nested" type fields within the schema.
        *   3.2.6.2. List Handling: Supports extracting lists of primitive values (e.g., list of strings from multiple `<li>` tags) or lists of structured objects (e.g., a list of product details, each with its own fields).

*   ### 3.3. Class `JsonXPathExtractionStrategy`
    *   3.3.1. Purpose: Extracts structured data from HTML/XML content using a JSON schema that defines XPath expressions to locate and extract data. It uses `lxml` for parsing and XPath evaluation.
    *   3.3.2. Inheritance: `JsonElementExtractionStrategy` (which inherits from `ExtractionStrategy`)
    *   3.3.3. Initialization (`__init__`):
        *   3.3.3.1. Signature: `JsonXPathExtractionStrategy(schema: Dict[str, Any], **kwargs)`
        *   3.3.3.2. Parameters:
            *   `schema (Dict[str, Any])`: The JSON schema defining extraction rules, where selectors are XPath expressions.
            *   `**kwargs`: Passed to the base class initializer. Includes `input_format` (default: "html").
    *   3.3.4. Schema Definition: The schema structure is identical to `JsonCssExtractionStrategy` (see 3.2.4), but the `baseSelector` and field `selector` values must be valid XPath expressions.
    *   3.3.5. Key Public Methods:
        *   `extract(self, url: str, html_content: str, *q, **kwargs) -> List[Dict[str, Any]]`:
            *   Description: Parses the `html_content` using `lxml` and applies the defined schema to extract structured data using XPath expressions.

*   ### 3.4. Class `JsonLxmlExtractionStrategy`
    *   3.4.1. Purpose: Provides an alternative CSS selector-based extraction strategy leveraging the `lxml` library for parsing and selection, which can offer performance benefits over BeautifulSoup4 in some cases.
    *   3.4.2. Inheritance: `JsonCssExtractionStrategy` (and thus `JsonElementExtractionStrategy`, `ExtractionStrategy`)
    *   3.4.3. Initialization (`__init__`):
        *   3.4.3.1. Signature: `JsonLxmlExtractionStrategy(schema: Dict[str, Any], **kwargs)`
        *   3.4.3.2. Parameters:
            *   `schema (Dict[str, Any])`: The JSON schema defining extraction rules, using CSS selectors.
            *   `**kwargs`: Passed to the base class initializer. Includes `input_format` (default: "html").
    *   3.4.4. Schema Definition: Identical to `JsonCssExtractionStrategy` (see 3.2.4).
    *   3.4.5. Key Public Methods:
        *   `extract(self, url: str, html_content: str, *q, **kwargs) -> List[Dict[str, Any]]`:
            *   Description: Parses the `html_content` using `lxml` and applies the defined schema to extract structured data using lxml's CSS selector capabilities (which often translates CSS to XPath internally).

*   ### 3.5. Class `RegexExtractionStrategy`
    *   3.5.1. Purpose: Extracts data from text content (HTML, Markdown, or plain text) using a collection of regular expression patterns. Each match is returned as a structured dictionary.
    *   3.5.2. Inheritance: `ExtractionStrategy`
    *   3.5.3. Initialization (`__init__`):
        *   3.5.3.1. Signature: `RegexExtractionStrategy(patterns: Union[Dict[str, str], List[Tuple[str, str]], "RegexExtractionStrategy._B"] = _B.NOTHING, input_format: str = "fit_html", **kwargs)`
        *   3.5.3.2. Parameters:
            *   `patterns (Union[Dict[str, str], List[Tuple[str, str]], "_B"], default: _B.NOTHING)`:
                *   Description: Defines the regex patterns to use.
                *   Can be a dictionary mapping labels to regex strings (e.g., `{"email": r"..."}`).
                *   Can be a list of (label, regex_string) tuples.
                *   Can be a bitwise OR combination of `RegexExtractionStrategy._B` enum members for using built-in patterns (e.g., `RegexExtractionStrategy.Email | RegexExtractionStrategy.Url`).
            *   `input_format (str, default: "fit_html")`: Specifies the input format for the content. Options: "html" (raw HTML), "markdown" (Markdown from HTML), "text" (plain text from HTML), "fit_html" (content filtered for relevance before regex application).
            *   `**kwargs`: Passed to the base `ExtractionStrategy`.
    *   3.5.4. Built-in Patterns (`RegexExtractionStrategy._B` Enum - an `IntFlag`):
        *   `EMAIL (auto())`: Matches email addresses. Example pattern: `r"[\\w.+-]+@[\\w-]+\\.[\\w.-]+"`
        *   `PHONE_INTL (auto())`: Matches international phone numbers. Example pattern: `r"\\+?\\d[\\d .()-]{7,}\\d"`
        *   `PHONE_US (auto())`: Matches US phone numbers. Example pattern: `r"\\(?\\d{3}\\)?[-. ]?\\d{3}[-. ]?\\d{4}"`
        *   `URL (auto())`: Matches URLs. Example pattern: `r"https?://[^\\s\\'\"<>]+"`
        *   `IPV4 (auto())`: Matches IPv4 addresses. Example pattern: `r"(?:\\d{1,3}\\.){3}\\d{1,3}"`
        *   `IPV6 (auto())`: Matches IPv6 addresses. Example pattern: `r"[A-F0-9]{1,4}(?::[A-F0-9]{1,4}){7}"`
        *   `UUID (auto())`: Matches UUIDs. Example pattern: `r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"`
        *   `CURRENCY (auto())`: Matches currency amounts. Example pattern: `r"(?:USD|EUR|RM|\\$|€|¥|£)\\s?\\d+(?:[.,]\\d{2})?"`
        *   `PERCENTAGE (auto())`: Matches percentages. Example pattern: `r"\\d+(?:\\.\\d+)?%"`
        *   `NUMBER (auto())`: Matches numbers (integers, decimals). Example pattern: `r"\\b\\d{1,3}(?:[,.]?\\d{3})*(?:\\.\\d+)?\\b"`
        *   `DATE_ISO (auto())`: Matches ISO 8601 dates (YYYY-MM-DD). Example pattern: `r"\\d{4}-\\d{2}-\\d{2}"`
        *   `DATE_US (auto())`: Matches US-style dates (MM/DD/YYYY or MM/DD/YY). Example pattern: `r"\\d{1,2}/\\d{1,2}/\\d{2,4}"`
        *   `TIME_24H (auto())`: Matches 24-hour time formats (HH:MM or HH:MM:SS). Example pattern: `r"\\b(?:[01]?\\d|2[0-3]):[0-5]\\d(?:[:.][0-5]\\d)?\\b"`
        *   `POSTAL_US (auto())`: Matches US postal codes (ZIP codes). Example pattern: `r"\\b\\d{5}(?:-\\d{4})?\\b"`
        *   `POSTAL_UK (auto())`: Matches UK postal codes. Example pattern: `r"\\b[A-Z]{1,2}\\d[A-Z\\d]? ?\\d[A-Z]{2}\\b"`
        *   `HTML_COLOR_HEX (auto())`: Matches HTML hex color codes. Example pattern: `r"#[0-9A-Fa-f]{6}\\b"`
        *   `TWITTER_HANDLE (auto())`: Matches Twitter handles. Example pattern: `r"@[\\w]{1,15}"`
        *   `HASHTAG (auto())`: Matches hashtags. Example pattern: `r"#[\\w-]+"`
        *   `MAC_ADDR (auto())`: Matches MAC addresses. Example pattern: `r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}"`
        *   `IBAN (auto())`: Matches IBANs. Example pattern: `r"[A-Z]{2}\\d{2}[A-Z0-9]{11,30}"`
        *   `CREDIT_CARD (auto())`: Matches common credit card numbers. Example pattern: `r"\\b(?:4\\d{12}(?:\\d{3})?|5[1-5]\\d{14}|3[47]\\d{13}|6(?:011|5\\d{2})\\d{12})\\b"`
        *   `ALL (_B(-1).value & ~_B.NOTHING.value)`: Includes all built-in patterns except `NOTHING`.
        *   `NOTHING (_B(0).value)`: Includes no built-in patterns.
    *   3.5.5. Key Public Methods:
        *   `extract(self, url: str, content: str, **kwargs) -> List[Dict[str, Any]]`:
            *   Description: Applies all configured regex patterns (built-in and custom) to the input `content`.
            *   Returns: `List[Dict[str, Any]]` - A list of dictionaries, where each dictionary represents a match and contains:
                *   `"url" (str)`: The source URL.
                *   `"label" (str)`: The label of the matching regex pattern.
                *   `"value" (str)`: The actual matched string.
                *   `"span" (Tuple[int, int])`: The start and end indices of the match within the content.
    *   3.5.6. Static Method: `generate_pattern`
        *   3.5.6.1. Signature: `staticmethod generate_pattern(label: str, html: str, query: Optional[str] = None, examples: Optional[List[str]] = None, llm_config: Optional[LLMConfig] = None, **kwargs) -> Dict[str, str]`
        *   3.5.6.2. Purpose: Uses an LLM to automatically generate a Python-compatible regular expression pattern for a given label, based on sample HTML content, an optional natural language query describing the target, and/or examples of desired matches.
        *   3.5.6.3. Parameters:
            *   `label (str)`: A descriptive label for the pattern to be generated (e.g., "product_price", "article_date").
            *   `html (str)`: The HTML content from which the pattern should be inferred.
            *   `query (Optional[str], default: None)`: A natural language description of what kind of data the regex should capture (e.g., "Extract the publication date", "Find all ISBN numbers").
            *   `examples (Optional[List[str]], default: None)`: A list of example strings that the generated regex should successfully match from the provided HTML.
            *   `llm_config (Optional[LLMConfig], default: None)`: Configuration for the LLM to be used. If `None`, uses default `LLMConfig`.
            *   `**kwargs`: Additional arguments passed to the LLM completion request (e.g., `temperature`, `max_tokens`).
        *   3.5.6.4. Returns: `Dict[str, str]` - A dictionary containing the generated pattern, in the format `{label: "regex_pattern_string"}`.

## 4. LLM-Based Extraction Strategies

*   ### 4.1. Class `LLMExtractionStrategy`
    *   4.1.1. Purpose: Employs Large Language Models (LLMs) to extract either structured data according to a schema or relevant blocks of text based on natural language instructions from various content formats (HTML, Markdown, text).
    *   4.1.2. Inheritance: `ExtractionStrategy`
    *   4.1.3. Initialization (`__init__`):
        *   4.1.3.1. Signature: `LLMExtractionStrategy(llm_config: Optional[LLMConfig] = None, instruction: Optional[str] = None, schema: Optional[Union[Dict[str, Any], "BaseModel"]] = None, extraction_type: str = "block", chunk_token_threshold: int = CHUNK_TOKEN_THRESHOLD, overlap_rate: float = OVERLAP_RATE, word_token_rate: float = WORD_TOKEN_RATE, apply_chunking: bool = True, force_json_response: bool = False, **kwargs)`
        *   4.1.3.2. Parameters:
            *   `llm_config (Optional[LLMConfig], default: None)`: Configuration for the LLM. If `None`, a default `LLMConfig` is created.
            *   `instruction (Optional[str], default: None)`: Natural language instructions to guide the LLM's extraction process (e.g., "Extract the main article content", "Summarize the key points").
            *   `schema (Optional[Union[Dict[str, Any], "BaseModel"]], default: None)`: A Pydantic model class or a dictionary representing a JSON schema. Used when `extraction_type` is "schema" to define the desired output structure.
            *   `extraction_type (str, default: "block")`: Determines the extraction mode.
                *   `"block"`: LLM identifies and extracts relevant blocks/chunks of text based on the `instruction`.
                *   `"schema"`: LLM attempts to populate the fields defined in `schema` from the content.
            *   `chunk_token_threshold (int, default: CHUNK_TOKEN_THRESHOLD)`: The target maximum number of tokens for each chunk of content sent to the LLM. `CHUNK_TOKEN_THRESHOLD` is defined in `crawl4ai.config` (default value: 10000).
            *   `overlap_rate (float, default: OVERLAP_RATE)`: The percentage of overlap between consecutive chunks to ensure context continuity. `OVERLAP_RATE` is defined in `crawl4ai.config` (default value: 0.1, i.e., 10%).
            *   `word_token_rate (float, default: WORD_TOKEN_RATE)`: An estimated ratio of words to tokens (e.g., 0.75 words per token). Used for approximating chunk boundaries. `WORD_TOKEN_RATE` is defined in `crawl4ai.config` (default value: 0.75).
            *   `apply_chunking (bool, default: True)`: If `True`, the input content is chunked before being sent to the LLM. If `False`, the entire content is sent (which might exceed token limits for large inputs).
            *   `force_json_response (bool, default: False)`: If `True` and `extraction_type` is "schema", instructs the LLM to strictly adhere to JSON output format.
            *   `**kwargs`: Passed to `ExtractionStrategy` and potentially to the underlying LLM API calls (e.g., `temperature`, `max_tokens` if not set in `llm_config`).
    *   4.1.4. Key Public Methods:
        *   `extract(self, url: str, content: str, *q, **kwargs) -> List[Dict[str, Any]]`:
            *   Description: Processes the input `content`. If `apply_chunking` is `True`, it first chunks the content using the specified `chunking_strategy` (or a default one if `LLMExtractionStrategy` manages it internally). Then, for each chunk (or the whole content if not chunked), it constructs a prompt based on `instruction` and/or `schema` and sends it to the configured LLM.
            *   Returns: `List[Dict[str, Any]]` - A list of dictionaries.
                *   If `extraction_type` is "block", each dictionary typically contains `{"index": int, "content": str, "tags": List[str]}`.
                *   If `extraction_type` is "schema", each dictionary is an instance of the extracted structured data, ideally conforming to the provided `schema`. If the LLM returns multiple JSON objects in a list, they are parsed and returned.
        *   `run(self, url: str, sections: List[str], *q, **kwargs) -> List[Dict[str, Any]]`:
            *   Description: Processes a list of content `sections` in parallel (using `ThreadPoolExecutor`). Each section is passed to the `extract` method logic.
            *   Returns: `List[Dict[str, Any]]` - Aggregated list of results from processing all sections.
    *   4.1.5. `TokenUsage` Tracking:
        *   `total_usage (TokenUsage)`: [Read-only Public Attribute] - An instance of `TokenUsage` that accumulates the token counts (prompt, completion, total) from all LLM API calls made by this `LLMExtractionStrategy` instance.
        *   `usages (List[TokenUsage])`: [Read-only Public Attribute] - A list containing individual `TokenUsage` objects for each separate LLM API call made during the extraction process. This allows for detailed tracking of token consumption per call.

## 5. `ChunkingStrategy` Interface and Implementations

*   ### 5.1. Interface `ChunkingStrategy`
    *   5.1.1. Purpose: The `ChunkingStrategy` class, found in `crawl4ai.chunking_strategy`, is an abstract base class (ABC) that defines the interface for different content chunking algorithms. Chunking is used to break down large pieces of text or HTML into smaller, manageable segments, often before feeding them to an LLM or other processing steps.
    *   5.1.2. Key Abstract Methods:
        *   `chunk(self, content: str) -> List[str]`:
            *   Description: Abstract method that must be implemented by subclasses to split the input `content` string into a list of string chunks.
            *   Parameters:
                *   `content (str)`: The content to be chunked.
            *   Returns: `List[str]` - A list of content chunks.

*   ### 5.2. Class `RegexChunking`
    *   5.2.1. Purpose: Implements `ChunkingStrategy` by splitting content based on a list of regular expression patterns. It can also attempt to merge smaller chunks to meet a target `chunk_size`.
    *   5.2.2. Inheritance: `ChunkingStrategy`
    *   5.2.3. Initialization (`__init__`):
        *   5.2.3.1. Signature: `RegexChunking(patterns: Optional[List[str]] = None, chunk_size: Optional[int] = None, overlap: Optional[int] = None, word_token_ratio: Optional[float] = WORD_TOKEN_RATE, **kwargs)`
        *   5.2.3.2. Parameters:
            *   `patterns (Optional[List[str]], default: None)`: A list of regex patterns used to split the text. If `None`, defaults to paragraph-based splitting (`["\\n\\n+"]`).
            *   `chunk_size (Optional[int], default: None)`: The target token size for each chunk. If specified, the strategy will try to merge smaller chunks created by regex splitting to approximate this size.
            *   `overlap (Optional[int], default: None)`: The target token overlap between consecutive chunks when `chunk_size` is active.
            *   `word_token_ratio (Optional[float], default: WORD_TOKEN_RATE)`: The estimated ratio of words to tokens, used if `chunk_size` or `overlap` are specified. `WORD_TOKEN_RATE` is defined in `crawl4ai.config` (default value: 0.75).
            *   `**kwargs`: Additional keyword arguments.
    *   5.2.4. Key Public Methods:
        *   `chunk(self, content: str) -> List[str]`:
            *   Description: Splits the input `content` using the configured regex patterns. If `chunk_size` is set, it then merges these initial chunks to meet the target size with the specified overlap.

*   ### 5.3. Class `IdentityChunking`
    *   5.3.1. Purpose: A `ChunkingStrategy` that does not perform any actual chunking. It returns the input content as a single chunk in a list.
    *   5.3.2. Inheritance: `ChunkingStrategy`
    *   5.3.3. Initialization (`__init__`):
        *   5.3.3.1. Signature: `IdentityChunking(**kwargs)`
        *   5.3.3.2. Parameters:
            *   `**kwargs`: Additional keyword arguments.
    *   5.3.4. Key Public Methods:
        *   `chunk(self, content: str) -> List[str]`:
            *   Description: Returns the input `content` as a single-element list: `[content]`.

## 6. Defining Schemas for Extraction

*   6.1. Purpose: Schemas provide a structured way to define what data needs to be extracted from content and how it should be organized. This allows for consistent and predictable output from the extraction process.
*   6.2. Schemas for CSS/XPath/LXML-based Extraction (`JsonCssExtractionStrategy`, etc.):
    *   6.2.1. Format: These strategies use a dictionary-based JSON-like schema.
    *   6.2.2. Key elements: As detailed in section 3.2.4 for `JsonCssExtractionStrategy`:
        *   `name (str)`: Name of the schema.
        *   `baseSelector (str)`: CSS selector (for CSS strategies) or XPath expression (for XPath strategy) identifying the repeating parent elements.
        *   `fields (List[Dict[str, Any]])`: A list defining each field to extract. Each field definition includes:
            *   `name (str)`: Output key for the field.
            *   `selector (str)`: CSS/XPath selector relative to the `baseSelector` or parent "nested" element.
            *   `type (str)`: "text", "attribute", "html", "list", "nested".
            *   `attribute (str, Optional)`: Name of HTML attribute (if type is "attribute").
            *   `fields (List[Dict], Optional)`: For "list" (of objects) or "nested" types.
            *   `transform (str, Optional)`: e.g., "lowercase".
            *   `default (Any, Optional)`: Default value if not found.
*   6.3. Schemas for LLM-based Extraction (`LLMExtractionStrategy`):
    *   6.3.1. Format: `LLMExtractionStrategy` accepts schemas in two main formats when `extraction_type="schema"`:
        *   Pydantic models: The Pydantic model class itself.
        *   Dictionary: A Python dictionary representing a valid JSON schema.
    *   6.3.2. Pydantic Models:
        *   Definition: Users can define a Pydantic `BaseModel` where each field represents a piece of data to be extracted. Field types and descriptions are automatically inferred.
        *   Conversion: `LLMExtractionStrategy` internally converts the Pydantic model to its JSON schema representation (`model_json_schema()`) to guide the LLM.
    *   6.3.3. Dictionary-based JSON Schema:
        *   Structure: Users can provide a dictionary that conforms to the JSON Schema specification. This typically includes a `type: "object"` at the root and a `properties` dictionary defining each field, its type (e.g., "string", "number", "array", "object"), and optionally a `description`.
        *   Usage: This schema is passed to the LLM to instruct it on the desired output format.

## 7. Configuration with `CrawlerRunConfig`

*   7.1. Purpose: The `CrawlerRunConfig` class (from `crawl4ai.async_configs`) is used to configure the behavior of a specific `arun()` or `arun_many()` call on an `AsyncWebCrawler` instance. It allows specifying various runtime parameters, including the extraction and chunking strategies.
*   7.2. Key Attributes:
    *   `extraction_strategy (Optional[ExtractionStrategy], default: None)`:
        *   Purpose: Specifies the `ExtractionStrategy` instance to be used for processing the content obtained during the crawl. If `None`, no structured extraction beyond basic Markdown generation occurs (unless a default is applied by the crawler).
        *   Type: An instance of a class inheriting from `ExtractionStrategy`.
    *   `chunking_strategy (Optional[ChunkingStrategy], default: RegexChunking())`:
        *   Purpose: Specifies the `ChunkingStrategy` instance to be used for breaking down content into smaller pieces before it's passed to an `ExtractionStrategy` (particularly `LLMExtractionStrategy`).
        *   Type: An instance of a class inheriting from `ChunkingStrategy`.
        *   Default: An instance of `RegexChunking()` with its default parameters (paragraph-based splitting).

## 8. LLM-Specific Configuration and Models

*   ### 8.1. Class `LLMConfig`
    *   8.1.1. Purpose: The `LLMConfig` class (from `crawl4ai.async_configs`) centralizes configuration parameters for interacting with Large Language Models (LLMs) through various providers.
    *   8.1.2. Initialization (`__init__`):
        *   8.1.2.1. Signature:
            ```python
            class LLMConfig:
                def __init__(
                    self,
                    provider: str = DEFAULT_PROVIDER,
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
        *   8.1.2.2. Parameters:
            *   `provider (str, default: DEFAULT_PROVIDER)`: Specifies the LLM provider and model, e.g., "openai/gpt-4o-mini", "ollama/llama3.3". `DEFAULT_PROVIDER` is "openai/gpt-4o-mini".
            *   `api_token (Optional[str], default: None)`: API token for the LLM provider. If `None`, the system attempts to read it from environment variables (e.g., `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY` based on provider). Can also be prefixed with "env:" (e.g., "env:MY_CUSTOM_LLM_KEY").
            *   `base_url (Optional[str], default: None)`: Custom base URL for the LLM API endpoint, for self-hosted or alternative provider endpoints.
            *   `temperature (Optional[float], default: None)`: Controls randomness in LLM generation. Higher values (e.g., 0.8) make output more random, lower (e.g., 0.2) more deterministic.
            *   `max_tokens (Optional[int], default: None)`: Maximum number of tokens the LLM should generate in its response.
            *   `top_p (Optional[float], default: None)`: Nucleus sampling parameter. An alternative to temperature; controls the cumulative probability mass of tokens considered for generation.
            *   `frequency_penalty (Optional[float], default: None)`: Penalizes new tokens based on their existing frequency in the text so far, decreasing repetition.
            *   `presence_penalty (Optional[float], default: None)`: Penalizes new tokens based on whether they have appeared in the text so far, encouraging new topics.
            *   `stop (Optional[List[str]], default: None)`: A list of sequences where the API will stop generating further tokens.
            *   `n (Optional[int], default: None)`: Number of completions to generate for each prompt.
    *   8.1.3. Helper Methods:
        *   `from_kwargs(kwargs: dict) -> LLMConfig`:
            *   Description: [Static method] Creates an `LLMConfig` instance from a dictionary of keyword arguments.
        *   `to_dict() -> dict`:
            *   Description: Converts the `LLMConfig` instance into a dictionary representation.
        *   `clone(**kwargs) -> LLMConfig`:
            *   Description: Creates a new `LLMConfig` instance as a copy of the current one, allowing specific attributes to be overridden with `kwargs`.

*   ### 8.2. Dataclass `TokenUsage`
    *   8.2.1. Purpose: The `TokenUsage` dataclass (from `crawl4ai.models`) is used to store information about the number of tokens consumed during an LLM API call.
    *   8.2.2. Fields:
        *   `completion_tokens (int, default: 0)`: The number of tokens generated by the LLM in the completion.
        *   `prompt_tokens (int, default: 0)`: The number of tokens in the prompt sent to the LLM.
        *   `total_tokens (int, default: 0)`: The sum of `completion_tokens` and `prompt_tokens`.
        *   `completion_tokens_details (Optional[dict], default: None)`: Provider-specific detailed breakdown of completion tokens, if available.
        *   `prompt_tokens_details (Optional[dict], default: None)`: Provider-specific detailed breakdown of prompt tokens, if available.

## 9. PDF Processing and Extraction

*   ### 9.1. Overview of PDF Processing
    *   9.1.1. Purpose: Crawl4ai provides specialized strategies to handle PDF documents, enabling the fetching of PDF content and subsequent extraction of text, images, and metadata. This allows PDFs to be treated as a primary content source similar to HTML web pages.
    *   9.1.2. Key Components:
        *   `PDFCrawlerStrategy`: For fetching/identifying PDF content.
        *   `PDFContentScrapingStrategy`: For processing PDF content using an underlying PDF processor.
        *   `NaivePDFProcessorStrategy`: The default logic for parsing PDF files.

*   ### 9.2. Class `PDFCrawlerStrategy`
    *   9.2.1. Purpose: An implementation of `AsyncCrawlerStrategy` specifically for handling PDF documents. It doesn't perform typical browser interactions but focuses on fetching PDF content and setting the appropriate response headers to indicate a PDF document, which then allows `PDFContentScrapingStrategy` to process it.
    *   9.2.2. Inheritance: `AsyncCrawlerStrategy` (from `crawl4ai.async_crawler_strategy`)
    *   9.2.3. Initialization (`__init__`):
        *   9.2.3.1. Signature: `PDFCrawlerStrategy(logger: Optional[AsyncLogger] = None)`
        *   9.2.3.2. Parameters:
            *   `logger (Optional[AsyncLogger], default: None)`: An optional logger instance for logging messages.
    *   9.2.4. Key Public Methods:
        *   `crawl(self, url: str, **kwargs) -> AsyncCrawlResponse`:
            *   Description: Fetches the content from the given `url`. If the content is identified as a PDF (either by URL extension or `Content-Type` header for remote URLs), it sets `response_headers={"Content-Type": "application/pdf"}` in the returned `AsyncCrawlResponse`. The `html` field of the response will contain a placeholder message as the actual PDF processing happens in the scraping strategy.
        *   `close(self) -> None`:
            *   Description: Placeholder for cleanup, typically does nothing in this strategy.
        *   `__aenter__(self) -> "PDFCrawlerStrategy"`:
            *   Description: Async context manager entry point.
        *   `__aexit__(self, exc_type, exc_val, exc_tb) -> None`:
            *   Description: Async context manager exit point, calls `close()`.

*   ### 9.3. Class `PDFContentScrapingStrategy`
    *   9.3.1. Purpose: An implementation of `ContentScrapingStrategy` designed to process PDF documents. It uses an underlying `PDFProcessorStrategy` (by default, `NaivePDFProcessorStrategy`) to extract text, images, and metadata from the PDF, then formats this information into a `ScrapingResult`.
    *   9.3.2. Inheritance: `ContentScrapingStrategy` (from `crawl4ai.content_scraping_strategy`)
    *   9.3.3. Initialization (`__init__`):
        *   9.3.3.1. Signature: `PDFContentScrapingStrategy(save_images_locally: bool = False, extract_images: bool = False, image_save_dir: Optional[str] = None, batch_size: int = 4, logger: Optional[AsyncLogger] = None)`
        *   9.3.3.2. Parameters:
            *   `save_images_locally (bool, default: False)`: If `True`, extracted images will be saved to the local filesystem.
            *   `extract_images (bool, default: False)`: If `True`, the strategy will attempt to extract images from the PDF.
            *   `image_save_dir (Optional[str], default: None)`: The directory where extracted images will be saved if `save_images_locally` is `True`. If `None`, a default or temporary directory might be used.
            *   `batch_size (int, default: 4)`: The number of PDF pages to process in parallel by the underlying `NaivePDFProcessorStrategy`.
            *   `logger (Optional[AsyncLogger], default: None)`: An optional logger instance.
    *   9.3.4. Key Attributes:
        *   `pdf_processor (NaivePDFProcessorStrategy)`: An instance of `NaivePDFProcessorStrategy` configured with the provided image and batch settings, used to do the actual PDF parsing.
    *   9.3.5. Key Public Methods:
        *   `scrape(self, url: str, html: str, **params) -> ScrapingResult`:
            *   Description: Takes a `url` (which can be a local file path or a remote HTTP/HTTPS URL pointing to a PDF) and processes it. The `html` parameter is typically a placeholder like "Scraper will handle the real work" as the content comes from the PDF file itself. It downloads remote PDFs to a temporary local file before processing.
            *   Returns: `ScrapingResult` containing the extracted PDF data, including `cleaned_html` (concatenated HTML of pages), `media` (extracted images), `links`, and `metadata`.
        *   `ascrape(self, url: str, html: str, **kwargs) -> ScrapingResult`:
            *   Description: Asynchronous version of `scrape`. Internally calls `scrape` using `asyncio.to_thread`.
    *   9.3.6. Internal Methods (Conceptual):
        *   `_get_pdf_path(self, url: str) -> str`:
            *   Description: If `url` is an HTTP/HTTPS URL, downloads the PDF to a temporary file and returns its path. If `url` starts with "file://", it strips the prefix and returns the local path. Otherwise, assumes `url` is already a local path. Handles download timeouts and errors.

*   ### 9.4. Class `NaivePDFProcessorStrategy`
    *   9.4.1. Purpose: The default implementation of `PDFProcessorStrategy` in Crawl4ai. It uses the PyPDF2 library (and Pillow for image processing) to parse PDF files, extract text content page by page, attempt to extract embedded images, and gather document metadata.
    *   9.4.2. Inheritance: `PDFProcessorStrategy` (from `crawl4ai.processors.pdf.processor`)
    *   9.4.3. Dependencies: Requires `PyPDF2` and `Pillow`. These are installed with the `crawl4ai[pdf]` extra.
    *   9.4.4. Initialization (`__init__`):
        *   9.4.4.1. Signature: `NaivePDFProcessorStrategy(image_dpi: int = 144, image_quality: int = 85, extract_images: bool = True, save_images_locally: bool = False, image_save_dir: Optional[Path] = None, batch_size: int = 4)`
        *   9.4.4.2. Parameters:
            *   `image_dpi (int, default: 144)`: DPI used when rendering PDF pages to images (if direct image extraction is not possible or disabled).
            *   `image_quality (int, default: 85)`: Quality setting (1-100) for images saved in lossy formats like JPEG.
            *   `extract_images (bool, default: True)`: If `True`, attempts to extract embedded images directly from the PDF's XObjects.
            *   `save_images_locally (bool, default: False)`: If `True`, extracted images are saved to disk. Otherwise, they are base64 encoded and returned in the `PDFPage.images` data.
            *   `image_save_dir (Optional[Path], default: None)`: If `save_images_locally` is True, this specifies the directory to save images. If `None`, a temporary directory (prefixed `pdf_images_`) is created and used.
            *   `batch_size (int, default: 4)`: The number of pages to process in parallel when using the `process_batch` method.
    *   9.4.5. Key Public Methods:
        *   `process(self, pdf_path: Path) -> PDFProcessResult`:
            *   Description: Processes the PDF specified by `pdf_path` page by page sequentially.
            *   Returns: `PDFProcessResult` containing metadata and a list of `PDFPage` objects.
        *   `process_batch(self, pdf_path: Path) -> PDFProcessResult`:
            *   Description: Processes the PDF specified by `pdf_path` by handling pages in parallel batches using a `ThreadPoolExecutor` with `max_workers` set to `batch_size`.
            *   Returns: `PDFProcessResult` containing metadata and a list of `PDFPage` objects, assembled in the correct page order.
    *   9.4.6. Internal Methods (Conceptual High-Level):
        *   `_process_page(self, page: PyPDF2PageObject, image_dir: Optional[Path]) -> PDFPage`: Extracts text, images (if `extract_images` is True), and links from a single PyPDF2 page object.
        *   `_extract_images(self, page: PyPDF2PageObject, image_dir: Optional[Path]) -> List[Dict]`: Iterates through XObjects on a page, identifies images, decodes them (handling FlateDecode, DCTDecode, CCITTFaxDecode, JPXDecode), and either saves them locally or base64 encodes them.
        *   `_extract_links(self, page: PyPDF2PageObject) -> List[str]`: Extracts URI actions from page annotations to get hyperlinks.
        *   `_extract_metadata(self, pdf_path: Path, reader: PyPDF2PdfReader) -> PDFMetadata`: Reads metadata from the PDF document information dictionary (e.g., /Title, /Author, /CreationDate).

*   ### 9.5. Data Models for PDF Processing
    *   9.5.1. Dataclass `PDFMetadata` (from `crawl4ai.processors.pdf.processor`)
        *   Fields:
            *   `title (Optional[str], default: None)`
            *   `author (Optional[str], default: None)`
            *   `producer (Optional[str], default: None)`
            *   `created (Optional[datetime], default: None)`
            *   `modified (Optional[datetime], default: None)`
            *   `pages (int, default: 0)`
            *   `encrypted (bool, default: False)`
            *   `file_size (Optional[int], default: None)`
    *   9.5.2. Dataclass `PDFPage` (from `crawl4ai.processors.pdf.processor`)
        *   Fields:
            *   `page_number (int)`
            *   `raw_text (str, default: "")`
            *   `markdown (str, default: "")`: Markdown representation of the page's text content, processed by `clean_pdf_text`.
            *   `html (str, default: "")`: HTML representation of the page's text content, processed by `clean_pdf_text_to_html`.
            *   `images (List[Dict], default_factory: list)`: List of image dictionaries. Each dictionary contains:
                *   `format (str)`: e.g., "png", "jpeg", "tiff", "jp2", "bin".
                *   `width (int)`
                *   `height (int)`
                *   `color_space (str)`: e.g., "/DeviceRGB", "/DeviceGray".
                *   `bits_per_component (int)`
                *   `path (str, Optional)`: If `save_images_locally` was True, path to the saved image file.
                *   `data (str, Optional)`: If `save_images_locally` was False, base64 encoded image data.
                *   `page (int)`: The page number this image was extracted from.
            *   `links (List[str], default_factory: list)`: List of hyperlink URLs found on the page.
            *   `layout (List[Dict], default_factory: list)`: List of dictionaries representing text layout elements, primarily: `{"type": "text", "text": str, "x": float, "y": float}`.
    *   9.5.3. Dataclass `PDFProcessResult` (from `crawl4ai.processors.pdf.processor`)
        *   Fields:
            *   `metadata (PDFMetadata)`
            *   `pages (List[PDFPage])`
            *   `processing_time (float, default: 0.0)`: Time in seconds taken to process the PDF.
            *   `version (str, default: "1.1")`: Version of the PDF processor strategy (e.g., "1.1" for current `NaivePDFProcessorStrategy`).

*   ### 9.6. Using PDF Strategies with `AsyncWebCrawler`
    *   9.6.1. Workflow:
        1.  Instantiate `AsyncWebCrawler`. The `crawler_strategy` parameter of `AsyncWebCrawler` should be set to an instance of `PDFCrawlerStrategy` if you intend to primarily crawl PDF URLs or local PDF files directly. If crawling mixed content where PDFs are discovered via links on HTML pages, the default `AsyncPlaywrightCrawlerStrategy` might be used initially, and then a PDF-specific scraping strategy would be applied when a PDF content type is detected.
        2.  In `CrawlerRunConfig`, set the `scraping_strategy` attribute to an instance of `PDFContentScrapingStrategy`. Configure this strategy with desired options like `extract_images`, `save_images_locally`, etc.
        3.  When `crawler.arun(url="path/to/document.pdf", config=run_config)` is called for a PDF URL or local file path:
            *   `PDFCrawlerStrategy` (if used) or the default crawler strategy fetches the file.
            *   `PDFContentScrapingStrategy.scrape()` is invoked. It uses its internal `NaivePDFProcessorStrategy` instance to parse the PDF.
            *   The extracted text, image data, and metadata are populated into the `CrawlResult` object (e.g., `result.markdown`, `result.media["images"]`, `result.metadata`).
    *   9.6.2. Example Snippet:
        ```python
        import asyncio
        from pathlib import Path
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, PDFCrawlerStrategy
        from crawl4ai.content_scraping_strategy import PDFContentScrapingStrategy
        from crawl4ai.processors.pdf import PDFContentScrapingStrategy # Corrected import path

        async def main():
            # Setup for PDF processing
            pdf_crawler_strategy = PDFCrawlerStrategy() # Use if directly targeting PDF URLs
            pdf_scraping_strategy = PDFContentScrapingStrategy(
                extract_images=True,
                save_images_locally=True,
                image_save_dir="./pdf_images_output" # Ensure this directory exists
            )
            Path("./pdf_images_output").mkdir(parents=True, exist_ok=True)

            # If crawling a website that links to PDFs, you might use the default crawler strategy
            # and rely on content-type detection to switch to PDFContentScrapingStrategy if needed.
            # For direct PDF URL:
            async with AsyncWebCrawler(crawler_strategy=pdf_crawler_strategy) as crawler:
                run_config = CrawlerRunConfig(scraping_strategy=pdf_scraping_strategy)
                # Example PDF URL (replace with a real one for testing)
                pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
                result = await crawler.arun(url=pdf_url, config=run_config)

                if result.success:
                    print(f"Successfully processed PDF: {result.url}")
                    if result.markdown:
                         print(f"Markdown content (first 500 chars): {result.markdown.raw_markdown[:500]}")
                    if result.media and result.media.images:
                        print(f"Extracted {len(result.media.images)} images.")
                        for img in result.media.images:
                            print(f"  - Image source/path: {img.src or img.path}, Page: {img.page}")
                    if result.metadata:
                        print(f"PDF Metadata: {result.metadata}")
                else:
                    print(f"Failed to process PDF: {result.url}, Error: {result.error_message}")

        # if __name__ == "__main__":
        #     asyncio.run(main())
        ```
```

---


## Data Extraction - Reasoning
Source: crawl4ai_extraction_reasoning_content.llm.md

Okay, I'm ready to generate the "Reasoning & Problem-Solving Framework" document for the `extraction` component, adhering strictly to the outline you provided and the principles for a "reasoning" document.

I will use the information from the previously shared code snippets and documentation to create illustrative examples, explain design rationale, and provide actionable advice.

Here is the `llm_reasoning_extraction.md` document:

```markdown
# Detailed Outline for crawl4ai - extraction Component

**Target Document Type:** reasoning
**Target Output Filename Suggestion:** `llm_reasoning_extraction.md`
**Library Version Context:** 0.6.0+ (based on provided code)
**Outline Generation Date:** 2024-05-24
---

# Mastering Data Extraction with Crawl4AI

## 1. Introduction: Why Structured Data Extraction Matters in Web Crawling
    * 1.1. The Value of Going Beyond Raw HTML: Turning Web Content into Actionable Data
        Web pages, in their raw HTML form, are designed for human consumption. While Crawl4AI excels at converting HTML to clean Markdown for LLMs, often the goal is to extract specific, structured pieces of information. This could be product prices, article headlines, author names, contact details, or any other data points that can be organized into a predictable format. Structured data is more readily usable for databases, APIs, analytics, training machine learning models, or feeding into other automated processes. Simply having the full HTML or Markdown isn't enough when you need to operate on discrete data fields.

    * 1.2. Common Challenges in Web Data Extraction (Dynamic content, varied structures, anti-scraping)
        Extracting data from the web isn't always straightforward. Common hurdles include:
        *   **Varied HTML Structures:** Websites change layouts, and even within a single site, different page types can have vastly different structures. A CSS selector that works today might break tomorrow.
        *   **Dynamic Content:** Much of the web's content is loaded via JavaScript after the initial HTML page. Extractors need to handle this, either by executing JS (as Crawl4AI's browser-based crawlers do) or by finding data in embedded JSON within `<script>` tags.
        *   **Anti-Scraping Measures:** Websites may employ techniques to deter or block automated scraping, requiring more sophisticated approaches.
        *   **Unstructured Data:** Sometimes, the data isn't neatly tagged. It might be buried in free-form text, requiring natural language understanding to identify and extract.
        *   **Scalability and Maintenance:** Writing and maintaining custom parsers for many sites can be a significant engineering effort.

    * 1.3. Crawl4AI's Approach: A Flexible, Strategy-Based Extraction Framework
        Crawl4AI tackles these challenges by offering a flexible and powerful extraction framework built around the concept of "strategies." This allows you to choose the best tool for the job, whether it's precise rule-based extraction or intelligent LLM-powered parsing.
        *   **`ExtractionStrategy` Interface:** This is the core. It defines a common contract for how extraction should happen. Crawl4AI provides several built-in strategies (CSS-based, XPath-based, Regex-based, LLM-based), and you can even implement your own for highly specialized needs. This promotes modularity – you can swap out extraction logic without changing your core crawling code.
        *   **`ChunkingStrategy` Interface:** Specifically for LLM-based extraction, this interface helps prepare content by breaking it into manageable pieces that fit within an LLM's context window. This is crucial for both performance and accuracy when dealing with large documents.
        *   **Balancing Rule-Based and LLM-Powered Extraction:** Crawl4AI doesn't force you into one paradigm. You can use fast and efficient CSS selectors for well-structured sites and then leverage the power of LLMs for complex, unstructured data, or even combine them in hybrid approaches. This flexibility is key to building robust and adaptable web data extraction pipelines.

## 2. Core Concepts in Crawl4AI Extraction
    * 2.1. The `ExtractionStrategy` Interface: Your Key to Custom Extraction
        *   2.1.1. Purpose: Why an interface? Promoting modularity and extensibility.
            The `ExtractionStrategy` interface (defined in `crawl4ai/extraction_strategy.py`) is a fundamental design choice in Crawl4AI. It establishes a common contract for all extraction methods. The primary benefit is **modularity**: your main crawling logic doesn't need to know the specifics of *how* data is extracted. It simply invokes the strategy, and the strategy handles the details. This makes your code cleaner and more maintainable.
            Furthermore, it promotes **extensibility**: if the built-in strategies don't fit your exact needs (e.g., you're dealing with a proprietary data format or a very unique web structure), you can create your own class that implements the `ExtractionStrategy` interface and plug it directly into Crawl4AI.

        *   2.1.2. Key Methods to Understand (Conceptual): `extract()` and `run()`.
            While you typically won't call these directly if using built-in strategies (Crawl4AI handles it), understanding their roles is important if you plan to create custom strategies:
            *   `extract(url: str, html_content: str, *args, **kwargs) -> List[Dict[str, Any]]`: This is the core method that every concrete strategy must implement. It takes the URL and HTML content (or pre-processed content like Markdown, depending on the `input_format` of the strategy) and returns a list of dictionaries, where each dictionary represents an extracted item.
            *   `run(url: str, sections: List[str], *args, **kwargs) -> List[Dict[str, Any]]`: This method is often used for strategies that process content in chunks (like `LLMExtractionStrategy`). It takes a list of content `sections` and typically calls `extract()` for each section, then aggregates the results. For simpler strategies that operate on the whole content at once, `run` might just call `extract` with the joined sections.

        *   2.1.3. When Would You Implement Your Own `ExtractionStrategy`?
            You'd consider creating a custom `ExtractionStrategy` in scenarios like:
            *   **Highly Specialized Data Sources:** If you're extracting data from a non-standard format (e.g., custom XML, binary files, or a very idiosyncratic HTML structure not well-suited for CSS/XPath/Regex).
            *   **Integrating Proprietary Extraction Logic:** If your organization has existing, specialized parsing libraries or algorithms you want to use within the Crawl4AI framework.
            *   **Advanced Performance Optimizations:** For extremely high-volume scraping of a specific site, you might develop a hyper-optimized parser that bypasses more general tools.
            *   **Unique Pre-processing or Post-processing:** If your extraction requires complex data transformations or enrichments beyond what the built-in strategies offer.

    * 2.2. The `ChunkingStrategy` Interface: Preparing Content for LLMs
        *   2.2.1. Why Chunking is Crucial for LLM-Based Extraction
            Large Language Models (LLMs) have a "context window" – a limit on the amount of text they can process at once (e.g., 4096, 8192, or even 128k+ tokens). If you feed an entire long webpage directly to an LLM for extraction:
            *   **Context Overflow:** The content might exceed the LLM's limit, leading to truncation and loss of information, or outright errors.
            *   **Reduced Accuracy:** Even if it fits, an LLM might struggle to find specific details in a very long, noisy document. Its attention can get diluted.
            *   **Higher Cost & Latency:** Processing more tokens means higher API costs (for paid models) and longer response times.
            Chunking addresses this by breaking down the input content into smaller, more focused segments, each of which can be processed by the LLM more effectively.

        *   2.2.2. How Chunking Strategies Work in Crawl4AI
            A `ChunkingStrategy` (defined in `crawl4ai/chunking_strategy.py`) is responsible for taking a single block of text (e.g., the Markdown content of a page) and dividing it into a list of smaller strings (chunks).
            *   The primary method is `chunk(document: str) -> List[str]`.
            *   The `LLMExtractionStrategy` then iterates over these chunks, sending each one (or a batch of them, depending on its internal logic) to the LLM for extraction. The results from each chunk are then typically aggregated.

        *   2.2.3. Overview of Built-in Chunking Strategies
            Crawl4AI provides a couple of ready-to-use chunking strategies:
            *   **`RegexChunking` (default for `LLMExtractionStrategy`):** This strategy (from `crawl4ai/chunking_strategy.py`) uses regular expressions to split text. By default, it might split by paragraphs or other common delimiters. It aims to create semantically meaningful chunks. This is often a good general-purpose choice.
                *   *When to use:* Good for text-heavy documents where paragraph or section breaks are meaningful.
            *   **`IdentityChunking`:** This strategy (from `crawl4ai/chunking_strategy.py`) doesn't actually do any chunking; it returns the input document as a single chunk.
                *   *When to use:*
                    *   When your input documents are already small enough to fit the LLM's context window.
                    *   When you have pre-processed your content into chunks *before* passing it to `LLMExtractionStrategy`.
                    *   When the LLM you're using has a very large context window and performs well on full documents for your specific task.

        *   2.2.4. When to Choose or Implement a Custom `ChunkingStrategy`.
            While the built-in chunkers are useful, you might need a custom `ChunkingStrategy` if:
            *   **Domain-Specific Document Structures:** Your content has unique structural elements that `RegexChunking` doesn't handle well (e.g., legal documents with numbered clauses, scripts with dialogue/scene breaks, log files).
            *   **Semantic Chunking Needs:** You require more sophisticated chunking based on semantic meaning rather than just regex patterns (though this can become complex and might involve NLP techniques within your custom chunker).
            *   **Fixed-Size Overlapping Chunks:** You want to implement a sliding window approach with precise control over chunk size and overlap, which might be beneficial for certain types_of information retrieval.
            *   **Table or List-Aware Chunking:** You need to ensure that tables or lists are not awkwardly split across chunks.

    * 2.3. Schema Definition: The Blueprint for Your Extracted Data
        *   2.3.1. Why a Well-Defined Schema is Essential
            A schema acts as a contract for your data. It defines:
            *   What pieces of information you expect to extract (the field names).
            *   The data type of each piece of information (e.g., string, integer, boolean, list, nested object).
            *   How to find each piece of information (e.g., CSS selector, XPath, or implied for LLM).
            Benefits include:
            *   **Consistency:** Ensures that extracted data always has the same structure, making it easier to process downstream.
            *   **Reliability:** Helps catch errors if a website's structure changes and a selector no longer works, or if an LLM fails to extract a required field.
            *   **Guidance:** For rule-based extractors, it provides the direct rules. For LLM-based extractors, it informs the LLM about the desired output structure, significantly improving the quality and predictability of results.
            *   **Validation:** Pydantic models, used with LLMs, offer automatic data validation.

        *   2.3.2. Defining Schemas for CSS/XPath/LXML Strategies (Dictionary-based)
            For strategies like `JsonCssExtractionStrategy`, `JsonXPathExtractionStrategy`, and `JsonLxmlExtractionStrategy`, the schema is a Python dictionary.
            *   **Structure:**
                ```python
                schema = {
                    "name": "MyExtractorName", # Optional: A name for your schema
                    "baseSelector": "div.product-item", # CSS selector for repeating items (e.g., products on a list page)
                    "fields": [
                        {
                            "name": "product_name",      # Name of the field in the output
                            "selector": "h2.product-title", # CSS/XPath selector relative to baseSelector (or page if no baseSelector)
                            "type": "text"             # "text", "attribute", "html", "nested", "list"
                        },
                        {
                            "name": "product_link",
                            "selector": "a.product-link",
                            "type": "attribute",
                            "attribute": "href"        # Name of the HTML attribute to extract (e.g., 'href' for links)
                        },
                        # ... more fields ...
                    ]
                }
                ```
            *   **Key Fields:**
                *   `baseSelector`: (Optional) If you're extracting a list of similar items (e.g., multiple products, articles), this selector targets the container element for each item. All field selectors will then be relative to this base element. If omitted, field selectors are relative to the whole document.
                *   `fields`: A list of dictionaries, each defining a field to extract.
                    *   `name`: The key for this field in the output JSON.
                    *   `selector`: The CSS selector or XPath expression to locate the data.
                    *   `type`:
                        *   `"text"`: Extracts the text content of the selected element.
                        *   `"attribute"`: Extracts the value of a specified HTML attribute (requires an additional `"attribute": "attr_name"` key).
                        *   `"html"`: Extracts the inner HTML of the selected element.
                        *   `"nested"`: Allows defining a sub-schema for extracting nested structured data (requires an additional `"fields": [...]` key, similar to the top-level fields).
                        *   `"list"`: Indicates that the selector is expected to return multiple elements, and the extraction logic (defined by sub-fields) should be applied to each. Often used with a nested `fields` definition.
            *   **Tips for Designing Dictionary-Based Schemas:**
                *   Be as specific as possible with your selectors to avoid ambiguity.
                *   Start with a simple schema and iteratively add more fields.
                *   Test your selectors in your browser's developer tools first.
                *   Use `baseSelector` for lists to keep field selectors concise and maintainable.
            *   **Example: Schema for extracting blog post titles and authors:**
                ```python
                blog_post_schema = {
                    "name": "BlogPostExtractor",
                    "baseSelector": "article.post",
                    "fields": [
                        {"name": "title", "selector": "h1.entry-title", "type": "text"},
                        {"name": "author", "selector": "span.author-name", "type": "text"},
                        {"name": "publication_date", "selector": "time.published-date", "type": "attribute", "attribute": "datetime"}
                    ]
                }
                ```

        *   2.3.3. Defining Schemas for `LLMExtractionStrategy` (Pydantic Models)
            When using `LLMExtractionStrategy` with `extraction_type="schema"` (the default), you provide a Pydantic model as the schema.
            *   **Advantages of Pydantic:**
                *   **Type Hints:** Clearly define the expected data type for each field.
                *   **Validation:** Pydantic automatically validates that the data extracted by the LLM conforms to your model's types and constraints. If not, it raises an error.
                *   **IDE Support:** Excellent autocompletion and type checking in modern IDEs.
                *   **Serialization:** Easy conversion to and from JSON.
            *   **How Pydantic Models Guide the LLM:** Crawl4AI internally converts your Pydantic model into a JSON schema representation, which is then included in the prompt to the LLM. This tells the LLM the exact structure and field names it should use in its JSON output.
            *   **Example: Pydantic model for product information:**
                ```python
                from pydantic import BaseModel, HttpUrl
                from typing import Optional, List

                class ProductInfo(BaseModel):
                    product_name: str
                    price: Optional[float]
                    description: str
                    image_urls: List[HttpUrl] = []
                    features: Optional[List[str]]
                ```
                When this model is used, the LLM will be instructed to return JSON objects that look like:
                ```json
                {
                  "product_name": "Awesome Laptop",
                  "price": 1299.99,
                  "description": "A very fast and light laptop.",
                  "image_urls": ["https://example.com/image1.jpg"],
                  "features": ["16GB RAM", "512GB SSD"]
                }
                ```

        *   2.3.4. Best Practices for Schema Design Across Strategy Types.
            *   **Be Specific with Field Names:** Use clear, descriptive names that reflect the data.
            *   **Start Simple:** Begin with a few key fields and expand as needed.
            *   **Handle Optional Data:** For fields that might not always be present, define them as optional in your Pydantic model (e.g., `Optional[str]`) or ensure your non-LLM logic handles missing elements gracefully (e.g., by providing default values or allowing `None`).
            *   **Consider Data Types:** Choose appropriate types (string, number, boolean, list, nested object) to ensure data integrity.
            *   **Test Iteratively:** Regularly test your schemas with real web content to catch issues early.

## 3. Non-LLM Based Extraction Strategies: Precision and Speed
    * 3.1. When to Choose Non-LLM Strategies
        Non-LLM (or rule-based) strategies are excellent choices when:
        *   **Website Structure is Consistent:** The target website has a stable and predictable HTML structure. Changes are infrequent.
        *   **Performance is Key:** These strategies are generally much faster and less resource-intensive than LLM-based approaches as they don't involve API calls to external services or loading large models.
        *   **Cost is a Major Factor:** Non-LLM strategies have no per-extraction operational cost beyond your own compute resources.
        *   **Data Points are Simple and Directly Targetable:** You need to extract clearly identifiable pieces of text, attributes, or simple lists.
        *   **You Have Expertise in CSS Selectors or XPath:** If you or your team are comfortable writing and maintaining these selectors.
        *   **No Semantic Interpretation Needed:** The data can be located purely by its position or tags in the HTML, without needing to understand the meaning of the surrounding text.

    * 3.2. Mastering `JsonCssExtractionStrategy`
        *   3.2.1. Understanding Its Strengths: Leveraging CSS Selectors
            `JsonCssExtractionStrategy` is often the first choice for non-LLM extraction due to the widespread familiarity with CSS selectors.
            *   **Strengths:**
                *   Relatively easy to learn and write.
                *   Well-supported by browsers' developer tools for testing.
                *   Efficient for most common extraction tasks.
            *   **Underlying Library:** Crawl4AI typically uses BeautifulSoup4 or LXML for parsing HTML and applying CSS selectors, providing robust and performant parsing.

        *   3.2.2. Workflow: Extracting Data with CSS
            *   **Step 1: Analyzing the Target HTML Structure:**
                *   Use your browser's developer tools (e.g., "Inspect Element") to examine the HTML of the page you want to scrape.
                *   Identify the HTML tags, classes, and IDs that uniquely contain the data you need.
                *   Example: If you want to extract an article's title, you might find it's always within an `<h1>` tag with class `article-title`.
            *   **Step 2: Crafting your Dictionary-Based Schema with CSS Selectors:**
                *   Define your schema as a Python dictionary, as described in section 2.3.2.
                *   Fill in the `selector` for each field with the appropriate CSS selector.
                ```python
                article_schema = {
                    "baseSelector": "article.post", # Target each article
                    "fields": [
                        {"name": "title", "selector": "h1.entry-title", "type": "text"},
                        {"name": "author_link", "selector": "a.author-url", "type": "attribute", "attribute": "href"}
                    ]
                }
                ```
            *   **Step 3: Configuring `CrawlerRunConfig` to use `JsonCssExtractionStrategy`:**
                ```python
                from crawl4ai import CrawlerRunConfig
                from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

                extraction_strategy = JsonCssExtractionStrategy(schema=article_schema)
                run_config = CrawlerRunConfig(extraction_strategy=extraction_strategy)
                ```
            *   **Step 4: Interpreting the Results:**
                *   The `result.extracted_content` will be a JSON string containing a list of dictionaries, where each dictionary matches your schema.
                ```python
                import json
                # Assuming 'result' is the output from crawler.arun()
                if result.extracted_content:
                    data = json.loads(result.extracted_content)
                    for item in data:
                        print(f"Title: {item.get('title')}, Author Link: {item.get('author_link')}")
                ```

        *   3.2.3. Handling Nested Data Structures
            You can extract nested data by defining a field with `type: "nested"` and providing another `fields` list within it.
            *   **How to define:** The `selector` for the nested field targets the container of the nested data. The sub-fields' selectors are then relative to this nested container.
            *   **Example: Extracting comments and their authors:**
                ```python
                comment_schema = {
                    "baseSelector": "div.comment-thread",
                    "fields": [
                        {"name": "comment_id", "selector": "div.comment", "type": "attribute", "attribute": "data-comment-id"},
                        {
                            "name": "main_comment",
                            "selector": "div.comment-body", # Selector for the main comment container
                            "type": "nested",
                            "fields": [
                                {"name": "author", "selector": "span.comment-author", "type": "text"},
                                {"name": "text", "selector": "p.comment-text", "type": "text"}
                            ]
                        },
                        {
                            "name": "replies",
                            "selector": "div.reply", # Selector for each reply
                            "type": "list", # Indicates multiple replies
                            "fields": [ # Schema for each reply item
                                {"name": "reply_author", "selector": "span.reply-author", "type": "text"},
                                {"name": "reply_text", "selector": "p.reply-text", "type": "text"}
                            ]
                        }
                    ]
                }
                ```

        *   3.2.4. Extracting Lists of Items
            The `baseSelector` is key for extracting lists.
            *   **`baseSelector`:** Targets each individual item in the list (e.g., each `<li>` in a `<ul>`, each `div.product-card`).
            *   **Relative Field Selectors:** All selectors within the `fields` list are then evaluated *relative* to each element matched by `baseSelector`.
            *   **Example: Extracting a list of products from a category page:**
                ```python
                product_list_schema = {
                    "name": "ProductList",
                    "baseSelector": "div.product-listing div.product-item-container", # Each product card
                    "fields": [
                        {"name": "product_name", "selector": "h3.product-name a", "type": "text"},
                        {"name": "price", "selector": "span.price", "type": "text"},
                        {"name": "url", "selector": "h3.product-name a", "type": "attribute", "attribute": "href"}
                    ]
                }
                ```
                This would produce a list of product dictionaries.

        *   3.2.5. Code Example: Extracting News Headlines and Links from Hacker News (Illustrative)
            ```python
            import asyncio
            import json
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
            from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
            from crawl4ai.cache_manager import CacheMode

            async def extract_hn_news():
                hn_schema = {
                    "name": "HackerNewsFrontPage",
                    "baseSelector": "tr.athing", # Each story row in Hacker News
                    "fields": [
                        {
                            "name": "rank",
                            "selector": "span.rank",
                            "type": "text"
                        },
                        {
                            "name": "title",
                            "selector": "span.titleline > a", # Get the first 'a' tag within titleline
                            "type": "text"
                        },
                        {
                            "name": "url",
                            "selector": "span.titleline > a",
                            "type": "attribute",
                            "attribute": "href"
                        },
                        # Example for next row (subtext) data - shows using a more complex relative selector
                        {
                            "name": "points",
                            "selector": "xpath=./following-sibling::tr[1]/td[@class='subtext']/span[@class='score']",
                            "type": "text" # Note: Using XPath within CSS strategy for advanced relative selection
                                           # This is a conceptual example; pure CSS might be trickier for direct sibling access.
                                           # A more common CSS approach would be to have a slightly broader baseSelector
                                           # or separate extraction steps if nesting is too complex for pure CSS.
                        }
                    ]
                }

                extraction_strategy = JsonCssExtractionStrategy(schema=hn_schema)
                browser_config = BrowserConfig(headless=True)
                run_config = CrawlerRunConfig(
                    extraction_strategy=extraction_strategy,
                    cache_mode=CacheMode.BYPASS # For fresh data in this example
                )

                async with AsyncWebCrawler(config=browser_config) as crawler:
                    result = await crawler.arun(
                        url="https://news.ycombinator.com/",
                        config=run_config
                    )

                if result.success and result.extracted_content:
                    articles = json.loads(result.extracted_content)
                    print(f"Extracted {len(articles)} articles from Hacker News:")
                    for i, article in enumerate(articles[:5]): # Print first 5
                        print(f"  {i+1}. {article.get('title')} ({article.get('points', 'N/A points')}) - {article.get('url')}")
                else:
                    print(f"Failed to extract articles: {result.error_message}")

            if __name__ == "__main__":
                asyncio.run(extract_hn_news())
            ```
            *Self-correction during thought process: The original `points` selector was a bit too complex for a pure CSS example within `JsonCssExtractionStrategy`. While some libraries might allow mixing, it's better to illustrate clear CSS or mention that for such relative sibling traversals, XPath might be more direct, or the schema/baseSelector might need restructuring.*

        *   3.2.6. Best Practices for Writing Robust CSS Selectors.
            *   **Prefer IDs if Stable:** `#unique-id` is usually the most robust if available and unique.
            *   **Use Specific but Not Overly Specific Classes:** `.meaningful-class` is good. Avoid overly long chains like `div.container > div.row > div.col-md-8 > article.post > h1` if `h1.post-title` is unique enough.
            *   **Attribute Selectors:** `input[name="email"]` can be very precise.
            *   **Avoid Relying on Order (unless necessary):** `:nth-child()` can be brittle if the page structure changes slightly. Use it sparingly.
            *   **Test Thoroughly:** Use browser dev tools to validate your selectors on various pages of the target site.

        *   3.2.7. Troubleshooting: Common Issues and Solutions
            *   **Selector Returning `None` or Empty List:**
                *   *Cause:* Selector is incorrect, element doesn't exist, or content is loaded dynamically *after* initial HTML.
                *   *Solution:* Double-check selector in dev tools. For dynamic content, ensure Crawl4AI's browser is rendering JS (default) or use `wait_for` in `CrawlerRunConfig`.
            *   **Handling Dynamic Class Names:**
                *   *Cause:* Sites using CSS-in-JS or frameworks might generate dynamic class names (e.g., `_header_a83hf8`).
                *   *Solution:* Look for stable parent elements or use attribute selectors that target parts of class names (e.g., `div[class*="header_"]`), or rely on structural selectors (e.g., `article > h1`). This is where XPath or LLM strategies might be more robust.
            *   **Extracting Incorrect Data:**
                *   *Cause:* Selector is too broad and matches multiple elements.
                *   *Solution:* Make your selector more specific. Use direct child `>` or adjacent sibling `+` combinators if appropriate.

    * 3.3. Leveraging `JsonXPathExtractionStrategy`
        *   3.3.1. When XPath Shines: Complex Selections and Navigating the DOM
            XPath (XML Path Language) is a powerful query language for selecting nodes from an XML or HTML document. It excels where CSS selectors might fall short:
            *   **Complex Relationships:** Selecting elements based on their ancestors, siblings, or preceding/following elements (e.g., "find the `div` that follows an `h2` with text 'Price'").
            *   **Text Content Matching:** Selecting elements based on their text content (e.g., `//button[contains(text(), 'Add to Cart')]`).
            *   **Navigating Up the DOM:** Easily selecting parent or ancestor elements.
            *   **Using Functions:** XPath has built-in functions for string manipulation, counting, etc.

        *   3.3.2. Key Differences from CSS Strategy (Syntax, capabilities).
            *   **Syntax:** XPath uses a path-like syntax (e.g., `/html/body/div[1]/h1`) whereas CSS uses selectors like `div.my-class > h1`.
            *   **Capabilities:** XPath is generally more powerful for traversing the DOM in complex ways. CSS is often simpler for common class/ID/tag selections.
            *   **Performance:** For simple selections, CSS can sometimes be faster. For complex traversals, a well-written XPath might be more efficient than a convoluted CSS equivalent. Crawl4AI uses LXML for XPath, which is highly performant.

        *   3.3.3. Workflow: Similar to CSS, but with XPath expressions.
            The workflow is identical to `JsonCssExtractionStrategy`, except your schema's `selector` fields will contain XPath expressions.
            *   **Step 1: Analyzing HTML:** Use browser developer tools. Many browsers allow you to right-click an element and "Copy XPath."
            *   **Step 2: Crafting your Dictionary-Based Schema with XPath:**
                ```python
                xpath_schema = {
                    "baseSelector": "//article[@class='blog-entry']", # XPath for each article
                    "fields": [
                        {"name": "title", "selector": ".//h1[contains(@class, 'title')]/text()", "type": "text"},
                        {"name": "author_url", "selector": ".//a[contains(@class, 'author-profile')]/@href", "type": "attribute"}
                        # Note: type "attribute" for XPath will get the attribute value if selector ends with /@attr
                        # type "text" will get text content. If selector selects an element, text() can be appended.
                    ]
                }
                ```
                *Important for XPath `type` handling:*
                *   If your XPath selector directly targets an attribute (e.g., `//a/@href`), `type: "attribute"` is redundant but harmless; the attribute value is returned.
                *   If your XPath selector targets an element and you want its text, use `type: "text"` (or append `/text()` to your XPath).
                *   If your XPath targets an element and you want an attribute of *that* element, you'd use `type: "attribute"` and specify the `attribute` key, e.g., `{"selector": "//img", "type": "attribute", "attribute": "src"}`.

            *   **Step 3: Configuration in `CrawlerRunConfig`:**
                ```python
                from crawl4ai.extraction_strategy import JsonXPathExtractionStrategy
                extraction_strategy = JsonXPathExtractionStrategy(schema=xpath_schema)
                run_config = CrawlerRunConfig(extraction_strategy=extraction_strategy)
                ```

        *   3.3.4. Code Example: Extracting Data Using XPath Functions (e.g., `contains()`, `text()`)
            ```python
            import asyncio
            import json
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
            from crawl4ai.extraction_strategy import JsonXPathExtractionStrategy
            from crawl4ai.cache_manager import CacheMode

            async def extract_with_xpath():
                # Example HTML content
                sample_html = """
                <html><body>
                    <div class="product">
                        <h2>Product A</h2>
                        <span class="price">Price: $19.99</span>
                        <a href="/product/a" class="details-link">View Details</a>
                    </div>
                    <div class="product">
                        <h2>Product B</h2>
                        <span class="price">Price: $29.99</span>
                        <a href="/product/b" class="details-link">More Info</a>
                    </div>
                </body></html>
                """

                product_schema_xpath = {
                    "name": "ProductXPathExtractor",
                    "baseSelector": "//div[@class='product']",
                    "fields": [
                        {"name": "name", "selector": ".//h2/text()", "type": "text"},
                        # Extracts text after "Price: "
                        {"name": "price_value", "selector": "substring-after(.//span[contains(@class,'price')]/text(), 'Price: $')", "type": "text"},
                        {"name": "details_url", "selector": ".//a[contains(@class,'details-link') or contains(text(),'More Info')]/@href", "type": "attribute"}
                    ]
                }
                extraction_strategy = JsonXPathExtractionStrategy(schema=product_schema_xpath)
                run_config = CrawlerRunConfig(extraction_strategy=extraction_strategy, cache_mode=CacheMode.BYPASS)

                async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
                    # Using raw HTML input for this example
                    result = await crawler.arun(url=f"raw://{sample_html}", config=run_config)

                if result.success and result.extracted_content:
                    products = json.loads(result.extracted_content)
                    print("Extracted Products using XPath:")
                    for product in products:
                        print(product)
                else:
                    print(f"XPath extraction failed: {result.error_message}")

            if __name__ == "__main__":
                asyncio.run(extract_with_xpath())
            ```

        *   3.3.5. Tips for Effective XPath Usage.
            *   **Start with `.` for relative paths:** Within a `baseSelector`, field selectors should usually start with `./` to be relative to the current base element.
            *   **Use `text()` to get text content:** `//div/text()` gets the direct text children. `//div//text()` gets all text within the div.
            *   **Select attributes with `/@attribute_name`:** `//img/@src`.
            *   **Leverage functions:** `contains()`, `starts-with()`, `substring-after()`, `normalize-space()` are very useful.
            *   **Be mindful of namespaces** if working with XML-heavy HTML or actual XML.

    * 3.4. Understanding `JsonLxmlExtractionStrategy`
        The `JsonLxmlExtractionStrategy` is essentially a specialized version of `JsonCssExtractionStrategy` that explicitly uses the LXML library for parsing and CSS selection.
        *   3.4.1. Potential Performance Gains: When to consider it.
            LXML is known for its speed. For very large HTML documents or high-throughput scraping scenarios where parsing speed is a bottleneck, `JsonLxmlExtractionStrategy` *might* offer better performance than the default BeautifulSoup-backed CSS selector engine (though BeautifulSoup itself can use LXML as a parser). The actual difference can vary.
        *   3.4.2. Usage and Configuration: Similarities and differences with `JsonCssExtractionStrategy`.
            Usage is identical to `JsonCssExtractionStrategy`. You provide the same dictionary-based schema with CSS selectors. Crawl4AI handles the backend difference.
            ```python
            from crawl4ai.extraction_strategy import JsonLxmlExtractionStrategy # Import this
            
            # Schema is the same as for JsonCssExtractionStrategy
            my_schema = { ... } 
            extraction_strategy = JsonLxmlExtractionStrategy(schema=my_schema)
            run_config = CrawlerRunConfig(extraction_strategy=extraction_strategy)
            ```
        *   3.4.3. When to benchmark against `JsonCssExtractionStrategy`.
            If you suspect CSS selection is a performance bottleneck in your Crawl4AI application, and you're processing a large volume of pages or very large pages, it's worth benchmarking `JsonLxmlExtractionStrategy` against the default `JsonCssExtractionStrategy` to see if it provides a noticeable speedup in your specific environment and use case.

    * 3.5. Precise Targeting with `RegexExtractionStrategy`
        *   3.5.1. The Power of Regular Expressions: When Are They the Right Tool?
            Regular expressions are ideal when:
            *   **Data is in Unstructured or Semi-Structured Text:** The information isn't neatly tagged with specific HTML elements or classes (e.g., extracting an email address from a paragraph of text).
            *   **Targeting Specific Patterns:** You need to find data that conforms to a known pattern, like email addresses, phone numbers, dates, URLs, postal codes, UUIDs, product SKUs, etc.
            *   **HTML Structure is Unreliable:** If the HTML tags around the data change frequently, but the data itself has a consistent textual pattern.
            *   **Fallback or Augmentation:** Can be used to extract data that CSS/XPath selectors miss, or to clean/validate data extracted by other means.

        *   3.5.2. Utilizing Built-in Patterns
            `RegexExtractionStrategy` (from `crawl4ai.extraction_strategy`) comes with a handy `BuiltInPatterns` IntFlag enum. This allows you to easily enable common extraction patterns without writing the regex yourself.
            *   **Overview:** Refer to `RegexExtractionStrategy._B` (or `RegexExtractionStrategy.BuiltInPatterns` if aliased publicly) for the available flags like `EMAIL`, `PHONE_US`, `URL`, `IPV4`, `UUID`, `DATE_ISO`, `CURRENCY`, etc. Each flag corresponds to a pre-defined, tested regex pattern.
            *   **How to use:** You pass the bitwise OR of the desired patterns to the `pattern` argument of the `RegexExtractionStrategy` constructor.
            *   **Code Example: Extracting all email addresses and US phone numbers from a webpage's text:**
                ```python
                import asyncio
                import json
                from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
                from crawl4ai.extraction_strategy import RegexExtractionStrategy

                async def extract_contact_info():
                    # Combine built-in patterns
                    patterns_to_use = RegexExtractionStrategy.BuiltInPatterns.EMAIL | \
                                      RegexExtractionStrategy.BuiltInPatterns.PHONE_US
                    
                    extraction_strategy = RegexExtractionStrategy(pattern=patterns_to_use)
                    
                    # This strategy works best on plain text, so use 'markdown' or 'text' input_format
                    # if using with the standard crawler flow, or pass plain text directly.
                    run_config = CrawlerRunConfig(
                        extraction_strategy=extraction_strategy,
                        # input_format='text' # Alternative: let the strategy handle HTML to text
                    )

                    sample_text_content = """
                    Contact us at support@example.com or call (800) 555-1212.
                    Our sales team can be reached at sales@example.com.
                    For urgent matters, dial 1-800-555-1234.
                    Our website is https://example.com.
                    """

                    async with AsyncWebCrawler() as crawler:
                        # Here, we're directly using the 'extract' method for simplicity with raw text
                        # In a full crawl, you'd use crawler.arun() with the run_config
                        extracted_data = extraction_strategy.extract(
                            url="raw://text_content", # Dummy URL for raw content
                            html_content=sample_text_content # Provide text directly
                        )
                    
                    print("Extracted Contact Info:")
                    for item in extracted_data:
                        print(f"  Label: {item['label']}, Value: {item['value']}, Span: {item['span']}")

                if __name__ == "__main__":
                    asyncio.run(extract_contact_info())
                ```
                **Output structure for `RegexExtractionStrategy`:**
                Each extracted item is a dictionary:
                `{"url": "source_url", "label": "pattern_label", "value": "matched_string", "span": [start_index, end_index]}`

        *   3.5.3. Defining and Using Custom Regex Patterns
            If built-in patterns aren't sufficient, you can provide your own.
            *   **Passing a Dictionary:** Supply a dictionary where keys are labels (strings) for your patterns, and values are the regex pattern strings.
            *   **Tips for Writing Regex:**
                *   Use non-capturing groups `(?:...)` if you don't need to capture a part of the match.
                *   Be mindful of greediness (e.g., use `*?` or `+?` for non-greedy matches).
                *   Test your regex thoroughly with tools like regex101.com.
                *   Remember that regex patterns are raw strings in Python (e.g., `r"\b\d{5}\b"`).
            *   **Code Example: Extracting custom product SKUs (e.g., SKU-XXXX-YYYY):**
                ```python
                import asyncio
                import json
                from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
                from crawl4ai.extraction_strategy import RegexExtractionStrategy

                async def extract_skus():
                    custom_patterns = {
                        "product_sku": r"SKU-\d{4}-[A-Z]{4}"
                    }
                    extraction_strategy = RegexExtractionStrategy(custom=custom_patterns)
                    run_config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

                    sample_text = "Product Alpha SKU-1234-ABCD and Product Beta SKU-5678-EFGH."
                    
                    # Direct usage for simplicity
                    extracted_data = extraction_strategy.extract(url="raw://text", html_content=sample_text)

                    print("Extracted SKUs:")
                    for item in extracted_data:
                        print(item)
                
                if __name__ == "__main__":
                    asyncio.run(extract_skus())
                ```

        *   3.5.4. Leveraging `generate_pattern()` for Dynamic Regex Creation
            The static method `RegexExtractionStrategy.generate_pattern(examples: List[str], labels: List[str] = None, llm_config: LLMConfig = None, **kwargs) -> str` (or Dict[str, str] if labels are provided) is a powerful utility that uses an LLM to generate a regex pattern for you based on examples.
            *   **How it Works:** You provide a list of example strings that you want to match. Optionally, you can provide corresponding labels if you want to generate multiple patterns for different types of data. The method then queries an LLM (configurable via `llm_config`) to infer a regex pattern that would capture those examples.
            *   **Use Cases:**
                *   You have a clear set of examples of the data you want to extract but are not a regex expert.
                *   You need to quickly prototype an extraction for a new data type.
                *   The pattern is complex, and you want an AI-assisted starting point.
            *   **Code Example: Generating a regex pattern from a list of example IDs:**
                ```python
                import asyncio
                from crawl4ai.extraction_strategy import RegexExtractionStrategy
                from crawl4ai import LLMConfig # Assuming LLMConfig is correctly imported

                async def generate_and_use_regex():
                    example_ids = ["ID_123_XYZ", "ID_456_ABC", "ID_789_DEF"]
                    
                    # Configure LLM for pattern generation (replace with your actual config)
                    # For open-source, set api_token=None or your specific setup
                    llm_for_regex = LLMConfig(provider="openai/gpt-3.5-turbo", api_token="YOUR_OPENAI_API_KEY") 
                                            # Or: provider="ollama/llama3", api_token=None

                    try:
                        # Generate a single pattern
                        generated_pattern_str = await RegexExtractionStrategy.generate_pattern(
                            examples=example_ids,
                            llm_config=llm_for_regex,
                            # Optional: Add a query to guide the LLM
                            query="Generate a regex to capture these types of IDs."
                        )
                        print(f"Generated Regex for IDs: {generated_pattern_str}")

                        # You can then use this generated_pattern_str in RegexExtractionStrategy:
                        # custom_patterns = {"custom_id": generated_pattern_str}
                        # strategy = RegexExtractionStrategy(custom=custom_patterns)
                        # ... then use the strategy ...

                        # Example for generating multiple labeled patterns
                        example_data = {
                            "order_id": ["ORD-001", "ORD-002"],
                            "user_id": ["USR_A", "USR_B"]
                        }
                        generated_patterns_dict = await RegexExtractionStrategy.generate_pattern(
                            examples=list(example_data.values()), # Pass lists of examples
                            labels=list(example_data.keys()),    # Corresponding labels
                            llm_config=llm_for_regex
                        )
                        print(f"Generated Labeled Regex Patterns: {generated_patterns_dict}")
                        # strategy_multi = RegexExtractionStrategy(custom=generated_patterns_dict)

                    except Exception as e:
                        print(f"Error generating pattern: {e}")
                        print("Make sure your LLMConfig is correctly set up and the LLM is accessible.")


                if __name__ == "__main__":
                    asyncio.run(generate_and_use_regex())
                ```
            *   **Limitations and Considerations:**
                *   **LLM Dependency:** Requires a configured and accessible LLM.
                *   **Quality Varies:** The quality of the generated regex depends on the LLM's capabilities and the quality/quantity of your examples.
                *   **Review and Test:** Always review and test LLM-generated regex patterns thoroughly before deploying them in production. They might be overly broad or miss edge cases.
                *   **Cost/Latency:** Involves an LLM call, so it's not for runtime pattern generation in a tight loop. Best used for one-off generation or infrequent updates.

        *   3.5.5. Best Practices for `RegexExtractionStrategy`.
            *   **Target Plain Text:** Regex works best on clean text. If applying to HTML, consider extracting text content first or using the `input_format="text"` or `input_format="markdown"` options in `LLMExtractionStrategy` if combining.
            *   **Be Specific:** Craft regex to be as specific as possible to avoid false positives.
            *   **Use Non-Capturing Groups:** `(?:...)` can improve performance if you don't need to capture certain parts of the match.
            *   **Test with Diverse Examples:** Ensure your regex works for various valid inputs and doesn't match invalid ones.

        *   3.5.6. Debugging Regex: Ensuring Accuracy and Avoiding Over-matching.
            *   **Online Regex Testers:** Use tools like regex101.com or pythex.org to build and test your patterns interactively with sample text.
            *   **Break Down Complex Patterns:** If a regex is very complex, test its components separately.
            *   **Log Matched Values:** During development, print out the `value` extracted by your regex to verify it's capturing what you intend.
            *   **Consider Edge Cases:** Think about variations in formatting, optional components, or unusual inputs that your regex might encounter.

## 4. LLM-Based Extraction Strategies: Handling Complexity and Ambiguity
    * 4.1. When to Turn to LLMs for Data Extraction
        LLM-based extraction strategies shine when:
        *   **Unstructured or Inconsistently Structured Content:** The data isn't in neat HTML tables or consistently tagged elements. It might be embedded in paragraphs, reviews, or forum posts.
        *   **Need for Semantic Understanding:** You need to extract information based on its meaning, not just its position or HTML tags (e.g., "What is the main sentiment of this review?" or "Extract the key arguments from this article.").
        *   **Rapid Prototyping:** When defining precise CSS/XPath selectors is too time-consuming or the site structure is unknown/volatile, an LLM can often get you started quickly with a descriptive prompt.
        *   **Extracting Nuanced Information:** For tasks like summarization, topic extraction, or identifying relationships between entities.
        *   **Schema Flexibility:** When the desired output structure is complex or might evolve, LLMs (especially with Pydantic schema guidance) can adapt more easily than hand-crafted rules.
        *   **Handling Diverse Sources:** If you need to extract similar information from many different websites with varying layouts, a well-crafted LLM prompt can be more generalizable than site-specific selectors.

    * 4.2. Deep Dive into `LLMExtractionStrategy`
        *   4.2.1. Core Idea: Instructing an LLM to be Your Extractor.
            The `LLMExtractionStrategy` (from `crawl4ai.extraction_strategy`) leverages the power of Large Language Models. Instead of writing explicit rules (like CSS selectors), you provide:
            1.  **Content:** The text (HTML, Markdown, or plain text) to extract from.
            2.  **Instruction:** A natural language prompt telling the LLM *what* to extract and *how* to structure it.
            3.  **(Optional but Recommended) Schema:** A Pydantic model defining the desired output structure, which helps the LLM produce consistent and validated JSON.
            The LLM then processes the content based on your instructions and attempts to return the data in the requested format.

        *   4.2.2. Configuring the LLM: The `LLMConfig` Object
            The `LLMConfig` object (from `crawl4ai.types` or `crawl4ai.async_configs`) is crucial for telling Crawl4AI which LLM to use and how to interact with it.
            ```python
            from crawl4ai import LLMConfig

            # Example for OpenAI
            openai_config = LLMConfig(
                provider="openai/gpt-4o-mini", # Or "openai/gpt-3.5-turbo", etc.
                api_token="sk-YOUR_OPENAI_API_KEY", # Best practice: use os.environ.get("OPENAI_API_KEY")
                # Optional parameters:
                # temperature=0.7, 
                # max_tokens=1024 
            )

            # Example for a local Ollama model
            ollama_config = LLMConfig(
                provider="ollama/llama3", # Assumes Ollama is running and llama3 model is pulled
                api_token=None, # Not needed for local Ollama by default
                base_url="http://localhost:11434" # Default Ollama API endpoint
            )

            # Example for Groq
            groq_config = LLMConfig(
                provider="groq/llama3-8b-8192",
                api_token=os.environ.get("GROQ_API_KEY")
            )
            ```
            *   **`provider` (str):** Specifies the LLM provider and model (e.g., `"openai/gpt-4o-mini"`, `"ollama/llama3"`, `"groq/llama3-8b-8192"`). Crawl4AI uses LiteLLM under the hood, supporting a wide range of models.
            *   **`api_token` (Optional[str]):** Your API key for the chosen provider. For local models like Ollama, this is often not needed.
                *   **Best Practice:** Store API keys in environment variables (e.g., `os.environ.get("OPENAI_API_KEY")`) rather than hardcoding them.
            *   **`base_url` (Optional[str]):** For self-hosted LLMs or providers with custom API endpoints (like local Ollama), specify the base URL of the API.
            *   **LLM Behavior Parameters:**
                *   `temperature` (Optional[float]): Controls randomness. Lower values (e.g., 0.2) make output more deterministic/focused; higher values (e.g., 0.8) make it more creative. For extraction, lower temperatures are usually preferred.
                *   `max_tokens` (Optional[int]): Maximum number of tokens to generate in the completion.
                *   `top_p` (Optional[float]): Nucleus sampling. An alternative to temperature.
                *   `frequency_penalty` (Optional[float]), `presence_penalty` (Optional[float]): Penalize new tokens based on their existing frequency or presence in the text so far, influencing topic diversity.
            *   **Choosing Parameters for Extraction:** For structured data extraction, you generally want the LLM to be factual and stick to the provided schema. Good starting points:
                *   `temperature`: 0.0 to 0.3
                *   `max_tokens`: Sufficient to cover your expected output size.

        *   4.2.3. The Art of the `instruction`: Guiding the LLM
            The `instruction` string you provide to `LLMExtractionStrategy` is critical. It's your primary way of telling the LLM what you want.
            *   **Why Clarity is Paramount:** LLMs are powerful but work best with clear, specific, and unambiguous instructions. Vague instructions lead to inconsistent or incorrect results.
            *   **Elements of a Good Extraction Instruction:**
                1.  **State the Goal Clearly:** "Extract the following information about each product..."
                2.  **Define Output Format (if not using a rigid schema for `extraction_type="block"`):** "Provide the output as a list of bullet points." or "Return a JSON object with keys 'name' and 'price'." (Though for JSON, using a Pydantic schema is better).
                3.  **Provide Examples (Few-Shot Prompting):** Show the LLM exactly what you mean. This is one of the most effective ways to improve accuracy.
                    ```
                    Instruction: "Extract the name and price from the text. Example:
                    Text: 'The SuperWidget costs $19.99 and is amazing.'
                    Output: {'name': 'SuperWidget', 'price': 19.99}"
                    ```
                4.  **Specify Handling of Missing/Ambiguous Data:** "If a price is not found, use null for the price field." or "If multiple authors are listed, return them as a list of strings."
                5.  **Be Concise but Complete:** Avoid unnecessary jargon, but ensure all critical details are present.
            *   **Examples: Good vs. Improvable Instructions:**
                *   *Improvable:* "Get product data."
                *   *Good:* "Extract the product name, price (as a float, omitting currency symbols), and a brief 2-sentence summary for each product listed in the provided HTML. If a price is not available, set the price field to null. Return the data as a list of JSON objects, each adhering to the Pydantic schema provided."

        *   4.2.4. Defining Your Target Output: `schema` (Pydantic Models) vs. `extraction_type="block"`
            `LLMExtractionStrategy` supports two main modes for `extraction_type`:
            *   **Schema-based Extraction (`extraction_type="schema"`, default):**
                *   **How it works:** You provide a Pydantic model to the `schema` parameter. Crawl4AI converts this model to a JSON schema and includes it in the prompt, instructing the LLM to format its output accordingly.
                *   **Benefits:**
                    *   **Structured Output:** Ensures the LLM returns data in a predictable, usable JSON format.
                    *   **Type Safety:** Pydantic validates the LLM's output against your defined types.
                    *   **Clarity:** Makes the desired output structure explicit to the LLM.
                *   **Code Example: Using a Pydantic model to extract author, title, and publication date from an article.**
                    ```python
                    from pydantic import BaseModel, Field
                    from typing import Optional
                    from datetime import date

                    class ArticleMeta(BaseModel):
                        title: str = Field(..., description="The main title of the article")
                        author: Optional[str] = Field(None, description="The primary author of the article")
                        publication_date: Optional[date] = Field(None, description="The date the article was published, in YYYY-MM-DD format")

                    # In LLMExtractionStrategy:
                    # llm_strategy = LLMExtractionStrategy(
                    #     llm_config=my_llm_config,
                    #     schema=ArticleMeta.model_json_schema(), # Pass the JSON schema representation
                    #     instruction="Extract article metadata according to the provided JSON schema.",
                    #     extraction_type="schema" 
                    # )
                    ```
                    *Self-correction: The `schema` parameter expects the JSON schema dictionary, not the Pydantic model class itself directly. `ArticleMeta.model_json_schema()` provides this.*
                    *(Further correction based on `crawl4ai/extraction_strategy.py` `LLMExtractionStrategy`): The `schema` parameter actually *can* take a Pydantic `BaseModel` type or a dictionary. The internal logic handles converting the Pydantic model to a JSON schema if needed. So, `schema=ArticleMeta` would also work, or even `schema=ArticleMeta.model_json_schema()`.*
                    For clarity and directness with Pydantic:
                    ```python
                    # Corrected usage for LLMExtractionStrategy with Pydantic
                    llm_strategy = LLMExtractionStrategy(
                        llm_config=my_llm_config,
                        schema=ArticleMeta, # Pass the Pydantic model class directly
                        instruction="Extract article metadata according to the provided Pydantic model structure.",
                        extraction_type="schema"
                    )
                    ```

            *   **Block-based Extraction (`extraction_type="block"`):**
                *   **When to use:** Useful when you want the LLM to identify and extract larger, coherent blocks of text rather than specific, fine-grained fields. Examples:
                    *   The main textual content of an article, excluding ads and sidebars.
                    *   All user reviews for a product.
                    *   A specific section of a long document based on a topic.
                *   **How it differs:** Instead of a rigid schema, your `instruction` guides the LLM on what kind of blocks to look for. The output will typically be a list of strings, where each string is an extracted block.
                *   **Code Example: Extracting all paragraphs discussing "environmental impact" from an article.**
                    ```python
                    # llm_strategy = LLMExtractionStrategy(
                    #     llm_config=my_llm_config,
                    #     instruction="Extract all paragraphs from the text that discuss the environmental impact of the product. Each paragraph should be a separate item in the output list.",
                    #     extraction_type="block" 
                    # )
                    ```
                    The `extracted_content` would then be a JSON string representing a list of text blocks, e.g., `["Paragraph 1 about impact...", "Another paragraph..."]`.

        *   4.2.5. Managing LLM Context: `ChunkingStrategy` in Action
            The `LLMExtractionStrategy` has two key parameters for controlling how it uses the `ChunkingStrategy`:
            *   **`chunk_token_threshold` (int, default from `config.CHUNK_TOKEN_THRESHOLD`):** This is the target maximum size (in tokens, roughly) for each chunk sent to the LLM. The `ChunkingStrategy` will try to create chunks that don't exceed this.
            *   **`overlap_rate` (float, default from `config.OVERLAP_RATE`):** This determines how much overlap there should be between consecutive chunks. An overlap (e.g., 0.1 for 10%) can help ensure that information at the boundaries of chunks isn't missed.
            *   **Strategies for Choosing Values:**
                *   Consult your LLM's documentation for its maximum context window size. Set `chunk_token_threshold` safely below this (e.g., 70-80% of the max).
                *   A small `overlap_rate` (e.g., 0.05 to 0.2) is often beneficial. Too much overlap increases redundant processing and cost.
                *   If your chosen `ChunkingStrategy` (like `RegexChunking` by paragraphs) naturally creates chunks much smaller than the `chunk_token_threshold`, the threshold might not be hit often, but it still acts as an upper bound.
            *   **Interaction with `ChunkingStrategy` implementations:**
                *   **`RegexChunking` (default for `LLMExtractionStrategy`):** It will first split the input document by its regex patterns (e.g., newlines, paragraphs). Then, it will try to merge these smaller pieces into chunks that are close to, but not exceeding, `chunk_token_threshold`, incorporating the `overlap_rate`.
                *   **`IdentityChunking`:** This strategy ignores `chunk_token_threshold` and `overlap_rate` and passes the content as a single chunk. Use this if your content is already appropriately sized or if your LLM handles very large contexts well for your task.
            *   **Code Example: Setting up chunking for a long article to be summarized by an LLM.**
                ```python
                from crawl4ai.chunking_strategy import RegexChunking
                # Assuming my_llm_config is defined
                
                # A chunker that aims for ~1500 token chunks with 10% overlap
                custom_chunker = RegexChunking(
                    # RegexChunking specific params can be set here if needed, 
                    # but LLMExtractionStrategy's params often suffice.
                )

                llm_summarizer_strategy = LLMExtractionStrategy(
                    llm_config=my_llm_config,
                    instruction="Summarize the following text block in 3 key bullet points.",
                    extraction_type="block", # We want blocks of summaries
                    chunking_strategy=custom_chunker, # Explicitly set if not default
                    chunk_token_threshold=1500, 
                    overlap_rate=0.1
                )
                ```

        *   4.2.6. Workflow Walkthrough:
            *   **Step 1: Define Your Extraction Goal and Target Schema/Output:**
                *   What specific information do you need? (e.g., product names, prices, features).
                *   If using `extraction_type="schema"`, create a Pydantic model.
                *   If using `extraction_type="block"`, define what characterizes a "block" you want.
            *   **Step 2: Configure `LLMConfig` and `LLMExtractionStrategy`:**
                *   Choose your LLM provider and model in `LLMConfig`.
                *   Set API keys and any custom `base_url`.
                *   Craft a clear `instruction` for `LLMExtractionStrategy`.
                *   Provide the `schema` (Pydantic model) or set `extraction_type="block"`.
                *   Configure `chunk_token_threshold`, `overlap_rate`, and select a `chunking_strategy` if the default isn't suitable.
            *   **Step 3: Integrate with `CrawlerRunConfig`:**
                ```python
                run_config = CrawlerRunConfig(
                    extraction_strategy=llm_strategy_instance,
                    # ... other run_config settings ...
                )
                ```
            *   **Step 4: Run the Crawl and Parse `extracted_content`:**
                ```python
                # result = await crawler.arun(url="...", config=run_config)
                # if result.success and result.extracted_content:
                #     try:
                #         extracted_data = json.loads(result.extracted_content)
                #         # Process extracted_data (which will be a list of dicts if schema-based,
                #         # or list of strings if block-based)
                #     except json.JSONDecodeError:
                #         print("LLM did not return valid JSON.")
                ```
            *   **Step 5: Analyze `TokenUsage`:**
                After the extraction (especially during development), inspect the `TokenUsage` object from the `LLMExtractionStrategy` instance to understand costs.
                ```python
                # llm_strategy_instance.show_usage() # Prints a summary
                # total_prompt_tokens = llm_strategy_instance.total_usage.prompt_tokens
                ```

        *   4.2.7. Code Example: Extracting Key Highlights from News Articles
            ```python
            import asyncio
            import json
            import os
            from pydantic import BaseModel, Field
            from typing import List, Optional
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, LLMConfig
            from crawl4ai.extraction_strategy import LLMExtractionStrategy
            from crawl4ai.chunking_strategy import RegexChunking
            from crawl4ai.cache_manager import CacheMode

            class ArticleHighlight(BaseModel):
                highlight: str = Field(..., description="A key highlight or main point from the article.")
                category: Optional[str] = Field(None, description="A potential category for this highlight (e.g., Technology, Politics, Sports)")

            class ArticleHighlights(BaseModel):
                article_title: Optional[str] = Field(None, description="The main title of the article, if identifiable.")
                highlights: List[ArticleHighlight] = Field(..., description="A list of 3-5 key highlights from the article.")

            async def extract_article_highlights():
                # Ensure OPENAI_API_KEY is set in your environment
                if not os.getenv("OPENAI_API_KEY"):
                    print("OPENAI_API_KEY environment variable not set. Skipping LLM example.")
                    return

                llm_config = LLMConfig(
                    provider="openai/gpt-3.5-turbo", # More cost-effective for this example
                    api_token=os.getenv("OPENAI_API_KEY"),
                    temperature=0.2
                )

                extraction_strategy = LLMExtractionStrategy(
                    llm_config=llm_config,
                    schema=ArticleHighlights, # Pass the Pydantic model class
                    instruction="From the provided news article content, identify the main title and extract 3 to 5 key highlights. For each highlight, also try to assign a general category.",
                    extraction_type="schema",
                    chunking_strategy=RegexChunking(), # Default, but explicit here
                    chunk_token_threshold=2000, # Adjust based on article length and model
                    overlap_rate=0.1,
                    input_format="markdown" # LLMs often work well with clean Markdown
                )

                browser_config = BrowserConfig(headless=True, user_agent_mode="random") # Use a real user agent
                run_config = CrawlerRunConfig(
                    extraction_strategy=extraction_strategy,
                    cache_mode=CacheMode.BYPASS, # Fresh crawl for demo
                    word_count_threshold=50 # Ensure we have some content
                )

                # A news article known for having decent text content
                news_url = "https://www.nbcnews.com/tech/tech-news" 

                async with AsyncWebCrawler(config=browser_config) as crawler:
                    print(f"Crawling {news_url} to extract highlights...")
                    result = await crawler.arun(url=news_url, config=run_config)

                if result.success and result.extracted_content:
                    try:
                        data = json.loads(result.extracted_content)
                        # Since we expect a single ArticleHighlights object from the whole page
                        if isinstance(data, list) and len(data) > 0: 
                             # LiteLLM might wrap single objects in a list if schema is complex, take first.
                            article_data = ArticleHighlights.model_validate(data[0])
                        elif isinstance(data, dict):
                            article_data = ArticleHighlights.model_validate(data)
                        else:
                            raise ValueError("Unexpected data format from LLM")

                        print(f"\nExtracted Highlights for: {article_data.article_title or 'Unknown Title'}")
                        for hl_obj in article_data.highlights:
                            print(f"  - [{hl_obj.category or 'General'}] {hl_obj.highlight}")
                        
                        extraction_strategy.show_usage() # Show token usage

                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Error parsing LLM output: {e}")
                        print("Raw LLM output:", result.extracted_content)
                elif result.success and not result.extracted_content:
                    print("LLM extraction returned no content. The page might have been too short or content unsuitable.")
                else:
                    print(f"Failed to crawl or extract: {result.error_message}")

            if __name__ == "__main__":
                asyncio.run(extract_article_highlights())
            ```

        *   4.2.8. Understanding and Optimizing Costs: The `TokenUsage` Model
            When using LLMs, especially commercial APIs, tracking token usage is vital for cost management. The `TokenUsage` model (from `crawl4ai.models`) stores this information.
            *   **Fields:**
                *   `prompt_tokens` (int): Number of tokens in the input prompt sent to the LLM.
                *   `completion_tokens` (int): Number of tokens in the output generated by the LLM.
                *   `total_tokens` (int): Sum of prompt and completion tokens.
                *   `prompt_tokens_details`, `completion_tokens_details` (Optional[dict]): Provider-specific detailed token counts if available.
            *   **How to Interpret:** After an `LLMExtractionStrategy` run, you can access `strategy_instance.total_usage` for aggregated counts across all chunks/calls, or `strategy_instance.usages` for a list of `TokenUsage` objects per call.
                ```python
                # After running the strategy
                llm_strategy.show_usage() 
                # print(f"Total prompt tokens: {llm_strategy.total_usage.prompt_tokens}")
                # print(f"Total completion tokens: {llm_strategy.total_usage.completion_tokens}")
                ```
            *   **Strategies for Reducing Token Consumption:**
                1.  **Precise Prompts/Instructions:** Shorter, more focused prompts consume fewer tokens.
                2.  **Efficient Chunking:** Optimize `chunk_token_threshold` and `overlap_rate`. Avoid overly small chunks (too many API calls) or excessive overlap.
                3.  **Pre-filtering Content:** If possible, use non-LLM methods (CSS, XPath) to isolate the most relevant sections of HTML *before* sending to the LLM. Pass this cleaner, shorter text.
                4.  **Choose Smaller/Cheaper Models:** For simpler extraction tasks, a less powerful (and cheaper) model might suffice (e.g., GPT-3.5-turbo instead of GPT-4, or a smaller Llama variant).
                5.  **Limit `max_tokens` in `LLMConfig`:** If you know your expected output is short, set a reasonable `max_tokens` to prevent the LLM from generating overly verbose responses.
                6.  **Ask for Concise Output:** Instruct the LLM to be brief or to only return the specified fields.

        *   4.2.9. Best Practices for `LLMExtractionStrategy`
            *   **Iterative Prompt Refinement:** Start with a simple prompt and schema. Test it. Refine the prompt based on the LLM's output until you get the desired results. This is often a trial-and-error process.
            *   **Few-Shot Examples:** Including 2-3 examples of desired input/output *within your instruction* can dramatically improve LLM performance and adherence to your schema.
            *   **Specificity is Key:** The more specific your instruction and schema (especially field descriptions in Pydantic models), the better the LLM will understand your intent.
            *   **Model Selection:** Different LLMs excel at different tasks. Some are better at following complex instructions, others at creative generation. Experiment if results aren't optimal. For pure extraction into a schema, models fine-tuned for function calling or JSON mode are often best.
            *   **Handle Failures Gracefully:** LLM outputs can sometimes be unpredictable. Implement try-except blocks for JSON parsing and Pydantic validation. Consider fallback logic if extraction fails.
            *   **Use `input_format` Wisely:**
                *   `input_format="markdown"` (default for `LLMExtractionStrategy` if `CrawlerRunConfig.markdown_generator` is set): Good for general text extraction, as Markdown is cleaner than raw HTML.
                *   `input_format="html"`: Useful if the LLM needs to see HTML tags (e.g., for extracting attributes or if table structure is critical and Markdown conversion loses it).
                *   `input_format="text"`: For when you only care about the raw textual content.
                *   `input_format="fit_html"`: Uses a preprocessed HTML more suitable for schema extraction, usually smaller.

        *   4.2.10. Troubleshooting LLM Extraction:
            *   **LLM Not Following Instructions / Incorrect Format:**
                *   *Cause:* Prompt too vague, ambiguous, or complex. LLM might not support forced JSON mode well (though LiteLLM tries to handle this).
                *   *Solution:* Simplify prompt. Add clear examples (few-shot). Use a Pydantic schema to strongly guide JSON output. Try a different model. Ensure `force_json_response=True` in `LLMExtractionStrategy` if your provider supports it robustly or if you are using a Pydantic schema.
            *   **Incorrect or Incomplete Data:**
                *   *Cause:* Instruction missing details, LLM misunderstanding, content chunking splitting relevant info.
                *   *Solution:* Refine instruction. Check `chunk_token_threshold` and `overlap_rate`. Ensure field descriptions in Pydantic schema are clear.
            *   **Handling Hallucinations or Fabricated Information:**
                *   *Cause:* LLMs can sometimes "invent" data if it's not present or if the prompt is leading.
                *   *Solution:* Instruct the LLM to use `null` or a specific placeholder (e.g., "N/A") for missing fields. Lower the `temperature`. Validate extracted data against known facts if possible.
            *   **Schema Validation Errors (Pydantic):**
                *   *Cause:* LLM output doesn't match the Pydantic model's types or constraints.
                *   *Solution:* Check the LLM's raw JSON output. Refine the prompt to better match the schema. Make Pydantic fields `Optional` if data might be missing.
            *   **API Errors / Rate Limits:**
                *   *Cause:* Invalid API key, insufficient credits, hitting provider rate limits.
                *   *Solution:* Check API key and account status. Implement backoff/retry logic (Crawl4AI does some of this internally). Reduce request frequency.

## 5. Choosing Your Extraction Weapon: A Decision Guide
    * 5.1. Factors to Consider:
        *   **Structure and Consistency of Target Data:**
            *   *Well-structured, consistent HTML?* => Favor Non-LLM (CSS, XPath).
            *   *Messy, inconsistent, or unstructured text?* => Favor LLM.
        *   **Complexity of Information to be Extracted:**
            *   *Simple fields, direct attributes?* => Non-LLM.
            *   *Nuanced relationships, summaries, sentiment, inferred data?* => LLM.
        *   **Development Time vs. Runtime Cost:**
            *   *Quick prototype needed, site structure complex/unknown?* => LLM can be faster to start.
            *   *High volume, long-term, cost-sensitive?* => Non-LLM, once set up, is cheaper to run.
        *   **Need for Semantic Understanding vs. Pattern Matching:**
            *   *Data identifiable by patterns (emails, dates, SKUs)?* => `RegexExtractionStrategy`.
            *   *Data requires understanding context or meaning?* => LLM.
        *   **Scalability and Performance Requirements:**
            *   *Need to scrape thousands of pages per minute?* => Non-LLM strategies are inherently faster. LLM API calls add latency.
            *   *Occasional or smaller-scale extraction?* => LLM latency might be acceptable.
        *   **Maintainability:**
            *   *Site changes frequently?* => LLM prompts *might* be more resilient than specific CSS/XPath selectors, but both can break. Regex is often robust if the underlying text pattern is stable.
        *   **Team Expertise:**
            *   *Strong in CSS/XPath/Regex?* => Leverage those skills with Non-LLM.
            *   *More comfortable with natural language prompts?* => LLM might be a good fit.

    * 5.2. Decision Table: Non-LLM vs. LLM Strategies
        | Feature                | Non-LLM (CSS, XPath, Regex)                       | LLM-Based (`LLMExtractionStrategy`)            |
        | ---------------------- | ------------------------------------------------- | ---------------------------------------------- |
        | **Best For**           | Well-structured, consistent HTML; pattern matching | Unstructured/complex data; semantic understanding |
        | **Development Speed**  | Slower if selectors are complex; faster for regex | Faster for initial prototype with good prompts    |
        | **Runtime Speed**      | Very Fast                                         | Slower (API latency, model inference)        |
        | **Runtime Cost**       | Negligible (CPU/Mem)                              | Can be significant (API calls, GPU if local)   |
        | **Accuracy**           | High if selectors are good; precise for regex   | Depends on prompt, model, content quality    |
        | **Resilience to Change**| Brittle to HTML changes (CSS/XPath)               | Potentially more resilient; prompt dependent   |
        | **Complexity Handled** | Lower for semantic, higher for pattern (regex)    | High for semantic and complex relationships    |
        | **Schema Enforcement** | Via schema definition                             | Strong via Pydantic schema; flexible otherwise |

    * 5.3. Hybrid Approaches: Combining the Best of Both Worlds
        Often, the most robust and efficient solution involves a hybrid approach:
        *   **Example 1: CSS/XPath Pre-filtering for LLM:**
            Use CSS or XPath selectors to isolate the main content block of an article (e.g., `<article class="main-story">`). Pass only this cleaned, focused HTML/Markdown to the `LLMExtractionStrategy`.
            *   *Why?* Reduces the amount of text the LLM needs to process, saving tokens (cost/latency) and potentially improving accuracy by removing noise.
            ```python
            # Conceptual - how you might structure the thought process
            # 1. Use AsyncWebCrawler with a CrawlerRunConfig that only does basic scraping (no LLM extraction yet)
            #    and uses a css_selector to get the main content.
            # 2. Get the result.cleaned_html (which is now just the main content).
            # 3. Pass this cleaned_html to a separate LLMExtractionStrategy call.
            # (Crawl4AI doesn't directly support "chaining" strategies in one run_config,
            # so this would involve multiple processing steps orchestrated by your code.)
            ```
        *   **Example 2: Regex for Simple Entities, LLM for Complex:**
            Use `RegexExtractionStrategy` to quickly and cheaply pull out all email addresses, phone numbers, and dates. Then, use `LLMExtractionStrategy` on the remaining text (or the full text) to extract more nuanced information like "the primary topic of discussion" or "the relationship between person A and company B."
        *   **How to Implement Hybrid:** Typically, you would run the crawl in stages or have a custom orchestrator.
            1.  First pass: Use a non-LLM strategy (e.g., `JsonCssExtractionStrategy` to get specific blocks, or just rely on `result.markdown`).
            2.  Second pass: Take the output from the first pass and feed it to an `LLMExtractionStrategy` (or another non-LLM strategy). You might do this by invoking the `extract` method of the second strategy directly with the content from the first.

## 6. The `NoExtractionStrategy`: When You Just Need the HTML/Markdown
    * 6.1. Purpose: Disabling structured data extraction.
        The `NoExtractionStrategy` (from `crawl4ai.extraction_strategy`) is a placeholder strategy that, as its name suggests, performs no actual data extraction. `result.extracted_content` will be `None` or an empty representation.
    * 6.2. Use Cases:
        *   **Archiving Raw Web Content:** If your goal is simply to fetch and store the raw HTML or the cleaned Markdown of pages.
        *   **Markdown Generation is Primary:** If you're primarily using Crawl4AI for its HTML-to-Markdown conversion capabilities and don't need structured data beyond that.
        *   **Feeding to External Pipelines:** If you have a separate, downstream system that will handle the data extraction and you just need Crawl4AI to fetch and pre-process the web pages.
        *   **Baseline/Testing:** Useful as a baseline when developing or debugging other parts of your crawling pipeline.
    * 6.3. How to Configure It.
        ```python
        from crawl4ai import CrawlerRunConfig
        from crawl4ai.extraction_strategy import NoExtractionStrategy

        run_config_no_extraction = CrawlerRunConfig(
            extraction_strategy=NoExtractionStrategy()
        )
        # When crawler.arun(url="...", config=run_config_no_extraction) is called,
        # result.extracted_content will likely be None.
        # You would primarily use result.html or result.markdown.
        ```

## 7. Integrating Extraction into Your Crawls
    * 7.1. The Role of `CrawlerRunConfig`
        The `CrawlerRunConfig` object is central to customizing how each individual crawl operation behaves. For extraction, its key parameters are:
        *   **`extraction_strategy: Optional[ExtractionStrategy]`:** You assign an instance of your chosen extraction strategy here (e.g., `JsonCssExtractionStrategy(...)`, `LLMExtractionStrategy(...)`). If `None`, no structured extraction specific to this strategy is performed, but default behaviors like Markdown generation might still occur.
        *   **`chunking_strategy: Optional[ChunkingStrategy]`:** Primarily used by `LLMExtractionStrategy`. If you want to use a non-default chunker (other than `RegexChunking`), you instantiate it and assign it here.
        *   **`input_format` (within `LLMExtractionStrategy`):** While not directly in `CrawlerRunConfig`, the `LLMExtractionStrategy` itself takes an `input_format` parameter (`"markdown"`, `"html"`, `"text"`, `"fit_html"`) that determines what version of the page content is fed to the LLM. `CrawlerRunConfig`'s `markdown_generator` influences the quality of the Markdown available.

    * 7.2. Data Flow: From Web Page to Extracted Data
        Here's a simplified conceptual data flow:
        ```
        [Web Page URL]
             |
             v
        AsyncWebCrawler.arun(config=CrawlerRunConfig)
             |
             v
        [Browser Engine (Playwright)] -- Fetches HTML, executes JS --> [Raw HTML]
             |
             v
        CrawlerRunConfig.scraping_strategy (e.g., WebScrapingStrategy)
             |--> Cleans HTML --> [Cleaned HTML]
             |--> (Optional) Generates Markdown via CrawlerRunConfig.markdown_generator --> [Markdown]
             |--> Extracts Links, Basic Media --> [Links, Media Objects]
             |
             v
        (If LLMExtractionStrategy with chunking)
        CrawlerRunConfig.chunking_strategy / LLMExtractionStrategy.chunking_strategy
             |--> Chunks the input_format content (e.g., Markdown) --> [List of Text Chunks]
             |
             v
        CrawlerRunConfig.extraction_strategy (e.g., LLMExtractionStrategy or JsonCssExtractionStrategy)
             |--> Processes HTML/Markdown/Chunks --> [Structured Data (JSON String)]
             |
             v
        [CrawlResult]
             - .html (raw)
             - .cleaned_html
             - .markdown (object with .raw_markdown, .fit_markdown etc.)
             - .extracted_content (JSON string from extraction_strategy)
             - .links
             - .media
        ```

    * 7.3. Complete Code Example: A Full Crawl with a Chosen Extraction Strategy
        ```python
        import asyncio
        import json
        from crawl4ai import (
            AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, LLMConfig, CacheMode
        )
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
        from crawl4ai.chunking_strategy import RegexChunking
        from pydantic import BaseModel, Field
        from typing import List, Optional

        # Define a Pydantic schema for LLM extraction
        class NewsSummary(BaseModel):
            title: str = Field(description="The main headline of the news article.")
            summary_points: List[str] = Field(description="A list of 2-3 key bullet points summarizing the article.")

        async def comprehensive_extraction_example():
            # --- Configuration ---
            browser_config = BrowserConfig(
                headless=True,
                user_agent_mode="random" # Use a realistic user agent
            )

            # Non-LLM: CSS-based extraction schema for basic info
            basic_info_schema = {
                "name": "PageLinks",
                "baseSelector": "a[href]", # Get all links
                "fields": [
                    {"name": "text", "selector": "self", "type": "text"}, # 'self' refers to the baseSelector element
                    {"name": "href", "selector": "self", "type": "attribute", "attribute": "href"}
                ]
            }
            css_extraction_strategy = JsonCssExtractionStrategy(schema=basic_info_schema)

            # LLM-based extraction for summarization (ensure API key is set for OpenAI)
            llm_config_openai = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY"))
            if not llm_config_openai.api_token: # Fallback to a local/free model if no key
                print("Warning: OPENAI_API_KEY not found. LLM summarization might be skipped or use a different model if configured.")
                # Optionally, configure a fallback like Ollama here if you have it running
                # llm_config_ollama = LLMConfig(provider="ollama/llama2", base_url="http://localhost:11434")
                # llm_summarization_strategy = LLMExtractionStrategy(...) using llm_config_ollama
                llm_summarization_strategy = None # Or a NoExtractionStrategy
            else:
                llm_summarization_strategy = LLMExtractionStrategy(
                    llm_config=llm_config_openai,
                    schema=NewsSummary, # Use Pydantic model
                    instruction="Analyze the provided news article content (likely in Markdown). Extract its main title and provide 2-3 key summary bullet points.",
                    extraction_type="schema",
                    chunking_strategy=RegexChunking(), # Default, good for articles
                    chunk_token_threshold=1500,
                    input_format="markdown"
                )
            
            # --- Create CrawlerRunConfig ---
            # We'll demonstrate two runs: one with CSS, one with LLM
            run_config_css = CrawlerRunConfig(
                extraction_strategy=css_extraction_strategy,
                cache_mode=CacheMode.BYPASS
            )
            run_config_llm = CrawlerRunConfig(
                extraction_strategy=llm_summarization_strategy,
                cache_mode=CacheMode.BYPASS
            )

            target_url = "https://www.bbc.com/news" # Example news site

            # --- Execute Crawl ---
            async with AsyncWebCrawler(config=browser_config) as crawler:
                print(f"--- Running CSS Extraction on {target_url} ---")
                result_css = await crawler.arun(url=target_url, config=run_config_css)
                if result_css.success and result_css.extracted_content:
                    links = json.loads(result_css.extracted_content)
                    print(f"Found {len(links)} links. First 3:")
                    for link_data in links[:3]:
                        print(f"  Text: {link_data.get('text', '')[:30]}..., Href: {link_data.get('href')}")
                else:
                    print(f"CSS Extraction failed or no content: {result_css.error_message}")

                if llm_summarization_strategy: # Only run if LLM is configured
                    print(f"\n--- Running LLM Summarization on {target_url} (using its Markdown) ---")
                    # The LLM strategy will use the Markdown from the previous crawl result if input_format is markdown
                    # or it would re-fetch if it was a different format or strategy.
                    # For simplicity here, we assume the crawler internally handles content reuse or re-fetch as needed
                    # based on the input_format.
                    # A more explicit way would be to pass result_css.markdown to llm_summarization_strategy.extract()
                    
                    result_llm = await crawler.arun(url=target_url, config=run_config_llm)
                    if result_llm.success and result_llm.extracted_content:
                        try:
                            summary_data_list = json.loads(result_llm.extracted_content)
                            # LLM might return a list if it finds multiple "articles" or if schema is treated as listable
                            if summary_data_list and isinstance(summary_data_list, list):
                                summary_data = NewsSummary.model_validate(summary_data_list[0]) # Take first for demo
                                print(f"Title: {summary_data.article_title}")
                                print("Summary Points:")
                                for point in summary_data.summary_points:
                                    print(f"  - {point}")
                            elif summary_data_list and isinstance(summary_data_list, dict): # Single object returned
                                summary_data = NewsSummary.model_validate(summary_data_list)
                                print(f"Title: {summary_data.article_title}")
                                print("Summary Points:")
                                for point in summary_data.summary_points:
                                    print(f"  - {point}")

                        except (json.JSONDecodeError, Exception) as e: # Broader exception for Pydantic validation
                            print(f"Error parsing LLM summary output: {e}")
                            print("Raw LLM output:", result_llm.extracted_content)
                        llm_summarization_strategy.show_usage()
                    else:
                        print(f"LLM Summarization failed or no content: {result_llm.error_message}")
                else:
                    print("\nLLM Summarization strategy not configured, skipping that part.")


        if __name__ == "__main__":
            asyncio.run(comprehensive_extraction_example())
        ```

## 8. Specialized Extraction: Working with PDF Content
    * 8.1. Understanding PDF Processing in Crawl4AI
        Crawl4AI provides dedicated strategies for handling PDF documents, as PDFs are a common format for reports, papers, and other important web content. The key components are:
        *   **`PDFCrawlerStrategy` (in `crawl4ai.processors.pdf.__init__.py`):**
            *   **Role:** This strategy is used as the `crawler_strategy` in `AsyncWebCrawler` when you intend to directly process a PDF URL. It doesn't crawl HTML pages to find PDFs; rather, it's designed to fetch a document *known* to be a PDF (or a URL that might serve a PDF). It primarily handles the downloading of the PDF content. The actual parsing is delegated to a "scraping" strategy.
            *   It sets the `Content-Type` in the response headers to `application/pdf` to signal to subsequent strategies that this is PDF content.
        *   **`PDFContentScrapingStrategy` (in `crawl4ai.processors.pdf.__init__.py`):**
            *   **Role:** This strategy is used as the `scraping_strategy` in `CrawlerRunConfig` when you're targeting PDFs. It takes the raw PDF bytes (fetched by `PDFCrawlerStrategy` or provided directly) and processes them.
            *   **Leveraging `NaivePDFProcessorStrategy`:** Internally, `PDFContentScrapingStrategy` uses `NaivePDFProcessorStrategy` (from `crawl4ai.processors.pdf.processor`) to do the heavy lifting of PDF parsing.
            *   **`NaivePDFProcessorStrategy` (from `crawl4ai.processors.pdf.processor`):** This is the workhorse. It uses the PyPDF2 library (and Pillow for images) to extract:
                *   **Text Content:** Page by page.
                *   **Images:** Can extract embedded images.
                *   **Metadata:** Document properties like title, author, creation date.
            *   **Key Outputs in `ScrapingResult`:** When `PDFContentScrapingStrategy` is used, the `ScrapingResult` object (which is then available as `result.cleaned_html` or `result.markdown` to the `ExtractionStrategy`, and also structured in `result.metadata` and `result.media`) will be populated as follows:
                *   `result.cleaned_html`: Contains an HTML representation of the PDF content, with each page typically wrapped in a `<div class="pdf-page">`. Images might be embedded as base64 or linked if saved locally.
                *   `result.markdown`: A Markdown representation of the PDF text content (via `DefaultMarkdownGenerator` applied to the HTML from `cleaned_html`).
                *   `result.metadata`: A dictionary containing metadata extracted from the PDF, mirroring the `PDFMetadata` model (title, author, pages, etc.).
                *   `result.media`: Will contain image information under `media["images"]` if image extraction is enabled.

    * 8.2. Configuring PDF Extraction
        Configuration options are primarily set on the `PDFContentScrapingStrategy` (which passes them to `NaivePDFProcessorStrategy`).
        *   **`extract_images` (bool, default: `False`):** Set to `True` to attempt to extract images from the PDF. This can increase processing time.
        *   **`save_images_locally` (bool, default: `False`):** If `extract_images` is `True`, setting this to `True` will save extracted images to disk.
        *   **`image_save_dir` (Optional[str], default: `None`):** Specifies the directory to save images if `save_images_locally` is `True`. If `None`, a temporary directory might be used by `NaivePDFProcessorStrategy` (or it might use a default configured path if the strategy has one). It's best to provide an explicit path.
        *   **`image_dpi` (int, default: `144` in `NaivePDFProcessorStrategy`):** Dots Per Inch for rendered images (if PDF pages are rendered as images, which is not the primary mode of `NaivePDFProcessorStrategy`'s image extraction; it usually extracts existing embedded images. This DPI might be more relevant for future strategies that render pages). For `NaivePDFProcessorStrategy`, this DPI is used if it falls back to rendering pages as images, for example if direct image extraction fails or for specific image types.
        *   **`batch_size` (int, default: `4` in `NaivePDFProcessorStrategy`):** Controls how many pages are processed in parallel by worker threads when using `process_batch`. This can speed up processing of multi-page PDFs.

        ```python
        from crawl4ai.processors.pdf import PDFContentScrapingStrategy

        pdf_scraping_config = PDFContentScrapingStrategy(
            extract_images=True,
            save_images_locally=True,
            image_save_dir="./pdf_extracted_images", # Ensure this directory exists
            # image_dpi=200 # Higher DPI for better quality, larger files
            batch_size=8    # Process more pages in parallel
        )
        ```

    * 8.3. Workflow: Extracting Content from PDFs
        1.  **Set `PDFCrawlerStrategy` in `AsyncWebCrawler`:** This tells the crawler to use the PDF-specific fetching logic.
            ```python
            from crawl4ai.processors.pdf import PDFCrawlerStrategy
            # crawler = AsyncWebCrawler(crawler_strategy=PDFCrawlerStrategy())
            ```
        2.  **Set `PDFContentScrapingStrategy` in `CrawlerRunConfig`:** This tells the scraping phase to use the PDF parser.
            ```python
            # run_config = CrawlerRunConfig(scraping_strategy=pdf_scraping_config)
            ```
        3.  **Run the Crawl:**
            ```python
            # result = await crawler.arun(url="https://example.com/mydoc.pdf", config=run_config)
            ```
        4.  **Accessing Extracted Data:**
            *   **Text:** `result.markdown.raw_markdown` (often the most useful for LLMs) or iterate through `result.cleaned_html` to get page-specific HTML.
            *   **Metadata:** `result.metadata` will be a dictionary (e.g., `result.metadata.get("title")`). This comes from `PDFProcessResult.metadata`.
            *   **Images:** `result.media["images"]` will be a list of image dictionaries if `extract_images=True`. Each image dict might contain `src` (path if saved locally, or base64 data URI), `alt`, `page` (page number where image was found).

    * 8.4. Code Example: Crawling a PDF and Extracting its Text and Metadata
        ```python
        import asyncio
        import os
        from pathlib import Path
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        from crawl4ai.processors.pdf import PDFCrawlerStrategy, PDFContentScrapingStrategy

        async def crawl_and_extract_pdf():
            # Example PDF URL (replace with a real, accessible PDF URL for testing)
            # For this example, let's assume a local PDF file to avoid network dependency.
            # Create a dummy PDF for testing if you don't have one handy
            # (Actual PDF creation is outside Crawl4AI scope, this is just for the example)
            
            # For a real URL:
            # pdf_url = "https://arxiv.org/pdf/1706.03762.pdf" # "Attention is All You Need" paper
            
            # For a local file:
            dummy_pdf_path = Path("dummy_test.pdf")
            if not dummy_pdf_path.exists():
                 try:
                    from reportlab.pdfgen import canvas
                    c = canvas.Canvas(str(dummy_pdf_path))
                    c.drawString(100, 750, "Hello World. This is page 1 of a dummy PDF.")
                    c.showPage()
                    c.drawString(100, 750, "This is page 2 with an important keyword: Crawl4AI.")
                    c.save()
                    print(f"Created dummy PDF: {dummy_pdf_path.resolve()}")
                 except ImportError:
                    print("reportlab not installed. Cannot create dummy PDF. Please provide a real PDF URL or local path.")
                    return

            pdf_url = f"file://{dummy_pdf_path.resolve()}"


            # Configure PDF processing
            pdf_image_output_dir = Path("./pdf_images_output")
            pdf_image_output_dir.mkdir(parents=True, exist_ok=True)

            pdf_scraping = PDFContentScrapingStrategy(
                extract_images=True, 
                save_images_locally=True, 
                image_save_dir=str(pdf_image_output_dir)
            )

            # Configure crawler run
            pdf_run_config = CrawlerRunConfig(
                scraping_strategy=pdf_scraping,
                cache_mode=CacheMode.BYPASS # Ensure fresh processing for demo
            )

            # Use PDFCrawlerStrategy for direct PDF handling
            # Note: BrowserConfig is less relevant here if directly fetching PDF, 
            # but AsyncWebCrawler still needs it.
            browser_cfg = BrowserConfig(headless=True) 
            
            async with AsyncWebCrawler(
                config=browser_cfg, 
                crawler_strategy=PDFCrawlerStrategy() # Crucial for PDF URLs
            ) as crawler:
                print(f"Processing PDF: {pdf_url}")
                result = await crawler.arun(url=pdf_url, config=pdf_run_config)

            if result.success:
                print("\n--- PDF Processing Successful ---")
                print(f"URL Processed: {result.url}")
                
                # Access metadata
                if result.metadata:
                    print("\nMetadata:")
                    print(f"  Title: {result.metadata.get('title', 'N/A')}")
                    print(f"  Author: {result.metadata.get('author', 'N/A')}")
                    print(f"  Pages: {result.metadata.get('pages', 'N/A')}")

                # Access text (via Markdown)
                if result.markdown:
                    print(f"\nMarkdown Content (first 300 chars):\n{result.markdown.raw_markdown[:300]}...")
                
                # Access images
                if result.media and result.media.get("images"):
                    print(f"\nExtracted {len(result.media['images'])} image(s):")
                    for img_info in result.media["images"]:
                        print(f"  - Src: {img_info.get('src', 'N/A')} (Page: {img_info.get('page', 'N/A')})")
                else:
                    print("\nNo images extracted or found.")
            else:
                print(f"\n--- PDF Processing Failed ---")
                print(f"Error: {result.error_message}")

            # Clean up dummy PDF
            if dummy_pdf_path.exists():
                # dummy_pdf_path.unlink() # Commented out to allow inspection
                print(f"Dummy PDF at {dummy_pdf_path.resolve()} can be manually deleted.")


        if __name__ == "__main__":
            asyncio.run(crawl_and_extract_pdf())
        ```

    * 8.5. When to Combine PDF Processing with Other Extraction Strategies
        The output of `PDFContentScrapingStrategy` (specifically `result.markdown.raw_markdown` or `result.cleaned_html`) can be fed into *another* `ExtractionStrategy` for more refined data extraction.
        *   **Using `LLMExtractionStrategy` on PDF Text:**
            *   *Why:* PDFs often contain unstructured text. An LLM can summarize, answer questions, or extract specific entities from the PDF's textual content.
            *   *How:*
                1.  Crawl the PDF using `PDFCrawlerStrategy` and `PDFContentScrapingStrategy`.
                2.  Take `result.markdown.raw_markdown`.
                3.  Instantiate an `LLMExtractionStrategy` with your desired schema and instruction.
                4.  Call `llm_strategy.extract(url=pdf_url, html_content=result.markdown.raw_markdown)` (using `html_content` as the parameter name, even though it's Markdown here, or ensure your LLM strategy is configured for `input_format="markdown"`).
        *   **Applying `RegexExtractionStrategy` to PDF Text:**
            *   *Why:* To find specific patterns (emails, phone numbers, case IDs, etc.) within the extracted text of the PDF.
            *   *How:* Similar to the LLM approach, use the text output from PDF processing as input to `RegexExtractionStrategy.extract()`.

## 9. Advanced Customization: Building Your Own Strategies
    * 9.1. Implementing a Custom `ExtractionStrategy`
        *   9.1.1. Why Create a Custom Strategy?
            *   **Unsupported Data Formats:** You're dealing with a data format Crawl4AI doesn't natively understand (e.g., custom binary formats, obscure XML dialects, non-standard text encodings that need special pre-processing).
            *   **Proprietary Internal APIs:** Your target data comes from an internal system with a unique API response structure that doesn't map well to JSON/CSS/XPath.
            *   **Highly Domain-Specific Logic:** The extraction rules are too complex or specific to your domain to be easily expressed with general-purpose selectors or even LLM prompts (e.g., extracting data from scientific diagrams based on their visual components, which might require CV models).
            *   **Performance-Critical Custom Parsing:** For extremely high-volume scraping of a single, known format, a hand-tuned parser might outperform general tools.

        *   9.1.2. Key Steps:
            1.  **Inherit from `ExtractionStrategy`:**
                ```python
                from crawl4ai.extraction_strategy import ExtractionStrategy, LLMConfig # Assuming LLMConfig is needed
                from typing import List, Dict, Any
                
                class MyCustomExtractionStrategy(ExtractionStrategy):
                    # ...
                ```
            2.  **Implement `__init__` (Optional but common):**
                To accept any configuration your strategy needs.
                ```python
                # def __init__(self, my_param: str, **kwargs):
                #     super().__init__(**kwargs) # Pass kwargs for base class (like input_format)
                #     self.my_param = my_param
                ```
            3.  **Implement the `extract` method:** This is the core logic.
                ```python
                # def extract(self, url: str, html_content: str, *q, **kwargs) -> List[Dict[str, Any]]:
                #     # Your custom parsing logic here
                #     # html_content will be whatever 'input_format' you specified (e.g., 'html', 'markdown')
                #     # or the raw content if not specified.
                #     processed_data = []
                #     # ... parse html_content ...
                #     # Example:
                #     # if "special_keyword" in html_content:
                #     #     processed_data.append({"url": url, "found_keyword": True, "snippet": html_content[:100]})
                #     return processed_data
                ```
            4.  **Implement `run` method (Optional):**
                The base `ExtractionStrategy.run` method simply takes a list of `sections` (chunks) and calls `self.extract` on their concatenation. You might override `run` if:
                *   You want to process chunks in parallel.
                *   Your strategy inherently works on chunks and needs to aggregate results differently.
                *   You need to manage state across chunk processing.
                ```python
                # async def run(self, url: str, sections: List[str], *q, **kwargs) -> List[Dict[str, Any]]:
                #     # Example: Process sections in parallel (conceptual, requires async/threading)
                #     all_results = []
                #     # In a real async scenario, you'd use asyncio.gather or similar
                #     for section in sections:
                #         # Note: self.extract is not async by default in base class. 
                #         # If your extract is I/O bound and async, you can await it.
                #         # Otherwise, use to_thread or a ThreadPoolExecutor for true parallelism.
                #         # For simplicity, this example is synchronous.
                #         all_results.extend(self.extract(url, section, **kwargs)) 
                #     return all_results
                ```
                *Note:* The base `ExtractionStrategy.run` is synchronous. If your custom `extract` method is I/O bound and you want true parallelism in `run`, you'll need to handle `asyncio` or threading appropriately. The `LLMExtractionStrategy` has a more complex `run` method for handling LLM calls.

        *   9.1.3. Simple Code Example: A Custom Strategy to Extract All `<meta>` Tags
            ```python
            import asyncio
            from bs4 import BeautifulSoup
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
            from crawl4ai.extraction_strategy import ExtractionStrategy
            from typing import List, Dict, Any

            class MetaTagExtractor(ExtractionStrategy):
                def __init__(self, **kwargs):
                    # This strategy will work on HTML
                    super().__init__(input_format="html", **kwargs)

                def extract(self, url: str, html_content: str, *q, **kwargs) -> List[Dict[str, Any]]:
                    if not html_content:
                        return []
                    
                    soup = BeautifulSoup(html_content, 'lxml') # Or 'html.parser'
                    meta_tags_data = []
                    for tag in soup.find_all('meta'):
                        meta_info = {"url": url, "attributes": dict(tag.attrs)}
                        if tag.get("name"):
                            meta_info["name"] = tag.get("name")
                        if tag.get("property"):
                            meta_info["property"] = tag.get("property")
                        if tag.get("content"):
                            meta_info["content"] = tag.get("content")
                        meta_tags_data.append(meta_info)
                    return meta_tags_data

            async def main_custom_meta_extractor():
                strategy = MetaTagExtractor()
                run_config = CrawlerRunConfig(extraction_strategy=strategy)
                
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url="https://example.com", config=run_config)
                
                if result.success and result.extracted_content:
                    import json
                    meta_data = json.loads(result.extracted_content)
                    print(f"Extracted {len(meta_data)} meta tags:")
                    for tag_data in meta_data[:3]: # Print first 3
                        print(json.dumps(tag_data, indent=2))
                else:
                    print(f"Extraction failed: {result.error_message}")

            if __name__ == "__main__":
                asyncio.run(main_custom_meta_extractor())
            ```

    * 9.2. Implementing a Custom `ChunkingStrategy`
        *   9.2.1. When Default Chunkers Aren't Enough.
            *   **Domain-Specific Document Structures:** Your documents have clear semantic boundaries not easily captured by generic regex (e.g., chapters in a book, acts/scenes in a play, specific log entry formats).
            *   **Needing Semantic Boundaries:** You want to split text based on topic shifts or semantic coherence, which might require more advanced NLP techniques within your chunker (though this can be complex).
            *   **Table or List-Aware Chunking:** You have large tables or lists and want to ensure they are either kept whole within a chunk or split at sensible row/item boundaries, rather than arbitrarily in the middle of a cell or list item.
            *   **Fine-Grained Control Over Overlap:** You need a specific overlapping strategy (e.g., sentence-level overlap) not provided by the `overlap_rate` parameter of `LLMExtractionStrategy`.

        *   9.2.2. Key Steps:
            1.  **Inherit from `ChunkingStrategy`:**
                ```python
                from crawl4ai.chunking_strategy import ChunkingStrategy
                from typing import List
                
                class MyCustomChunker(ChunkingStrategy):
                    # ...
                ```
            2.  **Implement `__init__` (Optional):**
                To store any configuration for your chunker.
                ```python
                # def __init__(self, chunk_delimiter: str = "\n\n"):
                #     self.chunk_delimiter = chunk_delimiter
                ```
            3.  **Implement the `chunk` method:** This is where your custom chunking logic goes.
                ```python
                # def chunk(self, document: str) -> List[str]:
                #     # Your logic to split 'document' into a list of strings
                #     # Example:
                #     # return document.split(self.chunk_delimiter)
                #     pass
                ```

        *   9.2.3. Simple Code Example: A Chunking Strategy that Splits by `<h1>` Tags (assuming HTML input)
            This example demonstrates chunking HTML content. In practice, `LLMExtractionStrategy` usually receives Markdown or text, so you'd adapt this logic or ensure your `LLMExtractionStrategy.input_format` is set to `"html"`.
            ```python
            import asyncio
            from bs4 import BeautifulSoup
            from crawl4ai.chunking_strategy import ChunkingStrategy
            from crawl4ai.extraction_strategy import LLMExtractionStrategy # For context
            from crawl4ai import LLMConfig, CrawlerRunConfig, AsyncWebCrawler
            from typing import List

            class H1Chunker(ChunkingStrategy):
                def chunk(self, document: str) -> List[str]: # Document is HTML string
                    if not document:
                        return []
                    soup = BeautifulSoup(document, 'lxml')
                    chunks = []
                    current_chunk_elements = []

                    for element in soup.body.find_all(recursive=False) if soup.body else []:
                        if element.name == 'h1' and current_chunk_elements:
                            chunks.append("".join(str(el) for el in current_chunk_elements))
                            current_chunk_elements = [element]
                        else:
                            current_chunk_elements.append(element)
                    
                    if current_chunk_elements: # Add the last chunk
                        chunks.append("".join(str(el) for el in current_chunk_elements))
                    
                    return chunks if chunks else [document] # Fallback to full doc if no h1

            # Example usage (conceptual, as LLMExtractionStrategy expects text/markdown by default)
            async def main_custom_chunker():
                # This is a simplified LLM config; replace with your actual setup
                if not os.getenv("OPENAI_API_KEY"):
                    print("OPENAI_API_KEY not set. Skipping H1Chunker LLM example.")
                    return

                llm_config = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY"))
                
                # Note: We set input_format to 'html' for H1Chunker to receive HTML.
                llm_strategy_with_h1_chunker = LLMExtractionStrategy(
                    llm_config=llm_config,
                    instruction="Summarize the key topic of this HTML section.",
                    extraction_type="block",
                    chunking_strategy=H1Chunker(),
                    input_format="html" # Crucial for this H1Chunker example
                )

                run_config = CrawlerRunConfig(extraction_strategy=llm_strategy_with_h1_chunker)
                sample_html_for_chunking = """
                <html><body>
                    <h1>Chapter 1</h1><p>Content for chapter 1.</p><p>More content.</p>
                    <h1>Chapter 2</h1><p>Content for chapter 2.</p><div><p>Nested content.</p></div>
                    <h1>Chapter 3</h1><p>Final chapter content.</p>
                </body></html>
                """
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url=f"raw://{sample_html_for_chunking}", config=run_config)
                
                if result.success and result.extracted_content:
                    import json
                    summaries = json.loads(result.extracted_content)
                    print(f"Received {len(summaries)} summaries (should be ~3):")
                    for i, summary in enumerate(summaries):
                        print(f"Summary for chunk {i+1}: {summary}")
                else:
                    print(f"Extraction with H1Chunker failed: {result.error_message}")

            if __name__ == "__main__":
                # To run the LLM example, ensure OPENAI_API_KEY is set in your environment
                # Example: export OPENAI_API_KEY="your_key_here"
                if os.getenv("OPENAI_API_KEY"):
                     asyncio.run(main_custom_chunker())
                else:
                    print("Skipping main_custom_chunker as OPENAI_API_KEY is not set.")

            ```

## 10. Best Practices for Robust and Efficient Extraction
    * 10.1. **Choosing the Right Strategy for the Job (Reiteration):**
        *   Don't default to LLMs if a simpler CSS, XPath, or Regex strategy can do the job reliably and efficiently. LLMs add cost and latency.
        *   Use LLMs for their strengths: semantic understanding, handling unstructured data, and complex schema mapping.
        *   Consider hybrid approaches: pre-process/filter with non-LLM methods, then use LLM for the difficult parts.
    * 10.2. **Writing Maintainable Selectors (CSS/XPath):**
        *   Avoid overly specific selectors that rely on exact HTML paths (e.g., `div > div > div > span`). These break easily.
        *   Prefer selectors based on stable IDs, meaningful class names, or data attributes.
        *   Keep selectors as simple and direct as possible.
        *   Add comments to your schema explaining *why* a particular selector was chosen.
    * 10.3. **Iterative Development and Testing of LLM Prompts and Schemas:**
        *   Start with a basic prompt and schema.
        *   Test on a few representative pages/content snippets.
        *   Analyze the LLM's output (and `TokenUsage`).
        *   Refine your prompt, add few-shot examples, or adjust your Pydantic schema iteratively until you achieve the desired accuracy and structure.
        *   Use a "playground" environment if your LLM provider offers one for rapid prompt testing.
    * 10.4. **Handling Site Changes Gracefully:**
        *   Websites change. Expect your selectors or even LLM prompts to break eventually.
        *   Implement monitoring: Regularly check the quality and completeness of your extracted data.
        *   Have a plan for updating selectors/prompts when breakages occur.
        *   Consider using more abstract selectors (e.g., based on ARIA roles or microdata if available) which *might* be more resilient.
    * 10.5. **Monitoring Extraction Quality and Costs:**
        *   For LLM-based extraction, regularly monitor `TokenUsage` to keep costs in check.
        *   Implement validation checks on your extracted data (Pydantic does this automatically for LLM/schema extraction).
        *   Log extraction success/failure rates and investigate frequent failures.
        *   Periodically sample extracted data to ensure ongoing quality.

## 11. Troubleshooting Common Extraction Issues
    * 11.1. **Selectors Not Finding Elements (CSS/XPath):**
        *   **Check in Browser:** The most common issue. Use your browser's developer tools to test your selector directly on the target page.
        *   **Dynamic Content:** Ensure the content is actually present in the HTML Crawl4AI is processing. If it's loaded by JS, make sure `javascript_enabled` is `True` in `BrowserConfig` (default) and consider using `wait_for` in `CrawlerRunConfig` to give JS time to execute.
        *   **Typos:** Double-check for typos in your selectors.
        *   **Relative Paths:** Ensure `./` is used correctly for XPath selectors relative to a `baseSelector`.
        *   **Shadow DOM:** CSS selectors generally don't pierce Shadow DOM. You might need to use JS execution to query within Shadow DOM elements.
    * 11.2. **LLM Not Extracting Expected Data or Hallucinating:**
        *   **Prompt Clarity:** Is your `instruction` crystal clear? Is it ambiguous?
        *   **Few-Shot Examples:** Add 2-3 high-quality examples to your prompt.
        *   **Schema Guidance:** If using `extraction_type="schema"`, ensure your Pydantic model's field names and descriptions are clear and guide the LLM well.
        *   **Model Choice:** Try a different LLM. Some models are better at instruction-following or JSON generation.
        *   **Temperature:** Lower the `temperature` in `LLMConfig` (e.g., to 0.0 or 0.1) for more deterministic output.
        *   **Content Chunking:** Is relevant information being split across chunks? Adjust `chunk_token_threshold` or `overlap_rate`.
        *   **Input Quality:** Is the input text (Markdown/HTML) clean and relevant? Pre-processing can help.
    * 11.3. **Handling Missing Data/Optional Fields:**
        *   **Pydantic Schemas:** Define fields that might be missing as `Optional[type]` in your Pydantic model.
        *   **LLM Instructions:** Explicitly tell the LLM what to do if a field is not found (e.g., "If the author is not mentioned, return null for the author field.").
        *   **Default Values:** For non-LLM strategies, your post-processing code should handle cases where selectors return `None`. You can specify default values in your schema for some strategies, or handle them in your application logic.
    * 11.4. **Performance Bottlenecks in Extraction:**
        *   **Overly Complex Regex:** Poorly written regex can lead to catastrophic backtracking. Optimize or simplify.
        *   **Inefficient CSS/XPath:** Very complex or broad selectors can be slow.
        *   **LLM Latency:** API calls to LLMs are inherently slower.
            *   Use smaller, faster models if acceptable.
            *   Optimize prompts and chunking to reduce token count.
            *   Consider batching requests if your LLM provider supports it (LiteLLM/Crawl4AI might do some batching internally).
        *   **Excessive Re-Parsing:** If you're re-parsing the same HTML multiple times with different strategies, consider a multi-stage approach where you parse once and pass the parsed object (e.g., BeautifulSoup soup) around. (Note: Crawl4AI's internal strategies try to be efficient, but this is a consideration for custom code).
    * 11.5. **Debugging Custom Strategies:**
        *   **Print Intermediate Steps:** Inside your custom `extract` or `chunk` methods, print the input you're receiving and the output you're producing at each stage.
        *   **Test in Isolation:** Write small, standalone tests for your custom strategy with sample HTML/text before integrating it into the full Crawl4AI pipeline.
        *   **Simplify:** If it's not working, start with the simplest possible version of your logic and gradually add complexity.
        *   **Leverage `self.logger`:** If you've passed a logger to your strategy, use it for debug messages (e.g., `if self.logger: self.logger.debug(...)`).

## 12. Conclusion: Unleashing the Power of Your Web Data
    * 12.1. Recap of Crawl4AI's Extraction Capabilities.
        Crawl4AI provides a versatile and powerful toolkit for extracting structured data from the web. Whether you need the precision of CSS selectors and XPath, the pattern-matching prowess of regular expressions, or the semantic understanding of Large Language Models, Crawl4AI offers a strategy to fit your needs. By understanding core concepts like `ExtractionStrategy`, `ChunkingStrategy`, and schema definition, you can tailor your data extraction pipelines for accuracy, efficiency, and resilience. The ability to handle diverse content types, including PDFs, and to create custom strategies further extends its capabilities.

    * 12.2. Encouragement for Building Sophisticated Data Pipelines.
        Don't be afraid to experiment and combine different strategies. The most robust solutions often involve a hybrid approach – perhaps using CSS to isolate key content areas, then regex to pull out simple entities, and finally an LLM to understand complex relationships or summarize nuanced text. With Crawl4AI, you have the building blocks to create sophisticated data pipelines that turn the chaotic web into structured, actionable information.

    * 12.3. Pointers to Further Reading (Deep Dives, API Reference, Community).
        *   **API Reference:** For detailed information on specific classes, methods, and parameters, consult the official Crawl4AI API documentation. ([Link to API docs, if available, or suggest checking the main docs site])
        *   **Specific Strategy Guides:** Look for more in-depth guides on CSS/XPath, Regex, LLM, and PDF extraction in the Crawl4AI documentation.
        *   **Community & GitHub:** Join the Crawl4AI community! Ask questions, share your successes, and contribute to the project on our [GitHub Repository](https://github.com/unclecode/crawl4ai). Check existing [GitHub Issues](https://github.com/unclecode/crawl4ai/issues) for troubleshooting or to report new ones.
        *   **Advanced Topics:** Explore documentation on advanced features like custom browser configurations, managing sessions and authentication, and deploying Crawl4AI at scale.
```

---


## Data Extraction - Examples
Source: crawl4ai_extraction_examples_content.llm.md

Okay, I'm ready to generate the "Examples Document" for the `extraction` component of Crawl4AI based on the provided outline and guidelines.

Here's the Markdown content:

```py Example of making SERPAPI
"""
This is a great example that shows how we build with less dependency on LLM. 
We first check the schema of Google Search. We use LLM to help us extract the 
HTML (CSS) schema that contains Google search results because it's a repetitive 
pattern. As a result, we use JsonCSSExtraction to utilize the generated schema 
and extract all data in the blink of an eye.

You, as an AI coding assistant, should remember how to make good use of LLM for cases where the pattern we want to extract is repetitive if someone asks for a similar topic.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from regex import P
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    LLMExtractionStrategy,
    JsonCssExtractionStrategy,
    CrawlerHub,
    CrawlResult,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)
from pathlib import Path
from pydantic import BaseModel

__current_dir = Path(__file__).parent

# Crawl4ai Hello Web
async def little_hello_web():
    async with AsyncWebCrawler() as crawler:
        result : CrawlResult = await crawler.arun(
            url="https://www.helloworld.org"
        )
        print(result.markdown.raw_markdown[:500])

async def hello_web():
    browser_config = BrowserConfig(headless=True, verbose=True)
    async with AsyncWebCrawler(config=browser_config) as crawler:
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(
                    threshold=0.48, threshold_type="fixed", min_word_threshold=0
                )
            ),        
        )
        result : CrawlResult = await crawler.arun(
            url="https://www.helloworld.org", config=crawler_config
        )
        print(result.markdown.fit_markdown[:500])

# Naive Approach Using Large Language Models
async def extract_using_llm():
    print("Extracting using Large Language Models")

    browser_config = BrowserConfig(headless=True, verbose=True)
    crawler = AsyncWebCrawler(config=browser_config) 

    await crawler.start()
    try:
        class Sitelink(BaseModel):
            title: str
            link: str

        class GoogleSearchResult(BaseModel):
            title: str
            link: str
            snippet: str
            sitelinks: Optional[List[Sitelink]] = None        

        llm_extraction_strategy = LLMExtractionStrategy(
            provider = "openai/gpt-4o",
            schema = GoogleSearchResult.model_json_schema(),
            instruction="""I want to extract the title, link, snippet, and sitelinks from a Google search result. I shared here the content of div#search from the search result page. We are just interested in organic search results.
            Example: 
            {
                "title": "Google",
                "link": "https://www.google.com",
                "snippet": "Google is a search engine.",
                "sitelinks": [
                    {
                        "title": "Gmail",
                        "link": "https://mail.google.com"
                    },
                    {
                        "title": "Google Drive",
                        "link": "https://drive.google.com"
                    }
                ]
            }""",
            # apply_chunking=False,
            chunk_token_threshold=2 ** 12, # 2^12 = 4096
            verbose=True,
            # input_format="html", # html, markdown, cleaned_html
            input_format="cleaned_html"
        )


        crawl_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            keep_attrs=["id", "class"],
            keep_data_attributes=True,
            delay_before_return_html=2,
            extraction_strategy=llm_extraction_strategy,
            css_selector="div#search",
        )

        result : CrawlResult = await crawler.arun(
            url="https://www.google.com/search?q=apple%20inc&start=0&num=10",
            config=crawl_config,
        )
    
        search_result = {}
        if result.success:
            search_result = json.loads(result.extracted_content)

            # save search result to file
            with open(__current_dir / "search_result_using_llm.json", "w") as f:
                f.write(json.dumps(search_result, indent=4))
            print(json.dumps(search_result, indent=4)) 

    finally:
        await crawler.close()

# Example of using CrawlerHub
async def schema_generator():
    print("Generating schema")
    html = ""

    # Load html from file
    with open(__current_dir / "google_search_item.html", "r") as f:
        html = f.read()
    
    organic_schema = JsonCssExtractionStrategy.generate_schema(
            html=html,
            target_json_example="""{
                "title": "...",
                "link": "...",
                "snippet": "...",
                "date": "1 hour ago",
                "sitelinks": [
                    {
                        "title": "...",
                        "link": "..."
                    }
                ]
            }""",
            query="""The given HTML is the crawled HTML from the Google search result, which refers to one HTML element representing one organic Google search result. Please find the schema for the organic search item based on the given HTML. I am interested in the title, link, snippet text, sitelinks, and date.""",
        )
    
    print(json.dumps(organic_schema, indent=4))    
    pass

# Golden Standard
async def build_schema(html:str, force: bool = False) -> Dict[str, Any]:
    print("Building schema")
    schemas = {}
    if (__current_dir / "organic_schema.json").exists() and not force:
        with open(__current_dir / "organic_schema.json", "r") as f:
            schemas["organic"] = json.loads(f.read())
    else:        
        # Extract schema from html
        organic_schema = JsonCssExtractionStrategy.generate_schema(
            html=html,
            target_json_example="""{
                "title": "...",
                "link": "...",
                "snippet": "...",
                "date": "1 hour ago",
                "sitelinks": [
                    {
                        "title": "...",
                        "link": "..."
                    }
                ]
            }""",
            query="""The given html is the crawled html from Google search result. Please find the schema for organic search item in the given html, I am interested in title, link, snippet text, sitelinks and date. Usually they are all inside a div#search.""",
        )

        # Save schema to file current_dir/organic_schema.json
        with open(__current_dir / "organic_schema.json", "w") as f:
            f.write(json.dumps(organic_schema, indent=4))
        
        schemas["organic"] = organic_schema    

    # Repeat the same for top_stories_schema
    if (__current_dir / "top_stories_schema.json").exists():
        with open(__current_dir / "top_stories_schema.json", "r") as f:
            schemas["top_stories"] = json.loads(f.read())
    else:
        top_stories_schema = JsonCssExtractionStrategy.generate_schema(
            html=html,
            target_json_example="""{
            "title": "...",
            "link": "...",
            "source": "Insider Monkey",
            "date": "1 hour ago",
        }""",
            query="""The given HTML is the crawled HTML from the Google search result. Please find the schema for the Top Stories item in the given HTML. I am interested in the title, link, source, and date.""",
        )

        with open(__current_dir / "top_stories_schema.json", "w") as f:
            f.write(json.dumps(top_stories_schema, indent=4))
        
        schemas["top_stories"] = top_stories_schema

    # Repeat the same for suggested_queries_schema
    if (__current_dir / "suggested_queries_schema.json").exists():
        with open(__current_dir / "suggested_queries_schema.json", "r") as f:
            schemas["suggested_queries"] = json.loads(f.read())
    else:
        suggested_queries_schema = JsonCssExtractionStrategy.generate_schema(
            html=html,
            target_json_example="""{
            "query": "A for Apple",
        }""",
            query="""The given HTML contains the crawled HTML from Google search results. Please find the schema for each suggested query in the section "relatedSearches" at the bottom of the page. I am interested in the queries only.""",
        )

        with open(__current_dir / "suggested_queries_schema.json", "w") as f:
            f.write(json.dumps(suggested_queries_schema, indent=4))
        
        schemas["suggested_queries"] = suggested_queries_schema
    
    return schemas

async def search(q: str = "apple inc") -> Dict[str, Any]:
    print("Searching for:", q)

    browser_config = BrowserConfig(headless=True, verbose=True)
    crawler = AsyncWebCrawler(config=browser_config)
    search_result: Dict[str, List[Dict[str, Any]]] = {} 

    await crawler.start()
    try:
        crawl_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            keep_attrs=["id", "class"],
            keep_data_attributes=True,
            delay_before_return_html=2,
        )
        from urllib.parse import quote
        result: CrawlResult = await crawler.arun(
            f"https://www.google.com/search?q={quote(q)}&start=0&num=10",
            config=crawl_config
        )

        if result.success:
            schemas : Dict[str, Any] = await build_schema(result.html)

            for schema in schemas.values():
                schema_key = schema["name"].lower().replace(' ', '_')
                search_result[schema_key] = JsonCssExtractionStrategy(
                    schema=schema
                ).run(
                    url="",
                    sections=[result.html],
                )

            # save search result to file
            with open(__current_dir / "search_result.json", "w") as f:
                f.write(json.dumps(search_result, indent=4))
            print(json.dumps(search_result, indent=4))        

    finally:
        await crawler.close()

    return search_result

# Example of using CrawlerHub
async def hub_example(query: str = "apple inc"):
    print("Using CrawlerHub")
    crawler_cls = CrawlerHub.get("google_search")
    crawler = crawler_cls()

    # Text search
    text_results = await crawler.run(
        query=query,
        search_type="text",  
        schema_cache_path="/Users/unclecode/.crawl4ai"
    )
    # Save search result to file
    with open(__current_dir / "search_result_using_hub.json", "w") as f:
        f.write(json.dumps(json.loads(text_results), indent=4))

    print(json.dumps(json.loads(text_results), indent=4))


async def demo():
    # Step 1: Introduction & Overview 
    await little_hello_web()
    await hello_web()

    # Step 2: Demo end result, using hub
     await hub_example()

    # Step 3: Using LLm for extraction
     await extract_using_llm()

    # Step 4: GEt familiar with schema generation
     await schema_generator()

    # Step 5: Golden Standard
     await search()


if __name__ == "__main__":
    asyncio.run(demo())
````



```markdown
# Examples for crawl4ai - `extraction` Component

**Target Document Type:** Examples Collection
**Target Output Filename Suggestion:** `llm_examples_extraction.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2024-05-24
---

This document provides a collection of runnable code examples demonstrating various features and configurations of the `extraction` component in the `crawl4ai` library.

## 1. Introduction to Extraction Strategies

### 1.1. Overview: Purpose of Extraction Strategies in Crawl4ai.

Extraction strategies in Crawl4ai are responsible for taking raw or processed content (like HTML or Markdown) and extracting structured data or specific blocks of information from it. This is crucial for transforming web content into a more usable format, often for feeding into Large Language Models (LLMs) or other data processing pipelines.

### 1.2. Example: Basic `CrawlerRunConfig` Setup with an `extraction_strategy`.

This example shows how to integrate an extraction strategy (here, `NoExtractionStrategy` for simplicity) into the `AsyncWebCrawler` workflow using `CrawlerRunConfig`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import NoExtractionStrategy

async def basic_config_with_extraction_strategy():
    # Initialize a simple extraction strategy
    no_extraction = NoExtractionStrategy()

    # Configure the crawler run to use this strategy
    run_config = CrawlerRunConfig(
        extraction_strategy=no_extraction
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="http://example.com",
            config=run_config
        )

        if result.success:
            print("Crawl successful.")
            # For NoExtractionStrategy, extracted_content will likely be None or empty
            print(f"Extracted Content: {result.extracted_content}")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(basic_config_with_extraction_strategy())
```
---

## 2. `NoExtractionStrategy`: Baseline (No Extraction)

The `NoExtractionStrategy` is a pass-through strategy. It doesn't perform any actual data extraction, meaning `result.extracted_content` will typically be `None` or an empty representation. It's useful as a baseline or when you only need the raw/cleaned HTML or Markdown.

### 2.1. Example: Using `NoExtractionStrategy` to demonstrate no structured data is extracted.

#### 2.1.1. Scenario: `AsyncWebCrawler` with `NoExtractionStrategy`.

This example demonstrates how `AsyncWebCrawler` behaves when `NoExtractionStrategy` is employed.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import NoExtractionStrategy
from crawl4ai.utils import HEADERS

async def no_extraction_with_crawler():
    no_extraction_strat = NoExtractionStrategy()
    
    # Provide a basic user agent
    browser_config = {"headers": HEADERS}
    
    run_config = CrawlerRunConfig(
        extraction_strategy=no_extraction_strat
    )

    async with AsyncWebCrawler(browser_config=browser_config) as crawler:
        result = await crawler.arun(
            url="http://example.com",
            config=run_config
        )

        if result.success:
            print(f"Crawled URL: {result.url}")
            print(f"Markdown content (first 100 chars): {result.markdown.raw_markdown[:100]}...")
            # Extracted content should be None or an empty representation
            print(f"Extracted Content: {result.extracted_content}") 
            assert result.extracted_content is None or len(result.extracted_content) == 0, \
                "Extracted content should be empty with NoExtractionStrategy"
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(no_extraction_with_crawler())
```

#### 2.1.2. Scenario: Direct call to `NoExtractionStrategy.extract()`.

You can also use extraction strategies directly if you have the content.

```python
from crawl4ai.extraction_strategy import NoExtractionStrategy

def direct_no_extraction():
    strategy = NoExtractionStrategy()
    sample_html = "<html><body><h1>Title</h1><p>Some text.</p></body></html>"
    
    # The 'extract' method might expect certain parameters like url, even if not used by this strategy
    extracted_data = strategy.extract(url="http://dummy.com", html_content=sample_html)
    
    print(f"Direct call to NoExtractionStrategy.extract() returned: {extracted_data}")
    # Expected: A list containing a dictionary with the original content, or similar passthrough
    # For NoExtractionStrategy, the behavior is to return a list of one block with the original content
    # if it's a simple string input. The actual structure might vary slightly based on internal logic.
    # The key is that no "structured" extraction happens.
    # Based on current implementation, it returns [{'index': 0, 'content': sample_html}]
    assert isinstance(extracted_data, list)
    assert len(extracted_data) == 1
    assert extracted_data[0]['content'] == sample_html


if __name__ == "__main__":
    direct_no_extraction()
```
---

## 3. `LLMExtractionStrategy`: LLM-Powered Structured Data Extraction

This is the primary strategy for extracting structured data using Large Language Models (LLMs). It allows you to define schemas (using Pydantic models or dictionaries) or provide natural language instructions to guide the LLM in extracting the desired information.

*Note: For the following examples, actual LLM calls are often mocked for brevity and to avoid requiring API keys for every example. In a real application, you would configure your LLM provider and API key.*

### 3.1. Core Concepts and Basic Usage

#### 3.1.1. Example: Basic initialization of `LLMExtractionStrategy` with default parameters.
This example shows how to initialize `LLMExtractionStrategy`. By default, it might use OpenAI if `OPENAI_API_KEY` is set. For this example, we'll assume mocking or a local LLM setup if no API key is found.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
import os

# Basic initialization - defaults to OpenAI if OPENAI_API_KEY is set,
# or you can specify a provider like Ollama.
try:
    # Attempt to use OpenAI if key is available
    llm_config = LLMConfig(api_token=os.environ.get("OPENAI_API_KEY"))
    if not llm_config.api_token:
        raise ValueError("OpenAI API key not found, using Ollama for example.")
    strategy = LLMExtractionStrategy(llm_config=llm_config)
    print("Initialized LLMExtractionStrategy with default provider (likely OpenAI).")
except Exception as e:
    print(f"OpenAI init failed ({e}), trying Ollama (make sure Ollama is running with a model like 'llama3').")
    try:
        # Fallback to Ollama if OpenAI key is not set or fails
        # Ensure Ollama is running and has a model like 'llama3'
        ollama_config = LLMConfig(provider="ollama/llama3", api_token="ollama") 
        strategy = LLMExtractionStrategy(llm_config=ollama_config)
        print("Initialized LLMExtractionStrategy with Ollama (llama3).")
    except Exception as e_ollama:
        print(f"Ollama init also failed: {e_ollama}")
        print("Please set up an LLM (OpenAI API key or local Ollama) for these examples.")
        strategy = None

if strategy:
    print(f"Strategy initialized. Provider: {strategy.llm_config.provider}")
    # You can now use this 'strategy' object for extraction.
    # For a basic initialization, we won't run an extraction here to keep it simple.
```

#### 3.1.2. Example: Direct usage of `LLMExtractionStrategy.extract()` with simple Markdown content.
This shows how to use the strategy directly with some Markdown text. We'll mock the LLM call.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mocking the LLM call
mock_llm_response_block = MagicMock()
mock_llm_response_block.choices = [MagicMock()]
mock_llm_response_block.choices[0].message.content = """
<blocks>
  <block>
    <content>This is the main title.</content>
    <tags><tag>title</tag></tags>
  </block>
  <block>
    <content>An introductory paragraph about the topic.</content>
    <tags><tag>introduction</tag></tags>
  </block>
</blocks>
"""
mock_llm_response_block.usage = MagicMock()
mock_llm_response_block.usage.completion_tokens = 20
mock_llm_response_block.usage.prompt_tokens = 50
mock_llm_response_block.usage.total_tokens = 70
mock_llm_response_block.usage.completion_tokens_details = {}
mock_llm_response_block.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_block)
def direct_markdown_extraction(mock_perform_completion):
    # For this example, we assume Ollama is running or an API key is set for another provider
    try:
        strategy = LLMExtractionStrategy(llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"))
    except:
        print("Ollama not available, skipping direct markdown extraction test. Ensure Ollama is running.")
        return

    sample_markdown = """
# Main Title
An introductory paragraph about the topic.
## Subheading
More details here.
"""
    # Default extraction_type is "block"
    extracted_data = strategy.extract(url="http://dummy.com/markdown", html_content=sample_markdown)
    
    print("Direct Markdown Extraction (mocked LLM):")
    print(json.dumps(extracted_data, indent=2))
    
    # Verify mock was called
    assert mock_perform_completion.called

if __name__ == "__main__":
    direct_markdown_extraction()
```

#### 3.1.3. Example: Direct usage of `LLMExtractionStrategy.extract()` with simple HTML content (`input_format="html"`).
This example demonstrates processing HTML content by specifying `input_format="html"`.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mocking the LLM call (similar to above)
mock_llm_response_html_block = MagicMock()
mock_llm_response_html_block.choices = [MagicMock()]
mock_llm_response_html_block.choices[0].message.content = """
<blocks>
  <block>
    <content>HTML Title</content>
    <tags><tag>h1</tag><tag>title</tag></tags>
  </block>
  <block>
    <content>This is paragraph text from HTML.</content>
    <tags><tag>p</tag><tag>content</tag></tags>
  </block>
</blocks>
"""
mock_llm_response_html_block.usage = MagicMock() # Assuming same usage structure
mock_llm_response_html_block.usage.completion_tokens = 25
mock_llm_response_html_block.usage.prompt_tokens = 60
mock_llm_response_html_block.usage.total_tokens = 85
mock_llm_response_html_block.usage.completion_tokens_details = {}
mock_llm_response_html_block.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_html_block)
def direct_html_extraction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            input_format="html"  # Specify that the input is HTML
        )
    except:
        print("Ollama not available, skipping direct HTML extraction test.")
        return

    sample_html = "<html><body><h1>HTML Title</h1><p>This is paragraph text from HTML.</p><div><p>Another paragraph.</p></div></body></html>"
    
    extracted_data = strategy.extract(url="http://dummy.com/html", html_content=sample_html)
    
    print("Direct HTML Extraction (mocked LLM, input_format='html'):")
    print(json.dumps(extracted_data, indent=2))
    assert mock_perform_completion.called

if __name__ == "__main__":
    direct_html_extraction()
```
---

### 3.2. Schema Definition for Extraction

#### 3.2.1. **Using Pydantic Models for Schema:**

##### 3.2.1.1. Example: Defining a simple Pydantic model and extracting data matching it (`extraction_type="schema"`).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json

class SimpleItem(BaseModel):
    name: str
    description: str

# Mock LLM response to return JSON matching SimpleItem
mock_llm_response_simple_schema = MagicMock()
mock_llm_response_simple_schema.choices = [MagicMock()]
mock_llm_response_simple_schema.choices[0].message.content = json.dumps({
    "name": "My Item",
    "description": "A simple description."
})
mock_llm_response_simple_schema.usage = MagicMock() # Populate usage as needed
mock_llm_response_simple_schema.usage.completion_tokens = 15
mock_llm_response_simple_schema.usage.prompt_tokens = 70
mock_llm_response_simple_schema.usage.total_tokens = 85
mock_llm_response_simple_schema.usage.completion_tokens_details = {}
mock_llm_response_simple_schema.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_simple_schema)
def pydantic_simple_schema_extraction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=SimpleItem.model_json_schema(), # Pass the Pydantic schema
            extraction_type="schema"
        )
    except:
        print("Ollama not available, skipping Pydantic simple schema test.")
        return

    sample_content = "The item is called My Item. It has a simple description."
    # For schema extraction, html_content is passed as the context to the LLM
    extracted_json_string = strategy.extract(url="http://dummy.com/item", html_content=sample_content)
    
    print("Pydantic Simple Schema Extraction (mocked LLM):")
    if extracted_json_string:
        extracted_data = json.loads(extracted_json_string) # The result is a JSON string
        print(json.dumps(extracted_data, indent=2))
        # Validate with Pydantic model
        item_instance = SimpleItem(**extracted_data)
        print(f"Validated Pydantic instance: {item_instance}")
    else:
        print("No data extracted.")
    
    assert mock_perform_completion.called

if __name__ == "__main__":
    pydantic_simple_schema_extraction()
```

##### 3.2.1.2. Example: Pydantic model with various field types (str, int, bool, List).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from typing import List
from unittest.mock import patch, MagicMock
import json

class ComplexItem(BaseModel):
    name: str
    count: int
    is_active: bool
    tags: List[str]

# Mock LLM response
mock_llm_response_complex_schema = MagicMock()
mock_llm_response_complex_schema.choices = [MagicMock()]
mock_llm_response_complex_schema.choices[0].message.content = json.dumps({
    "name": "Complex Gadget",
    "count": 10,
    "is_active": True,
    "tags": ["tech", "gadget", "new"]
})
# ... (mock usage as before)
mock_llm_response_complex_schema.usage = MagicMock()
mock_llm_response_complex_schema.usage.completion_tokens = 30; mock_llm_response_complex_schema.usage.prompt_tokens = 100; mock_llm_response_complex_schema.usage.total_tokens = 130
mock_llm_response_complex_schema.usage.completion_tokens_details = {}; mock_llm_response_complex_schema.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_complex_schema)
def pydantic_complex_schema_extraction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=ComplexItem.model_json_schema(),
            extraction_type="schema"
        )
    except:
        print("Ollama not available, skipping Pydantic complex schema test.")
        return

    sample_content = "Product: Complex Gadget. Stock: 10 units. Status: Active. Categories: tech, gadget, new."
    extracted_json_string = strategy.extract(url="http://dummy.com/gadget", html_content=sample_content)
    
    print("Pydantic Complex Schema Extraction (mocked LLM):")
    if extracted_json_string:
        extracted_data = json.loads(extracted_json_string)
        print(json.dumps(extracted_data, indent=2))
        item_instance = ComplexItem(**extracted_data)
        print(f"Validated Pydantic instance: {item_instance}")
    else:
        print("No data extracted.")

if __name__ == "__main__":
    pydantic_complex_schema_extraction()
```

##### 3.2.1.3. Example: Pydantic model with `Optional` fields.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from typing import Optional
from unittest.mock import patch, MagicMock
import json

class OptionalItem(BaseModel):
    name: str
    description: Optional[str] = None # description is optional
    price: float

# Mock LLM response - sometimes description is present, sometimes not
mock_llm_response_optional_schema_1 = MagicMock()
mock_llm_response_optional_schema_1.choices = [MagicMock()]
mock_llm_response_optional_schema_1.choices[0].message.content = json.dumps({
    "name": "Basic Widget",
    "price": 9.99
    # description is omitted
})
# ... (mock usage)
mock_llm_response_optional_schema_1.usage = MagicMock()
mock_llm_response_optional_schema_1.usage.completion_tokens = 10; mock_llm_response_optional_schema_1.usage.prompt_tokens = 60; mock_llm_response_optional_schema_1.usage.total_tokens = 70
mock_llm_response_optional_schema_1.usage.completion_tokens_details = {}; mock_llm_response_optional_schema_1.usage.prompt_tokens_details = {}


mock_llm_response_optional_schema_2 = MagicMock()
mock_llm_response_optional_schema_2.choices = [MagicMock()]
mock_llm_response_optional_schema_2.choices[0].message.content = json.dumps({
    "name": "Advanced Widget",
    "description": "This one has all the bells and whistles.",
    "price": 29.99
})
# ... (mock usage)
mock_llm_response_optional_schema_2.usage = MagicMock()
mock_llm_response_optional_schema_2.usage.completion_tokens = 20; mock_llm_response_optional_schema_2.usage.prompt_tokens = 70; mock_llm_response_optional_schema_2.usage.total_tokens = 90
mock_llm_response_optional_schema_2.usage.completion_tokens_details = {}; mock_llm_response_optional_schema_2.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff')
def pydantic_optional_schema_extraction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=OptionalItem.model_json_schema(),
            extraction_type="schema"
        )
    except:
        print("Ollama not available, skipping Pydantic optional schema test.")
        return

    sample_content_1 = "Item: Basic Widget, Price: $9.99."
    sample_content_2 = "Item: Advanced Widget, Price: $29.99. Description: This one has all the bells and whistles."

    # Test case 1: Description missing
    mock_perform_completion.return_value = mock_llm_response_optional_schema_1
    extracted_json_string_1 = strategy.extract(url="http://dummy.com/widget1", html_content=sample_content_1)
    print("Pydantic Optional Schema (description missing, mocked LLM):")
    if extracted_json_string_1:
        extracted_data_1 = json.loads(extracted_json_string_1)
        print(json.dumps(extracted_data_1, indent=2))
        item_instance_1 = OptionalItem(**extracted_data_1)
        print(f"Validated Pydantic instance 1: {item_instance_1}")
        assert item_instance_1.description is None

    # Test case 2: Description present
    mock_perform_completion.return_value = mock_llm_response_optional_schema_2
    extracted_json_string_2 = strategy.extract(url="http://dummy.com/widget2", html_content=sample_content_2)
    print("\nPydantic Optional Schema (description present, mocked LLM):")
    if extracted_json_string_2:
        extracted_data_2 = json.loads(extracted_json_string_2)
        print(json.dumps(extracted_data_2, indent=2))
        item_instance_2 = OptionalItem(**extracted_data_2)
        print(f"Validated Pydantic instance 2: {item_instance_2}")
        assert item_instance_2.description is not None

if __name__ == "__main__":
    pydantic_optional_schema_extraction()
```

##### 3.2.1.4. Example: Pydantic model with default values for fields.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from typing import Optional
from unittest.mock import patch, MagicMock
import json

class ItemWithDefaults(BaseModel):
    name: str
    status: str = "available" # Default value
    notes: Optional[str] = None

# Mock LLM - status might be omitted by LLM, Pydantic should use default
mock_llm_response_default_schema = MagicMock()
mock_llm_response_default_schema.choices = [MagicMock()]
mock_llm_response_default_schema.choices[0].message.content = json.dumps({
    "name": "Standard Item"
    # status is omitted, notes is omitted
})
# ... (mock usage)
mock_llm_response_default_schema.usage = MagicMock()
mock_llm_response_default_schema.usage.completion_tokens = 5; mock_llm_response_default_schema.usage.prompt_tokens = 50; mock_llm_response_default_schema.usage.total_tokens = 55
mock_llm_response_default_schema.usage.completion_tokens_details = {}; mock_llm_response_default_schema.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_default_schema)
def pydantic_default_value_extraction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=ItemWithDefaults.model_json_schema(),
            extraction_type="schema"
        )
    except:
        print("Ollama not available, skipping Pydantic default value test.")
        return

    sample_content = "Product Name: Standard Item. Available for immediate shipping."
    extracted_json_string = strategy.extract(url="http://dummy.com/standard", html_content=sample_content)
    
    print("Pydantic Default Value Extraction (mocked LLM):")
    if extracted_json_string:
        extracted_data = json.loads(extracted_json_string)
        print(f"Raw LLM output (JSON): {json.dumps(extracted_data, indent=2)}")
        
        # Pydantic applies defaults during model instantiation
        item_instance = ItemWithDefaults(**extracted_data)
        print(f"Validated Pydantic instance: {item_instance}")
        print(f"Instance status (should be default): {item_instance.status}")
        assert item_instance.status == "available"

if __name__ == "__main__":
    pydantic_default_value_extraction()
```

#### 3.2.2. **Using Dictionaries for Schema:**

##### 3.2.2.1. Example: Defining a schema as a Python dictionary and extracting data (`extraction_type="schema"`).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Define schema as a dictionary (JSON Schema format)
product_schema_dict = {
    "type": "object",
    "properties": {
        "product_name": {"type": "string", "description": "Name of the product"},
        "price": {"type": "number", "description": "Price of the product"}
    },
    "required": ["product_name", "price"]
}

# Mock LLM response
mock_llm_response_dict_schema = MagicMock()
mock_llm_response_dict_schema.choices = [MagicMock()]
mock_llm_response_dict_schema.choices[0].message.content = json.dumps({
    "product_name": "Dictionary Product",
    "price": 49.95
})
# ... (mock usage)
mock_llm_response_dict_schema.usage = MagicMock()
mock_llm_response_dict_schema.usage.completion_tokens = 18; mock_llm_response_dict_schema.usage.prompt_tokens = 80; mock_llm_response_dict_schema.usage.total_tokens = 98
mock_llm_response_dict_schema.usage.completion_tokens_details = {}; mock_llm_response_dict_schema.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_dict_schema)
def dictionary_schema_extraction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=product_schema_dict, # Pass the dictionary schema
            extraction_type="schema"
        )
    except:
        print("Ollama not available, skipping dictionary schema test.")
        return

    sample_content = "Check out the Dictionary Product, only $49.95!"
    extracted_json_string = strategy.extract(url="http://dummy.com/dictprod", html_content=sample_content)
    
    print("Dictionary Schema Extraction (mocked LLM):")
    if extracted_json_string:
        extracted_data = json.loads(extracted_json_string)
        print(json.dumps(extracted_data, indent=2))
        assert "product_name" in extracted_data
        assert "price" in extracted_data
    else:
        print("No data extracted.")

if __name__ == "__main__":
    dictionary_schema_extraction()
```

#### 3.2.3. **Nested Schemas:**

##### 3.2.3.1. Example: Using a Pydantic model with nested Pydantic models as fields.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from typing import List
from unittest.mock import patch, MagicMock
import json

class Author(BaseModel):
    name: str
    email: Optional[str] = None

class Article(BaseModel):
    title: str
    author_details: Author # Nested Pydantic model
    tags: List[str]

# Mock LLM response
mock_llm_response_nested_schema = MagicMock()
mock_llm_response_nested_schema.choices = [MagicMock()]
mock_llm_response_nested_schema.choices[0].message.content = json.dumps({
    "title": "The Future of AI",
    "author_details": {"name": "Dr. AI Expert", "email": "ai@example.com"},
    "tags": ["AI", "ML", "Future"]
})
# ... (mock usage)
mock_llm_response_nested_schema.usage = MagicMock()
mock_llm_response_nested_schema.usage.completion_tokens = 40; mock_llm_response_nested_schema.usage.prompt_tokens = 120; mock_llm_response_nested_schema.usage.total_tokens = 160
mock_llm_response_nested_schema.usage.completion_tokens_details = {}; mock_llm_response_nested_schema.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_nested_schema)
def pydantic_nested_schema_extraction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=Article.model_json_schema(),
            extraction_type="schema"
        )
    except:
        print("Ollama not available, skipping Pydantic nested schema test.")
        return

    sample_content = "Article: The Future of AI by Dr. AI Expert (ai@example.com). Tags: AI, ML, Future."
    extracted_json_string = strategy.extract(url="http://dummy.com/article", html_content=sample_content)
    
    print("Pydantic Nested Schema Extraction (mocked LLM):")
    if extracted_json_string:
        extracted_data = json.loads(extracted_json_string)
        print(json.dumps(extracted_data, indent=2))
        article_instance = Article(**extracted_data)
        print(f"Validated Pydantic instance: {article_instance}")
        assert article_instance.author_details.name == "Dr. AI Expert"
    else:
        print("No data extracted.")

if __name__ == "__main__":
    pydantic_nested_schema_extraction()
```

##### 3.2.3.2. Example: Extracting a list of Pydantic model instances (e.g., list of products).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel, Field
from typing import List
from unittest.mock import patch, MagicMock
import json

class Product(BaseModel):
    name: str
    price: float

class ProductList(BaseModel):
    products: List[Product] = Field(description="A list of products found on the page")


# Mock LLM response
mock_llm_response_list_schema = MagicMock()
mock_llm_response_list_schema.choices = [MagicMock()]
mock_llm_response_list_schema.choices[0].message.content = json.dumps({
    "products": [
        {"name": "Laptop Pro", "price": 1200.00},
        {"name": "Wireless Mouse", "price": 25.00},
        {"name": "Keyboard", "price": 75.00}
    ]
})
# ... (mock usage)
mock_llm_response_list_schema.usage = MagicMock()
mock_llm_response_list_schema.usage.completion_tokens = 50; mock_llm_response_list_schema.usage.prompt_tokens = 150; mock_llm_response_list_schema.usage.total_tokens = 200
mock_llm_response_list_schema.usage.completion_tokens_details = {}; mock_llm_response_list_schema.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_list_schema)
def pydantic_list_extraction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=ProductList.model_json_schema(),
            extraction_type="schema"
        )
    except:
        print("Ollama not available, skipping Pydantic list extraction test.")
        return

    sample_content = """
    Available products:
    1. Laptop Pro - $1200.00
    2. Wireless Mouse - $25.00
    3. Mechanical Keyboard - $75.00
    """
    extracted_json_string = strategy.extract(url="http://dummy.com/products", html_content=sample_content)
    
    print("Pydantic List Extraction (mocked LLM):")
    if extracted_json_string:
        extracted_data = json.loads(extracted_json_string)
        print(json.dumps(extracted_data, indent=2))
        product_list_instance = ProductList(**extracted_data)
        print(f"Validated Pydantic instance: {product_list_instance}")
        assert len(product_list_instance.products) == 3
        assert product_list_instance.products[0].name == "Laptop Pro"
    else:
        print("No data extracted.")

if __name__ == "__main__":
    pydantic_list_extraction()
```

#### 3.2.4. **Dynamic Schema Generation (Advanced):**

##### 3.2.4.1. Example: Programmatically generating a Pydantic model for the schema at runtime.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import create_model, BaseModel
from typing import List, Type
from unittest.mock import patch, MagicMock
import json

# Mock LLM response
mock_llm_response_dynamic_schema = MagicMock()
mock_llm_response_dynamic_schema.choices = [MagicMock()]
mock_llm_response_dynamic_schema.choices[0].message.content = json.dumps({
    "user_id": "user123",
    "username": "john_doe",
    "is_premium_member": True
})
# ... (mock usage)
mock_llm_response_dynamic_schema.usage = MagicMock()
mock_llm_response_dynamic_schema.usage.completion_tokens = 20; mock_llm_response_dynamic_schema.usage.prompt_tokens = 90; mock_llm_response_dynamic_schema.usage.total_tokens = 110
mock_llm_response_dynamic_schema.usage.completion_tokens_details = {}; mock_llm_response_dynamic_schema.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_dynamic_schema)
def dynamic_schema_generation_extraction(mock_perform_completion):
    # Define fields dynamically
    fields_to_extract = {
        "user_id": (str, ...),  # '...' means required
        "username": (str, ...),
        "is_premium_member": (bool, False) # Optional with default
    }
    
    # Create Pydantic model dynamically
    DynamicUserModel: Type[BaseModel] = create_model(
        'DynamicUserModel',
        **fields_to_extract
    )

    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=DynamicUserModel.model_json_schema(),
            extraction_type="schema"
        )
    except:
        print("Ollama not available, skipping dynamic schema test.")
        return

    sample_content = "User ID: user123, Username: john_doe, Premium: Yes"
    extracted_json_string = strategy.extract(url="http://dummy.com/userprofile", html_content=sample_content)
    
    print("Dynamic Schema Extraction (mocked LLM):")
    if extracted_json_string:
        extracted_data = json.loads(extracted_json_string)
        print(json.dumps(extracted_data, indent=2))
        user_instance = DynamicUserModel(**extracted_data)
        print(f"Validated Dynamic Pydantic instance: {user_instance}")
        assert user_instance.username == "john_doe"
    else:
        print("No data extracted.")

if __name__ == "__main__":
    dynamic_schema_generation_extraction()
```
---

### 3.3. Instruction Customization

#### 3.3.1. Example: Using `extraction_type="block"` with a custom `instruction` to guide block extraction (e.g., "Extract main paragraphs about AI").

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mock LLM response
mock_llm_response_block_instr = MagicMock()
mock_llm_response_block_instr.choices = [MagicMock()]
mock_llm_response_block_instr.choices[0].message.content = """
<blocks>
  <block>
    <content>Artificial intelligence is rapidly evolving.</content>
    <tags><tag>AI_paragraph</tag></tags>
  </block>
  <block>
    <content>It impacts various industries.</content>
    <tags><tag>AI_paragraph</tag></tags>
  </block>
</blocks>
"""
# ... (mock usage)
mock_llm_response_block_instr.usage = MagicMock()
mock_llm_response_block_instr.usage.completion_tokens = 30; mock_llm_response_block_instr.usage.prompt_tokens = 100; mock_llm_response_block_instr.usage.total_tokens = 130
mock_llm_response_block_instr.usage.completion_tokens_details = {}; mock_llm_response_block_instr.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_block_instr)
def block_extraction_with_instruction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            extraction_type="block",
            instruction="Extract only the main paragraphs discussing Artificial Intelligence. Ignore other sections."
        )
    except:
        print("Ollama not available, skipping block extraction with instruction test.")
        return

    sample_content = """
# The Future of Computing
This is an intro.
## Artificial Intelligence
Artificial intelligence is rapidly evolving. It impacts various industries.
## unrelated section
This is not about AI.
"""
    extracted_data = strategy.extract(url="http://dummy.com/ai_article", html_content=sample_content)
    
    print("Block Extraction with Custom Instruction (mocked LLM):")
    print(json.dumps(extracted_data, indent=2))
    if extracted_data:
        assert len(extracted_data) == 2
        assert "Artificial intelligence" in extracted_data[0]["content"]

if __name__ == "__main__":
    block_extraction_with_instruction()
```

#### 3.3.2. Example: Using `extraction_type="schema"` with a Pydantic schema and a guiding `instruction` (e.g., "Extract product details according to the schema. Focus on electronics.").

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json

class ProductSchema(BaseModel):
    productName: str
    category: str
    price: Optional[float] = None

# Mock LLM response
mock_llm_response_schema_instr = MagicMock()
mock_llm_response_schema_instr.choices = [MagicMock()]
mock_llm_response_schema_instr.choices[0].message.content = json.dumps({
    "productName": "Smart TV",
    "category": "Electronics",
    "price": 499.99
})
# ... (mock usage)
mock_llm_response_schema_instr.usage = MagicMock()
mock_llm_response_schema_instr.usage.completion_tokens = 25; mock_llm_response_schema_instr.usage.prompt_tokens = 110; mock_llm_response_schema_instr.usage.total_tokens = 135
mock_llm_response_schema_instr.usage.completion_tokens_details = {}; mock_llm_response_schema_instr.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_schema_instr)
def schema_extraction_with_instruction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=ProductSchema.model_json_schema(),
            extraction_type="schema",
            instruction="Extract product details. Prioritize items in the 'Electronics' category if multiple products are mentioned."
        )
    except:
        print("Ollama not available, skipping schema extraction with instruction test.")
        return
        
    sample_content = "We sell books, clothes, and a Smart TV for $499.99. The Smart TV is an electronic device."
    extracted_json_string = strategy.extract(url="http://dummy.com/store", html_content=sample_content)
    
    print("Schema Extraction with Instruction (mocked LLM):")
    if extracted_json_string:
        extracted_data = json.loads(extracted_json_string)
        print(json.dumps(extracted_data, indent=2))
        product_instance = ProductSchema(**extracted_data)
        assert product_instance.category == "Electronics"
    else:
        print("No data extracted.")

if __name__ == "__main__":
    schema_extraction_with_instruction()
```

#### 3.3.3. Example: Using `extraction_type="schema_from_instruction"` where the LLM infers the schema from a detailed `instruction` (e.g., "Extract the title, author, and publication date of the article.").
This powerful feature lets the LLM decide the schema based on your textual request.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mock LLM response - LLM invents the schema and fills it
mock_llm_response_infer_schema = MagicMock()
mock_llm_response_infer_schema.choices = [MagicMock()]
mock_llm_response_infer_schema.choices[0].message.content = json.dumps({
    "title": "Adventures in AI",
    "author": "Jane Coder",
    "publication_date": "2024-05-15"
})
# ... (mock usage)
mock_llm_response_infer_schema.usage = MagicMock()
mock_llm_response_infer_schema.usage.completion_tokens = 30; mock_llm_response_infer_schema.usage.prompt_tokens = 90; mock_llm_response_infer_schema.usage.total_tokens = 120
mock_llm_response_infer_schema.usage.completion_tokens_details = {}; mock_llm_response_infer_schema.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_infer_schema)
def schema_from_instruction_extraction(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            extraction_type="schema_from_instruction",
            instruction="Please extract the title, author, and publication date (YYYY-MM-DD) of this news article."
        )
    except:
        print("Ollama not available, skipping schema_from_instruction test.")
        return

    sample_content = """
    # Adventures in AI
    By Jane Coder, Published on May 15, 2024.
    This article explores the latest trends...
    """
    extracted_json_string = strategy.extract(url="http://dummy.com/news_article", html_content=sample_content)
    
    print("Schema from Instruction Extraction (mocked LLM):")
    if extracted_json_string:
        extracted_data = json.loads(extracted_json_string)
        print(json.dumps(extracted_data, indent=2))
        assert "title" in extracted_data and "author" in extracted_data and "publication_date" in extracted_data
    else:
        print("No data extracted.")

if __name__ == "__main__":
    schema_from_instruction_extraction()
```

#### 3.3.4. Example: Comparing outputs with and without a specific `instruction` when using `extraction_type="schema"`.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json

class Event(BaseModel):
    eventName: str
    location: str
    date: str

# Mock LLM responses
mock_llm_no_instr = MagicMock()
mock_llm_no_instr.choices = [MagicMock()]
mock_llm_no_instr.choices[0].message.content = json.dumps({"eventName": "Tech Meetup", "location": "Online", "date": "2024-06-01"})
mock_llm_no_instr.usage = MagicMock(); mock_llm_no_instr.usage.completion_tokens = 20; mock_llm_no_instr.usage.prompt_tokens = 80; mock_llm_no_instr.usage.total_tokens = 100
mock_llm_no_instr.usage.completion_tokens_details = {}; mock_llm_no_instr.usage.prompt_tokens_details = {}


mock_llm_with_instr = MagicMock()
mock_llm_with_instr.choices = [MagicMock()]
mock_llm_with_instr.choices[0].message.content = json.dumps({"eventName": "AI Conference", "location": "San Francisco", "date": "2024-07-20"})
mock_llm_with_instr.usage = MagicMock(); mock_llm_with_instr.usage.completion_tokens = 22; mock_llm_with_instr.usage.prompt_tokens = 95; mock_llm_with_instr.usage.total_tokens = 117
mock_llm_with_instr.usage.completion_tokens_details = {}; mock_llm_with_instr.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff')
def schema_extraction_instruction_comparison(mock_perform_completion):
    try:
        llm_conf = LLMConfig(provider="ollama/llama3", api_token="ollama")
    except:
        print("Ollama not available, skipping schema instruction comparison test.")
        return

    sample_content = """
    Upcoming Events:
    - Tech Meetup, Online, June 1st, 2024
    - AI Conference, San Francisco, July 20th, 2024
    - Local Bake Sale, Town Hall, June 5th, 2024
    """

    # Case 1: No specific instruction
    mock_perform_completion.return_value = mock_llm_no_instr
    strategy_no_instr = LLMExtractionStrategy(
        llm_config=llm_conf,
        schema=Event.model_json_schema(),
        extraction_type="schema"
    )
    result_no_instr_json = strategy_no_instr.extract(url="http://dummy.com/events", html_content=sample_content)
    result_no_instr = json.loads(result_no_instr_json) if result_no_instr_json else {}
    print(f"Without specific instruction: {result_no_instr}")

    # Case 2: With instruction to focus
    mock_perform_completion.return_value = mock_llm_with_instr
    strategy_with_instr = LLMExtractionStrategy(
        llm_config=llm_conf,
        schema=Event.model_json_schema(),
        extraction_type="schema",
        instruction="Focus on extracting details for the 'AI Conference'."
    )
    result_with_instr_json = strategy_with_instr.extract(url="http://dummy.com/events", html_content=sample_content)
    result_with_instr = json.loads(result_with_instr_json) if result_with_instr_json else {}
    print(f"With instruction to focus on AI Conference: {result_with_instr}")

    assert result_no_instr.get("eventName") == "Tech Meetup" # Mock returns first one
    assert result_with_instr.get("eventName") == "AI Conference" # Mock returns AI conf due to instruction

if __name__ == "__main__":
    schema_extraction_instruction_comparison()
```
---

### 3.4. Controlling `extraction_type`

#### 3.4.1. Example: Demonstrating `extraction_type="block"` - output structure (list of blocks with content and tags).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mock LLM response for block extraction
mock_llm_block_output = MagicMock()
mock_llm_block_output.choices = [MagicMock()]
mock_llm_block_output.choices[0].message.content = """
<blocks>
  <block>
    <content>First important point.</content>
    <tags><tag>key_takeaway</tag></tags>
  </block>
  <block>
    <content>Second supporting detail.</content>
    <tags><tag>detail</tag><tag>supporting_info</tag></tags>
  </block>
</blocks>
"""
mock_llm_block_output.usage = MagicMock(); mock_llm_block_output.usage.completion_tokens=30; mock_llm_block_output.usage.prompt_tokens=70; mock_llm_block_output.usage.total_tokens=100
mock_llm_block_output.usage.completion_tokens_details = {}; mock_llm_block_output.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_block_output)
def demonstrate_block_extraction_type(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            extraction_type="block" # Explicitly set to block
        )
    except:
        print("Ollama not available, skipping block extraction type demo.")
        return

    sample_content = "Some text with a First important point and then a Second supporting detail."
    extracted_data = strategy.extract(url="http://dummy.com/blocks", html_content=sample_content)
    
    print("Block Extraction Output Structure (mocked LLM):")
    print(json.dumps(extracted_data, indent=2))
    
    # Expected output is a list of dictionaries (blocks)
    assert isinstance(extracted_data, list)
    if extracted_data:
        assert "content" in extracted_data[0]
        assert "tags" in extracted_data[0]
        assert isinstance(extracted_data[0]["tags"], list)

if __name__ == "__main__":
    demonstrate_block_extraction_type()
```

#### 3.4.2. Example: Demonstrating `extraction_type="schema"` - output structure (JSON string matching the schema).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json

class MyData(BaseModel):
    field1: str
    field2: int

# Mock LLM response
mock_llm_schema_output = MagicMock()
mock_llm_schema_output.choices = [MagicMock()]
mock_llm_schema_output.choices[0].message.content = json.dumps({"field1": "value1", "field2": 123})
mock_llm_schema_output.usage = MagicMock(); mock_llm_schema_output.usage.completion_tokens=15; mock_llm_schema_output.usage.prompt_tokens=60; mock_llm_schema_output.usage.total_tokens=75
mock_llm_schema_output.usage.completion_tokens_details = {}; mock_llm_schema_output.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_schema_output)
def demonstrate_schema_extraction_type(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            schema=MyData.model_json_schema(),
            extraction_type="schema" # Explicitly set to schema
        )
    except:
        print("Ollama not available, skipping schema extraction type demo.")
        return

    sample_content = "Field one is value1 and field two is 123."
    extracted_json_string = strategy.extract(url="http://dummy.com/schema_data", html_content=sample_content)
    
    print("Schema Extraction Output Structure (mocked LLM):")
    print(f"Raw JSON string from LLM: {extracted_json_string}")
    
    # Expected output is a JSON string that can be parsed into the schema
    if extracted_json_string:
        data = json.loads(extracted_json_string)
        print(f"Parsed data: {data}")
        instance = MyData(**data) # Validate with Pydantic
        assert instance.field1 == "value1"

if __name__ == "__main__":
    demonstrate_schema_extraction_type()
```

#### 3.4.3. Example: Demonstrating `extraction_type="schema_from_instruction"` - output structure (JSON string based on inferred schema).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mock LLM response - LLM infers schema and provides data
mock_llm_infer_schema_output = MagicMock()
mock_llm_infer_schema_output.choices = [MagicMock()]
mock_llm_infer_schema_output.choices[0].message.content = json.dumps({
    "book_title": "The LLM Handbook",
    "pages": 300
})
mock_llm_infer_schema_output.usage = MagicMock(); mock_llm_infer_schema_output.usage.completion_tokens=20; mock_llm_infer_schema_output.usage.prompt_tokens=70; mock_llm_infer_schema_output.usage.total_tokens=90
mock_llm_infer_schema_output.usage.completion_tokens_details = {}; mock_llm_infer_schema_output.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_infer_schema_output)
def demonstrate_schema_from_instruction_type(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            extraction_type="schema_from_instruction",
            instruction="Extract the book title and number of pages."
        )
    except:
        print("Ollama not available, skipping schema_from_instruction type demo.")
        return

    sample_content = "The book 'The LLM Handbook' contains 300 pages of valuable insights."
    extracted_json_string = strategy.extract(url="http://dummy.com/book_info", html_content=sample_content)
    
    print("Schema from Instruction Output Structure (mocked LLM):")
    print(f"Raw JSON string from LLM: {extracted_json_string}")
    
    if extracted_json_string:
        data = json.loads(extracted_json_string)
        print(f"Parsed data: {data}")
        assert "book_title" in data and "pages" in data

if __name__ == "__main__":
    demonstrate_schema_from_instruction_type()
```
---

### 3.5. LLM Configuration (`llm_config`)

#### 3.5.1. Example: Using the default LLM provider and model.
This assumes `OPENAI_API_KEY` is set in the environment, as OpenAI is often a default. If not, it will error or fallback if a global default is set elsewhere (less common for `LLMExtractionStrategy` without explicit config).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig # For explicit configuration if needed
import os

# Note: For this example to run successfully without explicit llm_config, 
# the environment variable OPENAI_API_KEY should be set, or another
# global default LLM provider must be configured for LiteLLM.
# If neither is true, LLMExtractionStrategy() might raise an error.

try:
    # This will try to use the default provider (often OpenAI if key is set)
    # or another globally configured default for LiteLLM.
    strategy_default = LLMExtractionStrategy() 
    print(f"Successfully initialized LLMExtractionStrategy with default provider: {strategy_default.llm_config.provider}")
    # To make this example runnable without a real API call:
    print("Note: Actual extraction would require a configured LLM and API key.")
except Exception as e:
    print(f"Failed to initialize with default LLM provider: {e}")
    print("This example requires a default LLM (e.g., OPENAI_API_KEY set) or LiteLLM global config.")
    print("Alternatively, provide an explicit LLMConfig to LLMExtractionStrategy.")

# To show an explicit (but still default-targeting) configuration:
# if os.getenv("OPENAI_API_KEY"):
#     llm_config_openai = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY"))
#     strategy_explicit_openai = LLMExtractionStrategy(llm_config=llm_config_openai)
#     print(f"Initialized explicitly with OpenAI: {strategy_explicit_openai.llm_config.provider}")
# else:
#     print("OPENAI_API_KEY not set, cannot show explicit OpenAI example.")
```

#### 3.5.2. Example: Configuring `LLMExtractionStrategy` with a specific OpenAI model via `LLMConfig` (e.g., `openai/gpt-4o-mini`).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
import os

# Ensure you have your OPENAI_API_KEY set in your environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("OPENAI_API_KEY not found in environment. Skipping OpenAI example.")
    print("To run this, set your OPENAI_API_KEY.")
else:
    llm_config_openai = LLMConfig(
        provider="openai/gpt-4o-mini", # Specify the OpenAI model
        api_token=openai_api_key
    )
    strategy_openai = LLMExtractionStrategy(llm_config=llm_config_openai)
    print(f"Initialized LLMExtractionStrategy with OpenAI provider: {strategy_openai.llm_config.provider}")
    # To test, you would call strategy_openai.extract(...)
    # For this example, we'll just show initialization.
    print("Strategy ready to use OpenAI gpt-4o-mini.")
```

#### 3.5.3. Example: Configuring `LLMExtractionStrategy` with a specific Ollama model via `LLMConfig` (e.g., `ollama/llama3`).
This requires Ollama to be running locally and the specified model (e.g., `llama3`) to be pulled.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig

# Assumes Ollama is running locally and 'llama3' model is available
# 'api_token' for Ollama is typically 'ollama' or can be omitted if not needed by your setup.
try:
    llm_config_ollama = LLMConfig(
        provider="ollama/llama3", 
        api_token="ollama", # Often 'ollama' or can be None if not required by local setup
        base_url="http://localhost:11434" # Default Ollama API URL
    )
    strategy_ollama = LLMExtractionStrategy(llm_config=llm_config_ollama)
    print(f"Initialized LLMExtractionStrategy with Ollama provider: {strategy_ollama.llm_config.provider}")
    print("Strategy ready to use Ollama with llama3.")
    print("Note: For actual extraction, ensure Ollama server is running and has the 'llama3' model pulled.")
except Exception as e:
    print(f"Failed to initialize Ollama strategy: {e}")
    print("Ensure Ollama is running (e.g., `ollama serve`) and you have pulled the model (e.g., `ollama pull llama3`).")

# Example of a test call (would require Ollama to be active)
# from unittest.mock import patch, MagicMock
# import json
# mock_response = MagicMock()
# mock_response.choices = [MagicMock()]
# mock_response.choices[0].message.content = json.dumps({"info": "extracted by ollama"})
# mock_response.usage = MagicMock(completion_tokens=5, prompt_tokens=10, total_tokens=15)
# mock_response.usage.completion_tokens_details = {}; mock_response.usage.prompt_tokens_details = {}
# @patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_response)
# def _test_ollama_call(mock_call, strategy):
#     if strategy:
#         result = strategy.extract("url", "content", extraction_type="schema_from_instruction", instruction="get info")
#         print(f"Ollama mock call result: {result}")
# _test_ollama_call(None, strategy_ollama if 'strategy_ollama' in locals() else None)
```

#### 3.5.4. Example: Configuring `LLMExtractionStrategy` with a specific Gemini model via `LLMConfig`.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
import os

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    print("GEMINI_API_KEY not found in environment. Skipping Gemini example.")
    print("To run this, set your GEMINI_API_KEY.")
else:
    llm_config_gemini = LLMConfig(
        provider="gemini/gemini-1.5-pro-latest", # Or another Gemini model
        api_token=gemini_api_key
    )
    strategy_gemini = LLMExtractionStrategy(llm_config=llm_config_gemini)
    print(f"Initialized LLMExtractionStrategy with Gemini provider: {strategy_gemini.llm_config.provider}")
    print("Strategy ready to use Gemini.")
```

#### 3.5.5. Example: Configuring `LLMExtractionStrategy` with a specific Anthropic (Claude) model via `LLMConfig`.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
import os

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

if not anthropic_api_key:
    print("ANTHROPIC_API_KEY not found in environment. Skipping Anthropic Claude example.")
    print("To run this, set your ANTHROPIC_API_KEY.")
else:
    llm_config_claude = LLMConfig(
        provider="anthropic/claude-3-opus-20240229", # Or another Claude model
        api_token=anthropic_api_key
    )
    strategy_claude = LLMExtractionStrategy(llm_config=llm_config_claude)
    print(f"Initialized LLMExtractionStrategy with Anthropic provider: {strategy_claude.llm_config.provider}")
    print("Strategy ready to use Claude.")

```

#### 3.5.6. Example: Overriding LLM parameters like `temperature` and `max_tokens` using `LLMConfig`.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
import os

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("OPENAI_API_KEY not found. This example shows parameter override with OpenAI.")
else:
    llm_config_custom_params = LLMConfig(
        provider="openai/gpt-3.5-turbo", # Using a common model for this example
        api_token=openai_api_key,
        temperature=0.2,       # Lower temperature for more deterministic output
        max_tokens=150         # Limit the maximum number of tokens in the response
        # You can add other provider-specific parameters here in extra_args if needed
        # extra_args={"top_p": 0.9} 
    )
    
    strategy_custom_params = LLMExtractionStrategy(
        llm_config=llm_config_custom_params,
        instruction="Extract the main point." # A simple instruction
    )
    
    print(f"Initialized LLMExtractionStrategy with custom LLM parameters for provider: {strategy_custom_params.llm_config.provider}")
    print(f"  Temperature: {strategy_custom_params.llm_config.temperature}")
    print(f"  Max Tokens: {strategy_custom_params.llm_config.max_tokens}")
    # print(f"  Extra Args: {strategy_custom_params.extra_args}") # Note: extra_args on LLMExtractionStrategy, not LLMConfig for this
    
    # A mock test to show parameters would be passed to perform_completion_with_backoff
    # from unittest.mock import patch, MagicMock
    # mock_response = MagicMock() # ... (setup mock_response) ...
    # @patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_response)
    # def _test_params(mock_call):
    #     strategy_custom_params.extract("url", "content")
    #     called_args = mock_call.call_args
    #     assert called_args is not None
    #     assert called_args.kwargs.get('temperature') == 0.2
    #     assert called_args.kwargs.get('max_tokens') == 150
    #     print("LLM call would have used temperature=0.2 and max_tokens=150.")
    # _test_params()
```

#### 3.5.7. Example: Using `LLMConfig` to specify a custom `base_url` for a self-hosted LLM.
This is useful for local LLMs like Ollama (already shown), vLLM, or other self-hosted OpenAI-compatible endpoints.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig

# Example for a generic OpenAI-compatible API running locally
# The provider name might need to be "openai/custom-model-name" or just "custom/model-name"
# depending on how LiteLLM handles it. For Ollama, it's typically "ollama/model-name".
custom_llm_config = LLMConfig(
    provider="custom/my-local-model", # Or "openai/my-local-model"
    api_token="no_key_needed_for_local", # Or your actual local key
    base_url="http://localhost:8000/v1" # Adjust to your local LLM API endpoint
)

try:
    strategy_custom_endpoint = LLMExtractionStrategy(llm_config=custom_llm_config)
    print(f"Initialized LLMExtractionStrategy with custom endpoint:")
    print(f"  Provider: {strategy_custom_endpoint.llm_config.provider}")
    print(f"  Base URL: {strategy_custom_endpoint.llm_config.base_url}")
    print("Note: This example assumes an OpenAI-compatible API is running at the specified base_url.")
except Exception as e:
    print(f"Failed to initialize custom endpoint strategy: {e}")

# Example for Ollama (already covered more specifically, but fits here too)
ollama_local_config = LLMConfig(
    provider="ollama/mistral", # Assuming mistral model is pulled
    base_url="http://localhost:11434", # Default Ollama
    api_token="ollama" # Usually 'ollama' or None
)
try:
    strategy_ollama_local = LLMExtractionStrategy(llm_config=ollama_local_config)
    print(f"\nInitialized LLMExtractionStrategy with local Ollama endpoint:")
    print(f"  Provider: {strategy_ollama_local.llm_config.provider}")
    print(f"  Base URL: {strategy_ollama_local.llm_config.base_url}")
except Exception as e:
    print(f"Failed to initialize local Ollama strategy via custom base_url example: {e}")
```
---

### 3.6. Chunking Configuration (`apply_chunking` and related parameters)

#### 3.6.1. Example: Default chunking behavior (`apply_chunking=True`).
When content is long, `LLMExtractionStrategy` automatically chunks it.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mock LLM to be called multiple times if chunking happens
mock_responses = []
for i in range(3): # Simulate 3 chunks
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps({"chunk_data": f"Data from chunk {i+1}"})
    mock_resp.usage = MagicMock(completion_tokens=10, prompt_tokens=50, total_tokens=60)
    mock_resp.usage.completion_tokens_details = {}; mock_resp.usage.prompt_tokens_details = {}
    mock_responses.append(mock_resp)

@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', side_effect=mock_responses)
def default_chunking_behavior(mock_perform_completion):
    try:
        # Use a small chunk_token_threshold to force chunking for the example
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            extraction_type="schema_from_instruction",
            instruction="Extract data from this chunk.",
            chunk_token_threshold=10, # Very small to ensure chunking
            word_token_rate=0.75, # Approx tokens per word
            apply_chunking=True # Default
        )
    except:
        print("Ollama not available, skipping default chunking test.")
        return

    # Create content long enough to be chunked based on threshold and word_token_rate
    # (10 tokens / 0.75 tokens/word) approx 13 words for threshold.
    # Let's use 50 words.
    long_content = " ".join(["word"] * 50) 
    
    extracted_data_json = strategy.extract(url="http://dummy.com/long_content", html_content=long_content)
    
    print("Default Chunking Behavior (mocked LLM):")
    # The strategy internally merges results from chunks if schema-based.
    # For "schema_from_instruction", it might return a list of JSON strings or a merged JSON.
    # Current LLMExtractionStrategy for schema type returns a single JSON string, implying merging.
    # If it's block extraction, it would be a list of blocks.
    # Let's assume for schema extraction, it returns a list of dicts before final JSON dump in the example
    
    # The mock setup implies multiple calls. LLMExtractionStrategy aggregates results.
    # If the LLM returns a list for each chunk, results would be concatenated.
    # If it returns a dict, they'd be in a list.
    # The current mock returns a dict per chunk, so we expect a list of dicts if not merged by strategy.
    # However, the `extract` method's return is a single JSON string if schema-based.
    # This means the strategy handles merging internally or expects LLM to handle it.
    # For this test, we'll check if the LLM was called multiple times.
    
    print(f"LLM called {mock_perform_completion.call_count} times.")
    assert mock_perform_completion.call_count > 1, "Chunking should have occurred, LLM expected to be called multiple times."
    print(f"Final extracted JSON string: {extracted_data_json}")
    # Final result depends on how LLM merges/formats if it gets multiple chunk results.
    # Assuming the mock's structure (list of chunk_data) would be presented as a list by the LLM.
    if extracted_data_json:
        final_data = json.loads(extracted_data_json)
        print(json.dumps(final_data, indent=2))
        # Depending on LLM's aggregation logic, this might be a list or a single dict.
        # For this example, if our mock returns individual dicts, and the LLM is asked to provide a final JSON,
        # it might wrap them in a list. Let's assume it does.
        # For this particular mock structure and schema_from_instruction, the LLM would typically be
        # instructed to return a list of items if the content implies multiple items.
        # Here, the mock returns individual dicts, and the strategy just returns the last one.
        # To properly test chunk aggregation, a more sophisticated mock or real LLM is needed.
        # For now, verifying multiple calls is the main goal.

if __name__ == "__main__":
    default_chunking_behavior()
```

#### 3.6.2. Example: Disabling chunking (`apply_chunking=False`) for short content.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

mock_llm_no_chunking = MagicMock()
mock_llm_no_chunking.choices = [MagicMock()]
mock_llm_no_chunking.choices[0].message.content = json.dumps({"summary": "This is short content."})
mock_llm_no_chunking.usage = MagicMock(completion_tokens=5, prompt_tokens=20, total_tokens=25)
mock_llm_no_chunking.usage.completion_tokens_details = {}; mock_llm_no_chunking.usage.prompt_tokens_details = {}

@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_no_chunking)
def disable_chunking_behavior(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            apply_chunking=False, # Explicitly disable chunking
            extraction_type="schema_from_instruction",
            instruction="Summarize this."
        )
    except:
        print("Ollama not available, skipping disable chunking test.")
        return

    # Content is short enough that chunking wouldn't happen anyway, but this forces it.
    short_content = "This is a piece of short content." 
    extracted_data_json = strategy.extract(url="http://dummy.com/short", html_content=short_content)
    
    print("Disabled Chunking Behavior (mocked LLM):")
    print(f"LLM called {mock_perform_completion.call_count} time(s).")
    assert mock_perform_completion.call_count == 1, "Chunking was disabled, LLM should be called once."
    if extracted_data_json:
        print(json.dumps(json.loads(extracted_data_json), indent=2))


if __name__ == "__main__":
    disable_chunking_behavior()
```

#### 3.6.3. Example: Customizing `chunk_token_threshold` for smaller/larger chunks.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mock setup
mock_llm_response_chunk_size = MagicMock()
mock_llm_response_chunk_size.choices = [MagicMock()]
mock_llm_response_chunk_size.choices[0].message.content = json.dumps({"info": "some data"})
mock_llm_response_chunk_size.usage = MagicMock(completion_tokens=5, prompt_tokens=10, total_tokens=15)
mock_llm_response_chunk_size.usage.completion_tokens_details = {}; mock_llm_response_chunk_size.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_response_chunk_size)
def customize_chunk_token_threshold(mock_perform_completion):
    long_text = " ".join(["word_for_testing_chunk_size"] * 100) # Approx 100 words
    
    # Scenario 1: Small threshold, more chunks
    try:
        strategy_small_chunks = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            chunk_token_threshold=20, # Small threshold, e.g., ~26 words
            word_token_rate=0.75,
            extraction_type="schema_from_instruction", instruction="get info"
        )
    except:
        print("Ollama not available, cannot run small chunk test.")
        strategy_small_chunks = None

    if strategy_small_chunks:
        strategy_small_chunks.extract(url="http://dummy.com/small_chunks", html_content=long_text)
        print(f"Small chunk_token_threshold (20): LLM called {mock_perform_completion.call_count} times.")
        small_chunk_calls = mock_perform_completion.call_count
        mock_perform_completion.reset_mock() # Reset for next call
    else:
        small_chunk_calls = 0

    # Scenario 2: Larger threshold, fewer chunks
    try:
        strategy_large_chunks = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            chunk_token_threshold=80, # Larger threshold, e.g., ~106 words
            word_token_rate=0.75,
            extraction_type="schema_from_instruction", instruction="get info"
        )
    except:
        print("Ollama not available, cannot run large chunk test.")
        strategy_large_chunks = None

    if strategy_large_chunks:
        strategy_large_chunks.extract(url="http://dummy.com/large_chunks", html_content=long_text)
        print(f"Large chunk_token_threshold (80): LLM called {mock_perform_completion.call_count} times.")
        large_chunk_calls = mock_perform_completion.call_count
    else:
        large_chunk_calls = 0
        
    if strategy_small_chunks and strategy_large_chunks:
        assert small_chunk_calls > large_chunk_calls, "Smaller threshold should result in more LLM calls."

if __name__ == "__main__":
    customize_chunk_token_threshold()
```

#### 3.6.4. Example: Customizing `overlap_rate` between chunks.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mock setup - we'll primarily observe the number of calls or potentially the prompt content
mock_llm_overlap = MagicMock()
mock_llm_overlap.choices = [MagicMock()]
mock_llm_overlap.choices[0].message.content = json.dumps({"data_point": "value"})
mock_llm_overlap.usage = MagicMock(completion_tokens=5, prompt_tokens=10, total_tokens=15)
mock_llm_overlap.usage.completion_tokens_details = {}; mock_llm_overlap.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.LLMExtractionStrategy._create_llm_query_tasks') # Patching internal method to inspect chunks
def customize_overlap_rate(mock_create_tasks):
    # The _create_llm_query_tasks method is a good place to see the generated chunks.
    # It returns a list of partials. We can inspect the 'content' arg of the partials.
    
    long_text = "This is a moderately long text to demonstrate the effect of chunk overlap. " * 5
    # word_token_rate (default 0.75) means ~1 token per 1.33 words.
    # chunk_token_threshold (default 2048) is large.
    # Let's use a smaller threshold for demonstration.
    # Threshold 30 tokens => ~40 words.
    # Overlap 0.1 => 3 token overlap => ~4 words.
    # Overlap 0.5 => 15 token overlap => ~20 words.

    # Scenario 1: Small overlap
    try:
        strategy_small_overlap = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            chunk_token_threshold=30,
            overlap_rate=0.1, # 10% overlap
            extraction_type="block" # Block type is easier to see chunk content
        )
    except:
        print("Ollama not available. Skipping overlap rate test.")
        return

    strategy_small_overlap.extract(url="http://dummy.com/overlap1", html_content=long_text)
    chunks_small_overlap = [task.args[1] for task in mock_create_tasks.call_args[0][0]] # (tasks_list, url)
    print(f"Small overlap_rate (0.1) generated {len(chunks_small_overlap)} chunks.")
    if len(chunks_small_overlap) > 1:
        print(f"  Chunk 1 (end): ...{chunks_small_overlap[0][-30:]}")
        print(f"  Chunk 2 (start): {chunks_small_overlap[1][:30]}...")
    mock_create_tasks.reset_mock()

    # Scenario 2: Larger overlap
    strategy_large_overlap = LLMExtractionStrategy(
        llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
        chunk_token_threshold=30,
        overlap_rate=0.5, # 50% overlap
        extraction_type="block"
    )
    strategy_large_overlap.extract(url="http://dummy.com/overlap2", html_content=long_text)
    chunks_large_overlap = [task.args[1] for task in mock_create_tasks.call_args[0][0]]
    print(f"Large overlap_rate (0.5) generated {len(chunks_large_overlap)} chunks.")
    if len(chunks_large_overlap) > 1:
        print(f"  Chunk 1 (end): ...{chunks_large_overlap[0][-30:]}")
        print(f"  Chunk 2 (start): {chunks_large_overlap[1][:30]}...")
    
    # With more overlap, for the same content and threshold, you might get more chunks,
    # or similar number of chunks but with more redundant content.
    # This example primarily shows the parameter being used.
    # Actual number of chunks can be complex to predict without exact tokenization.

if __name__ == "__main__":
    customize_overlap_rate()
```

#### 3.6.5. Example: Demonstrating the effect of different `word_token_rate` values.
The `word_token_rate` helps estimate token count from word count for chunking.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock

# We'll patch the internal chunking function to see how many chunks are made.
# Or, more simply, observe the number of LLM calls if apply_chunking=True.

mock_llm_wtr = MagicMock() # Generic mock for counting calls
mock_llm_wtr.choices = [MagicMock(message=MagicMock(content="{}"))]
mock_llm_wtr.usage = MagicMock(completion_tokens=1, prompt_tokens=1, total_tokens=2)
mock_llm_wtr.usage.completion_tokens_details = {}; mock_llm_wtr.usage.prompt_tokens_details = {}

@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_wtr)
def customize_word_token_rate(mock_perform_completion):
    # Approx 50 words.
    # word_token_rate helps estimate token length for chunking.
    # chunk_token_threshold default is large (2048), so let's use a smaller one.
    test_content = "This is a test sentence. It has ten words precisely. " * 5 

    try:
        # Scenario 1: Lower word_token_rate (means more words per token, so fewer tokens for same text)
        # Should result in fewer chunks if text length is near threshold.
        strategy_low_wtr = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            chunk_token_threshold=30, # e.g. needs 30 tokens
            word_token_rate=0.5, # Estimates 0.5 tokens per word (i.e., 2 words/token)
                                 # So 50 words -> ~25 tokens. Should be 1 chunk.
            extraction_type="block"
        )
        strategy_low_wtr.extract("url", test_content)
        calls_low_wtr = mock_perform_completion.call_count
        print(f"word_token_rate=0.5 (estimates fewer tokens): LLM calls = {calls_low_wtr}")
        mock_perform_completion.reset_mock()

        # Scenario 2: Higher word_token_rate (means fewer words per token, so more tokens for same text)
        # Should result in more chunks if text length is near threshold.
        strategy_high_wtr = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            chunk_token_threshold=30,
            word_token_rate=1.0, # Estimates 1 token per word
                                 # So 50 words -> ~50 tokens. Should be >1 chunk.
            extraction_type="block"
        )
        strategy_high_wtr.extract("url", test_content)
        calls_high_wtr = mock_perform_completion.call_count
        print(f"word_token_rate=1.0 (estimates more tokens): LLM calls = {calls_high_wtr}")

        assert calls_high_wtr >= calls_low_wtr, \
            "Higher word_token_rate should lead to more or equal chunks for the same content and token threshold."

    except Exception as e:
        print(f"Ollama not available or other error, skipping word_token_rate test: {e}")


if __name__ == "__main__":
    customize_word_token_rate()
```

#### 3.6.6. Example: Processing very large content that requires multiple chunks.
This is similar to 3.6.1, emphasizing that the system handles large inputs by breaking them down.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Simulate multiple LLM calls for multiple chunks
mock_responses_large_content = []
for i in range(5): # Expecting around 5 chunks for this example
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    # Simulate LLM returning structured data for each chunk
    mock_resp.choices[0].message.content = json.dumps({"document_part": f"Content from part {i+1} of the large document."})
    mock_resp.usage = MagicMock(completion_tokens=15, prompt_tokens=100, total_tokens=115) # Example usage
    mock_resp.usage.completion_tokens_details = {}; mock_resp.usage.prompt_tokens_details = {}
    mock_responses_large_content.append(mock_resp)


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', side_effect=mock_responses_large_content)
def process_very_large_content(mock_perform_completion):
    # Content designed to be split into several chunks
    # Assuming chunk_token_threshold=50 and word_token_rate=0.75 (~66 words/chunk)
    # This content has 300 words. 300 / (50/0.75) = 300 / 66.6 = ~4.5 chunks
    very_large_content = ("This is a segment of a very large document that needs to be processed. " * 60) # 300 words

    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            extraction_type="schema_from_instruction",
            instruction="Extract key information from this segment of the document.",
            chunk_token_threshold=50, # Smaller threshold to ensure multiple chunks
            word_token_rate=0.75,      # Estimate tokens per word
            apply_chunking=True
        )
    except:
        print("Ollama not available, skipping large content chunking test.")
        return

    print("Processing very large content (mocked LLM calls per chunk)...")
    # The extract method will handle the chunking and aggregation if extraction_type is schema-based.
    # The final extracted_data_json should ideally be a merged/structured result.
    # For this mock, the LLM is assumed to return a list of objects if instruction implies it.
    # Here, we'll get the last chunk's result if schema_from_instruction unless LLM aggregates.
    # To truly show aggregation, a more complex mocking or real LLM is needed.
    # Focus here is on the multiple calls due to chunking.
    
    extracted_data_json_string = strategy.extract(url="http://dummy.com/very_large_doc", html_content=very_large_content)
    
    print(f"LLM was called {mock_perform_completion.call_count} times due to chunking.")
    assert mock_perform_completion.call_count > 1, "Expected multiple LLM calls for large content."

    print("Final Extracted Data (structure depends on LLM's handling of chunked results):")
    if extracted_data_json_string:
        print(json.dumps(json.loads(extracted_data_json_string), indent=2))
    else:
        print("No data extracted or an error occurred.")
        
if __name__ == "__main__":
    process_very_large_content()
```
---

### 3.7. Input Format Selection (`input_format`)

#### 3.7.1. Example: Extracting from Markdown content (`input_format="markdown"`, default).
This is the default behavior if `input_format` is not specified.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

mock_llm_md_input = MagicMock() # Setup mock as before
mock_llm_md_input.choices = [MagicMock(message=MagicMock(content=json.dumps({"title": "Markdown Test"})))]
mock_llm_md_input.usage = MagicMock(completion_tokens=5, prompt_tokens=30, total_tokens=35)
mock_llm_md_input.usage.completion_tokens_details = {}; mock_llm_md_input.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_md_input)
def extract_from_markdown(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            input_format="markdown", # Explicitly set, though it's the default
            extraction_type="schema_from_instruction",
            instruction="Extract the main title."
        )
    except:
        print("Ollama not available, skipping markdown input test.")
        return

    sample_markdown = "# Markdown Test\nThis is some **bold** text."
    extracted_json = strategy.extract(url="http://dummy.com/md_page", html_content=sample_markdown)
    
    print("Extraction from Markdown (mocked LLM):")
    if extracted_json:
        print(json.dumps(json.loads(extracted_json), indent=2))

if __name__ == "__main__":
    extract_from_markdown()
```

#### 3.7.2. Example: Extracting directly from raw HTML (`input_format="html"`).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

mock_llm_html_input = MagicMock() # Setup mock
mock_llm_html_input.choices = [MagicMock(message=MagicMock(content=json.dumps({"page_heading": "HTML Document"})))]
mock_llm_html_input.usage = MagicMock(completion_tokens=6, prompt_tokens=40, total_tokens=46)
mock_llm_html_input.usage.completion_tokens_details = {}; mock_llm_html_input.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_html_input)
def extract_from_raw_html(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            input_format="html",
            extraction_type="schema_from_instruction",
            instruction="Extract the main heading (h1)."
        )
    except:
        print("Ollama not available, skipping raw HTML input test.")
        return

    sample_html = "<html><head><title>Test</title></head><body><h1>HTML Document</h1><p>Content</p></body></html>"
    extracted_json = strategy.extract(url="http://dummy.com/html_page", html_content=sample_html)
    
    print("Extraction from Raw HTML (mocked LLM):")
    if extracted_json:
        print(json.dumps(json.loads(extracted_json), indent=2))

if __name__ == "__main__":
    extract_from_raw_html()
```

#### 3.7.3. Example: Extracting from filtered HTML (`input_format="fit_html"`) after `MarkdownGenerator` with a `ContentFilterStrategy` has run.
This example shows a two-step process: first filtering HTML using `MarkdownGenerator` and a `ContentFilterStrategy`, then feeding its `fit_html` output to `LLMExtractionStrategy`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter # Example filter
from unittest.mock import patch, MagicMock
import json

# Mock for the LLMExtractionStrategy part
mock_llm_fit_html = MagicMock()
mock_llm_fit_html.choices = [MagicMock(message=MagicMock(content=json.dumps({"main_content_summary": "Summary of pruned content."})))]
mock_llm_fit_html.usage = MagicMock(completion_tokens=10, prompt_tokens=50, total_tokens=60)
mock_llm_fit_html.usage.completion_tokens_details = {}; mock_llm_fit_html.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_fit_html)
async def extract_from_fit_html(mock_perform_completion):
    # Step 1: Setup MarkdownGenerator with a content filter to produce fit_html
    # For this example, we'll use PruningContentFilter.
    # In a real scenario, you might need an LLM for more advanced filters.
    # We'll use a simple mock HTML for this part.
    
    sample_raw_html = """
    <html><body>
        <header>Site Navigation</header>
        <nav>Links...</nav>
        <main>
            <h1>Main Article Title</h1>
            <p>This is the core content we want to keep.</p>
            <p>Another paragraph of important stuff.</p>
        </main>
        <aside>Related links</aside>
        <footer>Copyright info</footer>
    </body></html>
    """

    # Simulate getting fit_html (normally from crawler.arun() and result.markdown.fit_html)
    # Here we manually instantiate and run the filter's logic conceptually
    # Note: MarkdownGenerator itself creates fit_html when a filter is active
    # For simplicity, let's assume PruningContentFilter directly gives us usable HTML for LLM
    
    # A more accurate simulation would involve creating a MarkdownGenerator
    # and getting its `fit_html`. PruningContentFilter directly manipulates soup.
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_raw_html, "lxml")
    pruning_filter = PruningContentFilter() 
    # PruningContentFilter.filter_content modifies soup in-place and returns string list
    # We will simulate its effect by just taking the main content for this test
    main_content_element = soup.find("main")
    fit_html_content = str(main_content_element) if main_content_element else "<p>Filtered content.</p>"
    
    print(f"--- Simulated Fit HTML (for LLM input) ---\n{fit_html_content}\n--------------------------------------")

    # Step 2: Use LLMExtractionStrategy with input_format="fit_html" (or just "html" if it's valid HTML)
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            input_format="html", # fit_html is still HTML, or use "fit_html" if specific handling is added
            extraction_type="schema_from_instruction",
            instruction="Summarize the main content provided."
        )
    except:
        print("Ollama not available, skipping fit_html extraction test.")
        return

    extracted_json = strategy.extract(url="http://dummy.com/filtered_page", html_content=fit_html_content)
    
    print("\nExtraction from Fit HTML (mocked LLM):")
    if extracted_json:
        print(json.dumps(json.loads(extracted_json), indent=2))
    
    assert mock_perform_completion.called

if __name__ == "__main__":
    asyncio.run(extract_from_fit_html())
```

#### 3.7.4. Example: Extracting from plain text content (`input_format="text"`).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

mock_llm_text_input = MagicMock() # Setup mock
mock_llm_text_input.choices = [MagicMock(message=MagicMock(content=json.dumps({"sentiment": "positive"})))]
mock_llm_text_input.usage = MagicMock(completion_tokens=3, prompt_tokens=25, total_tokens=28)
mock_llm_text_input.usage.completion_tokens_details = {}; mock_llm_text_input.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_text_input)
def extract_from_plain_text(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            input_format="text",
            extraction_type="schema_from_instruction",
            instruction="Determine the sentiment of this text."
        )
    except:
        print("Ollama not available, skipping plain text input test.")
        return

    sample_text = "Crawl4ai is an amazing library for web scraping and data extraction!"
    extracted_json = strategy.extract(url="http://dummy.com/text_page", html_content=sample_text) 
    # html_content parameter is used for any text-based input, despite its name
    
    print("Extraction from Plain Text (mocked LLM):")
    if extracted_json:
        print(json.dumps(json.loads(extracted_json), indent=2))

if __name__ == "__main__":
    extract_from_plain_text()
```
---

### 3.8. Forcing JSON Response (`force_json_response`)

#### 3.8.1. Example: Using `force_json_response=True` with `extraction_type="schema"` or `"schema_from_instruction"`.
This is particularly useful with LLMs that might not strictly adhere to JSON output, or when using providers that support JSON mode.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json

class UserProfile(BaseModel):
    username: str
    email: str

# Mock LLM: simulate it trying to return JSON but maybe with extra text
# if force_json_response was False. With True, it should ensure clean JSON.
mock_llm_force_json = MagicMock()
mock_llm_force_json.choices = [MagicMock()]
# LiteLLM's JSON mode (which force_json_response=True often enables)
# typically ensures the LLM's output is directly the JSON object string.
mock_llm_force_json.choices[0].message.content = json.dumps(
    {"username": "testuser", "email": "test@example.com"}
)
mock_llm_force_json.usage = MagicMock(completion_tokens=15, prompt_tokens=70, total_tokens=85)
mock_llm_force_json.usage.completion_tokens_details = {}; mock_llm_force_json.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_force_json)
def force_json_response_example(mock_perform_completion):
    try:
        # Note: Some providers/models have better native JSON mode support.
        # OpenAI models often benefit from this.
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY","mock_key")), # Using OpenAI example
            schema=UserProfile.model_json_schema(),
            extraction_type="schema",
            force_json_response=True # Enable JSON mode
        )
        if not os.getenv("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY not set. Mocking will proceed, but real behavior might differ.")

    except:
        print("LLM provider not available, skipping force_json_response test.")
        return

    sample_content = "User: testuser, Email: test@example.com"
    extracted_json_string = strategy.extract(url="http://dummy.com/user", html_content=sample_content)
    
    print("Force JSON Response Example (mocked LLM):")
    if extracted_json_string:
        print(f"Raw output from LLM (should be clean JSON string): {extracted_json_string}")
        try:
            extracted_data = json.loads(extracted_json_string)
            print("Parsed data:", json.dumps(extracted_data, indent=2))
            UserProfile(**extracted_data) # Validate
            print("Successfully parsed and validated JSON.")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON even with force_json_response: {e}")
            print("This might indicate an issue with the LLM's JSON mode or the mock setup.")
    else:
        print("No data extracted.")
    
    # Check if the 'response_format' was passed to litellm
    # This depends on the internal implementation detail of how force_json_response is passed.
    # Assuming it sets 'response_format': {'type': 'json_object'} in extra_args for litellm.
    # mock_perform_completion.assert_called_once()
    # call_kwargs = mock_perform_completion.call_args.kwargs
    # assert call_kwargs.get("extra_args", {}).get("response_format") == {"type": "json_object"}
    # print("LLM call included JSON response format.")


if __name__ == "__main__":
    force_json_response_example()
```

#### 3.8.2. Example: Comparing LLM output with and without `force_json_response=True` to show its effect on non-JSON-compliant LLMs.
This example requires an LLM that is known to sometimes produce non-JSON output or a more sophisticated mock.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json
import os

class SimpleData(BaseModel):
    key: str

# Mock 1: LLM returns non-JSON compliant string
mock_llm_non_json = MagicMock()
mock_llm_non_json.choices = [MagicMock()]
mock_llm_non_json.choices[0].message.content = "Here is the JSON you asked for: ```json\n{\"key\": \"value_one\"}\n``` Some extra text."
mock_llm_non_json.usage = MagicMock(completion_tokens=30, prompt_tokens=80, total_tokens=110)
mock_llm_non_json.usage.completion_tokens_details = {}; mock_llm_non_json.usage.prompt_tokens_details = {}


# Mock 2: LLM returns clean JSON (as if force_json_response worked)
mock_llm_forced_json = MagicMock()
mock_llm_forced_json.choices = [MagicMock()]
mock_llm_forced_json.choices[0].message.content = json.dumps({"key": "value_one"})
mock_llm_forced_json.usage = MagicMock(completion_tokens=10, prompt_tokens=80, total_tokens=90)
mock_llm_forced_json.usage.completion_tokens_details = {}; mock_llm_forced_json.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff')
def compare_force_json_response(mock_perform_completion):
    sample_content = "The key is value_one."
    schema_def = SimpleData.model_json_schema()
    
    try:
        # Using a provider that might benefit from force_json_response
        llm_config_for_comparison = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY","mock_key_compare"))
        if not os.getenv("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY not set for comparison. Mocking will show intended difference.")
    except:
        print("LLM provider not available, skipping force_json comparison test.")
        return

    # Case 1: force_json_response = False (default)
    mock_perform_completion.return_value = mock_llm_non_json
    strategy_no_force = LLMExtractionStrategy(
        llm_config=llm_config_for_comparison,
        schema=schema_def,
        extraction_type="schema",
        force_json_response=False
    )
    print("--- Without force_json_response ---")
    result_no_force_json_str = strategy_no_force.extract("url", sample_content)
    print(f"Raw output: {result_no_force_json_str}")
    try:
        data_no_force = json.loads(result_no_force_json_str) # This would likely fail with the mock
        print(f"Parsed data: {data_no_force}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse as JSON (expected for this mock): {e}")

    # Case 2: force_json_response = True
    mock_perform_completion.return_value = mock_llm_forced_json
    strategy_with_force = LLMExtractionStrategy(
        llm_config=llm_config_for_comparison,
        schema=schema_def,
        extraction_type="schema",
        force_json_response=True
    )
    print("\n--- With force_json_response = True ---")
    result_with_force_json_str = strategy_with_force.extract("url", sample_content)
    print(f"Raw output: {result_with_force_json_str}")
    try:
        data_with_force = json.loads(result_with_force_json_str)
        SimpleData(**data_with_force) # Validate
        print(f"Parsed data: {data_with_force} (Successfully parsed and validated)")
    except json.JSONDecodeError as e:
        print(f"Failed to parse as JSON (unexpected with good JSON mode): {e}")

if __name__ == "__main__":
    compare_force_json_response()
```
---

### 3.9. Verbosity and Logging

#### 3.9.1. Example: Using `verbose=True` to see detailed LLM interaction logs.
Setting `verbose=True` in `LLMExtractionStrategy` enables detailed logging of prompts sent to and responses received from the LLM.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig, DefaultLogger
from unittest.mock import patch, MagicMock
import json
import io
import sys

# Mock LLM response
mock_llm_verbose = MagicMock()
mock_llm_verbose.choices = [MagicMock(message=MagicMock(content=json.dumps({"data": "verbose example"})))]
mock_llm_verbose.usage = MagicMock(completion_tokens=5, prompt_tokens=10, total_tokens=15)
mock_llm_verbose.usage.completion_tokens_details = {}; mock_llm_verbose.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_verbose)
def verbose_logging_example(mock_perform_completion):
    # Capture stdout to check for verbose logs
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        # Use a simple logger for this example that prints to stdout
        logger = DefaultLogger(verbose=True) 
        
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            verbose=True, # Enable verbose logging in the strategy
            logger=logger,  # Pass the logger
            extraction_type="schema_from_instruction",
            instruction="Extract something."
        )
    except: # Fallback if ollama/logger setup fails for some reason in test env
        sys.stdout = old_stdout
        print("Ollama/Logger not available, skipping verbose logging test.")
        return


    strategy.extract(url="http://dummy.com/verbose", html_content="Some sample content.")
    
    sys.stdout = old_stdout # Restore stdout
    output_log = captured_output.getvalue()
    
    print("\n--- Captured Verbose Log Output (should contain LLM prompt/response details) ---")
    print(output_log)

    # Check for typical verbose log messages (actual messages might vary)
    assert "LLM Request" in output_log or "Prompt for LLM" in output_log
    assert "LLM Response" in output_log or "Response from LLM" in output_log
    print("\nVerbose logging appeared to work.")

if __name__ == "__main__":
    verbose_logging_example()
```

#### 3.9.2. Example: Providing a custom `logger` instance to `LLMExtractionStrategy`.
You can integrate `LLMExtractionStrategy` with your existing logging setup.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig, DefaultLogger
import logging
import io

# Setup a custom Python logger
custom_logger = logging.getLogger("MyCustomExtractorLogger")
custom_logger.setLevel(logging.INFO)
log_capture_string = io.StringIO()
ch = logging.StreamHandler(log_capture_string)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
custom_logger.addHandler(ch)
custom_logger.propagate = False # Prevent duplicate logs if root logger also has a handler

# For LLMExtractionStrategy, we need to wrap this in a Crawl4ai compatible logger
class CustomCrawl4aiLogger(DefaultLogger):
    def __init__(self, py_logger, verbose=False):
        super().__init__(verbose=verbose)
        self.py_logger = py_logger

    def _log(self, level_str, message, tag=None, params=None, colors=None):
        # You can customize how messages are formatted and logged here
        log_message = f"[{tag or 'C4AI'}] {message}"
        if params:
            log_message = log_message.format(**params)
        
        if level_str.lower() == "info":
            self.py_logger.info(log_message)
        elif level_str.lower() == "error":
            self.py_logger.error(log_message)
        elif level_str.lower() == "warning":
            self.py_logger.warning(log_message)
        elif self.verbose and level_str.lower() == "debug": # Only log debug if verbose
             self.py_logger.debug(log_message)


# Mock the LLM call for this example to focus on logging
from unittest.mock import patch, MagicMock
import json
mock_llm_custom_log = MagicMock()
mock_llm_custom_log.choices = [MagicMock(message=MagicMock(content=json.dumps({"info":"logged"})))]
mock_llm_custom_log.usage = MagicMock(completion_tokens=3, prompt_tokens=10, total_tokens=13)
mock_llm_custom_log.usage.completion_tokens_details = {}; mock_llm_custom_log.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_custom_log)
def custom_logger_example(mock_perform_completion):
    crawl4ai_custom_logger = CustomCrawl4aiLogger(custom_logger, verbose=True)
    
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            logger=crawl4ai_custom_logger, # Pass the custom logger instance
            verbose=True, # Ensure strategy attempts to log debug messages too
            extraction_type="schema_from_instruction",
            instruction="Log this."
        )
    except:
        print("Ollama not available, skipping custom logger test.")
        return

    strategy.extract(url="http://dummy.com/custom_log", html_content="Content for custom logger.")
    
    log_contents = log_capture_string.getvalue()
    print("\n--- Captured Log Output (via custom Python logger) ---")
    print(log_contents)
    
    assert "MyCustomExtractorLogger" in log_contents # Check if our logger's name is in output
    assert "[LLM_REQ]" in log_contents or "[LLM_RESP]" in log_contents # Check for common strategy tags

if __name__ == "__main__":
    custom_logger_example()
```
---

### 3.10. Practical Extraction Scenarios
These examples use `AsyncWebCrawler` and might require actual internet access and potentially API keys for the LLMs. They will be mocked for consistency in testing, but the setup shows real-world usage.

#### 3.10.1. Example: Extracting product names, prices, and descriptions from an e-commerce page.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import List, Optional
from unittest.mock import patch, MagicMock
import json
import os

class ProductInfo(BaseModel):
    name: str = Field(..., description="The name of the product")
    price: Optional[float] = Field(None, description="The price of the product, as a float")
    description_snippet: Optional[str] = Field(None, description="A short snippet of the product description")

class ProductPageExtract(BaseModel):
    products: List[ProductInfo] = Field(description="List of products found on the page")

# Mock the LLM call
mock_ecommerce_response = MagicMock()
mock_ecommerce_response.choices = [MagicMock()]
mock_ecommerce_response.choices[0].message.content = json.dumps({
    "products": [
        {"name": "Super Widget X1000", "price": 99.99, "description_snippet": "The best widget ever."},
        {"name": "Basic Widget B50", "price": 19.99, "description_snippet": "A simple, reliable widget."}
    ]
})
mock_ecommerce_response.usage = MagicMock(completion_tokens=50, prompt_tokens=300, total_tokens=350)
mock_ecommerce_response.usage.completion_tokens_details = {}; mock_ecommerce_response.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_ecommerce_response)
async def extract_ecommerce_products(mock_perform_completion):
    # This URL is a placeholder; a real e-commerce page would be used.
    # For CI/testing, we use a simple example.com which won't have products.
    # The key is to show the setup.
    ecommerce_url = "http://example.com" 
    
    try:
        llm_conf = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY", "mock_key_ecommerce"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set. Mock will be used.")
        
        extraction_strat = LLMExtractionStrategy(
            llm_config=llm_conf,
            schema=ProductPageExtract.model_json_schema(),
            extraction_type="schema",
            instruction="Extract all product names, their prices, and a short description snippet from the page content."
        )
    except Exception as e:
        print(f"LLM setup failed for e-commerce example: {e}. Skipping.")
        return

    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strat,
        # word_count_threshold=5 # Lower for example.com if testing live
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=ecommerce_url, config=run_config)

    print(f"--- Extraction from E-commerce like page ({ecommerce_url}) ---")
    if result.success and result.extracted_content:
        extracted_data = json.loads(result.extracted_content)
        print(json.dumps(extracted_data, indent=2))
        
        # Validate with Pydantic
        page_data = ProductPageExtract(**extracted_data)
        for product in page_data.products:
            print(f"Product: {product.name}, Price: {product.price}")
    elif not result.success:
        print(f"Crawl failed: {result.error_message}")
    else:
        print("No structured data extracted or extraction failed.")
    
    assert mock_perform_completion.called

if __name__ == "__main__":
    asyncio.run(extract_ecommerce_products())
```

#### 3.10.2. Example: Extracting article headlines, authors, and publication dates from a news site.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import Optional
from unittest.mock import patch, MagicMock
import json
import os

class NewsArticle(BaseModel):
    headline: str = Field(..., description="The main headline of the news article")
    author: Optional[str] = Field(None, description="The author(s) of the article")
    publication_date: Optional[str] = Field(None, description="The date the article was published (e.g., YYYY-MM-DD)")

# Mock the LLM call
mock_news_response = MagicMock()
mock_news_response.choices = [MagicMock()]
mock_news_response.choices[0].message.content = json.dumps({
    "headline": "AI Breakthrough Announced", 
    "author": "Reporter Bot", 
    "publication_date": "2024-05-24"
})
mock_news_response.usage = MagicMock(completion_tokens=30, prompt_tokens=250, total_tokens=280)
mock_news_response.usage.completion_tokens_details = {}; mock_news_response.usage.prompt_tokens_details = {}

@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_news_response)
async def extract_news_article_details(mock_perform_completion):
    # Using Wikipedia for a stable, public news-like article structure
    news_url = "https://en.wikipedia.org/wiki/Artificial_intelligence" 
    
    try:
        llm_conf = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY", "mock_key_news"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set. Mock will be used.")

        extraction_strat = LLMExtractionStrategy(
            llm_config=llm_conf,
            schema=NewsArticle.model_json_schema(),
            extraction_type="schema",
            instruction="From the provided news article content, extract the main headline, the author(s), and the publication date."
        )
    except Exception as e:
        print(f"LLM setup failed for news example: {e}. Skipping.")
        return


    run_config = CrawlerRunConfig(extraction_strategy=extraction_strat)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=news_url, config=run_config)

    print(f"--- Extraction from News Article ({news_url}) ---")
    if result.success and result.extracted_content:
        extracted_data = json.loads(result.extracted_content)
        print(json.dumps(extracted_data, indent=2))
        article_data = NewsArticle(**extracted_data)
        print(f"Headline: {article_data.headline}")
    elif not result.success:
        print(f"Crawl failed: {result.error_message}")
    else:
        print("No structured data extracted or extraction failed.")
    
    assert mock_perform_completion.called

if __name__ == "__main__":
    asyncio.run(extract_news_article_details())
```

#### 3.10.3. Example: Extracting frequently asked questions (FAQs) and their answers from a support page.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import List
from unittest.mock import patch, MagicMock
import json
import os

class FAQItem(BaseModel):
    question: str
    answer: str

class FAQPage(BaseModel):
    faqs: List[FAQItem]

# Mock the LLM call
mock_faq_response = MagicMock()
mock_faq_response.choices = [MagicMock()]
mock_faq_response.choices[0].message.content = json.dumps({
    "faqs": [
        {"question": "What is Crawl4ai?", "answer": "An awesome web crawler."},
        {"question": "How to install?", "answer": "pip install crawl4ai"}
    ]
})
mock_faq_response.usage = MagicMock(completion_tokens=60, prompt_tokens=300, total_tokens=360)
mock_faq_response.usage.completion_tokens_details = {}; mock_faq_response.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_faq_response)
async def extract_faqs(mock_perform_completion):
    # Placeholder URL - a real FAQ page would be used
    faq_url = "http://example.com/faq" 

    try:
        llm_conf = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY", "mock_key_faq"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set. Mock will be used.")
        
        extraction_strat = LLMExtractionStrategy(
            llm_config=llm_conf,
            schema=FAQPage.model_json_schema(),
            extraction_type="schema",
            instruction="Extract all question and answer pairs from the FAQ section of this page."
        )
    except Exception as e:
        print(f"LLM setup failed for FAQ example: {e}. Skipping.")
        return

    run_config = CrawlerRunConfig(extraction_strategy=extraction_strat)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=faq_url, config=run_config)

    print(f"--- Extraction from FAQ Page ({faq_url}) ---")
    if result.success and result.extracted_content:
        extracted_data = json.loads(result.extracted_content)
        print(json.dumps(extracted_data, indent=2))
        faq_page_data = FAQPage(**extracted_data)
        for faq_item in faq_page_data.faqs:
            print(f"Q: {faq_item.question}\nA: {faq_item.answer}\n")
    elif not result.success:
        print(f"Crawl failed: {result.error_message}")
    else:
        print("No structured data extracted or extraction failed.")

    assert mock_perform_completion.called

if __name__ == "__main__":
    asyncio.run(extract_faqs())
```

#### 3.10.4. Example: Extracting contact information (email, phone, address) from a company's "Contact Us" page.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import Optional
from unittest.mock import patch, MagicMock
import json
import os

class ContactInfo(BaseModel):
    email: Optional[str] = Field(None, description="Company contact email address")
    phone: Optional[str] = Field(None, description="Company contact phone number")
    address: Optional[str] = Field(None, description="Company physical address")

# Mock the LLM call
mock_contact_response = MagicMock()
mock_contact_response.choices = [MagicMock()]
mock_contact_response.choices[0].message.content = json.dumps({
    "email": "support@example.com", 
    "phone": "1-800-555-1234", 
    "address": "123 Main St, Anytown, USA"
})
mock_contact_response.usage = MagicMock(completion_tokens=40, prompt_tokens=200, total_tokens=240)
mock_contact_response.usage.completion_tokens_details = {}; mock_contact_response.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_contact_response)
async def extract_contact_info(mock_perform_completion):
    contact_url = "http://example.com/contact" 

    try:
        llm_conf = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY", "mock_key_contact"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set. Mock will be used.")
        
        extraction_strat = LLMExtractionStrategy(
            llm_config=llm_conf,
            schema=ContactInfo.model_json_schema(),
            extraction_type="schema",
            instruction="Extract the primary email, phone number, and physical address from this contact page."
        )
    except Exception as e:
        print(f"LLM setup failed for contact info example: {e}. Skipping.")
        return

    run_config = CrawlerRunConfig(extraction_strategy=extraction_strat)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=contact_url, config=run_config)

    print(f"--- Extraction from Contact Page ({contact_url}) ---")
    if result.success and result.extracted_content:
        extracted_data = json.loads(result.extracted_content)
        print(json.dumps(extracted_data, indent=2))
        contact_data = ContactInfo(**extracted_data)
        print(f"Email: {contact_data.email}, Phone: {contact_data.phone}")
    elif not result.success:
        print(f"Crawl failed: {result.error_message}")
    else:
        print("No structured data extracted or extraction failed.")
    
    assert mock_perform_completion.called

if __name__ == "__main__":
    asyncio.run(extract_contact_info())
```

#### 3.10.5. Example: Extracting key entities (people, organizations, locations) from a block of text using `extraction_type="block"` and a specific instruction.
This uses "block" extraction but with an instruction to guide the LLM to tag specific entities.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from unittest.mock import patch, MagicMock
import json
import os

# Mock LLM response - for block extraction with entity tagging
mock_entity_response = MagicMock()
mock_entity_response.choices = [MagicMock()]
mock_entity_response.choices[0].message.content = """
<blocks>
  <block>
    <content>Apple Inc. is headquartered in Cupertino.</content>
    <tags><tag>sentence</tag><tag>ORG:Apple Inc.</tag><tag>LOC:Cupertino</tag></tags>
  </block>
  <block>
    <content>Tim Cook is the CEO.</content>
    <tags><tag>sentence</tag><tag>PER:Tim Cook</tag></tags>
  </block>
</blocks>
"""
mock_entity_response.usage = MagicMock(completion_tokens=50, prompt_tokens=150, total_tokens=200)
mock_entity_response.usage.completion_tokens_details = {}; mock_entity_response.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_entity_response)
async def extract_entities_with_block(mock_perform_completion):
    entity_url = "http://example.com/about-us" # Placeholder
    
    try:
        llm_conf = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY", "mock_key_entities"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set. Mock will be used.")
        
        extraction_strat = LLMExtractionStrategy(
            llm_config=llm_conf,
            extraction_type="block",
            instruction="Extract each sentence as a block. For each block, identify and add tags for People (PER:Name), Organizations (ORG:Name), and Locations (LOC:Name) found within that sentence."
        )
    except Exception as e:
        print(f"LLM setup failed for entity extraction example: {e}. Skipping.")
        return

    run_config = CrawlerRunConfig(extraction_strategy=extraction_strat)

    # For this demo, we'll use direct content instead of crawling a URL
    sample_text_for_entities = "Apple Inc. is headquartered in Cupertino. Tim Cook is the CEO."

    # Normally you'd use crawler.arun(url=..., config=...).
    # Here, we call the strategy directly for simplicity with local text.
    extracted_blocks = extraction_strat.extract(url=entity_url, html_content=sample_text_for_entities)


    print(f"--- Entity Extraction using extraction_type='block' ---")
    if extracted_blocks:
        print(json.dumps(extracted_blocks, indent=2))
        for block in extracted_blocks:
            print(f"Content: {block['content']}")
            print(f"  Tags: {block['tags']}")
    else:
        print("No blocks extracted or extraction failed.")
    
    assert mock_perform_completion.called

if __name__ == "__main__":
    asyncio.run(extract_entities_with_block())
```
---

## 4. Integration with `AsyncWebCrawler`

#### 4.1. Example: Basic `AsyncWebCrawler` run with `LLMExtractionStrategy` configured in `CrawlerRunConfig`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json
import os

class PageSummary(BaseModel):
    summary: str
    keywords: List[str]

mock_llm_crawler_run = MagicMock()
mock_llm_crawler_run.choices = [MagicMock()]
mock_llm_crawler_run.choices[0].message.content = json.dumps({
    "summary": "Example.com is a domain for use in illustrative examples.",
    "keywords": ["example", "domain", "documentation"]
})
mock_llm_crawler_run.usage = MagicMock(completion_tokens=30, prompt_tokens=100, total_tokens=130)
mock_llm_crawler_run.usage.completion_tokens_details = {}; mock_llm_crawler_run.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_crawler_run)
async def crawler_with_llm_extraction(mock_perform_completion):
    try:
        llm_conf = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY", "mock_key_crawler"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set. Mock will be used.")

        extraction_strat = LLMExtractionStrategy(
            llm_config=llm_conf,
            schema=PageSummary.model_json_schema(),
            extraction_type="schema",
            instruction="Provide a one-sentence summary of the page and list up to 3 main keywords."
        )
    except Exception as e:
        print(f"LLM setup failed for crawler integration example: {e}. Skipping.")
        return

    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strat,
        word_count_threshold=5 # Ensure example.com content is processed
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="http://example.com", config=run_config)

    print(f"--- Crawler run with LLMExtractionStrategy ---")
    if result.success and result.extracted_content:
        extracted_data = json.loads(result.extracted_content)
        print("Extracted Data:")
        print(json.dumps(extracted_data, indent=2))
        
        summary_instance = PageSummary(**extracted_data)
        print(f"\nValidated Summary: {summary_instance.summary}")
        print(f"Keywords: {summary_instance.keywords}")
    elif not result.success:
        print(f"Crawl failed: {result.error_message}")
    else:
        print("No structured data extracted.")
    
    assert mock_perform_completion.called

if __name__ == "__main__":
    asyncio.run(crawler_with_llm_extraction())
```

#### 4.2. Example: `AsyncWebCrawler` processing multiple URLs, each with the same `LLMExtractionStrategy`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json
import os

class SiteInfo(BaseModel):
    site_name: str
    main_purpose: str

# Mock LLM to return different info based on URL (simplified by just returning same mock structure)
mock_llm_multi_url = MagicMock()
mock_llm_multi_url.choices = [MagicMock()]
# We'll have the mock return slightly different content for each call
responses_for_multi_url = [
    json.dumps({"site_name": "Example Domain", "main_purpose": "Illustrative examples"}),
    json.dumps({"site_name": "IANA", "main_purpose": "Managing global IP addressing"})
]
call_count_multi = 0
def side_effect_multi_url(*args, **kwargs):
    global call_count_multi
    mock_llm_multi_url.choices[0].message.content = responses_for_multi_url[call_count_multi % len(responses_for_multi_url)]
    call_count_multi +=1
    return mock_llm_multi_url

mock_llm_multi_url.usage = MagicMock(completion_tokens=20, prompt_tokens=80, total_tokens=100) # Generic usage
mock_llm_multi_url.usage.completion_tokens_details = {}; mock_llm_multi_url.usage.prompt_tokens_details = {}

@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', side_effect=side_effect_multi_url)
async def crawler_many_with_llm_extraction(mock_perform_completion):
    urls_to_crawl = [
        "http://example.com",
        "https://www.iana.org/domains/reserved" # Another simple, stable page
    ]
    
    try:
        llm_conf = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY", "mock_key_many"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set. Mock will be used.")

        extraction_strat = LLMExtractionStrategy(
            llm_config=llm_conf,
            schema=SiteInfo.model_json_schema(),
            extraction_type="schema",
            instruction="Identify the site name and its main purpose."
        )
    except Exception as e:
        print(f"LLM setup failed for arun_many example: {e}. Skipping.")
        return

    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strat,
        word_count_threshold=10 # Adjust as needed for the test URLs
    )

    async with AsyncWebCrawler() as crawler:
        # arun_many returns an async generator if stream=True, or list if stream=False (default)
        results = await crawler.arun_many(urls=urls_to_crawl, config=run_config) 

    print(f"--- Crawler arun_many with LLMExtractionStrategy ---")
    for result in results:
        if result.success and result.extracted_content:
            extracted_data = json.loads(result.extracted_content)
            print(f"\nURL: {result.url}")
            print("Extracted Data:")
            print(json.dumps(extracted_data, indent=2))
        elif not result.success:
            print(f"\nCrawl for {result.url} failed: {result.error_message}")
        else:
            print(f"\nNo structured data extracted for {result.url}.")
    
    assert mock_perform_completion.call_count == len(urls_to_crawl)

if __name__ == "__main__":
    asyncio.run(crawler_many_with_llm_extraction())
```

#### 4.3. Example: `AsyncWebCrawler` where `CrawlerRunConfig` is dynamically changed per URL to use different extraction schemas or instructions.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from unittest.mock import patch, MagicMock
import json
import os

class TechArticleInfo(BaseModel):
    title: str
    primary_topic: str

class CompanyInfo(BaseModel):
    company_name: str
    services_offered: List[str]

# Mocks for different schemas
mock_tech_article_response = MagicMock()
mock_tech_article_response.choices = [MagicMock(message=MagicMock(content=json.dumps({"title": "Intro to Crawling", "primary_topic": "Web Scraping"})))]
mock_tech_article_response.usage = MagicMock(completion_tokens=15, prompt_tokens=70, total_tokens=85)
mock_tech_article_response.usage.completion_tokens_details = {}; mock_tech_article_response.usage.prompt_tokens_details = {}


mock_company_response = MagicMock()
mock_company_response.choices = [MagicMock(message=MagicMock(content=json.dumps({"company_name": "Example Corp", "services_offered": ["Web Hosting", "Domain Registration"]})))]
mock_company_response.usage = MagicMock(completion_tokens=20, prompt_tokens=90, total_tokens=110)
mock_company_response.usage.completion_tokens_details = {}; mock_company_response.usage.prompt_tokens_details = {}


# Side effect function to return different mocks based on schema/instruction
def dynamic_llm_side_effect(*args, **kwargs):
    # Heuristic: check prompt content for clues about which schema is expected
    prompt_content = args[1] # The prompt string is the second argument to perform_completion_with_backoff
    if "TechArticleInfo" in prompt_content or "primary_topic" in prompt_content:
        return mock_tech_article_response
    elif "CompanyInfo" in prompt_content or "services_offered" in prompt_content:
        return mock_company_response
    return MagicMock() # Default generic mock if no match

@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', side_effect=dynamic_llm_side_effect)
async def crawler_dynamic_configs(mock_perform_completion):
    urls_and_configs: List[Dict[str, Any]] = [
        {
            "url": "https://en.wikipedia.org/wiki/Web_scraping", # Tech article like
            "schema_model": TechArticleInfo,
            "instruction": "Extract title and primary topic of this technical article."
        },
        {
            "url": "http://example.com", # Generic company like
            "schema_model": CompanyInfo,
            "instruction": "Identify the company name and list its main services."
        }
    ]
    
    try:
        llm_conf = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY", "mock_key_dynamic"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set. Mock will be used.")
    except Exception as e:
        print(f"LLM setup failed for dynamic config example: {e}. Skipping.")
        return

    all_results_data = []

    async with AsyncWebCrawler() as crawler:
        for item in urls_and_configs:
            current_url = item["url"]
            CurrentSchemaModel = item["schema_model"]
            current_instruction = item["instruction"]

            extraction_strat = LLMExtractionStrategy(
                llm_config=llm_conf,
                schema=CurrentSchemaModel.model_json_schema(),
                extraction_type="schema",
                instruction=current_instruction
            )
            run_config = CrawlerRunConfig(
                extraction_strategy=extraction_strat, 
                word_count_threshold=10
            )
            
            print(f"\nCrawling {current_url} with schema {CurrentSchemaModel.__name__}...")
            result = await crawler.arun(url=current_url, config=run_config)
            
            if result.success and result.extracted_content:
                extracted_data = json.loads(result.extracted_content)
                print(f"Extracted for {current_url}:")
                print(json.dumps(extracted_data, indent=2))
                all_results_data.append(extracted_data)
            else:
                print(f"Failed or no extraction for {current_url}: {result.error_message}")
                all_results_data.append({"error": result.error_message, "url": current_url})
                
    assert mock_perform_completion.call_count == len(urls_and_configs)
    assert all_results_data[0].get("primary_topic") == "Web Scraping"
    assert "Web Hosting" in all_results_data[1].get("services_offered", [])


if __name__ == "__main__":
    asyncio.run(crawler_dynamic_configs())
```
---

## 5. Combining Extraction with Other Crawl4ai Features

### 5.1. **Extraction from PDF Content:**

#### 5.1.1. Example: Using `PDFCrawerStrategy` and `PDFContentScrapingStrategy` to get HTML/text from a PDF, then using `LLMExtractionStrategy` on that content.
This example requires `crawl4ai[pdf]` to be installed. We'll use a public PDF URL.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.content_scraping_strategy import PDFContentScrapingStrategy # For PDF processing
from crawl4ai.async_crawler_strategy import PDFCrawlerStrategy # To handle PDF URLs
from pydantic import BaseModel, Field
from typing import List, Optional
from unittest.mock import patch, MagicMock
import json
import os

# Note: This example requires PyPDF2. Install with: pip install crawl4ai[pdf]

class PDFSummary(BaseModel):
    title: Optional[str] = Field(None, description="The title of the PDF document, if discernible.")
    first_paragraph_summary: str = Field(..., description="A brief summary of the first main paragraph of text.")

# Mock for LLM
mock_llm_pdf_extract = MagicMock()
mock_llm_pdf_extract.choices = [MagicMock(message=MagicMock(content=json.dumps({
    "title": "Sample PDF Document",
    "first_paragraph_summary": "This PDF discusses important topics related to data."
})))]
mock_llm_pdf_extract.usage = MagicMock(completion_tokens=20, prompt_tokens=150, total_tokens=170)
mock_llm_pdf_extract.usage.completion_tokens_details = {}; mock_llm_pdf_extract.usage.prompt_tokens_details = {}

@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_pdf_extract)
async def extract_from_pdf_content(mock_perform_completion):
    # A public, simple PDF for testing. (e.g., a small, text-based PDF)
    # Using a known, stable PDF URL: an RFC document (plain text heavy)
    pdf_url = "https://www.rfc-editor.org/rfc/rfc2616.txt.pdf" # This is a PDF version of an RFC text file
    # pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" # A very simple dummy PDF

    try:
        llm_conf = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY", "mock_key_pdf"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set for PDF example. Mock will be used.")

        extraction_strat = LLMExtractionStrategy(
            llm_config=llm_conf,
            schema=PDFSummary.model_json_schema(),
            extraction_type="schema",
            instruction="From the provided PDF text, extract the document title if available, and summarize the first main paragraph.",
            input_format="text" # PDFContentScrapingStrategy will provide text
        )
    except Exception as e:
        print(f"LLM setup failed for PDF extraction example: {e}. Skipping.")
        return

    # BrowserConfig might be needed if the PDF is rendered in-browser and not a direct link
    browser_cfg = BrowserConfig() 

    # CrawlerRunConfig for PDF processing and then LLM extraction
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strat,
        # The PDFContentScrapingStrategy will be used by PDFCrawlerStrategy
        # to convert PDF to text/HTML for the LLMExtractionStrategy.
        # LLMExtractionStrategy expects text if input_format="text".
        scraping_strategy=PDFContentScrapingStrategy(output_format="text") # Ensure text output for LLM
    )
    
    # Use PDFCrawlerStrategy to handle the PDF URL
    # Note: For PDFCrawlerStrategy, the 'browser_config' of AsyncWebCrawler is not directly used for PDF fetching.
    # PDFCrawlerStrategy uses requests library directly.
    async with AsyncWebCrawler(crawler_strategy=PDFCrawlerStrategy(), browser_config=browser_cfg) as crawler:
        print(f"Crawling PDF: {pdf_url}")
        result = await crawler.arun(url=pdf_url, config=run_config)

    print(f"--- Extraction from PDF Content ({pdf_url}) ---")
    if result.success:
        if result.extracted_content:
            extracted_data = json.loads(result.extracted_content)
            print("Extracted Data from PDF:")
            print(json.dumps(extracted_data, indent=2))
            pdf_summary_instance = PDFSummary(**extracted_data)
            print(f"\nValidated Title: {pdf_summary_instance.title}")
            print(f"Summary: {pdf_summary_instance.first_paragraph_summary}")
        else:
            print("PDF content processed, but no structured data extracted by LLM.")
            print(f"Raw Markdown/Text from PDF (first 300 chars): {result.markdown.raw_markdown[:300] if result.markdown else 'N/A'}...")
    else:
        print(f"Crawl/Processing of PDF failed: {result.error_message}")
    
    if extraction_strat.llm_config.api_token != "mock_key_pdf": # Only assert if not fully mocked
         assert mock_perform_completion.called

if __name__ == "__main__":
    # This example needs `pip install crawl4ai[pdf]`
    try:
        import PyPDF2 # Check if PyPDF2 is installed
        asyncio.run(extract_from_pdf_content())
    except ImportError:
        print("PyPDF2 not found. Please install it with `pip install crawl4ai[pdf]` to run this example.")
    except Exception as e:
        print(f"An error occurred: {e}")
```

### 5.2. **Extraction After Content Filtering (Illustrative):**

#### 5.2.1. Example: Manually running a `ContentFilterStrategy` on HTML, then passing the filtered HTML to `LLMExtractionStrategy.extract(input_format="html")`.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter # Example filter
from crawl4ai.utils import LLMConfig
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock
import json

# Mock for LLM
mock_llm_filtered_html = MagicMock()
mock_llm_filtered_html.choices = [MagicMock(message=MagicMock(content=json.dumps({"main_idea": "The core idea is about X."})))]
mock_llm_filtered_html.usage = MagicMock(completion_tokens=10, prompt_tokens=40, total_tokens=50)
mock_llm_filtered_html.usage.completion_tokens_details = {}; mock_llm_filtered_html.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_filtered_html)
def extract_after_manual_filter(mock_perform_completion):
    sample_raw_html = """
    <html><head><title>Test Page</title></head><body>
        <header>Site Navigation Links...</header>
        <main id='content'>
            <h1>Article Title</h1>
            <p>This is the first important paragraph.</p>
            <div class='ad-banner'>Advertisement here</div>
            <p>This is the second important paragraph after an ad.</p>
        </main>
        <footer>Copyright 2024. All rights reserved.</footer>
    </body></html>
    """
    
    # Step 1: Manually apply a content filter
    # PruningContentFilter modifies the soup in-place
    soup = BeautifulSoup(sample_raw_html, "lxml")
    
    # Example of direct filter usage (conceptual, PruningContentFilter works on soup)
    # PruningContentFilter might typically be used within MarkdownGenerator
    # For this example, let's simulate its effect by selecting main content
    # and removing a known ad-like element.
    
    # Simulate pruning effect:
    header = soup.find("header")
    if header: header.decompose()
    footer = soup.find("footer")
    if footer: footer.decompose()
    ad_banner = soup.find("div", class_="ad-banner")
    if ad_banner: ad_banner.decompose()
        
    filtered_html_content = str(soup.find("main")) # Get HTML of the main content after pruning
    
    print(f"--- Filtered HTML (simulated) ---\n{filtered_html_content}\n---------------------------------")

    # Step 2: Pass filtered HTML to LLMExtractionStrategy
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"),
            input_format="html", # The filtered content is still HTML
            extraction_type="schema_from_instruction",
            instruction="What is the main idea of this content?"
        )
    except:
        print("Ollama not available, skipping manual filter extraction test.")
        return

    extracted_json = strategy.extract(url="http://dummy.com/filtered", html_content=filtered_html_content)
    
    print("\nExtraction from Manually Filtered HTML (mocked LLM):")
    if extracted_json:
        print(json.dumps(json.loads(extracted_json), indent=2))
    
    assert mock_perform_completion.called

if __name__ == "__main__":
    extract_after_manual_filter()
```
---

## 6. Advanced Techniques and Edge Cases

#### 6.1. Example: Handling cases where the LLM fails to extract data or returns an unexpected format (and how `force_json_response` might help).

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json
import os

class SimpleSchema(BaseModel):
    name: str

# Mock 1: LLM returns malformed JSON (e.g., with extra text, missing comma)
mock_malformed_json_response = MagicMock()
mock_malformed_json_response.choices = [MagicMock(message=MagicMock(content='Sure, here is the JSON: {"name": "Test" // oops, a comment'))]
mock_malformed_json_response.usage = MagicMock(completion_tokens=10, prompt_tokens=50, total_tokens=60)
mock_malformed_json_response.usage.completion_tokens_details = {}; mock_malformed_json_response.usage.prompt_tokens_details = {}


# Mock 2: LLM returns clean JSON (simulating successful force_json_response)
mock_clean_json_response = MagicMock()
mock_clean_json_response.choices = [MagicMock(message=MagicMock(content=json.dumps({"name": "Test"})))]
mock_clean_json_response.usage = MagicMock(completion_tokens=8, prompt_tokens=50, total_tokens=58)
mock_clean_json_response.usage.completion_tokens_details = {}; mock_clean_json_response.usage.prompt_tokens_details = {}


@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff')
def handle_llm_failures(mock_perform_completion):
    sample_content = "The name is Test."
    schema_def = SimpleSchema.model_json_schema()
    
    try:
        llm_conf = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY", "mock_key_failure"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set for failure handling example.")
    except:
        print("LLM provider setup failed. Skipping LLM failure handling test.")
        return

    # Scenario 1: LLM returns malformed JSON, force_json_response=False
    print("--- Scenario 1: Malformed JSON, force_json_response=False ---")
    mock_perform_completion.return_value = mock_malformed_json_response
    strategy_no_force = LLMExtractionStrategy(
        llm_config=llm_conf, schema=schema_def, extraction_type="schema", force_json_response=False
    )
    result_str_no_force = strategy_no_force.extract("url", sample_content)
    print(f"LLM raw output: {result_str_no_force}")
    try:
        # This should ideally fail or be handled by LiteLLM's built-in JSON parsing attempts
        parsed = json.loads(result_str_no_force) 
        SimpleSchema(**parsed) # Validate
        print(f"Parsed (unexpectedly successful for this mock): {parsed}")
    except Exception as e:
        print(f"Expected parsing/validation error: {e}")

    # Scenario 2: LLM returns malformed JSON, force_json_response=True
    # The mock for this scenario simulates that force_json_response helped the LLM return clean JSON
    print("\n--- Scenario 2: Malformed JSON (conceptually), force_json_response=True ---")
    mock_perform_completion.return_value = mock_clean_json_response 
    strategy_with_force = LLMExtractionStrategy(
        llm_config=llm_conf, schema=schema_def, extraction_type="schema", force_json_response=True
    )
    result_str_with_force = strategy_with_force.extract("url", sample_content)
    print(f"LLM raw output (should be clean JSON): {result_str_with_force}")
    try:
        parsed_forced = json.loads(result_str_with_force)
        SimpleSchema(**parsed_forced) # Validate
        print(f"Parsed successfully with force_json_response: {parsed_forced}")
    except Exception as e:
        print(f"Error parsing/validating even with force_json_response: {e}")

if __name__ == "__main__":
    handle_llm_failures()
```

#### 6.2. Example: Strategies for dealing with very long content that might exceed single LLM context windows even after chunking (e.g., iterative extraction or summarization prior to extraction).
This is a conceptual example. Real implementation would be more complex.
We'll show a simplified version where we first "summarize" chunks then extract from summaries.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from pydantic import BaseModel
from unittest.mock import patch, MagicMock
import json
import os

class DocumentExtract(BaseModel):
    overall_summary: str
    key_points: List[str]

# Mocks
# 1. For summarizing chunks
mock_summarize_chunk = MagicMock()
mock_summarize_chunk.choices = [MagicMock()]
mock_summarize_chunk.usage = MagicMock(completion_tokens=20, prompt_tokens=50, total_tokens=70)
mock_summarize_chunk.usage.completion_tokens_details = {}; mock_summarize_chunk.usage.prompt_tokens_details = {}


# 2. For final extraction from combined summaries
mock_final_extract = MagicMock()
mock_final_extract.choices = [MagicMock()]
mock_final_extract.choices[0].message.content = json.dumps({
    "overall_summary": "The document discusses AI advancements and their societal impact.",
    "key_points": ["AI is evolving fast.", "Ethics are important.", "Future is exciting."]
})
mock_final_extract.usage = MagicMock(completion_tokens=40, prompt_tokens=100, total_tokens=140)
mock_final_extract.usage.completion_tokens_details = {}; mock_final_extract.usage.prompt_tokens_details = {}


def mock_llm_router(*args, **kwargs):
    # Simplistic router based on instruction
    instruction = kwargs.get('instruction', '')
    if "summarize this chunk" in instruction.lower():
        # The content of the mock is less important here than the call itself
        mock_summarize_chunk.choices[0].message.content = json.dumps({"summary_of_chunk": "Chunk summary text."})
        return mock_summarize_chunk
    elif "overall document summary" in instruction.lower():
        return mock_final_extract
    return MagicMock() # Default

@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', side_effect=mock_llm_router)
def iterative_extraction_for_long_content(mock_perform_completion):
    very_long_document_content = ("This is part of a very long document. " * 100) # Simulate long content
    
    try:
        llm_conf = LLMConfig(provider="openai/gpt-3.5-turbo", api_token=os.getenv("OPENAI_API_KEY", "mock_key_iterative"))
        if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set for iterative example.")
    except:
        print("LLM setup failed. Skipping iterative extraction test.")
        return

    # Step 1: Create strategy for summarizing chunks (block extraction for simplicity)
    summarizer_strategy = LLMExtractionStrategy(
        llm_config=llm_conf,
        extraction_type="block", # Could be schema { "summary": "..." }
        instruction="Summarize this chunk of text concisely.",
        chunk_token_threshold=60, # Smaller chunks for summarization
        word_token_rate=0.75,
        apply_chunking=True
    )

    print("--- Step 1: Summarizing chunks of the long document ---")
    # LLMExtractionStrategy.extract returns list of blocks if extraction_type="block"
    chunk_summaries_blocks = summarizer_strategy.extract("url", very_long_document_content) 
    
    # We'd expect chunk_summaries_blocks to be a list of dicts like [{'content': 'summary1', 'tags':[]}, ...]
    # For this mock, we'll just take the mocked 'content'
    chunk_summaries = [block.get("content", "") for block in chunk_summaries_blocks if isinstance(block, dict)]
    combined_summary_text = "\n".join(chunk_summaries)
    
    print(f"Summarized {len(chunk_summaries_blocks)} chunks into combined text of length {len(combined_summary_text)}.")
    print(f"Combined summary (first 100 chars): {combined_summary_text[:100]}...")

    # Step 2: Create strategy for final extraction from combined summaries
    final_extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_conf,
        schema=DocumentExtract.model_json_schema(),
        extraction_type="schema",
        instruction="From the provided combined summaries, create an overall document summary and list key points."
    )

    print("\n--- Step 2: Final extraction from combined summaries ---")
    final_extracted_json_str = final_extraction_strategy.extract("url_summary", combined_summary_text)

    if final_extracted_json_str:
        final_data = json.loads(final_extracted_json_str)
        print(json.dumps(final_data, indent=2))
        doc_extract_instance = DocumentExtract(**final_data)
        assert "AI is evolving fast" in doc_extract_instance.key_points
    else:
        print("Final extraction failed.")

if __name__ == "__main__":
    iterative_extraction_for_long_content()
```

#### 6.3. Example: Showing how to access `TokenUsage` statistics after an LLM extraction.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
from unittest.mock import patch, MagicMock
import json

# Mock LLM response with usage data
mock_llm_usage = MagicMock()
mock_llm_usage.choices = [MagicMock(message=MagicMock(content=json.dumps({"extracted": "data"})))]
mock_llm_usage.usage = MagicMock()
mock_llm_usage.usage.completion_tokens = 50
mock_llm_usage.usage.prompt_tokens = 150
mock_llm_usage.usage.total_tokens = 200
# Example of detailed token usage (if provider supports it)
mock_llm_usage.usage.completion_tokens_details = {"gpt-3.5-turbo": 50} 
mock_llm_usage.usage.prompt_tokens_details = {"gpt-3.5-turbo": 150}

@patch('crawl4ai.extraction_strategy.perform_completion_with_backoff', return_value=mock_llm_usage)
def show_token_usage(mock_perform_completion):
    try:
        strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(provider="ollama/llama3", api_token="ollama"), # Or any provider
            extraction_type="schema_from_instruction",
            instruction="Extract data."
        )
    except:
        print("Ollama not available, skipping token usage test.")
        return

    strategy.extract(url="http://dummy.com/usage_test", html_content="Some content to extract from.")
    
    print("--- Token Usage Statistics ---")
    
    # Total usage accumulated by the strategy instance across all its .extract() calls
    print(f"Total Accumulated Usage for this strategy instance:")
    print(f"  Completion Tokens: {strategy.total_usage.completion_tokens}")
    print(f"  Prompt Tokens: {strategy.total_usage.prompt_tokens}")
    print(f"  Total Tokens: {strategy.total_usage.total_tokens}")

    # Usage for the last .extract() call (or list of calls if chunking happened)
    if strategy.usages:
        print(f"\nUsage for the last .extract() operation (may include multiple LLM calls if chunked):")
        for i, usage_info in enumerate(strategy.usages[-mock_perform_completion.call_count:]): # Show for calls made in this run
            print(f"  LLM Call {i+1}:")
            print(f"    Completion Tokens: {usage_info.completion_tokens}")
            print(f"    Prompt Tokens: {usage_info.prompt_tokens}")
            print(f"    Total Tokens: {usage_info.total_tokens}")
            if usage_info.completion_tokens_details:
                 print(f"    Completion Details: {usage_info.completion_tokens_details}")
            if usage_info.prompt_tokens_details:
                 print(f"    Prompt Details: {usage_info.prompt_tokens_details}")
    else:
        print("No usage data recorded for the last operation (might be an issue or first run).")
        
    assert strategy.total_usage.total_tokens == 200 # Based on mock

if __name__ == "__main__":
    show_token_usage()
```
---

## 7. Deprecated Parameter Usage (for backward compatibility reference, if necessary)

#### 7.1. Example: Initializing `LLMExtractionStrategy` using deprecated `provider`, `api_token`, `base_url` and showing equivalence with `llm_config`. (Mark as deprecated in example comments).
This example shows the old way of passing LLM configuration directly to `LLMExtractionStrategy` and the new, recommended way using `LLMConfig`.

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.utils import LLMConfig
import os
import warnings

# Suppress deprecation warnings for this specific example
warnings.filterwarnings("ignore", category=DeprecationWarning, module="crawl4ai.extraction_strategy")


print("--- Demonstrating LLM Configuration: Deprecated vs. LLMConfig ---")

# Parameters for the example
provider_name = "openai/gpt-3.5-turbo"
api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_PLACEHOLDER")
# base_api_url = "https://api.example.com/v1" # Example custom base URL

# --- Deprecated Way (for illustration) ---
# Note: This will raise DeprecationWarnings if not suppressed.
# It's included here to show users how to migrate.
print("\nAttempting initialization with DEPRECATED direct parameters:")
try:
    strategy_deprecated = LLMExtractionStrategy(
        provider=provider_name,
        api_token=api_key,
        # base_url=base_api_url, # If you had a custom base_url
        instruction="This is a test." # Need some instruction for it to init provider
    )
    print(f"  Deprecated way: Provider='{strategy_deprecated.llm_config.provider}', Token (first 5)='{strategy_deprecated.llm_config.api_token[:5] if strategy_deprecated.llm_config.api_token else None}', BaseURL='{strategy_deprecated.llm_config.base_url}'")
    assert strategy_deprecated.llm_config.provider == provider_name
except Exception as e:
    print(f"  Error with deprecated init (as expected if params fully removed or strict checks): {e}")


# --- New Recommended Way (using LLMConfig) ---
print("\nAttempting initialization with NEW LLMConfig object:")
llm_configuration = LLMConfig(
    provider=provider_name,
    api_token=api_key,
    # base_url=base_api_url # If you have a custom base_url
)
strategy_new = LLMExtractionStrategy(
    llm_config=llm_configuration,
    instruction="This is a test." # Need some instruction
)
print(f"  New way (LLMConfig): Provider='{strategy_new.llm_config.provider}', Token (first 5)='{strategy_new.llm_config.api_token[:5] if strategy_new.llm_config.api_token else None}', BaseURL='{strategy_new.llm_config.base_url}'")
assert strategy_new.llm_config.provider == provider_name

print("\nComparison:")
if 'strategy_deprecated' in locals() and strategy_deprecated.llm_config.provider == strategy_new.llm_config.provider:
    print("Both methods (deprecated and new) resulted in the same LLM provider configuration (provider name matches).")
else:
    print("There was a difference or the deprecated method failed as expected.")

# Restore default warning behavior if needed for other tests
warnings.resetwarnings()
```
---

**Note:** Many examples involving `LLMExtractionStrategy` use mocked LLM calls for simplicity and to avoid API key dependencies during automated testing or casual runs. When adapting these examples for real use, ensure you have a valid `LLMConfig` with appropriate provider details and API tokens, and remove or adapt the `@patch` decorators. For local testing, consider using Ollama with a model like `ollama/llama3`.

```

---

