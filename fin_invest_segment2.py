
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

# Khởi chạy ứng dụng
if __name__ == "__main__":
    print("🚀 Khởi động ứng dụng phân tích danh mục đầu tư...")
    show_usage_guide()
    print("\n" + "="*50)
    print("📱 Chạy lệnh sau để bắt đầu:")
    print("investment_app = create_investment_analyzer()")
    print("display(investment_app)")
    print("="*50)
    #print(f"🎯 PHÂN TÍCH PHÂN BỔ DANH MỤC ({display_currency})")
    #print("="*70)
    #print(f"💰 Tổng giá trị danh mục: {self.format_currency(total_value, display_currency)}")
    print("-"*70)
    
    # Create comparison visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Prepare data for comparison
    all_types = set(list(current_allocation_pct.keys()) + list(self.target_allocation.keys()))
    
    current_values = [current_allocation_pct.get(t, 0) for t in all_types]
    target_values = [self.target_allocation.get(t, 0) for t in all_types]
    
    # Bar chart comparison
    x = np.arange(len(all_types))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, current_values, width, label='Hiện tại', alpha=0.8, color='lightblue')
    bars2 = ax1.bar(x + width/2, target_values, width, label='Mục tiêu', alpha=0.8, color='orange')
    
    ax1.set_title('So Sánh Phân Bổ Hiện Tại vs Mục Tiêu')
    ax1.set_ylabel('Tỷ lệ (%)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(all_types, rotation=45)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # Deviation analysis
    deviations = []
    for asset_type in all_types:
        current_pct = current_allocation_pct.get(asset_type, 0)
        target_pct = self.target_allocation.get(asset_type, 0)
        deviation = current_pct - target_pct
        deviations.append((asset_type, deviation))
    
    # Sort by absolute deviation
    deviations.sort(key=lambda x: abs(x[1]), reverse=True)
    
    # Plot deviations
    deviation_types = [d[0] for d in deviations]
    deviation_values = [d[1] for d in deviations]
    colors = ['red' if x < 0 else 'green' for x in deviation_values]
    
    ax2.barh(deviation_types, deviation_values, color=colors, alpha=0.7)
    ax2.set_title('Độ Lệch So Với Mục Tiêu')
    ax2.set_xlabel('Độ lệch (%)')
    ax2.axvline(x=0, color='black', linestyle='-', alpha=0.5)
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print detailed analysis
    print("\n📊 PHÂN TÍCH CHI TIẾT:")
    print(f"{'Loại tài sản':<20} {'Hiện tại':<12} {'Mục tiêu':<12} {'Độ lệch':<12} {'Trạng thái':<15}")
    print("-"*75)
    
    total_deviation = 0
    for asset_type in all_types:
        current_pct = current_allocation_pct.get(asset_type, 0)
        target_pct = self.target_allocation.get(asset_type, 0)
        deviation = current_pct - target_pct
        total_deviation += abs(deviation)
        
        if deviation > 5:
            status = "🔴 Thừa nhiều"
        elif deviation > 1:
            status = "🟡 Thừa ít"
        elif deviation < -5:
            status = "🔵 Thiếu nhiều"
        elif deviation < -1:
            status = "🟠 Thiếu ít"
        else:
            status = "✅ Cân bằng"
        
        current_value = current_allocation.get(asset_type, 0)
        print(f"{asset_type:<20} {current_pct:>8.1f}% {target_pct:>8.1f}% {deviation:>+8.1f}% {status:<15}")
        print(f"{'':>20} {self.format_currency(current_value, display_currency)}")
    
    print("-"*75)
    print(f"📈 Tổng độ lệch tuyệt đối: {total_deviation:.1f}%")
    
    if total_deviation < 5:
        print("✅ Danh mục đã cân bằng tốt!")
    elif total_deviation < 15:
        print("🟡 Danh mục cần điều chỉnh nhẹ")
    else:
        print("🔴 Danh mục cần cân bằng lại!")
    
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
    
    def calculate_gini_coefficient(self, values):
        """Tính hệ số Gini để đo độ bất bình đẳng phân bổ"""
        if not values or len(values) == 1:
            return 0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        cumsum = np.cumsum(sorted_values)
        
        return (n + 1 - 2 * sum((n + 1 - i) * y for i, y in enumerate(sorted_values, 1))) / (n * sum(sorted_values))
    
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

