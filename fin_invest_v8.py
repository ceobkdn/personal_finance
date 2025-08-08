import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, date, timedelta
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
import os

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

        # Mapping từ savings type sang investment category
        self.investment_mapping = {
            'Đầu tư chứng khoán': 'Cổ phiếu',
            'Quỹ đầu tư': 'Quỹ cân bằng',
            'Quỹ cân bằng': 'Quỹ cân bằng',
            'Quỹ đầu tư cân bằng': 'Quỹ cân bằng',
            'Quỹ trái phiếu': 'Quỹ trái phiếu',
            'Quỹ đầu tư trái phiếu': 'Quỹ trái phiếu',
            'Quỹ cổ phiếu': 'Quỹ cổ phiếu',
            'Quỹ đầu tư cổ phiếu': 'Quỹ cổ phiếu',
            'Tiết kiệm ngân hàng': 'Tiền gửi',
            'Vàng': 'Vàng',
            'Bất động sản': 'Bất động sản',
            'Crypto': 'Crypto',
            'Khác': 'Khác'
        }

        # Cập nhật rủi ro và lợi nhuận theo loại quỹ
        self.asset_risk_levels = {
            'Tiền gửi': {'risk': 1, 'expected_return': 6.0, 'volatility': 0.5},
            'Quỹ trái phiếu': {'risk': 2, 'expected_return': 8.0, 'volatility': 3.0},
            'Vàng': {'risk': 2, 'expected_return': 7.5, 'volatility': 12.0},
            'Quỹ cân bằng': {'risk': 3, 'expected_return': 10.0, 'volatility': 8.0},
            'Bất động sản': {'risk': 3, 'expected_return': 12.0, 'volatility': 15.0},
            'Quỹ cổ phiếu': {'risk': 4, 'expected_return': 15.0, 'volatility': 18.0},
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

        # Target Allocation Management
        self.allocation_header = widgets.HTML(
            value="<h3 style='color: #6F42C1;'>🎯 PHÂN BỔ MỤC TIÊU</h3>"
        )
        self.allocation_type = widgets.Dropdown(
            options=[
                'Cổ phiếu',
                'Quỹ cổ phiếu',
                'Quỹ cân bằng',
                'Quỹ trái phiếu',
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
        self.show_fund_analysis_btn.on_click(self.show_fund_analysis)

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

        # Analysis tab
        analysis_tab = widgets.VBox([
            self.analysis_header,
            widgets.HBox([self.show_portfolio_overview_btn, self.show_performance_btn]),
            widgets.HBox([self.show_allocation_analysis_btn, self.show_rebalance_recommendation_btn]),
            widgets.HBox([self.show_risk_analysis_btn, self.show_fund_analysis_btn]),
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

    def update_exchange_rate(self, button):
        """Cập nhật tỷ giá"""
        if self.exchange_rate_input.value <= 0:
            with self.output:
                clear_output()
                print("❌ Tỷ giá phải lớn hơn 0!")
            return
        
        self.exchange_rate = self.exchange_rate_input.value
        self.save_settings()
        
        with self.output:
            clear_output()
            print(f"✅ Đã cập nhật tỷ giá: 1 KRW = {self.exchange_rate} VND")

    def set_target_allocation(self, button):
        """Thiết lập tỷ lệ phân bổ mục tiêu"""
        if self.target_percent.value < 0:
            with self.output:
                clear_output()
                print("❌ Tỷ lệ phần trăm phải >= 0!")
            return

        self.target_allocation[self.allocation_type.value] = self.target_percent.value
        self.save_target_allocation()
        
        with self.output:
            clear_output()
            print(f"✅ Đã thiết lập tỷ lệ mục tiêu cho {self.allocation_type.value}: {self.target_percent.value}%")
            
            print("\n🎯 Phân bổ mục tiêu hiện tại:")
            total_percent = sum(self.target_allocation.values())
            for asset_type, percent in self.target_allocation.items():
                print(f" • {asset_type}: {percent}%")
            print(f" 📊 Tổng: {total_percent}%")
            
            if total_percent != 100:
                print(f" ⚠️ Chưa đạt 100% (còn {100-total_percent}%)")

    def clear_target_allocation(self, button):
        """Xóa tất cả tỷ lệ phân bổ mục tiêu"""
        self.target_allocation = {}
        self.save_target_allocation()
        
        with self.output:
            clear_output()
            print("🗑️ Đã xóa tất cả tỷ lệ phân bổ mục tiêu")

    def convert_currency(self, amount, from_currency, to_currency):
        """Chuyển đổi tiền tệ"""
        if from_currency == to_currency:
            return amount
        if self.exchange_rate == 0:
            raise ValueError("Tỷ giá hối đoái không thể bằng 0!")
        if from_currency == 'KRW' and to_currency == 'VND':
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
        if any(not isinstance(v, (int, float)) or v < 0 for v in values):
            raise ValueError("Danh sách giá trị phải chứa các số không âm!")
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        cumsum = np.cumsum(sorted_values)
        return (n + 1 - 2 * sum((n + 1 - i) * y for i, y in enumerate(sorted_values, 1))) / (n * sum(sorted_values))

    def show_fund_analysis(self, button):
        # Giữ nguyên như code bạn cung cấp
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return

        display_currency = self.currency_display.value
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
            print("🏛️ PHÂN TÍCH CHI TIẾT QUỸ ĐẦU TƯ")
            print("="*80)

            fund_summary = {}
            total_fund_value = 0

            for inv in fund_data:
                fund_type = inv['type']
                try:
                    amount = self.convert_currency(inv['amount'], inv['currency'], display_currency)
                except ValueError as e:
                    print(f"⚠️ Lỗi chuyển đổi tiền tệ cho {fund_type}: {str(e)}")
                    continue

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

            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

            fund_names = list(fund_summary.keys())
            fund_values = [fund_summary[name]['value'] for name in fund_names]
            colors = ['lightgreen', 'gold', 'lightcoral']

            wedges, texts, autotexts = ax1.pie(fund_values, labels=fund_names, autopct='%1.1f%%',
                                             colors=colors[:len(fund_names)], startangle=90)
            ax1.set_title('Phân Bổ Giá Trị Quỹ Đầu Tư')

            risk_levels = [fund_summary[name]['risk_level'] for name in fund_names]
            expected_returns = [fund_summary[name]['expected_return'] for name in fund_names]

            scatter = ax2.scatter(risk_levels, expected_returns,
                                 s=[val/max(fund_values)*500 + 100 for val in fund_values],
                                 c=colors[:len(fund_names)], alpha=0.7)

            for i, name in enumerate(fund_names):
                ax2.annotate(name.replace('Quỹ ', ''),
                            (risk_levels[i], expected_returns[i]),
                            xytext=(5, 5), textcoords='offset points', fontsize=10)

            ax2.set_xlabel('Mức độ Rủi ro (1-5)')
            ax2.set_ylabel('Lợi nhuận Kỳ vọng (%/năm)')
            ax2.set_title('Ma Trận Rủi ro - Lợi nhuận Quỹ')
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(0.5, 5.5)

            x = np.arange(len(fund_names))
            width = 0.25

            risk_vals = [fund_summary[name]['risk_level'] for name in fund_names]
            return_vals = [fund_summary[name]['expected_return']/3 for name in fund_names]
            volatility_vals = [fund_summary[name]['volatility']/4 for name in fund_names]

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

            fund_df = pd.DataFrame(fund_data)
            try:
                fund_df['date'] = pd.to_datetime(fund_df['date'], errors='coerce')
                if fund_df['date'].isnull().any():
                    print("⚠️ Một số bản ghi có định dạng ngày không hợp lệ, bỏ qua các bản ghi này.")
                    fund_df = fund_df.dropna(subset=['date'])
            except Exception as e:
                print(f"⚠️ Lỗi xử lý ngày tháng: {str(e)}")
                ax4.text(0.5, 0.5, 'Lỗi xử lý ngày tháng', ha='center', va='center', fontsize=12)
                ax4.set_title('Xu Hướng Đầu Tư Theo Thời Gian')
                plt.tight_layout()
                plt.show()
                return

            fund_df['amount_display'] = fund_df.apply(
                lambda row: self.convert_currency(row['amount'], row['currency'], display_currency),
                axis=1
            )

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

            print(f"💰 Tổng giá trị quỹ đầu tư: {self.format_currency(total_fund_value, display_currency)}")
            print(f"📊 Số loại quỹ đang đầu tư: {len(fund_summary)}/3")
            print("-"*80)

            for fund_type in sorted(fund_summary.keys(), key=lambda x: fund_summary[x]['risk_level']):
                data = fund_summary[fund_type]
                percentage = (data['value'] / total_fund_value) * 100

                print(f"\n🏛️ {fund_type.upper()}")
                print(f" 💰 Giá trị: {self.format_currency(data['value'], display_currency)} ({percentage:.1f}%)")
                print(f" 📊 Số giao dịch: {data['count']}")
                print(f" ⚠️ Mức rủi ro: {data['risk_level']}/5 ({'Thấp' if data['risk_level'] <= 2 else 'Trung bình' if data['risk_level'] <= 3 else 'Cao'})")
                print(f" 📈 Lợi nhuận kỳ vọng: {data['expected_return']:.1f}%/năm")
                print(f" 📉 Độ biến động: {data['volatility']:.1f}%")

                if fund_type == 'Quỹ trái phiếu':
                    print(f" 💡 Đặc điểm: An toàn, ổn định, phù hợp bảo toàn vốn")
                    if percentage > 50:
                        print(f" 🟡 Cảnh báo: Tỷ trọng cao, có thể hạn chế tăng trưởng")
                elif fund_type == 'Quỹ cân bằng':
                    print(f" 💡 Đặc điểm: Cân bằng rủi ro-lợi nhuận, linh hoạt")
                    if percentage > 60:
                        print(f" 🟡 Gợi ý: Có thể đa dạng thêm sang các loại khác")
                elif fund_type == 'Quỹ cổ phiếu':
                    print(f" 💡 Đặc điểm: Tiềm năng tăng trưởng cao, biến động lớn")
                    if percentage > 40:
                        print(f" 🔴 Cảnh báo: Rủi ro cao, cần cân nhắc cân bằng")

            print(f"\n" + "="*80)
            print("📊 PHÂN TÍCH PORTFOLIO QUỸ TỔNG THỂ")
            print("="*80)

            weighted_risk = sum(fund_summary[name]['risk_level'] * fund_summary[name]['value']
                               for name in fund_names) / total_fund_value
            weighted_return = sum(fund_summary[name]['expected_return'] * fund_summary[name]['value']
                                 for name in fund_names) / total_fund_value
            weighted_volatility = sum(fund_summary[name]['volatility'] * fund_summary[name]['value']
                                     for name in fund_names) / total_fund_value

            print(f"⚡ Điểm rủi ro trung bình: {weighted_risk:.2f}/5")
            print(f"📈 Lợi nhuận kỳ vọng trung bình: {weighted_return:.1f}%/năm")
            print(f"📊 Độ biến động trung bình: {weighted_volatility:.1f}%")

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

            print(f"\n💡 KHUYẾN NGHỊ PHÂN BỔ QUỸ TỐI ƯU:")
            if weighted_risk < 2.0:
                print(" 🔹 Quỹ trái phiếu: 30-50% (hiện tại cần giảm)")
                print(" 🔹 Quỹ cân bằng: 30-40% (có thể tăng)")
                print(" 🔹 Quỹ cổ phiếu: 20-30% (nên tăng đáng kể)")
            elif weighted_risk < 3.0:
                print(" 🔹 Quỹ trái phiếu: 25-35% (tùy điều chỉnh)")
                print(" 🔹 Quỹ cân bằng: 35-45% (duy trì)")
                print(" 🔹 Quỹ cổ phiếu: 20-35% (có thể tăng nhẹ)")
            else:
                print(" 🔹 Quỹ trái phiếu: 20-30% (cần tăng)")
                print(" 🔹 Quỹ cân bằng: 30-40% (duy trì)")
                print(" 🔹 Quỹ cổ phiếu: 25-35% (cần giảm)")

            missing_funds = [fund for fund in fund_types if fund not in fund_summary]
            if missing_funds:
                print(f"\n⚠️ THIẾU HỤT LOẠI QUỸ:")
                for missing_fund in missing_funds:
                    risk_info = self.asset_risk_levels[missing_fund]
                    print(f" 🔸 {missing_fund}: Rủi ro {risk_info['risk']}/5, Lợi nhuận {risk_info['expected_return']}%")
                    if missing_fund == 'Quỹ trái phiếu':
                        print(" → Giúp ổn định danh mục, giảm rủi ro")
                    elif missing_fund == 'Quỹ cân bằng':
                        print(" → Cân bằng giữa an toàn và tăng trưởng")
                    elif missing_fund == 'Quỹ cổ phiếu':
                        print(" → Tăng tiềm năng lợi nhuận dài hạn")

            print(f"\n📊 DỰ BÁO LỢI NHUẬN VÀ RỦI RO:")
            expected_annual_return = total_fund_value * weighted_return / 100
            expected_volatility_range = total_fund_value * weighted_volatility / 100

            print(f" 📈 Lợi nhuận dự kiến/năm: {self.format_currency(expected_annual_return, display_currency)}")
            print(f" 📊 Biên độ dao động: ±{self.format_currency(expected_volatility_range, display_currency)}")
            print(f" 🎯 Kịch bản tốt: {self.format_currency(total_fund_value + expected_annual_return + expected_volatility_range, display_currency)}")
            print(f" ⚠️ Kịch bản xấu: {self.format_currency(total_fund_value + expected_annual_return - expected_volatility_range, display_currency)}")

            total_portfolio_value = sum(self.convert_currency(inv['amount'], inv['currency'], display_currency)
                                       for inv in self.investment_data)
            fund_percentage_in_portfolio = (total_fund_value / total_portfolio_value) * 100

            print(f"\n🔍 VỊ TRÍ TRONG TỔNG DANH MỤC:")
            print(f" 📊 Tỷ trọng quỹ trong tổng danh mục: {fund_percentage_in_portfolio:.1f}%")

            if fund_percentage_in_portfolio < 30:
                print(" 💡 Tỷ trọng quỹ thấp - có thể tăng để đa dạng hóa")
            elif fund_percentage_in_portfolio > 70:
                print(" ⚠️ Tỷ trọng quỹ cao - cân nhắc đa dạng sang tài sản khác")
            else:
                print(" ✅ Tỷ trọng quỹ hợp lý trong tổng danh mục")

    def import_investment_data(self, button):
        # Giữ nguyên như code bạn cung cấp
        try:
            file_path = self.import_file_path.value
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} không tồn tại!")
            
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            required_columns = ['date', 'type', 'description', 'amount']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"File CSV thiếu một hoặc nhiều cột: {required_columns}")
            
            if df['amount'].isnull().any() or not pd.to_numeric(df['amount'], errors='coerce').notnull().all():
                raise ValueError("Cột 'amount' chứa giá trị không phải số hoặc rỗng!")
            
            self.investment_data = []

            for _, row in df.iterrows():
                try:
                    pd.to_datetime(row['date'], errors='raise')
                    investment_type = self.investment_mapping.get(row['type'], 'Khác')
                    self.investment_data.append({
                        'date': pd.to_datetime(row['date']).date(),
                        'type': investment_type,
                        'description': row['description'],
                        'amount': float(row['amount']),
                        'currency': row.get('currency', 'VND'),
                        'original_type': row['type']
                    })
                except ValueError as e:
                    print(f"⚠️ Bỏ qua bản ghi với ngày không hợp lệ: {row['date']}")
                    continue

            self.update_asset_dropdown()

            with self.output:
                clear_output()
                print(f"✅ Đã import {len(self.investment_data)} bản ghi đầu tư từ {file_path}")
                print("📊 Phân loại đầu tư:")
                
                type_summary = {}
                for inv in self.investment_data:
                    inv_type = inv['type']
                    amount_vnd = self.convert_currency(inv['amount'], inv['currency'], 'VND')
                    type_summary[inv_type] = type_summary.get(inv_type, 0) + amount_vnd
                
                for inv_type, total in type_summary.items():
                    print(f" • {inv_type}: {total:,.0f}đ")
        
        except FileNotFoundError as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi: {str(e)}")
        except ValueError as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi định dạng file: {str(e)}")
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi không xác định khi import dữ liệu: {str(e)}")

    def update_asset_dropdown(self):
        # Giữ nguyên như code bạn cung cấp
        options = [('-- Chọn tài sản --', '')]
        assets = set(f"{inv['type']} - {inv['description']}" for inv in self.investment_data)
        for asset in sorted(assets):
            options.append((asset, asset))
        self.asset_dropdown.options = options

    def update_current_price(self, button):
        # Giữ nguyên như code bạn cung cấp
        if not self.asset_dropdown.value:
            with self.output:
                clear_output()
                print("❌ Vui lòng chọn tài sản!")
            return
        if self.current_price_input.value <= 0:
            with self.output:
                clear_output()
                print("❌ Giá hiện tại phải lớn hơn 0!")
            return

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

    def save_settings(self):
        """Lưu cài đặt tỷ giá"""
        try:
            if not os.access(os.path.dirname(self.data_files['settings']) or '.', os.W_OK):
                raise PermissionError("Không có quyền ghi vào thư mục chứa file settings!")
            
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
            if not os.access(os.path.dirname(self.data_files['investment_prices']) or '.', os.W_OK):
                raise PermissionError("Không có quyền ghi vào thư mục chứa file prices!")
                
            if self.current_prices:
                prices_data = [
                    {
                        'asset': asset_key,
                        'price': price_info['price'],
                        'currency': price_info['currency'],
                        'date': price_info['date']
                    }
                    for asset_key, price_info in self.current_prices.items()
                ]
                prices_df = pd.DataFrame(prices_data)
                prices_df.to_csv(self.data_files['investment_prices'], index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"Lỗi khi lưu giá: {str(e)}")

    def save_target_allocation(self):
        """Lưu tỷ lệ phân bổ mục tiêu"""
        try:
            if not os.access(os.path.dirname(self.data_files['target_allocation']) or '.', os.W_OK):
                raise PermissionError("Không có quyền ghi vào thư mục chứa file allocation!")
                
            if self.target_allocation:
                allocation_data = [
                    {
                        'asset_type': asset_type,
                        'target_percent': target_pct
                    }
                    for asset_type, target_pct in self.target_allocation.items()
                ]
                allocation_df = pd.DataFrame(allocation_data)
                allocation_df.to_csv(self.data_files['target_allocation'], index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"Lỗi khi lưu phân bổ mục tiêu: {str(e)}")

    def load_data(self):
        # Giữ nguyên như code bạn cung cấp
        try:
            if os.path.exists(self.data_files['settings']):
                df = pd.read_csv(self.data_files['settings'], encoding='utf-8-sig')
                if 'parameter' in df.columns and 'value' in df.columns:
                    for _, row in df.iterrows():
                        if row['parameter'] == 'exchange_rate':
                            self.exchange_rate = float(row['value'])
                            self.exchange_rate_input.value = self.exchange_rate
                    print(f"✅ Đã load cài đặt tỷ giá: {self.exchange_rate}")
                else:
                    print("⚠️ File cài đặt không đúng định dạng!")
            else:
                print("📝 Chưa có file cài đặt - sử dụng mặc định")
        except Exception as e:
            print(f"⚠️ Lỗi khi load cài đặt: {str(e)}")

        try:
            if os.path.exists(self.data_files['investment_prices']):
                df = pd.read_csv(self.data_files['investment_prices'], encoding='utf-8-sig')
                self.current_prices = {}
                for _, row in df.iterrows():
                    try:
                        self.current_prices[row['asset']] = {
                            'price': float(row['price']),
                            'currency': row['currency'],
                            'date': pd.to_datetime(row['date']).date()
                        }
                    except ValueError as e:
                        print(f"⚠️ Bỏ qua bản ghi giá với ngày không hợp lệ: {row['date']}")
                        continue
                print(f"✅ Đã load {len(self.current_prices)} giá tài sản")
            else:
                print("📝 Chưa có file giá tài sản")
        except Exception as e:
            print(f"⚠️ Lỗi khi load giá: {str(e)}")

        try:
            if os.path.exists(self.data_files['target_allocation']):
                df = pd.read_csv(self.data_files['target_allocation'], encoding='utf-8-sig')
                self.target_allocation = {}
                for _, row in df.iterrows():
                    self.target_allocation[row['asset_type']] = float(row['target_percent'])
                print(f"✅ Đã load tỷ lệ phân bổ mục tiêu cho {len(self.target_allocation)} loại tài sản")
            else:
                print("📝 Chưa có file phân bổ mục tiêu")
        except Exception as e:
            print(f"⚠️ Lỗi khi load phân bổ mục tiêu: {str(e)}")

    def save_all_data(self, button):
        # Giữ nguyên như code bạn cung cấp
        try:
            self.save_settings()
            self.save_current_prices()
            self.save_target_allocation()
            
            with self.output:
                clear_output()
                print("✅ Đã lưu tất cả dữ liệu!")
                print("📁 Các file được tạo:")
                print(" • investment_settings.csv - Cài đặt tỷ giá")
                print(" • investment_current_prices.csv - Giá hiện tại")
                print(" • target_allocation.csv - Phân bổ mục tiêu")
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi lưu dữ liệu: {str(e)}")

    def load_all_data(self, button):
        # Giữ nguyên như code bạn cung cấp
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
        # Giữ nguyên như code bạn cung cấp
        try:
            self.investment_data = []
            self.current_prices = {}
            self.target_allocation = {}
            self.exchange_rate = 18.0
            
            self.exchange_rate_input.value = 18.0
            self.update_asset_dropdown()
            
            for filename in self.data_files.values():
                if os.path.exists(filename):
                    os.remove(filename)
            
            with self.output:
                clear_output()
                print("⚠️ Đã xóa toàn bộ dữ liệu và file!")
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

    def show_rebalance_recommendation(self, button):
        """Đưa ra khuyến nghị cân bằng lại danh mục"""
        if not self.investment_data or not self.target_allocation:
            with self.output:
                clear_output()
                print("❌ Cần có dữ liệu đầu tư và tỷ lệ phân bổ mục tiêu!")
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
            
            print("="*80)
            print("🔄 KHUYẾN NGHỊ CÂN BẰNG LẠI DANH MỤC ĐẦU TƯ")
            print("="*80)
            print(f"💰 Tổng giá trị danh mục: {self.format_currency(total_value, display_currency)}")
            print("-"*80)
            
            # Calculate target values and recommendations
            recommendations = []
            
            for asset_type, target_pct in self.target_allocation.items():
                target_value = (target_pct / 100) * total_value
                current_value = current_allocation.get(asset_type, 0)
                difference = target_value - current_value
                
                recommendations.append({
                    'type': asset_type,
                    'current': current_value,
                    'target': target_value,
                    'difference': difference,
                    'action': 'Mua thêm' if difference > 0 else 'Bán bớt'
                })
            
            # Sort by absolute difference
            recommendations.sort(key=lambda x: abs(x['difference']), reverse=True)
            
            # Create visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Current vs Target values
            asset_types = [r['type'] for r in recommendations]
            current_values = [r['current'] for r in recommendations]
            target_values = [r['target'] for r in recommendations]
            
            x = np.arange(len(asset_types))
            width = 0.35
            
            ax1.bar(x - width/2, current_values, width, label='Hiện tại', alpha=0.8)
            ax1.bar(x + width/2, target_values, width, label='Mục tiêu', alpha=0.8)
            ax1.set_title('Giá Trị Hiện Tại vs Mục Tiêu')
            ax1.set_ylabel(f'Giá trị ({display_currency})')
            ax1.set_xticks(x)
            ax1.set_xticklabels(asset_types, rotation=45)
            ax1.legend()
            
            # Rebalance actions
            differences = [r['difference'] for r in recommendations]
            colors = ['green' if x > 0 else 'red' for x in differences]
            
            ax2.barh(asset_types, differences, color=colors, alpha=0.7)
            ax2.set_title('Hành Động Cần Thực Hiện')
            ax2.set_xlabel(f'Số tiền cần điều chỉnh ({display_currency})')
            ax2.axvline(x=0, color='black', linestyle='-', alpha=0.5)
            
            plt.tight_layout()
            plt.show()
            
            # Print detailed recommendations
            print("\n🎯 KHUYẾN NGHỊ CHI TIẾT:")
            print("-"*80)
            
            total_buy = 0
            total_sell = 0
            
            for rec in recommendations:
                if abs(rec['difference']) < total_value * 0.01:  # Less than 1% of portfolio
                    continue
                
                print(f"\n📊 {rec['type']}:")
                print(f"   💰 Giá trị hiện tại: {self.format_currency(rec['current'], display_currency)}")
                print(f"   🎯 Giá trị mục tiêu:  {self.format_currency(rec['target'], display_currency)}")
                
                if rec['difference'] > 0:
                    print(f"   🟢 {rec['action']}: {self.format_currency(rec['difference'], display_currency)}")
                    total_buy += rec['difference']
                    
                    # Suggest specific actions
                    if rec['type'] == 'Cổ phiếu':
                        print(f"      💡 Gợi ý: Mua thêm cổ phiếu blue-chip hoặc ETF")
                    elif rec['type'] == 'Quỹ':
                        print(f"      💡 Gợi ý: Đầu tư thêm vào quỹ đang có hiệu suất tốt")
                    elif rec['type'] == 'Tiền gửi':
                        print(f"      💡 Gợi ý: Gửi tiết kiệm kỳ hạn có lãi suất cao")
                else:
                    print(f"   🔴 {rec['action']}: {self.format_currency(abs(rec['difference']), display_currency)}")
                    total_sell += abs(rec['difference'])
                    
                    # Suggest specific actions
                    if rec['type'] == 'Cổ phiếu':
                        print(f"      💡 Gợi ý: Bán cổ phiếu đã lãi hoặc cắt lỗ")
                    elif rec['type'] == 'Quỹ':
                        print(f"      💡 Gợi ý: Rút một phần từ quỹ có hiệu suất thấp")
            
            print("\n" + "="*80)
            print("📋 TỔNG KẾT HÀNH ĐỘNG:")
            print(f"🟢 Tổng số tiền cần mua thêm: {self.format_currency(total_buy, display_currency)}")
            print(f"🔴 Tổng số tiền cần bán bớt:  {self.format_currency(total_sell, display_currency)}")
            
            if abs(total_buy - total_sell) < total_value * 0.001:
                print("✅ Danh mục sẽ được cân bằng hoàn hảo!")
            else:
                net_cash_needed = total_buy - total_sell
                if net_cash_needed > 0:
                    print(f"💰 Cần thêm tiền mặt: {self.format_currency(net_cash_needed, display_currency)}")
                else:
                    print(f"💸 Sẽ có tiền mặt dư: {self.format_currency(abs(net_cash_needed), display_currency)}")
            
            # Timeline recommendation
            print("\n⏰ KHUYẾN NGHỊ THỜI GIAN:")
            print("   • Thực hiện cân bằng lại từ từ trong 2-4 tuần")
            print("   • Ưu tiên điều chỉnh các tài sản có độ lệch lớn nhất trước")
            print("   • Tận dụng thời điểm thị trường biến động để mua/bán")
            print("   • Xem xét chi phí giao dịch khi thực hiện")

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_performance_analysis(self, button):
        """Phân tích hiệu suất danh mục đầu tư - Phiên bản cải tiến với tính toán annualized return chính xác"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        display_currency = self.currency_display.value
        
        with self.output:
            clear_output()
            print("="*100)
            print("📊 PHÂN TÍCH HIỆU SUẤT DANH MỤC CHI TIẾT")
            print("="*100)
            
            # Prepare data
            df = pd.DataFrame(self.investment_data)
            try:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.dropna(subset=['date'])
                if df.empty:
                    print("❌ Không có dữ liệu hợp lệ để phân tích hiệu suất!")
                    return
            except Exception as e:
                print(f"⚠️ Lỗi xử lý ngày tháng: {str(e)}")
                return
            
            df['amount_display'] = df.apply(
                lambda row: self.convert_currency(row['amount'], row['currency'], display_currency),
                axis=1
            )
            
            # Tạo unique identifier cho từng khoản đầu tư
            df['investment_id'] = df['type'] + ' - ' + df['description']
            
            # Phân tích hiệu suất từng khoản đầu tư riêng lẻ
            individual_performance = {}
            group_performance = {}
            
            # Ngày hiện tại để tính toán
            current_date = datetime.now()
            
            # Tính hiệu suất cho từng khoản đầu tư riêng lẻ
            for investment_id in df['investment_id'].unique():
                inv_data = df[df['investment_id'] == investment_id].copy()
                inv_data = inv_data.sort_values('date')
                
                # Tính cumulative cash flow (dòng tiền tích lũy)
                inv_data['cumulative_cashflow'] = inv_data['amount_display'].cumsum()
                
                # Tính hiệu suất nếu có đủ dữ liệu
                if len(inv_data) > 0:
                    asset_type = inv_data['type'].iloc[0]
                    description = inv_data['description'].iloc[0]
                    
                    # Tính tổng mua, tổng bán, và holding hiện tại
                    total_bought = inv_data[inv_data['amount_display'] > 0]['amount_display'].sum()
                    total_sold = abs(inv_data[inv_data['amount_display'] < 0]['amount_display'].sum())
                    net_cashflow = total_bought - total_sold  # Tiền còn đầu tư thực tế
                    current_holding_value = inv_data['cumulative_cashflow'].iloc[-1]  # Giá trị holding hiện tại
                    
                    # Lấy giá hiện tại nếu có để tính market value
                    current_price_info = self.current_prices.get(investment_id, None)
                    market_value = current_holding_value  # Mặc định bằng cost basis
                    
                    if current_price_info and current_holding_value != 0:
                        market_price_or_value = self.convert_currency(
                            current_price_info['price'], 
                            current_price_info['currency'], 
                            display_currency
                        )
                        
                        # Kiểm tra loại giá được chỉ định
                        price_type = current_price_info.get('type', 'total_value')  # Mặc định là total value
                        
                        if price_type == 'total_value':
                            # Đây là tổng market value của toàn bộ holding
                            market_value = market_price_or_value
                        else:
                            # price_type == 'per_unit': Đây là giá per unit
                            buy_transactions = inv_data[inv_data['amount_display'] > 0]
                            if len(buy_transactions) > 0:
                                # Estimate total quantity purchased
                                # Giả định: mỗi giao dịch mua 1 unit với giá bằng amount
                                total_units_bought = len(buy_transactions)
                                
                                # Estimate sold units (nếu có)
                                sell_transactions = inv_data[inv_data['amount_display'] < 0]
                                total_units_sold = len(sell_transactions)
                                
                                # Current units holding
                                current_units = total_units_bought - total_units_sold
                                
                                if current_units > 0:
                                    market_value = current_units * market_price_or_value
                                else:
                                    market_value = 0
                            else:
                                # Fallback: treat as total market value
                                market_value = market_price_or_value
                    
                    # Nếu đã bán hết (current_holding_value <= 0), tính dựa trên realized gain/loss
                    if current_holding_value <= 0:
                        # Đã bán hết, tính realized return
                        realized_gain = total_sold - total_bought
                        current_value = 0
                        absolute_gain = realized_gain
                    else:
                        # Còn đang giữ, tính unrealized gain/loss
                        current_value = market_value
                        absolute_gain = current_value - current_holding_value
                    
                    # Tính ROI dựa trên net investment
                    net_invested = abs(net_cashflow) if net_cashflow != 0 else total_bought
                    
                    # Tính ROI
                    if net_invested > 0:
                        if current_holding_value <= 0:
                            # Đã bán hết - tính ROI dựa trên realized gain
                            roi = (absolute_gain / total_bought) * 100
                        else:
                            # Còn đang giữ - tính ROI dựa trên unrealized gain
                            roi = (absolute_gain / abs(current_holding_value)) * 100
                    else:
                        roi = 0
                    
                    # ===== TÍNH ANNUALIZED RETURN CẢI TIẾN =====
                    start_date = inv_data['date'].iloc[0]
                    
                    # Nếu có giá hiện tại, sử dụng ngày nhập giá làm end_date
                    if current_price_info and 'date' in current_price_info:
                        try:
                            price_date = pd.to_datetime(current_price_info['date'], errors='coerce')
                            if pd.notna(price_date):
                                end_date = price_date
                            else:
                                end_date = current_date
                        except:
                            end_date = current_date
                    else:
                        # Nếu không có giá hiện tại hoặc đã bán hết, dùng ngày giao dịch cuối
                        if current_holding_value <= 0:
                            end_date = inv_data['date'].iloc[-1]  # Ngày bán cuối
                        else:
                            end_date = current_date  # Ngày hiện tại cho khoản đang giữ
                    
                    # Tính số tháng đầu tư
                    total_months = max((end_date - start_date).days / 30.44, 1)  # 30.44 = số ngày trung bình 1 tháng
                    years = total_months / 12
                    
                    # Tính annualized return dựa trên công thức compound annual growth rate (CAGR)
                    if years > 0 and net_invested > 0:
                        if current_holding_value <= 0:
                            # Đã bán hết - tính CAGR dựa trên total return realized
                            initial_value = total_bought
                            final_value = total_sold
                        else:
                            # Còn đang giữ - tính CAGR dựa trên current market value
                            initial_value = abs(current_holding_value)  # Cost basis
                            final_value = current_value  # Current market value
                        
                        if initial_value > 0 and final_value > 0:
                            # CAGR = (Final Value / Initial Value)^(1/years) - 1
                            annualized_return = (((final_value / initial_value) ** (1/years)) - 1) * 100
                        elif final_value == 0:
                            # Mất hết vốn
                            annualized_return = -100
                        else:
                            annualized_return = 0
                    else:
                        annualized_return = 0
                    
                    # Tính monthly return trung bình (để tham khảo)
                    if total_months > 0 and net_invested > 0:
                        total_return_ratio = (absolute_gain / net_invested) if net_invested > 0 else 0
                        monthly_return_avg = (total_return_ratio / total_months) * 100
                        # Ước lượng annualized từ monthly (compound)
                        if monthly_return_avg != 0:
                            annualized_from_monthly = (((1 + monthly_return_avg/100) ** 12) - 1) * 100
                        else:
                            annualized_from_monthly = 0
                    else:
                        monthly_return_avg = 0
                        annualized_from_monthly = 0
                    
                    # Status của investment
                    if current_holding_value <= 0:
                        status = "Đã bán"
                        display_current_value = 0
                    else:
                        status = "Đang giữ"
                        display_current_value = current_value
                    
                    individual_performance[investment_id] = {
                        'type': asset_type,
                        'description': description,
                        'total_bought': total_bought,
                        'total_sold': total_sold,
                        'net_cashflow': net_cashflow,
                        'current_holding_value': current_holding_value,
                        'market_value': market_value,
                        'current_value': display_current_value,
                        'absolute_gain': absolute_gain,
                        'roi_percent': roi,
                        'annualized_return': annualized_return,
                        'monthly_return_avg': monthly_return_avg,
                        'annualized_from_monthly': annualized_from_monthly,
                        'investment_period_years': years,
                        'investment_period_months': total_months,
                        'transactions': len(inv_data),
                        'first_date': start_date,
                        'last_date': end_date,
                        'status': status,
                        'has_current_price': current_price_info is not None,
                        'price_date': end_date if current_price_info else None
                    }
            
            # Tính hiệu suất trung bình cho từng nhóm
            type_groups = {}
            for inv_id, perf in individual_performance.items():
                asset_type = perf['type']
                if asset_type not in type_groups:
                    type_groups[asset_type] = []
                type_groups[asset_type].append(perf)
            
            for asset_type, performances in type_groups.items():
                total_bought = sum(p['total_bought'] for p in performances)
                total_sold = sum(p['total_sold'] for p in performances)
                total_current = sum(p['current_value'] for p in performances)
                net_invested = total_bought - total_sold
                
                # Weighted average ROI và annualized return dựa trên investment amount
                weighted_roi = 0
                weighted_annualized = 0
                weighted_monthly = 0
                total_weight = 0
                
                for perf in performances:
                    # Sử dụng total_bought làm trọng số cho tính toán
                    weight = perf['total_bought']
                    if weight > 0:
                        weighted_roi += perf['roi_percent'] * weight
                        weighted_annualized += perf['annualized_return'] * weight
                        weighted_monthly += perf['monthly_return_avg'] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    weighted_roi /= total_weight
                    weighted_annualized /= total_weight
                    weighted_monthly /= total_weight
                
                group_performance[asset_type] = {
                    'count': len(performances),
                    'total_bought': total_bought,
                    'total_sold': total_sold,
                    'net_invested': net_invested,
                    'total_current': total_current,
                    'total_gain': total_current - abs(net_invested) if net_invested != 0 else total_current - total_bought,
                    'weighted_roi': weighted_roi,
                    'weighted_annualized': weighted_annualized,
                    'weighted_monthly': weighted_monthly,
                    'best_performer': max(performances, key=lambda x: x['roi_percent']),
                    'worst_performer': min(performances, key=lambda x: x['roi_percent']),
                    'active_positions': len([p for p in performances if p['status'] == 'Đang giữ']),
                    'closed_positions': len([p for p in performances if p['status'] == 'Đã bán'])
                }
            
            # Create visualizations
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
            
            # 1. Individual Investment Performance
            if individual_performance:
                sorted_investments = sorted(individual_performance.items(), 
                                          key=lambda x: x[1]['roi_percent'], reverse=True)
                
                investment_names = [inv_id.split(' - ')[1][:15] + "..." if len(inv_id.split(' - ')[1]) > 15 
                                   else inv_id.split(' - ')[1] for inv_id, _ in sorted_investments]
                roi_values = [perf['roi_percent'] for _, perf in sorted_investments]
                colors = ['green' if roi > 0 else 'red' for roi in roi_values]
                
                bars = ax1.barh(investment_names, roi_values, color=colors, alpha=0.7)
                ax1.set_xlabel('ROI (%)')
                ax1.set_title('Hiệu Suất Từng Khoản Đầu Tư (ROI %)')
                ax1.grid(True, alpha=0.3)
                
                # Add value labels
                for i, v in enumerate(roi_values):
                    ax1.text(v + (1 if v >= 0 else -1), i, f'{v:.1f}%', 
                            va='center', ha='left' if v >= 0 else 'right')
            
            # 2. Group Performance Comparison
            if group_performance:
                groups = list(group_performance.keys())
                group_rois = [group_performance[g]['weighted_roi'] for g in groups]
                group_annualized = [group_performance[g]['weighted_annualized'] for g in groups]
                
                x = np.arange(len(groups))
                width = 0.35
                
                bars1 = ax2.bar(x - width/2, group_rois, width, label='ROI (%)', alpha=0.8, color='skyblue')
                bars2 = ax2.bar(x + width/2, group_annualized, width, label='Annualized (%)', alpha=0.8, color='lightcoral')
                
                ax2.set_xlabel('Loại Tài Sản')
                ax2.set_ylabel('Tỷ lệ (%)')
                ax2.set_title('So Sánh Hiệu Suất Theo Nhóm Tài Sản')
                ax2.set_xticks(x)
                ax2.set_xticklabels(groups, rotation=45, ha='right')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                
                # Add value labels
                for bars in [bars1, bars2]:
                    for bar in bars:
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
            
            # 3. Investment Value Distribution
            if individual_performance:
                values = [perf['current_value'] for perf in individual_performance.values()]
                types = [perf['type'] for perf in individual_performance.values()]
                
                type_sums = {}
                for t, v in zip(types, values):
                    type_sums[t] = type_sums.get(t, 0) + v
                
                colors = plt.cm.Set3(np.linspace(0, 1, len(type_sums)))
                ax3.pie(type_sums.values(), labels=type_sums.keys(), autopct='%1.1f%%', 
                       colors=colors, startangle=90)
                ax3.set_title('Phân Bổ Giá Trị Hiện Tại Theo Nhóm')
            
            # 4. Risk-Return Scatter Plot
            if individual_performance:
                returns = [perf['annualized_return'] for perf in individual_performance.values()]
                net_investments = [abs(perf['net_cashflow']) if perf['net_cashflow'] != 0 else perf['total_bought'] 
                                  for perf in individual_performance.values()]
                types = [perf['type'] for perf in individual_performance.values()]
                
                # Create color map for types
                unique_types = list(set(types))
                colors = plt.cm.tab10(np.linspace(0, 1, len(unique_types)))
                type_color_map = dict(zip(unique_types, colors))
                point_colors = [type_color_map[t] for t in types]
                
                scatter = ax4.scatter(net_investments, returns, c=point_colors, 
                                    s=[inv/max(net_investments)*300 + 50 for inv in net_investments], 
                                    alpha=0.6)
                
                ax4.set_xlabel(f'Số Tiền Đầu Tư Thực ({display_currency})')
                ax4.set_ylabel('Lợi Nhuận Hàng Năm (%)')
                ax4.set_title('Ma Trận Rủi Ro - Lợi Nhuận')
                ax4.grid(True, alpha=0.3)
                
                # Add legend for types
                for i, asset_type in enumerate(unique_types):
                    ax4.scatter([], [], c=[colors[i]], label=asset_type, s=100)
                ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            plt.show()
            
            # Detailed performance report
            print(f"\n{'='*100}")
            print("📊 BÁO CÁO HIỆU SUẤT CHI TIẾT TỪNG KHOẢN ĐẦU TƯ")
            print(f"{'='*100}")
            
            # Individual investments report
            for asset_type, performances in type_groups.items():
                print(f"\n🏛️  {asset_type.upper()}")
                print("-" * 110)
                print(f"{'Mã/Tên':<25} {'Mua':<12} {'Bán':<12} {'Hiện tại':<12} {'Lãi/Lỗ':<10} {'ROI%':<8} {'Tháng%':<8} {'Năm%':<8} {'Trạng thái'}")
                print("-" * 110)
                
                for perf in sorted(performances, key=lambda x: x['roi_percent'], reverse=True):
                    gain_loss = f"{perf['absolute_gain']:+,.0f}"
                    status_icon = "🟢" if perf['status'] == 'Đang giữ' else "🔴"
                    
                    print(f"{perf['description'][:24]:<25} "
                          f"{self.format_currency(perf['total_bought'], display_currency):<12} "
                          f"{self.format_currency(perf['total_sold'], display_currency):<12} "
                          f"{self.format_currency(perf['current_value'], display_currency):<12} "
                          f"{gain_loss:<10} "
                          f"{perf['roi_percent']:>6.1f}% "
                          f"{perf['monthly_return_avg']:>6.1f}% "
                          f"{perf['annualized_return']:>6.1f}% "
                          f"{status_icon} {perf['status']}")
                    
                    # Thêm thông tin chi tiết về thời gian đầu tư
                    period_info = f"Kỳ đầu tư: {perf['investment_period_months']:.1f} tháng"
                    if perf['price_date']:
                        price_date_str = perf['price_date'].strftime('%Y-%m-%d')
                        period_info += f" (đến {price_date_str})"
                    
                    # Thêm thông tin chi tiết cho các khoản có nhiều giao dịch
                    if perf['transactions'] > 2:
                        price_info = self.current_prices.get(investment_id, {})
                        price_type_desc = ""
                        if price_info:
                            if price_info.get('type') == 'total_value':
                                price_type_desc = f"(Giá thị trường: {self.format_currency(price_info['price'], price_info['currency'])} - Tổng giá trị)"
                            else:
                                price_type_desc = f"(Giá thị trường: {self.format_currency(price_info['price'], price_info['currency'])} - Per unit)"
                        
                        print(f"{'  └─ ' + str(perf['transactions']) + ' giao dịch':<25} "
                              f"{'Net cost: ' + self.format_currency(perf['net_cashflow'], display_currency):<25} "
                              f"{period_info}")
                        if price_type_desc:
                            print(f"{'    ' + price_type_desc}")
                    else:
                        print(f"{'  └─ ' + period_info}")
                        if perf['has_current_price']:
                            price_info = self.current_prices.get(investment_id, {})
                            if price_info.get('type') == 'total_value':
                                price_type_desc = "Tổng giá trị"
                            else:
                                price_type_desc = "Per unit"
                            print(f"{'    Có giá thị trường':<50} ({price_type_desc})")
            
            # Group summary
            print(f"\n{'='*100}")
            print("📈 TỔNG KẾT HIỆU SUẤT THEO NHÓM")
            print(f"{'='*100}")
            print(f"{'Nhóm':<20} {'SL':<4} {'Đang giữ':<8} {'Tổng mua':<12} {'Tổng bán':<12} {'Hiện tại':<12} {'ROI%':<8} {'Tháng%':<8} {'Năm%':<8}")
            print("-" * 115)
            
            portfolio_total_bought = 0
            portfolio_total_sold = 0
            portfolio_total_current = 0
            
            for asset_type, group_data in group_performance.items():
                portfolio_total_bought += group_data['total_bought']
                portfolio_total_sold += group_data['total_sold']
                portfolio_total_current += group_data['total_current']
                
                print(f"{asset_type:<20} "
                      f"{group_data['count']:<4} "
                      f"{group_data['active_positions']:<8} "
                      f"{self.format_currency(group_data['total_bought'], display_currency):<12} "
                      f"{self.format_currency(group_data['total_sold'], display_currency):<12} "
                      f"{self.format_currency(group_data['total_current'], display_currency):<12} "
                      f"{group_data['weighted_roi']:>6.1f}% "
                      f"{group_data['weighted_monthly']:>6.1f}% "
                      f"{group_data['weighted_annualized']:>6.1f}%")
            
            print("-" * 115)
            portfolio_net_invested = portfolio_total_bought - portfolio_total_sold
            portfolio_total_gain = portfolio_total_current - abs(portfolio_net_invested)
            portfolio_roi = (portfolio_total_gain / portfolio_total_bought * 100) if portfolio_total_bought > 0 else 0
            
            print(f"{'TỔNG DANH MỤC':<20} "
                  f"{sum(len(performances) for performances in type_groups.values()):<4} "
                  f"{sum(g['active_positions'] for g in group_performance.values()):<8} "
                  f"{self.format_currency(portfolio_total_bought, display_currency):<12} "
                  f"{self.format_currency(portfolio_total_sold, display_currency):<12} "
                  f"{self.format_currency(portfolio_total_current, display_currency):<12} "
                  f"{portfolio_roi:>6.1f}% "
                  f"{'--':<8} "
                  f"{'--':<8}")
            
            # Performance insights
            print(f"\n💡 NHẬN XÉT & KHUYẾN NGHỊ:")
            
            if group_performance:
                best_group = max(group_performance.items(), key=lambda x: x[1]['weighted_roi'])
                worst_group = min(group_performance.items(), key=lambda x: x[1]['weighted_roi'])
                
                print(f"🏆 Nhóm hiệu suất tốt nhất: {best_group[0]} ({best_group[1]['weighted_roi']:.1f}% ROI, {best_group[1]['weighted_annualized']:.1f}% năm)")
                print(f"⚠️  Nhóm cần cải thiện: {worst_group[0]} ({worst_group[1]['weighted_roi']:.1f}% ROI, {worst_group[1]['weighted_annualized']:.1f}% năm)")
                
                # Individual best/worst performers
                all_performances = []
                for performances in type_groups.values():
                    all_performances.extend(performances)
                
                if all_performances:
                    best_individual = max(all_performances, key=lambda x: x['roi_percent'])
                    worst_individual = min(all_performances, key=lambda x: x['roi_percent'])
                    
                    print(f"🌟 Khoản đầu tư tốt nhất: {best_individual['description']} ({best_individual['roi_percent']:.1f}% ROI, {best_individual['annualized_return']:.1f}% năm)")
                    print(f"📉 Khoản cần xem xét: {worst_individual['description']} ({worst_individual['roi_percent']:.1f}% ROI, {worst_individual['annualized_return']:.1f}% năm)")
            
            # Risk warnings
            high_risk_investments = [perf for perf in individual_performance.values() 
                                   if perf['roi_percent'] < -10]
            
            if high_risk_investments:
                print(f"\n🚨 CẢNH BÁO RỦI RO:")
                print(f"   Có {len(high_risk_investments)} khoản đầu tư lỗ trên 10%:")
                for inv in high_risk_investments[:3]:  # Hiển thị top 3
                    print(f"   • {inv['description']}: {inv['roi_percent']:.1f}% ROI ({inv['annualized_return']:.1f}% năm)")
            
            # Diversification insights
            type_count = len(group_performance)
            if type_count < 3:
                print(f"\n📊 KHUYẾN NGHỊ ĐA DẠNG HÓA:")
                print(f"   Danh mục chỉ có {type_count} loại tài sản. Nên đa dạng hóa thêm để giảm rủi ro.")
            
            # Performance analysis insights
            print(f"\n📈 PHÂN TÍCH HIỆU SUẤT:")
            if individual_performance:
                annualized_returns = [perf['annualized_return'] for perf in individual_performance.values()]
                avg_annualized = np.mean(annualized_returns)
                volatility = np.std(annualized_returns)
                
                print(f"   • Lợi nhuận hàng năm trung bình: {avg_annualized:.1f}%")
                print(f"   • Độ biến động danh mục: {volatility:.1f}%")
                
                # Sharpe ratio estimate (assuming risk-free rate = 3%)
                risk_free_rate = 3.0
                if volatility > 0:
                    sharpe_ratio = (avg_annualized - risk_free_rate) / volatility
                    print(f"   • Chỉ số Sharpe ước tính: {sharpe_ratio:.2f} ({'Tốt' if sharpe_ratio > 1 else 'Khá' if sharpe_ratio > 0.5 else 'Cần cải thiện'})")
                
                # Time-weighted performance insights
                long_term_investments = [perf for perf in individual_performance.values() if perf['investment_period_months'] > 12]
                short_term_investments = [perf for perf in individual_performance.values() if perf['investment_period_months'] <= 12]
                
                if long_term_investments:
                    long_term_avg = np.mean([perf['annualized_return'] for perf in long_term_investments])
                    print(f"   • Hiệu suất đầu tư dài hạn (>1 năm): {long_term_avg:.1f}%/năm ({len(long_term_investments)} khoản)")
                
                if short_term_investments:
                    short_term_avg = np.mean([perf['annualized_return'] for perf in short_term_investments])
                    print(f"   • Hiệu suất đầu tư ngắn hạn (≤1 năm): {short_term_avg:.1f}%/năm ({len(short_term_investments)} khoản)")
            
            print(f"\n⏰ Cập nhật lần cuối: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📝 Lưu ý: Hiệu suất được tính từ ngày đầu tư đến ngày có giá hiện tại (hoặc ngày hiện tại nếu không có giá)")
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_risk_analysis(self, button):
        """Phân tích rủi ro danh mục"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        display_currency = self.currency_display.value
        
        with self.output:
            clear_output()
            
            # Calculate risk metrics
            portfolio_summary = {}
            total_value = 0
            
            for inv in self.investment_data:
                inv_type = inv['type']
                amount = self.convert_currency(inv['amount'], inv['currency'], display_currency)
                portfolio_summary[inv_type] = portfolio_summary.get(inv_type, 0) + amount
                total_value += amount
            
            print("="*70)
            print("⚠️ PHÂN TÍCH RỦI RO DANH MỤC ĐẦU TƯ")
            print("="*70)
            
            # Calculate portfolio risk score
            weighted_risk = 0
            for asset_type, value in portfolio_summary.items():
                weight = value / total_value
                # Sử dụng self.asset_risk_levels để lấy mức rủi ro
                risk = self.asset_risk_levels.get(asset_type, {'risk': 3})['risk']
                weighted_risk += weight * risk
            
            print(f"📊 Điểm rủi ro danh mục: {weighted_risk:.2f}/5.0")
            
            # Risk assessment
            if weighted_risk <= 2.0:
                risk_level = "🟢 Thấp"
                risk_desc = "Danh mục bảo thủ, ít biến động"
            elif weighted_risk <= 3.0:
                risk_level = "🟡 Vừa phải"
                risk_desc = "Danh mục cân bằng, rủi ro hợp lý"
            elif weighted_risk <= 4.0:
                risk_level = "🟠 Cao"
                risk_desc = "Danh mục tích cực, biến động lớn"
            else:
                risk_level = "🔴 Rất cao"
                risk_desc = "Danh mục mạo hiểm, rủi ro cao"
            
            print(f"📈 Mức độ rủi ro: {risk_level}")
            print(f"💭 Đánh giá: {risk_desc}")
            
            # Create risk visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Risk distribution pie chart
            risk_data = {}
            for asset_type, value in portfolio_summary.items():
                risk = self.asset_risk_levels.get(asset_type, {'risk': 3})['risk']
                risk_label = f"Rủi ro {risk}/5"
                risk_data[risk_label] = risk_data.get(risk_label, 0) + value
            
            ax1.pie(risk_data.values(), labels=risk_data.keys(), autopct='%1.1f%%', startangle=90)
            ax1.set_title('Phân Bố Rủi Ro Danh Mục')
            
            # 2. Asset allocation with risk colors
            asset_types = list(portfolio_summary.keys())
            asset_values = list(portfolio_summary.values())
            risk_colors = []
            
            for asset_type in asset_types:
                risk = self.asset_risk_levels.get(asset_type, {'risk': 3})['risk']
                if risk == 1:
                    risk_colors.append('green')
                elif risk == 2:
                    risk_colors.append('lightgreen')
                elif risk == 3:
                    risk_colors.append('yellow')
                elif risk == 4:
                    risk_colors.append('orange')
                else:
                    risk_colors.append('red')
            
            bars = ax2.bar(asset_types, asset_values, color=risk_colors, alpha=0.7)
            ax2.set_title('Phân Bổ Tài Sản Theo Mức Rủi Ro')
            ax2.set_ylabel(f'Giá trị ({display_currency})')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add risk level labels
            for bar, asset_type in zip(bars, asset_types):
                risk = self.asset_risk_levels.get(asset_type, {'risk': 3})['risk']
                ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(asset_values)*0.01,
                         f'R{risk}', ha='center', va='bottom', fontweight='bold')
            
            # 3. Risk concentration analysis
            risk_concentration = {}
            for asset_type, value in portfolio_summary.items():
                risk = self.asset_risk_levels.get(asset_type, {'risk': 3})['risk']
                risk_concentration[risk] = risk_concentration.get(risk, 0) + value
            
            risk_labels = [f'Rủi ro {r}' for r in sorted(risk_concentration.keys())]
            risk_values = [risk_concentration[r] for r in sorted(risk_concentration.keys())]
            
            ax3.barh(risk_labels, risk_values, color=['green', 'lightgreen', 'yellow', 'orange', 'red'][:len(risk_values)])
            ax3.set_title('Tập Trung Rủi Ro')
            ax3.set_xlabel(f'Giá trị ({display_currency})')
            
            # 4. Diversification score visualization
            num_assets = len(portfolio_summary)
            gini_coefficient = self.calculate_gini_coefficient(list(portfolio_summary.values()))
            
            diversification_metrics = {
                'Số loại tài sản': min(num_assets / 5 * 100, 100),
                'Phân bổ đều': (1 - gini_coefficient) * 100,
                'Đa dạng rủi ro': min(len(set(self.asset_risk_levels.get(t, {'risk': 3})['risk'] for t in portfolio_summary.keys())) / 5 * 100, 100)
            }
            
            metrics = list(diversification_metrics.keys())
            scores = list(diversification_metrics.values())
            
            bars = ax4.barh(metrics, scores, color=['blue', 'green', 'purple'])
            ax4.set_title('Điểm Đa Dạng Hóa')
            ax4.set_xlabel('Điểm (%)')
            ax4.set_xlim(0, 100)
            
            # Add score labels
            for i, score in enumerate(scores):
                ax4.text(score + 2, i, f'{score:.1f}%', va='center')
            
            plt.tight_layout()
            plt.show()
            
            # Detailed risk analysis
            print(f"\n📊 PHÂN TÍCH CHI TIẾT:")
            print(f"{'Loại tài sản':<20} {'Giá trị':<15} {'Tỷ trọng':<10} {'Rủi ro':<8} {'Đánh giá':<15}")
            print("-"*70)
            
            for asset_type, value in sorted(portfolio_summary.items(), key=lambda x: x[1], reverse=True):
                percentage = (value / total_value) * 100
                risk = self.asset_risk_levels.get(asset_type, {'risk': 3})['risk']
                
                if risk == 1:
                    risk_desc = "🟢 Rất thấp"
                elif risk == 2:
                    risk_desc = "🟡 Thấp"
                elif risk == 3:
                    risk_desc = "🟠 Vừa"
                elif risk == 4:
                    risk_desc = "🔴 Cao"
                else:
                    risk_desc = "⚫ Rất cao"
                
                print(f"{asset_type:<20} {self.format_currency(value, display_currency):<15} {percentage:>6.1f}% {risk:>5}/5 {risk_desc:<15}")
            
            # Risk recommendations
            print(f"\n💡 KHUYẾN NGHỊ:")
            
            if weighted_risk < 2.5:
                print(" • Danh mục quá bảo thủ - có thể cân nhắc tăng tỷ trọng tài sản rủi ro cao hơn")
                print(" • Xem xét đầu tư thêm cổ phiếu hoặc quỹ tăng trưởng")
            elif weighted_risk > 3.5:
                print(" • Danh mục có rủi ro cao - nên tăng tỷ trọng tài sản an toàn")
                print(" • Xem xét tăng tiền gửi hoặc trái phiếu chính phủ")
            
            # Diversification recommendations
            if num_assets < 3:
                print(" • Danh mục chưa đủ đa dạng - nên đầu tư thêm các loại tài sản khác")
            
            if gini_coefficient > 0.6:
                print(" • Tài sản tập trung quá nhiều - nên phân bổ đều hơn")
            
            # Age-based recommendations
            print(f"\n🎯 KHUYẾN NGHỊ THEO ĐỘ TUỔI:")
            print(" • 20-30 tuổi: Rủi ro 3.5-4.5 (tích cực)")
            print(" • 30-50 tuổi: Rủi ro 2.5-3.5 (cân bằng)")
            print(" • 50+ tuổi: Rủi ro 1.5-2.5 (bảo thủ)")
    #------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_portfolio_overview(self, button):
        """Hiển thị tổng quan danh mục đầu tư - Phiên bản sửa lỗi"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        display_currency = self.currency_display.value
        
        with self.output:
            clear_output()
            
            # Calculate portfolio summary
            portfolio_summary = {}
            total_value = 0
            
            # Tạo DataFrame để xử lý cumulative values
            df = pd.DataFrame(self.investment_data)
            df['date'] = pd.to_datetime(df['date'])
            df['amount_display'] = df.apply(
                lambda row: self.convert_currency(row['amount'], row['currency'], display_currency),
                axis=1
            )
            df['investment_id'] = df['type'] + ' - ' + df['description']
            
            # Tính giá trị hiện tại cho mỗi khoản đầu tư
            current_portfolio_values = {}
            for investment_id in df['investment_id'].unique():
                inv_data = df[df['investment_id'] == investment_id]
                cumulative_value = inv_data['amount_display'].sum()  # Net position
                if cumulative_value > 0:  # Chỉ tính những khoản đang nắm giữ
                    inv_type = inv_data['type'].iloc[0]
                    if inv_type not in current_portfolio_values:
                        current_portfolio_values[inv_type] = 0
                    current_portfolio_values[inv_type] += cumulative_value
                    total_value += cumulative_value
            
            # Tính portfolio summary dựa trên current holdings
            for inv_type, current_value in current_portfolio_values.items():
                if inv_type not in portfolio_summary:
                    portfolio_summary[inv_type] = {
                        'current_value': 0,
                        'count': 0,
                        'assets': {}
                    }
                
                # Đếm số assets đang nắm giữ trong loại này
                active_assets = df[df['type'] == inv_type]['investment_id'].unique()
                for asset_id in active_assets:
                    asset_data = df[df['investment_id'] == asset_id]
                    net_position = asset_data['amount_display'].sum()
                    if net_position > 0:  # Đang nắm giữ
                        portfolio_summary[inv_type]['assets'][asset_id] = net_position
                        portfolio_summary[inv_type]['count'] += 1
                
                portfolio_summary[inv_type]['current_value'] = current_value
            
            print("="*70)
            print(f"📊 TỔNG QUAN DANH MỤC ĐẦU TƯ ({display_currency})")
            print("="*70)
            print(f"💰 Tổng giá trị hiện tại: {self.format_currency(total_value, display_currency)}")
            print(f"📈 Số loại tài sản: {len(portfolio_summary)}")
            print(f"🏷️  Tổng số khoản đang nắm giữ: {sum(data['count'] for data in portfolio_summary.values())}")
            print(f"📊 Tổng số giao dịch: {len(self.investment_data)}")
            print("-"*70)
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
            
            # 1. Pie chart - Portfolio allocation by type
            if portfolio_summary:
                types = list(portfolio_summary.keys())
                values = [portfolio_summary[t]['current_value'] for t in types]
                colors = plt.cm.Set3(np.linspace(0, 1, len(types)))
                
                wedges, texts, autotexts = ax1.pie(values, labels=types, autopct='%1.1f%%', 
                                                  colors=colors, startangle=90)
                ax1.set_title('Phân Bổ Danh Mục Theo Loại Tài Sản (Hiện Tại)')
                
                # 2. Bar chart - Investment amounts by type
                bars = ax2.bar(types, values, color=colors)
                ax2.set_title('Giá Trị Hiện Tại Theo Loại')
                ax2.set_ylabel(f'Giá trị ({display_currency})')
                ax2.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for bar, v in zip(bars, values):
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01, 
                            self.format_currency(v, display_currency), ha='center', va='bottom', fontsize=9)
            
            # 3. Timeline of cumulative investments (fixed stacked area chart)
            # Tính cumulative holdings theo thời gian (chỉ positive values)
            df_sorted = df.sort_values('date')
            
            # Tạo cumulative timeline cho mỗi loại tài sản
            timeline_data = {}
            
            for inv_type in df['type'].unique():
                type_data = df_sorted[df_sorted['type'] == inv_type].copy()
                type_data['cumulative'] = type_data['amount_display'].cumsum()
                
                # Resample theo tháng và lấy giá trị cuối tháng
                type_data.set_index('date', inplace=True)
                monthly_data = type_data['cumulative'].resample('M').last().fillna(method='ffill')
                
                # Chỉ giữ các giá trị dương (đang nắm giữ)
                monthly_data = monthly_data.clip(lower=0)
                timeline_data[inv_type] = monthly_data
            
            # Tạo DataFrame cho timeline
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data).fillna(0)
                
                if not timeline_df.empty and len(timeline_df) > 1:
                    # Vẽ area chart với giá trị đã được xử lý
                    timeline_df.plot(kind='area', stacked=True, ax=ax3, alpha=0.7, 
                                   colormap='Set3')
                    ax3.set_title('Xu Hướng Tích Lũy Đầu Tư Theo Thời Gian')
                    ax3.set_ylabel(f'Giá trị tích lũy ({display_currency})')
                    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
                    ax3.grid(True, alpha=0.3)
                    
                    # Format x-axis
                    ax3.tick_params(axis='x', rotation=45)
                else:
                    ax3.text(0.5, 0.5, 'Chưa đủ dữ liệu\nđể hiển thị xu hướng', 
                            ha='center', va='center', transform=ax3.transAxes, fontsize=12)
                    ax3.set_title('Xu Hướng Tích Lũy Đầu Tư Theo Thời Gian')
            
            # 4. Top investments by current value
            all_assets = {}
            for inv_type in portfolio_summary:
                for asset, value in portfolio_summary[inv_type]['assets'].items():
                    if value > 0:  # Chỉ hiển thị những khoản đang nắm giữ
                        all_assets[asset] = value
            
            top_assets = sorted(all_assets.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if top_assets:
                asset_names = [asset[0].split(' - ')[1][:25] + '...' if len(asset[0].split(' - ')[1]) > 25 
                              else asset[0].split(' - ')[1] for asset in top_assets]
                asset_values = [asset[1] for asset in top_assets]
                
                colors_bar = plt.cm.viridis(np.linspace(0, 1, len(asset_names)))
                bars = ax4.barh(asset_names, asset_values, color=colors_bar)
                ax4.set_title('Top 10 Khoản Đầu Tư Đang Nắm Giữ')
                ax4.set_xlabel(f'Giá trị ({display_currency})')
                
                # Add value labels
                for bar, v in zip(bars, asset_values):
                    width = bar.get_width()
                    ax4.text(width + max(asset_values)*0.01, bar.get_y() + bar.get_height()/2,
                            self.format_currency(v, display_currency), ha='left', va='center', fontsize=8)
            else:
                ax4.text(0.5, 0.5, 'Không có dữ liệu\nđể hiển thị', 
                        ha='center', va='center', transform=ax4.transAxes, fontsize=12)
                ax4.set_title('Top 10 Khoản Đầu Tư Đang Nắm Giữ')
            
            plt.tight_layout()
            plt.show()
            
            # Print detailed breakdown
            print("\n📋 CHI TIẾT THEO LOẠI TÀI SẢN (Đang nắm giữ):")
            
            for inv_type, data in portfolio_summary.items():
                if data['current_value'] > 0:
                    percentage = (data['current_value'] / total_value) * 100
                    print(f"\n🏛️  {inv_type}")
                    print(f"   💰 Giá trị hiện tại: {self.format_currency(data['current_value'], display_currency)} ({percentage:.1f}%)")
                    print(f"   📊 Số khoản đang nắm giữ: {data['count']}")
                    
                    # Thông tin rủi ro cho loại tài sản này
                    risk_info = self.asset_risk_levels.get(inv_type, {})
                    if risk_info:
                        print(f"   ⚠️  Mức rủi ro: {risk_info.get('risk', 'N/A')}/5")
                        print(f"   📈 Lợi nhuận kỳ vọng: {risk_info.get('expected_return', 'N/A')}%/năm")
                    
                    # Top assets trong loại này
                    sorted_assets = sorted(data['assets'].items(), key=lambda x: x[1], reverse=True)[:5]
                    if sorted_assets:
                        print(f"   🔝 Top khoản đầu tư:")
                        for i, (asset, value) in enumerate(sorted_assets, 1):
                            asset_name = asset.split(' - ')[1]
                            asset_pct = (value / data['current_value']) * 100
                            print(f"      {i}. {asset_name}: {self.format_currency(value, display_currency)} ({asset_pct:.1f}%)")
            
            # Portfolio statistics
            print(f"\n📊 THỐNG KÊ DANH MỤC:")
            
            # Tính Gini coefficient cho portfolio diversity
            if portfolio_summary:
                values_list = [data['current_value'] for data in portfolio_summary.values()]
                gini_coef = self.calculate_gini_coefficient(values_list)
                
                print(f"   📈 Hệ số đa dạng Gini: {gini_coef:.3f} (0 = hoàn toàn đều, 1 = tập trung hoàn toàn)")
                
                if gini_coef < 0.3:
                    diversity_status = "🟢 Đa dạng tốt"
                elif gini_coef < 0.6:
                    diversity_status = "🟡 Đa dạng trung bình"
                else:
                    diversity_status = "🔴 Quá tập trung"
                
                print(f"   🎯 Đánh giá đa dạng: {diversity_status}")
                
                # Risk assessment
                weighted_risk = sum(
                    data['current_value'] * self.asset_risk_levels.get(inv_type, {}).get('risk', 3)
                    for inv_type, data in portfolio_summary.items()
                ) / total_value if total_value > 0 else 0
                
                print(f"   ⚠️  Điểm rủi ro trung bình: {weighted_risk:.2f}/5")
                
                if weighted_risk <= 2.5:
                    risk_status = "🟢 Bảo thủ"
                elif weighted_risk <= 3.5:
                    risk_status = "🟡 Cân bằng"
                else:
                    risk_status = "🔴 Tích cực"
                
                print(f"   🎭 Profile rủi ro: {risk_status}")
            
            # Recommendations
            print(f"\n💡 KHUYẾN NGHỊ:")
            
            if len(portfolio_summary) < 3:
                print("   🔹 Nên đa dạng hóa thêm các loại tài sản để giảm rủi ro")
            
            # Check if any single investment takes up too much
            if all_assets:
                max_single_investment = max(all_assets.values())
                max_percentage = (max_single_investment / total_value) * 100
                if max_percentage > 20:
                    max_asset_name = [k for k, v in all_assets.items() if v == max_single_investment][0]
                    print(f"   ⚠️  Khoản đầu tư '{max_asset_name.split(' - ')[1]}' chiếm {max_percentage:.1f}% - cân nhắc giảm tỷ trọng")
            
            # Risk-based recommendations
            if portfolio_summary:
                high_risk_pct = sum(
                    (data['current_value'] / total_value) * 100 
                    for inv_type, data in portfolio_summary.items() 
                    if self.asset_risk_levels.get(inv_type, {}).get('risk', 3) >= 4
                )
                
                if high_risk_pct > 50:
                    print(f"   🔴 Tài sản rủi ro cao chiếm {high_risk_pct:.1f}% - cân nhắc cân bằng với tài sản an toàn hơn")
                elif high_risk_pct < 10:
                    print(f"   🟢 Danh mục khá bảo thủ ({high_risk_pct:.1f}% rủi ro cao) - có thể tăng tỷ trọng tài sản tăng trưởng")
            
            print(f"\n⏰ Cập nhật: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    #------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_trend_analysis(self, button):
        """Phân tích xu hướng đầu tư theo thời gian, xử lý giao dịch bán (giá trị âm)"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        display_currency = self.currency_display.value
        
        with self.output:
            clear_output()
            print("="*80)
            print("📈 PHÂN TÍCH XU HƯỚNG ĐẦU TƯ")
            print("="*80)
            
            # Prepare data
            df = pd.DataFrame(self.investment_data)
            try:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.dropna(subset=['date'])
                if df.empty:
                    print("❌ Không có dữ liệu hợp lệ để phân tích xu hướng!")
                    return
            except Exception as e:
                print(f"⚠️ Lỗi xử lý ngày tháng: {str(e)}")
                return
            
            df['amount_display'] = df.apply(
                lambda row: self.convert_currency(row['amount'], row['currency'], display_currency),
                axis=1
            )
            
            # Create visualizations
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Total portfolio value over time (weekly)
            weekly_value = df.groupby(df['date'].dt.to_period('W'))['amount_display'].sum()
            if not weekly_value.empty:
                weekly_value.index = weekly_value.index.to_timestamp()
                ax1.plot(weekly_value.index, weekly_value.values, marker='o', color='blue')
                ax1.set_title('Tổng Giá Trị Danh Mục (Theo Tuần)')
                ax1.set_ylabel(f'Số tiền ({display_currency})')
                ax1.tick_params(axis='x', rotation=45)
                ax1.grid(True, linestyle='--', alpha=0.7)
            else:
                ax1.text(0.5, 0.5, 'Không có dữ liệu để hiển thị', ha='center', va='center', fontsize=12)
                ax1.set_title('Tổng Giá Trị Danh Mục (Theo Tuần)')
            
            # 2. Investment trend by asset type (weekly) - Handle sales (negative values)
            # Calculate cumulative sum to reflect net value after sales
            df['cumsum'] = df.groupby(['type'])['amount_display'].cumsum()
            type_trend = df.groupby([df['date'].dt.to_period('W'), 'type'])['cumsum'].last().unstack(fill_value=0)
            # Ensure all values are non-negative for stacked area plot
            type_trend = type_trend.clip(lower=0)
            if not type_trend.empty:
                type_trend.index = type_trend.index.to_timestamp()
                type_trend.plot(kind='area', stacked=True, ax=ax2, alpha=0.7)
                ax2.set_title('Xu Hướng Giá Trị Tích Lũy Theo Loại Tài Sản (Theo Tuần)')
                ax2.set_ylabel(f'Số tiền ({display_currency})')
                ax2.tick_params(axis='x', rotation=45)
                ax2.grid(True, linestyle='--', alpha=0.7)
            else:
                ax2.text(0.5, 0.5, 'Không có dữ liệu để hiển thị', ha='center', va='center', fontsize=12)
                ax2.set_title('Xu Hướng Giá Trị Tích Lũy Theo Loại Tài Sản (Theo Tuần)')
            
            # 3. Cumulative investment over time
            for asset_type in df['type'].unique():
                type_data = df[df['type'] == asset_type][['date', 'cumsum']].sort_values('date')
                if not type_data.empty:
                    ax3.plot(type_data['date'], type_data['cumsum'], label=asset_type)
            ax3.set_title('Tích Lũy Đầu Tư Theo Loại Tài Sản')
            ax3.set_ylabel(f'Số tiền tích lũy ({display_currency})')
            ax3.tick_params(axis='x', rotation=45)
            ax3.legend()
            ax3.grid(True, linestyle='--', alpha=0.7)
            
            # 4. Investment frequency
            monthly_counts = df.groupby(df['date'].dt.to_period('M'))['type'].count()
            if not monthly_counts.empty:
                monthly_counts.index = monthly_counts.index.to_timestamp()
                ax4.bar(monthly_counts.index, monthly_counts.values, color='purple', alpha=0.7)
                ax4.set_title('Tần Suất Đầu Tư (Theo Tháng)')
                ax4.set_ylabel('Số lượng giao dịch')
                ax4.tick_params(axis='x', rotation=45)
                ax4.grid(True, linestyle='--', alpha=0.7)
            else:
                ax4.text(0.5, 0.5, 'Không có dữ liệu để hiển thị', ha='center', va='center', fontsize=12)
                ax4.set_title('Tần Suất Đầu Tư (Theo Tháng)')
            
            plt.tight_layout()
            plt.show()
            
            # Detailed trend analysis
            print("\n📊 PHÂN TÍCH CHI TIẾT:")
            print(f"{'Thời gian':<15} {'Loại tài sản':<20} {'Số tiền tích lũy':<15} {'Tỷ trọng':<10}")
            print("-"*60)
            
            for period, group in df.groupby(df['date'].dt.to_period('W')):
                total_period = group['cumsum'].iloc[-1] if not group.empty else 0
                if total_period == 0:
                    continue
                for _, row in group.iterrows():
                    percentage = (row['cumsum'] / total_period) * 100 if total_period != 0 else 0
                    print(f"{str(period):<15} {row['type']:<20} {self.format_currency(row['cumsum'], display_currency):<15} {percentage:>6.1f}%")
            
            # Trend insights
            print("\n💡 NHẬN XÉT:")
            if not weekly_value.empty:
                growth = ((weekly_value.iloc[-1] - weekly_value.iloc[0]) / weekly_value.iloc[0] * 100) if weekly_value.iloc[0] != 0 else 0
                print(f" • Tăng trưởng danh mục: {growth:.1f}% từ {weekly_value.index[0].strftime('%Y-%m-%d')} đến {weekly_value.index[-1].strftime('%Y-%m-%d')}")
            
            if not type_trend.empty:
                dominant_asset = type_trend.iloc[-1].idxmax() if type_trend.iloc[-1].sum() > 0 else "Không xác định"
                print(f" • Loại tài sản chiếm ưu thế gần đây: {dominant_asset}")
            
            if not monthly_counts.empty:
                avg_transactions = monthly_counts.mean()
                print(f" • Số giao dịch trung bình mỗi tháng: {avg_transactions:.1f}")


            
    def show_diversification_analysis(self, button):
        """Phân tích đa dạng hóa danh mục"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        display_currency = self.currency_display.value
        
        with self.output:
            clear_output()
            
            print("="*70)
            print("🌐 PHÂN TÍCH ĐA DẠNG HÓA DANH MỤC")
            print("="*70)
            
            # Calculate diversification metrics
            portfolio_summary = {}
            asset_details = {}
            total_value = 0
            
            for inv in self.investment_data:
                inv_type = inv['type']
                asset_key = f"{inv['type']} - {inv['description']}"
                amount = self.convert_currency(inv['amount'], inv['currency'], display_currency)
                
                portfolio_summary[inv_type] = portfolio_summary.get(inv_type, 0) + amount
                asset_details[asset_key] = asset_details.get(asset_key, 0) + amount
                total_value += amount
            
            # Diversification scores
            num_asset_types = len(portfolio_summary)
            num_individual_assets = len(asset_details)
            
            # Calculate Herfindahl Index (concentration measure)
            type_weights = [(value/total_value)**2 for value in portfolio_summary.values()]
            herfindahl_types = sum(type_weights)
            
            asset_weights = [(value/total_value)**2 for value in asset_details.values()]
            herfindahl_assets = sum(asset_weights)
            
            # Diversification scores (lower HHI = better diversification)
            type_diversification = (1 - herfindahl_types) * 100
            asset_diversification = (1 - herfindahl_assets) * 100
            
            # Create diversification visualizations
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Asset type concentration
            types = list(portfolio_summary.keys())
            type_values = list(portfolio_summary.values())
            type_percentages = [(v/total_value)*100 for v in type_values]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(types)))
            ax1.pie(type_values, labels=types, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('Đa Dạng Hóa Theo Loại Tài Sản')
            
            # 2. Individual asset concentration (top 10)
            sorted_assets = sorted(asset_details.items(), key=lambda x: x[1], reverse=True)[:10]
            asset_names = [asset[0].split(' - ')[1][:15] + '...' if len(asset[0].split(' - ')[1]) > 15 
                          else asset[0].split(' - ')[1] for asset in sorted_assets]
            asset_amounts = [asset[1] for asset in sorted_assets]
            
            ax2.barh(asset_names, asset_amounts, color=plt.cm.viridis(np.linspace(0, 1, len(asset_names))))
            ax2.set_title('Top 10 Tài Sản Cá Biệt')
            ax2.set_xlabel(f'Giá trị ({display_currency})')
            
            # 3. Diversification scores
            diversification_metrics = {
                'Số loại tài sản': min(num_asset_types * 20, 100),  # Max 5 types = 100%
                'Phân bổ loại TS': type_diversification,
                'Số tài sản cá biệt': min(num_individual_assets * 5, 100),  # Max 20 assets = 100%
                'Phân bổ cá biệt': asset_diversification,
                'Tổng thể': (type_diversification + asset_diversification + 
                            min(num_asset_types * 20, 100) + min(num_individual_assets * 5, 100)) / 4
            }
            
            metrics = list(diversification_metrics.keys())
            scores = list(diversification_metrics.values())
            
            bars = ax3.barh(metrics, scores, color=['blue', 'green', 'orange', 'red', 'purple'])
            ax3.set_title('Điểm Số Đa Dạng Hóa')
            ax3.set_xlabel('Điểm (%)')
            ax3.set_xlim(0, 100)
            
            # Add score labels and color coding
            for i, (bar, score) in enumerate(zip(bars, scores)):
                if score >= 80:
                    color = 'green'
                    status = '✅'
                elif score >= 60:
                    color = 'orange'
                    status = '🟡'
                else:
                    color = 'red'
                    status = '🔴'
                
                ax3.text(score + 2, i, f'{status} {score:.1f}%', va='center', color=color, fontweight='bold')
            
            # 4. Concentration risk analysis
            # Calculate what percentage is held in top assets
            sorted_asset_values = sorted(asset_details.values(), reverse=True)
            top_1_concentration = (sorted_asset_values[0] / total_value * 100) if len(sorted_asset_values) >= 1 else 0
            top_3_concentration = (sum(sorted_asset_values[:3]) / total_value * 100) if len(sorted_asset_values) >= 3 else top_1_concentration
            top_5_concentration = (sum(sorted_asset_values[:5]) / total_value * 100) if len(sorted_asset_values) >= 5 else top_3_concentration
            
            concentration_data = {
                'Top 1 tài sản': top_1_concentration,
                'Top 3 tài sản': top_3_concentration,
                'Top 5 tài sản': top_5_concentration,
                'Còn lại': 100 - top_5_concentration
            }
            
            ax4.pie(concentration_data.values(), labels=concentration_data.keys(), 
                   autopct='%1.1f%%', startangle=90)
            ax4.set_title('Tập Trung Rủi Ro')
            
            plt.tight_layout()
            plt.show()
            
            # Print detailed analysis
            print(f"📊 ĐIỂM SỐ ĐA DẠNG HÓA TỔNG THỂ: {diversification_metrics['Tổng thể']:.1f}/100")
            
            if diversification_metrics['Tổng thể'] >= 80:
                overall_rating = "🟢 Xuất sắc"
            elif diversification_metrics['Tổng thể'] >= 60:
                overall_rating = "🟡 Tốt"
            elif diversification_metrics['Tổng thể'] >= 40:
                overall_rating = "🟠 Trung bình"
            else:
                overall_rating = "🔴 Cần cải thiện"
            
            print(f"🏆 Đánh giá: {overall_rating}")
            print("-"*70)
            
            print(f"📈 Chi tiết phân tích:")
            print(f"   🏷️  Số loại tài sản: {num_asset_types}")
            print(f"   🎯 Số tài sản cá biệt: {num_individual_assets}")
            print(f"   📊 Herfindahl Index (loại): {herfindahl_types:.3f}")
            print(f"   📊 Herfindahl Index (cá biệt): {herfindahl_assets:.3f}")
            
            print(f"\n🎯 PHÂN BỔ THEO LOẠI TÀI SẢN:")
            for inv_type, value in sorted(portfolio_summary.items(), key=lambda x: x[1], reverse=True):
                percentage = (value / total_value) * 100
                if percentage > 40:
                    status = "🔴 Quá tập trung"
                elif percentage > 25:
                    status = "🟠 Tập trung cao"
                elif percentage > 10:
                    status = "🟡 Hợp lý"
                else:
                    status = "🟢 Cân bằng"
                
                print(f"   • {inv_type:<20}: {percentage:>6.1f}% {status}")
            
            print(f"\n⚠️  PHÂN TÍCH RỦI RO TẬP TRUNG:")
            print(f"   • Tài sản lớn nhất chiếm: {top_1_concentration:.1f}%")
            print(f"   • Top 3 tài sản chiếm: {top_3_concentration:.1f}%")
            print(f"   • Top 5 tài sản chiếm: {top_5_concentration:.1f}%")
            
            # Risk assessment
            if top_1_concentration > 50:
                print("   🔴 Rủi ro tập trung rất cao - một tài sản chiếm quá 50%")
            elif top_1_concentration > 30:
                print("   🟠 Rủi ro tập trung cao - nên giảm tỷ trọng tài sản lớn nhất")
            elif top_3_concentration > 70:
                print("   🟡 Có một ít tập trung ở top 3 tài sản")
            else:
                print("   🟢 Phân bổ tương đối cân bằng")
            
            # Recommendations
            print(f"\n💡 KHUYẾN NGHỊ TĂNG CƯỜNG ĐA DẠNG HÓA:")
            
            if num_asset_types < 4:
                print("   📊 Thêm các loại tài sản mới (cổ phiếu, quỹ, vàng, bất động sản)")
            
            if num_individual_assets < 10:
                print("   🎯 Tăng số lượng tài sản cá biệt trong mỗi loại")
            
            if top_1_concentration > 25:
                largest_asset = max(asset_details, key=asset_details.get)
                print(f"   ⚖️  Giảm tỷ trọng '{largest_asset.split(' - ')[1]}' xuống dưới 25%")
            
            if type_diversification < 60:
                print("   🌐 Cân bằng lại tỷ trọng giữa các loại tài sản")
            
            # Geographic diversification suggestion
            print(f"\n🌍 KHUYẾN NGHỊ ĐA DẠNG HÓA ĐỊA LÝ:")
            print("   • Xem xét đầu tư cả trong nước và quốc tế")
            print("   • Đa dạng hóa theo thị trường (Việt Nam, Hàn Quốc, Mỹ, châu Âu)")
            print("   • Cân nhắc ETF toàn cầu để tăng đa dạng hóa")
    
    def export_investment_report(self, button):
        """Xuất báo cáo đầu tư chi tiết"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu để xuất báo cáo!")
            return
        
        try:
            filename = f'BaoCaoPhongMucDauTu_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            
            with pd.ExcelWriter(filename) as writer:
                # Sheet 1: Raw investment data
                df_raw = pd.DataFrame(self.investment_data)
                df_raw['amount_vnd'] = df_raw.apply(
                    lambda row: self.convert_currency(row['amount'], row['currency'], 'VND'), axis=1
                )
                df_raw['amount_krw'] = df_raw.apply(
                    lambda row: self.convert_currency(row['amount'], row['currency'], 'KRW'), axis=1
                )
                df_raw.to_excel(writer, sheet_name='Dữ liệu Gốc', index=False)
                
                # Sheet 2: Portfolio summary
                portfolio_summary = {}
                for inv in self.investment_data:
                    inv_type = inv['type']
                    amount_vnd = self.convert_currency(inv['amount'], inv['currency'], 'VND')
                    amount_krw = self.convert_currency(inv['amount'], inv['currency'], 'KRW')
                    
                    if inv_type not in portfolio_summary:
                        portfolio_summary[inv_type] = {'vnd': 0, 'krw': 0, 'count': 0}
                    
                    portfolio_summary[inv_type]['vnd'] += amount_vnd
                    portfolio_summary[inv_type]['krw'] += amount_krw
                    portfolio_summary[inv_type]['count'] += 1
                
                summary_df = pd.DataFrame([
                    {
                        'Loại tài sản': inv_type,
                        'Giá trị VND': data['vnd'],
                        'Giá trị KRW': data['krw'],
                        'Số giao dịch': data['count'],
                        'Tỷ trọng (%)': (data['vnd'] / sum(d['vnd'] for d in portfolio_summary.values())) * 100
                    } for inv_type, data in portfolio_summary.items()
                ])
                summary_df.to_excel(writer, sheet_name='Tổng hợp Danh mục', index=False)
                
                # Sheet 3: Target allocation vs Current
                if self.target_allocation:
                    allocation_data = []
                    total_value = sum(data['vnd'] for data in portfolio_summary.values())
                    
                    all_types = set(list(portfolio_summary.keys()) + list(self.target_allocation.keys()))
                    for asset_type in all_types:
                        current_value = portfolio_summary.get(asset_type, {}).get('vnd', 0)
                        current_pct = (current_value / total_value * 100) if total_value > 0 else 0
                        target_pct = self.target_allocation.get(asset_type, 0)
                        deviation = current_pct - target_pct
                        
                        allocation_data.append({
                            'Loại tài sản': asset_type,
                            'Hiện tại (%)': current_pct,
                            'Mục tiêu (%)': target_pct,
                            'Độ lệch (%)': deviation,
                            'Giá trị hiện tại (VND)': current_value,
                            'Giá trị mục tiêu (VND)': (target_pct / 100) * total_value,
                            'Cần điều chỉnh (VND)': ((target_pct / 100) * total_value) - current_value
                        })
                    
                    allocation_df = pd.DataFrame(allocation_data)
                    allocation_df.to_excel(writer, sheet_name='Phân tích Phân bổ', index=False)
                
                # Sheet 4: Performance metrics
                df_perf = pd.DataFrame(self.investment_data)
                df_perf['date'] = pd.to_datetime(df_perf['date'])
                df_perf = df_perf.sort_values('date')
                df_perf['amount_vnd'] = df_perf.apply(
                    lambda row: self.convert_currency(row['amount'], row['currency'], 'VND'), axis=1
                )
                df_perf['cumulative_vnd'] = df_perf['amount_vnd'].cumsum()
                
                # Monthly summary
                monthly_perf = df_perf.groupby(df_perf['date'].dt.to_period('M')).agg({
                    'amount_vnd': ['sum', 'count', 'mean'],
                    'type': lambda x: ', '.join(x.unique())
                }).round(0)
                
                monthly_perf.columns = ['Tổng đầu tư (VND)', 'Số giao dịch', 'TB/giao dịch (VND)', 'Loại tài sản']
                monthly_perf.to_excel(writer, sheet_name='Hiệu suất Hàng tháng')
                
                # Sheet 5: Current prices (if any)
                if self.current_prices:
                    prices_data = []
                    for asset_key, price_info in self.current_prices.items():
                        prices_data.append({
                            'Tài sản': asset_key,
                            'Giá hiện tại': price_info['price'],
                            'Đơn vị': price_info['currency'],
                            'Ngày cập nhật': price_info['date'],
                            'Giá quy đổi VND': self.convert_currency(price_info['price'], price_info['currency'], 'VND'),
                            'Giá quy đổi KRW': self.convert_currency(price_info['price'], price_info['currency'], 'KRW')
                        })
                    
                    prices_df = pd.DataFrame(prices_data)
                    prices_df.to_excel(writer, sheet_name='Giá Hiện tại', index=False)
                
                # Sheet 6: Settings
                settings_data = [{
                    'Tham số': 'Tỷ giá KRW/VND',
                    'Giá trị': self.exchange_rate,
                    'Đơn vị': 'VND per KRW',
                    'Ngày cập nhật': datetime.now().date()
                }]
                
                if self.target_allocation:
                    for asset_type, target_pct in self.target_allocation.items():
                        settings_data.append({
                            'Tham số': f'Tỷ lệ mục tiêu - {asset_type}',
                            'Giá trị': target_pct,
                            'Đơn vị': '%',
                            'Ngày cập nhật': datetime.now().date()
                        })
                
                settings_df = pd.DataFrame(settings_data)
                settings_df.to_excel(writer, sheet_name='Cài đặt', index=False)
            
            with self.output:
                clear_output()
                print(f"✅ Đã xuất báo cáo đầu tư chi tiết: {filename}")
                print("📊 File bao gồm các sheet:")
                print("   • Dữ liệu Gốc - Tất cả giao dịch đầu tư")
                print("   • Tổng hợp Danh mục - Phân bổ theo loại tài sản")
                if self.target_allocation:
                    print("   • Phân tích Phân bổ - So sánh với mục tiêu")
                print("   • Hiệu suất Hàng tháng - Thống kê theo tháng")
                if self.current_prices:
                    print("   • Giá Hiện tại - Giá tài sản cập nhật")
                print("   • Cài đặt - Tỷ giá và mục tiêu phân bổ")
                
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi xuất báo cáo: {str(e)}")
    

def create_investment_analyzer():
    analyzer = InvestmentPortfolioAnalyzer()
    return analyzer.display()

# Hướng dẫn sử dụng
def show_usage_guide():
    """
    Hiển thị hướng dẫn sử dụng ứng dụng
    """
    guide = """
    📖 HƯỚNG DẪN SỬ DỤNG ỨNG DỤNG PHÂN TÍCH DANH MỤC ĐẦU TƯ
    
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
    └── Phân tích Rủi ro - Đánh giá mức độ rủi ro
    
    🔬 BƯỚC 4: PHÂN TÍCH NÂNG CAO
    ├── Xu hướng Đầu tư - Phân tích theo thời gian
    ├── Đa dạng hóa - Đánh giá mức độ đa dạng
    └── Tổng Tài sản - Quy đổi tiền tệ
    
    📄 BƯỚC 5: XUẤT BÁO CÁO
    └── Xuất file Excel chi tiết với tất cả phân tích
    
    💾 LƯU Ý:
    • Dữ liệu sẽ được lưu tự động vào các file CSV
    • Có thể import dữ liệu từ ứng dụng finance tracker
    • Hỗ trợ đầy đủ VND và KRW với tỷ giá linh hoạt
    """
    
    print(guide)

# Chạy ứng dụng
investment_app = create_investment_analyzer()
display(investment_app)
