#!/usr/bin/env python3
"""
Script per creare una scansione demo con esempi di tutti i tipi di issue
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
import json

# Aggiungi il percorso dell'app al Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import AsyncSessionLocal
from app.models import Client, Website, Scan, Page, Issue
from app.core.issue_registry import IssueRegistry, IssueCategory, IssueSeverity, IssueFormat
from sqlalchemy import select

async def create_demo_scan():
    """Crea una scansione demo con tutti i tipi di issue"""
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Trova o crea client demo
            client_result = await db.execute(
                select(Client).where(Client.name == "Demo Client")
            )
            client = client_result.scalar_one_or_none()
            
            if not client:
                client = Client(
                    name="Demo Client",
                    contact_email="demo@example.com",
                    description="Client demo per testing issue types"
                )
                db.add(client)
                await db.flush()
                print(f"Created demo client: {client.name}")
            else:
                print(f"Using existing demo client: {client.name}")
            
            # 2. Trova o crea website demo
            website_result = await db.execute(
                select(Website).where(
                    Website.domain == "demo-seo-test.com",
                    Website.client_id == client.id
                )
            )
            website = website_result.scalar_one_or_none()
            
            if not website:
                website = Website(
                    domain="demo-seo-test.com",
                    name="Demo SEO Test Site",
                    client_id=client.id,
                    scan_frequency="weekly",
                    max_pages=500
                )
                db.add(website)
                await db.flush()
                print(f"Created demo website: {website.domain}")
            else:
                print(f"Using existing demo website: {website.domain}")
            
            # 3. Crea nuova scansione demo
            scan = Scan(
                website_id=website.id,
                status="completed",
                seo_score=72.5,
                pages_scanned=15,
                total_issues=0,  # Sarà aggiornato dopo
                completed_at=datetime.now(timezone.utc)
            )
            db.add(scan)
            await db.flush()
            print(f"Created demo scan: #{scan.id}")
            
            # 4. Crea pagine demo
            demo_pages = [
                {
                    "url": "https://demo-seo-test.com/",
                    "title": "Homepage - Demo SEO Test",
                    "seo_score": 85.2,
                    "performance_score": 72.1,
                    "technical_score": 78.5,
                    "mobile_score": 82.3
                },
                {
                    "url": "https://demo-seo-test.com/prodotti/",
                    "title": "Prodotti - Catalogo Completo",
                    "seo_score": 68.9,
                    "performance_score": 65.4,
                    "technical_score": 71.2,
                    "mobile_score": 69.8
                },
                {
                    "url": "https://demo-seo-test.com/prodotti/laptop-gaming",
                    "title": "Laptop Gaming Professionale",
                    "seo_score": 52.3,
                    "performance_score": 45.7,
                    "technical_score": 58.9,
                    "mobile_score": 48.2
                },
                {
                    "url": "https://demo-seo-test.com/blog/",
                    "title": "Blog - Novità e Guide",
                    "seo_score": 74.6,
                    "performance_score": 71.8,
                    "technical_score": 76.3,
                    "mobile_score": 72.1
                },
                {
                    "url": "https://demo-seo-test.com/contatti",
                    "title": "Contattaci - Demo SEO Test",
                    "seo_score": 91.4,
                    "performance_score": 88.2,
                    "technical_score": 93.1,
                    "mobile_score": 89.7
                }
            ]
            
            pages = []
            for page_data in demo_pages:
                page = Page(
                    scan_id=scan.id,
                    url=page_data["url"],
                    title=page_data["title"],
                    status_code=200,
                    seo_score=page_data["seo_score"],
                    performance_score=page_data["performance_score"],
                    technical_score=page_data["technical_score"],
                    mobile_score=page_data["mobile_score"],
                    has_schema_markup=True if "prodotti" in page_data["url"] else False,
                    schema_types=["Product"] if "prodotti" in page_data["url"] else [],
                    core_web_vitals={
                        "lcp": 2300 + (len(pages) * 200),  # Varia per pagina
                        "fid": 45 + (len(pages) * 10),
                        "cls": 0.1 + (len(pages) * 0.02),
                        "ttfb": 850 + (len(pages) * 100)
                    },
                    technical_seo_data={
                        "page_size": 1024000 + (len(pages) * 512000),
                        "content_length": 45000 + (len(pages) * 12000)
                    }
                )
                db.add(page)
                pages.append(page)
            
            await db.flush()
            print(f"Created {len(pages)} demo pages")
            
            # 5. Crea issue per ogni tipo nel registry
            all_issues = IssueRegistry.get_all_issues()
            print(f"Creating issues for {len(all_issues)} issue types...")
            
            issue_count = 0
            for issue_type, issue_def in all_issues.items():
                # Seleziona una pagina casuale per l'issue
                page = pages[issue_count % len(pages)]
                
                # Crea dati di esempio specifici per il tipo di issue
                element_data = create_mock_element_data(issue_type, page.url)
                
                # Determina la severità (varia un po' per avere diversità)
                base_severity = issue_def.severity.value
                if issue_count % 4 == 0 and base_severity != 'critical':
                    # Escalate alcuni issues
                    severity_map = {'low': 'medium', 'medium': 'high', 'high': 'critical'}
                    severity = severity_map.get(base_severity, base_severity)
                else:
                    severity = base_severity
                
                issue = Issue(
                    page_id=page.id,
                    type=issue_type,
                    severity=severity,
                    category=issue_def.category.value,
                    title=issue_def.name_it,  # Add required title field
                    description=create_mock_description(issue_type, issue_def, page.url),
                    element=json.dumps(element_data) if element_data else None,
                    score_impact=get_score_impact(severity)
                )
                
                db.add(issue)
                issue_count += 1
                
                if issue_count % 20 == 0:
                    print(f"Created {issue_count} issues...")
            
            await db.commit()
            print(f"\n✅ Demo scan created successfully!")
            print(f"   Scan ID: {scan.id}")
            print(f"   Total Issues: {issue_count}")
            print(f"   URL: http://localhost:8000/templated/scans/{scan.id}/results")
            
            return scan.id
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating demo scan: {e}")
            raise

def create_mock_element_data(issue_type: str, page_url: str) -> Dict[str, Any]:
    """Crea dati di esempio specifici per ogni tipo di issue"""
    
    # Issues CSS/JS bloccanti
    if 'css_bloccante' in issue_type or 'risorsa_css' in issue_type:
        return {
            "resources": [
                {
                    "resource_url": f"{page_url.rstrip('/')}/assets/css/bootstrap.min.css",
                    "resource_type": "css",
                    "file_size": "156KB",
                    "load_time": "245ms",
                    "blocking_type": "render-blocking",
                    "optimization": "Considera il caricamento asincrono o inline per CSS critici"
                },
                {
                    "resource_url": f"{page_url.rstrip('/')}/assets/css/custom-styles.css",
                    "resource_type": "css", 
                    "file_size": "89KB",
                    "load_time": "178ms",
                    "blocking_type": "render-blocking",
                    "optimization": "Minimizza e combina i file CSS per ridurre le richieste"
                }
            ]
        }
    
    elif 'js_bloccante' in issue_type or 'risorsa_js' in issue_type:
        return {
            "resources": [
                {
                    "resource_url": f"{page_url.rstrip('/')}/assets/js/jquery-3.6.0.min.js",
                    "resource_type": "javascript",
                    "file_size": "97KB", 
                    "load_time": "312ms",
                    "blocking_type": "parser-blocking",
                    "optimization": "Sposta gli script non critici alla fine del body o usa defer/async"
                }
            ]
        }
    
    # Issues immagini
    elif 'immagine' in issue_type:
        return {
            "resources": [
                {
                    "resource_url": f"{page_url.rstrip('/')}/images/hero-banner.jpg",
                    "resource_type": "image",
                    "file_size": "2.3MB",
                    "mime_type": "image/jpeg",
                    "alt_text": "" if 'senza_alt' in issue_type else "Banner principale",
                    "optimization": "Ottimizza l'immagine e usa formati moderni come WebP"
                }
            ]
        }
    
    # Issues meta description
    elif 'meta_desc' in issue_type or 'meta_description' in issue_type:
        if 'mancante' in issue_type:
            return {
                "suggested_content": "Scopri i migliori prodotti per le tue esigenze. Qualità garantita, prezzi competitivi e spedizione gratuita. Visita il nostro catalogo online.",
                "length": 0
            }
        elif 'troppo_lunga' in issue_type or 'too_long' in issue_type:
            return {
                "current_content": "Benvenuti nel nostro incredibile negozio online dove potete trovare una vastissima selezione di prodotti di alta qualità per soddisfare tutte le vostre esigenze, con prezzi incredibilmente competitivi e un servizio clienti eccezionale che vi garantirà sempre la massima soddisfazione",
                "length": 245,
                "max_recommended": 160
            }
        elif 'troppo_corta' in issue_type or 'too_short' in issue_type:
            return {
                "current_content": "Il nostro negozio online",
                "length": 22,
                "min_recommended": 120
            }
    
    # Issues H1
    elif 'h1' in issue_type:
        if 'mancante' in issue_type:
            return {
                "suggested_content": "Laptop Gaming Professionale - Prestazioni Elevate",
                "page_title": "Laptop Gaming Professionale"
            }
        elif 'multipli' in issue_type:
            return {
                "h1_tags": [
                    "Benvenuti nel nostro store",
                    "Prodotti in evidenza", 
                    "Offerte speciali"
                ],
                "count": 3
            }
    
    # Issues canonical
    elif 'canonical' in issue_type:
        return {
            "suggested_canonical": page_url,
            "current_canonical": None if 'mancante' in issue_type else f"{page_url}?ref=duplicate"
        }
    
    # Issues schema markup
    elif 'schema' in issue_type:
        return {
            "page_type": "product" if "prodotti" in page_url else "webpage",
            "suggested_schemas": ["Product", "Organization"] if "prodotti" in page_url else ["WebPage", "Organization"]
        }
    
    # Issues contenuto
    elif 'contenuto' in issue_type:
        return {
            "word_count": 89,
            "min_recommended": 300,
            "content_quality_score": 2.1
        }
    
    return None

def create_mock_description(issue_type: str, issue_def, page_url: str) -> str:
    """Crea descrizioni specifiche per ogni tipo di issue"""
    
    if 'css_bloccante' in issue_type:
        return "Rilevati 2 file CSS che bloccano il rendering della pagina. Questi rallentano il tempo di caricamento iniziale."
    elif 'js_bloccante' in issue_type:
        return "File JavaScript bloccante nel <head> che ritarda l'analisi del DOM. Influisce negativamente sui Core Web Vitals."
    elif 'immagine_senza_alt' in issue_type:
        return "Immagine senza testo alternativo. Problemi di accessibilità e SEO per i motori di ricerca."
    elif 'meta_desc_troppo_lunga' in issue_type:
        return "Meta description di 245 caratteri supera il limite raccomandato di 160. Verrà troncata nei risultati di ricerca."
    elif 'meta_desc_troppo_corta' in issue_type:
        return "Meta description di soli 22 caratteri è troppo corta per essere efficace nei risultati di ricerca."
    elif 'meta_description_mancante' in issue_type:
        return "Pagina senza meta description. Opportunità mancata per migliorare il CTR nei risultati di ricerca."
    elif 'h1_mancante' in issue_type:
        return "Pagina senza tag H1. Importante per la struttura semantica e l'ottimizzazione SEO."
    elif 'h1_multipli' in issue_type:
        return "Rilevati 3 tag H1 nella pagina. Dovrebbe esserci un solo H1 per pagina per una struttura semantica corretta."
    elif 'canonical_mancante' in issue_type:
        return "Tag canonical mancante. Rischio di contenuto duplicato e problemi di indicizzazione."
    elif 'schema_markup_mancante' in issue_type:
        return "Schema markup mancante. Opportunità per migliorare l'aspetto nei risultati di ricerca con rich snippets."
    elif 'contenuto_scarso' in issue_type:
        return "Contenuto della pagina troppo breve (89 parole). I motori di ricerca preferiscono contenuti più approfonditi."
    
    return issue_def.description_it

def get_score_impact(severity: str) -> float:
    """Calcola l'impatto sul punteggio basato sulla severità"""
    impact_map = {
        'critical': 25.0,
        'high': 15.0, 
        'medium': 8.0,
        'low': 3.0
    }
    return impact_map.get(severity, 5.0)

if __name__ == "__main__":
    print("🚀 Creating demo scan with all issue types...")
    scan_id = asyncio.run(create_demo_scan())
    print(f"\n🎉 Demo scan created! Visit: http://localhost:8000/templated/scans/{scan_id}/results")