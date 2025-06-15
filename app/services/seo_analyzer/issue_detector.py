from typing import List, Dict, Any
from app.core.config import seo_config

class IssueDetector:
    """Detects and categorizes SEO issues using configurable rules"""
    
    def detect_all_issues(self, crawl_result, page_id: int) -> List[Dict[str, Any]]:
        """Detect all SEO issues for a page"""
        issues = []
        
        # Extract data from crawl result
        extracted = crawl_result.extracted_content or {}
        title = extracted.get('title', '')
        meta_desc = extracted.get('meta_description', '')
        word_count = extracted.get('word_count', 0)
        
        # Get additional data from media and links
        media = getattr(crawl_result, 'media', {})
        links = getattr(crawl_result, 'links', {})
        
        # Check title issues
        issues.extend(self._check_title_issues(title))
        
        # Check meta description issues
        issues.extend(self._check_meta_description_issues(meta_desc))
        
        # Check content issues
        issues.extend(self._check_content_issues(word_count))
        
        # Check image issues
        if media:
            issues.extend(self._check_image_issues(media.get('images', [])))
        
        # Check status code issues
        if hasattr(crawl_result, 'status_code'):
            issues.extend(self._check_status_code_issues(crawl_result.status_code))
        
        return issues
    
    def _check_title_issues(self, title: str) -> List[Dict[str, Any]]:
        """Check title for SEO issues"""
        issues = []
        
        if not title:
            issues.append({
                'type': 'missing_title',
                'category': 'on_page',
                'severity': 'critical',
                'title': 'Missing Title Tag',
                'description': 'Page is missing a title tag',
                'recommendation': 'Add a descriptive title tag of 30-60 characters',
                'score_impact': seo_config.scoring_weights['missing_title']
            })
        elif len(title) < seo_config.title_min_length:
            issues.append({
                'type': 'title_too_short',
                'category': 'on_page',
                'severity': 'medium',
                'title': 'Title Too Short',
                'description': f'Title is too short ({len(title)} chars)',
                'recommendation': f'Extend title to {seo_config.title_min_length}-{seo_config.title_max_length} characters',
                'score_impact': seo_config.scoring_weights['title_too_short']
            })
        elif len(title) > seo_config.title_max_length:
            issues.append({
                'type': 'title_too_long',
                'category': 'on_page',
                'severity': 'medium',
                'title': 'Title Too Long',
                'description': f'Title is too long ({len(title)} chars)',
                'recommendation': f'Shorten title to {seo_config.title_min_length}-{seo_config.title_max_length} characters',
                'score_impact': seo_config.scoring_weights['title_too_long']
            })
        
        return issues
    
    def _check_meta_description_issues(self, meta_desc: str) -> List[Dict[str, Any]]:
        """Check meta description for SEO issues"""
        issues = []
        
        if not meta_desc:
            issues.append({
                'type': 'missing_meta_description',
                'category': 'on_page',
                'severity': 'high',
                'title': 'Missing Meta Description',
                'description': 'Page is missing a meta description',
                'recommendation': f'Add a meta description of {seo_config.meta_desc_min_length}-{seo_config.meta_desc_max_length} characters',
                'score_impact': seo_config.scoring_weights['missing_meta_description']
            })
        elif len(meta_desc) < seo_config.meta_desc_min_length:
            issues.append({
                'type': 'meta_desc_too_short',
                'category': 'on_page',
                'severity': 'medium',
                'title': 'Meta Description Too Short',
                'description': f'Meta description is too short ({len(meta_desc)} chars)',
                'recommendation': f'Extend to {seo_config.meta_desc_min_length}-{seo_config.meta_desc_max_length} characters',
                'score_impact': seo_config.scoring_weights['meta_desc_too_short']
            })
        elif len(meta_desc) > seo_config.meta_desc_max_length:
            issues.append({
                'type': 'meta_desc_too_long',
                'category': 'on_page',
                'severity': 'medium',
                'title': 'Meta Description Too Long',
                'description': f'Meta description is too long ({len(meta_desc)} chars)',
                'recommendation': f'Shorten to {seo_config.meta_desc_min_length}-{seo_config.meta_desc_max_length} characters',
                'score_impact': seo_config.scoring_weights['meta_desc_too_long']
            })
        
        return issues
    
    def _check_content_issues(self, word_count: int) -> List[Dict[str, Any]]:
        """Check content quality issues"""
        issues = []
        
        if word_count < seo_config.min_word_count:
            issues.append({
                'type': 'thin_content',
                'category': 'content',
                'severity': 'medium',
                'title': 'Thin Content',
                'description': f'Page has thin content ({word_count} words)',
                'recommendation': f'Add more valuable content (minimum {seo_config.min_word_count} words)',
                'score_impact': seo_config.scoring_weights['thin_content']
            })
        
        return issues
    
    def _check_image_issues(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check image optimization issues"""
        issues = []
        images_without_alt = 0
        images_bad_filename = 0
        oversized_images = 0
        
        for img in images:
            if not img.get('alt') or not img.get('alt').strip():
                images_without_alt += 1
            
            # Check filename using the same logic as crawl4ai_analyzer
            src = img.get('src', '')
            if src and self._is_bad_filename(src):
                images_bad_filename += 1
            
            if self._is_oversized_image(img):
                oversized_images += 1
        
        if images_without_alt > 0:
            issues.append({
                'type': 'images_missing_alt',
                'category': 'on_page',
                'severity': 'high',
                'title': 'Images Missing Alt Text',
                'description': f'{images_without_alt} images are missing alt text',
                'recommendation': 'Add descriptive alt text to all images',
                'score_impact': seo_config.scoring_weights['images_missing_alt']
            })
        
        if images_bad_filename > 0:
            issues.append({
                'type': 'images_bad_filename',
                'category': 'technical',
                'severity': 'medium',
                'title': 'Non-Descriptive Image Filenames',
                'description': f'{images_bad_filename} images have non-descriptive filenames',
                'recommendation': 'Use descriptive, keyword-rich filenames for images',
                'score_impact': seo_config.scoring_weights['images_bad_filename']
            })
        
        if oversized_images > 0:
            issues.append({
                'type': 'oversized_images',
                'category': 'technical',
                'severity': 'medium',
                'title': 'Oversized Images',
                'description': f'{oversized_images} images might be oversized',
                'recommendation': 'Optimize image sizes and use appropriate formats',
                'score_impact': seo_config.scoring_weights['oversized_images']
            })
        
        return issues
    
    def _check_status_code_issues(self, status_code: int) -> List[Dict[str, Any]]:
        """Check HTTP status code issues"""
        issues = []
        
        if status_code >= 400:
            severity = 'critical' if status_code >= 500 else 'high'
            issues.append({
                'type': f'http_error_{status_code}',
                'category': 'technical',
                'severity': severity,
                'title': f'HTTP {status_code} Error',
                'description': f'Page returns HTTP {status_code} status code',
                'recommendation': 'Fix server errors or redirect issues',
                'score_impact': -15.0 if status_code >= 500 else -8.0
            })
        
        return issues
    
    def _is_bad_filename(self, src: str) -> bool:
        """Check if image filename is bad using configured patterns"""
        import re
        filename = src.split('/')[-1].lower()
        
        for pattern in seo_config.bad_filename_patterns:
            if re.match(pattern, filename):
                return True
        return False
    
    def _is_oversized_image(self, img: Dict[str, Any]) -> bool:
        """Check if image might be oversized using configured thresholds"""
        width = img.get('width')
        height = img.get('height')
        
        try:
            if width and int(width) > seo_config.max_image_width:
                return True
            if height and int(height) > seo_config.max_image_height:
                return True
        except (ValueError, TypeError):
            pass
        
        file_size = img.get('size')
        max_size_bytes = seo_config.max_image_size_mb * 1024 * 1024
        if file_size and file_size > max_size_bytes:
            return True
        
        return False