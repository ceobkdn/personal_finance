import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Import PyPortfolioOpt
try:
    from pypfopt import EfficientFrontier, risk_models, expected_returns
    from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
except ImportError:
    print("❌ Cài đặt: pip install PyPortfolioOpt")
    raise

import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
warnings.filterwarnings('ignore')

# Thiết lập style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class DataFetcher:
    """Lấy dữ liệu cổ phiếu từ nhiều nguồn"""
    
    @staticmethod
    def get_vn_stock(symbol, start_date, end_date):
        """Lấy dữ liệu VN từ nhiều nguồn"""
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Phương pháp 1: Thử vnstock3 (phiên bản mới)
        try:
            from vnstock3 import Vnstock
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            df = stock.quote.history(start=start_str, end=end_str)
            
            if df is not None and not df.empty:
                if 'time' in df.columns:
                    df.index = pd.to_datetime(df['time'])
                if 'close' in df.columns:
                    df['Adj Close'] = df['close']
                elif 'Close' in df.columns:
                    df['Adj Close'] = df['Close']
                
                if 'Adj Close' in df.columns:
                    result = df[['Adj Close']]
                    # Loại bỏ duplicate index
                    result = result[~result.index.duplicated(keep='last')]
                    return result
        except ImportError:
            pass
        except Exception as e:
            pass
        
        # Phương pháp 2: Thử vnstock (phiên bản cũ)
        try:
            from vnstock import stock_historical_data
            
            df = stock_historical_data(
                symbol=symbol,
                start_date=start_str,
                end_date=end_str,
                resolution='1D',
                type='stock'
            )
            
            if df is not None and not df.empty:
                if 'time' in df.columns:
                    df.index = pd.to_datetime(df['time'])
                elif 'TradingDate' in df.columns:
                    df.index = pd.to_datetime(df['TradingDate'])
                
                if 'close' in df.columns:
                    df['Adj Close'] = df['close']
                elif 'Close' in df.columns:
                    df['Adj Close'] = df['Close']
                
                if 'Adj Close' in df.columns:
                    result = df[['Adj Close']]
                    # Loại bỏ duplicate index
                    result = result[~result.index.duplicated(keep='last')]
                    return result
        except Exception as e:
            pass
        
        # Phương pháp 3: Thử yfinance với .VN suffix
        try:
            import pandas_datareader as pdr
            vn_symbol = f"{symbol}.VN"
            df = pdr.get_data_yahoo(vn_symbol, start=start_date, end=end_date)
            if df is not None and not df.empty and 'Adj Close' in df.columns:
                result = df[['Adj Close']]
                # Loại bỏ duplicate index
                result = result[~result.index.duplicated(keep='last')]
                return result
        except Exception as e:
            pass
        
        # Phương pháp 4: Thử với SSI API (nếu có)
        try:
            from vnstock import stock_historical_data
            
            # Thử với type='index' cho ETF
            df = stock_historical_data(
                symbol=symbol,
                start_date=start_str,
                end_date=end_str,
                resolution='1D',
                type='index'
            )
            
            if df is not None and not df.empty:
                if 'time' in df.columns:
                    df.index = pd.to_datetime(df['time'])
                if 'close' in df.columns:
                    df['Adj Close'] = df['close']
                elif 'Close' in df.columns:
                    df['Adj Close'] = df['Close']
                
                if 'Adj Close' in df.columns:
                    result = df[['Adj Close']]
                    # Loại bỏ duplicate index
                    result = result[~result.index.duplicated(keep='last')]
                    return result
        except Exception as e:
            pass
        
        return None
    
    @staticmethod
    def get_us_stock(symbol, start_date, end_date):
        """Lấy dữ liệu US từ pandas-datareader"""
        try:
            import pandas_datareader as pdr
            df = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
            if df is not None and not df.empty and 'Adj Close' in df.columns:
                result = df[['Adj Close']]
                # Loại bỏ duplicate index
                result = result[~result.index.duplicated(keep='last')]
                return result
        except ImportError:
            print(f"⚠️ Cài đặt: pip install pandas-datareader")
            return None
        except Exception as e:
            print(f"⚠️ Lỗi {symbol}: {str(e)}")
            return None

class PortfolioOptimizer:
    def __init__(self):
        self.df = None
        self.weights = None
        self.performance = None
        
        self.vn_stocks = ['E1VFVN30', 'FUEVFVND', 'FUESSV30', 'FUESSVFL', 'VNM', 'VIC', 
                          'VHM', 'GAS', 'MSN', 'HPG', 'TCB', 'MBB', 'VCB', 'BID', 
                          'CTG', 'FPT', 'MWG', 'VRE', 'PLX', 'GVR']
        
        self.risk_profiles = {
            'Bảo thủ': {
                'description': 'Ưu tiên bảo toàn vốn',
                'max_volatility': 0.12,
                'color': '#4CAF50'
            },
            'Trung bình': {
                'description': 'Cân bằng rủi ro và lợi nhuận',
                'max_volatility': 0.15,
                'color': '#FFC107'
            },
            'Tích cực': {
                'description': 'Chấp nhận rủi ro cao',
                'max_volatility': 0.20,
                'color': '#FF9800'
            },
        }
        
        self.create_widgets()
    
    def detect_market(self, symbol):
        """Xác định thị trường (VN hay US)"""
        if symbol in self.vn_stocks or '.VN' in symbol:
            return 'VN'
        return 'US'
    
    def fetch_data(self, symbols, start_date, end_date):
        """Lấy dữ liệu từ nhiều nguồn"""
        all_data = {}
        failed_symbols = []
        
        for symbol in symbols:
            market = self.detect_market(symbol)
            clean_symbol = symbol.replace('.VN', '')
            
            print(f"  • {clean_symbol}...", end=' ', flush=True)
            
            if market == 'VN':
                df = DataFetcher.get_vn_stock(clean_symbol, start_date, end_date)
            else:
                df = DataFetcher.get_us_stock(clean_symbol, start_date, end_date)
            
            if df is not None and not df.empty:
                # Đảm bảo không có duplicate index
                if df.index.duplicated().any():
                    print(f"(loại bỏ {df.index.duplicated().sum()} ngày trùng)...", end=' ')
                    df = df[~df.index.duplicated(keep='last')]
                
                all_data[symbol] = df['Adj Close']
                print(f"✓ ({len(df)} ngày)")
            else:
                print("✗")
                failed_symbols.append(clean_symbol)
        
        if failed_symbols:
            print(f"\n⚠️  Không tải được: {', '.join(failed_symbols)}")
            print(f"💡 Kiểm tra lại mã hoặc thử:")
            print(f"   - Thêm .VN (VD: {failed_symbols[0]}.VN)")
            print(f"   - Kiểm tra trên: https://www.vndirect.com.vn")
        
        if all_data:
            # Tạo DataFrame và đảm bảo index không trùng
            combined_df = pd.DataFrame(all_data)
            
            # Loại bỏ duplicate index trong DataFrame tổng hợp
            if combined_df.index.duplicated().any():
                print(f"\n🔧 Phát hiện {combined_df.index.duplicated().sum()} ngày trùng trong dữ liệu tổng hợp, đang xử lý...")
                combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
            
            return combined_df
        return None
    
    def clean_data(self, data):
        """Làm sạch và xử lý dữ liệu"""
        # Loại bỏ duplicate index ngay từ đầu
        if data.index.duplicated().any():
            print(f"  🔧 Loại bỏ {data.index.duplicated().sum()} ngày trùng lặp...")
            data = data[~data.index.duplicated(keep='last')]
        
        # Loại bỏ cột có quá nhiều NaN
        min_data_points = int(len(data) * 0.8)
        data = data.dropna(axis=1, thresh=min_data_points)
        
        # Forward fill, backward fill
        data = data.fillna(method='ffill').fillna(method='bfill')
        
        # Loại bỏ các hàng còn NaN
        data = data.dropna()
        
        # Loại bỏ các cột có giá trị = 0
        data = data.loc[:, (data != 0).all(axis=0)]
        
        # Loại bỏ các cột có giá trị âm
        data = data.loc[:, (data > 0).all(axis=0)]
        
        # Kiểm tra giá trị vô cùng
        data = data.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Kiểm tra lại duplicate sau khi xử lý
        if data.index.duplicated().any():
            data = data[~data.index.duplicated(keep='last')]
        
        return data
    
    def optimize_portfolio(self, data):
        """Tối ưu hóa danh mục với nhiều phương pháp fallback"""
        
        mode = self.allocation_mode.value
        n_assets = len(data.columns)
        
        # Chế độ phân bổ đều
        if mode == 'equal':
            print("  Chế độ: Phân bổ đều")
            weights = {col: 1/n_assets for col in data.columns}
            
            # Tính hiệu suất
            returns = data.pct_change().dropna()
            portfolio_return = np.sum(returns.mean() * np.array(list(weights.values()))) * 252
            portfolio_std = np.sqrt(np.dot(np.array(list(weights.values())).T, 
                                           np.dot(returns.cov() * 252, 
                                                  np.array(list(weights.values())))))
            sharpe = portfolio_return / portfolio_std if portfolio_std > 0 else 0
            
            performance = (portfolio_return, portfolio_std, sharpe)
            return weights, performance, "Equal Weight (Đều nhau)"
        
        # Xác định ràng buộc tỷ trọng
        if mode == 'min5':
            weight_bounds = (0.05, 1.0)
            mode_desc = "Tối ưu (min 5%)"
        elif mode == 'min10':
            weight_bounds = (0.10, 1.0)
            mode_desc = "Tối ưu (min 10%)"
        else:  # optimal
            weight_bounds = (0, 1.0)
            mode_desc = "Tối ưu (cho phép 0%)"
        
        # Phương pháp 1: Min Volatility với ràng buộc
        try:
            print(f"  Thử phương pháp 1: Min Volatility ({mode_desc})...")
            mu = expected_returns.mean_historical_return(data)
            S = risk_models.sample_cov(data)
            
            # Thêm regularization cho ma trận hiệp phương sai
            S_regularized = S + np.eye(len(S)) * 0.001
            
            ef = EfficientFrontier(mu, S_regularized, weight_bounds=weight_bounds)
            weights = ef.min_volatility()
            cleaned_weights = ef.clean_weights()
            performance = ef.portfolio_performance(verbose=False)
            
            return cleaned_weights, performance, f"Min Volatility ({mode_desc})"
        except Exception as e:
            print(f"    ✗ Thất bại: {e}")
        
        # Phương pháp 2: Max Sharpe với constraints lỏng hơn
        try:
            print(f"  Thử phương pháp 2: Max Sharpe ({mode_desc})...")
            mu = expected_returns.mean_historical_return(data)
            S = risk_models.sample_cov(data)
            S_regularized = S + np.eye(len(S)) * 0.001
            
            ef = EfficientFrontier(mu, S_regularized, weight_bounds=weight_bounds)
            weights = ef.max_sharpe()
            cleaned_weights = ef.clean_weights()
            performance = ef.portfolio_performance(verbose=False)
            
            return cleaned_weights, performance, f"Max Sharpe ({mode_desc})"
        except Exception as e:
            print(f"    ✗ Thất bại: {e}")
        
        # Phương pháp 3: Nếu có ràng buộc min%, thử lại với (0, 1)
        if mode in ['min5', 'min10']:
            try:
                print("  Thử phương pháp 3: Tối ưu không ràng buộc...")
                mu = expected_returns.mean_historical_return(data)
                S = risk_models.sample_cov(data)
                S_regularized = S + np.eye(len(S)) * 0.001
                
                ef = EfficientFrontier(mu, S_regularized, weight_bounds=(0, 1))
                weights = ef.min_volatility()
                cleaned_weights = ef.clean_weights()
                performance = ef.portfolio_performance(verbose=False)
                
                return cleaned_weights, performance, "Min Volatility (Tối ưu)"
            except Exception as e:
                print(f"    ✗ Thất bại: {e}")
        
        # Phương pháp 4: Equal Weighting (fallback cuối cùng)
        try:
            print("  Thử phương pháp 4: Equal Weighting...")
            weights = {col: 1/n_assets for col in data.columns}
            
            # Tính hiệu suất
            returns = data.pct_change().dropna()
            portfolio_return = np.sum(returns.mean() * np.array(list(weights.values()))) * 252
            portfolio_std = np.sqrt(np.dot(np.array(list(weights.values())).T, 
                                           np.dot(returns.cov() * 252, 
                                                  np.array(list(weights.values())))))
            sharpe = portfolio_return / portfolio_std if portfolio_std > 0 else 0
            
            performance = (portfolio_return, portfolio_std, sharpe)
            
            return weights, performance, "Equal Weight (Đều nhau)"
        except Exception as e:
            print(f"    ✗ Thất bại: {e}")
            raise
    
    def create_widgets(self):
        """Tạo giao diện"""
        self.header = widgets.HTML(
            value=f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
                <h1 style='color: white; text-align: center; margin: 0;'>
                    💼 PHÂN BỔ ĐẦU TƯ TỐI ƯU
                </h1>
                <p style='color: white; text-align: center; margin-top: 10px;'>
                    VN & International Markets | {datetime.now().strftime('%d/%m/%Y')}
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
        
        self.allocation_mode = widgets.Dropdown(
            options=[
                ('Tối ưu (cho phép 0%)', 'optimal'),
                ('Phân bổ đều', 'equal'),
                ('Tối thiểu 5% mỗi mã', 'min5'),
                ('Tối thiểu 10% mỗi mã', 'min10')
            ],
            value='optimal',
            description='Chế độ:',
            style={'description_width': '100px'}
        )
        
        self.funds_input = widgets.Textarea(
            value='VNM, VIC, GAS',
            placeholder='Nhập mã, cách nhau bởi dấu phẩy\nVD: VNM, VIC, GAS hoặc SPY, QQQ, BND',
            description='Danh mục:',
            layout=widgets.Layout(width='80%', height='100px')
        )
        
        self.years_back = widgets.IntSlider(
            value=2, min=1, max=5,
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
        
        # Thêm mẫu danh mục
        sample_portfolios = widgets.HTML(
            value="""
            <div style='background: #f5f5f5; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                <b>📋 Danh mục mẫu:</b><br>
                • VN Bluechips: VNM, VIC, VHM, GAS, HPG<br>
                • VN ETF: E1VFVN30, FUEVFVND, FUESSV30<br>
                • VN Tech: FPT, MWG<br>
                • US Index: SPY, QQQ, DIA, BND<br>
                • Balanced: SPY, BND, GLD, VNM, GAS<br><br>
                <b>💡 Chế độ phân bổ:</b><br>
                • <b>Tối ưu (0%):</b> Thuật toán chọn mã tốt nhất, loại mã kém<br>
                • <b>Phân bổ đều:</b> Chia đều 10 mã = 10% mỗi mã<br>
                • <b>Tối thiểu 5-10%:</b> Mỗi mã ít nhất 5-10%, còn lại tối ưu
            </div>
            """
        )
        
        input_box = widgets.VBox([
            widgets.HTML("<h2>🎯 THIẾT LẬP DANH MỤC</h2>"),
            sample_portfolios,
            self.risk_profile,
            self.allocation_mode,
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
        """Chạy phân tích"""
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
            
            data = self.fetch_data(funds, start_date, end_date)
            
            if data is None or data.empty:
                with self.output:
                    clear_output()
                    print("❌ Không có dữ liệu!")
                return
            
            with self.output:
                print(f"\n✅ Tải được {len(data.columns)} tài sản, {len(data)} ngày")
                print("🧹 Đang làm sạch dữ liệu...")
            
            data = self.clean_data(data)
            
            if len(data) < 60:
                with self.output:
                    clear_output()
                    print(f"❌ Chỉ có {len(data)} ngày hợp lệ (cần >60)")
                return
            
            if len(data.columns) < 2:
                with self.output:
                    clear_output()
                    print("❌ Không đủ tài sản hợp lệ sau khi làm sạch!")
                return
            
            self.df = data
            
            with self.output:
                print(f"✅ Dữ liệu sạch: {len(data.columns)} tài sản, {len(data)} ngày")
                print("⏳ Đang tối ưu danh mục...")
            
            # Tối ưu danh mục
            weights, performance, method = self.optimize_portfolio(data)
            
            self.weights = weights
            self.performance = performance
            self.method = method
            
            with self.output:
                print(f"✅ Hoàn tất! (Phương pháp: {method})")
                print(f"📈 Lợi nhuận kỳ vọng: {performance[0]*100:.2f}%/năm")
                print(f"📊 Volatility: {performance[1]*100:.2f}%")
                print(f"⭐ Sharpe Ratio: {performance[2]:.2f}")
            
            self.display_analysis()
            self.tabs.selected_index = 1
            
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
                import traceback
                print("\n📋 Chi tiết lỗi:")
                print(traceback.format_exc())
    
    def display_analysis(self):
        """Hiển thị kết quả phân tích"""
        with self.analysis_output:
            clear_output()
            
            print("="*80)
            print(" "*25 + "📊 KẾT QUẢ PHÂN TÍCH")
            print("="*80)
            
            print(f"\n📅 Kỳ phân tích: {self.df.index[0].strftime('%d/%m/%Y')} → {self.df.index[-1].strftime('%d/%m/%Y')}")
            print(f"💼 Số tài sản: {len([w for w in self.weights.values() if w > 0])}/{len(self.df.columns)}")
            print(f"💰 Vốn đầu tư: {self.total_capital.value:,.0f} VNĐ")
            print(f"🎯 Phương pháp: {self.method}")
            
            print("\n" + "="*80)
            print(" "*25 + "📈 HIỆU SUẤT KỲ VỌNG")
            print("="*80)
            
            expected_return = self.performance[0] * 100
            volatility = self.performance[1] * 100
            sharpe = self.performance[2]
            
            print(f"\n{'📈 Lợi nhuận kỳ vọng/năm:':<40} {expected_return:>10.2f}%")
            print(f"{'📊 Độ biến động (Volatility):':<40} {volatility:>10.2f}%")
            print(f"{'⭐ Sharpe Ratio:':<40} {sharpe:>10.2f}")
            
            if sharpe > 2:
                rating = "⭐⭐⭐ Xuất sắc"
            elif sharpe > 1:
                rating = "⭐⭐ Tốt"
            elif sharpe > 0.5:
                rating = "⭐ Chấp nhận được"
            else:
                rating = "⚠️ Cần cải thiện"
            print(f"{'🏆 Đánh giá:':<40} {rating}")
            
            print("\n" + "="*80)
            print(" "*30 + "💼 TỶ TRỌNG")
            print("="*80)
            
            weights_df = pd.DataFrame.from_dict(self.weights, orient='index', columns=['Tỷ trọng'])
            weights_df = weights_df[weights_df['Tỷ trọng'] > 0.001].sort_values('Tỷ trọng', ascending=False)
            weights_df['%'] = (weights_df['Tỷ trọng'] * 100).round(2)
            
            print(f"\n{'Mã':<15} {'Tỷ trọng':<12} {'Biểu đồ'}")
            print("-"*80)
            
            for idx, row in weights_df.iterrows():
                bar = "█" * int(row['%'] / 2)
                market = "🇻🇳" if self.detect_market(idx) == 'VN' else "🌎"
                print(f"{market} {idx:<12} {row['%']:>6.2f}%     {bar}")
            
            print("\n" + "="*80)
            print(f"Tổng tỷ trọng: {weights_df['%'].sum():.2f}%")
            
            self.plot_analysis()
    
    def plot_analysis(self):
        """Vẽ biểu đồ phân tích"""
        weights_df = pd.DataFrame.from_dict(self.weights, orient='index', columns=['Tỷ trọng'])
        weights_df = weights_df[weights_df['Tỷ trọng'] > 0.001].sort_values('Tỷ trọng', ascending=False)
        weights_df['%'] = (weights_df['Tỷ trọng'] * 100).round(2)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Pie chart
        colors = plt.cm.Set3(range(len(weights_df)))
        axes[0, 0].pie(weights_df['%'], labels=weights_df.index, autopct='%1.1f%%', 
                       colors=colors, startangle=90)
        axes[0, 0].set_title('💼 Phân Bổ Tỷ Trọng', fontsize=12, fontweight='bold')
        
        # Bar chart
        weights_df.plot(kind='barh', ax=axes[0, 1], color=colors, legend=False, y='%')
        axes[0, 1].set_xlabel('Tỷ trọng (%)')
        axes[0, 1].set_title('📊 Chi Tiết Tỷ Trọng', fontsize=12, fontweight='bold')
        axes[0, 1].grid(axis='x', alpha=0.3)
        
        # Price history
        normalized = self.df / self.df.iloc[0] * 100
        for col in normalized.columns:
            if col in self.weights and self.weights[col] > 0.001:
                axes[1, 0].plot(normalized.index, normalized[col], label=col, linewidth=2)
        axes[1, 0].set_ylabel('Giá chuẩn hóa (Base=100)')
        axes[1, 0].set_title('📈 Lịch Sử Giá', fontsize=12, fontweight='bold')
        axes[1, 0].legend(fontsize=8, loc='best')
        axes[1, 0].grid(alpha=0.3)
        axes[1, 0].axhline(y=100, color='red', linestyle='--', alpha=0.5, linewidth=1)
        
        # Correlation
        selected_cols = [col for col in self.df.columns if col in self.weights and self.weights[col] > 0.001]
        if len(selected_cols) > 1:
            corr = self.df[selected_cols].corr()
            im = axes[1, 1].imshow(corr, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
            axes[1, 1].set_xticks(range(len(corr)))
            axes[1, 1].set_yticks(range(len(corr)))
            axes[1, 1].set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=9)
            axes[1, 1].set_yticklabels(corr.columns, fontsize=9)
            axes[1, 1].set_title('🔗 Ma Trận Tương Quan', fontsize=12, fontweight='bold')
            
            # Thêm giá trị tương quan
            for i in range(len(corr)):
                for j in range(len(corr)):
                    text = axes[1, 1].text(j, i, f'{corr.iloc[i, j]:.2f}',
                                          ha="center", va="center", color="black", fontsize=8)
            
            plt.colorbar(im, ax=axes[1, 1])
        else:
            axes[1, 1].text(0.5, 0.5, 'Cần >1 tài sản\nđể hiển thị tương quan', 
                           ha='center', va='center', fontsize=12)
            axes[1, 1].set_title('🔗 Ma Trận Tương Quan', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def display(self):
        """Hiển thị giao diện"""
        display(self.header)
        display(self.tabs)

# Khởi động
"""
print("="*80)
print(" "*20 + "🚀 HỆ THỐNG PHÂN BỔ ĐẦU TƯ")
print("="*80)
print("\n📦 Yêu cầu:")
print("   pip install PyPortfolioOpt ipywidgets pandas-datareader")
print("   pip install vnstock  # (optional, cho cổ phiếu VN)")
print("\n✨ Sẵn sàng! Python 3.8+ Compatible")
print("="*80 + "\n")
"""
app = PortfolioOptimizer()
app.display()
