import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output
from datetime import datetime

class FlexibleMortgageCalculator:
    def __init__(self):
        self.principal_amount = 1_500_000_000  # 1.5 tỷ VND
        self.max_early_payments = 5  # Tối đa 5 lần trả trước hạn
        self.setup_widgets()
        self.setup_layout()
        
    def setup_widgets(self):
        """Thiết lập các widget đầu vào"""
        # Widget cho số tiền vay chung
        self.principal_widget = widgets.FloatText(
            value=1.5,
            description='Số tiền vay (tỷ):',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='300px')
        )
        
        # === PHƯƠNG ÁN 1 ===
        self.term1_widget = widgets.IntSlider(
            value=5,
            min=1,
            max=30,
            description='Thời gian vay PA1 (năm):',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='400px')
        )
        
        # Lãi suất ban đầu cho phương án 1
        self.initial_rate1_widget = widgets.FloatSlider(
            value=6.0,
            min=1.0,
            max=25.0,
            step=0.1,
            description='Lãi suất ban đầu PA1 (%/năm):',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='450px'),
            readout_format='.1f'
        )
        
        # Checkbox tự động tăng lãi suất PA1
        self.auto_increase1_widget = widgets.Checkbox(
            value=True,
            description='Tự động tăng 0.5%/kỳ',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='200px')
        )
        
        # Container cho rate widgets phương án 1
        self.rate1_widgets = []
        self.rate1_container = widgets.VBox()
        
        # Tạo widgets cho 60 kỳ (30 năm x 2 kỳ/năm)
        for i in range(60):
            widget = widgets.FloatSlider(
                value=6.0 + min(i * 0.5, 9.0),
                min=1.0,
                max=25.0,
                step=0.1,
                description=f'Kỳ {i+1} (tháng {i*6+1}-{(i+1)*6}):',
                style={'description_width': 'initial'},
                layout=widgets.Layout(width='450px'),
                readout_format='.1f'
            )
            self.rate1_widgets.append(widget)
        
        # === PHƯƠNG ÁN 2 ===
        self.term2_widget = widgets.IntSlider(
            value=10,
            min=1,
            max=30,
            description='Thời gian vay PA2 (năm):',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='400px')
        )
        
        # Lãi suất ban đầu cho phương án 2
        self.initial_rate2_widget = widgets.FloatSlider(
            value=6.0,
            min=1.0,
            max=25.0,
            step=0.1,
            description='Lãi suất ban đầu PA2 (%/năm):',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='450px'),
            readout_format='.1f'
        )
        
        # Checkbox tự động tăng lãi suất PA2
        self.auto_increase2_widget = widgets.Checkbox(
            value=True,
            description='Tự động tăng 0.5%/kỳ',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='200px')
        )
        
        # Container cho rate widgets phương án 2
        self.rate2_widgets = []
        self.rate2_container = widgets.VBox()
        
        # Tạo widgets cho 60 kỳ (30 năm x 2 kỳ/năm)
        for i in range(60):
            widget = widgets.FloatSlider(
                value=6.0 + min(i * 0.5, 9.0),
                min=1.0,
                max=25.0,
                step=0.1,
                description=f'Kỳ {i+1} (tháng {i*6+1}-{(i+1)*6}):',
                style={'description_width': 'initial'},
                layout=widgets.Layout(width='450px'),
                readout_format='.1f'
            )
            self.rate2_widgets.append(widget)
        
        # === TRẢ TRƯỚC HẠN LINH HOẠT ===
        self.early_payment_enabled = widgets.Checkbox(
            value=False,
            description='Có trả trước hạn',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='200px')
        )
        
        # Container cho các lần trả trước hạn
        self.early_payments = []
        self.early_payment_container = widgets.VBox()
        
        # Tạo widgets cho tối đa 5 lần trả trước hạn
        for i in range(self.max_early_payments):
            payment_group = {
                'enabled': widgets.Checkbox(
                    value=False,
                    description=f'Lần {i+1}:',
                    style={'description_width': '60px'},
                    layout=widgets.Layout(width='80px')
                ),
                'month': widgets.IntSlider(
                    value=12 + i*12,
                    min=6,
                    max=360,
                    description='Tháng:',
                    style={'description_width': '60px'},
                    layout=widgets.Layout(width='200px')
                ),
                'amount': widgets.FloatText(
                    value=200.0 + i*100,
                    description='Số tiền (triệu):',
                    style={'description_width': '120px'},
                    layout=widgets.Layout(width='200px')
                ),
                'fee_rate': widgets.FloatSlider(
                    value=2.0 + i*0.5,
                    min=0.0,
                    max=10.0,
                    step=0.1,
                    description='Phí (%):',
                    style={'description_width': '60px'},
                    layout=widgets.Layout(width='150px'),
                    readout_format='.1f'
                )
            }
            self.early_payments.append(payment_group)
        
        # Buttons
        self.calculate_button = widgets.Button(
            description='So Sánh 2 Phương Án',
            button_style='primary',
            layout=widgets.Layout(width='200px', height='40px')
        )
        
        self.reset_button = widgets.Button(
            description='Reset Mặc Định',
            button_style='warning',
            layout=widgets.Layout(width='200px', height='40px')
        )
        
        self.copy_rates_button = widgets.Button(
            description='Copy PA1 → PA2',
            button_style='info',
            layout=widgets.Layout(width='150px', height='40px')
        )
        
        self.update_rates1_button = widgets.Button(
            description='Cập nhật lãi suất PA1',
            button_style='success',
            layout=widgets.Layout(width='180px', height='40px')
        )
        
        self.update_rates2_button = widgets.Button(
            description='Cập nhật lãi suất PA2',
            button_style='success',
            layout=widgets.Layout(width='180px', height='40px')
        )
        
        # Output area
        self.output = widgets.Output()
        
        # Gắn sự kiện
        self.calculate_button.on_click(self.on_calculate_clicked)
        self.reset_button.on_click(self.on_reset_clicked)
        self.copy_rates_button.on_click(self.on_copy_rates_clicked)
        self.update_rates1_button.on_click(self.on_update_rates1_clicked)
        self.update_rates2_button.on_click(self.on_update_rates2_clicked)
        
    def setup_layout(self):
        """Thiết lập giao diện"""
        header = widgets.HTML(
            value="<h2 style='color: #2E86AB; text-align: center;'>SO SÁNH 2 PHƯƠNG ÁN VAY - KỲ ĐIỀU CHỈNH 6 THÁNG</h2>"
        )
        
        # Thông số chung
        common_params = widgets.VBox([
            widgets.HTML("<h3 style='color: #A23B72;'>Thông Số Chung</h3>"),
            self.principal_widget
        ])
        
        # Phương án 1
        plan1_title = widgets.HTML("<h3 style='color: #E74C3C;'>PHƯƠNG ÁN 1</h3>")
        plan1_controls = widgets.HBox([
            self.initial_rate1_widget,
            self.auto_increase1_widget,
            self.update_rates1_button
        ])
        self.rate1_container = widgets.VBox(
            layout=widgets.Layout(height='300px', overflow_y='auto', border='1px solid #E74C3C', padding='10px')
        )
        plan1_box = widgets.VBox([
            plan1_title,
            self.term1_widget,
            plan1_controls,
            widgets.HTML("<b>Lãi suất theo kỳ 6 tháng (%/năm):</b>"),
            self.rate1_container
        ])
        
        # Phương án 2
        plan2_title = widgets.HTML("<h3 style='color: #3498DB;'>PHƯƠNG ÁN 2</h3>")
        plan2_controls = widgets.HBox([
            self.initial_rate2_widget,
            self.auto_increase2_widget,
            self.update_rates2_button
        ])
        self.rate2_container = widgets.VBox(
            layout=widgets.Layout(height='300px', overflow_y='auto', border='1px solid #3498DB', padding='10px')
        )
        plan2_box = widgets.VBox([
            plan2_title,
            self.term2_widget,
            plan2_controls,
            widgets.HTML("<b>Lãi suất theo kỳ 6 tháng (%/năm):</b>"),
            self.rate2_container
        ])
        
        # Trả trước hạn linh hoạt
        early_payment_title = widgets.HTML("<h3 style='color: #9B59B6;'>TRẢ TRƯỚC HẠN LINH HOẠT (Áp dụng cho cả 2 phương án)</h3>")
        self.early_payment_container = widgets.VBox(
            layout=widgets.Layout(height='200px', overflow_y='auto', border='1px solid #9B59B6', padding='10px')
        )
        early_payment_box = widgets.VBox([
            early_payment_title,
            self.early_payment_enabled,
            widgets.HTML("<b>Cấu hình các lần trả trước hạn:</b>"),
            self.early_payment_container
        ])
        
        # Layout chính
        plans_layout = widgets.HBox([plan1_box, plan2_box])
        button_box = widgets.HBox([self.calculate_button, self.reset_button, self.copy_rates_button], 
                                 layout=widgets.Layout(justify_content='center'))
        
        self.main_layout = widgets.VBox([
            header,
            common_params,
            plans_layout,
            early_payment_box,
            button_box,
            self.output
        ])
        
    def auto_update_rates(self, plan_number):
        """Tự động cập nhật lãi suất theo kỳ"""
        if plan_number == 1:
            initial_rate = self.initial_rate1_widget.value
            auto_increase = self.auto_increase1_widget.value
            term_years = self.term1_widget.value
            widgets_list = self.rate1_widgets
        else:
            initial_rate = self.initial_rate2_widget.value
            auto_increase = self.auto_increase2_widget.value
            term_years = self.term2_widget.value
            widgets_list = self.rate2_widgets
        
        required_periods = (term_years * 12 + 5) // 6
        
        for i in range(min(required_periods, len(widgets_list))):
            if auto_increase:
                # Tăng dần 0.5% mỗi kỳ với giới hạn tối đa 25%
                widgets_list[i].value = min(initial_rate + i * 0.5, 25.0)
            else:
                # Giữ nguyên lãi suất ban đầu
                widgets_list[i].value = initial_rate
    
    def on_update_rates1_clicked(self, button):
        """Cập nhật lãi suất cho phương án 1"""
        self.auto_update_rates(1)
        self.update_rate_widgets_visibility()
        print("Đã cập nhật lãi suất cho Phương án 1!")
    
    def on_update_rates2_clicked(self, button):
        """Cập nhật lãi suất cho phương án 2"""
        self.auto_update_rates(2)
        self.update_rate_widgets_visibility()
        print("Đã cập nhật lãi suất cho Phương án 2!")
    
    def calculate_mortgage_payment(self, principal, annual_rate, remaining_months):
        """Tính toán số tiền phải trả hàng tháng"""
        if remaining_months <= 0 or principal <= 0:
            return 0, 0, 0
        
        monthly_rate = annual_rate / 12
        
        if monthly_rate == 0:
            monthly_payment = principal / remaining_months
            interest_payment = 0
            principal_payment = monthly_payment
        else:
            monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**remaining_months) / ((1 + monthly_rate)**remaining_months - 1)
            interest_payment = principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
        
        return monthly_payment, interest_payment, principal_payment
    
    def calculate_schedule(self, principal, loan_years, rates):
        """Tính toán lịch trình cho phương án với kỳ 6 tháng"""
        total_months = loan_years * 12
        payment_schedule = []
        remaining_principal = principal
        current_month = 1
        
        period_index = 0
        months_in_current_period = 0
        
        while current_month <= total_months and remaining_principal > 1:
            if months_in_current_period >= 6:
                period_index += 1
                months_in_current_period = 0
            
            if period_index >= len(rates):
                period_index = len(rates) - 1
                
            annual_rate = rates[period_index] / 100
            months_in_current_period += 1
            
            remaining_months = total_months - current_month + 1
            monthly_payment, interest_payment, principal_payment = self.calculate_mortgage_payment(
                remaining_principal, annual_rate, remaining_months
            )
            
            if principal_payment > remaining_principal:
                principal_payment = remaining_principal
                monthly_payment = interest_payment + principal_payment
            
            remaining_principal -= principal_payment
            
            payment_schedule.append({
                "Tháng": current_month,
                "Kỳ": f"Kỳ {period_index + 1}",
                "Lãi suất (%/năm)": rates[period_index],
                "Dư nợ đầu kỳ (VND)": remaining_principal + principal_payment,
                "Tiền lãi (VND)": interest_payment,
                "Tiền gốc (VND)": principal_payment,
                "Tổng thanh toán (VND)": monthly_payment,
                "Dư nợ cuối kỳ (VND)": remaining_principal
            })
            
            current_month += 1
            
            if remaining_principal <= 1:
                break
        
        return pd.DataFrame(payment_schedule)
    
    def apply_multiple_early_payments(self, df):
        """Áp dụng nhiều lần trả trước hạn"""
        if not self.early_payment_enabled.value:
            return df, 0
        
        df_modified = df.copy()
        df_modified['Trả trước hạn (VND)'] = 0
        df_modified['Phí trả trước (VND)'] = 0
        total_prepayment_fee = 0
        
        # Lấy danh sách các lần trả trước hạn được kích hoạt
        active_payments = []
        for i, payment in enumerate(self.early_payments):
            if payment['enabled'].value and payment['month'].value <= len(df_modified):
                active_payments.append({
                    'month': payment['month'].value,
                    'amount': payment['amount'].value * 1_000_000,
                    'fee_rate': payment['fee_rate'].value
                })
        
        # Sắp xếp theo tháng
        active_payments.sort(key=lambda x: x['month'])
        
        # Áp dụng từng lần trả trước hạn
        for payment in active_payments:
            month = payment['month']
            amount = payment['amount']
            fee_rate = payment['fee_rate']
            
            if month <= len(df_modified):
                # Lấy dư nợ tại thời điểm trả trước hạn
                remaining_balance = df_modified.iloc[month-1]['Dư nợ cuối kỳ (VND)']
                
                # Tính phí trả trước hạn
                prepayment_fee = remaining_balance * fee_rate / 100
                total_prepayment_fee += prepayment_fee
                
                # Điều chỉnh số tiền trả trước hạn nếu vượt quá dư nợ
                actual_payment = min(amount, remaining_balance)
                new_remaining = remaining_balance - actual_payment
                
                # Cập nhật tháng trả trước hạn
                df_modified.loc[month-1, 'Dư nợ cuối kỳ (VND)'] = new_remaining
                df_modified.loc[month-1, 'Trả trước hạn (VND)'] = actual_payment
                df_modified.loc[month-1, 'Phí trả trước (VND)'] = prepayment_fee
                df_modified.loc[month-1, 'Tổng thanh toán (VND)'] += actual_payment + prepayment_fee
                
                # Tính lại các tháng sau
                for i in range(month, len(df_modified)):
                    if new_remaining <= 0:
                        df_modified = df_modified.iloc[:month]
                        break
                    
                    remaining_months = len(df_modified) - i
                    annual_rate = df_modified.iloc[i]['Lãi suất (%/năm)'] / 100
                    
                    monthly_payment, interest_payment, principal_payment = self.calculate_mortgage_payment(
                        new_remaining, annual_rate, remaining_months
                    )
                    
                    if principal_payment > new_remaining:
                        principal_payment = new_remaining
                        monthly_payment = interest_payment + principal_payment
                    
                    new_remaining -= principal_payment
                    
                    df_modified.loc[i, 'Dư nợ đầu kỳ (VND)'] = new_remaining + principal_payment
                    df_modified.loc[i, 'Tiền lãi (VND)'] = interest_payment
                    df_modified.loc[i, 'Tiền gốc (VND)'] = principal_payment
                    df_modified.loc[i, 'Tổng thanh toán (VND)'] = monthly_payment
                    df_modified.loc[i, 'Dư nợ cuối kỳ (VND)'] = new_remaining
                    
                    if i != month-1:  # Không ghi đè lần trả trước hạn
                        df_modified.loc[i, 'Trả trước hạn (VND)'] = 0
                        df_modified.loc[i, 'Phí trả trước (VND)'] = 0
        
        return df_modified, total_prepayment_fee
    
    def update_rate_widgets_visibility(self):
        """Cập nhật hiển thị widgets lãi suất"""
        # Phương án 1
        required_periods1 = (self.term1_widget.value * 12 + 5) // 6
        visible_widgets1 = []
        for i in range(required_periods1):
            if i < len(self.rate1_widgets):
                widget = self.rate1_widgets[i]
                max_month = min((i+1)*6, self.term1_widget.value*12)
                widget.description = f'Kỳ {i+1} (tháng {i*6+1}-{max_month}):'
                visible_widgets1.append(widget)
        self.rate1_container.children = visible_widgets1
        
        # Phương án 2
        required_periods2 = (self.term2_widget.value * 12 + 5) // 6
        visible_widgets2 = []
        for i in range(required_periods2):
            if i < len(self.rate2_widgets):
                widget = self.rate2_widgets[i]
                max_month = min((i+1)*6, self.term2_widget.value*12)
                widget.description = f'Kỳ {i+1} (tháng {i*6+1}-{max_month}):'
                visible_widgets2.append(widget)
        self.rate2_container.children = visible_widgets2
    
    def update_early_payment_widgets_visibility(self):
        """Cập nhật hiển thị widgets trả trước hạn"""
        if self.early_payment_enabled.value:
            visible_widgets = []
            for i, payment in enumerate(self.early_payments):
                row = widgets.HBox([
                    payment['enabled'],
                    payment['month'],
                    payment['amount'],
                    payment['fee_rate']
                ])
                visible_widgets.append(row)
            self.early_payment_container.children = visible_widgets
        else:
            self.early_payment_container.children = []
    
    def on_calculate_clicked(self, button):
        """Xử lý khi nhấn nút tính toán"""
        with self.output:
            clear_output(wait=True)
            self.display_comparison_results()
    
    def on_reset_clicked(self, button):
        """Reset về giá trị mặc định"""
        self.principal_widget.value = 1.5
        self.term1_widget.value = 5
        self.term2_widget.value = 10
        self.initial_rate1_widget.value = 6.0
        self.initial_rate2_widget.value = 6.0
        self.auto_increase1_widget.value = True
        self.auto_increase2_widget.value = True
        
        # Reset phương án 1
        for i, widget in enumerate(self.rate1_widgets[:20]):
            widget.value = 6.0 + min(i * 0.5, 9.0)
        
        # Reset phương án 2
        for i, widget in enumerate(self.rate2_widgets[:20]):
            widget.value = 6.0 + min(i * 0.5, 9.0)
        
        # Reset trả trước hạn
        self.early_payment_enabled.value = False
        for i, payment in enumerate(self.early_payments):
            payment['enabled'].value = False
            payment['month'].value = 12 + i*12
            payment['amount'].value = 200.0 + i*100
            payment['fee_rate'].value = 2.0 + i*0.5
        
        self.update_rate_widgets_visibility()
        self.update_early_payment_widgets_visibility()
        
        with self.output:
            clear_output(wait=True)
            print("Đã reset về giá trị mặc định.")
    
    def on_copy_rates_clicked(self, button):
        """Copy lãi suất từ PA1 sang PA2"""
        # Copy lãi suất ban đầu
        self.initial_rate2_widget.value = self.initial_rate1_widget.value
        self.auto_increase2_widget.value = self.auto_increase1_widget.value
        
        # Lấy số kỳ của PA2
        required_periods2 = (self.term2_widget.value * 12 + 5) // 6
        
        # Copy từ PA1 sang PA2
        for i in range(min(required_periods2, len(self.rate1_widgets))):
            if i < len(self.rate2_widgets):
                self.rate2_widgets[i].value = self.rate1_widgets[i].value
        
        self.update_rate_widgets_visibility()
        print("Đã copy lãi suất từ Phương án 1 sang Phương án 2!")
    
    def display_comparison_results(self):
        """Hiển thị kết quả so sánh 2 phương án"""
        try:
            principal = self.principal_widget.value * 1_000_000_000
            
            # Lấy lãi suất từ widgets
            rates1 = [w.value for w in self.rate1_container.children]
            rates2 = [w.value for w in self.rate2_container.children]
            
            # Tính toán 2 phương án
            df1 = self.calculate_schedule(principal, self.term1_widget.value, rates1)
            df2 = self.calculate_schedule(principal, self.term2_widget.value, rates2)
            
            # Áp dụng trả trước hạn nếu có
            df1, prepay_fee1 = self.apply_multiple_early_payments(df1)
            df2, prepay_fee2 = self.apply_multiple_early_payments(df2)
            
            print("="*120)
            print("KẾT QUẢ SO SÁNH 2 PHƯƠNG ÁN VAY - KỲ ĐIỀU CHỈNH 6 THÁNG")
            print("="*120)
            
            # Tổng kết 2 phương án
            total1 = df1['Tổng thanh toán (VND)'].sum()
            total_interest1 = df1['Tiền lãi (VND)'].sum()
            total_early_payment1 = df1['Trả trước hạn (VND)'].sum() if 'Trả trước hạn (VND)' in df1.columns else 0
            
            total2 = df2['Tổng thanh toán (VND)'].sum()
            total_interest2 = df2['Tiền lãi (VND)'].sum()
            total_early_payment2 = df2['Trả trước hạn (VND)'].sum() if 'Trả trước hạn (VND)' in df2.columns else 0
            
            print(f"\nPHƯƠNG ÁN 1: {self.term1_widget.value} năm ({len(df1)} tháng)")
            print(f"  - Lãi suất ban đầu: {self.initial_rate1_widget.value:.1f}%/năm")
            print(f"  - Tổng tiền lãi: {total_interest1:,.0f} VND")
            print(f"  - Tổng thanh toán: {total1:,.0f} VND")
            if total_early_payment1 > 0:
                print(f"  - Tổng trả trước hạn: {total_early_payment1:,.0f} VND")
                print(f"  - Tổng phí trả trước: {prepay_fee1:,.0f} VND")
            
            print(f"\nPHƯƠNG ÁN 2: {self.term2_widget.value} năm ({len(df2)} tháng)")
            print(f"  - Lãi suất ban đầu: {self.initial_rate2_widget.value:.1f}%/năm")
            print(f"  - Tổng tiền lãi: {total_interest2:,.0f} VND")
            print(f"  - Tổng thanh toán: {total2:,.0f} VND")
            if total_early_payment2 > 0:
                print(f"  - Tổng trả trước hạn: {total_early_payment2:,.0f} VND")
                print(f"  - Tổng phí trả trước: {prepay_fee2:,.0f} VND")
            
            # So sánh
            difference = total1 - total2
            print(f"\n{'='*60}")
            print("KẾT LUẬN SO SÁNH")
            print("="*60)
            if abs(difference) < 1000:
                print("Hai phương án tương đương nhau")
            elif difference > 0:
                print(f"Phương án 2 ({self.term2_widget.value} năm) TỐT HƠN: Tiết kiệm {difference:,.0f} VND")
                print(f"Bằng {(difference/principal)*100:.2f}% số tiền vay")
            else:
                print(f"Phương án 1 ({self.term1_widget.value} năm) TỐT HƠN: Tiết kiệm {abs(difference):,.0f} VND")
                print(f"Bằng {(abs(difference)/principal)*100:.2f}% số tiền vay")
            
            # Hiển thị thông tin trả trước hạn
            self.display_early_payment_summary()
            
            # Hiển thị chi tiết 12 tháng đầu
            self.display_monthly_details(df1, df2)
            
            # Tạo biểu đồ so sánh với Plotly (từng biểu đồ riêng)
            self.create_individual_plotly_charts(df1, df2)
            
        except Exception as e:
            print(f"Có lỗi xảy ra: {str(e)}")
    
    def display_early_payment_summary(self):
        """Hiển thị tóm tắt các lần trả trước hạn"""
        if self.early_payment_enabled.value:
            print(f"\n{'='*60}")
            print("THÔNG TIN TRẢ TRƯỚC HẠN")
            print("="*60)
            
            active_count = 0
            for i, payment in enumerate(self.early_payments):
                if payment['enabled'].value:
                    active_count += 1
                    print(f"Lần {active_count}: Tháng {payment['month'].value} - "
                          f"{payment['amount'].value:,.0f} triệu VND - "
                          f"Phí {payment['fee_rate'].value:.1f}%")
            
            if active_count == 0:
                print("Không có lần trả trước hạn nào được kích hoạt")
    
    def display_monthly_details(self, df1, df2):
        """Hiển thị chi tiết hàng tháng"""
        print(f"\n{'='*80}")
        print("CHI TIẾT 12 THÁNG ĐẦU")
        print("="*80)
        
        print(f"\nPHƯƠNG ÁN 1 ({self.term1_widget.value} năm):")
        display_cols1 = ['Tháng', 'Kỳ', 'Lãi suất (%/năm)', 'Tổng thanh toán (VND)', 'Dư nợ cuối kỳ (VND)']
        if 'Trả trước hạn (VND)' in df1.columns and df1['Trả trước hạn (VND)'].sum() > 0:
            display_cols1.extend(['Trả trước hạn (VND)', 'Phí trả trước (VND)'])
        
        print(df1.head(12)[display_cols1].to_string(index=False, formatters={
            'Tổng thanh toán (VND)': '{:,.0f}'.format,
            'Dư nợ cuối kỳ (VND)': '{:,.0f}'.format,
            'Trả trước hạn (VND)': '{:,.0f}'.format,
            'Phí trả trước (VND)': '{:,.0f}'.format
        }))
        
        print(f"\nPHƯƠNG ÁN 2 ({self.term2_widget.value} năm):")
        display_cols2 = ['Tháng', 'Kỳ', 'Lãi suất (%/năm)', 'Tổng thanh toán (VND)', 'Dư nợ cuối kỳ (VND)']
        if 'Trả trước hạn (VND)' in df2.columns and df2['Trả trước hạn (VND)'].sum() > 0:
            display_cols2.extend(['Trả trước hạn (VND)', 'Phí trả trước (VND)'])
        
        print(df2.head(12)[display_cols2].to_string(index=False, formatters={
            'Tổng thanh toán (VND)': '{:,.0f}'.format,
            'Dư nợ cuối kỳ (VND)': '{:,.0f}'.format,
            'Trả trước hạn (VND)': '{:,.0f}'.format,
            'Phí trả trước (VND)': '{:,.0f}'.format
        }))
    
    def create_individual_plotly_charts(self, df1, df2):
        """Tạo các biểu đồ riêng lẻ với Plotly"""
        
        # 1. Biểu đồ So Sánh Lãi Suất
        fig1 = go.Figure()
        if len(df1) > 0:
            fig1.add_trace(
                go.Scatter(x=df1['Tháng'], y=df1['Lãi suất (%/năm)'], 
                          name=f'PA1: {self.term1_widget.value} năm', 
                          line=dict(color='#E74C3C', width=3),
                          mode='lines+markers', marker=dict(size=4))
            )
        if len(df2) > 0:
            fig1.add_trace(
                go.Scatter(x=df2['Tháng'], y=df2['Lãi suất (%/năm)'], 
                          name=f'PA2: {self.term2_widget.value} năm', 
                          line=dict(color='#3498DB', width=3),
                          mode='lines+markers', marker=dict(size=4))
            )
        
        fig1.update_layout(
            title="<b>1. So Sánh Lãi Suất Theo Thời Gian</b>",
            xaxis_title="Tháng",
            yaxis_title="Lãi suất (%/năm)",
            template="plotly_white",
            height=500
        )
        fig1.show()
        
        # 2. Biểu đồ So Sánh Thanh Toán Hàng Tháng
        fig2 = go.Figure()
        if len(df1) > 0:
            fig2.add_trace(
                go.Scatter(x=df1['Tháng'], y=df1['Tổng thanh toán (VND)']/1_000_000,
                          name=f'PA1: {self.term1_widget.value} năm', 
                          line=dict(color='#E74C3C', width=3))
            )
        if len(df2) > 0:
            fig2.add_trace(
                go.Scatter(x=df2['Tháng'], y=df2['Tổng thanh toán (VND)']/1_000_000,
                          name=f'PA2: {self.term2_widget.value} năm', 
                          line=dict(color='#3498DB', width=3))
            )
        
        fig2.update_layout(
            title="<b>2. So Sánh Thanh Toán Hàng Tháng</b>",
            xaxis_title="Tháng",
            yaxis_title="Triệu VND",
            template="plotly_white",
            height=500
        )
        fig2.show()
        
        # 3. Biểu đồ So Sánh Dư Nợ Còn Lại
        fig3 = go.Figure()
        if len(df1) > 0:
            fig3.add_trace(
                go.Scatter(x=df1['Tháng'], y=df1['Dư nợ cuối kỳ (VND)']/1_000_000_000,
                          name=f'PA1: {self.term1_widget.value} năm', 
                          line=dict(color='#E74C3C', width=3))
            )
        if len(df2) > 0:
            fig3.add_trace(
                go.Scatter(x=df2['Tháng'], y=df2['Dư nợ cuối kỳ (VND)']/1_000_000_000,
                          name=f'PA2: {self.term2_widget.value} năm', 
                          line=dict(color='#3498DB', width=3))
            )
        
        fig3.update_layout(
            title="<b>3. So Sánh Dư Nợ Còn Lại</b>",
            xaxis_title="Tháng",
            yaxis_title="Tỷ VND",
            template="plotly_white",
            height=500
        )
        fig3.show()
        
        # 4. Biểu đồ Tổng Thanh Toán Tích Lũy
        fig4 = go.Figure()
        if len(df1) > 0:
            cumulative1 = df1['Tổng thanh toán (VND)'].cumsum()
            fig4.add_trace(
                go.Scatter(x=df1['Tháng'], y=cumulative1/1_000_000_000,
                          name=f'PA1: {self.term1_widget.value} năm', 
                          line=dict(color='#E74C3C', width=4))
            )
        if len(df2) > 0:
            cumulative2 = df2['Tổng thanh toán (VND)'].cumsum()
            fig4.add_trace(
                go.Scatter(x=df2['Tháng'], y=cumulative2/1_000_000_000,
                          name=f'PA2: {self.term2_widget.value} năm', 
                          line=dict(color='#3498DB', width=4))
            )
        
        fig4.update_layout(
            title="<b>4. Tổng Thanh Toán Tích Lũy</b>",
            xaxis_title="Tháng",
            yaxis_title="Tỷ VND",
            template="plotly_white",
            height=500
        )
        fig4.show()
        
        # 5. Thành phần thanh toán - Phương án 1
        if len(df1) > 0:
            display_months1 = min(60, len(df1))
            df1_display = df1.head(display_months1)
            
            fig5 = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Bar charts cho tiền lãi và tiền gốc
            fig5.add_trace(
                go.Bar(x=df1_display['Tháng'], y=df1_display['Tiền lãi (VND)']/1_000_000,
                       name='Tiền lãi', marker_color='#FF6B6B', opacity=0.8),
                secondary_y=False
            )
            fig5.add_trace(
                go.Bar(x=df1_display['Tháng'], y=df1_display['Tiền gốc (VND)']/1_000_000,
                       name='Tiền gốc', marker_color='#4ECDC4', opacity=0.8),
                secondary_y=False
            )
            
            # Scatter plot cho trả trước hạn (trục thứ 2)
            if 'Trả trước hạn (VND)' in df1_display.columns:
                early_months = df1_display[df1_display['Trả trước hạn (VND)'] > 0]
                if len(early_months) > 0:
                    fig5.add_trace(
                        go.Scatter(x=early_months['Tháng'], 
                                 y=early_months['Trả trước hạn (VND)']/1_000_000,
                                 mode='markers+lines+text',
                                 marker=dict(color='red', size=10, symbol='diamond'),
                                 line=dict(color='red', width=2, dash='dash'),
                                 text=[f'TT: {val/1_000_000:.0f}tr' for val in early_months['Trả trước hạn (VND)']],
                                 textposition='top center',
                                 name='Trả trước hạn'),
                        secondary_y=True
                    )
            
            fig5.update_xaxes(title_text="Tháng")
            fig5.update_yaxes(title_text="Triệu VND (Thanh toán thường xuyên)", secondary_y=False)
            fig5.update_yaxes(title_text="Triệu VND (Trả trước hạn)", secondary_y=True)
            
            fig5.update_layout(
                title=f"<b>5. Thành Phần Thanh Toán - Phương Án 1 ({self.term1_widget.value} năm)</b>",
                template="plotly_white",
                barmode='stack',
                height=500
            )
            fig5.show()
        
        # 6. Thành phần thanh toán - Phương án 2
        if len(df2) > 0:
            display_months2 = min(60, len(df2))
            df2_display = df2.head(display_months2)
            
            fig6 = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Bar charts cho tiền lãi và tiền gốc
            fig6.add_trace(
                go.Bar(x=df2_display['Tháng'], y=df2_display['Tiền lãi (VND)']/1_000_000,
                       name='Tiền lãi', marker_color='#FF9F43', opacity=0.8),
                secondary_y=False
            )
            fig6.add_trace(
                go.Bar(x=df2_display['Tháng'], y=df2_display['Tiền gốc (VND)']/1_000_000,
                       name='Tiền gốc', marker_color='#5F27CD', opacity=0.8),
                secondary_y=False
            )
            
            # Scatter plot cho trả trước hạn (trục thứ 2)
            if 'Trả trước hạn (VND)' in df2_display.columns:
                early_months = df2_display[df2_display['Trả trước hạn (VND)'] > 0]
                if len(early_months) > 0:
                    fig6.add_trace(
                        go.Scatter(x=early_months['Tháng'], 
                                 y=early_months['Trả trước hạn (VND)']/1_000_000,
                                 mode='markers+lines+text',
                                 marker=dict(color='red', size=10, symbol='diamond'),
                                 line=dict(color='red', width=2, dash='dash'),
                                 text=[f'TT: {val/1_000_000:.0f}tr' for val in early_months['Trả trước hạn (VND)']],
                                 textposition='top center',
                                 name='Trả trước hạn'),
                        secondary_y=True
                    )
            
            fig6.update_xaxes(title_text="Tháng")
            fig6.update_yaxes(title_text="Triệu VND (Thanh toán thường xuyên)", secondary_y=False)
            fig6.update_yaxes(title_text="Triệu VND (Trả trước hạn)", secondary_y=True)
            
            fig6.update_layout(
                title=f"<b>6. Thành Phần Thanh Toán - Phương Án 2 ({self.term2_widget.value} năm)</b>",
                template="plotly_white",
                barmode='stack',
                height=500
            )
            fig6.show()
    
    def display(self):
        """Hiển thị giao diện chính"""
        # Cập nhật visibility khi thay đổi thời gian vay
        def on_term1_change(change):
            self.update_rate_widgets_visibility()
            # Cập nhật giới hạn tháng trả trước hạn
            max_months = self.term1_widget.value * 12
            for payment in self.early_payments:
                payment['month'].max = max_months
            
        def on_term2_change(change):
            self.update_rate_widgets_visibility()
            # Cập nhật giới hạn tháng trả trước hạn
            max_months = self.term2_widget.value * 12
            for payment in self.early_payments:
                payment['month'].max = max_months
        
        def on_early_payment_change(change):
            # Hiện/ẩn các tùy chọn trả trước hạn
            self.update_early_payment_widgets_visibility()
        
        self.term1_widget.observe(on_term1_change, names='value')
        self.term2_widget.observe(on_term2_change, names='value')
        self.early_payment_enabled.observe(on_early_payment_change, names='value')
        
        # Khởi tạo visibility
        self.update_rate_widgets_visibility()
        self.update_early_payment_widgets_visibility()
        
        display(self.main_layout)
        
        # Hiển thị hướng dẫn ban đầu
        with self.output:
            print("="*100)
            print("HƯỚNG DẪN SỬ DỤNG - MÁY TÍNH SO SÁNH VAY LINH HOẠT CẢI TIẾN")
            print("="*100)
            print("🏠 TÍNH NĂNG MỚI:")
            print("  ✓ Cài đặt lãi suất ban đầu cho từng phương án")
            print("  ✓ Tùy chọn tự động tăng 0.5%/kỳ hoặc giữ nguyên")
            print("  ✓ Nút 'Cập nhật lãi suất' để áp dụng cài đặt")
            print("  ✓ Biểu đồ riêng lẻ dễ quan sát")
            print("  ✓ Trục tọa độ riêng cho trả trước hạn")
            print()
            print("🏠 TÍNH NĂNG CHÍNH:")
            print("  ✓ So sánh 2 phương án vay với SỐ NĂM KHÁC NHAU")
            print("  ✓ Cùng kỳ điều chỉnh lãi suất 6 tháng")
            print("  ✓ Trả trước hạn LINH HOẠT tại NHIỀU thời điểm")
            print("  ✓ Mức phí trả trước hạn KHÁC NHAU cho từng lần")
            print()
            print("📋 CÁCH SỬ DỤNG:")
            print("1. Nhập số tiền vay chung")
            print("2. Chọn thời gian vay cho từng phương án (có thể khác nhau)")
            print("3. Cài đặt lãi suất ban đầu và chọn tự động tăng hay không")
            print("4. Nhấn 'Cập nhật lãi suất' để áp dụng")
            print("5. Điều chỉnh lãi suất thủ công (nếu cần)")
            print("6. Cấu hình trả trước hạn (nếu cần)")
            print("7. Nhấn 'So Sánh 2 Phương Án'")
            print()
            print("🔧 TÍNH NĂNG BỔ SUNG:")
            print("  • 'Cập nhật lãi suất PA1/PA2': Áp dụng cài đặt lãi suất")
            print("  • 'Copy PA1 → PA2': Copy toàn bộ cài đặt từ PA1 sang PA2")
            print("  • 'Reset Mặc Định': Khôi phục cài đặt ban đầu")
            print()
            print("📊 VÍ DỤ MẶC ĐỊNH:")
            print(f"  • Số tiền vay: {self.principal_widget.value} tỷ VND")
            print(f"  • PA1: {self.term1_widget.value} năm, PA2: {self.term2_widget.value} năm")
            print(f"  • Lãi suất ban đầu: {self.initial_rate1_widget.value}%/năm")
            print("  • Tự động tăng 0.5%/kỳ")
            print("  • 5 tùy chọn trả trước hạn linh hoạt")
            print()
            print("🎯 KẾT QUẢ HIỂN THỊ:")
            print("  ✓ Tổng kết tài chính chi tiết")
            print("  ✓ So sánh hiệu quả đầu tư")
            print("  ✓ 6 biểu đồ riêng lẻ tương tác Plotly")
            print("  ✓ Trục tọa độ riêng cho trả trước hạn")
            print("  ✓ Đánh dấu chi tiết các thời điểm trả trước hạn")
            print("="*100)

# Khởi tạo và hiển thị máy tính so sánh
print("🚀 Đang khởi tạo Máy Tính So Sánh Vay Linh Hoạt Cải Tiến...")
print("📱 Giao diện tương tác sẽ xuất hiện bên dưới:")
print("="*80)

calculator = FlexibleMortgageCalculator()
calculator.display()
