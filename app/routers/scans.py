from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
import tempfile
import os

from app.database import get_db
from app.models import Scan, Website, Page, Issue
from app.schemas import ScanCreate, ScanResponse, PageResponse, IssueResponse
from app.tasks.scan_tasks import run_website_scan, run_enterprise_website_scan
from app.services.report_service import ReportService
from celery import current_app as celery_app

router = APIRouter(prefix="/scans", tags=["scans"])

@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan: ScanCreate,
    db: AsyncSession = Depends(get_db),
    scan_type: str = "enterprise"  # "enterprise" or "basic"
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
    
    # Queue scan task with Celery - choose scan type
    if scan_type.lower() == "enterprise":
        task = run_enterprise_website_scan.delay(website.id, db_scan.id)
        db_scan.config = {"celery_task_id": task.id, "scan_type": "enterprise"}
    else:
        task = run_website_scan.delay(website.id, db_scan.id)
        db_scan.config = {"celery_task_id": task.id, "scan_type": "basic"}
    
    await db.commit()
    
    return db_scan

@router.post("/enterprise", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_enterprise_scan(
    scan: ScanCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create enterprise scan with sitemap-based URL discovery"""
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
    
    # Queue enterprise scan task
    task = run_enterprise_website_scan.delay(website.id, db_scan.id)
    db_scan.config = {"celery_task_id": task.id, "scan_type": "enterprise"}
    await db.commit()
    
    return db_scan

@router.get("/", response_model=List[ScanResponse])
async def list_scans(
    website_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Scan).options(selectinload(Scan.website))  # Eager load website for potential UI display
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
        select(Scan).options(selectinload(Scan.website)).where(Scan.id == scan_id)  # Eager load website
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
    
    from sqlalchemy.orm import selectinload
    
    query = select(Issue).join(Page).where(Page.scan_id == scan_id).options(selectinload(Issue.page))
    if severity:
        query = query.where(Issue.severity == severity)
    
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Issue.severity.desc())
    )
    issues = result.scalars().all()
    return issues

@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a scan and all its associated data"""
    # Get scan with task info
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Cancel Celery task if it exists and is running
    if scan.config and 'celery_task_id' in scan.config:
        task_id = scan.config['celery_task_id']
        try:
            celery_app.control.revoke(task_id, terminate=True)
        except Exception as e:
            print(f"Error cancelling Celery task {task_id}: {e}")
    
    # Delete associated issues first (through pages)
    pages_result = await db.execute(
        select(Page).where(Page.scan_id == scan_id)
    )
    pages = pages_result.scalars().all()
    
    for page in pages:
        # Delete issues for this page
        issues_result = await db.execute(
            select(Issue).where(Issue.page_id == page.id)
        )
        issues = issues_result.scalars().all()
        for issue in issues:
            await db.delete(issue)
        await db.delete(page)
    
    # Delete the scan
    await db.delete(scan)
    await db.commit()
    
    return {"detail": "Scan deleted successfully"}

@router.post("/{scan_id}/retry", response_model=ScanResponse)
async def retry_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed or stuck scan"""
    # Get scan
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Get website with client relationship
    website_result = await db.execute(
        select(Website).options(selectinload(Website.client)).where(Website.id == scan.website_id)
    )
    website = website_result.scalar_one_or_none()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated website not found"
        )
    
    # Cancel existing task if running
    if scan.config and 'celery_task_id' in scan.config:
        task_id = scan.config['celery_task_id']
        try:
            celery_app.control.revoke(task_id, terminate=True)
        except Exception as e:
            print(f"Error cancelling existing task {task_id}: {e}")
    
    # Reset scan status and start new task
    scan.status = "pending"
    scan.error_message = None
    scan.pages_scanned = 0
    scan.pages_failed = 0
    scan.total_issues = 0
    scan.completed_at = None
    
    # Queue new scan task
    task = run_website_scan.delay(website.id, scan.id)
    scan.config = {"celery_task_id": task.id}
    
    await db.commit()
    await db.refresh(scan)
    
    return scan

@router.get("/{scan_id}/report")
async def download_scan_report(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Generate and download a PDF report for a scan"""
    # Get scan with related data
    scan_result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = scan_result.scalar_one_or_none()
    
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    if scan.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report can only be generated for completed scans"
        )
    
    # Get website with client relationship
    website_result = await db.execute(
        select(Website).options(selectinload(Website.client)).where(Website.id == scan.website_id)
    )
    website = website_result.scalar_one_or_none()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated website not found"
        )
    
    # Get pages and issues
    pages_result = await db.execute(
        select(Page).where(Page.scan_id == scan_id)
    )
    pages = pages_result.scalars().all()
    
    issues_result = await db.execute(
        select(Issue).join(Page).where(Page.scan_id == scan_id)
    )
    issues = issues_result.scalars().all()
    
    try:
        # Generate PDF report
        report_service = ReportService()
        pdf_path = report_service.generate_scan_report(scan, website, pages, issues)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seo_report_{website.domain.replace('https://', '').replace('http://', '').replace('/', '_')}_{timestamp}.pdf"
        
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf",
            background=None  # File will be deleted after response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

@router.post("/{scan_id}/cancel", response_model=ScanResponse)
async def cancel_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running scan"""
    # Get scan
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Only allow cancelling running or pending scans
    if scan.status not in ["running", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel scan with status: {scan.status}"
        )
    
    # Cancel Celery task
    if scan.config and 'celery_task_id' in scan.config:
        task_id = scan.config['celery_task_id']
        try:
            celery_app.control.revoke(task_id, terminate=True)
        except Exception as e:
            print(f"Error cancelling Celery task {task_id}: {e}")
    
    # Update scan status
    scan.status = "cancelled"
    scan.error_message = "Scan cancelled by user"
    
    await db.commit()
    await db.refresh(scan)
    
    return scan

@router.get("/{scan_id}/report")
async def download_scan_report(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Generate and download a PDF report for a scan"""
    # Get scan with related data
    scan_result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = scan_result.scalar_one_or_none()
    
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    if scan.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report can only be generated for completed scans"
        )
    
    # Get website with client relationship
    website_result = await db.execute(
        select(Website).options(selectinload(Website.client)).where(Website.id == scan.website_id)
    )
    website = website_result.scalar_one_or_none()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated website not found"
        )
    
    # Get pages and issues
    pages_result = await db.execute(
        select(Page).where(Page.scan_id == scan_id)
    )
    pages = pages_result.scalars().all()
    
    issues_result = await db.execute(
        select(Issue).join(Page).where(Page.scan_id == scan_id)
    )
    issues = issues_result.scalars().all()
    
    try:
        # Generate PDF report
        report_service = ReportService()
        pdf_path = report_service.generate_scan_report(scan, website, pages, issues)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seo_report_{website.domain.replace('https://', '').replace('http://', '').replace('/', '_')}_{timestamp}.pdf"
        
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf",
            background=None  # File will be deleted after response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )