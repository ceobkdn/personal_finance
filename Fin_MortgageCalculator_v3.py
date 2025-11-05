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
        self.principal_amount = 1_500  # Triệu VND
        self.max_early_payments = 10
        self.setup_widgets()
        self.setup_layout()
        
    def setup_widgets(self):
        """Thiết lập các widget đầu vào"""
        # === THÔNG SỐ CHUNG ===
        self.principal_widget = widgets.FloatText(
            value=1500,
            description='Số tiền vay (triệu):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='350px')
        )
        
        # === PHƯƠNG ÁN 1 ===
        self.term1_widget = widgets.IntSlider(
            value=5,
            min=1,
            max=30,
            description='Thời gian (năm):',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.initial_rate1_widget = widgets.FloatSlider(
            value=6.0,
            min=1.0,
            max=25.0,
            step=0.1,
            description='Lãi suất ban đầu (%):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='450px'),
            readout_format='.1f'
        )
        
        self.auto_increase1_widget = widgets.Checkbox(
            value=True,
            description='Tự động tăng',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='120px')
        )
        
        self.auto_increase_rate1_widget = widgets.FloatText(
            value=0.5,
            description='Tăng (%/kỳ):',
            style={'description_width': '80px'},
            layout=widgets.Layout(width='180px'),
            disabled=False
        )
        
        self.rate1_widgets = []
        for i in range(60):
            widget = widgets.FloatSlider(
                value=6.0 + min(i * 0.5, 9.0),
                min=1.0,
                max=25.0,
                step=0.1,
                description=f'Kỳ {i+1}:',
                style={'description_width': '60px'},
                layout=widgets.Layout(width='400px'),
                readout_format='.1f'
            )
            self.rate1_widgets.append(widget)
        
        # === PHƯƠNG ÁN 2 ===
        self.term2_widget = widgets.IntSlider(
            value=10,
            min=1,
            max=30,
            description='Thời gian (năm):',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.initial_rate2_widget = widgets.FloatSlider(
            value=6.0,
            min=1.0,
            max=25.0,
            step=0.1,
            description='Lãi suất ban đầu (%):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='450px'),
            readout_format='.1f'
        )
        
        self.auto_increase2_widget = widgets.Checkbox(
            value=True,
            description='Tự động tăng',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='120px')
        )
        
        self.auto_increase_rate2_widget = widgets.FloatText(
            value=0.5,
            description='Tăng (%/kỳ):',
            style={'description_width': '80px'},
            layout=widgets.Layout(width='180px'),
            disabled=False
        )
        
        self.rate2_widgets = []
        for i in range(60):
            widget = widgets.FloatSlider(
                value=6.0 + min(i * 0.5, 9.0),
                min=1.0,
                max=25.0,
                step=0.1,
                description=f'Kỳ {i+1}:',
                style={'description_width': '60px'},
                layout=widgets.Layout(width='400px'),
                readout_format='.1f'
            )
            self.rate2_widgets.append(widget)
        
        # === TRẢ TRƯỚC HẠN PA1 ===
        self.early_payment1_enabled = widgets.Checkbox(
            value=False,
            description='Kích hoạt',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='100px')
        )
        
        self.num_early_payments1_widget = widgets.IntSlider(
            value=3,
            min=1,
            max=self.max_early_payments,
            description='Số lần:',
            style={'description_width': '60px'},
            layout=widgets.Layout(width='250px')
        )
        
        self.early_payments1 = []
        for i in range(self.max_early_payments):
            payment_group = {
                'enabled': widgets.Checkbox(
                    value=i < 3,
                    description=f'#{i+1}',
                    style={'description_width': '30px'},
                    layout=widgets.Layout(width='60px')
                ),
                'month': widgets.IntText(
                    value=12 + i*12,
                    description='Tháng:',
                    style={'description_width': '50px'},
                    layout=widgets.Layout(width='130px')
                ),
                'amount': widgets.FloatText(
                    value=200.0 + i*100,
                    description='Triệu:',
                    style={'description_width': '50px'},
                    layout=widgets.Layout(width='130px')
                ),
                'fee_rate': widgets.FloatText(
                    value=2.0 + i*0.5,
                    description='Phí %:',
                    style={'description_width': '50px'},
                    layout=widgets.Layout(width='130px')
                )
            }
            self.early_payments1.append(payment_group)
        
        # === TRẢ TRƯỚC HẠN PA2 ===
        self.early_payment2_enabled = widgets.Checkbox(
            value=False,
            description='Kích hoạt',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='100px')
        )
        
        self.num_early_payments2_widget = widgets.IntSlider(
            value=3,
            min=1,
            max=self.max_early_payments,
            description='Số lần:',
            style={'description_width': '60px'},
            layout=widgets.Layout(width='250px')
        )
        
        self.early_payments2 = []
        for i in range(self.max_early_payments):
            payment_group = {
                'enabled': widgets.Checkbox(
                    value=i < 3,
                    description=f'#{i+1}',
                    style={'description_width': '30px'},
                    layout=widgets.Layout(width='60px')
                ),
                'month': widgets.IntText(
                    value=24 + i*12,
                    description='Tháng:',
                    style={'description_width': '50px'},
                    layout=widgets.Layout(width='130px')
                ),
                'amount': widgets.FloatText(
                    value=150.0 + i*75,
                    description='Triệu:',
                    style={'description_width': '50px'},
                    layout=widgets.Layout(width='130px')
                ),
                'fee_rate': widgets.FloatText(
                    value=1.5 + i*0.3,
                    description='Phí %:',
                    style={'description_width': '50px'},
                    layout=widgets.Layout(width='130px')
                )
            }
            self.early_payments2.append(payment_group)
        
        # === KẾT QUẢ HIỂN THỊ ===
        self.result1_monthly = widgets.HTML(
            value="<div style='padding: 15px; background: #fff5f5; border: 2px solid #E74C3C; border-radius: 8px;'><h4 style='color: #E74C3C; margin: 0;'>Chưa tính toán</h4></div>"
        )
        
        self.result2_monthly = widgets.HTML(
            value="<div style='padding: 15px; background: #f0f8ff; border: 2px solid #3498DB; border-radius: 8px;'><h4 style='color: #3498DB; margin: 0;'>Chưa tính toán</h4></div>"
        )
        
        self.comparison_result = widgets.HTML(
            value="<div style='padding: 20px; background: #f5f5f5; border: 2px solid #95a5a6; border-radius: 8px; text-align: center;'><h3 style='color: #7f8c8d; margin: 0;'>Nhấn 'Tính Toán' để so sánh</h3></div>"
        )
        
        # === BUTTONS ===
        self.calculate_button = widgets.Button(
            description='🔍 Tính Toán & So Sánh',
            button_style='success',
            layout=widgets.Layout(width='250px', height='50px'),
            style={'font_weight': 'bold'}
        )
        
        self.reset_button = widgets.Button(
            description='🔄 Reset',
            button_style='warning',
            layout=widgets.Layout(width='150px', height='50px')
        )
        
        self.copy_rates_button = widgets.Button(
            description='📋 Copy Lãi Suất PA1→PA2',
            button_style='info',
            layout=widgets.Layout(width='200px', height='40px')
        )
        
        self.copy_rates_reverse_button = widgets.Button(
            description='📋 Copy Lãi Suất PA2→PA1',
            button_style='info',
            layout=widgets.Layout(width='200px', height='40px')
        )
        
        self.copy_prepay_button = widgets.Button(
            description='📋 Copy Trả Trước PA1→PA2',
            button_style='info',
            layout=widgets.Layout(width='200px', height='40px')
        )
        
        self.copy_prepay_reverse_button = widgets.Button(
            description='📋 Copy Trả Trước PA2→PA1',
            button_style='info',
            layout=widgets.Layout(width='200px', height='40px')
        )
        
        self.update_rates1_button = widgets.Button(
            description='⚡ Cập Nhật',
            button_style='primary',
            layout=widgets.Layout(width='120px', height='35px')
        )
        
        self.update_rates2_button = widgets.Button(
            description='⚡ Cập Nhật',
            button_style='primary',
            layout=widgets.Layout(width='120px', height='35px')
        )
        
        self.export_csv_button = widgets.Button(
            description='💾 Xuất File CSV',
            button_style='success',
            layout=widgets.Layout(width='200px', height='50px'),
            style={'font_weight': 'bold'}
        )
        
        self.output = widgets.Output()
        
        # Event handlers
        self.calculate_button.on_click(self.on_calculate_clicked)
        self.reset_button.on_click(self.on_reset_clicked)
        self.copy_rates_button.on_click(self.on_copy_rates_clicked)
        self.copy_rates_reverse_button.on_click(self.on_copy_rates_reverse_clicked)
        self.copy_prepay_button.on_click(self.on_copy_prepay_clicked)
        self.copy_prepay_reverse_button.on_click(self.on_copy_prepay_reverse_clicked)
        self.update_rates1_button.on_click(self.on_update_rates1_clicked)
        self.update_rates2_button.on_click(self.on_update_rates2_clicked)
        self.export_csv_button.on_click(self.on_export_csv_clicked)
        
        # Lưu trữ dữ liệu để export
        self.last_df1 = None
        self.last_df2 = None
        self.last_calculation_time = None
        
    def setup_layout(self):
        """Thiết lập giao diện chuyên nghiệp"""
        # Header
        header = widgets.HTML(
            value="""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 25px; border-radius: 15px; text-align: center; 
                        box-shadow: 0 8px 16px rgba(0,0,0,0.2); margin-bottom: 20px;'>
                <h1 style='color: white; margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                    💰 MÁY TÍNH SO SÁNH PHƯƠNG ÁN VAY
                </h1>
                <p style='color: #e0e0e0; margin: 10px 0 0 0; font-size: 14px;'>
                    Kỳ điều chỉnh lãi suất 6 tháng | Trả trước hạn linh hoạt
                </p>
            </div>
            """
        )
        
        # Thông số chung
        common_box = widgets.VBox([
            widgets.HTML("<div style='background: #2c3e50; color: white; padding: 10px; border-radius: 8px 8px 0 0; margin-bottom: 0;'><h3 style='margin: 0; font-size: 16px;'>⚙️ THÔNG SỐ CHUNG</h3></div>"),
            widgets.VBox([
                self.principal_widget
            ], layout=widgets.Layout(padding='15px', background='#ecf0f1', border='2px solid #2c3e50', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='100%', margin='0 0 20px 0'))
        
        # Phương án 1
        self.rate1_container = widgets.VBox(
            layout=widgets.Layout(height='280px', overflow_y='auto', border='1px solid #ddd', 
                                padding='10px', background='white', border_radius='5px')
        )
        
        plan1_rate_controls = widgets.HBox([
            self.auto_increase1_widget,
            self.auto_increase_rate1_widget,
            self.update_rates1_button
        ], layout=widgets.Layout(align_items='center', justify_content='flex-start'))
        
        plan1_box = widgets.VBox([
            widgets.HTML("<div style='background: #E74C3C; color: white; padding: 10px; border-radius: 8px 8px 0 0;'><h3 style='margin: 0; font-size: 16px;'>📊 PHƯƠNG ÁN 1</h3></div>"),
            widgets.VBox([
                self.term1_widget,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-weight: bold;'>Lãi suất:</div>"),
                self.initial_rate1_widget,
                plan1_rate_controls,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-weight: bold; font-size: 13px;'>Lãi suất theo kỳ (6 tháng):</div>"),
                self.rate1_container,
                widgets.HTML("<div style='margin: 15px 0 5px 0; font-weight: bold;'>📈 Kết quả tính toán:</div>"),
                self.result1_monthly
            ], layout=widgets.Layout(padding='15px', background='#fff5f5', border='2px solid #E74C3C', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='48%'))
        
        # Phương án 2
        self.rate2_container = widgets.VBox(
            layout=widgets.Layout(height='280px', overflow_y='auto', border='1px solid #ddd', 
                                padding='10px', background='white', border_radius='5px')
        )
        
        plan2_rate_controls = widgets.HBox([
            self.auto_increase2_widget,
            self.auto_increase_rate2_widget,
            self.update_rates2_button
        ], layout=widgets.Layout(align_items='center', justify_content='flex-start'))
        
        plan2_box = widgets.VBox([
            widgets.HTML("<div style='background: #3498DB; color: white; padding: 10px; border-radius: 8px 8px 0 0;'><h3 style='margin: 0; font-size: 16px;'>📊 PHƯƠNG ÁN 2</h3></div>"),
            widgets.VBox([
                self.term2_widget,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-weight: bold;'>Lãi suất:</div>"),
                self.initial_rate2_widget,
                plan2_rate_controls,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-weight: bold; font-size: 13px;'>Lãi suất theo kỳ (6 tháng):</div>"),
                self.rate2_container,
                widgets.HTML("<div style='margin: 15px 0 5px 0; font-weight: bold;'>📈 Kết quả tính toán:</div>"),
                self.result2_monthly
            ], layout=widgets.Layout(padding='15px', background='#f0f8ff', border='2px solid #3498DB', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='48%'))
        
        plans_layout = widgets.HBox([plan1_box, plan2_box], 
                                    layout=widgets.Layout(justify_content='space-between', margin='0 0 20px 0'))
        
        # Trả trước hạn PA1
        self.early_payment1_container = widgets.VBox(
            layout=widgets.Layout(height='250px', overflow_y='auto', border='1px solid #ddd', 
                                padding='10px', background='white', border_radius='5px')
        )
        
        early1_controls = widgets.HBox([
            self.early_payment1_enabled,
            self.num_early_payments1_widget
        ], layout=widgets.Layout(align_items='center'))
        
        early1_box = widgets.VBox([
            widgets.HTML("<div style='background: #c0392b; color: white; padding: 8px; border-radius: 8px 8px 0 0;'><h4 style='margin: 0; font-size: 14px;'>💵 TRẢ TRƯỚC HẠN - PA1</h4></div>"),
            widgets.VBox([
                early1_controls,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-size: 12px; color: #555;'>Cấu hình chi tiết:</div>"),
                self.early_payment1_container
            ], layout=widgets.Layout(padding='12px', background='#ffe6e6', border='2px solid #c0392b', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='48%'))
        
        # Trả trước hạn PA2
        self.early_payment2_container = widgets.VBox(
            layout=widgets.Layout(height='250px', overflow_y='auto', border='1px solid #ddd', 
                                padding='10px', background='white', border_radius='5px')
        )
        
        early2_controls = widgets.HBox([
            self.early_payment2_enabled,
            self.num_early_payments2_widget
        ], layout=widgets.Layout(align_items='center'))
        
        early2_box = widgets.VBox([
            widgets.HTML("<div style='background: #2980b9; color: white; padding: 8px; border-radius: 8px 8px 0 0;'><h4 style='margin: 0; font-size: 14px;'>💵 TRẢ TRƯỚC HẠN - PA2</h4></div>"),
            widgets.VBox([
                early2_controls,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-size: 12px; color: #555;'>Cấu hình chi tiết:</div>"),
                self.early_payment2_container
            ], layout=widgets.Layout(padding='12px', background='#e6f2ff', border='2px solid #2980b9', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='48%'))
        
        early_layout = widgets.HBox([early1_box, early2_box], 
                                    layout=widgets.Layout(justify_content='space-between', margin='0 0 20px 0'))
        
        # Buttons & Results
        button_row1 = widgets.HBox([
            self.calculate_button,
            self.reset_button,
            self.export_csv_button
        ], layout=widgets.Layout(justify_content='center', margin='10px 0'))
        
        button_row2 = widgets.HBox([
            self.copy_rates_button,
            self.copy_rates_reverse_button,
            self.copy_prepay_button,
            self.copy_prepay_reverse_button
        ], layout=widgets.Layout(justify_content='center', margin='10px 0'))
        
        result_box = widgets.VBox([
            widgets.HTML("<div style='background: #34495e; color: white; padding: 10px; border-radius: 8px 8px 0 0;'><h3 style='margin: 0; font-size: 16px;'>🎯 KẾT QUẢ SO SÁNH</h3></div>"),
            widgets.VBox([
                self.comparison_result
            ], layout=widgets.Layout(padding='15px', background='white', border='2px solid #34495e', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='100%', margin='20px 0'))
        
        # Main layout
        self.main_layout = widgets.VBox([
            header,
            common_box,
            plans_layout,
            early_layout,
            button_row1,
            button_row2,
            result_box,
            self.output
        ], layout=widgets.Layout(padding='20px', background='#f8f9fa'))
        
    def auto_update_rates(self, plan_number):
        """Tự động cập nhật lãi suất"""
        if plan_number == 1:
            initial_rate = self.initial_rate1_widget.value
            auto_increase = self.auto_increase1_widget.value
            increase_rate = self.auto_increase_rate1_widget.value
            term_years = self.term1_widget.value
            widgets_list = self.rate1_widgets
        else:
            initial_rate = self.initial_rate2_widget.value
            auto_increase = self.auto_increase2_widget.value
            increase_rate = self.auto_increase_rate2_widget.value
            term_years = self.term2_widget.value
            widgets_list = self.rate2_widgets
        
        required_periods = (term_years * 12 + 5) // 6
        
        for i in range(min(required_periods, len(widgets_list))):
            if auto_increase:
                widgets_list[i].value = min(initial_rate + i * increase_rate, 25.0)
            else:
                widgets_list[i].value = initial_rate
    
    def on_update_rates1_clicked(self, button):
        self.auto_update_rates(1)
        self.update_rate_widgets_visibility()
        print("✅ Đã cập nhật lãi suất cho Phương án 1!")
    
    def on_update_rates2_clicked(self, button):
        self.auto_update_rates(2)
        self.update_rate_widgets_visibility()
        print("✅ Đã cập nhật lãi suất cho Phương án 2!")
    
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
        """Tính toán lịch trình thanh toán"""
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
    
    def apply_multiple_early_payments(self, df, plan_number):
        """Áp dụng trả trước hạn"""
        if plan_number == 1:
            enabled = self.early_payment1_enabled.value
            early_payments_list = self.early_payments1
            num_payments = self.num_early_payments1_widget.value
        else:
            enabled = self.early_payment2_enabled.value
            early_payments_list = self.early_payments2
            num_payments = self.num_early_payments2_widget.value
            
        if not enabled:
            return df, 0
        
        df_modified = df.copy()
        df_modified['Trả trước hạn (VND)'] = 0
        df_modified['Phí trả trước (VND)'] = 0
        total_prepayment_fee = 0
        
        active_payments = []
        for i, payment in enumerate(early_payments_list[:num_payments]):
            if payment['enabled'].value and payment['month'].value <= len(df_modified):
                active_payments.append({
                    'month': payment['month'].value,
                    'amount': payment['amount'].value * 1_000_000,
                    'fee_rate': payment['fee_rate'].value
                })
        
        active_payments.sort(key=lambda x: x['month'])
        
        for payment in active_payments:
            month = payment['month']
            amount = payment['amount']
            fee_rate = payment['fee_rate']
            
            if month <= len(df_modified):
                remaining_balance = df_modified.iloc[month-1]['Dư nợ cuối kỳ (VND)']
                prepayment_fee = remaining_balance * fee_rate / 100
                total_prepayment_fee += prepayment_fee
                actual_payment = min(amount, remaining_balance)
                new_remaining = remaining_balance - actual_payment
                
                df_modified.loc[month-1, 'Dư nợ cuối kỳ (VND)'] = new_remaining
                df_modified.loc[month-1, 'Trả trước hạn (VND)'] = actual_payment
                df_modified.loc[month-1, 'Phí trả trước (VND)'] = prepayment_fee
                df_modified.loc[month-1, 'Tổng thanh toán (VND)'] += actual_payment + prepayment_fee
                
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
                    
                    if i != month-1:
                        df_modified.loc[i, 'Trả trước hạn (VND)'] = 0
                        df_modified.loc[i, 'Phí trả trước (VND)'] = 0
        
        return df_modified, total_prepayment_fee
    
    def update_rate_widgets_visibility(self):
        """Cập nhật hiển thị widgets lãi suất"""
        required_periods1 = (self.term1_widget.value * 12 + 5) // 6
        visible_widgets1 = []
        for i in range(required_periods1):
            if i < len(self.rate1_widgets):
                widget = self.rate1_widgets[i]
                max_month = min((i+1)*6, self.term1_widget.value*12)
                widget.description = f'Kỳ {i+1} (T{i*6+1}-{max_month}):'
                visible_widgets1.append(widget)
        self.rate1_container.children = visible_widgets1
        
        required_periods2 = (self.term2_widget.value * 12 + 5) // 6
        visible_widgets2 = []
        for i in range(required_periods2):
            if i < len(self.rate2_widgets):
                widget = self.rate2_widgets[i]
                max_month = min((i+1)*6, self.term2_widget.value*12)
                widget.description = f'Kỳ {i+1} (T{i*6+1}-{max_month}):'
                visible_widgets2.append(widget)
        self.rate2_container.children = visible_widgets2
    
    def update_early_payment_widgets_visibility(self):
        """Cập nhật hiển thị widgets trả trước hạn"""
        if self.early_payment1_enabled.value:
            visible_widgets1 = []
            num_payments1 = self.num_early_payments1_widget.value
            for i, payment in enumerate(self.early_payments1[:num_payments1]):
                row = widgets.HBox([
                    payment['enabled'],
                    payment['month'],
                    payment['amount'],
                    payment['fee_rate']
                ], layout=widgets.Layout(align_items='center', margin='2px 0'))
                visible_widgets1.append(row)
            self.early_payment1_container.children = visible_widgets1
        else:
            self.early_payment1_container.children = []
        
        if self.early_payment2_enabled.value:
            visible_widgets2 = []
            num_payments2 = self.num_early_payments2_widget.value
            for i, payment in enumerate(self.early_payments2[:num_payments2]):
                row = widgets.HBox([
                    payment['enabled'],
                    payment['month'],
                    payment['amount'],
                    payment['fee_rate']
                ], layout=widgets.Layout(align_items='center', margin='2px 0'))
                visible_widgets2.append(row)
            self.early_payment2_container.children = visible_widgets2
        else:
            self.early_payment2_container.children = []
    
    def format_currency(self, value):
        """Format số tiền"""
        return f"{value:,.0f}".replace(",", ".")
    
    def update_result_displays(self, df1, df2, prepay_fee1, prepay_fee2):
        """Cập nhật hiển thị kết quả trên GUI"""
        # Phương án 1
        avg_monthly1 = df1['Tổng thanh toán (VND)'].mean()
        total_interest1 = df1['Tiền lãi (VND)'].sum()
        total_payment1 = df1['Tổng thanh toán (VND)'].sum()
        total_early1 = df1['Trả trước hạn (VND)'].sum() if 'Trả trước hạn (VND)' in df1.columns else 0
        
        result1_html = f"""
        <div style='padding: 15px; background: white; border: 2px solid #E74C3C; border-radius: 8px;'>
            <h4 style='color: #E74C3C; margin: 0 0 12px 0; font-size: 16px;'>📊 Phương án {self.term1_widget.value} năm</h4>
            <div style='font-size: 13px; line-height: 1.8;'>
                <div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #fdd;'>
                    <span><b>Trả hàng tháng TB:</b></span>
                    <span style='color: #E74C3C; font-weight: bold;'>{self.format_currency(avg_monthly1/1_000_000)} triệu VND</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #fdd;'>
                    <span>Tổng lãi:</span>
                    <span>{self.format_currency(total_interest1/1_000_000)} triệu</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #fdd;'>
                    <span>Tổng thanh toán:</span>
                    <span>{self.format_currency(total_payment1/1_000_000)} triệu</span>
                </div>
                {"<div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #fdd;'><span>Trả trước hạn:</span><span>" + self.format_currency(total_early1/1_000_000) + " triệu</span></div>" if total_early1 > 0 else ""}
                {"<div style='display: flex; justify-content: space-between; padding: 5px 0;'><span>Phí trả trước:</span><span>" + self.format_currency(prepay_fee1/1_000_000) + " triệu</span></div>" if prepay_fee1 > 0 else ""}
                <div style='display: flex; justify-content: space-between; padding: 8px 0; margin-top: 5px; background: #fff5f5; border-radius: 5px;'>
                    <span style='padding-left: 5px;'><b>Thời gian:</b></span>
                    <span style='padding-right: 5px;'><b>{len(df1)} tháng</b></span>
                </div>
            </div>
        </div>
        """
        self.result1_monthly.value = result1_html
        
        # Phương án 2
        avg_monthly2 = df2['Tổng thanh toán (VND)'].mean()
        total_interest2 = df2['Tiền lãi (VND)'].sum()
        total_payment2 = df2['Tổng thanh toán (VND)'].sum()
        total_early2 = df2['Trả trước hạn (VND)'].sum() if 'Trả trước hạn (VND)' in df2.columns else 0
        
        result2_html = f"""
        <div style='padding: 15px; background: white; border: 2px solid #3498DB; border-radius: 8px;'>
            <h4 style='color: #3498DB; margin: 0 0 12px 0; font-size: 16px;'>📊 Phương án {self.term2_widget.value} năm</h4>
            <div style='font-size: 13px; line-height: 1.8;'>
                <div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #ddf;'>
                    <span><b>Trả hàng tháng TB:</b></span>
                    <span style='color: #3498DB; font-weight: bold;'>{self.format_currency(avg_monthly2/1_000_000)} triệu VND</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #ddf;'>
                    <span>Tổng lãi:</span>
                    <span>{self.format_currency(total_interest2/1_000_000)} triệu</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #ddf;'>
                    <span>Tổng thanh toán:</span>
                    <span>{self.format_currency(total_payment2/1_000_000)} triệu</span>
                </div>
                {"<div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #ddf;'><span>Trả trước hạn:</span><span>" + self.format_currency(total_early2/1_000_000) + " triệu</span></div>" if total_early2 > 0 else ""}
                {"<div style='display: flex; justify-content: space-between; padding: 5px 0;'><span>Phí trả trước:</span><span>" + self.format_currency(prepay_fee2/1_000_000) + " triệu</span></div>" if prepay_fee2 > 0 else ""}
                <div style='display: flex; justify-content: space-between; padding: 8px 0; margin-top: 5px; background: #f0f8ff; border-radius: 5px;'>
                    <span style='padding-left: 5px;'><b>Thời gian:</b></span>
                    <span style='padding-right: 5px;'><b>{len(df2)} tháng</b></span>
                </div>
            </div>
        </div>
        """
        self.result2_monthly.value = result2_html
        
        # So sánh
        difference = total_payment1 - total_payment2
        principal = self.principal_widget.value * 1_000_000
        
        if abs(difference) < 1000:
            comparison_html = """
            <div style='padding: 25px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                        border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='color: #7f8c8d; margin: 0; font-size: 20px;'>⚖️ HAI PHƯƠNG ÁN TƯƠNG ĐƯƠNG</h3>
                <p style='color: #95a5a6; margin: 10px 0 0 0;'>Chênh lệch không đáng kể</p>
            </div>
            """
        elif difference > 0:
            comparison_html = f"""
            <div style='padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 10px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.2);'>
                <h3 style='color: white; margin: 0 0 10px 0; font-size: 22px;'>🏆 PHƯƠNG ÁN 2 TỐT HƠN</h3>
                <div style='background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;'>
                    <div style='color: #fff; font-size: 16px; margin-bottom: 5px;'>Tiết kiệm được:</div>
                    <div style='color: #fff; font-size: 28px; font-weight: bold;'>{self.format_currency(difference/1_000_000)} triệu VND</div>
                </div>
                <div style='color: #e0e0e0; font-size: 14px;'>
                    Tương đương <b>{(difference/principal)*100:.2f}%</b> số tiền vay
                </div>
            </div>
            """
        else:
            comparison_html = f"""
            <div style='padding: 25px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        border-radius: 10px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.2);'>
                <h3 style='color: white; margin: 0 0 10px 0; font-size: 22px;'>🏆 PHƯƠNG ÁN 1 TỐT HƠN</h3>
                <div style='background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;'>
                    <div style='color: #fff; font-size: 16px; margin-bottom: 5px;'>Tiết kiệm được:</div>
                    <div style='color: #fff; font-size: 28px; font-weight: bold;'>{self.format_currency(abs(difference)/1_000_000)} triệu VND</div>
                </div>
                <div style='color: #e0e0e0; font-size: 14px;'>
                    Tương đương <b>{(abs(difference)/principal)*100:.2f}%</b> số tiền vay
                </div>
            </div>
            """
        
        self.comparison_result.value = comparison_html
    
    def on_export_csv_clicked(self, button):
        """Xuất kết quả ra file CSV"""
        if self.last_df1 is None or self.last_df2 is None:
            print("❌ Chưa có dữ liệu để xuất! Vui lòng nhấn 'Tính Toán' trước.")
            return
        
        try:
            from datetime import datetime
            import os
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Tạo thư mục nếu chưa có
            output_dir = "mortgage_exports"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Xuất Phương án 1
            filename1 = f"{output_dir}/PA1_{self.term1_widget.value}nam_{timestamp}.csv"
            df1_export = self.last_df1.copy()
            
            # Format lại số tiền thành triệu VND
            for col in df1_export.columns:
                if 'VND' in col:
                    df1_export[col] = df1_export[col] / 1_000_000
                    # Đổi tên cột
                    new_col = col.replace('(VND)', '(triệu VND)')
                    df1_export.rename(columns={col: new_col}, inplace=True)
            
            df1_export.to_csv(filename1, index=False, encoding='utf-8-sig')
            
            # Xuất Phương án 2
            filename2 = f"{output_dir}/PA2_{self.term2_widget.value}nam_{timestamp}.csv"
            df2_export = self.last_df2.copy()
            
            # Format lại số tiền thành triệu VND
            for col in df2_export.columns:
                if 'VND' in col:
                    df2_export[col] = df2_export[col] / 1_000_000
                    new_col = col.replace('(VND)', '(triệu VND)')
                    df2_export.rename(columns={col: new_col}, inplace=True)
            
            df2_export.to_csv(filename2, index=False, encoding='utf-8-sig')
            
            # Xuất file so sánh tổng hợp
            filename_summary = f"{output_dir}/So_Sanh_{timestamp}.csv"
            
            # Tạo DataFrame tổng hợp
            total1 = self.last_df1['Tổng thanh toán (VND)'].sum()
            total_interest1 = self.last_df1['Tiền lãi (VND)'].sum()
            total_early1 = self.last_df1['Trả trước hạn (VND)'].sum() if 'Trả trước hạn (VND)' in self.last_df1.columns else 0
            prepay_fee1 = self.last_df1['Phí trả trước (VND)'].sum() if 'Phí trả trước (VND)' in self.last_df1.columns else 0
            
            total2 = self.last_df2['Tổng thanh toán (VND)'].sum()
            total_interest2 = self.last_df2['Tiền lãi (VND)'].sum()
            total_early2 = self.last_df2['Trả trước hạn (VND)'].sum() if 'Trả trước hạn (VND)' in self.last_df2.columns else 0
            prepay_fee2 = self.last_df2['Phí trả trước (VND)'].sum() if 'Phí trả trước (VND)' in self.last_df2.columns else 0
            
            summary_data = {
                'Thông số': [
                    'Số tiền vay (triệu VND)',
                    'Thời gian vay (năm)',
                    'Thời gian vay (tháng)',
                    'Lãi suất ban đầu (%/năm)',
                    'Mức tăng lãi suất (%/kỳ)',
                    '',
                    'Trả hàng tháng TB (triệu VND)',
                    'Tổng tiền lãi (triệu VND)',
                    'Tổng thanh toán (triệu VND)',
                    'Tổng trả trước hạn (triệu VND)',
                    'Tổng phí trả trước (triệu VND)',
                    '',
                    'Chênh lệch tổng TT (triệu VND)',
                    'Phương án tốt hơn'
                ],
                'Phương án 1': [
                    self.principal_widget.value,
                    self.term1_widget.value,
                    len(self.last_df1),
                    self.initial_rate1_widget.value,
                    self.auto_increase_rate1_widget.value,
                    '',
                    round(self.last_df1['Tổng thanh toán (VND)'].mean() / 1_000_000, 2),
                    round(total_interest1 / 1_000_000, 2),
                    round(total1 / 1_000_000, 2),
                    round(total_early1 / 1_000_000, 2),
                    round(prepay_fee1 / 1_000_000, 2),
                    '',
                    round((total1 - total2) / 1_000_000, 2) if total1 > total2 else '',
                    'Phương án 1 tốt hơn' if total1 < total2 else ''
                ],
                'Phương án 2': [
                    self.principal_widget.value,
                    self.term2_widget.value,
                    len(self.last_df2),
                    self.initial_rate2_widget.value,
                    self.auto_increase_rate2_widget.value,
                    '',
                    round(self.last_df2['Tổng thanh toán (VND)'].mean() / 1_000_000, 2),
                    round(total_interest2 / 1_000_000, 2),
                    round(total2 / 1_000_000, 2),
                    round(total_early2 / 1_000_000, 2),
                    round(prepay_fee2 / 1_000_000, 2),
                    '',
                    round((total2 - total1) / 1_000_000, 2) if total2 > total1 else '',
                    'Phương án 2 tốt hơn' if total2 < total1 else ''
                ]
            }
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_csv(filename_summary, index=False, encoding='utf-8-sig')
            
            print("="*80)
            print("✅ XUẤT FILE THÀNH CÔNG!")
            print("="*80)
            print(f"📁 Thư mục: {output_dir}/")
            print(f"📄 File PA1: {os.path.basename(filename1)}")
            print(f"📄 File PA2: {os.path.basename(filename2)}")
            print(f"📊 File so sánh: {os.path.basename(filename_summary)}")
            print()
            print("💡 Các file đã được lưu với:")
            print("   - Đơn vị: Triệu VND")
            print("   - Encoding: UTF-8 with BOM (mở tốt trong Excel)")
            print("   - Timestamp: " + timestamp)
            print("="*80)
            
        except Exception as e:
            print(f"❌ Lỗi khi xuất file: {str(e)}")
    
    def on_calculate_clicked(self, button):
        """Xử lý khi nhấn nút tính toán"""
        with self.output:
            clear_output(wait=True)
            self.display_comparison_results()
    
    def on_reset_clicked(self, button):
        """Reset về giá trị mặc định"""
        self.principal_widget.value = 1500
        self.term1_widget.value = 5
        self.term2_widget.value = 10
        self.initial_rate1_widget.value = 6.0
        self.initial_rate2_widget.value = 6.0
        self.auto_increase1_widget.value = True
        self.auto_increase2_widget.value = True
        self.auto_increase_rate1_widget.value = 0.5
        self.auto_increase_rate2_widget.value = 0.5
        
        for i, widget in enumerate(self.rate1_widgets[:20]):
            widget.value = 6.0 + min(i * 0.5, 9.0)
        
        for i, widget in enumerate(self.rate2_widgets[:20]):
            widget.value = 6.0 + min(i * 0.5, 9.0)
        
        self.early_payment1_enabled.value = False
        self.num_early_payments1_widget.value = 3
        for i, payment in enumerate(self.early_payments1):
            payment['enabled'].value = i < 3
            payment['month'].value = 12 + i*12
            payment['amount'].value = 200.0 + i*100
            payment['fee_rate'].value = 2.0 + i*0.5
        
        self.early_payment2_enabled.value = False
        self.num_early_payments2_widget.value = 3
        for i, payment in enumerate(self.early_payments2):
            payment['enabled'].value = i < 3
            payment['month'].value = 24 + i*12
            payment['amount'].value = 150.0 + i*75
            payment['fee_rate'].value = 1.5 + i*0.3
        
        self.result1_monthly.value = "<div style='padding: 15px; background: #fff5f5; border: 2px solid #E74C3C; border-radius: 8px;'><h4 style='color: #E74C3C; margin: 0;'>Chưa tính toán</h4></div>"
        self.result2_monthly.value = "<div style='padding: 15px; background: #f0f8ff; border: 2px solid #3498DB; border-radius: 8px;'><h4 style='color: #3498DB; margin: 0;'>Chưa tính toán</h4></div>"
        self.comparison_result.value = "<div style='padding: 20px; background: #f5f5f5; border: 2px solid #95a5a6; border-radius: 8px; text-align: center;'><h3 style='color: #7f8c8d; margin: 0;'>Nhấn 'Tính Toán' để so sánh</h3></div>"
        
        self.update_rate_widgets_visibility()
        self.update_early_payment_widgets_visibility()
        
        with self.output:
            clear_output(wait=True)
            print("✅ Đã reset về giá trị mặc định.")
    
    def on_copy_rates_clicked(self, button):
        """Copy lãi suất từ PA1 sang PA2"""
        self.initial_rate2_widget.value = self.initial_rate1_widget.value
        self.auto_increase2_widget.value = self.auto_increase1_widget.value
        self.auto_increase_rate2_widget.value = self.auto_increase_rate1_widget.value
        required_periods2 = (self.term2_widget.value * 12 + 5) // 6
        for i in range(min(required_periods2, len(self.rate1_widgets))):
            if i < len(self.rate2_widgets):
                self.rate2_widgets[i].value = self.rate1_widgets[i].value
        self.update_rate_widgets_visibility()
        print("✅ Đã copy lãi suất từ PA1 → PA2!")
    
    def on_copy_rates_reverse_clicked(self, button):
        """Copy lãi suất từ PA2 sang PA1"""
        self.initial_rate1_widget.value = self.initial_rate2_widget.value
        self.auto_increase1_widget.value = self.auto_increase2_widget.value
        self.auto_increase_rate1_widget.value = self.auto_increase_rate2_widget.value
        required_periods1 = (self.term1_widget.value * 12 + 5) // 6
        for i in range(min(required_periods1, len(self.rate2_widgets))):
            if i < len(self.rate1_widgets):
                self.rate1_widgets[i].value = self.rate2_widgets[i].value
        self.update_rate_widgets_visibility()
        print("✅ Đã copy lãi suất từ PA2 → PA1!")
    
    def on_copy_prepay_clicked(self, button):
        """Copy cài đặt trả trước hạn từ PA1 sang PA2"""
        self.early_payment2_enabled.value = self.early_payment1_enabled.value
        self.num_early_payments2_widget.value = self.num_early_payments1_widget.value
        for i in range(self.max_early_payments):
            self.early_payments2[i]['enabled'].value = self.early_payments1[i]['enabled'].value
            self.early_payments2[i]['month'].value = self.early_payments1[i]['month'].value
            self.early_payments2[i]['amount'].value = self.early_payments1[i]['amount'].value
            self.early_payments2[i]['fee_rate'].value = self.early_payments1[i]['fee_rate'].value
        self.update_early_payment_widgets_visibility()
        print("✅ Đã copy cài đặt trả trước hạn từ PA1 → PA2!")
    
    def on_copy_prepay_reverse_clicked(self, button):
        """Copy cài đặt trả trước hạn từ PA2 sang PA1"""
        self.early_payment1_enabled.value = self.early_payment2_enabled.value
        self.num_early_payments1_widget.value = self.num_early_payments2_widget.value
        for i in range(self.max_early_payments):
            self.early_payments1[i]['enabled'].value = self.early_payments2[i]['enabled'].value
            self.early_payments1[i]['month'].value = self.early_payments2[i]['month'].value
            self.early_payments1[i]['amount'].value = self.early_payments2[i]['amount'].value
            self.early_payments1[i]['fee_rate'].value = self.early_payments2[i]['fee_rate'].value
        self.update_early_payment_widgets_visibility()
        print("✅ Đã copy cài đặt trả trước hạn từ PA2 → PA1!")
    
    def display_comparison_results(self):
        """Hiển thị kết quả so sánh"""
        try:
            principal = self.principal_widget.value * 1_000_000
            rates1 = [w.value for w in self.rate1_container.children]
            rates2 = [w.value for w in self.rate2_container.children]
            
            df1 = self.calculate_schedule(principal, self.term1_widget.value, rates1)
            df2 = self.calculate_schedule(principal, self.term2_widget.value, rates2)
            
            df1, prepay_fee1 = self.apply_multiple_early_payments(df1, 1)
            df2, prepay_fee2 = self.apply_multiple_early_payments(df2, 2)
            
            # Lưu dữ liệu để export
            self.last_df1 = df1.copy()
            self.last_df2 = df2.copy()
            self.last_calculation_time = datetime.now()
            
            # Cập nhật GUI
            self.update_result_displays(df1, df2, prepay_fee1, prepay_fee2)
            
            # In thông tin chi tiết
            print("="*120)
            print("📊 KẾT QUẢ SO SÁNH CHI TIẾT")
            print("="*120)
            
            self.display_early_payment_summary()
            self.display_monthly_details(df1, df2)
            self.create_individual_plotly_charts(df1, df2)
            
            print("\n" + "="*80)
            print("💡 Dữ liệu đã sẵn sàng! Nhấn nút '💾 Xuất File CSV' để lưu kết quả.")
            print("="*80)
            
        except Exception as e:
            print(f"❌ Có lỗi xảy ra: {str(e)}")
    
    def display_early_payment_summary(self):
        """Hiển thị tóm tắt trả trước hạn"""
        print(f"\n{'='*80}")
        print("💵 THÔNG TIN TRẢ TRƯỚC HẠN")
        print("="*80)
        
        print(f"\n📍 PHƯƠNG ÁN 1:")
        if self.early_payment1_enabled.value:
            active_count1 = 0
            for i, payment in enumerate(self.early_payments1[:self.num_early_payments1_widget.value]):
                if payment['enabled'].value:
                    active_count1 += 1
                    print(f"  Lần {active_count1}: Tháng {payment['month'].value} - "
                          f"{payment['amount'].value:,.0f} triệu VND - "
                          f"Phí {payment['fee_rate'].value:.1f}%")
            if active_count1 == 0:
                print("  ⚠️ Không có lần nào được kích hoạt")
        else:
            print("  ❌ Không sử dụng")
        
        print(f"\n📍 PHƯƠNG ÁN 2:")
        if self.early_payment2_enabled.value:
            active_count2 = 0
            for i, payment in enumerate(self.early_payments2[:self.num_early_payments2_widget.value]):
                if payment['enabled'].value:
                    active_count2 += 1
                    print(f"  Lần {active_count2}: Tháng {payment['month'].value} - "
                          f"{payment['amount'].value:,.0f} triệu VND - "
                          f"Phí {payment['fee_rate'].value:.1f}%")
            if active_count2 == 0:
                print("  ⚠️ Không có lần nào được kích hoạt")
        else:
            print("  ❌ Không sử dụng")
    
    def display_monthly_details(self, df1, df2):
        """Hiển thị chi tiết 12 tháng đầu"""
        print(f"\n{'='*80}")
        print("📅 CHI TIẾT 12 THÁNG ĐẦU TIÊN")
        print("="*80)
        
        print(f"\n🔴 PHƯƠNG ÁN 1 ({self.term1_widget.value} năm):")
        display_cols1 = ['Tháng', 'Lãi suất (%/năm)', 'Tổng thanh toán (VND)', 'Dư nợ cuối kỳ (VND)']
        if 'Trả trước hạn (VND)' in df1.columns and df1['Trả trước hạn (VND)'].sum() > 0:
            display_cols1.append('Trả trước hạn (VND)')
        
        print(df1.head(12)[display_cols1].to_string(index=False, formatters={
            'Tổng thanh toán (VND)': '{:,.0f}'.format,
            'Dư nợ cuối kỳ (VND)': '{:,.0f}'.format,
            'Trả trước hạn (VND)': '{:,.0f}'.format
        }))
        
        print(f"\n🔵 PHƯƠNG ÁN 2 ({self.term2_widget.value} năm):")
        display_cols2 = ['Tháng', 'Lãi suất (%/năm)', 'Tổng thanh toán (VND)', 'Dư nợ cuối kỳ (VND)']
        if 'Trả trước hạn (VND)' in df2.columns and df2['Trả trước hạn (VND)'].sum() > 0:
            display_cols2.append('Trả trước hạn (VND)')
        
        print(df2.head(12)[display_cols2].to_string(index=False, formatters={
            'Tổng thanh toán (VND)': '{:,.0f}'.format,
            'Dư nợ cuối kỳ (VND)': '{:,.0f}'.format,
            'Trả trước hạn (VND)': '{:,.0f}'.format
        }))
    
    def create_individual_plotly_charts(self, df1, df2):
        """Tạo biểu đồ Plotly"""
        # Chart 1: Lãi suất
        fig1 = go.Figure()
        if len(df1) > 0:
            fig1.add_trace(go.Scatter(
                x=df1['Tháng'], y=df1['Lãi suất (%/năm)'],
                name=f'PA1: {self.term1_widget.value} năm',
                line=dict(color='#E74C3C', width=3),
                mode='lines+markers', marker=dict(size=4)
            ))
        if len(df2) > 0:
            fig1.add_trace(go.Scatter(
                x=df2['Tháng'], y=df2['Lãi suất (%/năm)'],
                name=f'PA2: {self.term2_widget.value} năm',
                line=dict(color='#3498DB', width=3),
                mode='lines+markers', marker=dict(size=4)
            ))
        fig1.update_layout(
            title="<b>📈 So Sánh Lãi Suất Theo Thời Gian</b>",
            xaxis_title="Tháng", yaxis_title="Lãi suất (%/năm)",
            template="plotly_white", height=500
        )
        fig1.show()
        
        # Chart 2: Thanh toán hàng tháng
        fig2 = go.Figure()
        if len(df1) > 0:
            fig2.add_trace(go.Scatter(
                x=df1['Tháng'], y=df1['Tổng thanh toán (VND)']/1_000_000,
                name=f'PA1: {self.term1_widget.value} năm',
                line=dict(color='#E74C3C', width=3)
            ))
        if len(df2) > 0:
            fig2.add_trace(go.Scatter(
                x=df2['Tháng'], y=df2['Tổng thanh toán (VND)']/1_000_000,
                name=f'PA2: {self.term2_widget.value} năm',
                line=dict(color='#3498DB', width=3)
            ))
        fig2.update_layout(
            title="<b>💰 So Sánh Thanh Toán Hàng Tháng</b>",
            xaxis_title="Tháng", yaxis_title="Triệu VND",
            template="plotly_white", height=500
        )
        fig2.show()
        
        # Chart 3: Dư nợ
        fig3 = go.Figure()
        if len(df1) > 0:
            fig3.add_trace(go.Scatter(
                x=df1['Tháng'], y=df1['Dư nợ cuối kỳ (VND)']/1_000_000_000,
                name=f'PA1: {self.term1_widget.value} năm',
                line=dict(color='#E74C3C', width=3), fill='tozeroy'
            ))
        if len(df2) > 0:
            fig3.add_trace(go.Scatter(
                x=df2['Tháng'], y=df2['Dư nợ cuối kỳ (VND)']/1_000_000_000,
                name=f'PA2: {self.term2_widget.value} năm',
                line=dict(color='#3498DB', width=3), fill='tozeroy'
            ))
        fig3.update_layout(
            title="<b>📉 So Sánh Dư Nợ Còn Lại</b>",
            xaxis_title="Tháng", yaxis_title="Tỷ VND",
            template="plotly_white", height=500
        )
        fig3.show()
        
        # Chart 4: Tích lũy
        fig4 = go.Figure()
        if len(df1) > 0:
            cumulative1 = df1['Tổng thanh toán (VND)'].cumsum()
            fig4.add_trace(go.Scatter(
                x=df1['Tháng'], y=cumulative1/1_000_000_000,
                name=f'PA1: {self.term1_widget.value} năm',
                line=dict(color='#E74C3C', width=4)
            ))
        if len(df2) > 0:
            cumulative2 = df2['Tổng thanh toán (VND)'].cumsum()
            fig4.add_trace(go.Scatter(
                x=df2['Tháng'], y=cumulative2/1_000_000_000,
                name=f'PA2: {self.term2_widget.value} năm',
                line=dict(color='#3498DB', width=4)
            ))
        fig4.update_layout(
            title="<b>📊 Tổng Thanh Toán Tích Lũy</b>",
            xaxis_title="Tháng", yaxis_title="Tỷ VND",
            template="plotly_white", height=500
        )
        fig4.show()
        
        # Chart 5: Thành phần PA1
        if len(df1) > 0:
            display_months1 = min(60, len(df1))
            df1_display = df1.head(display_months1)
            
            fig5 = make_subplots(specs=[[{"secondary_y": True}]])
            
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
            
            if 'Trả trước hạn (VND)' in df1_display.columns:
                early_months = df1_display[df1_display['Trả trước hạn (VND)'] > 0]
                if len(early_months) > 0:
                    fig5.add_trace(
                        go.Scatter(x=early_months['Tháng'], 
                                 y=early_months['Trả trước hạn (VND)']/1_000_000,
                                 mode='markers+lines+text',
                                 marker=dict(color='red', size=12, symbol='diamond'),
                                 line=dict(color='red', width=3, dash='dash'),
                                 text=[f'{val/1_000_000:.0f}tr' for val in early_months['Trả trước hạn (VND)']],
                                 textposition='top center',
                                 textfont=dict(size=10, color='red'),
                                 name='Trả trước hạn'),
                        secondary_y=True
                    )
            
            fig5.update_xaxes(title_text="Tháng")
            fig5.update_yaxes(title_text="Triệu VND (Thanh toán thường)", secondary_y=False)
            fig5.update_yaxes(title_text="Triệu VND (Trả trước hạn)", secondary_y=True)
            
            fig5.update_layout(
                title=f"<b>🔴 Thành Phần Thanh Toán - PA1 ({self.term1_widget.value} năm)</b>",
                template="plotly_white", barmode='stack', height=500,
                legend=dict(x=0.01, y=0.99)
            )
            fig5.show()
        
        # Chart 6: Thành phần PA2
        if len(df2) > 0:
            display_months2 = min(60, len(df2))
            df2_display = df2.head(display_months2)
            
            fig6 = make_subplots(specs=[[{"secondary_y": True}]])
            
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
            
            if 'Trả trước hạn (VND)' in df2_display.columns:
                early_months = df2_display[df2_display['Trả trước hạn (VND)'] > 0]
                if len(early_months) > 0:
                    fig6.add_trace(
                        go.Scatter(x=early_months['Tháng'], 
                                 y=early_months['Trả trước hạn (VND)']/1_000_000,
                                 mode='markers+lines+text',
                                 marker=dict(color='red', size=12, symbol='diamond'),
                                 line=dict(color='red', width=3, dash='dash'),
                                 text=[f'{val/1_000_000:.0f}tr' for val in early_months['Trả trước hạn (VND)']],
                                 textposition='top center',
                                 textfont=dict(size=10, color='red'),
                                 name='Trả trước hạn'),
                        secondary_y=True
                    )
            
            fig6.update_xaxes(title_text="Tháng")
            fig6.update_yaxes(title_text="Triệu VND (Thanh toán thường)", secondary_y=False)
            fig6.update_yaxes(title_text="Triệu VND (Trả trước hạn)", secondary_y=True)
            
            fig6.update_layout(
                title=f"<b>🔵 Thành Phần Thanh Toán - PA2 ({self.term2_widget.value} năm)</b>",
                template="plotly_white", barmode='stack', height=500,
                legend=dict(x=0.01, y=0.99)
            )
            fig6.show()
    
    def display(self):
        """Hiển thị giao diện chính"""
        def on_term1_change(change):
            self.update_rate_widgets_visibility()
            max_months = self.term1_widget.value * 12
            for payment in self.early_payments1:
                payment['month'].max = max_months
            
        def on_term2_change(change):
            self.update_rate_widgets_visibility()
            max_months = self.term2_widget.value * 12
            for payment in self.early_payments2:
                payment['month'].max = max_months
        
        def on_early_payment1_change(change):
            self.update_early_payment_widgets_visibility()
            
        def on_early_payment2_change(change):
            self.update_early_payment_widgets_visibility()
            
        def on_num_early_payments1_change(change):
            self.update_early_payment_widgets_visibility()
            
        def on_num_early_payments2_change(change):
            self.update_early_payment_widgets_visibility()
        
        self.term1_widget.observe(on_term1_change, names='value')
        self.term2_widget.observe(on_term2_change, names='value')
        self.early_payment1_enabled.observe(on_early_payment1_change, names='value')
        self.early_payment2_enabled.observe(on_early_payment2_change, names='value')
        self.num_early_payments1_widget.observe(on_num_early_payments1_change, names='value')
        self.num_early_payments2_widget.observe(on_num_early_payments2_change, names='value')
        
        self.update_rate_widgets_visibility()
        self.update_early_payment_widgets_visibility()
        
        display(self.main_layout)
        
        with self.output:
            print("="*100)
            print("📚 HƯỚNG DẪN SỬ DỤNG - MÁY TÍNH SO SÁNH PHƯƠNG ÁN VAY CHUYÊN NGHIỆP")
            print("="*100)
            print()
            print("✨ TÍNH NĂNG NỔI BẬT:")
            print("  🎯 Giao diện chuyên nghiệp với thiết kế hiện đại")
            print("  💰 Đơn vị TRIỆU VND dễ nhập và theo dõi")
            print("  📊 Hiển thị số tiền trả hàng tháng TRỰC TIẾP trên GUI")
            print("  ⚙️ Tùy chỉnh mức tăng lãi suất tự động (%/kỳ)")
            print("  🔄 So sánh 2 phương án với thời gian vay khác nhau")
            print("  💵 Trả trước hạn linh hoạt, riêng biệt cho từng PA")
            print("  📈 6 biểu đồ tương tác Plotly chi tiết")
            print()
            print("📋 HƯỚNG DẪN TỪNG BƯỚC:")
            print("  1️⃣  Nhập số tiền vay (đơn vị: TRIỆU VND)")
            print("  2️⃣  Chọn thời gian vay cho mỗi phương án")
            print("  3️⃣  Cài đặt lãi suất ban đầu")
            print("  4️⃣  Chọn 'Tự động tăng' và nhập mức tăng (%/kỳ)")
            print("  5️⃣  Nhấn '⚡ Cập Nhật' để áp dụng lãi suất")
            print("  6️⃣  Cấu hình trả trước hạn (nếu cần):")
            print("       - Tích 'Kích hoạt'")
            print("       - Chọn số lần trả trước (1-10)")
            print("       - Cài đặt: tháng, số tiền (triệu), phí (%)")
            print("  7️⃣  Nhấn '🔍 Tính Toán & So Sánh'")
            print("  8️⃣  Xem kết quả ngay trên GUI:")
            print("       - Số tiền trả hàng tháng trung bình")
            print("       - Tổng lãi, tổng thanh toán")
            print("       - So sánh phương án nào tốt hơn")
            print()
            print("🎨 TÍNH NĂNG NHANH:")
            print("  📋 Copy Lãi Suất PA1→PA2 : Sao chép lãi suất từ PA1 sang PA2")
            print("  📋 Copy Lãi Suất PA2→PA1 : Sao chép lãi suất từ PA2 sang PA1")
            print("  📋 Copy Trả Trước PA1→PA2 : Sao chép trả trước từ PA1 sang PA2")
            print("  📋 Copy Trả Trước PA2→PA1 : Sao chép trả trước từ PA2 sang PA1")
            print("  💾 Xuất File CSV: Lưu kết quả chi tiết ra file Excel/CSV")
            print("  🔄 Reset: Khôi phục về cài đặt mặc định")
            print()
            print("💾 XUẤT FILE CSV:")
            print("  ✓ Xuất 3 file: PA1, PA2, và file so sánh tổng hợp")
            print("  ✓ Đơn vị: Triệu VND (dễ đọc trong Excel)")
            print("  ✓ Encoding UTF-8 with BOM (mở tốt trong Excel tiếng Việt)")
            print("  ✓ Tự động đặt tên file với timestamp")
            print("  ✓ Lưu trong thư mục 'mortgage_exports/'")
            print("  ✓ File so sánh có tổng hợp đầy đủ 2 phương án")
            print()
            print("💡 MẸO SỬ DỤNG:")
            print("  ✓ Số tiền vay mặc định: 1,500 triệu VND (1.5 tỷ)")
            print("  ✓ Mức tăng lãi suất mặc định: 0.5%/kỳ (có thể thay đổi)")
            print("  ✓ Kết quả hiển thị ngay trên GUI, không cần cuộn xuống")
            print("  ✓ Biểu đồ tương tác: click vào chú thích để ẩn/hiện")
            print("  ✓ Sử dụng Copy để so sánh công bằng giữa 2 phương án")
            print()
            print("🎯 KẾT QUẢ HIỂN THỊ:")
            print("  📊 Trên GUI: Kết quả nhanh với số tiền trả hàng tháng")
            print("  📈 Biểu đồ: 6 biểu đồ chi tiết về lãi suất, thanh toán, dư nợ")
            print("  📝 Bảng: Chi tiết 12 tháng đầu tiên")
            print("  🏆 So sánh: Phương án nào tốt hơn, tiết kiệm bao nhiêu")
            print()
            print("="*100)
            print("✅ Sẵn sàng sử dụng! Nhập thông tin và nhấn 'Tính Toán' để bắt đầu.")
            print("="*100)

# Khởi tạo và hiển thị
"""
print("🚀 Đang khởi tạo Máy Tính So Sánh Vay - Phiên Bản Chuyên Nghiệp...")
print("📱 Giao diện hiện đại với kết quả hiển thị trực tiếp trên GUI")
print("="*80)
"""
calculator = FlexibleMortgageCalculator()
calculator.display()
