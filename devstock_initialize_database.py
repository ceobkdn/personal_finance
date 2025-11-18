"""
Database Initialization Script
================================
Khởi tạo database schema cho Portfolio Management System
Run this BEFORE generating sample data
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = 'data/portfolio.db'

# Complete schema SQL
SCHEMA_SQL = """
-- ============================================
-- PORTFOLIO MANAGEMENT SYSTEM - DATABASE SCHEMA
-- ============================================

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    role VARCHAR(20) DEFAULT 'user',
    
    CHECK (email LIKE '%_@__%.__%'),
    CHECK (LENGTH(username) >= 3)
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    currency VARCHAR(10) DEFAULT 'VND',
    initial_value DECIMAL(20, 2) DEFAULT 0,
    current_value DECIMAL(20, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CHECK (initial_value >= 0),
    CHECK (current_value >= 0)
);

CREATE INDEX IF NOT EXISTS idx_portfolios_user ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolios_active ON portfolios(is_active);

-- Assets table
CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    asset_name VARCHAR(200),
    quantity DECIMAL(20, 8) NOT NULL,
    purchase_price DECIMAL(20, 8) NOT NULL,
    purchase_date DATE NOT NULL,
    current_price DECIMAL(20, 8),
    current_value DECIMAL(20, 2),
    cost_basis DECIMAL(20, 2),
    unrealized_gain_loss DECIMAL(20, 2),
    currency VARCHAR(10) DEFAULT 'VND',
    exchange VARCHAR(50),
    sector VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    CHECK (quantity >= 0),
    CHECK (purchase_price > 0),
    CHECK (asset_type IN ('stock', 'bond', 'crypto', 'forex', 'commodity', 'etf', 'mutual_fund', 'real_estate'))
);

CREATE INDEX IF NOT EXISTS idx_assets_portfolio ON assets(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_assets_symbol ON assets(symbol);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_composite ON assets(portfolio_id, symbol, asset_type);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    asset_id INTEGER,
    transaction_type VARCHAR(20) NOT NULL,
    symbol VARCHAR(20),
    quantity DECIMAL(20, 8),
    price DECIMAL(20, 8),
    total_amount DECIMAL(20, 2) NOT NULL,
    fee DECIMAL(20, 2) DEFAULT 0,
    tax DECIMAL(20, 2) DEFAULT 0,
    net_amount DECIMAL(20, 2),
    currency VARCHAR(10) DEFAULT 'VND',
    exchange VARCHAR(50),
    transaction_date DATE NOT NULL,
    settlement_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE SET NULL,
    CHECK (transaction_type IN ('buy', 'sell', 'deposit', 'withdrawal', 'dividend', 'interest', 'fee', 'split', 'transfer')),
    CHECK (quantity >= 0 OR quantity IS NULL),
    CHECK (fee >= 0),
    CHECK (tax >= 0)
);

CREATE INDEX IF NOT EXISTS idx_transactions_portfolio ON transactions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transactions_asset ON transactions(asset_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON transactions(symbol);
CREATE INDEX IF NOT EXISTS idx_transactions_composite ON transactions(portfolio_id, transaction_date DESC);

-- Market data cache
CREATE TABLE IF NOT EXISTS market_data_cache (
    symbol VARCHAR(20) PRIMARY KEY,
    asset_type VARCHAR(20) NOT NULL,
    current_price DECIMAL(20, 8) NOT NULL,
    open_price DECIMAL(20, 8),
    high_price DECIMAL(20, 8),
    low_price DECIMAL(20, 8),
    close_price DECIMAL(20, 8),
    volume BIGINT,
    market_cap DECIMAL(30, 2),
    change_percent DECIMAL(10, 4),
    change_value DECIMAL(20, 8),
    bid_price DECIMAL(20, 8),
    ask_price DECIMAL(20, 8),
    currency VARCHAR(10) DEFAULT 'VND',
    exchange VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (current_price > 0)
);

CREATE INDEX IF NOT EXISTS idx_market_cache_type ON market_data_cache(asset_type);
CREATE INDEX IF NOT EXISTS idx_market_cache_updated ON market_data_cache(last_updated);

-- Market data history
CREATE TABLE IF NOT EXISTS market_data_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open_price DECIMAL(20, 8) NOT NULL,
    high_price DECIMAL(20, 8) NOT NULL,
    low_price DECIMAL(20, 8) NOT NULL,
    close_price DECIMAL(20, 8) NOT NULL,
    volume BIGINT DEFAULT 0,
    timeframe VARCHAR(10) DEFAULT '1d',
    exchange VARCHAR(50),
    
    UNIQUE(symbol, timestamp, timeframe),
    CHECK (close_price > 0)
);

CREATE INDEX IF NOT EXISTS idx_market_history_symbol ON market_data_history(symbol);
CREATE INDEX IF NOT EXISTS idx_market_history_timestamp ON market_data_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_market_history_composite ON market_data_history(symbol, timestamp DESC, timeframe);

-- Alerts
CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    portfolio_id INTEGER,
    alert_type VARCHAR(30) NOT NULL,
    symbol VARCHAR(20),
    condition_type VARCHAR(20) NOT NULL,
    threshold_value DECIMAL(20, 8),
    current_value DECIMAL(20, 8),
    message TEXT NOT NULL,
    priority VARCHAR(10) DEFAULT 'medium',
    is_active BOOLEAN DEFAULT 1,
    is_triggered BOOLEAN DEFAULT 0,
    triggered_at TIMESTAMP,
    notification_sent BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    CHECK (alert_type IN ('price_above', 'price_below', 'price_change', 'target_allocation', 'rebalance', 'dividend', 'bond_expiry', 'stop_loss', 'take_profit')),
    CHECK (condition_type IN ('above', 'below', 'change_percent', 'equals')),
    CHECK (priority IN ('low', 'medium', 'high', 'critical'))
);

CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_portfolio ON alerts(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(is_active, is_triggered);
CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol);

-- Alert history
CREATE TABLE IF NOT EXISTS alert_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    triggered_value DECIMAL(20, 8),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_alert_history_user ON alert_history(user_id);
CREATE INDEX IF NOT EXISTS idx_alert_history_date ON alert_history(triggered_at DESC);

-- News
CREATE TABLE IF NOT EXISTS news (
    news_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    source VARCHAR(100) NOT NULL,
    url TEXT UNIQUE,
    author VARCHAR(100),
    published_at TIMESTAMP,
    category VARCHAR(50),
    sentiment VARCHAR(20),
    relevance_score DECIMAL(3, 2),
    symbols TEXT,
    tags TEXT,
    image_url TEXT,
    is_read BOOLEAN DEFAULT 0,
    is_bookmarked BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (category IN ('market', 'economy', 'stock', 'crypto', 'forex', 'commodity', 'company', 'regulation', 'analysis')),
    CHECK (sentiment IN ('positive', 'negative', 'neutral', 'mixed'))
);

CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_category ON news(category);
CREATE INDEX IF NOT EXISTS idx_news_sentiment ON news(sentiment);
CREATE INDEX IF NOT EXISTS idx_news_source ON news(source);

-- Portfolio snapshots
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    snapshot_date DATE NOT NULL,
    total_value DECIMAL(20, 2) NOT NULL,
    cash_balance DECIMAL(20, 2) DEFAULT 0,
    invested_value DECIMAL(20, 2) NOT NULL,
    total_gain_loss DECIMAL(20, 2),
    total_gain_loss_percent DECIMAL(10, 4),
    daily_return DECIMAL(10, 4),
    cumulative_return DECIMAL(10, 4),
    
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    UNIQUE(portfolio_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_portfolio ON portfolio_snapshots(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_date ON portfolio_snapshots(snapshot_date DESC);

-- Asset allocation
CREATE TABLE IF NOT EXISTS asset_allocation (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    snapshot_date DATE NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    sector VARCHAR(50),
    allocation_value DECIMAL(20, 2) NOT NULL,
    allocation_percent DECIMAL(5, 2) NOT NULL,
    
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    CHECK (allocation_percent >= 0 AND allocation_percent <= 100)
);

CREATE INDEX IF NOT EXISTS idx_allocation_portfolio ON asset_allocation(portfolio_id, snapshot_date DESC);

-- System config
CREATE TABLE IF NOT EXISTS system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configs
INSERT OR IGNORE INTO system_config (config_key, config_value, config_type, description) VALUES
('db_version', '1.0.0', 'string', 'Database schema version'),
('market_data_refresh_interval', '60', 'int', 'Market data refresh interval in seconds'),
('cache_ttl', '300', 'int', 'Cache time-to-live in seconds'),
('max_alerts_per_user', '50', 'int', 'Maximum alerts per user'),
('date_format', 'YYYY-MM-DD', 'string', 'Date format for display'),
('base_currency', 'VND', 'string', 'Base currency for calculations');

-- Triggers
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
END;

CREATE TRIGGER IF NOT EXISTS update_portfolios_timestamp 
AFTER UPDATE ON portfolios
BEGIN
    UPDATE portfolios SET updated_at = CURRENT_TIMESTAMP WHERE portfolio_id = NEW.portfolio_id;
END;

CREATE TRIGGER IF NOT EXISTS update_assets_timestamp 
AFTER UPDATE ON assets
BEGIN
    UPDATE assets SET updated_at = CURRENT_TIMESTAMP WHERE asset_id = NEW.asset_id;
END;

CREATE TRIGGER IF NOT EXISTS calculate_asset_gain_loss
AFTER UPDATE OF current_price ON assets
BEGIN
    UPDATE assets 
    SET 
        current_value = NEW.quantity * NEW.current_price,
        unrealized_gain_loss = (NEW.quantity * NEW.current_price) - NEW.cost_basis
    WHERE asset_id = NEW.asset_id;
END;

-- Views
CREATE VIEW IF NOT EXISTS v_portfolio_overview AS
SELECT 
    p.portfolio_id,
    p.user_id,
    p.name AS portfolio_name,
    p.currency,
    COUNT(DISTINCT a.asset_id) AS total_assets,
    SUM(a.current_value) AS total_value,
    SUM(a.cost_basis) AS total_cost,
    SUM(a.unrealized_gain_loss) AS total_gain_loss,
    CASE 
        WHEN SUM(a.cost_basis) > 0 
        THEN (SUM(a.unrealized_gain_loss) / SUM(a.cost_basis)) * 100 
        ELSE 0 
    END AS total_return_percent
FROM portfolios p
LEFT JOIN assets a ON p.portfolio_id = a.portfolio_id
WHERE p.is_active = 1
GROUP BY p.portfolio_id;

CREATE VIEW IF NOT EXISTS v_current_allocation AS
SELECT 
    a.portfolio_id,
    a.asset_type,
    COUNT(*) AS asset_count,
    SUM(a.current_value) AS total_value,
    ROUND((SUM(a.current_value) / total_portfolio.value) * 100, 2) AS allocation_percent
FROM assets a
INNER JOIN (
    SELECT portfolio_id, SUM(current_value) AS value
    FROM assets
    GROUP BY portfolio_id
) total_portfolio ON a.portfolio_id = total_portfolio.portfolio_id
GROUP BY a.portfolio_id, a.asset_type;

CREATE VIEW IF NOT EXISTS v_top_performers AS
SELECT 
    portfolio_id,
    symbol,
    asset_name,
    asset_type,
    current_value,
    unrealized_gain_loss,
    ROUND((unrealized_gain_loss / cost_basis) * 100, 2) AS return_percent
FROM assets
WHERE cost_basis > 0
ORDER BY return_percent DESC;
"""

def initialize_database(db_path=DB_PATH, force=False):
    """
    Khởi tạo database schema
    
    Args:
        db_path: Đường dẫn database
        force: Nếu True, xóa database cũ và tạo mới
    """
    print("="*70)
    print("🗄️  Database Initialization")
    print("="*70)
    print()
    
    # Create data directory if not exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Check if database exists
    db_exists = os.path.exists(db_path)
    
    if db_exists and force:
        print(f"⚠️  Removing existing database: {db_path}")
        os.remove(db_path)
        db_exists = False
    
    if db_exists:
        print(f"ℹ️  Database already exists: {db_path}")
        print("   Creating missing tables if any...")
    else:
        print(f"✨ Creating new database: {db_path}")
    
    print()
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📝 Executing schema SQL...")
        
        # Execute schema
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        
        # Verify tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Schema created successfully!")
        print()
        print(f"📊 Created {len(tables)} tables:")
        for i, table in enumerate(tables, 1):
            print(f"   {i:2d}. {table}")
        
        # Get database size
        db_size = os.path.getsize(db_path) / 1024  # KB
        print()
        print(f"💾 Database size: {db_size:.2f} KB")
        print(f"📍 Location: {os.path.abspath(db_path)}")
        
        # Test query
        cursor.execute("SELECT config_value FROM system_config WHERE config_key = 'db_version'")
        version = cursor.fetchone()
        if version:
            print(f"🔖 Database version: {version[0]}")
        
        conn.close()
        
        print()
        print("="*70)
        print("✅ Database initialization completed!")
        print("="*70)
        print()
        print("Next steps:")
        print("  1. Run: python sample_data_generator.py")
        print("  2. Or run the sample data generator notebook")
        print("  3. Then launch your dashboard!")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_status(db_path=DB_PATH):
    """
    Kiểm tra trạng thái database
    """
    print("🔍 Checking database status...")
    print()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("   Run initialize_database() first")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Database exists: {db_path}")
        print(f"📊 Tables found: {len(tables)}")
        
        # Check each table
        print()
        print("Table status:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  • {table:30s} {count:>8,} rows")
        
        conn.close()
        
        print()
        if len(tables) == 0:
            print("⚠️  No tables found. Run initialize_database() to create schema.")
            return False
        else:
            print("✅ Database is ready!")
            return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def reset_database(db_path=DB_PATH):
    """
    Reset database - xóa tất cả data nhưng giữ schema
    """
    print("⚠️  RESETTING DATABASE - This will delete all data!")
    confirm = input("Type 'YES' to confirm: ")
    
    if confirm != 'YES':
        print("Cancelled.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Delete all data
        for table in tables:
            print(f"  Clearing {table}...")
            cursor.execute(f"DELETE FROM {table}")
        
        conn.commit()
        conn.close()
        
        print("✅ Database reset completed!")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

# ============================================
# Main execution
# ============================================

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'check':
            check_database_status()
        elif sys.argv[1] == 'reset':
            reset_database()
        elif sys.argv[1] == 'force':
            initialize_database(force=True)
        else:
            print("Usage:")
            print("  python initialize_database.py        # Initialize database")
            print("  python initialize_database.py check  # Check database status")
            print("  python initialize_database.py reset  # Reset all data")
            print("  python initialize_database.py force  # Force recreate database")
    else:
        # Default: initialize database
        initialize_database()
