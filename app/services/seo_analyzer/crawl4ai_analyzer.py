from typing import Dict, List, Any
import re
import markdown
from markdown.extensions import toc

from app.core.config import seo_config

class Crawl4AIAnalyzer:
    """Analyzes SEO data using Crawl4AI's extracted content"""
    
    def extract_seo_data(self, crawl_result, domain: str) -> Dict[str, Any]:
        """Extract SEO data from Crawl4AI result"""
        
        # Get metadata from Crawl4AI (this contains title, description, etc.)
        metadata = getattr(crawl_result, 'metadata', {}) or {}
        
        # Extract title and meta description from metadata (NOT extracted_content)
        title = metadata.get('title', '')
        meta_desc = metadata.get('description', '') or metadata.get('meta_description', '')
        
        # Calculate word count from markdown content
        word_count = self._calculate_word_count(crawl_result)
        
        # Extract headings from structured data
        headings = self._extract_headings_from_crawl4ai(crawl_result)
        
        # Analyze images using Crawl4AI's media extraction
        image_data = self._analyze_images_from_crawl4ai(crawl_result)
        
        # Analyze links using Crawl4AI's link extraction
        link_data = self._analyze_links_from_crawl4ai(crawl_result, domain)
        
        return {
            'title': title,
            'meta_description': meta_desc,
            'word_count': word_count,
            **headings,
            **image_data,
            **link_data
        }
    
    def _extract_headings_from_crawl4ai(self, crawl_result) -> Dict[str, List[str]]:
        """Extract headings from Crawl4AI's markdown or HTML"""
        headings = {
            'h1_tags': [],
            'h2_tags': [],
            'h3_tags': []
        }
        
        # Try to get headings from markdown if available
        if hasattr(crawl_result, 'markdown') and crawl_result.markdown:
            headings = self._extract_headings_from_markdown(crawl_result.markdown)
        
        # Fallback to parsing cleaned HTML
        elif hasattr(crawl_result, 'cleaned_html') and crawl_result.cleaned_html:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(crawl_result.cleaned_html, 'html.parser')
            headings['h1_tags'] = [h.get_text(strip=True) for h in soup.find_all('h1')]
            headings['h2_tags'] = [h.get_text(strip=True) for h in soup.find_all('h2')]
            headings['h3_tags'] = [h.get_text(strip=True) for h in soup.find_all('h3')]
        
        return headings
    
    def _extract_headings_from_markdown(self, markdown_content: str) -> Dict[str, List[str]]:
        """Extract headings using python-markdown library with TOC extension"""
        headings = {
            'h1_tags': [],
            'h2_tags': [],
            'h3_tags': []
        }
        
        # Use markdown library with TOC extension to extract headings
        md = markdown.Markdown(extensions=['toc'])
        md.convert(markdown_content)
        
        # Extract headings from TOC
        if hasattr(md, 'toc_tokens'):
            for token in md.toc_tokens:
                level = token['level']
                title = token['name']
                
                if level == 1:
                    headings['h1_tags'].append(title)
                elif level == 2:
                    headings['h2_tags'].append(title)
                elif level == 3:
                    headings['h3_tags'].append(title)
        
        return headings
    
    def _analyze_images_from_crawl4ai(self, crawl_result) -> Dict[str, int]:
        """Analyze images using Crawl4AI's media extraction"""
        image_data = {
            'total_images': 0,
            'images_without_alt': 0,
            'images_bad_filename': 0,
            'oversized_images': 0
        }
        
        # Use Crawl4AI's media extraction if available
        if hasattr(crawl_result, 'media') and crawl_result.media:
            images = crawl_result.media.get('images', [])
            image_data['total_images'] = len(images)
            
            for img in images:
                # Check alt text
                if not img.get('alt') or not img.get('alt').strip():
                    image_data['images_without_alt'] += 1
                
                # Check filename
                src = img.get('src', '')
                if src and self._is_bad_filename(src):
                    image_data['images_bad_filename'] += 1
                
                # Check size (if available)
                if self._is_oversized_image(img):
                    image_data['oversized_images'] += 1
        
        return image_data
    
    def _analyze_links_from_crawl4ai(self, crawl_result, domain: str) -> Dict[str, int]:
        """Analyze links using Crawl4AI's link extraction"""
        link_data = {
            'internal_links': 0,
            'external_links': 0,
            'broken_links': 0
        }
        
        # Use Crawl4AI's links if available
        if hasattr(crawl_result, 'links') and crawl_result.links:
            internal_links = crawl_result.links.get('internal', [])
            external_links = crawl_result.links.get('external', [])
            
            link_data['internal_links'] = len(internal_links)
            link_data['external_links'] = len(external_links)
        
        return link_data
    
    def _is_bad_filename(self, src: str) -> bool:
        """Check if image filename is bad using configured patterns"""
        filename = src.split('/')[-1].lower()
        
        for pattern in seo_config.bad_filename_patterns:
            if re.match(pattern, filename):
                return True
        return False
    
    def _is_oversized_image(self, img: Dict[str, Any]) -> bool:
        """Check if image might be oversized using configured thresholds"""
        # Check dimensions if available
        width = img.get('width')
        height = img.get('height')
        
        try:
            if width and int(width) > seo_config.max_image_width:
                return True
            if height and int(height) > seo_config.max_image_height:
                return True
        except (ValueError, TypeError):
            pass
        
        # Check file size if available
        file_size = img.get('size')
        max_size_bytes = seo_config.max_image_size_mb * 1024 * 1024
        if file_size and file_size > max_size_bytes:
            return True
        
        return False
    
    def _calculate_word_count(self, crawl_result) -> int:
        """Calculate word count from Crawl4AI markdown content"""
        try:
            # Try to get word count from markdown content
            if hasattr(crawl_result, 'markdown') and crawl_result.markdown:
                # Get raw markdown text - handle both string and object types
                if hasattr(crawl_result, 'markdown') and crawl_result.markdown and hasattr(crawl_result.markdown, 'raw_markdown'):
                    text = crawl_result.markdown.raw_markdown
                else:
                    # Handle string markdown content directly
                    text = str(crawl_result.markdown) if crawl_result.markdown else ''
                
                if text:
                    # Simple word count (split by whitespace, filter empty strings)
                    words = [word for word in text.split() if word.strip()]
                    return len(words)
            
            # Fallback to cleaned HTML if markdown not available
            if hasattr(crawl_result, 'cleaned_html') and crawl_result.cleaned_html:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(crawl_result.cleaned_html, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                words = [word for word in text.split() if word.strip()]
                return len(words)
                
            return 0
            
        except Exception as e:
            # Log error but don't fail the whole analysis
            import logging
            logging.getLogger(__name__).warning(f"Error calculating word count: {str(e)}")
            return 0