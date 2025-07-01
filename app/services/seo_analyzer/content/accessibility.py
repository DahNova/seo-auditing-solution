"""
Accessibility Analyzer
WCAG compliance and accessibility analysis for better SEO and user experience
"""
from typing import Dict, List, Any, Optional, Tuple
import re
from bs4 import BeautifulSoup

from ..core.base_analyzer import BaseAnalyzer, AnalysisResult
from app.core.config import seo_config

class AccessibilityAnalyzer(BaseAnalyzer):
    """Analyzes accessibility compliance and UX factors"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # WCAG guidelines mapping
        self.wcag_checks = {
            'alt_text': {'level': 'A', 'guideline': '1.1.1'},
            'color_contrast': {'level': 'AA', 'guideline': '1.4.3'},
            'keyboard_navigation': {'level': 'A', 'guideline': '2.1.1'},
            'focus_indicators': {'level': 'AA', 'guideline': '2.4.7'},
            'headings_hierarchy': {'level': 'AA', 'guideline': '1.3.1'},
            'form_labels': {'level': 'A', 'guideline': '1.3.1'},
            'link_purpose': {'level': 'AA', 'guideline': '2.4.4'},
            'language_declaration': {'level': 'A', 'guideline': '3.1.1'}
        }
    
    def analyze(self, crawl_result, **kwargs) -> AnalysisResult:
        """Perform comprehensive accessibility analysis"""
        
        html_content = self.extract_html_content(crawl_result)
        text_content = self.extract_text_content(crawl_result)
        
        scores = {}
        issues = []
        opportunities = []
        metadata = {}
        
        if not html_content:
            return AnalysisResult(scores={'accessibility_score': 0}, issues=[], opportunities=[], metadata={})
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Perform different accessibility checks
        alt_text_data = self._check_alt_text(soup)
        color_contrast_data = self._check_color_contrast(html_content)
        keyboard_nav_data = self._check_keyboard_navigation(soup)
        form_accessibility_data = self._check_form_accessibility(soup)
        heading_structure_data = self._check_heading_structure(soup)
        link_accessibility_data = self._check_link_accessibility(soup)
        language_data = self._check_language_declaration(soup)
        aria_data = self._check_aria_attributes(soup)
        
        # Collect scores
        scores.update({
            'alt_text_score': alt_text_data.get('score', 0),
            'color_contrast_score': color_contrast_data.get('score', 0),
            'keyboard_navigation_score': keyboard_nav_data.get('score', 0),
            'form_accessibility_score': form_accessibility_data.get('score', 0),
            'heading_structure_score': heading_structure_data.get('score', 0),
            'link_accessibility_score': link_accessibility_data.get('score', 0),
            'language_score': language_data.get('score', 0),
            'aria_score': aria_data.get('score', 0)
        })
        
        # Collect issues
        issues.extend(alt_text_data.get('issues', []))
        issues.extend(color_contrast_data.get('issues', []))
        issues.extend(keyboard_nav_data.get('issues', []))
        issues.extend(form_accessibility_data.get('issues', []))
        issues.extend(heading_structure_data.get('issues', []))
        issues.extend(link_accessibility_data.get('issues', []))
        issues.extend(language_data.get('issues', []))
        issues.extend(aria_data.get('issues', []))
        
        # Collect opportunities
        opportunities.extend(alt_text_data.get('opportunities', []))
        opportunities.extend(color_contrast_data.get('opportunities', []))
        opportunities.extend(keyboard_nav_data.get('opportunities', []))
        opportunities.extend(form_accessibility_data.get('opportunities', []))
        
        # Calculate overall accessibility score
        overall_score = sum(scores.values()) / len(scores) if scores else 0
        scores['overall_accessibility'] = overall_score
        
        # Collect metadata
        metadata.update({
            'wcag_level': self._determine_wcag_level(scores),
            'accessibility_features_count': len([s for s in scores.values() if s > 80]),
            'critical_issues_count': len([i for i in issues if i.get('severity') == 'critical']),
            'compliance_percentage': overall_score
        })
        
        return AnalysisResult(scores=scores, issues=issues, opportunities=opportunities, metadata=metadata)
    
    def _check_alt_text(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Check image alt text compliance"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        images = soup.find_all('img')
        if not images:
            return result
        
        missing_alt = []
        empty_alt = []
        good_alt = []
        
        for img in images:
            alt_text = img.get('alt')
            src = img.get('src', 'unknown')
            
            if alt_text is None:
                missing_alt.append(src)
            elif not alt_text.strip():
                empty_alt.append(src)
            else:
                # Check alt text quality
                if len(alt_text) < 10:
                    empty_alt.append(src)  # Too short
                else:
                    good_alt.append(src)
        
        total_images = len(images)
        issues_count = len(missing_alt) + len(empty_alt)
        
        # NOTE: Alt text issues are now handled by IssueDetector with granular format
        # No need to create duplicate legacy issues here
        
        # NOTE: Poor alt text issues are also handled by IssueDetector with granular format
        # No need to create duplicate legacy issues here
        
        # Calculate score
        if total_images > 0:
            compliance_rate = (total_images - issues_count) / total_images
            result['score'] = compliance_rate * 100
        
        if issues_count == 0 and len(good_alt) > 0:
            result['opportunities'].append(
                self.create_opportunity(
                    'Image Optimization', 'Ottimizza ulteriormente le immagini',
                    'Tutte le immagini hanno alt text, considera l\'ottimizzazione per SEO',
                    'Low', 'Low', 'Includi parole chiave rilevanti negli alt text dove appropriato'
                )
            )
        
        return result
    
    def _check_color_contrast(self, html_content: str) -> Dict[str, Any]:
        """Check color contrast ratios (basic analysis)"""
        result = {'score': 85, 'issues': [], 'opportunities': []}  # Default good score
        
        # Look for inline styles that might indicate poor contrast
        inline_styles = re.findall(r'style=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        
        poor_contrast_patterns = [
            r'color:\s*#?([a-f0-9]{3,6}).*background[-\w]*:\s*#?([a-f0-9]{3,6})',
            r'background[-\w]*:\s*#?([a-f0-9]{3,6}).*color:\s*#?([a-f0-9]{3,6})'
        ]
        
        contrast_issues = 0
        for style in inline_styles:
            for pattern in poor_contrast_patterns:
                matches = re.findall(pattern, style, re.IGNORECASE)
                for match in matches:
                    # Basic heuristic for poor contrast
                    color1 = match[0].lower()
                    color2 = match[1].lower()
                    
                    # Check for obviously poor combinations
                    if (color1 in ['fff', 'ffffff', 'white'] and color2 in ['ff0', 'ffff00', 'yellow']) or \
                       (color1 in ['000', '000000', 'black'] and color2 in ['333', '333333']):
                        contrast_issues += 1
        
        if contrast_issues > 0:
            result['issues'].append(
                self.create_issue(
                    'poor_color_contrast', 'medium', 'accessibility',
                    'Possibili Problemi di Contrasto',
                    f'Rilevate {contrast_issues} possibili combinazioni di colori problematiche',
                    f'Verifica che il contrasto rispetti il ratio minimo {seo_config.min_color_contrast_ratio}:1 (WCAG 1.4.3)',
                    seo_config.scoring_weights.get('poor_color_contrast', -3.0)
                )
            )
            result['score'] = 60
        
        # Check for CSS that might help with contrast
        if 'contrast(' in html_content or 'filter:' in html_content:
            result['opportunities'].append(
                self.create_opportunity(
                    'Contrast Enhancement', 'Ottimizza i filtri CSS',
                    'Sono presenti filtri CSS, verifica che migliorino effettivamente il contrasto',
                    'Low', 'Low', 'Testa i filtri CSS con strumenti di accessibilità'
                )
            )
        
        return result
    
    def _check_keyboard_navigation(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Check keyboard navigation support"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        # Check for interactive elements without proper keyboard support
        interactive_elements = soup.find_all(['button', 'a', 'input', 'textarea', 'select'])
        
        missing_tabindex = []
        good_elements = []
        
        for element in interactive_elements:
            tag_name = element.name
            
            # Links should have href or proper role
            if tag_name == 'a':
                if not element.get('href') and not element.get('role'):
                    missing_tabindex.append(f'Link senza href: {element.get_text()[:30]}...')
                else:
                    good_elements.append(element)
            
            # Buttons should be properly marked
            elif tag_name == 'button':
                good_elements.append(element)
            
            # Form elements
            elif tag_name in ['input', 'textarea', 'select']:
                good_elements.append(element)
        
        # Check for click handlers on non-interactive elements
        clickable_divs = soup.find_all('div', attrs={'onclick': True})
        clickable_spans = soup.find_all('span', attrs={'onclick': True})
        
        non_accessible_clickables = len(clickable_divs) + len(clickable_spans)
        
        if missing_tabindex:
            result['issues'].append(
                self.create_issue(
                    'keyboard_navigation_issues', 'medium', 'accessibility',
                    'Problemi Navigazione da Tastiera',
                    f'{len(missing_tabindex)} elementi interattivi potrebbero non essere accessibili da tastiera',
                    'Assicurati che tutti gli elementi interattivi siano accessibili tramite tastiera (WCAG 2.1.1)',
                    seo_config.scoring_weights.get('keyboard_navigation_issues', -3.0)
                )
            )
            result['score'] = 70
        
        if non_accessible_clickables > 0:
            result['issues'].append(
                self.create_issue(
                    'non_accessible_clickables', 'high', 'accessibility',
                    'Elementi Clickabili Non Accessibili',
                    f'{non_accessible_clickables} div/span con onclick non accessibili da tastiera',
                    'Usa elementi button o aggiungi attributi tabindex e role appropriati',
                    -4.0
                )
            )
            result['score'] = min(result['score'], 60)
        
        if len(good_elements) > 5 and not missing_tabindex:
            result['opportunities'].append(
                self.create_opportunity(
                    'Keyboard Navigation', 'Aggiungi skip links',
                    'La pagina ha molti elementi interattivi, considera l\'aggiunta di skip links',
                    'Medium', 'Low', 'Aggiungi link "Vai al contenuto principale" per migliorare la navigazione'
                )
            )
        
        return result
    
    def _check_form_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Check form accessibility compliance"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        forms = soup.find_all('form')
        if not forms:
            return result
        
        total_inputs = 0
        inputs_with_labels = 0
        
        for form in forms:
            inputs = form.find_all(['input', 'textarea', 'select'])
            
            for input_elem in inputs:
                total_inputs += 1
                input_id = input_elem.get('id')
                input_name = input_elem.get('name')
                
                # Check for associated label
                if input_id:
                    label = form.find('label', attrs={'for': input_id})
                    if label:
                        inputs_with_labels += 1
                        continue
                
                # Check for aria-label
                if input_elem.get('aria-label') or input_elem.get('aria-labelledby'):
                    inputs_with_labels += 1
                    continue
                
                # Check for placeholder as fallback (not ideal but better than nothing)
                if input_elem.get('placeholder'):
                    inputs_with_labels += 0.5  # Half credit for placeholder
        
        if total_inputs > 0:
            label_compliance = inputs_with_labels / total_inputs
            result['score'] = label_compliance * 100
            
            if label_compliance < 0.8:
                missing_labels = total_inputs - int(inputs_with_labels)
                result['issues'].append(
                    self.create_issue(
                        'etichette_form_mancanti', 'high', 'accessibility',
                        'Etichette Form Mancanti',
                        f'{missing_labels} campi form senza etichette appropriate',
                        'Associa ogni campo form con una label usando for/id o aria-label (WCAG 1.3.1)',
                        -4.0
                    )
                )
        
        # Check for form validation messages
        error_elements = soup.find_all(attrs={'role': 'alert'}) + soup.find_all(class_=re.compile('error|invalid'))
        if not error_elements and total_inputs > 2:
            result['opportunities'].append(
                self.create_opportunity(
                    'Form Validation', 'Implementa messaggi di errore accessibili',
                    'I form potrebbero beneficiare di messaggi di errore accessibili',
                    'Medium', 'Medium', 'Aggiungi role="alert" e aria-live per i messaggi di validazione'
                )
            )
        
        return result
    
    def _check_heading_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Check heading hierarchy for accessibility"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                headings.append({
                    'level': level,
                    'text': heading.get_text(strip=True),
                    'element': heading
                })
        
        if not headings:
            result['issues'].append(
                self.create_issue(
                    'no_heading_structure', 'medium', 'accessibility',
                    'Mancanza Struttura Headings',
                    'La pagina non ha una struttura di headings per la navigazione',
                    'Aggiungi headings (H1-H6) per migliorare la navigazione assistiva (WCAG 1.3.1)',
                    -3.0
                )
            )
            result['score'] = 60
            return result
        
        # Check for proper hierarchy
        hierarchy_issues = []
        prev_level = 0
        
        for heading in headings:
            current_level = heading['level']
            
            # Check for skipped levels
            if current_level > prev_level + 1 and prev_level > 0:
                hierarchy_issues.append(f'Salto da H{prev_level} a H{current_level}')
            
            prev_level = current_level
        
        if hierarchy_issues:
            result['issues'].append(
                self.create_issue(
                    'broken_heading_hierarchy', 'medium', 'accessibility',
                    'Gerarchia Headings Interrotta',
                    f'Problemi nella gerarchia: {", ".join(hierarchy_issues)}',
                    'Mantieni una gerarchia logica dei headings senza saltare livelli',
                    -2.0
                )
            )
            result['score'] = 75
        
        return result
    
    def _check_link_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Check link accessibility and purpose clarity"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        links = soup.find_all('a', href=True)
        if not links:
            return result
        
        vague_links = []
        good_links = []
        
        vague_patterns = [
            r'^(clicca qui|click here|leggi di più|read more|qui|here|more)$',
            r'^(continua|continue|vai|go|vedi|see)$'
        ]
        
        for link in links:
            link_text = link.get_text(strip=True).lower()
            
            # Check for vague link text
            is_vague = any(re.match(pattern, link_text, re.IGNORECASE) for pattern in vague_patterns)
            
            if is_vague:
                vague_links.append(link_text)
            elif len(link_text) > 3:  # Reasonable link text
                good_links.append(link)
        
        if vague_links:
            result['issues'].append(
                self.create_issue(
                    'vague_link_text', 'medium', 'accessibility',
                    'Testo Link Non Descrittivo',
                    f'{len(vague_links)} link con testo generico ({", ".join(set(vague_links))})',
                    'Usa testi link descrittivi che spiegano la destinazione (WCAG 2.4.4)',
                    -2.0
                )
            )
            result['score'] = 70
        
        # Check for external links without indication
        external_links = [link for link in links if link.get('href', '').startswith('http')]
        external_without_indication = [
            link for link in external_links 
            if not link.get('target') and not link.get('aria-label') and 'external' not in link.get('class', [])
        ]
        
        if external_without_indication:
            result['opportunities'].append(
                self.create_opportunity(
                    'External Links', 'Indica i link esterni',
                    f'{len(external_without_indication)} link esterni senza indicazione',
                    'Low', 'Low', 'Aggiungi target="_blank" e aria-label per i link esterni'
                )
            )
        
        return result
    
    def _check_language_declaration(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Check for proper language declaration"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        html_tag = soup.find('html')
        
        if not html_tag or not html_tag.get('lang'):
            result['issues'].append(
                self.create_issue(
                    'missing_language_declaration', 'medium', 'accessibility',
                    'Dichiarazione Lingua Mancante',
                    'Tag HTML senza attributo lang',
                    'Aggiungi lang="it" (o lingua appropriata) al tag HTML (WCAG 3.1.1)',
                    -2.0
                )
            )
            result['score'] = 70
        
        return result
    
    def _check_aria_attributes(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Check for proper ARIA attributes usage"""
        result = {'score': 100, 'issues': [], 'opportunities': []}
        
        # Find elements with ARIA attributes
        aria_elements = soup.find_all(attrs={'role': True})
        aria_elements.extend(soup.find_all(attrs=lambda x: x and isinstance(x, dict) and any(k.startswith('aria-') for k in x.keys())))
        
        if aria_elements:
            # Good! ARIA is being used
            result['score'] = 100
            
            # Check for common ARIA patterns
            landmarks = soup.find_all(attrs={'role': re.compile('banner|navigation|main|complementary|contentinfo')})
            if landmarks:
                result['opportunities'].append(
                    self.create_opportunity(
                        'ARIA Landmarks', 'Ottima implementazione ARIA',
                        'La pagina usa landmarks ARIA per la navigazione assistiva',
                        'High', 'Completed', 'Continua a mantenere questa buona pratica'
                    )
                )
        else:
            # No ARIA, but might not be critical
            result['score'] = 85
            result['opportunities'].append(
                self.create_opportunity(
                    'ARIA Enhancement', 'Considera l\'aggiunta di ARIA',
                    'La pagina potrebbe beneficiare di attributi ARIA per migliorare l\'accessibilità',
                    'Medium', 'Medium', 'Aggiungi role, aria-label, e altri attributi ARIA dove appropriato'
                )
            )
        
        return result
    
    def _determine_wcag_level(self, scores: Dict[str, float]) -> str:
        """Determine WCAG compliance level based on scores"""
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        
        if avg_score >= 95:
            return 'AAA'
        elif avg_score >= 85:
            return 'AA'
        elif avg_score >= 70:
            return 'A'
        else:
            return 'Non-compliant'