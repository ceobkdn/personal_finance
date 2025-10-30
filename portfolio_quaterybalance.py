import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import warnings
warnings.filterwarnings('ignore')

# Thiết lập style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class QuarterlyFundPortfolio:
    def __init__(self):
        """
        Ứng dụng phân bổ đầu tư quỹ theo quý cho người mới bắt đầu
        """
        self.df = None
        self.quarterly_results = {}
        self.current_quarter = self.get_current_quarter()
        
        # Danh sách quỹ mẫu (ETF và Bond funds phổ biến tại VN/châu Á)
        self.sample_funds = {
            '🌏 Quỹ ETF Việt Nam': {
                'E1VFVN30.VN': 'VN30 ETF (Top 30 CP VN)',
                'FUEVFVND.VN': 'DCVFM VN Diamond ETF',
                'FUESSVFL.VN': 'SSIAM VN ETF',
            },
            '🌎 Quỹ ETF Quốc tế': {
                'SPY': 'SPDR S&P 500 ETF (Mỹ)',
                'QQQ': 'Invesco QQQ ETF (Tech Mỹ)',
                'VTI': 'Vanguard Total Stock Market',
                'EEM': 'iShares MSCI Emerging Markets',
                'VEA': 'Vanguard Developed Markets',
                'VXUS': 'Vanguard Total International Stock',
            },
            '📊 Quỹ Trái phiếu': {
                'BND': 'Vanguard Total Bond Market',
                'AGG': 'iShares Core US Aggregate Bond',
                'TLT': 'iShares 20+ Year Treasury Bond',
                'LQD': 'iShares iBoxx Investment Grade',
                'HYG': 'iShares iBoxx High Yield Corporate',
            },
            '🛡️ Quỹ Cân bằng': {
                'AOR': 'iShares Core Growth Allocation (60/40)',
                'AOK': 'iShares Core Conservative Allocation (30/70)',
                'AOM': 'iShares Core Moderate Allocation (40/60)',
            },
            '💰 Quỹ Vàng & Hàng hóa': {
                'GLD': 'SPDR Gold Shares',
                'IAU': 'iShares Gold Trust',
                'DBC': 'Invesco DB Commodity Index',
            }
        }
        
        self.risk_profiles = {
            'Bảo thủ': {
                'description': 'Ưu tiên bảo toàn vốn, chấp nhận lợi nhuận thấp',
                'stocks': 20, 'bonds': 70, 'others': 10,
                'max_volatility': 0.10
            },
            'Trung bình': {
                'description': 'Cân bằng giữa rủi ro và lợi nhuận',
                'stocks': 50, 'bonds': 40, 'others': 10,
                'max_volatility': 0.15
            },
            'Tích cực': {
                'description': 'Chấp nhận rủi ro cao để đạt lợi nhuận cao',
                'stocks': 70, 'bonds': 20, 'others': 10,
                'max_volatility': 0.25
            },
            'Rất tích cực': {
                'description': 'Tập trung vào tăng trưởng, rủi ro rất cao',
                'stocks': 90, 'bonds': 5, 'others': 5,
                'max_volatility': 0.35
            }
        }
        
        self.create_widgets()
        
    def get_current_quarter(self):
        """Xác định quý hiện tại"""
        today = datetime.now()
        quarter = (today.month - 1) // 3 + 1
        return f"Q{quarter}/{today.year}"
    
    def get_quarter_dates(self, year, quarter):
        """Lấy ngày bắt đầu và kết thúc của quý"""
        start_month = (quarter - 1) * 3 + 1
        start_date = datetime(year, start_month, 1)
        
        if quarter == 4:
            end_date = datetime(year, 12, 31)
        else:
            end_month = start_month + 3
            end_date = datetime(year, end_month, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    def create_widgets(self):
        """Tạo giao diện GUI"""
        
        # Header
        self.header = widgets.HTML(
            value="""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
                <h1 style='color: white; text-align: center; margin: 0;'>
                    💼 PHÂN BỔ ĐẦU TƯ QUỸ THEO QUÝ
                </h1>
                <p style='color: white; text-align: center; font-size: 16px; margin-top: 10px;'>
                    Dành cho nhà đầu tư mới bắt đầu | PyPortfolioOpt
                </p>
            </div>
            """
        )
        
        # Tabs
        self.tabs = widgets.Tab()
        
        tab1 = self.create_input_tab()
        tab2 = self.create_analysis_tab()
        tab3 = self.create_quarterly_plan_tab()
        tab4 = self.create_education_tab()
        
        self.tabs.children = [tab1, tab2, tab3, tab4]
        self.tabs.set_title(0, '🎯 Thiết Lập Danh Mục')
        self.tabs.set_title(1, '📊 Phân Tích Chi Tiết')
        self.tabs.set_title(2, '📅 Kế Hoạch Theo Quý')
        self.tabs.set_title(3, '📚 Kiến Thức Đầu Tư')
        
    def create_input_tab(self):
        """Tab nhập liệu"""
        
        # Hồ sơ rủi ro
        self.risk_profile = widgets.Dropdown(
            options=list(self.risk_profiles.keys()),
            value='Trung bình',
            description='Hồ sơ rủi ro:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='60%')
        )
        
        risk_info = widgets.HTML()
        
        def update_risk_info(change):
            profile = self.risk_profiles[change['new']]
            risk_info.value = f"""
            <div style='background: #f0f8ff; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                <b>📋 Mô tả:</b> {profile['description']}<br>
                <b>📊 Phân bổ đề xuất:</b> Cổ phiếu {profile['stocks']}% | 
                Trái phiếu {profile['bonds']}% | Khác {profile['others']}%<br>
                <b>⚠️ Độ biến động tối đa:</b> {profile['max_volatility']*100:.0f}%
            </div>
            """
        
        self.risk_profile.observe(update_risk_info, 'value')
        update_risk_info({'new': 'Trung bình'})
        
        # Chọn loại quỹ
        self.fund_category = widgets.Dropdown(
            options=list(self.sample_funds.keys()),
            description='Loại quỹ:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='60%')
        )
        
        # Danh sách mã quỹ
        self.funds_input = widgets.Textarea(
            value='SPY, BND, GLD',
            placeholder='Nhập mã quỹ, cách nhau bởi dấu phẩy (VD: SPY, BND, GLD)',
            description='Mã quỹ:',
            layout=widgets.Layout(width='80%', height='120px'),
            style={'description_width': '120px'}
        )
        
        # Nút gợi ý
        suggest_btn = widgets.Button(
            description='💡 Gợi ý quỹ',
            button_style='info',
            layout=widgets.Layout(width='150px')
        )
        
        def suggest_funds(b):
            category = self.fund_category.value
            funds = list(self.sample_funds[category].keys())
            self.funds_input.value = ', '.join(funds[:5])
        
        suggest_btn.on_click(suggest_funds)
        
        # Hiển thị thông tin quỹ
        fund_info_btn = widgets.Button(
            description='ℹ️ Xem thông tin',
            button_style='',
            layout=widgets.Layout(width='150px')
        )
        
        fund_info_output = widgets.Output()
        
        def show_fund_info(b):
            with fund_info_output:
                clear_output()
                category = self.fund_category.value
                print(f"\n📖 Danh sách quỹ trong '{category}':\n")
                print("-" * 70)
                for code, name in self.sample_funds[category].items():
                    print(f"• {code:<15} : {name}")
                print("-" * 70)
        
        fund_info_btn.on_click(show_fund_info)
        
        # Khoảng thời gian
        self.years_back = widgets.IntSlider(
            value=3,
            min=1,
            max=10,
            step=1,
            description='Số năm dữ liệu:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='60%')
        )
        
        # Vốn đầu tư
        self.total_capital = widgets.FloatText(
            value=100000000,
            description='Tổng vốn (VNĐ):',
            step=5000000,
            style={'description_width': '120px'},
            layout=widgets.Layout(width='60%')
        )
        
        self.quarterly_invest = widgets.FloatText(
            value=10000000,
            description='Vốn mỗi quý (VNĐ):',
            step=1000000,
            style={'description_width': '120px'},
            layout=widgets.Layout(width='60%')
        )
        
        # Phương pháp tối ưu
        self.optimization_method = widgets.RadioButtons(
            options=[
                ('Sharpe Ratio tối đa (Tối ưu lợi nhuận/rủi ro)', 'max_sharpe'),
                ('Rủi ro tối thiểu (Ổn định nhất)', 'min_volatility'),
                ('Efficient Risk (Cân bằng, phù hợp người mới)', 'efficient_risk')
            ],
            value='efficient_risk',
            description='',
            layout=widgets.Layout(width='100%')
        )
        
        # Nút phân tích
        self.analyze_btn = widgets.Button(
            description='🚀 Phân Tích Ngay',
            button_style='success',
            layout=widgets.Layout(width='250px', height='50px'),
            style={'font_weight': 'bold', 'font_size': '14px'}
        )
        self.analyze_btn.on_click(self.run_analysis)
        
        # Output
        self.output = widgets.Output()
        
        # Layout
        input_box = widgets.VBox([
            widgets.HTML("<h2>🎯 THIẾT LẬP DANH MỤC ĐẦU TƯ</h2>"),
            widgets.HTML("<hr>"),
            
            widgets.HTML("<h3>👤 1. Xác định hồ sơ rủi ro của bạn</h3>"),
            self.risk_profile,
            risk_info,
            
            widgets.HTML("<br><h3>📂 2. Chọn quỹ đầu tư</h3>"),
            self.fund_category,
            widgets.HBox([suggest_btn, fund_info_btn]),
            fund_info_output,
            self.funds_input,
            
            widgets.HTML("<br><h3>⏰ 3. Thời gian phân tích</h3>"),
            self.years_back,
            widgets.HTML("<p style='color: #666; margin-left: 10px;'>"
                        "💡 Gợi ý: 3-5 năm để có đủ dữ liệu qua nhiều chu kỳ thị trường</p>"),
            
            widgets.HTML("<br><h3>💰 4. Vốn đầu tư</h3>"),
            self.total_capital,
            self.quarterly_invest,
            widgets.HTML("<p style='color: #666; margin-left: 10px;'>"
                        "💡 Gợi ý: Vốn mỗi quý = 1/4 tổng vốn hàng năm hoặc theo khả năng tiết kiệm</p>"),
            
            widgets.HTML("<br><h3>⚙️ 5. Phương pháp tối ưu hóa</h3>"),
            self.optimization_method,
            
            widgets.HTML("<br>"),
            self.analyze_btn,
            self.output
        ])
        
        return input_box
    
    def create_analysis_tab(self):
        """Tab phân tích chi tiết"""
        self.analysis_output = widgets.Output()
        return self.analysis_output
    
    def create_quarterly_plan_tab(self):
        """Tab kế hoạch theo quý"""
        self.quarterly_output = widgets.Output()
        return self.quarterly_output
    
    def create_education_tab(self):
        """Tab kiến thức"""
        education_html = """
        <div style='padding: 20px; line-height: 1.8;'>
            <h2>📚 KIẾN THỨC CƠ BẢN VỀ ĐẦU TƯ QUỸ</h2>
            
            <div style='background: #e3f2fd; padding: 15px; border-radius: 10px; margin: 15px 0;'>
                <h3>🎯 1. Quỹ đầu tư là gì?</h3>
                <p><b>Quỹ đầu tư</b> là một công cụ tài chính gộp vốn từ nhiều nhà đầu tư để đầu tư vào 
                danh mục đa dạng các tài sản (cổ phiếu, trái phiếu, hàng hóa...) do chuyên gia quản lý.</p>
                
                <p><b>Ưu điểm:</b></p>
                <ul>
                    <li>✅ Đa dạng hóa tự động (giảm rủi ro)</li>
                    <li>✅ Quản lý chuyên nghiệp</li>
                    <li>✅ Vốn đầu tư nhỏ vẫn có thể tham gia</li>
                    <li>✅ Thanh khoản cao (ETF)</li>
                </ul>
            </div>
            
            <div style='background: #fff3e0; padding: 15px; border-radius: 10px; margin: 15px 0;'>
                <h3>📊 2. Các loại quỹ phổ biến</h3>
                
                <p><b>🏢 Quỹ Cổ phiếu (Equity Funds)</b></p>
                <ul>
                    <li>Đầu tư chủ yếu vào cổ phiếu</li>
                    <li>Tiềm năng lợi nhuận cao, rủi ro cao</li>
                    <li>VD: SPY (S&P 500), VNM ETF</li>
                </ul>
                
                <p><b>📜 Quỹ Trái phiếu (Bond Funds)</b></p>
                <ul>
                    <li>Đầu tư vào trái phiếu chính phủ, doanh nghiệp</li>
                    <li>Ổn định, rủi ro thấp, lợi nhuận vừa phải</li>
                    <li>VD: BND, AGG</li>
                </ul>
                
                <p><b>📈 ETF (Exchange Traded Fund)</b></p>
                <ul>
                    <li>Giao dịch như cổ phiếu trên sàn</li>
                    <li>Chi phí thấp, minh bạch</li>
                    <li>Theo dõi chỉ số thị trường</li>
                </ul>
                
                <p><b>⚖️ Quỹ Cân bằng (Balanced Funds)</b></p>
                <ul>
                    <li>Kết hợp cổ phiếu và trái phiếu</li>
                    <li>Cân bằng giữa tăng trưởng và ổn định</li>
                    <li>VD: AOR (60% cổ phiếu, 40% trái phiếu)</li>
                </ul>
            </div>
            
            <div style='background: #f3e5f5; padding: 15px; border-radius: 10px; margin: 15px 0;'>
                <h3>💡 3. Chiến lược đầu tư theo quý</h3>
                
                <p><b>Tại sao nên đầu tư định kỳ theo quý?</b></p>
                <ul>
                    <li>🎯 <b>Dollar Cost Averaging (DCA):</b> Mua đều đặn, giảm rủi ro thời điểm</li>
                    <li>📊 <b>Rebalancing:</b> Điều chỉnh danh mục về tỷ lệ mục tiêu</li>
                    <li>💰 <b>Dễ quản lý:</b> Phù hợp với thu nhập định kỳ</li>
                    <li>🧘 <b>Kỷ luật:</b> Tránh quyết định cảm tính</li>
                </ul>
                
                <p><b>Quy trình mỗi quý:</b></p>
                <ol>
                    <li><b>Đánh giá hiệu suất:</b> Xem lại lợi nhuận quý trước</li>
                    <li><b>Phân tích thị trường:</b> Cập nhật dữ liệu mới</li>
                    <li><b>Tối ưu danh mục:</b> Chạy PyPortfolioOpt</li>
                    <li><b>Rebalancing:</b> Điều chỉnh theo tỷ trọng mới</li>
                    <li><b>Đầu tư thêm:</b> Bổ sung vốn theo kế hoạch</li>
                </ol>
            </div>
            
            <div style='background: #e8f5e9; padding: 15px; border-radius: 10px; margin: 15px 0;'>
                <h3>📈 4. Hiểu các chỉ số quan trọng</h3>
                
                <p><b>Expected Return (Lợi nhuận kỳ vọng):</b></p>
                <ul>
                    <li>Lợi nhuận trung bình dự kiến hàng năm</li>
                    <li>Tính từ dữ liệu lịch sử</li>
                    <li>⚠️ Không đảm bảo hiệu suất tương lai</li>
                </ul>
                
                <p><b>Volatility (Độ biến động):</b></p>
                <ul>
                    <li>Đo lường mức độ dao động giá</li>
                    <li>Volatility cao = Rủi ro cao</li>
                    <li>VD: 15% volatility nghĩa là giá có thể dao động ±15%/năm</li>
                </ul>
                
                <p><b>Sharpe Ratio (Tỷ lệ Sharpe):</b></p>
                <ul>
                    <li>Công thức: (Lợi nhuận - Lãi suất phi rủi ro) / Volatility</li>
                    <li>Đo lường hiệu quả đầu tư sau khi điều chỉnh rủi ro</li>
                    <li>Sharpe > 1: Tốt | > 2: Rất tốt | > 3: Xuất sắc</li>
                </ul>
                
                <p><b>Correlation (Tương quan):</b></p>
                <ul>
                    <li>Đo lường mối quan hệ giữa các tài sản</li>
                    <li>-1 đến +1: -1 = ngược chiều, 0 = không liên quan, +1 = cùng chiều</li>
                    <li>Đa dạng hóa tốt: chọn tài sản có correlation thấp</li>
                </ul>
            </div>
            
            <div style='background: #ffebee; padding: 15px; border-radius: 10px; margin: 15px 0;'>
                <h3>⚠️ 5. Rủi ro và lưu ý quan trọng</h3>
                
                <p><b>Rủi ro thị trường:</b></p>
                <ul>
                    <li>Giá quỹ có thể giảm khi thị trường sụt giảm</li>
                    <li>Không có bảo đảm vốn gốc</li>
                </ul>
                
                <p><b>Chi phí:</b></p>
                <ul>
                    <li>Phí quản lý (Expense Ratio): 0.03% - 2%/năm</li>
                    <li>Phí giao dịch, thuế</li>
                    <li>ETF thường có phí thấp hơn quỹ mở</li>
                </ul>
                
                <p><b>⚠️ LƯU Ý QUAN TRỌNG:</b></p>
                <ul>
                    <li>🚫 Không bỏ hết trứng vào một giỏ - Đa dạng hóa!</li>
                    <li>📚 Đầu tư vào những gì bạn hiểu</li>
                    <li>⏰ Đầu tư dài hạn (tối thiểu 3-5 năm)</li>
                    <li>💰 Chỉ đầu tư số tiền bạn có thể chấp nhận mất</li>
                    <li>📊 Xem xét lại danh mục định kỳ</li>
                    <li>🧘 Không hoảng loạn khi thị trường biến động</li>
                </ul>
            </div>
            
            <div style='background: #e1f5fe; padding: 15px; border-radius: 10px; margin: 15px 0;'>
                <h3>🎓 6. Lộ trình cho người mới bắt đầu</h3>
                
                <p><b>Giai đoạn 1: Học hỏi (1-3 tháng)</b></p>
                <ul>
                    <li>Đọc sách, bài viết về đầu tư quỹ</li>
                    <li>Hiểu các khái niệm cơ bản</li>
                    <li>Thử nghiệm với số tiền nhỏ</li>
                </ul>
                
                <p><b>Giai đoạn 2: Thực hành (3-6 tháng)</b></p>
                <ul>
                    <li>Bắt đầu với danh mục đơn giản (2-3 quỹ)</li>
                    <li>Đầu tư định kỳ hàng tháng/quý</li>
                    <li>Theo dõi và học từ kết quả</li>
                </ul>
                
                <p><b>Giai đoạn 3: Mở rộng (6-12 tháng)</b></p>
                <ul>
                    <li>Tăng số lượng quỹ (5-8 quỹ)</li>
                    <li>Đa dạng hóa theo ngành, khu vực</li>
                    <li>Áp dụng rebalancing định kỳ</li>
                </ul>
                
                <p><b>Giai đoạn 4: Tinh chỉnh (1 năm+)</b></p>
                <ul>
                    <li>Tối ưu hóa dựa trên kinh nghiệm</li>
                    <li>Điều chỉnh theo mục tiêu tài chính</li>
                    <li>Có thể thêm các chiến lược nâng cao</li>
                </ul>
            </div>
            
            <div style='background: #fff9c4; padding: 15px; border-radius: 10px; margin: 15px 0;'>
                <h3>💼 7. Ví dụ danh mục mẫu</h3>
                
                <p><b>Danh mục Bảo thủ (20-30 tuổi, ít kinh nghiệm):</b></p>
                <ul>
                    <li>40% BND (Trái phiếu tổng hợp)</li>
                    <li>30% SPY (Cổ phiếu Mỹ)</li>
                    <li>20% VEA (Cổ phiếu quốc tế)</li>
                    <li>10% GLD (Vàng)</li>
                </ul>
                
                <p><b>Danh mục Cân bằng (30-50 tuổi, có kinh nghiệm):</b></p>
                <ul>
                    <li>50% SPY (Cổ phiếu Mỹ)</li>
                    <li>25% BND (Trái phiếu)</li>
                    <li>15% EEM (Thị trường mới nổi)</li>
                    <li>10% VNM ETF (Việt Nam)</li>
                </ul>
                
                <p><b>Danh mục Tích cực (trẻ, chấp nhận rủi ro cao):</b></p>
                <ul>
                    <li>40% QQQ (Tech Mỹ)</li>
                    <li>30% SPY (S&P 500)</li>
                    <li>20% EEM (Thị trường mới nổi)</li>
                    <li>10% BND (Trái phiếu)</li>
                </ul>
            </div>
            
            <div style='background: #fce4ec; padding: 15px; border-radius: 10px; margin: 15px 0;'>
                <h3>📞 8. Nguồn học thêm</h3>
                <ul>
                    <li>📚 Sách: "The Intelligent Investor" - Benjamin Graham</li>
                    <li>📚 Sách: "A Random Walk Down Wall Street" - Burton Malkiel</li>
                    <li>🌐 Website: Investopedia, Morningstar</li>
                    <li>📊 Công cụ: Yahoo Finance, TradingView</li>
                    <li>🎓 Khóa học: Coursera, edX về đầu tư</li>
                </ul>
            </div>
            
            <p style='text-align: center; margin-top: 30px; color: #666;'>
                <b>💡 Nhớ rằng: Đầu tư là một hành trình dài hạn, không phải cuộc đua ngắn hạn!</b>
            </p>
        </div>
        """
        return widgets.HTML(value=education_html)
    
    def run_analysis(self, b):
        """Chạy phân tích và tối ưu hóa"""
        with self.output:
            clear_output()
            print("🔄 Đang phân tích... Vui lòng đợi trong giây lát...")
        
        try:
            # Lấy danh sách quỹ
            funds = [f.strip().upper() for f in self.funds_input.value.split(',') if f.strip()]
            
            if len(funds) < 2:
                with self.output:
                    clear_output()
                    print("❌ Vui lòng nhập ít nhất 2 mã quỹ để đa dạng hóa!")
                return
            
            # Tải dữ liệu
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * self.years_back.value)
            
            with self.output:
                clear_output()
                print(f"📥 Đang tải dữ liệu {len(funds)} quỹ từ {start_date.strftime('%Y-%m-%d')}...")
            
            data = yf.download(funds, start=start_date, end=end_date, progress=False)['Adj Close']
            
            if isinstance(data, pd.Series):
                data = data.to_frame()
            
            # Xử lý dữ liệu
            if data.empty or len(data) < 60:
                with self.output:
                    clear_output()
                    print("❌ Không có đủ dữ liệu! Vui lòng:")
                    print("  • Kiểm tra mã quỹ có đúng không")
                    print("  • Thử tăng số năm dữ liệu")
                    print("  • Thử với các quỹ khác có lịch sử dài hơn")
                return
            
            data = data.dropna(axis=1, thresh=len(data)*0.7)
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            if len(data.columns) < 2:
                with self.output:
                    clear_output()
                    print("❌ Không đủ quỹ có dữ liệu hợp lệ!")
                return
            
            self.df = data
            
            # Tính toán
            with self.output:
                clear_output()
                print("📊 Đang tính toán tối ưu hóa danh mục...")
            
            mu = expected_returns.mean_historical_return(data)
            S = risk_models.sample_cov(data)
            
            # Áp dụng ràng buộc theo hồ sơ rủi ro
            profile = self.risk_profiles[self.risk_profile.value]
            
            ef = EfficientFrontier(mu, S)
            ef.add_constraint(lambda w: w <= 0.4)  # Giới hạn tối đa 40% cho 1 quỹ
            
            # Tối ưu hóa
            method = self.optimization_method.value
            if method == 'max_sharpe':
                weights = ef.max_sharpe()
            elif method == 'min_volatility':
                weights = ef.min_volatility()
            else:  # efficient_risk
                target_risk = profile['max_volatility']
                weights = ef.efficient_risk(target_risk)
            
            cleaned_weights = ef.clean_weights()
            performance = ef.portfolio_performance(verbose=False)
            
            # Lưu kết quả
            self.weights = cleaned_weights
            self.performance = performance
            
            # Hiển thị kết quả
            self.display_analysis()
            self.display_quarterly_plan()
            
            # Chuyển sang tab phân tích
            self.tabs.selected_index = 1
            
            with self.output:
                clear_output()
                print("✅ Phân tích hoàn tất! Vui lòng xem các tab 'Phân Tích Chi Tiết' và 'Kế Hoạch Theo Quý'")
        
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
                print("\n💡 Gợi ý khắc phục:")
                print("  • Kiểm tra kết nối internet")
                print("  • Đảm bảo mã quỹ đúng định dạng (VD: SPY, BND)")
                print("  • Thử giảm số năm dữ liệu xuống 2-3 năm")
                print("  • Thử với các quỹ phổ biến: SPY, BND, GLD")
    
    def display_analysis(self):
        """Hiển thị phân tích chi tiết"""
        with self.analysis_output:
            clear_output()
            
            # Header
            print("="*90)
            print(" "*30 + "📊 PHÂN TÍCH CHI TIẾT DANH MỤC")
            print("="*90)
            
            # Thông tin cơ bản
            print(f"\n📅 Kỳ phân tích: {self.df.index[0].strftime('%d/%m/%Y')} - {self.df.index[-1].strftime('%d/%m/%Y')}")
            print(f"📊 Số quỹ: {len([w for w in self.weights.values() if w > 0])}/{len(self.df.columns)}")
            print(f"👤 Hồ sơ rủi ro: {self.risk_profile.value}")
            print(f"💰 Tổng vốn: {self.total_capital.value:,.0f} VNĐ")
            
            # Hiệu suất danh mục
            print("\n" + "="*90)
            print(" "*25 + "🎯 HIỆU SUẤT DANH MỤC KỲ VỌNG")
            print("="*90)
            
            expected_return = self.performance[0] * 100
            volatility = self.performance[1] * 100
            sharpe = self.performance[2]
            
            print(f"\n{'Lợi nhuận hàng năm kỳ vọng:':<45} {expected_return:>10.2f}%")
            print(f"{'Độ biến động (rủi ro):':<45} {volatility:>10.2f}%")
            print(f"{'Sharpe Ratio:':<45} {sharpe:>10.2f}")
            
            # Đánh giá Sharpe Ratio
            if sharpe > 2:
                rating = "⭐⭐⭐ Xuất sắc"
            elif sharpe > 1:
                rating = "⭐⭐ Tốt"
            elif sharpe > 0.5:
                rating = "⭐ Chấp nhận được"
            else:
                rating = "⚠️ Cần cải thiện"
            print(f"{'Đánh giá:':<45} {rating}")
            
            # So sánh với hồ sơ rủi ro
            profile = self.risk_profiles[self.risk_profile.value]
            print(f"\n📋 So sánh với hồ sơ '{self.risk_profile.value}':")
            print(f"  • Rủi ro mục tiêu: {profile['max_volatility']*100:.1f}% | Rủi ro thực tế: {volatility:.1f}%")
            
            if volatility <= profile['max_volatility'] * 100:
                print("  ✅ Danh mục phù hợp với hồ sơ rủi ro của bạn")
            else:
                print("  ⚠️ Danh mục có rủi ro cao hơn hồ sơ, cân nhắc điều chỉnh")
            
            # Tỷ trọng quỹ
            print("\n" + "="*90)
            print(" "*30 + "💼 TỶ TRỌNG CÁC QUỸ")
            print("="*90)
            
            weights_df = pd.DataFrame.from_dict(self.weights, orient='index', columns=['Tỷ trọng'])
            weights_df = weights_df[weights_df['Tỷ trọng'] > 0].sort_values('Tỷ trọng', ascending=False)
            weights_df['Tỷ trọng %'] = (weights_df['Tỷ trọng'] * 100).round(2)
            
            print(f"\n{'Mã quỹ':<15} {'Tỷ trọng':<12} {'Biểu đồ'}")
            print("-"*90)
            
            for idx, row in weights_df.iterrows():
                bar = "█" * int(row['Tỷ trọng %'] / 2)
                print(f"{idx:<15} {row['Tỷ trọng %']:>6.2f}%     {bar}")
            
            # Phân bổ vốn cụ thể
            print("\n" + "="*90)
            print(" "*25 + "💰 PHÂN BỔ VỐN CHI TIẾT")
            print("="*90)
            
            latest_prices = get_latest_prices(self.df)
            da = DiscreteAllocation(self.weights, latest_prices, 
                                   total_portfolio_value=self.total_capital.value)
            allocation, leftover = da.greedy_portfolio()
            
            print(f"\n{'Mã quỹ':<15} {'Số lượng':<12} {'Giá/đơn vị':<18} {'Tổng tiền (VNĐ)':<20}")
            print("-"*90)
            
            total_invested = 0
            for ticker in weights_df.index:
                if ticker in allocation:
                    shares = allocation[ticker]
                    price = latest_prices[ticker]
                    total = shares * price
                    total_invested += total
                    print(f"{ticker:<15} {shares:<12} ${price:>12,.2f}     {total:>19,.0f}")
            
            print("-"*90)
            print(f"{'Tổng đã đầu tư:':<45} {total_invested:>19,.0f} VNĐ")
            print(f"{'Số dư còn lại (tiền mặt):':<45} {leftover:>19,.0f} VNĐ")
            print(f"{'Tỷ lệ tiền mặt:':<45} {(leftover/self.total_capital.value)*100:>18.2f}%")
            
            # Thống kê lịch sử
            print("\n" + "="*90)
            print(" "*25 + "📈 THỐNG KÊ LỊCH SỬ CÁC QUỸ")
            print("="*90)
            
            returns = self.df.pct_change()
            
            print(f"\n{'Mã quỹ':<15} {'Lợi nhuận TB':<18} {'Độ biến động':<18} {'Sharpe':<12}")
            print("-"*90)
            
            for ticker in weights_df.index:
                avg_return = returns[ticker].mean() * 252 * 100  # Annualized
                std = returns[ticker].std() * np.sqrt(252) * 100
                sharpe_individual = avg_return / std if std > 0 else 0
                
                print(f"{ticker:<15} {avg_return:>12.2f}%     {std:>12.2f}%     {sharpe_individual:>8.2f}")
            
            # Vẽ biểu đồ
            self.plot_analysis()
    
    def plot_analysis(self):
        """Vẽ các biểu đồ phân tích"""
        
        weights_df = pd.DataFrame.from_dict(self.weights, orient='index', columns=['Tỷ trọng'])
        weights_df = weights_df[weights_df['Tỷ trọng'] > 0].sort_values('Tỷ trọng', ascending=False)
        weights_df['Tỷ trọng %'] = (weights_df['Tỷ trọng'] * 100).round(2)
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Pie chart - Tỷ trọng
        ax1 = fig.add_subplot(gs[0, :2])
        colors = plt.cm.Set3(range(len(weights_df)))
        wedges, texts, autotexts = ax1.pie(weights_df['Tỷ trọng %'], 
                                            labels=weights_df.index,
                                            autopct='%1.1f%%',
                                            colors=colors, 
                                            startangle=90,
                                            textprops={'fontsize': 10})
        ax1.set_title('💼 Phân Bổ Tỷ Trọng Danh Mục', fontsize=14, fontweight='bold', pad=20)
        
        # 2. Bar chart - Tỷ trọng
        ax2 = fig.add_subplot(gs[0, 2])
        weights_df.plot(kind='barh', ax=ax2, color=colors, legend=False, y='Tỷ trọng %')
        ax2.set_xlabel('Tỷ trọng (%)', fontsize=10)
        ax2.set_title('📊 Phân Bổ Chi Tiết', fontsize=12, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # 3. Line chart - Giá lịch sử chuẩn hóa
        ax3 = fig.add_subplot(gs[1, :])
        normalized_prices = self.df / self.df.iloc[0] * 100
        
        for col in normalized_prices.columns:
            if col in self.weights and self.weights[col] > 0:
                ax3.plot(normalized_prices.index, normalized_prices[col], 
                        label=col, linewidth=2, alpha=0.8)
        
        ax3.set_xlabel('Thời gian', fontsize=10)
        ax3.set_ylabel('Giá chuẩn hóa (Base = 100)', fontsize=10)
        ax3.set_title('📈 Biến Động Giá Lịch Sử (Chuẩn Hóa)', fontsize=14, fontweight='bold', pad=15)
        ax3.legend(loc='best', fontsize=9, framealpha=0.9)
        ax3.grid(alpha=0.3)
        ax3.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='Baseline')
        
        # 4. Returns distribution
        ax4 = fig.add_subplot(gs[2, 0])
        returns = self.df.pct_change().dropna()
        
        for col in weights_df.index[:3]:  # Top 3 funds
            if col in returns.columns:
                ax4.hist(returns[col] * 100, bins=50, alpha=0.5, label=col)
        
        ax4.set_xlabel('Lợi nhuận hàng ngày (%)', fontsize=9)
        ax4.set_ylabel('Tần suất', fontsize=9)
        ax4.set_title('📊 Phân Phối Lợi Nhuận', fontsize=12, fontweight='bold')
        ax4.legend(fontsize=8)
        ax4.grid(alpha=0.3)
        
        # 5. Correlation heatmap
        ax5 = fig.add_subplot(gs[2, 1:])
        selected_cols = [col for col in self.df.columns if col in self.weights and self.weights[col] > 0]
        corr = self.df[selected_cols].corr()
        
        im = ax5.imshow(corr, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
        ax5.set_xticks(range(len(corr)))
        ax5.set_yticks(range(len(corr)))
        ax5.set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=9)
        ax5.set_yticklabels(corr.columns, fontsize=9)
        ax5.set_title('🔗 Ma Trận Tương Quan Giữa Các Quỹ', fontsize=12, fontweight='bold', pad=10)
        
        for i in range(len(corr)):
            for j in range(len(corr)):
                color = 'white' if abs(corr.iloc[i, j]) > 0.5 else 'black'
                ax5.text(j, i, f'{corr.iloc[i, j]:.2f}',
                        ha="center", va="center", color=color, fontsize=8)
        
        plt.colorbar(im, ax=ax5, label='Correlation')
        
        plt.suptitle('📊 PHÂN TÍCH DANH MỤC ĐẦU TƯ', 
                    fontsize=16, fontweight='bold', y=0.995)
        
        plt.show()
        
        print("\n💡 Ghi chú về biểu đồ:")
        print("  • Tương quan gần +1: Hai quỹ biến động cùng chiều (kém đa dạng)")
        print("  • Tương quan gần 0: Độc lập nhau (tốt cho đa dạng hóa)")
        print("  • Tương quan gần -1: Biến động ngược chiều (rất tốt cho giảm rủi ro)")
    
    def display_quarterly_plan(self):
        """Hiển thị kế hoạch đầu tư theo quý"""
        with self.quarterly_output:
            clear_output()
            
            print("="*90)
            print(" "*25 + "📅 KẾ HOẠCH ĐẦU TƯ THEO QUÝ")
            print("="*90)
            
            # Thông tin tổng quan
            print(f"\n💰 Vốn đầu tư mỗi quý: {self.quarterly_invest.value:,.0f} VNĐ")
            print(f"📊 Số quỹ trong danh mục: {len([w for w in self.weights.values() if w > 0])}")
            
            # Tạo kế hoạch 4 quý tiếp theo
            today = datetime.now()
            current_quarter = (today.month - 1) // 3 + 1
            current_year = today.year
            
            print("\n" + "="*90)
            print(" "*30 + "📆 KẾ HOẠCH 4 QUÝ TIẾP THEO")
            print("="*90)
            
            weights_df = pd.DataFrame.from_dict(self.weights, orient='index', columns=['Tỷ trọng'])
            weights_df = weights_df[weights_df['Tỷ trọng'] > 0].sort_values('Tỷ trọng', ascending=False)
            
            latest_prices = get_latest_prices(self.df)
            
            for i in range(4):
                quarter = current_quarter + i
                year = current_year
                
                if quarter > 4:
                    quarter = quarter - 4
                    year += 1
                
                print(f"\n{'━'*90}")
                print(f"📌 QUÝ {quarter}/{year}")
                print(f"{'━'*90}")
                
                start, end = self.get_quarter_dates(year, quarter)
                print(f"Thời gian: {start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}")
                
                # Tính phân bổ cho quý này
                da = DiscreteAllocation(self.weights, latest_prices,
                                       total_portfolio_value=self.quarterly_invest.value)
                allocation, leftover = da.greedy_portfolio()
                
                print(f"\n{'Mã quỹ':<15} {'Số lượng mua':<15} {'Giá dự kiến':<18} {'Số tiền (VNĐ)':<20}")
                print("-"*90)
                
                total = 0
                for ticker in weights_df.index:
                    if ticker in allocation and allocation[ticker] > 0:
                        shares = allocation[ticker]
                        price = latest_prices[ticker]
                        amount = shares * price
                        total += amount
                        print(f"{ticker:<15} {shares:<15} ${price:>12,.2f}     {amount:>19,.0f}")
                
                print("-"*90)
                print(f"{'Tổng đầu tư:':<48} {total:>19,.0f} VNĐ")
                print(f"{'Tiền mặt dự trữ:':<48} {leftover:>19,.0f} VNĐ")
                
                # Gợi ý hành động
                print(f"\n✅ Hành động cần làm trong quý {quarter}/{year}:")
                print(f"   1. Chuẩn bị: {self.quarterly_invest.value:,.0f} VNĐ")
                print(f"   2. Ngày đầu tư đề xuất: {start.strftime('%d/%m/%Y')} (đầu quý)")
                print(f"   3. Mua các quỹ theo bảng phân bổ trên")
                print(f"   4. Giữ lại tiền mặt: {leftover:,.0f} VNĐ làm dự phòng")
                print(f"   5. Xem xét rebalancing nếu danh mục lệch >5%")
            
            # Tổng kết năm
            print("\n" + "="*90)
            print(" "*30 + "📊 TỔNG KẾT NĂM")
            print("="*90)
            
            total_yearly = self.quarterly_invest.value * 4
            expected_return_amount = total_yearly * self.performance[0]
            
            print(f"\nTổng vốn đầu tư cả năm: {total_yearly:,.0f} VNĐ")
            print(f"Lợi nhuận kỳ vọng: {expected_return_amount:,.0f} VNĐ ({self.performance[0]*100:.2f}%)")
            print(f"Tổng tài sản dự kiến cuối năm: {total_yearly + expected_return_amount:,.0f} VNĐ")
            
            # Lời khuyên
            print("\n" + "="*90)
            print(" "*35 + "💡 LỜI KHUYÊN")
            print("="*90)
            
            advice = [
                "🎯 Tuân thủ kỷ luật: Đầu tư đúng số tiền, đúng thời điểm mỗi quý",
                "📊 Rebalancing: Điều chỉnh danh mục về tỷ trọng mục tiêu mỗi 6 tháng",
                "📈 Theo dõi: Xem xét hiệu suất cuối mỗi quý, không cần kiểm tra hàng ngày",
                "🧘 Kiên nhẫn: Đầu tư dài hạn, không hoảng loạn khi thị trường giảm",
                "📚 Học hỏi: Đọc báo cáo quỹ, cập nhật kiến thức thị trường",
                "💰 Dự phòng: Luôn giữ 3-6 tháng chi phí sinh hoạt bằng tiền mặt",
                "🔄 Linh hoạt: Điều chỉnh kế hoạch nếu hoàn cảnh thay đổi",
                "⚠️ Cảnh giác: Không vay nợ để đầu tư, chỉ dùng tiền nhàn rỗi"
            ]
            
            for tip in advice:
                print(f"\n{tip}")
            
            # Checklist theo quý
            print("\n" + "="*90)
            print(" "*30 + "✅ CHECKLIST TỪNG QUÝ")
            print("="*90)
            
            checklist = """
            📋 Đầu quý (Tuần đầu tiên):
               □ Chuẩn bị vốn đầu tư
               □ Xem lại tỷ trọng danh mục hiện tại
               □ Kiểm tra giá quỹ
               □ Thực hiện giao dịch mua
            
            📋 Giữa quý (Tuần thứ 6-7):
               □ Theo dõi hiệu suất danh mục
               □ Đọc tin tức thị trường
               □ Ghi chép nhật ký đầu tư
            
            📋 Cuối quý (Tuần cuối):
               □ Tính toán lợi nhuận/lỗ
               □ Đánh giá hiệu suất từng quỹ
               □ Quyết định rebalancing (nếu cần)
               □ Lập kế hoạch cho quý tiếp theo
               □ Cập nhật bảng theo dõi Excel/Google Sheets
            """
            
            print(checklist)
            
            # Template theo dõi
            print("\n" + "="*90)
            print(" "*25 + "📝 TEMPLATE THEO DÕI (Tự ghi chép)")
            print("="*90)
            
            template = f"""
            Quý: ___ / Năm: _____
            Ngày đầu tư: ___/___/____
            
            {'Mã quỹ':<15} | {'Số lượng':<10} | {'Giá mua':<12} | {'Tổng tiền':<15} | {'Ghi chú'}
            {'-'*85}
            
            
            
            Tổng đầu tư quý này: _______________ VNĐ
            Hiệu suất quý trước: ______%
            Tổng tài sản hiện tại: _______________ VNĐ
            
            Đánh giá:
            - Điểm tốt: ___________________________________________________
            - Cần cải thiện: _______________________________________________
            - Bài học: _____________________________________________________
            """
            
            print(template)
    
    def display(self):
        """Hiển thị ứng dụng"""
        display(self.header)
        display(self.tabs)

# Khởi tạo ứng dụng
print("="*90)
print("🚀 KHỞI ĐỘNG ỨNG DỤNG PHÂN BỔ ĐẦU TƯ QUỸ THEO QUÝ")
print("="*90)
print("\n📦 Yêu cầu thư viện: pandas, numpy, yfinance, matplotlib, seaborn, pypfopt, ipywidgets")
print("💡 Nếu chưa cài đặt, chạy: !pip install yfinance pypfopt ipywidgets")
print("\n" + "="*90)
print("✨ Ứng dụng đã sẵn sàng! Hãy bắt đầu với tab 'Thiết Lập Danh Mục'")
print("="*90 + "\n")

app = QuarterlyFundPortfolio()
app.display()
