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
        
        # Mapping từ savings type sang investment category
        self.investment_mapping = {
            'Đầu tư chứng khoán': 'Cổ phiếu',
            'Quỹ đầu tư': 'Quỹ',
            'Tiết kiệm ngân hàng': 'Tiền gửi',
            'Vàng': 'Vàng',
            'Bất động sản': 'Bất động sản',
            'Crypto': 'Crypto',
            'Khác': 'Khác'
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
            value="<h2 style='text-align: center; color: #2E86AB;'>📈 PHÂN TÍCH DANH MỤC ĐẦU TƯ</h2>"
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
            options=['Cổ phiếu', 'Quỹ', 'Tiền gửi', 'Vàng', 'Bất động sản', 'Crypto', 'Khác'],
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
            widgets.HBox([self.show_risk_analysis_btn]),
            
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
    
    def show_total_assets(self, button):
        """Hiển thị tổng tài sản với quy đổi tiền tệ"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        with self.output:
            clear_output()
            
            print("="*80)
            print("💰 TỔNG HỢP TÀI SẢN ĐẦU TƯ")
            print("="*80)
            print(f"💱 Tỷ giá hiện tại: 1 KRW = {self.exchange_rate} VND")
            print("-"*80)
            
            # Calculate totals in both currencies
            total_vnd = 0
            total_krw = 0
            asset_summary_vnd = {}
            asset_summary_krw = {}
            
            for inv in self.investment_data:
                inv_type = inv['type']
                amount_vnd = self.convert_currency(inv['amount'], inv['currency'], 'VND')
                amount_krw = self.convert_currency(inv['amount'], inv['currency'], 'KRW')
                
                total_vnd += amount_vnd
                total_krw += amount_krw
                
                asset_summary_vnd[inv_type] = asset_summary_vnd.get(inv_type, 0) + amount_vnd
                asset_summary_krw[inv_type] = asset_summary_krw.get(inv_type, 0) + amount_krw
            
            # Display totals
            print(f"🏆 TỔNG TÀI SẢN ĐẦU TƯ:")
            print(f"   💵 VND: {total_vnd:>20,.0f}đ")
            print(f"   💴 KRW: {total_krw:>20,.0f}₩")
            print("-"*50)
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
            
            # 1. Total assets comparison
            currencies = ['VND', 'KRW']
            totals = [total_vnd, total_krw]
            
            bars = ax1.bar(currencies, totals, color=['red', 'blue'], alpha=0.7)
            ax1.set_title('Tổng Tài Sản Theo Tiền Tệ')
            ax1.set_ylabel('Giá trị')
            
            # Add value labels
            for bar, total in zip(bars, totals):
                ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(totals)*0.02,
                        f'{total:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            # 2. Asset allocation in VND
            types_vnd = list(asset_summary_vnd.keys())
            values_vnd = list(asset_summary_vnd.values())
            
            ax2.pie(values_vnd, labels=types_vnd, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Phân Bổ Tài Sản (VND)')
            
            # 3. Asset allocation in KRW
            types_krw = list(asset_summary_krw.keys())
            values_krw = list(asset_summary_krw.values())
            
            ax3.pie(values_krw, labels=types_krw, autopct='%1.1f%%', startangle=90)
            ax3.set_title('Phân Bổ Tài Sản (KRW)')
            
            # 4. Exchange rate impact analysis
            # Show how much each asset type would change with ±10% exchange rate
            exchange_impact = {}
            for inv_type in asset_summary_vnd.keys():
                # Original values
                vnd_value = asset_summary_vnd[inv_type]
                krw_value = asset_summary_krw[inv_type]
                
                # Calculate impact of exchange rate change
                # If KRW portion exists, calculate impact
                krw_portion = 0
                for inv in self.investment_data:
                    if inv['type'] == inv_type and inv['currency'] == 'KRW':
                        krw_portion += inv['amount']
                
                # Impact of ±10% exchange rate change on VND value
                impact_10_percent = krw_portion * self.exchange_rate * 0.1
                exchange_impact[inv_type] = impact_10_percent
            
            if any(impact > 0 for impact in exchange_impact.values()):
                impact_types = list(exchange_impact.keys())
                impact_values = list(exchange_impact.values())
                
                ax4.barh(impact_types, impact_values, color='orange', alpha=0.7)
                ax4.set_title('Tác Động Tỷ Giá ±10% (VND)')
                ax4.set_xlabel('Thay đổi giá trị (VND)')
            else:
                ax4.text(0.5, 0.5, 'Không có tài sản KRW\nhoặc tác động nhỏ', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Tác Động Tỷ Giá')
            
            plt.tight_layout()
            plt.show()
            
            # Detailed breakdown
            print(f"📊 CHI TIẾT THEO LOẠI TÀI SẢN:")
            print(f"{'Loại tài sản':<20} {'VND':<20} {'KRW':<20} {'% Tổng':<10}")
            print("-"*75)
            
            for inv_type in sorted(asset_summary_vnd.keys(), key=lambda x: asset_summary_vnd[x], reverse=True):
                vnd_value = asset_summary_vnd[inv_type]
                krw_value = asset_summary_krw[inv_type]
                percentage = (vnd_value / total_vnd) * 100
                
                print(f"{inv_type:<20} {vnd_value:>15,.0f}đ {krw_value:>15,.0f}₩ {percentage:>6.1f}%")
            
            # Currency composition analysis
            print(f"\n💱 PHÂN TÍCH THÀNH PHẦN TIỀN TỆ:")
            
            vnd_investments = sum(1 for inv in self.investment_data if inv['currency'] == 'VND')
            krw_investments = sum(1 for inv in self.investment_data if inv['currency'] == 'KRW')
            total_investments = len(self.investment_data)
            
            vnd_value_original = sum(inv['amount'] for inv in self.investment_data if inv['currency'] == 'VND')
            krw_value_original = sum(inv['amount'] for inv in self.investment_data if inv['currency'] == 'KRW')
            
            print(f"   📊 Số giao dịch VND: {vnd_investments} ({vnd_investments/total_investments*100:.1f}%)")
            print(f"   📊 Số giao dịch KRW: {krw_investments} ({krw_investments/total_investments*100:.1f}%)")
            print(f"   💰 Giá trị gốc VND: {vnd_value_original:,.0f}đ")
            print(f"   💰 Giá trị gốc KRW: {krw_value_original:,.0f}₩")
            
            # Exchange rate sensitivity
            if krw_value_original > 0:
                sensitivity = (krw_value_original * self.exchange_rate) / total_vnd * 100
                print(f"\n⚖️  ĐỘ NHẠY CẢM TỶ GIÁ:")
                print(f"   📈 {sensitivity:.1f}% danh mục chịu ảnh hưởng tỷ giá KRW/VND")
                
                if sensitivity > 50:
                    print("   🔴 Rủi ro tỷ giá cao - cần cân nhắc hedging")
                elif sensitivity > 25:
                    print("   🟡 Rủi ro tỷ giá vừa phải - theo dõi thường xuyên")
                else:
                    print("   🟢 Rủi ro tỷ giá thấp")
                
                # Show impact scenarios
                print(f"\n📊 KỊCH BẢN TỶ GIÁ:")
                scenarios = [0.9, 0.95, 1.0, 1.05, 1.1]
                print(f"   {'Tỷ giá':<10} {'Tổng VND':<20} {'Thay đổi':<15}")
                print("   " + "-"*45)
                
                for scenario in scenarios:
                    new_rate = self.exchange_rate * scenario
                    new_total_vnd = vnd_value_original + (krw_value_original * new_rate)
                    change = ((new_total_vnd - total_vnd) / total_vnd) * 100
                    
                    print(f"   {new_rate:>7.1f} {new_total_vnd:>15,.0f}đ {change:>+10.1f}%")
    
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
