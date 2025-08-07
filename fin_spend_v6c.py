import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date
import ipywidgets as widgets
from IPython.display import display, clear_output
import numpy as np

# Thiết lập style cho matplotlib
plt.style.use('default')
sns.set_palette("husl")

class MonthlyFinanceTracker:
    def __init__(self):
        # Khởi tạo dữ liệu
        self.income_data = []
        self.expense_data = []
        self.loan_data = []
        self.savings_data = []
        self.exchange_rate = 1.0  # Tỷ giá mặc định KRW/VND
        self.base_currency = 'VND'  # Tiền tệ cơ sở để hiển thị báo cáo
        
        # File paths cho lưu dữ liệu
        self.data_files = {
            'income': 'finance_data_income.csv',
            'expense': 'finance_data_expense.csv', 
            'loan': 'finance_data_loan.csv',
            'savings': 'finance_data_savings.csv',
            'settings': 'finance_settings.csv'
        }
        
        # Tạo widgets trước
        self.create_widgets()
        
        # Tải dữ liệu có sẵn
        self.load_data()
        
        # Cập nhật dropdown sau khi load dữ liệu
        self.update_loan_dropdown()
        self.update_savings_dropdown()
        
        # Tạo layout cuối cùng
        self.create_layout()
        
    def create_widgets(self):
        # Header
        self.title = widgets.HTML(
            value="<h2 style='text-align: center; color: #2E86AB;'>📊 GIÁM SÁT THU CHI HÀNG THÁNG</h2>"
        )
        
        # Exchange Rate Settings
        self.settings_header = widgets.HTML(
            value="<h3 style='color: #17A2B8;'>⚙️ CÀI ĐẶT TỶ GIÁ & TIỀN TỆ</h3>"
        )
        self.exchange_rate_input = widgets.FloatText(
            value=1.0,
            description="Tỷ giá (1 KRW):",
            style={'description_width': 'initial'},
            tooltip="Nhập số VND tương ứng với 1 KRW"
        )
        self.base_currency_dropdown = widgets.Dropdown(
            options=['VND', 'KRW'],
            value='VND',
            description="Tiền tệ báo cáo:",
            style={'description_width': 'initial'}
        )
        #------------------------------------------------------------------------------------------------------------
        self.base_currency_dropdown.layout = widgets.Layout(width='20%')
        #------------------------------------------------------------------------------------------------------------

        
        self.update_rate_btn = widgets.Button(
            description="Cập nhật Tỷ giá",
            button_style='info',
            icon='refresh'
        )
        
        # Income widgets
        self.income_header = widgets.HTML(
            value="<h3 style='color: #28A745;'>💰 KHOẢN THU</h3>"
        )
        self.income_source = widgets.Text(
            placeholder="VD: Lương, Thưởng, Freelance...",
            description="Nguồn thu:",
            style={'description_width': 'initial'}
        )
        self.income_amount = widgets.FloatText(
            value=0.0,
            description="Số tiền:",
            style={'description_width': 'initial'}
        )
        self.income_currency = widgets.Dropdown(
            options=['VND', 'KRW'],
            value='VND',
            description="Tiền tệ:",
            style={'description_width': 'initial'}
        )
        #------------------------------------------------------------------------------------------------------------
        self.income_currency.layout = widgets.Layout(width='20%')
        #------------------------------------------------------------------------------------------------------------        
        
        self.income_date = widgets.DatePicker(
            description="Ngày:",
            value=date.today(),
            style={'description_width': 'initial'}
        )
        self.add_income_btn = widgets.Button(
            description="Thêm Thu Nhập",
            button_style='success',
            icon='plus'
        )
        
        # Expense widgets
        self.expense_header = widgets.HTML(
            value="<h3 style='color: #DC3545;'>💸 KHOẢN CHI</h3>"
        )
        self.expense_category = widgets.Dropdown(
            options=['Ăn uống', 'Đi lại', 'Nhà ở', 'Giải trí', 'Mua sắm', 
                    'Y tế', 'Giáo dục', 'Tiện ích', 'Khác'],
            description="Danh mục:",
            style={'description_width': 'initial'}
        )
        self.expense_description = widgets.Text(
            placeholder="VD: Cơm trưa, Xăng xe, Tiền nhà...",
            description="Mô tả:",
            style={'description_width': 'initial'}
        )
        self.expense_amount = widgets.FloatText(
            value=0.0,
            description="Số tiền:",
            style={'description_width': 'initial'}
        )
        self.expense_currency = widgets.Dropdown(
            options=['VND', 'KRW'],
            value='VND',
            description="Tiền tệ:",
            style={'description_width': 'initial'}
        )
        #------------------------------------------------------------------------------------------------------------
        self.expense_currency.layout = widgets.Layout(width='20%')
        #------------------------------------------------------------------------------------------------------------

        
        self.expense_date = widgets.DatePicker(
            description="Ngày:",
            value=date.today(),
            style={'description_width': 'initial'}
        )
        self.add_expense_btn = widgets.Button(
            description="Thêm Chi Phí",
            button_style='danger',
            icon='plus'
        )
        
        # Loan Management widgets
        self.loan_header = widgets.HTML(
            value="<h3 style='color: #FF6B35;'>🏦 QUẢN LÝ VAY NỢ</h3>"
        )
        
        # Dropdown để chọn khoản vay có sẵn
        self.existing_loan_dropdown = widgets.Dropdown(
            options=[('-- Tạo khoản vay mới --', '')],
            description="Chọn khoản vay:",
            style={'description_width': 'initial'},
            layout={'width': '400px'}
        )
        self.load_loan_btn = widgets.Button(
            description="Tải thông tin",
            button_style='info',
            icon='edit',
            layout={'width': '120px'}
        )
        
        self.loan_type = widgets.Dropdown(
            options=['Vay ngân hàng', 'Vay bạn bè', 'Thẻ tín dụng', 'Vay khác'],
            description="Loại vay:",
            style={'description_width': 'initial'}
        )
        self.loan_description = widgets.Text(
            placeholder="VD: Vay mua nhà, Vay tiêu dùng...",
            description="Mô tả:",
            style={'description_width': 'initial'}
        )
        self.loan_total = widgets.FloatText(
            value=0.0,
            description="Tổng nợ:",
            style={'description_width': 'initial'}
        )
        self.loan_currency = widgets.Dropdown(
            options=['VND', 'KRW'],
            value='VND',
            description="Tiền tệ:",
            style={'description_width': 'initial'}
        )
        #------------------------------------------------------------------------------------------------------------
        self.loan_currency.layout = widgets.Layout(width='20%')
        #------------------------------------------------------------------------------------------------------------

        
        self.loan_monthly = widgets.FloatText(
            value=0.0,
            description="Trả hàng tháng:",
            style={'description_width': 'initial'}
        )
        self.loan_paid = widgets.FloatText(
            value=0.0,
            description="Đã trả:",
            style={'description_width': 'initial'}
        )
        self.loan_date = widgets.DatePicker(
            description="Ngày trả:",
            value=date.today(),
            style={'description_width': 'initial'}
        )
        self.is_fixed_payment = widgets.Checkbox(
            value=True,
            description="Trả cố định hàng tháng",
            style={'description_width': 'initial'}
        )
        self.add_loan_btn = widgets.Button(
            description="Thêm/Cập nhật Vay",
            button_style='warning',
            icon='plus'
        )
        self.pay_loan_btn = widgets.Button(
            description="Ghi nhận Thanh toán",
            button_style='primary',
            icon='money-bill'
        )
        self.delete_loan_btn = widgets.Button(
            description="Xóa Khoản vay",
            button_style='danger',
            icon='trash'
        )
        
        # Savings & Investment widgets
        self.savings_header = widgets.HTML(
            value="<h3 style='color: #6F42C1;'>💎 TIẾT KIỆM & ĐẦU TƯ</h3>"
        )
        
        # Dropdown để chọn khoản tiết kiệm/đầu tư có sẵn
        self.existing_savings_dropdown = widgets.Dropdown(
            options=[('-- Tạo khoản mới --', '')],
            description="Chọn khoản:",
            style={'description_width': 'initial'},
            layout={'width': '400px'}
        )
        self.load_savings_btn = widgets.Button(
            description="Tải thông tin",
            button_style='info',
            icon='edit',
            layout={'width': '120px'}
        )
        
        self.savings_type = widgets.Dropdown(
            options=['Tiết kiệm ngân hàng', 'Đầu tư chứng khoán', 'Quỹ đầu tư', 
                    'Vàng', 'Bất động sản', 'Crypto', 'Khác'],
            description="Loại:",
            style={'description_width': 'initial'}
        )
        self.savings_description = widgets.Text(
            placeholder="VD: Gửi tiết kiệm 6 tháng, Mua cổ phiếu...",
            description="Mô tả:",
            style={'description_width': 'initial'}
        )
        self.savings_amount = widgets.FloatText(
            value=0.0,
            description="Số tiền:",
            style={'description_width': 'initial'}
        )
        self.savings_currency = widgets.Dropdown(
            options=['VND', 'KRW'],
            value='VND',
            description="Tiền tệ:",
            style={'description_width': 'initial'}
        )

        #------------------------------------------------------------------------------------------------------------
        self.savings_currency.layout = widgets.Layout(width='20%')
        #------------------------------------------------------------------------------------------------------------
        
        self.savings_date = widgets.DatePicker(
            description="Ngày:",
            value=date.today(),
            style={'description_width': 'initial'}
        )
        self.add_savings_btn = widgets.Button(
            description="Thêm Tiết kiệm/ĐT",
            button_style='info',
            icon='plus'
        )
        self.update_savings_btn = widgets.Button(
            description="Cập nhật Khoản",
            button_style='warning',
            icon='edit'
        )
        self.delete_savings_btn = widgets.Button(
            description="Xóa Khoản",
            button_style='danger',
            icon='trash'
        )
        
        # Analysis widgets
        self.analysis_header = widgets.HTML(
            value="<h3 style='color: #17A2B8;'>📈 PHÂN TÍCH & BÁO CÁO</h3>"
        )
        self.month_filter = widgets.Dropdown(
            options=self.get_month_options(),
            description="Tháng:",
            style={'description_width': 'initial'}
        )
        self.show_summary_btn = widgets.Button(
            description="Tổng Quan Tháng",
            button_style='info',
            icon='chart-bar'
        )
        self.show_cash_flow_btn = widgets.Button(
            description="Dòng Tiền & Phân bổ",
            button_style='success',
            icon='coins'
        )
        self.show_loan_status_btn = widgets.Button(
            description="Tình trạng Vay nợ",
            button_style='warning',
            icon='credit-card'
        )
        self.show_charts_btn = widgets.Button(
            description="Biểu Đồ Chi tiết",
            button_style='info',
            icon='chart-pie'
        )
        
        # New Investment Analysis buttons
        self.show_investment_detail_btn = widgets.Button(
            description="Chi tiết Đầu tư",
            button_style='primary',
            icon='list'
        )
        self.show_investment_charts_btn = widgets.Button(
            description="Biểu đồ Đầu tư",
            button_style='primary',
            icon='chart-line'
        )
        self.show_total_assets_btn = widgets.Button(
            description="Tổng Tài sản",
            button_style='success',
            icon='money-bill-wave'
        )
        
        self.export_btn = widgets.Button(
            description="Xuất Excel",
            button_style='',
            icon='download'
        )
        
        # Data management buttons
        self.save_data_btn = widgets.Button(
            description="Lưu Dữ liệu",
            button_style='success',
            icon='save',
            tooltip="Lưu tất cả dữ liệu vào file CSV"
        )
        self.load_data_btn = widgets.Button(
            description="Tải Dữ liệu",
            button_style='info',
            icon='upload',
            tooltip="Tải dữ liệu từ file CSV"
        )
        self.clear_data_btn = widgets.Button(
            description="Xóa Tất cả",
            button_style='danger',
            icon='trash',
            tooltip="Xóa toàn bộ dữ liệu (cẩn thận!)"
        )
        
        # Output area
        self.output = widgets.Output()
        
        # Bind events
        self.update_rate_btn.on_click(self.update_exchange_rate)
        self.add_income_btn.on_click(self.add_income)
        self.add_expense_btn.on_click(self.add_expense)
        self.add_loan_btn.on_click(self.add_loan)
        self.pay_loan_btn.on_click(self.pay_loan)
        self.add_savings_btn.on_click(self.add_savings)
        self.show_summary_btn.on_click(self.show_summary)
        self.show_cash_flow_btn.on_click(self.show_cash_flow)
        self.show_loan_status_btn.on_click(self.show_loan_status)
        self.show_charts_btn.on_click(self.show_charts)
        self.show_investment_detail_btn.on_click(self.show_investment_detail)
        self.show_investment_charts_btn.on_click(self.show_investment_charts)
        self.show_total_assets_btn.on_click(self.show_total_assets)
        self.export_btn.on_click(self.export_to_excel)
        
        # Data management events
        self.save_data_btn.on_click(self.save_data)
        self.load_data_btn.on_click(self.load_data_manual)
        self.clear_data_btn.on_click(self.clear_all_data)
        
        # Loan management events
        self.load_loan_btn.on_click(self.load_selected_loan)
        self.delete_loan_btn.on_click(self.delete_loan)
        
        # Savings management events  
        self.load_savings_btn.on_click(self.load_selected_savings)
        self.update_savings_btn.on_click(self.update_savings)
        self.delete_savings_btn.on_click(self.delete_savings)
    
    def convert_to_base_currency(self, amount, from_currency):
        """Chuyển đổi tiền tệ về tiền tệ báo cáo"""
        if from_currency == self.base_currency:
            return amount
        elif from_currency == 'KRW' and self.base_currency == 'VND':
            return amount * self.exchange_rate
        elif from_currency == 'VND' and self.base_currency == 'KRW':
            return amount / self.exchange_rate
        return amount
    
    def format_currency(self, amount, currency=None):
        """Format hiển thị tiền tệ"""
        if currency is None:
            currency = self.base_currency
        
        if currency == 'VND':
            return f"{amount:,.0f}đ"
        elif currency == 'KRW':
            return f"{amount:,.0f}₩"
        else:
            return f"{amount:,.0f}"
    
    def update_exchange_rate(self, button):
        """Cập nhật tỷ giá"""
        self.exchange_rate = self.exchange_rate_input.value
        self.base_currency = self.base_currency_dropdown.value
        
        # Lưu settings
        self.save_settings()
        
        with self.output:
            clear_output()
            print(f"✅ Đã cập nhật tỷ giá: 1 KRW = {self.exchange_rate:,.2f} VND")
            print(f"📊 Tiền tệ báo cáo: {self.base_currency}")
            print("💾 Cài đặt đã được lưu tự động")
    
    def save_settings(self):
        """Lưu cài đặt tỷ giá"""
        try:
            settings_data = {
                'exchange_rate': [self.exchange_rate],
                'base_currency': [self.base_currency],
                'last_updated': [datetime.now().isoformat()]
            }
            df = pd.DataFrame(settings_data)
            df.to_csv(self.data_files['settings'], index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"Lỗi khi lưu cài đặt: {str(e)}")
    
    def load_settings(self):
        """Tải cài đặt tỷ giá"""
        try:
            df = pd.read_csv(self.data_files['settings'], encoding='utf-8-sig')
            if not df.empty:
                self.exchange_rate = float(df['exchange_rate'].iloc[-1])
                self.base_currency = str(df['base_currency'].iloc[-1])
                self.exchange_rate_input.value = self.exchange_rate
                self.base_currency_dropdown.value = self.base_currency
                print(f"✅ Đã load cài đặt: 1 KRW = {self.exchange_rate:,.2f} VND, Báo cáo: {self.base_currency}")
        except FileNotFoundError:
            print("📝 Chưa có file cài đặt, sử dụng mặc định")
        except Exception as e:
            print(f"⚠️  Lỗi khi load cài đặt: {str(e)}")
    
    def get_month_options(self):
        current_month = datetime.now().month
        current_year = datetime.now().year
        options = []
        
        months_vn = {
            1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3", 4: "Tháng 4",
            5: "Tháng 5", 6: "Tháng 6", 7: "Tháng 7", 8: "Tháng 8",
            9: "Tháng 9", 10: "Tháng 10", 11: "Tháng 11", 12: "Tháng 12"
        }
        
        # Thêm 12 tháng gần nhất
        for i in range(12):
            month = ((current_month - i - 1) % 12) + 1
            year = current_year if current_month - i > 0 else current_year - 1
            options.append((f"{months_vn[month]} {year}", f"{year}-{month:02d}"))
        
        return options
    
    def create_layout(self):
        # Settings section
        settings_box = widgets.VBox([
            self.settings_header,
            widgets.HBox([self.exchange_rate_input, self.base_currency_dropdown, self.update_rate_btn])
        ])
        
        # Income section
        income_box = widgets.VBox([
            self.income_header,
            widgets.HBox([self.income_source, self.income_amount, self.income_currency]),
            widgets.HBox([self.income_date, self.add_income_btn])
        ])
        
        # Expense section
        expense_box = widgets.VBox([
            self.expense_header,
            widgets.HBox([self.expense_category, self.expense_description]),
            widgets.HBox([self.expense_amount, self.expense_currency, self.expense_date]),
            self.add_expense_btn
        ])
        
        # Loan section
        loan_box = widgets.VBox([
            self.loan_header,
            widgets.HTML("<h4 style='color: #666; margin: 5px 0;'>🔍 Chọn khoản vay có sẵn:</h4>"),
            widgets.HBox([self.existing_loan_dropdown, self.load_loan_btn]),
            widgets.HTML("<h4 style='color: #666; margin: 15px 0 5px 0;'>📝 Thông tin khoản vay:</h4>"),
            widgets.HBox([self.loan_type, self.loan_description]),
            widgets.HBox([self.loan_total, self.loan_currency, self.loan_monthly]),
            widgets.HBox([self.loan_paid, self.loan_date]),
            self.is_fixed_payment,
            widgets.HBox([self.add_loan_btn, self.pay_loan_btn, self.delete_loan_btn])
        ])
        
        # Savings section
        savings_box = widgets.VBox([
            self.savings_header,
            widgets.HTML("<h4 style='color: #666; margin: 5px 0;'>🔍 Chọn khoản có sẵn:</h4>"),
            widgets.HBox([self.existing_savings_dropdown, self.load_savings_btn]),
            widgets.HTML("<h4 style='color: #666; margin: 15px 0 5px 0;'>📝 Thông tin khoản tiết kiệm/đầu tư:</h4>"),
            widgets.HBox([self.savings_type, self.savings_description]),
            widgets.HBox([self.savings_amount, self.savings_currency, self.savings_date]),
            widgets.HBox([self.add_savings_btn, self.update_savings_btn, self.delete_savings_btn])
        ])
        
        # Analysis section
        analysis_box = widgets.VBox([
            self.analysis_header,
            self.month_filter,
            widgets.HTML("<h4 style='color: #666; margin: 10px 0 5px 0;'>📊 Báo cáo cơ bản:</h4>"),
            widgets.HBox([self.show_summary_btn, self.show_cash_flow_btn]),
            widgets.HBox([self.show_loan_status_btn, self.show_charts_btn]),
            widgets.HTML("<h4 style='color: #666; margin: 15px 0 5px 0;'>💎 Phân tích đầu tư:</h4>"),
            widgets.HBox([self.show_investment_detail_btn, self.show_investment_charts_btn]),
            widgets.HBox([self.show_total_assets_btn]),
            widgets.HTML("<hr style='margin: 10px 0;'>"),
            widgets.HTML("<h4 style='color: #6C757D; margin: 5px 0;'>🗃️ QUẢN LÝ DỮ LIỆU</h4>"),
            widgets.HBox([self.save_data_btn, self.load_data_btn, self.clear_data_btn, self.export_btn])
        ])
        
        # Main layout with tabs for better organization
        tab0 = settings_box  # Tab cài đặt
        tab1 = widgets.VBox([widgets.HBox([income_box, expense_box])])
        tab2 = widgets.VBox([widgets.HBox([loan_box, savings_box])])
        tab3 = analysis_box
        
        tabs = widgets.Tab()
        tabs.children = [tab0, tab1, tab2, tab3]
        tabs.titles = ['Cài đặt', 'Thu Chi Thường', 'Vay Nợ & Tiết Kiệm', 'Phân Tích']
        
        # Main layout
        self.main_layout = widgets.VBox([
            self.title,
            tabs,
            self.output
        ])
    
    def add_income(self, button):
        if self.income_source.value and self.income_amount.value > 0:
            self.income_data.append({
                'date': self.income_date.value,
                'source': self.income_source.value,
                'amount': self.income_amount.value,
                'currency': self.income_currency.value
            })
            
            # Auto-save after adding data
            self.save_data_silent()
            
            amount_display = self.format_currency(self.income_amount.value, self.income_currency.value)
            with self.output:
                clear_output()
                print(f"✅ Đã thêm thu nhập: {self.income_source.value} - {amount_display}")
                print("💾 Dữ liệu đã được lưu tự động")
            
            # Clear inputs
            self.income_source.value = ""
            self.income_amount.value = 0.0
        else:
            with self.output:
                clear_output()
                print("❌ Vui lòng nhập đầy đủ thông tin thu nhập!")
    
    def add_expense(self, button):
        if self.expense_description.value and self.expense_amount.value > 0:
            self.expense_data.append({
                'date': self.expense_date.value,
                'category': self.expense_category.value,
                'description': self.expense_description.value,
                'amount': self.expense_amount.value,
                'currency': self.expense_currency.value
            })
            
            # Auto-save after adding data
            self.save_data_silent()
            
            amount_display = self.format_currency(self.expense_amount.value, self.expense_currency.value)
            with self.output:
                clear_output()
                print(f"✅ Đã thêm chi phí: {self.expense_description.value} - {amount_display}")
                print("💾 Dữ liệu đã được lưu tự động")
            
            # Clear inputs
            self.expense_description.value = ""
            self.expense_amount.value = 0.0
        else:
            with self.output:
                clear_output()
                print("❌ Vui lòng nhập đầy đủ thông tin chi phí!")
    """
    def update_loan_dropdown(self):
        #Cập nhật dropdown danh sách khoản vay
        options = [('-- Tạo khoản vay mới --', '')]
        for i, loan in enumerate(self.loan_data):
            # Tính toán remaining amount để đảm bảo chính xác
            remaining = loan['total_amount'] - loan['paid_amount']
            loan['remaining_amount'] = max(0, remaining)  # Cập nhật lại remaining_amount
            
            # Convert to base currency for display
            remaining_display = self.convert_to_base_currency(remaining, loan['currency'])
            
            status = "Đã trả hết" if remaining <= 0 else f"Còn: {self.format_currency(remaining_display)}"
            display_name = f"{loan['description']} ({loan['type']}) - {status}"
            
            # Truncate tên nếu quá dài
            if len(display_name) > 60:
                display_name = display_name[:57] + "..."
            options.append((display_name, i))
        self.existing_loan_dropdown.options = options
        
        # Hiển thị thông báo số lượng khoản vay
        if len(self.loan_data) > 0:
            print(f"🏦 Đã load {len(self.loan_data)} khoản vay từ dữ liệu")
    
    def update_savings_dropdown(self):
        #Cập nhật dropdown danh sách tiết kiệm/đầu tư
        options = [('-- Tạo khoản mới --', '')]
        # Group savings by type and description
        savings_summary = {}
        for i, saving in enumerate(self.savings_data):
            key = f"{saving['type']} - {saving['description']}"
            if key in savings_summary:
                # Convert to base currency before summing
                converted_amount = self.convert_to_base_currency(saving['amount'], saving['currency'])
                savings_summary[key]['total'] += converted_amount
                savings_summary[key]['indices'].append(i)
            else:
                converted_amount = self.convert_to_base_currency(saving['amount'], saving['currency'])
                savings_summary[key] = {
                    'total': converted_amount,
                    'indices': [i],
                    'type': saving['type'],
                    'description': saving['description']
                }
        
        for key, data in savings_summary.items():
            display_name = f"{key} - Tổng: {self.format_currency(data['total'])}"
            if len(display_name) > 60:
                display_name = display_name[:57] + "..."
            options.append((display_name, key))
        
        self.existing_savings_dropdown.options = options
        
        # Hiển thị thông báo số lượng khoản tiết kiệm
        if len(savings_summary) > 0:
            print(f"💎 Đã load {len(savings_summary)} loại khoản tiết kiệm/đầu tư từ dữ liệu")
    """

    def update_loan_dropdown(self):
        """Cập nhật dropdown danh sách khoản vay"""
        options = [('-- Tạo khoản vay mới --', '')]
        for i, loan in enumerate(self.loan_data):
            # Tính toán remaining amount để đảm bảo chính xác
            remaining = loan['total_amount'] - loan['paid_amount']
            loan['remaining_amount'] = max(0, remaining)  # Cập nhật lại remaining_amount
            
            # Hiển thị với đơn vị tiền tệ gốc
            remaining_display = self.format_currency(remaining, loan['currency'])
            
            status = "Đã trả hết" if remaining <= 0 else f"Còn: {remaining_display}"
            display_name = f"{loan['description']} ({loan['type']}) - {status}"
            
            # Truncate tên nếu quá dài
            if len(display_name) > 60:
                display_name = display_name[:57] + "..."
            options.append((display_name, i))
        self.existing_loan_dropdown.options = options
        
        # Hiển thị thông báo số lượng khoản vay
        if len(self.loan_data) > 0:
            print(f"🏦 Đã load {len(self.loan_data)} khoản vay từ dữ liệu")
    
    def update_savings_dropdown(self):
        """Cập nhật dropdown danh sách tiết kiệm/đầu tư"""
        options = [('-- Tạo khoản mới --', '')]
        # Group savings by type, description, and currency
        savings_summary = {}
        for i, saving in enumerate(self.savings_data):
            # Thêm currency vào key để tách biệt các loại tiền tệ khác nhau
            key = f"{saving['type']} - {saving['description']} ({saving['currency']})"
            if key in savings_summary:
                # Cộng trực tiếp không chuyển đổi vì cùng loại tiền tệ
                savings_summary[key]['total'] += saving['amount']
                savings_summary[key]['indices'].append(i)
            else:
                savings_summary[key] = {
                    'total': saving['amount'],
                    'indices': [i],
                    'type': saving['type'],
                    'description': saving['description'],
                    'currency': saving['currency']
                }
        
        for key, data in savings_summary.items():
            # Hiển thị với đơn vị tiền tệ gốc
            total_display = self.format_currency(data['total'], data['currency'])
            display_name = f"{data['type']} - {data['description']} - Tổng: {total_display}"
            if len(display_name) > 60:
                display_name = display_name[:57] + "..."
            options.append((display_name, key))
        
        self.existing_savings_dropdown.options = options
        
        # Hiển thị thông báo số lượng khoản tiết kiệm
        if len(savings_summary) > 0:
            print(f"💎 Đã load {len(savings_summary)} loại khoản tiết kiệm/đầu tư từ dữ liệu")
    
    def add_loan(self, button):
        if self.loan_description.value and self.loan_total.value > 0:
            # Tìm xem đã có khoản vay này chưa
            existing_loan = None
            for loan in self.loan_data:
                if loan['description'] == self.loan_description.value and loan['type'] == self.loan_type.value:
                    existing_loan = loan
                    break
            
            if existing_loan:
                # Cập nhật khoản vay hiện có
                existing_loan.update({
                    'total_amount': self.loan_total.value,
                    'monthly_payment': self.loan_monthly.value,
                    'paid_amount': self.loan_paid.value,
                    'remaining_amount': self.loan_total.value - self.loan_paid.value,
                    'currency': self.loan_currency.value,
                    'is_fixed': self.is_fixed_payment.value,
                    'last_updated': date.today()
                })
                message = f"🔄 Đã cập nhật khoản vay: {self.loan_description.value}"
            else:
                # Thêm khoản vay mới
                self.loan_data.append({
                    'type': self.loan_type.value,
                    'description': self.loan_description.value,
                    'total_amount': self.loan_total.value,
                    'monthly_payment': self.loan_monthly.value,
                    'paid_amount': self.loan_paid.value,
                    'remaining_amount': self.loan_total.value - self.loan_paid.value,
                    'currency': self.loan_currency.value,
                    'is_fixed': self.is_fixed_payment.value,
                    'created_date': date.today(),
                    'last_updated': date.today(),
                    'payment_history': []
                })
                message = f"✅ Đã thêm khoản vay: {self.loan_description.value}"
            
            # Auto-save after adding/updating loan
            self.save_data_silent()
            self.update_loan_dropdown()  # Cập nhật dropdown
            
            total_display = self.format_currency(self.loan_total.value, self.loan_currency.value)
            monthly_display = self.format_currency(self.loan_monthly.value, self.loan_currency.value)
            
            with self.output:
                clear_output()
                print(message)
                print(f"   💰 Tổng nợ: {total_display}")
                print(f"   📅 Trả hàng tháng: {monthly_display} ({'Cố định' if self.is_fixed_payment.value else 'Linh hoạt'})")
                print("💾 Dữ liệu đã được lưu tự động")
        else:
            with self.output:
                clear_output()
                print("❌ Vui lòng nhập đầy đủ thông tin khoản vay!")
    
    def load_selected_loan(self, button):
        """Tải thông tin khoản vay đã chọn"""
        selected_index = self.existing_loan_dropdown.value
        if selected_index == '' or not isinstance(selected_index, int):
            # Clear form for new loan
            self.loan_type.value = 'Vay ngân hàng'
            self.loan_description.value = ''
            self.loan_total.value = 0.0
            self.loan_monthly.value = 0.0
            self.loan_paid.value = 0.0
            self.loan_currency.value = 'VND'
            self.is_fixed_payment.value = True
            
            with self.output:
                clear_output()
                print("📝 Form đã được reset để tạo khoản vay mới")
            return
        
        if selected_index < len(self.loan_data):
            loan = self.loan_data[selected_index]
            
            # Populate form with loan data
            self.loan_type.value = loan['type']
            self.loan_description.value = loan['description']
            self.loan_total.value = loan['total_amount']
            self.loan_monthly.value = loan['monthly_payment']
            self.loan_paid.value = loan['paid_amount']
            self.loan_currency.value = loan.get('currency', 'VND')
            self.is_fixed_payment.value = loan['is_fixed']
            
            total_display = self.format_currency(loan['total_amount'], loan.get('currency', 'VND'))
            paid_display = self.format_currency(loan['paid_amount'], loan.get('currency', 'VND'))
            remaining_display = self.format_currency(loan['remaining_amount'], loan.get('currency', 'VND'))
            
            with self.output:
                clear_output()
                print(f"✅ Đã tải thông tin: {loan['description']}")
                print(f"   💰 Tổng nợ: {total_display}")
                print(f"   ✅ Đã trả: {paid_display}")
                print(f"   ❗ Còn lại: {remaining_display}")
                
                if loan['payment_history']:
                    print(f"   📊 Lịch sử: {len(loan['payment_history'])} lần thanh toán")
    
    def delete_loan(self, button):
        """Xóa khoản vay đã chọn"""
        selected_index = self.existing_loan_dropdown.value
        if selected_index == '' or not isinstance(selected_index, int):
            with self.output:
                clear_output()
                print("❌ Vui lòng chọn khoản vay cần xóa!")
            return
        
        if selected_index < len(self.loan_data):
            deleted_loan = self.loan_data.pop(selected_index)
            self.save_data_silent()
            self.update_loan_dropdown()
            
            # Clear form
            self.loan_type.value = 'Vay ngân hàng'
            self.loan_description.value = ''
            self.loan_total.value = 0.0
            self.loan_monthly.value = 0.0
            self.loan_paid.value = 0.0
            self.loan_currency.value = 'VND'
            self.is_fixed_payment.value = True
            
            with self.output:
                clear_output()
                print(f"🗑️ Đã xóa khoản vay: {deleted_loan['description']}")
                print("💾 Dữ liệu đã được lưu tự động")
    
    def pay_loan(self, button):
        if not self.loan_description.value:
            with self.output:
                clear_output()
                print("❌ Vui lòng nhập mô tả khoản vay cần thanh toán!")
            return
            
        # Tìm khoản vay để thanh toán
        target_loan = None
        for loan in self.loan_data:
            if loan['description'] == self.loan_description.value and loan['type'] == self.loan_type.value:
                target_loan = loan
                break
        
        if not target_loan:
            with self.output:
                clear_output()
                print("❌ Không tìm thấy khoản vay này!")
            return
        
        payment_amount = self.loan_paid.value if self.loan_paid.value > 0 else target_loan['monthly_payment']
        
        # Ghi nhận thanh toán
        payment_record = {
            'date': self.loan_date.value,
            'amount': payment_amount,
            'remaining_before': target_loan['remaining_amount']
        }
        
        target_loan['payment_history'].append(payment_record)
        target_loan['paid_amount'] += payment_amount
        target_loan['remaining_amount'] = max(0, target_loan['total_amount'] - target_loan['paid_amount'])
        target_loan['last_updated'] = date.today()
        
        # Auto-save after payment
        self.save_data_silent()
        self.update_loan_dropdown()  # Cập nhật dropdown sau khi trả nợ
        
        payment_display = self.format_currency(payment_amount, target_loan.get('currency', 'VND'))
        remaining_display = self.format_currency(target_loan['remaining_amount'], target_loan.get('currency', 'VND'))
        
        with self.output:
            clear_output()
            print(f"✅ Đã ghi nhận thanh toán: {self.loan_description.value}")
            print(f"   💸 Số tiền trả: {payment_display}")
            print(f"   💰 Còn lại: {remaining_display}")
            print("💾 Dữ liệu đã được lưu tự động")
            if target_loan['remaining_amount'] == 0:
                print("   🎉 Đã trả hết nợ!")
    
    def add_savings(self, button):
        if self.savings_description.value and self.savings_amount.value > 0:
            self.savings_data.append({
                'date': self.savings_date.value,
                'type': self.savings_type.value,
                'description': self.savings_description.value,
                'amount': self.savings_amount.value,
                'currency': self.savings_currency.value
            })
            
            # Auto-save after adding data
            self.save_data_silent()
            self.update_savings_dropdown()  # Cập nhật dropdown
            
            amount_display = self.format_currency(self.savings_amount.value, self.savings_currency.value)
            with self.output:
                clear_output()
                print(f"✅ Đã thêm tiết kiệm/đầu tư: {self.savings_description.value} - {amount_display}")
                print("💾 Dữ liệu đã được lưu tự động")
            
            # Clear inputs
            self.savings_description.value = ""
            self.savings_amount.value = 0.0
        else:
            with self.output:
                clear_output()
                print("❌ Vui lòng nhập đầy đủ thông tin tiết kiệm/đầu tư!")
    
    def load_selected_savings(self, button):
        """Tải thông tin khoản tiết kiệm/đầu tư đã chọn"""
        selected_key = self.existing_savings_dropdown.value
        if selected_key == '':
            # Clear form for new savings
            self.savings_type.value = 'Tiết kiệm ngân hàng'
            self.savings_description.value = ''
            self.savings_amount.value = 0.0
            self.savings_currency.value = 'VND'
            
            with self.output:
                clear_output()
                print("📝 Form đã được reset để tạo khoản mới")
            return
        
        # Tìm khoản tiết kiệm/đầu tư theo key
        target_savings = None
        total_amount = 0
        count = 0
        
        for saving in self.savings_data:
            key = f"{saving['type']} - {saving['description']}"
            if key == selected_key:
                if target_savings is None:
                    target_savings = saving
                # Convert to base currency for display
                converted_amount = self.convert_to_base_currency(saving['amount'], saving['currency'])
                total_amount += converted_amount
                count += 1
        
        if target_savings:
            # Populate form with savings data
            self.savings_type.value = target_savings['type']
            self.savings_description.value = target_savings['description']
            self.savings_amount.value = 0.0  # Reset amount for new entry
            self.savings_currency.value = target_savings.get('currency', 'VND')
            
            with self.output:
                clear_output()
                print(f"✅ Đã tải thông tin: {target_savings['description']}")
                print(f"   💎 Loại: {target_savings['type']}")
                print(f"   💰 Tổng đã đầu tư: {self.format_currency(total_amount)}")
                print(f"   📊 Số lần giao dịch: {count}")
                print("📝 Bạn có thể thêm giao dịch mới hoặc cập nhật")

    """
    def update_savings(self, button):
        "Cập nhật khoản tiết kiệm/đầu tư (tương tự add nhưng với thông báo khác)"
        if self.savings_description.value and self.savings_amount.value > 0:
            self.savings_data.append({
                'date': self.savings_date.value,
                'type': self.savings_type.value,
                'description': self.savings_description.value,
                'amount': self.savings_amount.value,
                'currency': self.savings_currency.value
            })
            
            # Auto-save after updating data
            self.save_data_silent()
            self.update_savings_dropdown()  # Cập nhật dropdown
            
            amount_display = self.format_currency(self.savings_amount.value, self.savings_currency.value)
            with self.output:
                clear_output()
                print(f"🔄 Đã cập nhật/thêm vào {self.savings_description.value}: {amount_display}")
                print("💾 Dữ liệu đã được lưu tự động")
            
            # Clear amount but keep type and description
            self.savings_amount.value = 0.0
        else:
            with self.output:
                clear_output()
                print("❌ Vui lòng nhập đầy đủ thông tin!")
    """

    """
    def update_savings(self, button):
        #Cập nhật khoản tiết kiệm/đầu tư (hỗ trợ cả gửi tiền và rút tiền)
        # Kiểm tra điều kiện: có mô tả và số tiền khác 0
        if self.savings_description.value and self.savings_amount.value != 0:
            self.savings_data.append({
                'date': self.savings_date.value,
                'type': self.savings_type.value,
                'description': self.savings_description.value,
                'amount': self.savings_amount.value,  # Cho phép cả giá trị âm và dương
                'currency': self.savings_currency.value
            })
                        
            # Auto-save after updating data
            self.save_data_silent()
            self.update_savings_dropdown()  # Cập nhật dropdown
                        
            amount_display = self.format_currency(abs(self.savings_amount.value), self.savings_currency.value)
            
            # Xác định loại giao dịch dựa trên dấu của số tiền
            if self.savings_amount.value > 0:
                action_icon = "➕"
                action_text = "Đã thêm vào"
            else:
                action_icon = "➖"
                action_text = "Đã rút từ"
                
            with self.output:
                clear_output()
                print(f"{action_icon} {action_text} {self.savings_description.value}: {amount_display}")
                print("💾 Dữ liệu đã được lưu tự động")
                        
            # Clear amount but keep type and description
            self.savings_amount.value = 0.0
        else:
            with self.output:
                clear_output()
                if not self.savings_description.value:
                    print("❌ Vui lòng nhập mô tả!")
                elif self.savings_amount.value == 0:
                    print("❌ Vui lòng nhập số tiền khác 0!")
                else:
                    print("❌ Vui lòng nhập đầy đủ thông tin!")
    """

    def update_savings(self, button):
        """Cập nhật khoản tiết kiệm/đầu tư (hỗ trợ cả gửi tiền và rút tiền)"""
        # Kiểm tra điều kiện: có mô tả và số tiền khác 0
        if self.savings_description.value and self.savings_amount.value != 0:
            # Nếu là giao dịch rút tiền (số âm), kiểm tra số dư
            if self.savings_amount.value < 0:
                # Tính tổng số dư hiện tại cho loại tiết kiệm này
                current_balance = sum(item['amount'] for item in self.savings_data 
                                    if item['type'] == self.savings_type.value 
                                    and item['currency'] == self.savings_currency.value)
                
                withdrawal_amount = abs(self.savings_amount.value)
                
                # Kiểm tra xem có đủ tiền để rút không
                if current_balance < withdrawal_amount:
                    with self.output:
                        clear_output()
                        current_balance_display = self.format_currency(current_balance, self.savings_currency.value)
                        withdrawal_display = self.format_currency(withdrawal_amount, self.savings_currency.value)
                        print(f"❌ Không thể rút {withdrawal_display}!")
                        print(f"💰 Số dư hiện tại của {self.savings_type.value}: {current_balance_display}")
                        print(f"📝 Số tiền rút không được vượt quá số dư hiện có")
                    return  # Dừng thực hiện nếu không đủ tiền
            
            # Nếu đủ điều kiện, thực hiện giao dịch
            self.savings_data.append({
                'date': self.savings_date.value,
                'type': self.savings_type.value,
                'description': self.savings_description.value,
                'amount': self.savings_amount.value,  # Cho phép cả giá trị âm và dương
                'currency': self.savings_currency.value
            })
                         
            # Auto-save after updating data
            self.save_data_silent()
            self.update_savings_dropdown()  # Cập nhật dropdown
                         
            amount_display = self.format_currency(abs(self.savings_amount.value), self.savings_currency.value)
            
            # Xác định loại giao dịch dựa trên dấu của số tiền
            if self.savings_amount.value > 0:
                action_icon = "➕"
                action_text = "Đã thêm vào"
            else:
                action_icon = "➖"
                action_text = "Đã rút từ"
                
            with self.output:
                clear_output()
                print(f"{action_icon} {action_text} {self.savings_description.value}: {amount_display}")
                print("💾 Dữ liệu đã được lưu tự động")
                         
            # Clear amount but keep type and description
            self.savings_amount.value = 0.0
        else:
            with self.output:
                clear_output()
                if not self.savings_description.value:
                    print("❌ Vui lòng nhập mô tả!")
                elif self.savings_amount.value == 0:
                    print("❌ Vui lòng nhập số tiền khác 0!")
                else:
                    print("❌ Vui lòng nhập đầy đủ thông tin!")
                    
    def delete_savings(self, button):
        """Xóa tất cả giao dịch của một loại tiết kiệm/đầu tư"""
        selected_key = self.existing_savings_dropdown.value
        if selected_key == '':
            with self.output:
                clear_output()
                print("❌ Vui lòng chọn khoản cần xóa!")
            return
        
        # Tìm và xóa tất cả giao dịch với key này
        deleted_items = []
        remaining_savings = []
        
        for saving in self.savings_data:
            key = f"{saving['type']} - {saving['description']}"
            if key == selected_key:
                deleted_items.append(saving)
            else:
                remaining_savings.append(saving)
        
        if deleted_items:
            self.savings_data = remaining_savings
            self.save_data_silent()
            self.update_savings_dropdown()
            
            # Clear form
            self.savings_type.value = 'Tiết kiệm ngân hàng'
            self.savings_description.value = ''
            self.savings_amount.value = 0.0
            self.savings_currency.value = 'VND'
            
            # Calculate total deleted amount in base currency
            total_deleted = 0
            for item in deleted_items:
                total_deleted += self.convert_to_base_currency(item['amount'], item['currency'])
            
            with self.output:
                clear_output()
                print(f"🗑️ Đã xóa {len(deleted_items)} giao dịch: {selected_key}")
                print(f"   💰 Tổng số tiền: {self.format_currency(total_deleted)}")
                print("💾 Dữ liệu đã được lưu tự động")
    
    def filter_data_by_month(self, data, month_str):
        if not data:
            return []
        
        year, month = map(int, month_str.split('-'))
        filtered_data = []
        
        for item in data:
            item_date = item['date']
            if item_date.year == year and item_date.month == month:
                filtered_data.append(item)
        
        return filtered_data
    
    def calculate_monthly_loan_payments(self, month_str):
        """Tính tổng khoản vay phải trả trong tháng (đã chuyển đổi sang tiền tệ báo cáo)"""
        year, month = map(int, month_str.split('-'))
        total_fixed_payment = 0
        total_flexible_payment = 0
        
        for loan in self.loan_data:
            if loan['remaining_amount'] > 0:  # Chỉ tính các khoản vay chưa trả hết
                loan_currency = loan.get('currency', 'VND')
                
                if loan['is_fixed']:
                    converted_payment = self.convert_to_base_currency(loan['monthly_payment'], loan_currency)
                    total_fixed_payment += converted_payment
                else:
                    # Với vay linh hoạt, tính từ lịch sử thanh toán trong tháng
                    monthly_payments = 0
                    for payment in loan['payment_history']:
                        if payment['date'].year == year and payment['date'].month == month:
                            monthly_payments += payment['amount']
                    converted_payment = self.convert_to_base_currency(monthly_payments, loan_currency)
                    total_flexible_payment += converted_payment
        
        return total_fixed_payment, total_flexible_payment
    
    def show_investment_detail(self, button):
        """Hiển thị chi tiết các khoản đầu tư"""
        if not self.savings_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư nào!")
            return
        
        # Group by type and description
        investment_summary = {}
        total_investment = 0
        
        for saving in self.savings_data:
            key = f"{saving['type']} - {saving['description']}"
            converted_amount = self.convert_to_base_currency(saving['amount'], saving['currency'])
            
            if key in investment_summary:
                investment_summary[key]['total'] += converted_amount
                investment_summary[key]['transactions'].append({
                    'date': saving['date'],
                    'amount': converted_amount,
                    'original_amount': saving['amount'],
                    'original_currency': saving['currency']
                })
            else:
                investment_summary[key] = {
                    'type': saving['type'],
                    'description': saving['description'],
                    'total': converted_amount,
                    'transactions': [{
                        'date': saving['date'],
                        'amount': converted_amount,
                        'original_amount': saving['amount'],
                        'original_currency': saving['currency']
                    }]
                }
            total_investment += converted_amount
        
        with self.output:
            clear_output()
            print("="*70)
            print("💎 CHI TIẾT CÁC KHOẢN ĐẦU TƯ & TIẾT KIỆM")
            print("="*70)
            print(f"💰 TỔNG CỘNG TẤT CẢ: {self.format_currency(total_investment)}")
            print("="*70)
            
            # Sort by total amount descending
            sorted_investments = sorted(investment_summary.items(), 
                                      key=lambda x: x[1]['total'], reverse=True)
            
            for i, (key, data) in enumerate(sorted_investments, 1):
                percentage = (data['total'] / total_investment) * 100 if total_investment > 0 else 0
                
                print(f"\n{i}. {data['type']} - {data['description']}")
                print(f"   💰 Tổng giá trị: {self.format_currency(data['total'])} ({percentage:.1f}%)")
                print(f"   📊 Số giao dịch: {len(data['transactions'])}")
                
                # Show recent transactions (max 3)
                recent_transactions = sorted(data['transactions'], 
                                           key=lambda x: x['date'], reverse=True)[:3]
                
                print("   📅 Giao dịch gần nhất:")
                for trans in recent_transactions:
                    if trans['original_currency'] != self.base_currency:
                        print(f"      • {trans['date']}: {trans['original_amount']:,.0f} {trans['original_currency']} "
                              f"(≈ {self.format_currency(trans['amount'])})")
                    else:
                        print(f"      • {trans['date']}: {self.format_currency(trans['amount'])}")
                
                if len(data['transactions']) > 3:
                    print(f"      ... và {len(data['transactions']) - 3} giao dịch khác")
                
                print("-" * 50)
    
    def show_investment_charts(self, button):
        """Hiển thị biểu đồ chi tiết về đầu tư"""
        if not self.savings_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư để vẽ biểu đồ!")
            return
        
        # Process data for charts
        investment_by_type = {}
        investment_timeline = {}
        investment_by_description = {}
        
        for saving in self.savings_data:
            converted_amount = self.convert_to_base_currency(saving['amount'], saving['currency'])
            
            # By type
            if saving['type'] in investment_by_type:
                investment_by_type[saving['type']] += converted_amount
            else:
                investment_by_type[saving['type']] = converted_amount
            
            # By timeline (month-year)
            month_key = f"{saving['date'].year}-{saving['date'].month:02d}"
            if month_key in investment_timeline:
                investment_timeline[month_key] += converted_amount
            else:
                investment_timeline[month_key] = converted_amount
            
            # By description (top investments)
            if saving['description'] in investment_by_description:
                investment_by_description[saving['description']] += converted_amount
            else:
                investment_by_description[saving['description']] = converted_amount
        
        with self.output:
            clear_output()
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Phân Tích Chi Tiết Đầu Tư & Tiết Kiệm (Tính bằng {self.base_currency})', 
                        fontsize=16, fontweight='bold')
            
            # 1. Investment by type (pie chart)
            if investment_by_type:
                wedges, texts, autotexts = axes[0,0].pie(
                    investment_by_type.values(), 
                    labels=investment_by_type.keys(), 
                    autopct='%1.1f%%',
                    startangle=90
                )
                axes[0,0].set_title('Phân Bổ Theo Loại Đầu Tư')
                
                # Add amount to labels
                for i, (key, value) in enumerate(investment_by_type.items()):
                    autotexts[i].set_text(f'{autotexts[i].get_text()}\n{self.format_currency(value)}')
            
            # 2. Investment timeline (line chart)
            if investment_timeline:
                timeline_sorted = dict(sorted(investment_timeline.items()))
                dates = list(timeline_sorted.keys())
                amounts = list(timeline_sorted.values())
                
                # Calculate cumulative investment
                cumulative = np.cumsum(amounts)
                
                axes[0,1].plot(dates, amounts, 'o-', label='Đầu tư hàng tháng', color='#6F42C1', linewidth=2, markersize=6)
                axes[0,1].plot(dates, cumulative, 's-', label='Tích lũy', color='#28A745', linewidth=2, markersize=4)
                axes[0,1].set_title('Lịch Sử Đầu Tư Theo Thời Gian')
                axes[0,1].set_ylabel(f'Số tiền ({self.base_currency})')
                axes[0,1].legend()
                axes[0,1].tick_params(axis='x', rotation=45)
                axes[0,1].grid(True, alpha=0.3)
            
            # 3. Top investments by description (horizontal bar)
            if investment_by_description:
                # Get top 10 investments
                top_investments = dict(sorted(investment_by_description.items(), 
                                            key=lambda x: x[1], reverse=True)[:10])
                
                y_pos = range(len(top_investments))
                descriptions = [desc[:30] + '...' if len(desc) > 30 else desc 
                              for desc in top_investments.keys()]
                amounts = list(top_investments.values())
                
                bars = axes[1,0].barh(y_pos, amounts, color='#17A2B8', alpha=0.8)
                axes[1,0].set_yticks(y_pos)
                axes[1,0].set_yticklabels(descriptions)
                axes[1,0].set_xlabel(f'Số tiền ({self.base_currency})')
                axes[1,0].set_title('Top 10 Khoản Đầu Tư')
                
                # Add value labels on bars
                for i, (bar, amount) in enumerate(zip(bars, amounts)):
                    axes[1,0].text(bar.get_width() + max(amounts) * 0.01, 
                                 bar.get_y() + bar.get_height()/2,
                                 f'{self.format_currency(amount)}',
                                 ha='left', va='center', fontsize=8)
            
            # 4. Investment growth analysis
            if len(investment_timeline) > 1:
                timeline_sorted = dict(sorted(investment_timeline.items()))
                dates = list(timeline_sorted.keys())
                amounts = list(timeline_sorted.values())
                cumulative = np.cumsum(amounts)
                
                # Monthly growth rate
                growth_rates = []
                for i in range(1, len(cumulative)):
                    if cumulative[i-1] > 0:
                        growth = ((cumulative[i] - cumulative[i-1]) / cumulative[i-1]) * 100
                        growth_rates.append(growth)
                    else:
                        growth_rates.append(0)
                
                if growth_rates:
                    axes[1,1].bar(dates[1:], growth_rates, color='#FFC107', alpha=0.7)
                    axes[1,1].set_title('Tăng Trưởng Đầu Tư Hàng Tháng (%)')
                    axes[1,1].set_ylabel('Tăng trưởng (%)')
                    axes[1,1].tick_params(axis='x', rotation=45)
                    axes[1,1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
                    axes[1,1].grid(True, alpha=0.3)
            else:
                axes[1,1].text(0.5, 0.5, 'Cần ít nhất 2 tháng dữ liệu\nđể phân tích tăng trưởng', 
                             ha='center', va='center', transform=axes[1,1].transAxes)
                axes[1,1].set_title('Phân Tích Tăng Trưởng')
            
            plt.tight_layout()
            plt.show()
            
            # Summary statistics
            total_investment = sum(self.convert_to_base_currency(s['amount'], s['currency']) 
                                 for s in self.savings_data)
            avg_monthly = total_investment / len(set(f"{s['date'].year}-{s['date'].month:02d}" 
                                                   for s in self.savings_data)) if self.savings_data else 0
            
            print("\n" + "="*50)
            print("📊 THỐNG KÊ TỔNG QUAN:")
            print(f"💰 Tổng đầu tư: {self.format_currency(total_investment)}")
            print(f"📈 Trung bình/tháng: {self.format_currency(avg_monthly)}")
            print(f"🎯 Số loại đầu tư: {len(investment_by_type)}")
            print(f"📊 Tổng số giao dịch: {len(self.savings_data)}")
    
    def show_total_assets(self, button):
        """Hiển thị tổng tài sản hiện tại"""
        # Calculate total income (converted to base currency)
        total_income = 0
        for income in self.income_data:
            converted = self.convert_to_base_currency(income['amount'], income['currency'])
            total_income += converted
        
        # Calculate total expenses (converted to base currency)  
        total_expense = 0
        for expense in self.expense_data:
            converted = self.convert_to_base_currency(expense['amount'], expense['currency'])
            total_expense += converted
        
        # Calculate total investments (converted to base currency)
        total_investments = 0
        for saving in self.savings_data:
            converted = self.convert_to_base_currency(saving['amount'], saving['currency'])
            total_investments += converted
        
        # Calculate total outstanding loans (converted to base currency)
        total_loans_remaining = 0
        total_loans_original = 0
        for loan in self.loan_data:
            converted_remaining = self.convert_to_base_currency(loan['remaining_amount'], loan.get('currency', 'VND'))
            converted_original = self.convert_to_base_currency(loan['total_amount'], loan.get('currency', 'VND'))
            total_loans_remaining += converted_remaining
            total_loans_original += converted_original
        
        # Calculate net cash flow (income - expenses - loan payments)
        cash_balance = total_income - total_expense
        
        # Net worth calculation (cash + investments - remaining loans)
        net_worth = cash_balance + total_investments - total_loans_remaining
        
        with self.output:
            clear_output()
            print("="*70)
            print(f"💎 TỔNG QUAN TÀI SAN HIỆN TẠI (Tính bằng {self.base_currency})")
            print(f"📊 Tỷ giá hiện tại: 1 KRW = {self.exchange_rate:,.2f} VND")
            print("="*70)
            
            print("\n📈 NGUỒN THU:")
            print(f"   💰 Tổng thu nhập:         {self.format_currency(total_income):>20}")
            
            print("\n📉 KHOẢN CHI:")
            print(f"   💸 Tổng chi tiêu:         {self.format_currency(total_expense):>20}")
            print(f"   💵 Số dư tiền mặt:        {self.format_currency(cash_balance):>20}")
            
            print("\n💎 TÀI SẢN ĐẦU TƯ:")
            print(f"   🏆 Tổng đầu tư/tiết kiệm: {self.format_currency(total_investments):>20}")
            
            # Breakdown by investment type
            investment_by_type = {}
            for saving in self.savings_data:
                converted = self.convert_to_base_currency(saving['amount'], saving['currency'])
                if saving['type'] in investment_by_type:
                    investment_by_type[saving['type']] += converted
                else:
                    investment_by_type[saving['type']] = converted
            
            if investment_by_type:
                for inv_type, amount in sorted(investment_by_type.items(), key=lambda x: x[1], reverse=True):
                    percentage = (amount / total_investments) * 100 if total_investments > 0 else 0
                    print(f"      • {inv_type:.<25} {self.format_currency(amount):>15} ({percentage:.1f}%)")
            
            print("\n🏦 NỢ PHẢI TRẢ:")
            if total_loans_remaining > 0:
                print(f"   ❗ Tổng nợ còn lại:       {self.format_currency(total_loans_remaining):>20}")
                print(f"   📊 Tổng nợ ban đầu:      {self.format_currency(total_loans_original):>20}")
                
                # Show loan breakdown
                for loan in self.loan_data:
                    if loan['remaining_amount'] > 0:
                        converted_remaining = self.convert_to_base_currency(loan['remaining_amount'], loan.get('currency', 'VND'))
                        converted_original = self.convert_to_base_currency(loan['total_amount'], loan.get('currency', 'VND'))
                        paid_percentage = ((converted_original - converted_remaining) / converted_original) * 100 if converted_original > 0 else 0
                        
                        print(f"      • {loan['description'][:20]:.<20} {self.format_currency(converted_remaining):>15} "
                              f"(Đã trả {paid_percentage:.1f}%)")
            else:
                print(f"   ✅ Không có nợ:          {self.format_currency(0):>20}")
            
            print("\n" + "="*70)
            print(f"💰 TỔNG TÀI SẢN RÒNG:       {self.format_currency(net_worth):>20}")
            
            if net_worth > 0:
                print("✅ Bạn có tài sản ròng dương - tình hình tài chính tốt!")
            elif net_worth == 0:
                print("⚖️  Tài sản ròng cân bằng")
            else:
                print("⚠️  Tài sản ròng âm - cần cải thiện tình hình tài chính")
            
            # Additional insights
            print("\n📊 PHÂN TÍCH BỔ SUNG:")
            
            # Asset allocation
            total_assets = cash_balance + total_investments
            if total_assets > 0:
                cash_ratio = (cash_balance / total_assets) * 100 if cash_balance > 0 else 0
                investment_ratio = (total_investments / total_assets) * 100
                
                print(f"   💵 Tỷ lệ tiền mặt:        {cash_ratio:>18.1f}%")
                print(f"   📈 Tỷ lệ đầu tư:          {investment_ratio:>18.1f}%")
                
                # Recommendations based on ratios
                if cash_ratio > 70:
                    print("   💡 Khuyến nghị: Nên tăng đầu tư để tối ưu lợi nhuận")
                elif cash_ratio < 10:
                    print("   💡 Khuyến nghị: Nên duy trì quỹ khẩn cấp cao hơn")
                else:
                    print("   💡 Phân bổ tài sản hợp lý")
            
            # Debt to asset ratio
            if total_assets > 0 and total_loans_remaining > 0:
                debt_ratio = (total_loans_remaining / total_assets) * 100
                print(f"   🏦 Tỷ lệ nợ/tài sản:      {debt_ratio:>18.1f}%")
                
                if debt_ratio > 50:
                    print("   ⚠️  Khuyến nghị: Ưu tiên trả nợ để giảm rủi ro")
                elif debt_ratio > 30:
                    print("   💡 Khuyến nghị: Cân nhắc tăng tốc trả nợ")
                else:
                    print("   ✅ Mức nợ trong tầm kiểm soát")
            
            # Show in both currencies if different from base
            if self.base_currency != 'KRW':
                net_worth_krw = net_worth / self.exchange_rate if self.exchange_rate > 0 else 0
                print(f"\n🔄 TỔNG TÀI SẢN RÒNG (KRW): {net_worth_krw:>15,.0f}₩")
            
            if self.base_currency != 'VND':
                net_worth_vnd = net_worth * self.exchange_rate
                print(f"\n🔄 TỔNG TÀI SẢN RÒNG (VND): {net_worth_vnd:>15,.0f}đ")
            
            print("="*70)
    
    def show_cash_flow(self, button):
        selected_month = self.month_filter.value
        
        # Tính toán các khoản thu chi (đã convert sang base currency)
        income_filtered = self.filter_data_by_month(self.income_data, selected_month)
        expense_filtered = self.filter_data_by_month(self.expense_data, selected_month)
        savings_filtered = self.filter_data_by_month(self.savings_data, selected_month)
        
        total_income = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                          for item in income_filtered)
        total_expense = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                           for item in expense_filtered)
        total_savings = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                           for item in savings_filtered)
        
        # Tính khoản vay phải trả
        fixed_loan, flexible_loan = self.calculate_monthly_loan_payments(selected_month)
        total_loan_payment = fixed_loan + flexible_loan
        
        # Tính dòng tiền
        basic_balance = total_income - total_expense  # Số dư sau chi tiêu cơ bản
        after_loan = basic_balance - total_loan_payment  # Số dư sau trả nợ
        final_balance = after_loan - total_savings  # Số dư cuối cùng
        
        with self.output:
            clear_output()
            print("="*60)
            print(f"💰 DÒNG TIỀN VÀ PHÂN BỔ THÁNG {selected_month}")
            print(f"💱 Hiển thị bằng: {self.base_currency} (Tỷ giá: 1 KRW = {self.exchange_rate:,.2f} VND)")
            print("="*60)
            
            # Thu nhập
            print(f"📈 TỔNG THU NHẬP:           {self.format_currency(total_income):>15}")
            print("-"*50)
            
            # Chi tiêu cơ bản
            print(f"📊 Chi tiêu sinh hoạt:      {self.format_currency(total_expense):>15}")
            print(f"   → Số dư sau chi cơ bản:  {self.format_currency(basic_balance):>15}")
            print("-"*50)
            
            # Trả nợ
            print("🏦 KHOẢN VAY PHẢI TRẢ:")
            if fixed_loan > 0:
                print(f"   • Vay cố định hàng tháng: {self.format_currency(fixed_loan):>15}")
            if flexible_loan > 0:
                print(f"   • Vay linh hoạt đã trả:   {self.format_currency(flexible_loan):>15}")
            print(f"   → Tổng trả nợ tháng này:  {self.format_currency(total_loan_payment):>15}")
            print(f"   → Số dư sau trả nợ:       {self.format_currency(after_loan):>15}")
            print("-"*50)
            
            # Tiết kiệm/Đầu tư
            if total_savings > 0:
                print(f"💎 Tiết kiệm & Đầu tư:      {self.format_currency(total_savings):>15}")
                print(f"   → Số dư sau tiết kiệm:    {self.format_currency(final_balance):>15}")
            else:
                print(f"💎 Tiết kiệm & Đầu tư:      {self.format_currency(0):>15}")
                final_balance = after_loan
            
            print("="*60)
            
            # Kết luận và khuyến nghị
            if final_balance > 0:
                print(f"✅ SỐ DƯ CÓ THỂ PHÂN BỔ:   {self.format_currency(final_balance):>15}")
                print("\n💡 KHUYẾN NGHỊ PHÂN BỔ:")
                
                # Gợi ý phân bổ theo nguyên tắc 50-30-20
                emergency_fund = final_balance * 0.3
                investment = final_balance * 0.5
                extra_saving = final_balance * 0.2
                
                print(f"   📦 Quỹ khẩn cấp (30%):    {self.format_currency(emergency_fund):>15}")
                print(f"   📈 Đầu tư (50%):          {self.format_currency(investment):>15}") 
                print(f"   💰 Tiết kiệm thêm (20%):  {self.format_currency(extra_saving):>15}")
                
            elif final_balance == 0:
                print(f"⚖️  SỐ DƯ CUỐI THÁNG:       {self.format_currency(final_balance):>15}")
                print("\n💡 Bạn đã cân bằng thu chi tốt!")
            else:
                print(f"❌ THÂM HỤT:               {self.format_currency(final_balance):>15}")
                print("\n⚠️  CẢNH BÁO: Chi tiêu vượt thu nhập!")
                print("💡 Khuyến nghị:")
                print("   • Xem xét cắt giảm chi tiêu không cần thiết")
                print("   • Tìm thêm nguồn thu nhập")
                print("   • Hoãn các khoản đầu tư/tiết kiệm")
    
    def show_loan_status(self, button):
        if not self.loan_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu khoản vay nào!")
            return
        
        with self.output:
            clear_output()
            print("="*70)
            print("🏦 TÌNH TRẠNG CÁC KHOẢN VAY")
            print(f"💱 Hiển thị bằng: {self.base_currency}")
            print("="*70)
            
            total_remaining = 0
            total_monthly_fixed = 0
            
            for i, loan in enumerate(self.loan_data, 1):
                loan_currency = loan.get('currency', 'VND')
                
                # Convert amounts to base currency for display
                total_converted = self.convert_to_base_currency(loan['total_amount'], loan_currency)
                paid_converted = self.convert_to_base_currency(loan['paid_amount'], loan_currency)
                remaining_converted = self.convert_to_base_currency(loan['remaining_amount'], loan_currency)
                monthly_converted = self.convert_to_base_currency(loan['monthly_payment'], loan_currency)
                
                print(f"\n{i}. {loan['description']} ({loan['type']})")
                print(f"   💰 Tiền tệ gốc:    {loan_currency}")
                print(f"   📊 Tổng nợ:        {self.format_currency(total_converted):>15}")
                print(f"   ✅ Đã trả:        {self.format_currency(paid_converted):>15}")
                print(f"   ❗ Còn lại:       {self.format_currency(remaining_converted):>15}")
                
                if loan['remaining_amount'] > 0:
                    progress = (loan['paid_amount'] / loan['total_amount']) * 100
                    print(f"   📈 Tiến độ:       {progress:>15.1f}%")
                    
                    if loan['is_fixed']:
                        print(f"   💰 Trả/tháng:     {self.format_currency(monthly_converted):>15} (cố định)")
                        total_monthly_fixed += monthly_converted
                        
                        # Ước tính thời gian trả hết
                        if loan['monthly_payment'] > 0:
                            months_left = loan['remaining_amount'] / loan['monthly_payment']
                            print(f"   ⏰ Còn ~{months_left:.1f} tháng để trả hết")
                    else:
                        print(f"   💰 Trả linh hoạt (gộp đến đủ rồi trả)")
                else:
                    print(f"   🎉 ĐÃ TRẢ HẾT!")
                
                total_remaining += remaining_converted
                print("-" * 50)
            
            print(f"\n📋 TỔNG HỢP:")
            print(f"   💸 Tổng nợ còn lại:       {self.format_currency(total_remaining):>15}")
            print(f"   🏦 Phải trả cố định/tháng: {self.format_currency(total_monthly_fixed):>15}")
            
            # Tính vay linh hoạt
            flexible_loans = [loan for loan in self.loan_data 
                            if not loan['is_fixed'] and loan['remaining_amount'] > 0]
            if flexible_loans:
                total_flexible = sum(self.convert_to_base_currency(loan['remaining_amount'], loan.get('currency', 'VND')) 
                                   for loan in flexible_loans)
                print(f"   🤝 Nợ linh hoạt:          {self.format_currency(total_flexible):>15}")
    
    def show_summary(self, button):
        selected_month = self.month_filter.value
        
        income_filtered = self.filter_data_by_month(self.income_data, selected_month)
        expense_filtered = self.filter_data_by_month(self.expense_data, selected_month)
        
        total_income = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                          for item in income_filtered)
        total_expense = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                           for item in expense_filtered)
        basic_balance = total_income - total_expense
        
        fixed_loan, flexible_loan = self.calculate_monthly_loan_payments(selected_month)
        
        with self.output:
            clear_output()
            print("="*50)
            print(f"📊 BÁO CÁO TỔNG QUAN THÁNG {selected_month}")
            print(f"💱 Hiển thị bằng: {self.base_currency}")
            print("="*50)
            print(f"💰 Tổng thu nhập:    {self.format_currency(total_income)}")
            print(f"💸 Tổng chi tiêu:    {self.format_currency(total_expense)}")
            print(f"🏦 Trả nợ cố định:   {self.format_currency(fixed_loan)}")
            print(f"🤝 Trả nợ linh hoạt: {self.format_currency(flexible_loan)}")
            print("-"*30)
            
            net_balance = basic_balance - fixed_loan - flexible_loan
            if net_balance >= 0:
                print(f"✅ Số dư khả dụng:   +{self.format_currency(net_balance)}")
            else:
                print(f"❌ Thâm hụt:         {self.format_currency(net_balance)}")
            print("="*50)
            
            if expense_filtered:
                print("\n📋 CHI TIẾT CHI PHÍ THEO DANH MỤC:")
                
                # Group expenses by category and convert to base currency
                category_summary = {}
                for expense in expense_filtered:
                    converted_amount = self.convert_to_base_currency(expense['amount'], expense['currency'])
                    if expense['category'] in category_summary:
                        category_summary[expense['category']] += converted_amount
                    else:
                        category_summary[expense['category']] = converted_amount
                
                # Sort by amount descending
                sorted_categories = sorted(category_summary.items(), key=lambda x: x[1], reverse=True)
                
                for category, amount in sorted_categories:
                    percentage = (amount / total_expense) * 100 if total_expense > 0 else 0
                    print(f"  • {category}: {self.format_currency(amount)} ({percentage:.1f}%)")
    
    def show_charts(self, button):
        selected_month = self.month_filter.value
        
        income_filtered = self.filter_data_by_month(self.income_data, selected_month)
        expense_filtered = self.filter_data_by_month(self.expense_data, selected_month)
        savings_filtered = self.filter_data_by_month(self.savings_data, selected_month)
        
        if not income_filtered and not expense_filtered and not savings_filtered:
            with self.output:
                clear_output()
                print("❌ Không có dữ liệu để hiển thị biểu đồ!")
            return
        
        with self.output:
            clear_output()
            
            # Tạo figure với subplots
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle(f'Báo Cáo Tài Chính Chi Tiết Tháng {selected_month} (Tính bằng {self.base_currency})', 
                        fontsize=16, fontweight='bold')
            
            # 1. Biểu đồ dòng tiền tổng quan
            total_income = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                              for item in income_filtered)
            total_expense = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                               for item in expense_filtered)
            total_savings = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                               for item in savings_filtered)
            fixed_loan, flexible_loan = self.calculate_monthly_loan_payments(selected_month)
            
            categories = ['Thu nhập', 'Chi tiêu', 'Trả nợ\ncố định', 'Trả nợ\nlinh hoạt', 'Tiết kiệm\n& ĐT']
            amounts = [total_income, -total_expense, -fixed_loan, -flexible_loan, -total_savings]
            colors = ['#28A745', '#DC3545', '#FF6B35', '#FFA500', '#6F42C1']
            
            bars = axes[0,0].bar(categories, amounts, color=colors)
            axes[0,0].set_title('Dòng Tiền Tổng Quan')
            axes[0,0].set_ylabel(f'Số tiền ({self.base_currency})')
            axes[0,0].axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Thêm giá trị lên cột
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                axes[0,0].text(bar.get_x() + bar.get_width()/2., 
                             height + np.sign(height) * max(abs(a) for a in amounts) * 0.01,
                             f'{abs(amount):,.0f}', ha='center', va='bottom' if height >= 0 else 'top')
            
            # 2. Biểu đồ tròn chi phí theo danh mục
            if expense_filtered:
                category_summary = {}
                for expense in expense_filtered:
                    converted_amount = self.convert_to_base_currency(expense['amount'], expense['currency'])
                    if expense['category'] in category_summary:
                        category_summary[expense['category']] += converted_amount
                    else:
                        category_summary[expense['category']] = converted_amount
                
                axes[0,1].pie(category_summary.values(), labels=category_summary.keys(), autopct='%1.1f%%')
                axes[0,1].set_title('Phân Bố Chi Phí Theo Danh Mục')
            else:
                axes[0,1].text(0.5, 0.5, 'Không có dữ liệu chi phí', ha='center', va='center')
                axes[0,1].set_title('Phân Bố Chi Phí Theo Danh Mục')
            
            # 3. Tình trạng các khoản vay
            if self.loan_data:
                loan_names = []
                remaining_amounts = []
                
                for loan in self.loan_data:
                    if loan['remaining_amount'] > 0:
                        loan_names.append(loan['description'][:20] + '...' if len(loan['description']) > 20 
                                        else loan['description'])
                        converted_remaining = self.convert_to_base_currency(loan['remaining_amount'], 
                                                                          loan.get('currency', 'VND'))
                        remaining_amounts.append(converted_remaining)
                
                if loan_names:
                    axes[0,2].barh(loan_names, remaining_amounts, color='#FF6B35')
                    axes[0,2].set_title('Nợ Còn Lại Theo Khoản Vay')
                    axes[0,2].set_xlabel(f'Số tiền ({self.base_currency})')
                else:
                    axes[0,2].text(0.5, 0.5, 'Đã trả hết nợ!', ha='center', va='center')
                    axes[0,2].set_title('Nợ Còn Lại Theo Khoản Vay')
            else:
                axes[0,2].text(0.5, 0.5, 'Không có khoản vay', ha='center', va='center')
                axes[0,2].set_title('Nợ Còn Lại Theo Khoản Vay')
            
            # 4. Chi phí theo ngày
            if expense_filtered:
                daily_expense = {}
                for expense in expense_filtered:
                    expense_date = expense['date']
                    converted_amount = self.convert_to_base_currency(expense['amount'], expense['currency'])
                    if expense_date in daily_expense:
                        daily_expense[expense_date] += converted_amount
                    else:
                        daily_expense[expense_date] = converted_amount
                
                dates = sorted(daily_expense.keys())
                amounts = [daily_expense[date] for date in dates]
                
                axes[1,0].plot(dates, amounts, marker='o', 
                             color='#DC3545', linewidth=2, markersize=6)
                axes[1,0].set_title('Chi Phí Theo Ngày')
                axes[1,0].set_ylabel(f'Số tiền ({self.base_currency})')
                axes[1,0].tick_params(axis='x', rotation=45)
            else:
                axes[1,0].text(0.5, 0.5, 'Không có dữ liệu chi phí', ha='center', va='center')
                axes[1,0].set_title('Chi Phí Theo Ngày')
            
            # 5. Tiết kiệm & Đầu tư theo loại
            if savings_filtered:
                savings_summary = {}
                for saving in savings_filtered:
                    converted_amount = self.convert_to_base_currency(saving['amount'], saving['currency'])
                    if saving['type'] in savings_summary:
                        savings_summary[saving['type']] += converted_amount
                    else:
                        savings_summary[saving['type']] = converted_amount
                
                savings_types = list(savings_summary.keys())
                savings_amounts = list(savings_summary.values())
                
                axes[1,1].barh(savings_types, savings_amounts, color='#6F42C1')
                axes[1,1].set_title('Tiết Kiệm & Đầu Tư Theo Loại')
                axes[1,1].set_xlabel(f'Số tiền ({self.base_currency})')
            else:
                axes[1,1].text(0.5, 0.5, 'Không có dữ liệu tiết kiệm', ha='center', va='center')
                axes[1,1].set_title('Tiết Kiệm & Đầu Tư Theo Loại')
            
            # 6. Biểu đồ waterfall - dòng tiền tích lũy
            waterfall_categories = ['Thu nhập', 'Chi tiêu', 'Trả nợ', 'Tiết kiệm', 'Số dư']
            waterfall_values = [total_income, -total_expense, -(fixed_loan + flexible_loan), 
                              -total_savings, total_income - total_expense - fixed_loan - flexible_loan - total_savings]
            
            # Tính giá trị tích lũy
            cumulative = [0]
            for i, val in enumerate(waterfall_values[:-1]):
                cumulative.append(cumulative[-1] + val)
            
            # Vẽ waterfall
            for i in range(len(waterfall_categories)-1):
                if waterfall_values[i] > 0:
                    axes[1,2].bar(i, waterfall_values[i], bottom=cumulative[i], color='#28A745', alpha=0.7)
                else:
                    axes[1,2].bar(i, abs(waterfall_values[i]), bottom=cumulative[i+1], color='#DC3545', alpha=0.7)
            
            # Vẽ cột cuối (số dư)
            final_color = '#28A745' if waterfall_values[-1] >= 0 else '#DC3545'
            axes[1,2].bar(len(waterfall_categories)-1, abs(waterfall_values[-1]), color=final_color, alpha=0.7)
            
            axes[1,2].set_title('Waterfall - Dòng Tiền Tích Lũy')
            axes[1,2].set_xticks(range(len(waterfall_categories)))
            axes[1,2].set_xticklabels(waterfall_categories, rotation=45)
            axes[1,2].axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            plt.tight_layout()
            plt.show()
    
    def export_to_excel(self, button):
        if not any([self.income_data, self.expense_data, self.loan_data, self.savings_data]):
            with self.output:
                clear_output()
                print("❌ Không có dữ liệu để xuất!")
            return
        
        try:
            filename = f'BaoCaoThuChi_ChiTiet_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Sheet thu nhập
                if self.income_data:
                    income_df = pd.DataFrame(self.income_data)
                    # Add converted amounts
                    income_df['amount_base_currency'] = income_df.apply(
                        lambda row: self.convert_to_base_currency(row['amount'], row['currency']), axis=1
                    )
                    income_df['base_currency'] = self.base_currency
                    income_df.to_excel(writer, sheet_name='Thu Nhập', index=False)
                
                # Sheet chi phí
                if self.expense_data:
                    expense_df = pd.DataFrame(self.expense_data)
                    expense_df['amount_base_currency'] = expense_df.apply(
                        lambda row: self.convert_to_base_currency(row['amount'], row['currency']), axis=1
                    )
                    expense_df['base_currency'] = self.base_currency
                    expense_df.to_excel(writer, sheet_name='Chi Phí', index=False)
                
                # Sheet vay nợ
                if self.loan_data:
                    loan_df = pd.DataFrame([
                        {
                            'Loại vay': loan['type'],
                            'Mô tả': loan['description'],
                            'Tổng nợ': loan['total_amount'],
                            'Đã trả': loan['paid_amount'],
                            'Còn lại': loan['remaining_amount'],
                            'Tiền tệ': loan.get('currency', 'VND'),
                            'Tổng nợ (base)': self.convert_to_base_currency(loan['total_amount'], loan.get('currency', 'VND')),
                            'Đã trả (base)': self.convert_to_base_currency(loan['paid_amount'], loan.get('currency', 'VND')),
                            'Còn lại (base)': self.convert_to_base_currency(loan['remaining_amount'], loan.get('currency', 'VND')),
                            'Tiền tệ báo cáo': self.base_currency,
                            'Trả hàng tháng': loan['monthly_payment'],
                            'Loại thanh toán': 'Cố định' if loan['is_fixed'] else 'Linh hoạt',
                            'Ngày tạo': loan['created_date'],
                            'Cập nhật lần cuối': loan['last_updated']
                        } for loan in self.loan_data
                    ])
                    loan_df.to_excel(writer, sheet_name='Vay Nợ', index=False)
                
                # Sheet tiết kiệm
                if self.savings_data:
                    savings_df = pd.DataFrame(self.savings_data)
                    savings_df['amount_base_currency'] = savings_df.apply(
                        lambda row: self.convert_to_base_currency(row['amount'], row['currency']), axis=1
                    )
                    savings_df['base_currency'] = self.base_currency
                    savings_df.to_excel(writer, sheet_name='Tiết Kiệm & Đầu Tư', index=False)
                
                # Sheet tổng hợp theo tháng
                summary_data = []
                for month_option in self.get_month_options():
                    month_name, month_value = month_option
                    income_filtered = self.filter_data_by_month(self.income_data, month_value)
                    expense_filtered = self.filter_data_by_month(self.expense_data, month_value)
                    savings_filtered = self.filter_data_by_month(self.savings_data, month_value)
                    
                    total_income = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                                      for item in income_filtered)
                    total_expense = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                                       for item in expense_filtered)
                    total_savings = sum(self.convert_to_base_currency(item['amount'], item['currency']) 
                                       for item in savings_filtered)
                    fixed_loan, flexible_loan = self.calculate_monthly_loan_payments(month_value)
                    
                    if any([total_income, total_expense, total_savings, fixed_loan, flexible_loan]):
                        net_balance = total_income - total_expense - fixed_loan - flexible_loan - total_savings
                        summary_data.append({
                            'Tháng': month_name,
                            'Thu nhập': total_income,
                            'Chi tiêu': total_expense,
                            'Trả nợ cố định': fixed_loan,
                            'Trả nợ linh hoạt': flexible_loan,
                            'Tiết kiệm & ĐT': total_savings,
                            'Số dư cuối': net_balance,
                            'Tiền tệ': self.base_currency,
                            'Tỷ giá (1 KRW)': self.exchange_rate
                        })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Tổng Hợp Theo Tháng', index=False)
                
                # Sheet phân tích đầu tư
                if self.savings_data:
                    investment_analysis = []
                    investment_summary = {}
                    
                    for saving in self.savings_data:
                        key = f"{saving['type']} - {saving['description']}"
                        converted_amount = self.convert_to_base_currency(saving['amount'], saving['currency'])
                        
                        if key in investment_summary:
                            investment_summary[key]['total'] += converted_amount
                            investment_summary[key]['count'] += 1
                        else:
                            investment_summary[key] = {
                                'type': saving['type'],
                                'description': saving['description'],
                                'total': converted_amount,
                                'count': 1
                            }
                    
                    for key, data in investment_summary.items():
                        investment_analysis.append({
                            'Loại đầu tư': data['type'],
                            'Mô tả': data['description'],
                            'Tổng giá trị': data['total'],
                            'Số giao dịch': data['count'],
                            'Trung bình/giao dịch': data['total'] / data['count'],
                            'Tiền tệ': self.base_currency
                        })
                    
                    if investment_analysis:
                        investment_df = pd.DataFrame(investment_analysis)
                        investment_df = investment_df.sort_values('Tổng giá trị', ascending=False)
                        investment_df.to_excel(writer, sheet_name='Phân Tích Đầu Tư', index=False)
            
            with self.output:
                clear_output()
                print(f"✅ Đã xuất báo cáo chi tiết ra file: {filename}")
                print("📊 File bao gồm các sheet:")
                print("   • Thu Nhập (có chuyển đổi tiền tệ)")
                print("   • Chi Phí (có chuyển đổi tiền tệ)") 
                print("   • Vay Nợ (có chuyển đổi tiền tệ)")
                print("   • Tiết Kiệm & Đầu Tư (có chuyển đổi tiền tệ)")
                print("   • Tổng Hợp Theo Tháng")
                print("   • Phân Tích Đầu Tư")
                print(f"💱 Tỷ giá sử dụng: 1 KRW = {self.exchange_rate:,.2f} VND")
                print(f"📊 Tiền tệ báo cáo: {self.base_currency}")
                
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi xuất file: {str(e)}")
    
    def save_data_silent(self):
        """Lưu dữ liệu tự động mà không hiển thị thông báo"""
        try:
            self.save_data_to_files()
            self.save_settings()  # Lưu cả settings
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu: {str(e)}")
    
    def save_data(self, button):
        """Lưu dữ liệu thủ công với thông báo"""
        try:
            self.save_data_to_files()
            self.save_settings()
            with self.output:
                clear_output()
                print("✅ Đã lưu tất cả dữ liệu vào file CSV!")
                print("📁 Các file được tạo:")
                for data_type, filename in self.data_files.items():
                    print(f"   • {filename}")
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi lưu dữ liệu: {str(e)}")
    
    def save_data_to_files(self):
        """Lưu dữ liệu vào các file CSV"""
        # Lưu thu nhập
        if self.income_data:
            df = pd.DataFrame(self.income_data)
            df['date'] = df['date'].astype(str)  # Convert date to string for CSV
            df.to_csv(self.data_files['income'], index=False, encoding='utf-8-sig')
        
        # Lưu chi phí
        if self.expense_data:
            df = pd.DataFrame(self.expense_data)
            df['date'] = df['date'].astype(str)
            df.to_csv(self.data_files['expense'], index=False, encoding='utf-8-sig')
        
        # Lưu vay nợ (phức tạp hơn vì có nested data)
        if self.loan_data:
            loan_rows = []
            for loan in self.loan_data:
                base_row = {
                    'type': loan['type'],
                    'description': loan['description'],
                    'total_amount': loan['total_amount'],
                    'monthly_payment': loan['monthly_payment'],
                    'paid_amount': loan['paid_amount'],
                    'remaining_amount': loan['remaining_amount'],
                    'currency': loan.get('currency', 'VND'),
                    'is_fixed': loan['is_fixed'],
                    'created_date': str(loan['created_date']),
                    'last_updated': str(loan['last_updated'])
                }
                
                # Lưu lịch sử thanh toán như JSON string
                if loan['payment_history']:
                    base_row['payment_history'] = str(loan['payment_history'])
                else:
                    base_row['payment_history'] = '[]'
                
                loan_rows.append(base_row)
            
            df = pd.DataFrame(loan_rows)
            df.to_csv(self.data_files['loan'], index=False, encoding='utf-8-sig')
        
        # Lưu tiết kiệm
        if self.savings_data:
            df = pd.DataFrame(self.savings_data)
            df['date'] = df['date'].astype(str)
            df.to_csv(self.data_files['savings'], index=False, encoding='utf-8-sig')
    
    def load_data(self):
        """Tải dữ liệu từ file khi khởi động"""
        try:
            # Load settings first
            self.load_settings()
            
            # Tải thu nhập
            try:
                df = pd.read_csv(self.data_files['income'], encoding='utf-8-sig')
                self.income_data = []
                for _, row in df.iterrows():
                    self.income_data.append({
                        'date': pd.to_datetime(row['date']).date(),
                        'source': row['source'],
                        'amount': float(row['amount']),
                        'currency': row.get('currency', 'VND')
                    })
                print(f"✅ Đã load {len(self.income_data)} bản ghi thu nhập")
            except FileNotFoundError:
                print("📝 Chưa có file dữ liệu thu nhập")
            except Exception as e:
                print(f"⚠️  Lỗi khi load thu nhập: {str(e)}")
            
            # Tải chi phí
            try:
                df = pd.read_csv(self.data_files['expense'], encoding='utf-8-sig')
                self.expense_data = []
                for _, row in df.iterrows():
                    self.expense_data.append({
                        'date': pd.to_datetime(row['date']).date(),
                        'category': row['category'],
                        'description': row['description'],
                        'amount': float(row['amount']),
                        'currency': row.get('currency', 'VND')
                    })
                print(f"✅ Đã load {len(self.expense_data)} bản ghi chi phí")
            except FileNotFoundError:
                print("📝 Chưa có file dữ liệu chi phí")
            except Exception as e:
                print(f"⚠️  Lỗi khi load chi phí: {str(e)}")
            
            # Tải vay nợ
            try:
                df = pd.read_csv(self.data_files['loan'], encoding='utf-8-sig')
                self.loan_data = []
                for _, row in df.iterrows():
                    # Parse payment history từ string
                    try:
                        payment_history = eval(row['payment_history']) if row['payment_history'] != '[]' else []
                        # Convert date strings back to date objects trong payment history
                        for payment in payment_history:
                            if 'date' in payment and isinstance(payment['date'], str):
                                payment['date'] = pd.to_datetime(payment['date']).date()
                    except:
                        payment_history = []
                    
                    self.loan_data.append({
                        'type': row['type'],
                        'description': row['description'],
                        'total_amount': float(row['total_amount']),
                        'monthly_payment': float(row['monthly_payment']),
                        'paid_amount': float(row['paid_amount']),
                        'remaining_amount': float(row['remaining_amount']),
                        'currency': row.get('currency', 'VND'),
                        'is_fixed': bool(row['is_fixed']),
                        'created_date': pd.to_datetime(row['created_date']).date(),
                        'last_updated': pd.to_datetime(row['last_updated']).date(),
                        'payment_history': payment_history
                    })
                print(f"✅ Đã load {len(self.loan_data)} khoản vay")
            except FileNotFoundError:
                print("📝 Chưa có file dữ liệu vay nợ")
            except Exception as e:
                print(f"⚠️  Lỗi khi load vay nợ: {str(e)}")
            
            # Tải tiết kiệm
            try:
                df = pd.read_csv(self.data_files['savings'], encoding='utf-8-sig')
                self.savings_data = []
                for _, row in df.iterrows():
                    self.savings_data.append({
                        'date': pd.to_datetime(row['date']).date(),
                        'type': row['type'],
                        'description': row['description'],
                        'amount': float(row['amount']),
                        'currency': row.get('currency', 'VND')
                    })
                print(f"✅ Đã load {len(self.savings_data)} bản ghi tiết kiệm/đầu tư")
            except FileNotFoundError:
                print("📝 Chưa có file dữ liệu tiết kiệm")
            except Exception as e:
                print(f"⚠️  Lỗi khi load tiết kiệm: {str(e)}")
                
        except Exception as e:
            print(f"❌ Lỗi tổng quát khi tải dữ liệu: {str(e)}")
    
    def load_data_manual(self, button):
        """Tải lại dữ liệu thủ công"""
        try:
            self.load_data()
            # Cập nhật dropdown sau khi load
            self.update_loan_dropdown()
            self.update_savings_dropdown()
            
            with self.output:
                clear_output()
                print("✅ Đã tải lại dữ liệu từ file CSV!")
                print(f"📊 Thu nhập: {len(self.income_data)} bản ghi")
                print(f"📊 Chi phí: {len(self.expense_data)} bản ghi")
                print(f"📊 Vay nợ: {len(self.loan_data)} bản ghi")
                print(f"📊 Tiết kiệm: {len(self.savings_data)} bản ghi")
                print(f"💱 Tỷ giá: 1 KRW = {self.exchange_rate:,.2f} VND")
                print(f"📊 Tiền tệ báo cáo: {self.base_currency}")
                print("🔄 Đã cập nhật dropdown danh sách")
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi tải dữ liệu: {str(e)}")
    
    def clear_all_data(self, button):
        """Xóa toàn bộ dữ liệu"""
        import os
        
        try:
            # Xóa dữ liệu trong bộ nhớ
            self.income_data = []
            self.expense_data = []
            self.loan_data = []
            self.savings_data = []
            
            # Reset settings
            self.exchange_rate = 1.0
            self.base_currency = 'VND'
            self.exchange_rate_input.value = 1.0
            self.base_currency_dropdown.value = 'VND'
            
            # Cập nhật dropdown
            self.update_loan_dropdown()
            self.update_savings_dropdown()
            
            # Xóa file CSV
            for filename in self.data_files.values():
                if os.path.exists(filename):
                    os.remove(filename)
            
            with self.output:
                clear_output()
                print("⚠️  Đã xóa toàn bộ dữ liệu và file CSV!")
                print("📝 Bạn có thể bắt đầu nhập dữ liệu mới.")
                print("🔄 Đã reset tất cả dropdown và cài đặt")
                print("💱 Tỷ giá đã reset về: 1 KRW = 1 VND")
                print("📊 Tiền tệ báo cáo đã reset về: VND")
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi xóa dữ liệu: {str(e)}")
    
    def display(self):
        return self.main_layout

# Tạo và hiển thị ứng dụng
def create_finance_tracker():
    """
    Hàm khởi tạo ứng dụng giám sát thu chi với quản lý vay nợ, phân bổ tiết kiệm và hỗ trợ đa tiền tệ
    
    Tính năng mới:
    - Hỗ trợ đa tiền tệ (VND/KRW) với tỷ giá tùy chỉnh
    - Phân tích đầu tư chi tiết với biểu đồ
    - Tính tổng tài sản hiện tại quy đổi
    - Xuất báo cáo Excel với chuyển đổi tiền tệ
    """
    tracker = MonthlyFinanceTracker()
    return tracker.display()

# Chạy ứng dụng
finance_app = create_finance_tracker()
display(finance_app)
