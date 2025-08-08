
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
