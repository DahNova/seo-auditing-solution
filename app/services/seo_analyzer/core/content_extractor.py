"""
Content Extraction Utilities
Shared functions for extracting and analyzing content from crawl results
"""
import re
import math
from typing import List, Dict, Any, Tuple, Optional
from bs4 import BeautifulSoup
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Utility class for content extraction and analysis"""
    
    # Common stop words for content analysis
    STOP_WORDS = {
        'it': {'il', 'la', 'di', 'che', 'e', 'a', 'un', 'per', 'in', 'con', 'su', 'da', 'del', 'al', 'dei', 'le', 'si', 'non', 'una', 'ma', 'anche', 'come', 'più', 'sono', 'molto', 'dalla', 'nel', 'nella', 'alle', 'alla', 'questa', 'questo', 'tutto', 'tutti'},
        'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
    }
    
    @staticmethod
    def extract_text_blocks(html_content: str) -> List[Dict[str, Any]]:
        """Extract meaningful text blocks from HTML"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script, style, nav, footer elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
            element.decompose()
        
        text_blocks = []
        
        # Extract headings
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                text = heading.get_text(strip=True)
                if text:
                    text_blocks.append({
                        'type': f'heading_{level}',
                        'text': text,
                        'length': len(text),
                        'position': len(text_blocks)
                    })
        
        # Extract paragraphs
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Ignore very short paragraphs
                text_blocks.append({
                    'type': 'paragraph',
                    'text': text,
                    'length': len(text),
                    'position': len(text_blocks)
                })
        
        # Extract list items
        for li in soup.find_all('li'):
            text = li.get_text(strip=True)
            if text:
                text_blocks.append({
                    'type': 'list_item',
                    'text': text,
                    'length': len(text),
                    'position': len(text_blocks)
                })
        
        return text_blocks
    
    @staticmethod
    def calculate_readability_score(text: str, method: str = 'flesch_kincaid') -> float:
        """Calculate readability score using various methods"""
        if not text or len(text) < 100:
            return 0.0
        
        # Basic text statistics
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', text.lower())
        syllables = sum(ContentExtractor._count_syllables(word) for word in words)
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        if method == 'flesch_kincaid':
            # Flesch-Kincaid Grade Level
            score = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
            return max(0, min(20, score))  # Clamp between 0-20
        
        elif method == 'flesch_reading_ease':
            # Flesch Reading Ease (0-100, higher is easier)
            score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
            return max(0, min(100, score))
        
        return 0.0
    
    @staticmethod
    def _count_syllables(word: str) -> int:
        """Count syllables in a word (approximation)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllables = 0
        prev_char_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_char_was_vowel:
                    syllables += 1
                prev_char_was_vowel = True
            else:
                prev_char_was_vowel = False
        
        # Handle silent 'e'
        if word.endswith('e') and syllables > 1:
            syllables -= 1
        
        return max(1, syllables)
    
    @staticmethod
    def extract_keywords(text: str, lang: str = 'it', top_n: int = 10) -> List[Tuple[str, int]]:
        """Extract most frequent keywords from text"""
        if not text:
            return []
        
        # Clean and tokenize
        words = re.findall(r'\b\w{3,}\b', text.lower())
        
        # Remove stop words
        stop_words = ContentExtractor.STOP_WORDS.get(lang, set())
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count frequencies
        word_counts = Counter(filtered_words)
        
        return word_counts.most_common(top_n)
    
    @staticmethod
    def calculate_keyword_density(text: str, keyword: str) -> float:
        """Calculate keyword density as percentage"""
        if not text or not keyword:
            return 0.0
        
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        total_words = len(re.findall(r'\b\w+\b', text_lower))
        keyword_count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', text_lower))
        
        if total_words == 0:
            return 0.0
        
        return (keyword_count / total_words) * 100
    
    @staticmethod
    def detect_content_type(text: str) -> Dict[str, Any]:
        """Detect content type and characteristics"""
        if not text:
            return {'type': 'empty', 'confidence': 1.0}
        
        # Length-based classification
        word_count = len(re.findall(r'\b\w+\b', text))
        
        if word_count < 100:
            content_type = 'snippet'
        elif word_count < 500:
            content_type = 'short_form'
        elif word_count < 1500:
            content_type = 'medium_form'
        else:
            content_type = 'long_form'
        
        # Detect commercial intent
        commercial_keywords = [
            'prezzo', 'costo', 'acquista', 'compra', 'vendita', 'offerta', 'sconto',
            'price', 'cost', 'buy', 'purchase', 'sale', 'offer', 'discount'
        ]
        
        commercial_score = 0
        for keyword in commercial_keywords:
            if keyword in text.lower():
                commercial_score += 1
        
        # Detect informational intent
        info_keywords = [
            'come', 'cosa', 'perché', 'quando', 'dove', 'guida', 'tutorial',
            'how', 'what', 'why', 'when', 'where', 'guide', 'tutorial'
        ]
        
        info_score = 0
        for keyword in info_keywords:
            if keyword in text.lower():
                info_score += 1
        
        return {
            'type': content_type,
            'word_count': word_count,
            'commercial_intent': commercial_score / len(commercial_keywords),
            'informational_intent': info_score / len(info_keywords),
            'reading_time_minutes': math.ceil(word_count / 200)  # Average reading speed
        }
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """Extract named entities (basic pattern matching)"""
        entities = {
            'emails': [],
            'phones': [],
            'addresses': [],
            'organizations': [],
            'locations': []
        }
        
        if not text:
            return entities
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = re.findall(email_pattern, text)
        
        # Phone pattern (Italian + international)
        phone_pattern = r'(?:\+39|0039)?[\s\-]?(?:0\d{2,3}[\s\-]?\d{6,7}|\d{3}[\s\-]?\d{3}[\s\-]?\d{4})'
        entities['phones'] = re.findall(phone_pattern, text)
        
        # Simple address pattern
        address_pattern = r'\b(?:via|viale|corso|piazza|largo|strada)\s+[A-Za-z\s,]+\d+\b'
        entities['addresses'] = re.findall(address_pattern, text, re.IGNORECASE)
        
        # Italian city pattern (basic)
        italian_cities = ['Roma', 'Milano', 'Napoli', 'Torino', 'Palermo', 'Genova', 'Bologna', 'Firenze', 'Bari', 'Catania']
        for city in italian_cities:
            if city in text:
                entities['locations'].append(city)
        
        return entities