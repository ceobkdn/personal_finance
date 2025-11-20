# -*- coding: utf-8 -*-
"""
Market Data Integration Script
===============================
Integrate real-time market data with portfolio dashboard
Run this to update all asset prices automatically

Usage:
    python market_data_integration.py update        # Update all prices once
    python market_data_integration.py schedule      # Start auto-update
    python market_data_integration.py fetch         # Fetch historical data
"""

import sys
import argparse
from market_data_module import MarketDataManager, MarketDataScheduler
from market_data_module import fetch_and_save_all_symbols


def update_prices():
    """Update all asset prices once"""
    print("="*70)
    print("🔄 Updating Asset Prices")
    print("="*70)
    print()
    
    manager = MarketDataManager()
    result = manager.update_all_assets()
    
    print()
    print("📊 Update Summary:")
    print(f"  ✅ Updated: {result['updated']}")
    print(f"  ❌ Failed:  {result['failed']}")
    print()


def schedule_updates(interval=300):
    """Start automatic price updates"""
    print("="*70)
    print("⏰ Starting Scheduled Updates")
    print("="*70)
    print(f"Interval: {interval} seconds ({interval/60:.1f} minutes)")
    print("Press Ctrl+C to stop")
    print()
    
    manager = MarketDataManager()
    scheduler = MarketDataScheduler(manager, interval=interval)
    
    try:
        scheduler.start()
        
        # Keep running
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping scheduler...")
        scheduler.stop()
        print("✅ Scheduler stopped")


def fetch_historical():
    """Fetch historical data for all symbols"""
    print("="*70)
    print("📥 Fetching Historical Data")
    print("="*70)
    print()
    
    fetch_and_save_all_symbols()


def test_connection():
    """Test API connections"""
    print("="*70)
    print("🧪 Testing API Connections")
    print("="*70)
    print()
    
    manager = MarketDataManager()
    
    # Test samples
    test_symbols = [
        ('AAPL', 'stock', 'Yahoo Finance'),
        ('BTC', 'crypto', 'CoinGecko'),
        ('VNM', 'vnstock', 'VNStock')
    ]
    
    results = []
    
    for symbol, asset_type, provider in test_symbols:
        print(f"Testing {provider} with {symbol}...")
        try:
            quote = manager.get_quote(symbol, asset_type)
            
            if quote:
                price = quote.get('current_price', 0)
                change = quote.get('change_percent', 0)
                
                status = "✅"
                message = f"${price:,.2f} ({change:+.2f}%)" if asset_type != 'vnstock' else f"{price:,.0f} VND ({change:+.2f}%)"
                results.append((status, provider, message))
                print(f"  {status} {provider}: {message}")
            else:
                status = "❌"
                message = "Failed to fetch data"
                results.append((status, provider, message))
                print(f"  {status} {provider}: {message}")
                
        except Exception as e:
            status = "❌"
            message = str(e)
            results.append((status, provider, message))
            print(f"  {status} {provider}: {message}")
        
        print()
    
    # Summary
    print("="*70)
    print("📋 Connection Summary:")
    print("="*70)
    for status, provider, message in results:
        print(f"  {status} {provider:15s} - {message}")
    print()


def interactive_menu():
    """Interactive menu for market data operations"""
    while True:
        print("\n" + "="*70)
        print("📊 Market Data Integration Menu")
        print("="*70)
        print()
        print("1. Update all asset prices (once)")
        print("2. Start scheduled updates")
        print("3. Fetch historical data")
        print("4. Test API connections")
        print("5. Update specific symbol")
        print("6. View recent updates")
        print("0. Exit")
        print()
        
        choice = input("Select option (0-6): ").strip()
        
        if choice == '1':
            update_prices()
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            interval = input("Update interval in seconds (default 300): ").strip()
            interval = int(interval) if interval.isdigit() else 300
            schedule_updates(interval)
            
        elif choice == '3':
            fetch_historical()
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            test_connection()
            input("\nPress Enter to continue...")
            
        elif choice == '5':
            symbol = input("Enter symbol (e.g., AAPL, BTC, VNM): ").strip().upper()
            asset_type = input("Asset type (stock/crypto/vnstock): ").strip().lower()
            
            manager = MarketDataManager()
            quote = manager.get_quote(symbol, asset_type)
            
            if quote:
                print(f"\n✅ Quote for {symbol}:")
                print(f"   Price: {quote.get('current_price', 0):,.2f}")
                print(f"   Change: {quote.get('change_percent', 0):+.2f}%")
                print(f"   Volume: {quote.get('volume', 0):,}")
            else:
                print(f"\n❌ Failed to fetch quote for {symbol}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            view_recent_updates()
            input("\nPress Enter to continue...")
            
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
            
        else:
            print("\n❌ Invalid option. Please try again.")


def view_recent_updates():
    """View recent price updates from database"""
    import sqlite3
    import pandas as pd
    from datetime import datetime, timedelta
    
    print("\n" + "="*70)
    print("📋 Recent Price Updates")
    print("="*70)
    print()
    
    try:
        conn = sqlite3.connect('data/portfolio.db')
        
        # Get recent updates
        query = """
        SELECT 
            symbol,
            asset_type,
            current_price,
            change_percent,
            volume,
            last_updated
        FROM market_data_cache
        ORDER BY last_updated DESC
        LIMIT 20
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            print("No recent updates found.")
            return
        
        # Format and display
        df['last_updated'] = pd.to_datetime(df['last_updated'])
        df['time_ago'] = df['last_updated'].apply(
            lambda x: f"{int((datetime.now() - x).total_seconds() / 60)} min ago"
        )
        
        print(f"{'Symbol':<10} {'Type':<10} {'Price':<15} {'Change':<10} {'Updated':<15}")
        print("-" * 70)
        
        for _, row in df.iterrows():
            symbol = row['symbol']
            asset_type = row['asset_type']
            price = f"${row['current_price']:,.2f}"
            change = f"{row['change_percent']:+.2f}%"
            updated = row['time_ago']
            
            print(f"{symbol:<10} {asset_type:<10} {price:<15} {change:<10} {updated:<15}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def setup_cron_job():
    """Generate cron job configuration for automatic updates"""
    print("="*70)
    print("⏰ Cron Job Setup")
    print("="*70)
    print()
    print("To schedule automatic price updates, add this to your crontab:")
    print()
    print("# Update portfolio prices every 5 minutes during market hours")
    print("*/5 * * * * cd /path/to/portfolio_system && python market_data_integration.py update")
    print()
    print("# Fetch historical data daily at 6 PM")
    print("0 18 * * * cd /path/to/portfolio_system && python market_data_integration.py fetch")
    print()
    print("To edit crontab:")
    print("  crontab -e")
    print()


# ============================================
# MAIN
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description='Market Data Integration for Portfolio System'
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['update', 'schedule', 'fetch', 'test', 'menu', 'cron'],
        default='menu',
        help='Command to execute'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Update interval in seconds (for schedule command)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'update':
        update_prices()
    
    elif args.command == 'schedule':
        schedule_updates(args.interval)
    
    elif args.command == 'fetch':
        fetch_historical()
    
    elif args.command == 'test':
        test_connection()
    
    elif args.command == 'cron':
        setup_cron_job()
    
    else:  # menu
        interactive_menu()


if __name__ == "__main__":
    main()
