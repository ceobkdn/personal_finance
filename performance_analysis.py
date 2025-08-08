
    def show_performance_analysis(self, button):
        """Phân tích hiệu suất danh mục đầu tư"""
        if not self.investment_data:
            with self.output:
                clear_output()
                print("❌ Chưa có dữ liệu đầu tư!")
            return
        
        display_currency = self.currency_display.value
        
        with self.output:
            clear_output()
            print("="*80)
            print("📊 PHÂN TÍCH HIỆU SUẤT DANH MỤC")
            print("="*80)
            
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
            
            # Create visualizations
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Portfolio growth over time
            monthly_value = df.groupby(df['date'].dt.to_period('M'))['amount_display'].sum()
            if not monthly_value.empty:
                monthly_value.index = monthly_value.index.to_timestamp()
                ax1.plot(monthly_value.index, monthly_value.values, marker='o', color='blue')
                ax1.set_title('Tăng Trưởng Danh Mục (Theo Tháng)')
                ax1.set_ylabel(f'Số tiền ({display_currency})')
                ax1.tick_params(axis='x', rotation=45)
                ax1.grid(True, linestyle='--', alpha=0.7)
            else:
                ax1.text(0.5, 0.5, 'Không có dữ liệu để hiển thị', ha='center', va='center', fontsize=12)
                ax1.set_title('Tăng Trưởng Danh Mục (Theo Tháng)')
            
            # 2. Performance by asset type
            type_performance = df.groupby('type')['amount_display'].sum()
            if not type_performance.empty:
                bars = ax2.bar(type_performance.index, type_performance.values, color='green', alpha=0.7)
                ax2.set_title('Hiệu Suất Theo Loại Tài Sản')
                ax2.set_ylabel(f'Số tiền ({display_currency})')
                ax2.tick_params(axis='x', rotation=45)
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height, 
                             self.format_currency(height, display_currency),
                             ha='center', va='bottom' if height >= 0 else 'top')
            else:
                ax2.text(0.5, 0.5, 'Không có dữ liệu để hiển thị', ha='center', va='center', fontsize=12)
                ax2.set_title('Hiệu Suất Theo Loại Tài Sản')
            
            # 3. Investment allocation timeline by type (monthly) - Handle sales (negative values)
            df['cumsum'] = df.groupby(['type'])['amount_display'].cumsum()
            type_timeline = df.groupby([df['date'].dt.to_period('M'), 'type'])['cumsum'].last().unstack(fill_value=0)
            type_timeline = type_timeline.clip(lower=0)
            if not type_timeline.empty:
                type_timeline.index = type_timeline.index.to_timestamp()
                type_timeline.plot(kind='area', stacked=True, ax=ax3, alpha=0.7)
                ax3.set_title('Phân Bổ Giá Trị Tích Lũy Theo Loại Theo Thời Gian (Theo Tháng)')
                ax3.set_ylabel(f'Số tiền ({display_currency})')
                ax3.tick_params(axis='x', rotation=45)
                ax3.grid(True, linestyle='--', alpha=0.7)
            else:
                ax3.text(0.5, 0.5, 'Không có dữ liệu để hiển thị', ha='center', va='center', fontsize=12)
                ax3.set_title('Phân Bổ Giá Trị Tích Lũy Theo Loại Theo Thời Gian')
            
            # 4. Return contribution by asset type
            returns = {}
            for asset_type in df['type'].unique():
                type_data = df[df['type'] == asset_type]
                if not type_data.empty:
                    initial = type_data['amount_display'].iloc[0]
                    final = type_data['cumsum'].iloc[-1]
                    returns[asset_type] = ((final - initial) / initial * 100) if initial != 0 else 0
            if returns:
                ax4.bar(returns.keys(), returns.values(), color='purple', alpha=0.7)
                ax4.set_title('Đóng Góp Lợi Suất Theo Loại Tài Sản')
                ax4.set_ylabel('Lợi suất (%)')
                ax4.tick_params(axis='x', rotation=45)
                for i, v in enumerate(returns.values()):
                    ax4.text(i, v, f'{v:.1f}%', ha='center', va='bottom' if v >= 0 else 'top')
            else:
                ax4.text(0.5, 0.5, 'Không có dữ liệu để hiển thị', ha='center', va='center', fontsize=12)
                ax4.set_title('Đóng Góp Lợi Suất Theo Loại Tài Sản')
            
            plt.tight_layout()
            plt.show()
            
            # Detailed performance analysis
            print("\n📊 PHÂN TÍCH CHI TIẾT:")
            print(f"{'Loại tài sản':<20} {'Số tiền':<15} {'Lợi suất (%)':<12} {'Tỷ trọng':<10}")
            print("-"*60)
            
            total_value = df['cumsum'].iloc[-1] if not df.empty else 0
            for asset_type in df['type'].unique():
                type_data = df[df['type'] == asset_type]
                if not type_data.empty:
                    amount = type_data['cumsum'].iloc[-1]
                    percentage = (amount / total_value * 100) if total_value != 0 else 0
                    initial = type_data['amount_display'].iloc[0]
                    roi = ((amount - initial) / initial * 100) if initial != 0 else 0
                    print(f"{asset_type:<20} {self.format_currency(amount, display_currency):<15} {roi:>9.1f}% {percentage:>6.1f}%")
            
            # Performance insights
            print("\n💡 NHẬN XÉT:")
            if not monthly_value.empty:
                growth = ((monthly_value.iloc[-1] - monthly_value.iloc[0]) / monthly_value.iloc[0] * 100) if monthly_value.iloc[0] != 0 else 0
                print(f" • Tăng trưởng danh mục: {growth:.1f}% từ {monthly_value.index[0].strftime('%Y-%m')} đến {monthly_value.index[-1].strftime('%Y-%m')}")
            
            if returns:
                best_performer = max(returns, key=returns.get, default="Không xác định")
                print(f" • Tài sản hiệu suất tốt nhất: {best_performer} ({returns.get(best_performer, 0):.1f}%)")
            
            if total_value > 0:
                print(f" • Giá trị danh mục hiện tại: {self.format_currency(total_value, display_currency)}")
