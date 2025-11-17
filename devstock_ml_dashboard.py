#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Machine Learning Dashboard
===========================
Interactive ML predictions and analytics

Features:
- Price prediction visualization
- Volatility forecasting
- Anomaly detection charts
- Model comparison
- Feature importance analysis

Usage:
    In Jupyter Notebook:
    exec(open('ml_dashboard.py').read())
    launch_ml_dashboard(symbol='AAPL')
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Import ML module
try:
    from ml_module_core import MLManager, LSTMPredictor, ProphetForecaster, ARIMAForecaster
    ML_AVAILABLE = True
except ImportError:
    print("Warning: ml_module_core not found")
    ML_AVAILABLE = False


# ============================================
# DATA LOADER FOR ML
# ============================================

class MLDataLoader:
    """Load and prepare data for ML models"""
    
    def __init__(self, db_path='data/portfolio.db'):
        self.db_path = db_path
    
    def get_price_history(self, symbol: str, days: int = 365) -> pd.Series:
        """
        Get price history for a symbol
        
        Args:
            symbol: Asset symbol
            days: Number of days
            
        Returns:
            Price series
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT timestamp, close_price
        FROM market_data_history
        WHERE symbol = ?
        AND timestamp >= date('now', '-' || ? || ' days')
        ORDER BY timestamp
        """
        
        df = pd.read_sql_query(query, conn, params=(symbol, days))
        conn.close()
        
        if df.empty:
            return pd.Series()
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        return df['close_price']
    
    def get_portfolio_symbols(self, portfolio_id: int) -> List[str]:
        """Get all symbols in a portfolio"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT DISTINCT symbol FROM assets WHERE portfolio_id = ?"
        df = pd.read_sql_query(query, conn, params=(portfolio_id,))
        
        conn.close()
        
        return df['symbol'].tolist()


# ============================================
# VISUALIZATION FUNCTIONS
# ============================================

def plot_price_prediction(historical: pd.Series, 
                          predictions: Dict[str, pd.Series],
                          title: str = "Price Prediction"):
    """
    Plot historical prices with multiple predictions
    
    Args:
        historical: Historical price series
        predictions: Dict of {method_name: prediction_series}
        title: Chart title
    """
    fig = go.Figure()
    
    # Historical prices
    fig.add_trace(go.Scatter(
        x=historical.index,
        y=historical.values,
        mode='lines',
        name='Historical',
        line=dict(color='blue', width=2)
    ))
    
    # Predictions
    colors = {'lstm': 'red', 'prophet': 'green', 'arima': 'orange'}
    
    for method, pred_series in predictions.items():
        if not pred_series.empty:
            fig.add_trace(go.Scatter(
                x=pred_series.index,
                y=pred_series.values,
                mode='lines',
                name=f'{method.upper()} Prediction',
                line=dict(
                    color=colors.get(method, 'gray'),
                    width=2,
                    dash='dash'
                )
            ))
    
    # Add vertical line at prediction start
    if predictions:
        last_date = historical.index[-1]
        #last_date = str(historical.index[-1])
        fig.add_vline(
            x=last_date,
            line_dash="dash",
            line_color="gray",
            #annotation_text="Prediction Start"
        )
        fig.add_annotation(
            x=last_date,
            y=1,
            yref="paper",
            text="Prediction Start",
            showarrow=True,
            arrowhead=2
        )
        
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Price',
        height=500,
        template='plotly_white',
        hovermode='x unified',
        showlegend=True
    )
    
    fig.show()


def plot_anomaly_detection(prices: pd.Series, anomalies: pd.DataFrame):
    """
    Plot price with anomaly highlights
    
    Args:
        prices: Price series
        anomalies: DataFrame with anomaly flags
    """
    # Align data
    common_index = prices.index.intersection(anomalies.index)
    prices_aligned = prices.loc[common_index]
    anomalies_aligned = anomalies.loc[common_index]
    
    # Separate normal and anomalous points
    normal_prices = prices_aligned[~anomalies_aligned['is_anomaly']]
    anomaly_prices = prices_aligned[anomalies_aligned['is_anomaly']]
    
    fig = go.Figure()
    
    # Normal prices
    fig.add_trace(go.Scatter(
        x=normal_prices.index,
        y=normal_prices.values,
        mode='lines',
        name='Normal',
        line=dict(color='blue', width=2)
    ))
    
    # Anomalies
    fig.add_trace(go.Scatter(
        x=anomaly_prices.index,
        y=anomaly_prices.values,
        mode='markers',
        name='Anomaly',
        marker=dict(
            color='red',
            size=10,
            symbol='x'
        )
    ))
    
    fig.update_layout(
        title='Anomaly Detection',
        xaxis_title='Date',
        yaxis_title='Price',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.show()
    
    # Show anomaly statistics
    n_anomalies = anomalies_aligned['is_anomaly'].sum()
    pct_anomalies = (n_anomalies / len(anomalies_aligned)) * 100
    
    display(HTML(f"""
    <div style="padding: 15px; background: #f8f9fa; border-radius: 5px; margin: 10px 0;">
        <strong>Anomaly Statistics:</strong><br>
        Total anomalies: {n_anomalies} ({pct_anomalies:.1f}% of data)<br>
        Detection period: {len(anomalies_aligned)} days
    </div>
    """))


def plot_volatility_forecast(historical_vol: pd.Series, 
                             forecast_vol: pd.Series):
    """
    Plot historical and forecasted volatility
    
    Args:
        historical_vol: Historical volatility
        forecast_vol: Forecasted volatility
    """
    fig = go.Figure()
    
    # Historical
    fig.add_trace(go.Scatter(
        x=historical_vol.index,
        y=historical_vol.values * 100,  # Convert to percentage
        mode='lines',
        name='Historical Volatility',
        line=dict(color='blue', width=2)
    ))
    
    # Forecast
    if not forecast_vol.empty:
        # Create dates for forecast
        last_date = historical_vol.index[-1]
        #last_date = pd.Timestamp(historical_vol.index[-1])
        forecast_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=len(forecast_vol),
            freq='D'
        )
        
        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=forecast_vol.values * 100,
            mode='lines',
            name='Volatility Forecast',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Vertical line
        fig.add_vline(
            x=last_date,
            line_dash="dash",
            line_color="gray",
            annotation_text="Forecast Start"
        )
    
    fig.update_layout(
        title='Volatility Analysis & Forecast',
        xaxis_title='Date',
        yaxis_title='Volatility (%)',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.show()


def plot_model_comparison(historical: pd.Series, 
                         predictions: Dict[str, pd.Series],
                         actual_future: pd.Series = None):
    """
    Compare different model predictions
    
    Args:
        historical: Historical prices
        predictions: Dict of predictions
        actual_future: Actual future prices (if available)
    """
    fig = go.Figure()
    
    # Historical
    fig.add_trace(go.Scatter(
        x=historical.index,
        y=historical.values,
        mode='lines',
        name='Historical',
        line=dict(color='black', width=3)
    ))
    
    # Each prediction
    colors = ['red', 'green', 'orange', 'purple', 'brown']
    
    for i, (method, pred) in enumerate(predictions.items()):
        if not pred.empty:
            fig.add_trace(go.Scatter(
                x=pred.index,
                y=pred.values,
                mode='lines',
                name=method.upper(),
                line=dict(color=colors[i % len(colors)], width=2, dash='dash')
            ))
    
    # Actual future (if available for backtesting)
    if actual_future is not None and not actual_future.empty:
        fig.add_trace(go.Scatter(
            x=actual_future.index,
            y=actual_future.values,
            mode='lines',
            name='Actual',
            line=dict(color='blue', width=2)
        ))
    
    fig.update_layout(
        title='Model Comparison',
        xaxis_title='Date',
        yaxis_title='Price',
        height=600,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.show()
    
    # Calculate errors if actual available
    if actual_future is not None:
        display(HTML("<h4>Prediction Errors (RMSE):</h4>"))
        
        errors = []
        for method, pred in predictions.items():
            if not pred.empty:
                # Align dates
                common_dates = pred.index.intersection(actual_future.index)
                if len(common_dates) > 0:
                    pred_aligned = pred.loc[common_dates]
                    actual_aligned = actual_future.loc[common_dates]
                    
                    rmse = np.sqrt(((pred_aligned - actual_aligned) ** 2).mean())
                    mape = (np.abs((actual_aligned - pred_aligned) / actual_aligned)).mean() * 100
                    
                    errors.append({
                        'Method': method.upper(),
                        'RMSE': f'{rmse:.2f}',
                        'MAPE': f'{mape:.2f}%'
                    })
        
        if errors:
            display(pd.DataFrame(errors))


# ============================================
# MAIN ML DASHBOARD
# ============================================

def launch_ml_dashboard(symbol: str = None, portfolio_id: int = None):
    """
    Launch ML dashboard
    
    Args:
        symbol: Specific symbol to analyze
        portfolio_id: Portfolio ID to get symbols from
    """
    if not ML_AVAILABLE:
        print("Error: ML module not available")
        return
    
    # Header
    display(HTML("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🤖 Machine Learning Dashboard</h1>
        <p style="color: white; margin-top: 10px;">AI-Powered Predictions & Analytics</p>
    </div>
    """))
    
    # Initialize
    data_loader = MLDataLoader()
    ml_manager = MLManager()
    
    # Get symbols
    if symbol:
        symbols = [symbol]
    elif portfolio_id:
        symbols = data_loader.get_portfolio_symbols(portfolio_id)
    else:
        symbols = ['AAPL']  # Default
    
    print(f"Analyzing {len(symbols)} symbol(s): {', '.join(symbols)}")
    print()
    
    # Widgets
    symbol_dropdown = widgets.Dropdown(
        options=symbols,
        value=symbols[0],
        description='Symbol:',
        style={'description_width': 'initial'}
    )
    
    days_slider = widgets.IntSlider(
        value=365,
        min=90,
        max=730,
        step=30,
        description='History (days):',
        style={'description_width': 'initial'}
    )
    
    forecast_slider = widgets.IntSlider(
        value=30,
        min=7,
        max=90,
        step=7,
        description='Forecast (days):',
        style={'description_width': 'initial'}
    )
    
    method_dropdown = widgets.Dropdown(
        options=['arima', 'lstm', 'prophet', 'all'],
        value='arima',
        description='Method:',
        style={'description_width': 'initial'}
    )
    
    predict_button = widgets.Button(
        description='🔮 Predict',
        button_style='success',
        icon='magic'
    )
    
    anomaly_button = widgets.Button(
        description='🚨 Detect Anomalies',
        button_style='warning',
        icon='exclamation-triangle'
    )
    
    volatility_button = widgets.Button(
        description='📊 Forecast Volatility',
        button_style='info',
        icon='chart-line'
    )
    
    output = widgets.Output()
    
    def on_predict_click(btn):
        """Handle predict button click"""
        with output:
            clear_output(wait=True)
            
            symbol = symbol_dropdown.value
            days = days_slider.value
            forecast_days = forecast_slider.value
            method = method_dropdown.value
            
            display(HTML(f"<h3>Price Prediction for {symbol}</h3>"))
            print(f"Loading {days} days of historical data...")
            
            # Load data
            prices = data_loader.get_price_history(symbol, days=days)
            
            if prices.empty:
                print(f"❌ No data available for {symbol}")
                print("Run: python market_data_integration.py fetch")
                return
            
            print(f"✓ Loaded {len(prices)} days of data")
            print(f"Predicting next {forecast_days} days using {method}...")
            print()
            
            # Predict
            predictions = {}
            
            if method == 'all':
                methods_to_try = ['arima', 'lstm', 'prophet']
            else:
                methods_to_try = [method]
            
            for m in methods_to_try:
                try:
                    pred = ml_manager.predict_price(prices, method=m, days=forecast_days)
                    if not pred.empty:
                        predictions[m] = pred
                        print(f"✓ {m.upper()}: Next day prediction = {pred.iloc[0]:.2f}")
                except Exception as e:
                    print(f"✗ {m.upper()}: {str(e)}")
            
            if predictions:
                print()
                plot_price_prediction(prices, predictions, title=f"{symbol} Price Prediction")
            else:
                print("❌ All prediction methods failed")
    
    def on_anomaly_click(btn):
        """Handle anomaly detection click"""
        with output:
            clear_output(wait=True)
            
            symbol = symbol_dropdown.value
            days = days_slider.value
            
            display(HTML(f"<h3>Anomaly Detection for {symbol}</h3>"))
            print(f"Analyzing {days} days of data...")
            
            # Load data
            prices = data_loader.get_price_history(symbol, days=days)
            
            if prices.empty:
                print(f"❌ No data available for {symbol}")
                return
            
            print(f"✓ Loaded {len(prices)} days")
            print("Detecting anomalies...")
            
            # Detect anomalies
            try:
                prices_df = pd.DataFrame({'price': prices})
                anomalies = ml_manager.detect_anomalies(prices_df)
                
                print("✓ Anomaly detection complete")
                print()
                
                plot_anomaly_detection(prices, anomalies)
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def on_volatility_click(btn):
        """Handle volatility forecast click"""
        with output:
            clear_output(wait=True)
            
            symbol = symbol_dropdown.value
            days = days_slider.value
            forecast_days = forecast_slider.value
            
            display(HTML(f"<h3>Volatility Forecast for {symbol}</h3>"))
            print(f"Analyzing {days} days of data...")
            
            # Load data
            prices = data_loader.get_price_history(symbol, days=days)
            
            if prices.empty:
                print(f"❌ No data available for {symbol}")
                return
            
            # Calculate returns
            returns = prices.pct_change().dropna()
            
            # Calculate historical volatility
            historical_vol = returns.rolling(30).std()
            
            print(f"✓ Calculated historical volatility")
            print("Forecasting future volatility...")
            
            try:
                forecast_vol = ml_manager.predict_volatility(returns, days=forecast_days)
                
                print(f"✓ Forecast complete")
                print()
                
                plot_volatility_forecast(historical_vol, forecast_vol)
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Attach handlers
    predict_button.on_click(on_predict_click)
    anomaly_button.on_click(on_anomaly_click)
    volatility_button.on_click(on_volatility_click)
    
    # Layout
    controls = widgets.VBox([
        widgets.HBox([symbol_dropdown, days_slider, forecast_slider, method_dropdown]),
        widgets.HBox([predict_button, anomaly_button, volatility_button])
    ])
    
    dashboard = widgets.VBox([controls, output])
    
    display(dashboard)
    
    # Footer
    display(HTML("""
    <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; 
                border-radius: 5px; text-align: center;">
        <p style="margin: 0; color: #6c757d;">
            💡 <strong>Note:</strong> Predictions are based on historical data and should not be 
            used as sole basis for investment decisions. Always do your own research.
        </p>
    </div>
    """))


# ============================================
# STANDALONE FUNCTIONS
# ============================================

def quick_predict(symbol: str, days: int = 30, method: str = 'arima'):
    """Quick price prediction"""
    data_loader = MLDataLoader()
    ml_manager = MLManager()
    
    prices = data_loader.get_price_history(symbol, days=365)
    
    if prices.empty:
        print(f"No data for {symbol}")
        return
    
    prediction = ml_manager.predict_price(prices, method=method, days=days)
    
    print(f"{symbol} Price Prediction ({method.upper()}):")
    print(f"  Current: {prices.iloc[-1]:.2f}")
    print(f"  Next day: {prediction.iloc[0]:.2f}")
    print(f"  {days} days: {prediction.iloc[-1]:.2f}")


print("✅ ML dashboard module loaded!")
print()
print("Available commands:")
print("  launch_ml_dashboard(symbol='AAPL')          - Full dashboard")
print("  launch_ml_dashboard(portfolio_id=1)         - Portfolio symbols")
print("  quick_predict('AAPL', days=30, method='arima')  - Quick prediction")
print()
