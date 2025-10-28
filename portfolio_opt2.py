import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Import từ PyPortfolioOpt
try:
    from pypfopt import EfficientFrontier, risk_models, expected_returns
    from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
except ImportError:
    try:
        import pypfopt
        from pypfopt.efficient_frontier import EfficientFrontier
        from pypfopt import risk_models, expected_returns
        from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
    except ImportError as e:
        print(f"❌ Lỗi: {e}")
        print("Cài đặt: pip install PyPortfolioOpt")
        raise

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import warnings
warnings.filterwarnings('ignore')

# Thiết lập style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class VNStockDataFetcher:
    """Lấy dữ liệu cổ phiếu Việt Nam"""
    
    @staticmethod
    def get_stock_data(symbol, start_date, end_date):
        try:
            from vnstock import stock_historical_data
            
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            df = stock_historical_data(
                symbol=symbol,
                start_date=start_str,
                end_date=end_str,
                resolution='1D',
                type='stock'
            )
            
            if df is None or df.empty:
                return None
            
            if 'time' in df.columns:
                df.index = pd.to_datetime(df['time'])
            elif 'TradingDate' in df.columns:
                df.index = pd.to_datetime(df['TradingDate'])
            
            if 'close' in df.columns:
                df['Adj Close'] = df['close']
            elif 'Close' in df.columns:
                df['Adj Close'] = df['Close']
            else:
                return None
            
            return df[['Adj Close']]
            
        except ImportError:
            print(f"⚠️ vnstock chưa cài đặt. Không thể lấy {symbol}")
            return None
        except Exception as e:
            print(f"⚠️ Lỗi {symbol}: {str(e)}")
            return None

class EnhancedQuarterlyFundPortfolio:
    def __init__(self):
        self.df = None
        self.quarterly_results = {}
        self.current_quarter = self.get_current_quarter()
        
        self.sample_funds = {
            '🇻🇳 Cổ Phiếu & ETF Việt Nam': {
                'E1VFVN30': 'VN30 ETF',
                'VNM': 'Vinamilk',
                'VIC': 'Vingroup',
                'VHM': 'Vinhomes',
                'GAS': 'PV Gas',
            },
            '🌎 ETF Quốc tế': {
                'SPY': 'S&P 500',
                'QQQ': 'Nasdaq Tech',
                'VTI': 'Total Stock',
                'BND': 'Total Bond',
                'GLD': 'Gold',
            },
        }
        
        self.risk_profiles = {
            'Bảo thủ': {
                'description': 'Ưu tiên bảo toàn vốn',
                'stocks': 25, 'bonds': 65, 'others': 10,
                'max_volatility': 0.12,
                'color': '#4CAF50'
            },
            'Trung bình': {
                'description': 'Cân bằng rủi ro và lợi nhuận',
                'stocks': 50, 'bonds': 40, 'others': 10,
                'max_volatility': 0.15,
                'color': '#FFC107'
            },
            'Tích cực': {
                'description': 'Chấp nhận rủi ro cao',
                'stocks': 70, 'bonds': 20, 'others': 10,
                'max_volatility': 0.20,
                'color': '#FF9800'
            },
        }
        
        self.create_widgets()
    
    def get_current_quarter(self):
        today = datetime.now()
        quarter = (today.month - 1) // 3 + 1
        return f"Q{quarter}/{today.year}"
    
    def get_quarter_dates(self, year, quarter):
        start_month = (quarter - 1) * 3 + 1
        start_date = datetime(year, start_month, 1)
        
        if quarter == 4:
            end_date = datetime(year, 12, 31)
        else:
            end_month = start_month + 3
            end_date = datetime(year, end_month, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    def detect_market(self, symbol):
        vn_stocks = ['E1VFVN30', 'FUEVFVND', 'VNM', 'VIC', 'VHM', 'GAS', 'MSN']
        
        if symbol in vn_stocks or '.VN' in symbol:
            return 'VN'
        else:
            return 'US'
    
    def fetch_mixed_data(self, symbols, start_date, end_date):
        all_data = {}
        vn_symbols = []
        us_symbols = []
        
        for symbol in symbols:
            market = self.detect_market(symbol)
            if market == 'VN':
                vn_symbols.append(symbol)
            else:
                us_symbols.append(symbol)
        
        print(f"📊 {len(vn_symbols)} mã VN, {len(us_symbols)} mã quốc tế")
        
        if vn_symbols:
            print(f"\n🇻🇳 Tải {len(vn_symbols)} mã VN...")
            for symbol in vn_symbols:
                clean_symbol = symbol.replace('.VN', '')
                print(f"  • {clean_symbol}...", end=' ')
                
                df = VNStockDataFetcher.get_stock_data(clean_symbol, start_date, end_date)
                if df is not None and not df.empty:
                    all_data[symbol] = df['Adj Close']
                    print("✓")
                else:
                    print("✗")
        
        if us_symbols:
            print(f"\n🌎 Tải {len(us_symbols)} mã quốc tế...")
            try:
                us_data = yf.download(us_symbols, start=start_date, end=end_date, progress=False)['Adj Close']
                
                if isinstance(us_data, pd.Series):
                    us_data = us_data.to_frame()
                    us_data.columns = [us_symbols[0]]
                
                for symbol in us_symbols:
                    if symbol in us_data.columns:
                        all_data[symbol] = us_data[symbol]
                        print(f"  • {symbol}... ✓")
                    else:
                        print(f"  • {symbol}... ✗")
            except Exception as e:
                print(f"  ⚠️ Lỗi: {str(e)}")
        
        if all_data:
            combined_df = pd.DataFrame(all_data)
            return combined_df
        else:
            return None
    
    def create_widgets(self):
        self.header = widgets.HTML(
            value=f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
                <h1 style='color: white; text-align: center; margin: 0;'>
                    💼 HỆ THỐNG PHÂN BỔ ĐẦU TƯ
                </h1>
                <p style='color: white; text-align: center; margin-top: 10px;'>
                    VN & Quốc tế | {datetime.now().strftime('%d/%m/%Y')}
                </p>
            </div>
            """
        )
        
        self.risk_profile = widgets.Dropdown(
            options=list(self.risk_profiles.keys()),
            value='Trung bình',
            description='Rủi ro:',
            style={'description_width': '100px'}
        )
        
        self.funds_input = widgets.Textarea(
            value='SPY, BND, GLD',
            placeholder='Nhập mã, cách nhau bởi dấu phẩy',
            description='Danh mục:',
            layout=widgets.Layout(width='80%', height='100px')
        )
        
        self.years_back = widgets.IntSlider(
            value=3, min=1, max=10,
            description='Số năm:',
            style={'description_width': '100px'}
        )
        
        self.total_capital = widgets.FloatText(
            value=100000000,
            description='Vốn (VNĐ):',
            style={'description_width': '100px'}
        )
        
        self.analyze_btn = widgets.Button(
            description='🚀 PHÂN TÍCH',
            button_style='success',
            layout=widgets.Layout(width='200px', height='45px')
        )
        self.analyze_btn.on_click(self.run_analysis)
        
        self.output = widgets.Output()
        
        input_box = widgets.VBox([
            widgets.HTML("<h2>🎯 THIẾT LẬP DANH MỤC</h2>"),
            self.risk_profile,
            self.funds_input,
            self.years_back,
            self.total_capital,
            self.analyze_btn,
            self.output
        ])
        
        self.tabs = widgets.Tab()
        self.analysis_output = widgets.Output()
        
        self.tabs.children = [input_box, self.analysis_output]
        self.tabs.set_title(0, '🎯 Thiết Lập')
        self.tabs.set_title(1, '📊 Phân Tích')
    
    def run_analysis(self, b):
        with self.output:
            clear_output()
            print("🔄 Đang phân tích...")
        
        try:
            funds = [f.strip().upper() for f in self.funds_input.value.split(',') if f.strip()]
            
            if len(funds) < 2:
                with self.output:
                    clear_output()
                    print("❌ Cần ít nhất 2 mã!")
                return
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * self.years_back.value)
            
            with self.output:
                clear_output()
                print("📥 Đang tải dữ liệu...\n")
            
            data = self.fetch_mixed_data(funds, start_date, end_date)
            
            if data is None or data.empty:
                with self.output:
                    clear_output()
                    print("❌ Không có dữ liệu!")
                return
            
            if len(data) < 60:
                with self.output:
                    clear_output()
                    print(f"❌ Chỉ có {len(data)} ngày (cần >60)")
                return
            
            data = data.dropna(axis=1, thresh=len(data)*0.7)
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            if len(data.columns) < 2:
                with self.output:
                    clear_output()
                    print("❌ Không đủ dữ liệu hợp lệ!")
                return
            
            self.df = data
            
            with self.output:
                print(f"\n✅ Tải {len(data.columns)} tài sản, {len(data)} ngày")
                print("⏳ Đang tối ưu...")
            
            mu = expected_returns.mean_historical_return(data)
            S = risk_models.sample_cov(data)
            
            profile = self.risk_profiles[self.risk_profile.value]
            
            try:
                ef = EfficientFrontier(mu, S, weight_bounds=(0, 0.4))
                weights = ef.min_volatility()
                cleaned_weights = ef.clean_weights()
                performance = ef.portfolio_performance(verbose=False)
            except Exception as e:
                with self.output:
                    print(f"⚠️ Lỗi tối ưu: {e}")
                return
            
            self.weights = cleaned_weights
            self.performance = performance
            
            with self.output:
                print(f"✅ Hoàn tất!")
                print(f"📈 Lợi nhuận: {performance[0]*100:.2f}%")
                print(f"📊 Volatility: {performance[1]*100:.2f}%")
                print(f"⭐ Sharpe: {performance[2]:.2f}")
            
            self.display_analysis()
            self.tabs.selected_index = 1
            
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
                import traceback
                print(traceback.format_exc())
    
    def display_analysis(self):
        with self.analysis_output:
            clear_output()
            
            print("="*80)
            print(" "*25 + "📊 KẾT QUẢ PHÂN TÍCH")
            print("="*80)
            
            print(f"\n📅 Kỳ: {self.df.index[0].strftime('%d/%m/%Y')} → {self.df.index[-1].strftime('%d/%m/%Y')}")
            print(f"💼 Số tài sản: {len([w for w in self.weights.values() if w > 0])}")
            print(f"💰 Vốn: {self.total_capital.value:,.0f} VNĐ")
            
            print("\n" + "="*80)
            print(" "*25 + "🎯 HIỆU SUẤT KỲ VỌNG")
            print("="*80)
            
            expected_return = self.performance[0] * 100
            volatility = self.performance[1] * 100
            sharpe = self.performance[2]
            
            print(f"\n{'📈 Lợi nhuận/năm:':<40} {expected_return:>10.2f}%")
            print(f"{'📊 Độ biến động:':<40} {volatility:>10.2f}%")
            print(f"{'⭐ Sharpe Ratio:':<40} {sharpe:>10.2f}")
            
            if sharpe > 2:
                print(f"{'🏆 Đánh giá:':<40} ⭐⭐⭐ Xuất sắc")
            elif sharpe > 1:
                print(f"{'🏆 Đánh giá:':<40} ⭐⭐ Tốt")
            else:
                print(f"{'🏆 Đánh giá:':<40} ⭐ Chấp nhận")
            
            print("\n" + "="*80)
            print(" "*30 + "💼 TỶ TRỌNG")
            print("="*80)
            
            weights_df = pd.DataFrame.from_dict(self.weights, orient='index', columns=['Tỷ trọng'])
            weights_df = weights_df[weights_df['Tỷ trọng'] > 0].sort_values('Tỷ trọng', ascending=False)
            weights_df['%'] = (weights_df['Tỷ trọng'] * 100).round(2)
            
            print(f"\n{'Mã':<15} {'Tỷ trọng':<12} {'Biểu đồ'}")
            print("-"*80)
            
            for idx, row in weights_df.iterrows():
                bar = "█" * int(row['%'] / 2)
                market = "🇻🇳" if self.detect_market(idx) == 'VN' else "🌎"
                print(f"{market} {idx:<12} {row['%']:>6.2f}%     {bar}")
            
            print("\n" + "="*80)
            print(" "*25 + "💰 PHÂN BỔ VỐN")
            print("="*80)
            
            latest_prices = get_latest_prices(self.df)
            da = DiscreteAllocation(self.weights, latest_prices, 
                                   total_portfolio_value=self.total_capital.value)
            allocation, leftover = da.greedy_portfolio()
            
            print(f"\n{'Mã':<15} {'SL':<10} {'Giá':<15} {'Tổng (VNĐ)':<15}")
            print("-"*80)
            
            total_invested = 0
            for ticker in weights_df.index:
                if ticker in allocation:
                    shares = allocation[ticker]
                    price = latest_prices[ticker]
                    total = shares * price
                    total_invested += total
                    print(f"{ticker:<15} {shares:<10} ${price:>10,.2f}   {total:>14,.0f}")
            
            print("-"*80)
            print(f"{'Tổng đầu tư:':<40} {total_invested:>14,.0f} VNĐ")
            print(f"{'Tiền mặt:':<40} {leftover:>14,.0f} VNĐ")
            
            self.plot_analysis()
    
    def plot_analysis(self):
        weights_df = pd.DataFrame.from_dict(self.weights, orient='index', columns=['Tỷ trọng'])
        weights_df = weights_df[weights_df['Tỷ trọng'] > 0].sort_values('Tỷ trọng', ascending=False)
        weights_df['%'] = (weights_df['Tỷ trọng'] * 100).round(2)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Pie chart
        colors = plt.cm.Set3(range(len(weights_df)))
        axes[0, 0].pie(weights_df['%'], labels=weights_df.index, autopct='%1.1f%%', colors=colors)
        axes[0, 0].set_title('💼 Phân Bổ Tỷ Trọng', fontsize=12, fontweight='bold')
        
        # Bar chart
        weights_df.plot(kind='barh', ax=axes[0, 1], color=colors, legend=False, y='%')
        axes[0, 1].set_xlabel('Tỷ trọng (%)')
        axes[0, 1].set_title('📊 Chi Tiết', fontsize=12, fontweight='bold')
        axes[0, 1].grid(axis='x', alpha=0.3)
        
        # Price history
        normalized = self.df / self.df.iloc[0] * 100
        for col in normalized.columns:
            if col in self.weights and self.weights[col] > 0:
                axes[1, 0].plot(normalized.index, normalized[col], label=col, linewidth=2)
        axes[1, 0].set_ylabel('Giá chuẩn hóa')
        axes[1, 0].set_title('📈 Lịch Sử Giá', fontsize=12, fontweight='bold')
        axes[1, 0].legend(fontsize=8)
        axes[1, 0].grid(alpha=0.3)
        axes[1, 0].axhline(y=100, color='red', linestyle='--', alpha=0.5)
        
        # Correlation
        selected_cols = [col for col in self.df.columns if col in self.weights and self.weights[col] > 0]
        corr = self.df[selected_cols].corr()
        im = axes[1, 1].imshow(corr, cmap='RdYlGn', vmin=-1, vmax=1)
        axes[1, 1].set_xticks(range(len(corr)))
        axes[1, 1].set_yticks(range(len(corr)))
        axes[1, 1].set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=9)
        axes[1, 1].set_yticklabels(corr.columns, fontsize=9)
        axes[1, 1].set_title('🔗 Tương Quan', fontsize=12, fontweight='bold')
        plt.colorbar(im, ax=axes[1, 1])
        
        plt.tight_layout()
        plt.show()
    
    def display(self):
        display(self.header)
        display(self.tabs)

# Khởi động
print("="*80)
print(" "*20 + "🚀 HỆ THỐNG PHÂN BỔ ĐẦU TƯ")
print("="*80)
print("\n📦 Cài đặt:")
print("   pip install yfinance PyPortfolioOpt ipywidgets vnstock")
print("\n✨ Sẵn sàng!")
print("="*80 + "\n")

app = EnhancedQuarterlyFundPortfolio()
app.display()
