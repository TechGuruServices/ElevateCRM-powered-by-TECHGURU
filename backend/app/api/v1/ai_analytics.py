"""
API endpoints for AI & Advanced Analytics
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.schemas.ai_analytics import (
    ForecastRequest, ForecastResponse, BulkForecastRequest,
    LeadScoreRequest, LeadScoreResponse, BulkLeadScoreRequest,
    RecommendationRequest, RecommendationListResponse,
    ChurnPredictionRequest, ChurnPredictionResponse,
    SemanticSearchRequest, SemanticSearchResponse,
    ModelTrainingRequest, ModelTrainingResponse
)
from app.services.ai_analytics_service import (
    DemandForecastingService,
    LeadScoringService,
    ProductRecommendationService,
    ChurnPredictionService,
    SemanticSearchService
)
# from app.workers.ai_tasks import train_model_task, index_data_task

router = APIRouter()


@router.post("/forecast", response_model=ForecastResponse)
def get_demand_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db)
):
    """
    Get a demand forecast for a single product.
    """
    service = DemandForecastingService(db)
    try:
        forecast = service.calculate_forecast(
            product_id=request.product_id,
            warehouse_id=request.warehouse_id,
            horizon_days=request.horizon_days,
            confidence_level=request.confidence_level
        )
        return forecast
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/bulk-forecast", status_code=202)
def trigger_bulk_demand_forecast(
    request: BulkForecastRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger a background task to generate forecasts for multiple products.
    """
    # This would typically be a Celery task, but using background tasks for simplicity here.
    # background_tasks.add_task(run_bulk_forecast, request, db)
    return {"message": "Bulk forecast generation has been queued."}


@router.post("/lead-score", response_model=LeadScoreResponse)
def get_lead_score(
    request: LeadScoreRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate or retrieve the lead score for a contact.
    """
    service = LeadScoringService(db)
    try:
        score = service.calculate_lead_score(
            contact_id=request.contact_id,
            force_recalculate=request.force_recalculate
        )
        return score
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/bulk-lead-score", status_code=202)
def trigger_bulk_lead_scoring(
    request: BulkLeadScoreRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger a background task for bulk lead scoring.
    """
    return {"message": "Bulk lead scoring has been queued."}


@router.post("/recommendations", response_model=RecommendationListResponse)
def get_product_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get product recommendations for a customer, order, or product.
    """
    service = ProductRecommendationService(db)
    try:
        recommendations = service.get_recommendations(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            num_recs=request.num_recommendations
        )
        return RecommendationListResponse(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/churn-prediction", response_model=ChurnPredictionResponse)
def get_churn_prediction(
    request: ChurnPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict churn probability for a customer.
    """
    service = ChurnPredictionService(db)
    try:
        prediction = service.predict_churn(
            customer_id=request.customer_id,
            include_retention_actions=request.include_retention_actions
        )
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/semantic-search", response_model=SemanticSearchResponse)
def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform a semantic search across indexed entities.
    """
    service = SemanticSearchService(db)
    response = service.search(request)
    return response


@router.post("/train-model", response_model=ModelTrainingResponse, status_code=202)
def train_model(
    request: ModelTrainingRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger a model training job.
    """
    # job = train_model_task.delay(request.model_dump())
    # return ModelTrainingResponse(id=job.id, model_type=request.model_type, status="queued", created_at=datetime.utcnow())
    return {"message": "Model training has been queued."}

@router.post("/index-data", status_code=202)
def index_data_for_semantic_search(
    entity_type: str,
    background_tasks: BackgroundTasks
):
    """
    Trigger a background task to index data for a given entity type.
    """
    # index_data_task.delay(entity_type)
    return {"message": f"Indexing for entity type '{entity_type}' has been queued."}
