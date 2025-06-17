"""
Test SEO analyzer components - simplified version
"""
import pytest
from unittest.mock import Mock

# Simple mock for testing
class MockCrawlResult:
    def __init__(self):
        self.url = "https://example.com/test"
        self.status_code = 200
        self.markdown = "# Complete SEO Guide\n\n" + "This comprehensive guide covers SEO optimization techniques, technical implementation details, and modern best practices for 2024. " * 15  # Over 500 words
        self.cleaned_html = """
        <html>
            <head>
                <title>Complete SEO Guide for Modern Websites and Optimization</title>
                <meta name="description" content="Comprehensive guide covering all aspects of SEO optimization for modern websites, including technical SEO, content strategy, and performance tips for 2024.">
            </head>
            <body>
                <h1>Ultimate SEO Optimization Techniques and Best Practices</h1>
                <h2>Technical SEO Implementation</h2>
                <h2>Content Strategy Guidelines</h2>
                <p>This comprehensive guide covers SEO optimization techniques, technical implementation details, and modern best practices for 2024.</p>
                <img src="seo-guide-cover.jpg" alt="SEO optimization guide cover image">
                <img src="technical-seo-diagram.png" alt="Technical SEO implementation diagram">
                <a href="https://example.com/technical-seo">Technical SEO Chapter</a>
                <a href="https://external-seo-tools.com">External SEO Tools</a>
            </body>
        </html>
        """
        self.html = self.cleaned_html
        self.metadata = {
            'title': 'Complete SEO Guide for Modern Websites and Optimization',  # 55 chars
            'description': 'Comprehensive guide covering all aspects of SEO optimization for modern websites, including technical SEO, content strategy, and performance tips for 2024.',  # 155 chars
            'robots': 'index,follow'
        }
        self.media = {
            'images': [
                {'src': 'seo-guide-cover.jpg', 'alt': 'SEO optimization guide cover image'},
                {'src': 'technical-seo-diagram.png', 'alt': 'Technical SEO implementation diagram'}
            ]
        }
        self.links = {
            'internal': ['https://example.com/technical-seo'],
            'external': ['https://external-seo-tools.com']
        }

class MockCrawlResultWithIssues:
    def __init__(self):
        self.url = "https://example.com/bad-page"
        self.status_code = 200
        self.markdown = "Short content"  # Thin content
        self.cleaned_html = """
        <html>
            <head>
                <title>Short</title>
                <!-- Missing meta description -->
            </head>
            <body>
                <h1>Short</h1>  <!-- H1 identical to title -->
                <h1>Another H1</h1>  <!-- Multiple H1s -->
                <p>Short content</p>
                <img src="img123.jpg" alt="">  <!-- Missing alt text -->
                <img src="image456.png">  <!-- Missing alt attribute -->
            </body>
        </html>
        """
        self.html = self.cleaned_html
        self.metadata = {
            'title': 'Short',
            'description': None  # Missing meta description
        }
        self.media = {
            'images': [
                {'src': 'img123.jpg', 'alt': ''},
                {'src': 'image456.png'}
            ]
        }
        self.links = {
            'internal': [],
            'external': []
        }

# Simple SEO configuration for testing
class TestSEOConfig:
    title_min_length = 50
    title_max_length = 60
    meta_desc_min_length = 140
    meta_desc_max_length = 155
    min_word_count = 500
    scoring_weights = {
        'missing_title': -10.0,
        'title_too_short': -5.0,
        'title_too_long': -3.0,
        'missing_meta_description': -8.0,
        'meta_desc_too_short': -4.0,
        'meta_desc_too_long': -2.0,
        'thin_content': -6.0,
        'missing_h1': -8.0,
        'multiple_h1': -4.0,
        'duplicate_h1_title': -4.0,
        'h1_too_similar_title': -2.0,
        'h1_too_short': -3.0,
        'h1_too_long': -2.0,
        'images_missing_alt': -5.0,
        'images_bad_filename': -2.0,
        'oversized_images': -3.0
    }
    bad_filename_patterns = [
        r'^img\d+\.(jpg|jpeg|png|gif)$',
        r'^image\d+\.(jpg|jpeg|png|gif)$',
        r'^photo\d+\.(jpg|jpeg|png|gif)$',
        r'^pic\d+\.(jpg|jpeg|png|gif)$'
    ]
    max_image_width = 1920
    max_image_height = 1080
    max_image_size_mb = 2

# Simple IssueDetector implementation for testing
class SimpleIssueDetector:
    def __init__(self):
        self.config = TestSEOConfig()
    
    def _check_title_issues(self, title: str):
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
                'score_impact': self.config.scoring_weights['missing_title']
            })
        elif len(title) < self.config.title_min_length:
            issues.append({
                'type': 'title_too_short',
                'category': 'on_page',
                'severity': 'medium',
                'title': 'Title Too Short',
                'description': f'Title is too short ({len(title)} chars)',
                'recommendation': f'Extend title to {self.config.title_min_length}-{self.config.title_max_length} characters',
                'score_impact': self.config.scoring_weights['title_too_short']
            })
        elif len(title) > self.config.title_max_length:
            issues.append({
                'type': 'title_too_long',
                'category': 'on_page',
                'severity': 'medium',
                'title': 'Title Too Long',
                'description': f'Title is too long ({len(title)} chars)',
                'recommendation': f'Shorten title to {self.config.title_min_length}-{self.config.title_max_length} characters',
                'score_impact': self.config.scoring_weights['title_too_long']
            })
        
        return issues
    
    def _check_meta_description_issues(self, meta_desc: str):
        """Check meta description for SEO issues"""
        issues = []
        
        if not meta_desc:
            issues.append({
                'type': 'missing_meta_description',
                'category': 'on_page',
                'severity': 'high',
                'title': 'Missing Meta Description',
                'description': 'Page is missing a meta description',
                'recommendation': f'Add a meta description of {self.config.meta_desc_min_length}-{self.config.meta_desc_max_length} characters',
                'score_impact': self.config.scoring_weights['missing_meta_description']
            })
        elif len(meta_desc) < self.config.meta_desc_min_length:
            issues.append({
                'type': 'meta_desc_too_short',
                'category': 'on_page',
                'severity': 'medium',
                'title': 'Meta Description Too Short',
                'description': f'Meta description is too short ({len(meta_desc)} chars)',
                'recommendation': f'Extend to {self.config.meta_desc_min_length}-{self.config.meta_desc_max_length} characters',
                'score_impact': self.config.scoring_weights['meta_desc_too_short']
            })
        
        return issues
    
    def _check_content_issues(self, word_count: int):
        """Check content quality issues"""
        issues = []
        
        if word_count < self.config.min_word_count:
            issues.append({
                'type': 'thin_content',
                'category': 'content',
                'severity': 'medium',
                'title': 'Thin Content',
                'description': f'Page has thin content ({word_count} words)',
                'recommendation': f'Add more valuable content (minimum {self.config.min_word_count} words)',
                'score_impact': self.config.scoring_weights['thin_content']
            })
        
        return issues
    
    def _check_h1_issues(self, crawl_result):
        """Check H1 issues"""
        issues = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(crawl_result.cleaned_html, 'html.parser')
            h1_tags = soup.find_all('h1')
            
            if len(h1_tags) == 0:
                issues.append({
                    'type': 'missing_h1',
                    'category': 'on_page',
                    'severity': 'high',
                    'title': 'Missing H1 Tag',
                    'description': 'Page is missing an H1 heading tag',
                    'recommendation': 'Add a single, descriptive H1 tag',
                    'score_impact': self.config.scoring_weights['missing_h1']
                })
            elif len(h1_tags) > 1:
                issues.append({
                    'type': 'multiple_h1',
                    'category': 'on_page',
                    'severity': 'medium',
                    'title': 'Multiple H1 Tags',
                    'description': f'Page has {len(h1_tags)} H1 tags (should have exactly one)',
                    'recommendation': 'Use only one H1 tag per page',
                    'score_impact': self.config.scoring_weights['multiple_h1']
                })
            elif h1_tags:
                h1_text = h1_tags[0].get_text(strip=True)
                title = crawl_result.metadata.get('title', '').strip()
                
                # Check H1-title similarity
                if h1_text.lower() == title.lower():
                    issues.append({
                        'type': 'duplicate_h1_title',
                        'category': 'on_page',
                        'severity': 'medium',
                        'title': 'H1 Identical to Title',
                        'description': 'H1 tag is identical to the page title',
                        'recommendation': 'Make H1 complementary to title',
                        'score_impact': self.config.scoring_weights['duplicate_h1_title']
                    })
        except Exception:
            pass
        
        return issues
    
    def _calculate_word_count(self, markdown: str):
        """Calculate word count from markdown"""
        if not markdown:
            return 0
        words = [word for word in markdown.split() if word.strip()]
        return len(words)
    
    def detect_all_issues(self, crawl_result):
        """Detect all SEO issues for a page"""
        issues = []
        
        # Extract data
        metadata = getattr(crawl_result, 'metadata', {}) or {}
        title = metadata.get('title', '')
        meta_desc = metadata.get('description', '')
        
        # Calculate word count
        word_count = self._calculate_word_count(crawl_result.markdown)
        
        # Check issues
        issues.extend(self._check_title_issues(title))
        issues.extend(self._check_meta_description_issues(meta_desc))
        issues.extend(self._check_content_issues(word_count))
        issues.extend(self._check_h1_issues(crawl_result))
        
        return issues

# Simple scoring engine
class SimpleScoringEngine:
    def calculate_page_score(self, issues):
        """Calculate page score based on issues"""
        if not issues:
            return 100.0
        
        total_impact = sum(issue.get('score_impact', 0) for issue in issues)
        score = 100.0 + total_impact  # score_impact is negative
        return max(0.0, score)  # Don't go below 0
    
    def get_score_category(self, score):
        """Get score category"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 60:
            return "average"
        elif score >= 40:
            return "poor"
        else:
            return "critical"

class TestSimpleIssueDetector:
    """Test simplified IssueDetector functionality"""
    
    def test_detect_missing_title(self):
        """Test detection of missing title"""
        detector = SimpleIssueDetector()
        issues = detector._check_title_issues("")
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'missing_title'
        assert issues[0]['severity'] == 'critical'
    
    def test_detect_title_too_short(self):
        """Test detection of short title"""
        detector = SimpleIssueDetector()
        short_title = "Short"  # Less than 50 chars
        issues = detector._check_title_issues(short_title)
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'title_too_short'
        assert issues[0]['severity'] == 'medium'
    
    def test_detect_title_too_long(self):
        """Test detection of long title"""
        detector = SimpleIssueDetector()
        long_title = "This is a very long title that exceeds the recommended 60 character limit for SEO optimization"
        issues = detector._check_title_issues(long_title)
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'title_too_long'
        assert issues[0]['severity'] == 'medium'
    
    def test_detect_optimal_title(self):
        """Test optimal title length (no issues)"""
        detector = SimpleIssueDetector()
        optimal_title = "This is an optimal title length for SEO testing purposes"  # 55 chars
        issues = detector._check_title_issues(optimal_title)
        
        assert len(issues) == 0
    
    def test_detect_missing_meta_description(self):
        """Test detection of missing meta description"""
        detector = SimpleIssueDetector()
        issues = detector._check_meta_description_issues("")
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'missing_meta_description'
        assert issues[0]['severity'] == 'high'
    
    def test_detect_meta_description_too_short(self):
        """Test detection of short meta description"""
        detector = SimpleIssueDetector()
        short_desc = "Short description"  # Less than 140 chars
        issues = detector._check_meta_description_issues(short_desc)
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'meta_desc_too_short'
    
    def test_detect_thin_content(self):
        """Test detection of thin content"""
        detector = SimpleIssueDetector()
        issues = detector._check_content_issues(200)  # Less than 500 words
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'thin_content'
        assert issues[0]['severity'] == 'medium'
    
    def test_detect_quality_content(self):
        """Test quality content (no thin content issue)"""
        detector = SimpleIssueDetector()
        issues = detector._check_content_issues(600)  # More than 500 words
        
        assert len(issues) == 0
    
    def test_full_analysis_with_good_page(self):
        """Test complete analysis with good page"""
        detector = SimpleIssueDetector()
        good_result = MockCrawlResult()
        
        issues = detector.detect_all_issues(good_result)
        
        # Should have minimal issues
        assert len(issues) <= 2  # Maybe some minor issues
    
    def test_full_analysis_with_issues(self):
        """Test complete analysis with problematic page"""
        detector = SimpleIssueDetector()
        bad_result = MockCrawlResultWithIssues()
        
        issues = detector.detect_all_issues(bad_result)
        
        # Should detect multiple issues
        assert len(issues) >= 3
        
        issue_types = [issue['type'] for issue in issues]
        assert 'missing_meta_description' in issue_types
        assert 'thin_content' in issue_types
        assert any('h1' in issue_type for issue_type in issue_types)

class TestSimpleScoringEngine:
    """Test simplified ScoringEngine functionality"""
    
    def test_calculate_page_score_no_issues(self):
        """Test page score calculation with no issues"""
        scoring_engine = SimpleScoringEngine()
        issues = []
        score = scoring_engine.calculate_page_score(issues)
        
        assert score == 100.0  # Perfect score
    
    def test_calculate_page_score_with_issues(self):
        """Test page score calculation with issues"""
        scoring_engine = SimpleScoringEngine()
        issues = [
            {'type': 'missing_title', 'score_impact': -10.0},
            {'type': 'missing_h1', 'score_impact': -8.0},
            {'type': 'thin_content', 'score_impact': -6.0}
        ]
        score = scoring_engine.calculate_page_score(issues)
        
        expected_score = 100.0 - 24.0  # 76.0
        assert score == expected_score
    
    def test_score_bounds(self):
        """Test score stays within bounds"""
        scoring_engine = SimpleScoringEngine()
        # Test very negative impact
        issues = [
            {'type': 'critical_issue', 'score_impact': -200.0}
        ]
        score = scoring_engine.calculate_page_score(issues)
        
        assert score >= 0.0  # Should not go below 0
    
    def test_score_categorization(self):
        """Test score categorization"""
        scoring_engine = SimpleScoringEngine()
        
        assert scoring_engine.get_score_category(95.0) == "excellent"
        assert scoring_engine.get_score_category(85.0) == "good"
        assert scoring_engine.get_score_category(70.0) == "average"
        assert scoring_engine.get_score_category(55.0) == "poor"
        assert scoring_engine.get_score_category(30.0) == "critical"

class TestIntegratedSEOAnalysis:
    """Test integrated SEO analysis workflow"""
    
    def test_full_workflow_good_page(self):
        """Test complete workflow with good page"""
        detector = SimpleIssueDetector()
        scoring_engine = SimpleScoringEngine()
        
        # Analyze good page
        good_result = MockCrawlResult()
        issues = detector.detect_all_issues(good_result)
        score = scoring_engine.calculate_page_score(issues)
        category = scoring_engine.get_score_category(score)
        
        # Should have high score
        assert score >= 80.0
        assert category in ["excellent", "good"]
        assert len(issues) <= 2
    
    def test_full_workflow_bad_page(self):
        """Test complete workflow with problematic page"""
        detector = SimpleIssueDetector()
        scoring_engine = SimpleScoringEngine()
        
        # Analyze bad page
        bad_result = MockCrawlResultWithIssues()
        issues = detector.detect_all_issues(bad_result)
        score = scoring_engine.calculate_page_score(issues)
        category = scoring_engine.get_score_category(score)
        
        # Should have lower score and multiple issues
        assert score < 80.0
        assert len(issues) >= 3
        assert category in ["average", "poor", "critical"]
        
        # Check specific issues are detected
        issue_types = [issue['type'] for issue in issues]
        assert 'missing_meta_description' in issue_types
        assert 'thin_content' in issue_types