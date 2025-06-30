from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import os
import logging

from app.database import get_db
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
        "components/modals/client_modal_semrush.html",
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
        "components/modals/website_modal_semrush.html",
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
        "components/modals/scan_modal_semrush.html",
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
    
    # Get client
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update client with form data
    if form_data.get("name"):
        client.name = form_data.get("name")
    if form_data.get("email"):
        client.email = form_data.get("email")
    if form_data.get("phone"):
        client.phone = form_data.get("phone")
    if form_data.get("company"):
        client.company = form_data.get("company")
    
    await db.commit()
    await db.refresh(client)
    
    # Return updated clients table
    result = await db.execute(select(Client).order_by(Client.created_at.desc()))
    clients = result.scalars().all()
    
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
    
    # Get website
    result = await db.execute(
        select(Website)
        .options(selectinload(Website.client))
        .where(Website.id == website_id)
    )
    website = result.scalar_one_or_none()
    
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Update website with form data
    if form_data.get("url"):
        website.url = form_data.get("url")
    if form_data.get("name"):
        website.name = form_data.get("name")
    if form_data.get("client_id"):
        website.client_id = int(form_data.get("client_id"))
    
    await db.commit()
    await db.refresh(website)
    
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
    try:
        # Get client first
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Delete client
        await db.delete(client)
        await db.commit()
        
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
    try:
        # Get website first
        result = await db.execute(select(Website).where(Website.id == website_id))
        website = result.scalar_one_or_none()
        
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Delete website
        await db.delete(website)
        await db.commit()
        
        # Return empty content to remove the row
        return HTMLResponse(content="")
    except Exception as e:
        logger.error(f"Error deleting website {website_id}: {e}")
        raise HTTPException(status_code=400, detail="Cannot delete website")