import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, date, timedelta
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
warnings.filterwarnings('ignore')

# Thiết lập style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (12, 8)

class InvestmentPortfolioAnalyzer:
    def __init__(self):
        # Khởi tạo dữ liệu
        self.investment_data = []
        self.current_prices = {}
        self.target_allocation = {}
        self.exchange_rate = 18.0  # KRW to VND
        
        # Mapping từ savings type sang investment category - CẬP NHẬT CHI TIẾT HỆ THỐNG QUỸ
        self.investment_mapping = {
            'Đầu tư chứng khoán': 'Cổ phiếu',
            'Quỹ đầu tư': 'Quỹ cân bằng',  # Quỹ đầu tư cân bằng
            'Quỹ đầu tư cân bằng': 'Quỹ cân bằng',
            'Quỹ trái phiếu': 'Quỹ trái phiếu',  # Quỹ đầu tư trái phiếu
            'Quỹ đầu tư trái phiếu': 'Quỹ trái phiếu',
            'Quỹ cổ phiếu': 'Quỹ cổ phiếu',  # Quỹ đầu tư cổ phiếu
            'Quỹ đầu tư cổ phiếu': 'Quỹ cổ phiếu',
            'Tiết kiệm ngân hàng': 'Tiền gửi',
            'Vàng': 'Vàng',
            'Bất động sản': 'Bất động sản',
            'Crypto': 'Crypto',
            'Khác': 'Khác'
        }
        
        # CẬP NHẬT RỦI RO VÀ LỢI NHUẬN THEO LOẠI QUỸ
        self.asset_risk_levels = {
            'Tiền gửi': {'risk': 1, 'expected_return': 6.0, 'volatility': 0.5},
            'Quỹ trái phiếu': {'risk': 2, 'expected_return': 8.0, 'volatility': 3.0},  # Thấp nhất trong các quỹ
            'Vàng': {'risk': 2, 'expected_return': 7.5, 'volatility': 12.0},
            'Quỹ cân bằng': {'risk': 3, 'expected_return': 10.0, 'volatility': 8.0},  # Cân bằng rủi ro/lợi nhuận
            'Bất động sản': {'risk': 3, 'expected_return': 12.0, 'volatility': 15.0},
            'Quỹ cổ phiếu': {'risk': 4, 'expected_return': 15.0, 'volatility': 18.0},  # Cao nhất trong các quỹ
            'Cổ phiếu': {'risk': 4, 'expected_return': 16.0, 'volatility': 20.0},
            'Crypto': {'risk': 5, 'expected_return': 25.0, 'volatility': 35.0},
            'Khác': {'risk': 3, 'expected_return': 10.0, 'volatility': 10.0}
        }
        
        # File paths
        self.data_files = {
            'savings': 'finance_data_savings.csv',
            'investment_prices': 'investment_current_prices.csv',
            'target_allocation': 'target_allocation.csv',
            'settings': 'investment_settings.csv'
        }
        
        # Tạo widgets
        self.create_widgets()
        
        # Load data
        self.load_data()
        
        # Create layout
        self.create_layout()


def create_widgets(self):
        # Header
        self.title = widgets.HTML(
            value="<h2 style='text-align: center; color: #2E86AB;'>📈 PHÂN TÍCH DANH MỤC ĐẦU TƯ - PHIÊN BẢN QUỸ NÂNG CAO</h2>"
        )
        
        # Settings Section
        self.settings_header = widgets.HTML(
            value="<h3 style='color: #17A2B8;'>⚙️ CÀI ĐẶT</h3>"
        )
        self.exchange_rate_input = widgets.FloatText(
            value=18.0,
            description="Tỷ giá (1 KRW =):",
            style={'description_width': 'initial'},
            layout={'width': '200px'}
        )
        self.exchange_rate_unit = widgets.HTML(value="<span style='margin-left: 5px;'>VND</span>")
        self.update_exchange_btn = widgets.Button(
            description="Cập nhật Tỷ giá",
            button_style='info',
            icon='refresh'
        )
        
        self.currency_display = widgets.Dropdown(
            options=[('VND', 'VND'), ('KRW', 'KRW')],
            value='VND',
            description="Hiển thị:",
            style={'description_width': 'initial'}
        )
        
        # Data Import Section
        self.import_header = widgets.HTML(
            value="<h3 style='color: #28A745;'>📂 IMPORT DỮ LIỆU</h3>"
        )
        self.import_file_path = widgets.Text(
            value='finance_data_savings.csv',
            placeholder='Nhập đường dẫn file CSV...',
            description="File CSV:",
            style={'description_width': 'initial'},
            layout={'width': '400px'}
        )
        self.import_data_btn = widgets.Button(
            description="Import Dữ liệu Đầu tư",
            button_style='success',
            icon='upload'
        )
        
        # Current Price Management
        self.price_header = widgets.HTML(
            value="<h3 style='color: #FF6B35;'>💰 CẬP NHẬT GIÁ HIỆN TẠI</h3>"
        )
        self.asset_dropdown = widgets.Dropdown(
            options=[('-- Chọn tài sản --', '')],
            description="Tài sản:",
            style={'description_width': 'initial'},
            layout={'width': '300px'}
        )
        self.current_price_input = widgets.FloatText(
            value=0.0,
            description="Giá hiện tại:",
            style={'description_width': 'initial'}
        )
        self.price_currency = widgets.Dropdown(
            options=[('VND', 'VND'), ('KRW', 'KRW')],
            value='VND',
            description="Đơn vị:",
            style={'description_width': 'initial'}
        )
        self.price_date = widgets.DatePicker(
            description="Ngày:",
            value=date.today(),
            style={'description_width': 'initial'}
        )
        self.update_price_btn = widgets.Button(
            description="Cập nhật Giá",
            button_style='warning',
            icon='edit'
        )
        
        # Target Allocation Management - CẬP NHẬT DANH SÁCH LOẠI TÀI SẢN
        self.allocation_header = widgets.HTML(
            value="<h3 style='color: #6F42C1;'>🎯 PHÂN BỔ MỤC TIÊU</h3>"
        )
        self.allocation_type = widgets.Dropdown(
            options=[
                'Cổ phiếu', 
                'Quỹ cổ phiếu',      # Rủi ro cao, lợi nhuận cao
                'Quỹ cân bằng',      # Rủi ro trung bình
                'Quỹ trái phiếu',    # Rủi ro thấp, lợi nhuận thấp
                'Tiền gửi', 
                'Vàng', 
                'Bất động sản', 
                'Crypto', 
                'Khác'
            ],
            description="Loại tài sản:",
            style={'description_width': 'initial'}
        )
        self.target_percent = widgets.FloatText(
            value=0.0,
            description="Tỷ lệ mục tiêu (%):",
            style={'description_width': 'initial'}
        )
        self.set_allocation_btn = widgets.Button(
            description="Thiết lập Tỷ lệ",
            button_style='info',
            icon='target'
        )
        self.clear_allocation_btn = widgets.Button(
            description="Xóa Tất cả",
            button_style='danger',
            icon='trash'
        )
        
        # Analysis Buttons
        self.analysis_header = widgets.HTML(
            value="<h3 style='color: #DC3545;'>📊 PHÂN TÍCH DANH MỤC</h3>"
        )
        self.show_portfolio_overview_btn = widgets.Button(
            description="Tổng quan Danh mục",
            button_style='info',
            icon='chart-pie'
        )
        self.show_performance_btn = widgets.Button(
            description="Hiệu suất Đầu tư",
            button_style='success',
            icon='chart-line'
        )
        self.show_allocation_analysis_btn = widgets.Button(
            description="Phân tích Phân bổ",
            button_style='warning',
            icon='balance-scale'
        )
        self.show_rebalance_recommendation_btn = widgets.Button(
            description="Khuyến nghị Cân bằng",
            button_style='primary',
            icon='sync-alt'
        )
        self.show_risk_analysis_btn = widgets.Button(
            description="Phân tích Rủi ro",
            button_style='danger',
            icon='exclamation-triangle'
        )
        
        # THÊM BUTTON PHÂN TÍCH QUỸ ĐẦU TƯ
        self.show_fund_analysis_btn = widgets.Button(
            description="Phân tích Quỹ Đầu tư",
            button_style='info',
            icon='chart-bar',
            tooltip="Phân tích chi tiết 3 loại quỹ: Trái phiếu, Cân bằng, Cổ phiếu"
        )
        
        # Advanced Analysis
        self.advanced_header = widgets.HTML(
            value="<h3 style='color: #17A2B8;'>🔬 PHÂN TÍCH NÂNG CAO</h3>"
        )
        self.time_period = widgets.Dropdown(
            options=[('3 tháng', 90), ('6 tháng', 180), ('1 năm', 365), ('2 năm', 730)],
            value=365,
            description="Thời gian:",
            style={'description_width': 'initial'}
        )
        self.show_trend_analysis_btn = widgets.Button(
            description="Xu hướng Đầu tư",
            button_style='info',
            icon='chart-area'
        )
        self.show_diversification_btn = widgets.Button(
            description="Đa dạng hóa",
            button_style='success',
            icon='sitemap'
        )
        self.export_report_btn = widgets.Button(
            description="Xuất Báo cáo",
            button_style='',
            icon='file-export'
        )
        
        # Data Management
        self.data_mgmt_header = widgets.HTML(
            value="<h3 style='color: #6C757D;'>💾 QUẢN LÝ DỮ LIỆU</h3>"
        )
        self.save_all_btn = widgets.Button(
            description="Lưu Tất cả",
            button_style='success',
            icon='save'
        )
        self.load_all_btn = widgets.Button(
            description="Tải Dữ liệu",
            button_style='info',
            icon='folder-open'
        )
        self.clear_all_btn = widgets.Button(
            description="Xóa Tất cả",
            button_style='danger',
            icon='trash-alt'
        )
        
        # Output
        self.output = widgets.Output()
        
        # Bind events
        self.update_exchange_btn.on_click(self.update_exchange_rate)
        self.import_data_btn.on_click(self.import_investment_data)
        self.update_price_btn.on_click(self.update_current_price)
        self.set_allocation_btn.on_click(self.set_target_allocation)
        self.clear_allocation_btn.on_click(self.clear_target_allocation)
        
        # Analysis events
        self.show_portfolio_overview_btn.on_click(self.show_portfolio_overview)
        self.show_performance_btn.on_click(self.show_performance_analysis)
        self.show_allocation_analysis_btn.on_click(self.show_allocation_analysis)
        self.show_rebalance_recommendation_btn.on_click(self.show_rebalance_recommendation)
        self.show_risk_analysis_btn.on_click(self.show_risk_analysis)
        self.show_fund_analysis_btn.on_click(self.show_fund_analysis)  # THÊM EVENT
        
        # Advanced analysis events
        self.show_trend_analysis_btn.on_click(self.show_trend_analysis)
        self.show_diversification_btn.on_click(self.show_diversification_analysis)
        self.export_report_btn.on_click(self.export_investment_report)
        
        # Data management events
        self.save_all_btn.on_click(self.save_all_data)
        self.load_all_btn.on_click(self.load_all_data)
        self.clear_all_btn.on_click(self.clear_all_data)

    def create_layout(self):
        # Settings tab
        settings_tab = widgets.VBox([
            self.settings_header,
            widgets.HBox([self.exchange_rate_input, self.exchange_rate_unit, self.update_exchange_btn]),
            widgets.HBox([self.currency_display]),
            
            self.import_header,
            widgets.HBox([self.import_file_path, self.import_data_btn]),
            
            self.price_header,
            widgets.HBox([self.asset_dropdown, self.current_price_input]),
            widgets.HBox([self.price_currency, self.price_date, self.update_price_btn]),
            
            self.allocation_header,
            widgets.HBox([self.allocation_type, self.target_percent]),
            widgets.HBox([self.set_allocation_btn, self.clear_allocation_btn])
        ])
        
        # Analysis tab - THÊM BUTTON PHÂN TÍCH QUỸ
        analysis_tab = widgets.VBox([
            self.analysis_header,
            widgets.HBox([self.show_portfolio_overview_btn, self.show_performance_btn]),
            widgets.HBox([self.show_allocation_analysis_btn, self.show_rebalance_recommendation_btn]),
            widgets.HBox([self.show_risk_analysis_btn, self.show_fund_analysis_btn]),  # THÊM VÀO ĐÂY
            
            self.advanced_header,
            widgets.HBox([self.time_period, self.show_trend_analysis_btn]),
            widgets.HBox([self.show_diversification_btn, self.export_report_btn]),
            
            self.data_mgmt_header,
            widgets.HBox([self.save_all_btn, self.load_all_btn, self.clear_all_btn])
        ])
        
        # Create tabs
        tabs = widgets.Tab()
        tabs.children = [settings_tab, analysis_tab]
        tabs.titles = ['Cài đặt & Dữ liệu', 'Phân tích Danh mục']
        
        self.main_layout = widgets.VBox([
            self.title,
            tabs,
            self.output
        ])


        def convert_currency(self, amount, from_currency, to_currency):
        """Chuyển đổi tiền tệ"""
        if from_currency == to_currency:
            return amount
        elif from_currency == 'KRW' and to_currency == 'VND':
            return amount * self.exchange_rate
        elif from_currency == 'VND' and to_currency == 'KRW':
            return amount / self.exchange_rate
        return amount
    
    def format_currency(self, amount, currency):
        """Format hiển thị tiền tệ"""
        if currency == 'VND':
            return f"{amount:,.0f}đ"
        elif currency == 'KRW':
            return f"{amount:,.0f}₩"
        return f"{amount:,.0f}"
    
    def calculate_gini_coefficient(self, values):
        """Tính hệ số Gini để đo độ bất bình đẳng phân bổ"""
        if not values or len(values) == 1:
            return 0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        cumsum = np.cumsum(sorted_values)
        
        return (n + 1 - 2 * sum((n + 1 - i) * y for i, y in enumerate(sorted_values, 1))) / (n * sum(sorted_values))


def show_fund_analysis(self, button):
        """Phân tích chi tiết 3 loại quỹ đầu tư"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        display_currency = self.currency_display.value
        
        # Lọc dữ liệu quỹ đầu tư
        fund_types = ['Quỹ trái phiếu', 'Quỹ cân bằng', 'Quỹ cổ phiếu']
        fund_data = [inv for inv in self.investment_data if inv['type'] in fund_types]
        
        if not fund_data:
            with self.output:
                clear_output()
                print("❌ Không có dữ liệu quỹ đầu tư để phân tích!")
                print("💡 Hãy đầu tư vào các quỹ: Quỹ trái phiếu, Quỹ cân bằng, hoặc Quỹ cổ phiếu")
            return
        
        with self.output:
            clear_output()
            
            print("="*80)
            print("🏛️  PHÂN TÍCH CHI TIẾT QUỸ ĐẦU TƯ")
            print("="*80)
            
            # Tính toán thống kê quỹ
            fund_summary = {}
            total_fund_value = 0
            
            for inv in fund_data:
                fund_type = inv['type']
                amount = self.convert_currency(inv['amount'], inv['currency'], display_currency)
                
                if fund_type not in fund_summary:
                    fund_summary[fund_type] = {
                        'value': 0,
                        'count': 0,
                        'risk_level': self.asset_risk_levels[fund_type]['risk'],
                        'expected_return': self.asset_risk_levels[fund_type]['expected_return'],
                        'volatility': self.asset_risk_levels[fund_type]['volatility']
                    }
                
                fund_summary[fund_type]['value'] += amount
                fund_summary[fund_type]['count'] += 1
                total_fund_value += amount
            
            # Tạo visualizations
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Phân bổ giá trị quỹ
            fund_names = list(fund_summary.keys())
            fund_values = [fund_summary[name]['value'] for name in fund_names]
            colors = ['lightgreen', 'gold', 'lightcoral']  # Xanh (trái phiếu), Vàng (cân bằng), Đỏ (cổ phiếu)
            
            wedges, texts, autotexts = ax1.pie(fund_values, labels=fund_names, autopct='%1.1f%%', 
                                              colors=colors[:len(fund_names)], startangle=90)
            ax1.set_title('Phân Bổ Giá Trị Quỹ Đầu Tư')
            
            # 2. So sánh rủi ro vs lợi nhuận
            risk_levels = [fund_summary[name]['risk_level'] for name in fund_names]
            expected_returns = [fund_summary[name]['expected_return'] for name in fund_names]
            
            scatter = ax2.scatter(risk_levels, expected_returns, 
                                s=[val/max(fund_values)*500 + 100 for val in fund_values],
                                c=colors[:len(fund_names)], alpha=0.7)
            
            # Thêm labels cho từng điểm
            for i, name in enumerate(fund_names):
                ax2.annotate(name.replace('Quỹ ', ''), 
                           (risk_levels[i], expected_returns[i]),
                           xytext=(5, 5), textcoords='offset points', fontsize=10)
            
            ax2.set_xlabel('Mức độ Rủi ro (1-5)')
            ax2.set_ylabel('Lợi nhuận Kỳ vọng (%/năm)')
            ax2.set_title('Ma Trận Rủi ro - Lợi nhuận Quỹ')
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(0.5, 5.5)
            
            # 3. Biểu đồ cột so sánh các chỉ số
            x = np.arange(len(fund_names))
            width = 0.25
            
            risk_vals = [fund_summary[name]['risk_level'] for name in fund_names]
            return_vals = [fund_summary[name]['expected_return']/3 for name in fund_names]  # Scale down for display
            volatility_vals = [fund_summary[name]['volatility']/4 for name in fund_names]  # Scale down for display
            
            bars1 = ax3.bar(x - width, risk_vals, width, label='Rủi ro (1-5)', color='red', alpha=0.7)
            bars2 = ax3.bar(x, return_vals, width, label='Lợi nhuận (%/3)', color='green', alpha=0.7)
            bars3 = ax3.bar(x + width, volatility_vals, width, label='Biến động (%/4)', color='orange', alpha=0.7)
            
            ax3.set_xlabel('Loại Quỹ')
            ax3.set_ylabel('Giá trị (Đã chuẩn hóa)')
            ax3.set_title('So Sánh Các Chỉ Số Quỹ')
            ax3.set_xticks(x)
            ax3.set_xticklabels([name.replace('Quỹ ', '') for name in fund_names])
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 4. Hiệu suất theo thời gian (nếu có nhiều giao dịch)
            fund_df = pd.DataFrame(fund_data)
            fund_df['date'] = pd.to_datetime(fund_df['date'])
            fund_df['amount_display'] = fund_df.apply(
                lambda row: self.convert_currency(row['amount'], row['currency'], display_currency), 
                axis=1
            )
            
            # Tích lũy theo từng loại quỹ
            fund_cumulative = fund_df.groupby(['date', 'type'])['amount_display'].sum().unstack(fill_value=0).cumsum()
            
            if not fund_cumulative.empty and len(fund_cumulative) > 1:
                for fund_type in fund_cumulative.columns:
                    color_map = {'Quỹ trái phiếu': 'green', 'Quỹ cân bằng': 'orange', 'Quỹ cổ phiếu': 'red'}
                    ax4.plot(fund_cumulative.index, fund_cumulative[fund_type], 
                           marker='o', label=fund_type.replace('Quỹ ', ''), 
                           color=color_map.get(fund_type, 'blue'), linewidth=2)
                
                ax4.set_title('Tích Lũy Đầu Tư Theo Loại Quỹ')
                ax4.set_ylabel(f'Tổng đầu tư ({display_currency})')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'Chưa đủ dữ liệu\nđể hiển thị xu hướng', 
                        ha='center', va='center', transform=ax4.transAxes, fontsize=12)
                ax4.set_title('Xu Hướng Đầu Tư Theo Thời Gian')
            
            plt.tight_layout()
            plt.show()
            
            # In báo cáo chi tiết
            print(f"💰 Tổng giá trị quỹ đầu tư: {self.format_currency(total_fund_value, display_currency)}")
            print(f"📊 Số loại quỹ đang đầu tư: {len(fund_summary)}/3")
            print("-"*80)
            
            # Phân tích từng loại

# Phân tích từng loại quỹ
            for fund_type in sorted(fund_summary.keys(), key=lambda x: fund_summary[x]['risk_level']):
                data = fund_summary[fund_type]
                percentage = (data['value'] / total_fund_value) * 100
                
                print(f"\n🏛️  {fund_type.upper()}")
                print(f"   💰 Giá trị: {self.format_currency(data['value'], display_currency)} ({percentage:.1f}%)")
                print(f"   📊 Số giao dịch: {data['count']}")
                print(f"   ⚠️  Mức rủi ro: {data['risk_level']}/5 ({'Thấp' if data['risk_level'] <= 2 else 'Trung bình' if data['risk_level'] <= 3 else 'Cao'})")
                print(f"   📈 Lợi nhuận kỳ vọng: {data['expected_return']:.1f}%/năm")
                print(f"   📉 Độ biến động: {data['volatility']:.1f}%")
                
                # Đánh giá và khuyến nghị
                if fund_type == 'Quỹ trái phiếu':
                    print(f"   💡 Đặc điểm: An toàn, ổn định, phù hợp bảo toàn vốn")
                    if percentage > 50:
                        print(f"   🟡 Cảnh báo: Tỷ trọng cao, có thể hạn chế tăng trưởng")
                elif fund_type == 'Quỹ cân bằng':
                    print(f"   💡 Đặc điểm: Cân bằng rủi ro-lợi nhuận, linh hoạt")
                    if percentage > 60:
                        print(f"   🟡 Gợi ý: Có thể đa dạng thêm sang các loại khác")
                elif fund_type == 'Quỹ cổ phiếu':
                    print(f"   💡 Đặc điểm: Tiềm năng tăng trưởng cao, biến động lớn")
                    if percentage > 40:
                        print(f"   🔴 Cảnh báo: Rủi ro cao, cần cân nhắc cân bằng")
            
            # Phân tích portfolio quỹ tổng thể
            print(f"\n" + "="*80)
            print("📊 PHÂN TÍCH PORTFOLIO QUỸ TỔNG THỂ")
            print("="*80)
            
            # Tính điểm rủi ro và lợi nhuận trung bình có trọng số
            weighted_risk = sum(fund_summary[name]['risk_level'] * fund_summary[name]['value'] 
                               for name in fund_names) / total_fund_value
            weighted_return = sum(fund_summary[name]['expected_return'] * fund_summary[name]['value'] 
                                 for name in fund_names) / total_fund_value
            weighted_volatility = sum(fund_summary[name]['volatility'] * fund_summary[name]['value'] 
                                     for name in fund_names) / total_fund_value
            
            print(f"⚡ Điểm rủi ro trung bình: {weighted_risk:.2f}/5")
            print(f"📈 Lợi nhuận kỳ vọng trung bình: {weighted_return:.1f}%/năm")
            print(f"📊 Độ biến động trung bình: {weighted_volatility:.1f}%")
            
            # Đánh giá portfolio
            if weighted_risk <= 2.5:
                risk_assessment = "🟢 Bảo thủ - Ưu tiên an toàn"
                recommendation = "Có thể tăng tỷ trọng quỹ cổ phiếu để tăng lợi nhuận"
            elif weighted_risk <= 3.5:
                risk_assessment = "🟡 Cân bằng - Hài hòa rủi ro và lợi nhuận"
                recommendation = "Portfolio quỹ đã cân bằng tốt"
            else:
                risk_assessment = "🔴 Tích cực - Ưu tiên tăng trưởng"
                recommendation = "Cần tăng tỷ trọng quỹ trái phiếu để giảm rủi ro"
            
            print(f"🎯 Đánh giá portfolio: {risk_assessment}")
            print(f"💡 Khuyến nghị: {recommendation}")
            
            # Khuyến nghị phân bổ tối ưu
            print(f"\n💡 KHUYẾN NGHỊ PHÂN BỔ QUỸ TỐI ƯU:")
            
            # Dựa trên risk profile để đưa ra khuyến nghị
            if weighted_risk < 2.0:
                print("   🔹 Quỹ trái phiếu: 30-50% (hiện tại cần giảm)")
                print("   🔹 Quỹ cân bằng: 30-40% (có thể tăng)")
                print("   🔹 Quỹ cổ phiếu: 20-30% (nên tăng đáng kể)")
            elif weighted_risk < 3.0:
                print("   🔹 Quỹ trái phiếu: 25-35% (tùy điều chỉnh)")
                print("   🔹 Quỹ cân bằng: 35-45% (duy trì)")
                print("   🔹 Quỹ cổ phiếu: 20-35% (có thể tăng nhẹ)")
            else:
                print("   🔹 Quỹ trái phiếu: 20-30% (cần tăng)")
                print("   🔹 Quỹ cân bằng: 30-40% (duy trì)")
                print("   🔹 Quỹ cổ phiếu: 25-35% (cần giảm)")
            
            # Phân tích thiếu hụt
            missing_funds = [fund for fund in fund_types if fund not in fund_summary]
            if missing_funds:
                print(f"\n⚠️  THIẾU HỤT LOẠI QUỸ:")
                for missing_fund in missing_funds:
                    risk_info = self.asset_risk_levels[missing_fund]
                    print(f"   🔸 {missing_fund}: Rủi ro {risk_info['risk']}/5, Lợi nhuận {risk_info['expected_return']}%")
                    if missing_fund == 'Quỹ trái phiếu':
                        print("      → Giúp ổn định danh mục, giảm rủi ro")
                    elif missing_fund == 'Quỹ cân bằng':
                        print("      → Cân bằng giữa an toàn và tăng trưởng")
                    elif missing_fund == 'Quỹ cổ phiếu':
                        print("      → Tăng tiềm năng lợi nhuận dài hạn")
            
            # Tính toán lợi nhuận dự kiến
            print(f"\n📊 DỰ BÁO LỢI NHUẬN VÀ RỦI RO:")
            expected_annual_return = total_fund_value * weighted_return / 100
            expected_volatility_range = total_fund_value * weighted_volatility / 100
            
            print(f"   📈 Lợi nhuận dự kiến/năm: {self.format_currency(expected_annual_return, display_currency)}")
            print(f"   📊 Biên độ dao động: ±{self.format_currency(expected_volatility_range, display_currency)}")
            print(f"   🎯 Kịch bản tốt: {self.format_currency(total_fund_value + expected_annual_return + expected_volatility_range, display_currency)}")
            print(f"   ⚠️  Kịch bản xấu: {self.format_currency(total_fund_value + expected_annual_return - expected_volatility_range, display_currency)}")
            
            # So sánh với tổng portfolio
            total_portfolio_value = sum(self.convert_currency(inv['amount'], inv['currency'], display_currency) 
                                       for inv in self.investment_data)
            fund_percentage_in_portfolio = (total_fund_value / total_portfolio_value) * 100
            
            print(f"\n🔍 VỊ TRÍ TRONG TỔNG DANH MỤC:")
            print(f"   📊 Tỷ trọng quỹ trong tổng danh mục: {fund_percentage_in_portfolio:.1f}%")
            
            if fund_percentage_in_portfolio < 30:
                print("   💡 Tỷ trọng quỹ thấp - có thể tăng để đa dạng hóa")
            elif fund_percentage_in_portfolio > 70:
                print("   ⚠️  Tỷ trọng quỹ cao - cân nhắc đa dạng sang tài sản khác")
            else:
                print("   ✅ Tỷ trọng quỹ hợp lý trong tổng danh mục")


def update_exchange_rate(self, button):
        """Cập nhật tỷ giá"""
        if self.exchange_rate_input.value > 0:
            self.exchange_rate = self.exchange_rate_input.value
            self.save_settings()
            
            with self.output:
                clear_output()
                print(f"✅ Đã cập nhật tỷ giá: 1 KRW = {self.exchange_rate} VND")
        else:
            with self.output:
                clear_output()
                print("❌ Tỷ giá phải lớn hơn 0!")
    
    def import_investment_data(self, button):
        """Import dữ liệu đầu tư từ file CSV của finance tracker"""
        try:
            file_path = self.import_file_path.value
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # Clear existing data
            self.investment_data = []
            
            # Process data
            for _, row in df.iterrows():
                investment_type = self.investment_mapping.get(row['type'], 'Khác')
                
                self.investment_data.append({
                    'date': pd.to_datetime(row['date']).date(),
                    'type': investment_type,
                    'description': row['description'],
                    'amount': float(row['amount']),
                    'currency': row.get('currency', 'VND'),
                    'original_type': row['type']
                })
            
            # Update asset dropdown
            self.update_asset_dropdown()
            
            with self.output:
                clear_output()
                print(f"✅ Đã import {len(self.investment_data)} bản ghi đầu tư từ {file_path}")
                print("📊 Phân loại đầu tư:")
                
                # Show investment breakdown
                type_summary = {}
                for inv in self.investment_data:
                    inv_type = inv['type']
                    amount_vnd = self.convert_currency(inv['amount'], inv['currency'], 'VND')
                    type_summary[inv_type] = type_summary.get(inv_type, 0) + amount_vnd
                
                for inv_type, total in type_summary.items():
                    print(f"   • {inv_type}: {total:,.0f}đ")
                    
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi import dữ liệu: {str(e)}")
    
    def update_asset_dropdown(self):
        """Cập nhật dropdown danh sách tài sản"""
        options = [('-- Chọn tài sản --', '')]
        
        # Group by type and description
        assets = set()
        for inv in self.investment_data:
            asset_key = f"{inv['type']} - {inv['description']}"
            assets.add(asset_key)
        
        for asset in sorted(assets):
            options.append((asset, asset))
        
        self.asset_dropdown.options = options
    
    def update_current_price(self, button):
        """Cập nhật giá hiện tại của tài sản"""
        if self.asset_dropdown.value and self.current_price_input.value > 0:
            asset_key = self.asset_dropdown.value
            price_info = {
                'price': self.current_price_input.value,
                'currency': self.price_currency.value,
                'date': self.price_date.value
            }
            
            self.current_prices[asset_key] = price_info
            self.save_current_prices()
            
            with self.output:
                clear_output()
                formatted_price = self.format_currency(self.current_price_input.value, self.price_currency.value)
                print(f"✅ Đã cập nhật giá {asset_key}: {formatted_price}")
        else:
            with self.output:
                clear_output()
                print("❌ Vui lòng chọn tài sản và nhập giá hợp lệ!")
    
    def set_target_allocation(self, button):
        """Thiết lập tỷ lệ phân bổ mục tiêu"""
        if self.target_percent.value >= 0:
            self.target_allocation[self.allocation_type.value] = self.target_percent.value
            self.save_target_allocation()
            
            with self.output:
                clear_output()
                print(f"✅ Đã thiết lập tỷ lệ mục tiêu cho {self.allocation_type.value}: {self.target_percent.value}%")
                
                # Show current allocation targets
                print("\n🎯 Phân bổ mục tiêu hiện tại:")
                total_percent = 0
                for asset_type, percent in self.target_allocation.items():
                    print(f"   • {asset_type}: {percent}%")
                    total_percent += percent
                print(f"   📊 Tổng: {total_percent}%")
                
                if total_percent != 100:
                    print(f"   ⚠️  Chưa đạt 100% (còn {100-total_percent}%)")
        else:
            with self.output:
                clear_output()
                print("❌ Tỷ lệ phần trăm phải >= 0!")
    
    def clear_target_allocation(self, button):
        """Xóa tất cả tỷ lệ phân bổ mục tiêu"""
        self.target_allocation = {}
        self.save_target_allocation()
        
        with self.output:
            clear_output()
            print("🗑️ Đã xóa tất cả tỷ lệ phân bổ mục tiêu")

def save_settings(self):
        """Lưu cài đặt tỷ giá"""
        try:
            settings_df = pd.DataFrame([{
                'parameter': 'exchange_rate',
                'value': self.exchange_rate,
                'updated_date': datetime.now().date()
            }])
            settings_df.to_csv(self.data_files['settings'], index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"Lỗi khi lưu cài đặt: {str(e)}")
    
    def save_current_prices(self):
        """Lưu giá hiện tại"""
        try:
            if self.current_prices:
                prices_data = []
                for asset_key, price_info in self.current_prices.items():
                    prices_data.append({
                        'asset': asset_key,
                        'price': price_info['price'],
                        'currency': price_info['currency'],
                        'date': price_info['date']
                    })
                
                prices_df = pd.DataFrame(prices_data)
                prices_df.to_csv(self.data_files['investment_prices'], index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"Lỗi khi lưu giá: {str(e)}")
    
    def save_target_allocation(self):
        """Lưu tỷ lệ phân bổ mục tiêu"""
        try:
            if self.target_allocation:
                allocation_data = []
                for asset_type, target_pct in self.target_allocation.items():
                    allocation_data.append({
                        'asset_type': asset_type,
                        'target_percent': target_pct
                    })
                
                allocation_df = pd.DataFrame(allocation_data)
                allocation_df.to_csv(self.data_files['target_allocation'], index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"Lỗi khi lưu phân bổ mục tiêu: {str(e)}")
    
    def load_data(self):
        """Tải dữ liệu từ các file"""
        # Load settings
        try:
            df = pd.read_csv(self.data_files['settings'], encoding='utf-8-sig')
            for _, row in df.iterrows():
                if row['parameter'] == 'exchange_rate':
                    self.exchange_rate = float(row['value'])
                    self.exchange_rate_input.value = self.exchange_rate
            print(f"✅ Đã load cài đặt tỷ giá: {self.exchange_rate}")
        except FileNotFoundError:
            print("📝 Chưa có file cài đặt - sử dụng mặc định")
        except Exception as e:
            print(f"⚠️  Lỗi khi load cài đặt: {str(e)}")
        
        # Load current prices
        try:
            df = pd.read_csv(self.data_files['investment_prices'], encoding='utf-8-sig')
            self.current_prices = {}
            for _, row in df.iterrows():
                self.current_prices[row['asset']] = {
                    'price': float(row['price']),
                    'currency': row['currency'],
                    'date': pd.to_datetime(row['date']).date()
                }
            print(f"✅ Đã load {len(self.current_prices)} giá tài sản")
        except FileNotFoundError:
            print("📝 Chưa có file giá tài sản")
        except Exception as e:
            print(f"⚠️  Lỗi khi load giá: {str(e)}")
        
        # Load target allocation
        try:
            df = pd.read_csv(self.data_files['target_allocation'], encoding='utf-8-sig')
            self.target_allocation = {}
            for _, row in df.iterrows():
                self.target_allocation[row['asset_type']] = float(row['target_percent'])
            print(f"✅ Đã load tỷ lệ phân bổ mục tiêu cho {len(self.target_allocation)} loại tài sản")
        except FileNotFoundError:
            print("📝 Chưa có file phân bổ mục tiêu")
        except Exception as e:
            print(f"⚠️  Lỗi khi load phân bổ mục tiêu: {str(e)}")
    
    def save_all_data(self, button):
        """Lưu tất cả dữ liệu"""
        try:
            self.save_settings()
            self.save_current_prices()
            self.save_target_allocation()
            
            with self.output:
                clear_output()
                print("✅ Đã lưu tất cả dữ liệu!")
                print("📁 Các file được tạo:")
                print("   • investment_settings.csv - Cài đặt tỷ giá")
                print("   • investment_current_prices.csv - Giá hiện tại")
                print("   • target_allocation.csv - Phân bổ mục tiêu")
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi lưu dữ liệu: {str(e)}")
    
    def load_all_data(self, button):
        """Tải lại tất cả dữ liệu"""
        try:
            self.load_data()
            self.update_asset_dropdown()
            
            with self.output:
                clear_output()
                print("✅ Đã tải lại tất cả dữ liệu!")
                print(f"📊 Tỷ giá: 1 KRW = {self.exchange_rate} VND")
                print(f"📊 Giá tài sản: {len(self.current_prices)} mục")
                print(f"📊 Phân bổ mục tiêu: {len(self.target_allocation)} loại")
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi tải dữ liệu: {str(e)}")
    
    def clear_all_data(self, button):
        """Xóa tất cả dữ liệu"""
        import os
        
        try:
            # Clear memory data
            self.investment_data = []
            self.current_prices = {}
            self.target_allocation = {}
            self.exchange_rate = 18.0
            
            # Update UI
            self.exchange_rate_input.value = 18.0
            self.update_asset_dropdown()
            
            # Remove files
            for filename in self.data_files.values():
                if os.path.exists(filename):
                    os.remove(filename)
            
            with self.output:
                clear_output()
                print("⚠️  Đã xóa toàn bộ dữ liệu và file!")
                print("📝 Bạn có thể bắt đầu import dữ liệu mới.")
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi xóa dữ liệu: {str(e)}")
    
    def display(self):
        return self.main_layout

def show_allocation_analysis(self, button):
        """Phân tích phân bổ danh mục so với mục tiêu"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        if not self.target_allocation:
            with self.output:
                clear_output()
                print("❌ Chưa thiết lập tỷ lệ phân bổ mục tiêu!")
            return
        
        display_currency = self.currency_display.value
        
        with self.output:
            clear_output()

            # Calculate current allocation
            current_allocation = {}
            total_value = 0
            
            for inv in self.investment_data:
                inv_type = inv['type']
                amount = self.convert_currency(inv['amount'], inv['currency'], display_currency)
                
                current_allocation[inv_type] = current_allocation.get(inv_type, 0) + amount
                total_value += amount
            
            # Convert to percentages
            current_allocation_pct = {
                asset_type: (value / total_value) * 100 
                for asset_type, value in current_allocation.items()
            }

            print("="*70)
            print(f"🎯 PHÂN TÍCH PHÂN BỔ DANH MỤC ({display_currency})")
            print("="*70)
            print(f"💰 Tổng giá trị danh mục: {self.format_currency(total_value, display_currency)}")
            print("-"*70)
            
            # Create comparison visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # Get all asset types from both current and target
            all_asset_types = set(list(current_allocation_pct.keys()) + list(self.target_allocation.keys()))
            
            # Prepare data for comparison
            comparison_data = []
            for asset_type in all_asset_types:
                current_pct = current_allocation_pct.get(asset_type, 0)
                target_pct = self.target_allocation.get(asset_type, 0)
                deviation = current_pct - target_pct
                
                comparison_data.append({
                    'asset_type': asset_type,
                    'current_pct': current_pct,
                    'target_pct': target_pct,
                    'deviation': deviation,
                    'current_value': current_allocation.get(asset_type, 0),
                    'target_value': (target_pct / 100) * total_value if total_value > 0 else 0,
                    'adjustment_needed': ((target_pct / 100) * total_value) - current_allocation.get(asset_type, 0)
                })
            
            # Sort by absolute deviation for better visualization
            comparison_data.sort(key=lambda x: abs(x['deviation']), reverse=True)
            
            # 1. Current vs Target Allocation (Bar Chart)
            asset_types = [item['asset_type'] for item in comparison_data]
            current_values = [item['current_pct'] for item in comparison_data]
            target_values = [item['target_pct'] for item in comparison_data]
            
            x = np.arange(len(asset_types))
            width = 0.35
            
            bars1 = ax1.bar(x - width/2, current_values, width, label='Hiện tại', color='lightblue', alpha=0.8)
            bars2 = ax1.bar(x + width/2, target_values, width, label='Mục tiêu', color='lightcoral', alpha=0.8)
            
            ax1.set_xlabel('Loại Tài Sản')
            ax1.set_ylabel('Tỷ lệ (%)')
            ax1.set_title('So Sánh Phân Bổ Hiện Tại vs Mục Tiêu')
            ax1.set_xticks(x)
            ax1.set_xticklabels(asset_types, rotation=45, ha='right')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
            
            for bar in bars2:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
            
            # 2. Deviation Analysis
            deviations = [item['deviation'] for item in comparison_data]
            colors = ['red' if dev < -5 else 'orange' if dev < -2 else 'lightgreen' if abs(dev) <= 2 else 'yellow' if dev

colors = ['red' if dev < -5 else 'orange' if dev < -2 else 'lightgreen' if abs(dev) <= 2 else 'yellow' if dev < 5 else 'red' for dev in deviations]
            
            bars = ax2.barh(asset_types, deviations, color=colors, alpha=0.7)
            ax2.set_xlabel('Độ lệch (%)')
            ax2.set_title('Độ Lệch So Với Mục Tiêu')
            ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
            ax2.grid(True, alpha=0.3)
            
            # Add deviation labels
            for i, (bar, dev) in enumerate(zip(bars, deviations)):
                ax2.text(dev + (0.5 if dev >= 0 else -0.5), i,
                        f'{dev:+.1f}%', va='center', ha='left' if dev >= 0 else 'right', fontweight='bold')
            
            # 3. Current Allocation Pie Chart
            current_types = [k for k, v in current_allocation_pct.items() if v > 0]
            current_pcts = [current_allocation_pct[k] for k in current_types]
            
            colors_pie = plt.cm.Set3(np.linspace(0, 1, len(current_types)))
            ax3.pie(current_pcts, labels=current_types, autopct='%1.1f%%', colors=colors_pie, startangle=90)
            ax3.set_title('Phân Bổ Hiện Tại')
            
            # 4. Target Allocation Pie Chart
            target_types = [k for k, v in self.target_allocation.items() if v > 0]
            target_pcts = [self.target_allocation[k] for k in target_types]
            
            ax4.pie(target_pcts, labels=target_types, autopct='%1.1f%%', colors=colors_pie, startangle=90)
            ax4.set_title('Phân Bổ Mục Tiêu')
            
            plt.tight_layout()
            plt.show()
            
            # Print detailed analysis
            print("📊 CHI TIẾT PHÂN TÍCH PHÂN BỔ:")
            print(f"{'Loại tài sản':<20} {'Hiện tại':<12} {'Mục tiêu':<12} {'Độ lệch':<12} {'Trạng thái':<15}")
            print("-"*85)
            
            total_deviation = 0
            critical_deviations = 0
            
            for item in comparison_data:
                asset_type = item['asset_type']
                current_pct = item['current_pct']
                target_pct = item['target_pct']
                deviation = item['deviation']
                
                # Determine status
                if abs(deviation) <= 2:
                    status = "🟢 Tốt"
                elif abs(deviation) <= 5:
                    status = "🟡 Chấp nhận được"
                elif deviation > 5:
                    status = "🔴 Quá cao"
                    critical_deviations += 1
                else:
                    status = "🔵 Quá thấp"
                    critical_deviations += 1
                
                print(f"{asset_type:<20} {current_pct:>8.1f}% {target_pct:>8.1f}% {deviation:>+8.1f}% {status:<15}")
                total_deviation += abs(deviation)
            
            # Overall assessment
            print("-"*85)
            print(f"📈 ĐÁNH GIÁ TỔNG QUAN:")
            print(f"   • Tổng độ lệch tuyệt đối: {total_deviation:.1f}%")
            print(f"   • Số loại tài sản cần điều chỉnh: {critical_deviations}")
            
            if total_deviation <= 10:
                overall_status = "🟢 Danh mục cân bằng tốt"
            elif total_deviation <= 20:
                overall_status = "🟡 Cần điều chỉnh nhẹ"
            else:
                overall_status = "🔴 Cần tái cân bằng mạnh"
            
            print(f"   • Trạng thái tổng thể: {overall_status}")
            
            # Rebalancing recommendations
            print(f"\n💡 KHUYẾN NGHỊ TÁI CÂN BẰNG:")
            
            rebalance_needed = False
            for item in comparison_data:
                if abs(item['deviation']) > 5:
                    rebalance_needed = True
                    asset_type = item['asset_type']
                    deviation = item['deviation']
                    adjustment_value = abs(item['adjustment_needed'])
                    
                    if deviation > 5:
                        action = "Giảm"
                        print(f"   🔻 {action} {asset_type}: {self.format_currency(adjustment_value, display_currency)}")
                    else:
                        action = "Tăng"
                        print(f"   🔺 {action} {asset_type}: {self.format_currency(adjustment_value, display_currency)}")
            
            if not rebalance_needed:
                print("   ✅ Danh mục hiện tại đã khá cân bằng, không cần điều chỉnh lớn!")
            
            # Risk assessment cho từng loại quỹ
            print(f"\n⚠️  ĐÁNH GIÁ RỦI RO PHÂN BỔ QUỸ:")
            
            # Kiểm tra phân bổ quỹ
            fund_allocation = {}
            for item in comparison_data:
                asset_type = item['asset_type']
                if 'Quỹ' in asset_type:
                    fund_allocation[asset_type] = {
                        'current': item['current_pct'],
                        'target': item['target_pct'],
                        'deviation': item['deviation']
                    }
            
            if fund_allocation:
                print("   📊 Phân tích quỹ đầu tư:")
                for fund_type, data in fund_allocation.items():
                    risk_level = self.asset_risk_levels.get(fund_type, {}).get('risk', 3)
                    expected_return = self.asset_risk_levels.get(fund_type, {}).get('expected_return', 10)
                    
                    print(f"   • {fund_type}:")
                    print(f"     - Hiện tại: {data['current']:.1f}%, Mục tiêu: {data['target']:.1f}%")
                    print(f"     - Rủi ro: {risk_level}/5, Lợi nhuận KV: {expected_return}%/năm")
                    
                    if abs(data['deviation']) > 5:
                        if fund_type == 'Quỹ trái phiếu' and data['deviation'] < -5:
                            print(f"     - ⚠️ Thiếu quỹ an toàn, có thể tăng rủi ro danh mục")
                        elif fund_type == 'Quỹ cổ phiếu' and data['deviation'] > 5:
                            print(f"     - ⚠️ Quá nhiều quỹ rủi ro cao, cần cân bằng")
                        elif fund_type == 'Quỹ cân bằng':
                            if data['deviation'] > 5:
                                print(f"     - 💡 Có thể phân bổ sang các quỹ chuyên biệt hơn")
                            else:
                                print(f"     - 💡 Cần tăng để cân bằng danh mục")
            
            # Timeline recommendation
            if critical_deviations > 0:
                print(f"\n📅 LỊCH TRÌNH ĐỀ XUẤT:")
                print(f"   • Tái cân bằng ngay: {critical_deviations} loại tài sản cần điều chỉnh mạnh")
                print(f"   • Theo dõi hàng tháng: Các loại tài sản khác")
                print(f"   • Đánh giá lại mục tiêu: Sau 3-6 tháng")

# Hàm tạo ứng dụng
def create_investment_analyzer():
    """
    Hàm khởi tạo ứng dụng phân tích danh mục đầu tư
    """
    analyzer = InvestmentPortfolioAnalyzer()
    return analyzer.display()

# Hướng dẫn sử dụng
def show_usage_guide():
    """
    Hiển thị hướng dẫn sử dụng ứng dụng
    """
    guide = """
    📖 HƯỚNG DẪN SỬ DỤNG ỨNG DỤNG PHÂN TÍCH DANH MỤC ĐẦU TƯ - PHIÊN BẢN QUỸ NÂNG CAO
    
    🔧 BƯỚC 1: CÀI ĐẶT BAN ĐẦU
    ├── Cập nhật tỷ giá KRW/VND hiện tại
    ├── Import dữ liệu từ file finance_data_savings.csv
    └── Thiết lập tỷ lệ phân bổ mục tiêu cho từng loại tài sản
    
    💰 BƯỚC 2: CẬP NHẬT GIÁ TÀI SẢN (tùy chọn)
    ├── Chọn tài sản từ dropdown
    ├── Nhập giá hiện tại và đơn vị tiền tệ
    └── Cập nhật để phân tích hiệu suất chính xác
    
    📊 BƯỚC 3: PHÂN TÍCH DANH MỤC
    ├── Tổng quan Danh mục - Xem phân bổ tổng thể
    ├── Hiệu suất Đầu tư - Phân tích xu hướng đầu tư
    ├── Phân tích Phân bổ - So sánh với mục tiêu
    ├── Khuyến nghị Cân bằng - Hành động cần thực hiện
    ├── Phân tích Rủi ro - Đánh giá mức độ rủi ro
    └── Phân tích Quỹ Đầu tư - Chi tiết 3 loại quỹ ⭐ MỚI
    
    🔬 BƯỚC 4: PHÂN TÍCH NÂNG CAO
    ├── Xu hướng Đầu tư - Phân tích theo thời gian
    ├── Đa dạng hóa - Đánh giá mức độ đa dạng
    └── Tổng Tài sản - Quy đổi tiền tệ
    
    📄 BƯỚC 5: XUẤT BÁO CÁO
    └── Xuất file Excel chi tiết với tất cả phân tích
    
    💾 ĐẶC ĐIỂM MỚI - PHÂN TÍCH QUỸ:
    • Quỹ Trái phiếu: Rủi ro thấp (2/5), Lợi nhuận 8%/năm
    • Quỹ Cân bằng: Rủi ro trung bình (3/5), Lợi nhuận 10%/năm  
    • Quỹ Cổ phiếu: Rủi ro cao (4/5), Lợi nhuận 15%/năm
    • Ma trận rủi ro-lợi nhuận với khuyến nghị phân bổ tối ưu
    • Dự báo lợi nhuận và kịch bản rủi ro
    
    💡 LƯU Ý:
    • Dữ liệu sẽ được lưu tự động vào các file CSV
    • Có thể import dữ liệu từ ứng dụng finance tracker
    • Hỗ trợ đầy đủ VND và KRW với tỷ giá linh hoạt
    • Hệ thống mapping tự động từ "Quỹ đầu tư" sang 3 loại quỹ chi tiết
    """
    
    print(guide)

# Khởi chạy ứng dụng
if __name__ == "__main__":
    print("🚀 Khởi động ứng dụng phân tích danh mục đầu tư - Phiên bản Quỹ Nâng cao...")
    show_usage_guide()
    print("\n" + "="*50)
    print("📱 Chạy lệnh sau để bắt đầu:")
    print("investment_app = create_investment_analyzer()")
    print("display(investment_app)")
    print("="*50)



        
