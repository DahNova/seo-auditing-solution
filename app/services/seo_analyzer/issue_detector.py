from typing import List, Dict, Any
from app.core.config import seo_config
from .core.resource_details import ResourceDetailsBuilder, IssueFactory
from .performance_analyzer import PerformanceAnalyzer

class IssueDetector:
    """Detects and categorizes SEO issues using configurable rules"""
    
    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
    
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
        
        # Add granular performance issues (blocking resources)
        if content_type == 'html':
            performance_issues = self._check_performance_issues(crawl_result)
            issues.extend(performance_issues)
        
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
                'recommendation': 'Add a descriptive title tag of 50-60 characters',
                'score_impact': seo_config.scoring_weights['missing_title']
            })
        elif len(title) < seo_config.title_min_length:
            issues.append({
                'type': 'title_too_short',
                'category': 'on_page',
                'severity': 'medium',
                'title': 'Title Too Short',
                'description': f'Title is too short ({len(title)} chars)',
                'recommendation': f'Extend title to {seo_config.title_min_length}-{seo_config.title_max_length} characters - longer titles perform better in 2024+',
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
            
            # Check H1 quality if present
            elif h1_tags:
                h1_text = h1_tags[0].get_text(strip=True)
                
                # Check H1 length
                if len(h1_text) < 10:
                    issues.append({
                        'type': 'h1_too_short',
                        'category': 'on_page',
                        'severity': 'medium',
                        'title': 'H1 Too Short',
                        'description': f'H1 tag is too short ({len(h1_text)} characters)',
                        'recommendation': 'H1 should be 10-70 characters for optimal SEO',
                        'score_impact': seo_config.scoring_weights.get('h1_too_short', -3.0)
                    })
                elif len(h1_text) > 70:
                    issues.append({
                        'type': 'h1_too_long',
                        'category': 'on_page',
                        'severity': 'medium',
                        'title': 'H1 Too Long',
                        'description': f'H1 tag is too long ({len(h1_text)} characters)',
                        'recommendation': 'H1 should be 10-70 characters for optimal readability',
                        'score_impact': seo_config.scoring_weights.get('h1_too_long', -2.0)
                    })
                
                # Check H1 vs Title similarity
                issues.extend(self._check_h1_title_similarity(h1_text, crawl_result))
            
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
    
    def _check_h1_title_similarity(self, h1_text: str, crawl_result) -> List[Dict[str, Any]]:
        """Check similarity between H1 and Title"""
        issues = []
        
        # Get title from metadata
        metadata = getattr(crawl_result, 'metadata', {}) or {}
        title = metadata.get('title', '').strip()
        
        if not title:
            return issues
        
        # Normalize texts for comparison
        h1_normalized = h1_text.lower().strip()
        title_normalized = title.lower().strip()
        
        # Check if H1 and Title are identical
        if h1_normalized == title_normalized:
            issues.append({
                'type': 'duplicate_h1_title',
                'category': 'on_page',
                'severity': 'medium',
                'title': 'H1 Identical to Title',
                'description': 'H1 tag is identical to the page title',
                'recommendation': 'Make H1 complementary to title with additional keywords or context',
                'score_impact': seo_config.scoring_weights.get('duplicate_h1_title', -4.0)
            })
        else:
            # Check similarity using word overlap
            h1_words = set(h1_normalized.split())
            title_words = set(title_normalized.split())
            
            if len(h1_words) > 0 and len(title_words) > 0:
                overlap = len(h1_words.intersection(title_words))
                similarity = overlap / max(len(h1_words), len(title_words))
                
                if similarity > 0.8:  # More than 80% word overlap
                    issues.append({
                        'type': 'h1_too_similar_title',
                        'category': 'on_page',
                        'severity': 'low',
                        'title': 'H1 Too Similar to Title',
                        'description': f'H1 and title share {int(similarity*100)}% of words',
                        'recommendation': 'Diversify H1 and title to target different keyword variations',
                        'score_impact': seo_config.scoring_weights.get('h1_too_similar_title', -2.0)
                    })
        
        return issues
    
    def _check_image_issues(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check image optimization issues - GRANULAR VERSION"""
        issues = []
        
        for img in images:
            src = img.get('src', '')
            if not src:
                continue
                
            alt_text = img.get('alt', '')
            
            # Individual issue for each image missing alt text
            if not alt_text or not alt_text.strip():
                # Determine page context from image position or surrounding content
                page_context = self._get_image_context(img, src)
                
                resource_details = ResourceDetailsBuilder.image_missing_alt(
                    img_src=src,
                    page_context=page_context,
                    current_alt=alt_text,
                    selector=f'img[src="{src}"]'
                )
                
                issue = IssueFactory.create_granular_issue(
                    issue_type='image_missing_alt',
                    severity='high',
                    category='accessibility',
                    title='Image Missing Alt Text',
                    description=f'Image {self._truncate_url(src)} is missing descriptive alt text',
                    recommendation=f'Add descriptive alt text for {self._truncate_url(src)}',
                    resource_details=resource_details,
                    score_impact=seo_config.scoring_weights['images_missing_alt'] / 5  # Distribute weight
                )
                issues.append(issue)
            
            # Individual issue for each image with bad filename
            if src and self._is_bad_filename(src):
                page_context = self._get_image_context(img, src)
                suggested_filename = self._suggest_seo_filename(src)
                
                resource_details = ResourceDetailsBuilder.image_bad_filename(
                    img_src=src,
                    suggested_filename=suggested_filename,
                    page_context=page_context
                )
                
                issue = IssueFactory.create_granular_issue(
                    issue_type='image_bad_filename',
                    severity='medium',
                    category='technical',
                    title='Non-SEO Friendly Image Filename',
                    description=f'Image {self._truncate_url(src)} has non-descriptive filename',
                    recommendation=f'Rename to {suggested_filename}',
                    resource_details=resource_details,
                    score_impact=seo_config.scoring_weights['images_bad_filename'] / 3  # Distribute weight
                )
                issues.append(issue)
            
            # Individual issue for each oversized image
            if self._is_oversized_image(img):
                width = self._safe_int(img.get('width', 0))
                height = self._safe_int(img.get('height', 0))
                file_size = img.get('size')
                page_context = self._get_image_context(img, src)
                
                resource_details = ResourceDetailsBuilder.image_oversized(
                    img_src=src,
                    width=width,
                    height=height,
                    file_size=file_size,
                    page_context=page_context
                )
                
                issue = IssueFactory.create_granular_issue(
                    issue_type='image_oversized',
                    severity='medium',
                    category='performance',
                    title='Oversized Image',
                    description=f'Image {self._truncate_url(src)} is oversized ({width}x{height})',
                    recommendation=f'Optimize to max 1920x1080px and compress file size',
                    resource_details=resource_details,
                    score_impact=seo_config.scoring_weights['oversized_images'] / 3  # Distribute weight
                )
                issues.append(issue)
        
        return issues
    
    def _get_image_context(self, img: Dict[str, Any], src: str) -> str:
        """Determine image context from filename or attributes"""
        filename = src.split('/')[-1].lower()
        
        # Context clues from filename
        if any(term in filename for term in ['hero', 'banner', 'header']):
            return "Hero/Banner section"
        elif any(term in filename for term in ['logo', 'brand']):
            return "Logo/Branding"
        elif any(term in filename for term in ['product', 'item']):
            return "Product showcase"
        elif any(term in filename for term in ['gallery', 'thumb']):
            return "Image gallery"
        elif any(term in filename for term in ['icon', 'button']):
            return "UI element"
        else:
            return "Content image"
    
    def _truncate_url(self, url: str, max_length: int = 50) -> str:
        """Truncate URL for display purposes"""
        if len(url) <= max_length:
            return url
        return url[:max_length-3] + "..."
    
    def _suggest_seo_filename(self, src: str) -> str:
        """Suggest SEO-friendly filename"""
        filename = src.split('/')[-1]
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, 'jpg')
        
        # Basic suggestion - could be enhanced with AI/context
        if any(term in name.lower() for term in ['img', 'image', 'dsc', 'photo']):
            return f"descriptive-keyword.{ext}"
        return f"seo-friendly-{name}.{ext}"
    
    def _safe_int(self, value, default: int = 0) -> int:
        """Safely convert value to int"""
        try:
            return int(value) if value else default
        except (ValueError, TypeError):
            return default
    
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
    
    def _check_performance_issues(self, crawl_result) -> List[Dict[str, Any]]:
        """Check for granular performance issues using PerformanceAnalyzer"""
        issues = []
        
        try:
            # Get HTML content for blocking resource analysis
            html_content = getattr(crawl_result, 'html', '') or getattr(crawl_result, 'cleaned_html', '')
            
            if html_content:
                # Get granular blocking resources issues
                blocking_issues = self.performance_analyzer._identify_blocking_resources(html_content)
                issues.extend(blocking_issues)
            
        except Exception as e:
            # Log error but don't fail the whole analysis
            import logging
            logging.getLogger(__name__).warning(f"Error checking performance issues: {str(e)}")
        
        return issues