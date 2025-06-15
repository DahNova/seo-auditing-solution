from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Scan, Website, Page, Issue
from app.schemas import ScanCreate, ScanResponse, PageResponse, IssueResponse
# from app.tasks.scan_tasks import run_website_scan  # Disabled for testing

router = APIRouter(prefix="/scans", tags=["scans"])

@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan: ScanCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify website exists
    website_result = await db.execute(
        select(Website).where(Website.id == scan.website_id)
    )
    website = website_result.scalar_one_or_none()
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    # Create scan record
    db_scan = Scan(website_id=scan.website_id)
    db.add(db_scan)
    await db.commit()
    await db.refresh(db_scan)
    
    # TODO: Queue scan task with Celery (disabled for testing)
    # task = run_website_scan.delay(website.id, db_scan.id)
    # db_scan.config = {"celery_task_id": task.id}
    await db.commit()
    
    return db_scan

@router.get("/", response_model=List[ScanResponse])
async def list_scans(
    website_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Scan)
    if website_id:
        query = query.where(Scan.website_id == website_id)
    
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Scan.created_at.desc())
    )
    scans = result.scalars().all()
    return scans

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return scan

@router.get("/{scan_id}/pages", response_model=List[PageResponse])
async def get_scan_pages(
    scan_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Verify scan exists
    scan_result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    if not scan_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    result = await db.execute(
        select(Page).where(Page.scan_id == scan_id).offset(skip).limit(limit)
    )
    pages = result.scalars().all()
    return pages

@router.get("/{scan_id}/issues", response_model=List[IssueResponse])
async def get_scan_issues(
    scan_id: int,
    severity: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Verify scan exists
    scan_result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    if not scan_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    query = select(Issue).join(Page).where(Page.scan_id == scan_id)
    if severity:
        query = query.where(Issue.severity == severity)
    
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Issue.severity.desc())
    )
    issues = result.scalars().all()
    return issues