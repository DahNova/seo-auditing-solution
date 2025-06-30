from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import os
import logging

from app.database import get_db
from app.services.client_service import ClientService
from app.services.website_service import WebsiteService
from app.models import Client, Website

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/htmx", tags=["htmx"])

# Setup Jinja2 templates
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=template_dir)


@router.get("/modals/add-client", response_class=HTMLResponse)
async def get_add_client_modal(request: Request):
    """Get the add client modal template"""
    return templates.TemplateResponse(
        "components/modals/add_client_modal.html",
        {"request": request}
    )


@router.get("/modals/add-website", response_class=HTMLResponse)
async def get_add_website_modal(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get the add website modal template with clients for dropdown"""
    # Get all clients for the dropdown
    result = await db.execute(select(Client).order_by(Client.name))
    clients = result.scalars().all()
    
    return templates.TemplateResponse(
        "components/modals/add_website_modal.html",
        {"request": request, "clients": clients}
    )


@router.get("/modals/add-scan", response_class=HTMLResponse)
async def get_add_scan_modal(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get the add scan modal template with websites for dropdown"""
    # Get all websites with their clients for the dropdown
    result = await db.execute(
        select(Website)
        .options(selectinload(Website.client))
        .order_by(Website.url)
    )
    websites = result.scalars().all()
    
    return templates.TemplateResponse(
        "components/modals/add_scan_modal.html",
        {"request": request, "websites": websites}
    )


@router.get("/clients/{client_id}/edit", response_class=HTMLResponse)
async def get_edit_client_modal(
    client_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get the edit client modal template"""
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return templates.TemplateResponse(
        "components/forms/client_edit_form.html",
        {"request": request, "client": client}
    )


@router.get("/websites/{website_id}/edit", response_class=HTMLResponse)
async def get_edit_website_modal(
    website_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get the edit website modal template"""
    result = await db.execute(
        select(Website)
        .options(selectinload(Website.client))
        .where(Website.id == website_id)
    )
    website = result.scalar_one_or_none()
    
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Get all clients for the dropdown
    clients_result = await db.execute(select(Client).order_by(Client.name))
    clients = clients_result.scalars().all()
    
    return templates.TemplateResponse(
        "components/forms/website_edit_form.html",
        {"request": request, "website": website, "clients": clients}
    )


@router.put("/clients/{client_id}", response_class=HTMLResponse)
async def update_client_htmx(
    client_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Update client and return updated clients table"""
    form_data = await request.form()
    
    client_service = ClientService(db)
    client = await client_service.get_client(client_id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update client with form data
    update_data = {
        "name": form_data.get("name"),
        "email": form_data.get("email"),
        "phone": form_data.get("phone"),
        "company": form_data.get("company")
    }
    
    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v}
    
    await client_service.update_client(client_id, update_data)
    
    # Return updated clients table
    clients = await client_service.get_all_clients()
    return templates.TemplateResponse(
        "components/tables/clients_table.html",
        {"request": request, "clients": clients}
    )


@router.put("/websites/{website_id}", response_class=HTMLResponse)
async def update_website_htmx(
    website_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Update website and return updated websites table"""
    form_data = await request.form()
    
    website_service = WebsiteService(db)
    website = await website_service.get_website(website_id)
    
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Update website with form data
    update_data = {
        "url": form_data.get("url"),
        "name": form_data.get("name"),
        "client_id": int(form_data.get("client_id")) if form_data.get("client_id") else None
    }
    
    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    await website_service.update_website(website_id, update_data)
    
    # Return updated websites table with clients loaded
    result = await db.execute(
        select(Website)
        .options(selectinload(Website.client))
        .order_by(Website.created_at.desc())
    )
    websites = result.scalars().all()
    
    return templates.TemplateResponse(
        "components/tables/websites_table.html",
        {"request": request, "websites": websites}
    )


@router.delete("/clients/{client_id}", response_class=HTMLResponse)
async def delete_client_htmx(
    client_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Delete client and return empty response"""
    client_service = ClientService(db)
    
    try:
        await client_service.delete_client(client_id)
        # Return empty content to remove the row
        return HTMLResponse(content="")
    except Exception as e:
        logger.error(f"Error deleting client {client_id}: {e}")
        raise HTTPException(status_code=400, detail="Cannot delete client")


@router.delete("/websites/{website_id}", response_class=HTMLResponse)
async def delete_website_htmx(
    website_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Delete website and return empty response"""
    website_service = WebsiteService(db)
    
    try:
        await website_service.delete_website(website_id)
        # Return empty content to remove the row
        return HTMLResponse(content="")
    except Exception as e:
        logger.error(f"Error deleting website {website_id}: {e}")
        raise HTTPException(status_code=400, detail="Cannot delete website")