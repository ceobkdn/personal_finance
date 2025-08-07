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
        
        # File paths cho lưu dữ liệu
        self.data_files = {
            'income': 'finance_data_income.csv',
            'expense': 'finance_data_expense.csv', 
            'loan': 'finance_data_loan.csv',
            'savings': 'finance_data_savings.csv'
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
        self.add_income_btn.on_click(self.add_income)
        self.add_expense_btn.on_click(self.add_expense)
        self.add_loan_btn.on_click(self.add_loan)
        self.pay_loan_btn.on_click(self.pay_loan)
        self.add_savings_btn.on_click(self.add_savings)
        self.show_summary_btn.on_click(self.show_summary)
        self.show_cash_flow_btn.on_click(self.show_cash_flow)
        self.show_loan_status_btn.on_click(self.show_loan_status)
        self.show_charts_btn.on_click(self.show_charts)
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
        # Income section
        income_box = widgets.VBox([
            self.income_header,
            widgets.HBox([self.income_source, self.income_amount]),
            widgets.HBox([self.income_date, self.add_income_btn])
        ])
        
        # Expense section
        expense_box = widgets.VBox([
            self.expense_header,
            widgets.HBox([self.expense_category, self.expense_description]),
            widgets.HBox([self.expense_amount, self.expense_date]),
            self.add_expense_btn
        ])
        
        # Loan section
        loan_box = widgets.VBox([
            self.loan_header,
            widgets.HTML("<h4 style='color: #666; margin: 5px 0;'>🔍 Chọn khoản vay có sẵn:</h4>"),
            widgets.HBox([self.existing_loan_dropdown, self.load_loan_btn]),
            widgets.HTML("<h4 style='color: #666; margin: 15px 0 5px 0;'>📝 Thông tin khoản vay:</h4>"),
            widgets.HBox([self.loan_type, self.loan_description]),
            widgets.HBox([self.loan_total, self.loan_monthly]),
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
            widgets.HBox([self.savings_amount, self.savings_date]),
            widgets.HBox([self.add_savings_btn, self.update_savings_btn, self.delete_savings_btn])
        ])
        
        # Analysis section
        analysis_box = widgets.VBox([
            self.analysis_header,
            self.month_filter,
            widgets.HBox([self.show_summary_btn, self.show_cash_flow_btn]),
            widgets.HBox([self.show_loan_status_btn, self.show_charts_btn]),
            widgets.HTML("<hr style='margin: 10px 0;'>"),
            widgets.HTML("<h4 style='color: #6C757D; margin: 5px 0;'>🗃️ QUẢN LÝ DỮ LIỆU</h4>"),
            widgets.HBox([self.save_data_btn, self.load_data_btn, self.clear_data_btn, self.export_btn])
        ])
        
        # Main layout with tabs for better organization
        tab1 = widgets.VBox([widgets.HBox([income_box, expense_box])])
        tab2 = widgets.VBox([widgets.HBox([loan_box, savings_box])])
        tab3 = analysis_box
        
        tabs = widgets.Tab()
        tabs.children = [tab1, tab2, tab3]
        tabs.titles = ['Thu Chi Thường', 'Vay Nợ & Tiết Kiệm', 'Phân Tích']
        
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
                'amount': self.income_amount.value
            })
            
            # Auto-save after adding data
            self.save_data_silent()
            
            with self.output:
                clear_output()
                print(f"✅ Đã thêm thu nhập: {self.income_source.value} - {self.income_amount.value:,.0f}đ")
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
                'amount': self.expense_amount.value
            })
            
            # Auto-save after adding data
            self.save_data_silent()
            
            with self.output:
                clear_output()
                print(f"✅ Đã thêm chi phí: {self.expense_description.value} - {self.expense_amount.value:,.0f}đ")
                print("💾 Dữ liệu đã được lưu tự động")
            
            # Clear inputs
            self.expense_description.value = ""
            self.expense_amount.value = 0.0
        else:
            with self.output:
                clear_output()
                print("❌ Vui lòng nhập đầy đủ thông tin chi phí!")
    
    def update_loan_dropdown(self):
        """Cập nhật dropdown danh sách khoản vay"""
        options = [('-- Tạo khoản vay mới --', '')]
        for i, loan in enumerate(self.loan_data):
            # Tính toán remaining amount để đảm bảo chính xác
            remaining = loan['total_amount'] - loan['paid_amount']
            loan['remaining_amount'] = max(0, remaining)  # Cập nhật lại remaining_amount
            
            status = "Đã trả hết" if remaining <= 0 else f"Còn: {remaining:,.0f}đ"
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
        # Group savings by type and description
        savings_summary = {}
        for i, saving in enumerate(self.savings_data):
            key = f"{saving['type']} - {saving['description']}"
            if key in savings_summary:
                savings_summary[key]['total'] += saving['amount']
                savings_summary[key]['indices'].append(i)
            else:
                savings_summary[key] = {
                    'total': saving['amount'],
                    'indices': [i],
                    'type': saving['type'],
                    'description': saving['description']
                }
        
        for key, data in savings_summary.items():
            display_name = f"{key} - Tổng: {data['total']:,.0f}đ"
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
                    'is_fixed': self.is_fixed_payment.value,
                    'created_date': date.today(),
                    'last_updated': date.today(),
                    'payment_history': []
                })
                message = f"✅ Đã thêm khoản vay: {self.loan_description.value}"
            
            # Auto-save after adding/updating loan
            self.save_data_silent()
            self.update_loan_dropdown()  # Cập nhật dropdown
            
            with self.output:
                clear_output()
                print(message)
                print(f"   💰 Tổng nợ: {self.loan_total.value:,.0f}đ")
                print(f"   📅 Trả hàng tháng: {self.loan_monthly.value:,.0f}đ ({'Cố định' if self.is_fixed_payment.value else 'Linh hoạt'})")
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
            self.is_fixed_payment.value = loan['is_fixed']
            
            with self.output:
                clear_output()
                print(f"✅ Đã tải thông tin: {loan['description']}")
                print(f"   💰 Tổng nợ: {loan['total_amount']:,.0f}đ")
                print(f"   ✅ Đã trả: {loan['paid_amount']:,.0f}đ")
                print(f"   ❗ Còn lại: {loan['remaining_amount']:,.0f}đ")
                
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
        
        with self.output:
            clear_output()
            print(f"✅ Đã ghi nhận thanh toán: {self.loan_description.value}")
            print(f"   💸 Số tiền trả: {payment_amount:,.0f}đ")
            print(f"   💰 Còn lại: {target_loan['remaining_amount']:,.0f}đ")
            print("💾 Dữ liệu đã được lưu tự động")
            if target_loan['remaining_amount'] == 0:
                print("   🎉 Đã trả hết nợ!")
    
    def add_savings(self, button):
        if self.savings_description.value and self.savings_amount.value > 0:
            self.savings_data.append({
                'date': self.savings_date.value,
                'type': self.savings_type.value,
                'description': self.savings_description.value,
                'amount': self.savings_amount.value
            })
            
            # Auto-save after adding data
            self.save_data_silent()
            self.update_savings_dropdown()  # Cập nhật dropdown
            
            with self.output:
                clear_output()
                print(f"✅ Đã thêm tiết kiệm/đầu tư: {self.savings_description.value} - {self.savings_amount.value:,.0f}đ")
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
                total_amount += saving['amount']
                count += 1
        
        if target_savings:
            # Populate form with savings data
            self.savings_type.value = target_savings['type']
            self.savings_description.value = target_savings['description']
            self.savings_amount.value = 0.0  # Reset amount for new entry
            
            with self.output:
                clear_output()
                print(f"✅ Đã tải thông tin: {target_savings['description']}")
                print(f"   💎 Loại: {target_savings['type']}")
                print(f"   💰 Tổng đã đầu tư: {total_amount:,.0f}đ")
                print(f"   📊 Số lần giao dịch: {count}")
                print("📝 Bạn có thể thêm giao dịch mới hoặc cập nhật")
    
    def update_savings(self, button):
        """Cập nhật khoản tiết kiệm/đầu tư (tương tự add nhưng với thông báo khác)"""
        if self.savings_description.value and self.savings_amount.value > 0:
            self.savings_data.append({
                'date': self.savings_date.value,
                'type': self.savings_type.value,
                'description': self.savings_description.value,
                'amount': self.savings_amount.value
            })
            
            # Auto-save after updating data
            self.save_data_silent()
            self.update_savings_dropdown()  # Cập nhật dropdown
            
            with self.output:
                clear_output()
                print(f"🔄 Đã cập nhật/thêm vào {self.savings_description.value}: {self.savings_amount.value:,.0f}đ")
                print("💾 Dữ liệu đã được lưu tự động")
            
            # Clear amount but keep type and description
            self.savings_amount.value = 0.0
        else:
            with self.output:
                clear_output()
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
            
            total_deleted = sum(item['amount'] for item in deleted_items)
            with self.output:
                clear_output()
                print(f"🗑️ Đã xóa {len(deleted_items)} giao dịch: {selected_key}")
                print(f"   💰 Tổng số tiền: {total_deleted:,.0f}đ")
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
        """Tính tổng khoản vay phải trả trong tháng"""
        year, month = map(int, month_str.split('-'))
        total_fixed_payment = 0
        total_flexible_payment = 0
        
        for loan in self.loan_data:
            if loan['remaining_amount'] > 0:  # Chỉ tính các khoản vay chưa trả hết
                if loan['is_fixed']:
                    total_fixed_payment += loan['monthly_payment']
                else:
                    # Với vay linh hoạt, tính từ lịch sử thanh toán trong tháng
                    monthly_payments = 0
                    for payment in loan['payment_history']:
                        if payment['date'].year == year and payment['date'].month == month:
                            monthly_payments += payment['amount']
                    total_flexible_payment += monthly_payments
        
        return total_fixed_payment, total_flexible_payment
    
    def show_cash_flow(self, button):
        selected_month = self.month_filter.value
        
        # Tính toán các khoản thu chi
        income_filtered = self.filter_data_by_month(self.income_data, selected_month)
        expense_filtered = self.filter_data_by_month(self.expense_data, selected_month)
        savings_filtered = self.filter_data_by_month(self.savings_data, selected_month)
        
        total_income = sum(item['amount'] for item in income_filtered)
        total_expense = sum(item['amount'] for item in expense_filtered)
        total_savings = sum(item['amount'] for item in savings_filtered)
        
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
            print("="*60)
            
            # Thu nhập
            print(f"📈 TỔNG THU NHẬP:           {total_income:>15,.0f}đ")
            print("-"*50)
            
            # Chi tiêu cơ bản
            print(f"📊 Chi tiêu sinh hoạt:      {total_expense:>15,.0f}đ")
            print(f"   → Số dư sau chi cơ bản:  {basic_balance:>15,.0f}đ")
            print("-"*50)
            
            # Trả nợ
            print("🏦 KHOẢN VAY PHẢI TRẢ:")
            if fixed_loan > 0:
                print(f"   • Vay cố định hàng tháng: {fixed_loan:>15,.0f}đ")
            if flexible_loan > 0:
                print(f"   • Vay linh hoạt đã trả:   {flexible_loan:>15,.0f}đ")
            print(f"   → Tổng trả nợ tháng này:  {total_loan_payment:>15,.0f}đ")
            print(f"   → Số dư sau trả nợ:       {after_loan:>15,.0f}đ")
            print("-"*50)
            
            # Tiết kiệm/Đầu tư
            if total_savings > 0:
                print(f"💎 Tiết kiệm & Đầu tư:      {total_savings:>15,.0f}đ")
                print(f"   → Số dư sau tiết kiệm:    {final_balance:>15,.0f}đ")
            else:
                print(f"💎 Tiết kiệm & Đầu tư:      {0:>15,.0f}đ")
                final_balance = after_loan
            
            print("="*60)
            
            # Kết luận và khuyến nghị
            if final_balance > 0:
                print(f"✅ SỐ DƯ CÓ THỂ PHÂN BỔ:   {final_balance:>15,.0f}đ")
                print("\n💡 KHUYẾN NGHỊ PHÂN BỔ:")
                
                # Gợi ý phân bổ theo nguyên tắc 50-30-20
                emergency_fund = final_balance * 0.3
                investment = final_balance * 0.5
                extra_saving = final_balance * 0.2
                
                print(f"   📦 Quỹ khẩn cấp (30%):    {emergency_fund:>15,.0f}đ")
                print(f"   📈 Đầu tư (50%):          {investment:>15,.0f}đ") 
                print(f"   💰 Tiết kiệm thêm (20%):  {extra_saving:>15,.0f}đ")
                
            elif final_balance == 0:
                print(f"⚖️  SỐ DƯ CUỐI THÁNG:       {final_balance:>15,.0f}đ")
                print("\n💡 Bạn đã cân bằng thu chi tốt!")
            else:
                print(f"❌ THÂM HỤT:               {final_balance:>15,.0f}đ")
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
            print("="*70)
            
            total_remaining = 0
            total_monthly_fixed = 0
            
            for i, loan in enumerate(self.loan_data, 1):
                print(f"\n{i}. {loan['description']} ({loan['type']})")
                print(f"   📊 Tổng nợ:        {loan['total_amount']:>15,.0f}đ")
                print(f"   ✅ Đã trả:        {loan['paid_amount']:>15,.0f}đ")
                print(f"   ❗ Còn lại:       {loan['remaining_amount']:>15,.0f}đ")
                
                if loan['remaining_amount'] > 0:
                    progress = (loan['paid_amount'] / loan['total_amount']) * 100
                    print(f"   📈 Tiến độ:       {progress:>15.1f}%")
                    
                    if loan['is_fixed']:
                        print(f"   💰 Trả/tháng:     {loan['monthly_payment']:>15,.0f}đ (cố định)")
                        total_monthly_fixed += loan['monthly_payment']
                        
                        # Ước tính thời gian trả hết
                        if loan['monthly_payment'] > 0:
                            months_left = loan['remaining_amount'] / loan['monthly_payment']
                            print(f"   ⏰ Còn ~{months_left:.1f} tháng để trả hết")
                    else:
                        print(f"   💰 Trả linh hoạt (gộp đến đủ rồi trả)")
                else:
                    print(f"   🎉 ĐÃ TRẢ HẾT!")
                
                total_remaining += loan['remaining_amount']
                print("-" * 50)
            
            print(f"\n📋 TỔNG HỢP:")
            print(f"   💸 Tổng nợ còn lại:       {total_remaining:>15,.0f}đ")
            print(f"   🏦 Phải trả cố định/tháng: {total_monthly_fixed:>15,.0f}đ")
            
            # Tính vay linh hoạt
            flexible_loans = [loan for loan in self.loan_data 
                            if not loan['is_fixed'] and loan['remaining_amount'] > 0]
            if flexible_loans:
                total_flexible = sum(loan['remaining_amount'] for loan in flexible_loans)
                print(f"   🤝 Nợ linh hoạt:          {total_flexible:>15,.0f}đ")
    
    def show_summary(self, button):
        selected_month = self.month_filter.value
        
        income_filtered = self.filter_data_by_month(self.income_data, selected_month)
        expense_filtered = self.filter_data_by_month(self.expense_data, selected_month)
        
        total_income = sum(item['amount'] for item in income_filtered)
        total_expense = sum(item['amount'] for item in expense_filtered)
        basic_balance = total_income - total_expense
        
        fixed_loan, flexible_loan = self.calculate_monthly_loan_payments(selected_month)
        
        with self.output:
            clear_output()
            print("="*50)
            print(f"📊 BÁO CÁO TỔNG QUAN THÁNG {selected_month}")
            print("="*50)
            print(f"💰 Tổng thu nhập:    {total_income:,.0f}đ")
            print(f"💸 Tổng chi tiêu:    {total_expense:,.0f}đ")
            print(f"🏦 Trả nợ cố định:   {fixed_loan:,.0f}đ")
            print(f"🤝 Trả nợ linh hoạt: {flexible_loan:,.0f}đ")
            print("-"*30)
            
            net_balance = basic_balance - fixed_loan - flexible_loan
            if net_balance >= 0:
                print(f"✅ Số dư khả dụng:   +{net_balance:,.0f}đ")
            else:
                print(f"❌ Thâm hụt:         {net_balance:,.0f}đ")
            print("="*50)
            
            if expense_filtered:
                print("\n📋 CHI TIẾT CHI PHÍ THEO DANH MỤC:")
                expense_df = pd.DataFrame(expense_filtered)
                category_summary = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False)
                
                for category, amount in category_summary.items():
                    percentage = (amount / total_expense) * 100 if total_expense > 0 else 0
                    print(f"  • {category}: {amount:,.0f}đ ({percentage:.1f}%)")
    
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
            fig.suptitle(f'Báo Cáo Tài Chính Chi Tiết Tháng {selected_month}', fontsize=16, fontweight='bold')
            
            # 1. Biểu đồ dòng tiền tổng quan
            total_income = sum(item['amount'] for item in income_filtered)
            total_expense = sum(item['amount'] for item in expense_filtered)
            total_savings = sum(item['amount'] for item in savings_filtered)
            fixed_loan, flexible_loan = self.calculate_monthly_loan_payments(selected_month)
            
            categories = ['Thu nhập', 'Chi tiêu', 'Trả nợ\ncố định', 'Trả nợ\nlinh hoạt', 'Tiết kiệm\n& ĐT']
            amounts = [total_income, -total_expense, -fixed_loan, -flexible_loan, -total_savings]
            colors = ['#28A745', '#DC3545', '#FF6B35', '#FFA500', '#6F42C1']
            
            bars = axes[0,0].bar(categories, amounts, color=colors)
            axes[0,0].set_title('Dòng Tiền Tổng Quan')
            axes[0,0].set_ylabel('Số tiền (VNĐ)')
            axes[0,0].axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Thêm giá trị lên cột
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                axes[0,0].text(bar.get_x() + bar.get_width()/2., 
                             height + np.sign(height) * max(abs(a) for a in amounts) * 0.01,
                             f'{abs(amount):,.0f}', ha='center', va='bottom' if height >= 0 else 'top')
            
            # 2. Biểu đồ tròn chi phí theo danh mục
            if expense_filtered:
                expense_df = pd.DataFrame(expense_filtered)
                category_summary = expense_df.groupby('category')['amount'].sum()
                
                axes[0,1].pie(category_summary.values, labels=category_summary.index, autopct='%1.1f%%')
                axes[0,1].set_title('Phân Bố Chi Phí Theo Danh Mục')
            else:
                axes[0,1].text(0.5, 0.5, 'Không có dữ liệu chi phí', ha='center', va='center')
                axes[0,1].set_title('Phân Bố Chi Phí Theo Danh Mục')
            
            # 3. Tình trạng các khoản vay
            if self.loan_data:
                loan_names = []
                remaining_amounts = []
                paid_percentages = []
                
                for loan in self.loan_data:
                    if loan['remaining_amount'] > 0:
                        loan_names.append(loan['description'][:20] + '...' if len(loan['description']) > 20 
                                        else loan['description'])
                        remaining_amounts.append(loan['remaining_amount'])
                        paid_percentages.append((loan['paid_amount'] / loan['total_amount']) * 100)
                
                if loan_names:
                    axes[0,2].barh(loan_names, remaining_amounts, color='#FF6B35')
                    axes[0,2].set_title('Nợ Còn Lại Theo Khoản Vay')
                    axes[0,2].set_xlabel('Số tiền (VNĐ)')
                else:
                    axes[0,2].text(0.5, 0.5, 'Đã trả hết nợ!', ha='center', va='center')
                    axes[0,2].set_title('Nợ Còn Lại Theo Khoản Vay')
            else:
                axes[0,2].text(0.5, 0.5, 'Không có khoản vay', ha='center', va='center')
                axes[0,2].set_title('Nợ Còn Lại Theo Khoản Vay')
            
            # 4. Chi phí theo ngày
            if expense_filtered:
                expense_df = pd.DataFrame(expense_filtered)
                daily_expense = expense_df.groupby('date')['amount'].sum().sort_index()
                
                axes[1,0].plot(daily_expense.index, daily_expense.values, marker='o', 
                             color='#DC3545', linewidth=2, markersize=6)
                axes[1,0].set_title('Chi Phí Theo Ngày')
                axes[1,0].set_ylabel('Số tiền (VNĐ)')
                axes[1,0].tick_params(axis='x', rotation=45)
            else:
                axes[1,0].text(0.5, 0.5, 'Không có dữ liệu chi phí', ha='center', va='center')
                axes[1,0].set_title('Chi Phí Theo Ngày')
            
            # 5. Tiết kiệm & Đầu tư theo loại
            if savings_filtered:
                savings_df = pd.DataFrame(savings_filtered)
                savings_summary = savings_df.groupby('type')['amount'].sum().sort_values(ascending=True)
                
                axes[1,1].barh(savings_summary.index, savings_summary.values, color='#6F42C1')
                axes[1,1].set_title('Tiết Kiệm & Đầu Tư Theo Loại')
                axes[1,1].set_xlabel('Số tiền (VNĐ)')
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
            with pd.ExcelWriter(filename) as writer:
                # Sheet thu nhập
                if self.income_data:
                    income_df = pd.DataFrame(self.income_data)
                    income_df.to_excel(writer, sheet_name='Thu Nhập', index=False)
                
                # Sheet chi phí
                if self.expense_data:
                    expense_df = pd.DataFrame(self.expense_data)
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
                    savings_df.to_excel(writer, sheet_name='Tiết Kiệm & Đầu Tư', index=False)
                
                # Sheet tổng hợp theo tháng
                summary_data = []
                for month_option in self.get_month_options():
                    month_name, month_value = month_option
                    income_filtered = self.filter_data_by_month(self.income_data, month_value)
                    expense_filtered = self.filter_data_by_month(self.expense_data, month_value)
                    savings_filtered = self.filter_data_by_month(self.savings_data, month_value)
                    
                    total_income = sum(item['amount'] for item in income_filtered)
                    total_expense = sum(item['amount'] for item in expense_filtered)
                    total_savings = sum(item['amount'] for item in savings_filtered)
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
                            'Số dư cuối': net_balance
                        })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Tổng Hợp Theo Tháng', index=False)
            
            with self.output:
                clear_output()
                print(f"✅ Đã xuất báo cáo chi tiết ra file: {filename}")
                print("📊 File bao gồm các sheet:")
                print("   • Thu Nhập")
                print("   • Chi Phí") 
                print("   • Vay Nợ")
                print("   • Tiết Kiệm & Đầu Tư")
                print("   • Tổng Hợp Theo Tháng")
                
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi xuất file: {str(e)}")
    
    def save_data_silent(self):
        """Lưu dữ liệu tự động mà không hiển thị thông báo"""
        try:
            self.save_data_to_files()
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu: {str(e)}")
    
    def save_data(self, button):
        """Lưu dữ liệu thủ công với thông báo"""
        try:
            self.save_data_to_files()
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
            # Tải thu nhập
            try:
                df = pd.read_csv(self.data_files['income'], encoding='utf-8-sig')
                self.income_data = []
                for _, row in df.iterrows():
                    self.income_data.append({
                        'date': pd.to_datetime(row['date']).date(),
                        'source': row['source'],
                        'amount': float(row['amount'])
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
                        'amount': float(row['amount'])
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
                        'amount': float(row['amount'])
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
                print("🔄 Đã reset tất cả dropdown")
        except Exception as e:
            with self.output:
                clear_output()
                print(f"❌ Lỗi khi xóa dữ liệu: {str(e)}")
    
    def display(self):
        return self.main_layout

# Tạo và hiển thị ứng dụng
def create_finance_tracker():
    """
    Hàm khởi tạo ứng dụng giám sát thu chi với quản lý vay nợ và phân bổ tiết kiệm
    """
    tracker = MonthlyFinanceTracker()
    return tracker.display()

# Chạy ứng dụng
# finance_app = create_finance_tracker()
# display(finance_app)
