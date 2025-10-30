"""
Portfolio Optimizer & Rebalancer App
Ứng dụng tối ưu và cân bằng danh mục đầu tư chuyên nghiệp
Tích hợp vnstock và quản lý dữ liệu tự động
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# ==================== CẤU HÌNH ====================

DATA_DIR = Path("./data_portfolio")
DATA_DIR.mkdir(exist_ok=True)

OPTIMIZED_FILE = DATA_DIR / "optimized_portfolio.csv"
REBALANCED_FILE = DATA_DIR / "rebalanced_portfolio.csv"
PORTFOLIO_STATE_FILE = DATA_DIR / "portfolio_state.csv"

# ==================== DATA MANAGER ====================

class DataManager:
    """Quản lý dữ liệu cổ phiếu"""
    
    @staticmethod
    def get_data_filepath(ticker):
        """Lấy đường dẫn file dữ liệu cho mã cổ phiếu"""
        return DATA_DIR / f"{ticker}.csv"
    
    @staticmethod
    def create_empty_csv(ticker):
        """Tạo file CSV trống với cấu trúc chuẩn"""
        filepath = DataManager.get_data_filepath(ticker)
        df = pd.DataFrame(columns=['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df.to_csv(filepath, index=False)
        return filepath
    
    @staticmethod
    def load_data(ticker):
        """Tải dữ liệu từ file CSV"""
        filepath = DataManager.get_data_filepath(ticker)
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.sort_values('Date')
                return df
            except Exception as e:
                st.error(f"Lỗi đọc file {ticker}: {e}")
                return None
        return None
    
    @staticmethod
    def save_data(ticker, df):
        """Lưu dữ liệu vào file CSV"""
        filepath = DataManager.get_data_filepath(ticker)
        df.to_csv(filepath, index=False)
        return filepath
    
    @staticmethod
    def fetch_from_vnstock(ticker, start_date, end_date):
        """Tải dữ liệu từ vnstock"""
        try:
            from vnstock3 import Vnstock
            stock = Vnstock().stock(symbol=ticker, source='VCI')
            df = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )
            
            if df is not None and not df.empty:
                # Chuẩn hóa dữ liệu
                result = pd.DataFrame()
                result['Date'] = pd.to_datetime(df['time']) if 'time' in df.columns else df.index
                result['Ticker'] = ticker
                result['Open'] = df['open'] if 'open' in df.columns else df['Open']
                result['High'] = df['high'] if 'high' in df.columns else df['High']
                result['Low'] = df['low'] if 'low' in df.columns else df['Low']
                result['Close'] = df['close'] if 'close' in df.columns else df['Close']
                result['Volume'] = df['volume'] if 'volume' in df.columns else df['Volume']
                
                return result
        except Exception as e:
            st.warning(f"Không tải được {ticker} từ vnstock: {e}")
        
        return None
    
    @staticmethod
    def get_all_tickers():
        """Lấy danh sách tất cả các mã cổ phiếu đã lưu"""
        csv_files = list(DATA_DIR.glob("*.csv"))
        tickers = []
        for f in csv_files:
            if f.name not in ['optimized_portfolio.csv', 'rebalanced_portfolio.csv', 'portfolio_state.csv']:
                tickers.append(f.stem)
        return sorted(tickers)

# ==================== PORTFOLIO OPTIMIZER ====================

class PortfolioOptimizer:
    """Tối ưu danh mục đầu tư"""
    
    @staticmethod
    def prepare_data(tickers, start_date, end_date):
        """Chuẩn bị dữ liệu giá đóng cửa"""
        all_data = {}
        
        for ticker in tickers:
            df = DataManager.load_data(ticker)
            if df is not None and not df.empty and 'Date' in df.columns and 'Close' in df.columns:
                df = df[['Date', 'Close']].copy()
                df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
                if len(df) > 0:
                    df = df.set_index('Date')
                    all_data[ticker] = df['Close']
        
        if not all_data:
            return None
        
        # Kết hợp dữ liệu
        combined_df = pd.DataFrame(all_data)
        combined_df = combined_df.dropna()
        
        return combined_df
    
    @staticmethod
    def calculate_returns(prices):
        """Tính lợi nhuận"""
        returns = prices.pct_change().dropna()
        return returns
    
    @staticmethod
    def optimize_portfolio(returns, method='min_volatility'):
        """Tối ưu danh mục"""
        n_assets = len(returns.columns)
        
        # Tính toán các thông số
        mean_returns = returns.mean() * 252  # Annualized
        cov_matrix = returns.cov() * 252  # Annualized
        
        if method == 'equal_weight':
            weights = np.array([1/n_assets] * n_assets)
        else:
            # Tối ưu hóa - Minimum Volatility
            from scipy.optimize import minimize
            
            def portfolio_volatility(weights, cov_matrix):
                return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
            bounds = tuple((0, 1) for _ in range(n_assets))
            initial_weights = np.array([1/n_assets] * n_assets)
            
            result = minimize(
                portfolio_volatility,
                initial_weights,
                args=(cov_matrix,),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            weights = result.x
        
        # Tính toán hiệu suất
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0
        
        # Tạo DataFrame kết quả
        result_df = pd.DataFrame({
            'Ticker': returns.columns,
            'Weight': weights,
            'Weight_%': weights * 100
        })
        result_df = result_df[result_df['Weight'] > 0.001].sort_values('Weight', ascending=False)
        
        performance = {
            'Expected_Return': portfolio_return,
            'Volatility': portfolio_std,
            'Sharpe_Ratio': sharpe_ratio
        }
        
        return result_df, performance
    
    @staticmethod
    def save_optimized_portfolio(result_df, performance):
        """Lưu kết quả tối ưu"""
        # Lưu weights
        result_df.to_csv(OPTIMIZED_FILE, index=False)
        
        # Lưu trạng thái để dùng cho rebalancing
        state_df = result_df.copy()
        state_df['Target_Weight_%'] = state_df['Weight_%']
        state_df.to_csv(PORTFOLIO_STATE_FILE, index=False)
        
        return OPTIMIZED_FILE

# ==================== PORTFOLIO REBALANCER ====================

class PortfolioRebalancer:
    """Cân bằng danh mục đầu tư"""
    
    @staticmethod
    def load_target_weights():
        """Tải tỷ trọng mục tiêu từ file đã tối ưu"""
        if PORTFOLIO_STATE_FILE.exists():
            df = pd.read_csv(PORTFOLIO_STATE_FILE)
            return df
        return None
    
    @staticmethod
    def calculate_rebalancing(current_holdings, target_weights, threshold=5.0):
        """Tính toán cân bằng danh mục
        
        Args:
            current_holdings: DataFrame với columns [Ticker, Shares, Cost_Basis]
            target_weights: DataFrame với columns [Ticker, Target_Weight_%]
            threshold: Ngưỡng drift (%) để cần cân bằng
        """
        # Lấy giá hiện tại
        current_prices = {}
        for ticker in current_holdings['Ticker'].unique():
            df = DataManager.load_data(ticker)
            if df is not None and not df.empty:
                current_prices[ticker] = df['Close'].iloc[-1]
        
        # Tính giá trị hiện tại
        current_holdings['Current_Price'] = current_holdings['Ticker'].map(current_prices)
        current_holdings['Current_Value'] = current_holdings['Shares'] * current_holdings['Current_Price']
        
        total_value = current_holdings['Current_Value'].sum()
        current_holdings['Current_Weight_%'] = (current_holdings['Current_Value'] / total_value) * 100
        
        # Merge với target weights
        rebalance_df = current_holdings.merge(
            target_weights[['Ticker', 'Target_Weight_%']], 
            on='Ticker', 
            how='outer'
        )
        
        rebalance_df = rebalance_df.fillna(0)
        
        # Tính drift
        rebalance_df['Drift_%'] = rebalance_df['Target_Weight_%'] - rebalance_df['Current_Weight_%']
        rebalance_df['Needs_Rebalance'] = abs(rebalance_df['Drift_%']) > threshold
        
        # Tính số lượng cần thay đổi
        rebalance_df['Target_Value'] = (rebalance_df['Target_Weight_%'] / 100) * total_value
        rebalance_df['Value_Change'] = rebalance_df['Target_Value'] - rebalance_df['Current_Value']
        rebalance_df['Shares_Change'] = rebalance_df['Value_Change'] / rebalance_df['Current_Price']
        rebalance_df['Shares_Change'] = rebalance_df['Shares_Change'].fillna(0)
        
        # Làm tròn theo lô 100 (TTCK VN)
        rebalance_df['Shares_Change_Rounded'] = (rebalance_df['Shares_Change'] / 100).round() * 100
        rebalance_df['New_Shares'] = rebalance_df['Shares'] + rebalance_df['Shares_Change_Rounded']
        
        return rebalance_df
    
    @staticmethod
    def save_rebalancing_result(rebalance_df):
        """Lưu kết quả cân bằng"""
        rebalance_df.to_csv(REBALANCED_FILE, index=False)
        return REBALANCED_FILE

# ==================== VISUALIZATION ====================

class Visualizer:
    """Tạo các biểu đồ trực quan"""
    
    @staticmethod
    def plot_allocation_pie(weights_df):
        """Vẽ biểu đồ tròn phân bổ"""
        fig = go.Figure(data=[go.Pie(
            labels=weights_df['Ticker'],
            values=weights_df['Weight_%'],
            hole=0.3,
            textinfo='label+percent',
            textposition='auto'
        )])
        
        fig.update_layout(
            title='📊 Phân Bổ Danh Mục Tối Ưu',
            height=500,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def plot_price_history(prices_df):
        """Vẽ lịch sử giá"""
        fig = go.Figure()
        
        # Chuẩn hóa giá về 100
        normalized = (prices_df / prices_df.iloc[0]) * 100
        
        for col in normalized.columns:
            fig.add_trace(go.Scatter(
                x=normalized.index,
                y=normalized[col],
                mode='lines',
                name=col,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title='📈 Lịch Sử Giá (Chuẩn Hóa = 100)',
            xaxis_title='Ngày',
            yaxis_title='Giá trị',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def plot_rebalancing_comparison(rebalance_df):
        """Vẽ so sánh trước/sau cân bằng"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Hiện tại',
            x=rebalance_df['Ticker'],
            y=rebalance_df['Current_Weight_%'],
            marker_color='#e74c3c'
        ))
        
        fig.add_trace(go.Bar(
            name='Mục tiêu',
            x=rebalance_df['Ticker'],
            y=rebalance_df['Target_Weight_%'],
            marker_color='#27ae60'
        ))
        
        fig.update_layout(
            title='⚖️ So Sánh Tỷ Trọng: Hiện Tại vs Mục Tiêu',
            xaxis_title='Mã CK',
            yaxis_title='Tỷ trọng (%)',
            barmode='group',
            height=500
        )
        
        return fig

# ==================== STREAMLIT APP ====================

def main():
    st.set_page_config(
        page_title="Portfolio Optimizer Pro",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS tùy chỉnh
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💼 PORTFOLIO OPTIMIZER PRO</h1>
        <p>Tối ưu & Cân bằng Danh mục Đầu tư Chuyên nghiệp</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=Portfolio+Pro", use_container_width=True)
        st.markdown("---")
        
        page = st.radio(
            "📌 Chọn chức năng",
            ["📊 Tối Ưu Danh Mục", "⚖️ Cân Bằng Danh Mục", "📁 Quản Lý Dữ Liệu"],
            index=0
        )
        
        st.markdown("---")
        st.info(f"📂 Thư mục dữ liệu: `{DATA_DIR}`")
        
        existing_tickers = DataManager.get_all_tickers()
        if existing_tickers:
            st.success(f"✅ Đã có {len(existing_tickers)} mã trong hệ thống")
    
    # Main content
    if page == "📊 Tối Ưu Danh Mục":
        show_optimization_page()
    elif page == "⚖️ Cân Bằng Danh Mục":
        show_rebalancing_page()
    else:
        show_data_management_page()


def show_optimization_page():
    """Trang tối ưu danh mục"""
    st.header("📊 Tối Ưu Danh Mục Đầu Tư")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Thiết lập danh mục")
        
        # Input danh mục
        portfolio_input = st.text_area(
            "Nhập danh sách mã cổ phiếu (cách nhau bởi dấu phẩy hoặc xuống dòng)",
            value="VNM, VIC, GAS, FPT, HPG",
            height=100,
            help="Ví dụ: VNM, VIC, GAS hoặc mỗi mã một dòng"
        )
        
        # Xử lý input
        tickers = []
        for line in portfolio_input.split('\n'):
            tickers.extend([t.strip().upper() for t in line.split(',') if t.strip()])
        tickers = list(set(tickers))
        
        if tickers:
            st.info(f"📝 Đã nhập {len(tickers)} mã: {', '.join(tickers)}")
    
    with col2:
        st.subheader("⚙️ Cấu hình")
        
        date_range = st.date_input(
            "Khoảng thời gian",
            value=(datetime.now() - timedelta(days=730), datetime.now()),
            help="Chọn khoảng thời gian để tối ưu"
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = datetime.now() - timedelta(days=730)
            end_date = datetime.now()
        
        optimization_method = st.selectbox(
            "Phương pháp tối ưu",
            ["min_volatility", "equal_weight"],
            format_func=lambda x: "Tối thiểu rủi ro" if x == "min_volatility" else "Phân bổ đều"
        )
    
    st.markdown("---")
    
    # Tải dữ liệu
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Tải dữ liệu từ vnstock", type="primary", use_container_width=True):
            with st.spinner("Đang tải dữ liệu..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, ticker in enumerate(tickers):
                    status_text.text(f"Đang tải {ticker}...")
                    
                    df = DataManager.fetch_from_vnstock(ticker, start_date, end_date)
                    
                    if df is not None and not df.empty:
                        DataManager.save_data(ticker, df)
                        st.success(f"✅ {ticker}: {len(df)} ngày")
                    else:
                        # Tạo file CSV trống
                        filepath = DataManager.create_empty_csv(ticker)
                        st.warning(f"⚠️ {ticker}: Không có dữ liệu, đã tạo file trống tại `{filepath}`")
                    
                    progress_bar.progress((i + 1) / len(tickers))
                
                status_text.text("✅ Hoàn tất!")
                st.balloons()
    
    with col2:
        if st.button("🔄 Cập nhật dữ liệu mới nhất", use_container_width=True):
            st.info("Đang cập nhật dữ liệu mới nhất từ vnstock...")
            # Logic tương tự như tải dữ liệu
    
    with col3:
        if st.button("🗑️ Xóa cache", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Đã xóa cache!")
    
    st.markdown("---")
    
    # Tối ưu hóa
    st.subheader("🚀 Chạy tối ưu hóa")
    
    if st.button("▶️ Tối Ưu Danh Mục", type="primary", use_container_width=True):
        with st.spinner("Đang tối ưu danh mục..."):
            # Chuẩn bị dữ liệu
            prices = PortfolioOptimizer.prepare_data(tickers, start_date, end_date)
            
            if prices is None or prices.empty:
                st.error("❌ Không có đủ dữ liệu để tối ưu!")
                st.info("💡 Hãy tải dữ liệu từ vnstock hoặc nhập dữ liệu thủ công")
                return
            
            st.success(f"✅ Đã tải {len(prices.columns)} mã với {len(prices)} ngày dữ liệu")
            
            # Tính returns
            returns = PortfolioOptimizer.calculate_returns(prices)
            
            # Tối ưu
            result_df, performance = PortfolioOptimizer.optimize_portfolio(
                returns, 
                method=optimization_method
            )
            
            # Lưu kết quả
            PortfolioOptimizer.save_optimized_portfolio(result_df, performance)
            
            # Hiển thị kết quả
            st.success("🎉 Tối ưu hoàn tất!")
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "📈 Lợi nhuận kỳ vọng/năm",
                    f"{performance['Expected_Return']*100:.2f}%"
                )
            
            with col2:
                st.metric(
                    "📊 Độ lệch chuẩn (Rủi ro)",
                    f"{performance['Volatility']*100:.2f}%"
                )
            
            with col3:
                st.metric(
                    "⭐ Sharpe Ratio",
                    f"{performance['Sharpe_Ratio']:.2f}"
                )
            
            # Bảng phân bổ
            st.subheader("💼 Tỷ trọng phân bổ tối ưu")
            st.dataframe(
                result_df.style.format({
                    'Weight': '{:.4f}',
                    'Weight_%': '{:.2f}%'
                }).background_gradient(subset=['Weight_%'], cmap='Greens'),
                use_container_width=True
            )
            
            # Biểu đồ
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie = Visualizer.plot_allocation_pie(result_df)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                fig_history = Visualizer.plot_price_history(prices)
                st.plotly_chart(fig_history, use_container_width=True)
            
            # Download
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tải xuống kết quả (CSV)",
                data=csv,
                file_name=f"optimized_portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )


def show_rebalancing_page():
    """Trang cân bằng danh mục"""
    st.header("⚖️ Cân Bằng Danh Mục")
    
    # Tải target weights
    target_weights = PortfolioRebalancer.load_target_weights()
    
    if target_weights is None:
        st.warning("⚠️ Chưa có danh mục tối ưu!")
        st.info("💡 Hãy chạy tối ưu danh mục trước")
        return
    
    st.success(f"✅ Đã tải tỷ trọng mục tiêu cho {len(target_weights)} mã")
    
    with st.expander("📋 Xem tỷ trọng mục tiêu", expanded=False):
        st.dataframe(target_weights, use_container_width=True)
    
    st.markdown("---")
    
    # Input danh mục hiện tại
    st.subheader("📝 Nhập danh mục hiện tại")
    
    st.info("""
    **Hướng dẫn nhập:**
    - Format: `MÃ, SỐ_LƯỢNG, GIÁ_MUA`
    - Ví dụ: `VNM, 1000, 85000`
    - Mỗi dòng một mã cổ phiếu
    """)
    
    current_input = st.text_area(
        "Danh mục hiện tại",
        value="VNM, 1000, 85000\nVIC, 500, 90000\nGAS, 800, 75000",
        height=150
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        threshold = st.slider(
            "Ngưỡng drift (%)",
            min_value=1.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            help="Nếu độ lệch vượt ngưỡng này, cần cân bằng lại"
        )
    
    with col2:
        new_capital = st.number_input(
            "Vốn mới bổ sung (VNĐ)",
            min_value=0.0,
            value=0.0,
            step=1000000.0,
            format="%.0f"
        )
    
    st.markdown("---")
    
    # Parse input
    if st.button("🔍 Phân Tích Cân Bằng", type="primary", use_container_width=True):
        try:
            # Parse current holdings
            holdings_data = []
            for line in current_input.strip().split('\n'):
                if line.strip():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) == 3:
                        holdings_data.append({
                            'Ticker': parts[0].upper(),
                            'Shares': float(parts[1]),
                            'Cost_Basis': float(parts[2])
                        })
            
            if not holdings_data:
                st.error("❌ Không có dữ liệu danh mục hiện tại!")
                return
            
            current_holdings = pd.DataFrame(holdings_data)
            
            with st.spinner("Đang phân tích..."):
                # Tính toán cân bằng
                rebalance_df = PortfolioRebalancer.calculate_rebalancing(
                    current_holdings,
                    target_weights,
                    threshold=threshold
                )
                
                # Lưu kết quả
                PortfolioRebalancer.save_rebalancing_result(rebalance_df)
                
                st.success("✅ Phân tích hoàn tất!")
                
                # Tổng quan
                total_value = rebalance_df['Current_Value'].sum()
                needs_rebalance = rebalance_df['Needs_Rebalance'].sum()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("💰 Tổng giá trị hiện tại", f"{total_value:,.0f} VNĐ")
                
                with col2:
                    st.metric("⚠️ Cần cân bằng", f"{needs_rebalance}/{len(rebalance_df)} mã")
                
                with col3:
                    st.metric("💵 Vốn mới", f"{new_capital:,.0f} VNĐ")
                
                # Bảng chi tiết
                st.subheader("📊 Chi tiết phân tích")
                
                display_df = rebalance_df[[
                    'Ticker', 'Shares', 'Current_Price', 'Current_Value',
                    'Current_Weight_%', 'Target_Weight_%', 'Drift_%', 'Needs_Rebalance',
                    'Shares_Change_Rounded'
                ]].copy()
                
                display_df.columns = [
                    'Mã', 'SL Hiện Tại', 'Giá', 'GT Hiện Tại',
                    '% Hiện Tại', '% Mục Tiêu', 'Drift %', 'Cần CB', 'Thay Đổi SL'
                ]
                
                # Format và highlight
                styled_df = display_df.style.format({
                    'SL Hiện Tại': '{:.0f}',
                    'Giá': '{:,.0f}',
                    'GT Hiện Tại': '{:,.0f}',
                    '% Hiện Tại': '{:.2f}',
                    '% Mục Tiêu': '{:.2f}',
                    'Drift %': '{:.2f}',
                    'Thay Đổi SL': '{:.0f}'
                }).background_gradient(subset=['Drift %'], cmap='RdYlGn_r', vmin=-10, vmax=10)
                
                st.dataframe(styled_df, use_container_width=True)
                
                # Biểu đồ so sánh
                fig_comparison = Visualizer.plot_rebalancing_comparison(rebalance_df)
                st.plotly_chart(fig_comparison, use_container_width=True)
                
                # Giao dịch cần thực hiện
                st.subheader("💼 Giao dịch cần thực hiện")
                
                transactions = rebalance_df[rebalance_df['Shares_Change_Rounded'] != 0].copy()
                
                if len(transactions) == 0:
                    st.success("🎉 Danh mục đã cân bằng! Không cần giao dịch.")
                else:
                    buy_trans = transactions[transactions['Shares_Change_Rounded'] > 0]
                    sell_trans = transactions[transactions['Shares_Change_Rounded'] < 0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if len(buy_trans) > 0:
                            st.markdown("### 🟢 MUA")
                            buy_display = buy_trans[['Ticker', 'Shares_Change_Rounded', 'Current_Price']].copy()
                            buy_display['Tổng tiền'] = buy_display['Shares_Change_Rounded'] * buy_display['Current_Price']
                            buy_display.columns = ['Mã', 'Số lượng', 'Giá', 'Tổng (VNĐ)']
                            
                            st.dataframe(
                                buy_display.style.format({
                                    'Số lượng': '{:.0f}',
                                    'Giá': '{:,.0f}',
                                    'Tổng (VNĐ)': '{:,.0f}'
                                }),
                                use_container_width=True
                            )
                            
                            total_buy = buy_display['Tổng (VNĐ)'].sum()
                            st.metric("💰 Tổng tiền cần mua", f"{total_buy:,.0f} VNĐ")
                    
                    with col2:
                        if len(sell_trans) > 0:
                            st.markdown("### 🔴 BÁN")
                            sell_display = sell_trans[['Ticker', 'Shares_Change_Rounded', 'Current_Price']].copy()
                            sell_display['Shares_Change_Rounded'] = abs(sell_display['Shares_Change_Rounded'])
                            sell_display['Tổng tiền'] = sell_display['Shares_Change_Rounded'] * sell_display['Current_Price']
                            sell_display.columns = ['Mã', 'Số lượng', 'Giá', 'Tổng (VNĐ)']
                            
                            st.dataframe(
                                sell_display.style.format({
                                    'Số lượng': '{:.0f}',
                                    'Giá': '{:,.0f}',
                                    'Tổng (VNĐ)': '{:,.0f}'
                                }),
                                use_container_width=True
                            )
                            
                            total_sell = sell_display['Tổng (VNĐ)'].sum()
                            st.metric("💵 Tổng tiền thu được", f"{total_sell:,.0f} VNĐ")
                    
                    # Tổng kết
                    st.markdown("---")
                    st.subheader("📊 Tổng kết giao dịch")
                    
                    total_buy = buy_trans['Shares_Change_Rounded'].dot(buy_trans['Current_Price']) if len(buy_trans) > 0 else 0
                    total_sell = abs(sell_trans['Shares_Change_Rounded'].dot(sell_trans['Current_Price'])) if len(sell_trans) > 0 else 0
                    
                    net_cash = total_sell + new_capital - total_buy
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("💵 Tiền bán", f"{total_sell:,.0f}")
                    with col2:
                        st.metric("💰 Vốn mới", f"{new_capital:,.0f}")
                    with col3:
                        st.metric("💳 Tiền mua", f"{total_buy:,.0f}")
                    with col4:
                        st.metric("💸 Chênh lệch", f"{net_cash:,.0f}", 
                                 delta="Dư" if net_cash > 0 else "Thiếu")
                    
                    st.info("""
                    **💡 Lưu ý giao dịch TTCK Việt Nam:**
                    - 📦 Khối lượng: Bội số 100 cổ phiếu
                    - 📅 Thanh toán: T+2 (2 ngày làm việc)
                    - 💰 Phí giao dịch: ~0.15-0.3% (phí môi giới + thuế)
                    - ⏰ Giờ giao dịch: 9h00 - 11h30, 13h00 - 14h30
                    """)
                
                # Download
                csv = rebalance_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Tải xuống kết quả cân bằng (CSV)",
                    data=csv,
                    file_name=f"rebalanced_portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")
            st.exception(e)


def show_data_management_page():
    """Trang quản lý dữ liệu"""
    st.header("📁 Quản Lý Dữ Liệu")
    
    # Danh sách tất cả các mã
    all_tickers = DataManager.get_all_tickers()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Danh sách mã cổ phiếu trong hệ thống")
        
        if all_tickers:
            st.success(f"✅ Có {len(all_tickers)} mã trong hệ thống")
            
            # Tạo bảng thông tin
            data_info = []
            for ticker in all_tickers:
                df = DataManager.load_data(ticker)
                if df is not None:
                    data_info.append({
                        'Mã': ticker,
                        'Số dòng': len(df),
                        'Từ ngày': df['Date'].min().strftime('%Y-%m-%d') if 'Date' in df.columns and len(df) > 0 else 'N/A',
                        'Đến ngày': df['Date'].max().strftime('%Y-%m-%d') if 'Date' in df.columns and len(df) > 0 else 'N/A',
                        'File': f"{ticker}.csv"
                    })
            
            info_df = pd.DataFrame(data_info)
            st.dataframe(info_df, use_container_width=True)
        else:
            st.info("📭 Chưa có dữ liệu nào trong hệ thống")
    
    with col2:
        st.subheader("⚙️ Thao tác")
        
        # Thêm mã mới
        new_ticker = st.text_input("Thêm mã mới", placeholder="Ví dụ: VNM")
        
        if st.button("➕ Tạo file CSV trống", use_container_width=True):
            if new_ticker:
                ticker = new_ticker.strip().upper()
                filepath = DataManager.create_empty_csv(ticker)
                st.success(f"✅ Đã tạo file: `{filepath}`")
                st.info("💡 Bạn có thể tải file này về, nhập dữ liệu thủ công, rồi tải lên lại")
            else:
                st.warning("⚠️ Hãy nhập mã cổ phiếu")
        
        st.markdown("---")
        
        # Xóa dữ liệu
        if all_tickers:
            ticker_to_delete = st.selectbox("Xóa dữ liệu mã", [""] + all_tickers)
            
            if st.button("🗑️ Xóa", type="secondary", use_container_width=True):
                if ticker_to_delete:
                    filepath = DataManager.get_data_filepath(ticker_to_delete)
                    try:
                        filepath.unlink()
                        st.success(f"✅ Đã xóa {ticker_to_delete}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Lỗi: {e}")
    
    st.markdown("---")
    
    # Upload dữ liệu thủ công
    st.subheader("📤 Tải lên dữ liệu thủ công")
    
    st.info("""
    **Hướng dẫn:**
    1. Tải file CSV mẫu cho mã cổ phiếu (nếu chưa có)
    2. Mở file bằng Excel, nhập dữ liệu theo format: Date, Ticker, Open, High, Low, Close, Volume
    3. Lưu lại và tải lên ở đây
    """)
    
    uploaded_file = st.file_uploader(
        "Chọn file CSV",
        type=['csv'],
        help="File CSV phải có cột: Date, Ticker, Open, High, Low, Close, Volume"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validate
            required_cols = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Thiếu các cột: {', '.join(missing_cols)}")
            else:
                st.success("✅ File hợp lệ!")
                
                # Preview
                st.write("**Xem trước dữ liệu:**")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Lưu
                if st.button("💾 Lưu vào hệ thống", type="primary"):
                    ticker = df['Ticker'].iloc[0]
                    DataManager.save_data(ticker, df)
                    st.success(f"✅ Đã lưu dữ liệu cho {ticker}")
                    st.balloons()
        
        except Exception as e:
            st.error(f"❌ Lỗi đọc file: {e}")
    
    st.markdown("---")
    
    # Xem chi tiết dữ liệu
    st.subheader("🔍 Xem chi tiết dữ liệu")
    
    if all_tickers:
        selected_ticker = st.selectbox("Chọn mã để xem", all_tickers)
        
        if selected_ticker:
            df = DataManager.load_data(selected_ticker)
            
            if df is not None and not df.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📊 Số dòng", len(df))
                with col2:
                    if 'Date' in df.columns:
                        st.metric("📅 Từ ngày", df['Date'].min().strftime('%Y-%m-%d'))
                with col3:
                    if 'Date' in df.columns:
                        st.metric("📅 Đến ngày", df['Date'].max().strftime('%Y-%m-%d'))
                
                # Hiển thị dữ liệu
                st.dataframe(df, use_container_width=True)
                
                # Download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Tải xuống {selected_ticker}.csv",
                    data=csv,
                    file_name=f"{selected_ticker}.csv",
                    mime="text/csv"
                )
                
                # Biểu đồ giá
                if 'Date' in df.columns and 'Close' in df.columns:
                    st.subheader(f"📈 Biểu đồ giá {selected_ticker}")
                    
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df['Date'],
                        open=df['Open'] if 'Open' in df.columns else df['Close'],
                        high=df['High'] if 'High' in df.columns else df['Close'],
                        low=df['Low'] if 'Low' in df.columns else df['Close'],
                        close=df['Close'],
                        name=selected_ticker
                    ))
                    
                    fig.update_layout(
                        title=f'Giá {selected_ticker}',
                        yaxis_title='Giá (VNĐ)',
                        xaxis_title='Ngày',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Thống kê hệ thống
    st.subheader("📊 Thống kê hệ thống")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📦 Tổng số mã", len(all_tickers))
    
    with col2:
        total_rows = sum(len(DataManager.load_data(t)) for t in all_tickers if DataManager.load_data(t) is not None)
        st.metric("📊 Tổng số dòng dữ liệu", f"{total_rows:,}")
    
    with col3:
        # Tính dung lượng thư mục
        total_size = sum(f.stat().st_size for f in DATA_DIR.glob("*.csv"))
        st.metric("💾 Dung lượng", f"{total_size / 1024 / 1024:.2f} MB")
    
    # Backup/Restore
    st.markdown("---")
    st.subheader("💾 Sao lưu & Khôi phục")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📦 Tạo bản sao lưu", use_container_width=True):
            st.info("Tính năng đang phát triển...")
    
    with col2:
        if st.button("♻️ Khôi phục từ backup", use_container_width=True):
            st.info("Tính năng đang phát triển...")


if __name__ == "__main__":
    main()
