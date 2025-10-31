"""
Portfolio Optimizer & Rebalancer Pro - Enhanced Version
Ứng dụng chuyên nghiệp tối ưu và cân bằng danh mục đầu tư
VN & International Markets với quản lý dữ liệu tự động
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
from pathlib import Path

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


# ==================== DATA MANAGER ====================

class DataManager:
    """Quản lý dữ liệu: lưu, tải, tạo file template"""
    
    def __init__(self, data_dir='portfolio_data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Thư mục con
        self.price_dir = self.data_dir / 'price_data'
        self.portfolio_dir = self.data_dir / 'portfolios'
        self.config_dir = self.data_dir / 'configs'
        
        for d in [self.price_dir, self.portfolio_dir, self.config_dir]:
            d.mkdir(exist_ok=True)
    
    def get_price_file_path(self, symbol):
        """Lấy đường dẫn file giá"""
        return self.price_dir / f"{symbol}_price.csv"
    
    def create_price_template(self, symbol):
        """Tạo file CSV template cho giá cổ phiếu"""
        filename = self.get_price_file_path(symbol)
        
        # Template với 1 năm dữ liệu mẫu
        dates = pd.date_range(end=datetime.now(), periods=252, freq='B')
        template_df = pd.DataFrame({
            'Date': dates.strftime('%Y-%m-%d'),
            'Adj Close': [100.0] * len(dates)
        })
        
        template_df.to_csv(filename, index=False)
        return filename
    
    def save_price_data(self, symbol, df):
        """Lưu dữ liệu giá vào CSV"""
        filename = self.get_price_file_path(symbol)
        
        # Chuẩn hóa dữ liệu
        save_df = df.copy()
        save_df.index.name = 'Date'
        save_df = save_df.reset_index()
        save_df['Date'] = pd.to_datetime(save_df['Date']).dt.strftime('%Y-%m-%d')
        
        save_df.to_csv(filename, index=False)
        return filename
    
    def load_price_from_csv(self, symbol):
        """Tải giá từ file CSV"""
        filename = self.get_price_file_path(symbol)
        
        if not filename.exists():
            return None
        
        try:
            df = pd.read_csv(filename, parse_dates=['Date'], index_col='Date')
            if 'Adj Close' in df.columns:
                # Loại bỏ duplicate dates
                df = df[~df.index.duplicated(keep='last')]
                return df[['Adj Close']]
        except Exception as e:
            print(f"⚠️ Lỗi đọc {filename}: {e}")
        
        return None
    
    def check_price_file_exists(self, symbol):
        """Kiểm tra file giá có tồn tại không"""
        return self.get_price_file_path(symbol).exists()
    
    def save_portfolio_weights(self, name, weights, performance, method, symbols):
        """Lưu kết quả tối ưu"""
        filename = self.portfolio_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'weights': weights,
            'performance': {
                'return': performance[0],
                'volatility': performance[1],
                'sharpe': performance[2]
            },
            'method': method,
            'symbols': symbols
        }
        
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def load_latest_portfolio(self, name=None):
        """Tải portfolio gần nhất"""
        import json
        
        files = list(self.portfolio_dir.glob('*.json'))
        if not files:
            return None
        
        if name:
            files = [f for f in files if f.stem.startswith(name)]
        
        if not files:
            return None
        
        latest = max(files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def list_portfolios(self):
        """Liệt kê các portfolio đã lưu"""
        import json
        
        files = list(self.portfolio_dir.glob('*.json'))
        portfolios = []
        
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    portfolios.append({
                        'file': f.name,
                        'name': data.get('name', 'Unknown'),
                        'timestamp': data.get('timestamp', ''),
                        'symbols': data.get('symbols', [])
                    })
            except:
                pass
        
        return sorted(portfolios, key=lambda x: x['timestamp'], reverse=True)


# ==================== DATA FETCHER ====================

class DataFetcher:
    """Lấy dữ liệu cổ phiếu từ nhiều nguồn"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_vn_stock(self, symbol, start_date, end_date):
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
    
    def get_us_stock(self, symbol, start_date, end_date):
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
    
    def fetch_and_save(self, symbol, start_date, end_date, market='VN'):
        """Tải dữ liệu từ online và lưu vào CSV"""
        if market == 'VN':
            df = self.get_vn_stock(symbol, start_date, end_date)
        else:
            df = self.get_us_stock(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            # Lưu vào CSV
            self.data_manager.save_price_data(symbol, df)
            return df, 'online'
        
        return None, None
    
    def get_price_data(self, symbol, start_date, end_date, force_csv=False):
        """Lấy dữ liệu - ưu tiên CSV nếu có"""
        # Nếu force_csv hoặc file CSV đã tồn tại, đọc từ CSV trước
        if force_csv or self.data_manager.check_price_file_exists(symbol):
            df = self.data_manager.load_price_from_csv(symbol)
            if df is not None and not df.empty:
                # Filter theo date range
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                if not df.empty:
                    return df, 'csv'
        
        # Không có CSV hoặc CSV rỗng -> return None
        return None, None
    
    def get_latest_price(self, symbol, market='VN'):
        """Lấy giá mới nhất"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Thử load từ CSV trước
        df, source = self.get_price_data(symbol, start_date, end_date, force_csv=True)
        
        if df is not None and not df.empty:
            return df['Adj Close'].iloc[-1]
        
        # Nếu không có, thử online
        if market == 'VN':
            df = self.get_vn_stock(symbol, start_date, end_date)
        else:
            df = self.get_us_stock(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            return df['Adj Close'].iloc[-1]
        
        return None


# ==================== MAIN APP ====================

class PortfolioProApp:
    """Ứng dụng chính"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.data_fetcher = DataFetcher(self.data_manager)
        
        self.df = None
        self.weights = None
        self.performance = None
        self.method = None
        self.symbols_with_weights = []
        self.current_portfolio = None
        self.rebalanced_portfolio = None
        
        # Danh sách mã VN
        self.vn_stocks = ['E1VFVN30', 'FUEVFVND', 'FUESSV30', 'FUESSVFL', 
                          'VNM', 'VIC', 'VHM', 'GAS', 'MSN', 'HPG', 
                          'TCB', 'MBB', 'VCB', 'BID', 'CTG', 'FPT', 
                          'MWG', 'VRE', 'PLX', 'GVR']
        
        # Track symbols cần download
        self.missing_symbols = {}
        
        if WIDGETS_AVAILABLE:
            self.create_widgets()
    
    def detect_market(self, symbol):
        """Xác định thị trường"""
        if symbol in self.vn_stocks or '.VN' in symbol:
            return 'VN'
        return 'US'
    
    def download_data(self, symbols, start_date, end_date):
        """Tải dữ liệu từ online và lưu vào CSV"""
        success_symbols = []
        failed_symbols = []
        
        for symbol in symbols:
            market = self.detect_market(symbol)
            clean_symbol = symbol.replace('.VN', '')
            
            print(f"  • {clean_symbol}...", end=' ', flush=True)
            
            df, source = self.data_fetcher.fetch_and_save(
                clean_symbol, start_date, end_date, market
            )
            
            if df is not None and not df.empty:
                success_symbols.append(clean_symbol)
                print(f"✓ ({len(df)} ngày, đã lưu)")
            else:
                failed_symbols.append(clean_symbol)
                print("✗")
        
        return success_symbols, failed_symbols
    
    def load_data_from_csv(self, symbols, start_date, end_date):
        """Tải dữ liệu từ CSV đã lưu"""
        all_data = {}
        missing_symbols = []
        
        for symbol in symbols:
            clean_symbol = symbol.replace('.VN', '')
            
            print(f"  • {clean_symbol}...", end=' ', flush=True)
            
            # Kiểm tra file có tồn tại không
            if not self.data_manager.check_price_file_exists(clean_symbol):
                print("✗ (chưa có file)")
                missing_symbols.append(clean_symbol)
                continue
            
            # Tải từ CSV
            df, source = self.data_fetcher.get_price_data(
                clean_symbol, start_date, end_date, force_csv=True
            )
            
            if df is not None and not df.empty:
                all_data[symbol] = df['Adj Close']
                print(f"✓ ({len(df)} ngày)")
            else:
                print("✗ (file rỗng hoặc lỗi)")
                missing_symbols.append(clean_symbol)
        
        if all_data:
            combined_df = pd.DataFrame(all_data)
            if combined_df.index.duplicated().any():
                combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
            return combined_df, missing_symbols
        
        return None, missing_symbols
    
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
    
    def optimize_portfolio(self, data, mode='optimal', risk_profile='moderate', target_return=None, max_volatility=None):
        """Tối ưu danh mục với mức độ rủi ro"""
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
        
        # Xác định ràng buộc tỷ trọng
        if mode == 'min5':
            weight_bounds = (0.05, 1.0)
            mode_desc = "min 5%"
        elif mode == 'min10':
            weight_bounds = (0.10, 1.0)
            mode_desc = "min 10%"
        else:
            weight_bounds = (0, 1.0)
            mode_desc = "optimal"
        
        # Tính expected returns và covariance
        mu = expected_returns.mean_historical_return(data)
        S = risk_models.sample_cov(data)
        S_regularized = S + np.eye(len(S)) * 0.001
        
        # Chọn phương pháp tối ưu theo risk profile
        try:
            ef = EfficientFrontier(mu, S_regularized, weight_bounds=weight_bounds)
            
            if risk_profile == 'conservative':
                # Bảo thủ: Min Volatility
                weights = ef.min_volatility()
                method_name = "Min Volatility (Bảo thủ)"
                
            elif risk_profile == 'aggressive':
                # Tích cực: Max Sharpe (tối đa lợi nhuận điều chỉnh rủi ro)
                weights = ef.max_sharpe()
                method_name = "Max Sharpe (Tích cực)"
                
            elif risk_profile == 'custom':
                # Tùy chỉnh: Efficient Risk hoặc Efficient Return
                if target_return and max_volatility:
                    # Thử target return trước
                    try:
                        weights = ef.efficient_return(target_return / 100)
                        method_name = f"Target Return {target_return}% (Tùy chỉnh)"
                    except:
                        # Nếu không đạt được, dùng max volatility
                        ef = EfficientFrontier(mu, S_regularized, weight_bounds=weight_bounds)
                        weights = ef.efficient_risk(max_volatility / 100)
                        method_name = f"Max Volatility {max_volatility}% (Tùy chỉnh)"
                elif target_return:
                    weights = ef.efficient_return(target_return / 100)
                    method_name = f"Target Return {target_return}% (Tùy chỉnh)"
                elif max_volatility:
                    weights = ef.efficient_risk(max_volatility / 100)
                    method_name = f"Max Volatility {max_volatility}% (Tùy chỉnh)"
                else:
                    weights = ef.max_sharpe()
                    method_name = "Max Sharpe (Tùy chỉnh)"
                    
            else:  # moderate
                # Trung bình: Max Sharpe nhưng với ràng buộc volatility vừa phải
                weights = ef.max_sharpe()
                method_name = "Max Sharpe (Trung bình)"
            
            cleaned_weights = ef.clean_weights()
            performance = ef.portfolio_performance(verbose=False)
            
            return cleaned_weights, performance, f"{method_name} ({mode_desc})"
            
        except Exception as e:
            print(f"⚠️ Tối ưu thất bại: {e}")
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
                <p style='color: #90a0b0; text-align: center; margin-top: 8px; font-size: 12px;'>
                    📁 Dữ liệu lưu tại: {self.data_manager.data_dir}
                </p>
            </div>
            """
        )
        
        # ===== TAB 1: OPTIMIZE =====
        self.create_optimize_widgets()
        
        # ===== TAB 2: REBALANCE =====
        self.create_rebalance_widgets()
        
        # ===== TAB 3: DATA MANAGEMENT =====
        self.create_data_management_widgets()
        
        # ===== MAIN TABS =====
        self.main_tabs = widgets.Tab()
        self.main_tabs.children = [self.optimize_tab, self.rebalance_tab, self.data_tab]
        self.main_tabs.set_title(0, '📈 Tối Ưu Danh Mục')
        self.main_tabs.set_title(1, '⚖️ Cân Bằng Danh Mục')
        self.main_tabs.set_title(2, '💾 Quản Lý Dữ Liệu')
    
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
                    <li><b>Chọn mức độ rủi ro:</b> Bảo thủ, Trung bình, Tích cực hoặc Tùy chỉnh</li>
                    <li>Nhấn "📥 Tải Dữ Liệu Online" để download và lưu CSV</li>
                    <li>Nếu thiếu dữ liệu: nhập vào file CSV, rồi nhấn "🚀 Tối Ưu"</li>
                    <li>Kết quả tự động lưu và có thể xuất sang tab Cân Bằng</li>
                </ol>
                <p style='color: #1976d2; margin: 10px 0;'><b>💡 Mức độ rủi ro:</b></p>
                <ul style='margin: 5px 0; padding-left: 20px;'>
                    <li><b>🛡️ Bảo thủ:</b> Giảm thiểu biến động, ưu tiên bảo toàn vốn</li>
                    <li><b>⚖️ Trung bình:</b> Cân bằng giữa lợi nhuận và rủi ro</li>
                    <li><b>🚀 Tích cực:</b> Tối đa hóa lợi nhuận, chấp nhận rủi ro cao</li>
                    <li><b>📊 Tùy chỉnh:</b> Đặt mục tiêu lợi nhuận hoặc giới hạn rủi ro cụ thể</li>
                </ul>
            </div>
            """
        )
        
        # Portfolio name
        self.opt_portfolio_name = widgets.Text(
            value='MyPortfolio',
            description='Tên danh mục:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        # Load saved portfolio
        self.opt_load_btn = widgets.Button(
            description='📂 Tải Danh Mục Đã Lưu',
            button_style='info',
            layout=widgets.Layout(width='200px')
        )
        self.opt_load_btn.on_click(self.load_saved_portfolio)
        
        # Input
        self.opt_funds = widgets.Textarea(
            value='VNM, VIC, GAS, FPT, HPG',
            placeholder='Nhập mã, cách nhau bởi dấu phẩy',
            description='Danh mục:',
            layout=widgets.Layout(width='90%', height='100px'),
            style={'description_width': '120px'}
        )
        
        # Risk profile
        self.opt_risk_profile = widgets.Dropdown(
            options=[
                ('🛡️ Bảo thủ - Ưu tiên bảo toàn vốn', 'conservative'),
                ('⚖️ Trung bình - Cân bằng rủi ro/lợi nhuận', 'moderate'),
                ('🚀 Tích cực - Tối đa hóa lợi nhuận', 'aggressive'),
                ('📊 Tùy chỉnh - Chọn mục tiêu cụ thể', 'custom')
            ],
            value='moderate',
            description='Mức độ rủi ro:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='600px')
        )
        
        # Target settings (for custom mode)
        self.opt_target_return = widgets.FloatSlider(
            value=15,
            min=5,
            max=50,
            step=1,
            description='Mục tiêu LN (%/năm):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='550px'),
            disabled=True
        )
        
        self.opt_max_volatility = widgets.FloatSlider(
            value=20,
            min=5,
            max=50,
            step=1,
            description='Giới hạn rủi ro (%):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='550px'),
            disabled=True
        )
        
        # Enable/disable custom settings
        def on_risk_change(change):
            is_custom = change['new'] == 'custom'
            self.opt_target_return.disabled = not is_custom
            self.opt_max_volatility.disabled = not is_custom
        
        self.opt_risk_profile.observe(on_risk_change, names='value')
        
        self.opt_mode = widgets.Dropdown(
            options=[
                ('Tối ưu (cho phép 0%)', 'optimal'),
                ('Phân bổ đều', 'equal'),
                ('Tối thiểu 5%/mã', 'min5'),
                ('Tối thiểu 10%/mã', 'min10')
            ],
            value='optimal',
            description='Chế độ phân bổ:',
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
        
        # Buttons - PHÂN TÁCH RÕ RÀNG
        self.opt_download_btn = widgets.Button(
            description='📥 Tải Dữ Liệu Online',
            button_style='info',
            tooltip='Tải dữ liệu từ vnstock/Yahoo và lưu vào CSV',
            layout=widgets.Layout(width='200px', height='45px'),
            style={'font_weight': 'bold'}
        )
        self.opt_download_btn.on_click(self.download_online_data)
        
        self.opt_btn = widgets.Button(
            description='🚀 Tối Ưu Danh Mục',
            button_style='success',
            tooltip='Chạy tối ưu với dữ liệu CSV đã có',
            layout=widgets.Layout(width='200px', height='45px'),
            style={'font_weight': 'bold'}
        )
        self.opt_btn.on_click(self.run_optimize)
        
        self.opt_export_btn = widgets.Button(
            description='💾 Xuất Sang Cân Bằng',
            button_style='primary',
            layout=widgets.Layout(width='200px', height='45px'),
            style={'font_weight': 'bold'}
        )
        self.opt_export_btn.on_click(self.export_to_rebalance)
        
        # Output
        self.opt_output = widgets.Output()
        self.opt_result = widgets.Output()
        
        # Layout
        self.optimize_tab = widgets.VBox([
            widgets.HTML("<h2 style='color: #1976d2; border-bottom: 3px solid #2196F3; padding-bottom: 10px;'>🎯 Thiết Lập Tối Ưu</h2>"),
            guide,
            widgets.HBox([self.opt_portfolio_name, self.opt_load_btn]),
            self.opt_funds,
            widgets.HTML("<br>"),
            widgets.HTML("<h3 style='color: #1976d2;'>⚙️ Cấu Hình Tối Ưu</h3>"),
            self.opt_risk_profile,
            self.opt_target_return,
            self.opt_max_volatility,
            widgets.HTML("<br>"),
            widgets.HBox([self.opt_mode, self.opt_years]),
            self.opt_capital,
            widgets.HTML("<br>"),
            widgets.HTML("<div style='background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0;'><b>Bước 1:</b> Tải dữ liệu online (sẽ tự động lưu CSV)</div>"),
            self.opt_download_btn,
            widgets.HTML("<div style='background: #d1ecf1; padding: 10px; border-radius: 5px; margin: 10px 0;'><b>Bước 2:</b> Nếu thiếu dữ liệu, nhập CSV rồi chạy tối ưu</div>"),
            widgets.HBox([self.opt_btn, self.opt_export_btn]),
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
                    <li>Nhấn "🔄 Tải Từ Tối Ưu" để tự động điền dữ liệu</li>
                    <li>Nhập số lượng cổ phiếu hiện tại và giá mua</li>
                    <li>Cấu hình ngưỡng cân bằng và tiền mới (nếu có)</li>
                    <li>Nhấn "⚖️ Phân Tích Cân Bằng"</li>
                </ol>
            </div>
            """
        )
        
        # Auto-load button
        self.reb_autoload_btn = widgets.Button(
            description='🔄 Tải Từ Tối Ưu',
            button_style='info',
            layout=widgets.Layout(width='200px')
        )
        self.reb_autoload_btn.on_click(self.autoload_from_optimize)
        
        # Current portfolio
        self.reb_current = widgets.Textarea(
            value='',
            placeholder='MÃ,Số_lượng,Giá_mua\nVD: VCB,500,90000',
            description='Danh mục hiện tại:',
            layout=widgets.Layout(width='90%', height='150px'),
            style={'description_width': '150px'}
        )
        
        # Target allocation (auto-filled)
        self.reb_target = widgets.Textarea(
            value='',
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
            self.reb_autoload_btn,
            widgets.HTML("<br>"),
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
    
    def create_data_management_widgets(self):
        """Tab quản lý dữ liệu"""
        
        guide = widgets.HTML(
            value=f"""
            <div style='background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); 
                        padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #9C27B0;'>
                <h3 style='margin-top: 0; color: #6a1b9a;'>💾 Quản Lý Dữ Liệu</h3>
                <p style='margin: 10px 0;'><b>📁 Thư mục dữ liệu:</b> {self.data_manager.data_dir}</p>
                <ul style='margin: 5px 0; padding-left: 20px;'>
                    <li><b>price_data/</b> - Giá cổ phiếu (mỗi mã 1 file CSV)</li>
                    <li><b>portfolios/</b> - Danh mục đã lưu (JSON)</li>
                    <li><b>configs/</b> - Cấu hình cân bằng</li>
                </ul>
                <p style='color: #7b1fa2; margin: 10px 0;'><b>💡 Format CSV:</b></p>
                <p style='margin: 5px 0; font-family: monospace;'>Date,Adj Close<br>2024-01-01,100.0<br>2024-01-02,101.5</p>
            </div>
            """
        )
        
        # List saved portfolios
        self.data_refresh_btn = widgets.Button(
            description='🔄 Làm Mới Danh Sách',
            button_style='info',
            layout=widgets.Layout(width='200px')
        )
        self.data_refresh_btn.on_click(self.refresh_portfolio_list)
        
        self.data_output = widgets.Output()
        
        # Open folder button
        self.data_open_folder_btn = widgets.Button(
            description='📂 Mở Thư Mục Dữ Liệu',
            button_style='primary',
            layout=widgets.Layout(width='220px')
        )
        self.data_open_folder_btn.on_click(self.open_data_folder)
        
        # Layout
        self.data_tab = widgets.VBox([
            widgets.HTML("<h2 style='color: #6a1b9a; border-bottom: 3px solid #9C27B0; padding-bottom: 10px;'>💾 Quản Lý Dữ Liệu</h2>"),
            guide,
            widgets.HBox([self.data_refresh_btn, self.data_open_folder_btn]),
            widgets.HTML("<br>"),
            self.data_output
        ], layout=widgets.Layout(padding='20px'))
        
        # Initial refresh
        self.refresh_portfolio_list(None)
    
    def download_online_data(self, b):
        """Tải dữ liệu từ online và lưu CSV"""
        with self.opt_output:
            clear_output()
            print("📥 Đang tải dữ liệu từ online...\n")
        
        try:
            funds = [f.strip().upper() for f in self.opt_funds.value.split(',') if f.strip()]
            
            if len(funds) < 2:
                with self.opt_output:
                    clear_output()
                    print("❌ Cần ít nhất 2 mã!")
                return
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * self.opt_years.value)
            
            # Download và lưu
            success_symbols, failed_symbols = self.download_data(funds, start_date, end_date)
            
            with self.opt_output:
                print(f"\n{'='*70}")
                print(f"✅ Thành công: {len(success_symbols)} mã")
                if success_symbols:
                    print(f"   {', '.join(success_symbols)}")
                
                if failed_symbols:
                    print(f"\n❌ Thất bại: {len(failed_symbols)} mã")
                    print(f"   {', '.join(failed_symbols)}")
                    print(f"\n📝 Đang tạo file template CSV...")
                    
                    # Tạo template cho các mã thất bại
                    for symbol in failed_symbols:
                        template_file = self.data_manager.create_price_template(symbol)
                        print(f"   ✓ {template_file.name}")
                    
                    print(f"\n💡 Hướng dẫn:")
                    print(f"   1. Mở thư mục: {self.data_manager.price_dir}")
                    print(f"   2. Nhập dữ liệu vào file CSV (format: Date,Adj Close)")
                    print(f"   3. Nhấn '🚀 Tối Ưu Danh Mục' để tiếp tục")
                    
                    self.missing_symbols = {s: str(self.data_manager.get_price_file_path(s)) 
                                          for s in failed_symbols}
                else:
                    print(f"\n✅ Tất cả dữ liệu đã sẵn sàng!")
                    print(f"💡 Bây giờ có thể nhấn '🚀 Tối Ưu Danh Mục'")
                    self.missing_symbols = {}
                
                print(f"{'='*70}")
        
        except Exception as e:
            with self.opt_output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
    
    def load_saved_portfolio(self, b):
        """Tải danh mục đã lưu"""
        with self.opt_output:
            clear_output()
            
        portfolios = self.data_manager.list_portfolios()
        
        if not portfolios:
            with self.opt_output:
                print("⚠️ Chưa có danh mục nào được lưu!")
            return
        
        # Show selection
        with self.opt_output:
            print("📂 Danh mục đã lưu:\n")
            for i, p in enumerate(portfolios[:10], 1):
                timestamp = datetime.fromisoformat(p['timestamp']).strftime('%d/%m/%Y %H:%M')
                symbols_str = ', '.join(p['symbols'][:5])
                if len(p['symbols']) > 5:
                    symbols_str += f" +{len(p['symbols'])-5}"
                print(f"{i}. {p['name']} - {timestamp}")
                print(f"   Mã: {symbols_str}\n")
            
            print("💡 Đang tải danh mục gần nhất...")
        
        # Load latest
        latest = self.data_manager.load_latest_portfolio()
        if latest:
            self.opt_funds.value = ', '.join(latest['symbols'])
            self.opt_portfolio_name.value = latest['name']
            
            with self.opt_output:
                print(f"\n✅ Đã tải: {latest['name']}")
                print(f"📅 Ngày: {datetime.fromisoformat(latest['timestamp']).strftime('%d/%m/%Y %H:%M')}")
    
    def export_to_rebalance(self, b):
        """Xuất dữ liệu sang tab cân bằng"""
        if not self.weights or not self.symbols_with_weights:
            with self.opt_output:
                clear_output()
                print("⚠️ Chưa có kết quả tối ưu!")
                print("💡 Chạy 'Tối Ưu Danh Mục' trước")
            return
        
        # Prepare target allocation text
        target_lines = []
        for symbol in self.symbols_with_weights:
            if symbol in self.weights and self.weights[symbol] > 0.001:
                weight_pct = self.weights[symbol] * 100
                target_lines.append(f"{symbol},{weight_pct:.2f}")
        
        self.reb_target.value = '\n'.join(target_lines)
        
        # Prepare current portfolio template
        current_lines = []
        for symbol in self.symbols_with_weights:
            if symbol in self.weights and self.weights[symbol] > 0.001:
                # Get latest price
                market = self.detect_market(symbol)
                price = self.data_fetcher.get_latest_price(symbol, market)
                if price:
                    # Calculate shares based on capital allocation
                    value = self.weights[symbol] * self.opt_capital.value
                    shares = int(value / price / 100) * 100  # Round to 100
                    current_lines.append(f"{symbol},{shares},{price:.0f}")
        
        self.reb_current.value = '\n'.join(current_lines)
        
        # Switch to rebalance tab
        self.main_tabs.selected_index = 1
        
        with self.opt_output:
            clear_output()
            print("✅ Đã xuất dữ liệu sang tab Cân Bằng!")
            print(f"📊 {len(target_lines)} mã được chuyển")
    
    def autoload_from_optimize(self, b):
        """Tự động tải từ kết quả tối ưu"""
        self.export_to_rebalance(b)
    
    def refresh_portfolio_list(self, b):
        """Làm mới danh sách portfolio"""
        with self.data_output:
            clear_output()
            
            portfolios = self.data_manager.list_portfolios()
            
            if not portfolios:
                print("📭 Chưa có danh mục nào được lưu")
                return
            
            print("="*90)
            print(" "*30 + "📂 DANH MỤC ĐÃ LƯU")
            print("="*90)
            print(f"\nTổng số: {len(portfolios)} danh mục\n")
            
            print(f"{'#':<4} {'Tên':<20} {'Ngày lưu':<20} {'Số mã':<8} {'File':<30}")
            print("-"*90)
            
            for i, p in enumerate(portfolios[:20], 1):
                timestamp = datetime.fromisoformat(p['timestamp']).strftime('%d/%m/%Y %H:%M')
                print(f"{i:<4} {p['name'][:20]:<20} {timestamp:<20} {len(p['symbols']):<8} {p['file'][:30]:<30}")
            
            if len(portfolios) > 20:
                print(f"\n... và {len(portfolios)-20} danh mục khác")
            
            # List price files
            print("\n" + "="*90)
            print(" "*30 + "📊 FILE GIÁ CỔ PHIẾU")
            print("="*90)
            
            price_files = list(self.data_manager.price_dir.glob('*_price.csv'))
            if price_files:
                print(f"\nTổng số: {len(price_files)} file\n")
                for i, pf in enumerate(sorted(price_files)[:20], 1):
                    symbol = pf.stem.replace('_price', '')
                    size = pf.stat().st_size / 1024  # KB
                    mtime = datetime.fromtimestamp(pf.stat().st_mtime).strftime('%d/%m/%Y %H:%M')
                    print(f"{i:<4} {symbol:<15} {size:>8.1f} KB    {mtime}")
                
                if len(price_files) > 20:
                    print(f"\n... và {len(price_files)-20} file khác")
            else:
                print("\n📭 Chưa có file giá nào")
    
    def open_data_folder(self, b):
        """Mở thư mục dữ liệu"""
        import platform
        import subprocess
        
        folder_path = str(self.data_manager.price_dir.absolute())
        
        try:
            if platform.system() == 'Windows':
                os.startfile(folder_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', folder_path])
            else:  # Linux
                subprocess.run(['xdg-open', folder_path])
            
            with self.data_output:
                print(f"\n✅ Đã mở: {folder_path}")
        except Exception as e:
            with self.data_output:
                print(f"\n📁 Đường dẫn: {folder_path}")
                print(f"⚠️ Không thể tự động mở: {e}")
    
    def run_optimize(self, b):
        """Chạy tối ưu với dữ liệu CSV"""
        with self.opt_output:
            clear_output()
            print("🔄 Đang tối ưu danh mục...\n")
        
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
                print("📂 Đang tải dữ liệu từ CSV...\n")
            
            # Load từ CSV
            data, missing_symbols = self.load_data_from_csv(funds, start_date, end_date)
            
            if missing_symbols:
                with self.opt_output:
                    print(f"\n{'='*70}")
                    print(f"⚠️ Thiếu dữ liệu cho {len(missing_symbols)} mã: {', '.join(missing_symbols)}")
                    print(f"\n💡 Hướng dẫn:")
                    print(f"   1. Nhấn '📥 Tải Dữ Liệu Online' để thử download")
                    print(f"   2. Hoặc nhập thủ công vào file CSV:")
                    for symbol in missing_symbols:
                        file_path = self.data_manager.get_price_file_path(symbol)
                        print(f"      • {file_path}")
                    print(f"   3. Sau đó nhấn '🚀 Tối Ưu Danh Mục' lại")
                    print(f"{'='*70}")
                return
            
            if data is None or data.empty:
                with self.opt_output:
                    clear_output()
                    print("❌ Không có dữ liệu!")
                    print("💡 Nhấn '📥 Tải Dữ Liệu Online' để download")
                return
            
            with self.opt_output:
                print(f"\n✅ Tải được {len(data.columns)} tài sản, {len(data)} ngày")
                print("🧹 Đang làm sạch dữ liệu...")
            
            data = self.clean_data(data)
            
            if len(data) < 60 or len(data.columns) < 2:
                with self.opt_output:
                    clear_output()
                    print(f"❌ Dữ liệu không đủ (cần >60 ngày, ≥2 mã)")
                    print(f"   Hiện có: {len(data)} ngày, {len(data.columns)} mã")
                return
            
            self.df = data
            self.symbols_with_weights = list(data.columns)
            
            with self.opt_output:
                print(f"✅ Dữ liệu sạch: {len(data.columns)} tài sản, {len(data)} ngày")
                print("⏳ Đang tối ưu danh mục...")
            
            # Get risk profile settings
            risk_profile = self.opt_risk_profile.value
            target_return = self.opt_target_return.value if risk_profile == 'custom' else None
            max_volatility = self.opt_max_volatility.value if risk_profile == 'custom' else None
            
            # Tối ưu danh mục
            weights, performance, method = self.optimize_portfolio(
                data, 
                mode=self.opt_mode.value,
                risk_profile=risk_profile,
                target_return=target_return,
                max_volatility=max_volatility
            )
            
            self.weights = weights
            self.performance = performance
            self.method = method
            
            with self.opt_output:
                print(f"✅ Hoàn tất! ({method})")
                print(f"📈 Lợi nhuận: {performance[0]*100:.2f}%/năm")
                print(f"📊 Volatility: {performance[1]*100:.2f}%")
                print(f"⭐ Sharpe: {performance[2]:.2f}")
            
            # Save portfolio
            save_file = self.data_manager.save_portfolio_weights(
                self.opt_portfolio_name.value,
                weights,
                performance,
                method,
                self.symbols_with_weights
            )
            
            with self.opt_output:
                print(f"\n💾 Đã lưu: {save_file.name}")
            
            self.display_optimize_result()
            
        except Exception as e:
            with self.opt_output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
                import traceback
                print("\n📋 Chi tiết:")
                print(traceback.format_exc())
    
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
                price = self.data_fetcher.get_latest_price(ticker, market)
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
            
            # Display risk profile info
            risk_info = {
                'conservative': '🛡️ Bảo thủ - Ưu tiên bảo toàn vốn',
                'moderate': '⚖️ Trung bình - Cân bằng rủi ro/lợi nhuận',
                'aggressive': '🚀 Tích cực - Tối đa hóa lợi nhuận',
                'custom': '📊 Tùy chỉnh'
            }
            risk_profile = self.opt_risk_profile.value
            print(f"⚡ Mức độ rủi ro: {risk_info.get(risk_profile, 'Không xác định')}")
            
            if risk_profile == 'custom':
                if self.opt_target_return.value:
                    print(f"   • Mục tiêu LN: {self.opt_target_return.value}%/năm")
                if self.opt_max_volatility.value:
                    print(f"   • Giới hạn rủi ro: {self.opt_max_volatility.value}%")
            
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
                
                total_buy = 0
                total_sell = 0
                
                # MUA
                if len(buys) > 0:
                    print("\n🟢 MUA:")
                    print(f"{'Mã':<10} {'Số lượng':<15} {'Giá':<15} {'Tổng (VNĐ)':<20}")
                    print("-"*90)
                    
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
        print("\n📁 Dữ liệu sẽ được lưu tại: portfolio_data/")
        print("   • price_data/ - File CSV giá (mỗi mã 1 file)")
        print("   • portfolios/ - Kết quả tối ưu (JSON)")
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
