import re
from typing import Dict
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class ImageAnalyzer:
    """Analyzes images for SEO optimization"""
    
    def __init__(self):
        self.bad_filename_patterns = [
            r'^img\d+\.(jpg|jpeg|png|gif|webp)$',
            r'^image\d+\.(jpg|jpeg|png|gif|webp)$',
            r'^dsc\d+\.(jpg|jpeg|png|gif|webp)$',
            r'^screenshot.*\.(jpg|jpeg|png|gif|webp)$',
            r'^untitled.*\.(jpg|jpeg|png|gif|webp)$'
        ]
    
    def analyze(self, soup: BeautifulSoup, page_url: str) -> Dict[str, int]:
        """Analyze all images on the page"""
        images = soup.find_all('img')
        
        total_images = len(images)
        images_without_alt = 0
        images_bad_filename = 0
        oversized_images = 0
        
        for img in images:
            # Check alt text
            if not img.get('alt') or not img.get('alt').strip():
                images_without_alt += 1
            
            # Check filename
            src = img.get('src', '')
            if src:
                # Convert relative URLs to absolute
                full_url = urljoin(page_url, src)
                filename = urlparse(full_url).path.split('/')[-1].lower()
                
                if self._is_bad_filename(filename):
                    images_bad_filename += 1
            
            # Check if image might be oversized (basic heuristic)
            if self._might_be_oversized(img):
                oversized_images += 1
        
        return {
            'total_images': total_images,
            'images_without_alt': images_without_alt,
            'images_bad_filename': images_bad_filename,
            'oversized_images': oversized_images
        }
    
    def _is_bad_filename(self, filename: str) -> bool:
        """Check if filename follows bad naming patterns"""
        for pattern in self.bad_filename_patterns:
            if re.match(pattern, filename, re.IGNORECASE):
                return True
        return False
    
    def _might_be_oversized(self, img_tag) -> bool:
        """Basic heuristic to detect potentially oversized images"""
        # Check if image has width/height attributes that suggest it's large
        width = img_tag.get('width')
        height = img_tag.get('height')
        
        try:
            if width and int(width) > 1920:
                return True
            if height and int(height) > 1080:
                return True
        except ValueError:
            pass
        
        # Check for common patterns in src that suggest large images
        src = img_tag.get('src', '').lower()
        if any(size in src for size in ['2k', '4k', 'hd', 'fullsize', 'original']):
            return True
        
        return False
    
    def get_image_issues(self, image_data: Dict[str, int]) -> list:
        """Generate issues based on image analysis"""
        issues = []
        
        if image_data['images_without_alt'] > 0:
            issues.append({
                'type': 'images_missing_alt',
                'severity': 'high',
                'message': f"{image_data['images_without_alt']} images are missing alt text"
            })
        
        if image_data['images_bad_filename'] > 0:
            issues.append({
                'type': 'images_bad_filename',
                'severity': 'medium',
                'message': f"{image_data['images_bad_filename']} images have non-descriptive filenames"
            })
        
        if image_data['oversized_images'] > 0:
            issues.append({
                'type': 'oversized_images',
                'severity': 'medium',
                'message': f"{image_data['oversized_images']} images might be oversized"
            })
        
        return issues