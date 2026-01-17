-- BCMCE Platform Database Schema
-- Migration 001: Create core tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2) DEFAULT 'TX',
    zip_code VARCHAR(10),
    location_lat DECIMAL(10,6),
    location_lng DECIMAL(10,6),
    txdot_certified BOOLEAN DEFAULT FALSE,
    lat_certified BOOLEAN DEFAULT FALSE,
    delivery_radius_miles INTEGER DEFAULT 50,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('active', 'pending', 'suspended', 'inactive')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_suppliers_status ON suppliers(status);
CREATE INDEX idx_suppliers_location ON suppliers(location_lat, location_lng);

-- Materials Table
CREATE TABLE IF NOT EXISTS materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    grade VARCHAR(100),
    txdot_spec VARCHAR(50),
    unit VARCHAR(20) DEFAULT 'TON',
    description TEXT,
    typical_use TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_materials_code ON materials(code);
CREATE INDEX idx_materials_category ON materials(category);

-- Pricing History Table (Time Series)
CREATE TABLE IF NOT EXISTS pricing_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    material_id UUID REFERENCES materials(id) ON DELETE CASCADE,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    spot_price DECIMAL(10,2) NOT NULL,
    quantity_available DECIMAL(10,2),
    delivery_radius_miles INTEGER,
    timestamp TIMESTAMP DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'supplier_feed'
);

CREATE INDEX idx_pricing_material ON pricing_history(material_id, timestamp DESC);
CREATE INDEX idx_pricing_supplier ON pricing_history(supplier_id, timestamp DESC);
CREATE INDEX idx_pricing_timestamp ON pricing_history(timestamp DESC);

-- Option Contracts Table
CREATE TABLE IF NOT EXISTS option_contracts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    material_id UUID REFERENCES materials(id) ON DELETE RESTRICT,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE RESTRICT,
    buyer_id VARCHAR(255) NOT NULL,
    buyer_name VARCHAR(255) NOT NULL,
    buyer_email VARCHAR(255),
    strike_price DECIMAL(10,2) NOT NULL,
    quantity_tons DECIMAL(10,2) NOT NULL CHECK (quantity_tons > 0),
    premium_paid DECIMAL(10,2),
    duration_days INTEGER NOT NULL CHECK (duration_days IN (30, 90, 180, 365)),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'exercised', 'expired', 'cancelled')),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    exercised_at TIMESTAMP
);

CREATE INDEX idx_options_buyer ON option_contracts(buyer_id);
CREATE INDEX idx_options_status ON option_contracts(status);
CREATE INDEX idx_options_expiry ON option_contracts(expires_at);

-- County Requirements Table
CREATE TABLE IF NOT EXISTS county_requirements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    county_name VARCHAR(100) DEFAULT 'Bosque County',
    precinct INTEGER,
    material_id UUID REFERENCES materials(id) ON DELETE RESTRICT,
    quantity_tons DECIMAL(10,2) NOT NULL CHECK (quantity_tons > 0),
    delivery_location VARCHAR(255),
    delivery_lat DECIMAL(10,6),
    delivery_lng DECIMAL(10,6),
    required_by_date DATE,
    budget_allocated DECIMAL(12,2),
    txdot_spec_required VARCHAR(50),
    special_requirements TEXT,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'bidding', 'awarded', 'closed', 'cancelled')),
    posted_at TIMESTAMP DEFAULT NOW(),
    bid_deadline TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_requirements_county ON county_requirements(county_name);
CREATE INDEX idx_requirements_status ON county_requirements(status);
CREATE INDEX idx_requirements_deadline ON county_requirements(bid_deadline);

-- Bids Table
CREATE TABLE IF NOT EXISTS bids (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requirement_id UUID REFERENCES county_requirements(id) ON DELETE CASCADE,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE RESTRICT,
    material_id UUID REFERENCES materials(id) ON DELETE RESTRICT,
    quantity_tons DECIMAL(10,2) NOT NULL CHECK (quantity_tons > 0),
    price_per_ton DECIMAL(10,2) NOT NULL CHECK (price_per_ton > 0),
    total_price DECIMAL(12,2) NOT NULL,
    delivery_date DATE,
    delivery_method VARCHAR(100) DEFAULT 'Supplier Delivery',
    payment_terms VARCHAR(100) DEFAULT 'Net 30',
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'withdrawn')),
    submitted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_bids_requirement ON bids(requirement_id);
CREATE INDEX idx_bids_supplier ON bids(supplier_id);
CREATE INDEX idx_bids_status ON bids(status);

-- Material Inventory Table
CREATE TABLE IF NOT EXISTS material_inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    material_id UUID REFERENCES materials(id) ON DELETE CASCADE,
    quantity_available_tons DECIMAL(10,2) NOT NULL CHECK (quantity_available_tons >= 0),
    price_per_ton DECIMAL(10,2) NOT NULL CHECK (price_per_ton > 0),
    quality_grade VARCHAR(100),
    txdot_spec VARCHAR(50),
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(supplier_id, material_id)
);

CREATE INDEX idx_inventory_supplier ON material_inventory(supplier_id);
CREATE INDEX idx_inventory_material ON material_inventory(material_id);

-- Budget Tracking Table
CREATE TABLE IF NOT EXISTS budget_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    county_name VARCHAR(100) DEFAULT 'Bosque County',
    fiscal_year INTEGER NOT NULL,
    total_budget DECIMAL(12,2) NOT NULL,
    allocated DECIMAL(12,2) DEFAULT 0,
    spent DECIMAL(12,2) DEFAULT 0,
    committed DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(county_name, fiscal_year)
);

CREATE INDEX idx_budget_county ON budget_tracking(county_name, fiscal_year);

-- Audit Log Table
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    action VARCHAR(50) NOT NULL,
    user_id VARCHAR(255),
    user_email VARCHAR(255),
    changes JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_timestamp ON audit_log(created_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_materials_updated_at BEFORE UPDATE ON materials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_requirements_updated_at BEFORE UPDATE ON county_requirements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bids_updated_at BEFORE UPDATE ON bids
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budget_updated_at BEFORE UPDATE ON budget_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bcmce_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO bcmce_app;
