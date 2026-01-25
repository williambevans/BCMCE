"""
County Scraper API
Endpoints for scraping and managing county bid requests
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..database import get_db, ScrapedBid as ScrapedBidModel
from ..models.schemas import ScrapedBid, ScrapeSummary, SuccessResponse
from ..scrapers.bosque_scraper import BosqueScraper
from .auth import get_current_user
from ..database import User as UserModel

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# SCRAPING ENDPOINTS
# ============================================================================

@router.post("/scrape/bosque", response_model=ScrapeSummary)
async def scrape_bosque_county(
    force_refresh: bool = Query(False, description="Force rescrape even if recent data exists"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scrape bid requests from Bosque County website

    Args:
        force_refresh: Skip cache check and scrape fresh data
        current_user: Authenticated user
        db: Database session

    Returns:
        Summary of scraping operation
    """
    logger.info(f"User {current_user.email} initiated Bosque County scrape")

    # Check if we have recent data (within last 6 hours)
    if not force_refresh:
        six_hours_ago = datetime.utcnow() - timedelta(hours=6)
        recent_count = db.query(ScrapedBidModel).filter(
            ScrapedBidModel.county_name == "BOSQUE",
            ScrapedBidModel.scraped_at > six_hours_ago
        ).count()

        if recent_count > 0:
            logger.info(f"Found {recent_count} recent Bosque County bids, skipping scrape")
            return ScrapeSummary(
                county_name="BOSQUE",
                total_bids=recent_count,
                new_bids=0,
                scraped_at=datetime.utcnow()
            )

    try:
        # Initialize scraper
        scraper = BosqueScraper()

        # Scrape bids
        bids = scraper.scrape_bids()

        logger.info(f"Scraped {len(bids)} bids from Bosque County")

        # Store in database
        new_bids = 0
        for bid_data in bids:
            # Check if this bid already exists (by URL or title)
            existing = None
            if bid_data.get('url'):
                existing = db.query(ScrapedBidModel).filter(
                    ScrapedBidModel.county_name == "BOSQUE",
                    ScrapedBidModel.url == bid_data['url']
                ).first()

            if not existing and bid_data.get('title'):
                existing = db.query(ScrapedBidModel).filter(
                    ScrapedBidModel.county_name == "BOSQUE",
                    ScrapedBidModel.title == bid_data['title']
                ).first()

            if not existing:
                # Create new scraped bid record
                scraped_bid = ScrapedBidModel(
                    county_name="BOSQUE",
                    title=bid_data.get('title', 'Untitled'),
                    url=bid_data.get('url'),
                    description=bid_data.get('description'),
                    date_posted=bid_data.get('date_posted'),
                    deadline=bid_data.get('deadline'),
                    category=bid_data.get('category'),
                    source=bid_data.get('source', 'scraper'),
                    section=bid_data.get('section'),
                    scraped_at=datetime.utcnow()
                )
                db.add(scraped_bid)
                new_bids += 1

        db.commit()

        logger.info(f"Stored {new_bids} new bids in database")

        return ScrapeSummary(
            county_name="BOSQUE",
            total_bids=len(bids),
            new_bids=new_bids,
            scraped_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Failed to scrape Bosque County: {e}")
        db.rollback()
        return ScrapeSummary(
            county_name="BOSQUE",
            total_bids=0,
            new_bids=0,
            failed=True,
            error_message=str(e),
            scraped_at=datetime.utcnow()
        )


@router.get("/scraped-bids", response_model=List[ScrapedBid])
async def get_scraped_bids(
    county_name: Optional[str] = Query(None, description="Filter by county name"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    unprocessed_only: bool = Query(False, description="Show only unprocessed bids"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get scraped bid requests

    Args:
        county_name: Filter by county name
        limit: Maximum results to return
        offset: Results to skip (for pagination)
        unprocessed_only: Only show bids not yet processed
        current_user: Authenticated user
        db: Database session

    Returns:
        List of scraped bids
    """
    query = db.query(ScrapedBidModel)

    # Apply filters
    if county_name:
        query = query.filter(ScrapedBidModel.county_name == county_name.upper())

    if unprocessed_only:
        query = query.filter(ScrapedBidModel.is_processed == False)

    # Order by most recent first
    query = query.order_by(ScrapedBidModel.scraped_at.desc())

    # Apply pagination
    bids = query.offset(offset).limit(limit).all()

    # Convert to response schema
    return [
        ScrapedBid(
            id=str(bid.id),
            county_name=bid.county_name,
            title=bid.title,
            url=bid.url,
            description=bid.description,
            date_posted=bid.date_posted,
            deadline=bid.deadline,
            category=bid.category,
            source=bid.source,
            section=bid.section,
            is_processed=bid.is_processed,
            scraped_at=bid.scraped_at,
            created_at=bid.created_at,
            updated_at=bid.updated_at
        )
        for bid in bids
    ]


@router.get("/scraped-bids/{bid_id}", response_model=ScrapedBid)
async def get_scraped_bid(
    bid_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific scraped bid by ID

    Args:
        bid_id: Bid UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        Scraped bid details
    """
    bid = db.query(ScrapedBidModel).filter(ScrapedBidModel.id == bid_id).first()

    if not bid:
        raise HTTPException(status_code=404, detail="Scraped bid not found")

    return ScrapedBid(
        id=str(bid.id),
        county_name=bid.county_name,
        title=bid.title,
        url=bid.url,
        description=bid.description,
        date_posted=bid.date_posted,
        deadline=bid.deadline,
        category=bid.category,
        source=bid.source,
        section=bid.section,
        is_processed=bid.is_processed,
        scraped_at=bid.scraped_at,
        created_at=bid.created_at,
        updated_at=bid.updated_at
    )


@router.post("/scraped-bids/{bid_id}/mark-processed", response_model=SuccessResponse)
async def mark_bid_processed(
    bid_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a scraped bid as processed

    Args:
        bid_id: Bid UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        Success response
    """
    bid = db.query(ScrapedBidModel).filter(ScrapedBidModel.id == bid_id).first()

    if not bid:
        raise HTTPException(status_code=404, detail="Scraped bid not found")

    bid.is_processed = True
    bid.updated_at = datetime.utcnow()
    db.commit()

    logger.info(f"User {current_user.email} marked bid {bid_id} as processed")

    return SuccessResponse(
        success=True,
        message="Bid marked as processed",
        data={"bid_id": str(bid.id)}
    )


@router.delete("/scraped-bids/{bid_id}", response_model=SuccessResponse)
async def delete_scraped_bid(
    bid_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a scraped bid

    Args:
        bid_id: Bid UUID
        current_user: Authenticated user (must be admin)
        db: Database session

    Returns:
        Success response
    """
    # Only admins can delete
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete scraped bids")

    bid = db.query(ScrapedBidModel).filter(ScrapedBidModel.id == bid_id).first()

    if not bid:
        raise HTTPException(status_code=404, detail="Scraped bid not found")

    db.delete(bid)
    db.commit()

    logger.info(f"Admin {current_user.email} deleted scraped bid {bid_id}")

    return SuccessResponse(
        success=True,
        message="Scraped bid deleted",
        data={"bid_id": bid_id}
    )


@router.get("/scrape/stats")
async def get_scrape_stats(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about scraped bids

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Statistics summary
    """
    total_bids = db.query(ScrapedBidModel).count()
    unprocessed_bids = db.query(ScrapedBidModel).filter(
        ScrapedBidModel.is_processed == False
    ).count()

    # Get count by county
    from sqlalchemy import func
    county_stats = db.query(
        ScrapedBidModel.county_name,
        func.count(ScrapedBidModel.id).label('count')
    ).group_by(ScrapedBidModel.county_name).all()

    # Get recent scrape times
    recent_scrapes = db.query(
        ScrapedBidModel.county_name,
        func.max(ScrapedBidModel.scraped_at).label('last_scraped')
    ).group_by(ScrapedBidModel.county_name).all()

    return {
        "total_bids": total_bids,
        "unprocessed_bids": unprocessed_bids,
        "processed_bids": total_bids - unprocessed_bids,
        "by_county": [
            {"county": county, "count": count}
            for county, count in county_stats
        ],
        "last_scrapes": [
            {"county": county, "last_scraped": last_scraped.isoformat()}
            for county, last_scraped in recent_scrapes
        ]
    }
