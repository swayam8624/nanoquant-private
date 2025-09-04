-- Database initialization script for NanoQuant Enterprise

-- Create users table
CREATE TABLE
IF NOT EXISTS users
(
    id SERIAL PRIMARY KEY,
    email VARCHAR
(255) UNIQUE NOT NULL,
    password_hash VARCHAR
(255),
    social_id VARCHAR
(255),
    credits INTEGER DEFAULT 100,
    tier VARCHAR
(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    credit_log JSONB
);

-- Create coupons table
CREATE TABLE
IF NOT EXISTS coupons
(
    id SERIAL PRIMARY KEY,
    code VARCHAR
(255) UNIQUE NOT NULL,
    credits INTEGER NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_by INTEGER REFERENCES users
(id),
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create payments table
CREATE TABLE
IF NOT EXISTS payments
(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users
(id),
    amount INTEGER NOT NULL,
    currency VARCHAR
(10) NOT NULL,
    payment_method VARCHAR
(50) NOT NULL,
    status VARCHAR
(50) NOT NULL,
    payment_id VARCHAR
(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create compression_jobs table
CREATE TABLE
IF NOT EXISTS compression_jobs
(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users
(id),
    model_id VARCHAR
(255) NOT NULL,
    compression_level VARCHAR
(50) NOT NULL,
    status VARCHAR
(50) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    output_path VARCHAR
(255),
    credits_used INTEGER
);

-- Create indexes for better performance
CREATE INDEX
IF NOT EXISTS idx_users_email ON users
(email);
CREATE INDEX
IF NOT EXISTS idx_users_social_id ON users
(social_id);
CREATE INDEX
IF NOT EXISTS idx_coupons_code ON coupons
(code);
CREATE INDEX
IF NOT EXISTS idx_payments_user_id ON payments
(user_id);
CREATE INDEX
IF NOT EXISTS idx_compression_jobs_user_id ON compression_jobs
(user_id);

-- Insert default admin user (in production, this should be done securely)
INSERT INTO users
    (email, password_hash, credits, tier)
VALUES
    ('admin@nanoquant.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PZvO.S', 10000, 'admin')
ON CONFLICT
(email) DO NOTHING;

-- Insert sample coupons (for testing)
INSERT INTO coupons
    (code, credits, expires_at)
VALUES
    ('WELCOME100', 100, CURRENT_TIMESTAMP + INTERVAL
'30 days'),
('TEST200', 200, CURRENT_TIMESTAMP + INTERVAL '30 days')
ON CONFLICT
(code) DO NOTHING;