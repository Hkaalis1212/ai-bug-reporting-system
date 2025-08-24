-- Fleet Management SaaS Database Schema
-- This single schema supports all three front doors: Audit, Routing, and Document AI

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies table (multi-tenant support)
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'trial', -- trial, audit_only, basic, premium
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trucks/Vehicles table
CREATE TABLE trucks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    truck_number VARCHAR(50) NOT NULL,
    make VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    vin VARCHAR(17),
    license_plate VARCHAR(20),
    fuel_type VARCHAR(50) DEFAULT 'diesel',
    max_weight_capacity INTEGER,
    purchase_date DATE,
    purchase_price DECIMAL(10,2),
    current_mileage INTEGER,
    status VARCHAR(50) DEFAULT 'active', -- active, maintenance, retired
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Drivers table
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    driver_number VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    license_number VARCHAR(50),
    license_expiry DATE,
    hire_date DATE,
    pay_rate_per_mile DECIMAL(8,4),
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, terminated
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Loads/Trips table
CREATE TABLE loads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    truck_id UUID REFERENCES trucks(id),
    driver_id UUID REFERENCES drivers(id),
    load_number VARCHAR(100),
    origin_city VARCHAR(100),
    origin_state VARCHAR(50),
    origin_zip VARCHAR(10),
    destination_city VARCHAR(100),
    destination_state VARCHAR(50),
    destination_zip VARCHAR(10),
    pickup_date DATE,
    delivery_date DATE,
    miles DECIMAL(8,2),
    weight_lbs INTEGER,
    revenue DECIMAL(10,2),
    fuel_gallons DECIMAL(8,2),
    fuel_cost DECIMAL(10,2),
    other_expenses DECIMAL(10,2),
    hours_driven DECIMAL(6,2),
    status VARCHAR(50) DEFAULT 'planned', -- planned, in_transit, delivered, cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Maintenance records
CREATE TABLE maintenance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    truck_id UUID REFERENCES trucks(id) ON DELETE CASCADE,
    maintenance_date DATE NOT NULL,
    maintenance_type VARCHAR(100), -- preventive, repair, inspection
    description TEXT,
    cost DECIMAL(10,2),
    mileage_at_service INTEGER,
    vendor VARCHAR(255),
    next_service_due_miles INTEGER,
    next_service_due_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document storage (for Document AI)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    load_id UUID REFERENCES loads(id),
    document_type VARCHAR(50), -- bol, pod, invoice, receipt
    file_name VARCHAR(255),
    file_path VARCHAR(500), -- Supabase storage path
    extracted_data JSONB, -- AI-extracted structured data
    status VARCHAR(50) DEFAULT 'uploaded', -- uploaded, processing, processed, error
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Audit reports (for Optimization Audit tool)
CREATE TABLE audit_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    report_type VARCHAR(50) DEFAULT 'optimization_audit',
    analysis_period_start DATE,
    analysis_period_end DATE,
    total_revenue DECIMAL(12,2),
    total_expenses DECIMAL(12,2),
    total_miles DECIMAL(12,2),
    key_findings JSONB,
    recommendations JSONB,
    potential_savings DECIMAL(10,2),
    report_file_path VARCHAR(500), -- PDF storage path
    status VARCHAR(50) DEFAULT 'generating', -- generating, completed, delivered
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Route optimization (for Routing & Dispatch Hub)
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    route_name VARCHAR(255),
    route_date DATE,
    truck_id UUID REFERENCES trucks(id),
    driver_id UUID REFERENCES drivers(id),
    stops JSONB, -- Array of stop locations and times
    total_miles DECIMAL(8,2),
    estimated_duration_hours DECIMAL(6,2),
    status VARCHAR(50) DEFAULT 'planned', -- planned, active, completed
    optimized_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User accounts (for multi-user access)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user', -- admin, manager, dispatcher, user
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_trucks_company_id ON trucks(company_id);
CREATE INDEX idx_drivers_company_id ON drivers(company_id);
CREATE INDEX idx_loads_company_id ON loads(company_id);
CREATE INDEX idx_loads_truck_id ON loads(truck_id);
CREATE INDEX idx_loads_driver_id ON loads(driver_id);
CREATE INDEX idx_loads_pickup_date ON loads(pickup_date);
CREATE INDEX idx_maintenance_truck_id ON maintenance_records(truck_id);
CREATE INDEX idx_documents_company_id ON documents(company_id);
CREATE INDEX idx_documents_load_id ON documents(load_id);
CREATE INDEX idx_routes_company_id ON routes(company_id);
CREATE INDEX idx_users_company_id ON users(company_id);

-- Row Level Security (RLS) policies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE trucks ENABLE ROW LEVEL SECURITY;
ALTER TABLE drivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE loads ENABLE ROW LEVEL SECURITY;
ALTER TABLE maintenance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE routes ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (users can only see their company's data)
CREATE POLICY "Company data isolation" ON trucks FOR ALL USING (
    company_id IN (
        SELECT company_id FROM users WHERE id = auth.uid()
    )
);

-- Similar policies would be created for all other tables
-- (Additional policies would be added for each table following the same pattern)