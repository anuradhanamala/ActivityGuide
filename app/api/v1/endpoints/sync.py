"""
Manual sync endpoints for ActivityGuide
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.sync import sync_service
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/manual-sync")
async def manual_sync(
    zip_codes: List[str] = Query(..., description="List of ZIP codes to sync")
):
    """
    Manually trigger sync for specific ZIP codes
    
    Example: POST /api/v1/sync/manual-sync?zip_codes=48083&zip_codes=48084&zip_codes=48085
    """
    try:
        logger.info(f"Manual sync requested for ZIP codes: {zip_codes}")
        
        # Run the sync
        results = await sync_service.sync_all_sources(zip_codes)
        
        return {
            "status": "success",
            "message": f"Sync completed for {len(zip_codes)} ZIP codes",
            "zip_codes": zip_codes,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.post("/sync-city")
async def sync_city(
    city: str = Query(..., description="City name (e.g., 'Troy MI', 'Troy, MI', 'troy mi')")
):
    """
    Sync activities for a specific city with 25-mile radius
    
    Example: POST /api/v1/sync/sync-city?city=Troy%20MI
    """
    try:
        # Normalize city name
        city_lower = city.lower().strip()
        
        # Map city names to their zip codes
        city_zip_mapping = {
            "troy": ["48007", "48083", "48084", "48085", "48098", "48099"],
            "troy mi": ["48007", "48083", "48084", "48085", "48098", "48099"],
            "troy, mi": ["48007", "48083", "48084", "48085", "48098", "48099"],
            "troy michigan": ["48007", "48083", "48084", "48085", "48098", "48099"],
            "troy, michigan": ["48007", "48083", "48084", "48085", "48098", "48099"]
        }
        
        # Find matching city
        zip_codes = None
        for city_key, zips in city_zip_mapping.items():
            if city_key in city_lower:
                zip_codes = zips
                break
        
        if not zip_codes:
            # Default to Troy if no match found
            zip_codes = ["48007", "48083", "48084", "48085", "48098", "48099"]
            logger.warning(f"City '{city}' not recognized, defaulting to Troy, MI")
        
        logger.info(f"City sync requested for '{city}' -> ZIP codes: {zip_codes}")
        
        results = await sync_service.sync_all_sources(zip_codes)
        
        return {
            "status": "success",
            "message": f"Sync completed for {city} (25-mile radius)",
            "city": city,
            "zip_codes": zip_codes,
            "radius_miles": 25,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"City sync failed for '{city}': {e}")
        raise HTTPException(status_code=500, detail=f"City sync failed: {str(e)}")

@router.post("/sync-troy")
async def sync_troy():
    """
    Sync all Troy, MI ZIP codes (legacy endpoint)
    """
    troy_zip_codes = ["48007", "48083", "48084", "48085", "48098", "48099"]
    
    try:
        logger.info("Troy sync requested")
        
        results = await sync_service.sync_all_sources(troy_zip_codes)
        
        return {
            "status": "success",
            "message": "Troy, MI sync completed",
            "zip_codes": troy_zip_codes,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Troy sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Troy sync failed: {str(e)}")

@router.get("/sync-status")
async def sync_status():
    """
    Get current sync status and available ZIP codes
    """
    return {
        "status": "active",
        "available_cities": {
            "troy_mi": {
                "zip_codes": ["48007", "48083", "48084", "48085", "48098", "48099"],
                "description": "Troy, Michigan ZIP codes",
                "radius_miles": 25
            }
        },
        "sync_methods": [
            "POST /api/v1/sync/sync-city?city=Troy%20MI",
            "POST /api/v1/sync/sync-city?city=troy%20mi", 
            "POST /api/v1/sync/sync-city?city=Troy,%20MI",
            "POST /api/v1/sync/manual-sync?zip_codes=48083&zip_codes=48084",
            "POST /api/v1/sync/sync-troy"
        ]
    }
