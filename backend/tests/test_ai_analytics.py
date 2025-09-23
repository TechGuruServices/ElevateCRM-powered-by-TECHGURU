import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.main import app
from app.core.database import get_db, Base, engine
from app.models.product import Product
from app.models.contact import Contact
from app.models.order import Order, OrderItem
from app.schemas.ai_analytics import SemanticSearchRequest

# Create a test client
client = TestClient(app)

# Setup and teardown for the test database
@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    yield db
    Base.metadata.drop_all(bind=engine)

def test_demand_forecast(db_session: Session):
    # Create a product
    product = Product(id=uuid4(), name="Test Product", price=10.0)
    db_session.add(product)
    db_session.commit()

    request_data = {"product_id": str(product.id)}
    response = client.post("/api/v1/ai/forecast", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == str(product.id)
    assert "predicted_demand" in data

def test_lead_score(db_session: Session):
    # Create a contact
    contact = Contact(id=uuid4(), first_name="Test", last_name="User", email="test@example.com")
    db_session.add(contact)
    db_session.commit()

    request_data = {"contact_id": str(contact.id)}
    response = client.post("/api/v1/ai/lead-score", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["contact_id"] == str(contact.id)
    assert "score" in data

def test_product_recommendations(db_session: Session):
    # Create an order with items
    order = Order(id=uuid4(), contact_id=uuid4(), total_amount=100.0)
    product1 = Product(id=uuid4(), name="Rec Product 1", price=50.0)
    product2 = Product(id=uuid4(), name="Rec Product 2", price=50.0)
    order_item1 = OrderItem(order_id=order.id, product_id=product1.id, quantity=1, price=50.0)
    order_item2 = OrderItem(order_id=order.id, product_id=product2.id, quantity=1, price=50.0)

    db_session.add_all([order, product1, product2, order_item1, order_item2])
    db_session.commit()

    request_data = {"entity_type": "order", "entity_id": str(order.id)}
    response = client.post("/api/v1/ai/recommendations", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == str(order.id)
    assert "recommendations" in data

def test_churn_prediction(db_session: Session):
    contact = Contact(id=uuid4(), first_name="Churn", last_name="Test", email="churn@example.com")
    db_session.add(contact)
    db_session.commit()

    request_data = {"customer_id": str(contact.id)}
    response = client.post("/api/v1/ai/churn-prediction", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == str(contact.id)
    assert "churn_probability" in data

def test_semantic_search(db_session: Session):
    # Index some data first
    # This would normally be a background task, but we can call the service directly for testing
    from app.services.ai_analytics_service import SemanticSearchService
    service = SemanticSearchService(db_session)
    product_data = [{"id": uuid4(), "content": "This is a test product for semantic search."}]
    service.index_batch("product", product_data)

    request_data = {"query": "test product"}
    response = client.post("/api/v1/ai/semantic-search", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
    assert data["results"][0]["entity_type"] == "product"
