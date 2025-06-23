"""
Tests for URL cleaning and normalization functionality
"""
import pytest
from app.services.url_utils import URLCleaner, clean_url, normalize_url, detect_invisible_characters


class TestURLCleaning:
    """Test URL cleaning functionality"""
    
    def test_clean_basic_url(self):
        """Test cleaning of basic URL without invisible characters"""
        url = "https://example.com/page"
        cleaned = clean_url(url)
        assert cleaned == url
        assert len(cleaned) == len(url)
    
    def test_clean_url_with_word_joiner(self):
        """Test cleaning URL with WORD JOINER character (U+2060)"""
        url = "https://example.com/page\u2060/subpage"
        cleaned = clean_url(url)
        expected = "https://example.com/page/subpage"
        assert cleaned == expected
        assert len(cleaned) == len(url) - 1  # Should be one character shorter
    
    def test_clean_url_with_zero_width_space(self):
        """Test cleaning URL with ZERO WIDTH SPACE (U+200B)"""
        url = "https://example.com/page\u200B/subpage"
        cleaned = clean_url(url)
        expected = "https://example.com/page/subpage"
        assert cleaned == expected
    
    def test_clean_url_with_multiple_invisible_chars(self):
        """Test cleaning URL with multiple invisible characters"""
        url = "https://example.com/page\u2060\u200B\u200C/subpage"
        cleaned = clean_url(url)
        expected = "https://example.com/page/subpage"
        assert cleaned == expected
        assert len(cleaned) == len(url) - 3  # Should be three characters shorter
    
    def test_clean_url_with_invisible_chars_at_end(self):
        """Test cleaning URL with invisible characters at the end"""
        url = "https://example.com/page\u2060"
        cleaned = clean_url(url)
        expected = "https://example.com/page"
        assert cleaned == expected
    
    def test_clean_url_with_invisible_chars_at_beginning(self):
        """Test cleaning URL with invisible characters at the beginning"""
        url = "\u2060https://example.com/page"
        cleaned = clean_url(url)
        expected = "https://example.com/page"
        assert cleaned == expected
    
    def test_clean_url_with_bom_character(self):
        """Test cleaning URL with BOM character (U+FEFF)"""
        url = "https://example.com/page\uFEFF/subpage"
        cleaned = clean_url(url)
        expected = "https://example.com/page/subpage"
        assert cleaned == expected
    
    def test_clean_empty_url(self):
        """Test cleaning empty or None URL"""
        assert clean_url("") == ""
        assert clean_url(None) == ""
    
    def test_clean_url_with_query_params(self):
        """Test cleaning URL with query parameters containing invisible chars"""
        url = "https://example.com/page?param=value\u2060&other=test"
        cleaned = clean_url(url)
        expected = "https://example.com/page?param=value&other=test"
        assert cleaned == expected


class TestURLNormalization:
    """Test URL normalization functionality"""
    
    def test_normalize_basic_url(self):
        """Test normalization of basic URL"""
        url = "https://example.com/page"
        normalized = normalize_url(url)
        assert normalized == url
    
    def test_normalize_url_with_invisible_chars(self):
        """Test normalization removes invisible characters"""
        url = "https://example.com/page\u2060/subpage"
        normalized = normalize_url(url)
        expected = "https://example.com/page/subpage"
        assert normalized == expected
    
    def test_normalize_url_case_sensitivity(self):
        """Test normalization handles case sensitivity correctly"""
        url = "HTTPS://EXAMPLE.COM/page"
        normalized = normalize_url(url)
        expected = "https://example.com/page"
        assert normalized == expected
    
    def test_normalize_url_with_default_port(self):
        """Test normalization removes default ports"""
        url = "https://example.com:443/page"
        normalized = normalize_url(url)
        expected = "https://example.com/page"
        assert normalized == expected
        
        url = "http://example.com:80/page"
        normalized = normalize_url(url)
        expected = "http://example.com/page"
        assert normalized == expected


class TestInvisibleCharacterDetection:
    """Test invisible character detection functionality"""
    
    def test_detect_no_invisible_characters(self):
        """Test detection when no invisible characters are present"""
        url = "https://example.com/page"
        detection = detect_invisible_characters(url)
        assert detection['has_invisible'] is False
        assert len(detection['characters']) == 0
        assert len(detection['positions']) == 0
    
    def test_detect_word_joiner(self):
        """Test detection of WORD JOINER character"""
        url = "https://example.com/page\u2060/subpage"
        detection = detect_invisible_characters(url)
        assert detection['has_invisible'] is True
        assert len(detection['characters']) == 1
        assert detection['characters'][0]['unicode_code'] == 'U+2060'
        assert detection['positions'] == [24]
    
    def test_detect_multiple_invisible_characters(self):
        """Test detection of multiple invisible characters"""
        url = "https://example.com/page\u2060\u200B/subpage"
        detection = detect_invisible_characters(url)
        assert detection['has_invisible'] is True
        assert len(detection['characters']) == 2
        assert detection['positions'] == [24, 25]
    
    def test_detect_empty_url(self):
        """Test detection on empty URL"""
        detection = detect_invisible_characters("")
        assert detection['has_invisible'] is False
        assert len(detection['characters']) == 0


class TestHTMLURLExtraction:
    """Test URL extraction from HTML with cleaning"""
    
    def test_extract_clean_urls_from_html(self):
        """Test extraction and cleaning of URLs from HTML"""
        html = '''
        <html>
        <head>
            <link rel="stylesheet" href="https://example.com/styles\u2060.css">
        </head>
        <body>
            <a href="https://example.com/link\u200B/page">Link</a>
            <img src="https://example.com/image\u2060.jpg" alt="Image">
            <script src="https://example.com/script\u200B.js"></script>
        </body>
        </html>
        '''
        
        extracted = URLCleaner.extract_clean_urls_from_html(html)
        
        # All URLs should be cleaned of invisible characters
        assert "https://example.com/styles.css" in extracted['css']
        assert "https://example.com/link/page" in extracted['links']
        assert "https://example.com/image.jpg" in extracted['images']
        assert "https://example.com/script.js" in extracted['js']
        
        # Verify no invisible characters remain
        for url_list in extracted.values():
            for url in url_list:
                detection = detect_invisible_characters(url)
                assert not detection['has_invisible'], f"URL still has invisible chars: {url}"
    
    def test_extract_from_empty_html(self):
        """Test extraction from empty HTML"""
        extracted = URLCleaner.extract_clean_urls_from_html("")
        assert extracted == {'links': [], 'images': [], 'css': [], 'js': []}
        
        extracted = URLCleaner.extract_clean_urls_from_html(None)
        assert extracted == {'links': [], 'images': [], 'css': [], 'js': []}