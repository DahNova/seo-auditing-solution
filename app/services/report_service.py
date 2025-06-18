import tempfile
import os
from datetime import datetime
from typing import List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, red, orange, blue
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

from app.models import Scan, Website, Page, Issue


class ReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF report"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=HexColor('#2c3e50'),
            spaceAfter=30
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#34495e'),
            spaceBefore=20,
            spaceAfter=12
        )
        
        # Summary style
        self.summary_style = ParagraphStyle(
            'Summary',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12
        )
    
    def generate_scan_report(self, scan: Scan, website: Website, pages: List[Page], issues: List[Issue]) -> str:
        """Generate a comprehensive PDF report for a scan"""
        
        # Create temporary file for the PDF
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                temp_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build report content
            content = []
            
            # Title and header
            content.extend(self._build_header(scan, website))
            
            # Executive Summary
            content.extend(self._build_executive_summary(scan, pages, issues))
            
            # Statistics Overview
            content.extend(self._build_statistics_overview(pages, issues))
            
            # Issues Analysis
            content.extend(self._build_issues_analysis(issues))
            
            # Pages Summary
            content.extend(self._build_pages_summary(pages))
            
            # Recommendations
            content.extend(self._build_recommendations(issues))
            
            # Build PDF
            doc.build(content)
            
            return temp_path
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    
    def _build_header(self, scan: Scan, website: Website) -> List:
        """Build report header section"""
        content = []
        
        # Main title
        title = f"Report SEO - {website.domain}"
        content.append(Paragraph(title, self.title_style))
        content.append(Spacer(1, 20))
        
        # Scan details
        scan_date = scan.completed_at.strftime("%d/%m/%Y alle %H:%M") if scan.completed_at else "N/A"
        details = f"""
        <b>Data Scansione:</b> {scan_date}<br/>
        <b>Sito Web:</b> {website.domain}<br/>
        <b>Cliente:</b> {website.client.name if website.client else 'N/A'}<br/>
        <b>Status:</b> {scan.status.title()}
        """
        content.append(Paragraph(details, self.summary_style))
        content.append(Spacer(1, 30))
        
        return content
    
    def _build_executive_summary(self, scan: Scan, pages: List[Page], issues: List[Issue]) -> List:
        """Build executive summary section"""
        content = []
        
        content.append(Paragraph("Riepilogo Esecutivo", self.heading_style))
        
        # Count issues by severity
        issues_by_severity = self._count_issues_by_severity(issues)
        
        # Calculate SEO score (simple algorithm)
        total_issues = len(issues)
        total_pages = len(pages)
        seo_score = max(0, 100 - (total_issues / max(total_pages, 1) * 10))
        
        summary_text = f"""
        La scansione SEO del sito web ha analizzato <b>{total_pages} pagine</b> e identificato 
        <b>{total_issues} problemi</b> da risolvere per migliorare la visibilità sui motori di ricerca.
        <br/><br/>
        <b>Punteggio SEO Stimato:</b> {seo_score:.1f}/100<br/>
        <b>Problemi Critici:</b> {issues_by_severity.get('critical', 0)}<br/>
        <b>Problemi Moderati:</b> {issues_by_severity.get('moderate', 0)}<br/>
        <b>Problemi Minori:</b> {issues_by_severity.get('minor', 0)}
        """
        
        content.append(Paragraph(summary_text, self.summary_style))
        content.append(Spacer(1, 20))
        
        return content
    
    def _build_statistics_overview(self, pages: List[Page], issues: List[Issue]) -> List:
        """Build statistics overview section"""
        content = []
        
        content.append(Paragraph("Panoramica Statistiche", self.heading_style))
        
        # Create statistics table
        stats_data = [
            ['Metrica', 'Valore'],
            ['Pagine Analizzate', str(len(pages))],
            ['Problemi Totali', str(len(issues))],
            ['Pagine con Errori', str(sum(1 for page in pages if page.status_code != 200))],
            ['Pagine Senza Titolo', str(sum(1 for page in pages if not page.title))],
            ['Tempo Medio Risposta', f"{self._calculate_avg_response_time(pages):.2f}ms"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(stats_table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _build_issues_analysis(self, issues: List[Issue]) -> List:
        """Build issues analysis section"""
        content = []
        
        content.append(Paragraph("Analisi Problemi SEO", self.heading_style))
        
        if not issues:
            content.append(Paragraph("Nessun problema rilevato.", self.summary_style))
            return content
        
        # Group issues by type and severity
        issues_by_type = {}
        for issue in issues[:50]:  # Limit to first 50 issues for PDF size
            issue_type = issue.type or 'Altro'
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # Create issues table
        issues_data = [['Tipo', 'Livello', 'Descrizione', 'Pagina']]
        
        for issue_type, type_issues in issues_by_type.items():
            for issue in type_issues[:10]:  # Limit per type
                severity_color = self._get_severity_color(issue.severity)
                page_url = issue.page.url if issue.page else 'N/A'
                # Truncate URL for display
                display_url = page_url[:40] + '...' if len(page_url) > 40 else page_url
                
                issues_data.append([
                    issue_type,
                    issue.severity.title() if issue.severity else 'N/A',
                    issue.description[:60] + '...' if len(issue.description or '') > 60 else (issue.description or 'N/A'),
                    display_url
                ])
        
        issues_table = Table(issues_data, colWidths=[1.5*inch, 1*inch, 2.5*inch, 2*inch])
        issues_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        content.append(issues_table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _build_pages_summary(self, pages: List[Page]) -> List:
        """Build pages summary section"""
        content = []
        
        content.append(Paragraph("Riepilogo Pagine", self.heading_style))
        
        if not pages:
            content.append(Paragraph("Nessuna pagina analizzata.", self.summary_style))
            return content
        
        # Create pages table (top 20 pages)
        pages_data = [['URL', 'Status', 'Titolo', 'Problemi']]
        
        for page in pages[:20]:  # Limit to first 20 pages
            status_code = str(page.status_code) if page.status_code else 'N/A'
            title = page.title[:40] + '...' if len(page.title or '') > 40 else (page.title or 'N/A')
            url = page.url[:50] + '...' if len(page.url) > 50 else page.url
            issues_count = str(page.issues_count or 0)
            
            pages_data.append([url, status_code, title, issues_count])
        
        pages_table = Table(pages_data, colWidths=[3*inch, 0.7*inch, 2.5*inch, 0.8*inch])
        pages_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        content.append(pages_table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _build_recommendations(self, issues: List[Issue]) -> List:
        """Build recommendations section"""
        content = []
        
        content.append(Paragraph("Raccomandazioni", self.heading_style))
        
        # Generic recommendations based on issues found
        recommendations = []
        
        if any(issue.type == 'meta' for issue in issues):
            recommendations.append("• Ottimizzare i meta tag (title, description) per migliorare la visibilità sui motori di ricerca")
        
        if any(issue.type == 'heading' for issue in issues):
            recommendations.append("• Ristrutturare la gerarchia dei titoli (H1, H2, H3) per migliorare la struttura del contenuto")
        
        if any(issue.type == 'image' for issue in issues):
            recommendations.append("• Aggiungere testi alternativi (alt text) alle immagini per migliorare l'accessibilità")
        
        if any(issue.type == 'link' for issue in issues):
            recommendations.append("• Controllare e correggere i link non funzionanti")
        
        if any(issue.severity == 'critical' for issue in issues):
            recommendations.append("• Dare priorità alla risoluzione dei problemi critici")
        
        if not recommendations:
            recommendations.append("• Continuare a monitorare regolarmente il sito per mantenere buone performance SEO")
        
        recommendations_text = "<br/>".join(recommendations)
        content.append(Paragraph(recommendations_text, self.summary_style))
        
        # Add footer
        content.append(Spacer(1, 30))
        footer_text = f"Report generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} - SEO Auditing Solution"
        footer_style = ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey)
        content.append(Paragraph(footer_text, footer_style))
        
        return content
    
    def _count_issues_by_severity(self, issues: List[Issue]) -> dict:
        """Count issues by severity level"""
        count = {}
        for issue in issues:
            severity = issue.severity or 'unknown'
            count[severity] = count.get(severity, 0) + 1
        return count
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        color_map = {
            'critical': '#e74c3c',
            'moderate': '#f39c12',
            'minor': '#3498db'
        }
        return color_map.get(severity, '#95a5a6')
    
    def _calculate_avg_response_time(self, pages: List[Page]) -> float:
        """Calculate average response time"""
        response_times = [page.response_time for page in pages if page.response_time is not None]
        return sum(response_times) / len(response_times) if response_times else 0.0