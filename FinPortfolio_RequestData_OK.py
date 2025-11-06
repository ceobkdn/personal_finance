import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go


import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API")

class StockInfoWidget:
    def __init__(self):
        # Ô nhập mã cổ phiếu
        self.symbol_input = widgets.Text(
            value='VNM',
            placeholder='Nhập mã cổ phiếu, ví dụ: VNM, FPT, E1VFVN30...',
            description='Mã CP:',
            style={'description_width': '100px'}
        )

        # Chọn ngày bắt đầu và kết thúc
        today = datetime.now().date()
        self.start_date_picker = widgets.DatePicker(
            description='Từ ngày:',
            value=today - timedelta(days=60),
            style={'description_width': '100px'}
        )
        self.end_date_picker = widgets.DatePicker(
            description='Đến ngày:',
            value=today,
            style={'description_width': '100px'}
        )

        # Nút thực thi
        self.fetch_button = widgets.Button(
            description='📈 Lấy Dữ Liệu',
            button_style='primary',
            icon='download'
        )

        # Khu vực hiển thị
        self.output = widgets.Output()

        # Gắn sự kiện
        self.fetch_button.on_click(self.fetch_stock_info)

        # Layout
        self.container = widgets.VBox([
            widgets.HTML("<h2>Tra Cứu & Biểu Đồ Cổ Phiếu</h2>"),
            self.symbol_input,
            widgets.HBox([self.start_date_picker, self.end_date_picker]),
            self.fetch_button,
            self.output
        ])

    def fetch_stock_info(self, button):
        with self.output:
            clear_output(wait=True)

            symbol = self.symbol_input.value.strip().upper()
            if not symbol:
                print("⚠️ Vui lòng nhập mã cổ phiếu hợp lệ (VD: FPT, VNM, SSI...)")
                return

            start_date = self.start_date_picker.value
            end_date = self.end_date_picker.value

            if start_date >= end_date:
                print("⚠️ Ngày bắt đầu phải nhỏ hơn ngày kết thúc!")
                return

            try:
                # Import vnstock
                try:
                    from vnstock import stock_historical_data
                except ImportError:
                    print("❌ Chưa cài đặt thư viện vnstock.")
                    print("➡️ Cài đặt bằng lệnh: pip install vnstock plotly ipywidgets")
                    return

                print(f"🔍 Đang tải dữ liệu cho mã {symbol}...")
                print(f"⏳ Từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}\n")

                # Lấy dữ liệu
                df = stock_historical_data(
                    symbol=symbol,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    resolution='1D',
                    type='stock'
                )

                if df is None or df.empty:
                    print(f"❌ Không tìm thấy dữ liệu cho mã {symbol}")
                    return

                # Chuẩn hóa dữ liệu
                if 'time' in df.columns:
                    df['time'] = pd.to_datetime(df['time'])
                elif 'TradingDate' in df.columns:
                    df['time'] = pd.to_datetime(df['TradingDate'])
                else:
                    df['time'] = pd.to_datetime(df.index)
                df.sort_values('time', inplace=True)

                # Lấy ngày đầu và cuối
                first_row = df.iloc[0]
                last_row = df.iloc[-1]

                open_first = first_row.get('open', 0)
                close_last = last_row.get('close', 0)
                volume_avg = df['volume'].mean() if 'volume' in df.columns else 0

                change_value = close_last - open_first
                change_percent = (change_value / open_first * 100) if open_first > 0 else 0
                color = "green" if change_value >= 0 else "red"
                arrow = "📈" if change_value >= 0 else "📉"

                # ==== HIỂN THỊ THÔNG TIN TỔNG HỢP ====
                display(HTML(f"""
                <div style='border:2px solid #4CAF50; padding:20px; border-radius:10px; background-color:#f9f9f9;'>
                    <h3 style='color:#4CAF50;'>Thông Tin Tổng Hợp: {symbol}</h3>
                    <p><strong>Khoảng thời gian:</strong> {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}</p>
                    <hr>
                    <table style='width:100%; border-collapse:collapse;'>
                        <tr><td><b>Giá đầu kỳ (Open)</b></td><td style='text-align:right;'>{open_first:,.2f} VND</td></tr>
                        <tr><td><b>Giá cuối kỳ (Close)</b></td><td style='text-align:right;'>{close_last:,.2f} VND</td></tr>
                        <tr><td><b>Khối lượng trung bình</b></td><td style='text-align:right;'>{int(volume_avg):,}</td></tr>
                    </table>
                    <hr>
                    <p style='text-align:center; color:{color}; font-size:18px; font-weight:bold;'>
                        {arrow} Biến động: {change_percent:+.2f}% ({change_value:+,.2f} VND)
                    </p>
                </div>
                """))

                # ==== VẼ BIỂU ĐỒ TƯƠNG TÁC (PLOTLY) ====
                fig = go.Figure()

                # Biểu đồ nến OHLC
                fig.add_trace(go.Candlestick(
                    x=df['time'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Giá (Candlestick)'
                ))

                # Thêm khối lượng
                if 'volume' in df.columns:
                    fig.add_trace(go.Bar(
                        x=df['time'],
                        y=df['volume'],
                        name='Khối lượng',
                        yaxis='y2',
                        opacity=0.3,
                        marker_color='rgba(100, 149, 237, 0.5)'
                    ))

                # Cấu hình layout
                fig.update_layout(
                    title=f"Biểu đồ giá cổ phiếu {symbol}",
                    xaxis_title="Ngày giao dịch",
                    yaxis_title="Giá (VND)",
                    yaxis2=dict(
                        title="Khối lượng",
                        overlaying='y',
                        side='right',
                        showgrid=False
                    ),
                    hovermode='x unified',
                    template='plotly_white',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=40, r=40, t=60, b=40)
                )

                fig.update_xaxes(rangeslider_visible=True)
                fig.show()

                # Bảng dữ liệu gần nhất
                print("\n📋 Dữ liệu 5 ngày gần nhất:")
                display(df.tail(5)[['time', 'open', 'close', 'high', 'low', 'volume']])

            except Exception as e:
                print(f"❌ Lỗi: {e}")

    def display(self):
        display(self.container)


# Chạy ứng dụng
print("🚀 Khởi tạo ứng dụng tra cứu cổ phiếu nâng cao (Plotly interactive)...")
print("📦 Cần cài: pip install vnstock plotly ipywidgets\n")

app = StockInfoWidget()
app.display()

print("\n📝 Hướng dẫn:")
print("1️⃣ Nhập mã cổ phiếu (VD: FPT, VNM, E1VFVN30)")
print("2️⃣ Chọn khoảng thời gian cần xem")
print("3️⃣ Nhấn '📈 Lấy Dữ Liệu'")
print("4️⃣ Xem biểu đồ tương tác (zoom, rê chuột xem chi tiết)")
