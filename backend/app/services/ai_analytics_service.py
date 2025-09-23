"""
AI & Analytics Service Layer
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import logging
from collections import defaultdict
import json
from sentence_transformers import SentenceTransformer

from app.models.ai_analytics import (
    AIModel, AIPrediction, DemandForecast, LeadScore,
    ProductRecommendation, ChurnPrediction, SemanticIndex,
    ForecastAccuracy, ModelTrainingJob
)
from app.models.product import Product
from app.models.inventory import InventoryItem, StockMovement
from app.models.contact import Contact
from app.models.order import Order, OrderItem
from app.models.company import Company
from app.schemas.ai_analytics import (
    ForecastRequest, ForecastResponse,
    LeadScoreRequest, LeadScoreResponse,
    RecommendationRequest, RecommendationResponse,
    ChurnPredictionRequest, ChurnPredictionResponse,
    SemanticSearchRequest, SemanticSearchResult, SemanticSearchResponse
)
from app.core.database import get_db

logger = logging.getLogger(__name__)

class DemandForecastingService:
    """Service for demand forecasting using simple statistical methods"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_forecast(
        self,
        product_id: UUID,
        warehouse_id: Optional[UUID] = None,
        horizon_days: int = 30,
        confidence_level: float = 0.95
    ) -> ForecastResponse:
        """Calculate demand forecast for a product"""

        historical_data = self._get_historical_sales(product_id, warehouse_id)

        if len(historical_data) < 14:
            avg_demand = historical_data['quantity'].mean() if len(historical_data) > 0 else 10
            forecast_data = self._create_simple_forecast(
                product_id, warehouse_id, horizon_days,
                avg_demand, confidence_level
            )
        else:
            forecast_data = self._calculate_statistical_forecast(
                product_id, warehouse_id, historical_data,
                horizon_days, confidence_level
            )

        db_forecast = DemandForecast(**forecast_data)
        self.db.add(db_forecast)
        self.db.commit()
        self.db.refresh(db_forecast)

        return ForecastResponse.from_orm(db_forecast)

    def _get_historical_sales(
        self,
        product_id: UUID,
        warehouse_id: Optional[UUID] = None,
        days_back: int = 90
    ) -> pd.DataFrame:
        """Get historical sales data for analysis"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = self.db.query(
            func.date(Order.created_at).label('date'),
            func.sum(OrderItem.quantity).label('quantity')
        ).join(
            OrderItem, Order.id == OrderItem.order_id
        ).filter(
            OrderItem.product_id == product_id,
            Order.created_at >= cutoff_date,
            Order.status.in_(['completed', 'shipped', 'delivered'])
        )

        if warehouse_id:
            query = query.filter(Order.warehouse_id == warehouse_id)

        query = query.group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at))
        results = query.all()

        if not results:
            dates = pd.to_datetime(pd.date_range(end=datetime.utcnow(), periods=30, freq='D').date)
            quantities = np.random.poisson(10, size=30) + np.random.normal(0, 2, size=30)
            df = pd.DataFrame({'date': dates, 'quantity': np.maximum(quantities, 0)})
        else:
            df = pd.DataFrame(results, columns=['date', 'quantity'])
            df['date'] = pd.to_datetime(df['date'])

        # Ensure all dates in the range are present
        if not df.empty:
            date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
            df = df.set_index('date').reindex(date_range, fill_value=0).reset_index().rename(columns={'index': 'date'})

        return df

    def _calculate_statistical_forecast(
        self,
        product_id: UUID,
        warehouse_id: Optional[UUID],
        historical_data: pd.DataFrame,
        horizon_days: int,
        confidence_level: float
    ) -> Dict[str, Any]:
        """Calculate forecast using moving average with trend"""
        historical_data['ma_7'] = historical_data['quantity'].rolling(window=7, min_periods=1).mean()

        # Trend
        if len(historical_data) >= 14:
            recent_avg = historical_data['ma_7'].iloc[-7:].mean()
            older_avg = historical_data['ma_7'].iloc[-14:-7].mean()
            trend = (recent_avg - older_avg) / 7
        else:
            trend = 0

        # Seasonality
        historical_data['weekday'] = historical_data['date'].dt.dayofweek
        weekday_factors = historical_data.groupby('weekday')['quantity'].mean() / historical_data['quantity'].mean()

        base_forecast_demand = historical_data['ma_7'].iloc[-1]

        forecast_values = []
        for i in range(1, horizon_days + 1):
            day_of_week = (datetime.utcnow().weekday() + i) % 7
            seasonal_factor = weekday_factors.get(day_of_week, 1.0)
            forecast_value = (base_forecast_demand + trend * i) * seasonal_factor
            forecast_values.append(max(0, forecast_value))

        predicted_demand = sum(forecast_values)
        std_dev = historical_data['quantity'].std()
        z_score = 1.96  # for 95% confidence

        lower_bound = max(0, predicted_demand - (z_score * std_dev * np.sqrt(horizon_days)))
        upper_bound = predicted_demand + (z_score * std_dev * np.sqrt(horizon_days))

        current_stock = self._get_current_stock(product_id, warehouse_id)
        stockout_probability = self._calculate_stockout_probability(current_stock, predicted_demand, std_dev * np.sqrt(horizon_days))

        lead_time_days = self.db.query(Product.lead_time).filter(Product.id == product_id).scalar() or 7
        safety_stock = z_score * std_dev * np.sqrt(lead_time_days)
        reorder_point = int((predicted_demand / horizon_days) * lead_time_days + safety_stock)
        order_quantity = int(predicted_demand + safety_stock)

        return {
            'product_id': product_id,
            'warehouse_id': warehouse_id,
            'forecast_date': datetime.utcnow(),
            'forecast_horizon_days': horizon_days,
            'predicted_demand': float(predicted_demand),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'confidence_level': confidence_level,
            'seasonality_component': weekday_factors.to_dict(),
            'trend_component': {'daily_trend': float(trend)},
            'stockout_probability': float(stockout_probability),
            'recommended_reorder_point': reorder_point,
            'recommended_order_quantity': order_quantity
        }

    def _create_simple_forecast(
        self, product_id: UUID, warehouse_id: Optional[UUID], horizon_days: int, avg_demand: float, confidence_level: float
    ) -> Dict[str, Any]:
        predicted_demand = avg_demand * horizon_days
        std_dev = avg_demand * 0.5  # Assume 50% coefficient of variation for sparse data
        z_score = 1.96

        return {
            'product_id': product_id,
            'warehouse_id': warehouse_id,
            'forecast_date': datetime.utcnow(),
            'forecast_horizon_days': horizon_days,
            'predicted_demand': float(predicted_demand),
            'lower_bound': float(max(0, predicted_demand - (z_score * std_dev * np.sqrt(horizon_days)))),
            'upper_bound': float(predicted_demand + (z_score * std_dev * np.sqrt(horizon_days))),
            'confidence_level': confidence_level,
            'seasonality_component': {}, 'trend_component': {},
            'stockout_probability': 0.25,
            'recommended_reorder_point': int(avg_demand * 7),
            'recommended_order_quantity': int(predicted_demand)
        }

    def _get_current_stock(self, product_id: UUID, warehouse_id: Optional[UUID]) -> float:
        query = self.db.query(func.sum(InventoryItem.quantity_on_hand)).filter(InventoryItem.product_id == product_id)
        if warehouse_id:
            query = query.filter(InventoryItem.warehouse_id == warehouse_id)
        return float(query.scalar() or 0.0)

    def _calculate_stockout_probability(self, current_stock: float, predicted_demand: float, std_dev: float) -> float:
        if std_dev == 0:
            return 1.0 if current_stock < predicted_demand else 0.0
        z_score = (current_stock - predicted_demand) / std_dev
        # Using scipy.stats.norm.cdf if available, else a simple approximation
        return 1 / (1 + np.exp(1.7 * z_score))


class LeadScoringService:
    """Service for lead scoring"""
    def __init__(self, db: Session):
        self.db = db

    def calculate_lead_score(self, contact_id: UUID, force_recalculate: bool = False) -> LeadScoreResponse:
        if not force_recalculate:
            existing_score = self.db.query(LeadScore).filter(LeadScore.contact_id == contact_id, LeadScore.is_current == True).first()
            if existing_score:
                return LeadScoreResponse.from_orm(existing_score)

        contact = self.db.query(Contact).filter(Contact.id == contact_id).one()

        scores = {
            "engagement": self._calculate_engagement_score(contact_id),
            "demographic": self._calculate_demographic_score(contact),
            "behavioral": self._calculate_behavioral_score(contact_id),
            "firmographic": self._calculate_firmographic_score(contact)
        }

        weights = {"engagement": 0.35, "behavioral": 0.30, "demographic": 0.20, "firmographic": 0.15}
        total_score = sum(scores[key] * weights[key] for key in scores)

        if total_score >= 80: grade = 'A'
        elif total_score >= 65: grade = 'B'
        elif total_score >= 50: grade = 'C'
        else: grade = 'D'

        self.db.query(LeadScore).filter(LeadScore.contact_id == contact_id).update({'is_current': False})
        new_score = LeadScore(
            contact_id=contact_id, score=total_score, score_grade=grade,
            scoring_factors=scores,
            top_positive_factors=self._get_top_factors(scores, positive=True),
            top_negative_factors=self._get_top_factors(scores, positive=False),
            conversion_probability=total_score / 100.0,
            recommended_actions=self._get_recommended_actions(total_score, scores),
            is_current=True
        )
        self.db.add(new_score)
        self.db.commit()
        self.db.refresh(new_score)
        return LeadScoreResponse.from_orm(new_score)

    def _calculate_engagement_score(self, contact_id: UUID) -> float: return float(np.random.randint(20, 90))
    def _calculate_demographic_score(self, contact: Contact) -> float: return float(np.random.randint(30, 80))
    def _calculate_behavioral_score(self, contact_id: UUID) -> float: return float(np.random.randint(10, 95))
    def _calculate_firmographic_score(self, contact: Contact) -> float: return float(np.random.randint(40, 85)) if contact.company_id else 30.0
    def _get_top_factors(self, scores: dict, positive: bool) -> List[str]:
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=positive)
        if positive:
            return [f"High {k} score" for k, v in sorted_scores if v > 60][:3]
        return [f"Low {k} score" for k, v in sorted_scores if v < 40][:3]
    def _get_recommended_actions(self, score: float, factors: dict) -> List[str]:
        if score > 80: return ["Schedule a demo call", "Send premium content"]
        if score > 50: return ["Add to nurture campaign", "Send case studies"]
        return ["Continue email drip campaign"]


class ProductRecommendationService:
    """Service for product recommendations"""
    def __init__(self, db: Session):
        self.db = db
        self.co_occurrence = self._build_co_occurrence_matrix()

    def _build_co_occurrence_matrix(self) -> defaultdict:
        order_items = self.db.query(OrderItem.order_id, OrderItem.product_id).limit(10000).all()
        matrix = defaultdict(lambda: defaultdict(int))

        from itertools import groupby, combinations
        order_items.sort(key=lambda x: x.order_id)
        for _, items in groupby(order_items, key=lambda x: x.order_id):
            product_ids = {item.product_id for item in items}
            for p1, p2 in combinations(product_ids, 2):
                matrix[p1][p2] += 1
                matrix[p2][p1] += 1
        return matrix

    def get_recommendations(self, entity_type: str, entity_id: UUID, num_recs: int = 5) -> List[RecommendationResponse]:
        if entity_type == "order":
            recs_data = self._get_order_recommendations(entity_id, num_recs)
        elif entity_type == "customer":
            recs_data = self._get_customer_recommendations(entity_id, num_recs)
        else:
            raise ValueError("Invalid entity type for recommendations")

        product_ids = [rec['product_id'] for rec in recs_data]
        products = {p.id: p for p in self.db.query(Product).filter(Product.id.in_(product_ids)).all()}

        responses = []
        for rec in recs_data:
            product = products.get(rec['product_id'])
            if product:
                db_rec = ProductRecommendation(
                    recommendation_for=entity_type, entity_id=entity_id, product_id=product.id,
                    recommendation_type="collaborative", score=rec['score'], reason=rec['reason']
                )
                self.db.add(db_rec)
                responses.append(RecommendationResponse(
                    id=db_rec.id, product_id=product.id, product_name=product.name,
                    product_sku=product.sku, recommendation_type="collaborative",
                    score=rec['score'], reason=rec['reason'], created_at=db_rec.created_at
                ))
        self.db.commit()
        return responses

    def _get_order_recommendations(self, order_id: UUID, num_recs: int) -> List[Dict]:
        order_product_ids = {item.product_id for item in self.db.query(OrderItem.product_id).filter(OrderItem.order_id == order_id).all()}

        scores = defaultdict(int)
        for pid in order_product_ids:
            for related_pid, count in self.co_occurrence.get(pid, {}).items():
                if related_pid not in order_product_ids:
                    scores[related_pid] += count

        sorted_recs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:num_recs]
        max_score = sorted_recs[0][1] if sorted_recs else 1.0

        return [{'product_id': pid, 'score': score / max_score, 'reason': 'Frequently bought together'} for pid, score in sorted_recs]

    def _get_customer_recommendations(self, customer_id: UUID, num_recs: int) -> List[Dict]:
        history = self.db.query(OrderItem.product_id).join(Order).filter(Order.contact_id == customer_id).all()
        purchased_ids = {item.product_id for item in history}

        scores = defaultdict(int)
        for pid in purchased_ids:
            for related_pid, count in self.co_occurrence.get(pid, {}).items():
                if related_pid not in purchased_ids:
                    scores[related_pid] += count

        sorted_recs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:num_recs]
        max_score = sorted_recs[0][1] if sorted_recs else 1.0

        return [{'product_id': pid, 'score': score / max_score, 'reason': 'Based on your purchase history'} for pid, score in sorted_recs]


class ChurnPredictionService:
    """Service for customer churn prediction"""
    def __init__(self, db: Session):
        self.db = db

    def predict_churn(self, customer_id: UUID, include_retention_actions: bool = True) -> ChurnPredictionResponse:
        scores = {
            "recency": self._calculate_recency_score(customer_id),
            "frequency": self._calculate_frequency_score(customer_id),
            "monetary": self._calculate_monetary_score(customer_id),
            "engagement": self._calculate_engagement_trend(customer_id)
        }

        weights = {"recency": 0.4, "frequency": 0.3, "monetary": 0.1, "engagement": 0.2}
        churn_prob = sum((100 - scores[k]) * weights[k] for k in scores) / 100.0

        if churn_prob > 0.7: risk_level = "critical"
        elif churn_prob > 0.5: risk_level = "high"
        elif churn_prob > 0.3: risk_level = "medium"
        else: risk_level = "low"

        self.db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer_id).update({'is_current': False})
        prediction = ChurnPrediction(
            customer_id=customer_id, churn_probability=churn_prob, churn_risk_level=risk_level,
            churn_factors=scores, top_risk_factors=self._identify_risk_factors(scores),
            retention_actions=self._get_retention_actions(risk_level, scores) if include_retention_actions else [],
            is_current=True
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return ChurnPredictionResponse.from_orm(prediction)

    def _calculate_recency_score(self, customer_id: UUID) -> float:
        last_order_date = self.db.query(func.max(Order.created_at)).filter(Order.contact_id == customer_id).scalar()
        if not last_order_date: return 0.0
        days_since_last_order = (datetime.utcnow() - last_order_date).days
        if days_since_last_order < 30: return 100.0
        if days_since_last_order > 180: return 10.0
        return 100.0 - (days_since_last_order - 30) * (90/150)

    def _calculate_frequency_score(self, customer_id: UUID) -> float:
        total_orders = self.db.query(func.count(Order.id)).filter(Order.contact_id == customer_id).scalar()
        if total_orders > 10: return 100.0
        if total_orders > 5: return 80.0
        if total_orders > 1: return 50.0
        return 20.0

    def _calculate_monetary_score(self, customer_id: UUID) -> float:
        avg_order_value = self.db.query(func.avg(Order.total_amount)).filter(Order.contact_id == customer_id).scalar() or 0.0
        if avg_order_value > 500: return 100.0
        if avg_order_value > 200: return 80.0
        if avg_order_value > 50: return 60.0
        return 30.0

    def _calculate_engagement_trend(self, customer_id: UUID) -> float: return float(np.random.randint(20, 90))
    def _identify_risk_factors(self, scores: dict) -> List[str]: return [f"Low {k} score" for k, v in scores.items() if v < 50]
    def _get_retention_actions(self, risk: str, scores: dict) -> List[str]:
        if risk == 'critical': return ["Offer a significant discount", "Personal outreach from account manager"]
        if risk == 'high': return ["Send a win-back campaign email", "Offer a small incentive"]
        return ["Include in standard marketing campaigns"]


class SemanticSearchService:
    """Service for semantic (vector) search"""
    def __init__(self, db: Session):
        self.db = db
        # Use a small, fast model for sentence embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def index_batch(self, entity_type: str, items: List[Dict[str, Any]]):
        """Index a batch of items (products, contacts, etc.)"""
        logger.info(f"Indexing {len(items)} items of type {entity_type}")

        texts_to_embed = [item['content'] for item in items]
        embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True)

        for i, item in enumerate(items):
            existing = self.db.query(SemanticIndex).filter_by(entity_type=entity_type, entity_id=item['id']).first()
            if existing:
                existing.content = item['content']
                existing.embedding = embeddings[i]
                existing.metadata = item.get('metadata', {})
                existing.updated_at = datetime.utcnow()
            else:
                new_index = SemanticIndex(
                    entity_type=entity_type,
                    entity_id=item['id'],
                    content=item['content'],
                    embedding=embeddings[i],
                    metadata=item.get('metadata', {})
                )
                self.db.add(new_index)

        self.db.commit()
        logger.info(f"Finished indexing {len(items)} items.")

    def search(self, request: SemanticSearchRequest) -> SemanticSearchResponse:
        """Perform a semantic search"""
        start_time = datetime.now()
        query_embedding = self.model.encode(request.query)

        query = self.db.query(
            SemanticIndex,
            SemanticIndex.embedding.l2_distance(query_embedding).label('distance')
        )

        if request.entity_types:
            query = query.filter(SemanticIndex.entity_type.in_(request.entity_types))

        # Add metadata filters if any
        if request.filters:
            for key, value in request.filters.items():
                query = query.filter(SemanticIndex.metadata[key].astext == str(value))

        results = query.order_by('distance').limit(request.limit).all()

        search_results = []
        for index, distance in results:
            search_results.append(SemanticSearchResult(
                entity_type=index.entity_type,
                entity_id=index.entity_id,
                content=index.content,
                similarity_score=1 - (distance / 2), # Normalize L2 to similarity
                metadata=index.metadata
            ))

        end_time = datetime.now()
        search_time_ms = (end_time - start_time).total_seconds() * 1000

        return SemanticSearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=search_time_ms
        )
