from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Website, Client
from app.schemas import WebsiteCreate, WebsiteResponse, WebsiteUpdate

router = APIRouter(prefix="/websites", tags=["websites"])

@router.post("/", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def create_website(
    website: WebsiteCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify client exists
    client_result = await db.execute(
        select(Client).where(Client.id == website.client_id)
    )
    if not client_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db_website = Website(**website.model_dump())
    db.add(db_website)
    await db.commit()
    await db.refresh(db_website)
    return db_website

@router.get("/", response_model=List[WebsiteResponse])
async def list_websites(
    client_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Website)
    if client_id:
        query = query.where(Website.client_id == client_id)
    
    result = await db.execute(
        query.offset(skip).limit(limit)
    )
    websites = result.scalars().all()
    return websites

@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(
    website_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Website).where(Website.id == website_id)
    )
    website = result.scalar_one_or_none()
    
    if website is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    return website

@router.put("/{website_id}", response_model=WebsiteResponse)
async def update_website(
    website_id: int,
    website_update: WebsiteUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Website).where(Website.id == website_id)
    )
    db_website = result.scalar_one_or_none()
    
    if db_website is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    update_data = website_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_website, field, value)
    
    await db.commit()
    await db.refresh(db_website)
    return db_website

@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website(
    website_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Website).where(Website.id == website_id)
    )
    db_website = result.scalar_one_or_none()
    
    if db_website is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    await db.delete(db_website)
    await db.commit()