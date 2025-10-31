"""
Portfolio Optimizer & Rebalancer Pro
Ứng dụng chuyên nghiệp tối ưu và cân bằng danh mục đầu tư
VN & International Markets
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Import PyPortfolioOpt
try:
    from pypfopt import EfficientFrontier, risk_models, expected_returns
    PYPFOPT_AVAILABLE = True
except ImportError:
    PYPFOPT_AVAILABLE = False
    print("⚠️ Cài đặt: pip install PyPortfolioOpt")

# Import ipywidgets
try:
    import ipywidgets as widgets
    from IPython.display import display, clear_output
    WIDGETS_AVAILABLE = True
except ImportError:
    WIDGETS_AVAILABLE = False
    print("⚠️ Cài đặt: pip install ipywidgets")

warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10


# ==================== DATA FETCHER ====================

class DataFetcher:
    """Lấy dữ liệu cổ phiếu từ nhiều nguồn"""
    
    @staticmethod
    def get_vn_stock(symbol, start_date, end_date):
        """Lấy dữ liệu VN từ nhiều nguồn"""
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Phương pháp 1: vnstock3
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
                    result = result[~result.index.duplicated(keep='last')]
                    return result
        except:
            pass
        
        # Phương pháp 2: vnstock cũ
        try:
            from vnstock import stock_historical_data
            df = stock_historical_data(
                symbol=symbol, start_date=start_str, end_date=end_str,
                resolution='1D', type='stock'
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
                    result = result[~result.index.duplicated(keep='last')]
                    return result
        except:
            pass
        
        # Phương pháp 3: yfinance
        try:
            import pandas_datareader as pdr
            vn_symbol = f"{symbol}.VN"
            df = pdr.get_data_yahoo(vn_symbol, start=start_date, end=end_date)
            if df is not None and not df.empty and 'Adj Close' in df.columns:
                result = df[['Adj Close']]
                result = result[~result.index.duplicated(keep='last')]
                return result
        except:
            pass
        
        return None
    
    @staticmethod
    def get_us_stock(symbol, start_date, end_date):
        """Lấy dữ liệu US"""
        try:
            import pandas_datareader as pdr
            df = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
            if df is not None and not df.empty and 'Adj Close' in df.columns:
                result = df[['Adj Close']]
                result = result[~result.index.duplicated(keep='last')]
                return result
        except:
            return None
    
    @staticmethod
    def get_latest_price(symbol, market='VN'):
        """Lấy giá mới nhất"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        if market == 'VN':
            df = DataFetcher.get_vn_stock(symbol, start_date, end_date)
        else:
            df = DataFetcher.get_us_stock(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            return df['Adj Close'].iloc[-1]
        return None


# ==================== MAIN APP ====================

class PortfolioProApp:
    """Ứng dụng chính"""
    
    def __init__(self):
        self.df = None
        self.weights = None
        self.performance = None
        self.method = None
        self.current_portfolio = None
        self.rebalanced_portfolio = None
        
        # Danh sách mã VN
        self.vn_stocks = ['E1VFVN30', 'FUEVFVND', 'FUESSV30', 'FUESSVFL', 
                          'VNM', 'VIC', 'VHM', 'GAS', 'MSN', 'HPG', 
                          'TCB', 'MBB', 'VCB', 'BID', 'CTG', 'FPT', 
                          'MWG', 'VRE', 'PLX', 'GVR']
        
        if WIDGETS_AVAILABLE:
            self.create_widgets()
    
    def detect_market(self, symbol):
        """Xác định thị trường"""
        if symbol in self.vn_stocks or '.VN' in symbol:
            return 'VN'
        return 'US'
    
    def fetch_data(self, symbols, start_date, end_date):
        """Lấy dữ liệu"""
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
                if df.index.duplicated().any():
                    df = df[~df.index.duplicated(keep='last')]
                all_data[symbol] = df['Adj Close']
                print(f"✓ ({len(df)} ngày)")
            else:
                print("✗")
                failed_symbols.append(clean_symbol)
        
        if failed_symbols:
            print(f"\n⚠️ Không tải được: {', '.join(failed_symbols)}")
        
        if all_data:
            combined_df = pd.DataFrame(all_data)
            if combined_df.index.duplicated().any():
                combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
            return combined_df
        return None
    
    def clean_data(self, data):
        """Làm sạch dữ liệu"""
        if data.index.duplicated().any():
            data = data[~data.index.duplicated(keep='last')]
        
        min_data_points = int(len(data) * 0.8)
        data = data.dropna(axis=1, thresh=min_data_points)
        data = data.fillna(method='ffill').fillna(method='bfill')
        data = data.dropna()
        data = data.loc[:, (data != 0).all(axis=0)]
        data = data.loc[:, (data > 0).all(axis=0)]
        data = data.replace([np.inf, -np.inf], np.nan).dropna()
        
        if data.index.duplicated().any():
            data = data[~data.index.duplicated(keep='last')]
        
        return data
    
    def optimize_portfolio(self, data, mode='optimal'):
        """Tối ưu danh mục"""
        n_assets = len(data.columns)
        
        # Phân bổ đều
        if mode == 'equal':
            weights = {col: 1/n_assets for col in data.columns}
            returns = data.pct_change().dropna()
            portfolio_return = np.sum(returns.mean() * np.array(list(weights.values()))) * 252
            portfolio_std = np.sqrt(np.dot(np.array(list(weights.values())).T, 
                                           np.dot(returns.cov() * 252, 
                                                  np.array(list(weights.values())))))
            sharpe = portfolio_return / portfolio_std if portfolio_std > 0 else 0
            performance = (portfolio_return, portfolio_std, sharpe)
            return weights, performance, "Equal Weight"
        
        # Xác định ràng buộc
        if mode == 'min5':
            weight_bounds = (0.05, 1.0)
            mode_desc = "min 5%"
        elif mode == 'min10':
            weight_bounds = (0.10, 1.0)
            mode_desc = "min 10%"
        else:
            weight_bounds = (0, 1.0)
            mode_desc = "optimal"
        
        # Tối ưu với PyPortfolioOpt
        try:
            mu = expected_returns.mean_historical_return(data)
            S = risk_models.sample_cov(data)
            S_regularized = S + np.eye(len(S)) * 0.001
            
            ef = EfficientFrontier(mu, S_regularized, weight_bounds=weight_bounds)
            weights = ef.min_volatility()
            cleaned_weights = ef.clean_weights()
            performance = ef.portfolio_performance(verbose=False)
            
            return cleaned_weights, performance, f"Min Volatility ({mode_desc})"
        except Exception as e:
            # Fallback: Equal weight
            weights = {col: 1/n_assets for col in data.columns}
            returns = data.pct_change().dropna()
            portfolio_return = np.sum(returns.mean() * np.array(list(weights.values()))) * 252
            portfolio_std = np.sqrt(np.dot(np.array(list(weights.values())).T, 
                                           np.dot(returns.cov() * 252, 
                                                  np.array(list(weights.values())))))
            sharpe = portfolio_return / portfolio_std if portfolio_std > 0 else 0
            performance = (portfolio_return, portfolio_std, sharpe)
            return weights, performance, "Equal Weight (Fallback)"
    
    def create_widgets(self):
        """Tạo giao diện"""
        
        # ===== HEADER =====
        self.header = widgets.HTML(
            value=f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 35px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
                <h1 style='color: white; text-align: center; margin: 0; font-size: 32px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                    💼 PORTFOLIO PRO
                </h1>
                <p style='color: #e0e0e0; text-align: center; margin-top: 12px; font-size: 16px;'>
                    Tối ưu & Cân bằng Danh mục Đầu tư Chuyên nghiệp
                </p>
                <p style='color: #b0b0b0; text-align: center; margin-top: 5px; font-size: 13px;'>
                    🇻🇳 Vietnam & 🌎 International Markets | {datetime.now().strftime('%d/%m/%Y')}
                </p>
            </div>
            """
        )
        
        # ===== TAB 1: OPTIMIZE =====
        self.create_optimize_widgets()
        
        # ===== TAB 2: REBALANCE =====
        self.create_rebalance_widgets()
        
        # ===== MAIN TABS =====
        self.main_tabs = widgets.Tab()
        self.main_tabs.children = [self.optimize_tab, self.rebalance_tab]
        self.main_tabs.set_title(0, '📈 Tối Ưu Danh Mục')
        self.main_tabs.set_title(1, '⚖️ Cân Bằng Danh Mục')
    
    def create_optimize_widgets(self):
        """Tab tối ưu danh mục"""
        
        # Hướng dẫn
        guide = widgets.HTML(
            value="""
            <div style='background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                        padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2196F3;'>
                <h3 style='margin-top: 0; color: #1565c0;'>📖 Hướng dẫn sử dụng</h3>
                <ol style='margin: 10px 0; padding-left: 20px;'>
                    <li>Nhập danh sách mã chứng khoán (VN hoặc US)</li>
                    <li>Chọn chế độ phân bổ và số năm dữ liệu</li>
                    <li>Nhập vốn đầu tư</li>
                    <li>Nhấn "🚀 Tối Ưu Danh Mục" để phân tích</li>
                </ol>
                <p style='color: #1976d2; margin: 10px 0;'><b>💡 Mẫu danh mục:</b></p>
                <ul style='margin: 5px 0; padding-left: 20px;'>
                    <li><b>VN Bluechips:</b> VNM, VIC, VHM, GAS, HPG</li>
                    <li><b>VN ETF:</b> E1VFVN30, FUEVFVND, FUESSV30</li>
                    <li><b>US Index:</b> SPY, QQQ, DIA, BND</li>
                    <li><b>Mixed:</b> SPY, BND, GLD, VNM, GAS</li>
                </ul>
            </div>
            """
        )
        
        # Input
        self.opt_funds = widgets.Textarea(
            value='VNM, VIC, GAS, FPT, HPG',
            placeholder='Nhập mã, cách nhau bởi dấu phẩy',
            description='Danh mục:',
            layout=widgets.Layout(width='90%', height='100px'),
            style={'description_width': '120px'}
        )
        
        self.opt_mode = widgets.Dropdown(
            options=[
                ('Tối ưu (cho phép 0%)', 'optimal'),
                ('Phân bổ đều', 'equal'),
                ('Tối thiểu 5%/mã', 'min5'),
                ('Tối thiểu 10%/mã', 'min10')
            ],
            value='optimal',
            description='Chế độ:',
            style={'description_width': '120px'}
        )
        
        self.opt_years = widgets.IntSlider(
            value=2, min=1, max=5, description='Số năm lịch sử:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='500px')
        )
        
        self.opt_capital = widgets.FloatText(
            value=100000000, description='Vốn (VNĐ):',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        # Button
        self.opt_btn = widgets.Button(
            description='🚀 Tối Ưu Danh Mục',
            button_style='success',
            layout=widgets.Layout(width='250px', height='50px'),
            style={'button_color': '#4CAF50', 'font_weight': 'bold'}
        )
        self.opt_btn.on_click(self.run_optimize)
        
        # Output
        self.opt_output = widgets.Output()
        self.opt_result = widgets.Output()
        
        # Layout
        self.optimize_tab = widgets.VBox([
            widgets.HTML("<h2 style='color: #1976d2; border-bottom: 3px solid #2196F3; padding-bottom: 10px;'>🎯 Thiết Lập Tối Ưu</h2>"),
            guide,
            self.opt_funds,
            widgets.HBox([self.opt_mode, self.opt_years]),
            self.opt_capital,
            widgets.HTML("<br>"),
            self.opt_btn,
            self.opt_output,
            widgets.HTML("<hr style='margin: 30px 0; border: 0; border-top: 2px solid #e0e0e0;'>"),
            widgets.HTML("<h2 style='color: #1976d2; border-bottom: 3px solid #2196F3; padding-bottom: 10px;'>📊 Kết Quả Phân Tích</h2>"),
            self.opt_result
        ], layout=widgets.Layout(padding='20px'))
    
    def create_rebalance_widgets(self):
        """Tab cân bằng danh mục"""
        
        # Hướng dẫn
        guide = widgets.HTML(
            value="""
            <div style='background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); 
                        padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #FF9800;'>
                <h3 style='margin-top: 0; color: #e65100;'>📖 Hướng dẫn sử dụng</h3>
                <ol style='margin: 10px 0; padding-left: 20px;'>
                    <li>Nhập danh mục hiện tại (format: MÃ,SỐ_LƯỢNG,GIÁ_MUA)</li>
                    <li>Nhập phân bổ mục tiêu (format: MÃ,TỶ_TRỌNG_%)</li>
                    <li>Cấu hình ngưỡng cân bằng và tiền mới (nếu có)</li>
                    <li>Nhấn "⚖️ Phân Tích Cân Bằng"</li>
                </ol>
                <p style='color: #f57c00; margin: 10px 0;'><b>💡 Ví dụ:</b></p>
                <ul style='margin: 5px 0; padding-left: 20px;'>
                    <li><b>Danh mục hiện tại:</b> VCB,500,90000</li>
                    <li><b>Mục tiêu:</b> VCB,25 (nghĩa là 25%)</li>
                </ul>
            </div>
            """
        )
        
        # Current portfolio
        self.reb_current = widgets.Textarea(
            value='VCB,500,90000\nHPG,2000,25000\nVNM,1000,85000',
            placeholder='MÃ,Số_lượng,Giá_mua\nVD: VCB,500,90000',
            description='Danh mục hiện tại:',
            layout=widgets.Layout(width='90%', height='150px'),
            style={'description_width': '150px'}
        )
        
        # Target allocation
        self.reb_target = widgets.Textarea(
            value='VCB,30\nHPG,30\nVNM,20\nFPT,20',
            placeholder='MÃ,Tỷ_trọng_%\nVD: VCB,25',
            description='Phân bổ mục tiêu:',
            layout=widgets.Layout(width='90%', height='120px'),
            style={'description_width': '150px'}
        )
        
        # Settings
        self.reb_threshold = widgets.FloatSlider(
            value=5, min=1, max=20, step=0.5,
            description='Ngưỡng drift (%):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='500px')
        )
        
        self.reb_new_money = widgets.FloatText(
            value=0, description='Tiền mới (VNĐ):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )
        
        # Button
        self.reb_btn = widgets.Button(
            description='⚖️ Phân Tích Cân Bằng',
            button_style='warning',
            layout=widgets.Layout(width='250px', height='50px'),
            style={'font_weight': 'bold'}
        )
        self.reb_btn.on_click(self.run_rebalance)
        
        # Output
        self.reb_output = widgets.Output()
        self.reb_result = widgets.Output()
        
        # Layout
        self.rebalance_tab = widgets.VBox([
            widgets.HTML("<h2 style='color: #e65100; border-bottom: 3px solid #FF9800; padding-bottom: 10px;'>📋 Thiết Lập Cân Bằng</h2>"),
            guide,
            self.reb_current,
            self.reb_target,
            widgets.HTML("<br>"),
            widgets.HTML("<h3 style='color: #f57c00;'>⚙️ Cấu Hình</h3>"),
            self.reb_threshold,
            self.reb_new_money,
            widgets.HTML("<br>"),
            self.reb_btn,
            self.reb_output,
            widgets.HTML("<hr style='margin: 30px 0; border: 0; border-top: 2px solid #e0e0e0;'>"),
            widgets.HTML("<h2 style='color: #e65100; border-bottom: 3px solid #FF9800; padding-bottom: 10px;'>📊 Kết Quả Phân Tích</h2>"),
            self.reb_result
        ], layout=widgets.Layout(padding='20px'))
    
    def run_optimize(self, b):
        """Chạy tối ưu"""
        with self.opt_output:
            clear_output()
            print("🔄 Đang phân tích...")
        
        try:
            funds = [f.strip().upper() for f in self.opt_funds.value.split(',') if f.strip()]
            
            if len(funds) < 2:
                with self.opt_output:
                    clear_output()
                    print("❌ Cần ít nhất 2 mã!")
                return
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * self.opt_years.value)
            
            with self.opt_output:
                clear_output()
                print("📥 Đang tải dữ liệu...\n")
            
            data = self.fetch_data(funds, start_date, end_date)
            
            if data is None or data.empty:
                with self.opt_output:
                    clear_output()
                    print("❌ Không có dữ liệu!")
                return
            
            with self.opt_output:
                print(f"\n✅ Tải được {len(data.columns)} tài sản, {len(data)} ngày")
                print("🧹 Đang làm sạch dữ liệu...")
            
            data = self.clean_data(data)
            
            if len(data) < 60 or len(data.columns) < 2:
                with self.opt_output:
                    clear_output()
                    print(f"❌ Dữ liệu không đủ (cần >60 ngày, ≥2 mã)")
                return
            
            self.df = data
            
            with self.opt_output:
                print(f"✅ Dữ liệu sạch: {len(data.columns)} tài sản, {len(data)} ngày")
                print("⏳ Đang tối ưu danh mục...")
            
            weights, performance, method = self.optimize_portfolio(
                data, mode=self.opt_mode.value
            )
            
            self.weights = weights
            self.performance = performance
            self.method = method
            
            with self.opt_output:
                print(f"✅ Hoàn tất! ({method})")
                print(f"📈 Lợi nhuận: {performance[0]*100:.2f}%/năm")
                print(f"📊 Volatility: {performance[1]*100:.2f}%")
                print(f"⭐ Sharpe: {performance[2]:.2f}")
            
            self.display_optimize_result()
            
        except Exception as e:
            with self.opt_output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
    
    def run_rebalance(self, b):
        """Chạy cân bằng"""
        with self.reb_output:
            clear_output()
            print("🔄 Đang phân tích...")
        
        try:
            # Parse current
            current_lines = [line.strip() for line in self.reb_current.value.split('\n') if line.strip()]
            current_data = []
            for line in current_lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 3:
                    current_data.append({
                        'ticker': parts[0].upper(),
                        'shares': float(parts[1]),
                        'cost_basis': float(parts[2])
                    })
            
            if not current_data:
                raise ValueError("Danh mục hiện tại trống!")
            
            current_df = pd.DataFrame(current_data)
            
            # Parse target
            target_lines = [line.strip() for line in self.reb_target.value.split('\n') if line.strip()]
            target_data = []
            for line in target_lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 2:
                    target_data.append({
                        'ticker': parts[0].upper(),
                        'allocation_target': float(parts[1]) / 100
                    })
            
            if not target_data:
                raise ValueError("Phân bổ mục tiêu trống!")
            
            target_df = pd.DataFrame(target_data)
            
            # Validate total
            total = target_df['allocation_target'].sum()
            if not np.isclose(total, 1.0, atol=0.02):
                raise ValueError(f"Tổng tỷ trọng = {total*100:.1f}%, cần = 100%")
            
            # Get prices
            all_tickers = list(set(current_df['ticker'].tolist() + target_df['ticker'].tolist()))
            
            with self.reb_output:
                clear_output()
                print(f"📥 Đang lấy giá {len(all_tickers)} mã...")
            
            prices = {}
            for ticker in all_tickers:
                market = self.detect_market(ticker)
                price = DataFetcher.get_latest_price(ticker, market)
                if price:
                    prices[ticker] = price
                    print(f"  ✓ {ticker}: {price:,.0f}")
            
            if not prices:
                raise ValueError("Không lấy được giá!")
            
            prices_series = pd.Series(prices)
            
            # Merge & calculate
            portfolio = current_df.merge(target_df, on='ticker', how='outer')
            portfolio = portfolio.merge(prices_series.to_frame('close'), 
                                       left_on='ticker', right_index=True, how='left')
            
            portfolio['shares'] = portfolio['shares'].fillna(0)
            portfolio['allocation_target'] = portfolio['allocation_target'].fillna(0)
            portfolio['value'] = portfolio['shares'] * portfolio['close']
            
            total_value = portfolio['value'].sum()
            portfolio['allocation_current'] = portfolio['value'] / total_value
            portfolio['drift'] = portfolio['allocation_target'] - portfolio['allocation_current']
            
            threshold = self.reb_threshold.value / 100
            portfolio['needs_rebal'] = np.abs(portfolio['drift']) > threshold
            
            total_value_new = total_value + self.reb_new_money.value
            portfolio['target_value'] = portfolio['allocation_target'] * total_value_new
            portfolio['value_change'] = portfolio['target_value'] - portfolio['value']
            portfolio['shares_change'] = portfolio['value_change'] / portfolio['close']
            portfolio['shares_change_rounded'] = (portfolio['shares_change'] / 100).round() * 100
            portfolio['new_shares'] = portfolio['shares'] + portfolio['shares_change_rounded']
            portfolio['new_value'] = portfolio['new_shares'] * portfolio['close']
            portfolio['new_allocation'] = portfolio['new_value'] / portfolio['new_value'].sum()
            
            self.rebalanced_portfolio = portfolio
            
            with self.reb_output:
                clear_output()
                print("✅ Phân tích hoàn tất!")
            
            self.display_rebalance_result()
            
        except Exception as e:
            with self.reb_output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
    
    def display_optimize_result(self):
        """Hiển thị kết quả tối ưu"""
        with self.opt_result:
            clear_output()
            
            print("="*85)
            print(" "*28 + "📊 KẾT QUẢ TỐI ƯU DANH MỤC")
            print("="*85)
            
            print(f"\n📅 Kỳ: {self.df.index[0].strftime('%d/%m/%Y')} → {self.df.index[-1].strftime('%d/%m/%Y')}")
            print(f"💼 Số tài sản: {len([w for w in self.weights.values() if w > 0])}/{len(self.df.columns)}")
            print(f"💰 Vốn: {self.opt_capital.value:,.0f} VNĐ")
            print(f"🎯 Phương pháp: {self.method}")
            
            print("\n" + "="*85)
            print(" "*30 + "📈 HIỆU SUẤT KỲ VỌNG")
            print("="*85)
            
            expected_return = self.performance[0] * 100
            volatility = self.performance[1] * 100
            sharpe = self.performance[2]
            
            print(f"\n{'📈 Lợi nhuận/năm:':<35} {expected_return:>12.2f}%")
            print(f"{'📊 Volatility:':<35} {volatility:>12.2f}%")
            print(f"{'⭐ Sharpe Ratio:':<35} {sharpe:>12.2f}")
            
            if sharpe > 2:
                rating = "⭐⭐⭐ Xuất sắc"
            elif sharpe > 1:
                rating = "⭐⭐ Tốt"
            elif sharpe > 0.5:
                rating = "⭐ Chấp nhận được"
            else:
                rating = "⚠️ Cần cải thiện"
            print(f"{'🏆 Đánh giá:':<35} {rating}")
            
            print("\n" + "="*85)
            print(" "*32 + "💼 TỶ TRỌNG PHÂN BỔ")
            print("="*85)
            
            weights_df = pd.DataFrame.from_dict(self.weights, orient='index', columns=['Tỷ trọng'])
            weights_df = weights_df[weights_df['Tỷ trọng'] > 0.001].sort_values('Tỷ trọng', ascending=False)
            weights_df['%'] = (weights_df['Tỷ trọng'] * 100).round(2)
            weights_df['Giá trị'] = (weights_df['Tỷ trọng'] * self.opt_capital.value).round(0)
            
            print(f"\n{'Mã':<12} {'Tỷ trọng':<12} {'Giá trị (VNĐ)':<20} {'Biểu đồ'}")
            print("-"*85)
            
            for idx, row in weights_df.iterrows():
                bar = "█" * int(row['%'] / 2)
                market = "🇻🇳" if self.detect_market(idx) == 'VN' else "🌎"
                print(f"{market} {idx:<9} {row['%']:>6.2f}%     {row['Giá trị']:>18,.0f}     {bar}")
            
            print("\n" + "="*85)
            print(f"Tổng: {weights_df['%'].sum():.2f}%     {weights_df['Giá trị'].sum():,.0f} VNĐ")
            
            # Plots
            self.plot_optimize_charts()
    
    def display_rebalance_result(self):
        """Hiển thị kết quả cân bằng"""
        with self.reb_result:
            clear_output()
            
            df = self.rebalanced_portfolio
            
            print("="*90)
            print(" "*30 + "⚖️ KẾT QUẢ CÂN BẰNG DANH MỤC")
            print("="*90)
            
            print(f"\n💰 Tổng giá trị hiện tại: {df['value'].sum():,.0f} VNĐ")
            print(f"💵 Tiền mới đầu tư: {self.reb_new_money.value:,.0f} VNĐ")
            print(f"💎 Tổng giá trị mới: {df['new_value'].sum():,.0f} VNĐ")
            
            needs = df[df['needs_rebal']].shape[0]
            print(f"\n⚠️ Cần cân bằng: {needs}/{len(df)} mã")
            print(f"📊 Ngưỡng drift: {self.reb_threshold.value}%")
            
            print("\n" + "="*90)
            print(f"\n{'Mã':<8} {'SL hiện':<10} {'Giá':<13} {'GT hiện':<16} "
                  f"{'% Hiện':<9} {'% Mục tiêu':<11} {'Drift':<8}")
            print("-"*90)
            
            for _, row in df.iterrows():
                drift_color = "🔴" if row['needs_rebal'] else "🟢"
                print(f"{drift_color} {row['ticker']:<6} {row['shares']:>9,.0f} "
                      f"{row['close']:>12,.0f} {row['value']:>15,.0f} "
                      f"{row['allocation_current']*100:>7.1f}% {row['allocation_target']*100:>9.1f}% "
                      f"{row['drift']*100:>6.1f}%")
            
            print("\n" + "="*90)
            print(" "*32 + "💼 GIAO DỊCH CẦN THỰC HIỆN")
            print("="*90)
            
            trans = df[df['shares_change_rounded'] != 0].copy()
            
            if len(trans) == 0:
                print("\n✅ Không cần giao dịch!")
            else:
                buys = trans[trans['shares_change_rounded'] > 0]
                sells = trans[trans['shares_change_rounded'] < 0]
                
                # MUA
                if len(buys) > 0:
                    print("\n🟢 MUA:")
                    print(f"{'Mã':<10} {'Số lượng':<15} {'Giá':<15} {'Tổng (VNĐ)':<20}")
                    print("-"*90)
                    
                    total_buy = 0
                    for _, row in buys.iterrows():
                        amt = row['shares_change_rounded'] * row['close']
                        total_buy += amt
                        print(f"{row['ticker']:<10} {int(row['shares_change_rounded']):>14,} "
                              f"{row['close']:>14,.0f} {amt:>19,.0f}")
                    
                    print("-"*90)
                    print(f"Tổng MUA: {total_buy:>19,.0f} VNĐ")
                
                # BÁN
                if len(sells) > 0:
                    print("\n🔴 BÁN:")
                    print(f"{'Mã':<10} {'Số lượng':<15} {'Giá':<15} {'Tổng (VNĐ)':<20}")
                    print("-"*90)
                    
                    total_sell = 0
                    for _, row in sells.iterrows():
                        amt = abs(row['shares_change_rounded']) * row['close']
                        total_sell += amt
                        print(f"{row['ticker']:<10} {int(abs(row['shares_change_rounded'])):>14,} "
                              f"{row['close']:>14,.0f} {amt:>19,.0f}")
                    
                    print("-"*90)
                    print(f"Tổng BÁN: {total_sell:>19,.0f} VNĐ")
                
                # Tổng kết
                print("\n" + "="*90)
                net = total_buy - total_sell - self.reb_new_money.value
                print(f"\n💵 Tiền thu từ bán: {total_sell:>20,.0f} VNĐ")
                print(f"💰 Tiền mới đầu tư: {self.reb_new_money.value:>20,.0f} VNĐ")
                print(f"💳 Cần tiền để mua: {total_buy:>20,.0f} VNĐ")
                print(f"{'💸 Chênh lệch:' if net >= 0 else '💹 Dư ra:'} {abs(net):>20,.0f} VNĐ")
                
                print("\n💡 Lưu ý TTCK VN:")
                print("  • Khối lượng giao dịch: Bội số 100")
                print("  • Thanh toán: T+2")
                print("  • Phí giao dịch: ~0.3% (môi giới + thuế)")
            
            # Plot
            self.plot_rebalance_charts()
    
    def plot_optimize_charts(self):
        """Vẽ biểu đồ tối ưu"""
        weights_df = pd.DataFrame.from_dict(self.weights, orient='index', columns=['Tỷ trọng'])
        weights_df = weights_df[weights_df['Tỷ trọng'] > 0.001].sort_values('Tỷ trọng', ascending=False)
        weights_df['%'] = (weights_df['Tỷ trọng'] * 100).round(2)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('📊 Phân Tích Tối Ưu Danh Mục', fontsize=16, fontweight='bold', y=0.995)
        
        # 1. Pie chart
        colors = plt.cm.Set3(range(len(weights_df)))
        axes[0, 0].pie(weights_df['%'], labels=weights_df.index, autopct='%1.1f%%', 
                       colors=colors, startangle=90)
        axes[0, 0].set_title('💼 Phân Bổ Tỷ Trọng', fontsize=12, fontweight='bold', pad=10)
        
        # 2. Bar chart
        weights_df.plot(kind='barh', ax=axes[0, 1], color=colors, legend=False, y='%')
        axes[0, 1].set_xlabel('Tỷ trọng (%)', fontsize=10)
        axes[0, 1].set_title('📊 Chi Tiết Tỷ Trọng', fontsize=12, fontweight='bold', pad=10)
        axes[0, 1].grid(axis='x', alpha=0.3)
        
        # 3. Price history
        normalized = self.df / self.df.iloc[0] * 100
        for col in normalized.columns:
            if col in self.weights and self.weights[col] > 0.001:
                axes[1, 0].plot(normalized.index, normalized[col], label=col, linewidth=2, alpha=0.8)
        axes[1, 0].set_ylabel('Giá chuẩn hóa (Base=100)', fontsize=10)
        axes[1, 0].set_title('📈 Lịch Sử Giá', fontsize=12, fontweight='bold', pad=10)
        axes[1, 0].legend(fontsize=8, loc='best', framealpha=0.9)
        axes[1, 0].grid(alpha=0.3)
        axes[1, 0].axhline(y=100, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        
        # 4. Correlation
        selected_cols = [col for col in self.df.columns if col in self.weights and self.weights[col] > 0.001]
        if len(selected_cols) > 1:
            corr = self.df[selected_cols].corr()
            im = axes[1, 1].imshow(corr, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
            axes[1, 1].set_xticks(range(len(corr)))
            axes[1, 1].set_yticks(range(len(corr)))
            axes[1, 1].set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=9)
            axes[1, 1].set_yticklabels(corr.columns, fontsize=9)
            axes[1, 1].set_title('🔗 Ma Trận Tương Quan', fontsize=12, fontweight='bold', pad=10)
            
            for i in range(len(corr)):
                for j in range(len(corr)):
                    axes[1, 1].text(j, i, f'{corr.iloc[i, j]:.2f}',
                                   ha="center", va="center", color="black", fontsize=8)
            
            plt.colorbar(im, ax=axes[1, 1])
        else:
            axes[1, 1].text(0.5, 0.5, 'Cần >1 tài sản\nđể hiển thị tương quan', 
                           ha='center', va='center', fontsize=12)
            axes[1, 1].set_title('🔗 Ma Trận Tương Quan', fontsize=12, fontweight='bold', pad=10)
        
        plt.tight_layout()
        plt.show()
    
    def plot_rebalance_charts(self):
        """Vẽ biểu đồ cân bằng"""
        df = self.rebalanced_portfolio
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('⚖️ Phân Tích Cân Bằng Danh Mục', fontsize=16, fontweight='bold', y=0.995)
        
        # 1. Current vs Target
        ax1 = axes[0, 0]
        x = np.arange(len(df))
        width = 0.35
        
        ax1.bar(x - width/2, df['allocation_current'] * 100, width, 
               label='Hiện tại', alpha=0.8, color='#e74c3c')
        ax1.bar(x + width/2, df['allocation_target'] * 100, width, 
               label='Mục tiêu', alpha=0.8, color='#27ae60')
        
        ax1.set_xlabel('Mã', fontsize=10)
        ax1.set_ylabel('Tỷ trọng (%)', fontsize=10)
        ax1.set_title('📊 Hiện Tại vs Mục Tiêu', fontweight='bold', fontsize=12, pad=10)
        ax1.set_xticks(x)
        ax1.set_xticklabels(df['ticker'], rotation=45)
        ax1.legend(loc='best')
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Drift
        ax2 = axes[0, 1]
        threshold = self.reb_threshold.value / 100
        colors = ['#e74c3c' if d < -threshold else 
                 '#27ae60' if d > threshold else '#95a5a6' 
                 for d in df['drift']]
        
        ax2.barh(df['ticker'], df['drift'] * 100, color=colors, alpha=0.8)
        ax2.axvline(x=0, color='black', linewidth=1.5)
        ax2.axvline(x=threshold*100, color='red', linestyle='--', alpha=0.5, label='Ngưỡng')
        ax2.axvline(x=-threshold*100, color='red', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Lệch (%)', fontsize=10)
        ax2.set_title('📉 Drift (Độ Lệch)', fontweight='bold', fontsize=12, pad=10)
        ax2.grid(axis='x', alpha=0.3)
        ax2.legend()
        
        # 3. Value change
        ax3 = axes[1, 0]
        colors = ['#27ae60' if v > 0 else '#e74c3c' for v in df['value_change']]
        ax3.bar(df['ticker'], df['value_change']/1e6, color=colors, alpha=0.8)
        ax3.axhline(y=0, color='black', linewidth=1.5)
        ax3.set_xlabel('Mã', fontsize=10)
        ax3.set_ylabel('Triệu VNĐ', fontsize=10)
        ax3.set_title('💰 Thay Đổi Giá Trị', fontweight='bold', fontsize=12, pad=10)
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Pie - New allocation
        ax4 = axes[1, 1]
        pie_df = df[df['new_allocation'] > 0.001].copy()
        colors_pie = plt.cm.Set3(range(len(pie_df)))
        ax4.pie(pie_df['new_allocation'], labels=pie_df['ticker'],
                autopct='%1.1f%%', startangle=90, colors=colors_pie)
        ax4.set_title('🎯 Phân Bổ Sau Cân Bằng', fontweight='bold', fontsize=12, pad=10)
        
        plt.tight_layout()
        plt.show()
    
    def display(self):
        """Hiển thị ứng dụng"""
        if WIDGETS_AVAILABLE:
            display(self.header)
            display(self.main_tabs)
        else:
            print("⚠️ Cần cài đặt ipywidgets để sử dụng giao diện!")


# ==================== MAIN ====================

def main():
    """Hàm chính"""
    print("="*85)
    print(" "*25 + "💼 PORTFOLIO PRO")
    print(" "*15 + "Tối ưu & Cân bằng Danh mục Đầu tư Chuyên nghiệp")
    print("="*85)
    
    print(f"\n📦 Kiểm tra thư viện:")
    print(f"  • PyPortfolioOpt: {'✅' if PYPFOPT_AVAILABLE else '❌ pip install PyPortfolioOpt'}")
    print(f"  • ipywidgets: {'✅' if WIDGETS_AVAILABLE else '❌ pip install ipywidgets'}")
    
    if not PYPFOPT_AVAILABLE:
        print("\n⚠️ Cần cài đặt: pip install PyPortfolioOpt")
    if not WIDGETS_AVAILABLE:
        print("\n⚠️ Cần cài đặt: pip install ipywidgets")
    
    if PYPFOPT_AVAILABLE and WIDGETS_AVAILABLE:
        print("\n✨ Tất cả thư viện đã sẵn sàng!")
        print("\n💡 Thư viện bổ sung (khuyến nghị):")
        print("  • vnstock3: pip install vnstock3 (cho cổ phiếu VN)")
        print("  • pandas-datareader: pip install pandas-datareader (cho cổ phiếu US)")
        print("="*85 + "\n")
        
        app = PortfolioProApp()
        app.display()
    else:
        print("\n❌ Vui lòng cài đặt các thư viện cần thiết!")


if __name__ == "__main__":
    main()
else:
    # Jupyter mode
    try:
        if PYPFOPT_AVAILABLE and WIDGETS_AVAILABLE:
            app = PortfolioProApp()
            app.display()
        else:
            print("⚠️ Cần cài đặt đầy đủ thư viện:")
            if not PYPFOPT_AVAILABLE:
                print("  pip install PyPortfolioOpt")
            if not WIDGETS_AVAILABLE:
                print("  pip install ipywidgets")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        print(traceback.format_exc())
