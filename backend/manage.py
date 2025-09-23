import typer
from app.core.database import SessionLocal
from app.models.product import Product
from app.models.contact import Contact
from app.models.order import Order, OrderItem
from uuid import uuid4
import random
from datetime import datetime, timedelta

app = typer.Typer()

@app.command()
def seed_demo(if_empty: bool = True):
    """
    Seed the database with demo data.
    """
    db = SessionLocal()
    try:
        if if_empty and db.query(Product).first():
            print("Database is not empty. Skipping seed.")
            return

        print("Seeding demo data...")

        # Create products
        products = []
        for i in range(20):
            product = Product(id=uuid4(), name=f"Product {i+1}", price=random.uniform(10.0, 100.0), description=f"Description for product {i+1}")
            products.append(product)
        db.add_all(products)
        db.commit()

        # Create contacts
        contacts = []
        for i in range(10):
            contact = Contact(id=uuid4(), first_name=f"User", last_name=f"{i+1}", email=f"user{i+1}@example.com")
            contacts.append(contact)
        db.add_all(contacts)
        db.commit()

        # Create orders
        for contact in contacts:
            for _ in range(random.randint(1, 5)):
                order_id = uuid4()
                order_products = random.sample(products, k=random.randint(1, 5))
                total_amount = sum(p.price for p in order_products)
                order = Order(id=order_id, contact_id=contact.id, total_amount=total_amount, created_at=datetime.utcnow() - timedelta(days=random.randint(0, 90)))
                db.add(order)
                for product in order_products:
                    order_item = OrderItem(order_id=order_id, product_id=product.id, quantity=1, price=product.price)
                    db.add(order_item)
        db.commit()

        print("Demo data seeded successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    app()
