# Crawl4AI Custom LLM Context
Generated on: 2025-06-15T06:15:10.083Z
Total files: 3

---

## Markdown Generation - Memory
Source: crawl4ai_markdown_memory_content.llm.md

Okay, I have processed the instructions and the provided information. I will now generate the detailed "Foundational Memory" document for the `markdown` component of `crawl4ai`, adhering strictly to the outline you've provided and focusing on factual API details.

```markdown
# Detailed Outline for crawl4ai - markdown Component

**Target Document Type:** memory
**Target Output Filename Suggestion:** `llm_memory_markdown.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2025-05-24
---

## 1. Introduction to Markdown Generation in Crawl4ai

*   1.1. Purpose: This section outlines the `markdown` component of the `crawl4ai` library. Its primary role is to convert HTML content, obtained during web crawling, into various Markdown formats. These formats are designed to be suitable for consumption by Large Language Models (LLMs), as well as for other applications requiring structured text from web pages.
*   1.2. Key Abstractions:
    *   `MarkdownGenerationStrategy`: An abstract base class that defines the interface for different markdown generation algorithms and approaches. This allows for customizable Markdown conversion processes.
    *   `DefaultMarkdownGenerator`: The standard, out-of-the-box implementation of `MarkdownGenerationStrategy`. It handles the conversion of HTML to Markdown, including features like link-to-citation conversion and integration with content filtering.
    *   `MarkdownGenerationResult`: A Pydantic data model that encapsulates the various outputs of the markdown generation process, such as raw markdown, markdown with citations, and markdown derived from filtered content.
    *   `CrawlerRunConfig.markdown_generator`: An attribute within the `CrawlerRunConfig` class that allows users to specify which instance of a `MarkdownGenerationStrategy` should be used for a particular crawl operation.
*   1.3. Relationship with Content Filtering: The markdown generation process can be integrated with `RelevantContentFilter` strategies. When a content filter is applied, it first refines the input HTML, and then this filtered HTML is used to produce a `fit_markdown` output, providing a more focused version of the content.

## 2. Core Interface: `MarkdownGenerationStrategy`

*   2.1. Purpose: The `MarkdownGenerationStrategy` class is an abstract base class (ABC) that defines the contract for all markdown generation strategies within `crawl4ai`. It ensures that any custom markdown generator will adhere to a common interface, making them pluggable into the crawling process.
*   2.2. Source File: `crawl4ai/markdown_generation_strategy.py`
*   2.3. Initialization (`__init__`)
    *   2.3.1. Signature:
        ```python
        class MarkdownGenerationStrategy(ABC):
            def __init__(
                self,
                content_filter: Optional[RelevantContentFilter] = None,
                options: Optional[Dict[str, Any]] = None,
                verbose: bool = False,
                content_source: str = "cleaned_html",
            ):
                # ...
        ```
    *   2.3.2. Parameters:
        *   `content_filter (Optional[RelevantContentFilter]`, default: `None`)`: An optional `RelevantContentFilter` instance. If provided, this filter will be used to process the HTML before generating the `fit_markdown` and `fit_html` outputs in the `MarkdownGenerationResult`.
        *   `options (Optional[Dict[str, Any]]`, default: `None`)`: A dictionary for strategy-specific custom options. This allows subclasses to receive additional configuration parameters. Defaults to an empty dictionary if `None`.
        *   `verbose (bool`, default: `False`)`: If `True`, enables verbose logging for the markdown generation process.
        *   `content_source (str`, default: `"cleaned_html"`)`: A string indicating the source of HTML to use for Markdown generation. Common values might include `"raw_html"` (original HTML from the page), `"cleaned_html"` (HTML after initial cleaning by the scraping strategy), or `"fit_html"` (HTML after being processed by `content_filter`). The actual available sources depend on the `ScrapingResult` provided to the markdown generator.
*   2.4. Abstract Methods:
    *   2.4.1. `generate_markdown(self, input_html: str, base_url: str = "", html2text_options: Optional[Dict[str, Any]] = None, content_filter: Optional[RelevantContentFilter] = None, citations: bool = True, **kwargs) -> MarkdownGenerationResult`
        *   Purpose: This abstract method must be implemented by concrete subclasses. It is responsible for taking an HTML string and converting it into various Markdown representations, encapsulated within a `MarkdownGenerationResult` object.
        *   Parameters:
            *   `input_html (str)`: The HTML string content to be converted to Markdown.
            *   `base_url (str`, default: `""`)`: The base URL of the crawled page. This is crucial for resolving relative URLs, especially when converting links to citations.
            *   `html2text_options (Optional[Dict[str, Any]]`, default: `None`)`: A dictionary of options to be passed to the underlying HTML-to-text conversion engine (e.g., `CustomHTML2Text`).
            *   `content_filter (Optional[RelevantContentFilter]`, default: `None`)`: An optional `RelevantContentFilter` instance. If provided, this filter is used to generate `fit_markdown` and `fit_html`. This parameter overrides any filter set during the strategy's initialization for this specific call.
            *   `citations (bool`, default: `True`)`: A boolean flag indicating whether to convert Markdown links into a citation format (e.g., `[text]^[1]^`) with a corresponding reference list.
            *   `**kwargs`: Additional keyword arguments to allow for future extensions or strategy-specific parameters.
        *   Returns: (`MarkdownGenerationResult`) An object containing the results of the Markdown generation, including `raw_markdown`, `markdown_with_citations`, `references_markdown`, and potentially `fit_markdown` and `fit_html`.

## 3. Default Implementation: `DefaultMarkdownGenerator`

*   3.1. Purpose: `DefaultMarkdownGenerator` is the standard concrete implementation of `MarkdownGenerationStrategy`. It provides a robust mechanism for converting HTML to Markdown, featuring link-to-citation conversion and the ability to integrate with `RelevantContentFilter` strategies for focused content output.
*   3.2. Source File: `crawl4ai/markdown_generation_strategy.py`
*   3.3. Inheritance: Inherits from `MarkdownGenerationStrategy`.
*   3.4. Initialization (`__init__`)
    *   3.4.1. Signature:
        ```python
        class DefaultMarkdownGenerator(MarkdownGenerationStrategy):
            def __init__(
                self,
                content_filter: Optional[RelevantContentFilter] = None,
                options: Optional[Dict[str, Any]] = None,
                # content_source parameter from parent is available
                # verbose parameter from parent is available
            ):
                super().__init__(content_filter, options, content_source=kwargs.get("content_source", "cleaned_html"), verbose=kwargs.get("verbose", False))
        ```
        *(Note: The provided code snippet for `DefaultMarkdownGenerator.__init__` does not explicitly list `verbose` and `content_source`, but they are passed to `super().__init__` through `**kwargs` in the actual library code, so their effective signature matches the parent.)*
    *   3.4.2. Parameters:
        *   `content_filter (Optional[RelevantContentFilter]`, default: `None`)`: As defined in `MarkdownGenerationStrategy`.
        *   `options (Optional[Dict[str, Any]]`, default: `None`)`: As defined in `MarkdownGenerationStrategy`.
        *   `verbose (bool`, default: `False`)`: (Passed via `kwargs` to parent) As defined in `MarkdownGenerationStrategy`.
        *   `content_source (str`, default: `"cleaned_html"`)`: (Passed via `kwargs` to parent) As defined in `MarkdownGenerationStrategy`.
*   3.5. Key Class Attributes:
    *   3.5.1. `LINK_PATTERN (re.Pattern)`: A compiled regular expression pattern used to find Markdown links. The pattern is `r'!\[(.[^\]]*)\]\(([^)]*?)(?:\s*\"(.*)\")?\)'`.
*   3.6. Key Public Methods:
    *   3.6.1. `generate_markdown(self, input_html: str, base_url: str = "", html2text_options: Optional[Dict[str, Any]] = None, content_filter: Optional[RelevantContentFilter] = None, citations: bool = True, **kwargs) -> MarkdownGenerationResult`
        *   Purpose: Implements the conversion of HTML to Markdown. It uses `CustomHTML2Text` for the base conversion, handles link-to-citation transformation, and integrates with an optional `RelevantContentFilter` to produce `fit_markdown`.
        *   Parameters:
            *   `input_html (str)`: The HTML content to convert.
            *   `base_url (str`, default: `""`)`: Base URL for resolving relative links.
            *   `html2text_options (Optional[Dict[str, Any]]`, default: `None`)`: Options for the `CustomHTML2Text` converter. If not provided, it uses `self.options`.
            *   `content_filter (Optional[RelevantContentFilter]`, default: `None`)`: Overrides the instance's `content_filter` for this call.
            *   `citations (bool`, default: `True`)`: Whether to convert links to citations.
            *   `**kwargs`: Additional arguments (not currently used by this specific implementation beyond parent class).
        *   Core Logic:
            1.  Instantiates `CustomHTML2Text` using `base_url` and the resolved `html2text_options` (merged from method arg, `self.options`, and defaults).
            2.  Converts `input_html` to `raw_markdown` using the `CustomHTML2Text` instance.
            3.  If `citations` is `True`, calls `self.convert_links_to_citations(raw_markdown, base_url)` to get `markdown_with_citations` and `references_markdown`.
            4.  If `citations` is `False`, `markdown_with_citations` is set to `raw_markdown`, and `references_markdown` is an empty string.
            5.  Determines the active `content_filter` (parameter or instance's `self.content_filter`).
            6.  If an active `content_filter` exists:
                *   Calls `active_filter.filter_content(input_html)` to get a list of filtered HTML strings.
                *   Joins these strings with `\n` and wraps them in `<div>` tags to form `fit_html`.
                *   Uses a new `CustomHTML2Text` instance to convert `fit_html` into `fit_markdown`.
            7.  Otherwise, `fit_html` and `fit_markdown` are set to `None` (or empty strings based on implementation details).
            8.  Constructs and returns a `MarkdownGenerationResult` object with all generated Markdown variants.
    *   3.6.2. `convert_links_to_citations(self, markdown: str, base_url: str = "") -> Tuple[str, str]`
        *   Purpose: Transforms standard Markdown links within the input `markdown` string into a citation format (e.g., `[Link Text]^[1]^`) and generates a corresponding numbered list of references.
        *   Parameters:
            *   `markdown (str)`: The input Markdown string.
            *   `base_url (str`, default: `""`)`: The base URL used to resolve relative link URLs before they are added to the reference list.
        *   Returns: (`Tuple[str, str]`) A tuple where the first element is the Markdown string with links converted to citations, and the second element is a string containing the formatted list of references.
        *   Internal Logic:
            *   Uses the `LINK_PATTERN` regex to find all Markdown links.
            *   For each link, it resolves the URL using `fast_urljoin(base, url)` if `base_url` is provided and the link is relative.
            *   Assigns a unique citation number to each unique URL.
            *   Replaces the original link markup with the citation format (e.g., `[Text]^[Number]^`).
            *   Constructs a Markdown formatted reference list string.
*   3.7. Role of `CustomHTML2Text`:
    *   `CustomHTML2Text` is a customized version of an HTML-to-Markdown converter, likely based on the `html2text` library.
    *   It's instantiated by `DefaultMarkdownGenerator` to perform the core HTML to plain Markdown conversion.
    *   Its behavior is controlled by options passed via `html2text_options` in `generate_markdown` or `self.options` of the `DefaultMarkdownGenerator`. These options can include `body_width`, `ignore_links`, `ignore_images`, etc., influencing the final Markdown output. (Refer to `crawl4ai/html2text.py` for specific options).

## 4. Output Data Model: `MarkdownGenerationResult`

*   4.1. Purpose: `MarkdownGenerationResult` is a Pydantic `BaseModel` designed to structure and encapsulate the various Markdown outputs generated by any `MarkdownGenerationStrategy`. It provides a consistent way to access different versions of the converted content.
*   4.2. Source File: `crawl4ai/models.py`
*   4.3. Fields:
    *   4.3.1. `raw_markdown (str)`: The direct result of converting the input HTML to Markdown, before any citation processing or specific content filtering (by the generator itself) is applied. This represents the most basic Markdown version of the content.
    *   4.3.2. `markdown_with_citations (str)`: Markdown content where hyperlinks have been converted into a citation style (e.g., `[Link Text]^[1]^`). This is typically derived from `raw_markdown`.
    *   4.3.3. `references_markdown (str)`: A string containing a formatted list of references (e.g., numbered list of URLs) corresponding to the citations found in `markdown_with_citations`.
    *   4.3.4. `fit_markdown (Optional[str]`, default: `None`)`: Markdown content generated from HTML that has been processed by a `RelevantContentFilter`. This version is intended to be more concise or focused on relevant parts of the original content. It is `None` if no content filter was applied or if the filter resulted in no content.
    *   4.3.5. `fit_html (Optional[str]`, default: `None`)`: The HTML content that remains after being processed by a `RelevantContentFilter`. `fit_markdown` is generated from this `fit_html`. It is `None` if no content filter was applied or if the filter resulted in no content.
*   4.4. Methods:
    *   4.4.1. `__str__(self) -> str`:
        *   Purpose: Defines the string representation of a `MarkdownGenerationResult` object.
        *   Signature: `__str__(self) -> str`
        *   Returns: (`str`) The content of the `raw_markdown` field.

## 5. Integration with Content Filtering (`RelevantContentFilter`)

*   5.1. Purpose of Integration: `DefaultMarkdownGenerator` allows integration with `RelevantContentFilter` strategies to produce a `fit_markdown` output. This enables generating Markdown from a version of the HTML that has been refined or focused based on relevance criteria defined by the filter (e.g., keywords, semantic similarity, or LLM-based assessment).
*   5.2. Mechanism:
    *   A `RelevantContentFilter` instance can be passed to `DefaultMarkdownGenerator` either during its initialization (via the `content_filter` parameter) or directly to its `generate_markdown` method. The filter passed to `generate_markdown` takes precedence if both are provided.
    *   When an active filter is present, `DefaultMarkdownGenerator.generate_markdown` calls the filter's `filter_content(input_html)` method. This method is expected to return a list of HTML string chunks deemed relevant.
    *   These chunks are then joined (typically with `\n` and wrapped in `<div>` tags) to form the `fit_html` string.
    *   This `fit_html` is then converted to Markdown using `CustomHTML2Text`, and the result is stored as `fit_markdown`.
*   5.3. Impact on `MarkdownGenerationResult`:
    *   If a `RelevantContentFilter` is successfully used:
        *   `MarkdownGenerationResult.fit_markdown` will contain the Markdown derived from the filtered HTML.
        *   `MarkdownGenerationResult.fit_html` will contain the actual filtered HTML string.
    *   If no filter is used, or if the filter returns an empty list of chunks (indicating no content passed the filter), `fit_markdown` and `fit_html` will be `None` (or potentially empty strings, depending on the exact implementation details of joining an empty list).
*   5.4. Supported Filter Types (High-Level Mention):
    *   `PruningContentFilter`: A filter that likely removes irrelevant HTML sections based on predefined rules or structural analysis (e.g., removing common boilerplate like headers, footers, navbars).
    *   `BM25ContentFilter`: A filter that uses the BM25 ranking algorithm to score and select HTML chunks based on their relevance to a user-provided query.
    *   `LLMContentFilter`: A filter that leverages a Large Language Model to assess the relevance of HTML chunks, potentially based on a user query or a general understanding of content importance.
    *   *Note: Detailed descriptions and usage of each filter strategy are covered in their respective documentation sections.*

## 6. Configuration via `CrawlerRunConfig`

*   6.1. `CrawlerRunConfig.markdown_generator`
    *   Purpose: This attribute of the `CrawlerRunConfig` class allows a user to specify a custom `MarkdownGenerationStrategy` instance to be used for the markdown conversion phase of a crawl. This provides flexibility in how HTML content is transformed into Markdown.
    *   Type: `MarkdownGenerationStrategy` (accepts any concrete implementation of this ABC).
    *   Default Value: If not specified, an instance of `DefaultMarkdownGenerator()` is used by default within the `AsyncWebCrawler`'s `aprocess_html` method when `config.markdown_generator` is `None`.
    *   Usage Example:
        ```python
        from crawl4ai import CrawlerRunConfig, DefaultMarkdownGenerator, AsyncWebCrawler
        from crawl4ai.content_filter_strategy import BM25ContentFilter
        import asyncio

        # Example: Configure a markdown generator with a BM25 filter
        bm25_filter = BM25ContentFilter(user_query="Python programming language")
        custom_md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)

        run_config_with_custom_md = CrawlerRunConfig(
            markdown_generator=custom_md_generator,
            # Other run configurations...
        )

        async def example_crawl():
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url="https://en.wikipedia.org/wiki/Python_(programming_language)",
                    config=run_config_with_custom_md
                )
                if result.success and result.markdown:
                    print("Raw Markdown (snippet):", result.markdown.raw_markdown[:200])
                    if result.markdown.fit_markdown:
                        print("Fit Markdown (snippet):", result.markdown.fit_markdown[:200])
        
        # asyncio.run(example_crawl())
        ```

## 7. Influencing Markdown Output for LLM Consumption

*   7.1. Role of `DefaultMarkdownGenerator.options` and `html2text_options`:
    *   The `options` parameter in `DefaultMarkdownGenerator.__init__` and the `html2text_options` parameter in its `generate_markdown` method are used to pass configuration settings directly to the underlying `CustomHTML2Text` instance.
    *   `html2text_options` provided to `generate_markdown` will take precedence over `self.options` set during initialization.
    *   These options control various aspects of the HTML-to-Markdown conversion, such as line wrapping, handling of links, images, and emphasis, which can be crucial for preparing text for LLMs.
*   7.2. Key `CustomHTML2Text` Options (via `html2text_options` or `DefaultMarkdownGenerator.options`):
    *   `bodywidth (int`, default: `0` when `DefaultMarkdownGenerator` calls `CustomHTML2Text` for `raw_markdown` and `fit_markdown` if not otherwise specified): Determines the width for wrapping lines. A value of `0` disables line wrapping, which is often preferred for LLM processing as it preserves sentence structure across lines.
    *   `ignore_links (bool`, default: `False` in `CustomHTML2Text`): If `True`, all hyperlinks (`<a>` tags) are removed from the output, leaving only their anchor text.
    *   `ignore_images (bool`, default: `False` in `CustomHTML2Text`): If `True`, all image tags (`<img>`) are removed from the output.
    *   `ignore_emphasis (bool`, default: `False` in `CustomHTML2Text`): If `True`, emphasized text (e.g., `<em>`, `<strong>`) is rendered as plain text without Markdown emphasis characters (like `*` or `_`).
    *   `bypass_tables (bool`, default: `False` in `CustomHTML2Text`): If `True`, tables are not formatted as Markdown tables but are rendered as a series of paragraphs, which might be easier for some LLMs to process.
    *   `default_image_alt (str`, default: `""` in `CustomHTML2Text`): Specifies a default alt text for images that do not have an `alt` attribute.
    *   `protect_links (bool`, default: `False` in `CustomHTML2Text`): If `True`, URLs in links are not processed or modified.
    *   `single_line_break (bool`, default: `True` in `CustomHTML2Text`): If `True`, single newlines in HTML are converted to Markdown line breaks (two spaces then a newline). This can help preserve some formatting.
    *   `mark_code (bool`, default: `True` in `CustomHTML2Text`): If `True`, `<code>` and `<pre>` blocks are appropriately marked in Markdown.
    *   `escape_snob (bool`, default: `False` in `CustomHTML2Text`): If `True`, more aggressive escaping of special Markdown characters is performed.
    *   *Note: This list is based on common `html2text` options; refer to `crawl4ai/html2text.py` for the exact implementation and default behaviors within `CustomHTML2Text`.*
*   7.3. Impact of `citations (bool)` in `generate_markdown`:
    *   When `citations=True` (default in `DefaultMarkdownGenerator.generate_markdown`):
        *   Standard Markdown links `[text](url)` are converted to `[text]^[citation_number]^`.
        *   A `references_markdown` string is generated, listing all unique URLs with their corresponding citation numbers. This helps LLMs trace information back to its source and can reduce token count if URLs are long or repetitive.
    *   When `citations=False`:
        *   Links remain in their original Markdown format `[text](url)`.
        *   `references_markdown` will be an empty string.
        *   This might be preferred if the LLM needs to directly process the URLs or if the citation format is not desired.
*   7.4. Role of `content_source` in `MarkdownGenerationStrategy`:
    *   This parameter (defaulting to `"cleaned_html"` in `DefaultMarkdownGenerator`) specifies which HTML version is used as the primary input for the `generate_markdown` method.
    *   `"cleaned_html"`: Typically refers to HTML that has undergone initial processing by the `ContentScrapingStrategy` (e.g., removal of scripts, styles, and potentially some boilerplate based on the scraping strategy's rules). This is usually the recommended source for general Markdown conversion.
    *   `"raw_html"`: The original, unmodified HTML content fetched from the web page. Using this source would bypass any initial cleaning done by the scraping strategy.
    *   `"fit_html"`: This source is relevant when a `RelevantContentFilter` is used. `fit_html` is the HTML output *after* the `RelevantContentFilter` has processed the `input_html` (which itself is determined by `content_source`). If `content_source` is, for example, `"cleaned_html"`, then `fit_html` is the result of filtering that cleaned HTML. `fit_markdown` is then generated from this `fit_html`.
*   7.5. `fit_markdown` vs. `raw_markdown`/`markdown_with_citations`:
    *   `raw_markdown` (or `markdown_with_citations` if `citations=True`) is generated from the HTML specified by `content_source` (e.g., `"cleaned_html"`). It represents a general conversion of that source.
    *   `fit_markdown` is generated *only if* a `RelevantContentFilter` is active (either set in `DefaultMarkdownGenerator` or passed to `generate_markdown`). It is derived from the `fit_html` (the output of the content filter).
    *   **Choosing which to use for LLMs:**
        *   Use `fit_markdown` when you need a concise, highly relevant subset of the page's content tailored to a specific query or set of criteria defined by the filter. This can reduce noise and token count for the LLM.
        *   Use `raw_markdown` or `markdown_with_citations` when you need a more comprehensive representation of the page's textual content, or when no specific filtering criteria are applied.
```

---


## Markdown Generation - Reasoning
Source: crawl4ai_markdown_reasoning_content.llm.md

```markdown
# Detailed Outline for crawl4ai - markdown Component

**Target Document Type:** reasoning
**Target Output Filename Suggestion:** `llm_reasoning_markdown_generation.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2025-05-24
---

## 1. Introduction to Markdown Generation in Crawl4AI

*   1.1. **Why Markdown Generation Matters for LLMs**
    *   1.1.1. The role of clean, structured text for Large Language Model consumption.
        *   **Explanation:** LLMs perform significantly better when input data is well-structured and free of irrelevant noise (like HTML tags, scripts, or complex layouts not meant for textual understanding). Markdown, with its simple syntax, provides a human-readable and machine-parseable format that captures essential semantic structure (headings, lists, paragraphs, code blocks, tables) without the clutter of full HTML. This makes it easier for LLMs to understand the content's hierarchy, identify key information, and perform tasks like summarization, question-answering, or RAG (Retrieval Augmented Generation) more accurately and efficiently.
    *   1.1.2. Benefits of Markdown: readability, structure preservation, common format.
        *   **Explanation:**
            *   **Readability:** Markdown is designed to be easily readable in its raw form, making it simple for developers and users to inspect and understand the crawled content.
            *   **Structure Preservation:** It effectively preserves the semantic structure of the original HTML (headings, lists, emphasis, etc.), which is crucial context for LLMs.
            *   **Common Format:** Markdown is a widely adopted standard, ensuring compatibility with a vast ecosystem of tools, editors, and LLM input pipelines.
    *   1.1.3. How Crawl4AI's Markdown generation facilitates RAG and other LLM applications.
        *   **Explanation:** For RAG, Crawl4AI's Markdown output, especially when combined with content filtering, provides clean, relevant text chunks that can be easily embedded and indexed. This improves the quality of retrieved context for LLM prompts. For fine-tuning or direct prompting, the structured Markdown helps the LLM focus on the core content, leading to better quality responses and reducing token consumption by eliminating HTML overhead.

*   1.2. **Overview of Crawl4AI's Markdown Generation Pipeline**
    *   1.2.1. High-level flow: HTML -> (Optional Filtering) -> Markdown Conversion -> (Optional Citation Handling).
        *   **Explanation:**
            1.  **Input HTML:** The process starts with either raw HTML from the crawled page or a cleaned/selected HTML segment.
            2.  **Optional Content Filtering:** Before Markdown conversion, a `RelevantContentFilter` can be applied to the HTML. This step aims to remove boilerplate, ads, or irrelevant sections, resulting in `fit_html`. This is crucial for generating `fit_markdown`.
            3.  **Markdown Conversion:** The selected HTML (either the original, cleaned, or filtered `fit_html`) is converted into Markdown using an underlying `html2text` library, specifically `CustomHTML2Text` in Crawl4AI for enhanced control.
            4.  **Optional Citation Handling:** If enabled, inline links in the generated Markdown are converted to a citation format (e.g., `text [^1^]`), and a separate list of references is created.
    *   1.2.2. Key components involved: `MarkdownGenerationStrategy`, `DefaultMarkdownGenerator`, `CustomHTML2Text`, `RelevantContentFilter`.
        *   **Explanation:**
            *   **`MarkdownGenerationStrategy`:** An interface defining how Markdown should be generated. Allows for custom implementations.
            *   **`DefaultMarkdownGenerator`:** The standard implementation of `MarkdownGenerationStrategy`, using `CustomHTML2Text`. It orchestrates filtering (if provided) and citation handling.
            *   **`CustomHTML2Text`:** An enhanced version of the `html2text` library, providing fine-grained control over the HTML-to-Markdown conversion.
            *   **`RelevantContentFilter`:** An interface for strategies that filter HTML content before it's converted to Markdown, producing `fit_html` and consequently `fit_markdown`.
    *   1.2.3. How `CrawlerRunConfig` ties these components together.
        *   **Explanation:** The `CrawlerRunConfig` object allows you to specify which `MarkdownGenerationStrategy` (and by extension, which filters and `CustomHTML2Text` options) should be used for a particular crawl run via its `markdown_generator` parameter. This provides run-specific control over the Markdown output.

*   1.3. **Goals of this Guide**
    *   1.3.1. Understanding how to configure and customize Markdown output.
        *   **Explanation:** This guide will walk you through the various configuration options available, from choosing HTML sources and content filters to fine-tuning the `html2text` conversion itself.
    *   1.3.2. Best practices for generating LLM-friendly Markdown.
        *   **Explanation:** We'll discuss tips and techniques to produce Markdown that is optimally structured and cleaned for consumption by Large Language Models.
    *   1.3.3. Troubleshooting common Markdown generation issues.
        *   **Explanation:** We'll cover common problems encountered during Markdown generation (e.g., noisy output, missing content) and provide strategies for diagnosing and resolving them.

## 2. Core Concepts in Markdown Generation

*   2.1. **The `MarkdownGenerationStrategy` Interface**
    *   2.1.1. **Purpose and Design Rationale:**
        *   Why use a strategy pattern for Markdown generation? (Flexibility, extensibility).
            *   **Explanation:** The strategy pattern allows Crawl4AI to define a common interface for Markdown generation while enabling different concrete implementations. This means users can easily swap out the default Markdown generator for a custom one without altering the core crawler logic. It promotes flexibility and makes the system extensible for future Markdown conversion needs or integration with other libraries.
        *   Core problem it solves: Decoupling Markdown generation logic from the crawler.
            *   **Explanation:** By abstracting Markdown generation into a strategy, the `AsyncWebCrawler` itself doesn't need to know the specifics of *how* Markdown is created. It simply delegates the task to the configured strategy. This separation of concerns makes the codebase cleaner and easier to maintain.
    *   2.1.2. **When to Implement a Custom `MarkdownGenerationStrategy`:**
        *   Scenarios requiring completely different Markdown conversion logic.
            *   **Example:** If you need to convert HTML to a very specific dialect of Markdown not supported by `html2text`, or if you want to use a different underlying conversion library entirely.
        *   Integrating third-party Markdown conversion libraries.
            *   **Example:** If you prefer to use a library like `turndown` or `mistune` for its specific features or output style.
        *   Advanced pre/post-processing of Markdown.
            *   **Example:** If you need to perform complex transformations on the Markdown *after* initial generation, such as custom table formatting, complex footnote handling beyond standard citations, or domain-specific semantic tagging within the Markdown.
    *   2.1.3. **How to Implement a Custom `MarkdownGenerationStrategy`:**
        *   Key methods to override (`generate_markdown`).
            *   **Explanation:** The primary method to implement is `generate_markdown(self, input_html: str, base_url: str = "", html2text_options: Optional[Dict[str, Any]] = None, content_filter: Optional[RelevantContentFilter] = None, citations: bool = True, **kwargs) -> MarkdownGenerationResult`. This method will receive the HTML (based on `content_source`), and it's responsible for returning a `MarkdownGenerationResult` object.
        *   Input parameters and expected output (`MarkdownGenerationResult`).
            *   **Explanation:** Your custom strategy will receive the `input_html`, the `base_url` (for resolving relative links if needed), `html2text_options` (which you can choose to use or ignore), an optional `content_filter`, and a `citations` flag. It must return an instance of `MarkdownGenerationResult` populated with the relevant Markdown strings.
        *   *Code Example:*
            ```python
            from crawl4ai import MarkdownGenerationStrategy, MarkdownGenerationResult, RelevantContentFilter
            from typing import Optional, Dict, Any

            class MyCustomMarkdownStrategy(MarkdownGenerationStrategy):
                def __init__(self, content_source: str = "cleaned_html", **kwargs):
                    super().__init__(content_source=content_source, **kwargs)
                    # Initialize any custom resources if needed

                def generate_markdown(
                    self,
                    input_html: str,
                    base_url: str = "",
                    html2text_options: Optional[Dict[str, Any]] = None, # You can use or ignore these
                    content_filter: Optional[RelevantContentFilter] = None,
                    citations: bool = True, # You can decide how to handle this
                    **kwargs
                ) -> MarkdownGenerationResult:
                    
                    # 1. Apply content filter if provided and desired
                    fit_html_output = ""
                    if content_filter:
                        # Assuming content_filter.filter_content returns a list of HTML strings
                        filtered_html_blocks = content_filter.filter_content(input_html) 
                        fit_html_output = "\n".join(filtered_html_blocks)
                    
                    # 2. Your custom HTML to Markdown conversion logic
                    # This is where you'd use your preferred library or custom logic
                    raw_markdown_text = f"# Custom Markdown for {base_url}\n\n{input_html[:200]}..." # Placeholder
                    
                    markdown_with_citations_text = raw_markdown_text # Placeholder for citation logic
                    references_markdown_text = "" # Placeholder for references

                    # If you used a filter, also generate fit_markdown
                    fit_markdown_text = ""
                    if fit_html_output:
                        fit_markdown_text = f"# Custom Filtered Markdown\n\n{fit_html_output[:200]}..." # Placeholder

                    return MarkdownGenerationResult(
                        raw_markdown=raw_markdown_text,
                        markdown_with_citations=markdown_with_citations_text,
                        references_markdown=references_markdown_text,
                        fit_markdown=fit_markdown_text,
                        fit_html=fit_html_output
                    )

            # Usage:
            # custom_md_generator = MyCustomMarkdownStrategy()
            # run_config = CrawlerRunConfig(markdown_generator=custom_md_generator)
            ```
        *   Common pitfalls when creating custom strategies.
            *   **Explanation:**
                *   Forgetting to handle all fields in `MarkdownGenerationResult` (even if some are empty strings).
                *   Incorrectly managing `base_url` for relative links if your custom converter doesn't handle it.
                *   Performance bottlenecks if your custom logic is inefficient.
                *   Not properly integrating with the `content_filter` if one is provided.
    *   2.1.4. **Understanding `content_source` in `MarkdownGenerationStrategy`**
        *   2.1.4.1. Purpose: What HTML source should be used for Markdown generation?
            *   **Explanation:** The `content_source` attribute of a `MarkdownGenerationStrategy` (including `DefaultMarkdownGenerator`) tells the strategy which version of the HTML to use as the primary input for generating `raw_markdown` and `markdown_with_citations`.
        *   2.1.4.2. Available options: `"cleaned_html"`, `"raw_html"`, `"fit_html"`.
            *   **`"cleaned_html"` (Default):** This is the HTML after Crawl4AI's internal `ContentScrapingStrategy` (e.g., `WebScrapingStrategy` or `LXMLWebScrapingStrategy`) has processed it. This usually involves removing scripts, styles, and applying structural cleaning or selection based on `target_elements` or `css_selector` in `CrawlerRunConfig`.
            *   **`"raw_html"`:** The original, unmodified HTML fetched from the page. This is useful if you want to apply your own complete cleaning and Markdown conversion pipeline.
            *   **`"fit_html"`:** The HTML *after* a `RelevantContentFilter` (if provided to the `MarkdownGenerationStrategy`) has processed the input HTML (which would be `cleaned_html` or `raw_html` depending on the initial source). This option is powerful when you want Markdown generated *only* from the most relevant parts of the page.
        *   2.1.4.3. **Decision Guide: Choosing the Right `content_source`**:
            *   **When to use `"cleaned_html"`:** This is the recommended default for most LLM use cases. It provides a good balance of structured content without excessive noise, as common boilerplate is often removed by the scraping strategy.
            *   **When to use `"raw_html"`:** Choose this if you need absolute control over the HTML input for your Markdown converter, or if Crawl4AI's default cleaning removes elements you wish to keep. Be aware that this might result in noisier Markdown.
            *   **When to use `"fit_html"`:** Opt for this when you are using a `RelevantContentFilter` with your `MarkdownGenerationStrategy` and you want the `raw_markdown` and `markdown_with_citations` to be based *only* on the filtered content. This is distinct from just using the `fit_markdown` field in the result, as it makes the filtered content the *primary* source for all main Markdown outputs.
            *   **Impact on performance and output quality:**
                *   `"raw_html"` might be slightly faster if Crawl4AI's cleaning is complex, but could lead to lower quality Markdown due to more noise.
                *   `"cleaned_html"` offers a good trade-off.
                *   `"fit_html"` depends on the performance of the `RelevantContentFilter` itself.
        *   2.1.4.4. *Example Scenarios:*
            *   **General Summarization:** `"cleaned_html"` is usually best.
            *   **Highly Specific Q&A on a Section:** Use a `RelevantContentFilter` to produce `fit_html`, then set `content_source="fit_html"` (or just use the `fit_markdown` from the result if `raw_markdown` from `"cleaned_html"` is also desired).
            *   **Archiving Raw Structure:** `"raw_html"` might be chosen if the goal is to convert the entire, unmodified page structure to Markdown, perhaps for later, more nuanced processing.

*   2.2. **The `MarkdownGenerationResult` Model**
    *   2.2.1. **Understanding its Purpose:** Why a structured result object?
        *   **Explanation:** A structured object like `MarkdownGenerationResult` is used instead of a single Markdown string to provide different views or versions of the generated Markdown, catering to various use cases. This allows users to pick the representation that best suits their needs (e.g., with or without citations, raw vs. filtered) without re-processing. It also clearly separates the main content from metadata like references or the intermediate `fit_html`.
    *   2.2.2. **Deep Dive into `MarkdownGenerationResult` Fields:**
        *   `raw_markdown`:
            *   **What it is:** This is the direct, primary Markdown output generated from the `content_source` (e.g., `cleaned_html`) defined in the `MarkdownGenerationStrategy`. It does *not* have inline links converted to citation format.
            *   **How to use it:** Use this when you need the most "vanilla" Markdown, perhaps for LLMs that are sensitive to citation formats or if you plan to implement your own link/reference handling.
            *   **When it's useful:** For direct input to LLMs that don't require source attribution within the text, or as a base for further custom Markdown processing.
        *   `markdown_with_citations`:
            *   **What it is:** This takes the `raw_markdown` and converts its inline links (e.g., `[link text](http://example.com)`) into a citation format (e.g., `link text [^1^]`).
            *   **How it's generated:** The `DefaultMarkdownGenerator` (via `CustomHTML2Text`) scans `raw_markdown` for links, assigns unique numerical IDs to each unique URL, replaces the inline link with the text and citation marker, and populates `references_markdown`.
            *   **How to use it:** This is often the most useful Markdown for LLM tasks requiring RAG or for generating human-readable documents where sources are important. Combine it with `references_markdown`.
            *   *Example:*
                ```html
                <!-- Input HTML fragment -->
                <p>Crawl4AI is an <a href="https://github.com/unclecode/crawl4ai">open-source</a> library.</p>
                ```
                ```markdown
                // Resulting markdown_with_citations (simplified)
                Crawl4AI is an open-source [^1^] library.
                ```
        *   `references_markdown`:
            *   **What it is:** A separate Markdown string that lists all unique URLs found and converted to citations, formatted typically as a numbered list.
            *   **How to use it:** Append this string to the end of `markdown_with_citations` to create a complete document with a bibliography or reference section.
            *   **Why it's separate:** This provides flexibility. You can choose to display references at the end, in a sidebar, or not at all.
            *   *Example:*
                ```markdown
                ## References

                [^1^]: https://github.com/unclecode/crawl4ai
                ```
        *   `fit_markdown`:
            *   **What it is:** This is Markdown generated *exclusively* from the `fit_html`. `fit_html` itself is the output of a `RelevantContentFilter` if one was provided to the `MarkdownGenerationStrategy`. If no filter was used, `fit_markdown` will likely be empty or reflect the `raw_markdown`.
            *   **How to use it:** When your primary goal is to feed an LLM with the most relevant, filtered content. This is excellent for tasks like generating concise summaries or providing highly focused context for RAG.
            *   **Relationship with `raw_markdown`:** If a filter is active, `fit_markdown` is based on a *subset* or *transformed version* of the HTML that `raw_markdown` was based on (assuming `content_source` wasn't `"fit_html"`). If `content_source` *was* `"fit_html"`, then `raw_markdown` and `fit_markdown` would be derived from the same filtered HTML, but `fit_markdown` might still undergo different processing if the strategy handles it distinctly.
            *   *Example:* Imagine a news article page. `raw_markdown` might contain the article, comments, ads, and navigation. If a `BM25ContentFilter` is used with a query about "stock market impact", `fit_markdown` would ideally only contain paragraphs related to that topic, stripped of other page elements.
        *   `fit_html`:
            *   **What it is:** The actual HTML string *after* a `RelevantContentFilter` (like `PruningContentFilter` or `LLMContentFilter`) has processed the input HTML. If no filter is applied, this field will be empty.
            *   **How to use it:** Primarily for debugging your content filters. You can inspect `fit_html` to see exactly what HTML content was deemed "relevant" by your filter before it was converted to `fit_markdown`. It can also be useful if you need this filtered HTML for purposes other than Markdown generation.
            *   **Why it's included:** It provides transparency into the filtering process and allows advanced users to work with the intermediate filtered HTML directly.

## 3. The `DefaultMarkdownGenerator` - Your Go-To Solution

*   3.1. **Understanding the `DefaultMarkdownGenerator`**
    *   3.1.1. **Purpose and Design:** The `DefaultMarkdownGenerator` is Crawl4AI's standard, out-of-the-box mechanism for converting HTML content into various Markdown representations. It's designed to be a robust and generally applicable solution for most common use cases, especially when targeting LLM consumption.
    *   3.1.2. Core Functionality: Its primary task is to orchestrate the HTML-to-Markdown conversion. It internally uses an instance of `CustomHTML2Text` (Crawl4AI's enhanced `html2text` wrapper) to perform the actual conversion.
    *   3.1.3. How it handles citations and references by default.
        *   **Explanation:** If the `citations` parameter in its `generate_markdown` method is `True` (which it is by default), `DefaultMarkdownGenerator` will post-process the initially generated Markdown to convert inline links into citation markers (e.g., `[^1^]`) and generate a corresponding `references_markdown` block. This is done by its internal `CustomHTML2Text` instance.

*   3.2. **Configuring `DefaultMarkdownGenerator`**
    *   3.2.1. **Initialization Options:**
        *   `content_filter (Optional[RelevantContentFilter])`:
            *   **Why use it:** To refine the HTML *before* it's converted to Markdown. This is essential if you want `fit_markdown` (and consequently `fit_html`) to contain only the most relevant parts of the page, leading to a more focused Markdown output.
            *   **How it integrates:** When `generate_markdown` is called, if a `content_filter` is present, `DefaultMarkdownGenerator` first passes the `input_html` (determined by `content_source`) to this filter. The filter returns a list of HTML strings (or a single string if merged). This filtered HTML becomes the `fit_html`. Then, `fit_markdown` is generated from this `fit_html`. The `raw_markdown` and `markdown_with_citations` are still generated from the original `content_source` unless `content_source` itself is set to `"fit_html"`.
            *   *Impact:* Directly influences `fit_markdown` and `fit_html` fields in `MarkdownGenerationResult`. Can significantly reduce the noise and improve the relevance of the final Markdown for LLMs.
            *   *Code Example:*
                ```python
                from crawl4ai import DefaultMarkdownGenerator, CrawlerRunConfig
                from crawl4ai.content_filter_strategy import PruningContentFilter

                # Initialize a filter
                pruning_filter = PruningContentFilter(threshold_type="fixed", threshold=0.5)
                
                # Initialize DefaultMarkdownGenerator with the filter
                md_generator_with_filter = DefaultMarkdownGenerator(content_filter=pruning_filter)

                # This generator will now produce 'fit_markdown' based on pruning.
                # run_config = CrawlerRunConfig(markdown_generator=md_generator_with_filter)
                # result = await crawler.arun(url="...", config=run_config)
                # print(result.markdown.fit_markdown) 
                ```
        *   `options (Optional[Dict[str, Any]])`:
            *   **What it is:** This dictionary allows you to pass configuration options directly to the underlying `CustomHTML2Text` instance. These options control the specifics of the HTML-to-Markdown conversion process.
            *   **How to use it:** Provide a dictionary where keys are `html2text` option names (e.g., `body_width`, `ignore_links`) and values are their desired settings.
            *   *See Section 6: Mastering `CustomHTML2Text` for detailed options.*
        *   `content_source (str)`:
            *   **Reiteration:** As discussed in section 2.1.4, this determines the primary HTML input for `raw_markdown` and `markdown_with_citations`.
            *   **How it interacts with `content_filter`:**
                *   If `content_source` is, for example, `"cleaned_html"` and a `content_filter` is also provided, the `content_filter` will process this `"cleaned_html"` to produce `fit_html`. The `fit_markdown` field in `MarkdownGenerationResult` will be based on this `fit_html`.
                *   However, `raw_markdown` and `markdown_with_citations` will still be based on the original `"cleaned_html"` (unless `content_source` was explicitly set to `"fit_html"`). This allows you to have both a "fuller" Markdown and a "filtered" Markdown from a single generation step.

*   3.3. **Common Workflows with `DefaultMarkdownGenerator`**
    *   3.3.1. **Workflow: Generating Basic Markdown with Citations**
        *   Steps: Instantiate `DefaultMarkdownGenerator` (or use the crawler's default). The crawler calls its `generate_markdown` method. Access `result.markdown.markdown_with_citations` and `result.markdown.references_markdown`.
        *   *Code Example:*
            ```python
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator

            async def basic_markdown_workflow():
                # DefaultMarkdownGenerator is used implicitly if none is specified in CrawlerRunConfig
                # Or explicitly:
                md_generator = DefaultMarkdownGenerator() 
                run_config = CrawlerRunConfig(markdown_generator=md_generator)

                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url="https://example.com", config=run_config)
                    if result.success:
                        print("--- Markdown with Citations ---")
                        print(result.markdown.markdown_with_citations[:500]) # Show first 500 chars
                        print("\n--- References ---")
                        print(result.markdown.references_markdown)
                    else:
                        print(f"Crawl failed: {result.error_message}")
            ```
    *   3.3.2. **Workflow: Generating Focused Markdown using a Content Filter**
        *   Steps:
            1.  Choose and instantiate a `RelevantContentFilter` (e.g., `BM25ContentFilter`).
            2.  Instantiate `DefaultMarkdownGenerator`, passing the filter to its `content_filter` parameter.
            3.  Set this `DefaultMarkdownGenerator` instance in `CrawlerRunConfig.markdown_generator`.
            4.  After crawling, access `result.markdown.fit_markdown`.
        *   Key configuration considerations for the filter and generator:
            *   For `BM25ContentFilter`, ensure you provide a relevant `user_query`.
            *   Adjust filter thresholds (e.g., `bm25_threshold`) as needed.
            *   The `content_source` for `DefaultMarkdownGenerator` will be the input to the filter.
        *   *Code Example:*
            ```python
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode
            from crawl4ai.content_filter_strategy import BM25ContentFilter

            async def filtered_markdown_workflow():
                user_query = "information about Crawl4AI library"
                bm25_filter = BM25ContentFilter(user_query=user_query, bm25_threshold=0.1)
                
                md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
                
                run_config = CrawlerRunConfig(
                    markdown_generator=md_generator,
                    cache_mode=CacheMode.BYPASS # For consistent demo results
                )

                async with AsyncWebCrawler() as crawler:
                    # Using a page that hopefully has content related to the query
                    result = await crawler.arun(url="https://github.com/unclecode/crawl4ai", config=run_config) 
                    if result.success:
                        print("--- Fit Markdown (BM25 Filtered) ---")
                        print(result.markdown.fit_markdown) # This is the key output
                        # You can also inspect fit_html to see what the filter selected
                        # print("\n--- Fit HTML ---")
                        # print(result.markdown.fit_html[:500])
                    else:
                        print(f"Crawl failed: {result.error_message}")
            ```
    *   3.3.3. **Workflow: Customizing Markdown Style via `html2text_options`**
        *   Steps: Instantiate `DefaultMarkdownGenerator` passing a dictionary of `html2text` options to its `options` parameter.
        *   *Code Example:*
            ```python
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator

            async def custom_style_markdown_workflow():
                # Example: Disable line wrapping and ignore images
                html2text_opts = {
                    "body_width": 0,      # Disable line wrapping
                    "ignore_images": True # Don't include image markdown ![alt](src)
                }
                md_generator = DefaultMarkdownGenerator(options=html2text_opts)
                
                run_config = CrawlerRunConfig(markdown_generator=md_generator)

                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url="https://example.com", config=run_config)
                    if result.success:
                        print("--- Custom Styled Markdown (No Wrap, No Images) ---")
                        print(result.markdown.raw_markdown[:500]) # raw_markdown will reflect these options
                    else:
                        print(f"Crawl failed: {result.error_message}")
            ```
*   3.4. **Best Practices for `DefaultMarkdownGenerator`**
    *   **When to use `DefaultMarkdownGenerator` vs. a custom strategy:**
        *   Use `DefaultMarkdownGenerator` for most cases. It's robust and highly configurable through `content_filter` and `html2text_options`.
        *   Opt for a custom strategy only if you need fundamentally different conversion logic or integration with external Markdown libraries that `CustomHTML2Text` doesn't cover.
    *   **Tips for choosing the right `content_source` and `content_filter`:**
        *   Start with `content_source="cleaned_html"` (default) and no filter.
        *   If the output is too noisy, introduce a `RelevantContentFilter`. `PruningContentFilter` is a good first step for general boilerplate. Use `BM25ContentFilter` or `LLMContentFilter` for more targeted filtering based on semantic relevance.
        *   If your filter is very effective and you *only* want Markdown from the filtered content, consider setting `content_source="fit_html"` in your `DefaultMarkdownGenerator` instance.
    *   **How to leverage `MarkdownGenerationResult` effectively:**
        *   For LLM input where source attribution is important, use `markdown_with_citations` + `references_markdown`.
        *   For tasks needing maximum conciseness based on relevance, use `fit_markdown` (after configuring a `content_filter`).
        *   Use `raw_markdown` if you need the "purest" Markdown conversion without citation processing.
        *   Inspect `fit_html` to debug your content filters.

## 4. Integrating Content Filters for Smarter Markdown (`fit_markdown`)

*   4.1. **The "Why": Purpose of Content Filtering Before Markdown Generation**
    *   4.1.1. Reducing noise and improving relevance for LLMs.
        *   **Explanation:** Web pages often contain much more than just the main article content (e.g., navigation, ads, footers, related articles). These can be detrimental to LLM performance, increasing token count, processing time, and potentially confusing the model. Content filters aim to isolate the core, relevant information.
    *   4.1.2. Generating more concise and focused Markdown (`fit_markdown`).
        *   **Explanation:** By filtering the HTML *before* converting it to Markdown, the resulting `fit_markdown` is inherently more concise and focused on what the filter deemed important. This is ideal for tasks where brevity and relevance are key.
    *   4.1.3. How `fit_html` is generated and its role.
        *   **Explanation:** When a `RelevantContentFilter` is used with a `MarkdownGenerationStrategy`, the strategy first passes the input HTML (e.g., `cleaned_html`) to the filter's `filter_content` method. This method returns a list of HTML strings (or a single merged string). This output is stored as `fit_html` in the `MarkdownGenerationResult`. `fit_markdown` is then generated by converting this `fit_html` to Markdown.

*   4.2. **Overview of `RelevantContentFilter` Strategies**
    *   4.2.1. **`PruningContentFilter`**:
        *   **How it works:** Applies heuristic rules to remove common boilerplate. For example, it might remove elements with very short text content, elements with a high link-to-text ratio, or elements matching common boilerplate CSS classes/IDs (like "footer", "nav", "sidebar").
        *   **When to use it:** A good first-pass filter for general-purpose cleaning. It's fast and doesn't require LLM calls or complex configuration.
        *   **Impact on `fit_markdown`:** Typically good at removing obvious non-content sections, resulting in a cleaner, more article-focused Markdown.
    *   4.2.2. **`BM25ContentFilter`**:
        *   **How it works:** This filter uses the BM25 algorithm, a classical information retrieval technique. It tokenizes the HTML content into chunks and scores each chunk's relevance against a `user_query`. Chunks exceeding a `bm25_threshold` are kept.
        *   **When to use it:** When you want to extract content specifically related to a user's query from a larger page. Excellent for targeted information retrieval.
        *   **Impact on `fit_markdown`:** The output will be highly tailored to the query. If the query is "Tell me about Crawl4AI's caching", `fit_markdown` should primarily contain sections discussing caching.
    *   4.2.3. **`LLMContentFilter`**:
        *   **How it works:** This is the most powerful and flexible filter. It chunks the input HTML and sends each chunk (or a summary) to an LLM with specific `instructions` (e.g., "Extract only the paragraphs discussing financial results"). The LLM decides which chunks are relevant.
        *   **When to use it:** For complex filtering criteria that are hard to express with rules or keywords, or when nuanced understanding of content is required.
        *   **Impact on `fit_markdown`:** Can produce very precise and contextually relevant Markdown. However, it's generally slower and can be more expensive due to LLM API calls.
*   4.3. **Decision Guide: Choosing the Right `RelevantContentFilter`**
    *   *Table:*
        | Filter                | Speed      | Cost (LLM API) | Accuracy/Nuance | Use Case Examples                                  | Configuration Complexity |
        |-----------------------|------------|----------------|-----------------|----------------------------------------------------|--------------------------|
        | `PruningContentFilter`| Very Fast  | None           | Low-Medium      | General boilerplate removal, quick cleaning.       | Low                      |
        | `BM25ContentFilter`   | Fast       | None           | Medium          | Query-focused extraction, finding relevant sections. | Medium (query, threshold)|
        | `LLMContentFilter`    | Slow       | Potentially High| High            | Complex criteria, nuanced extraction, summarization. | High (prompt engineering)  |
    *   Factors to consider:
        *   **Desired Output Quality:** For the highest semantic relevance, `LLMContentFilter` is often best, but at a cost.
        *   **Performance Constraints:** If speed is critical, `PruningContentFilter` or `BM25ContentFilter` are preferred.
        *   **Nature of the HTML Content:** For well-structured articles, `PruningContentFilter` might be sufficient. For diverse content or Q&A, `BM25ContentFilter` or `LLMContentFilter` might be better.
        *   **Specificity of Task:** If you have a clear query, `BM25ContentFilter` excels. If you have complex instructions, `LLMContentFilter` is suitable.
*   4.4. **Code Examples: Combining Filters with `DefaultMarkdownGenerator`**
    *   4.4.1. *Example:* [Using `PruningContentFilter` to generate `fit_markdown`].
        ```python
        from crawl4ai import DefaultMarkdownGenerator, CrawlerRunConfig, AsyncWebCrawler, CacheMode
        from crawl4ai.content_filter_strategy import PruningContentFilter

        async def pruning_filter_example():
            pruning_filter = PruningContentFilter(threshold=0.4, threshold_type="fixed") # Adjust threshold as needed
            md_generator = DefaultMarkdownGenerator(content_filter=pruning_filter)
            run_config = CrawlerRunConfig(markdown_generator=md_generator, cache_mode=CacheMode.BYPASS)

            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url="https://en.wikipedia.org/wiki/Python_(programming_language)", config=run_config)
                if result.success:
                    print("--- Fit Markdown (Pruned) ---")
                    print(result.markdown.fit_markdown[:1000]) # Show first 1000 chars
                    # print("\n--- Original Raw Markdown (for comparison) ---")
                    # print(result.markdown.raw_markdown[:1000])
        ```
    *   4.4.2. *Example:* [Using `BM25ContentFilter` with a query to generate query-focused `fit_markdown`].
        ```python
        from crawl4ai import DefaultMarkdownGenerator, CrawlerRunConfig, AsyncWebCrawler, CacheMode
        from crawl4ai.content_filter_strategy import BM25ContentFilter

        async def bm25_filter_example():
            user_query = "Python syntax and semantics"
            bm25_filter = BM25ContentFilter(user_query=user_query, bm25_threshold=0.1)
            md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
            run_config = CrawlerRunConfig(markdown_generator=md_generator, cache_mode=CacheMode.BYPASS)
            
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url="https://en.wikipedia.org/wiki/Python_(programming_language)", config=run_config)
                if result.success:
                    print(f"--- Fit Markdown (BM25 Filtered for query: '{user_query}') ---")
                    print(result.markdown.fit_markdown)
        ```
    *   4.4.3. *Example:* [Using `LLMContentFilter` for nuanced content selection before Markdown generation].
        ```python
        from crawl4ai import DefaultMarkdownGenerator, CrawlerRunConfig, AsyncWebCrawler, LLMConfig, CacheMode
        from crawl4ai.content_filter_strategy import LLMContentFilter
        import os

        async def llm_filter_example():
            # Ensure OPENAI_API_KEY is set in your environment
            if not os.getenv("OPENAI_API_KEY"):
                print("OPENAI_API_KEY not set. Skipping LLMContentFilter example.")
                return

            llm_config_obj = LLMConfig(provider="openai/gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
            
            instruction = "Extract only the sections that discuss Python's history and its creator."
            llm_filter = LLMContentFilter(
                llm_config=llm_config_obj,
                instruction=instruction,
                # chunk_token_threshold=1000 # Adjust as needed
            )
            
            md_generator = DefaultMarkdownGenerator(content_filter=llm_filter, content_source="cleaned_html")
            
            run_config = CrawlerRunConfig(markdown_generator=md_generator, cache_mode=CacheMode.BYPASS)

            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url="https://en.wikipedia.org/wiki/Python_(programming_language)", config=run_config)
                if result.success:
                    print(f"--- Fit Markdown (LLM Filtered with instruction: '{instruction}') ---")
                    print(result.markdown.fit_markdown)
                    llm_filter.show_usage() # Display token usage
                else:
                    print(f"Crawl failed: {result.error_message}")
        ```
*   4.5. **Best Practices for Content Filtering for Markdown**
    *   **Start Simple:** Begin with `PruningContentFilter` for general cleanup. It's fast and often effective for removing common boilerplate.
    *   **Query-Specific Tasks:** If your goal is to extract information relevant to a specific query, `BM25ContentFilter` is a great, cost-effective choice.
    *   **Nuanced Selection:** Reserve `LLMContentFilter` for tasks requiring deeper semantic understanding or complex filtering logic that rules-based or keyword-based approaches can't handle. Be mindful of its cost and latency.
    *   **Iterate and Test:** Content filtering is often an iterative process. Test your filter configurations on various pages to ensure they behave as expected. Inspect `fit_html` to understand what the filter is selecting/discarding.
    *   **Combine with `content_source`:** Remember that `fit_markdown` is derived from the output of the filter. If you also need Markdown from the pre-filtered content, ensure your `MarkdownGenerationStrategy`'s `content_source` is set appropriately (e.g., `"cleaned_html"`) so that `raw_markdown` reflects that, while `fit_markdown` reflects the filtered version.

## 5. Customizing Markdown Output via `CrawlerRunConfig`

*   5.1. **The Role of `CrawlerRunConfig.markdown_generator`**
    *   5.1.1. How it allows specifying a custom Markdown generation strategy for a crawl run.
        *   **Explanation:** The `markdown_generator` parameter within the `CrawlerRunConfig` object is the primary way to control how Markdown is generated for a specific crawl operation (i.e., a call to `crawler.arun()` or tasks within `crawler.arun_many()`). You can assign an instance of any class that adheres to the `MarkdownGenerationStrategy` interface to it.
    *   5.1.2. Overriding the default Markdown generation behavior.
        *   **Explanation:** If `CrawlerRunConfig.markdown_generator` is not set (i.e., it's `None`), Crawl4AI will use a default instance of `DefaultMarkdownGenerator` with its standard settings. By providing your own `MarkdownGenerationStrategy` instance (be it a configured `DefaultMarkdownGenerator` or a custom class), you override this default behavior for that particular run.

*   5.2. **Scenarios for Using `CrawlerRunConfig.markdown_generator`**
    *   5.2.1. Applying a pre-configured `DefaultMarkdownGenerator` with specific filters or options.
        *   **Why:** You might want different filtering logic or `html2text` options for different URLs or types of content you're crawling, even within the same `AsyncWebCrawler` instance.
    *   5.2.2. Plugging in a completely custom `MarkdownGenerationStrategy`.
        *   **Why:** As discussed in section 2.1.2, if you have unique Markdown requirements or want to use a different conversion library.
    *   5.2.3. Disabling Markdown generation entirely by setting it to `None` (if applicable, or by using a "NoOp" strategy).
        *   **Why:** If, for a specific crawl, you only need the HTML or extracted structured data and don't require Markdown output, you can pass `markdown_generator=None` (or a strategy that does nothing) to save processing time.
        *   *Note:* To truly disable Markdown generation and its associated `CustomHTML2Text` processing, you might need a "NoOpMarkdownGenerator". If `markdown_generator` is `None`, the crawler might still fall back to a default. A NoOp strategy would explicitly do nothing.
            ```python
            # class NoOpMarkdownGenerator(MarkdownGenerationStrategy):
            #     def generate_markdown(self, input_html: str, **kwargs) -> MarkdownGenerationResult:
            #         return MarkdownGenerationResult(raw_markdown="", markdown_with_citations="", references_markdown="")
            # run_config = CrawlerRunConfig(markdown_generator=NoOpMarkdownGenerator())
            ```

*   5.3. **Code Examples:**
    *   5.3.1. *Example:* [Setting a `DefaultMarkdownGenerator` with a `PruningContentFilter` in `CrawlerRunConfig`].
        ```python
        from crawl4ai import (
            AsyncWebCrawler, 
            CrawlerRunConfig, 
            DefaultMarkdownGenerator, 
            CacheMode
        )
        from crawl4ai.content_filter_strategy import PruningContentFilter

        async def run_with_specific_md_generator():
            # Configure a specific markdown generator
            pruning_filter = PruningContentFilter(threshold=0.6)
            specific_md_generator = DefaultMarkdownGenerator(
                content_filter=pruning_filter,
                options={"body_width": 0, "ignore_links": True} 
            )

            # Configure the crawl run to use this generator
            run_config = CrawlerRunConfig(
                markdown_generator=specific_md_generator,
                cache_mode=CacheMode.BYPASS
            )

            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url="https://example.com/article1", config=run_config)
                if result.success:
                    print("--- Markdown from Article 1 (Pruned, No Links, No Wrap) ---")
                    print(result.markdown.fit_markdown[:500]) 
                    # raw_markdown would also reflect no-wrap and no-links from html2text_options

                # For another URL, you could use a different (or default) generator
                # default_run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
                # result2 = await crawler.arun(url="https://example.com/article2", config=default_run_config)

        # asyncio.run(run_with_specific_md_generator())
        ```
    *   5.3.2. *Example:* [Setting a custom `MyMarkdownStrategy` in `CrawlerRunConfig` (assuming `MyCustomMarkdownStrategy` from 2.1.3)].
        ```python
        # Assuming MyCustomMarkdownStrategy is defined as in section 2.1.3
        # from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode
        # from your_module import MyCustomMarkdownStrategy # If it's in another file

        # async def run_with_custom_md_strategy():
        #     custom_strategy = MyCustomMarkdownStrategy(content_source="raw_html")
        #     run_config_custom = CrawlerRunConfig(
        #         markdown_generator=custom_strategy,
        #         cache_mode=CacheMode.BYPASS
        #     )

        #     async with AsyncWebCrawler() as crawler:
        #         result = await crawler.arun(url="https://example.com", config=run_config_custom)
        #         if result.success:
        #             print("--- Markdown from Custom Strategy ---")
        #             print(result.markdown.raw_markdown) # Or other fields your strategy populates
        
        # asyncio.run(run_with_custom_md_strategy())
        ```
*   5.4. **Interaction with Global vs. Run-Specific Configurations**
    *   **Explanation:** `AsyncWebCrawler` itself does not have a global `markdown_generator` setting during its initialization. Markdown generation is configured *per run* via `CrawlerRunConfig`. This design choice provides maximum flexibility, allowing different Markdown strategies for different URLs or tasks within the same crawler instance lifecycle. If `CrawlerRunConfig.markdown_generator` is not provided, a default `DefaultMarkdownGenerator` instance is used for that specific run.

## 6. Mastering `CustomHTML2Text` for Fine-Grained Control

*   6.1. **Understanding `CustomHTML2Text`**
    *   6.1.1. **Purpose:** Why Crawl4AI includes its own `html2text` extension.
        *   **Enhanced control:** `CustomHTML2Text` is a subclass of the standard `html2text.HTML2Text` library. Crawl4AI uses this custom version to gain more precise control over the HTML-to-Markdown conversion process, particularly to make the output more suitable for LLMs.
        *   **Specific adaptations:** It includes logic for handling Crawl4AI's citation and reference generation (`convert_links_to_citations`), and potentially other tweaks that improve the quality and utility of the Markdown output for AI applications.
    *   6.1.2. **How it's used by `DefaultMarkdownGenerator`**.
        *   **Explanation:** `DefaultMarkdownGenerator` instantiates `CustomHTML2Text` internally. When you pass `options` to `DefaultMarkdownGenerator`, these are ultimately used to configure this `CustomHTML2Text` instance. The `handle()` method of `CustomHTML2Text` is what performs the core HTML to Markdown conversion.

*   6.2. **Key `html2text_options` and Their Impact**
    *   (These options are passed via `DefaultMarkdownGenerator(options=...)`)
    *   6.2.1. `body_width`:
        *   **What it does:** Controls the maximum width of lines in the generated Markdown before wrapping.
        *   **Why configure it:** For LLM consumption, it's often best to disable automatic line wrapping to allow the LLM to process text based on natural paragraph breaks. Setting `body_width=0` achieves this.
        *   *Example:*
            *   `body_width=80` (default-ish for some tools):
                ```markdown
                This is a longer sentence that will be wrapped by html2text if the body_width is
                set to a value like 80 characters.
                ```
            *   `body_width=0`:
                ```markdown
                This is a longer sentence that will not be wrapped by html2text if body_width is 0, allowing the LLM to handle line breaks.
                ```
    *   6.2.2. `ignore_links`:
        *   **What it does:** If `True`, all hyperlink information (`[text](url)`) is removed, leaving only the link text.
        *   **Why configure it:** Set to `True` if links are considered noise for your LLM task and you don't need source attribution. If `False` (default for Crawl4AI's `CustomHTML2Text` unless overridden), links are preserved and can then be converted to citations by `DefaultMarkdownGenerator`.
        *   *Example:*
            *   `ignore_links=False` (then processed for citations): `Visit [Crawl4AI](https://crawl4ai.com)` -> `Visit Crawl4AI [^1^]`
            *   `ignore_links=True`: `Visit [Crawl4AI](https://crawl4ai.com)` -> `Visit Crawl4AI`
    *   6.2.3. `ignore_images`:
        *   **What it does:** If `True`, image tags (`<img>`) are completely ignored, and no Markdown image syntax (`![alt](src)`) is generated.
        *   **Why configure it:** Useful if image information is irrelevant to your LLM task and you want cleaner, more text-focused Markdown.
        *   *Example:*
            *   HTML: `<img src="logo.png" alt="My Logo">`
            *   `ignore_images=False`: `![My Logo](logo.png)`
            *   `ignore_images=True`: (nothing is output for the image)
    *   6.2.4. `protect_links`:
        *   **What it does:** If `True`, surrounds link URLs with `<` and `>`. E.g., `[text](<url>)`.
        *   **Why configure it:** This can sometimes help Markdown parsers that might misinterpret URLs containing special characters. However, with Crawl4AI's citation handling, this is generally not needed, as the raw URLs are moved to the reference section.
    *   6.2.5. `mark_code`:
        *   **What it does:** Controls how `<pre>` and `<code>` tags are handled. If `True`, it attempts to use Markdown code block syntax (backticks).
        *   **Why configure it:** Essential for preserving code snippets correctly. Usually, you'd want this to be `True`.
    *   6.2.6. `default_image_alt`:
        *   **What it does:** Provides a default alt text string if an `<img>` tag is missing an `alt` attribute.
        *   **Why configure it:** Can make Markdown more consistent if you choose to include images.
    *   6.2.7. `bypass_tables`:
        *   **What it does:** If `True`, `<table>` elements are not converted into Markdown table syntax. Their content might be rendered as plain text or omitted, depending on other settings.
        *   **Why configure it:** Standard Markdown table syntax is limited and may not handle complex tables (with `colspan`, `rowspan`, nested tables) well. If you encounter mangled tables, setting this to `True` and processing the table HTML separately (e.g., by extracting the `<table>` HTML and using a specialized table-to-text or table-to-JSON library) might be a better approach.
    *   6.2.8. `pad_tables`:
        *   **What it does:** If `True`, adds padding spaces around cell content in Markdown tables for better visual alignment in raw Markdown.
        *   **Why configure it:** Mostly an aesthetic choice for human readability of the raw Markdown; LLMs typically don't care about this padding.
    *   *Other relevant options identified from `CustomHTML2Text` (or base `html2text`) source:*
        *   `escape_snob`: If `True`, escapes `>` and `&` characters. Default is `False`.
        *   `skip_internal_links`: If `True`, ignores links that start with `#`. Default is `False`.
        *   `links_each_paragraph`: If `True`, puts a link list after each paragraph. Default is `False`. Crawl4AI's citation system provides a better alternative.
        *   `unicode_snob`: If `True`, uses Unicode characters instead of ASCII approximations. Default is `False` in base `html2text`, but `CustomHTML2Text` might behave differently or Crawl4AI ensures UTF-8 handling.
*   6.3. **Best Practices for Configuring `CustomHTML2Text`**
    *   6.3.1. **General recommendations for LLM-friendly output:**
        *   Set `body_width=0` to disable line wrapping and let paragraphs flow naturally.
        *   Consider `ignore_images=True` if images are not relevant to the LLM's task.
        *   Usually, keep `ignore_links=False` (Crawl4AI default) to allow `DefaultMarkdownGenerator` to handle citations properly.
    *   6.3.2. **How to balance information preservation with conciseness:**
        *   Be selective with `ignore_*` options. Removing too much might discard useful context.
        *   Use content filters (Section 4) for semantic reduction rather than relying solely on `html2text` options to remove large irrelevant sections.
    *   6.3.3. **Experimenting with options to achieve desired Markdown style:**
        *   Create a small test HTML snippet.
        *   Instantiate `DefaultMarkdownGenerator` with different `options` dictionaries.
        *   Call its `generate_markdown` method directly (or `_html_to_markdown` on its internal `CustomHTML2Text` instance if you want to bypass citation logic for testing) and observe the output.
*   6.4. **Handling Citations and References (`convert_links_to_citations` method in `CustomHTML2Text`)**
    *   6.4.1. **How it works:**
        *   The `convert_links_to_citations` method (called by `DefaultMarkdownGenerator` if citations are enabled) iterates through the Markdown produced by `html2text.handle()`.
        *   It uses a regular expression (`LINK_PATTERN`) to find all Markdown links (`[text](url "optional title")`).
        *   For each unique URL, it assigns an incremental citation number.
        *   It replaces the original Markdown link with `text [^N^]` (or `![text][^N^]` for images if not ignored).
        *   It builds up a list of reference strings like `[^N^]: url "optional title - text if different from title"`.
    *   6.4.2. **When it's called:** This method is invoked by `DefaultMarkdownGenerator.generate_markdown()` *after* the initial HTML-to-Markdown conversion by `CustomHTML2Text.handle()` if the `citations` flag is `True`.
    *   6.4.3. **Impact on `MarkdownGenerationResult` fields:**
        *   The modified Markdown (with `[^N^]` markers) is stored in `markdown_with_citations`.
        *   The collected reference list is stored in `references_markdown`.
        *   `raw_markdown` remains the version *before* citation processing.
    *   6.4.4. **Customizing Citation Behavior (if possible through options or by subclassing)**.
        *   **Explanation:** Direct customization of the citation format (e.g., changing `[^N^]` to `(N)`) via options is not explicitly provided in `CustomHTML2Text`.
        *   To change this, you would need to:
            1.  Create your own class inheriting from `DefaultMarkdownGenerator`.
            2.  Override the `generate_markdown` method.
            3.  In your override, you could either:
                *   Call the parent's `generate_markdown`, get the `MarkdownGenerationResult`, and then post-process `markdown_with_citations` and `references_markdown` to your desired format.
                *   Or, more invasively, replicate the logic but modify the citation generation part. This might involve creating a custom version of `CustomHTML2Text` or its `convert_links_to_citations` method.
        *   For most users, the default citation format is standard and widely accepted.

## 7. Advanced Markdown Generation Techniques & Best Practices

*   7.1. **Achieving LLM-Friendly Markdown Output**
    *   7.1.1. Prioritizing semantic structure (headings, lists, paragraphs).
        *   **Why:** LLMs leverage structural cues to understand context and hierarchy. Ensure your `html2text_options` (e.g., for headings, list indentation) preserve this structure faithfully.
        *   **How:** Rely on `CustomHTML2Text`'s default handling of semantic HTML tags. If specific tags are problematic, consider pre-processing the HTML.
    *   7.1.2. Handling complex HTML structures (nested tables, complex layouts).
        *   **Strategies for simplifying or selectively extracting from them:**
            *   **Tables:** For very complex tables, consider `html2text_options={'bypass_tables': True}`. Then, extract the table HTML separately (e.g., using `CrawlResult.html` and a CSS selector for the table) and process it with a specialized table parsing library or even an LLM call focused just on table interpretation.
            *   **Layouts:** Aggressive `RelevantContentFilter` strategies can help. If parts of a complex layout are consistently noise, use `CrawlerRunConfig.excluded_selector` to remove them before they even reach the Markdown generator.
    *   7.1.3. When to prefer `fit_markdown` over `raw_markdown` (or `markdown_with_citations`).
        *   **Reasoning:**
            *   **`fit_markdown`:** Best for tasks requiring high relevance and conciseness (e.g., RAG context, focused summarization). It reflects the output of your content filtering.
            *   **`raw_markdown` / `markdown_with_citations`:** Better when you need a broader representation of the page's textual content, or when the filtering might be too aggressive and discard potentially useful context. Also, if your `content_source` is already very clean (e.g., from a targeted CSS selector), the difference might be minimal.
    *   7.1.4. Balancing detail vs. conciseness for different LLM tasks (e.g., summarization vs. Q&A).
        *   **Summarization:** `fit_markdown` from a well-configured `LLMContentFilter` or `BM25ContentFilter` is often ideal. You might also use more aggressive `html2text_options` to remove minor elements.
        *   **Q&A / RAG:** You might prefer a slightly less aggressive filter or even `raw_markdown` (if `content_source` is clean) to ensure all potentially relevant details are available. Citations (`markdown_with_citations` and `references_markdown`) are crucial here for source tracking.

*   7.2. **Pre-processing HTML for Better Markdown**
    *   7.2.1. Using `CrawlerRunConfig.excluded_tags` or `excluded_selector` to remove noise before Markdown generation.
        *   **How:** These parameters in `CrawlerRunConfig` are applied by the `ContentScrapingStrategy` *before* the HTML even reaches the `MarkdownGenerationStrategy`.
        *   **Why:** This is the most efficient way to remove large, consistently irrelevant sections (like global headers, footers, sidebars, ad blocks) across all outputs (HTML, Markdown, etc.).
        *   *Code Example:*
            ```python
            # In CrawlerRunConfig
            # config = CrawlerRunConfig(
            #     excluded_tags=["nav", "footer", "script", "style"],
            #     excluded_selector=".ads, #social-share-buttons"
            # )
            ```
    *   7.2.2. The role of `ContentScrapingStrategy` (e.g., `LXMLWebScrapingStrategy` or the default `WebScrapingStrategy` using BeautifulSoup) in preparing the HTML that `DefaultMarkdownGenerator` receives.
        *   **Explanation:** The `ContentScrapingStrategy` is responsible for the initial cleaning of the HTML. Its output (what becomes `cleaned_html`) is the direct input to `DefaultMarkdownGenerator` if `content_source` is `"cleaned_html"`. Understanding how your chosen scraping strategy cleans HTML is key to predicting the input for Markdown generation. `LXMLWebScrapingStrategy` is generally faster and can be more robust for heavily malformed HTML.

*   7.3. **Post-processing Generated Markdown**
    *   7.3.1. When and why you might need to further process Markdown from `MarkdownGenerationResult`.
        *   **Scenarios:**
            *   Custom formatting not achievable with `html2text` options (e.g., specific table styles, unique list markers).
            *   Domain-specific transformations (e.g., converting certain patterns to custom shortcodes).
            *   Further cleaning or condensing based on rules `html2text` or content filters don't cover.
    *   7.3.2. *Example:* [Python snippet for custom regex replacements or structural adjustments on `raw_markdown`].
        ```python
        import re

        def custom_post_process_markdown(markdown_text):
            # Example: Replace all occurrences of "Crawl4AI" with "**Crawl4AI**"
            markdown_text = re.sub(r"Crawl4AI", r"**Crawl4AI**", markdown_text)
            
            # Example: Add a horizontal rule after every H2 heading
            markdown_text = re.sub(r"(^## .*)", r"\1\n\n---", markdown_text, flags=re.MULTILINE)
            return markdown_text

        # result = await crawler.arun(...)
        # if result.success:
        #     final_markdown = custom_post_process_markdown(result.markdown.raw_markdown)
        #     print(final_markdown)
        ```

*   7.4. **Combining Different Strategies for Optimal Results**
    *   7.4.1. *Scenario:* Using a `RelevantContentFilter` to get `fit_html`, then passing `fit_html` to a custom Markdown generator that expects highly focused input.
        *   **How:**
            1.  Instantiate your filter (e.g., `LLMContentFilter`).
            2.  Instantiate your custom Markdown generator (`MyCustomMarkdownStrategy`).
            3.  In `CrawlerRunConfig`, set `markdown_generator` to your custom generator.
            4.  Crucially, within your custom generator's `generate_markdown` method, ensure you *first* apply the `content_filter` (passed as an argument) to the `input_html` to get the `fit_html`, and then process this `fit_html` with your custom logic. Or, configure your custom generator's `content_source="fit_html"` and pass the filter during its initialization.
    *   7.4.2. *Scenario:* Using one set of `html2text_options` for `raw_markdown` and another for generating an alternative Markdown representation (perhaps for a different LLM or purpose).
        *   **How:** This would typically require two separate calls to `crawler.arun()` with different `CrawlerRunConfig` objects, each specifying a `DefaultMarkdownGenerator` with different `options`. Alternatively, a custom `MarkdownGenerationStrategy` could internally generate multiple Markdown versions with different settings and include them in custom fields within `MarkdownGenerationResult` (though this would require modifying or extending `MarkdownGenerationResult`).

## 8. Troubleshooting Common Markdown Generation Issues

*   8.1. **Problem: Markdown is too noisy / includes boilerplate**
    *   8.1.1. **Solutions:**
        *   **Use a `RelevantContentFilter`**:
            *   Start with `PruningContentFilter`. It's fast and good for common boilerplate.
                ```python
                # from crawl4ai.content_filter_strategy import PruningContentFilter
                # from crawl4ai import DefaultMarkdownGenerator
                # md_generator = DefaultMarkdownGenerator(content_filter=PruningContentFilter(threshold=0.5))
                ```
            *   If more precision is needed, try `BM25ContentFilter` with a relevant query or `LLMContentFilter` with clear instructions.
        *   **Refine `excluded_tags` or `excluded_selector` in `CrawlerRunConfig`**: This removes elements *before* any Markdown strategy sees them.
            ```python
            # run_config = CrawlerRunConfig(
            #     excluded_tags=["nav", "footer", "aside", "script"],
            #     excluded_selector=".ad-banner, #social-links"
            # )
            ```
        *   **Adjust `html2text_options`**: Options like `ignore_links`, `ignore_images`, `skip_internal_links` can reduce clutter.
            ```python
            # from crawl4ai import DefaultMarkdownGenerator
            # md_generator = DefaultMarkdownGenerator(options={"ignore_images": True, "ignore_links": True})
            ```

*   8.2. **Problem: Important content is missing from Markdown**
    *   8.2.1. **Solutions:**
        *   **Check if `content_filter` is too aggressive**: If using a filter, try lowering its threshold (e.g., `bm25_threshold` for `BM25ContentFilter`) or simplifying instructions for `LLMContentFilter`. Temporarily disable the filter to see if the content appears in `raw_markdown`.
        *   **Ensure `word_count_threshold` in `CrawlerRunConfig` (or scraping strategy) is not too high**: The default `WebScrapingStrategy` might have its own cleaning. If `CrawlerRunConfig.word_count_threshold` is too high, it might remove short but important paragraphs.
        *   **Verify `html2text_options` are not inadvertently removing desired content**: For example, if `ignore_links=True` is set, link text itself might still be there, but the link URL will be gone.
        *   **Examine `cleaned_html` or `fit_html`**: Inspect `result.markdown.fit_html` (if a filter was used) or `result.cleaned_html` (if no filter and `content_source` was `cleaned_html`). If the content is missing here, the issue is with HTML cleaning or filtering, not the Markdown conversion itself. If it's present in these HTML versions but not in the final Markdown, the issue is likely with `html2text_options` or the conversion process.

*   8.3. **Problem: Tables are mangled or poorly formatted**
    *   8.3.1. **Solutions:**
        *   **Try `html2text_options={'bypass_tables': True}`**: This tells `html2text` to skip converting tables.
            ```python
            # from crawl4ai import DefaultMarkdownGenerator
            # md_generator = DefaultMarkdownGenerator(options={"bypass_tables": True})
            # run_config = CrawlerRunConfig(markdown_generator=md_generator)
            # result = await crawler.arun(...)
            # # Now result.markdown.raw_markdown will not have Markdown tables.
            # # You'd need to parse tables from result.cleaned_html or result.markdown.fit_html
            ```
            You can then extract the table HTML directly from `result.cleaned_html` (or `result.markdown.fit_html`) using BeautifulSoup or lxml and parse it with a library better suited for complex tables (e.g., pandas `read_html`, or a custom parser).
        *   **Experiment with other `html2text` table formatting options**: Options like `pad_tables` might slightly improve appearance, but won't fix fundamentally complex table structures.
        *   **Consider if the table is truly a data table or a layout table**: Layout tables are often problematic for Markdown conversion and should ideally be filtered out by `PruningContentFilter` or more aggressive cleaning.

*   8.4. **Problem: Citations or references are incorrect/missing**
    *   8.4.1. **Solutions:**
        *   **Ensure links are present in the HTML input to `DefaultMarkdownGenerator`**: If the links were removed during an earlier HTML cleaning stage (e.g., by an aggressive `ContentScrapingStrategy` or `excluded_tags`), they can't be converted to citations.
        *   **Verify `ignore_links` is not `True` in `html2text_options`**: `DefaultMarkdownGenerator` relies on `CustomHTML2Text` to see the links to convert them. If `ignore_links=True`, the links are stripped before citation processing can occur.
        *   **Check for unusual link structures in the HTML**: Very non-standard link formats (e.g., heavily JavaScript-driven links without `href` attributes) might not be picked up. `CustomHTML2Text` primarily looks for standard `<a href="...">` tags.

*   8.5. **Problem: Markdown formatting is not ideal for a specific LLM**
    *   8.5.1. **Solutions:**
        *   **Fine-tune `html2text_options` extensively**: This is the first line of defense. Experiment with all available options (see Section 6.2) to control aspects like heading styles, list formatting, code block rendering, etc.
        *   **Consider a custom `MarkdownGenerationStrategy`**: If `html2text` options are insufficient, you might need to build your own strategy, possibly using a different Markdown conversion library or implementing custom transformation logic (see Section 2.1.3).
        *   **Implement post-processing steps**: After getting the Markdown from `MarkdownGenerationResult`, apply your own Python scripts (e.g., using regex) to further refine the formatting (see Section 7.3.2).

*   8.6. **Debugging Workflow**
    *   8.6.1. **Start with `raw_html` from `CrawlResult`**: `print(result.html)` This is the very first HTML fetched, before any processing. Is your target content even here?
    *   8.6.2. **Examine `cleaned_html` (or `fit_html`)**:
        *   If no content filter is used in `MarkdownGenerationStrategy`, inspect `result.cleaned_html`. This is what `DefaultMarkdownGenerator` (with `content_source="cleaned_html"`) will use.
        *   If a content filter *is* used, inspect `result.markdown.fit_html`. This is what `DefaultMarkdownGenerator` will use to produce `fit_markdown`.
        *   Is your target content present in these intermediate HTML stages?
    *   8.6.3. **Isolate the issue**:
        *   **HTML Cleaning/Scraping:** If content is missing from `cleaned_html` (but present in `raw_html`), the issue lies with the `ContentScrapingStrategy` or `CrawlerRunConfig` parameters like `excluded_tags`, `css_selector`, `target_elements`.
        *   **Content Filtering:** If content is in `cleaned_html` but missing from `fit_html`, the issue is with your `RelevantContentFilter` configuration.
        *   **Markdown Conversion:** If content is in `cleaned_html`/`fit_html` but malformed or missing in the final Markdown fields (`raw_markdown`, `fit_markdown`), the issue is likely with `html2text_options` or the `CustomHTML2Text` conversion process.
    *   8.6.4. **Use `verbose=True` in relevant configs**: Set `verbose=True` in `BrowserConfig` and `CrawlerRunConfig` for more detailed logging output from Crawl4AI, which can provide clues.

## 9. Conclusion and Next Steps

*   9.1. Recap of key strategies for effective Markdown generation.
    *   **Summary:** Crawl4AI provides a flexible Markdown generation pipeline. Start with `DefaultMarkdownGenerator`. Use `html2text_options` for stylistic control. Employ `RelevantContentFilter` strategies (`PruningContentFilter`, `BM25ContentFilter`, `LLMContentFilter`) to create focused `fit_markdown` for LLMs. Choose the appropriate `content_source` based on your needs. For highly custom requirements, implement your own `MarkdownGenerationStrategy`.
*   9.2. Pointers to other relevant documentation sections (e.g., `RelevantContentFilter` deep dive, `CustomHTML2Text` options in API reference).
    *   **Suggestion:** For a detailed breakdown of each `RelevantContentFilter`, see the "Content Filtering Strategies" guide. For an exhaustive list of `html2text` options, refer to the `CustomHTML2Text` API documentation or the original `html2text` library's documentation.
*   9.3. Encouragement for experimentation and community contributions.
    *   **Call to Action:** The best way to master Markdown generation is to experiment with different configurations and content types. If you develop useful custom strategies or identify improvements, consider contributing them back to the Crawl4AI community!

---
```

---


## Markdown Generation - Examples
Source: crawl4ai_markdown_examples_content.llm.md

# Examples Outline for crawl4ai - markdown Component

**Target Document Type:** Examples Collection
**Target Output Filename Suggestion:** `llm_examples_markdown.md`
**Library Version Context:** 0.6.3
**Outline Generation Date:** 2025-05-24
---

This document provides practical, runnable code examples for the `markdown` component of the `crawl4ai` library, focusing on the `DefaultMarkdownGenerator` and its various configurations.

## 1. Basic Markdown Generation with `DefaultMarkdownGenerator`

### 1.1. Example: Generating Markdown with default `DefaultMarkdownGenerator` settings via `AsyncWebCrawler`.
This example demonstrates the most basic usage of `DefaultMarkdownGenerator` within an `AsyncWebCrawler` run.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode

async def basic_markdown_generation_via_crawler():
    # DefaultMarkdownGenerator will be used by default if markdown_generator is not specified,
    # but we explicitly set it here for clarity.
    md_generator = DefaultMarkdownGenerator()
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS # Use BYPASS for fresh content in examples
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com", config=config)
        if result.success and result.markdown:
            print("--- Raw Markdown (First 300 chars) ---")
            print(result.markdown.raw_markdown[:300])
            print("\n--- Markdown with Citations (First 300 chars) ---")
            print(result.markdown.markdown_with_citations[:300])
            print("\n--- References Markdown ---")
            print(result.markdown.references_markdown) # example.com has no outbound links usually
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(basic_markdown_generation_via_crawler())
```
---

### 1.2. Example: Direct instantiation and use of `DefaultMarkdownGenerator`.
You can use `DefaultMarkdownGenerator` directly if you already have HTML content.

```python
from crawl4ai import DefaultMarkdownGenerator

def direct_markdown_generation():
    generator = DefaultMarkdownGenerator()
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Welcome to Example</h1>
            <p>This is a paragraph with a <a href="https://example.org/another-page">link</a>.</p>
            <p>Another paragraph follows.</p>
        </body>
    </html>
    """
    # base_url is important for resolving relative links if any, and for citation context
    result_md = generator.generate_markdown(input_html=html_content, base_url="https://example.com")

    print("--- Raw Markdown (Direct Generation) ---")
    print(result_md.raw_markdown)
    print("\n--- Markdown with Citations (Direct Generation) ---")
    print(result_md.markdown_with_citations)
    print("\n--- References Markdown (Direct Generation) ---")
    print(result_md.references_markdown)

if __name__ == "__main__":
    direct_markdown_generation()
```
---

## 2. Citation Management in Markdown

### 2.1. Example: Default citation behavior (citations enabled).
By default, `DefaultMarkdownGenerator` generates citations for links.

```python
from crawl4ai import DefaultMarkdownGenerator

def default_citation_behavior():
    generator = DefaultMarkdownGenerator()
    html_content = """
    <html><body>
        <p>Check out <a href="https://crawl4ai.com" title="Crawl4ai Homepage">Crawl4ai</a> and
        <a href="/docs">our documentation</a>.</p>
    </body></html>
    """
    result_md = generator.generate_markdown(input_html=html_content, base_url="https://example.com")

    print("--- Raw Markdown ---")
    print(result_md.raw_markdown)
    print("\n--- Markdown with Citations ---")
    print(result_md.markdown_with_citations)
    print("\n--- References Markdown ---")
    print(result_md.references_markdown)

if __name__ == "__main__":
    default_citation_behavior()
```
---

### 2.2. Example: Disabling citations in `DefaultMarkdownGenerator`.
You can disable citation generation by setting `citations=False` in the `generate_markdown` method.

```python
from crawl4ai import DefaultMarkdownGenerator

def disabling_citations():
    generator = DefaultMarkdownGenerator()
    html_content = """
    <html><body>
        <p>A link to <a href="https://anothersite.com">another site</a> will not be cited.</p>
    </body></html>
    """
    # Disable citations for this specific call
    result_md_no_citations = generator.generate_markdown(
        input_html=html_content,
        base_url="https://example.com",
        citations=False
    )

    print("--- Raw Markdown (Citations Disabled) ---")
    print(result_md_no_citations.raw_markdown)
    print("\n--- Markdown with Citations (Citations Disabled) ---")
    # This should be the same as raw_markdown when citations=False
    print(result_md_no_citations.markdown_with_citations)
    print("\n--- References Markdown (Citations Disabled) ---")
    # This should be empty or minimal
    print(result_md_no_citations.references_markdown)

    # For comparison, with citations enabled (default)
    result_md_with_citations = generator.generate_markdown(
        input_html=html_content,
        base_url="https://example.com",
        citations=True # Default
    )
    print("\n--- For Comparison: Markdown with Citations (Enabled) ---")
    print(result_md_with_citations.markdown_with_citations)
    print("\n--- For Comparison: References Markdown (Enabled) ---")
    print(result_md_with_citations.references_markdown)


if __name__ == "__main__":
    disabling_citations()
```
---

### 2.3. Example: Impact of `base_url` on citation links for relative URLs.
The `base_url` parameter is crucial for correctly resolving relative URLs in your HTML content into absolute URLs in the references.

```python
from crawl4ai import DefaultMarkdownGenerator

def base_url_impact_on_citations():
    generator = DefaultMarkdownGenerator()
    html_content = """
    <html><body>
        <p>Links: <a href="/features">Features</a>, <a href="pricing.html">Pricing</a>,
        and an absolute link to <a href="https://external.com/resource">External Resource</a>.</p>
    </body></html>
    """

    print("--- Case 1: With base_url='https://example.com/products/' ---")
    result_md_case1 = generator.generate_markdown(
        input_html=html_content,
        base_url="https://example.com/products/"
    )
    print(result_md_case1.references_markdown)

    print("\n--- Case 2: With base_url='https://another-domain.net/' ---")
    result_md_case2 = generator.generate_markdown(
        input_html=html_content,
        base_url="https://another-domain.net/"
    )
    print(result_md_case2.references_markdown)

    print("\n--- Case 3: Without base_url (relative links might be incomplete) ---")
    result_md_case3 = generator.generate_markdown(input_html=html_content)
    print(result_md_case3.references_markdown)

if __name__ == "__main__":
    base_url_impact_on_citations()
```
---

### 2.4. Example: Handling HTML with no links (empty `references_markdown`).
If the input HTML contains no hyperlinks, the `references_markdown` will be empty.

```python
from crawl4ai import DefaultMarkdownGenerator

def no_links_in_html():
    generator = DefaultMarkdownGenerator()
    html_content = "<html><body><p>This is a paragraph with no links at all.</p><b>Just some bold text.</b></body></html>"
    result_md = generator.generate_markdown(input_html=html_content, base_url="https://example.com")

    print("--- Raw Markdown ---")
    print(result_md.raw_markdown)
    print("\n--- Markdown with Citations ---")
    print(result_md.markdown_with_citations) # Should be same as raw_markdown
    print("\n--- References Markdown ---")
    print(f"'{result_md.references_markdown}'") # Should be empty or contain minimal boilerplate

if __name__ == "__main__":
    no_links_in_html()
```
---

## 3. Controlling `html2text` Conversion Options
The `DefaultMarkdownGenerator` uses the `html2text` library internally. You can pass options to `html2text` either during generator initialization (`options` parameter) or during the `generate_markdown` call (`html2text_options` parameter).

### 3.1. Example: Initializing `DefaultMarkdownGenerator` with `options` to ignore links.
This will prevent links from appearing in the Markdown output altogether (different from `citations=False` which keeps link text but omits citation markers).

```python
from crawl4ai import DefaultMarkdownGenerator

def ignore_links_option():
    # Initialize with html2text option to ignore links
    generator = DefaultMarkdownGenerator(options={"ignore_links": True})
    html_content = "<html><body><p>A link to <a href='https://example.com'>Example Site</a> and some text.</p></body></html>"
    result_md = generator.generate_markdown(input_html=html_content)

    print("--- Markdown (ignore_links=True) ---")
    print(result_md.raw_markdown) # Link text might be present or absent based on html2text behavior
    print("--- Markdown with Citations (ignore_links=True) ---")
    print(result_md.markdown_with_citations) # No citations as links are ignored
    print("--- References (ignore_links=True) ---")
    print(f"'{result_md.references_markdown}'") # Should be empty

if __name__ == "__main__":
    ignore_links_option()
```
---

### 3.2. Example: Initializing `DefaultMarkdownGenerator` with `options` to ignore images.
This will prevent image references (like `![alt text](src)`) from appearing in the Markdown.

```python
from crawl4ai import DefaultMarkdownGenerator

def ignore_images_option():
    generator = DefaultMarkdownGenerator(options={"ignore_images": True})
    html_content = "<html><body><p>An image: <img src='image.png' alt='My Test Image'></p></body></html>"
    result_md = generator.generate_markdown(input_html=html_content)

    print("--- Markdown (ignore_images=True) ---")
    print(result_md.raw_markdown) # Image markdown should be absent

if __name__ == "__main__":
    ignore_images_option()
```
---

### 3.3. Example: Initializing `DefaultMarkdownGenerator` with `options` for `body_width=0` (no line wrapping).
`body_width=0` tells `html2text` not to wrap lines.

```python
from crawl4ai import DefaultMarkdownGenerator

def no_line_wrapping_option():
    generator = DefaultMarkdownGenerator(options={"body_width": 0})
    long_text = "This is a very long line of text that would normally be wrapped by html2text. " * 5
    html_content = f"<html><body><p>{long_text}</p></body></html>"
    result_md = generator.generate_markdown(input_html=html_content)

    print("--- Markdown (body_width=0) ---")
    print(result_md.raw_markdown) # Observe the long line without soft wraps

if __name__ == "__main__":
    no_line_wrapping_option()
```
---

### 3.4. Example: Initializing `DefaultMarkdownGenerator` to disable emphasis.
This will remove formatting for `<em>` and `<strong>` tags.

```python
from crawl4ai import DefaultMarkdownGenerator

def ignore_emphasis_option():
    generator = DefaultMarkdownGenerator(options={"ignore_emphasis": True})
    html_content = "<html><body><p>Normal, <em>emphasized</em>, and <strong>strongly emphasized</strong> text.</p></body></html>"
    result_md = generator.generate_markdown(input_html=html_content)

    print("--- Markdown (ignore_emphasis=True) ---")
    print(result_md.raw_markdown) # Emphasis should be gone

if __name__ == "__main__":
    ignore_emphasis_option()
```
---

### 3.5. Example: Overriding `html2text_options` at `generate_markdown` call time.
Options passed to `generate_markdown` via `html2text_options` take precedence.

```python
from crawl4ai import DefaultMarkdownGenerator

def override_html2text_options():
    # Initial generator might have some defaults
    generator = DefaultMarkdownGenerator(options={"ignore_links": False})
    html_content = "<html><body><p>Link: <a href='https://example.com'>Example</a>.</p></body></html>"

    # Override at call time to protect links
    result_md = generator.generate_markdown(
        input_html=html_content,
        html2text_options={"protect_links": True} # Links will be <URL>
    )

    print("--- Markdown (protect_links=True via call-time override) ---")
    print(result_md.raw_markdown)

if __name__ == "__main__":
    override_html2text_options()
```
---

### 3.6. Example: Combining multiple `html2text` options.
Multiple options can be combined for fine-grained control over the Markdown output.

```python
from crawl4ai import DefaultMarkdownGenerator

def combined_html2text_options():
    generator = DefaultMarkdownGenerator(options={
        "ignore_links": True,
        "ignore_images": True,
        "body_width": 60  # Wrap at 60 characters
    })
    html_content = """
    <html><body>
        <p>This is a paragraph with a <a href='https://example.com'>link to ignore</a> and an
        <img src='image.png' alt='image to ignore'>. It also has some long text to demonstrate wrapping.
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        </p>
    </body></html>
    """
    result_md = generator.generate_markdown(input_html=html_content)

    print("--- Markdown (Combined Options: ignore_links, ignore_images, body_width=60) ---")
    print(result_md.raw_markdown)

if __name__ == "__main__":
    combined_html2text_options()
```
---

## 4. Selecting the HTML Content Source for Markdown Generation
The `DefaultMarkdownGenerator` can generate Markdown from different HTML sources within the `CrawlResult`.

### 4.1. Example: Markdown from `cleaned_html` (default `content_source`).
This is the default behavior. `cleaned_html` is the HTML after `WebScrapingStrategy` (e.g., `LXMLWebScrapingStrategy`) has processed it.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode

async def markdown_from_cleaned_html():
    # Default content_source is "cleaned_html"
    md_generator = DefaultMarkdownGenerator()
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        # Using a more complex page to see the effect of cleaning
        result = await crawler.arun(url="https://news.ycombinator.com", config=config)
        if result.success and result.markdown:
            print("--- Markdown from Cleaned HTML (Default - First 300 chars) ---")
            print(result.markdown.raw_markdown[:300])
            # For comparison, show a snippet of cleaned_html
            print("\n--- Cleaned HTML (Source - First 300 chars) ---")
            print(result.cleaned_html[:300])
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(markdown_from_cleaned_html())
```
---

### 4.2. Example: Markdown from `raw_html`.
This example uses the original, unprocessed HTML fetched from the URL as the source for Markdown generation.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode

async def markdown_from_raw_html():
    md_generator = DefaultMarkdownGenerator(content_source="raw_html")
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com", config=config)
        if result.success and result.markdown:
            print("--- Markdown from Raw HTML (First 300 chars) ---")
            print(result.markdown.raw_markdown[:300])
            print("\n--- Raw Page HTML (Source - First 300 chars for comparison) ---")
            print(result.html[:300]) # result.html contains the raw HTML
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(markdown_from_raw_html())
```
---

### 4.3. Example: Markdown from `fit_html` (requires a `ContentFilterStrategy`).
`fit_html` is the HTML content after a `ContentFilterStrategy` (like `PruningContentFilter`) has processed it.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter

async def markdown_from_fit_html():
    # A content filter must run to produce fit_html
    pruning_filter = PruningContentFilter()
    md_generator = DefaultMarkdownGenerator(
        content_filter=pruning_filter,
        content_source="fit_html" # Explicitly use the output of the filter
    )
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        # Using a news site which PruningContentFilter can work on
        result = await crawler.arun(url="https://news.ycombinator.com", config=config)
        if result.success and result.markdown:
            print("--- Markdown from Fit HTML (Output of PruningFilter - First 300 chars) ---")
            # When content_source="fit_html", result.markdown.raw_markdown IS from fit_html
            print(result.markdown.raw_markdown[:300])
            print("\n--- Fit HTML itself (Source - First 300 chars for comparison) ---")
            print(result.markdown.fit_html[:300])
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(markdown_from_fit_html())
```
---

## 5. Integration with Content Filters
`DefaultMarkdownGenerator` can work in conjunction with `ContentFilterStrategy` instances. If a filter is provided, it will produce `fit_html` and `fit_markdown`.

### 5.1. Example: `DefaultMarkdownGenerator` with `PruningContentFilter`.
The `PruningContentFilter` attempts to remove boilerplate and keep main content.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter

async def md_with_pruning_filter():
    pruning_filter = PruningContentFilter()
    # By default, raw_markdown is from cleaned_html, fit_markdown is from fit_html
    md_generator = DefaultMarkdownGenerator(content_filter=pruning_filter)
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://news.ycombinator.com", config=config)
        if result.success and result.markdown:
            print("--- Raw Markdown (from cleaned_html - First 200 chars) ---")
            print(result.markdown.raw_markdown[:200])
            print("\n--- Fit Markdown (from PruningFilter's fit_html - First 200 chars) ---")
            print(result.markdown.fit_markdown[:200])
            print("\n--- Fit HTML (Source for Fit Markdown - First 200 chars) ---")
            print(result.markdown.fit_html[:200])
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(md_with_pruning_filter())
```
---

### 5.2. Example: `DefaultMarkdownGenerator` with `BM25ContentFilter`.
`BM25ContentFilter` filters content based on relevance to a user query.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode
from crawl4ai.content_filter_strategy import BM25ContentFilter

async def md_with_bm25_filter():
    bm25_filter = BM25ContentFilter(user_query="Python programming language features")
    md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        # Using a relevant page for the query
        result = await crawler.arun(url="https://docs.python.org/3/tutorial/classes.html", config=config)
        if result.success and result.markdown:
            print("--- Fit Markdown (from BM25Filter - First 300 chars) ---")
            print(result.markdown.fit_markdown[:300])
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(md_with_bm25_filter())
```
---

### 5.3. Example: `DefaultMarkdownGenerator` with `LLMContentFilter`.
`LLMContentFilter` uses an LLM to intelligently filter or summarize content based on instructions. (Requires API Key)

```python
import asyncio
import os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, LLMConfig, CacheMode
from crawl4ai.content_filter_strategy import LLMContentFilter

async def md_with_llm_filter():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("OPENAI_API_KEY not found. Skipping LLMContentFilter example.")
        return

    llm_config = LLMConfig(api_token=openai_api_key, provider="openai/gpt-3.5-turbo")
    llm_filter = LLMContentFilter(
        llm_config=llm_config,
        instruction="Summarize the main arguments presented in this Hacker News discussion thread."
    )
    md_generator = DefaultMarkdownGenerator(content_filter=llm_filter)
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS # Fresh run for LLM
    )

    async with AsyncWebCrawler() as crawler:
        # Example Hacker News discussion
        result = await crawler.arun(url="https://news.ycombinator.com/item?id=39000000", config=config) # A past popular item
        if result.success and result.markdown:
            print("--- Fit Markdown (from LLMContentFilter - First 500 chars) ---")
            print(result.markdown.fit_markdown[:500])
            llm_filter.show_usage() # Show token usage
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(md_with_llm_filter())
```
---

### 5.4. Example: Forcing Markdown generation from `fit_html` when a filter is active.
This example shows how to ensure the `raw_markdown` itself is generated from the `fit_html` (output of the filter) rather than `cleaned_html`.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter

async def md_forced_from_fit_html():
    pruning_filter = PruningContentFilter()
    # Explicitly set content_source to "fit_html"
    md_generator = DefaultMarkdownGenerator(
        content_filter=pruning_filter,
        content_source="fit_html"
    )
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://news.ycombinator.com", config=config)
        if result.success and result.markdown:
            print("--- Raw Markdown (forced from fit_html - First 300 chars) ---")
            # This raw_markdown is now generated from the output of PruningFilter
            print(result.markdown.raw_markdown[:300])
            print("\n--- Fit HTML (Source for Raw Markdown - First 300 chars) ---")
            print(result.markdown.fit_html[:300])
            print("\n--- Fit Markdown (should be same as Raw Markdown here - First 300 chars) ---")
            print(result.markdown.fit_markdown[:300])
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(md_forced_from_fit_html())
```
---

### 5.5. Example: Markdown generation when no filter is active.
If no `content_filter` is provided to `DefaultMarkdownGenerator`, `fit_markdown` and `fit_html` will be empty or None.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode

async def md_no_filter():
    md_generator = DefaultMarkdownGenerator() # No filter provided
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com", config=config)
        if result.success and result.markdown:
            print("--- Raw Markdown (First 300 chars) ---")
            print(result.markdown.raw_markdown[:300])
            print("\n--- Fit Markdown (Expected: None or empty) ---")
            print(result.markdown.fit_markdown)
            print("\n--- Fit HTML (Expected: None or empty) ---")
            print(result.markdown.fit_html)
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(md_no_filter())
```
---

## 6. Understanding `MarkdownGenerationResult` Output Fields

### 6.1. Example: Accessing all fields of `MarkdownGenerationResult`.
This example demonstrates how to access all the different Markdown and HTML outputs available in the `MarkdownGenerationResult` object.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter # Using a filter to populate fit_html/fit_markdown

async def access_all_markdown_fields():
    # Setup with a filter to ensure fit_html and fit_markdown are generated
    content_filter = PruningContentFilter()
    md_generator = DefaultMarkdownGenerator(
        content_filter=content_filter,
        content_source="cleaned_html" # raw_markdown will be from cleaned_html
    )
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        # Using a content-rich page
        result = await crawler.arun(url="https://en.wikipedia.org/wiki/Python_(programming_language)", config=config)
        if result.success and result.markdown:
            md_result = result.markdown

            print("--- Accessing MarkdownGenerationResult Fields ---")

            print(f"\n1. Raw Markdown (from '{md_generator.content_source}' - snippet):")
            print(md_result.raw_markdown[:300] + "...")

            print(f"\n2. Markdown with Citations (snippet):")
            print(md_result.markdown_with_citations[:300] + "...")

            print(f"\n3. References Markdown (snippet):")
            print(md_result.references_markdown[:200] + "...")

            print(f"\n4. Fit HTML (from ContentFilter - snippet):")
            if md_result.fit_html:
                print(md_result.fit_html[:300] + "...")
            else:
                print("None (No filter or filter produced no output)")

            print(f"\n5. Fit Markdown (from fit_html - snippet):")
            if md_result.fit_markdown:
                print(md_result.fit_markdown[:300] + "...")
            else:
                print("None (No filter or filter produced no output)")
        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(access_all_markdown_fields())
```
---

## 7. Advanced and Specific Scenarios

### 7.1. Example: Handling HTML with complex table structures.
`DefaultMarkdownGenerator` (via `html2text`) attempts to render HTML tables into Markdown tables.

```python
from crawl4ai import DefaultMarkdownGenerator

def markdown_for_tables():
    generator = DefaultMarkdownGenerator()
    html_content = """
    <html><body>
        <h3>Product Comparison</h3>
        <table>
            <thead>
                <tr><th>Feature</th><th>Product A</th><th>Product B</th></tr>
            </thead>
            <tbody>
                <tr><td>Price</td><td>$100</td><td>$120</td></tr>
                <tr><td>Rating</td><td>4.5 stars</td><td>4.2 stars</td></tr>
                <tr><td>Multi-row<br/>Feature</td><td colspan="2">Supported by Both</td></tr>
            </tbody>
        </table>
    </body></html>
    """
    result_md = generator.generate_markdown(input_html=html_content)

    print("--- Markdown for Table ---")
    print(result_md.raw_markdown)

if __name__ == "__main__":
    markdown_for_tables()
```
---

### 7.2. Example: Handling HTML with code blocks.
Code blocks are generally preserved in Markdown format.

```python
from crawl4ai import DefaultMarkdownGenerator

def markdown_for_code_blocks():
    generator = DefaultMarkdownGenerator()
    html_content = """
    <html><body>
        <p>Here is some Python code:</p>
        <pre><code class="language-python">
def greet(name):
    print(f"Hello, {name}!")

greet("World")
        </code></pre>
        <p>And an inline <code>example_function()</code>.</p>
    </body></html>
    """
    result_md = generator.generate_markdown(input_html=html_content)

    print("--- Markdown for Code Blocks ---")
    print(result_md.raw_markdown)

if __name__ == "__main__":
    markdown_for_code_blocks()
```
---

### 7.3. Example: Using a custom `MarkdownGenerationStrategy` (conceptual).
You can create your own Markdown generation logic by subclassing `MarkdownGenerationStrategy`.

```python
import asyncio
from crawl4ai import (
    AsyncWebCrawler, CrawlerRunConfig, CacheMode,
    MarkdownGenerationStrategy, MarkdownGenerationResult
)

# Define a minimal custom Markdown generator
class CustomMarkdownGenerator(MarkdownGenerationStrategy):
    def __init__(self, prefix="CUSTOM MD: ", **kwargs):
        super().__init__(**kwargs) # Pass along any other options
        self.prefix = prefix

    def generate_markdown(
        self,
        input_html: str,
        base_url: str = "",
        html2text_options: dict = None, # Can be used by html2text
        citations: bool = True, # Standard param
        **kwargs # For other potential strategy-specific params
    ) -> MarkdownGenerationResult:
        # Simplified custom logic: just prefix and take a snippet
        # A real custom generator would do more sophisticated parsing/conversion
        custom_raw_md = self.prefix + input_html[:100].strip() + "..."

        # For simplicity, we'll just return the custom raw markdown for all fields
        return MarkdownGenerationResult(
            raw_markdown=custom_raw_md,
            markdown_with_citations=custom_raw_md, # No real citation logic here
            references_markdown="",
            fit_markdown=None, # Not implementing filtering here
            fit_html=None
        )

async def use_custom_markdown_generator():
    custom_generator = CustomMarkdownGenerator(prefix="[MyGenerator Says]: ")
    config = CrawlerRunConfig(
        markdown_generator=custom_generator,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com", config=config)
        if result.success and result.markdown:
            print("--- Output from CustomMarkdownGenerator ---")
            print(result.markdown.raw_markdown)
            # Since our custom generator doesn't really do citations or filtering:
            print(f"Citations: '{result.markdown.markdown_with_citations}'")
            print(f"References: '{result.markdown.references_markdown}'")
            print(f"Fit Markdown: '{result.markdown.fit_markdown}'")

        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(use_custom_markdown_generator())
```
---
**End of Examples Document**
```

---

