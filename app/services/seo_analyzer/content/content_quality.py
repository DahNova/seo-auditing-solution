"""
Content Quality Analyzer
Advanced analysis of content quality, readability, and optimization
"""
from typing import Dict, List, Any, Optional
import re
from collections import Counter
from datetime import datetime, timedelta

from ..core.base_analyzer import BaseAnalyzer, AnalysisResult
from ..core.content_extractor import ContentExtractor
from app.core.config import seo_config

class ContentQualityAnalyzer(BaseAnalyzer):
    """Analyzes content quality, readability, and SEO optimization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.extractor = ContentExtractor()
    
    def analyze(self, crawl_result, **kwargs) -> AnalysisResult:
        """Perform comprehensive content quality analysis"""
        
        # Extract content
        text_content = self.extract_text_content(crawl_result)
        html_content = self.extract_html_content(crawl_result)
        
        # Initialize result structure
        scores = {}
        issues = []
        opportunities = []
        metadata = {}
        
        # Analyze different aspects
        readability_data = self._analyze_readability(text_content)
        keyword_data = self._analyze_keyword_optimization(text_content, html_content)
        structure_data = self._analyze_content_structure(html_content)
        freshness_data = self._analyze_content_freshness(text_content, html_content)
        uniqueness_data = self._analyze_content_uniqueness(text_content)
        
        # Collect scores
        scores.update({
            'readability_score': readability_data.get('score', 0),
            'keyword_optimization_score': keyword_data.get('score', 0),
            'content_structure_score': structure_data.get('score', 0),
            'content_freshness_score': freshness_data.get('score', 0),
            'content_uniqueness_score': uniqueness_data.get('score', 0)
        })
        
        # Collect issues
        issues.extend(readability_data.get('issues', []))
        issues.extend(keyword_data.get('issues', []))
        issues.extend(structure_data.get('issues', []))
        issues.extend(freshness_data.get('issues', []))
        issues.extend(uniqueness_data.get('issues', []))
        
        # Collect opportunities
        opportunities.extend(readability_data.get('opportunities', []))
        opportunities.extend(keyword_data.get('opportunities', []))
        opportunities.extend(structure_data.get('opportunities', []))
        
        # Calculate overall content quality score
        overall_score = sum(scores.values()) / len(scores) if scores else 0
        scores['overall_content_quality'] = overall_score
        
        # Collect metadata
        metadata.update({
            'word_count': len(re.findall(r'\b\w+\b', text_content)),
            'character_count': len(text_content),
            'reading_time_minutes': self.extractor.detect_content_type(text_content).get('reading_time_minutes', 0),
            'content_type': self.extractor.detect_content_type(text_content),
            'top_keywords': self.extractor.extract_keywords(text_content, 'it', 5),
            'entities': self.extractor.extract_entities(text_content)
        })
        
        return AnalysisResult(scores=scores, issues=issues, opportunities=opportunities, metadata=metadata)
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability and complexity"""
        result = {'score': 0, 'issues': [], 'opportunities': []}
        
        if not text or len(text) < 100:
            result['issues'].append(
                self.create_issue(
                    'insufficient_content', 'high', 'content_quality',
                    'Contenuto Insufficiente', 'Il contenuto è troppo breve per l\'analisi',
                    'Aggiungi più contenuto testuale (minimo 100 caratteri)',
                    seo_config.scoring_weights.get('thin_content', -5.0)
                )
            )
            return result
        
        # Calculate readability scores
        flesch_kincaid = self.extractor.calculate_readability_score(text, 'flesch_kincaid')
        flesch_ease = self.extractor.calculate_readability_score(text, 'flesch_reading_ease')
        
        # Evaluate Flesch-Kincaid (lower is better for general audience)
        if flesch_kincaid > seo_config.readability_max_score:
            result['issues'].append(
                self.create_issue(
                    'poor_readability', 'medium', 'content_quality',
                    'Testo Troppo Complesso', 
                    f'Il testo ha un livello di lettura troppo alto ({flesch_kincaid:.1f})',
                    f'Semplifica il linguaggio per un pubblico più ampio (target: {seo_config.readability_min_score}-{seo_config.readability_max_score})',
                    seo_config.scoring_weights.get('poor_readability', -4.0)
                )
            )
            score = 40
        elif flesch_kincaid < seo_config.readability_min_score:
            result['opportunities'].append(
                self.create_opportunity(
                    'Content Readability', 'Arricchisci il vocabolario',
                    'Il testo potrebbe beneficiare di un linguaggio più ricco',
                    'Low', 'Medium', 'Usa sinonimi e variazioni linguistiche appropriate'
                )
            )
            score = 80
        else:
            score = 100
        
        # Evaluate sentence structure
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = len(re.findall(r'\b\w+\b', text)) / len(sentences)
            
            if avg_sentence_length > 25:
                result['issues'].append(
                    self.create_issue(
                        'long_sentences', 'low', 'content_quality',
                        'Frasi Troppo Lunghe',
                        f'La lunghezza media delle frasi è alta ({avg_sentence_length:.1f} parole)',
                        'Usa frasi più brevi per migliorare la leggibilità',
                        -2.0
                    )
                )
                score = min(score, 75)
        
        result['score'] = score
        return result
    
    def _analyze_keyword_optimization(self, text: str, html: str) -> Dict[str, Any]:
        """Analyze keyword usage and optimization"""
        result = {'score': 80, 'issues': [], 'opportunities': []}
        
        if not text:
            return result
        
        # Extract top keywords
        keywords = self.extractor.extract_keywords(text, 'it', 10)
        
        if not keywords:
            result['issues'].append(
                self.create_issue(
                    'no_clear_keywords', 'medium', 'content_quality',
                    'Nessuna Parola Chiave Identificata',
                    'Non sono state identificate parole chiave principali nel contenuto',
                    'Ottimizza il contenuto per parole chiave specifiche',
                    -3.0
                )
            )
            result['score'] = 40
            return result
        
        # Check keyword density for top keyword
        top_keyword = keywords[0][0]
        density = self.extractor.calculate_keyword_density(text, top_keyword)
        
        if density > seo_config.keyword_density_max:
            result['issues'].append(
                self.create_issue(
                    'keyword_stuffing', 'high', 'content_quality',
                    'Keyword Stuffing Rilevato',
                    f'La densità della parola chiave "{top_keyword}" è troppo alta ({density:.1f}%)',
                    f'Riduci la densità sotto il {seo_config.keyword_density_max}% per evitare penalizzazioni',
                    seo_config.scoring_weights.get('keyword_stuffing', -6.0)
                )
            )
            result['score'] = 30
        elif density < 0.5:
            result['opportunities'].append(
                self.create_opportunity(
                    'Keyword Optimization', 'Aumenta la densità delle parole chiave',
                    f'La parola chiave principale "{top_keyword}" potrebbe essere usata più frequentemente',
                    'Medium', 'Low', 'Includi la parola chiave in modo naturale nel contenuto'
                )
            )
        
        # Check keyword placement in important elements
        if html:
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
            
            keyword_in_title = bool(title_match and top_keyword.lower() in title_match.group(1).lower())
            keyword_in_h1 = bool(h1_match and top_keyword.lower() in h1_match.group(1).lower())
            
            if not keyword_in_title:
                result['opportunities'].append(
                    self.create_opportunity(
                        'Title Optimization', 'Includi la parola chiave nel title',
                        'La parola chiave principale non è presente nel tag title',
                        'High', 'Low', 'Aggiungi la parola chiave nel title tag'
                    )
                )
            
            if not keyword_in_h1:
                result['opportunities'].append(
                    self.create_opportunity(
                        'H1 Optimization', 'Includi la parola chiave nell\'H1',
                        'La parola chiave principale non è presente nell\'H1',
                        'High', 'Low', 'Aggiungi la parola chiave nell\'H1'
                    )
                )
        
        return result
    
    def _analyze_content_structure(self, html: str) -> Dict[str, Any]:
        """Analyze content structure and organization"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        if not html:
            return result
        
        # Extract text blocks
        text_blocks = self.extractor.extract_text_blocks(html)
        
        # Count different types of content
        headings = [block for block in text_blocks if block['type'].startswith('heading_')]
        paragraphs = [block for block in text_blocks if block['type'] == 'paragraph']
        lists = [block for block in text_blocks if block['type'] == 'list_item']
        
        # Check heading structure
        if not headings:
            result['issues'].append(
                self.create_issue(
                    'no_headings', 'medium', 'content_quality',
                    'Mancanza di Struttura',
                    'Il contenuto non ha headings per organizzare l\'informazione',
                    'Aggiungi headings (H2, H3, etc.) per strutturare il contenuto',
                    -3.0
                )
            )
            result['score'] = 60
        
        # Check paragraph length
        if paragraphs:
            long_paragraphs = [p for p in paragraphs if p['length'] > 300]
            if long_paragraphs:
                result['opportunities'].append(
                    self.create_opportunity(
                        'Content Structure', 'Dividi i paragrafi lunghi',
                        f'{len(long_paragraphs)} paragrafi sono molto lunghi',
                        'Medium', 'Low', 'Dividi paragrafi lunghi per migliorare la leggibilità'
                    )
                )
        
        # Check for lists (good for structure)
        if not lists and len(paragraphs) > 5:
            result['opportunities'].append(
                self.create_opportunity(
                    'Content Format', 'Aggiungi liste puntate',
                    'Il contenuto potrebbe beneficiare di liste per migliorare la scansionabilità',
                    'Low', 'Low', 'Converti alcune informazioni in liste puntate o numerate'
                )
            )
        
        # Check internal linking
        internal_links = re.findall(r'<a[^>]*href=["\'](?!http|mailto|tel)([^"\']+)["\'][^>]*>', html)
        if not internal_links:
            result['issues'].append(
                self.create_issue(
                    'missing_internal_links', 'low', 'content_quality',
                    'Mancanza di Link Interni',
                    'La pagina non contiene link interni ad altre pagine del sito',
                    'Aggiungi link interni rilevanti per migliorare la navigazione e il SEO',
                    seo_config.scoring_weights.get('missing_internal_links', -2.0)
                )
            )
            result['score'] = min(result['score'], 80)
        
        return result
    
    def _analyze_content_freshness(self, text: str, html: str) -> Dict[str, Any]:
        """Analyze content freshness and date indicators"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        # Look for date patterns in content
        date_patterns = [
            r'\b(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+\d{4}\b',
            r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{4}\b',
            r'\b(202[0-4])\b'  # Recent years
        ]
        
        found_dates = []
        for pattern in date_patterns:
            found_dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Look for freshness indicators
        freshness_keywords = [
            'aggiornato', 'ultimo', 'recente', 'nuovo', 'attuale', 'oggi',
            'updated', 'latest', 'recent', 'new', 'current', 'today'
        ]
        
        freshness_signals = sum(1 for keyword in freshness_keywords if keyword in text.lower())
        
        if not found_dates and freshness_signals < 2:
            result['opportunities'].append(
                self.create_opportunity(
                    'Content Freshness', 'Aggiungi indicatori di freschezza',
                    'Il contenuto non mostra chiari indicatori di quando è stato aggiornato',
                    'Medium', 'Low', 'Aggiungi date di pubblicazione/aggiornamento e indicatori di freschezza'
                )
            )
            result['score'] = 80
        
        # Check for outdated references (basic heuristic)
        old_years = re.findall(r'\b(201[0-8])\b', text)
        if old_years and not re.search(r'\b(202[0-4])\b', text):
            result['issues'].append(
                self.create_issue(
                    'outdated_content', 'low', 'content_quality',
                    'Possibili Riferimenti Datati',
                    f'Il contenuto contiene riferimenti a anni passati ({", ".join(set(old_years))})',
                    'Verifica e aggiorna i contenuti con informazioni più recenti',
                    seo_config.scoring_weights.get('outdated_content', -3.0)
                )
            )
            result['score'] = min(result['score'], 70)
        
        return result
    
    def _analyze_content_uniqueness(self, text: str) -> Dict[str, Any]:
        """Analyze content uniqueness and detect potential duplication"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        if not text:
            return result
        
        # Simple duplicate detection based on repeated phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s) > 20]
        
        if sentences:
            # Check for exact duplicate sentences
            sentence_counts = Counter(sentences)
            duplicates = [sent for sent, count in sentence_counts.items() if count > 1]
            
            if duplicates:
                result['issues'].append(
                    self.create_issue(
                        'duplicate_content', 'medium', 'content_quality',
                        'Contenuto Duplicato Interno',
                        f'{len(duplicates)} frasi sono ripetute nel contenuto',
                        'Rimuovi o riformula le frasi duplicate per migliorare l\'unicità',
                        seo_config.scoring_weights.get('duplicate_content', -8.0)
                    )
                )
                result['score'] = 70
            
            # Check for very similar sentence patterns (basic)
            short_sentences = [s for s in sentences if len(s.split()) < 5]
            if len(short_sentences) > len(sentences) * 0.4:
                result['opportunities'].append(
                    self.create_opportunity(
                        'Content Variety', 'Varia la lunghezza delle frasi',
                        'Molte frasi sono molto brevi, considera di variare la lunghezza',
                        'Low', 'Low', 'Alterna frasi brevi e lunghe per migliorare il ritmo'
                    )
                )
        
        return result