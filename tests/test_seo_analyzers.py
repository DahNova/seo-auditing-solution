"""
Test SEO analyzer components
"""
import pytest
from unittest.mock import Mock, patch

from app.services.seo_analyzer.issue_detector import IssueDetector
from app.services.seo_analyzer.crawl4ai_analyzer import Crawl4AIAnalyzer
from app.services.seo_analyzer.scoring_engine import ScoringEngine
from app.core.config import seo_config

class TestIssueDetector:
    """Test IssueDetector functionality"""
    
    @pytest.fixture
    def detector(self):
        return IssueDetector()
    
    def test_detect_missing_title(self, detector, mock_crawl_result):
        """Test detection of missing title"""
        mock_crawl_result.metadata = {}
        issues = detector._check_title_issues("")
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'missing_title'
        assert issues[0]['severity'] == 'critical'
        
    def test_detect_title_too_short(self, detector):
        """Test detection of short title"""
        short_title = "Short"  # Less than 50 chars
        issues = detector._check_title_issues(short_title)
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'title_too_short'
        assert issues[0]['severity'] == 'medium'
        
    def test_detect_title_too_long(self, detector):
        """Test detection of long title"""
        long_title = "This is a very long title that exceeds the recommended 60 character limit for SEO optimization"
        issues = detector._check_title_issues(long_title)
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'title_too_long'
        assert issues[0]['severity'] == 'medium'
        
    def test_detect_optimal_title(self, detector):
        """Test optimal title length (no issues)"""
        optimal_title = "This is an optimal title length for SEO testing"
        issues = detector._check_title_issues(optimal_title)
        
        assert len(issues) == 0
        
    def test_detect_missing_meta_description(self, detector):
        """Test detection of missing meta description"""
        issues = detector._check_meta_description_issues("")
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'missing_meta_description'
        assert issues[0]['severity'] == 'high'
        
    def test_detect_meta_description_too_short(self, detector):
        """Test detection of short meta description"""
        short_desc = "Short description"  # Less than 140 chars
        issues = detector._check_meta_description_issues(short_desc)
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'meta_desc_too_short'
        
    def test_detect_thin_content(self, detector):
        """Test detection of thin content"""
        issues = detector._check_content_issues(200)  # Less than 500 words
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'thin_content'
        assert issues[0]['severity'] == 'medium'
        
    def test_detect_quality_content(self, detector):
        """Test quality content (no thin content issue)"""
        issues = detector._check_content_issues(600)  # More than 500 words
        
        assert len(issues) == 0
        
    def test_h1_title_similarity(self, detector, mock_crawl_result):
        """Test H1 vs Title similarity detection"""
        mock_crawl_result.metadata = {'title': 'Test Page Title'}
        
        # Test identical H1 and title
        issues = detector._check_h1_title_similarity('Test Page Title', mock_crawl_result)
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'duplicate_h1_title'
        assert issues[0]['severity'] == 'medium'
        
    def test_h1_title_similarity_high_overlap(self, detector, mock_crawl_result):
        """Test H1 with high word overlap to title"""
        mock_crawl_result.metadata = {'title': 'Test Page Title SEO'}
        
        # Test high similarity (>80% overlap)
        issues = detector._check_h1_title_similarity('Test Page Title', mock_crawl_result)
        
        assert len(issues) == 1
        assert issues[0]['type'] == 'h1_too_similar_title'
        assert issues[0]['severity'] == 'low'
        
    def test_h1_title_different(self, detector, mock_crawl_result):
        """Test H1 different from title (no issues)"""
        mock_crawl_result.metadata = {'title': 'Test Page Title'}
        
        # Test different H1
        issues = detector._check_h1_title_similarity('Completely Different Heading', mock_crawl_result)
        
        assert len(issues) == 0
        
    def test_detect_multiple_h1_tags(self, detector, mock_crawl_result_with_issues):
        """Test detection of multiple H1 tags"""
        issues = detector._check_heading_issues(mock_crawl_result_with_issues)
        
        multiple_h1_issues = [issue for issue in issues if issue['type'] == 'multiple_h1']
        assert len(multiple_h1_issues) == 1
        assert multiple_h1_issues[0]['severity'] == 'medium'
        
    def test_detect_h1_length_issues(self, detector, mock_crawl_result):
        """Test H1 length validation"""
        from bs4 import BeautifulSoup
        
        # Test short H1
        mock_crawl_result.cleaned_html = "<html><body><h1>Short</h1></body></html>"
        issues = detector._check_heading_issues(mock_crawl_result)
        
        short_h1_issues = [issue for issue in issues if issue['type'] == 'h1_too_short']
        assert len(short_h1_issues) == 1
        
        # Test long H1
        long_h1 = "This is a very long H1 tag that exceeds the recommended 70 character limit for optimal SEO"
        mock_crawl_result.cleaned_html = f"<html><body><h1>{long_h1}</h1></body></html>"
        issues = detector._check_heading_issues(mock_crawl_result)
        
        long_h1_issues = [issue for issue in issues if issue['type'] == 'h1_too_long']
        assert len(long_h1_issues) == 1

class TestCrawl4AIAnalyzer:
    """Test Crawl4AIAnalyzer functionality"""
    
    @pytest.fixture
    def analyzer(self):
        return Crawl4AIAnalyzer()
    
    def test_extract_basic_data(self, analyzer, mock_crawl_result):
        """Test basic data extraction from crawl result"""
        result = analyzer.analyze_crawl_result(mock_crawl_result, 1)
        
        assert result['url'] == 'https://example.com/test'
        assert result['title'] == 'Test Page Title'
        assert result['meta_description'] == 'Test meta description for SEO'
        assert result['status_code'] == 200
        assert result['word_count'] > 0
        
    def test_extract_headings(self, analyzer, mock_crawl_result):
        """Test heading extraction"""
        result = analyzer.analyze_crawl_result(mock_crawl_result, 1)
        
        assert result['h1_count'] == 1
        assert result['h2_count'] == 2
        assert 'Main Heading' in str(result.get('headings', {}))
        
    def test_extract_images(self, analyzer, mock_crawl_result):
        """Test image data extraction"""
        result = analyzer.analyze_crawl_result(mock_crawl_result, 1)
        
        assert result['image_count'] == 2
        # Should detect image without alt text
        
    def test_extract_links(self, analyzer, mock_crawl_result):
        """Test link extraction"""
        result = analyzer.analyze_crawl_result(mock_crawl_result, 1)
        
        assert result['internal_links'] >= 1
        assert result['external_links'] >= 1
        assert result['link_count'] >= 2
        
    def test_word_count_calculation(self, analyzer, mock_crawl_result):
        """Test word count calculation from markdown"""
        word_count = analyzer._calculate_word_count_from_markdown(mock_crawl_result.markdown)
        
        assert word_count > 0
        assert isinstance(word_count, int)
        
    def test_handle_missing_metadata(self, analyzer, mock_crawl_result):
        """Test handling of missing metadata"""
        mock_crawl_result.metadata = None
        result = analyzer.analyze_crawl_result(mock_crawl_result, 1)
        
        assert result['title'] == ''
        assert result['meta_description'] == ''

class TestScoringEngine:
    """Test ScoringEngine functionality"""
    
    @pytest.fixture
    def scoring_engine(self):
        return ScoringEngine()
    
    def test_calculate_page_score_no_issues(self, scoring_engine):
        """Test page score calculation with no issues"""
        issues = []
        score = scoring_engine.calculate_page_score(issues)
        
        assert score == 100.0  # Perfect score
        
    def test_calculate_page_score_with_issues(self, scoring_engine):
        """Test page score calculation with issues"""
        issues = [
            {'type': 'missing_title', 'score_impact': -10.0},
            {'type': 'missing_h1', 'score_impact': -8.0},
            {'type': 'thin_content', 'score_impact': -5.0}
        ]
        score = scoring_engine.calculate_page_score(issues)
        
        expected_score = 100.0 - 23.0  # 77.0
        assert score == expected_score
        
    def test_score_bounds(self, scoring_engine):
        """Test score stays within bounds"""
        # Test very negative impact
        issues = [
            {'type': 'critical_issue', 'score_impact': -200.0}
        ]
        score = scoring_engine.calculate_page_score(issues)
        
        assert score >= 0.0  # Should not go below 0
        
    def test_calculate_overall_scan_score(self, scoring_engine):
        """Test overall scan score calculation"""
        page_scores = [85.0, 90.0, 75.0, 95.0]
        overall_score = scoring_engine.calculate_overall_score(page_scores)
        
        expected_average = sum(page_scores) / len(page_scores)
        assert overall_score == expected_average
        
    def test_empty_page_scores(self, scoring_engine):
        """Test handling of empty page scores"""
        page_scores = []
        overall_score = scoring_engine.calculate_overall_score(page_scores)
        
        assert overall_score == 0.0
        
    def test_score_categorization(self, scoring_engine):
        """Test score categorization"""
        assert scoring_engine.get_score_category(95.0) == "excellent"
        assert scoring_engine.get_score_category(85.0) == "good"
        assert scoring_engine.get_score_category(70.0) == "average"
        assert scoring_engine.get_score_category(55.0) == "poor"
        assert scoring_engine.get_score_category(40.0) == "critical"

class TestIntegratedSEOAnalysis:
    """Test integrated SEO analysis workflow"""
    
    @pytest.fixture
    def issue_detector(self):
        return IssueDetector()
    
    @pytest.fixture
    def analyzer(self):
        return Crawl4AIAnalyzer()
    
    @pytest.fixture
    def scoring_engine(self):
        return ScoringEngine()
    
    def test_full_analysis_workflow(self, issue_detector, analyzer, scoring_engine, mock_crawl_result_with_issues):
        """Test complete SEO analysis workflow"""
        # 1. Analyze crawl result
        analysis_result = analyzer.analyze_crawl_result(mock_crawl_result_with_issues, 1)
        
        # 2. Detect issues
        issues = issue_detector.detect_all_issues(mock_crawl_result_with_issues, 1)
        
        # 3. Calculate score
        score = scoring_engine.calculate_page_score(issues)
        
        # Assertions
        assert len(issues) > 0  # Should detect issues
        assert score < 100.0  # Score should be reduced due to issues
        
        # Check specific issues are detected
        issue_types = [issue['type'] for issue in issues]
        assert 'missing_meta_description' in issue_types
        assert 'thin_content' in issue_types
        assert 'duplicate_h1_title' in issue_types
        assert 'multiple_h1' in issue_types
        
    def test_analysis_with_perfect_page(self, issue_detector, analyzer, scoring_engine, mock_crawl_result):
        """Test analysis with a well-optimized page"""
        # Modify mock to be perfect
        mock_crawl_result.metadata = {
            'title': 'Perfect SEO Optimized Page Title for Testing',
            'description': 'This is a perfect meta description that is between 140-155 characters long and provides great value for search engine users.'
        }
        mock_crawl_result.cleaned_html = """
        <html>
            <head>
                <title>Perfect SEO Optimized Page Title for Testing</title>
                <meta name="description" content="This is a perfect meta description that is between 140-155 characters long and provides great value for search engine users.">
            </head>
            <body>
                <h1>Comprehensive SEO Guide for Modern Websites</h1>
                <h2>Introduction to SEO</h2>
                <h2>Technical SEO Best Practices</h2>
                <p>This page contains substantial content with over 500 words providing valuable information about SEO optimization techniques and best practices.</p>
                <img src="seo-guide.jpg" alt="Comprehensive SEO optimization guide">
            </body>
        </html>
        """
        mock_crawl_result.markdown = "# Comprehensive SEO Guide\n\n" + "Quality content paragraph. " * 100
        
        # Analyze
        analysis_result = analyzer.analyze_crawl_result(mock_crawl_result, 1)
        issues = issue_detector.detect_all_issues(mock_crawl_result, 1)
        score = scoring_engine.calculate_page_score(issues)
        
        # Should have minimal issues and high score
        assert score >= 90.0
        assert len(issues) <= 2  # Maybe minor issues only