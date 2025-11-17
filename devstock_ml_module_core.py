#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Machine Learning Module
========================
AI-powered portfolio analytics and predictions

Features:
- Price prediction (LSTM, Prophet, ARIMA)
- Risk forecasting (volatility prediction)
- Portfolio recommendation (ML-based)
- Anomaly detection
- Feature engineering

Author: Portfolio System
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# LSTM PRICE PREDICTOR
# ============================================

class LSTMPredictor:
    """
    LSTM-based price prediction
    Uses deep learning for time series forecasting
    """
    
    def __init__(self, lookback: int = 60, forecast_days: int = 30):
        """
        Initialize LSTM predictor
        
        Args:
            lookback: Number of days to look back
            forecast_days: Number of days to forecast
        """
        self.lookback = lookback
        self.forecast_days = forecast_days
        self.model = None
        self.scaler = None
        
        # Try to import tensorflow
        try:
            import tensorflow as tf
            from tensorflow import keras
            self.tf_available = True
            logger.info("TensorFlow available - LSTM enabled")
        except ImportError:
            self.tf_available = False
            logger.warning("TensorFlow not available - LSTM disabled")
    
    def prepare_data(self, prices: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for LSTM
        
        Args:
            prices: Price series
            
        Returns:
            Tuple of (X, y) training data
        """
        from sklearn.preprocessing import MinMaxScaler
        
        # Normalize data
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = self.scaler.fit_transform(prices.values.reshape(-1, 1))
        
        # Create sequences
        X, y = [], []
        
        for i in range(self.lookback, len(scaled_data)):
            X.append(scaled_data[i-self.lookback:i, 0])
            y.append(scaled_data[i, 0])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple) -> None:
        """
        Build LSTM model
        
        Args:
            input_shape: Shape of input data
        """
        if not self.tf_available:
            raise ImportError("TensorFlow not available")
        
        from tensorflow import keras
        from tensorflow.keras import layers
        
        model = keras.Sequential([
            layers.LSTM(50, return_sequences=True, input_shape=input_shape),
            layers.Dropout(0.2),
            layers.LSTM(50, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(25),
            layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        self.model = model
        
        logger.info("LSTM model built successfully")
    
    def train(self, prices: pd.Series, epochs: int = 50, batch_size: int = 32) -> Dict:
        """
        Train LSTM model
        
        Args:
            prices: Historical prices
            epochs: Training epochs
            batch_size: Batch size
            
        Returns:
            Training history
        """
        if not self.tf_available:
            logger.error("TensorFlow not available")
            return {}
        
        # Prepare data
        X, y = self.prepare_data(prices)
        
        # Reshape for LSTM
        X = X.reshape(X.shape[0], X.shape[1], 1)
        
        # Split train/test
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Build model if not exists
        if self.model is None:
            self.build_model((X.shape[1], 1))
        
        # Train
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            verbose=0
        )
        
        # Evaluate
        train_loss = history.history['loss'][-1]
        val_loss = history.history['val_loss'][-1]
        
        logger.info(f"Training complete - Train loss: {train_loss:.4f}, Val loss: {val_loss:.4f}")
        
        return {
            'train_loss': train_loss,
            'val_loss': val_loss,
            'history': history.history
        }
    
    def predict(self, prices: pd.Series, steps: int = None) -> pd.Series:
        """
        Predict future prices
        
        Args:
            prices: Historical prices
            steps: Number of steps to predict (default: forecast_days)
            
        Returns:
            Predicted prices
        """
        if not self.tf_available or self.model is None:
            logger.error("Model not available or not trained")
            return pd.Series()
        
        if steps is None:
            steps = self.forecast_days
        
        # Prepare last sequence
        scaled_data = self.scaler.transform(prices.values.reshape(-1, 1))
        last_sequence = scaled_data[-self.lookback:]
        
        # Predict iteratively
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(steps):
            # Reshape for prediction
            X = current_sequence.reshape(1, self.lookback, 1)
            
            # Predict
            pred = self.model.predict(X, verbose=0)[0, 0]
            predictions.append(pred)
            
            # Update sequence
            current_sequence = np.append(current_sequence[1:], [[pred]], axis=0)
        
        # Inverse transform
        predictions = self.scaler.inverse_transform(
            np.array(predictions).reshape(-1, 1)
        ).flatten()
        
        # Create series with future dates
        last_date = prices.index[-1]
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=steps,
            freq='D'
        )
        
        return pd.Series(predictions, index=future_dates)


# ============================================
# PROPHET TIME SERIES FORECASTER
# ============================================

class ProphetForecaster:
    """
    Facebook Prophet for time series forecasting
    Good for data with trends and seasonality
    """
    
    def __init__(self, forecast_days: int = 30):
        """
        Initialize Prophet forecaster
        
        Args:
            forecast_days: Number of days to forecast
        """
        self.forecast_days = forecast_days
        self.model = None
        
        # Try to import prophet
        try:
            from prophet import Prophet
            self.prophet_available = True
            logger.info("Prophet available")
        except ImportError:
            self.prophet_available = False
            logger.warning("Prophet not available - install: pip install prophet")
    
    def train(self, prices: pd.Series, **kwargs) -> None:
        """
        Train Prophet model
        
        Args:
            prices: Historical prices
            **kwargs: Additional Prophet parameters
        """
        if not self.prophet_available:
            logger.error("Prophet not available")
            return
        
        from prophet import Prophet
        
        # Prepare data for Prophet
        df = pd.DataFrame({
            'ds': prices.index,
            'y': prices.values
        })
        
        # Initialize and train
        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            **kwargs
        )
        
        self.model.fit(df)
        logger.info("Prophet model trained")
    
    def predict(self, steps: int = None) -> pd.DataFrame:
        """
        Predict future prices
        
        Args:
            steps: Number of steps to predict
            
        Returns:
            DataFrame with predictions and confidence intervals
        """
        if not self.prophet_available or self.model is None:
            logger.error("Model not available or not trained")
            return pd.DataFrame()
        
        if steps is None:
            steps = self.forecast_days
        
        # Make future dataframe
        future = self.model.make_future_dataframe(periods=steps)
        
        # Predict
        forecast = self.model.predict(future)
        
        # Return only future predictions
        forecast = forecast.tail(steps)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


# ============================================
# ARIMA FORECASTER
# ============================================

class ARIMAForecaster:
    """
    ARIMA model for time series forecasting
    Traditional statistical approach
    """
    
    def __init__(self, order: Tuple = (5, 1, 0)):
        """
        Initialize ARIMA forecaster
        
        Args:
            order: ARIMA order (p, d, q)
        """
        self.order = order
        self.model = None
        
        # Try to import statsmodels
        try:
            from statsmodels.tsa.arima.model import ARIMA
            self.arima_available = True
            logger.info("ARIMA available")
        except ImportError:
            self.arima_available = False
            logger.warning("ARIMA not available - install: pip install statsmodels")
    
    def train(self, prices: pd.Series) -> None:
        """
        Train ARIMA model
        
        Args:
            prices: Historical prices
        """
        if not self.arima_available:
            logger.error("ARIMA not available")
            return
        
        from statsmodels.tsa.arima.model import ARIMA
        
        # Fit model
        model = ARIMA(prices, order=self.order)
        self.model = model.fit()
        
        logger.info(f"ARIMA{self.order} model trained")
    
    def predict(self, steps: int = 30) -> pd.Series:
        """
        Predict future prices
        
        Args:
            steps: Number of steps to predict
            
        Returns:
            Predicted prices
        """
        if not self.arima_available or self.model is None:
            logger.error("Model not available or not trained")
            return pd.Series()
        
        # Forecast
        forecast = self.model.forecast(steps=steps)
        
        return forecast


# ============================================
# VOLATILITY PREDICTOR
# ============================================

class VolatilityPredictor:
    """
    Predict future volatility using GARCH models
    """
    
    def __init__(self):
        """Initialize volatility predictor"""
        # Try to import arch
        try:
            from arch import arch_model
            self.arch_available = True
            logger.info("ARCH/GARCH available")
        except ImportError:
            self.arch_available = False
            logger.warning("ARCH not available - install: pip install arch")
        
        self.model = None
    
    def train(self, returns: pd.Series) -> None:
        """
        Train GARCH model
        
        Args:
            returns: Return series
        """
        if not self.arch_available:
            logger.error("ARCH not available")
            return
        
        from arch import arch_model
        
        # Fit GARCH(1,1) model
        model = arch_model(returns * 100, vol='Garch', p=1, q=1)
        self.model = model.fit(disp='off')
        
        logger.info("GARCH model trained")
    
    def predict(self, horizon: int = 30) -> pd.Series:
        """
        Predict future volatility
        
        Args:
            horizon: Forecast horizon
            
        Returns:
            Predicted volatility
        """
        if not self.arch_available or self.model is None:
            logger.error("Model not available or not trained")
            return pd.Series()
        
        # Forecast
        forecast = self.model.forecast(horizon=horizon)
        
        # Extract variance and convert to volatility
        variance = forecast.variance.values[-1, :]
        volatility = np.sqrt(variance) / 100  # Convert back from percentage
        
        return pd.Series(volatility)


# ============================================
# ML PORTFOLIO RECOMMENDER
# ============================================

class MLPortfolioRecommender:
    """
    Machine learning based portfolio recommendations
    Uses ensemble methods
    """
    
    def __init__(self):
        """Initialize recommender"""
        self.model = None
        
        try:
            from sklearn.ensemble import RandomForestRegressor
            self.sklearn_available = True
            logger.info("Scikit-learn available")
        except ImportError:
            self.sklearn_available = False
            logger.warning("Scikit-learn not available")
    
    def create_features(self, prices_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features from price data
        
        Args:
            prices_df: DataFrame with prices
            
        Returns:
            DataFrame with features
        """
        features = pd.DataFrame(index=prices_df.index)
        
        for col in prices_df.columns:
            prices = prices_df[col]
            
            # Returns
            features[f'{col}_return'] = prices.pct_change()
            
            # Moving averages
            features[f'{col}_ma5'] = prices.rolling(5).mean()
            features[f'{col}_ma20'] = prices.rolling(20).mean()
            
            # Volatility
            features[f'{col}_vol'] = prices.pct_change().rolling(20).std()
            
            # RSI
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            features[f'{col}_rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = prices.ewm(span=12, adjust=False).mean()
            exp2 = prices.ewm(span=26, adjust=False).mean()
            features[f'{col}_macd'] = exp1 - exp2
        
        return features.dropna()
    
    def train(self, features: pd.DataFrame, target: pd.Series) -> Dict:
        """
        Train recommendation model
        
        Args:
            features: Feature DataFrame
            target: Target variable (future returns)
            
        Returns:
            Training metrics
        """
        if not self.sklearn_available:
            logger.error("Scikit-learn not available")
            return {}
        
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Model trained - MSE: {mse:.4f}, R2: {r2:.4f}")
        
        return {
            'mse': mse,
            'r2': r2,
            'feature_importance': dict(zip(
                features.columns,
                self.model.feature_importances_
            ))
        }
    
    def predict_returns(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predict future returns
        
        Args:
            features: Feature DataFrame
            
        Returns:
            Predicted returns
        """
        if self.model is None:
            logger.error("Model not trained")
            return np.array([])
        
        return self.model.predict(features)


# ============================================
# ANOMALY DETECTOR
# ============================================

class AnomalyDetector:
    """
    Detect anomalies in price movements
    Uses Isolation Forest
    """
    
    def __init__(self, contamination: float = 0.05):
        """
        Initialize anomaly detector
        
        Args:
            contamination: Expected proportion of outliers
        """
        self.contamination = contamination
        self.model = None
        
        try:
            from sklearn.ensemble import IsolationForest
            self.sklearn_available = True
        except ImportError:
            self.sklearn_available = False
            logger.warning("Scikit-learn not available")
    
    def train(self, features: pd.DataFrame) -> None:
        """
        Train anomaly detector
        
        Args:
            features: Feature DataFrame
        """
        if not self.sklearn_available:
            logger.error("Scikit-learn not available")
            return
        
        from sklearn.ensemble import IsolationForest
        
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=42
        )
        self.model.fit(features)
        
        logger.info("Anomaly detector trained")
    
    def detect(self, features: pd.DataFrame) -> np.ndarray:
        """
        Detect anomalies
        
        Args:
            features: Feature DataFrame
            
        Returns:
            Array of 1 (normal) or -1 (anomaly)
        """
        if self.model is None:
            logger.error("Model not trained")
            return np.array([])
        
        return self.model.predict(features)
    
    def get_anomaly_scores(self, features: pd.DataFrame) -> np.ndarray:
        """
        Get anomaly scores
        
        Args:
            features: Feature DataFrame
            
        Returns:
            Anomaly scores (lower = more anomalous)
        """
        if self.model is None:
            logger.error("Model not trained")
            return np.array([])
        
        return self.model.score_samples(features)


# ============================================
# UNIFIED ML MANAGER
# ============================================

class MLManager:
    """
    Unified interface for all ML models
    """
    
    def __init__(self):
        """Initialize ML manager"""
        self.lstm = LSTMPredictor()
        self.prophet = ProphetForecaster()
        self.arima = ARIMAForecaster()
        self.volatility = VolatilityPredictor()
        self.recommender = MLPortfolioRecommender()
        self.anomaly = AnomalyDetector()
        
        logger.info("ML Manager initialized")
    
    def predict_price(self, prices: pd.Series, method: str = 'lstm', 
                     days: int = 30) -> pd.Series:
        """
        Predict future prices
        
        Args:
            prices: Historical prices
            method: Prediction method ('lstm', 'prophet', 'arima')
            days: Number of days to predict
            
        Returns:
            Predicted prices
        """
        logger.info(f"Predicting price using {method} for {days} days")
        
        if method == 'lstm':
            if not self.lstm.tf_available:
                logger.error("LSTM not available")
                return pd.Series()
            
            # Train and predict
            self.lstm.train(prices, epochs=50)
            return self.lstm.predict(prices, steps=days)
        
        elif method == 'prophet':
            if not self.prophet.prophet_available:
                logger.error("Prophet not available")
                return pd.Series()
            
            self.prophet.train(prices)
            forecast = self.prophet.predict(steps=days)
            return pd.Series(
                forecast['yhat'].values,
                index=pd.to_datetime(forecast['ds'])
            )
        
        elif method == 'arima':
            if not self.arima.arima_available:
                logger.error("ARIMA not available")
                return pd.Series()
            
            self.arima.train(prices)
            return self.arima.predict(steps=days)
        
        else:
            logger.error(f"Unknown method: {method}")
            return pd.Series()
    
    def predict_volatility(self, returns: pd.Series, days: int = 30) -> pd.Series:
        """
        Predict future volatility
        
        Args:
            returns: Historical returns
            days: Number of days to predict
            
        Returns:
            Predicted volatility
        """
        logger.info(f"Predicting volatility for {days} days")
        
        self.volatility.train(returns)
        return self.volatility.predict(horizon=days)
    
    def detect_anomalies(self, prices_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalies in price movements
        
        Args:
            prices_df: DataFrame with prices
            
        Returns:
            DataFrame with anomaly flags
        """
        logger.info("Detecting anomalies")
        
        # Create features
        features = self.recommender.create_features(prices_df)
        
        # Train and detect
        self.anomaly.train(features)
        anomalies = self.anomaly.detect(features)
        scores = self.anomaly.get_anomaly_scores(features)
        
        return pd.DataFrame({
            'is_anomaly': anomalies == -1,
            'anomaly_score': scores
        }, index=features.index)


# ============================================
# MAIN - DEMO
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("🤖 Machine Learning Module - Demo")
    print("="*70)
    print()
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    
    # Simulate price series
    prices = pd.Series(
        100 + np.cumsum(np.random.normal(0.1, 1, len(dates))),
        index=dates
    )
    
    print("Sample data generated:")
    print(f"  Period: {len(dates)} days")
    print(f"  Price range: {prices.min():.2f} - {prices.max():.2f}")
    print()
    
    # Initialize ML manager
    ml = MLManager()
    
    # Test available methods
    print("Testing ML methods:")
    print()
    
    # Test ARIMA (usually available)
    if ml.arima.arima_available:
        print("1️⃣  ARIMA Prediction:")
        try:
            arima_pred = ml.predict_price(prices, method='arima', days=10)
            print(f"   ✓ Predicted next 10 days")
            print(f"   Next day: {arima_pred.iloc[0]:.2f}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    else:
        print("1️⃣  ARIMA: Not available (install statsmodels)")
    
    print()
    
    # Test anomaly detection
    if ml.anomaly.sklearn_available:
        print("2️⃣  Anomaly Detection:")
        try:
            # Create simple features
            features = pd.DataFrame({
                'return': prices.pct_change(),
                'vol': prices.pct_change().rolling(20).std()
            }).dropna()
            
            ml.anomaly.train(features)
            anomalies = ml.anomaly.detect(features)
            n_anomalies = (anomalies == -1).sum()
            
            print(f"   ✓ Detected {n_anomalies} anomalies")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    else:
        print("2️⃣  Anomaly Detection: Not available (install scikit-learn)")
    
    print()
    print("="*70)
    print("✅ Demo completed!")
    print("="*70)
    print()
    print("Note: Install optional dependencies for full functionality:")
    print("  pip install tensorflow prophet statsmodels arch scikit-learn")
