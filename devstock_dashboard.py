# -*- coding: utf-8 -*-
"""
Portfolio Management Dashboard
===============================
Interactive dashboard cho Jupyter Lab
Platform: Jetson Nano
Libraries: Plotly, Matplotlib, Seaborn, ipywidgets
"""

# ============================================
# CELL 1: Import Libraries
# ============================================

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Plotting libraries
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Interactive widgets
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

# Custom styling
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("✓ All libraries imported successfully!")


# ============================================
# CELL 2: Database Connection & Helper Functions
# ============================================

class DashboardData:
    """Class để load và cache dữ liệu từ database"""
    
    def __init__(self, db_path='data/portfolio.db'):
        self.db_path = db_path
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Kết nối database"""
        import os
        
        # Check if database file exists
        if not os.path.exists(self.db_path):
            print(f"✗ Database file not found: {self.db_path}")
            print(f"✗ Current directory: {os.getcwd()}")
            print(f"✗ Please run initialize_database.py first!")
            return
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            print(f"✓ Connected to database: {self.db_path}")
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            import traceback
            traceback.print_exc()
    
    def is_connected(self):
        """Check if database is connected"""
        return self.conn is not None
    
    def get_portfolios(self):
        """Lấy danh sách portfolios"""
        query = """
        SELECT portfolio_id, name, currency, current_value, 
               initial_value, updated_at
        FROM portfolios 
        WHERE is_active = 1
        ORDER BY name
        """
        return pd.read_sql_query(query, self.conn)
    
    def get_assets(self, portfolio_id=None):
        """Lấy danh sách assets"""
        query = """
        SELECT a.*, p.name as portfolio_name
        FROM assets a
        JOIN portfolios p ON a.portfolio_id = p.portfolio_id
        WHERE 1=1
        """
        params = []
        
        if portfolio_id:
            query += " AND a.portfolio_id = ?"
            params.append(portfolio_id)
        
        if params:
            return pd.read_sql_query(query, self.conn, params=params)
        return pd.read_sql_query(query, self.conn)
    
    def get_transactions(self, portfolio_id=None, days=90):
        """Lấy lịch sử transactions"""
        query = """
        SELECT t.*, p.name as portfolio_name
        FROM transactions t
        JOIN portfolios p ON t.portfolio_id = p.portfolio_id
        WHERE t.transaction_date >= date('now', '-' || ? || ' days')
        """
        params = [days]
        
        if portfolio_id:
            query += " AND t.portfolio_id = ?"
            params.append(portfolio_id)
        
        query += " ORDER BY t.transaction_date DESC"
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_portfolio_snapshots(self, portfolio_id, days=365):
        """Lấy historical portfolio values"""
        query = """
        SELECT snapshot_date, total_value, total_gain_loss,
               total_gain_loss_percent, daily_return
        FROM portfolio_snapshots
        WHERE portfolio_id = ?
        AND snapshot_date >= date('now', '-' || ? || ' days')
        ORDER BY snapshot_date
        """
        return pd.read_sql_query(query, self.conn, params=[portfolio_id, days])
    
    def get_asset_allocation(self, portfolio_id):
        """Lấy phân bổ tài sản hiện tại"""
        query = """
        SELECT asset_type,
               SUM(current_value) as total_value,
               COUNT(*) as count
        FROM assets
        WHERE portfolio_id = ?
        GROUP BY asset_type
        ORDER BY total_value DESC
        """
        return pd.read_sql_query(query, self.conn, params=[portfolio_id])
    
    def get_sector_allocation(self, portfolio_id):
        """Lấy phân bổ theo sector"""
        query = """
        SELECT COALESCE(sector, 'Other') as sector,
               SUM(current_value) as total_value,
               COUNT(*) as count
        FROM assets
        WHERE portfolio_id = ?
        GROUP BY sector
        ORDER BY total_value DESC
        """
        return pd.read_sql_query(query, self.conn, params=[portfolio_id])
    
    def get_performance_summary(self, portfolio_id):
        """Tính toán performance metrics"""
        query = """
        SELECT 
            COUNT(*) as total_assets,
            SUM(current_value) as total_value,
            SUM(cost_basis) as total_cost,
            SUM(unrealized_gain_loss) as total_gain_loss,
            CASE 
                WHEN SUM(cost_basis) > 0 
                THEN (SUM(unrealized_gain_loss) / SUM(cost_basis)) * 100 
                ELSE 0 
            END as return_percent
        FROM assets
        WHERE portfolio_id = ?
        """
        return pd.read_sql_query(query, self.conn, params=[portfolio_id])
    
    def close(self):
        """Đóng connection"""
        if self.conn:
            self.conn.close()

# Initialize data loader
data = DashboardData()
print("✓ Dashboard data loader ready!")


# ============================================
# CELL 3: Styling & Configuration
# ============================================

# Custom CSS for better styling
dashboard_css = """
<style>
    .dashboard-title {
        font-size: 32px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 14px;
        color: #7f8c8d;
        margin-top: 5px;
    }
    .positive {
        color: #27ae60;
    }
    .negative {
        color: #e74c3c;
    }
</style>
"""

display(HTML(dashboard_css))

# Plotly theme configuration
plotly_template = "plotly_white"
color_palette = px.colors.qualitative.Set3

print("✓ Styling configured!")


# ============================================
# CELL 4: KPI Cards Function
# ============================================

def display_kpi_cards(portfolio_id):
    """
    Hiển thị KPI cards với metrics chính
    """
    # Get performance summary
    perf = data.get_performance_summary(portfolio_id)
    
    if perf.empty:
        print("No data available for this portfolio")
        return
    
    perf = perf.iloc[0]
    
    # Format numbers
    total_value = f"{perf['total_value']:,.0f}"
    total_cost = f"{perf['total_cost']:,.0f}"
    gain_loss = f"{perf['total_gain_loss']:,.0f}"
    return_pct = f"{perf['return_percent']:.2f}%"
    
    # Determine color for gain/loss
    gain_color = 'positive' if perf['total_gain_loss'] >= 0 else 'negative'
    
    # Create HTML for KPI cards
    kpi_html = f"""
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
        <div class="metric-card">
            <div class="metric-value">{total_value}</div>
            <div class="metric-label">Current Value (VND)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{total_cost}</div>
            <div class="metric-label">Total Cost (VND)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value {gain_color}">{gain_loss}</div>
            <div class="metric-label">Gain/Loss (VND)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value {gain_color}">{return_pct}</div>
            <div class="metric-label">Return (%)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{int(perf['total_assets'])}</div>
            <div class="metric-label">Total Assets</div>
        </div>
    </div>
    """
    
    display(HTML(kpi_html))

print("✓ KPI cards function ready!")


# ============================================
# CELL 5: Portfolio Value Over Time Chart
# ============================================

def plot_portfolio_value_trend(portfolio_id, days=365):
    """
    Biểu đồ giá trị portfolio theo thời gian
    """
    # Get snapshot data
    snapshots = data.get_portfolio_snapshots(portfolio_id, days)
    
    if snapshots.empty:
        print("No historical data available")
        return
    
    # Convert date column
    snapshots['snapshot_date'] = pd.to_datetime(snapshots['snapshot_date'])
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Portfolio Value Over Time', 'Daily Return (%)'),
        row_heights=[0.7, 0.3]
    )
    
    # Portfolio value line
    fig.add_trace(
        go.Scatter(
            x=snapshots['snapshot_date'],
            y=snapshots['total_value'],
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#667eea', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ),
        row=1, col=1
    )
    
    # Daily return bar chart
    if 'daily_return' in snapshots.columns:
        colors = ['green' if x >= 0 else 'red' for x in snapshots['daily_return']]
        fig.add_trace(
            go.Bar(
                x=snapshots['snapshot_date'],
                y=snapshots['daily_return'],
                name='Daily Return',
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        height=700,
        template=plotly_template,
        hovermode='x unified',
        showlegend=True,
        title_text="Portfolio Performance Dashboard",
        title_font_size=20
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Value (VND)", row=1, col=1)
    fig.update_yaxes(title_text="Return (%)", row=2, col=1)
    
    fig.show()

print("✓ Portfolio value trend function ready!")


# ============================================
# CELL 6: Asset Allocation Pie Chart
# ============================================

def plot_asset_allocation(portfolio_id):
    """
    Pie chart phân bổ tài sản theo loại
    """
    allocation = data.get_asset_allocation(portfolio_id)
    
    if allocation.empty:
        print("No allocation data available")
        return
    
    # Calculate percentages
    allocation['percentage'] = (allocation['total_value'] / 
                                allocation['total_value'].sum() * 100)
    
    # Create subplots: 1 row, 2 columns
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type':'pie'}, {'type':'pie'}]],
        subplot_titles=('Asset Type Allocation', 'Sector Allocation')
    )
    
    # Asset type pie chart
    fig.add_trace(
        go.Pie(
            labels=allocation['asset_type'],
            values=allocation['total_value'],
            text=[f"{x:.1f}%" for x in allocation['percentage']],
            textinfo='label+text',
            textposition='inside',
            hole=0.4,
            marker=dict(colors=color_palette),
            hovertemplate='<b>%{label}</b><br>' +
                         'Value: %{value:,.0f} VND<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Sector allocation
    sector_data = data.get_sector_allocation(portfolio_id)
    if not sector_data.empty:
        sector_data['percentage'] = (sector_data['total_value'] / 
                                     sector_data['total_value'].sum() * 100)
        
        fig.add_trace(
            go.Pie(
                labels=sector_data['sector'],
                values=sector_data['total_value'],
                text=[f"{x:.1f}%" for x in sector_data['percentage']],
                textinfo='label+text',
                textposition='inside',
                hole=0.4,
                marker=dict(colors=color_palette),
                hovertemplate='<b>%{label}</b><br>' +
                             'Value: %{value:,.0f} VND<br>' +
                             'Percentage: %{percent}<br>' +
                             '<extra></extra>'
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        height=500,
        template=plotly_template,
        showlegend=True,
        title_text="Portfolio Allocation Analysis",
        title_font_size=20
    )
    
    fig.show()

print("✓ Asset allocation chart function ready!")


# ============================================
# CELL 7: Gain/Loss by Asset Chart
# ============================================

def plot_asset_performance(portfolio_id, top_n=15):
    """
    Biểu đồ lãi/lỗ theo từng tài sản
    """
    assets = data.get_assets(portfolio_id)
    
    if assets.empty:
        print("No assets found")
        return
    
    # Calculate return percentage
    assets['return_pct'] = (assets['unrealized_gain_loss'] / 
                           assets['cost_basis'] * 100)
    
    # Sort by absolute gain/loss and take top N
    assets_sorted = assets.reindex(
        assets['unrealized_gain_loss'].abs().sort_values(ascending=False).index
    ).head(top_n)
    
    # Create figure with two subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Gain/Loss by Asset (VND)', 'Return by Asset (%)'),
        horizontal_spacing=0.15
    )
    
    # Determine colors
    colors = ['green' if x >= 0 else 'red' 
              for x in assets_sorted['unrealized_gain_loss']]
    
    # Bar chart 1: Absolute gain/loss
    fig.add_trace(
        go.Bar(
            y=assets_sorted['symbol'],
            x=assets_sorted['unrealized_gain_loss'],
            orientation='h',
            marker_color=colors,
            text=assets_sorted['unrealized_gain_loss'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                         'Gain/Loss: %{x:,.0f} VND<br>' +
                         '<extra></extra>',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Bar chart 2: Return percentage
    colors_pct = ['green' if x >= 0 else 'red' 
                  for x in assets_sorted['return_pct']]
    
    fig.add_trace(
        go.Bar(
            y=assets_sorted['symbol'],
            x=assets_sorted['return_pct'],
            orientation='h',
            marker_color=colors_pct,
            text=assets_sorted['return_pct'].apply(lambda x: f'{x:.1f}%'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                         'Return: %{x:.2f}%<br>' +
                         '<extra></extra>',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=max(400, top_n * 30),
        template=plotly_template,
        title_text="Asset Performance Analysis",
        title_font_size=20
    )
    
    fig.update_xaxes(title_text="Gain/Loss (VND)", row=1, col=1)
    fig.update_xaxes(title_text="Return (%)", row=1, col=2)
    fig.update_yaxes(title_text="", row=1, col=1)
    fig.update_yaxes(title_text="", row=1, col=2)
    
    fig.show()

print("✓ Asset performance chart function ready!")


# ============================================
# CELL 8: Asset Details Table
# ============================================

def display_asset_table(portfolio_id):
    """
    Hiển thị bảng chi tiết assets
    """
    assets = data.get_assets(portfolio_id)
    
    if assets.empty:
        print("No assets found")
        return
    
    # Select relevant columns
    display_cols = ['symbol', 'asset_type', 'quantity', 'purchase_price', 
                    'current_price', 'current_value', 'cost_basis', 
                    'unrealized_gain_loss']
    
    assets_display = assets[display_cols].copy()
    
    # Calculate return percentage
    assets_display['return_pct'] = (assets['unrealized_gain_loss'] / 
                                    assets['cost_basis'] * 100)
    
    # Rename columns
    assets_display.columns = ['Symbol', 'Type', 'Quantity', 'Buy Price', 
                              'Current Price', 'Current Value', 'Cost', 
                              'Gain/Loss', 'Return %']
    
    # Format numbers
    format_dict = {
        'Quantity': '{:,.4f}',
        'Buy Price': '{:,.2f}',
        'Current Price': '{:,.2f}',
        'Current Value': '{:,.0f}',
        'Cost': '{:,.0f}',
        'Gain/Loss': '{:,.0f}',
        'Return %': '{:,.2f}'
    }
    
    # Sort by gain/loss
    assets_display = assets_display.sort_values('Gain/Loss', ascending=False)
    
    # Style the dataframe
    styled_df = assets_display.style\
        .format(format_dict)\
        .background_gradient(subset=['Gain/Loss'], cmap='RdYlGn', vmin=-1000000, vmax=1000000)\
        .background_gradient(subset=['Return %'], cmap='RdYlGn', vmin=-50, vmax=50)\
        .set_properties(**{'text-align': 'right'})\
        .set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#667eea'), 
                                         ('color', 'white'), 
                                         ('font-weight', 'bold'),
                                         ('text-align', 'center')]}
        ])
    
    display(styled_df)

print("✓ Asset table function ready!")


# ============================================
# CELL 9: Transaction History Chart
# ============================================

def plot_transaction_history(portfolio_id, days=90):
    """
    Biểu đồ lịch sử giao dịch
    """
    transactions = data.get_transactions(portfolio_id, days)
    
    if transactions.empty:
        print("No transactions found")
        return
    
    # Convert date
    transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])
    
    # Aggregate by date and type
    daily_trans = transactions.groupby(
        ['transaction_date', 'transaction_type']
    )['net_amount'].sum().reset_index()
    
    # Create figure
    fig = go.Figure()
    
    # Add trace for each transaction type
    for trans_type in daily_trans['transaction_type'].unique():
        data_subset = daily_trans[daily_trans['transaction_type'] == trans_type]
        
        fig.add_trace(
            go.Bar(
                x=data_subset['transaction_date'],
                y=data_subset['net_amount'],
                name=trans_type.capitalize(),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>' +
                             f'{trans_type}: %{{y:,.0f}} VND<br>' +
                             '<extra></extra>'
            )
        )
    
    # Update layout
    fig.update_layout(
        height=400,
        template=plotly_template,
        title_text=f"Transaction History (Last {days} Days)",
        title_font_size=20,
        barmode='stack',
        xaxis_title="Date",
        yaxis_title="Amount (VND)",
        hovermode='x unified'
    )
    
    fig.show()

print("✓ Transaction history chart function ready!")


# ============================================
# CELL 10: Interactive Dashboard with Widgets
# ============================================

def create_interactive_dashboard():
    """
    Tạo dashboard tương tác với widgets
    """
    # Get portfolios
    portfolios = data.get_portfolios()
    
    if portfolios.empty:
        print("No portfolios found. Please create a portfolio first.")
        return
    
    # Create widgets
    portfolio_dropdown = widgets.Dropdown(
        options=[(row['name'], row['portfolio_id']) 
                 for _, row in portfolios.iterrows()],
        description='Portfolio:',
        style={'description_width': 'initial'}
    )
    
    time_range = widgets.Dropdown(
        options=[('1 Month', 30), ('3 Months', 90), ('6 Months', 180), 
                 ('1 Year', 365), ('All Time', 3650)],
        value=365,
        description='Time Range:',
        style={'description_width': 'initial'}
    )
    
    top_n_slider = widgets.IntSlider(
        value=10,
        min=5,
        max=20,
        step=1,
        description='Top Assets:',
        style={'description_width': 'initial'}
    )
    
    refresh_button = widgets.Button(
        description='🔄 Refresh Dashboard',
        button_style='info',
        tooltip='Click to refresh data',
        icon='refresh'
    )
    
    output = widgets.Output()
    
    def update_dashboard(change=None):
        """Update all charts"""
        with output:
            clear_output(wait=True)
            
            portfolio_id = portfolio_dropdown.value
            days = time_range.value
            top_n = top_n_slider.value
            
            # Title
            display(HTML('<div class="dashboard-title">📊 Portfolio Management Dashboard</div>'))
            
            # KPI Cards
            display(HTML('<h2>📈 Key Performance Indicators</h2>'))
            display_kpi_cards(portfolio_id)
            
            # Portfolio value trend
            display(HTML('<h2>💰 Portfolio Value Trend</h2>'))
            plot_portfolio_value_trend(portfolio_id, days)
            
            # Asset allocation
            display(HTML('<h2>🥧 Asset Allocation</h2>'))
            plot_asset_allocation(portfolio_id)
            
            # Asset performance
            display(HTML('<h2>📊 Top Assets Performance</h2>'))
            plot_asset_performance(portfolio_id, top_n)
            
            # Transaction history
            display(HTML('<h2>💳 Transaction History</h2>'))
            plot_transaction_history(portfolio_id, min(days, 90))
            
            # Asset details table
            display(HTML('<h2>📋 Asset Details</h2>'))
            display_asset_table(portfolio_id)
            
            print("\n✓ Dashboard updated successfully!")
    
    # Attach event handlers
    portfolio_dropdown.observe(update_dashboard, 'value')
    time_range.observe(update_dashboard, 'value')
    top_n_slider.observe(update_dashboard, 'value')
    refresh_button.on_click(update_dashboard)
    
    # Layout
    controls = widgets.HBox([portfolio_dropdown, time_range, top_n_slider, refresh_button])
    dashboard = widgets.VBox([controls, output])
    
    display(dashboard)
    
    # Initial update
    update_dashboard()

print("✓ Interactive dashboard function ready!")
print("\n" + "="*60)
print("🎉 Dashboard is ready! Run the next cell to launch it.")
print("="*60)


# ============================================
# CELL 11: Launch Dashboard
# ============================================

# Uncomment below to launch the dashboard
# create_interactive_dashboard()


# ============================================
# CELL 12: Optional - Matplotlib Static Charts
# ============================================

def create_static_dashboard(portfolio_id):
    """
    Tạo dashboard tĩnh với Matplotlib (cho export)
    """
    # Set up the figure
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Get data
    assets = data.get_assets(portfolio_id)
    allocation = data.get_asset_allocation(portfolio_id)
    snapshots = data.get_portfolio_snapshots(portfolio_id, 365)
    
    # 1. Portfolio Value Line Chart
    ax1 = fig.add_subplot(gs[0, :])
    if not snapshots.empty:
        snapshots['snapshot_date'] = pd.to_datetime(snapshots['snapshot_date'])
        ax1.plot(snapshots['snapshot_date'], snapshots['total_value'], 
                linewidth=2, color='#667eea', marker='o', markersize=4)
        ax1.fill_between(snapshots['snapshot_date'], snapshots['total_value'], 
                         alpha=0.3, color='#667eea')
        ax1.set_title('Portfolio Value Over Time', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Value (VND)')
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
    
    # 2. Asset Allocation Pie Chart
    ax2 = fig.add_subplot(gs[1, 0])
    if not allocation.empty:
        colors_pie = sns.color_palette("husl", len(allocation))
        wedges, texts, autotexts = ax2.pie(
            allocation['total_value'], 
            labels=allocation['asset_type'],
            autopct='%1.1f%%',
            colors=colors_pie,
            startangle=90
        )
        ax2.set_title('Asset Type Allocation', fontsize=14, fontweight='bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    # 3. Top 10 Assets by Value
    ax3 = fig.add_subplot(gs[1, 1:])
    if not assets.empty:
        top_assets = assets.nlargest(10, 'current_value')
        colors_bar = ['green' if x >= 0 else 'red' 
                      for x in top_assets['unrealized_gain_loss']]
        ax3.barh(top_assets['symbol'], top_assets['current_value'], color=colors_bar, alpha=0.7)
        ax3.set_title('Top 10 Assets by Value', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Current Value (VND)')
        ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        ax3.grid(axis='x', alpha=0.3)
    
    # 4. Gain/Loss Distribution
    ax4 = fig.add_subplot(gs[2, 0])
    if not assets.empty:
        gains = assets[assets['unrealized_gain_loss'] >= 0]['unrealized_gain_loss']
        losses = assets[assets['unrealized_gain_loss'] < 0]['unrealized_gain_loss']
        
        ax4.hist([gains, losses], bins=20, color=['green', 'red'], 
                alpha=0.7, label=['Gains', 'Losses'])
        ax4.set_title('Gain/Loss Distribution', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Gain/Loss (VND)')
        ax4.set_ylabel('Frequency')
        ax4.legend()
        ax4.grid(axis='y', alpha=0.3)
    
    # 5. Return Percentage Box Plot
    ax5 = fig.add_subplot(gs[2, 1])
    if not assets.empty:
        assets['return_pct'] = (assets['unrealized_gain_loss'] / 
                               assets['cost_basis'] * 100)
        by_type = [assets[assets['asset_type'] == t]['return_pct'].dropna() 
                   for t in assets['asset_type'].unique()]
        bp = ax5.boxplot(by_type, labels=assets['asset_type'].unique(), 
                        patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('#667eea')
            patch.set_alpha(0.7)
        ax5.set_title('Return % by Asset Type', fontsize=14, fontweight='bold')
        ax5.set_ylabel('Return (%)')
        ax5.grid(axis='y', alpha=0.3)
        ax5.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    
    # 6. Performance Summary Text
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis('off')
    
    if not assets.empty:
        total_value = assets['current_value'].sum()
        total_cost = assets['cost_basis'].sum()
        total_gain_loss = assets['unrealized_gain_loss'].sum()
        return_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        summary_text = f"""
        PORTFOLIO SUMMARY
        ==================
        
        Total Assets: {len(assets)}
        
        Current Value:
        {total_value:,.0f} VND
        
        Total Cost:
        {total_cost:,.0f} VND
        
        Gain/Loss:
        {total_gain_loss:,.0f} VND
        
        Return:
        {return_pct:.2f}%
        
        Best Performer:
        {assets.nlargest(1, 'return_pct')['symbol'].values[0]}
        
        Worst Performer:
        {assets.nsmallest(1, 'return_pct')['symbol'].values[0]}
        """
        
        ax6.text(0.1, 0.5, summary_text, fontsize=12, 
                verticalalignment='center', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('📊 Portfolio Dashboard - Static Report', 
                fontsize=20, fontweight='bold', y=0.98)
    
    return fig

print("✓ Static dashboard function ready!")


# ============================================
# CELL 13: Advanced Analytics - Correlation Matrix
# ============================================

def plot_correlation_matrix(portfolio_id):
    """
    Heatmap correlation giữa các assets
    (Requires historical price data)
    """
    try:
        assets = data.get_assets(portfolio_id)
        
        if assets.empty or len(assets) < 2:
            print("Need at least 2 assets for correlation analysis")
            return
        
        # Get market data history for each symbol
        symbols = assets['symbol'].unique()[:15]  # Limit to 15 for readability
        
        # Placeholder: In real implementation, fetch historical prices
        # For now, create sample correlation based on returns
        returns_data = {}
        for symbol in symbols:
            asset = assets[assets['symbol'] == symbol].iloc[0]
            # Simulate returns distribution
            np.random.seed(hash(symbol) % 2**32)
            returns_data[symbol] = np.random.normal(
                asset['unrealized_gain_loss'] / asset['cost_basis'] * 100,
                10,
                100
            )
        
        returns_df = pd.DataFrame(returns_data)
        correlation = returns_df.corr()
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        
        mask = np.triu(np.ones_like(correlation, dtype=bool))
        
        sns.heatmap(correlation, mask=mask, annot=True, fmt='.2f',
                   cmap='RdYlGn', center=0, square=True,
                   linewidths=1, cbar_kws={"shrink": 0.8})
        
        plt.title('Asset Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.show()
        
        print("✓ Correlation matrix displayed")
        print("ℹ️  Note: This uses simulated data. Connect to market_data_history for real correlations.")
        
    except Exception as e:
        print(f"Error creating correlation matrix: {e}")

print("✓ Correlation matrix function ready!")


# ============================================
# CELL 14: Risk Analysis - Volatility & Sharpe Ratio
# ============================================

def calculate_portfolio_metrics(portfolio_id):
    """
    Tính toán các metrics rủi ro và hiệu suất
    """
    try:
        snapshots = data.get_portfolio_snapshots(portfolio_id, 365)
        
        if snapshots.empty:
            print("No historical data for risk calculation")
            return None
        
        # Convert to datetime
        snapshots['snapshot_date'] = pd.to_datetime(snapshots['snapshot_date'])
        snapshots = snapshots.sort_values('snapshot_date')
        
        # Calculate daily returns if not present
        if 'daily_return' not in snapshots.columns:
            snapshots['daily_return'] = snapshots['total_value'].pct_change() * 100
        
        # Drop NaN
        returns = snapshots['daily_return'].dropna()
        
        if len(returns) == 0:
            print("Insufficient data for metrics calculation")
            return None
        
        # Calculate metrics
        avg_return = returns.mean()
        volatility = returns.std()
        
        # Annualize
        annual_return = avg_return * 252  # 252 trading days
        annual_volatility = volatility * np.sqrt(252)
        
        # Sharpe Ratio (assuming 3% risk-free rate)
        risk_free_rate = 3.0
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # Sortino Ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252)
        sortino_ratio = (annual_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
        
        # Maximum Drawdown
        cumulative = (1 + returns / 100).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns, 5)
        
        # Conditional VaR (Expected Shortfall)
        cvar_95 = returns[returns <= var_95].mean()
        
        metrics = {
            'Average Daily Return (%)': avg_return,
            'Daily Volatility (%)': volatility,
            'Annual Return (%)': annual_return,
            'Annual Volatility (%)': annual_volatility,
            'Sharpe Ratio': sharpe_ratio,
            'Sortino Ratio': sortino_ratio,
            'Max Drawdown (%)': max_drawdown,
            'VaR 95% (%)': var_95,
            'CVaR 95% (%)': cvar_95,
            'Best Day (%)': returns.max(),
            'Worst Day (%)': returns.min()
        }
        
        return metrics, returns, drawdown
        
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return None

def display_risk_dashboard(portfolio_id):
    """
    Dashboard phân tích rủi ro
    """
    result = calculate_portfolio_metrics(portfolio_id)
    
    if result is None:
        return
    
    metrics, returns, drawdown = result
    
    # Create figure
    fig = plt.figure(figsize=(20, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # 1. Metrics Table
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    
    metrics_text = "RISK METRICS\n" + "="*30 + "\n\n"
    for key, value in metrics.items():
        metrics_text += f"{key}:\n  {value:.2f}\n\n"
    
    ax1.text(0.1, 0.5, metrics_text, fontsize=11, 
            verticalalignment='center', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    # 2. Return Distribution
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(returns, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    ax2.axvline(returns.mean(), color='red', linestyle='--', 
               linewidth=2, label=f'Mean: {returns.mean():.2f}%')
    ax2.axvline(metrics['VaR 95% (%)'], color='orange', linestyle='--',
               linewidth=2, label=f'VaR 95%: {metrics["VaR 95% (%)"]:.2f}%')
    ax2.set_title('Daily Returns Distribution', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Daily Return (%)')
    ax2.set_ylabel('Frequency')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    # 3. Q-Q Plot
    ax3 = fig.add_subplot(gs[0, 2])
    from scipy import stats
    stats.probplot(returns, dist="norm", plot=ax3)
    ax3.set_title('Q-Q Plot (Normality Check)', fontsize=14, fontweight='bold')
    ax3.grid(alpha=0.3)
    
    # 4. Drawdown Chart
    ax4 = fig.add_subplot(gs[1, :])
    snapshots = data.get_portfolio_snapshots(portfolio_id, 365)
    snapshots['snapshot_date'] = pd.to_datetime(snapshots['snapshot_date'])
    
    ax4.fill_between(range(len(drawdown)), drawdown, 0, 
                     color='red', alpha=0.3, label='Drawdown')
    ax4.plot(drawdown, color='darkred', linewidth=2)
    ax4.axhline(metrics['Max Drawdown (%)'], color='red', 
               linestyle='--', linewidth=2,
               label=f'Max Drawdown: {metrics["Max Drawdown (%)"]:.2f}%')
    ax4.set_title('Portfolio Drawdown Over Time', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Days')
    ax4.set_ylabel('Drawdown (%)')
    ax4.legend()
    ax4.grid(alpha=0.3)
    
    plt.suptitle('📉 Risk Analysis Dashboard', fontsize=20, fontweight='bold')
    plt.show()

print("✓ Risk analysis functions ready!")


# ============================================
# CELL 15: Export Dashboard to HTML/PDF
# ============================================

def export_dashboard_html(portfolio_id, filename='dashboard_export.html'):
    """
    Export dashboard to HTML file
    """
    try:
        from plotly.offline import plot
        
        # Create all charts
        figs = []
        
        # Portfolio value trend
        snapshots = data.get_portfolio_snapshots(portfolio_id, 365)
        if not snapshots.empty:
            snapshots['snapshot_date'] = pd.to_datetime(snapshots['snapshot_date'])
            
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=snapshots['snapshot_date'],
                y=snapshots['total_value'],
                mode='lines+markers',
                name='Portfolio Value',
                line=dict(color='#667eea', width=3)
            ))
            fig1.update_layout(title='Portfolio Value Over Time', height=400)
            figs.append(fig1)
        
        # Asset allocation
        allocation = data.get_asset_allocation(portfolio_id)
        if not allocation.empty:
            fig2 = go.Figure(data=[go.Pie(
                labels=allocation['asset_type'],
                values=allocation['total_value'],
                hole=0.4
            )])
            fig2.update_layout(title='Asset Allocation', height=400)
            figs.append(fig2)
        
        # Generate HTML
        html_content = """
        <html>
        <head>
            <title>Portfolio Dashboard Export</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #667eea; text-align: center; }
                .chart { margin: 30px 0; }
            </style>
        </head>
        <body>
            <h1>📊 Portfolio Dashboard Export</h1>
            <p style="text-align: center; color: #7f8c8d;">
                Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
            </p>
        """
        
        for i, fig in enumerate(figs):
            html_content += f'<div class="chart">{plot(fig, output_type="div", include_plotlyjs="cdn")}</div>'
        
        html_content += """
        </body>
        </html>
        """
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Dashboard exported to: {filename}")
        
    except Exception as e:
        print(f"Error exporting dashboard: {e}")

print("✓ Export functions ready!")


# ============================================
# CELL 16: Real-time Updates (Simulation)
# ============================================

def create_realtime_dashboard(portfolio_id, update_interval=5):
    """
    Dashboard với real-time updates (simulation)
    """
    import time
    from IPython.display import clear_output
    
    print("🔄 Real-time Dashboard Started")
    print("Press 'Interrupt Kernel' to stop")
    print("-" * 50)
    
    try:
        iteration = 0
        while True:
            clear_output(wait=True)
            
            # Display header
            print("="*60)
            print(f"🔴 LIVE DASHBOARD - Update #{iteration + 1}")
            print(f"⏰ Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            print()
            
            # Get fresh data
            perf = data.get_performance_summary(portfolio_id)
            
            if not perf.empty:
                perf = perf.iloc[0]
                
                print(f"💰 Total Value:     {perf['total_value']:>15,.0f} VND")
                print(f"💵 Total Cost:      {perf['total_cost']:>15,.0f} VND")
                print(f"📊 Gain/Loss:       {perf['total_gain_loss']:>15,.0f} VND")
                print(f"📈 Return:          {perf['return_percent']:>15.2f} %")
                print(f"🎯 Total Assets:    {int(perf['total_assets']):>15}")
                
                # Simple price movement simulation
                price_change = np.random.uniform(-0.5, 0.5)
                arrow = "📈" if price_change > 0 else "📉"
                print(f"\n{arrow} Simulated Price Change: {price_change:+.2f}%")
            
            print("\n" + "-"*60)
            print(f"Next update in {update_interval} seconds...")
            
            iteration += 1
            time.sleep(update_interval)
            
    except KeyboardInterrupt:
        print("\n\n✓ Real-time dashboard stopped")

print("✓ Real-time dashboard function ready!")


# ============================================
# CELL 17: Custom Widget - Portfolio Selector
# ============================================

class PortfolioSelector:
    """
    Custom widget class for portfolio selection with advanced features
    """
    
    def __init__(self, data_loader):
        self.data = data_loader
        self.selected_portfolio = None
        
        # Create widgets
        self.portfolio_dropdown = widgets.Dropdown(
            description='Portfolio:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='300px')
        )
        
        self.refresh_btn = widgets.Button(
            description='🔄 Refresh',
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        
        self.info_output = widgets.Output()
        
        # Load portfolios
        self.refresh_portfolios()
        
        # Attach handlers
        self.portfolio_dropdown.observe(self.on_portfolio_change, 'value')
        self.refresh_btn.on_click(self.refresh_portfolios)
    
    def refresh_portfolios(self, btn=None):
        """Refresh portfolio list"""
        portfolios = self.data.get_portfolios()
        
        if not portfolios.empty:
            options = [(f"{row['name']} ({row['currency']})", row['portfolio_id']) 
                      for _, row in portfolios.iterrows()]
            self.portfolio_dropdown.options = options
            
            if len(options) > 0:
                self.selected_portfolio = options[0][1]
        
        with self.info_output:
            clear_output()
            print(f"✓ Loaded {len(portfolios)} portfolios")
    
    def on_portfolio_change(self, change):
        """Handle portfolio selection change"""
        self.selected_portfolio = change['new']
        with self.info_output:
            clear_output()
            print(f"✓ Selected portfolio ID: {self.selected_portfolio}")
    
    def display(self):
        """Display the widget"""
        container = widgets.VBox([
            widgets.HBox([self.portfolio_dropdown, self.refresh_btn]),
            self.info_output
        ])
        display(container)
    
    def get_selected_id(self):
        """Get currently selected portfolio ID"""
        return self.selected_portfolio

print("✓ Custom portfolio selector widget ready!")


# ============================================
# CELL 18: Complete Dashboard Launcher
# ============================================

def launch_complete_dashboard():
    """
    Launch the complete interactive dashboard with all features
    """
    # Title
    display(HTML("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px; border-radius: 15px; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 36px;">
            📊 Portfolio Management Dashboard
        </h1>
        <p style="color: white; margin-top: 10px; font-size: 16px;">
            Professional-grade portfolio analytics for Jupyter Lab
        </p>
    </div>
    """))
    
    # Create portfolio selector
    selector = PortfolioSelector(data)
    selector.display()
    
    # Create tabs for different views
    tab_contents = []
    tab_titles = ['📈 Overview', '🥧 Allocation', '📊 Performance', 
                  '📉 Risk', '💳 Transactions']
    
    for title in tab_titles:
        tab_contents.append(widgets.Output())
    
    tabs = widgets.Tab(children=tab_contents)
    for i, title in enumerate(tab_titles):
        tabs.set_title(i, title)
    
    # Update button
    update_btn = widgets.Button(
        description='🔄 Update All Views',
        button_style='success',
        layout=widgets.Layout(width='200px', height='40px')
    )
    
    def update_all_views(btn=None):
        """Update all dashboard views"""
        portfolio_id = selector.get_selected_id()
        
        if portfolio_id is None:
            print("Please select a portfolio first")
            return
        
        # Tab 0: Overview
        with tab_contents[0]:
            clear_output(wait=True)
            display(HTML('<h2>📈 Portfolio Overview</h2>'))
            display_kpi_cards(portfolio_id)
            plot_portfolio_value_trend(portfolio_id, 365)
        
        # Tab 1: Allocation
        with tab_contents[1]:
            clear_output(wait=True)
            display(HTML('<h2>🥧 Asset Allocation Analysis</h2>'))
            plot_asset_allocation(portfolio_id)
            display_asset_table(portfolio_id)
        
        # Tab 2: Performance
        with tab_contents[2]:
            clear_output(wait=True)
            display(HTML('<h2>📊 Performance Analysis</h2>'))
            plot_asset_performance(portfolio_id, 15)
        
        # Tab 3: Risk
        with tab_contents[3]:
            clear_output(wait=True)
            display(HTML('<h2>📉 Risk Analysis</h2>'))
            display_risk_dashboard(portfolio_id)
        
        # Tab 4: Transactions
        with tab_contents[4]:
            clear_output(wait=True)
            display(HTML('<h2>💳 Transaction History</h2>'))
            plot_transaction_history(portfolio_id, 90)
        
        print("\n✅ All views updated successfully!")
    
    # Attach handler
    update_btn.on_click(update_all_views)
    
    # Display layout
    display(widgets.VBox([
        update_btn,
        tabs
    ]))
    
    # Initial update
    update_all_views()

print("✓ Complete dashboard launcher ready!")
print("\n" + "="*70)
print("🎉 ALL DASHBOARD FUNCTIONS LOADED!")
print("="*70)
print("\nAvailable functions:")
print("  • create_interactive_dashboard()  - Basic interactive dashboard")
print("  • launch_complete_dashboard()     - Full-featured tabbed dashboard")
print("  • create_static_dashboard(id)     - Static Matplotlib dashboard")
print("  • display_risk_dashboard(id)      - Risk analysis dashboard")
print("  • create_realtime_dashboard(id)   - Real-time updating dashboard")
print("  • export_dashboard_html(id, file) - Export to HTML")
print("\n" + "="*70)
