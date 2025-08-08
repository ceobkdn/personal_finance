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
    
    def show_performance_analysis(self, button):
        """Phân tích hiệu suất đầu tư"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        display_currency = self.currency_display.value
        
        with self.output:
            clear_output()
            
            # Calculate performance metrics
            df = pd.DataFrame(self.investment_data)
            df['date'] = pd.to_datetime(df['date'])
            df['amount_display'] = df.apply(
                lambda row: self.convert_currency(row['amount'], row['currency'], display_currency), 
                axis=1
            )
            
            # Sort by date
            df = df.sort_values('date')
            
            print("="*70)
            print(f"📈 PHÂN TÍCH HIỆU SUẤT ĐẦU TƯ ({display_currency})")
            print("="*70)
            
            # Create visualizations
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Cumulative investment over time
            df['cumulative'] = df['amount_display'].cumsum()
            ax1.plot(df['date'], df['cumulative'], marker='o', linewidth=2, markersize=4)
            ax1.set_title('Tích Lũy Đầu Tư Theo Thời Gian')
            ax1.set_ylabel(f'Tổng đầu tư ({display_currency})')
            ax1.grid(True, alpha=0.3)
            
            # 2. Monthly investment pattern
            monthly_investment = df.groupby(df['date'].dt.to_period('M'))['amount_display'].sum()
            ax2.bar(range(len(monthly_investment)), monthly_investment.values, alpha=0.7)
            ax2.set_title('Mô Hình Đầu Tư Hàng Tháng')
            ax2.set_ylabel(f'Số tiền đầu tư ({display_currency})')
            ax2.set_xlabel('Tháng')
            
            # Set month labels
            month_labels = [str(period) for period in monthly_investment.index[::max(1, len(monthly_investment)//6)]]
            ax2.set_xticks(range(0, len(monthly_investment), max(1, len(monthly_investment)//6)))
            ax2.set_xticklabels(month_labels, rotation=45)
            
            # 3. Investment by type over time
            type_timeline = df.groupby([df['date'].dt.to_period('M'), 'type'])['amount_display'].sum().unstack(fill_value=0)
            if not type_timeline.empty:
                type_timeline.plot(kind='area', stacked=True, ax=ax3, alpha=0.7)
                ax3.set_title('Phân Bổ Đầu Tư Theo Loại Theo Thời Gian')
                ax3.set_ylabel(f'Số tiền ({display_currency})')
                ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # 4. Average investment by day of week
            df['day_of_week'] = df['date'].dt.day_name()
            day_avg = df.groupby('day_of_week')['amount_display'].mean()
            
            # Reorder days
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_avg_ordered = day_avg.reindex([day for day in day_order if day in day_avg.index])
            
            ax4.bar(range(len(day_avg_ordered)), day_avg_ordered.values, alpha=0.7, color='skyblue')
            ax4.set_title('Số Tiền Đầu Tư Trung Bình Theo Thứ')
            ax4.set_ylabel(f'Trung bình ({display_currency})')
            ax4.set_xticks(range(len(day_avg_ordered)))
            ax4.set_xticklabels([day[:3] for day in day_avg_ordered.index], rotation=45)
            
            plt.tight_layout()
            plt.show()
            
            # Calculate key metrics
            total_invested = df['amount_display'].sum()
            investment_period = (df['date'].max() - df['date'].min()).days
            avg_monthly_investment = monthly_investment.mean() if not monthly_investment.empty else 0
            
            print(f"💰 Tổng số tiền đã đầu tư: {self.format_currency(total_invested, display_currency)}")
            print(f"⏰ Thời gian đầu tư: {investment_period} ngày ({investment_period/30:.1f} tháng)")
            print(f"📊 Đầu tư trung bình/tháng: {self.format_currency(avg_monthly_investment, display_currency)}")
            print(f"📈 Số lần giao dịch: {len(df)}")
            
            # Investment frequency analysis
            print("\n📊 PHÂN TÍCH TẦN SUẤT ĐẦU TƯ:")
            
            if investment_period > 0:
                frequency = len(df) / (investment_period / 30)  # transactions per month
                print(f"   🔄 Tần suất giao dịch: {frequency:.1f} lần/tháng")
                
                if frequency > 4:
                    print("   💡 Bạn đầu tư khá thường xuyên - tốt cho DCA!")
                elif frequency > 1:
                    print("   💡 Tần suất đầu tư vừa phải - có thể tăng frequency")
                else:
                    print("   💡 Đầu tư ít - cân nhắc tăng tần suất để DCA hiệu quả")
            
            # Best and worst performing months
            if len(monthly_investment) > 1:
                best_month = monthly_investment.idxmax()
                worst_month = monthly_investment.idxmin()
                
                print(f"\n🏆 Tháng đầu tư nhiều nhất: {best_month} - {self.format_currency(monthly_investment[best_month], display_currency)}")
                print(f"📉 Tháng đầu tư ít nhất: {worst_month} - {self.format_currency(monthly_investment[worst_month], display_currency)}")
            
            # Investment consistency analysis
            if len(monthly_investment) > 2:
                std_dev = monthly_investment.std()
                consistency = (avg_monthly_investment - std_dev) / avg_monthly_investment * 100
                
                print(f"\n📊 Độ ổn định đầu tư: {consistency:.1f}%")
                if consistency > 70:
                    print("   ✅ Đầu tư rất ổn định!")
                elif consistency > 40:
                    print("   🟡 Đầu tư tương đối ổn định")
                else:
                    print("   🔴 Đầu tư chưa ổn định, cần có kế hoạch rõ ràng hơn")
    
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
            
            # Risk levels by asset type
            risk_levels = {
                'Tiền gửi': 1,
                'Vàng': 2,
                'Quỹ': 3,
                'Bất động sản': 3,
                'Cổ phiếu': 4,
                'Crypto': 5,
                'Khác': 3
            }
            
            print("="*70)
            print("⚠️  PHÂN TÍCH RỦI RO DANH MỤC ĐẦU TƯ")
            print("="*70)
            
            # Calculate portfolio risk score
            weighted_risk = 0
            for asset_type, value in portfolio_summary.items():
                weight = value / total_value
                risk = risk_levels.get(asset_type, 3)
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
                risk = risk_levels.get(asset_type, 3)
                risk_label = f"Rủi ro {risk}/5"
                risk_data[risk_label] = risk_data.get(risk_label, 0) + value
            
            ax1.pie(risk_data.values(), labels=risk_data.keys(), autopct='%1.1f%%', startangle=90)
            ax1.set_title('Phân Bố Rủi Ro Danh Mục')
            
            # 2. Asset allocation with risk colors
            asset_types = list(portfolio_summary.keys())
            asset_values = list(portfolio_summary.values())
            risk_colors = []
            
            for asset_type in asset_types:
                risk = risk_levels.get(asset_type, 3)
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
                risk = risk_levels.get(asset_type, 3)
                ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(asset_values)*0.01,
                        f'R{risk}', ha='center', va='bottom', fontweight='bold')
            
            # 3. Risk concentration analysis
            risk_concentration = {}
            for asset_type, value in portfolio_summary.items():
                risk = risk_levels.get(asset_type, 3)
                risk_concentration[risk] = risk_concentration.get(risk, 0) + value
            
            risk_labels = [f'Rủi ro {r}' for r in sorted(risk_concentration.keys())]
            risk_values = [risk_concentration[r] for r in sorted(risk_concentration.keys())]
            
            ax3.barh(risk_labels, risk_values, color=['green', 'lightgreen', 'yellow', 'orange', 'red'][:len(risk_values)])
            ax3.set_title('Tập Trung Rủi Ro')
            ax3.set_xlabel(f'Giá trị ({display_currency})')
            
            # 4. Diversification analysis
            num_assets = len(portfolio_summary)
            gini_coefficient = self.calculate_gini_coefficient(list(portfolio_summary.values()))
            
            # Create diversification score visualization
            diversification_metrics = {
                'Số loại tài sản': min(num_assets / 5 * 100, 100),
                'Phân bổ đều': (1 - gini_coefficient) * 100,
                'Đa dạng rủi ro': min(len(set(risk_levels[t] for t in portfolio_summary.keys())) / 5 * 100, 100)
            }
            
            metrics = list(diversification_metrics.keys())
            scores = list(diversification_metrics.values())
            
            ax4.barh(metrics, scores, color=['blue', 'green', 'purple'])
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
                risk = risk_levels.get(asset_type, 3)
                
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
                print("   • Danh mục quá bảo thủ - có thể cân nhắc tăng tỷ trọng tài sản rủi ro cao hơn")
                print("   • Xem xét đầu tư thêm cổ phiếu hoặc quỹ tăng trưởng")
            elif weighted_risk > 3.5:
                print("   • Danh mục có rủi ro cao - nên tăng tỷ trọng tài sản an toàn")
                print("   • Xem xét tăng tiền gửi hoặc trái phiếu chính phủ")
            
            # Diversification recommendations
            if num_assets < 3:
                print("   • Danh mục chưa đủ đa dạng - nên đầu tư thêm các loại tài sản khác")
            
            if gini_coefficient > 0.6:
                print("   • Tài sản tập trung quá nhiều - nên phân bổ đều hơn")
            
            # Age-based recommendations (assuming user input later)
            print(f"\n🎯 KHUYẾN NGHỊ THEO ĐỘ TUỔI:")
            print("   • 20-30 tuổi: Rủi ro 3.5-4.5 (tích cực)")
            print("   • 30-50 tuổi: Rủi ro 2.5-3.5 (cân bằng)")
            print("   • 50+ tuổi: Rủi ro 1.5-2.5 (bảo thủ)")
    
    def show_portfolio_overview(self, button):
        """Hiển thị tổng quan danh mục đầu tư"""
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
            
            for inv in self.investment_data:
                inv_type = inv['type']
                amount = self.convert_currency(inv['amount'], inv['currency'], display_currency)
                
                if inv_type not in portfolio_summary:
                    portfolio_summary[inv_type] = {
                        'original_cost': 0,
                        'count': 0,
                        'assets': {}
                    }
                
                portfolio_summary[inv_type]['original_cost'] += amount
                portfolio_summary[inv_type]['count'] += 1
                total_value += amount
                
                # Group by asset
                asset_key = f"{inv['type']} - {inv['description']}"
                if asset_key not in portfolio_summary[inv_type]['assets']:
                    portfolio_summary[inv_type]['assets'][asset_key] = 0
                portfolio_summary[inv_type]['assets'][asset_key] += amount
            
            print("="*60)
            print(f"📊 TỔNG QUAN DANH MỤC ĐẦU TƯ ({display_currency})")
            print("="*60)
            print(f"💰 Tổng giá trị gốc: {self.format_currency(total_value, display_currency)}")
            print(f"📈 Số loại tài sản: {len(portfolio_summary)}")
            print(f"🏷️  Tổng số giao dịch: {len(self.investment_data)}")
            print("-"*60)
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Pie chart - Portfolio allocation by type
            types = list(portfolio_summary.keys())
            values = [portfolio_summary[t]['original_cost'] for t in types]
            colors = plt.cm.Set3(np.linspace(0, 1, len(types)))
            
            wedges, texts, autotexts = ax1.pie(values, labels=types, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            ax1.set_title('Phân Bổ Danh Mục Theo Loại Tài Sản')
            
            # 2. Bar chart - Investment amounts by type
            ax2.bar(types, values, color=colors)
            ax2.set_title('Giá Trị Đầu Tư Theo Loại')
            ax2.set_ylabel(f'Giá trị ({display_currency})')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for i, v in enumerate(values):
                ax2.text(i, v + max(values)*0.01, f'{v:,.0f}', ha='center', va='bottom')
            
            # 3. Timeline of investments
            df_viz = pd.DataFrame(self.investment_data)
            df_viz['date'] = pd.to_datetime(df_viz['date'])
            df_viz['amount_display'] = df_viz.apply(
                lambda row: self.convert_currency(row['amount'], row['currency'], display_currency), 
                axis=1
            )
            
            monthly_investment = df_viz.groupby([df_viz['date'].dt.to_period('M'), 'type'])['amount_display'].sum().unstack(fill_value=0)
            
            if not monthly_investment.empty:
                monthly_investment.plot(kind='area', stacked=True, ax=ax3, alpha=0.7)
                ax3.set_title('Xu Hướng Đầu Tư Theo Thời Gian')
                ax3.set_ylabel(f'Giá trị ({display_currency})')
                ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # 4. Top investments by value
            all_assets = {}
            for inv_type in portfolio_summary:
                for asset, value in portfolio_summary[inv_type]['assets'].items():
                    all_assets[asset] = value
            
            top_assets = sorted(all_assets.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if top_assets:
                asset_names = [asset[0].split(' - ')[1][:20] + '...' if len(asset[0].split(' - ')[1]) > 20 
                              else asset[0].split(' - ')[1] for asset in top_assets]
                asset_values = [asset[1] for asset in top_assets]
                
                ax4.barh(asset_names, asset_values, color=plt.cm.viridis(np.linspace(0, 1, len(asset_names))))
                ax4.set_title('Top 10 Khoản Đầu Tư Lớn Nhất')
                ax4.set_xlabel(f'Giá trị ({display_currency})')
            
            plt.tight_layout()
            plt.show()
            
            # Print detailed breakdown
            print("\n📋 CHI TIẾT THEO LOẠI TÀI SẢN:")
            for inv_type, data in portfolio_summary.items():
                percentage = (data['original_cost'] / total_value) * 100
                print(f"\n🏷️  {inv_type}")
                print(f"   💰 Giá trị: {self.format_currency(data['original_cost'], display_currency)} ({percentage:.1f}%)")
                print(f"   📊 Số giao dịch: {data['count']}")
                
                # Top 3 assets in this category
                sorted_assets = sorted(data['assets'].items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"   🔝 Top tài sản:")
                for asset, value in sorted_assets:
                    asset_name = asset.split(' - ')[1]
                    print(f"      • {asset_name}: {self.format_currency(value, display_currency)}")

    def show_trend_analysis(self, button):
        """Phân tích xu hướng đầu tư"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        display_currency = self.currency_display.value
        days = self.time_period.value
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        # Filter data by time period
        filtered_data = [inv for inv in self.investment_data if inv['date'] >= cutoff_date]
        
        if not filtered_data:
            with self.output:
                clear_output()
                print(f"❌ Không có dữ liệu trong {days} ngày qua!")
            return
        
        with self.output:
            clear_output()
            
            print("="*70)
            print(f"📈 PHÂN TÍCH XU HƯỚNG ĐẦU TƯ ({days} NGÀY QUA)")
            print("="*70)
            
            df = pd.DataFrame(filtered_data)
            df['date'] = pd.to_datetime(df['date'])
            df['amount_display'] = df.apply(
                lambda row: self.convert_currency(row['amount'], row['currency'], display_currency), 
                axis=1
            )
            df = df.sort_values('date')
            
            # Create trend visualizations
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Investment trend over time
            daily_investment = df.groupby('date')['amount_display'].sum()
            
            # Calculate moving averages
            ma_7 = daily_investment.rolling(window=7, min_periods=1).mean()
            ma_30 = daily_investment.rolling(window=30, min_periods=1).mean()
            
            ax1.plot(daily_investment.index, daily_investment.values, 'o-', alpha=0.6, label='Hàng ngày')
            ax1.plot(ma_7.index, ma_7.values, '-', linewidth=2, label='MA 7 ngày')
            ax1.plot(ma_30.index, ma_30.values, '-', linewidth=2, label='MA 30 ngày')
            ax1.set_title('Xu Hướng Đầu Tư Theo Thời Gian')
            ax1.set_ylabel(f'Số tiền ({display_currency})')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. Investment by type trend
            type_trend = df.groupby([df['date'].dt.to_period('W'), 'type'])['amount_display'].sum().unstack(fill_value=0)
            if not type_trend.empty:
                type_trend.plot(kind='area', stacked=True, ax=ax2, alpha=0.7)
                ax2.set_title('Xu Hướng Theo Loại Tài Sản (Theo Tuần)')
                ax2.set_ylabel(f'Số tiền ({display_currency})')
                ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # 3. Investment frequency analysis
            df['day_of_week'] = df['date'].dt.day_name()
            df['week_of_year'] = df['date'].dt.isocalendar().week
            
            weekly_frequency = df.groupby('week_of_year').size()
            ax3.bar(weekly_frequency.index, weekly_frequency.values, alpha=0.7, color='lightblue')
            ax3.set_title('Tần Suất Đầu Tư Theo Tuần')
            ax3.set_ylabel('Số lần giao dịch')
            ax3.set_xlabel('Tuần trong năm')
            
            # 4. Cumulative investment with trend line
            df_sorted = df.sort_values('date')
            df_sorted['cumulative'] = df_sorted['amount_display'].cumsum()
            df_sorted['days_from_start'] = (df_sorted['date'] - df_sorted['date'].min()).dt.days
            
            ax4.scatter(df_sorted['days_from_start'], df_sorted['cumulative'], alpha=0.6, color='blue')
            
            # Add trend line
            if len(df_sorted) > 1:
                z = np.polyfit(df_sorted['days_from_start'], df_sorted['cumulative'], 1)
                p = np.poly1d(z)
                ax4.plot(df_sorted['days_from_start'], p(df_sorted['days_from_start']), "r--", alpha=0.8, linewidth=2)
            
            ax4.set_title('Tích Lũy Đầu Tư & Xu Hướng')
            ax4.set_xlabel('Ngày từ lúc bắt đầu')
            ax4.set_ylabel(f'Tổng tích lũy ({display_currency})')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            # Calculate trend statistics
            total_invested = df['amount_display'].sum()
            avg_daily = total_invested / days
            
            # Investment momentum
            first_half = df[df['date'] <= df['date'].min() + timedelta(days=days//2)]['amount_display'].sum()
            second_half = df[df['date'] > df['date'].min() + timedelta(days=days//2)]['amount_display'].sum()
            
            momentum = ((second_half - first_half) / max(first_half, 1)) * 100 if first_half > 0 else 0
            
            print(f"💰 Tổng đầu tư trong {days} ngày: {self.format_currency(total_invested, display_currency)}")
            print(f"📊 Trung bình mỗi ngày: {self.format_currency(avg_daily, display_currency)}")
            print(f"🚀 Momentum đầu tư: {momentum:+.1f}%")
            
            if momentum > 20:
                print("   📈 Xu hướng tăng mạnh - bạn đang đầu tư tích cực hơn!")
            elif momentum > 5:
                print("   📊 Xu hướng tăng nhẹ - duy trì đà tốt!")
            elif momentum > -5:
                print("   ⚖️  Xu hướng ổn định - đầu tư đều đặn")
            else:
                print("   📉 Xu hướng giảm - có thể cần tăng cường đầu tư")
            
            # Best performing periods
            if len(daily_investment) > 7:
                best_week = daily_investment.rolling(7).sum().idxmax()
                best_week_amount = daily_investment.rolling(7).sum().max()
                
                print(f"\n🏆 Tuần đầu tư mạnh nhất: {best_week.strftime('%d/%m/%Y')}")
                print(f"   💰 Số tiền: {self.format_currency(best_week_amount, display_currency)}")
            
            # Investment consistency
            investment_days = df.groupby('date')['amount_display'].sum()
            if len(investment_days) > 1:
                consistency = len(investment_days) / days * 100
                print(f"\n📅 Tần suất đầu tư: {consistency:.1f}% số ngày ({len(investment_days)}/{days} ngày)")
                
                if consistency > 20:
                    print("   🎯 Rất thường xuyên!")
                elif consistency > 10:
                    print("   👍 Khá đều đặn")
                elif consistency > 5:
                    print("   📊 Trung bình")
                else:
                    print("   💡 Có thể tăng tần suất đầu tư")

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

def show_usage_guide():
    guide = """
    📖 HƯỚNG DẪN SỬ DỤNG ỨNG DỤNG PHÂN TÍCH DANH MỤC ĐẦU TƯ - PHIÊN BẢN QUỸ NÂNG CAO
    ...
    """
    print(guide)

# Chạy ứng dụng
investment_app = create_investment_analyzer()
display(investment_app)
