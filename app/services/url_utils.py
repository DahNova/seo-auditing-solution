"""
URL Utilities for SEO Auditing
Handles URL cleaning, normalization, and invisible character removal
"""
import re
import urllib.parse
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse


class URLCleaner:
    """Comprehensive URL cleaning utility for SEO auditing platform"""
    
    # Comprehensive list of invisible Unicode characters that can cause issues
    INVISIBLE_CHARS = [
        '\u200B',  # ZERO WIDTH SPACE
        '\u200C',  # ZERO WIDTH NON-JOINER
        '\u200D',  # ZERO WIDTH JOINER
        '\u200E',  # LEFT-TO-RIGHT MARK
        '\u200F',  # RIGHT-TO-LEFT MARK
        '\u2060',  # WORD JOINER (the main culprit in our logs)
        '\u2061',  # FUNCTION APPLICATION
        '\u2062',  # INVISIBLE TIMES
        '\u2063',  # INVISIBLE SEPARATOR
        '\u2064',  # INVISIBLE PLUS
        '\u2066',  # LEFT-TO-RIGHT ISOLATE
        '\u2067',  # RIGHT-TO-LEFT ISOLATE
        '\u2068',  # FIRST STRONG ISOLATE
        '\u2069',  # POP DIRECTIONAL ISOLATE
        '\u206A',  # INHIBIT SYMMETRIC SWAPPING
        '\u206B',  # ACTIVATE SYMMETRIC SWAPPING
        '\u206C',  # INHIBIT ARABIC FORM SHAPING
        '\u206D',  # ACTIVATE ARABIC FORM SHAPING
        '\u206E',  # NATIONAL DIGIT SHAPES
        '\u206F',  # NOMINAL DIGIT SHAPES
        '\uFEFF',  # ZERO WIDTH NO-BREAK SPACE (BOM)
        '\u00AD',  # SOFT HYPHEN
        '\u034F',  # COMBINING GRAPHEME JOINER
    ]
    
    @classmethod
    def clean_url(cls, url: str) -> str:
        """
        Clean a URL by removing invisible characters and normalizing
        
        Args:
            url: The URL to clean
            
        Returns:
            Cleaned and normalized URL
        """
        if not url:
            return ""
            
        # Remove invisible characters
        cleaned_url = url
        for char in cls.INVISIBLE_CHARS:
            cleaned_url = cleaned_url.replace(char, '')
        
        # Strip whitespace
        cleaned_url = cleaned_url.strip()
        
        # Basic URL validation and normalization
        if cleaned_url:
            try:
                # Parse and reconstruct to normalize
                parsed = urlparse(cleaned_url)
                if parsed.scheme and parsed.netloc:
                    # Reconstruct normalized URL
                    cleaned_url = urlunparse(parsed)
            except Exception:
                # If parsing fails, return cleaned string as-is
                pass
                
        return cleaned_url
    
    @classmethod
    def clean_url_list(cls, urls: List[str]) -> List[str]:
        """
        Clean a list of URLs
        
        Args:
            urls: List of URLs to clean
            
        Returns:
            List of cleaned URLs with duplicates removed
        """
        if not urls:
            return []
            
        cleaned_urls = []
        seen_urls = set()
        
        for url in urls:
            cleaned = cls.clean_url(url)
            if cleaned and cleaned not in seen_urls:
                cleaned_urls.append(cleaned)
                seen_urls.add(cleaned)
                
        return cleaned_urls
    
    @classmethod
    def extract_urls_from_html(cls, html_content: str, base_url: Optional[str] = None) -> List[str]:
        """
        Extract and clean URLs from HTML content
        
        Args:
            html_content: HTML content to extract URLs from
            base_url: Base URL for resolving relative URLs
            
        Returns:
            List of cleaned and normalized URLs
        """
        if not html_content:
            return []
            
        # Simple regex patterns for common URL attributes
        url_patterns = [
            r'href\s*=\s*["\']([^"\']+)["\']',
            r'src\s*=\s*["\']([^"\']+)["\']',
            r'action\s*=\s*["\']([^"\']+)["\']',
            r'content\s*=\s*["\']([^"\']*(?:https?://[^"\']+)[^"\']*)["\']',
        ]
        
        found_urls = set()
        
        for pattern in url_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                # Clean the URL
                cleaned = cls.clean_url(match)
                if cleaned:
                    # Resolve relative URLs if base_url provided
                    if base_url and not urlparse(cleaned).scheme:
                        try:
                            cleaned = urljoin(base_url, cleaned)
                        except Exception:
                            continue
                    
                    # Only include HTTP/HTTPS URLs
                    parsed = urlparse(cleaned)
                    if parsed.scheme in ('http', 'https'):
                        found_urls.add(cleaned)
        
        return list(found_urls)
    
    @classmethod
    def has_invisible_characters(cls, url: str) -> bool:
        """
        Check if URL contains invisible characters
        
        Args:
            url: URL to check
            
        Returns:
            True if invisible characters are found
        """
        if not url:
            return False
            
        return any(char in url for char in cls.INVISIBLE_CHARS)
    
    @classmethod
    def get_invisible_characters_in_url(cls, url: str) -> Set[str]:
        """
        Get set of invisible characters found in URL
        
        Args:
            url: URL to analyze
            
        Returns:
            Set of invisible characters found
        """
        if not url:
            return set()
            
        found_chars = set()
        for char in cls.INVISIBLE_CHARS:
            if char in url:
                found_chars.add(char)
                
        return found_chars
    
    @classmethod
    def debug_url_characters(cls, url: str) -> dict:
        """
        Debug utility to analyze URL characters
        
        Args:
            url: URL to debug
            
        Returns:
            Dictionary with debug information
        """
        if not url:
            return {"url": "", "length": 0, "invisible_chars": [], "cleaned_url": ""}
            
        invisible_chars = cls.get_invisible_characters_in_url(url)
        cleaned = cls.clean_url(url)
        
        return {
            "original_url": url,
            "original_length": len(url),
            "cleaned_url": cleaned,
            "cleaned_length": len(cleaned),
            "has_invisible_chars": bool(invisible_chars),
            "invisible_chars_found": [
                {
                    "char": char,
                    "unicode": f"U+{ord(char):04X}",
                    "name": cls._get_unicode_name(char),
                    "count": url.count(char)
                }
                for char in invisible_chars
            ],
            "characters_removed": len(url) - len(cleaned)
        }
    
    @classmethod
    def _get_unicode_name(cls, char: str) -> str:
        """Get Unicode character name for debugging"""
        names = {
            '\u200B': 'ZERO WIDTH SPACE',
            '\u200C': 'ZERO WIDTH NON-JOINER',
            '\u200D': 'ZERO WIDTH JOINER',
            '\u200E': 'LEFT-TO-RIGHT MARK',
            '\u200F': 'RIGHT-TO-LEFT MARK',
            '\u2060': 'WORD JOINER',
            '\u2061': 'FUNCTION APPLICATION',
            '\u2062': 'INVISIBLE TIMES',
            '\u2063': 'INVISIBLE SEPARATOR',
            '\u2064': 'INVISIBLE PLUS',
            '\u2066': 'LEFT-TO-RIGHT ISOLATE',
            '\u2067': 'RIGHT-TO-LEFT ISOLATE',
            '\u2068': 'FIRST STRONG ISOLATE',
            '\u2069': 'POP DIRECTIONAL ISOLATE',
            '\u206A': 'INHIBIT SYMMETRIC SWAPPING',
            '\u206B': 'ACTIVATE SYMMETRIC SWAPPING',
            '\u206C': 'INHIBIT ARABIC FORM SHAPING',
            '\u206D': 'ACTIVATE ARABIC FORM SHAPING',
            '\u206E': 'NATIONAL DIGIT SHAPES',
            '\u206F': 'NOMINAL DIGIT SHAPES',
            '\uFEFF': 'ZERO WIDTH NO-BREAK SPACE (BOM)',
            '\u00AD': 'SOFT HYPHEN',
            '\u034F': 'COMBINING GRAPHEME JOINER',
        }
        return names.get(char, f'UNKNOWN_U+{ord(char):04X}')


# Convenience functions for easy import
def clean_url(url: str) -> str:
    """Convenience function to clean a single URL"""
    return URLCleaner.clean_url(url)


def clean_urls(urls: List[str]) -> List[str]:
    """Convenience function to clean a list of URLs"""
    return URLCleaner.clean_url_list(urls)


def has_invisible_chars(url: str) -> bool:
    """Convenience function to check for invisible characters"""
    return URLCleaner.has_invisible_characters(url)


def debug_url(url: str) -> dict:
    """Convenience function to debug URL characters"""
    return URLCleaner.debug_url_characters(url)


def normalize_url(url: str) -> str:
    """Convenience function to normalize URL (alias for clean_url)"""
    return URLCleaner.clean_url(url)