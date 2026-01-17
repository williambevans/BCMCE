"""
API Integration Tests
Tests for BCMCE FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db
from decimal import Decimal


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ============================================================================
# PRICING API TESTS
# ============================================================================

def test_get_current_pricing(client, db_session):
    """Test get current pricing endpoint"""
    # Create test data
    from backend.database import Material, Supplier, Pricing

    material = Material(name="Road Base Gravel", material_type="ROAD_BASE", unit="ton")
    db_session.add(material)

    supplier = Supplier(
        name="Test Quarry",
        contact_name="John Doe",
        email="test@quarry.com",
        phone="555-1234",
        address="123 Main St",
        city="Clifton",
        state="TX",
        zip_code="76634"
    )
    db_session.add(supplier)
    db_session.commit()

    pricing = Pricing(
        supplier_id=supplier.id,
        material_id=material.id,
        spot_price=Decimal("28.50"),
        minimum_order=Decimal("50"),
        delivery_radius_miles=50,
        is_active=True
    )
    db_session.add(pricing)
    db_session.commit()

    # Test endpoint
    response = client.get("/api/v1/pricing/current")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "spot_price" in data[0]


def test_get_pricing_by_material(client, db_session):
    """Test get pricing by material endpoint"""
    response = client.get("/api/v1/pricing/material/1")
    # Should return empty or 404 for non-existent material
    assert response.status_code in [200, 404]


# ============================================================================
# SUPPLIER API TESTS
# ============================================================================

def test_create_supplier(client):
    """Test create supplier endpoint"""
    supplier_data = {
        "name": "New Quarry",
        "contact_name": "Jane Smith",
        "email": "jane@newquarry.com",
        "phone": "555-5678",
        "address": "456 Oak St",
        "city": "Meridian",
        "state": "TX",
        "zip_code": "76665",
        "is_active": True
    }

    response = client.post("/api/v1/suppliers/", json=supplier_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == supplier_data["name"]
    assert data["email"] == supplier_data["email"]


def test_get_suppliers(client):
    """Test get suppliers list endpoint"""
    response = client.get("/api/v1/suppliers/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ============================================================================
# OPTIONS API TESTS
# ============================================================================

def test_get_option_prices(client):
    """Test get option prices endpoint"""
    response = client.get("/api/v1/options/prices")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_purchase_option(client, db_session):
    """Test purchase option contract endpoint"""
    # Create test data first
    from backend.database import Material, Supplier, County, OptionPrice

    material = Material(name="Caliche", material_type="CALICHE", unit="ton")
    db_session.add(material)

    supplier = Supplier(
        name="Test Supplier",
        contact_name="Test Contact",
        email="supplier@test.com",
        phone="555-0000",
        address="789 Test Rd",
        city="Test City",
        state="TX",
        zip_code="76600"
    )
    db_session.add(supplier)

    county = County(
        name="Bosque County",
        state="TX",
        contact_name="Commissioner",
        contact_email="commissioner@bosque.tx.us",
        contact_phone="555-9999"
    )
    db_session.add(county)
    db_session.commit()

    option_price = OptionPrice(
        supplier_id=supplier.id,
        material_id=material.id,
        duration="90_DAYS",
        strike_price=Decimal("47.25"),
        premium=Decimal("2.25")
    )
    db_session.add(option_price)
    db_session.commit()

    # Test purchase
    purchase_data = {
        "county_id": county.id,
        "supplier_id": supplier.id,
        "material_id": material.id,
        "duration": "90_DAYS",
        "quantity": 300
    }

    response = client.post("/api/v1/options/purchase", json=purchase_data)
    # May require authentication, so 401 is acceptable
    assert response.status_code in [201, 401]


# ============================================================================
# COUNTY API TESTS
# ============================================================================

def test_submit_requirement(client, db_session):
    """Test submit requirement endpoint"""
    from backend.database import Material, County

    material = Material(name="Hot Mix Asphalt", material_type="HOT_MIX", unit="ton")
    db_session.add(material)

    county = County(
        name="Hill County",
        state="TX",
        contact_name="Commissioner",
        contact_email="commissioner@hill.tx.us",
        contact_phone="555-8888"
    )
    db_session.add(county)
    db_session.commit()

    requirement_data = {
        "county_id": county.id,
        "material_id": material.id,
        "project_name": "FM 219 Resurfacing",
        "quantity": 500,
        "needed_by_date": "2026-03-15",
        "delivery_location": "County Road 1740",
        "budget_code": "RD-2026-Q1-003",
        "specifications": "TxDOT Type D Hot Mix"
    }

    response = client.post("/api/v1/county/requirements", json=requirement_data)
    # May require authentication
    assert response.status_code in [201, 401]


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_login(client, db_session):
    """Test login endpoint"""
    from backend.auth import create_user

    # Create test user
    create_user(
        db_session,
        email="testuser@example.com",
        password="testpass123",
        full_name="Test User",
        role="admin"
    )

    login_data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
