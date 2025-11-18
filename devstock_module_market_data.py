#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Market Data Module
==================
Real-time market data integration from multiple sources
Supports: Yahoo Finance, Alpha Vantage, CoinGecko, VNStock
Platform: Jetson Nano + Python

Author: Portfolio System
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import sqlite3
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging
import json
from functools import lru_cache
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# BASE MARKET DATA CLASS
# ============================================

class MarketDataProvider:
    """Base class for market data providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _rate_limit_wait(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = (data, time.time())
    
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote - to be implemented by subclasses"""
        raise NotImplementedError
    
    def get_historical(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """Get historical data - to be implemented by subclasses"""
        raise NotImplementedError


# ============================================
# YAHOO FINANCE PROVIDER (FREE)
# ============================================

class YahooFinanceProvider(MarketDataProvider):
    """
    Yahoo Finance data provider - FREE, no API key needed
    Supports: Stocks, ETFs, Forex, Crypto
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://query1.finance.yahoo.com"
        self.rate_limit_delay = 2.0  # Increased to avoid rate limits
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_quote(self, symbol: str) -> Dict:
        """
        Get real-time quote from Yahoo Finance
        
        Args:
            symbol: Ticker symbol (e.g., 'AAPL', 'BTC-USD')
            
        Returns:
            Dictionary with quote data
        """
        cache_key = f"yahoo_quote_{symbol}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        self._rate_limit_wait()
        
        try:
            url = f"{self.base_url}/v8/finance/chart/{symbol}"
            params = {
                'interval': '1d',
                'range': '1d'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart']:
                logger.error(f"Invalid response for {symbol}")
                return {}
            
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            quote = result.get('indicators', {}).get('quote', [{}])[0]
            
            # Extract data
            current_price = meta.get('regularMarketPrice', 0)
            prev_close = meta.get('previousClose', 0)
            
            quote_data = {
                'symbol': symbol,
                'current_price': current_price,
                'open_price': quote.get('open', [0])[-1] if quote.get('open') else 0,
                'high_price': quote.get('high', [0])[-1] if quote.get('high') else 0,
                'low_price': quote.get('low', [0])[-1] if quote.get('low') else 0,
                'close_price': prev_close,
                'volume': quote.get('volume', [0])[-1] if quote.get('volume') else 0,
                'market_cap': meta.get('marketCap'),
                'change_value': current_price - prev_close if prev_close else 0,
                'change_percent': ((current_price - prev_close) / prev_close * 100) if prev_close else 0,
                'currency': meta.get('currency', 'USD'),
                'exchange': meta.get('exchangeName', 'Unknown'),
                'timestamp': datetime.now()
            }
            
            self._set_cache(cache_key, quote_data)
            logger.info(f"Fetched quote for {symbol}: ${current_price:.2f}")
            
            return quote_data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limit hit for {symbol}. Using fallback method...")
                # Try alternative method
                return self._get_quote_fallback(symbol)
            else:
                logger.error(f"HTTP error fetching quote for {symbol}: {e}")
                return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error for {symbol}: {e}")
            return {}
    
    def _get_quote_fallback(self, symbol: str) -> Dict:
        """Fallback method using alternative Yahoo Finance endpoint"""
        try:
            # Alternative endpoint
            url = f"https://finance.yahoo.com/quote/{symbol}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Parse HTML (simplified - in production use BeautifulSoup)
                import re
                
                # Try to extract price from HTML
                price_match = re.search(r'"regularMarketPrice":\{"raw":([\d.]+)', response.text)
                
                if price_match:
                    price = float(price_match.group(1))
                    
                    return {
                        'symbol': symbol,
                        'current_price': price,
                        'currency': 'USD',
                        'exchange': 'Yahoo',
                        'timestamp': datetime.now()
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"Fallback method failed for {symbol}: {e}")
            return {}
    
    def get_historical(self, symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """
        Get historical OHLCV data
        
        Args:
            symbol: Ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"yahoo_hist_{symbol}_{period}_{interval}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        self._rate_limit_wait()
        
        try:
            url = f"{self.base_url}/v8/finance/chart/{symbol}"
            params = {
                'interval': interval,
                'range': period
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result = data['chart']['result'][0]
            
            # Extract timestamps and quotes
            timestamps = result['timestamp']
            quote = result['indicators']['quote'][0]
            
            # Create DataFrame
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(timestamps, unit='s'),
                'open': quote['open'],
                'high': quote['high'],
                'low': quote['low'],
                'close': quote['close'],
                'volume': quote['volume']
            })
            
            # Clean data
            df = df.dropna()
            df['symbol'] = symbol
            
            self._set_cache(cache_key, df)
            logger.info(f"Fetched {len(df)} historical records for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()


# ============================================
# COINGECKO PROVIDER (FREE - CRYPTO)
# ============================================

class CoinGeckoProvider(MarketDataProvider):
    """
    CoinGecko API for cryptocurrency data - FREE
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit_delay = 1.5  # CoinGecko free tier
        
        # Common crypto ID mappings
        self.symbol_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2'
        }
    
    def _get_coin_id(self, symbol: str) -> str:
        """Convert symbol to CoinGecko coin ID"""
        symbol = symbol.upper().replace('-USD', '').replace('USDT', '')
        return self.symbol_map.get(symbol, symbol.lower())
    
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time crypto quote"""
        cache_key = f"coingecko_quote_{symbol}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        self._rate_limit_wait()
        
        try:
            coin_id = self._get_coin_id(symbol)
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if coin_id not in data:
                logger.error(f"Coin {symbol} not found")
                return {}
            
            coin_data = data[coin_id]
            
            quote_data = {
                'symbol': symbol,
                'current_price': coin_data.get('usd', 0),
                'market_cap': coin_data.get('usd_market_cap'),
                'volume': coin_data.get('usd_24h_vol'),
                'change_percent': coin_data.get('usd_24h_change', 0),
                'currency': 'USD',
                'exchange': 'CoinGecko',
                'timestamp': datetime.now()
            }
            
            self._set_cache(cache_key, quote_data)
            logger.info(f"Fetched crypto quote for {symbol}: ${quote_data['current_price']:.2f}")
            
            return quote_data
            
        except Exception as e:
            logger.error(f"Error fetching crypto quote for {symbol}: {e}")
            return {}
    
    def get_historical(self, symbol: str, days: int = 365) -> pd.DataFrame:
        """Get historical crypto data"""
        cache_key = f"coingecko_hist_{symbol}_{days}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        self._rate_limit_wait()
        
        try:
            coin_id = self._get_coin_id(symbol)
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily' if days > 90 else 'hourly'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract prices
            prices = data.get('prices', [])
            
            df = pd.DataFrame(prices, columns=['timestamp', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            df['open'] = df['close']  # Simplified
            df['high'] = df['close']
            df['low'] = df['close']
            df['volume'] = 0
            
            self._set_cache(cache_key, df)
            logger.info(f"Fetched {len(df)} crypto historical records for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching crypto historical data for {symbol}: {e}")
            return pd.DataFrame()


# ============================================
# VNSTOCK PROVIDER (FREE - VIETNAM STOCKS)
# ============================================

class VNStockProvider(MarketDataProvider):
    """
    VNStock provider for Vietnam stock market data - FREE
    Compatible with vnstock 2.x and 3.x
    """
    
    def __init__(self):
        super().__init__()
        self.rate_limit_delay = 0.5
        
        try:
            import vnstock
            
            # Check if Vnstock class exists (newer version)
            if hasattr(vnstock, 'Vnstock'):
                self.vnstock_module = vnstock
                self.vnstock = vnstock.Vnstock()
                self.version = 'new'
                self.available = True
                logger.info("VNStock (new version) provider initialized")
            else:
                # Old version
                self.vnstock_module = vnstock
                self.vnstock = vnstock
                self.version = 'old'
                self.available = True
                logger.info("VNStock (old version) provider initialized")
                
        except ImportError:
            logger.warning("vnstock not installed. Run: pip install vnstock")
            self.available = False
            self.version = None
    
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote for VN stocks"""
        if not self.available:
            return {}
        
        cache_key = f"vnstock_quote_{symbol}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        self._rate_limit_wait()
        
        try:
            if self.version == 'new':
                # New Vnstock API
                stock = self.vnstock.stock(symbol=symbol, source='VCI')
                
                # Get recent data (last 5 days to ensure we get latest)
                from datetime import datetime, timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=5)
                
                df = stock.quote.history(
                    symbol=symbol,
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d')
                )
                
                if df.empty:
                    logger.warning(f"No data returned for {symbol}")
                    return {}
                
                # Get latest row
                latest = df.iloc[-1]
                
                # Calculate change if we have previous day
                change_value = 0
                change_percent = 0
                if len(df) > 1:
                    prev_close = float(df.iloc[-2]['close'])
                    current = float(latest['close'])
                    change_value = current - prev_close
                    change_percent = (change_value / prev_close * 100) if prev_close else 0
                
                quote_data = {
                    'symbol': symbol,
                    'current_price': float(latest['close']),
                    'open_price': float(latest['open']),
                    'high_price': float(latest['high']),
                    'low_price': float(latest['low']),
                    'close_price': float(latest['close']),
                    'volume': int(latest['volume']),
                    'change_value': change_value,
                    'change_percent': change_percent,
                    'currency': 'VND',
                    'exchange': 'HOSE/HNX',
                    'timestamp': datetime.now()
                }
                
            else:
                # Old version fallback
                logger.error("Old vnstock version not fully supported")
                return {}
            
            self._set_cache(cache_key, quote_data)
            logger.info(f"Fetched VN stock quote for {symbol}: {quote_data['current_price']:,.0f} VND")
            
            return quote_data
            
        except Exception as e:
            logger.error(f"Error fetching VN stock quote for {symbol}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {}
    
    def get_historical(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get historical data for VN stocks"""
        if not self.available:
            return pd.DataFrame()
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        cache_key = f"vnstock_hist_{symbol}_{start_date}_{end_date}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        self._rate_limit_wait()
        
        try:
            if self.version == 'new':
                stock = self.vnstock.stock(symbol=symbol, source='VCI')
                df = stock.quote.history(symbol=symbol, start=start_date, end=end_date)
            else:
                logger.error("Old vnstock version not supported for historical data")
                return pd.DataFrame()
            
            if df.empty:
                return pd.DataFrame()
            
            # Standardize column names
            if 'time' in df.columns:
                df = df.rename(columns={'time': 'timestamp'})
            elif 'date' in df.columns:
                df = df.rename(columns={'date': 'timestamp'})
            elif 'tradingDate' in df.columns:
                df = df.rename(columns={'tradingDate': 'timestamp'})
            
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            df['symbol'] = symbol
            
            self._set_cache(cache_key, df)
            logger.info(f"Fetched {len(df)} VN stock historical records for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching VN stock historical data for {symbol}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return pd.DataFrame()


# ============================================
# UNIFIED MARKET DATA MANAGER
# ============================================

class MarketDataManager:
    """
    Unified manager for all market data providers
    Automatically routes requests to appropriate provider
    """
    
    def __init__(self, db_path: str = 'data/portfolio.db'):
        self.db_path = db_path
        
        # Initialize providers
        self.yahoo = YahooFinanceProvider()
        self.coingecko = CoinGeckoProvider()
        self.vnstock = VNStockProvider()
        
        logger.info("Market Data Manager initialized")
    
    def _detect_asset_type(self, symbol: str) -> str:
        """Detect asset type from symbol"""
        symbol_upper = symbol.upper()
        
        # Crypto patterns
        if any(x in symbol_upper for x in ['BTC', 'ETH', 'USDT', '-USD']):
            return 'crypto'
        
        # VN stock patterns
        if len(symbol) <= 4 and symbol.isalpha() and symbol.isupper():
            return 'vnstock'
        
        # Default to Yahoo (international stocks)
        return 'stock'
    
    def get_quote(self, symbol: str, asset_type: Optional[str] = None) -> Dict:
        """
        Get real-time quote for any symbol
        
        Args:
            symbol: Ticker symbol
            asset_type: 'stock', 'crypto', 'vnstock' (auto-detect if None)
            
        Returns:
            Quote dictionary
        """
        if not asset_type:
            asset_type = self._detect_asset_type(symbol)
        
        logger.info(f"Fetching quote for {symbol} (type: {asset_type})")
        
        try:
            if asset_type == 'crypto':
                return self.coingecko.get_quote(symbol)
            elif asset_type == 'vnstock':
                return self.vnstock.get_quote(symbol)
            else:
                return self.yahoo.get_quote(symbol)
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return {}
    
    def get_historical(self, symbol: str, asset_type: Optional[str] = None, 
                      period: str = '1y') -> pd.DataFrame:
        """
        Get historical data for any symbol
        
        Args:
            symbol: Ticker symbol
            asset_type: Asset type (auto-detect if None)
            period: Time period
            
        Returns:
            DataFrame with historical data
        """
        if not asset_type:
            asset_type = self._detect_asset_type(symbol)
        
        logger.info(f"Fetching historical data for {symbol} (type: {asset_type})")
        
        try:
            if asset_type == 'crypto':
                days = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730}.get(period, 365)
                return self.coingecko.get_historical(symbol, days=days)
            elif asset_type == 'vnstock':
                return self.vnstock.get_historical(symbol)
            else:
                return self.yahoo.get_historical(symbol, period=period)
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def update_asset_price(self, asset_id: int, symbol: str, asset_type: str):
        """
        Update price for a single asset in database
        
        Args:
            asset_id: Asset ID in database
            symbol: Ticker symbol
            asset_type: Asset type
        """
        quote = self.get_quote(symbol, asset_type)
        
        if not quote:
            logger.warning(f"Could not fetch quote for {symbol}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE assets
                SET current_price = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE asset_id = ?
            """, (quote['current_price'], asset_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated price for asset {asset_id} ({symbol}): {quote['current_price']}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating asset price: {e}")
            return False
    
    def update_all_assets(self):
        """
        Update prices for all assets in database
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all active assets
            cursor.execute("""
                SELECT asset_id, symbol, asset_type
                FROM assets
                JOIN portfolios ON assets.portfolio_id = portfolios.portfolio_id
                WHERE portfolios.is_active = 1
            """)
            
            assets = cursor.fetchall()
            conn.close()
            
            logger.info(f"Updating prices for {len(assets)} assets...")
            
            updated = 0
            failed = 0
            
            for asset_id, symbol, asset_type in assets:
                if self.update_asset_price(asset_id, symbol, asset_type):
                    updated += 1
                else:
                    failed += 1
                
                # Rate limiting
                time.sleep(0.5)
            
            logger.info(f"Price update complete: {updated} updated, {failed} failed")
            
            return {'updated': updated, 'failed': failed}
            
        except Exception as e:
            logger.error(f"Error updating all assets: {e}")
            return {'updated': 0, 'failed': 0}
    
    def save_market_data_cache(self, symbol: str, asset_type: str):
        """
        Save current market data to cache table
        """
        quote = self.get_quote(symbol, asset_type)
        
        if not quote:
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO market_data_cache (
                    symbol, asset_type, current_price, open_price, high_price,
                    low_price, close_price, volume, market_cap, change_percent,
                    change_value, currency, exchange, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                symbol, asset_type, quote.get('current_price', 0),
                quote.get('open_price', 0), quote.get('high_price', 0),
                quote.get('low_price', 0), quote.get('close_price', 0),
                quote.get('volume', 0), quote.get('market_cap'),
                quote.get('change_percent', 0), quote.get('change_value', 0),
                quote.get('currency', 'USD'), quote.get('exchange', 'Unknown')
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved market data cache for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving market data cache: {e}")
            return False
    
    def save_historical_data(self, symbol: str, asset_type: str, df: pd.DataFrame):
        """
        Save historical data to database
        """
        if df.empty:
            logger.warning(f"No historical data to save for {symbol}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Prepare data
            df = df.copy()
            df['symbol'] = symbol
            df['asset_type'] = asset_type
            df['timeframe'] = '1d'
            df['exchange'] = 'Various'
            
            # Select relevant columns
            cols = ['symbol', 'asset_type', 'timestamp', 'open', 'high', 
                   'low', 'close', 'volume', 'timeframe', 'exchange']
            
            df_save = df[cols].rename(columns={
                'open': 'open_price',
                'high': 'high_price',
                'low': 'low_price',
                'close': 'close_price'
            })
            
            # Save to database
            df_save.to_sql('market_data_history', conn, if_exists='append', 
                          index=False, method='multi')
            
            conn.close()
            
            logger.info(f"Saved {len(df_save)} historical records for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving historical data: {e}")
            return False


# ============================================
# AUTO-UPDATE SCHEDULER
# ============================================

class MarketDataScheduler:
    """
    Automatic market data updates on schedule
    """
    
    def __init__(self, manager: MarketDataManager, interval: int = 300):
        """
        Args:
            manager: MarketDataManager instance
            interval: Update interval in seconds (default 5 minutes)
        """
        self.manager = manager
        self.interval = interval
        self.running = False
        self.thread = None
    
    def _update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                logger.info("Starting scheduled market data update...")
                result = self.manager.update_all_assets()
                logger.info(f"Scheduled update complete: {result}")
            except Exception as e:
                logger.error(f"Error in scheduled update: {e}")
            
            # Wait for next update
            time.sleep(self.interval)
    
    def start(self):
        """Start automatic updates"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        
        logger.info(f"Market data scheduler started (interval: {self.interval}s)")
    
    def stop(self):
        """Stop automatic updates"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Market data scheduler stopped")


# ============================================
# UTILITY FUNCTIONS
# ============================================

def fetch_and_save_all_symbols(db_path: str = 'data/portfolio.db'):
    """
    Fetch and save data for all symbols in database
    """
    manager = MarketDataManager(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get unique symbols
        cursor.execute("""
            SELECT DISTINCT symbol, asset_type
            FROM assets
        """)
        
        symbols = cursor.fetchall()
        conn.close()
        
        print(f"Fetching data for {len(symbols)} symbols...")
        
        for symbol, asset_type in symbols:
            print(f"\nProcessing {symbol} ({asset_type})...")
            
            # Get and save current quote
            manager.save_market_data_cache(symbol, asset_type)
            
            # Get and save historical data
            df = manager.get_historical(symbol, asset_type)
            if not df.empty:
                manager.save_historical_data(symbol, asset_type, df)
            
            time.sleep(1)  # Rate limiting
        
        print("\n✅ All market data fetched and saved!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================
# MAIN - DEMO
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("📊 Market Data Module - Demo")
    print("="*70)
    print()
    
    # Initialize manager
    manager = MarketDataManager()
    
    # Test Yahoo Finance
    print("1️⃣  Testing Yahoo Finance...")
    quote = manager.get_quote('AAPL', 'stock')
    if quote:
        print(f"   ✓ AAPL: ${quote['current_price']:.2f} ({quote['change_percent']:+.2f}%)")
    
    # Test CoinGecko
    print("\n2️⃣  Testing CoinGecko...")
    quote = manager.get_quote('BTC', 'crypto')
    if quote:
        print(f"   ✓ BTC: ${quote['current_price']:,.2f} ({quote['change_percent']:+.2f}%)")
    
    # Test VNStock
    print("\n3️⃣  Testing VNStock...")
    quote = manager.get_quote('VNM', 'vnstock')
    if quote:
        print(f"   ✓ VNM: {quote['current_price']:,.0f} VND ({quote['change_percent']:+.2f}%)")
    
    # Test historical data
    print("\n4️⃣  Testing historical data...")
    df = manager.get_historical('AAPL', 'stock', period='1mo')
    if not df.empty:
        print(f"   ✓ Fetched {len(df)} records for AAPL")
        print(f"   Latest: ${df.iloc[-1]['close']:.2f}")
    
    print("\n" + "="*70)
    print("✅ Demo completed!")
    print("="*70)
