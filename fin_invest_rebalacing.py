"""
Portfolio Rebalancing & Tracking Tool
Công cụ theo dõi và cân bằng lại danh mục đầu tư
Dựa trên: https://evgenypogorelov.com/portfolio-rebalancing-python
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Import thư viện cần thiết
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance không có")

try:
    from vnstock3 import Vnstock
    VNSTOCK_AVAILABLE = True
except:
    VNSTOCK_AVAILABLE = False

try:
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    WIDGETS_AVAILABLE = True
except:
    WIDGETS_AVAILABLE = False

warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)


class PortfolioRebalancer:
    """
    Công cụ cân bằng lại danh mục đầu tư
    """
    
    def __init__(self):
        self.vnstock = Vnstock() if VNSTOCK_AVAILABLE else None
        
        # Cấu hình mặc định
        self.rebal_threshold = 0.05  # 5% drift
        self.rebal_timeframe = 180  # 180 ngày
        self.new_money = 0  # Tiền mới đầu tư thêm
        
        # Dữ liệu
        self.current_portfolio = None
        self.target_allocation = None
        self.latest_prices = None
        self.rebalanced_portfolio = None
        
        # Account types
        self.account_types = {
            'TAXB': 'Tài khoản chịu thuế',
            '401K': '401K',
            'RIRA': 'Roth IRA',
            'TIRA': 'Traditional IRA',
            'CASH': 'Tiền mặt'
        }
        
        # Asset classes
        self.asset_classes = {
            'ST': 'Cổ phiếu',
            'BD': 'Trái phiếu',
            'CS': 'Tiền mặt & Hàng hóa',
            'RE': 'Bất động sản',
            'ALT': 'Thay thế'
        }
        
        if WIDGETS_AVAILABLE:
            self.create_widgets()
    
    def is_vn_stock(self, symbol):
        """Kiểm tra mã VN"""
        return (len(symbol) == 3 and symbol.isupper() and 
                not any(c in symbol for c in ['.', '-', '^']))
    
    def get_latest_prices(self, tickers):
        """Lấy giá mới nhất"""
        prices = {}
        
        vn_tickers = [t for t in tickers if self.is_vn_stock(t)]
        intl_tickers = [t for t in tickers if not self.is_vn_stock(t)]
        
        # Lấy giá VN
        if vn_tickers and self.vnstock:
            for ticker in vn_tickers:
                try:
                    stock = self.vnstock.stock(symbol=ticker, source='VCI')
                    df = stock.quote.history(start='2024-01-01', end=datetime.now().strftime('%Y-%m-%d'))
                    if not df.empty:
                        prices[ticker] = df['close'].iloc[-1]
                except:
                    print(f"⚠️ Không lấy được giá {ticker}")
        
        # Lấy giá quốc tế
        if intl_tickers and YFINANCE_AVAILABLE:
            try:
                data = yf.download(intl_tickers, period='5d', progress=False)
                if isinstance(data, pd.DataFrame):
                    if 'Adj Close' in data.columns:
                        for ticker in intl_tickers:
                            if ticker in data['Adj Close'].columns:
                                prices[ticker] = data['Adj Close'][ticker].iloc[-1]
                            elif len(intl_tickers) == 1:
                                prices[ticker] = data['Adj Close'].iloc[-1]
            except Exception as e:
                print(f"⚠️ Lỗi yfinance: {e}")
        
        return pd.Series(prices, name='close')
    
    def create_widgets(self):
        """Tạo giao diện"""
        
        # Header
        self.header = widgets.HTML(
            value="""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 25px; border-radius: 12px; margin-bottom: 20px;'>
                <h1 style='color: white; text-align: center; margin: 0;'>
                    ⚖️ Công Cụ Cân Bằng Danh Mục Đầu Tư
                </h1>
                <p style='color: white; text-align: center; margin-top: 8px;'>
                    Portfolio Rebalancing & Tracking Tool
                </p>
            </div>
            """
        )
        
        # Tab system
        self.tabs = widgets.Tab()
        
        # Tab 1: Danh mục hiện tại
        self.current_portfolio_text = widgets.Textarea(
            value='ticker,shares,cost_basis,account_type,asset_class,last_rebal_date\nSPY,100,400,TAXB,ST,2024-01-01\nBND,200,80,RIRA,BD,2024-01-01\nGLD,50,180,TAXB,CS,2024-01-01',
            placeholder='ticker,shares,cost_basis,account_type,asset_class,last_rebal_date',
            description='',
            layout=widgets.Layout(width='95%', height='200px')
        )
        
        # Tab 2: Phân bổ mục tiêu
        self.target_allocation_text = widgets.Textarea(
            value='ticker,allocation_target,asset_class\nSPY,0.60,ST\nBND,0.30,BD\nGLD,0.10,CS',
            placeholder='ticker,allocation_target,asset_class',
            description='',
            layout=widgets.Layout(width='95%', height='150px')
        )
        
        # Cấu hình
        self.rebal_threshold_input = widgets.FloatSlider(
            value=5,
            min=1,
            max=20,
            step=1,
            description='Ngưỡng drift (%):',
            style={'description_width': '150px'}
        )
        
        self.rebal_timeframe_input = widgets.IntSlider(
            value=180,
            min=30,
            max=365,
            step=30,
            description='Thời gian (ngày):',
            style={'description_width': '150px'}
        )
        
        self.new_money_input = widgets.FloatText(
            value=0,
            description='Tiền mới (VNĐ):',
            step=1000000,
            style={'description_width': '150px'}
        )
        
        # Nút phân tích
        self.rebalance_btn = widgets.Button(
            description='⚖️ Cân Bằng Lại',
            button_style='success',
            layout=widgets.Layout(width='200px', height='40px')
        )
        self.rebalance_btn.on_click(self.run_rebalance)
        
        # Output
        self.output = widgets.Output()
        self.analysis_output = widgets.Output()
        self.transactions_output = widgets.Output()
        
        # Tab layouts
        tab1 = widgets.VBox([
            widgets.HTML('<h2>📊 Danh Mục Hiện Tại</h2>'),
            widgets.HTML('<p>Nhập danh mục hiện tại của bạn (CSV format):</p>'),
            widgets.HTML('<p><i>Cột: ticker, shares (số lượng), cost_basis (giá mua), account_type (loại TK), asset_class (loại tài sản), last_rebal_date (lần cân bằng cuối)</i></p>'),
            self.current_portfolio_text,
            widgets.HTML('<br><h3>🎯 Phân Bổ Mục Tiêu</h3>'),
            widgets.HTML('<p>Nhập tỷ trọng mục tiêu (CSV format):</p>'),
            widgets.HTML('<p><i>Cột: ticker, allocation_target (tỷ trọng 0-1), asset_class</i></p>'),
            self.target_allocation_text,
            widgets.HTML('<br><h3>⚙️ Cấu Hình</h3>'),
            self.rebal_threshold_input,
            self.rebal_timeframe_input,
            self.new_money_input,
            widgets.HTML('<br>'),
            self.rebalance_btn,
            self.output
        ])
        
        tab2 = widgets.VBox([
            widgets.HTML('<h2>📈 Phân Tích Cân Bằng</h2>'),
            self.analysis_output
        ])
        
        tab3 = widgets.VBox([
            widgets.HTML('<h2>💼 Giao Dịch Cần Thực Hiện</h2>'),
            self.transactions_output
        ])
        
        self.tabs.children = [tab1, tab2, tab3]
        self.tabs.set_title(0, '📝 Nhập Liệu')
        self.tabs.set_title(1, '📊 Phân Tích')
        self.tabs.set_title(2, '💼 Giao Dịch')
    
    def parse_input(self):
        """Parse input data"""
        try:
            # Parse current portfolio
            from io import StringIO
            current_df = pd.read_csv(StringIO(self.current_portfolio_text.value))
            current_df['last_rebal_date'] = pd.to_datetime(current_df['last_rebal_date'])
            
            # Parse target allocation
            target_df = pd.read_csv(StringIO(self.target_allocation_text.value))
            
            # Validate
            if not np.isclose(target_df['allocation_target'].sum(), 1.0, atol=0.01):
                raise ValueError(f"Tổng tỷ trọng mục tiêu = {target_df['allocation_target'].sum():.2f}, cần = 1.0")
            
            return current_df, target_df
        
        except Exception as e:
            raise ValueError(f"Lỗi parse dữ liệu: {str(e)}")
    
    def run_rebalance(self, b=None):
        """Chạy rebalancing"""
        with self.output:
            clear_output()
            print("🔄 Đang phân tích...")
        
        try:
            # Parse input
            current_df, target_df = self.parse_input()
            
            # Get settings
            self.rebal_threshold = self.rebal_threshold_input.value / 100
            self.rebal_timeframe = self.rebal_timeframe_input.value
            self.new_money = self.new_money_input.value
            
            # Get latest prices
            all_tickers = list(set(current_df['ticker'].tolist() + target_df['ticker'].tolist()))
            
            with self.output:
                clear_output()
                print(f"📥 Đang lấy giá {len(all_tickers)} quỹ...")
            
            prices = self.get_latest_prices(all_tickers)
            
            if prices.empty:
                raise ValueError("Không lấy được giá!")
            
            # Aggregate current portfolio
            current_agg = current_df.groupby('ticker').agg({
                'shares': 'sum',
                'cost_basis': 'mean',
                'asset_class': 'first',
                'last_rebal_date': 'max'
            }).reset_index()
            
            # Merge with prices and target
            portfolio = current_agg.merge(target_df[['ticker', 'allocation_target']], 
                                         on='ticker', how='outer')
            portfolio = portfolio.merge(prices.to_frame('close'), 
                                       left_on='ticker', right_index=True, how='left')
            
            # Fill NaN
            portfolio['shares'] = portfolio['shares'].fillna(0)
            portfolio['allocation_target'] = portfolio['allocation_target'].fillna(0)
            portfolio['cost_basis'] = portfolio['cost_basis'].fillna(portfolio['close'])
            
            # Calculate current values
            portfolio['value'] = portfolio['shares'] * portfolio['close']
            total_value = portfolio['value'].sum()
            portfolio['allocation_current'] = portfolio['value'] / total_value
            
            # Calculate drift
            portfolio['drift'] = portfolio['allocation_target'] - portfolio['allocation_current']
            portfolio['drift_pct'] = portfolio['drift'] / portfolio['allocation_target'].replace(0, 1)
            
            # Calculate days since rebalance
            today = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))
            portfolio['days_since_rebal'] = (today - portfolio['last_rebal_date']).dt.days
            portfolio['days_since_rebal'] = portfolio['days_since_rebal'].fillna(999)
            
            # Determine rebalance flags
            portfolio['needs_rebal_drift'] = np.abs(portfolio['drift']) > self.rebal_threshold
            portfolio['needs_rebal_time'] = portfolio['days_since_rebal'] > self.rebal_timeframe
            portfolio['needs_rebal_exit'] = (portfolio['allocation_current'] > 0) & (portfolio['allocation_target'] == 0)
            portfolio['needs_rebal'] = (portfolio['needs_rebal_drift'] | 
                                       portfolio['needs_rebal_time'] | 
                                       portfolio['needs_rebal_exit'])
            
            # Calculate target with new money
            total_value_new = total_value + self.new_money
            portfolio['target_value'] = portfolio['allocation_target'] * total_value_new
            portfolio['value_change'] = portfolio['target_value'] - portfolio['value']
            portfolio['shares_change'] = portfolio['value_change'] / portfolio['close']
            
            # Round shares
            portfolio['shares_change_rounded'] = portfolio['shares_change'].round(0)
            portfolio['new_shares'] = portfolio['shares'] + portfolio['shares_change_rounded']
            portfolio['new_value'] = portfolio['new_shares'] * portfolio['close']
            portfolio['new_allocation'] = portfolio['new_value'] / portfolio['new_value'].sum()
            
            # Store results
            self.current_portfolio = current_df
            self.target_allocation = target_df
            self.rebalanced_portfolio = portfolio
            
            # Display results
            self.display_analysis()
            self.display_transactions()
            
            self.tabs.selected_index = 1
            
            with self.output:
                clear_output()
                print("✅ Phân tích hoàn tất! Xem tab Phân Tích và Giao Dịch")
        
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
                import traceback
                print("\n" + traceback.format_exc())
    
    def display_analysis(self):
        """Hiển thị phân tích"""
        with self.analysis_output:
            clear_output()
            
            df = self.rebalanced_portfolio
            
            print("="*90)
            print(" "*30 + "📊 PHÂN TÍCH CÂN BẰNG DANH MỤC")
            print("="*90)
            
            # Tổng quan
            print(f"\n💰 Tổng giá trị hiện tại: {df['value'].sum():,.0f} VNĐ")
            print(f"💵 Tiền mới đầu tư thêm: {self.new_money:,.0f} VNĐ")
            print(f"💎 Tổng giá trị mới: {df['new_value'].sum():,.0f} VNĐ")
            
            # Số lượng cần rebalance
            needs_rebal = df[df['needs_rebal']].shape[0]
            print(f"\n⚠️ Cần cân bằng lại: {needs_rebal}/{len(df)} quỹ")
            
            # Hiển thị bảng
            print("\n" + "="*90)
            print(" "*35 + "💼 DANH MỤC CHI TIẾT")
            print("="*90)
            
            display_df = df[['ticker', 'shares', 'close', 'value', 
                            'allocation_current', 'allocation_target', 
                            'drift', 'needs_rebal']].copy()
            display_df['allocation_current'] = (display_df['allocation_current'] * 100).round(2)
            display_df['allocation_target'] = (display_df['allocation_target'] * 100).round(2)
            display_df['drift'] = (display_df['drift'] * 100).round(2)
            
            display_df.columns = ['Ticker', 'Số lượng', 'Giá', 'Giá trị', 
                                 'Hiện tại (%)', 'Mục tiêu (%)', 'Lệch (%)', 'Cần rebal']
            
            print(display_df.to_string(index=False))
            
            # Vẽ biểu đồ
            self.plot_rebalance_charts()
    
    def plot_rebalance_charts(self):
        """Vẽ biểu đồ"""
        df = self.rebalanced_portfolio
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Current vs Target Allocation
        ax1 = axes[0, 0]
        x = np.arange(len(df))
        width = 0.35
        
        ax1.bar(x - width/2, df['allocation_current'] * 100, width, 
               label='Hiện tại', alpha=0.8, color='#3498db')
        ax1.bar(x + width/2, df['allocation_target'] * 100, width, 
               label='Mục tiêu', alpha=0.8, color='#2ecc71')
        
        ax1.set_xlabel('Ticker')
        ax1.set_ylabel('Tỷ trọng (%)')
        ax1.set_title('📊 So Sánh Phân Bổ: Hiện Tại vs Mục Tiêu', fontweight='bold', pad=15)
        ax1.set_xticks(x)
        ax1.set_xticklabels(df['ticker'], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Drift Analysis
        ax2 = axes[0, 1]
        colors = ['#e74c3c' if d < -self.rebal_threshold else 
                 '#2ecc71' if d > self.rebal_threshold else '#95a5a6' 
                 for d in df['drift']]
        
        ax2.barh(df['ticker'], df['drift'] * 100, color=colors, alpha=0.8)
        ax2.axvline(x=-self.rebal_threshold*100, color='red', linestyle='--', 
                   linewidth=2, label=f'Ngưỡng -{self.rebal_threshold*100}%')
        ax2.axvline(x=self.rebal_threshold*100, color='red', linestyle='--', 
                   linewidth=2, label=f'Ngưỡng +{self.rebal_threshold*100}%')
        ax2.axvline(x=0, color='black', linewidth=1)
        ax2.set_xlabel('Độ lệch (%)')
        ax2.set_title('📉 Phân Tích Drift', fontweight='bold', pad=15)
        ax2.legend()
        ax2.grid(axis='x', alpha=0.3)
        
        # 3. Value Changes
        ax3 = axes[1, 0]
        colors = ['#2ecc71' if v > 0 else '#e74c3c' for v in df['value_change']]
        ax3.bar(df['ticker'], df['value_change'], color=colors, alpha=0.8)
        ax3.axhline(y=0, color='black', linewidth=1)
        ax3.set_xlabel('Ticker')
        ax3.set_ylabel('Thay đổi giá trị (VNĐ)')
        ax3.set_title('💰 Thay Đổi Giá Trị', fontweight='bold', pad=15)
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Pie chart - New Allocation
        ax4 = axes[1, 1]
        # Only show non-zero allocations
        pie_df = df[df['new_allocation'] > 0.001].copy()
        colors_pie = plt.cm.Set3(range(len(pie_df)))
        
        wedges, texts, autotexts = ax4.pie(pie_df['new_allocation'], 
                                            labels=pie_df['ticker'],
                                            autopct='%1.1f%%',
                                            colors=colors_pie,
                                            startangle=90)
        ax4.set_title('🎯 Phân Bổ Sau Cân Bằng', fontweight='bold', pad=15)
        
        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        plt.show()
        
        print("\n💡 Giải thích:")
        print("  • Cột xanh lá: Cần MUA thêm")
        print("  • Cột đỏ: Cần BÁN bớt")
        print(f"  • Ngưỡng drift: ±{self.rebal_threshold*100}%")
    
    def display_transactions(self):
        """Hiển thị giao dịch cần thực hiện"""
        with self.transactions_output:
            clear_output()
            
            df = self.rebalanced_portfolio
            
            print("="*80)
            print(" "*25 + "💼 GIAO DỊCH CẦN THỰC HIỆN")
            print("="*80)
            
            # Lọc các giao dịch cần làm
            transactions = df[df['shares_change_rounded'] != 0].copy()
            transactions = transactions.sort_values('shares_change_rounded', ascending=False)
            
            if len(transactions) == 0:
                print("\n✅ Không cần thực hiện giao dịch nào!")
                print("Danh mục của bạn đã cân bằng tốt.")
                return
            
            # Chia thành mua và bán
            buys = transactions[transactions['shares_change_rounded'] > 0]
            sells = transactions[transactions['shares_change_rounded'] < 0]
            
            # Hiển thị lệnh MUA
            if len(buys) > 0:
                print("\n" + "="*80)
                print(" "*35 + "🟢 LỆNH MUA")
                print("="*80)
                print(f"\n{'Ticker':<10} {'SL mua':<10} {'Giá':<12} {'Tổng tiền':<18} {'Tỷ trọng mới':<12}")
                print("-"*80)
                
                total_buy = 0
                for _, row in buys.iterrows():
                    amount = row['shares_change_rounded'] * row['close']
                    total_buy += amount
                    print(f"{row['ticker']:<10} {int(row['shares_change_rounded']):<10} "
                          f"{row['close']:>10,.2f}  {amount:>16,.0f}  "
                          f"{row['new_allocation']*100:>10.2f}%")
                
                print("-"*80)
                print(f"{'Tổng tiền cần:':<34} {total_buy:>16,.0f} VNĐ")
            
            # Hiển thị lệnh BÁN
            if len(sells) > 0:
                print("\n" + "="*80)
                print(" "*35 + "🔴 LỆNH BÁN")
                print("="*80)
                print(f"\n{'Ticker':<10} {'SL bán':<10} {'Giá':<12} {'Tổng tiền':<18} {'Tỷ trọng mới':<12}")
                print("-"*80)
                
                total_sell = 0
                for _, row in sells.iterrows():
                    amount = abs(row['shares_change_rounded']) * row['close']
                    total_sell += amount
                    print(f"{row['ticker']:<10} {int(abs(row['shares_change_rounded'])):<10} "
                          f"{row['close']:>10,.2f}  {amount:>16,.0f}  "
                          f"{row['new_allocation']*100:>10.2f}%")
                
                print("-"*80)
                print(f"{'Tổng tiền thu:':<34} {total_sell:>16,.0f} VNĐ")
            
            # Tổng kết
            print("\n" + "="*80)
            print(" "*32 + "📊 TỔNG KẾT")
            print("="*80)
            
            net_cash_flow = total_buy - total_sell - self.new_money
            
            print(f"\nTiền từ bán: {total_sell:>25,.0f} VNĐ")
            print(f"Tiền mới thêm: {self.new_money:>23,.0f} VNĐ")
            print(f"Tổng có sẵn: {total_sell + self.new_money:>23,.0f} VNĐ")
            print(f"Tiền cần mua: {total_buy:>24,.0f} VNĐ")
            print("-"*80)
            print(f"Chênh lệch: {net_cash_flow:>26,.0f} VNĐ")
            
            if abs(net_cash_flow) < 1000:
                print("\n✅ Cân đối tốt!")
            elif net_cash_flow < 0:
                print(f"\n⚠️ Thiếu {abs(net_cash_flow):,.0f} VNĐ - Cần thêm tiền")
            else:
                print(f"\n💰 Dư {net_cash_flow:,.0f} VNĐ - Có thể giữ lại")
            
            # Lưu ý
            print("\n" + "="*80)
            print(" "*32 + "💡 LƯU Ý")
            print("="*80)
            print("""
✅ Checklist trước khi thực hiện:
   □ Kiểm tra giá thị trường hiện tại
   □ Tính phí giao dịch và thuế
   □ Xem xét tác động thuế (tax-loss harvesting)
   □ Đảm bảo có đủ tiền mặt
   □ Thực hiện theo đúng thứ tự: BÁN trước, MUA sau
   
⚠️ Các yếu tố cần cân nhắc:
   • Chi phí giao dịch
   • Tác động thuế (chênh lệch vốn)
   • Thời điểm thực hiện (tránh FOMO)
   • Thanh khoản thị trường
   • Có nên rebalance 100% hay từng phần
            """)
            
            # Export instructions
            print("\n📥 Export dữ liệu:")
            print("Bạn có thể copy bảng trên vào Excel để theo dõi")
    
    def display(self):
        """Hiển thị ứng dụng"""
        if WIDGETS_AVAILABLE:
            display(self.header)
            display(self.tabs)
        else:
            print("❌ Cần ipywidgets để chạy GUI")


# ==================== KHỞI ĐỘNG ====================

def main():
    print("="*80)
    print("⚖️ PORTFOLIO REBALANCING & TRACKING TOOL")
    print("="*80)
    
    print(f"\n{'pandas:':<20} ✅")
    print(f"{'yfinance:':<20} {'✅' if YFINANCE_AVAILABLE else '❌'}")
    print(f"{'vnstock3:':<20} {'✅' if VNSTOCK_AVAILABLE else '⚠️ (tùy chọn)'}")
    print(f"{'ipywidgets:':<20} {'✅' if WIDGETS_AVAILABLE else '❌'}")
    
    if not WIDGETS_AVAILABLE:
        print("\n❌ Cần ipywidgets!")
        print("📦 Cài đặt: pip install ipywidgets")
        return
    
    print("\n" + "="*80)
    print("✨ Ứng dụng sẵn sàng!")
    print("="*80)
    print("\n💡 Hướng dẫn nhanh:")
    print("  1. Tab 'Nhập Liệu': Nhập danh mục hiện tại và mục tiêu")
    print("  2. Tab 'Phân Tích': Xem phân tích chi tiết")
    print("  3. Tab 'Giao Dịch': Lệnh mua/bán cụ thể")
    print("\n" + "="*80 + "\n")
    
    app = PortfolioRebalancer()
    app.display()


# ==================== HELPER FUNCTIONS ====================

def create_sample_portfolio():
    """Tạo portfolio mẫu để test"""
    
    current = pd.DataFrame({
        'ticker': ['SPY', 'BND', 'GLD', 'VNM', 'VCB'],
        'shares': [100, 200, 50, 1000, 500],
        'cost_basis': [400, 80, 180, 85, 92],
        'account_type': ['TAXB', 'RIRA', 'TAXB', 'TAXB', 'RIRA'],
        'asset_class': ['ST', 'BD', 'CS', 'ST', 'ST'],
        'last_rebal_date': ['2024-01-01']*5
    })
    
    target = pd.DataFrame({
        'ticker': ['SPY', 'BND', 'GLD', 'VNM', 'VCB'],
        'allocation_target': [0.40, 0.30, 0.10, 0.15, 0.05],
        'asset_class': ['ST', 'BD', 'CS', 'ST', 'ST']
    })
    
    return current, target


def export_to_csv(portfolio_df, filename='portfolio_rebalance.csv'):
    """Export kết quả ra CSV"""
    portfolio_df.to_csv(filename, index=False)
    print(f"✅ Đã xuất file: {filename}")


def calculate_tax_impact(portfolio_df, tax_rate=0.20):
    """Tính tác động thuế"""
    
    # Chỉ tính thuế cho lệnh BÁN có lãi
    sells = portfolio_df[portfolio_df['shares_change_rounded'] < 0].copy()
    
    if len(sells) == 0:
        return 0
    
    sells['capital_gain'] = (sells['close'] - sells['cost_basis']) * abs(sells['shares_change_rounded'])
    sells['tax'] = sells['capital_gain'].clip(lower=0) * tax_rate
    
    total_tax = sells['tax'].sum()
    
    print("\n" + "="*80)
    print(" "*30 + "💰 PHÂN TÍCH THUẾ")
    print("="*80)
    print(f"\n{'Ticker':<10} {'Giá mua':<12} {'Giá bán':<12} {'Lãi/lỗ':<15} {'Thuế (20%)':<15}")
    print("-"*80)
    
    for _, row in sells.iterrows():
        print(f"{row['ticker']:<10} {row['cost_basis']:>10,.0f}  {row['close']:>10,.0f}  "
              f"{row['capital_gain']:>13,.0f}  {row['tax']:>13,.0f}")
    
    print("-"*80)
    print(f"{'Tổng thuế phải nộp:':<44} {total_tax:>13,.0f} VNĐ")
    
    return total_tax


def schedule_rebalance(months_interval=6):
    """Lịch rebalance đề xuất"""
    
    today = datetime.now()
    schedule = []
    
    for i in range(1, 5):
        next_date = today + timedelta(days=months_interval*30*i)
        quarter = (next_date.month - 1) // 3 + 1
        schedule.append({
            'date': next_date.strftime('%Y-%m-%d'),
            'quarter': f"Q{quarter}/{next_date.year}",
            'note': 'Rebalance định kỳ'
        })
    
    print("\n" + "="*80)
    print(" "*27 + "📅 LỊCH REBALANCE ĐỀ XUẤT")
    print("="*80)
    print(f"\n{'Ngày':<15} {'Quý':<12} {'Ghi chú'}")
    print("-"*80)
    
    for item in schedule:
        print(f"{item['date']:<15} {item['quarter']:<12} {item['note']}")
    
    print("\n💡 Gợi ý:")
    print(f"  • Rebalance mỗi {months_interval} tháng")
    print("  • Hoặc khi drift > 5%")
    print("  • Kết hợp với đóng góp định kỳ")


def compare_with_benchmark(portfolio_df, benchmark='SPY'):
    """So sánh với benchmark"""
    
    if not YFINANCE_AVAILABLE:
        print("⚠️ Cần yfinance để so sánh benchmark")
        return
    
    try:
        # Tải dữ liệu benchmark
        bench_data = yf.download(benchmark, period='1y', progress=False)
        
        if bench_data.empty:
            print(f"⚠️ Không lấy được dữ liệu {benchmark}")
            return
        
        # Tính return
        bench_return = (bench_data['Adj Close'].iloc[-1] / bench_data['Adj Close'].iloc[0] - 1) * 100
        
        print("\n" + "="*80)
        print(" "*25 + "📊 SO SÁNH VỚI BENCHMARK")
        print("="*80)
        print(f"\nBenchmark: {benchmark}")
        print(f"Return 1 năm: {bench_return:.2f}%")
        print("\n💡 So sánh danh mục của bạn với benchmark để đánh giá hiệu suất")
    
    except Exception as e:
        print(f"⚠️ Lỗi so sánh benchmark: {e}")


def generate_rebalance_report(rebalancer):
    """Tạo báo cáo tổng hợp"""
    
    if rebalancer.rebalanced_portfolio is None:
        print("❌ Chưa có dữ liệu rebalance!")
        return
    
    df = rebalancer.rebalanced_portfolio
    
    print("\n" + "="*80)
    print(" "*25 + "📋 BÁO CÁO CÂN BẰNG DANH MỤC")
    print("="*80)
    
    print(f"\n📅 Ngày báo cáo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 Tổng giá trị: {df['value'].sum():,.0f} VNĐ")
    print(f"💵 Tiền mới: {rebalancer.new_money:,.0f} VNĐ")
    
    # Tóm tắt theo asset class
    print("\n" + "-"*80)
    print("Phân bổ theo loại tài sản:")
    print("-"*80)
    
    asset_summary = df.groupby('asset_class').agg({
        'value': 'sum',
        'new_value': 'sum'
    })
    
    asset_summary['current_pct'] = asset_summary['value'] / asset_summary['value'].sum() * 100
    asset_summary['new_pct'] = asset_summary['new_value'] / asset_summary['new_value'].sum() * 100
    
    asset_names = rebalancer.asset_classes
    
    for asset_class, row in asset_summary.iterrows():
        name = asset_names.get(asset_class, asset_class)
        print(f"\n{name}:")
        print(f"  Hiện tại: {row['current_pct']:.1f}%")
        print(f"  Sau rebalance: {row['new_pct']:.1f}%")
    
    # Số lượng giao dịch
    transactions = df[df['shares_change_rounded'] != 0]
    n_buy = len(transactions[transactions['shares_change_rounded'] > 0])
    n_sell = len(transactions[transactions['shares_change_rounded'] < 0])
    
    print("\n" + "-"*80)
    print(f"Tổng số giao dịch: {len(transactions)}")
    print(f"  • Lệnh mua: {n_buy}")
    print(f"  • Lệnh bán: {n_sell}")
    
    # Drift lớn nhất
    max_drift = df.loc[df['drift'].abs().idxmax()]
    print("\n" + "-"*80)
    print(f"Drift lớn nhất: {max_drift['ticker']} ({max_drift['drift']*100:.2f}%)")
    
    print("\n" + "="*80)


def backtesting_rebalance(tickers, initial_weights, start_date, end_date, 
                         rebal_freq='Q'):
    """
    Backtest chiến lược rebalancing
    
    Parameters:
    - tickers: list of tickers
    - initial_weights: dict of weights
    - start_date, end_date: date strings
    - rebal_freq: 'M' (monthly), 'Q' (quarterly), 'Y' (yearly)
    """
    
    if not YFINANCE_AVAILABLE:
        print("⚠️ Cần yfinance để backtest")
        return
    
    print("\n" + "="*80)
    print(" "*27 + "🔬 BACKTEST REBALANCING")
    print("="*80)
    print(f"\nKỳ: {start_date} đến {end_date}")
    print(f"Tần suất: {rebal_freq}")
    
    try:
        # Tải dữ liệu
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Adj Close']
        
        if isinstance(data, pd.Series):
            data = data.to_frame()
        
        # Tính return
        returns = data.pct_change().dropna()
        
        # Strategy 1: Buy & Hold
        bh_value = 100  # Start with 100
        weights = pd.Series(initial_weights)
        
        for date, ret in returns.iterrows():
            bh_value *= (1 + (ret * weights).sum())
        
        # Strategy 2: Rebalancing
        rebal_value = 100
        current_weights = weights.copy()
        
        # Tạo dates cho rebalancing
        if rebal_freq == 'Q':
            rebal_dates = pd.date_range(start=start_date, end=end_date, freq='QS')
        elif rebal_freq == 'M':
            rebal_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
        else:  # Y
            rebal_dates = pd.date_range(start=start_date, end=end_date, freq='YS')
        
        for date, ret in returns.iterrows():
            # Apply returns
            port_return = (ret * current_weights).sum()
            rebal_value *= (1 + port_return)
            
            # Update weights
            current_weights *= (1 + ret)
            current_weights /= current_weights.sum()
            
            # Rebalance if needed
            if date in rebal_dates:
                current_weights = weights.copy()
        
        # Kết quả
        print(f"\n📈 Kết quả:")
        print(f"  Buy & Hold: {(bh_value - 100):.2f}%")
        print(f"  Rebalancing: {(rebal_value - 100):.2f}%")
        print(f"  Outperformance: {(rebal_value - bh_value):.2f}%")
        
        if rebal_value > bh_value:
            print(f"\n✅ Rebalancing tốt hơn Buy & Hold!")
        else:
            print(f"\n⚠️ Buy & Hold tốt hơn trong kỳ này")
    
    except Exception as e:
        print(f"❌ Lỗi backtest: {e}")


# ==================== CLI MODE (Không cần widgets) ====================

def run_cli_mode():
    """Chạy ở chế độ CLI (không GUI)"""
    
    print("\n🖥️  Chế độ CLI (Command Line Interface)")
    print("="*80)
    
    # Tạo sample data
    print("\n📊 Sử dụng dữ liệu mẫu...")
    current, target = create_sample_portfolio()
    
    print("\n1️⃣ Danh mục hiện tại:")
    print(current.to_string(index=False))
    
    print("\n2️⃣ Phân bổ mục tiêu:")
    print(target.to_string(index=False))
    
    # Tạo rebalancer
    rebalancer = PortfolioRebalancer()
    rebalancer.current_portfolio = current
    rebalancer.target_allocation = target
    rebalancer.new_money = 10_000_000
    rebalancer.rebal_threshold = 0.05
    
    print("\n3️⃣ Đang lấy giá...")
    
    all_tickers = list(set(current['ticker'].tolist() + target['ticker'].tolist()))
    prices = rebalancer.get_latest_prices(all_tickers)
    
    if prices.empty:
        print("❌ Không lấy được giá!")
        return
    
    print(f"✅ Đã lấy giá {len(prices)} quỹ")
    
    # Aggregate và tính toán (giống run_rebalance)
    current_agg = current.groupby('ticker').agg({
        'shares': 'sum',
        'cost_basis': 'mean',
        'asset_class': 'first',
        'last_rebal_date': 'max'
    }).reset_index()
    
    current_agg['last_rebal_date'] = pd.to_datetime(current_agg['last_rebal_date'])
    
    portfolio = current_agg.merge(target[['ticker', 'allocation_target']], 
                                 on='ticker', how='outer')
    portfolio = portfolio.merge(prices.to_frame('close'), 
                               left_on='ticker', right_index=True, how='left')
    
    portfolio['shares'] = portfolio['shares'].fillna(0)
    portfolio['allocation_target'] = portfolio['allocation_target'].fillna(0)
    portfolio['cost_basis'] = portfolio['cost_basis'].fillna(portfolio['close'])
    
    portfolio['value'] = portfolio['shares'] * portfolio['close']
    total_value = portfolio['value'].sum()
    portfolio['allocation_current'] = portfolio['value'] / total_value
    
    portfolio['drift'] = portfolio['allocation_target'] - portfolio['allocation_current']
    
    today = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))
    portfolio['days_since_rebal'] = (today - portfolio['last_rebal_date']).dt.days
    portfolio['days_since_rebal'] = portfolio['days_since_rebal'].fillna(999)
    
    portfolio['needs_rebal'] = (np.abs(portfolio['drift']) > rebalancer.rebal_threshold)
    
    total_value_new = total_value + rebalancer.new_money
    portfolio['target_value'] = portfolio['allocation_target'] * total_value_new
    portfolio['value_change'] = portfolio['target_value'] - portfolio['value']
    portfolio['shares_change'] = portfolio['value_change'] / portfolio['close']
    portfolio['shares_change_rounded'] = portfolio['shares_change'].round(0)
    portfolio['new_shares'] = portfolio['shares'] + portfolio['shares_change_rounded']
    portfolio['new_value'] = portfolio['new_shares'] * portfolio['close']
    portfolio['new_allocation'] = portfolio['new_value'] / portfolio['new_value'].sum()
    
    rebalancer.rebalanced_portfolio = portfolio
    
    # Hiển thị kết quả
    print("\n4️⃣ Kết quả phân tích:")
    print("="*80)
    
    print(f"\n💰 Tổng giá trị: {total_value:,.0f} VNĐ")
    print(f"💵 Tiền mới: {rebalancer.new_money:,.0f} VNĐ")
    print(f"💎 Tổng mới: {portfolio['new_value'].sum():,.0f} VNĐ")
    
    # Bảng tóm tắt
    summary = portfolio[['ticker', 'allocation_current', 'allocation_target', 
                        'drift', 'shares_change_rounded']].copy()
    summary['allocation_current'] = (summary['allocation_current'] * 100).round(1)
    summary['allocation_target'] = (summary['allocation_target'] * 100).round(1)
    summary['drift'] = (summary['drift'] * 100).round(1)
    summary.columns = ['Ticker', 'Hiện tại%', 'Mục tiêu%', 'Lệch%', 'SL thay đổi']
    
    print("\n" + summary.to_string(index=False))
    
    # Giao dịch
    transactions = portfolio[portfolio['shares_change_rounded'] != 0]
    
    if len(transactions) > 0:
        print(f"\n5️⃣ Cần thực hiện {len(transactions)} giao dịch:")
        
        for _, row in transactions.iterrows():
            action = "MUA" if row['shares_change_rounded'] > 0 else "BÁN"
            amount = abs(row['shares_change_rounded'])
            value = amount * row['close']
            print(f"  {action} {int(amount)} {row['ticker']} = {value:,.0f} VNĐ")
    else:
        print("\n5️⃣ ✅ Không cần giao dịch!")
    
    print("\n" + "="*80)
    print("✅ Hoàn tất!")


# ==================== MAIN ====================

if __name__ == "__main__":
    if WIDGETS_AVAILABLE:
        main()
    else:
        print("\n⚠️ ipywidgets không có, chạy ở chế độ CLI...")
        run_cli_mode()
else:
    # Jupyter notebook
    try:
        if WIDGETS_AVAILABLE:
            app = PortfolioRebalancer()
            app.display()
        else:
            run_cli_mode()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("\n💡 Hướng dẫn cài đặt:")
        print("  pip install pandas numpy matplotlib seaborn")
        print("  pip install ipywidgets")
        print("  pip install yfinance")
        print("  pip install vnstock3  # Tùy chọn")
