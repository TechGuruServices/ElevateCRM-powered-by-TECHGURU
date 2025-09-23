"""
Celery tasks for AI and Analytics
"""
import logging
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.ai_analytics_service import SemanticSearchService
from app.models.product import Product
from app.models.contact import Contact
from app.models.order import Order

logger = logging.getLogger(__name__)

@celery_app.task(name="ai.train_model")
def train_model_task(model_type: str, params: dict):
    """
    A Celery task to train an AI model.
    This is a placeholder for a real training pipeline.
    """
    logger.info(f"Starting training for model type: {model_type} with params: {params}")
    # In a real implementation, this would involve:
    # 1. Loading data from the database
    # 2. Preprocessing the data
    # 3. Training the model (e.g., Prophet, scikit-learn)
    # 4. Evaluating the model
    # 5. Saving the model artifact and metadata to the database
    logger.info(f"Completed training for model type: {model_type}")
    return {"status": "completed", "model_type": model_type}


@celery_app.task(name="ai.index_data")
def index_data_task(entity_type: str):
    """
    A Celery task to index data for semantic search.
    """
    logger.info(f"Starting indexing for entity type: {entity_type}")
    db = SessionLocal()
    try:
        service = SemanticSearchService(db)

        if entity_type == "product":
            items = db.query(Product).all()
            batch = [{"id": item.id, "content": f"{item.name} {item.description}"} for item in items]
        elif entity_type == "contact":
            items = db.query(Contact).all()
            batch = [{"id": item.id, "content": f"{item.first_name} {item.last_name} {item.email} {item.job_title}"} for item in items]
        elif entity_type == "order":
            items = db.query(Order).limit(5000).all() # Limiting for performance
            batch = [{"id": item.id, "content": f"Order {item.order_number} for customer {item.customer_id} with status {item.status}"} for item in items]
        else:
            logger.warning(f"Unknown entity type for indexing: {entity_type}")
            return

        if batch:
            service.index_batch(entity_type, batch)

        logger.info(f"Successfully indexed {len(batch)} items of type {entity_type}")

    finally:
        db.close()

    return {"status": "completed", "entity_type": entity_type}

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Set up periodic tasks for AI and Analytics.
    """
    # Schedule daily re-indexing of all entities
    sender.add_periodic_task(
        24 * 60 * 60.0,  # 24 hours
        index_data_task.s('product'),
        name='re-index all products daily'
    )
    sender.add_periodic_task(
        24 * 60 * 60.0,
        index_data_task.s('contact'),
        name='re-index all contacts daily'
    )
    # Schedule daily model training
    sender.add_periodic_task(
        24 * 60 * 60.0,
        train_model_task.s('forecast', {}),
        name='daily forecast model training'
    )
    sender.add_periodic_task(
        24 * 60 * 60.0,
        train_model_task.s('lead_score', {}),
        name='daily lead score model training'
    )
