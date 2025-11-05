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
        self.max_payment_adjustments = 10  # Số lần điều chỉnh tối đa cho PA3
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
        
        # === PHƯƠNG ÁN 3 - ĐIỀU CHỈNH MỨC TRẢ ===
        self.term3_widget = widgets.IntSlider(
            value=8,
            min=1,
            max=30,
            description='Thời gian (năm):',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.initial_rate3_widget = widgets.FloatSlider(
            value=6.0,
            min=1.0,
            max=25.0,
            step=0.1,
            description='Lãi suất ban đầu (%):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='450px'),
            readout_format='.1f'
        )
        
        self.auto_increase3_widget = widgets.Checkbox(
            value=True,
            description='Tự động tăng',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='120px')
        )
        
        self.auto_increase_rate3_widget = widgets.FloatText(
            value=0.5,
            description='Tăng (%/kỳ):',
            style={'description_width': '80px'},
            layout=widgets.Layout(width='180px'),
            disabled=False
        )
        
        self.rate3_widgets = []
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
            self.rate3_widgets.append(widget)
        
        # Điều chỉnh mức trả PA3
        self.payment_adjustment3_enabled = widgets.Checkbox(
            value=False,
            description='Kích hoạt điều chỉnh',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='150px')
        )
        
        self.num_payment_adjustments3_widget = widgets.IntSlider(
            value=2,
            min=1,
            max=self.max_payment_adjustments,
            description='Số lần:',
            style={'description_width': '60px'},
            layout=widgets.Layout(width='250px')
        )
        
        self.payment_adjustments3 = []
        for i in range(self.max_payment_adjustments):
            adjustment_group = {
                'enabled': widgets.Checkbox(
                    value=i < 2,
                    description=f'#{i+1}',
                    style={'description_width': '30px'},
                    layout=widgets.Layout(width='60px')
                ),
                'month': widgets.IntText(
                    value=7 + i*12,
                    description='Từ tháng:',
                    style={'description_width': '70px'},
                    layout=widgets.Layout(width='150px')
                ),
                'amount': widgets.FloatText(
                    value=20.0 if i == 0 else 15.0,
                    description='Trả/tháng (triệu):',
                    style={'description_width': '110px'},
                    layout=widgets.Layout(width='220px')
                )
            }
            self.payment_adjustments3.append(adjustment_group)
        
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
        
        self.result3_monthly = widgets.HTML(
            value="<div style='padding: 15px; background: #f0fff0; border: 2px solid #27AE60; border-radius: 8px;'><h4 style='color: #27AE60; margin: 0;'>Chưa tính toán</h4></div>"
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
        
        self.update_rates3_button = widgets.Button(
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
        self.update_rates1_button.on_click(self.on_update_rates1_clicked)
        self.update_rates2_button.on_click(self.on_update_rates2_clicked)
        self.update_rates3_button.on_click(self.on_update_rates3_clicked)
        self.export_csv_button.on_click(self.on_export_csv_clicked)
        
        # Lưu trữ dữ liệu để export
        self.last_df1 = None
        self.last_df2 = None
        self.last_df3 = None
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
                    💰 MÁY TÍNH SO SÁNH 3 PHƯƠNG ÁN VAY
                </h1>
                <p style='color: #e0e0e0; margin: 10px 0 0 0; font-size: 14px;'>
                    PA1&2: Kỳ điều chỉnh 6 tháng | PA3: Điều chỉnh mức trả linh hoạt
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
            layout=widgets.Layout(height='200px', overflow_y='auto', border='1px solid #ddd', 
                                padding='10px', background='white', border_radius='5px')
        )
        
        plan1_rate_controls = widgets.HBox([
            self.auto_increase1_widget,
            self.auto_increase_rate1_widget,
            self.update_rates1_button
        ], layout=widgets.Layout(align_items='center', justify_content='flex-start'))
        
        plan1_box = widgets.VBox([
            widgets.HTML("<div style='background: #E74C3C; color: white; padding: 8px; border-radius: 8px 8px 0 0;'><h4 style='margin: 0; font-size: 14px;'>📊 PHƯƠNG ÁN 1</h4></div>"),
            widgets.VBox([
                self.term1_widget,
                self.initial_rate1_widget,
                plan1_rate_controls,
                widgets.HTML("<div style='margin: 8px 0 3px 0; font-weight: bold; font-size: 12px;'>Lãi suất theo kỳ:</div>"),
                self.rate1_container,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-weight: bold; font-size: 12px;'>📈 Kết quả:</div>"),
                self.result1_monthly
            ], layout=widgets.Layout(padding='12px', background='#fff5f5', border='2px solid #E74C3C', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='32%'))
        
        # Phương án 2
        self.rate2_container = widgets.VBox(
            layout=widgets.Layout(height='200px', overflow_y='auto', border='1px solid #ddd', 
                                padding='10px', background='white', border_radius='5px')
        )
        
        plan2_rate_controls = widgets.HBox([
            self.auto_increase2_widget,
            self.auto_increase_rate2_widget,
            self.update_rates2_button
        ], layout=widgets.Layout(align_items='center', justify_content='flex-start'))
        
        plan2_box = widgets.VBox([
            widgets.HTML("<div style='background: #3498DB; color: white; padding: 8px; border-radius: 8px 8px 0 0;'><h4 style='margin: 0; font-size: 14px;'>📊 PHƯƠNG ÁN 2</h4></div>"),
            widgets.VBox([
                self.term2_widget,
                self.initial_rate2_widget,
                plan2_rate_controls,
                widgets.HTML("<div style='margin: 8px 0 3px 0; font-weight: bold; font-size: 12px;'>Lãi suất theo kỳ:</div>"),
                self.rate2_container,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-weight: bold; font-size: 12px;'>📈 Kết quả:</div>"),
                self.result2_monthly
            ], layout=widgets.Layout(padding='12px', background='#f0f8ff', border='2px solid #3498DB', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='32%'))
        
        # Phương án 3
        self.rate3_container = widgets.VBox(
            layout=widgets.Layout(height='200px', overflow_y='auto', border='1px solid #ddd', 
                                padding='10px', background='white', border_radius='5px')
        )
        
        plan3_rate_controls = widgets.HBox([
            self.auto_increase3_widget,
            self.auto_increase_rate3_widget,
            self.update_rates3_button
        ], layout=widgets.Layout(align_items='center', justify_content='flex-start'))
        
        plan3_box = widgets.VBox([
            widgets.HTML("<div style='background: #27AE60; color: white; padding: 8px; border-radius: 8px 8px 0 0;'><h4 style='margin: 0; font-size: 14px;'>📊 PHƯƠNG ÁN 3 - Điều Chỉnh Linh Hoạt</h4></div>"),
            widgets.VBox([
                self.term3_widget,
                self.initial_rate3_widget,
                plan3_rate_controls,
                widgets.HTML("<div style='margin: 8px 0 3px 0; font-weight: bold; font-size: 12px;'>Lãi suất theo kỳ:</div>"),
                self.rate3_container,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-weight: bold; font-size: 12px;'>📈 Kết quả:</div>"),
                self.result3_monthly
            ], layout=widgets.Layout(padding='12px', background='#f0fff0', border='2px solid #27AE60', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='32%'))
        
        plans_layout = widgets.HBox([plan1_box, plan2_box, plan3_box], 
                                    layout=widgets.Layout(justify_content='space-between', margin='0 0 20px 0'))
        
        # Điều chỉnh mức trả PA3
        self.payment_adjustment3_container = widgets.VBox(
            layout=widgets.Layout(height='200px', overflow_y='auto', border='1px solid #ddd', 
                                padding='10px', background='white', border_radius='5px')
        )
        
        adjustment3_controls = widgets.HBox([
            self.payment_adjustment3_enabled,
            self.num_payment_adjustments3_widget
        ], layout=widgets.Layout(align_items='center'))
        
        adjustment3_box = widgets.VBox([
            widgets.HTML("<div style='background: #229954; color: white; padding: 8px; border-radius: 8px 8px 0 0;'><h4 style='margin: 0; font-size: 14px;'>💵 ĐIỀU CHỈNH MỨC TRẢ - PA3</h4></div>"),
            widgets.VBox([
                adjustment3_controls,
                widgets.HTML("<div style='margin: 10px 0 5px 0; font-size: 12px; color: #555;'>Cấu hình điều chỉnh:</div>"),
                self.payment_adjustment3_container,
                widgets.HTML("<div style='margin: 10px 0 0 0; font-size: 11px; color: #e67e22; font-style: italic;'>💡 Mẹo: Tháng càng muộn, dư nợ càng ít → mức trả có thể giảm xuống</div>")
            ], layout=widgets.Layout(padding='12px', background='#e8f8f5', border='2px solid #229954', border_radius='0 0 8px 8px'))
        ], layout=widgets.Layout(width='48%'))
        
        # Trả trước hạn PA1
        self.early_payment1_container = widgets.VBox(
            layout=widgets.Layout(height='200px', overflow_y='auto', border='1px solid #ddd', 
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
        ], layout=widgets.Layout(width='32%'))
        
        # Trả trước hạn PA2
        self.early_payment2_container = widgets.VBox(
            layout=widgets.Layout(height='200px', overflow_y='auto', border='1px solid #ddd', 
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
        ], layout=widgets.Layout(width='32%'))
        
        early_layout = widgets.HBox([adjustment3_box, early1_box, early2_box], 
                                    layout=widgets.Layout(justify_content='space-between', margin='0 0 20px 0'))
        
        # Buttons & Results
        button_row = widgets.HBox([
            self.calculate_button,
            self.reset_button,
            self.export_csv_button
        ], layout=widgets.Layout(justify_content='center', margin='10px 0'))
        
        result_box = widgets.VBox([
            widgets.HTML("<div style='background: #34495e; color: white; padding: 10px; border-radius: 8px 8px 0 0;'><h3 style='margin: 0; font-size: 16px;'>🎯 KẾT QUẢ SO SÁNH 3 PHƯƠNG ÁN</h3></div>"),
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
            button_row,
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
        elif plan_number == 2:
            initial_rate = self.initial_rate2_widget.value
            auto_increase = self.auto_increase2_widget.value
            increase_rate = self.auto_increase_rate2_widget.value
            term_years = self.term2_widget.value
            widgets_list = self.rate2_widgets
        else:  # plan_number == 3
            initial_rate = self.initial_rate3_widget.value
            auto_increase = self.auto_increase3_widget.value
            increase_rate = self.auto_increase_rate3_widget.value
            term_years = self.term3_widget.value
            widgets_list = self.rate3_widgets
        
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
    
    def on_update_rates3_clicked(self, button):
        self.auto_update_rates(3)
        self.update_rate_widgets_visibility()
        print("✅ Đã cập nhật lãi suất cho Phương án 3!")
    
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
    
    def calculate_schedule_with_flexible_payment(self, principal, loan_years, rates):
        """Tính toán lịch trình thanh toán với điều chỉnh mức trả linh hoạt (PA3)"""
        if not self.payment_adjustment3_enabled.value:
            # Nếu không kích hoạt điều chỉnh, tính như bình thường
            return self.calculate_schedule(principal, loan_years, rates)
        
        # Lấy danh sách các điều chỉnh
        adjustments = []
        for i, adj in enumerate(self.payment_adjustments3[:self.num_payment_adjustments3_widget.value]):
            if adj['enabled'].value:
                adjustments.append({
                    'month': adj['month'].value,
                    'amount': adj['amount'].value * 1_000_000
                })
        
        # Sắp xếp theo tháng
        adjustments.sort(key=lambda x: x['month'])
        
        total_months = loan_years * 12
        payment_schedule = []
        remaining_principal = principal
        current_month = 1
        
        period_index = 0
        months_in_current_period = 0
        
        # Xác định mức trả hiện tại
        def get_current_payment_amount(month):
            current_amount = None
            for adj in adjustments:
                if month >= adj['month']:
                    current_amount = adj['amount']
            return current_amount
        
        while current_month <= total_months and remaining_principal > 1:
            if months_in_current_period >= 6:
                period_index += 1
                months_in_current_period = 0
            
            if period_index >= len(rates):
                period_index = len(rates) - 1
                
            annual_rate = rates[period_index] / 100
            months_in_current_period += 1
            
            # Tính lãi tháng này
            monthly_rate = annual_rate / 12
            interest_payment = remaining_principal * monthly_rate
            
            # Kiểm tra xem tháng này có điều chỉnh mức trả không
            target_payment = get_current_payment_amount(current_month)
            
            if target_payment is not None:
                # Có điều chỉnh mức trả
                monthly_payment = target_payment
                principal_payment = monthly_payment - interest_payment
                
                # Đảm bảo không trả quá dư nợ
                if principal_payment > remaining_principal:
                    principal_payment = remaining_principal
                    monthly_payment = interest_payment + principal_payment
                
                # Không cho phép principal_payment âm
                if principal_payment < 0:
                    principal_payment = 0
                    monthly_payment = interest_payment
            else:
                # Không có điều chỉnh, tính theo công thức bình thường
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
                "Dư nợ cuối kỳ (VND)": max(0, remaining_principal),
                "Điều chỉnh": "Có" if target_payment is not None else ""
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
        else:  # plan_number == 2
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
        
        required_periods3 = (self.term3_widget.value * 12 + 5) // 6
        visible_widgets3 = []
        for i in range(required_periods3):
            if i < len(self.rate3_widgets):
                widget = self.rate3_widgets[i]
                max_month = min((i+1)*6, self.term3_widget.value*12)
                widget.description = f'Kỳ {i+1} (T{i*6+1}-{max_month}):'
                visible_widgets3.append(widget)
        self.rate3_container.children = visible_widgets3
    
    def update_payment_adjustment_widgets_visibility(self):
        """Cập nhật hiển thị widgets điều chỉnh mức trả PA3"""
        if self.payment_adjustment3_enabled.value:
            visible_widgets = []
            num_adjustments = self.num_payment_adjustments3_widget.value
            for i, adjustment in enumerate(self.payment_adjustments3[:num_adjustments]):
                row = widgets.HBox([
                    adjustment['enabled'],
                    adjustment['month'],
                    adjustment['amount']
                ], layout=widgets.Layout(align_items='center', margin='2px 0'))
                visible_widgets.append(row)
            self.payment_adjustment3_container.children = visible_widgets
        else:
            self.payment_adjustment3_container.children = []
    
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
    
    def update_result_displays(self, df1, df2, df3, prepay_fee1, prepay_fee2):
        """Cập nhật hiển thị kết quả trên GUI"""
        # Phương án 1
        avg_monthly1 = df1['Tổng thanh toán (VND)'].mean()
        total_interest1 = df1['Tiền lãi (VND)'].sum()
        total_payment1 = df1['Tổng thanh toán (VND)'].sum()
        total_early1 = df1['Trả trước hạn (VND)'].sum() if 'Trả trước hạn (VND)' in df1.columns else 0
        
        result1_html = f"""
        <div style='padding: 12px; background: white; border: 2px solid #E74C3C; border-radius: 8px;'>
            <h4 style='color: #E74C3C; margin: 0 0 10px 0; font-size: 14px;'>📊 PA1 - {self.term1_widget.value} năm</h4>
            <div style='font-size: 11px; line-height: 1.6;'>
                <div style='display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #fdd;'>
                    <span><b>TB/tháng:</b></span>
                    <span style='color: #E74C3C; font-weight: bold;'>{self.format_currency(avg_monthly1/1_000_000)} tr</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #fdd;'>
                    <span>Tổng lãi:</span>
                    <span>{self.format_currency(total_interest1/1_000_000)} tr</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 4px 0;'>
                    <span>Tổng TT:</span>
                    <span>{self.format_currency(total_payment1/1_000_000)} tr</span>
                </div>
                {"<div style='display: flex; justify-content: space-between; padding: 4px 0;'><span>Trả trước:</span><span>" + self.format_currency(total_early1/1_000_000) + " tr</span></div>" if total_early1 > 0 else ""}
                <div style='display: flex; justify-content: space-between; padding: 6px 0; margin-top: 4px; background: #fff5f5; border-radius: 4px;'>
                    <span style='padding-left: 4px;'><b>Thời gian:</b></span>
                    <span style='padding-right: 4px;'><b>{len(df1)} tháng</b></span>
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
        <div style='padding: 12px; background: white; border: 2px solid #3498DB; border-radius: 8px;'>
            <h4 style='color: #3498DB; margin: 0 0 10px 0; font-size: 14px;'>📊 PA2 - {self.term2_widget.value} năm</h4>
            <div style='font-size: 11px; line-height: 1.6;'>
                <div style='display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #ddf;'>
                    <span><b>TB/tháng:</b></span>
                    <span style='color: #3498DB; font-weight: bold;'>{self.format_currency(avg_monthly2/1_000_000)} tr</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #ddf;'>
                    <span>Tổng lãi:</span>
                    <span>{self.format_currency(total_interest2/1_000_000)} tr</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 4px 0;'>
                    <span>Tổng TT:</span>
                    <span>{self.format_currency(total_payment2/1_000_000)} tr</span>
                </div>
                {"<div style='display: flex; justify-content: space-between; padding: 4px 0;'><span>Trả trước:</span><span>" + self.format_currency(total_early2/1_000_000) + " tr</span></div>" if total_early2 > 0 else ""}
                <div style='display: flex; justify-content: space-between; padding: 6px 0; margin-top: 4px; background: #f0f8ff; border-radius: 4px;'>
                    <span style='padding-left: 4px;'><b>Thời gian:</b></span>
                    <span style='padding-right: 4px;'><b>{len(df2)} tháng</b></span>
                </div>
            </div>
        </div>
        """
        self.result2_monthly.value = result2_html
        
        # Phương án 3
        avg_monthly3 = df3['Tổng thanh toán (VND)'].mean()
        total_interest3 = df3['Tiền lãi (VND)'].sum()
        total_payment3 = df3['Tổng thanh toán (VND)'].sum()
        
        result3_html = f"""
        <div style='padding: 12px; background: white; border: 2px solid #27AE60; border-radius: 8px;'>
            <h4 style='color: #27AE60; margin: 0 0 10px 0; font-size: 14px;'>📊 PA3 - {self.term3_widget.value} năm (Linh hoạt)</h4>
            <div style='font-size: 11px; line-height: 1.6;'>
                <div style='display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #dfd;'>
                    <span><b>TB/tháng:</b></span>
                    <span style='color: #27AE60; font-weight: bold;'>{self.format_currency(avg_monthly3/1_000_000)} tr</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #dfd;'>
                    <span>Tổng lãi:</span>
                    <span>{self.format_currency(total_interest3/1_000_000)} tr</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 4px 0;'>
                    <span>Tổng TT:</span>
                    <span>{self.format_currency(total_payment3/1_000_000)} tr</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 6px 0; margin-top: 4px; background: #f0fff0; border-radius: 4px;'>
                    <span style='padding-left: 4px;'><b>Thời gian:</b></span>
                    <span style='padding-right: 4px;'><b>{len(df3)} tháng</b></span>
                </div>
            </div>
        </div>
        """
        self.result3_monthly.value = result3_html
        
        # So sánh 3 phương án
        payments = [
            ('PA1', total_payment1, self.term1_widget.value),
            ('PA2', total_payment2, self.term2_widget.value),
            ('PA3', total_payment3, self.term3_widget.value)
        ]
        payments.sort(key=lambda x: x[1])
        
        best_plan = payments[0][0]
        best_payment = payments[0][1]
        worst_payment = payments[2][1]
        difference = worst_payment - best_payment
        principal = self.principal_widget.value * 1_000_000
        
        if difference < 1000:
            comparison_html = """
            <div style='padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                        border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='color: #7f8c8d; margin: 0; font-size: 18px;'>⚖️ BA PHƯƠNG ÁN TƯƠNG ĐƯƠNG</h3>
                <p style='color: #95a5a6; margin: 8px 0 0 0;'>Chênh lệch không đáng kể</p>
            </div>
            """
        else:
            colors = {'PA1': '#E74C3C', 'PA2': '#3498DB', 'PA3': '#27AE60'}
            gradients = {
                'PA1': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'PA2': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'PA3': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
            }
            
            comparison_html = f"""
            <div style='padding: 20px; background: {gradients[best_plan]}; 
                        border-radius: 10px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.2);'>
                <h3 style='color: white; margin: 0 0 8px 0; font-size: 20px;'>🏆 {best_plan} TỐT NHẤT</h3>
                <div style='background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; margin: 8px 0;'>
                    <div style='color: #fff; font-size: 14px; margin-bottom: 4px;'>Tiết kiệm so với phương án tệ nhất:</div>
                    <div style='color: #fff; font-size: 24px; font-weight: bold;'>{self.format_currency(difference/1_000_000)} triệu VND</div>
                </div>
                <div style='color: #e0e0e0; font-size: 13px;'>
                    Tương đương <b>{(difference/principal)*100:.2f}%</b> số tiền vay
                </div>
                <div style='margin-top: 12px; color: #fff; font-size: 12px; opacity: 0.9;'>
                    {payments[0][0]}: {self.format_currency(payments[0][1]/1_000_000)} tr | 
                    {payments[1][0]}: {self.format_currency(payments[1][1]/1_000_000)} tr | 
                    {payments[2][0]}: {self.format_currency(payments[2][1]/1_000_000)} tr
                </div>
            </div>
            """
        
        self.comparison_result.value = comparison_html
    
    def on_export_csv_clicked(self, button):
        """Xuất kết quả ra file CSV"""
        if self.last_df1 is None or self.last_df2 is None or self.last_df3 is None:
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
            
            # Xuất 3 phương án
            for idx, (df, term) in enumerate([(self.last_df1, self.term1_widget.value),
                                               (self.last_df2, self.term2_widget.value),
                                               (self.last_df3, self.term3_widget.value)], 1):
                filename = f"{output_dir}/PA{idx}_{term}nam_{timestamp}.csv"
                df_export = df.copy()
                
                # Format lại số tiền thành triệu VND
                for col in df_export.columns:
                    if 'VND' in col:
                        df_export[col] = df_export[col] / 1_000_000
                        new_col = col.replace('(VND)', '(triệu VND)')
                        df_export.rename(columns={col: new_col}, inplace=True)
                
                df_export.to_csv(filename, index=False, encoding='utf-8-sig')
            
            # Xuất file so sánh tổng hợp
            filename_summary = f"{output_dir}/So_Sanh_3PA_{timestamp}.csv"
            
            total1 = self.last_df1['Tổng thanh toán (VND)'].sum()
            total_interest1 = self.last_df1['Tiền lãi (VND)'].sum()
            total_early1 = self.last_df1['Trả trước hạn (VND)'].sum() if 'Trả trước hạn (VND)' in self.last_df1.columns else 0
            
            total2 = self.last_df2['Tổng thanh toán (VND)'].sum()
            total_interest2 = self.last_df2['Tiền lãi (VND)'].sum()
            total_early2 = self.last_df2['Trả trước hạn (VND)'].sum() if 'Trả trước hạn (VND)' in self.last_df2.columns else 0
            
            total3 = self.last_df3['Tổng thanh toán (VND)'].sum()
            total_interest3 = self.last_df3['Tiền lãi (VND)'].sum()
            
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
                    '',
                    'Xếp hạng (1=tốt nhất)'
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
                    '',
                    ''
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
                    '',
                    ''
                ],
                'Phương án 3': [
                    self.principal_widget.value,
                    self.term3_widget.value,
                    len(self.last_df3),
                    self.initial_rate3_widget.value,
                    self.auto_increase_rate3_widget.value,
                    '',
                    round(self.last_df3['Tổng thanh toán (VND)'].mean() / 1_000_000, 2),
                    round(total_interest3 / 1_000_000, 2),
                    round(total3 / 1_000_000, 2),
                    0,
                    '',
                    ''
                ]
            }
            
            # Xếp hạng
            payments = [
                ('Phương án 1', total1),
                ('Phương án 2', total2),
                ('Phương án 3', total3)
            ]
            payments.sort(key=lambda x: x[1])
            for rank, (name, _) in enumerate(payments, 1):
                summary_data[name][-1] = rank
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_csv(filename_summary, index=False, encoding='utf-8-sig')
            
            print("="*80)
            print("✅ XUẤT FILE THÀNH CÔNG!")
            print("="*80)
            print(f"📁 Thư mục: {output_dir}/")
            print(f"📄 File PA1: PA1_{self.term1_widget.value}nam_{timestamp}.csv")
            print(f"📄 File PA2: PA2_{self.term2_widget.value}nam_{timestamp}.csv")
            print(f"📄 File PA3: PA3_{self.term3_widget.value}nam_{timestamp}.csv")
            print(f"📊 File so sánh: So_Sanh_3PA_{timestamp}.csv")
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
        self.term3_widget.value = 8
        self.initial_rate1_widget.value = 6.0
        self.initial_rate2_widget.value = 6.0
        self.initial_rate3_widget.value = 6.0
        self.auto_increase1_widget.value = True
        self.auto_increase2_widget.value = True
        self.auto_increase3_widget.value = True
        self.auto_increase_rate1_widget.value = 0.5
        self.auto_increase_rate2_widget.value = 0.5
        self.auto_increase_rate3_widget.value = 0.5
        
        for i, widget in enumerate(self.rate1_widgets[:20]):
            widget.value = 6.0 + min(i * 0.5, 9.0)
        
        for i, widget in enumerate(self.rate2_widgets[:20]):
            widget.value = 6.0 + min(i * 0.5, 9.0)
        
        for i, widget in enumerate(self.rate3_widgets[:20]):
            widget.value = 6.0 + min(i * 0.5, 9.0)
        
        self.payment_adjustment3_enabled.value = False
        self.num_payment_adjustments3_widget.value = 2
        for i, adj in enumerate(self.payment_adjustments3):
            adj['enabled'].value = i < 2
            adj['month'].value = 7 + i*12
            adj['amount'].value = 20.0 if i == 0 else 15.0
        
        self.early_payment1_enabled.value = False
        self.early_payment2_enabled.value = False
        
        self.result1_monthly.value = "<div style='padding: 15px; background: #fff5f5; border: 2px solid #E74C3C; border-radius: 8px;'><h4 style='color: #E74C3C; margin: 0;'>Chưa tính toán</h4></div>"
        self.result2_monthly.value = "<div style='padding: 15px; background: #f0f8ff; border: 2px solid #3498DB; border-radius: 8px;'><h4 style='color: #3498DB; margin: 0;'>Chưa tính toán</h4></div>"
        self.result3_monthly.value = "<div style='padding: 15px; background: #f0fff0; border: 2px solid #27AE60; border-radius: 8px;'><h4 style='color: #27AE60; margin: 0;'>Chưa tính toán</h4></div>"
        self.comparison_result.value = "<div style='padding: 20px; background: #f5f5f5; border: 2px solid #95a5a6; border-radius: 8px; text-align: center;'><h3 style='color: #7f8c8d; margin: 0;'>Nhấn 'Tính Toán' để so sánh</h3></div>"
        
        self.update_rate_widgets_visibility()
        self.update_payment_adjustment_widgets_visibility()
        self.update_early_payment_widgets_visibility()
        
        with self.output:
            clear_output(wait=True)
            print("✅ Đã reset về giá trị mặc định.")
    
    def display_comparison_results(self):
        """Hiển thị kết quả so sánh"""
        try:
            principal = self.principal_widget.value * 1_000_000
            rates1 = [w.value for w in self.rate1_container.children]
            rates2 = [w.value for w in self.rate2_container.children]
            rates3 = [w.value for w in self.rate3_container.children]
            
            df1 = self.calculate_schedule(principal, self.term1_widget.value, rates1)
            df2 = self.calculate_schedule(principal, self.term2_widget.value, rates2)
            df3 = self.calculate_schedule_with_flexible_payment(principal, self.term3_widget.value, rates3)
            
            df1, prepay_fee1 = self.apply_multiple_early_payments(df1, 1)
            df2, prepay_fee2 = self.apply_multiple_early_payments(df2, 2)
            
            # Lưu dữ liệu để export
            self.last_df1 = df1.copy()
            self.last_df2 = df2.copy()
            self.last_df3 = df3.copy()
            self.last_calculation_time = datetime.now()
            
            # Cập nhật GUI
            self.update_result_displays(df1, df2, df3, prepay_fee1, prepay_fee2)
            
            # In thông tin chi tiết
            print("="*120)
            print("📊 KẾT QUẢ SO SÁNH 3 PHƯƠNG ÁN")
            print("="*120)
            
            self.display_payment_adjustment_summary()
            self.display_monthly_details(df1, df2, df3)
            self.create_plotly_charts(df1, df2, df3)
            
            print("\n" + "="*80)
            print("💡 Dữ liệu đã sẵn sàng! Nhấn nút '💾 Xuất File CSV' để lưu kết quả.")
            print("="*80)
            
        except Exception as e:
            print(f"❌ Có lỗi xảy ra: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def display_payment_adjustment_summary(self):
        """Hiển thị tóm tắt điều chỉnh mức trả PA3"""
        print(f"\n{'='*80}")
        print("💵 THÔNG TIN ĐIỀU CHỈNH MỨC TRẢ - PA3")
        print("="*80)
        
        if self.payment_adjustment3_enabled.value:
            active_count = 0
            for i, adj in enumerate(self.payment_adjustments3[:self.num_payment_adjustments3_widget.value]):
                if adj['enabled'].value:
                    active_count += 1
                    print(f"  Lần {active_count}: Từ tháng {adj['month'].value} - "
                          f"Trả {adj['amount'].value:,.0f} triệu VND/tháng")
            if active_count == 0:
                print("  ⚠️ Không có lần nào được kích hoạt")
        else:
            print("  ❌ Không sử dụng điều chỉnh (trả theo lịch cố định)")
    
    def display_monthly_details(self, df1, df2, df3):
        """Hiển thị chi tiết 12 tháng đầu"""
        print(f"\n{'='*80}")
        print("📅 CHI TIẾT 12 THÁNG ĐẦU TIÊN")
        print("="*80)
        
        print(f"\n🔴 PHƯƠNG ÁN 1 ({self.term1_widget.value} năm):")
        display_cols1 = ['Tháng', 'Lãi suất (%/năm)', 'Tổng thanh toán (VND)', 'Dư nợ cuối kỳ (VND)']
        print(df1.head(12)[display_cols1].to_string(index=False, formatters={
            'Tổng thanh toán (VND)': '{:,.0f}'.format,
            'Dư nợ cuối kỳ (VND)': '{:,.0f}'.format
        }))
        
        print(f"\n🔵 PHƯƠNG ÁN 2 ({self.term2_widget.value} năm):")
        display_cols2 = ['Tháng', 'Lãi suất (%/năm)', 'Tổng thanh toán (VND)', 'Dư nợ cuối kỳ (VND)']
        print(df2.head(12)[display_cols2].to_string(index=False, formatters={
            'Tổng thanh toán (VND)': '{:,.0f}'.format,
            'Dư nợ cuối kỳ (VND)': '{:,.0f}'.format
        }))
        
        print(f"\n🟢 PHƯƠNG ÁN 3 ({self.term3_widget.value} năm - Điều chỉnh linh hoạt):")
        display_cols3 = ['Tháng', 'Lãi suất (%/năm)', 'Tổng thanh toán (VND)', 'Dư nợ cuối kỳ (VND)']
        if 'Điều chỉnh' in df3.columns:
            display_cols3.append('Điều chỉnh')
        print(df3.head(12)[display_cols3].to_string(index=False, formatters={
            'Tổng thanh toán (VND)': '{:,.0f}'.format,
            'Dư nợ cuối kỳ (VND)': '{:,.0f}'.format
        }))
    
    def create_plotly_charts(self, df1, df2, df3):
        """Tạo biểu đồ Plotly so sánh 3 phương án"""
        # Chart 1: Thanh toán hàng tháng
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df1['Tháng'], y=df1['Tổng thanh toán (VND)']/1_000_000,
            name=f'PA1: {self.term1_widget.value} năm',
            line=dict(color='#E74C3C', width=2)
        ))
        fig1.add_trace(go.Scatter(
            x=df2['Tháng'], y=df2['Tổng thanh toán (VND)']/1_000_000,
            name=f'PA2: {self.term2_widget.value} năm',
            line=dict(color='#3498DB', width=2)
        ))
        fig1.add_trace(go.Scatter(
            x=df3['Tháng'], y=df3['Tổng thanh toán (VND)']/1_000_000,
            name=f'PA3: {self.term3_widget.value} năm (Linh hoạt)',
            line=dict(color='#27AE60', width=2, dash='dot')
        ))
        
        # Đánh dấu các điểm điều chỉnh PA3
        if 'Điều chỉnh' in df3.columns:
            adjusted_points = df3[df3['Điều chỉnh'] == 'Có']
            if len(adjusted_points) > 0:
                fig1.add_trace(go.Scatter(
                    x=adjusted_points['Tháng'],
                    y=adjusted_points['Tổng thanh toán (VND)']/1_000_000,
                    mode='markers',
                    marker=dict(color='#e74c3c', size=10, symbol='star'),
                    name='Điểm điều chỉnh PA3',
                    showlegend=True
                ))
        
        fig1.update_layout(
            title="<b>💰 So Sánh Thanh Toán Hàng Tháng - 3 Phương Án</b>",
            xaxis_title="Tháng", yaxis_title="Triệu VND",
            template="plotly_white", height=500,
            hovermode='x unified'
        )
        fig1.show()
        
        # Chart 2: Dư nợ
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df1['Tháng'], y=df1['Dư nợ cuối kỳ (VND)']/1_000_000_000,
            name=f'PA1: {self.term1_widget.value} năm',
            line=dict(color='#E74C3C', width=3), fill='tozeroy'
        ))
        fig2.add_trace(go.Scatter(
            x=df2['Tháng'], y=df2['Dư nợ cuối kỳ (VND)']/1_000_000_000,
            name=f'PA2: {self.term2_widget.value} năm',
            line=dict(color='#3498DB', width=3), fill='tozeroy'
        ))
        fig2.add_trace(go.Scatter(
            x=df3['Tháng'], y=df3['Dư nợ cuối kỳ (VND)']/1_000_000_000,
            name=f'PA3: {self.term3_widget.value} năm (Linh hoạt)',
            line=dict(color='#27AE60', width=3), fill='tozeroy'
        ))
        fig2.update_layout(
            title="<b>📉 So Sánh Dư Nợ Còn Lại - 3 Phương Án</b>",
            xaxis_title="Tháng", yaxis_title="Tỷ VND",
            template="plotly_white", height=500
        )
        fig2.show()
        
        # Chart 3: Tích lũy
        fig3 = go.Figure()
        cumulative1 = df1['Tổng thanh toán (VND)'].cumsum()
        cumulative2 = df2['Tổng thanh toán (VND)'].cumsum()
        cumulative3 = df3['Tổng thanh toán (VND)'].cumsum()
        
        fig3.add_trace(go.Scatter(
            x=df1['Tháng'], y=cumulative1/1_000_000_000,
            name=f'PA1: {self.term1_widget.value} năm',
            line=dict(color='#E74C3C', width=3)
        ))
        fig3.add_trace(go.Scatter(
            x=df2['Tháng'], y=cumulative2/1_000_000_000,
            name=f'PA2: {self.term2_widget.value} năm',
            line=dict(color='#3498DB', width=3)
        ))
        fig3.add_trace(go.Scatter(
            x=df3['Tháng'], y=cumulative3/1_000_000_000,
            name=f'PA3: {self.term3_widget.value} năm (Linh hoạt)',
            line=dict(color='#27AE60', width=3)
        ))
        fig3.update_layout(
            title="<b>📊 Tổng Thanh Toán Tích Lũy - 3 Phương Án</b>",
            xaxis_title="Tháng", yaxis_title="Tỷ VND",
            template="plotly_white", height=500
        )
        fig3.show()
        
        # Chart 4: So sánh tổng chi phí
        total1 = df1['Tổng thanh toán (VND)'].sum()
        total2 = df2['Tổng thanh toán (VND)'].sum()
        total3 = df3['Tổng thanh toán (VND)'].sum()
        
        fig4 = go.Figure(data=[
            go.Bar(
                x=[f'PA1\n{self.term1_widget.value} năm', 
                   f'PA2\n{self.term2_widget.value} năm', 
                   f'PA3\n{self.term3_widget.value} năm'],
                y=[total1/1_000_000_000, total2/1_000_000_000, total3/1_000_000_000],
                marker_color=['#E74C3C', '#3498DB', '#27AE60'],
                text=[f'{total1/1_000_000_000:.2f} tỷ', 
                      f'{total2/1_000_000_000:.2f} tỷ', 
                      f'{total3/1_000_000_000:.2f} tỷ'],
                textposition='outside'
            )
        ])
        fig4.update_layout(
            title="<b>💵 Tổng Chi Phí So Sánh - 3 Phương Án</b>",
            xaxis_title="Phương án", yaxis_title="Tỷ VND",
            template="plotly_white", height=500
        )
        fig4.show()
    
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
        
        def on_term3_change(change):
            self.update_rate_widgets_visibility()
            max_months = self.term3_widget.value * 12
            for adj in self.payment_adjustments3:
                adj['month'].max = max_months
        
        def on_payment_adjustment3_change(change):
            self.update_payment_adjustment_widgets_visibility()
        
        def on_num_payment_adjustments3_change(change):
            self.update_payment_adjustment_widgets_visibility()
        
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
        self.term3_widget.observe(on_term3_change, names='value')
        self.payment_adjustment3_enabled.observe(on_payment_adjustment3_change, names='value')
        self.num_payment_adjustments3_widget.observe(on_num_payment_adjustments3_change, names='value')
        self.early_payment1_enabled.observe(on_early_payment1_change, names='value')
        self.early_payment2_enabled.observe(on_early_payment2_change, names='value')
        self.num_early_payments1_widget.observe(on_num_early_payments1_change, names='value')
        self.num_early_payments2_widget.observe(on_num_early_payments2_change, names='value')
        
        self.update_rate_widgets_visibility()
        self.update_payment_adjustment_widgets_visibility()
        self.update_early_payment_widgets_visibility()
        
        display(self.main_layout)
        
        with self.output:
            print("="*100)
            print("📚 HƯỚNG DẪN SỬ DỤNG - MÁY TÍNH SO SÁNH 3 PHƯƠNG ÁN VAY")
            print("="*100)
            print()
            print("✨ TÍNH NĂNG MỚI - PHƯƠNG ÁN 3:")
            print("  🎯 Điều chỉnh mức trả hàng tháng LINH HOẠT theo thời gian")
            print("  💡 VD: Tháng 1-6 trả 10tr/tháng, từ tháng 7 trả 20tr/tháng")
            print("  📈 Phù hợp khi thu nhập tăng hoặc muốn tất toán sớm")
            print("  ⚡ Giúp tiết kiệm lãi suất khi trả nhanh hơn")
            print()
            print("📋 CÁCH SỬ DỤNG PA3:")
            print("  1️⃣  Nhập thông tin cơ bản (số tiền, thời gian, lãi suất)")
            print("  2️⃣  Tích 'Kích hoạt điều chỉnh' ở mục PA3")
            print("  3️⃣  Chọn số lần điều chỉnh (tối đa 10 lần)")
            print("  4️⃣  Cài đặt từng lần điều chỉnh:")
            print("       - Tích checkbox để kích hoạt")
            print("       - Nhập tháng bắt đầu điều chỉnh")
            print("       - Nhập mức trả/tháng mới (triệu VND)")
            print("  5️⃣  Nhấn 'Tính Toán' để so sánh với PA1 và PA2")
            print()
            print("💡 MẸO SỬ DỤNG:")
            print("  ✓ Mức trả càng cao → Nợ trả càng nhanh → Tiết kiệm lãi")
            print("  ✓ Có thể giảm mức trả ở tháng sau nếu dư nợ đã ít")
            print("  ✓ Kết hợp PA3 với PA1, PA2 để chọn phương án tối ưu")
            print("  ✓ PA1, PA2 vẫn có trả trước hạn như bản cũ")
            print()
            print("🎨 CÁC PHƯƠNG ÁN:")
            print("  🔴 PA1 & PA2: Trả theo lịch cố định, có thể trả trước hạn")
            print("  🟢 PA3: Điều chỉnh mức trả linh hoạt theo kế hoạch tài chính")
            print()
            print("📊 KẾT QUẢ:")
            print("  ✓ So sánh 3 phương án trên cùng 1 màn hình")
            print("  ✓ Hiển thị phương án tốt nhất tự động")
            print("  ✓ 4 biểu đồ so sánh chi tiết")
            print("  ✓ Xuất CSV cho cả 3 phương án")
            print()
            print("="*100)
            print("✅ Sẵn sàng sử dụng! Nhập thông tin và nhấn 'Tính Toán' để bắt đầu.")
            print("="*100)

# Khởi tạo và hiển thị
calculator = FlexibleMortgageCalculator()
calculator.display()
