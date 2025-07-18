"""
Scan Results Template Router - Optimized and Modularized
Handles the complex scan results page with performance optimizations
"""

from fastapi import Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple

from app.database import get_db
from app.services.seo_analyzer.core.resource_details import IssueFactory
from app.models import Client, Website, Scan, Issue, Page

logger = logging.getLogger(__name__)

# Template configuration
# Path calculation: from app/routers/templates/scan_results.py to app/templates/
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=template_dir)

# Performance constants
MAX_ISSUES_FOR_UI = 2000
CRITICAL_ISSUE_RATIO = 0.40


def _calculate_avg_load_time(pages: List[Page]) -> float:
    """Calculate average load time from pages core web vitals data"""
    load_times = []
    
    for page in pages:
        if page.core_web_vitals:
            # Try to get TTFB (Time to First Byte) from core web vitals
            ttfb = page.core_web_vitals.get('ttfb')
            if ttfb and isinstance(ttfb, (int, float)) and ttfb > 0:
                load_times.append(ttfb / 1000)  # Convert ms to seconds
            
            # Fallback to LCP (Largest Contentful Paint) if TTFB not available
            elif page.core_web_vitals.get('lcp'):
                lcp = page.core_web_vitals.get('lcp')
                if isinstance(lcp, (int, float)) and lcp > 0:
                    load_times.append(lcp / 1000)  # Convert ms to seconds
    
    # Return average or fallback to reasonable default
    if load_times:
        return round(sum(load_times) / len(load_times), 2)
    return 0.0  # No performance data available


def _calculate_avg_page_size(pages: List[Page]) -> int:
    """Calculate average page size from pages performance data"""
    page_sizes = []
    
    for page in pages:
        if page.core_web_vitals:
            # Try to get page size from technical SEO data
            if page.technical_seo_data and 'page_size' in page.technical_seo_data:
                size = page.technical_seo_data['page_size']
                if isinstance(size, (int, float)) and size > 0:
                    page_sizes.append(int(size))
            
            # Fallback: estimate from content length if available
            elif page.technical_seo_data and 'content_length' in page.technical_seo_data:
                length = page.technical_seo_data['content_length']
                if isinstance(length, (int, float)) and length > 0:
                    page_sizes.append(int(length))
    
    # Return average or fallback to reasonable default
    if page_sizes:
        return int(sum(page_sizes) / len(page_sizes))
    return 0  # No size data available


HIGH_ISSUE_RATIO = 0.35
MEDIUM_ISSUE_RATIO = 0.20
LOW_ISSUE_RATIO = 0.05

async def scan_results_handler(
    request: Request, 
    scan_id: int, 
    page: int = 1,
    per_page: int = 50,
    db: AsyncSession = Depends(get_db)
) -> HTMLResponse:
    """
    Optimized scan results handler - modularized and performance-optimized
    """
    
    # Validate parameters
    if per_page not in [25, 50, 100, 200]:
        per_page = 50
    if page < 1:
        page = 1
    
    try:
        # Get scan with related data
        scan_result = await db.execute(
            select(Scan, Website.name.label('website_name'), Client.name.label('client_name'))
            .join(Website, Scan.website_id == Website.id)
            .join(Client, Website.client_id == Client.id)
            .where(Scan.id == scan_id)
        )
        scan_data = scan_result.first()
        
        if not scan_data:
            raise HTTPException(status_code=404, detail="Scan not found")
            
        scan, website_name, client_name = scan_data
        
        # Get total pages count first
        total_pages_result = await db.execute(
            select(func.count(Page.id)).where(Page.scan_id == scan_id)
        )
        total_pages_count = total_pages_result.scalar() or 0
        
        # Calculate pagination
        offset = (page - 1) * per_page
        total_pages_pagination = (total_pages_count + per_page - 1) // per_page
        
        # Get paginated pages with Core Web Vitals and Technical SEO data
        pages_result = await db.execute(
            select(Page).where(Page.scan_id == scan_id)
            .order_by(Page.seo_score.desc().nulls_last(), Page.url)
            .offset(offset)
            .limit(per_page)
        )
        pages = pages_result.scalars().all()
        
        # Calculate overall Core Web Vitals scores for the scan
        all_pages_result = await db.execute(
            select(Page).where(Page.scan_id == scan_id)
        )
        all_pages = all_pages_result.scalars().all()
        
        # Create complete page_id → URL mapping for ALL pages in scan
        page_url_mapping = {page.id: page.url for page in all_pages}
        
        # Get optimized issues with smart distribution for large scans
        total_issues_count = await db.scalar(
            select(func.count(Issue.id)).join(Page).where(Page.scan_id == scan_id)
        )
        
        if total_issues_count > MAX_ISSUES_FOR_UI:
            logger.warning(f"Scan {scan_id} has {total_issues_count} issues. Loading limited set ({MAX_ISSUES_FOR_UI}) with smart distribution for performance.")
            
            # Smart distribution loading
            issues_raw = []
            
            # Load critical issues (40%) with eager loading
            critical_limit = int(MAX_ISSUES_FOR_UI * CRITICAL_ISSUE_RATIO)
            critical_result = await db.execute(
                select(Issue).join(Page)
                .where(Page.scan_id == scan_id, Issue.severity == 'critical')
                .options(selectinload(Issue.page))  # Prevent N+1 queries
                .order_by(func.length(Issue.element).desc(), Issue.id)
                .limit(critical_limit)
            )
            critical_issues = critical_result.scalars().all()
            issues_raw.extend(critical_issues)
            
            # Load high severity issues (35%) with eager loading
            high_limit = int(MAX_ISSUES_FOR_UI * HIGH_ISSUE_RATIO)
            high_result = await db.execute(
                select(Issue).join(Page)
                .where(Page.scan_id == scan_id, Issue.severity == 'high')
                .options(selectinload(Issue.page))  # Prevent N+1 queries
                .order_by(func.length(Issue.element).desc(), Issue.id)
                .limit(high_limit)
            )
            high_issues = high_result.scalars().all()
            issues_raw.extend(high_issues)
            
            # Load medium severity issues (20%) with eager loading
            medium_limit = int(MAX_ISSUES_FOR_UI * MEDIUM_ISSUE_RATIO)
            medium_result = await db.execute(
                select(Issue).join(Page)
                .where(Page.scan_id == scan_id, Issue.severity == 'medium')
                .options(selectinload(Issue.page))  # Prevent N+1 queries
                .order_by(func.length(Issue.element).desc(), Issue.id)
                .limit(medium_limit)
            )
            medium_issues = medium_result.scalars().all()
            issues_raw.extend(medium_issues)
            
            # Load low severity issues (5%) with eager loading
            low_limit = int(MAX_ISSUES_FOR_UI * LOW_ISSUE_RATIO)
            low_result = await db.execute(
                select(Issue).join(Page)
                .where(Page.scan_id == scan_id, Issue.severity == 'low')
                .options(selectinload(Issue.page))  # Prevent N+1 queries
                .order_by(func.length(Issue.element).desc(), Issue.id)
                .limit(low_limit)
            )
            low_issues = low_result.scalars().all()
            issues_raw.extend(low_issues)
            
            issues_truncated = True
            issues_truncated_count = total_issues_count - len(issues_raw)
        else:
            # Load all issues for smaller scans
            issues_result = await db.execute(
                select(Issue)
                .join(Page, Issue.page_id == Page.id)
                .where(Page.scan_id == scan_id)
                .options(selectinload(Issue.page))  # Eager load to prevent N+1
            )
            issues_raw = issues_result.scalars().all()
            issues_truncated = False
            issues_truncated_count = 0
        
        # Sort issues by severity
        severity_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
        issues = sorted(issues_raw, key=lambda issue: (
            severity_order.get(issue.severity, 5),
            issue.type,
            issue.id
        ))
        
        # Create hierarchical structure for templates
        issues_hierarchy = {}
        issues_by_severity = {}
        issues_by_type = {}
        
        # Issue type display mappings
        issue_type_info = {
            'missing_title': {'name': 'Title Tag Mancante', 'icon': 'bi-tag'},
            'title_too_short': {'name': 'Title Troppo Corto', 'icon': 'bi-tag'},
            'title_too_long': {'name': 'Title Troppo Lungo', 'icon': 'bi-tag'},
            'missing_meta_description': {'name': 'Meta Description Mancante', 'icon': 'bi-card-text'},
            'meta_desc_too_short': {'name': 'Meta Description Troppo Corta', 'icon': 'bi-card-text'},
            'meta_desc_too_long': {'name': 'Meta Description Troppo Lunga', 'icon': 'bi-card-text'},
            'missing_h1': {'name': 'H1 Mancante', 'icon': 'bi-type-h1'},
            'h1_mancante': {'name': 'H1 Mancante', 'icon': 'bi-type-h1'},
            'h1_multipli': {'name': 'H1 Multipli', 'icon': 'bi-type-h1'},
            'h1_too_short': {'name': 'H1 Troppo Corto', 'icon': 'bi-type-h1'},
            'h1_too_long': {'name': 'H1 Troppo Lungo', 'icon': 'bi-type-h1'},
            'duplicate_h1': {'name': 'H1 Duplicato', 'icon': 'bi-files'},
            'multiple_h1': {'name': 'H1 Multipli', 'icon': 'bi-type-h1'},
            'canonical_mancante': {'name': 'Canonical Mancante', 'icon': 'bi-link'},
            'missing_canonical': {'name': 'Canonical Mancante', 'icon': 'bi-link'},
            'image_without_alt': {'name': 'Immagini Senza Alt', 'icon': 'bi-image'},
            'image_missing_alt': {'name': 'Immagini Senza Alt', 'icon': 'bi-image'},
            'contenuto_scarso': {'name': 'Contenuto Scarso', 'icon': 'bi-file-text'},
            'blocking_css_resource': {'name': 'CSS Bloccante', 'icon': 'bi-file-earmark-code'},
            'blocking_js_resource': {'name': 'JavaScript Bloccante', 'icon': 'bi-file-earmark-text'},
            'large_image': {'name': 'Immagini Grandi', 'icon': 'bi-image'},
            'slow_response': {'name': 'Risposta Lenta', 'icon': 'bi-clock'},
            'missing_schema': {'name': 'Schema Markup Mancante', 'icon': 'bi-code-square'},
            'canonical_mancante': {'name': 'Canonical Mancante', 'icon': 'bi-link'},
            'meta_description_mancante': {'name': 'Meta Description Mancante', 'icon': 'bi-card-text'},
            'h1_mancante': {'name': 'H1 Mancante', 'icon': 'bi-type-h1'},
            'missing_schema_markup': {'name': 'Schema Markup Mancante', 'icon': 'bi-code-square'}
        }
        
        for issue in issues:
            severity = issue.severity
            issue_type = issue.type
            page_url = page_url_mapping.get(issue.page_id, 'N/A')
            
            # Initialize hierarchy levels
            if severity not in issues_hierarchy:
                issues_hierarchy[severity] = {}
                issues_by_severity[severity] = []
            
            if issue_type not in issues_hierarchy[severity]:
                issues_hierarchy[severity][issue_type] = {
                    'title': issue_type_info.get(issue_type, {}).get('name', issue_type.replace('_', ' ').title()),
                    'icon': issue_type_info.get(issue_type, {}).get('icon', 'bi-exclamation-triangle'),
                    'count': 0,
                    'pages': [],
                    'resource_details': []
                }
            
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            
            # Add to collections
            issues_by_severity[severity].append(issue)
            issues_by_type[issue_type].append(issue)
            issues_hierarchy[severity][issue_type]['count'] += 1
            
            # Add page URL
            if page_url not in issues_hierarchy[severity][issue_type]['pages']:
                issues_hierarchy[severity][issue_type]['pages'].append(page_url)
            
            # Process resource details
            issue_dict = {
                'element': issue.element or '',
                'description': issue.description or '',
                'type': issue.type,
                'severity': issue.severity
            }
            
            try:
                # Prima prova a estrarre come issue consolidato
                consolidated_resources = IssueFactory.extract_consolidated_resources(issue_dict)
                if consolidated_resources:
                    # Issue consolidato con multiple risorse
                    for resource_details in consolidated_resources:
                        resource_data = {
                            'page_url': page_url,
                            'resource_url': getattr(resource_details, 'resource_url', ''),
                            'resource_type': getattr(resource_details, 'resource_type', ''),
                            'file_size': getattr(resource_details, 'file_size', ''),
                            'load_time': getattr(resource_details, 'load_time', ''),
                            'blocking_type': getattr(resource_details, 'blocking_type', ''),
                            'optimization': getattr(resource_details, 'optimization', ''),
                            'mime_type': getattr(resource_details, 'mime_type', ''),
                            'alt_text': getattr(resource_details, 'alt_text', ''),
                            'title': getattr(resource_details, 'title', ''),
                            'content': getattr(resource_details, 'content', ''),
                            'href': getattr(resource_details, 'href', ''),
                            'status_code': getattr(resource_details, 'status_code', '')
                        }
                        issues_hierarchy[severity][issue_type]['resource_details'].append(resource_data)
                    logger.debug(f"Added {len(consolidated_resources)} consolidated resources for issue {issue.id} type {issue_type}")
                else:
                    # Prova come issue singolo
                    resource_details = IssueFactory.extract_resource_details(issue_dict)
                    if resource_details:
                        resource_data = {
                            'page_url': page_url,
                            'resource_url': getattr(resource_details, 'resource_url', ''),
                            'resource_type': getattr(resource_details, 'resource_type', ''),
                            'file_size': getattr(resource_details, 'file_size', ''),
                            'load_time': getattr(resource_details, 'load_time', ''),
                            'blocking_type': getattr(resource_details, 'blocking_type', ''),
                            'optimization': getattr(resource_details, 'optimization', ''),
                            'mime_type': getattr(resource_details, 'mime_type', ''),
                            'alt_text': getattr(resource_details, 'alt_text', ''),
                            'title': getattr(resource_details, 'title', ''),
                            'content': getattr(resource_details, 'content', ''),
                            'href': getattr(resource_details, 'href', ''),
                            'status_code': getattr(resource_details, 'status_code', '')
                        }
                        issues_hierarchy[severity][issue_type]['resource_details'].append(resource_data)
                        logger.debug(f"Added resource details for issue {issue.id} type {issue_type}")
                    else:
                        # Logica intelligente per fallback: solo per issue types che non dovrebbero avere risorse specifiche
                        resource_based_issues = {
                            'blocking_css_resource', 'risorsa_css_bloccante',
                            'blocking_js_resource', 'risorsa_js_bloccante', 
                            'image_missing_alt', 'immagine_senza_alt',
                            'image_oversized', 'immagine_sovradimensionata',
                            'too_many_images', 'troppe_immagini',
                            'image_bad_filename', 'immagine_nome_file_cattivo',
                            'large_image', 'immagine_grande',
                            'missing_meta_description', 'meta_description_mancante',
                            'h1_mancante', 'missing_h1',
                            'canonical_mancante', 'missing_canonical',
                            'missing_schema_markup', 'schema_markup_mancante'
                        }
                        
                        if issue_type not in resource_based_issues:
                            # Issue types come title, meta description, contenuto, ecc. che non hanno risorse specifiche
                            # Creiamo dettagli specifici basati sul tipo di issue
                            optimization_text = issue.description or 'Risolvi questo problema'
                            resource_type = 'pagina'
                            
                            # Personalizza in base al tipo di issue
                            if 'meta_desc' in issue_type or 'meta_description' in issue_type:
                                resource_type = 'meta-description'
                                if 'too_long' in issue_type or 'troppo_lunga' in issue_type:
                                    optimization_text = f"Meta description troppo lunga. {issue.description or ''}"
                                elif 'too_short' in issue_type or 'troppo_corta' in issue_type:
                                    optimization_text = f"Meta description troppo corta. {issue.description or ''}"
                            elif 'title' in issue_type:
                                resource_type = 'title-tag'
                                if 'too_long' in issue_type or 'troppo_lungo' in issue_type:
                                    optimization_text = f"Title tag troppo lungo. {issue.description or ''}"
                                elif 'too_short' in issue_type or 'troppo_corto' in issue_type:
                                    optimization_text = f"Title tag troppo corto. {issue.description or ''}"
                            elif 'content' in issue_type or 'contenuto' in issue_type:
                                resource_type = 'contenuto'
                            
                            fallback_resource = {
                                'page_url': page_url,
                                'resource_url': '',  # Vuoto per indicare che è a livello pagina
                                'resource_type': resource_type,
                                'file_size': '',
                                'load_time': '',
                                'blocking_type': '',
                                'optimization': optimization_text,
                                'mime_type': '',
                                'alt_text': '',
                                'title': optimization_text,
                                'content': issue.description or '',
                                'href': page_url,
                                'status_code': ''
                            }
                            issues_hierarchy[severity][issue_type]['resource_details'].append(fallback_resource)
                            logger.debug(f"Added page-level fallback for issue {issue.id} type {issue_type}")
                        else:
                            # Issue types basati su risorse: se non abbiamo details granulari, è un problema
                            logger.debug(f"No granular resource details for resource-based issue {issue.id} type {issue_type}")
            except Exception as e:
                logger.error(f"Error processing resource details for issue {issue.id}: {e}")
                # Non creiamo fallback resource quando c'è un errore - meglio nessun dato che dati falsi
                continue
        
        # Calculate performance overview
        performance_scores = [p.performance_score for p in all_pages if p.performance_score is not None]
        technical_scores = [p.technical_score for p in all_pages if p.technical_score is not None]
        mobile_scores = [p.mobile_score for p in all_pages if p.mobile_score is not None]
        
        avg_performance = sum(performance_scores) / len(performance_scores) if performance_scores else 0
        avg_technical = sum(technical_scores) / len(technical_scores) if technical_scores else 0
        avg_mobile = sum(mobile_scores) / len(mobile_scores) if mobile_scores else 0
        
        # Schema coverage
        schema_pages = sum(1 for p in all_pages if p.has_schema_markup)
        schema_coverage = (schema_pages / len(all_pages)) * 100 if all_pages else 0
        
        # Mobile coverage (pages with mobile_score > 70)
        mobile_optimized = sum(1 for p in all_pages if p.mobile_score and p.mobile_score > 70)
        mobile_coverage = (mobile_optimized / len(all_pages)) * 100 if all_pages else 0
        
        # Build context for template
        context = {
            "request": request,
            "page_title": f"Risultati Scansione #{scan_id} - SEOAudit",
            "app_version": "2.0.0",
            "template_mode": True,
            "scan": {
                "id": scan.id,
                "website_name": website_name,
                "client_name": client_name,
                "status": scan.status,
                "seo_score": scan.seo_score,
                "pages_scanned": scan.pages_scanned,
                "created_at": scan.created_at,
                "completed_at": scan.completed_at
            },
            "pages": [
                {
                    "id": page.id,
                    "url": page.url,
                    "title": page.title,
                    "status_code": page.status_code,
                    "seo_score": page.seo_score,
                    "performance_score": page.performance_score,
                    "technical_score": page.technical_score,
                    "mobile_score": page.mobile_score,
                    "has_schema_markup": bool(page.has_schema_markup),
                    "schema_types": page.schema_types or [],
                    "core_web_vitals": page.core_web_vitals or {},
                    "technical_seo_data": page.technical_seo_data or {},
                    "issues_count": len([i for i in issues_raw if i.page_id == page.id])
                }
                for page in pages
            ],
            "issues": [
                {
                    "id": issue.id,
                    "type": issue.type,
                    "severity": issue.severity,
                    "message": issue.description,
                    "page_url": page_url_mapping.get(issue.page_id, "N/A")
                }
                for issue in issues
            ],
            "issues_hierarchy": issues_hierarchy,
            "issues_by_severity": issues_by_severity,
            "issues_by_type": issues_by_type,
            "page_url_mapping": page_url_mapping,
            "issue_type_info": issue_type_info,
            "performance_overview": {
                "avg_performance_score": round(avg_performance, 1),
                "avg_technical_score": round(avg_technical, 1),
                "schema_coverage": round(schema_coverage, 1),
                "mobile_coverage": round(mobile_coverage, 1),
                "total_pages_analyzed": len(all_pages),
                "pages_with_performance_data": len(performance_scores),
                "pages_with_technical_data": len(technical_scores),
                "avg_load_time": _calculate_avg_load_time(all_pages),
                "avg_page_size": _calculate_avg_page_size(all_pages),
                "optimization_score": round(avg_performance, 0)
            },
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_pages": total_pages_pagination,
                "total_items": total_pages_count,
                "has_prev": page > 1,
                "has_next": page < total_pages_pagination,
                "prev_page": page - 1 if page > 1 else None,
                "next_page": page + 1 if page < total_pages_pagination else None,
                "start_item": ((page - 1) * per_page) + 1 if total_pages_count > 0 else 0,
                "end_item": min(page * per_page, total_pages_count)
            },
            "issues_performance": {
                "total_issues_count": len(issues_raw) + (issues_truncated_count if issues_truncated else 0),
                "loaded_issues_count": len(issues_raw),
                "is_truncated": issues_truncated,
                "truncated_count": issues_truncated_count,
                "max_issues_ui": MAX_ISSUES_FOR_UI
            },
            "current_section": "scan_results"
        }
        
        return templates.TemplateResponse("scan_results_wrapper.html", context)
        
    except Exception as e:
        logger.error(f"Error in scan_results for scan_id {scan_id}: {str(e)}")
        logger.exception("Full traceback:")
        
        # Fallback context for error cases
        context = {
            "request": request,
            "page_title": f"Errore Scansione #{scan_id} - SEOAudit",
            "app_version": "2.0.0",
            "template_mode": True,
            "scan": None,
            "error_message": f"Errore nel caricamento dei risultati: {str(e)}",
            "current_section": "scan_results"
        }
        
        return templates.TemplateResponse("error.html", context)