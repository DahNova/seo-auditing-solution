from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import os

from app.database import get_db
from app.models import Client, Website, Scan, Issue, Page
from app.schemas.client import ClientCreate, ClientUpdate
from app.schemas.website import WebsiteCreate, WebsiteUpdate
from app.schemas.scan import ScanCreate
from app.services.scan_service import ScanService

router = APIRouter(prefix="/htmx", tags=["htmx"])

# Setup Jinja2 templates
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=template_dir)

# ===== CLIENT HTMX ENDPOINTS =====

@router.post("/clients/create", response_class=HTMLResponse)
async def create_client_htmx(
    request: Request,
    name: str = Form(...),
    contact_email: str = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Create client and return updated clients table"""
    try:
        # Create client
        client = Client(
            name=name,
            contact_email=contact_email,
            description=description
        )
        db.add(client)
        await db.commit()
        await db.refresh(client)
        
        # Get all clients with website counts for table refresh
        clients_result = await db.execute(
            select(Client).order_by(Client.name)
        )
        clients = clients_result.scalars().all()
        
        clients_data = []
        for client in clients:
            websites_count = await db.scalar(
                select(func.count(Website.id)).where(Website.client_id == client.id)
            )
            clients_data.append({
                "id": client.id,
                "name": client.name,
                "contact_email": client.contact_email,
                "contact_phone": None,  # Not in model
                "company": None,  # Not in model  
                "websites_count": websites_count or 0,
                "status": "Attivo",
                "created_at": client.created_at,
                "updated_at": client.updated_at
            })
        
        # Return updated table
        return templates.TemplateResponse(
            "components/tables/clients_table.html",
            {"clients": clients_data, "request": request}
        )
        
    except Exception as e:
        # Return error message
        return f'<div class="alert alert-danger">Errore: {str(e)}</div>'

@router.get("/clients/{client_id}/edit", response_class=HTMLResponse)
async def get_client_edit_form(
    request: Request,
    client_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get client edit form"""
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    response = templates.TemplateResponse(
        "components/forms/client_edit_form.html",
        {"client": client, "request": request}
    )
    response.headers["HX-Trigger-After-Swap"] = "showModal"
    return response

@router.put("/clients/{client_id}", response_class=HTMLResponse)
async def update_client_htmx(
    request: Request,
    client_id: int,
    name: str = Form(...),
    contact_email: str = Form(...),
    contact_phone: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Update client and return updated table row"""
    try:
        client = await db.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client.name = name
        client.contact_email = contact_email
        client.contact_phone = contact_phone
        client.company = company
        client.notes = notes
        
        await db.commit()
        await db.refresh(client)
        
        # Get website count
        websites_count = await db.scalar(
            select(func.count(Website.id)).where(Website.client_id == client.id)
        )
        
        client_data = {
            "id": client.id,
            "name": client.name,
            "contact_email": client.contact_email,
            "contact_phone": client.contact_phone,
            "company": client.company,
            "websites_count": websites_count or 0,
            "status": "Attivo",
            "created_at": client.created_at,
            "updated_at": client.updated_at
        }
        
        return templates.TemplateResponse(
            "components/tables/client_row.html",
            {"client": client_data, "request": request}
        )
        
    except Exception as e:
        return f'<div class="alert alert-danger">Errore: {str(e)}</div>'

@router.delete("/clients/{client_id}", response_class=HTMLResponse)
async def delete_client_htmx(
    request: Request,
    client_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete client and return empty response"""
    try:
        client = await db.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        await db.delete(client)
        await db.commit()
        
        return HTMLResponse("")  # Empty response removes the row
        
    except Exception as e:
        return f'<div class="alert alert-danger">Errore: {str(e)}</div>'

# ===== WEBSITE HTMX ENDPOINTS =====

@router.post("/websites/create", response_class=HTMLResponse)
async def create_website_htmx(
    request: Request,
    name: str = Form(...),
    domain: str = Form(...),
    client_id: int = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Create website and return updated websites table"""
    try:
        # Create website
        website = Website(
            name=name,
            domain=domain,
            client_id=client_id,
            description=description
        )
        db.add(website)
        await db.commit()
        await db.refresh(website)
        
        # Get all websites with client info for table refresh
        websites_result = await db.execute(
            select(Website, Client.name.label('client_name'))
            .join(Client, Website.client_id == Client.id)
            .order_by(Website.name)
        )
        
        websites_data = []
        for website, client_name in websites_result:
            scans_count = await db.scalar(
                select(func.count(Scan.id)).where(Scan.website_id == website.id)
            )
            
            websites_data.append({
                "id": website.id,
                "name": website.name,
                "url": website.domain,  # Model uses 'domain' not 'url'
                "client_name": client_name,
                "client_id": website.client_id,
                "scans_count": scans_count or 0,
                "status": "Attivo",
                "created_at": website.created_at,
                "updated_at": website.updated_at
            })
        
        # Return updated table
        return templates.TemplateResponse(
            "components/tables/websites_table.html",
            {"websites": websites_data, "request": request}
        )
        
    except Exception as e:
        return f'<div class="alert alert-danger">Errore: {str(e)}</div>'

@router.get("/websites/{website_id}/edit", response_class=HTMLResponse)
async def get_website_edit_form(
    request: Request,
    website_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get website edit form"""
    website = await db.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Get clients for dropdown
    clients_result = await db.execute(select(Client).order_by(Client.name))
    clients = clients_result.scalars().all()
    
    response = templates.TemplateResponse(
        "components/forms/website_edit_form.html",
        {"website": website, "clients": clients, "request": request}
    )
    response.headers["HX-Trigger-After-Swap"] = "showModal"
    return response

@router.put("/websites/{website_id}", response_class=HTMLResponse)
async def update_website_htmx(
    request: Request,
    website_id: int,
    name: str = Form(...),
    domain: str = Form(...),
    client_id: int = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Update website and return updated table row"""
    try:
        website = await db.get(Website, website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        website.name = name
        website.domain = domain
        website.client_id = client_id
        website.description = description
        
        await db.commit()
        await db.refresh(website)
        
        # Get client name and scan count
        client = await db.get(Client, client_id)
        scans_count = await db.scalar(
            select(func.count(Scan.id)).where(Scan.website_id == website.id)
        )
        
        website_data = {
            "id": website.id,
            "name": website.name,
            "url": website.domain,
            "client_name": client.name if client else "Unknown",
            "client_id": website.client_id,
            "scans_count": scans_count or 0,
            "status": "Attivo",
            "created_at": website.created_at,
            "updated_at": website.updated_at
        }
        
        return templates.TemplateResponse(
            "components/tables/website_row.html",
            {"website": website_data, "request": request}
        )
        
    except Exception as e:
        return f'<div class="alert alert-danger">Errore: {str(e)}</div>'

@router.delete("/websites/{website_id}", response_class=HTMLResponse)
async def delete_website_htmx(
    request: Request,
    website_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete website and return empty response"""
    try:
        website = await db.get(Website, website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        await db.delete(website)
        await db.commit()
        
        return HTMLResponse("")  # Empty response removes the row
        
    except Exception as e:
        return f'<div class="alert alert-danger">Errore: {str(e)}</div>'

# ===== SCAN HTMX ENDPOINTS =====

@router.post("/scans/create", response_class=HTMLResponse)
async def create_scan_htmx(
    request: Request,
    website_id: int = Form(...),
    max_pages: int = Form(1000),
    max_depth: int = Form(5),
    respect_robots: bool = Form(True),
    include_external: bool = Form(False),
    generate_report: bool = Form(True),
    db: AsyncSession = Depends(get_db)
):
    """Create scan and return updated scans table"""
    try:
        # Create scan
        scan = Scan(
            website_id=website_id,
            status="pending",
            max_pages=max_pages,
            max_depth=max_depth,
            respect_robots=respect_robots,
            include_external=include_external,
            generate_report=generate_report
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        
        # Start scan task (async)
        scan_service = ScanService(db)
        await scan_service.start_scan(scan.id)
        
        # Get all scans for table refresh
        scans_result = await db.execute(
            select(Scan, Website.name.label('website_name'), Client.name.label('client_name'))
            .outerjoin(Website, Scan.website_id == Website.id)
            .outerjoin(Client, Website.client_id == Client.id)
            .order_by(Scan.created_at.desc())
        )
        
        scans_data = []
        for scan, website_name, client_name in scans_result:
            issues_count = await db.scalar(
                select(func.count(Issue.id)).where(Issue.scan_id == scan.id)
            ) or 0
            
            scans_data.append({
                "id": scan.id,
                "website_name": website_name or f"Website {scan.website_id}",
                "client_name": client_name or "Cliente Sconosciuto",
                "website_id": scan.website_id,
                "status": scan.status,
                "issues_count": issues_count,
                "pages_scanned": scan.pages_scanned or 0,
                "seo_score": scan.seo_score,
                "created_at": scan.created_at,
                "completed_at": scan.completed_at,
                "scan_type": "Completa"
            })
        
        # Return updated table
        return templates.TemplateResponse(
            "components/tables/scans_table.html",
            {"scans": scans_data, "request": request}
        )
        
    except Exception as e:
        return f'<div class="alert alert-danger">Errore: {str(e)}</div>'

@router.delete("/scans/{scan_id}", response_class=HTMLResponse)
async def delete_scan_htmx(
    request: Request,
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete scan and return empty response"""
    try:
        scan = await db.get(Scan, scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        await db.delete(scan)
        await db.commit()
        
        return HTMLResponse("")  # Empty response removes the row
        
    except Exception as e:
        return f'<div class="alert alert-danger">Errore: {str(e)}</div>'

# ===== MODAL ENDPOINTS =====

@router.get("/modals/add-client", response_class=HTMLResponse)
async def get_add_client_modal(request: Request):
    """Get add client modal"""
    response = templates.TemplateResponse(
        "components/forms/client_form.html",
        {"request": request, "mode": "create"}
    )
    response.headers["HX-Trigger-After-Swap"] = "showModal"
    return response

@router.get("/modals/add-website", response_class=HTMLResponse)
async def get_add_website_modal(request: Request, db: AsyncSession = Depends(get_db)):
    """Get add website modal with clients dropdown"""
    clients_result = await db.execute(select(Client).order_by(Client.name))
    clients = clients_result.scalars().all()
    
    response = templates.TemplateResponse(
        "components/forms/website_form.html",
        {"request": request, "mode": "create", "clients": clients}
    )
    response.headers["HX-Trigger-After-Swap"] = "showModal"
    return response

@router.get("/modals/add-scan", response_class=HTMLResponse)
async def get_add_scan_modal(request: Request, db: AsyncSession = Depends(get_db)):
    """Get add scan modal with websites dropdown"""
    websites_result = await db.execute(
        select(Website, Client.name.label('client_name'))
        .join(Client, Website.client_id == Client.id)
        .order_by(Website.name)
    )
    websites = [
        {"id": w.id, "name": w.name, "client_name": client_name}
        for w, client_name in websites_result
    ]
    
    response = templates.TemplateResponse(
        "components/forms/scan_form.html",
        {"request": request, "mode": "create", "websites": websites}
    )
    response.headers["HX-Trigger-After-Swap"] = "showModal"
    return response