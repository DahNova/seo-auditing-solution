from typing import List, Dict, Any
from app.core.config import seo_config

class IssueDetector:
    """Detects and categorizes SEO issues using configurable rules"""
    
    def detect_all_issues(self, crawl_result, page_id: int) -> List[Dict[str, Any]]:
        """Detect all SEO issues for a page"""
        issues = []
        
        # Extract data from crawl result metadata (not extracted_content)
        metadata = getattr(crawl_result, 'metadata', {}) or {}
        title = metadata.get('title', '')
        meta_desc = metadata.get('description', '') or metadata.get('meta_description', '')
        
        # Calculate word count from markdown
        word_count = self._calculate_word_count_from_crawl_result(crawl_result)
        
        # Get URL and content type
        url = getattr(crawl_result, 'url', '')
        content_type = self._detect_content_type(url)
        
        # Get additional data from media and links
        media = getattr(crawl_result, 'media', {})
        links = getattr(crawl_result, 'links', {})
        
        # Only check HTML content for content/meta issues
        if content_type == 'html':
            # Check title issues
            issues.extend(self._check_title_issues(title))
            
            # Check meta description issues
            issues.extend(self._check_meta_description_issues(meta_desc))
            
            # Check content issues
            issues.extend(self._check_content_issues(word_count))
            
            # Check heading structure issues
            issues.extend(self._check_heading_issues(crawl_result))
        
        # Check image-specific issues for image files
        elif content_type == 'image':
            issues.extend(self._check_image_file_issues(url))
        
        # Check PDF-specific issues for PDFs
        elif content_type == 'pdf':
            issues.extend(self._check_pdf_file_issues(url))
        
        # Check image issues for HTML pages with images
        if media and content_type == 'html':
            issues.extend(self._check_image_issues(media.get('images', [])))
        
        # Check status code issues for all content types
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
    
    def _check_heading_issues(self, crawl_result) -> List[Dict[str, Any]]:
        """Check heading structure for SEO issues"""
        issues = []
        
        try:
            # Get HTML content to analyze headings
            html_content = getattr(crawl_result, 'cleaned_html', '') or getattr(crawl_result, 'html', '')
            
            if not html_content:
                return issues
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all heading tags
            h1_tags = soup.find_all('h1')
            h2_tags = soup.find_all('h2')
            h3_tags = soup.find_all('h3')
            
            # Check for missing H1
            if len(h1_tags) == 0:
                issues.append({
                    'type': 'missing_h1',
                    'category': 'on_page',
                    'severity': 'high',
                    'title': 'Missing H1 Tag',
                    'description': 'Page is missing an H1 heading tag',
                    'recommendation': 'Add a single, descriptive H1 tag that includes the main keyword',
                    'score_impact': seo_config.scoring_weights.get('missing_h1', -8.0)
                })
            
            # Check for multiple H1 tags
            elif len(h1_tags) > 1:
                issues.append({
                    'type': 'multiple_h1',
                    'category': 'on_page',
                    'severity': 'medium',
                    'title': 'Multiple H1 Tags',
                    'description': f'Page has {len(h1_tags)} H1 tags (should have exactly one)',
                    'recommendation': 'Use only one H1 tag per page, convert others to H2-H6',
                    'score_impact': seo_config.scoring_weights.get('multiple_h1', -4.0)
                })
            
            # Check for empty H1
            elif h1_tags and not h1_tags[0].get_text(strip=True):
                issues.append({
                    'type': 'empty_h1',
                    'category': 'on_page',
                    'severity': 'high',
                    'title': 'Empty H1 Tag',
                    'description': 'H1 tag is present but empty',
                    'recommendation': 'Add descriptive text to the H1 tag',
                    'score_impact': seo_config.scoring_weights.get('empty_h1', -6.0)
                })
            
            # Check heading hierarchy (H2 without H1, H3 without H2, etc.)
            if len(h1_tags) == 0 and len(h2_tags) > 0:
                issues.append({
                    'type': 'broken_heading_hierarchy',
                    'category': 'on_page',
                    'severity': 'medium',
                    'title': 'Broken Heading Hierarchy',
                    'description': f'Page has H2 tags ({len(h2_tags)}) but no H1',
                    'recommendation': 'Ensure proper heading hierarchy: H1 > H2 > H3',
                    'score_impact': seo_config.scoring_weights.get('broken_heading_hierarchy', -3.0)
                })
            
            # Check for too many headings (content structure issue)
            total_headings = len(h1_tags) + len(h2_tags) + len(h3_tags)
            if total_headings > 15:  # Arbitrary threshold
                issues.append({
                    'type': 'excessive_headings',
                    'category': 'content',
                    'severity': 'low',
                    'title': 'Excessive Headings',
                    'description': f'Page has {total_headings} heading tags (may be over-structured)',
                    'recommendation': 'Consider simplifying content structure',
                    'score_impact': seo_config.scoring_weights.get('excessive_headings', -1.0)
                })
                
        except Exception as e:
            # Log error but don't fail the whole analysis
            import logging
            logging.getLogger(__name__).warning(f"Error analyzing headings: {str(e)}")
        
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
    
    def _detect_content_type(self, url: str) -> str:
        """Detect content type based on URL extension"""
        url_lower = url.lower()
        
        # Image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico']
        if any(url_lower.endswith(ext) for ext in image_extensions):
            return 'image'
        
        # PDF extensions
        if url_lower.endswith('.pdf'):
            return 'pdf'
        
        # Document extensions
        doc_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        if any(url_lower.endswith(ext) for ext in doc_extensions):
            return 'document'
        
        # Video/Audio extensions
        media_extensions = ['.mp4', '.avi', '.mov', '.mp3', '.wav', '.ogg']
        if any(url_lower.endswith(ext) for ext in media_extensions):
            return 'media'
        
        # Default to HTML for pages and unknown content
        return 'html'
    
    def _check_image_file_issues(self, url: str) -> List[Dict[str, Any]]:
        """Check SEO issues specific to image files"""
        issues = []
        
        # Extract filename from URL
        filename = url.split('/')[-1].lower()
        
        # Check for bad filename patterns
        if self._is_bad_filename(url):
            issues.append({
                'type': 'image_bad_filename',
                'category': 'technical',
                'severity': 'medium',
                'title': 'Non-SEO Friendly Image Filename',
                'description': f'Image filename "{filename}" is not SEO-friendly',
                'recommendation': 'Use descriptive, keyword-rich filenames (e.g., "serramenti-alluminio.jpg")',
                'score_impact': -3.0
            })
        
        # Check if image has no alt text context (if it's a standalone image)
        # Note: This is detected at the HTML level, not file level
        
        return issues
    
    def _check_pdf_file_issues(self, url: str) -> List[Dict[str, Any]]:
        """Check SEO issues specific to PDF files"""
        issues = []
        
        # Extract filename from URL
        filename = url.split('/')[-1].lower()
        
        # Check for bad filename patterns
        if self._is_bad_filename(url):
            issues.append({
                'type': 'pdf_bad_filename',
                'category': 'technical',
                'severity': 'medium',
                'title': 'Non-SEO Friendly PDF Filename',
                'description': f'PDF filename "{filename}" is not SEO-friendly',
                'recommendation': 'Use descriptive, keyword-rich filenames for PDFs',
                'score_impact': -2.0
            })
        
        # PDFs should ideally be linked from HTML pages, not crawled directly
        issues.append({
            'type': 'pdf_accessibility',
            'category': 'technical',
            'severity': 'minor',
            'title': 'PDF Accessibility',
            'description': 'PDF file detected - ensure it has proper text content and is accessible',
            'recommendation': 'Consider providing HTML alternatives or ensure PDF is screen-reader friendly',
            'score_impact': -1.0
        })
        
        return issues
    
    def _calculate_word_count_from_crawl_result(self, crawl_result) -> int:
        """Calculate word count from Crawl4AI result"""
        try:
            # Try to get word count from markdown content
            if hasattr(crawl_result, 'markdown') and crawl_result.markdown:
                # Get raw markdown text
                if hasattr(crawl_result.markdown, 'raw_markdown'):
                    text = crawl_result.markdown.raw_markdown
                else:
                    text = str(crawl_result.markdown)
                
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
            logging.getLogger(__name__).warning(f"Error calculating word count in issue detector: {str(e)}")
            return 0