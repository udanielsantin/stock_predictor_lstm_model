import streamlit as st
import torch
import torch.nn as nn
import joblib
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import pandas as pd

# ==================== MODEL DEFINITION ====================
class StockLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out


# ==================== HELPER FUNCTIONS ====================
@st.cache_resource
def load_model_and_scaler():
    """Load pre-trained model and scaler"""
    model = StockLSTM(input_size=1, hidden_size=64, num_layers=2)
    model.load_state_dict(torch.load("/workspaces/stock_predictor_lstm_model/models/stock_lstm.pt", 
                                     weights_only=True))
    model.eval()
    
    scaler = joblib.load("/workspaces/stock_predictor_lstm_model/models/scaler.joblib")
    
    return model, scaler


def load_stock_data(ticker, start, end):
    """Download stock data from Yahoo Finance"""
    yf_ticker = ticker if "." in ticker else f"{ticker}.SA"
    try:
        df = yf.download(yf_ticker, start=start, end=end, auto_adjust=False)[["Close"]]
    except Exception as e:
        st.error(f"❌ Erro ao baixar dados para {yf_ticker}: {e}")
        return None
    
    if df is None or df.empty:
        st.error(f"❌ Nenhum dado encontrado para {yf_ticker}")
        return None
    
    df.dropna(inplace=True)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df


def create_sequences(data, seq_length=50):
    """Create sequences for LSTM"""
    x, y = [], []
    for i in range(len(data) - seq_length):
        x.append(data[i : i + seq_length])
        y.append(data[i + seq_length])
    return np.array(x), np.array(y)


def predict_stock(ticker, start_date, end_date, model, scaler):
    """Predict stock prices using the loaded model"""
    
    # Load data
    df = load_stock_data(ticker, start_date, end_date)
    if df is None:
        return None
    
    df.reset_index(inplace=True)
    
    # Scale data with a new scaler (fit on the new data)
    scaler_new = MinMaxScaler()
    scaled_data = scaler_new.fit_transform(df[["Close"]])
    
    # Create sequences
    X, y = create_sequences(scaled_data, seq_length=50)
    
    if len(X) == 0:
        st.error("❌ Dados insuficientes para criar sequências (mínimo 51 dias)")
        return None
    
    # Convert to tensors
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    
    # Make predictions
    model.eval()
    with torch.no_grad():
        y_pred = model(X_t).numpy()
        y_true = y_t.numpy()
    
    # Inverse transform
    y_pred_inv = scaler_new.inverse_transform(y_pred)
    y_true_inv = scaler_new.inverse_transform(y_true)
    
    # Calculate metrics
    mse = float(np.mean((y_true - y_pred) ** 2))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(mse))
    mape = float(np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1e-8, None))) * 100)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else float("nan")
    
    # Predict next price
    with torch.no_grad():
        last_seq = torch.tensor(scaled_data[-50:], dtype=torch.float32).unsqueeze(0)
        pred_next_scaled = model(last_seq).numpy()
        pred_next_price = scaler_new.inverse_transform(pred_next_scaled)[0][0]
    
    return {
        "y_true": y_true_inv.squeeze().tolist(),
        "y_pred": y_pred_inv.squeeze().tolist(),
        "metrics": {
            "MSE": mse,
            "MAE": mae,
            "RMSE": rmse,
            "MAPE_%": mape,
            "R2": r2
        },
        "next_price": pred_next_price,
        "last_close": float(df["Close"].iloc[-1]),
        "data_points": len(X)
    }


# ==================== STREAMLIT APP ====================
st.set_page_config(page_title="Stock LSTM Predictor", layout="wide", initial_sidebar_state="expanded")

st.title("📈 Stock Price Predictor with LSTM")
st.markdown("---")

# Load model
model, scaler = load_model_and_scaler()

# Sidebar for inputs
st.sidebar.header("⚙️ Configurações")

ticker = st.sidebar.text_input(
    "Ticker da Ação",
    value="ABEV3",
    placeholder="Ex: ABEV3, VALE3, etc"
).upper()

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.sidebar.date_input(
        "Data Inicial",
        value=datetime.now() - timedelta(days=365)
    )

with col2:
    end_date = st.sidebar.date_input(
        "Data Final",
        value=datetime.now()
    )

# Validate dates
if start_date >= end_date:
    st.error("❌ Data inicial deve ser anterior à data final!")
    st.stop()

# Predict button
if st.sidebar.button("🚀 Fazer Previsão", use_container_width=True, type="primary"):
    with st.spinner("⏳ Carregando dados e fazendo previsões..."):
        results = predict_stock(ticker, start_date, end_date, model, scaler)
    
    if results:
        st.success("✅ Previsão concluída com sucesso!")
        
        # Display summary metrics
        st.markdown("---")
        st.header("📊 Resumo da Análise")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Preço Atual (Último Fecha)",
                f"R$ {results['last_close']:.2f}"
            )
        
        with col2:
            st.metric(
                "Próximo Preço Previsto",
                f"R$ {results['next_price']:.2f}",
                delta=f"R$ {results['next_price'] - results['last_close']:.2f}"
            )
        
        with col3:
            st.metric(
                "Número de Pontos",
                f"{results['data_points']} dias"
            )
        
        with col4:
            st.metric(
                "R² Score",
                f"{results['metrics']['R2']:.4f}"
            )
        
        # Display detailed metrics
        st.markdown("---")
        st.subheader("📋 Métricas Detalhadas")
        
        metrics_df = pd.DataFrame([results['metrics']])
        
        col_metric1, col_metric2, col_metric3, col_metric4, col_metric5 = st.columns(5)
        
        with col_metric1:
            st.metric("MSE", f"{results['metrics']['MSE']:.6f}")
        with col_metric2:
            st.metric("MAE", f"{results['metrics']['MAE']:.6f}")
        with col_metric3:
            st.metric("RMSE", f"{results['metrics']['RMSE']:.6f}")
        with col_metric4:
            st.metric("MAPE", f"{results['metrics']['MAPE_%']:.2f}%")
        with col_metric5:
            st.metric("R²", f"{results['metrics']['R2']:.4f}")
        
        # Plot predictions vs real
        st.markdown("---")
        st.subheader("📈 Gráfico: Previsto vs Real")
        
        fig, ax = plt.subplots(figsize=(14, 5))
        
        ax.plot(results['y_true'], label='Preço Real', color='#1f77b4', linewidth=2.5, alpha=0.8)
        ax.plot(results['y_pred'], label='Preço Previsto', color='#ff7f0e', linewidth=2.5, alpha=0.8)
        
        ax.set_title(f'{ticker} - Análise de Previsão ({start_date} a {end_date})', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Índice de Tempo (dias)', fontsize=11)
        ax.set_ylabel('Preço (R$)', fontsize=11)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        
        # Display text summary
        st.markdown("---")
        st.subheader("📝 Resumo Executivo")
        
        summary_text = f"""
        **Ação Analisada:** {ticker}
        
        **Período:** {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}
        
        **Informações de Preço:**
        - 💰 Último preço de fechamento: **R$ {results['last_close']:.2f}**
        - 📊 Próximo preço previsto: **R$ {results['next_price']:.2f}**
        - 📈 Variação prevista: **R$ {results['next_price'] - results['last_close']:.2f}** 
        ({((results['next_price'] - results['last_close']) / results['last_close'] * 100):.2f}%)
        
        **Qualidade da Previsão:**
        - 🎯 R² Score: **{results['metrics']['R2']:.4f}** (quanto mais próximo de 1, melhor)
        - 📉 Erro Médio Absoluto (MAE): **R$ {results['metrics']['MAE']:.2f}**
        - 📊 Erro Percentual Absoluto Médio (MAPE): **{results['metrics']['MAPE_%']:.2f}%**
        
        **Dados Utilizados:**
        - 📅 Total de dias: **{results['data_points']}**
        - 🔢 Sequências de 50 dias processadas
        
        ---
        *Modelo: LSTM de 2 camadas com 64 neurônios*
        """
        
        st.markdown(summary_text)

else:
    st.info("👈 Configure os parâmetros na barra lateral e clique em 'Fazer Previsão'")
