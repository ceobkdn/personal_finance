"""
Portfolio Rebalancing - Vietnam Stock Market Edition
Công cụ cân bằng danh mục đầu tư - TTCK Việt Nam
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

try:
    from vnstock3 import Vnstock
    VNSTOCK_AVAILABLE = True
except:
    VNSTOCK_AVAILABLE = False

try:
    import ipywidgets as widgets
    from IPython.display import display, clear_output
    WIDGETS_AVAILABLE = True
except:
    WIDGETS_AVAILABLE = False

warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)


class VNPortfolioRebalancer:
    """Công cụ cân bằng danh mục cho TTCK Việt Nam"""
    
    def __init__(self):
        self.vnstock = Vnstock() if VNSTOCK_AVAILABLE else None
        
        # Cấu hình
        self.rebal_threshold = 0.05
        self.rebal_timeframe = 180
        self.new_money = 0
        
        # Dữ liệu
        self.current_portfolio = None
        self.target_allocation = None
        self.rebalanced_portfolio = None
        
        # Asset classes
        self.asset_classes = {
            'CP': 'Cổ phiếu',
            'ETF': 'Quỹ ETF',
            'TM': 'Tiền mặt'
        }
        
        self.account_types = {
            'TKCK': 'TK Chứng khoán',
            'TM': 'Tiền mặt'
        }
        
        if WIDGETS_AVAILABLE:
            self.create_widgets()
    
    def get_vn_stock_price(self, ticker):
        """Lấy giá cổ phiếu VN"""
        if not self.vnstock:
            return None
        
        try:
            stock = self.vnstock.stock(symbol=ticker, source='VCI')
            df = stock.quote.history(
                start=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                end=datetime.now().strftime('%Y-%m-%d')
            )
            if not df.empty:
                return df['close'].iloc[-1]
        except:
            pass
        
        return None
    
    def get_latest_prices(self, tickers):
        """Lấy giá mới nhất"""
        prices = {}
        
        print("📥 Đang lấy giá từ vnstock3...")
        for ticker in tickers:
            price = self.get_vn_stock_price(ticker)
            if price:
                prices[ticker] = price
                print(f"  ✓ {ticker}: {price:,.0f} VNĐ")
        
        return pd.Series(prices, name='close')
    
    def create_widgets(self):
        """Tạo giao diện"""
        
        # Header
        self.header = widgets.HTML(
            value="""
            <div style='background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
                        padding: 25px; border-radius: 12px; margin-bottom: 20px;'>
                <h1 style='color: white; text-align: center; margin: 0;'>
                    ⚖️ Cân Bằng Danh Mục Đầu Tư
                </h1>
                <p style='color: white; text-align: center; margin-top: 8px;'>
                    Thị Trường Chứng Khoán Việt Nam 🇻🇳
                </p>
            </div>
            """
        )
        
        # Instructions
        instructions = widgets.HTML(
            value="""
            <div style='background: #ecf0f1; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                <h3 style='margin-top: 0;'>📖 Hướng dẫn:</h3>
                <ol>
                    <li>Nhập danh mục hiện tại (mỗi hàng 1 mã)</li>
                    <li>Nhập tỷ trọng mục tiêu (tổng = 100%)</li>
                    <li>Nhấn "Phân Tích" để xem kết quả</li>
                </ol>
                <p style='color: #7f8c8d;'>💡 Format: MÃ,SL,GIÁ_MUA,LOẠI_TK,LOẠI_TS,NGÀY</p>
            </div>
            """
        )
        
        # ===== DANH MỤC HIỆN TẠI =====
        self.current_text = widgets.Textarea(
            value='VCB,500,90000,TKCK,CP,2024-01-01\nHPG,2000,25000,TKCK,CP,2024-01-01\nVNM,1000,85000,TKCK,CP,2024-01-01\nFPT,800,95000,TKCK,CP,2024-01-01\nVHM,1500,55000,TKCK,CP,2024-01-01',
            placeholder='VCB,500,90000,TKCK,CP,2024-01-01\nHPG,2000,25000,TKCK,CP,2024-01-01',
            description='',
            layout=widgets.Layout(width='100%', height='180px')
        )
        
        current_help = widgets.HTML(
            value="""
            <div style='background: #d5f4e6; padding: 10px; border-radius: 5px; margin-top: 5px;'>
                <small><b>Format:</b> MÃ_CK, Số_lượng, Giá_mua, Loại_TK, Loại_TS, Ngày_rebal_cuối</small><br>
                <small><b>Loại TK:</b> TKCK (TK chứng khoán), TM (Tiền mặt)</small><br>
                <small><b>Loại TS:</b> CP (Cổ phiếu), ETF, TM (Tiền mặt)</small><br>
                <small><b>Ví dụ:</b> VCB,500,90000,TKCK,CP,2024-01-01</small>
            </div>
            """
        )
        
        # ===== PHÂN BỔ MỤC TIÊU =====
        self.target_text = widgets.Textarea(
            value='VCB,25,CP\nHPG,20,CP\nVNM,20,CP\nFPT,20,CP\nVHM,15,CP',
            placeholder='VCB,25,CP\nHPG,20,CP\nVNM,20,CP',
            description='',
            layout=widgets.Layout(width='100%', height='150px')
        )
        
        target_help = widgets.HTML(
            value="""
            <div style='background: #fef5e7; padding: 10px; border-radius: 5px; margin-top: 5px;'>
                <small><b>Format:</b> MÃ_CK, Tỷ_trọng_%, Loại_TS</small><br>
                <small><b>Lưu ý:</b> Tổng tỷ trọng phải = 100%</small><br>
                <small><b>Ví dụ:</b> VCB,25,CP (nghĩa là 25%)</small>
            </div>
            """
        )
        
        # Validate button
        self.validate_btn = widgets.Button(
            description='✓ Kiểm tra dữ liệu',
            button_style='info',
            layout=widgets.Layout(width='180px')
        )
        self.validate_btn.on_click(self.validate_input)
        
        # Clear buttons
        clear_current_btn = widgets.Button(
            description='🗑️ Xóa danh mục',
            button_style='warning',
            layout=widgets.Layout(width='150px')
        )
        clear_current_btn.on_click(lambda b: self.current_text.set_trait('value', ''))
        
        clear_target_btn = widgets.Button(
            description='🗑️ Xóa mục tiêu',
            button_style='warning',
            layout=widgets.Layout(width='150px')
        )
        clear_target_btn.on_click(lambda b: self.target_text.set_trait('value', ''))
        
        # ===== CẤU HÌNH =====
        self.rebal_threshold_input = widgets.FloatSlider(
            value=5,
            min=1,
            max=20,
            step=0.5,
            description='Ngưỡng drift (%):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='500px')
        )
        
        self.rebal_timeframe_input = widgets.IntSlider(
            value=180,
            min=30,
            max=365,
            step=30,
            description='Thời gian (ngày):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='500px')
        )
        
        self.new_money_input = widgets.FloatText(
            value=0,
            description='Tiền mới (VNĐ):',
            step=10_000_000,
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )
        
        # Analyze button
        self.analyze_btn = widgets.Button(
            description='⚖️ Phân Tích & Cân Bằng',
            button_style='success',
            layout=widgets.Layout(width='280px', height='50px')
        )
        self.analyze_btn.on_click(self.run_rebalance)
        
        # Outputs
        self.output = widgets.Output()
        self.analysis_output = widgets.Output()
        self.transactions_output = widgets.Output()
        
        # Main container
        self.main_container = widgets.VBox([
            self.header,
            instructions,
            
            widgets.HTML("<h2 style='color: #2c3e50; margin-top: 20px;'>📊 1. Danh Mục Hiện Tại</h2>"),
            self.current_text,
            current_help,
            widgets.HBox([clear_current_btn], layout=widgets.Layout(margin='10px 0')),
            
            widgets.HTML("<h2 style='color: #2c3e50; margin-top: 20px;'>🎯 2. Phân Bổ Mục Tiêu</h2>"),
            self.target_text,
            target_help,
            widgets.HBox([clear_target_btn], layout=widgets.Layout(margin='10px 0')),
            
            widgets.HTML("<h2 style='color: #2c3e50; margin-top: 20px;'>⚙️ 3. Cấu Hình</h2>"),
            self.rebal_threshold_input,
            self.rebal_timeframe_input,
            self.new_money_input,
            
            widgets.HTML("<br>"),
            widgets.HBox([self.validate_btn, self.analyze_btn], 
                        layout=widgets.Layout(margin='10px 0')),
            self.output,
            
            widgets.HTML("<hr style='margin: 30px 0;'>"),
            widgets.HTML("<h2 style='color: #2c3e50;'>📈 4. Kết Quả Phân Tích</h2>"),
            self.analysis_output,
            
            widgets.HTML("<br><h2 style='color: #2c3e50;'>💼 5. Giao Dịch</h2>"),
            self.transactions_output
        ])
    
    def validate_input(self, b):
        """Kiểm tra dữ liệu nhập"""
        with self.output:
            clear_output()
            try:
                current_df, target_df = self.parse_input()
                
                print("✅ Kiểm tra thành công!")
                print(f"\n📊 Danh mục hiện tại: {len(current_df)} mã")
                print(current_df[['ticker', 'shares', 'cost_basis']].to_string(index=False))
                
                print(f"\n🎯 Phân bổ mục tiêu: {len(target_df)} mã")
                print(target_df[['ticker', 'allocation_target']].to_string(index=False))
                print(f"\nTổng tỷ trọng: {target_df['allocation_target'].sum()*100:.1f}%")
                
            except Exception as e:
                print(f"❌ Lỗi: {str(e)}")
    
    def parse_input(self):
        """Parse input từ textarea"""
        # Parse current portfolio
        current_lines = [line.strip() for line in self.current_text.value.split('\n') if line.strip()]
        
        if not current_lines:
            raise ValueError("Danh mục hiện tại trống!")
        
        current_data = []
        for i, line in enumerate(current_lines, 1):
            try:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) != 6:
                    raise ValueError(f"Dòng {i}: Cần 6 cột, có {len(parts)} cột")
                
                current_data.append({
                    'ticker': parts[0].upper(),
                    'shares': float(parts[1]),
                    'cost_basis': float(parts[2]),
                    'account_type': parts[3].upper(),
                    'asset_class': parts[4].upper(),
                    'last_rebal_date': parts[5]
                })
            except Exception as e:
                raise ValueError(f"Lỗi dòng {i} (danh mục): {str(e)}")
        
        current_df = pd.DataFrame(current_data)
        current_df['last_rebal_date'] = pd.to_datetime(current_df['last_rebal_date'])
        
        # Parse target allocation
        target_lines = [line.strip() for line in self.target_text.value.split('\n') if line.strip()]
        
        if not target_lines:
            raise ValueError("Phân bổ mục tiêu trống!")
        
        target_data = []
        for i, line in enumerate(target_lines, 1):
            try:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) != 3:
                    raise ValueError(f"Dòng {i}: Cần 3 cột, có {len(parts)} cột")
                
                target_data.append({
                    'ticker': parts[0].upper(),
                    'allocation_target': float(parts[1]) / 100,  # Convert % to decimal
                    'asset_class': parts[2].upper()
                })
            except Exception as e:
                raise ValueError(f"Lỗi dòng {i} (mục tiêu): {str(e)}")
        
        target_df = pd.DataFrame(target_data)
        
        # Validate total
        total = target_df['allocation_target'].sum()
        if not np.isclose(total, 1.0, atol=0.02):
            raise ValueError(f"Tổng tỷ trọng = {total*100:.1f}%, cần = 100%")
        
        return current_df, target_df
    
    def run_rebalance(self, b):
        """Chạy phân tích"""
        with self.output:
            clear_output()
            print("🔄 Đang phân tích...")
        
        try:
            # Parse
            current_df, target_df = self.parse_input()
            
            # Settings
            self.rebal_threshold = self.rebal_threshold_input.value / 100
            self.rebal_timeframe = self.rebal_timeframe_input.value
            self.new_money = self.new_money_input.value
            
            # Get prices
            all_tickers = list(set(current_df['ticker'].tolist() + target_df['ticker'].tolist()))
            
            with self.output:
                clear_output()
                print(f"📥 Đang lấy giá {len(all_tickers)} mã...")
            
            prices = self.get_latest_prices(all_tickers)
            
            if prices.empty:
                raise ValueError("Không lấy được giá! Kiểm tra kết nối hoặc mã CK")
            
            # Aggregate
            current_agg = current_df.groupby('ticker').agg({
                'shares': 'sum',
                'cost_basis': 'mean',
                'asset_class': 'first',
                'last_rebal_date': 'max'
            }).reset_index()
            
            # Merge
            portfolio = current_agg.merge(target_df[['ticker', 'allocation_target']], 
                                         on='ticker', how='outer')
            portfolio = portfolio.merge(prices.to_frame('close'), 
                                       left_on='ticker', right_index=True, how='left')
            
            # Fill NaN
            portfolio['shares'] = portfolio['shares'].fillna(0)
            portfolio['allocation_target'] = portfolio['allocation_target'].fillna(0)
            portfolio['cost_basis'] = portfolio['cost_basis'].fillna(portfolio['close'])
            
            # Asset class
            for idx, row in portfolio.iterrows():
                if pd.isna(row['asset_class']):
                    match = target_df[target_df['ticker'] == row['ticker']]
                    if not match.empty:
                        portfolio.at[idx, 'asset_class'] = match.iloc[0]['asset_class']
            
            # Calculate
            portfolio['value'] = portfolio['shares'] * portfolio['close']
            total_value = portfolio['value'].sum()
            portfolio['allocation_current'] = portfolio['value'] / total_value
            portfolio['drift'] = portfolio['allocation_target'] - portfolio['allocation_current']
            
            today = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))
            portfolio['days_since_rebal'] = (today - portfolio['last_rebal_date']).dt.days
            portfolio['days_since_rebal'] = portfolio['days_since_rebal'].fillna(999)
            
            portfolio['needs_rebal_drift'] = np.abs(portfolio['drift']) > self.rebal_threshold
            portfolio['needs_rebal_time'] = portfolio['days_since_rebal'] > self.rebal_timeframe
            portfolio['needs_rebal_exit'] = (portfolio['allocation_current'] > 0) & (portfolio['allocation_target'] == 0)
            portfolio['needs_rebal'] = (portfolio['needs_rebal_drift'] | 
                                       portfolio['needs_rebal_time'] | 
                                       portfolio['needs_rebal_exit'])
            
            total_value_new = total_value + self.new_money
            portfolio['target_value'] = portfolio['allocation_target'] * total_value_new
            portfolio['value_change'] = portfolio['target_value'] - portfolio['value']
            portfolio['shares_change'] = portfolio['value_change'] / portfolio['close']
            
            # Round (bội số 100)
            portfolio['shares_change_rounded'] = (portfolio['shares_change'] / 100).round() * 100
            portfolio['new_shares'] = portfolio['shares'] + portfolio['shares_change_rounded']
            portfolio['new_value'] = portfolio['new_shares'] * portfolio['close']
            portfolio['new_allocation'] = portfolio['new_value'] / portfolio['new_value'].sum()
            
            # Store
            self.current_portfolio = current_df
            self.target_allocation = target_df
            self.rebalanced_portfolio = portfolio
            
            # Display
            self.display_analysis()
            self.display_transactions()
            
            with self.output:
                clear_output()
                print("✅ Phân tích hoàn tất!")
        
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
    
    def display_analysis(self):
        """Hiển thị phân tích"""
        with self.analysis_output:
            clear_output()
            
            df = self.rebalanced_portfolio
            
            print("="*90)
            print(" "*28 + "📊 PHÂN TÍCH CÂN BẰNG DANH MỤC")
            print("="*90)
            
            print(f"\n💰 Tổng giá trị: {df['value'].sum():,.0f} VNĐ")
            print(f"💵 Tiền mới: {self.new_money:,.0f} VNĐ")
            print(f"💎 Tổng mới: {df['new_value'].sum():,.0f} VNĐ")
            
            needs = df[df['needs_rebal']].shape[0]
            print(f"\n⚠️ Cần cân bằng: {needs}/{len(df)} mã")
            
            print("\n" + "="*90)
            print(f"\n{'Mã':<8} {'SL':<10} {'Giá':<15} {'Giá trị':<18} "
                  f"{'Hiện tại':<10} {'Mục tiêu':<10} {'Lệch':<10}")
            print("-"*90)
            
            for _, row in df.iterrows():
                print(f"{row['ticker']:<8} {row['shares']:>9,.0f} "
                      f"{row['close']:>14,.0f} {row['value']:>17,.0f} "
                      f"{row['allocation_current']*100:>8.1f}% {row['allocation_target']*100:>8.1f}% "
                      f"{row['drift']*100:>8.1f}%")
            
            # Charts
            self.plot_charts()
    
    def plot_charts(self):
        """Vẽ biểu đồ"""
        df = self.rebalanced_portfolio
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 11))
        
        # 1. Current vs Target
        ax1 = axes[0, 0]
        x = np.arange(len(df))
        width = 0.35
        
        ax1.bar(x - width/2, df['allocation_current'] * 100, width, 
               label='Hiện tại', alpha=0.8, color='#e74c3c')
        ax1.bar(x + width/2, df['allocation_target'] * 100, width, 
               label='Mục tiêu', alpha=0.8, color='#27ae60')
        
        ax1.set_xlabel('Mã')
        ax1.set_ylabel('Tỷ trọng (%)')
        ax1.set_title('📊 Hiện Tại vs Mục Tiêu', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df['ticker'], rotation=45)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Drift
        ax2 = axes[0, 1]
        colors = ['#e74c3c' if d < -self.rebal_threshold else 
                 '#27ae60' if d > self.rebal_threshold else '#95a5a6' 
                 for d in df['drift']]
        
        ax2.barh(df['ticker'], df['drift'] * 100, color=colors, alpha=0.8)
        ax2.axvline(x=0, color='black', linewidth=1.5)
        ax2.set_xlabel('Lệch (%)')
        ax2.set_title('📉 Drift', fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # 3. Value change
        ax3 = axes[1, 0]
        colors = ['#27ae60' if v > 0 else '#e74c3c' for v in df['value_change']]
        ax3.bar(df['ticker'], df['value_change']/1e6, color=colors, alpha=0.8)
        ax3.axhline(y=0, color='black', linewidth=1.5)
        ax3.set_xlabel('Mã')
        ax3.set_ylabel('Triệu VNĐ')
        ax3.set_title('💰 Thay Đổi', fontweight='bold')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Pie
        ax4 = axes[1, 1]
        pie_df = df[df['new_allocation'] > 0.001]
        ax4.pie(pie_df['new_allocation'], labels=pie_df['ticker'],
                autopct='%1.1f%%', startangle=90)
        ax4.set_title('🎯 Phân Bổ Mới', fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def display_transactions(self):
        """Hiển thị giao dịch"""
        with self.transactions_output:
            clear_output()
            
            df = self.rebalanced_portfolio
            
            print("="*85)
            print(" "*27 + "💼 GIAO DỊCH CẦN THỰC HIỆN")
            print("="*85)
            
            trans = df[df['shares_change_rounded'] != 0].copy()
            
            if len(trans) == 0:
                print("\n✅ Không cần giao dịch!")
                return
            
            buys = trans[trans['shares_change_rounded'] > 0]
            sells = trans[trans['shares_change_rounded'] < 0]
            
            # MUA
            if len(buys) > 0:
                print("\n" + "="*85)
                print(" "*37 + "🟢 MUA")
                print("="*85)
                print(f"\n{'Mã':<8} {'SL':<12} {'Giá':<15} {'Tổng':<20}")
                print("-"*85)
                
                total_buy = 0
                for _, row in buys.iterrows():
                    amt = row['shares_change_rounded'] * row['close']
                    total_buy += amt
                    print(f"{row['ticker']:<8} {int(row['shares_change_rounded']):>11,} "
                          f"{row['close']:>14,.0f} {amt:>19,.0f}")
                
                print("-"*85)
                print(f"Tổng: {total_buy:>19,.0f} VNĐ")
            
            # BÁN
            if len(sells) > 0:
                print("\n" + "="*85)
                print(" "*37 + "🔴 BÁN")
                print("="*85)
                print(f"\n{'Mã':<8} {'SL':<12} {'Giá':<15} {'Tổng':<20}")
                print("-"*85)
                
                total_sell = 0
                for _, row in sells.iterrows():
                    amt = abs(row['shares_change_rounded']) * row['close']
                    total_sell += amt
                    print(f"{row['ticker']:<8} {int(abs(row['shares_change_rounded'])):>11,} "
                          f"{row['close']:>14,.0f} {amt:>19,.0f}")
                
                print("-"*85)
                print(f"Tổng: {total_sell:>19,.0f} VNĐ")
            
            # Tổng kết
            print("\n" + "="*85)
            net = total_buy - total_sell - self.new_money
            print(f"\nTiền bán: {total_sell:,.0f} VNĐ")
            print(f"Tiền mới: {self.new_money:,.0f} VNĐ")
            print(f"Cần mua: {total_buy:,.0f} VNĐ")
            print(f"Chênh lệch: {net:,.0f} VNĐ")
            
            print("\n💡 Lưu ý TTCK VN:")
            print("  • Khối lượng: Bội số 100")
            print("  • Thanh toán: T+2")
            print("  • Phí: ~0.3% (môi giới + thuế)")
    
    def display(self):
        """Hiển thị app"""
        if WIDGETS_AVAILABLE:
            display(self.main_container)


# ==================== MAIN ====================

def main():
    print("="*80)
    print("⚖️ CÂN BẰNG DANH MỤC - THỊ TRƯỜNG VIỆT NAM")
    print("="*80)
    
    print(f"\nvnstock3: {'✅' if VNSTOCK_AVAILABLE else '❌'}")
    print(f"ipywidgets: {'✅' if WIDGETS_AVAILABLE else '❌'}")
    
    if not VNSTOCK_AVAILABLE:
        print("\n⚠️ Cài: pip install vnstock3")
        return
    
    if not WIDGETS_AVAILABLE:
        print("\n⚠️ Cài: pip install ipywidgets")
        return
    
    print("\n✨ Sẵn sàng!")
    print("\n💡 Mã phổ biến: VCB, HPG, VNM, FPT, VHM")
    print("="*80 + "\n")
    
    app = VNPortfolioRebalancer()
    app.display()


if __name__ == "__main__":
    main()
else:
    # Jupyter mode
    try:
        if WIDGETS_AVAILABLE and VNSTOCK_AVAILABLE:
            app = VNPortfolioRebalancer()
            app.display()
        else:
            print("⚠️ Cần cài đặt:")
            if not VNSTOCK_AVAILABLE:
                print("  pip install vnstock3")
            if not WIDGETS_AVAILABLE:
                print("  pip install ipywidgets")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        print(traceback.format_exc())
