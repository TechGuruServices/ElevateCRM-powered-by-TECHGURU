"""
AI & Analytics Models for ElevateCRM
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
    UniqueConstraint,
    ARRAY,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, VECTOR
import uuid

from app.core.database import Base


class AIModel(Base):
    """AI/ML Model Registry"""

    __tablename__ = "ai_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    model_type = Column(String(100), nullable=False)  # forecasting, scoring, recommendation, etc.
    version = Column(String(50), nullable=False)
    algorithm = Column(String(100))  # prophet, arima, neural_network, etc.
    parameters = Column(JSONB, default={})
    metrics = Column(JSONB, default={})  # accuracy, mse, mae, etc.
    training_data_info = Column(JSONB, default={})
    model_path = Column(String(500))  # Path to serialized model
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trained_at = Column(DateTime)
    trained_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    predictions = relationship("AIPrediction", back_populates="model")
    forecasts = relationship("DemandForecast", back_populates="model")

    __table_args__ = (
        Index("idx_ai_models_type_active", "model_type", "is_active"),
        UniqueConstraint("name", "version", name="uq_ai_model_name_version"),
    )


class AIPrediction(Base):
    """Generic AI Predictions"""

    __tablename__ = "ai_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False)
    entity_type = Column(String(100), nullable=False)  # product, customer, order, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    prediction_type = Column(String(100), nullable=False)
    prediction_value = Column(Float)
    prediction_data = Column(JSONB, default={})
    confidence_score = Column(Float)
    features_used = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    # Relationships
    model = relationship("AIModel", back_populates="predictions")

    __table_args__ = (
        Index("idx_ai_predictions_entity", "entity_type", "entity_id"),
        Index("idx_ai_predictions_type_created", "prediction_type", "created_at"),
    )


class DemandForecast(Base):
    """Demand Forecasting Results"""

    __tablename__ = "demand_forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ai_models.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"))
    forecast_date = Column(DateTime, nullable=False)
    forecast_horizon_days = Column(Integer, default=30)
    predicted_demand = Column(Float, nullable=False)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    confidence_level = Column(Float, default=0.95)
    seasonality_component = Column(JSONB, default={})
    trend_component = Column(JSONB, default={})
    stockout_probability = Column(Float)
    recommended_reorder_point = Column(Integer)
    recommended_order_quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    model = relationship("AIModel", back_populates="forecasts")
    product = relationship("Product")
    warehouse = relationship("Warehouse")

    __table_args__ = (
        Index("idx_demand_forecast_product_date", "product_id", "forecast_date"),
        Index("idx_demand_forecast_warehouse", "warehouse_id"),
    )


class LeadScore(Base):
    """Lead Scoring for Contacts/Opportunities"""

    __tablename__ = "lead_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)
    score = Column(Float, nullable=False)  # 0-100
    score_grade = Column(String(10))  # A, B, C, D, F
    scoring_factors = Column(JSONB, default={})
    top_positive_factors = Column(JSONB, default=[])  # Top 3 reasons for high score
    top_negative_factors = Column(JSONB, default=[])  # Top 3 reasons for low score
    engagement_score = Column(Float)
    demographic_score = Column(Float)
    behavioral_score = Column(Float)
    firmographic_score = Column(Float)
    conversion_probability = Column(Float)
    recommended_actions = Column(JSONB, default=[])
    last_calculated = Column(DateTime, default=datetime.utcnow)
    next_calculation = Column(DateTime)
    is_current = Column(Boolean, default=True)

    # Relationships
    contact = relationship("Contact")

    __table_args__ = (
        Index("idx_lead_scores_contact_current", "contact_id", "is_current"),
        Index("idx_lead_scores_grade", "score_grade"),
    )


class ProductRecommendation(Base):
    """Product Recommendations"""

    __tablename__ = "product_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_for = Column(String(50), nullable=False)  # customer, order, product
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    recommendation_type = Column(String(50))  # collaborative, content_based, hybrid
    score = Column(Float, nullable=False)
    reason = Column(Text)
    factors = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    clicked = Column(Boolean, default=False)
    converted = Column(Boolean, default=False)

    # Relationships
    product = relationship("Product")

    __table_args__ = (
        Index("idx_recommendations_entity", "recommendation_for", "entity_id"),
        Index("idx_recommendations_score", "score"),
    )


class ChurnPrediction(Base):
    """Customer Churn Predictions"""

    __tablename__ = "churn_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)
    churn_probability = Column(Float, nullable=False)  # 0-1
    churn_risk_level = Column(String(20))  # low, medium, high, critical
    predicted_churn_date = Column(DateTime)
    days_until_churn = Column(Integer)
    churn_factors = Column(JSONB, default={})
    top_risk_factors = Column(JSONB, default=[])
    retention_actions = Column(JSONB, default=[])
    customer_lifetime_value = Column(Float)
    potential_revenue_loss = Column(Float)
    last_order_days_ago = Column(Integer)
    order_frequency_change = Column(Float)
    average_order_value_change = Column(Float)
    support_ticket_trend = Column(String(20))
    calculated_at = Column(DateTime, default=datetime.utcnow)
    is_current = Column(Boolean, default=True)

    # Relationships
    customer = relationship("Contact")

    __table_args__ = (
        Index("idx_churn_customer_current", "customer_id", "is_current"),
        Index("idx_churn_risk_level", "churn_risk_level"),
        Index("idx_churn_probability", "churn_probability"),
    )


class SemanticIndex(Base):
    """Semantic Search Index using Vector Embeddings"""

    __tablename__ = "semantic_index"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(100), nullable=False)  # product, contact, order, document
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    content = Column(Text, nullable=False)  # Original text content
    embedding = Column(VECTOR(384))  # Vector embedding (384 dims for all-MiniLM-L6-v2)
    metadata = Column(JSONB, default={})
    language = Column(String(10), default="en")
    indexed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_semantic_entity", "entity_type", "entity_id"),
        Index("idx_semantic_embedding", "embedding", postgresql_using="ivfflat"),
    )


class ForecastAccuracy(Base):
    """Track forecast accuracy for model improvement"""

    __tablename__ = "forecast_accuracy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("demand_forecasts.id"))
    actual_demand = Column(Float)
    absolute_error = Column(Float)
    percentage_error = Column(Float)
    squared_error = Column(Float)
    measured_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    forecast = relationship("DemandForecast")

    __table_args__ = (Index("idx_forecast_accuracy_measured", "measured_at"),)


class ModelTrainingJob(Base):
    """Track model training jobs"""

    __tablename__ = "model_training_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_type = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    parameters = Column(JSONB, default={})
    training_data_query = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    metrics = Column(JSONB, default={})
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_training_jobs_status", "status"),
        Index("idx_training_jobs_type", "model_type"),
    )
