"""
Complete Setup Script for Portfolio Dashboard
==============================================
This script will:
1. Check and create data directory
2. Initialize database schema
3. Generate sample data
4. Verify everything is ready

Run this ONCE before using the dashboard.
"""

import os
import sys
from pathlib import Path

print("="*70)
print("🚀 Portfolio Dashboard - Complete Setup")
print("="*70)
print()

# ============================================
# STEP 1: Setup directories
# ============================================

print("📁 Step 1: Setting up directories...")

# Get current directory
current_dir = os.getcwd()
print(f"   Current directory: {current_dir}")

# Create data directory
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)
print(f"   ✓ Data directory: {data_dir.absolute()}")

# Create backups directory
backup_dir = data_dir / 'backups'
backup_dir.mkdir(exist_ok=True)
print(f"   ✓ Backups directory: {backup_dir.absolute()}")

# Create market_data directory
market_data_dir = data_dir / 'market_data'
market_data_dir.mkdir(exist_ok=True)
print(f"   ✓ Market data directory: {market_data_dir.absolute()}")

print()

# ============================================
# STEP 2: Initialize database
# ============================================

print("🗄️  Step 2: Initializing database...")

DB_PATH = 'data/portfolio.db'

# Check if database already exists
db_exists = os.path.exists(DB_PATH)

if db_exists:
    print(f"   ℹ️  Database already exists: {DB_PATH}")
    response = input("   Do you want to recreate it? (yes/no): ").lower()
    
    if response == 'yes':
        print("   🗑️  Removing old database...")
        os.remove(DB_PATH)
        db_exists = False
    else:
        print("   ✓ Using existing database")

if not db_exists:
    print("   ✨ Creating new database...")
    
    # Import and run initialize_database
    try:
        # Try to import from file
        if os.path.exists('initialize_database.py'):
            import initialize_database
            success = initialize_database.initialize_database(DB_PATH)
        else:
            # Run inline
            print("   📝 Running inline initialization...")
            exec(open('initialize_database.py').read())
            success = True
        
        if success:
            print("   ✅ Database initialized successfully!")
        else:
            print("   ❌ Database initialization failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\n   Please run initialize_database.py manually first:")
        print("   $ python initialize_database.py")
        sys.exit(1)

print()

# ============================================
# STEP 3: Generate sample data
# ============================================

print("📊 Step 3: Generating sample data...")

response = input("   Generate sample data? (yes/no): ").lower()

if response == 'yes':
    try:
        # Try to import from file
        if os.path.exists('sample_data_generator.py'):
            print("   Running sample_data_generator.py...")
            exec(open('sample_data_generator.py').read())
        else:
            print("   ⚠️  sample_data_generator.py not found")
            print("   You can generate sample data later")
    except Exception as e:
        print(f"   ❌ Error generating sample data: {e}")
        print("   You can run it manually later:")
        print("   $ python sample_data_generator.py")
else:
    print("   ⏭️  Skipped sample data generation")

print()

# ============================================
# STEP 4: Verify setup
# ============================================

print("✅ Step 4: Verifying setup...")
print()

try:
    import sqlite3
    
    # Check database
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"   ✓ Database file: {os.path.abspath(DB_PATH)}")
        print(f"   ✓ Database size: {os.path.getsize(DB_PATH) / 1024:.2f} KB")
        print(f"   ✓ Tables found: {len(tables)}")
        
        # Check data
        print()
        print("   Data summary:")
        for table in ['users', 'portfolios', 'assets', 'transactions']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                status = "✓" if count > 0 else "⚠️"
                print(f"     {status} {table:20s} {count:>6,} rows")
        
        conn.close()
        
        print()
        print("="*70)
        print("🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("="*70)
        print()
        print("📖 Next steps:")
        print()
        print("1. Open Jupyter Lab:")
        print("   $ jupyter lab")
        print()
        print("2. Create a new notebook or open dashboard notebook")
        print()
        print("3. Import and run dashboard:")
        print("   ```python")
        print("   # Copy code from 'Interactive Portfolio Dashboard' artifact")
        print("   # Or run:")
        print("   exec(open('dashboard.py').read())")
        print("   create_interactive_dashboard()")
        print("   ```")
        print()
        print("4. Login credentials (if sample data generated):")
        print("   - Username: demo_user")
        print("   - Password: demo123")
        print()
        print("="*70)
        
    else:
        print("   ❌ Database file not found!")
        print("   Please run initialize_database.py")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================
# STEP 5: Create quick start script
# ============================================

print()
print("📝 Creating quick start script...")

quick_start = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
Quick Start Dashboard
Run this to launch the dashboard quickly
\"\"\"

import sys
import os

# Check database
if not os.path.exists('data/portfolio.db'):
    print("❌ Database not found!")
    print("Run: python complete_setup.py")
    sys.exit(1)

# Launch dashboard
print("🚀 Launching dashboard...")
print("This will open in your default browser...")
print()

# Import dashboard code
exec(open('dashboard.py').read())

# Launch
launch_complete_dashboard()
"""

with open('quick_start.py', 'w') as f:
    f.write(quick_start)

os.chmod('quick_start.py', 0o755)
print("   ✓ Created quick_start.py")

print()
print("You can now run:")
print("  $ python quick_start.py")
print()

# ============================================
# Create config file
# ============================================

config_content = """# Portfolio System Configuration
# Edit this file to customize your settings

[database]
path = data/portfolio.db
backup_path = data/backups/

[market_data]
refresh_interval = 60
cache_ttl = 300
data_path = data/market_data/

[dashboard]
default_time_range = 365
max_assets_display = 15
chart_height = 500

[api]
# Add your API keys here (never commit this file!)
# alpha_vantage_key = YOUR_KEY_HERE
# yahoo_finance_key = YOUR_KEY_HERE
"""

with open('config.ini', 'w') as f:
    f.write(config_content)

print("   ✓ Created config.ini")
print()

# ============================================
# Create .gitignore
# ============================================

gitignore_content = """# Portfolio System .gitignore

# Database files
data/portfolio.db
data/portfolio.db-wal
data/portfolio.db-shm
data/backups/
data/market_data/

# API keys and secrets
config.ini
api_keys.yaml
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# Jupyter
.ipynb_checkpoints/
*.ipynb

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""

with open('.gitignore', 'w') as f:
    f.write(gitignore_content)

print("   ✓ Created .gitignore")
print()

print("="*70)
print("✨ All setup files created!")
print("="*70)
