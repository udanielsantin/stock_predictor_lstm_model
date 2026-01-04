import torch
import torch.nn as nn
import joblib
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import base64

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


# ==================== LOAD MODEL ====================
def load_model_and_scaler(model_path: str, scaler_path: str):
    model = StockLSTM(input_size=1, hidden_size=64, num_layers=2)
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    
    scaler = joblib.load(scaler_path)
    
    return model, scaler


# ==================== DATA LOADING ====================
def load_stock_data(ticker: str, start: str, end: str):
    """Download stock data from Yahoo Finance"""
    # Aceita qualquer ticker (internacional ou brasileiro)
    # Se não tiver sufixo e parecer ser brasileiro (apenas letras + números), adiciona .SA
    # Caso contrário, usa como está (MSFT, AAPL, etc.)
    yf_ticker = ticker
    
    # Tenta primeiro com o ticker original
    try:
        df = yf.download(yf_ticker, start=start, end=end, auto_adjust=False)[["Close"]]
        
        # Se não retornar dados e não tiver ponto, tenta adicionar .SA para ações brasileiras
        if (df is None or df.empty) and "." not in ticker:
            print(f"⚠️  Ticker '{ticker}' não retornou dados. Tentando '{ticker}.SA'...")
            yf_ticker = f"{ticker}.SA"
            df = yf.download(yf_ticker, start=start, end=end, auto_adjust=False)[["Close"]]
    except Exception as e:
        # Se falhar e não tiver ponto, tenta com .SA como fallback
        if "." not in ticker:
            print(f"⚠️  Erro com '{ticker}'. Tentando '{ticker}.SA'...")
            yf_ticker = f"{ticker}.SA"
            try:
                df = yf.download(yf_ticker, start=start, end=end, auto_adjust=False)[["Close"]]
            except Exception as e2:
                raise RuntimeError(f"Failed to download data for both {ticker} and {yf_ticker}: {e2}")
        else:
            raise RuntimeError(f"Failed to download data for {yf_ticker}: {e}")
    
    if df is None or df.empty:
        raise RuntimeError(f"No data returned for {yf_ticker}. Verifique se o ticker está correto.")
    
    df.dropna(inplace=True)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df


# ==================== SEQUENCE CREATION ====================
def create_sequences(data, seq_length=50):
    x, y = [], []
    for i in range(len(data) - seq_length):
        x.append(data[i : i + seq_length])
        y.append(data[i + seq_length])
    return np.array(x), np.array(y)


# ==================== PLOTTING ====================
def generate_plot_base64(y_true, y_pred, ticker: str, start_date: str, end_date: str) -> str:
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(y_true, label='Preço Real', color='#1f77b4', linewidth=2.5, alpha=0.8)
    ax.plot(y_pred, label='Preço Previsto', color='#ff7f0e', linewidth=2.5, alpha=0.8)
    
    ax.set_title(f'{ticker} - Análise de Previsão ({start_date} a {end_date})',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Índice de Tempo (dias)', fontsize=11)
    ax.set_ylabel('Preço (R$)', fontsize=11)
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)
    
    # Save to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


# ==================== PREDICTION ====================
def predict_stock(
    ticker: str,
    start_date: str,
    end_date: str,
    model,
    scaler
) -> dict:

    df = load_stock_data(ticker, start_date, end_date)
    df.reset_index(inplace=True)
    
    scaler_new = MinMaxScaler()
    scaled_data = scaler_new.fit_transform(df[["Close"]])
    
    X, y = create_sequences(scaled_data, seq_length=50)
    
    if len(X) == 0:
        raise ValueError("Dados insuficientes para criar sequências (mínimo 51 dias)")
    
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    
    model.eval()
    with torch.no_grad():
        y_pred = model(X_t).numpy()
        y_true = y_t.numpy()
    
    y_pred_inv = scaler_new.inverse_transform(y_pred)
    y_true_inv = scaler_new.inverse_transform(y_true)
    
    mse = float(np.mean((y_true - y_pred) ** 2))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(mse))
    mape = float(np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1e-8, None))) * 100)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else float("nan")
    
    with torch.no_grad():
        last_seq = torch.tensor(scaled_data[-50:], dtype=torch.float32).unsqueeze(0)
        pred_next_scaled = model(last_seq).numpy()
        pred_next_price = scaler_new.inverse_transform(pred_next_scaled)[0][0]
    
    plot_image = generate_plot_base64(
        y_true_inv.squeeze().tolist(),
        y_pred_inv.squeeze().tolist(),
        ticker,
        start_date,
        end_date
    )
    
    last_close = float(df["Close"].iloc[-1])
    price_change = pred_next_price - last_close
    price_change_pct = (price_change / last_close) * 100
    
    return {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "last_close": round(last_close, 2),
        "next_price": round(pred_next_price, 2),
        "price_change": round(price_change, 2),
        "price_change_pct": round(price_change_pct, 2),
        "metrics": {
            "MSE": round(mse, 6),
            "MAE": round(mae, 6),
            "RMSE": round(rmse, 6),
            "MAPE": round(mape, 2),
            "R2": round(r2, 4)
        },
        "data_points": len(X),
        "plot": f"data:image/png;base64,{plot_image}"
    }
