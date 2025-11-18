# -*- coding: utf-8 -*-
"""
Enhanced Dashboard with Real-time Market Data
==============================================
Dashboard integrated with live market data APIs
"""

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Import market data module
try:
    from module_market_data import MarketDataManager
    MARKET_DATA_AVAILABLE = True
except ImportError:
    print("⚠️  Market data module not found. Real-time updates disabled.")
    MARKET_DATA_AVAILABLE = False


# ============================================
# Real-time Price Widget
# ============================================

class RealTimePriceWidget:
    """Widget showing real-time price updates"""
    
    def __init__(self, manager: MarketDataManager = None):
        self.manager = manager or MarketDataManager()
        self.symbols = []
        self.auto_refresh = False
        
        # Create widgets
        self.symbol_input = widgets.Text(
            description='Symbol:',
            placeholder='Enter symbol (e.g., AAPL)',
            style={'description_width': 'initial'}
        )
        
        self.asset_type = widgets.Dropdown(
            options=['stock', 'crypto', 'vnstock'],
            value='stock',
            description='Type:',
            style={'description_width': 'initial'}
        )
        
        self.add_btn = widgets.Button(
            description='Add Symbol',
            button_style='primary',
            icon='plus'
        )
        
        self.refresh_btn = widgets.Button(
            description='Refresh',
            button_style='info',
            icon='refresh'
        )
        
        self.auto_refresh_toggle = widgets.Checkbox(
            value=False,
            description='Auto-refresh (30s)',
            style={'description_width': 'initial'}
        )
        
        self.output = widgets.Output()
        
        # Event handlers
        self.add_btn.on_click(self.add_symbol)
        self.refresh_btn.on_click(self.refresh_prices)
        self.auto_refresh_toggle.observe(self.toggle_auto_refresh, 'value')
    
    def add_symbol(self, btn):
        """Add symbol to watchlist"""
        symbol = self.symbol_input.value.strip().upper()
        asset_type = self.asset_type.value
        
        if symbol and (symbol, asset_type) not in self.symbols:
            self.symbols.append((symbol, asset_type))
            self.symbol_input.value = ''
            self.refresh_prices()
    
    def refresh_prices(self, btn=None):
        """Refresh all prices"""
        with self.output:
            clear_output(wait=True)
            
            if not self.symbols:
                print("No symbols in watchlist. Add symbols above.")
                return
            
            # Create price table
            html = """
            <style>
                .price-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }
                .price-table th {
                    background: #667eea;
                    color: white;
                    padding: 10px;
                    text-align: left;
                }
                .price-table td {
                    padding: 8px;
                    border-bottom: 1px solid #ddd;
                }
                .price-up { color: green; font-weight: bold; }
                .price-down { color: red; font-weight: bold; }
            </style>
            <table class="price-table">
                <tr>
                    <th>Symbol</th>
                    <th>Type</th>
                    <th>Price</th>
                    <th>Change</th>
                    <th>Volume</th>
                    <th>Updated</th>
                </tr>
            """
            
            for symbol, asset_type in self.symbols:
                quote = self.manager.get_quote(symbol, asset_type)
                
                if quote:
                    price = quote.get('current_price', 0)
                    change = quote.get('change_percent', 0)
                    volume = quote.get('volume', 0)
                    currency = quote.get('currency', 'USD')
                    
                    change_class = 'price-up' if change >= 0 else 'price-down'
                    change_symbol = '▲' if change >= 0 else '▼'
                    
                    if currency == 'VND':
                        price_str = f"{price:,.0f} VND"
                    else:
                        price_str = f"${price:,.2f}"
                    
                    html += f"""
                    <tr>
                        <td><b>{symbol}</b></td>
                        <td>{asset_type}</td>
                        <td>{price_str}</td>
                        <td class="{change_class}">{change_symbol} {abs(change):.2f}%</td>
                        <td>{volume:,}</td>
                        <td>{datetime.now().strftime('%H:%M:%S')}</td>
                    </tr>
                    """
                else:
                    html += f"""
                    <tr>
                        <td><b>{symbol}</b></td>
                        <td>{asset_type}</td>
                        <td colspan="4" style="color: red;">Failed to fetch</td>
                    </tr>
                    """
            
            html += "</table>"
            display(HTML(html))
    
    def toggle_auto_refresh(self, change):
        """Toggle auto-refresh"""
        self.auto_refresh = change['new']
        
        if self.auto_refresh:
            self._start_auto_refresh()
    
    def _start_auto_refresh(self):
        """Start auto-refresh loop"""
        import threading
        
        def refresh_loop():
            while self.auto_refresh:
                self.refresh_prices()
                time.sleep(30)
        
        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()
    
    def display(self):
        """Display the widget"""
        # FIXED: Use widgets.HTML instead of IPython.display.HTML
        header = widgets.HTML("<h3>📊 Real-time Price Tracker</h3>")
        
        controls = widgets.HBox([
            self.symbol_input,
            self.asset_type,
            self.add_btn,
            self.refresh_btn,
            self.auto_refresh_toggle
        ])
        
        display(widgets.VBox([
            header,  # Now using widgets.HTML
            controls,
            self.output
        ]))
        
        # Initial refresh if symbols exist
        if self.symbols:
            self.refresh_prices()


# ============================================
# Portfolio Value with Real-time Updates
# ============================================

class LivePortfolioWidget:
    """Portfolio widget with live price updates"""
    
    def __init__(self, db_path='data/portfolio.db'):
        self.db_path = db_path
        self.manager = MarketDataManager(db_path) if MARKET_DATA_AVAILABLE else None
        
        # Widgets
        self.portfolio_dropdown = widgets.Dropdown(
            description='Portfolio:',
            style={'description_width': 'initial'}
        )
        
        self.update_btn = widgets.Button(
            description='Update Prices',
            button_style='success',
            icon='refresh'
        )
        
        self.output = widgets.Output()
        
        # Load portfolios
        self.load_portfolios()
        
        # Event handlers
        self.update_btn.on_click(self.update_prices)
        self.portfolio_dropdown.observe(self.on_portfolio_change, 'value')
    
    def load_portfolios(self):
        """Load portfolio list"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT portfolio_id, name, currency
            FROM portfolios
            WHERE is_active = 1
            ORDER BY name
        """)
        
        portfolios = cursor.fetchall()
        conn.close()
        
        self.portfolio_dropdown.options = [
            (f"{name} ({currency})", pid) 
            for pid, name, currency in portfolios
        ]
    
    def on_portfolio_change(self, change):
        """Handle portfolio selection change"""
        self.display_portfolio()
    
    def update_prices(self, btn=None):
        """Update all prices for selected portfolio"""
        if not self.manager:
            with self.output:
                print("⚠️  Market data module not available")
            return
        
        portfolio_id = self.portfolio_dropdown.value
        
        with self.output:
            clear_output(wait=True)
            print("🔄 Updating prices...")
            
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get assets for this portfolio
            cursor.execute("""
                SELECT asset_id, symbol, asset_type
                FROM assets
                WHERE portfolio_id = ?
            """, (portfolio_id,))
            
            assets = cursor.fetchall()
            conn.close()
            
            updated = 0
            failed = 0
            
            for asset_id, symbol, asset_type in assets:
                if self.manager.update_asset_price(asset_id, symbol, asset_type):
                    updated += 1
                    print(f"  ✅ {symbol}")
                else:
                    failed += 1
                    print(f"  ❌ {symbol}")
                
                time.sleep(0.5)  # Rate limiting
            
            print()
            print(f"✅ Update complete: {updated} updated, {failed} failed")
            
            # Refresh display
            time.sleep(1)
            self.display_portfolio()
    
    def display_portfolio(self):
        """Display portfolio value and assets"""
        portfolio_id = self.portfolio_dropdown.value
        
        with self.output:
            clear_output(wait=True)
            
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            
            # Get portfolio summary
            query = """
            SELECT 
                COUNT(*) as total_assets,
                SUM(current_value) as total_value,
                SUM(cost_basis) as total_cost,
                SUM(unrealized_gain_loss) as total_gain_loss
            FROM assets
            WHERE portfolio_id = ?
            """
            
            df_summary = pd.read_sql_query(query, conn, params=(portfolio_id,))
            
            # Get asset details
            query_assets = """
            SELECT 
                symbol,
                asset_type,
                quantity,
                current_price,
                current_value,
                unrealized_gain_loss,
                updated_at
            FROM assets
            WHERE portfolio_id = ?
            ORDER BY current_value DESC
            """
            
            df_assets = pd.read_sql_query(query_assets, conn, params=(portfolio_id,))
            conn.close()
            
            # Display summary
            if not df_summary.empty:
                summary = df_summary.iloc[0]
                
                total_value = summary['total_value'] or 0
                total_cost = summary['total_cost'] or 0
                total_gain = summary['total_gain_loss'] or 0
                return_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0
                
                html = f"""
                <div style="display: flex; gap: 20px; margin: 20px 0;">
                    <div style="background: linear-gradient(135deg, #667eea, #764ba2); 
                               color: white; padding: 20px; border-radius: 10px; flex: 1;">
                        <h3 style="margin: 0;">Total Value</h3>
                        <h2 style="margin: 10px 0;">{total_value:,.0f}</h2>
                    </div>
                    <div style="background: {'#27ae60' if total_gain >= 0 else '#e74c3c'}; 
                               color: white; padding: 20px; border-radius: 10px; flex: 1;">
                        <h3 style="margin: 0;">Gain/Loss</h3>
                        <h2 style="margin: 10px 0;">{total_gain:+,.0f}</h2>
                        <p style="margin: 0; font-size: 18px;">{return_pct:+.2f}%</p>
                    </div>
                </div>
                """
                display(HTML(html))
            
            # Display assets table
            if not df_assets.empty:
                print("\n📋 Assets:")
                print(df_assets.to_string(index=False))
    
    def display(self):
        """Display the widget"""
        # FIXED: Use widgets.HTML instead of IPython.display.HTML
        header = widgets.HTML("<h3>💼 Live Portfolio Value</h3>")
        
        controls = widgets.HBox([
            self.portfolio_dropdown,
            self.update_btn
        ])
        
        display(widgets.VBox([
            header,  # Now using widgets.HTML
            controls,
            self.output
        ]))
        
        # Initial display
        if self.portfolio_dropdown.options:
            self.display_portfolio()


# ============================================
# Main Enhanced Dashboard
# ============================================

def launch_enhanced_dashboard():
    """Launch enhanced dashboard with market data"""
    
    # Header - display directly, not in VBox
    display(HTML("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">📊 Enhanced Portfolio Dashboard</h1>
        <p style="color: white; margin-top: 10px;">With Real-time Market Data Integration</p>
    </div>
    """))
    
    if not MARKET_DATA_AVAILABLE:
        display(HTML("""
        <div style="background: #fff3cd; border: 1px solid #ffc107; 
                    padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <strong>⚠️ Warning:</strong> Market data module not available. 
            Some features will be disabled. 
            Run: <code>pip install requests</code>
        </div>
        """))
    
    # Create tabs
    tab_price_tracker = widgets.Output()
    tab_portfolio = widgets.Output()
    tab_updates = widgets.Output()
    
    tabs = widgets.Tab(children=[tab_price_tracker, tab_portfolio, tab_updates])
    tabs.set_title(0, '📊 Price Tracker')
    tabs.set_title(1, '💼 Portfolio')
    tabs.set_title(2, '🔄 Updates')
    
    # Tab 1: Price Tracker
    with tab_price_tracker:
        if MARKET_DATA_AVAILABLE:
            price_widget = RealTimePriceWidget()
            
            # Add some default symbols
            price_widget.symbols = [
                ('AAPL', 'stock'),
                ('BTC', 'crypto'),
                ('VNM', 'vnstock')
            ]
            
            price_widget.display()
        else:
            print("Market data module not available")
    
    # Tab 2: Portfolio
    with tab_portfolio:
        portfolio_widget = LivePortfolioWidget()
        portfolio_widget.display()
    
    # Tab 3: Updates
    with tab_updates:
        # FIXED: Use widgets.HTML for headers inside tabs
        display(widgets.HTML("<h3>🔄 Market Data Updates</h3>"))
        
        update_all_btn = widgets.Button(
            description='Update All Prices',
            button_style='success',
            icon='refresh'
        )
        
        fetch_history_btn = widgets.Button(
            description='Fetch Historical Data',
            button_style='primary',
            icon='download'
        )
        
        update_output = widgets.Output()
        
        def update_all_prices(btn):
            with update_output:
                clear_output(wait=True)
                print("🔄 Updating all asset prices...")
                print("This may take a few minutes...")
                print()
                
                if MARKET_DATA_AVAILABLE:
                    manager = MarketDataManager()
                    result = manager.update_all_assets()
                    
                    print()
                    print("✅ Update complete!")
                    print(f"  Updated: {result['updated']}")
                    print(f"  Failed: {result['failed']}")
                else:
                    print("❌ Market data module not available")
        
        def fetch_historical_data(btn):
            with update_output:
                clear_output(wait=True)
                print("📥 Fetching historical data...")
                print("This may take several minutes...")
                print()
                
                if MARKET_DATA_AVAILABLE:
                    from module_market_data import fetch_and_save_all_symbols
                    fetch_and_save_all_symbols()
                else:
                    print("❌ Market data module not available")
        
        update_all_btn.on_click(update_all_prices)
        fetch_history_btn.on_click(fetch_historical_data)
        
        display(widgets.HBox([update_all_btn, fetch_history_btn]))
        display(update_output)
    
    # Display tabs
    display(tabs)
    
    # Footer - display directly, not in VBox
    display(HTML("""
    <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; 
                border-radius: 5px; text-align: center;">
        <p style="margin: 0; color: #6c757d;">
            💡 <strong>Tip:</strong> Enable auto-refresh in Price Tracker for real-time monitoring
        </p>
    </div>
    """))


# ============================================
# Standalone widgets for Jupyter
# ============================================

def show_price_tracker():
    """Standalone price tracker widget"""
    if MARKET_DATA_AVAILABLE:
        widget = RealTimePriceWidget()
        widget.display()
    else:
        print("❌ Market data module not available")

def show_live_portfolio():
    """Standalone live portfolio widget"""
    widget = LivePortfolioWidget()
    widget.display()


# ============================================
# Quick commands
# ============================================

print("✅ Enhanced dashboard module loaded!")
print()
print("Available commands:")
print("  launch_enhanced_dashboard()  - Full enhanced dashboard")
print("  show_price_tracker()         - Price tracker only")
print("  show_live_portfolio()        - Live portfolio only")
print()
