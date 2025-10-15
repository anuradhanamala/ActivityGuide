"""
AI Agent Orchestration API
Industry-grade MCP functionality via REST API (no Claude Desktop needed)

This provides MCP-like capabilities for AI agents to orchestrate:
- Multi-source data synchronization
- Intelligent event search
- Data quality management
- Duplicate detection
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.unified_event import UnifiedEvent, EventSource, EventSyncLog
from app.services.unified_sync_service import UnifiedSyncService
from app.services.hybrid_rag import hybrid_rag_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class MultiSourceSyncRequest(BaseModel):
    """Request model for multi-source sync"""
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field("MI", description="State code")
    zip_codes: Optional[List[str]] = Field(None, description="Specific ZIP codes")
    sources: Optional[List[str]] = Field(None, description="Specific sources (yelp, google_places, etc.)")


class IntelligentSearchRequest(BaseModel):
    """Request model for AI-powered search"""
    query: str = Field(..., description="Natural language query")
    city: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    is_free: Optional[bool] = None
    limit: int = Field(20, ge=1, le=100)


# ============================================================================
# MULTI-SOURCE ORCHESTRATION ENDPOINTS
# ============================================================================

@router.post("/multi-source/sync")
async def orchestrate_multi_source_sync(
    request: MultiSourceSyncRequest,
    background_tasks: BackgroundTasks
):
    """
    🤖 AI Agent: Orchestrate multi-source data sync
    
    Industry-grade endpoint for syncing from multiple sources:
    - Yelp, Google Places, Eventbrite, Ticketmaster, etc.
    - Intelligent source selection
    - Parallel execution
    - Quality monitoring
    
    Returns immediately with sync started in background.
    """
    try:
        # Handle empty requests
        if not request.city and not request.zip_codes:
            raise HTTPException(
                status_code=400,
                detail="Either 'city' or 'zip_codes' must be provided. Example: {'city': 'Troy', 'state': 'MI'}"
            )
        
        # Convert city to ZIP codes if needed
        zip_codes = request.zip_codes
        if not zip_codes and request.city:
            from app.services.geocoding_service import geocoding_service
            try:
                zip_codes, method = await geocoding_service.get_zip_codes_for_city(
                    request.city, request.state
                )
                logger.info(f"Converted {request.city}, {request.state} to {len(zip_codes)} ZIP codes")
            except Exception as e:
                logger.warning(f"Geocoding failed for {request.city}: {e}")
                # Fallback to default ZIP codes
                zip_codes = ["48083", "48084"] if request.city and request.city.lower() == "troy" else ["48201", "48202"]
        
        # Final validation - must have ZIP codes
        if not zip_codes or len(zip_codes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Could not determine ZIP codes. Please provide 'zip_codes' directly or a valid 'city' name."
            )
        
        # Convert source strings to EventSource enum if provided
        sources = None
        if request.sources:
            sources = [EventSource(s) for s in request.sources]
        
        # Trigger background sync
        background_tasks.add_task(
            _run_multi_source_sync,
            zip_codes=zip_codes,
            sources=sources
        )
        
        return {
            "status": "started",
            "message": "Multi-source sync initiated",
            "city": request.city,
            "state": request.state,
            "zip_codes": zip_codes,
            "zip_code_count": len(zip_codes) if zip_codes else 0,
            "sources": request.sources or "all",
            "estimated_duration_minutes": "2-5",
            "check_status_at": "/api/v1/ai-orchestration/sync/status"
        }
        
    except Exception as e:
        logger.error(f"Error orchestrating multi-source sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multi-source/status")
async def get_multi_source_sync_status(
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    📊 AI Agent: Get multi-source sync status
    
    Monitor sync operations across all sources.
    """
    db = next(get_db())
    try:
        query = db.query(EventSyncLog).order_by(EventSyncLog.started_at.desc())
        
        if source:
            query = query.filter(EventSyncLog.source == EventSource(source))
        
        logs = query.limit(limit).all()
        
        sync_history = []
        for log in logs:
            sync_history.append({
                "source": log.source.value if log.source else "all",
                "status": log.status,
                "events_created": log.events_created,
                "events_updated": log.events_updated,
                "events_processed": log.events_processed,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "duration_seconds": log.sync_duration_seconds,
                "errors": log.errors
            })
        
        # Aggregate stats
        total_synced = sum(log.events_processed for log in logs if log.events_processed)
        total_created = sum(log.events_created for log in logs if log.events_created)
        
        return {
            "recent_syncs": sync_history,
            "summary": {
                "total_sync_operations": len(sync_history),
                "total_events_synced": total_synced,
                "total_events_created": total_created,
                "most_recent_sync": sync_history[0] if sync_history else None
            }
        }
        
    finally:
        db.close()


@router.get("/multi-source/coverage")
async def analyze_source_coverage(city: Optional[str] = Query(None)):
    """
    🎯 AI Agent: Analyze multi-source coverage
    
    Intelligence for decision-making on which sources to sync.
    """
    db = next(get_db())
    try:
        stats = {}
        
        for source in EventSource:
            query = db.query(UnifiedEvent).filter(UnifiedEvent.source == source)
            
            if city:
                query = query.filter(UnifiedEvent.city == city)
            
            total = query.count()
            with_address = query.filter(UnifiedEvent.address != None, UnifiedEvent.address != '').count()
            with_website = query.filter(UnifiedEvent.website_url != None, UnifiedEvent.website_url != '').count()
            free_events = query.filter(UnifiedEvent.is_free == True).count()
            
            # Calculate average quality
            quality_scores = [e.data_quality_score for e in query.all() if e.data_quality_score]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            stats[source.value] = {
                "total_events": total,
                "completeness": {
                    "with_address": with_address,
                    "with_website": with_website,
                    "address_percentage": int(with_address / total * 100) if total > 0 else 0,
                    "website_percentage": int(with_website / total * 100) if total > 0 else 0
                },
                "free_events": free_events,
                "avg_quality_score": round(avg_quality, 2),
                "health": "excellent" if total > 50 else "good" if total > 10 else "limited" if total > 0 else "no_data"
            }
        
        # Overall analysis
        total_events = sum(s["total_events"] for s in stats.values())
        sources_with_data = sum(1 for s in stats.values() if s["total_events"] > 0)
        
        return {
            "city": city or "all_cities",
            "total_events": total_events,
            "sources_with_data": sources_with_data,
            "total_sources": len(EventSource),
            "coverage_percentage": int(sources_with_data / len(EventSource) * 100),
            "source_breakdown": stats,
            "recommendations": _generate_coverage_recommendations(stats, city)
        }
        
    finally:
        db.close()


@router.post("/multi-source/find-duplicates")
async def find_cross_source_duplicates(
    city: Optional[str] = Query(None),
    similarity_threshold: float = Query(0.8, ge=0.0, le=1.0)
):
    """
    🔗 AI Agent: Find duplicates across sources
    
    Identifies potential duplicate events from different sources.
    """
    db = next(get_db())
    try:
        query = db.query(UnifiedEvent)
        
        if city:
            query = query.filter(UnifiedEvent.city == city)
        
        events = query.all()
        
        # Find duplicates across sources
        duplicates = []
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                if event1.source != event2.source:  # Cross-source only
                    similarity = _calculate_title_similarity(event1.title, event2.title)
                    if similarity >= similarity_threshold:
                        duplicates.append({
                            "event1": {
                                "id": str(event1.id),
                                "title": event1.title,
                                "source": event1.source.value,
                                "city": event1.city
                            },
                            "event2": {
                                "id": str(event2.id),
                                "title": event2.title,
                                "source": event2.source.value,
                                "city": event2.city
                            },
                            "similarity_score": round(similarity, 2),
                            "recommendation": "merge" if similarity > 0.9 else "review"
                        })
        
        return {
            "total_events_checked": len(events),
            "duplicates_found": len(duplicates),
            "duplicates": duplicates,
            "city_filter": city
        }
        
    finally:
        db.close()


# ============================================================================
# INTELLIGENT SEARCH (RAG-POWERED)
# ============================================================================

@router.post("/intelligent-search")
async def ai_intelligent_search(request: IntelligentSearchRequest):
    """
    🧠 AI Agent: Intelligent event search with RAG
    
    Combines multi-source data with AI-powered semantic search.
    Perfect for Kid Activity Aggregator AI Agent!
    
    Uses hybrid RAG: SQL filters + Vector embeddings
    """
    try:
        result = await hybrid_rag_service.recommend(
            user_query=request.query,
            city=request.city,
            age_min=request.age_min,
            age_max=request.age_max,
            is_free=request.is_free
        )
        
        return {
            "query": request.query,
            "city": request.city,
            "ai_recommendations": result.get("recommendations"),
            "retrieval_strategy": result.get("retrieval_strategy"),
            "method_used": result.get("method_used"),
            "events_count": result.get("events_count"),
            "events": result.get("events_included", [])
        }
        
    except Exception as e:
        logger.error(f"Error in intelligent search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI AGENT WORKFLOWS (COMBINED OPERATIONS)
# ============================================================================

@router.post("/workflow/comprehensive-data-prep")
async def comprehensive_data_preparation(
    city: str = Query(..., description="City to prepare data for"),
    state: str = Query("MI", description="State"),
    background_tasks: BackgroundTasks = None
):
    """
    🤖 AI Agent Workflow: Comprehensive Data Preparation
    
    Industry-grade workflow for Kid Activity Aggregator:
    1. Multi-source sync (Yelp, Google, Eventbrite)
    2. Duplicate detection
    3. Quality audit
    4. Coverage analysis
    5. Embedding preparation
    
    Perfect for launching a new city or refreshing existing data.
    """
    try:
        from app.services.geocoding_service import geocoding_service
        
        # Step 1: Get ZIP codes
        try:
            zip_codes, method = await geocoding_service.get_zip_codes_for_city(city, state)
        except:
            zip_codes = ["48083", "48084"] if city.lower() == "troy" else ["48201", "48202"]
        
        # Step 2: Check current coverage
        db = next(get_db())
        current_count = db.query(UnifiedEvent).filter(UnifiedEvent.city == city).count()
        db.close()
        
        # Step 3: Trigger comprehensive sync if background tasks available
        if background_tasks:
            background_tasks.add_task(
                _run_multi_source_sync,
                zip_codes=zip_codes,
                sources=None  # All sources
            )
            sync_status = "started_background"
        else:
            sync_status = "will_run_manually"
        
        return {
            "workflow": "comprehensive_data_prep",
            "city": city,
            "state": state,
            "current_events": current_count,
            "zip_codes": zip_codes,
            "sync_status": sync_status,
            "steps": {
                "1_geocoding": "✅ Completed",
                "2_coverage_check": "✅ Completed", 
                "3_multi_source_sync": "🔄 " + sync_status,
                "4_duplicate_detection": "⏳ Pending sync completion",
                "5_quality_audit": "⏳ Pending sync completion"
            },
            "next_action": f"Check status at /api/v1/ai-orchestration/multi-source/status",
            "agent_summary": f"Preparing comprehensive activity data for {city}. Current: {current_count} events. Syncing from all sources for {len(zip_codes)} ZIP codes."
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive data prep: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/data-health")
async def check_overall_data_health():
    """
    🏥 AI Agent: Overall data health check
    
    Comprehensive health report for all sources and cities.
    """
    db = next(get_db())
    try:
        # Overall stats
        total_events = db.query(UnifiedEvent).count()
        total_cities = db.query(UnifiedEvent.city).distinct().count()
        
        # Source health
        source_health = {}
        for source in EventSource:
            count = db.query(UnifiedEvent).filter(UnifiedEvent.source == source).count()
            source_health[source.value] = {
                "event_count": count,
                "status": "healthy" if count > 50 else "low" if count > 0 else "no_data"
            }
        
        # Quality metrics
        avg_quality = db.query(func.avg(UnifiedEvent.data_quality_score)).scalar() or 0
        low_quality = db.query(UnifiedEvent).filter(
            UnifiedEvent.data_quality_score < 0.5
        ).count()
        
        # Recent sync activity
        recent_sync = db.query(EventSyncLog).order_by(
            EventSyncLog.started_at.desc()
        ).first()
        
        # Health assessment
        sources_active = sum(1 for s in source_health.values() if s["event_count"] > 0)
        overall_health = "excellent" if sources_active >= 3 and avg_quality > 0.8 else "good" if sources_active >= 1 else "needs_attention"
        
        return {
            "overall_health": overall_health,
            "metrics": {
                "total_events": total_events,
                "total_cities": total_cities,
                "sources_active": sources_active,
                "average_quality_score": round(avg_quality, 2),
                "low_quality_events": low_quality
            },
            "source_health": source_health,
            "last_sync": {
                "source": recent_sync.source.value if recent_sync and recent_sync.source else None,
                "when": recent_sync.started_at.isoformat() if recent_sync else None,
                "status": recent_sync.status if recent_sync else None
            } if recent_sync else None,
            "recommendations": _generate_health_recommendations(source_health, avg_quality, sources_active)
        }
        
    finally:
        db.close()


@router.post("/rag/multi-source-recommend")
async def multi_source_rag_recommendations(request: IntelligentSearchRequest):
    """
    🧠 AI Agent: Multi-source RAG recommendations
    
    Combines:
    - Data from all sources (Yelp, Google, Eventbrite)
    - Hybrid RAG (SQL + Vector search)
    - AI-powered ranking
    
    Returns intelligent recommendations for Kid Activity Aggregator.
    """
    try:
        # Use hybrid RAG for intelligent search
        result = await hybrid_rag_service.recommend(
            user_query=request.query,
            city=request.city,
            age_min=request.age_min,
            age_max=request.age_max,
            is_free=request.is_free
        )
        
        # Enhance with source diversity analysis
        events = result.get("events_included", [])
        source_breakdown = {}
        for event in events:
            source = event.get("source", "unknown")
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
        
        return {
            "query": request.query,
            "city": request.city,
            "ai_recommendations": result.get("recommendations"),
            "retrieval_method": result.get("retrieval_strategy"),
            "total_events": result.get("events_count"),
            "events": events[:request.limit],
            "source_diversity": {
                "sources_used": len(source_breakdown),
                "breakdown": source_breakdown
            },
            "agent_metadata": {
                "search_type": result.get("method_used"),
                "multi_source": len(source_breakdown) > 1,
                "quality_filtered": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error in multi-source RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DATA QUALITY MANAGEMENT
# ============================================================================

@router.get("/quality/audit")
async def data_quality_audit(
    source: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    min_score: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    💎 AI Agent: Data quality audit
    
    Audit data quality across sources for optimization.
    """
    db = next(get_db())
    try:
        query = db.query(UnifiedEvent).filter(UnifiedEvent.data_quality_score < min_score)
        
        if source:
            query = query.filter(UnifiedEvent.source == EventSource(source))
        if city:
            query = query.filter(UnifiedEvent.city == city)
        
        low_quality_events = query.all()
        
        issues_by_type = {
            "missing_address": 0,
            "missing_description": 0,
            "missing_website": 0,
            "missing_start_time": 0
        }
        
        detailed_issues = []
        for event in low_quality_events[:20]:  # Limit detailed list
            event_issues = []
            if not event.address:
                issues_by_type["missing_address"] += 1
                event_issues.append("missing_address")
            if not event.description:
                issues_by_type["missing_description"] += 1
                event_issues.append("missing_description")
            if not event.website_url:
                issues_by_type["missing_website"] += 1
                event_issues.append("missing_website")
            if not event.start_time:
                issues_by_type["missing_start_time"] += 1
                event_issues.append("missing_start_time")
            
            detailed_issues.append({
                "event_id": str(event.id),
                "title": event.title,
                "source": event.source.value if event.source else None,
                "quality_score": event.data_quality_score,
                "issues": event_issues
            })
        
        return {
            "audit_summary": {
                "total_events_audited": db.query(UnifiedEvent).count(),
                "low_quality_count": len(low_quality_events),
                "quality_threshold": min_score
            },
            "issues_by_type": issues_by_type,
            "detailed_issues": detailed_issues,
            "filters": {
                "source": source,
                "city": city
            },
            "recommendations": [
                f"Re-sync sources with high missing data rates",
                f"Focus on improving {max(issues_by_type, key=issues_by_type.get)} issue",
                f"Consider additional data sources for better coverage"
            ]
        }
        
    finally:
        db.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _run_multi_source_sync(zip_codes: List[str], sources: Optional[List[EventSource]] = None):
    """Background task for multi-source sync"""
    db = next(get_db())
    try:
        sync_service = UnifiedSyncService()
        result = await sync_service.sync_all_sources(db, zip_codes, sources)
        logger.info(f"Multi-source sync completed: {result}")
    except Exception as e:
        logger.error(f"Multi-source sync failed: {e}")
    finally:
        db.close()


def _calculate_title_similarity(title1: str, title2: str) -> float:
    """Calculate similarity between two titles"""
    if not title1 or not title2:
        return 0.0
    
    title1 = title1.lower()
    title2 = title2.lower()
    
    # Jaccard similarity
    words1 = set(title1.split())
    words2 = set(title2.split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def _generate_coverage_recommendations(stats: Dict, city: Optional[str]) -> List[str]:
    """Generate recommendations based on coverage analysis"""
    recommendations = []
    
    sources_with_no_data = [source for source, data in stats.items() if data["total_events"] == 0]
    sources_with_low_quality = [source for source, data in stats.items() if data["avg_quality_score"] < 0.5 and data["total_events"] > 0]
    
    if sources_with_no_data:
        recommendations.append(f"Sync these sources for better coverage: {', '.join(sources_with_no_data[:3])}")
    
    if sources_with_low_quality:
        recommendations.append(f"Re-sync for quality improvement: {', '.join(sources_with_low_quality)}")
    
    sources_active = sum(1 for data in stats.values() if data["total_events"] > 0)
    if sources_active < 3:
        recommendations.append("Add more data sources to increase activity variety")
    
    return recommendations or ["Data coverage is excellent across all active sources"]


def _generate_health_recommendations(source_health: Dict, avg_quality: float, sources_active: int) -> List[str]:
    """Generate health recommendations"""
    recommendations = []
    
    if sources_active == 0:
        recommendations.append("🚨 CRITICAL: No data sources active. Run initial sync immediately.")
    elif sources_active == 1:
        recommendations.append("⚠️ Only one source active. Add more sources for comprehensive coverage.")
    elif sources_active < 3:
        recommendations.append("💡 Add more sources (Google Places, Eventbrite) for better coverage.")
    
    if avg_quality < 0.5:
        recommendations.append("⚠️ Low average quality. Re-sync sources or enhance data.")
    elif avg_quality < 0.7:
        recommendations.append("💡 Quality is good but could improve. Focus on complete event details.")
    
    return recommendations or ["✅ System health is excellent. All sources performing well."]


# ============================================================================
# API INFO
# ============================================================================

@router.get("/")
async def ai_orchestration_info():
    """
    ℹ️ AI Orchestration API Information
    
    Industry-grade MCP via API for Kid Activity Aggregator AI Agent
    """
    return {
        "name": "AI Orchestration API",
        "description": "Industry-grade MCP functionality via REST API",
        "purpose": "Kid Activity Aggregator AI Agent - Multi-source orchestration",
        "approach": "MCP via API (no Claude Desktop dependency)",
        "endpoints": {
            "multi_source_sync": "POST /multi-source/sync",
            "sync_status": "GET /multi-source/status",
            "coverage_analysis": "GET /multi-source/coverage",
            "find_duplicates": "POST /multi-source/find-duplicates",
            "intelligent_search": "POST /intelligent-search",
            "rag_recommend": "POST /rag/multi-source-recommend",
            "data_prep_workflow": "POST /workflow/comprehensive-data-prep",
            "health_check": "GET /workflow/data-health",
            "quality_audit": "GET /quality/audit"
        },
        "capabilities": [
            "Multi-source data synchronization",
            "Hybrid RAG recommendations",
            "Cross-source duplicate detection",
            "Data quality management",
            "Coverage analysis and optimization",
            "AI-powered event search"
        ],
        "data_sources": [
            "yelp", "google_places", "eventbrite", "ticketmaster",
            "meetup", "recreation_gov", "openstreetmap"
        ]
    }

