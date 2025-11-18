"""
Sample Data Generator for Portfolio Dashboard
==============================================
Tạo dữ liệu mẫu để test dashboard
Platform: Jetson Nano + Jupyter Lab
"""

import sqlite3
import random
import numpy as np
from datetime import datetime, timedelta
import hashlib

# ============================================
# CELL 1: Configuration
# ============================================

# Database path
DB_PATH = 'data/portfolio.db'

# Sample data configuration
NUM_PORTFOLIOS = 2
NUM_ASSETS_PER_PORTFOLIO = 10
NUM_TRANSACTIONS_PER_ASSET = 5
NUM_HISTORICAL_DAYS = 365

# Asset symbols for different types
SAMPLE_STOCKS = ['VNM', 'VCB', 'HPG', 'VHM', 'FPT', 'GAS', 'PLX', 'MSN', 'MWG', 'VRE',
                 'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
SAMPLE_CRYPTO = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'DOT', 'MATIC', 'AVAX']
SAMPLE_BONDS = ['BOND-VN-10Y', 'BOND-US-10Y', 'BOND-CORP-AAA']

SECTORS = ['Technology', 'Finance', 'Energy', 'Consumer', 'Healthcare', 'Industrial']
EXCHANGES_STOCK = ['HOSE', 'HNX', 'NYSE', 'NASDAQ']
EXCHANGES_CRYPTO = ['Binance', 'Coinbase', 'Kraken']

print("✓ Configuration loaded")


# ============================================
# CELL 2: Helper Functions
# ============================================

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def random_date(start_date, end_date):
    """Generate random date between start and end"""
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    return start_date + timedelta(days=random_days)

def generate_price_series(initial_price, num_days, volatility=0.02, trend=0.0001):
    """
    Generate realistic price series using geometric Brownian motion
    
    Args:
        initial_price: Starting price
        num_days: Number of days
        volatility: Daily volatility (default 2%)
        trend: Daily trend/drift (default 0.01%)
    
    Returns:
        Array of prices
    """
    prices = [initial_price]
    
    for _ in range(num_days - 1):
        change = np.random.normal(trend, volatility)
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 0.01))  # Prevent negative prices
    
    return np.array(prices)

print("✓ Helper functions defined")


# ============================================
# CELL 3: Generate Users
# ============================================

def create_sample_users(conn):
    """Create sample users"""
    cursor = conn.cursor()
    
    users = [
        ('demo_user', 'demo@example.com', hash_password('demo123'), 'Demo User', 'user'),
        ('john_doe', 'john@example.com', hash_password('john123'), 'John Doe', 'user'),
        ('admin', 'admin@example.com', hash_password('admin123'), 'Administrator', 'admin'),
    ]
    
    cursor.executemany("""
        INSERT INTO users (username, email, password_hash, full_name, role)
        VALUES (?, ?, ?, ?, ?)
    """, users)
    
    conn.commit()
    
    print(f"✓ Created {len(users)} users")
    
    # Return user IDs
    cursor.execute("SELECT user_id FROM users")
    return [row[0] for row in cursor.fetchall()]


# ============================================
# CELL 4: Generate Portfolios
# ============================================

def create_sample_portfolios(conn, user_ids):
    """Create sample portfolios"""
    cursor = conn.cursor()
    
    portfolio_names = [
        'Growth Portfolio',
        'Conservative Portfolio',
        'Crypto Portfolio',
        'Dividend Portfolio',
        'Tech Focus Portfolio'
    ]
    
    portfolios = []
    for i in range(NUM_PORTFOLIOS):
        user_id = random.choice(user_ids)
        name = portfolio_names[i % len(portfolio_names)]
        currency = random.choice(['VND', 'USD'])
        initial_value = random.randint(100_000_000, 1_000_000_000)  # 100M - 1B VND
        
        portfolios.append((
            user_id, name, f'Sample {name}', currency, initial_value, initial_value
        ))
    
    cursor.executemany("""
        INSERT INTO portfolios (user_id, name, description, currency, initial_value, current_value)
        VALUES (?, ?, ?, ?, ?, ?)
    """, portfolios)
    
    conn.commit()
    
    print(f"✓ Created {len(portfolios)} portfolios")
    
    # Return portfolio IDs
    cursor.execute("SELECT portfolio_id FROM portfolios")
    return [row[0] for row in cursor.fetchall()]


# ============================================
# CELL 5: Generate Assets
# ============================================

def create_sample_assets(conn, portfolio_ids):
    """Create sample assets"""
    cursor = conn.cursor()
    
    assets = []
    asset_price_data = {}  # Store for later use
    
    for portfolio_id in portfolio_ids:
        # Determine portfolio strategy
        num_assets = random.randint(5, NUM_ASSETS_PER_PORTFOLIO)
        
        for _ in range(num_assets):
            # Randomly choose asset type
            asset_type = random.choice(['stock', 'stock', 'stock', 'crypto', 'bond'])
            
            if asset_type == 'stock':
                symbol = random.choice(SAMPLE_STOCKS)
                exchange = random.choice(EXCHANGES_STOCK)
                sector = random.choice(SECTORS)
                purchase_price = random.uniform(10, 500) * 1000  # VND or USD
                current_price = purchase_price * random.uniform(0.7, 1.5)
            elif asset_type == 'crypto':
                symbol = random.choice(SAMPLE_CRYPTO)
                exchange = random.choice(EXCHANGES_CRYPTO)
                sector = 'Cryptocurrency'
                purchase_price = random.uniform(100, 50000)
                current_price = purchase_price * random.uniform(0.5, 2.0)
            else:  # bond
                symbol = random.choice(SAMPLE_BONDS)
                exchange = 'OTC'
                sector = 'Fixed Income'
                purchase_price = random.uniform(1000, 10000)
                current_price = purchase_price * random.uniform(0.95, 1.05)
            
            asset_name = f"{symbol} - {asset_type.title()}"
            quantity = random.uniform(1, 100)
            purchase_date = random_date(
                datetime.now() - timedelta(days=730),
                datetime.now() - timedelta(days=30)
            )
            
            cost_basis = quantity * purchase_price
            current_value = quantity * current_price
            unrealized_gain_loss = current_value - cost_basis
            
            asset_data = (
                portfolio_id, symbol, asset_type, asset_name, quantity,
                purchase_price, purchase_date.date(), current_price,
                current_value, cost_basis, unrealized_gain_loss,
                'VND', exchange, sector
            )
            
            assets.append(asset_data)
            
            # Store price info for historical data
            asset_key = f"{symbol}_{asset_type}"
            if asset_key not in asset_price_data:
                asset_price_data[asset_key] = {
                    'symbol': symbol,
                    'type': asset_type,
                    'current_price': current_price,
                    'exchange': exchange
                }
    
    cursor.executemany("""
        INSERT INTO assets (
            portfolio_id, symbol, asset_type, asset_name, quantity,
            purchase_price, purchase_date, current_price, current_value,
            cost_basis, unrealized_gain_loss, currency, exchange, sector
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, assets)
    
    conn.commit()
    
    print(f"✓ Created {len(assets)} assets")
    
    # Return asset IDs and price data
    cursor.execute("SELECT asset_id, symbol, asset_type FROM assets")
    asset_ids = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
    
    return asset_ids, asset_price_data


# ============================================
# CELL 6: Generate Transactions
# ============================================

def create_sample_transactions(conn, asset_ids):
    """Create sample transactions"""
    cursor = conn.cursor()
    
    transactions = []
    
    for asset_id, symbol, asset_type in asset_ids:
        # Get asset details
        cursor.execute("""
            SELECT portfolio_id, purchase_price, purchase_date, quantity
            FROM assets WHERE asset_id = ?
        """, (asset_id,))
        
        portfolio_id, purchase_price, purchase_date, current_quantity = cursor.fetchone()
        purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')
        
        # Initial buy transaction
        transactions.append((
            portfolio_id, asset_id, 'buy', symbol,
            current_quantity, purchase_price,
            current_quantity * purchase_price,
            current_quantity * purchase_price * 0.001,  # 0.1% fee
            0,  # tax
            current_quantity * purchase_price * 0.999,
            'VND', 'HOSE', purchase_date.date()
        ))
        
        # Additional transactions
        num_trans = random.randint(1, NUM_TRANSACTIONS_PER_ASSET)
        
        for _ in range(num_trans):
            trans_type = random.choice(['buy', 'sell', 'dividend'])
            trans_date = random_date(
                purchase_date,
                datetime.now()
            )
            
            if trans_type in ['buy', 'sell']:
                quantity = current_quantity * random.uniform(0.1, 0.3)
                price = purchase_price * random.uniform(0.8, 1.2)
                total_amount = quantity * price
                fee = total_amount * 0.001
                tax = total_amount * 0.001 if trans_type == 'sell' else 0
                net_amount = total_amount - fee - tax
                
                transactions.append((
                    portfolio_id, asset_id, trans_type, symbol,
                    quantity, price, total_amount, fee, tax, net_amount,
                    'VND', 'HOSE', trans_date.date()
                ))
            
            elif trans_type == 'dividend':
                dividend_amount = current_quantity * purchase_price * random.uniform(0.01, 0.05)
                
                transactions.append((
                    portfolio_id, asset_id, 'dividend', symbol,
                    None, None, dividend_amount, 0, 0, dividend_amount,
                    'VND', 'HOSE', trans_date.date()
                ))
    
    cursor.executemany("""
        INSERT INTO transactions (
            portfolio_id, asset_id, transaction_type, symbol,
            quantity, price, total_amount, fee, tax, net_amount,
            currency, exchange, transaction_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, transactions)
    
    conn.commit()
    
    print(f"✓ Created {len(transactions)} transactions")


# ============================================
# CELL 7: Generate Historical Market Data
# ============================================

def create_sample_market_data(conn, asset_price_data):
    """Create historical market data"""
    cursor = conn.cursor()
    
    # Current market data cache
    cache_data = []
    for key, data in asset_price_data.items():
        cache_data.append((
            data['symbol'], data['type'], data['current_price'],
            data['current_price'] * 0.98,  # open
            data['current_price'] * 1.02,  # high
            data['current_price'] * 0.97,  # low
            data['current_price'] * 0.99,  # close
            random.randint(100000, 10000000),  # volume
            random.randint(1000000000, 100000000000),  # market_cap
            random.uniform(-5, 5),  # change_percent
            'VND', data['exchange']
        ))
    
    cursor.executemany("""
        INSERT OR REPLACE INTO market_data_cache (
            symbol, asset_type, current_price, open_price, high_price,
            low_price, close_price, volume, market_cap, change_percent,
            currency, exchange
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, cache_data)
    
    print(f"✓ Created {len(cache_data)} market data cache entries")
    
    # Historical OHLCV data
    history_data = []
    end_date = datetime.now()
    
    for key, data in list(asset_price_data.items())[:5]:  # Limit to 5 assets for performance
        symbol = data['symbol']
        asset_type = data['type']
        current_price = data['current_price']
        
        # Generate price series
        prices = generate_price_series(
            initial_price=current_price * 0.8,
            num_days=NUM_HISTORICAL_DAYS,
            volatility=0.02
        )
        
        for i in range(len(prices)):
            date = end_date - timedelta(days=NUM_HISTORICAL_DAYS - i)
            open_price = prices[i] * random.uniform(0.98, 1.02)
            high_price = prices[i] * random.uniform(1.00, 1.05)
            low_price = prices[i] * random.uniform(0.95, 1.00)
            close_price = prices[i]
            volume = random.randint(10000, 1000000)
            
            history_data.append((
                symbol, asset_type, date, open_price, high_price,
                low_price, close_price, volume, '1d', data['exchange']
            ))
    
    cursor.executemany("""
        INSERT OR IGNORE INTO market_data_history (
            symbol, asset_type, timestamp, open_price, high_price,
            low_price, close_price, volume, timeframe, exchange
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, history_data)
    
    conn.commit()
    
    print(f"✓ Created {len(history_data)} historical market data entries")


# ============================================
# CELL 8: Generate Portfolio Snapshots
# ============================================

def create_sample_snapshots(conn, portfolio_ids):
    """Create daily portfolio value snapshots"""
    cursor = conn.cursor()
    
    snapshots = []
    
    for portfolio_id in portfolio_ids:
        # Get initial portfolio value
        cursor.execute("""
            SELECT initial_value FROM portfolios WHERE portfolio_id = ?
        """, (portfolio_id,))
        initial_value = cursor.fetchone()[0]
        
        # Generate daily snapshots
        end_date = datetime.now()
        values = generate_price_series(
            initial_price=initial_value,
            num_days=NUM_HISTORICAL_DAYS,
            volatility=0.015,
            trend=0.0002
        )
        
        for i in range(len(values)):
            date = end_date - timedelta(days=NUM_HISTORICAL_DAYS - i)
            total_value = values[i]
            invested_value = initial_value
            total_gain_loss = total_value - invested_value
            total_gain_loss_percent = (total_gain_loss / invested_value * 100) if invested_value > 0 else 0
            
            # Daily return
            if i > 0:
                daily_return = (values[i] / values[i-1] - 1) * 100
            else:
                daily_return = 0
            
            # Cumulative return
            cumulative_return = (total_value / initial_value - 1) * 100
            
            snapshots.append((
                portfolio_id, date.date(), total_value,
                initial_value * 0.1,  # cash balance
                invested_value, total_gain_loss, total_gain_loss_percent,
                daily_return, cumulative_return
            ))
    
    cursor.executemany("""
        INSERT OR REPLACE INTO portfolio_snapshots (
            portfolio_id, snapshot_date, total_value, cash_balance,
            invested_value, total_gain_loss, total_gain_loss_percent,
            daily_return, cumulative_return
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, snapshots)
    
    conn.commit()
    
    print(f"✓ Created {len(snapshots)} portfolio snapshots")


# ============================================
# CELL 9: Generate Alerts
# ============================================

def create_sample_alerts(conn, portfolio_ids, asset_ids):
    """Create sample alerts"""
    cursor = conn.cursor()
    
    # Get user IDs
    cursor.execute("""
        SELECT DISTINCT user_id FROM portfolios WHERE portfolio_id IN ({})
    """.format(','.join('?' * len(portfolio_ids))), portfolio_ids)
    user_ids = [row[0] for row in cursor.fetchall()]
    
    alerts = []
    
    for user_id in user_ids:
        # Price alerts
        for _ in range(3):
            asset_id, symbol, asset_type = random.choice(asset_ids)
            alert_type = random.choice(['price_above', 'price_below', 'price_change'])
            threshold = random.uniform(100000, 1000000)
            
            alerts.append((
                user_id, None, alert_type, symbol, 'above' if 'above' in alert_type else 'below',
                threshold, None, f'Alert: {symbol} price {alert_type}', 'medium', 1, 0
            ))
        
        # Portfolio rebalance alert
        portfolio_id = random.choice(portfolio_ids)
        alerts.append((
            user_id, portfolio_id, 'rebalance', None, 'change_percent',
            5.0, None, 'Time to rebalance portfolio', 'high', 1, 0
        ))
    
    cursor.executemany("""
        INSERT INTO alerts (
            user_id, portfolio_id, alert_type, symbol, condition_type,
            threshold_value, current_value, message, priority, is_active, is_triggered
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, alerts)
    
    conn.commit()
    
    print(f"✓ Created {len(alerts)} alerts")


# ============================================
# CELL 10: Generate News
# ============================================

def create_sample_news(conn):
    """Create sample news articles"""
    cursor = conn.cursor()
    
    news_titles = [
        "Market hits new record high on tech rally",
        "Central bank announces interest rate decision",
        "Tech sector leads market gains for third consecutive week",
        "Oil prices surge on supply concerns",
        "Banking stocks decline amid regulatory uncertainty",
        "Cryptocurrency market shows signs of recovery",
        "Economic growth exceeds expectations in Q3",
        "Major merger announced in technology sector",
        "Dividend increases announced by top companies",
        "Market volatility increases amid global tensions"
    ]
    
    sources = ['Bloomberg', 'Reuters', 'CNBC', 'Financial Times', 'VnExpress', 'CafeF']
    categories = ['market', 'economy', 'stock', 'crypto', 'company']
    sentiments = ['positive', 'neutral', 'negative']
    
    news = []
    
    for i, title in enumerate(news_titles):
        published_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        news.append((
            title,
            f"Summary of {title.lower()}...",
            None,  # content
            random.choice(sources),
            f"https://example.com/news/{i+1}",
            'Financial Analyst',
            published_date,
            random.choice(categories),
            random.choice(sentiments),
            random.uniform(0.5, 1.0),
            ','.join(random.sample(SAMPLE_STOCKS, 3)),
            'market,finance,investment',
            f"https://example.com/image/{i+1}.jpg"
        ))
    
    cursor.executemany("""
        INSERT INTO news (
            title, summary, content, source, url, author,
            published_at, category, sentiment, relevance_score,
            symbols, tags, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, news)
    
    conn.commit()
    
    print(f"✓ Created {len(news)} news articles")


# ============================================
# CELL 11: Main Generation Function
# ============================================

def generate_all_sample_data():
    """Main function to generate all sample data"""
    
    print("="*60)
    print("📊 Portfolio Sample Data Generator")
    print("="*60)
    print()
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        print(f"✓ Connected to database: {DB_PATH}\n")
        
        # Generate data in order
        print("1️⃣  Generating users...")
        user_ids = create_sample_users(conn)
        
        print("\n2️⃣  Generating portfolios...")
        portfolio_ids = create_sample_portfolios(conn, user_ids)
        
        print("\n3️⃣  Generating assets...")
        asset_ids, asset_price_data = create_sample_assets(conn, portfolio_ids)
        
        print("\n4️⃣  Generating transactions...")
        create_sample_transactions(conn, asset_ids)
        
        print("\n5️⃣  Generating market data...")
        create_sample_market_data(conn, asset_price_data)
        
        print("\n6️⃣  Generating portfolio snapshots...")
        create_sample_snapshots(conn, portfolio_ids)
        
        print("\n7️⃣  Generating alerts...")
        create_sample_alerts(conn, portfolio_ids, asset_ids)
        
        print("\n8️⃣  Generating news...")
        create_sample_news(conn)
        
        # Close connection
        conn.close()
        
        print("\n" + "="*60)
        print("✅ Sample data generation completed successfully!")
        print("="*60)
        print("\n📝 Summary:")
        print(f"  • Users: {len(user_ids)}")
        print(f"  • Portfolios: {len(portfolio_ids)}")
        print(f"  • Assets: {len(asset_ids)}")
        print(f"  • Historical days: {NUM_HISTORICAL_DAYS}")
        print(f"\n🚀 You can now run the dashboard!")
        print(f"   Demo credentials:")
        print(f"   - Username: demo_user")
        print(f"   - Password: demo123")
        
    except Exception as e:
        print(f"\n✗ Error generating data: {e}")
        raise


# ============================================
# CELL 12: Run Generation
# ============================================

# Run the generation
generate_all_sample_data()

print("\n" + "="*60)
print("Next steps:")
print("  1. Open dashboard notebook")
print("  2. Run: create_interactive_dashboard()")
print("  3. Or run: launch_complete_dashboard()")
print("="*60)
