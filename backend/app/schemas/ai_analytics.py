"""
AI & Analytics Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# Base schemas
class AIModelBase(BaseModel):
    name: str
    model_type: str
    version: str
    algorithm: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}
    is_active: bool = True


class AIModelCreate(AIModelBase):
    pass


class AIModelUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None


class AIModelResponse(AIModelBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    metrics: Dict[str, Any] = {}
    training_data_info: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    trained_at: Optional[datetime] = None


# Demand Forecasting schemas
class ForecastRequest(BaseModel):
    product_id: UUID
    warehouse_id: Optional[UUID] = None
    horizon_days: int = Field(default=30, ge=1, le=365)
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.99)


class ForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    warehouse_id: Optional[UUID] = None
    forecast_date: datetime
    forecast_horizon_days: int
    predicted_demand: float
    lower_bound: float
    upper_bound: float
    confidence_level: float
    seasonality_component: Dict[str, Any] = {}
    trend_component: Dict[str, Any] = {}
    stockout_probability: float
    recommended_reorder_point: int
    recommended_order_quantity: int
    created_at: datetime


class BulkForecastRequest(BaseModel):
    product_ids: Optional[List[UUID]] = None  # None means all products
    warehouse_id: Optional[UUID] = None
    horizon_days: int = Field(default=30, ge=1, le=365)
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.99)


# Lead Scoring schemas
class LeadScoreRequest(BaseModel):
    contact_id: UUID
    force_recalculate: bool = False


class LeadScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    contact_id: UUID
    score: float = Field(ge=0, le=100)
    score_grade: str
    scoring_factors: Dict[str, Any] = {}
    top_positive_factors: List[str] = []
    top_negative_factors: List[str] = []
    engagement_score: Optional[float] = None
    demographic_score: Optional[float] = None
    behavioral_score: Optional[float] = None
    firmographic_score: Optional[float] = None
    conversion_probability: float
    recommended_actions: List[str] = []
    last_calculated: datetime
    next_calculation: Optional[datetime] = None


class BulkLeadScoreRequest(BaseModel):
    contact_ids: Optional[List[UUID]] = None  # None means all contacts
    force_recalculate: bool = False


# Product Recommendation schemas
class RecommendationRequest(BaseModel):
    entity_type: str = Field(..., pattern="^(customer|order|product)$")
    entity_id: UUID
    num_recommendations: int = Field(default=5, ge=1, le=20)
    recommendation_type: Optional[str] = Field(
        default="hybrid", pattern="^(collaborative|content_based|hybrid)$"
    )


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    recommendation_type: str
    score: float = Field(ge=0, le=1)
    reason: Optional[str] = None
    factors: Dict[str, Any] = {}
    created_at: datetime


class RecommendationListResponse(BaseModel):
    entity_type: str
    entity_id: UUID
    recommendations: List[RecommendationResponse]
    generated_at: datetime


# Churn Prediction schemas
class ChurnPredictionRequest(BaseModel):
    customer_id: UUID
    include_retention_actions: bool = True


class ChurnPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    churn_probability: float = Field(ge=0, le=1)
    churn_risk_level: str
    predicted_churn_date: Optional[datetime] = None
    days_until_churn: Optional[int] = None
    churn_factors: Dict[str, Any] = {}
    top_risk_factors: List[str] = []
    retention_actions: List[str] = []
    customer_lifetime_value: Optional[float] = None
    potential_revenue_loss: Optional[float] = None
    calculated_at: datetime


# Semantic Search schemas
class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    entity_types: Optional[List[str]] = None
    limit: int = Field(default=10, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = {}


class SemanticSearchResult(BaseModel):
    entity_type: str
    entity_id: UUID
    content: str
    similarity_score: float = Field(ge=0, le=1)
    metadata: Dict[str, Any] = {}


class SemanticSearchResponse(BaseModel):
    query: str
    results: List[SemanticSearchResult]
    total_results: int
    search_time_ms: float


# Model Training schemas
class ModelTrainingRequest(BaseModel):
    model_type: str = Field(..., pattern="^(forecast|lead_score|recommendation|churn)$")
    parameters: Optional[Dict[str, Any]] = {}
    training_data_query: Optional[str] = None


class ModelTrainingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    model_type: str
    status: str
    parameters: Dict[str, Any] = {}
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = {}
    created_at: datetime


class ModelTrainingStatusResponse(BaseModel):
    job_id: UUID
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


# Analytics Dashboard schemas
class AnalyticsDashboardRequest(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    metrics: Optional[List[str]] = None


class ForecastAccuracyMetrics(BaseModel):
    mean_absolute_error: float
    mean_squared_error: float
    mean_absolute_percentage_error: float
    forecast_bias: float
    tracking_signal: float


class ModelPerformanceMetrics(BaseModel):
    model_type: str
    model_id: UUID
    accuracy: float
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    last_trained: datetime
    predictions_count: int


class AnalyticsDashboardResponse(BaseModel):
    forecast_accuracy: Optional[ForecastAccuracyMetrics] = None
    model_performance: List[ModelPerformanceMetrics] = []
    active_models_count: int
    total_predictions: int
    stockout_alerts: int
    high_churn_risk_customers: int
    top_recommended_products: List[Dict[str, Any]] = []
    period_start: datetime
    period_end: datetime
