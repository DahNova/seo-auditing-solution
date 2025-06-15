from typing import Dict, List, Any
import re
import markdown
from markdown.extensions import toc

from app.core.config import seo_config

class Crawl4AIAnalyzer:
    """Analyzes SEO data using Crawl4AI's extracted content"""
    
    def extract_seo_data(self, crawl_result, domain: str) -> Dict[str, Any]:
        """Extract SEO data from Crawl4AI result"""
        
        # Get extracted content from Crawl4AI
        extracted = crawl_result.extracted_content or {}
        
        # Extract title and meta description
        title = extracted.get('title', '')
        meta_desc = extracted.get('meta_description', '')
        
        # Extract headings from structured data
        headings = self._extract_headings_from_crawl4ai(crawl_result)
        
        # Analyze images using Crawl4AI's media extraction
        image_data = self._analyze_images_from_crawl4ai(crawl_result)
        
        # Analyze links using Crawl4AI's link extraction
        link_data = self._analyze_links_from_crawl4ai(crawl_result, domain)
        
        # Get word count from Crawl4AI
        word_count = extracted.get('word_count', 0)
        
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