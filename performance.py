
    def show_performance_analysis(self, button):
        """Phân tích hiệu suất danh mục đầu tư - Phiên bản cải tiến"""
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
                    
                    # Tính annualized return
                    start_date = inv_data['date'].iloc[0]
                    end_date = inv_data['date'].iloc[-1]
                    years = max((end_date - start_date).days / 365.25, 1/12)  # Tối thiểu 1 tháng
                    
                    if years > 0 and net_invested > 0:
                        if current_holding_value <= 0:
                            # Đã bán hết
                            final_value = total_sold
                            annualized_return = (((final_value / total_bought) ** (1/years)) - 1) * 100
                        else:
                            # Còn đang giữ
                            final_value = current_value
                            annualized_return = (((final_value / abs(current_holding_value)) ** (1/years)) - 1) * 100
                    else:
                        annualized_return = 0
                    
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
                        'investment_period_years': years,
                        'transactions': len(inv_data),
                        'first_date': start_date,
                        'last_date': end_date,
                        'status': status,
                        'has_current_price': current_price_info is not None
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
                
                # Weighted average ROI dựa trên net cash flow
                weighted_roi = 0
                weighted_annualized = 0
                total_weight = 0
                
                for perf in performances:
                    # Sử dụng total_bought làm trọng số cho tính toán
                    weight = perf['total_bought']
                    if weight > 0:
                        weighted_roi += perf['roi_percent'] * weight
                        weighted_annualized += perf['annualized_return'] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    weighted_roi /= total_weight
                    weighted_annualized /= total_weight
                
                group_performance[asset_type] = {
                    'count': len(performances),
                    'total_bought': total_bought,
                    'total_sold': total_sold,
                    'net_invested': net_invested,
                    'total_current': total_current,
                    'total_gain': total_current - abs(net_invested) if net_invested != 0 else total_current - total_bought,
                    'weighted_roi': weighted_roi,
                    'weighted_annualized': weighted_annualized,
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
                print("-" * 95)
                print(f"{'Mã/Tên':<25} {'Mua':<12} {'Bán':<12} {'Hiện tại':<12} {'Lãi/Lỗ':<10} {'ROI%':<8} {'Năm%':<8} {'Trạng thái'}")
                print("-" * 95)
                
                for perf in sorted(performances, key=lambda x: x['roi_percent'], reverse=True):
                    gain_loss = f"{perf['absolute_gain']:+,.0f}"
                    status_icon = "🟢" if perf['status'] == 'Đang giữ' else "🔴"
                    
                    print(f"{perf['description'][:24]:<25} "
                          f"{self.format_currency(perf['total_bought'], display_currency):<12} "
                          f"{self.format_currency(perf['total_sold'], display_currency):<12} "
                          f"{self.format_currency(perf['current_value'], display_currency):<12} "
                          f"{gain_loss:<10} "
                          f"{perf['roi_percent']:>6.1f}% "
                          f"{perf['annualized_return']:>6.1f}% "
                          f"{status_icon} {perf['status']}")
                    
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
                              f"{price_type_desc}")
                    elif perf['has_current_price']:
                        price_info = self.current_prices.get(investment_id, {})
                        if price_info.get('type') == 'total_value':
                            price_type_desc = "Tổng giá trị"
                        else:
                            price_type_desc = "Per unit"
                        print(f"{'  └─ Có giá thị trường':<50} ({price_type_desc})")
            
            # Group summary
            print(f"\n{'='*100}")
            print("📈 TỔNG KẾT HIỆU SUẤT THEO NHÓM")
            print(f"{'='*100}")
            print(f"{'Nhóm':<20} {'SL':<4} {'Đang giữ':<8} {'Tổng mua':<12} {'Tổng bán':<12} {'Hiện tại':<12} {'ROI%':<8} {'Năm%':<8}")
            print("-" * 100)
            
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
                      f"{group_data['weighted_annualized']:>6.1f}%")
            
            print("-" * 100)
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
                  f"{'--':<8}")
            
            # Performance insights
            print(f"\n💡 NHẬN XÉT & KHUYẾN NGHỊ:")
            
            if group_performance:
                best_group = max(group_performance.items(), key=lambda x: x[1]['weighted_roi'])
                worst_group = min(group_performance.items(), key=lambda x: x[1]['weighted_roi'])
                
                print(f"🏆 Nhóm hiệu suất tốt nhất: {best_group[0]} ({best_group[1]['weighted_roi']:.1f}% ROI)")
                print(f"⚠️  Nhóm cần cải thiện: {worst_group[0]} ({worst_group[1]['weighted_roi']:.1f}% ROI)")
                
                # Individual best/worst performers
                all_performances = []
                for performances in type_groups.values():
                    all_performances.extend(performances)
                
                if all_performances:
                    best_individual = max(all_performances, key=lambda x: x['roi_percent'])
                    worst_individual = min(all_performances, key=lambda x: x['roi_percent'])
                    
                    print(f"🌟 Khoản đầu tư tốt nhất: {best_individual['description']} ({best_individual['roi_percent']:.1f}% ROI)")
                    print(f"📉 Khoản cần xem xét: {worst_individual['description']} ({worst_individual['roi_percent']:.1f}% ROI)")
            
            # Risk warnings
            high_risk_investments = [perf for perf in individual_performance.values() 
                                   if perf['roi_percent'] < -10]
            
            if high_risk_investments:
                print(f"\n🚨 CẢNH BÁO RỦI RO:")
                print(f"   Có {len(high_risk_investments)} khoản đầu tư lỗ trên 10%:")
                for inv in high_risk_investments[:3]:  # Hiển thị top 3
                    print(f"   • {inv['description']}: {inv['roi_percent']:.1f}% ROI")
            
            # Diversification insights
            type_count = len(group_performance)
            if type_count < 3:
                print(f"\n📊 KHUYẾN NGHỊ ĐA DẠNG HÓA:")
                print(f"   Danh mục chỉ có {type_count} loại tài sản. Nên đa dạng hóa thêm để giảm rủi ro.")
            
            print(f"\n⏰ Cập nhật lần cuối: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
