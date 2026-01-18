"""
Database Connection and ORM Layer
PostgreSQL connection with SQLAlchemy
"""

import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, \
    Numeric, DateTime, Date, Boolean, Text, ForeignKey, Index, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import QueuePool
from datetime import datetime
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bcmce_user:secure_password@localhost:5432/bcmce_db"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Metadata
metadata = MetaData()


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# ORM MODELS
# ============================================================================

class Material(Base):
    """Material ORM model"""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    material_type = Column(String(50), nullable=False, index=True)
    txdot_spec = Column(String(100))
    unit = Column(String(50), default="ton")
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pricing = relationship("Pricing", back_populates="material")
    option_prices = relationship("OptionPrice", back_populates="material")


class Supplier(Base):
    """Supplier ORM model"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    contact_name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), default="TX")
    zip_code = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    rating = Column(Numeric(3, 2), default=0.0)
    total_orders = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pricing = relationship("Pricing", back_populates="supplier")
    option_prices = relationship("OptionPrice", back_populates="supplier")
    bids = relationship("Bid", back_populates="supplier")
    orders = relationship("Order", back_populates="supplier")

    __table_args__ = (
        Index('idx_supplier_location', 'city', 'state'),
    )


class Pricing(Base):
    """Pricing ORM model"""
    __tablename__ = "pricing"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    spot_price = Column(Numeric(10, 2), nullable=False)
    minimum_order = Column(Numeric(10, 2), nullable=False)
    delivery_radius_miles = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier = relationship("Supplier", back_populates="pricing")
    material = relationship("Material", back_populates="pricing")

    __table_args__ = (
        Index('idx_pricing_active', 'supplier_id', 'material_id', 'is_active'),
    )


class PricingHistory(Base):
    """Pricing history for analytics"""
    __tablename__ = "pricing_history"

    id = Column(Integer, primary_key=True, index=True)
    pricing_id = Column(Integer, ForeignKey("pricing.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_pricing_history_time', 'pricing_id', 'recorded_at'),
    )


class County(Base):
    """County ORM model"""
    __tablename__ = "counties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    state = Column(String(2), default="TX")
    contact_name = Column(String(200), nullable=False)
    contact_email = Column(String(200), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    requirements = relationship("Requirement", back_populates="county")
    option_contracts = relationship("OptionContract", back_populates="county")
    budgets = relationship("Budget", back_populates="county")
    orders = relationship("Order", back_populates="county")


class Requirement(Base):
    """County requirement ORM model"""
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    requirement_number = Column(String(50), unique=True, nullable=False, index=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    project_name = Column(String(200), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    needed_by_date = Column(Date, nullable=False, index=True)
    delivery_location = Column(String(500), nullable=False)
    budget_code = Column(String(100), nullable=False)
    specifications = Column(Text)
    status = Column(String(50), default="OPEN", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    county = relationship("County", back_populates="requirements")
    material = relationship("Material")
    bids = relationship("Bid", back_populates="requirement")


class OptionPrice(Base):
    """Option price ORM model"""
    __tablename__ = "option_prices"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    duration = Column(String(20), nullable=False)  # 30_DAYS, 90_DAYS, etc.
    strike_price = Column(Numeric(10, 2), nullable=False)
    premium = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier = relationship("Supplier", back_populates="option_prices")
    material = relationship("Material", back_populates="option_prices")
    contracts = relationship("OptionContract", back_populates="option_price")

    __table_args__ = (
        Index('idx_option_price_lookup', 'supplier_id', 'material_id', 'duration'),
    )


class OptionContract(Base):
    """Option contract ORM model"""
    __tablename__ = "option_contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    option_price_id = Column(Integer, ForeignKey("option_prices.id"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    total_value = Column(Numeric(10, 2), nullable=False)
    purchase_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), default="ACTIVE", index=True)
    exercised_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    county = relationship("County", back_populates="option_contracts")
    option_price = relationship("OptionPrice", back_populates="contracts")


class Bid(Base):
    """Bid ORM model"""
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    bid_number = Column(String(50), unique=True, nullable=False, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    quoted_price = Column(Numeric(10, 2), nullable=False)
    quantity_available = Column(Numeric(10, 2), nullable=False)
    delivery_date = Column(Date, nullable=False)
    status = Column(String(20), default="SUBMITTED", index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    requirement = relationship("Requirement", back_populates="bids")
    supplier = relationship("Supplier", back_populates="bids")


class Order(Base):
    """Order ORM model"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    delivery_location = Column(String(500), nullable=False)
    delivery_date = Column(Date, nullable=False)
    status = Column(String(20), default="PENDING", index=True)
    notes = Column(Text)
    fulfilled_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    county = relationship("County", back_populates="orders")
    supplier = relationship("Supplier", back_populates="orders")
    material = relationship("Material")


class Budget(Base):
    """Budget ORM model"""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    fiscal_year = Column(Integer, nullable=False, index=True)
    quarter = Column(Integer)  # 1-4, or NULL for annual
    category = Column(String(100), nullable=False)
    allocated_amount = Column(Numeric(10, 2), nullable=False)
    spent_amount = Column(Numeric(10, 2), default=0.0)
    committed_amount = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    county = relationship("County", back_populates="budgets")

    __table_args__ = (
        Index('idx_budget_lookup', 'county_id', 'fiscal_year', 'quarter'),
    )


class User(Base):
    """User ORM model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False, index=True)  # supplier, county, admin
    is_active = Column(Boolean, default=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    county_id = Column(Integer, ForeignKey("counties.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


class AuditLog(Base):
    """Audit log for tracking changes"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    changes = Column(Text)  # JSON string of changes
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
    )


# ============================================================================
# DATABASE UTILITIES
# ============================================================================

def init_db():
    """
    Initialize database - create all tables

    Usage:
        from backend.database import init_db
        init_db()
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_db():
    """
    Drop all tables (use with caution!)
    """
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


def get_db_session() -> Session:
    """
    Get a database session (alternative to dependency injection)

    Usage:
        from backend.database import get_db_session
        db = get_db_session()
        try:
            # Use db
            pass
        finally:
            db.close()
    """
    return SessionLocal()


# ============================================================================
# CONNECTION POOL EVENTS
# ============================================================================

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log new database connections"""
    logger.debug("New database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log connection checkouts from pool"""
    logger.debug("Connection checked out from pool")


# ============================================================================
# HEALTH CHECK
# ============================================================================

def check_db_health() -> bool:
    """
    Check database connectivity

    Returns:
        bool: True if database is accessible
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


# Alias for compatibility
check_database_health = check_db_health


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")

    if check_db_health():
        print("✓ Database connection successful")
        print(f"✓ Database URL: {DATABASE_URL}")

        # Create tables
        print("\nCreating tables...")
        init_db()
        print("✓ Tables created")
    else:
        print("✗ Database connection failed")
